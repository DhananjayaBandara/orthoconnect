'use strict';

// Article collections are independent. Query parameters carry browsing context
// through ordinary links, including new tabs, without browser storage.
(() => {
  const filterKeys = ['lang', 'audience', 'region', 'topic', 'q'];
  const library = document.querySelector('[data-article-library]');

  function cleanParams(params) {
    const clean = new URLSearchParams();
    filterKeys.forEach((key) => {
      const value = (params.get(key) || '').trim().slice(0, key === 'q' ? 160 : 64);
      if (!value || value === 'all') return;
      if (key === 'lang' && !['en', 'si'].includes(value)) return;
      if (key === 'audience' && !['adult', 'children'].includes(value)) return;
      if (['region', 'topic'].includes(key) && !/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(value)) return;
      clean.set(key, value);
    });
    return clean;
  }

  function carryContext(params) {
    const context = params.toString();
    document.querySelectorAll('[data-article-link]').forEach((link) => {
      const destination = new URL(link.getAttribute('href'), window.location.href);
      // An empty library parameter deliberately means the unfiltered collection.
      destination.searchParams.set('library', context);
      link.setAttribute('href', destination.pathname.split('/').pop() + destination.search + destination.hash);
      if (library) {
        // Listing links live one directory above the independent reading pages.
        link.setAttribute('href', `articles/${destination.pathname.split('/').pop()}${destination.search}${destination.hash}`);
      }
    });
    document.querySelectorAll('[data-article-return]').forEach((link) => {
      link.setAttribute('href', `../articles.html${context ? `?${context}` : ''}`);
    });
  }

  if (!library) {
    // The parent Articles item in both navigation menus is also a return route.
    document.querySelectorAll('#primary-navigation a[aria-current="location"], .footer-navigation a[aria-current="location"]').forEach((link) => {
      link.setAttribute('data-article-return', '');
    });
    const current = new URLSearchParams(window.location.search);
    const params = current.has('library')
      ? cleanParams(new URLSearchParams(current.get('library')))
      : cleanParams(new URLSearchParams({ lang: document.documentElement.lang }));
    carryContext(params);
    return;
  }

  const form = library.querySelector('[data-article-form]');
  const count = library.querySelector('[data-article-count]');
  const empty = library.querySelector('[data-article-empty]');
  const controls = {
    audience: form.elements.namedItem('audience'),
    region: form.elements.namedItem('region'),
    topic: form.elements.namedItem('topic'),
    q: form.elements.namedItem('q'),
  };
  const items = [...library.querySelectorAll('.filterable-item')].map((element) => ({
    element,
    language: element.dataset.language,
    audiences: JSON.parse(element.dataset.audiences),
    regions: JSON.parse(element.dataset.regions),
    topics: JSON.parse(element.dataset.topics),
    search: normalise(element.dataset.search),
  }));

  function normalise(value) {
    // NFC preserves Sinhala vowel signs and recognises canonical equivalents.
    return value.normalize('NFC').toLocaleLowerCase().trim();
  }

  function readForm() {
    const params = new URLSearchParams();
    params.set('lang', form.querySelector('input[name="lang"]:checked').value);
    Object.entries(controls).forEach(([key, control]) => params.set(key, control.value));
    return cleanParams(params);
  }

  function applyParams(params) {
    const language = params.get('lang') || 'all';
    form.querySelectorAll('input[name="lang"]').forEach((input) => { input.checked = input.value === language; });
    Object.entries(controls).forEach(([key, control]) => {
      const value = params.get(key) || (key === 'q' ? '' : 'all');
      control.value = key === 'q' || [...control.options].some((option) => option.value === value) ? value : 'all';
    });
  }

  function update() {
    const params = readForm();
    const words = normalise(params.get('q') || '').split(/\s+/).filter(Boolean);
    const selectedLanguage = params.get('lang');
    const audience = params.get('audience');
    const region = params.get('region');
    const topic = params.get('topic');
    let visible = 0;
    let english = 0;
    let sinhala = 0;
    items.forEach((item) => {
      const matches = (!selectedLanguage || item.language === selectedLanguage)
        && (!audience || item.audiences.includes(audience))
        && (!region || item.regions.includes(region))
        && (!topic || item.topics.includes(topic))
        && words.every((word) => item.search.includes(word));
      item.element.hidden = !matches;
      if (matches) {
        visible += 1;
        english += item.language === 'en' ? 1 : 0;
        sinhala += item.language === 'si' ? 1 : 0;
      }
    });
    count.replaceChildren(document.createTextNode(`${visible} ${visible === 1 ? 'article' : 'articles'} · ${english} English · `));
    const sinhalaCount = document.createElement('span');
    sinhalaCount.lang = 'si';
    sinhalaCount.textContent = `${sinhala} සිංහල`;
    count.append(sinhalaCount);
    empty.hidden = visible !== 0;
    carryContext(params);
    const destination = new URL(window.location.href);
    destination.search = params.toString();
    try {
      window.history.replaceState(null, '', destination);
    } catch {
      // Restricted file viewers can disallow History API updates. Decorated
      // article links still preserve the selected filters for return navigation.
    }
  }

  function restoreFromURL() {
    applyParams(cleanParams(new URLSearchParams(window.location.search)));
    update();
  }

  form.addEventListener('submit', (event) => { event.preventDefault(); update(); });
  form.addEventListener('input', update);
  form.addEventListener('change', update);
  form.addEventListener('reset', () => { queueMicrotask(update); });
  library.querySelector('[data-article-reset]').addEventListener('click', () => {
    form.reset();
    controls.q.focus();
  });
  window.addEventListener('popstate', restoreFromURL);
  window.addEventListener('pageshow', restoreFromURL);
  restoreFromURL();
})();
