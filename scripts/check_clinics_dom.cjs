#!/usr/bin/env node
'use strict';

// Optional DOM verification using an existing jsdom installation. This does
// not prove browser rendering, responsive geometry or native keyboard input.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { JSDOM, VirtualConsole } = require(process.env.ORTHOCONNECT_JSDOM_MODULE || 'jsdom');
const root = path.resolve(__dirname, '..');
const errors = [];
let assertions = 0;
function check(value, message) { assert.ok(value, message); assertions += 1; }

async function open(filename = 'clinics.html', query = '', protocol = 'http', run = true) {
  const virtualConsole = new VirtualConsole();
  virtualConsole.on('jsdomError', (error) => errors.push(error.message));
  const url = protocol === 'file' ? `file://${path.join(root, filename)}${query}` : `https://orthoconnect.example/${filename}${query}`;
  const dom = new JSDOM(fs.readFileSync(path.join(root, filename), 'utf8'), { url, runScripts: 'outside-only', pretendToBeVisual: true, virtualConsole });
  dom.window.matchMedia = () => ({ matches: false, addEventListener() {} });
  dom.window.HTMLElement.prototype.scrollIntoView = function scrollIntoView() {};
  dom.window.fetch = () => { throw new Error('Directory filtering must not make network requests'); };
  if (run) {
    dom.window.eval(fs.readFileSync(path.join(root, 'scripts/main.js'), 'utf8'));
    dom.window.eval(fs.readFileSync(path.join(root, 'scripts/effects.js'), 'utf8'));
    if (dom.window.document.querySelector('[data-clinic-directory]')) {
      dom.window.eval(fs.readFileSync(path.join(root, 'scripts/clinics.js'), 'utf8'));
    }
  }
  await new Promise((resolve) => setTimeout(resolve, 25));
  return dom;
}
const cards = (dom) => [...dom.window.document.querySelectorAll('.clinic-filterable')].filter((c) => !c.hidden);
function change(dom, id, value) {
  const field = dom.window.document.getElementById(id);
  field.value = value;
  field.dispatchEvent(new dom.window.Event(field.tagName === 'INPUT' ? 'input' : 'change', { bubbles: true }));
}
const platform = (dom, value) => dom.window.document.getElementById(`clinic-platform-${value}`).click();
async function clear(dom, empty = false) {
  const selectors = empty ? '[data-clinic-empty] [data-clear-clinic-filters]' : '[data-clinic-form] [data-clear-clinic-filters]';
  dom.window.document.querySelector(selectors).click();
  await Promise.resolve();
}

