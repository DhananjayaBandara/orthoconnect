'use strict';

// The supplied banners advance in order. Interaction, background tabs and
// off-screen placement pause the timer; reduced motion starts with autoplay off.
document.querySelectorAll('[data-banner-carousel]').forEach((carousel) => {
  const slides = [...carousel.querySelectorAll('.banner-slide')];
  const dots = [...carousel.querySelectorAll('[data-banner-dot]')];
  const viewport = carousel.querySelector('.banner-viewport');
  const header = document.querySelector('.site-header');
  const status = carousel.querySelector('[data-banner-status]');
  const motion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const interval = Number(carousel.dataset.bannerInterval) || 2000;
  let current = 0;
  let hovered = false;
  let focused = carousel.contains(document.activeElement);
  let inView = !('IntersectionObserver' in window);
  let timer;
  let touch;
  let suppressClickUntil = 0;

  function measureHeader() {
    const height = header?.getBoundingClientRect().height;
    if (height) carousel.style.setProperty('--banner-header-height', `${height}px`);
  }
  measureHeader();
  if (header && 'ResizeObserver' in window) new ResizeObserver(measureHeader).observe(header);
  window.addEventListener('resize', measureHeader, { passive: true });

  function schedule() {
    window.clearTimeout(timer);
    const playing = !motion.matches && !hovered && !focused && !touch && inView && !document.hidden;
    carousel.dataset.bannerPlaying = String(playing);
    status.setAttribute('aria-live', playing ? 'off' : 'polite');
    if (playing) timer = window.setTimeout(() => show(current + 1), interval);
  }

  function show(index, announce = false) {
    const previous = current;
    current = (index + slides.length) % slides.length;
    slides.forEach((slide, position) => {
      const active = position === current;
      // Retain the outgoing image beneath the incoming fade. This keeps the
      // transition fully painted instead of fading both images to the backdrop.
      slide.classList.toggle('is-previous', previous !== current && position === previous);
      slide.classList.toggle('is-active', active);
      slide.toggleAttribute('inert', !active);
      if (active) slide.removeAttribute('aria-hidden');
      else slide.setAttribute('aria-hidden', 'true');
      if (active) dots[position].setAttribute('aria-current', 'true');
      else dots[position].removeAttribute('aria-current');
    });
    const active = slides[current];
    // Warm the next image so the fade does not reveal an unloaded banner.
    [active, slides[(current + 1) % slides.length]].forEach((slide) => {
      slide.querySelector('img').loading = 'eager';
    });
    carousel.dataset.bannerIndex = String(current);
    schedule();
    if (announce) status.textContent = `Slide ${current + 1} of ${slides.length}: ${active.dataset.bannerTitle}`;
  }

  dots.forEach((dot, index) => dot.addEventListener('click', () => show(index, true)));
  carousel.addEventListener('pointerenter', (event) => {
    if (event.pointerType === 'touch') return;
    hovered = true;
    schedule();
  });
  carousel.addEventListener('pointerleave', () => { hovered = false; schedule(); });
  carousel.addEventListener('focusin', () => { focused = true; schedule(); });
  carousel.addEventListener('focusout', () => {
    // Focus may be moving to another control inside the same carousel.
    window.queueMicrotask(() => { focused = carousel.contains(document.activeElement); schedule(); });
  });
  carousel.addEventListener('keydown', (event) => {
    if (event.altKey || event.ctrlKey || event.metaKey) return;
    const target = { ArrowLeft: current - 1, ArrowRight: current + 1, Home: 0, End: slides.length - 1 }[event.key];
    if (target === undefined) return;
    event.preventDefault();
    show(target, true);
  });
  viewport.addEventListener('touchstart', (event) => {
    const point = event.touches.length === 1 ? event.touches[0] : null;
    touch = point ? { x: point.clientX, y: point.clientY } : null;
    suppressClickUntil = 0;
    schedule();
  }, { passive: true });
  viewport.addEventListener('touchend', (event) => {
    if (touch && event.changedTouches.length) {
      const dx = event.changedTouches[0].clientX - touch.x;
      const dy = event.changedTouches[0].clientY - touch.y;
      if (Math.abs(dx) > 50 && Math.abs(dx) > Math.abs(dy) * 1.5) {
        suppressClickUntil = performance.now() + 500;
        show(current + (dx < 0 ? 1 : -1), true);
      }
    }
    touch = null;
    schedule();
  }, { passive: true });
  viewport.addEventListener('touchcancel', () => { touch = null; schedule(); }, { passive: true });
  viewport.addEventListener('click', (event) => {
    if (performance.now() < suppressClickUntil) {
      event.preventDefault();
      event.stopPropagation();
    }
  }, true);
  document.addEventListener('visibilitychange', schedule);
  motion.addEventListener('change', schedule);
  if ('IntersectionObserver' in window) {
    new IntersectionObserver(([entry]) => { inView = entry.isIntersecting; schedule(); }).observe(carousel);
  }
  carousel.querySelector('[data-banner-controls]').hidden = false;
  carousel.setAttribute('data-banner-ready', '');
  show(0);
});

