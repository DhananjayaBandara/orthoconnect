#!/usr/bin/env node
'use strict';

// Deterministic DOM/timer checks. These do not verify browser rendering,
// native touch gestures, responsive geometry or the visual fade.
const assert = require('node:assert/strict');
const crypto = require('node:crypto');
const fs = require('node:fs');
const path = require('node:path');
const { JSDOM, VirtualConsole } = require(process.env.ORTHOCONNECT_JSDOM_MODULE || 'jsdom');
const root = path.resolve(__dirname, '..');
const html = fs.readFileSync(path.join(root, 'index.html'), 'utf8');
const source = fs.readFileSync(path.join(root, 'scripts/home.js'), 'utf8');
const config = JSON.parse(fs.readFileSync(path.join(root, 'content/home-carousel.json'), 'utf8'));
const interval = config.interval_ms;
const errors = [];
let assertions = 0;
const check = (value, message) => { assert.ok(value, message); assertions += 1; };

function open({ reduced = false, observer = true, scripts = true } = {}) {
  const virtualConsole = new VirtualConsole();
  virtualConsole.on('jsdomError', (error) => errors.push(error.message));
  const dom = new JSDOM(html, { url: 'file://' + path.join(root, 'index.html'), runScripts: 'outside-only', pretendToBeVisual: true, virtualConsole });
  const { window } = dom;
  const { document } = window;
  let headerHeight = 117;
  const header = document.querySelector('.site-header');
  header.getBoundingClientRect = () => ({ height: headerHeight });
  let time = 0;
  let serial = 0;
  const timers = new Map();
  window.setTimeout = (callback, delay) => { const id = ++serial; timers.set(id, { at: time + delay, callback }); return id; };
  window.clearTimeout = (id) => timers.delete(id);
  Object.defineProperty(window.performance, 'now', { value: () => time });
  const tick = (duration) => {
    const end = time + duration;
    while (true) {
      const next = [...timers].filter(([, timer]) => timer.at <= end).sort((a, b) => a[1].at - b[1].at)[0];
      if (!next) break;
      timers.delete(next[0]);
      time = next[1].at;
      next[1].callback();
    }
    time = end;
  };
  let hidden = false;
  Object.defineProperty(document, 'hidden', { get: () => hidden });
  const listeners = [];
  const motion = { matches: reduced, addEventListener: (_event, listener) => listeners.push(listener) };
  window.matchMedia = () => motion;
  const resizeObservers = new Map();
  window.ResizeObserver = class {
    constructor(callback) { this.callback = callback; }
    observe(target) { resizeObservers.set(target, this.callback); }
  };
  let intersection;
  if (observer) {
    window.IntersectionObserver = class {
      constructor(callback) { intersection = callback; }
      observe() { this.setVisible(true); }
      setVisible(value) { intersection([{ isIntersecting: value }]); }
    };
  }
  if (scripts) window.eval(source);
  const carousel = document.querySelector('[data-banner-carousel]');
  const slides = [...carousel.querySelectorAll('.banner-slide')];
  const dots = [...carousel.querySelectorAll('[data-banner-dot]')];
  const viewport = carousel.querySelector('.banner-viewport');
  const index = () => Number(carousel.dataset.bannerIndex);
  const pointer = (type, pointerType = 'mouse') => {
    const event = new window.Event(type);
    Object.defineProperty(event, 'pointerType', { value: pointerType });
    carousel.dispatchEvent(event);
  };
  const touch = (type, x = 0, y = 0) => {
    const event = new window.Event(type, { bubbles: true });
    Object.defineProperties(event, {
      touches: { value: type === 'touchstart' ? [{ clientX: x, clientY: y }] : [] },
      changedTouches: { value: [{ clientX: x, clientY: y }] },
    });
    viewport.dispatchEvent(event);
  };
  const key = (keyName, extras = {}) => carousel.dispatchEvent(new window.KeyboardEvent('keydown', { key: keyName, bubbles: true, cancelable: true, ...extras }));
  return {
    dom, window, document, carousel, slides, dots, viewport, index, tick, pointer, touch, key, timers,
    headerHeight(value, observer = true) {
      headerHeight = value;
      if (observer) resizeObservers.get(header)?.();
      else window.dispatchEvent(new window.Event('resize'));
    },
    visible(value) { intersection([{ isIntersecting: value }]); },
    hidden(value) { hidden = value; document.dispatchEvent(new window.Event('visibilitychange')); },
    reduced(value) { motion.matches = value; listeners.forEach((listener) => listener({ matches: value })); },
  };
}

