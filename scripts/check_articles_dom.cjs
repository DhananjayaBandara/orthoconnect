#!/usr/bin/env node
'use strict';

// Optional interaction verification. jsdom is a test dependency only; the site
// itself stays dependency-free. Set ARTICLE_JSDOM_MODULE to an installed module
// path if jsdom is not resolvable locally. This does not verify browser layout.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { JSDOM, VirtualConsole } = require(process.env.ARTICLE_JSDOM_MODULE || 'jsdom');
const root = path.resolve(__dirname, '..');
const errors = [];
let assertions = 0;

function check(condition, message) {
  assert.ok(condition, message);
  assertions += 1;
}

async function openPage(filename, query = '', protocol = 'http') {
  const url = protocol === 'file'
    ? `file://${path.join(root, filename)}${query}`
    : `http://127.0.0.1:8080/${filename}${query}`;
  const virtualConsole = new VirtualConsole();
  virtualConsole.on('jsdomError', (error) => errors.push(error.message));
  const dom = new JSDOM(fs.readFileSync(path.join(root, filename), 'utf8'), {
    url, runScripts: 'outside-only', pretendToBeVisual: true, virtualConsole,
  });
  dom.window.matchMedia = () => ({ matches: false, addEventListener() {}, removeEventListener() {} });
  dom.window.HTMLElement.prototype.scrollIntoView = function scrollIntoView() {};
  dom.window.eval(fs.readFileSync(path.join(root, 'scripts/main.js'), 'utf8'));
  dom.window.eval(fs.readFileSync(path.join(root, 'scripts/effects.js'), 'utf8'));
  dom.window.eval(fs.readFileSync(path.join(root, 'scripts/articles.js'), 'utf8'));
  await new Promise((resolve) => setTimeout(resolve, 20));
  return dom;
}

function visible(dom) {
  return [...dom.window.document.querySelectorAll('[data-article-library] .filterable-item')]
    .filter((card) => !card.hidden);
}

function field(dom, id, value) {
  const input = dom.window.document.getElementById(id);
  input.value = value;
  input.dispatchEvent(new dom.window.Event(input.tagName === 'INPUT' ? 'input' : 'change', { bubbles: true }));
}

function language(dom, value) {
  dom.window.document.getElementById(`article-language-${value}`).click();
}

async function reset(dom) {
  dom.window.document.querySelector('[data-article-form]').reset();
  await Promise.resolve();
}