// Links work on their own. Hover and focus only connect matching visual cues.
document.querySelectorAll('[data-body-explorer]').forEach((explorer) => {
  const links = [...explorer.querySelectorAll('[data-region]')];
  const highlight = (region) => links.forEach((link) => {
    link.classList.toggle('is-active', link.dataset.region === region);
  });
  links.forEach((link) => {
    link.addEventListener('pointerenter', () => highlight(link.dataset.region));
    link.addEventListener('focus', () => highlight(link.dataset.region));
    link.addEventListener('pointerleave', () => highlight(document.activeElement?.dataset.region));
    link.addEventListener('blur', () => highlight(null));
  });
});

// Native horizontal scrolling supplies touch/trackpad support. No autoplay,
// cloned slides, hidden cards, timers for movement, or focus reassignment.
document.querySelectorAll('[data-resource-carousel]').forEach((carousel) => {
  const track = carousel.querySelector('.resource-track');
  const slides = [...track.children];
  const previous = carousel.querySelector('.carousel-previous');
  const next = carousel.querySelector('.carousel-next');
  const status = carousel.querySelector('[data-carousel-status]');
  const motion = window.matchMedia('(prefers-reduced-motion: reduce)');
  let announcement;

  function update(announce = true) {
    const bounds = track.getBoundingClientRect();
    const visible = slides.map((slide, index) => ({ index, rect: slide.getBoundingClientRect() }))
      .filter(({ rect }) => rect.left >= bounds.left - 2 && rect.right <= bounds.right + 2);
    const first = visible[0]?.index ?? slides.findIndex((slide) => slide.getBoundingClientRect().right > bounds.left + 12);
    const last = visible.at(-1)?.index ?? first;
    const atStart = track.scrollLeft <= 2;
    const atEnd = track.scrollLeft + track.clientWidth >= track.scrollWidth - 2;
    previous.setAttribute('aria-disabled', String(atStart));
    next.setAttribute('aria-disabled', String(atEnd));
    if (announce) {
      const range = first === last ? `${first + 1}` : `${first + 1}–${last + 1}`;
      const message = `Showing ${range} of ${slides.length} resources`;
      if (status.textContent !== message) status.textContent = message;
    }
  }

  function move(direction, endpoint = false) {
    if ((direction < 0 ? previous : next).getAttribute('aria-disabled') === 'true') return;
    const step = slides[1] ? slides[1].offsetLeft - slides[0].offsetLeft : track.clientWidth;
    const left = endpoint ? (direction < 0 ? 0 : track.scrollWidth) : track.scrollLeft + direction * step;
    track.scrollTo({ left, behavior: motion.matches ? 'instant' : 'smooth' });
  }

  previous.addEventListener('click', () => move(-1));
  next.addEventListener('click', () => move(1));
  track.addEventListener('keydown', (event) => {
    if (event.target !== track) return;
    if (['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) {
      event.preventDefault();
      move(['ArrowLeft', 'Home'].includes(event.key) ? -1 : 1, ['Home', 'End'].includes(event.key));
    }
  });
  track.addEventListener('scroll', () => {
    update(false);
    clearTimeout(announcement);
    announcement = setTimeout(update, 180);
  }, { passive: true });
  track.addEventListener('focusin', (event) => {
    const slide = event.target.closest('.resource-slide');
    if (!slide) return;
    const bounds = track.getBoundingClientRect();
    const rect = slide.getBoundingClientRect();
    if (rect.left < bounds.left || rect.right > bounds.right) {
      // Scroll only this container: focusing a link must not move the page.
      track.scrollBy({ left: rect.left - bounds.left - 8, behavior: 'instant' });
    }
  });
  carousel.setAttribute('data-carousel-ready', '');
  track.tabIndex = 0;
  track.setAttribute('aria-label', 'Featured resources. Use the arrow keys to browse.');
  carousel.querySelector('[data-carousel-controls]').hidden = false;
  new ResizeObserver(() => update()).observe(track);
  update();
});
