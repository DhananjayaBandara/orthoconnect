#!/usr/bin/env node
'use strict';

// Logic and graceful-fallback checks with mocked geometry/animation APIs.
// These tests are not evidence of rendering or native browser keyboard input.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { JSDOM, VirtualConsole } = require(process.env.ORTHOCONNECT_JSDOM_MODULE || 'jsdom');
const root = path.resolve(__dirname, '..');
let assertions = 0;
const errors = [];
const check = (value, message) => { assert.ok(value, message); assertions += 1; };
const settle = () => new Promise((resolve) => setTimeout(resolve, 35));

async function open(filename, options = {}) {
  const virtualConsole = new VirtualConsole();
  virtualConsole.on('jsdomError', (error) => errors.push(error.message));
  const dom = new JSDOM(fs.readFileSync(path.join(root, filename), 'utf8'), {
    url: `https://orthoconnect.example/${filename}${options.hash || ''}`,
    runScripts: 'outside-only', pretendToBeVisual: true, virtualConsole,
  });
  const window = dom.window;
  const state = { scroll: 0, articleTop: 500, articleBottom: 2500 };
  Object.defineProperty(window, 'scrollY', { get: () => state.scroll });
  Object.defineProperty(window, 'innerHeight', { value: 800 });
  const queries = new Map();
  window.matchMedia = (query) => {
    if (!queries.has(query)) {
      const listeners = new Set();
      const media = {
        matches: query.includes('reduced-motion') ? Boolean(options.reduced) : query.includes('1191') ? Boolean(options.desktop) : false,
        addEventListener: (_type, fn) => listeners.add(fn),
        set(value) { this.matches = value; listeners.forEach((fn) => fn({ matches: value })); },
      };
      queries.set(query, media);
    }
    return queries.get(query);
  };
  window.HTMLElement.prototype.scrollIntoView = function scrollIntoView() {};
  window.HTMLElement.prototype.getBoundingClientRect = function getBoundingClientRect() {
    const top = this.matches('.site-header') ? 0 : this.matches('.reading-article') ? state.articleTop - state.scroll : 1200 - state.scroll;
    const height = this.matches('.site-header') ? 116 : this.matches('.reading-article') ? state.articleBottom - state.articleTop : 150;
    return { x: 0, y: top, top, bottom: top + height, height, left: 0, right: 600, width: 600 };
  };
  const animations = [];
  if (options.animation !== false) {
    window.Element.prototype.animate = function animate(frames, config) {
      let complete;
      const record = { element: this, frames, config, cancelled: false };
      const animation = { finished: new Promise((resolve) => { complete = resolve; }), cancel() { record.cancelled = true; complete(); } };
      animations.push(record);
      return animation;
    };
  }
  const observers = [];
  if (options.observer !== false) {
    window.IntersectionObserver = class {
      constructor(callback) { this.callback = callback; this.targets = new Set(); observers.push(this); }
      observe(element) { this.targets.add(element); }
      unobserve(element) { this.targets.delete(element); }
      disconnect() { this.targets.clear(); }
      enter(element) { this.callback([{ target: element, isIntersecting: true, boundingClientRect: element.getBoundingClientRect() }]); }
    };
  }
  let resize;
  window.ResizeObserver = class {
    constructor(callback) { resize = callback; }
    observe() {}
  };
  if (options.scripts !== false) {
    window.eval(fs.readFileSync(path.join(root, 'scripts/main.js'), 'utf8'));
    window.eval(fs.readFileSync(path.join(root, 'scripts/effects.js'), 'utf8'));
  }
  await settle();
  return { dom, window, document: window.document, state, queries, animations, observers, resize: () => resize?.() };
}

