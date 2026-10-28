'use strict';

// Booking links are normal anchors and work without JavaScript. Only the
// optional directory filters need this script; no patient data is collected.
document.querySelectorAll('[data-clinic-directory]').forEach((directory) => {
  const form = directory.querySelector('[data-clinic-form]');
  const search = form.elements.q;
  const locationField = form.elements.location;
  const platform = form.elements.platform;
  const cards = [...directory.querySelectorAll('.clinic-filterable')];
  const count = directory.querySelector('[data-clinic-count]');
  const empty = directory.querySelector('[data-clinic-empty]');
  const normalise = (value) => value.normalize('NFKD').replace(/[\u0300-\u036f]/g, '').trim().toLowerCase();
  const words = (value) => normalise(value).split(/[^\p{L}\p{N}]+/u).filter(Boolean);

  function readURL() {
    const params = new URL(window.location.href).searchParams;
    search.value = (params.get('q') || '').slice(0, search.maxLength);
    const selectedLocation = params.get('location');
    locationField.value = [...locationField.options].some((option) => option.value === selectedLocation) ? selectedLocation : 'all';
    const selectedPlatform = params.get('platform');
    platform.value = ['echannelling', 'doc990'].includes(selectedPlatform) ? selectedPlatform : 'all';
  }

  function writeURL() {
    const url = new URL(window.location.href);
    const values = { q: search.value.trim(), location: locationField.value, platform: platform.value };
    Object.entries(values).forEach(([name, value]) => {
      if (value && value !== 'all') url.searchParams.set(name, value);
      else url.searchParams.delete(name);
    });
    if (url.href !== window.location.href) {
      // Direct-file viewing is supported. Some browsers restrict history
      // changes on file URLs; filtering remains available in that case.
      try { window.history.replaceState(window.history.state, '', url); }
      catch { /* The filtering itself does not depend on URL persistence. */ }
    }
  }

  function update(syncURL = true) {
    const terms = words(search.value);
    let visible = 0;
    cards.forEach((card) => {
      const text = words(card.dataset.search);
      // Match word prefixes so Ragama does not also match Maharagama.
      const matches = terms.every((term) => text.some((word) => word.startsWith(term)))
        && (locationField.value === 'all' || card.dataset.location === locationField.value)
        && (platform.value === 'all' || card.dataset.platforms.split(' ').includes(platform.value));
      card.hidden = !matches;
      if (matches) visible += 1;
    });
    count.textContent = visible === cards.length ? `Showing ${visible} clinics` : `Showing ${visible} of ${cards.length} clinics`;
    empty.hidden = visible > 0;
    if (syncURL) writeURL();
  }

  form.addEventListener('submit', (event) => event.preventDefault());
  form.addEventListener('input', () => update());
  form.addEventListener('change', () => update());
  form.addEventListener('reset', () => queueMicrotask(() => update()));
  directory.querySelectorAll('[data-clear-clinic-filters]').forEach((button) => {
    button.addEventListener('click', () => {
      form.reset();
      search.focus({ preventScroll: true });
    });
  });
  window.addEventListener('popstate', () => { readURL(); update(false); });
  window.addEventListener('pageshow', () => { readURL(); update(false); });
  readURL();
  update(false);
  form.hidden = false;
});
