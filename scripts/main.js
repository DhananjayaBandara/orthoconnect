'use strict';

document.documentElement.classList.add('js-enabled');

const navigation = document.querySelector('#primary-navigation');
const menuToggle = document.querySelector('.menu-toggle');
const desktopNavigation = window.matchMedia('(min-width: 1191px)');

function setMenu(open) {
  navigation.classList.toggle('is-open', open);
  menuToggle.setAttribute('aria-expanded', String(open));
  menuToggle.setAttribute('aria-label', open ? 'Close navigation' : 'Open navigation');
  menuToggle.querySelector('use').setAttribute('href', `#icon-${open ? 'close' : 'menu'}`);
  navigation.toggleAttribute('inert', !desktopNavigation.matches && !open);
}

menuToggle.addEventListener('click', () => {
  setMenu(menuToggle.getAttribute('aria-expanded') !== 'true');
});

navigation.addEventListener('click', (event) => {
  if (event.target.closest('a')) setMenu(false);
});

document.addEventListener('click', (event) => {
  if (!event.target.closest('.site-header')) setMenu(false);
});

document.addEventListener('keydown', (event) => {
  if (event.key === 'Escape' && menuToggle.getAttribute('aria-expanded') === 'true') {
    setMenu(false);
    menuToggle.focus();
  }
});

desktopNavigation.addEventListener('change', (event) => {
  if (event.matches) setMenu(false);
  else navigation.toggleAttribute('inert', menuToggle.getAttribute('aria-expanded') !== 'true');
});
document.addEventListener('focusin', (event) => {
  if (menuToggle.getAttribute('aria-expanded') === 'true' && !event.target.closest('.site-header')) setMenu(false);
});
setMenu(false);

function normalise(value) {
  return value.normalize('NFKD').replace(/[\u0300-\u036f]/g, '').trim().toLowerCase();
}

// Topic library filters run locally. The clinic directory owns its filters in clinics.js.
document.querySelectorAll('[data-filter-scope]').forEach((scope) => {
  const form = scope.querySelector('[data-filter-form]');
  const search = scope.querySelector('[data-search-input]');
  const category = scope.querySelector('[data-category-filter]');
  const items = [...scope.querySelectorAll('.filterable-item')];
  const count = scope.querySelector('[data-results-count]');
  const empty = scope.querySelector('[data-empty-state]');

  function updateFilters() {
    const query = normalise(search?.value || '');
    const selectedCategory = category?.value || 'all';
    let visible = 0;
    items.forEach((item) => {
      const matchesSearch = !query || normalise(item.dataset.search || item.textContent).includes(query);
      const matchesCategory = selectedCategory === 'all' || item.dataset.category === selectedCategory;
      item.hidden = !(matchesSearch && matchesCategory);
      if (!item.hidden) visible += 1;
    });
    const noun = visible === 1 ? 'topic' : 'topics';
    count.textContent = `${visible} ${noun}`;
    empty.hidden = visible !== 0;
  }

  form.addEventListener('submit', (event) => event.preventDefault());
  form.addEventListener('input', updateFilters);
  form.addEventListener('change', updateFilters);
  form.addEventListener('reset', () => requestAnimationFrame(updateFilters));
  scope.querySelectorAll('[data-clear-filters]').forEach((button) => {
    button.addEventListener('click', () => {
      form.reset();
      (search || category)?.focus();
    });
  });
  updateFilters();
});

function revealHashTarget() {
  let id;
  try { id = decodeURIComponent(location.hash.slice(1)); }
  catch { return; }
  const target = document.getElementById(id);
  if (target?.dataset.readingUrl) {
    // Keep bookmarks from the former expandable cards usable.
    location.replace(target.querySelector('[data-article-link]')?.href || target.dataset.readingUrl);
    return;
  }
  if (!(target instanceof HTMLDetailsElement)) return;
  const hiddenItem = target.closest('.filterable-item');
  if (hiddenItem?.hidden) target.closest('[data-filter-scope]')?.querySelector('form')?.reset();
  target.open = true;
  requestAnimationFrame(() => target.scrollIntoView({ block: 'start' }));
}
window.addEventListener('hashchange', revealHashTarget);
window.addEventListener('load', revealHashTarget);

// Long reading pages retain native anchor navigation. The contents list is
// compact above the article on smaller screens and remains beside it on desktop.
const readingContents = document.querySelector('[data-reading-contents]');
if (readingContents) {
  const desktopReading = window.matchMedia('(min-width: 1041px)');
  const links = [...readingContents.querySelectorAll('[data-reading-toc-link]')];
  const targets = links.map((link) => document.getElementById(link.hash.slice(1)));
  let readingScrollQueued = false;

  function setReadingContents() {
    readingContents.open = desktopReading.matches;
  }

  function updateReadingContents() {
    const rootStyle = getComputedStyle(document.documentElement);
    const gap = parseFloat(rootStyle.getPropertyValue('--space-6')) * parseFloat(rootStyle.fontSize);
    const threshold = document.querySelector('.site-header').getBoundingClientRect().bottom + gap;
    let active = targets[0];
    targets.forEach((target) => {
      if (target && target.getBoundingClientRect().top <= threshold) active = target;
    });
    links.forEach((link, index) => {
      if (targets[index] === active) link.setAttribute('aria-current', 'location');
      else link.removeAttribute('aria-current');
    });
    readingScrollQueued = false;
  }

  readingContents.addEventListener('click', (event) => {
    const link = event.target.closest('[data-reading-toc-link]');
    if (!link) return;
    const target = document.getElementById(link.hash.slice(1));
    if (target) target.focus({ preventScroll: true });
    if (!desktopReading.matches) readingContents.open = false;
  });

  window.addEventListener('scroll', () => {
    if (!readingScrollQueued) {
      readingScrollQueued = true;
      requestAnimationFrame(updateReadingContents);
    }
  }, { passive: true });
  window.addEventListener('resize', updateReadingContents, { passive: true });
  desktopReading.addEventListener('change', setReadingContents);
  setReadingContents();
  updateReadingContents();
}

document.querySelectorAll('[data-year]').forEach((element) => {
  element.textContent = String(new Date().getFullYear());
});