async function main() {
  const home = await open('index.html');
  const toggle = home.document.querySelector('.menu-toggle');
  const navigation = home.document.getElementById('primary-navigation');
  check(navigation.hasAttribute('inert'), 'Closed mobile navigation must be inert during its visual transition');
  toggle.click();
  check(!navigation.hasAttribute('inert') && toggle.getAttribute('aria-expanded') === 'true', 'Opening mobile navigation enables its links');
  navigation.querySelector('a').focus();
  home.document.dispatchEvent(new home.window.KeyboardEvent('keydown', { key: 'Escape', bubbles: true }));
  check(navigation.hasAttribute('inert') && home.document.activeElement === toggle, 'Escape closes navigation and restores toggle focus');
  toggle.click();
  const mainLink = home.document.querySelector('.hero-actions a');
  mainLink.focus();
  check(toggle.getAttribute('aria-expanded') === 'false' && home.document.activeElement === mainLink, 'Tabbing out closes the disclosure without stealing focus');
  home.queries.get('(min-width: 1191px)').set(true);
  check(!navigation.hasAttribute('inert'), 'Desktop navigation must remain available after a viewport change');
  home.queries.get('(min-width: 1191px)').set(false);
  check(navigation.hasAttribute('inert'), 'Returning to mobile keeps a closed menu inert');
  check(home.animations.some((a) => a.element.matches('.portrait-frame')), 'The decorative portrait frame gets a short entrance');
  check(!home.animations.some((a) => a.element.matches('h1, .hero-actions, [data-booking-provider]')), 'Name and booking controls must not wait for an entrance');
  const observer = home.observers.at(-1);
  const card = home.document.querySelector('.expertise-card');
  check(observer.targets.has(card), 'Offscreen introductory cards can receive an optional reveal');
  home.state.scroll = 500;
  observer.enter(card);
  const cardAnimations = () => home.animations.filter((a) => a.element === card);
  check(cardAnimations().length === 1 && !observer.targets.has(card), 'A reveal unobserves its target after the first entry');
  observer.enter(card);
  check(cardAnimations().length === 1, 'A previously revealed group never replays');
  check([...home.document.querySelectorAll('[data-booking-provider]')].every((link) => !link.closest('[data-reveal]')), 'External clinic booking controls remain outside reveal groups');
  home.queries.get('(prefers-reduced-motion: reduce)').set(true);
  await settle();
  check(home.animations.every((a) => a.cancelled), 'Enabling reduced motion cancels active entrance animations');
  check(home.document.documentElement.classList.contains('motion-reduced') && observer.targets.size === 0, 'Reduced motion disables pending observers and CSS transitions');
  home.window.close();

  for (const options of [{ reduced: true }, { animation: false }, { observer: false }, { hash: '#main' }]) {
    const page = await open('index.html', options);
    check([...page.document.querySelectorAll('[data-reveal]')].every((element) => !element.hidden && element.style.opacity !== '0'), 'Fallbacks never leave content hidden');
    if (options.reduced || options.animation === false) check(page.animations.length === 0, 'Reduced-motion or missing animation API skips animation');
    if (options.hash) check(page.animations.length === 0 && page.observers.every((o) => o.targets.size === 0), 'Direct anchors are immediately available without entrance effects');
    check(page.document.querySelectorAll('[data-booking-provider]').length === 3, 'Working homepage booking anchors survive every enhancement fallback');
    page.window.close();
  }
  const nojs = await open('clinics.html', { scripts: false });
  check(nojs.document.querySelectorAll('[data-booking-provider]').length === 26 && !nojs.document.querySelector('[inert]'), 'All links and native navigation remain available without JavaScript');
  nojs.window.close();

  for (const filename of ['articles/en-adult-hip.html', 'articles/si-adult-hip-replacement.html', 'treatments/hip-replacement.html', 'patient-information/consultation-faq.html']) {
    const page = await open(filename, { reduced: true });
    const bar = page.document.querySelector('[data-reading-progress]');
    check(!bar.hidden && bar.getAttribute('aria-hidden') === 'true', 'Progress is a quiet decorative aid, independent of reduced motion');
    check(bar.dataset.progress === '0', 'Progress starts before the article');
    page.state.scroll = 1042;
    page.window.dispatchEvent(new page.window.Event('scroll'));
    await settle();
    check(bar.dataset.progress === '50' && page.document.querySelector('.site-header').classList.contains('is-scrolled'), 'Mocked halfway geometry produces halfway progress and scrolled header feedback');
    page.state.articleBottom = 3500;
    page.resize();
    await settle();
    check(Number(bar.dataset.progress) < 50, 'Content/image resize recalculates progress');
    page.state.scroll = 5000;
    page.window.dispatchEvent(new page.window.PageTransitionEvent('pageshow', { persisted: true }));
    await settle();
    check(bar.dataset.progress === '100', 'Restored scroll and overscroll clamp progress at completion');
    check(!page.document.querySelector('.reading-article [data-reveal]') && page.animations.length === 0, 'Reading paragraphs and medical figures never animate on scroll');
    page.state.articleTop = 500; page.state.articleBottom = 620; page.state.scroll = 0;
    page.resize(); await settle();
    check(bar.dataset.progress === '0', 'Short reading pages start at zero before their article');
    page.state.scroll = 400; page.resize(); await settle();
    check(bar.dataset.progress === '100', 'Short reading pages have a finite completion state');
    page.window.close();
  }
  const faq = await open('patient-information.html');
  const disclosure = faq.document.querySelector('.faq-item');
  disclosure.open = true;
  disclosure.dispatchEvent(new faq.window.Event('toggle'));
  check(faq.animations.some((a) => a.element.matches('.disclosure-body')), 'Native disclosure opening receives optional feedback');
  disclosure.open = false;
  disclosure.dispatchEvent(new faq.window.Event('toggle'));
  check(faq.animations.every((a) => a.cancelled), 'Closing leaves no animation running on hidden disclosure content');
  faq.window.close();

  const paths = fs.readdirSync(root).filter((name) => name.endsWith('.html'));
  for (const directory of ['articles', 'treatments', 'patient-information']) paths.push(...fs.readdirSync(path.join(root, directory)).filter((name) => name.endsWith('.html')).map((name) => `${directory}/${name}`));
  for (const filename of paths) {
    const dom = new JSDOM(fs.readFileSync(path.join(root, filename), 'utf8'));
    const doc = dom.window.document;
    check(doc.querySelectorAll('script[src$="scripts/effects.js"]').length === 1 && doc.querySelectorAll('link[href$="styles/effects.css"]').length === 1, `${filename}: shared enhancements are loaded exactly once`);
    const reading = filename.includes('/');
    check(doc.querySelectorAll('[data-reading-progress]').length === Number(reading), `${filename}: progress is present only on reading pages`);
    if (reading) check(doc.querySelector('[data-reading-progress]').hidden, 'Progress stays hidden without JavaScript');
    dom.window.close();
  }
  check(errors.length === 0, `No DOM script errors: ${errors.join('; ')}`);
  console.log(`PASS: ${assertions} visual-enhancement DOM assertions; navigation focus/inert state, one-time reveals, motion preference changes, missing APIs, native disclosure, mocked progress geometry and ${paths.length} page integrations.`);
  console.log('LIMIT: animation and geometry APIs are mocked; rendered layout and native browser input are not verified.');
}

main().catch((error) => { console.error(error); process.exitCode = 1; });