async function main() {
  check(interval === 2000, 'Autoplay must advance every two seconds');
  check(config.slides.map((slide) => slide.id).join(',') === '01-surgeon,02-services,03-information,04-consultation', 'All four supplied banners must retain their order');
  for (const slide of config.slides) {
    const bytes = fs.readFileSync(path.join(root, slide.src));
    check(crypto.createHash('sha256').update(bytes).digest('hex') === slide.sha256, `${slide.id}: original PNG checksum`);
    check(bytes.readUInt32BE(16) === slide.width && bytes.readUInt32BE(20) === slide.height, `${slide.id}: intrinsic image dimensions`);
    check(slide.variants.every((variant) => fs.existsSync(path.join(root, variant.src))), `${slide.id}: responsive variants must exist`);
    const desktop = slide.desktop;
    const desktopBytes = fs.readFileSync(path.join(root, desktop.src));
    check(crypto.createHash('sha256').update(desktopBytes).digest('hex') === desktop.sha256, `${slide.id}: desktop WebP must retain its original checksum`);
    check(desktop.width === 1920 && desktop.height === 700, `${slide.id}: desktop banner dimensions`);
  }

  const app = open();
  try {
    check(app.carousel === app.document.querySelector('main').firstElementChild, 'Banner carousel must be the first homepage section');
    check(app.index() === 0 && app.slides.length === 4, 'First supplied banner must appear initially');
    app.slides.forEach((slide, index) => {
      const source = slide.querySelector('picture').firstElementChild;
      check(source.getAttribute('media') === '(min-width: 761px)' && source.getAttribute('srcset') === `${config.slides[index].desktop.src} 1920w`, `Slide ${index + 1}: desktop artwork must take priority on desktop`);
    });
    check(!app.carousel.querySelector('[data-banner-controls]').hidden, 'Slide dots must be revealed');
    check(!app.carousel.querySelector('.banner-toolbar, [data-banner-link], [data-banner-counter], [data-banner-previous], [data-banner-next], [data-banner-playback]'), 'Captions, counters, arrows and playback buttons must be removed');
    check(app.carousel.style.getPropertyValue('--banner-header-height') === '117px', 'Viewport sizing must account for the actual header height');
    app.headerHeight(146);
    check(app.carousel.style.getPropertyValue('--banner-header-height') === '146px', 'Header size changes must update the available carousel space');
    app.headerHeight(93, false);
    check(app.carousel.style.getPropertyValue('--banner-header-height') === '93px', 'Window resizing must refresh the header measurement');
    app.headerHeight(117);
    check(app.carousel.querySelector('[data-banner-status]').getAttribute('aria-live') === 'off', 'Autoplay must not repeatedly announce banners');
    app.tick(config.interval_ms - 1);
    check(app.index() === 0, 'Autoplay must leave time to read each banner');
    for (const expected of [1, 2, 3, 0]) {
      app.tick(expected === 1 ? 1 : config.interval_ms);
      check(app.index() === expected, `Autoplay must advance in order and wrap to ${expected}`);
    }
    app.dots[2].click();
    check(app.index() === 2, 'Slide selectors must navigate directly');
    check(app.slides[0].classList.contains('is-previous'), 'The outgoing image must remain underneath the incoming fade');
    check(app.slides.filter((slide) => slide.classList.contains('is-previous')).length === 1, 'Only one outgoing banner must remain as the fade backdrop');
    check(app.slides[2].querySelector('a').getAttribute('href') === 'patient-information.html', 'The banner image must retain its corresponding page link');
    check(app.dots.filter((dot) => dot.hasAttribute('aria-current')).length === 1, 'Exactly one slide selector must indicate the current banner');
    check(app.slides.every((slide, position) => position === 2 ? !slide.hasAttribute('inert') && !slide.hasAttribute('aria-hidden') : slide.hasAttribute('inert') && slide.getAttribute('aria-hidden') === 'true'), 'Only the current slide must be accessible to focus and assistive technology');
    app.tick(interval - 500);
    app.dots[0].click();
    app.tick(500);
    check(app.index() === 0, 'Manual navigation must reset the full reading interval');
    app.tick(interval - 500);
    check(app.index() === 1, 'Autoplay must resume after the new interval');

    app.pointer('pointerenter');
    app.tick(interval * 2);
    check(app.index() === 1 && app.carousel.dataset.bannerPlaying === 'false', 'Hover must suspend autoplay');
    app.pointer('pointerleave');
    app.tick(interval);
    check(app.index() === 2, 'Leaving the banner must resume autoplay');
    app.pointer('pointerenter', 'touch');
    app.tick(interval);
    check(app.index() === 3, 'Touch pointer entry must not leave autoplay permanently paused');

    app.dots[0].focus();
    app.tick(interval * 2);
    check(app.index() === 3, 'Keyboard focus must suspend autoplay');
    check(app.carousel.querySelector('[data-banner-status]').getAttribute('aria-live') === 'polite', 'Manual navigation must have a polite status announcement');
    app.key('ArrowRight');
    check(app.index() === 0 && app.document.activeElement === app.dots[0], 'Arrow keys must wrap without moving keyboard focus');
    app.key('End');
    check(app.index() === 3, 'End must select the fourth banner');
    app.key('Home');
    check(app.index() === 0, 'Home must select the first banner');
    app.key('ArrowLeft');
    check(app.index() === 3, 'Left arrow must wrap backwards');
    app.key('ArrowRight', { altKey: true });
    check(app.index() === 3, 'Modified navigation shortcuts must retain their native behavior');
    app.dots[1].focus();
    await Promise.resolve();
    app.tick(interval);
    check(app.index() === 3, 'Moving focus within the carousel must keep autoplay paused');
    app.dots[1].blur();
    await Promise.resolve();
    app.tick(interval);
    check(app.index() === 0, 'Moving focus outside the carousel must resume autoplay');

    app.dots[1].click();
    app.hidden(true);
    app.tick(interval * 2);
    check(app.index() === 1, 'Background tabs must suspend autoplay');
    app.hidden(false);
    app.tick(interval);
    check(app.index() === 2, 'Returning to the tab must resume with a full interval');
    app.visible(false);
    app.tick(interval * 2);
    check(app.index() === 2, 'Off-screen banners must suspend autoplay');
    app.visible(true);
    app.tick(interval);
    check(app.index() === 3, 'Visible banners must resume autoplay');

    app.touch('touchstart', 300, 100);
    app.tick(interval);
    check(app.index() === 3, 'A held touch must suspend autoplay');
    app.touch('touchend', 150, 105);
    check(app.index() === 0, 'A horizontal left swipe must advance');
    const accidentalClick = new app.window.MouseEvent('click', { bubbles: true, cancelable: true });
    app.slides[0].querySelector('a').dispatchEvent(accidentalClick);
    check(accidentalClick.defaultPrevented, 'Completing a swipe must not accidentally open a banner link');
    app.touch('touchstart', 100, 100);
    app.touch('touchend', 250, 105);
    check(app.index() === 3, 'A horizontal right swipe must go backwards');
    app.touch('touchstart', 100, 100);
    app.touch('touchend', 105, 250);
    check(app.index() === 3, 'Vertical page-scrolling gestures must not change banners');
    app.touch('touchstart', 100, 100);
    app.touch('touchcancel');
    app.tick(interval);
    check(app.index() === 0, 'Cancelled gestures must not leave autoplay stuck');
    app.reduced(true);
    app.tick(interval * 2);
    check(app.index() === 0 && app.carousel.dataset.bannerPlaying === 'false', 'Switching reduced motion on must stop autoplay immediately');
  } finally { app.dom.window.close(); }

  const reduced = open({ reduced: true });
  try {
    reduced.tick(interval * 4);
    check(reduced.index() === 0 && reduced.carousel.dataset.bannerPlaying === 'false', 'Reduced motion must start with autoplay paused');
    reduced.dots[1].click();
    check(reduced.index() === 1, 'Reduced-motion users must retain manual navigation');
    reduced.reduced(false);
    reduced.tick(interval);
    check(reduced.index() === 2, 'Autoplay must follow a change to the reduced-motion preference');
  } finally { reduced.dom.window.close(); }

  const fallback = open({ scripts: false });
  try {
    check(fallback.slides.filter((slide) => slide.classList.contains('is-active')).length === 1, 'No JavaScript must retain a single static first banner');
    check(fallback.slides[0].querySelector('a').getAttribute('href') === 'about.html', 'Static banner link must remain usable without JavaScript');
    check(fallback.carousel.querySelector('[data-banner-controls]').hidden, 'Inert dots must remain hidden without JavaScript');
    check(fallback.document.querySelector('.home-hero h1').textContent === 'Dr. Suneth De Silva', 'The existing homepage introduction must remain available');
  } finally { fallback.dom.window.close(); }

  const noObserver = open({ observer: false });
  try {
    noObserver.tick(interval);
    check(noObserver.index() === 1, 'Missing IntersectionObserver must preserve basic autoplay');
  } finally { noObserver.dom.window.close(); }
  check(errors.length === 0, `No DOM runtime errors: ${errors.join('; ')}`);
  console.log(`PASS: ${assertions} banner DOM/asset checks: header sizing, removed controls, order, timer, looping, slide dots, keyboard events, swipe events, reduced motion, visibility and static fallback.`);
  console.log('LIMIT: mocked DOM/timer checks do not prove rendering, visual transitions, native input or responsive geometry.');
}

main().catch((error) => { console.error(error); process.exitCode = 1; });