async function main() {
  const dom = await open();
  const document = dom.window.document;
  check(cards(dom).length === 18, 'Initial directory must show all 18 real centres');
  check(!document.querySelector('[data-clinic-form]').hidden, 'Working filters must become visible');
  check(document.querySelector('[data-clinic-count]').textContent === 'Showing 18 clinics', 'Initial count');
  check(document.getElementById('clinic-platform-all').checked, 'All platforms is the default');
  check(new Set([...document.querySelectorAll('#clinic-location option')].map((o) => o.value)).size === document.querySelectorAll('#clinic-location option').length, 'Locations must be deduplicated');
  const count = document.querySelector('[data-clinic-count]');
  check(count.getAttribute('aria-live') === 'polite', 'Result changes must be announced');
  change(dom, 'clinic-search', '  hEmAs  ');
  check(cards(dom).length === 1 && cards(dom)[0].id === 'clinic-hemas-hospital-thalawathugoda', 'Case and surrounding whitespace must not prevent hospital search');
  check(cards(dom)[0].querySelectorAll('[data-booking-provider]').length === 1 && cards(dom)[0].querySelector('[data-booking-provider]').dataset.bookingProvider === 'doc990', 'Hemas must show only its documented Doc990 option');
  check(new URL(dom.window.location.href).searchParams.get('q') === 'hEmAs', 'Search must be retained in the URL');
  await clear(dom);
  change(dom, 'clinic-search', 'Ragama Leesons');
  check(cards(dom).length === 1 && cards(dom)[0].id === 'clinic-leesons-hospital-ragama', 'Search terms can match hospital and town in either order');
  await clear(dom);
  change(dom, 'clinic-location', 'Homagama');
  check(cards(dom).length === 2, 'Homagama must include both Healan and Medihelp');
  platform(dom, 'doc990');
  check(cards(dom).length === 1 && cards(dom)[0].id === 'clinic-healan-hospitals-homagama', 'Platform and location filters must intersect');
  check(cards(dom)[0].querySelectorAll('[data-booking-provider]').length === 2, 'Both documented choices stay visible on a dual-platform clinic');
  change(dom, 'clinic-search', 'Medihelp');
  check(cards(dom).length === 0 && !document.querySelector('[data-clinic-empty]').hidden, 'Search, location and platform must intersect with a helpful empty state');
  check(count.textContent === 'Showing 0 of 18 clinics', 'Empty result count');
  await clear(dom, true);
  check(cards(dom).length === 18 && document.querySelector('[data-clinic-empty]').hidden, 'Empty-state clear must restore all clinics');
  check(document.activeElement.id === 'clinic-search' && dom.window.location.search === '', 'Clear restores search focus and clears URL filter state');
  for (const provider of ['echannelling', 'doc990']) {
    platform(dom, provider);
    check(cards(dom).length === 13, `${provider} filter must show all 13 documented centres`);
    check(cards(dom).every((card) => card.querySelector(`[data-booking-provider="${provider}"]`)), 'Platform results must have that provider');
    await clear(dom);
  }
  change(dom, 'clinic-search', 'MDK');
  check(cards(dom).length === 1 && !cards(dom)[0].querySelector('.clinic-address'), 'MDK remains discoverable without an invented location');
  await clear(dom);
  change(dom, 'clinic-search', '<svg onload=alert(1)>');
  check(cards(dom).length === 0 && !document.querySelector('#clinic-search svg'), 'Search is treated as text');
  await clear(dom);
  const submit = new dom.window.Event('submit', { bubbles: true, cancelable: true });
  document.querySelector('[data-clinic-form]').dispatchEvent(submit);
  check(submit.defaultPrevented, 'Enter in search must not submit to a server');
  dom.window.history.pushState(null, '', '?q=Ragama&platform=doc990&utm_source=clinic#clinic-directory');
  dom.window.dispatchEvent(new dom.window.PopStateEvent('popstate'));
  check(cards(dom).length === 2 && document.getElementById('clinic-platform-doc990').checked, 'History restores controls and visible results');
  await clear(dom);
  check(dom.window.location.search === '?utm_source=clinic' && dom.window.location.hash === '#clinic-directory', 'Clear must preserve unrelated URL parameters and anchors');
  dom.window.history.replaceState(null, '', '?location=Homagama&platform=echannelling');
  dom.window.dispatchEvent(new dom.window.PageTransitionEvent('pageshow', { persisted: true }));
  check(cards(dom).length === 2 && document.getElementById('clinic-location').value === 'Homagama', 'Back/forward-cache restoration');
  dom.window.close();

  for (const filename of ['clinics.html', 'hospitals.html']) {
    for (const protocol of ['http', 'file']) {
      const shared = await open(filename, '?q=Ragama&platform=echannelling', protocol);
      check(cards(shared).length === 2, `Shared URL restores filters on ${filename} over ${protocol}`);
      await clear(shared);
      check(cards(shared).length === 18, 'Filtering must work with HTTP and direct-file viewing');
      shared.window.close();
    }
  }
  const malformed = await open('clinics.html', '?location=unknown&platform=unknown');
  check(cards(malformed).length === 18 && malformed.window.document.getElementById('clinic-platform-all').checked, 'Unknown filter values fall back to all clinics');
  malformed.window.close();
  const nojs = await open('clinics.html', '', 'http', false);
  check(cards(nojs).length === 18 && nojs.window.document.querySelectorAll('[data-booking-provider]').length === 26, 'All centres and all 26 booking links work without JavaScript');
  check(nojs.window.document.querySelector('[data-clinic-form]').hidden, 'Inert filters are hidden without JavaScript');
  nojs.window.close();

  // Shared navigation code must still initialise across every rebuilt page.
  const files = fs.readdirSync(root).filter((name) => name.endsWith('.html'));
  for (const dir of ['articles', 'treatments', 'patient-information']) {
    files.push(...fs.readdirSync(path.join(root, dir)).filter((name) => name.endsWith('.html')).map((name) => `${dir}/${name}`));
  }
  for (const filename of files) {
    const page = await open(filename);
    check(!page.window.document.querySelector('dialog, [data-contact], [data-enquiry], button[data-booking]'), `${filename}: no demonstration controls`);
    const toggle = page.window.document.querySelector('.menu-toggle');
    toggle.click();
    check(toggle.getAttribute('aria-expanded') === 'true', `${filename}: navigation opens`);
    page.window.document.dispatchEvent(new page.window.KeyboardEvent('keydown', { key: 'Escape', bubbles: true }));
    check(toggle.getAttribute('aria-expanded') === 'false', `${filename}: navigation closes`);
    page.window.close();
  }
  const library = await open('conditions.html');
  change(library, 'library-search', 'knee');
  check([...library.window.document.querySelectorAll('.filterable-item')].some((card) => card.hidden), 'Existing topic-library search still works');
  library.window.close();
  check(errors.length === 0, `No DOM script errors: ${errors.join('; ')}`);
  console.log(`PASS: ${assertions} DOM assertions; directory search/filter intersections, exact platform choices, reset/empty state, URL/history, aliases, direct-file/no-JavaScript and shared navigation on ${files.length} pages.`);
  console.log('LIMIT: DOM verification does not prove rendered layout or native browser input.');
}

main().catch((error) => { console.error(error); process.exitCode = 1; });