async function main() {
  const dom = await openPage('articles.html');
  const document = dom.window.document;
  check(visible(dom).length === 40, 'Initial view must contain exactly the 40 supplied entries');
  check(document.querySelector('[data-article-count]').textContent === '40 articles · 19 English · 21 සිංහල', 'Initial language counts');
  check(document.getElementById('article-language-all').checked, 'All languages is the initial selection');
  language(dom, 'si');
  check(visible(dom).length === 21 && visible(dom).every((card) => card.lang === 'si'), 'Sinhala collection');
  language(dom, 'en');
  check(visible(dom).length === 19 && visible(dom).every((card) => card.lang === 'en'), 'English collection contains only the supplied articles');
  field(dom, 'article-audience', 'children');
  check(visible(dom).length === 7, 'English children collection');
  language(dom, 'si');
  check(visible(dom).length === 13, 'Sinhala children collection includes guide and the explicitly shared-audience complex-fracture article');
  await reset(dom);
  language(dom, 'si');
  field(dom, 'article-audience', 'adult');
  field(dom, 'article-region', 'hip');
  field(dom, 'article-topic', 'joint-replacement');
  check(visible(dom).length === 1 && visible(dom)[0].id === 'si-adult-hip-replacement', 'Language, audience, region and topic must intersect');
  field(dom, 'article-search', 'උකුල');
  check(visible(dom).length === 1, 'Sinhala search combined with all filters');
  const listingURL = new URL(dom.window.location.href);
  check(listingURL.searchParams.get('lang') === 'si' && listingURL.searchParams.get('region') === 'hip' && listingURL.searchParams.get('q') === 'උකුල', 'Shareable URL must reflect all selected filters');
  const readingURL = new URL(visible(dom)[0].querySelector('[data-article-link]').href);
  check(readingURL.pathname === '/articles/si-adult-hip-replacement.html', 'Independent reading URL');
  const reader = await openPage('articles/si-adult-hip-replacement.html', readingURL.search);
  check(reader.window.document.documentElement.lang === 'si', 'Sinhala document language');
  check(reader.window.document.querySelectorAll('[data-article-return]').length === 4, 'Header, footer, breadcrumb and article return routes all retain context');
  reader.window.document.querySelectorAll('[data-article-return]').forEach((link) => {
    check(new URL(link.href).pathname === '/articles.html' && new URL(link.href).search === listingURL.search, 'Navigation, breadcrumb and return links must restore originating filters');
  });
  reader.window.document.querySelectorAll('[data-article-link]').forEach((link) => {
    check(new URL(link.href).searchParams.get('library') === listingURL.searchParams.toString(), 'Related reading must carry browsing context');
  });
  const returned = await openPage('articles.html', new URL(reader.window.document.querySelector('[data-article-return]').href).search);
  check(visible(returned).length === 1 && visible(returned)[0].id === 'si-adult-hip-replacement', 'Return navigation restores results without browser storage');
  returned.window.close(); reader.window.close();
  const shared = await openPage('articles.html', listingURL.search);
  check(visible(shared).length === 1 && shared.window.document.getElementById('article-search').value === 'උකුල', 'Freshly opened shared URL restores controls and results');
  shared.window.close();
  field(dom, 'article-audience', 'children');
  check(visible(dom).length === 0 && !document.querySelector('[data-article-empty]').hidden, 'No-result state');
  document.querySelector('[data-article-reset]').click();
  await Promise.resolve();
  check(visible(dom).length === 40 && document.querySelector('[data-article-empty]').hidden, 'Empty-state reset restores all supplied entries');
  check(dom.window.location.search === '' && document.activeElement.id === 'article-search', 'Reset clears the share URL and restores search focus');
  field(dom, 'article-search', 'ඔස්ටියෝපොරෝසිස්'.normalize('NFD'));
  check(visible(dom).length === 1 && visible(dom)[0].id === 'si-adult-osteoporosis', 'Canonically equivalent Sinhala input must match');
  await reset(dom);
  field(dom, 'article-search', 'osteoporosis');
  check(visible(dom).length === 1 && visible(dom)[0].id === 'si-adult-osteoporosis', 'English discovery keyword can locate the independent Sinhala article');
  dom.window.history.pushState(null, '', '?lang=en&audience=children');
  dom.window.dispatchEvent(new dom.window.PopStateEvent('popstate'));
  check(visible(dom).length === 7 && document.getElementById('article-language-en').checked, 'History event restores URL state');
  dom.window.history.replaceState(null, '', '?lang=si&audience=adult');
  dom.window.dispatchEvent(new dom.window.PageTransitionEvent('pageshow', { persisted: true }));
  check(visible(dom).length === 9, 'Back/forward-cache pageshow handler restores URL state');
  check(!document.querySelector('link[hreflang]'), 'Independent articles must not imply translation pairs');
  dom.window.close();

  const direct = await openPage('articles/si-children-overview.html');
  check(direct.window.document.querySelector('[data-article-return]').getAttribute('href') === '../articles.html?lang=si', 'Direct Sinhala article defaults to the Sinhala collection');
  check(direct.window.document.querySelectorAll('#reading-topic-guide [data-article-link]').length === 11, 'Children’s guide contains all 11 topic links');
  direct.window.close();
  const allReader = await openPage('articles/si-adult-hip-replacement.html', '?library=');
  check(allReader.window.document.querySelector('[data-article-return]').getAttribute('href') === '../articles.html', 'Explicit unfiltered origin remains All languages');
  allReader.window.close();
  const safeReader = await openPage('articles/en-adult-hip.html', '?library=return%3Dhttps%253A%252F%252Fexample.com%26lang%3Dsi');
  check(safeReader.window.document.querySelector('[data-article-return]').getAttribute('href') === '../articles.html?lang=si', 'Return context accepts filter keys, never redirect destinations');
  safeReader.window.close();
  const invalid = await openPage('articles.html', '?lang=zz&audience=bad&region=unknown&topic=unknown');
  check(visible(invalid).length === 40 && invalid.window.location.search === '', 'Unknown filters fall back to the complete supplied collection');
  invalid.window.close();
  const file = await openPage('articles.html', '?lang=si&topic=bone-health', 'file');
  check(visible(file).length === 1, 'Direct-file preview supports filters');
  check(new URL(visible(file)[0].querySelector('[data-article-link]').href).pathname.endsWith('/articles/si-adult-osteoporosis.html'), 'Direct-file preview resolves nested reading links');
  file.window.close();
  const fallback = await openPage('articles.html');
  fallback.window.history.replaceState = () => { throw new fallback.window.DOMException('History disabled', 'SecurityError'); };
  language(fallback, 'si');
  check(visible(fallback).length === 21 && visible(fallback)[0].querySelector('[data-article-link]').getAttribute('href').includes('library=lang%3Dsi'), 'Restricted viewers retain filter context in article links');
  fallback.window.close();
  check(errors.length === 0, `Unexpected script errors: ${errors.join('; ')}`);
  console.log(`PASS: ${assertions} DOM interaction assertions, including combined filters, Unicode search, counts, resets, share/return links, guide links, history handlers and direct-file preview.`);
  console.log('LIMIT: jsdom does not verify browser rendering, native keyboard behaviour, font shaping, image layout or responsive geometry.');
}

main().catch((error) => { console.error(error); process.exitCode = 1; });
