'use strict';

// Optional visual enhancement. Content starts visible, native links/disclosures
// retain their behaviour, and no animation is needed to use the website.
(() => {
  const motion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const header = document.querySelector('.site-header');
  const progress = document.querySelector('[data-reading-progress]');
  const article = document.querySelector('.reading-article');
  const fill = progress?.querySelector('[data-reading-progress-fill]');
  const active = new Set();
  const running = new WeakMap();
  const seen = new WeakSet();
  let observer;
  let framePending = false;

  function stop(element) {
    const animation = running.get(element);
    if (animation) {
      animation.cancel();
      active.delete(animation);
      running.delete(element);
    }
  }

  function animate(element, frames, options) {
    if (motion.matches || !element?.animate) return;
    stop(element);
    const animation = element.animate(frames, options);
    active.add(animation);
    running.set(element, animation);
    const clean = () => {
      active.delete(animation);
      if (running.get(element) === animation) running.delete(element);
    };
    animation.finished?.then(clean, clean);
  }

  function updateScrollUI() {
    framePending = false;
    const scroll = Math.max(0, window.scrollY);
    header?.classList.toggle('is-scrolled', scroll > 12);
    if (!progress || !article) return;
    const headerBottom = Math.max(0, header?.getBoundingClientRect().bottom || 0);
    const bounds = article.getBoundingClientRect();
    const start = bounds.top + scroll - headerBottom - 24;
    const end = bounds.bottom + scroll - window.innerHeight + 24;
    const distance = end - start;
    const ratio = distance > 0 ? Math.max(0, Math.min(1, (scroll - start) / distance)) : (scroll >= start ? 1 : 0);
    progress.style.top = `${headerBottom}px`;
    fill.style.transform = `scaleX(${ratio})`;
    progress.dataset.progress = String(Math.round(ratio * 100));
    progress.hidden = false;
  }

  function scheduleScrollUI() {
    if (framePending) return;
    framePending = true;
    requestAnimationFrame(updateScrollUI);
  }

  // Reveal selected introduction groups only. Clinic results, filters, the hero
  // copy and every reading paragraph stay immediately visible and stationary.
  const groups = {
    home: '.section-heading, .expertise-card, .body-explorer, .consultation-journey > li, .home-photo-callout',
    about: '.qualification-card, .training-timeline > li, .fellowship-layout > div',
  };
  const selector = groups[document.body.dataset.page];
  const targets = selector ? [...document.querySelectorAll(selector)] : [];
  targets.forEach((element) => element.setAttribute('data-reveal', ''));

  function installReveals() {
    observer?.disconnect();
    if (motion.matches || !window.IntersectionObserver || !Element.prototype.animate) return;
    observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting || seen.has(entry.target)) return;
        const element = entry.target;
        seen.add(element);
        observer.unobserve(element);
        if (entry.boundingClientRect.top < 0 || element.contains(document.activeElement) || document.hidden) return;
        const delay = (targets.indexOf(element) % 3) * 45;
        animate(element, [{ opacity: 0, transform: 'translateY(10px)' }, { opacity: 1, transform: 'translateY(0)' }], {
          duration: 340, delay, easing: 'cubic-bezier(.2,.65,.3,1)', fill: 'backwards',
        });
      });
    }, { threshold: 0.08, rootMargin: '0px 0px -24px 0px' });
    targets.forEach((element) => {
      if (seen.has(element)) return;
      // Above-the-fold content and restored anchor targets never wait for or
      // replay an entrance. Default styles remain visible even if JS fails.
      if (location.hash || element.getBoundingClientRect().top < window.innerHeight) seen.add(element);
      else observer.observe(element);
    });
  }

  function updateMotionPreference() {
    document.documentElement.classList.toggle('motion-reduced', motion.matches);
    if (motion.matches) {
      active.forEach((animation) => animation.cancel());
      active.clear();
    }
    installReveals();
  }

  document.querySelectorAll('.faq-item, .topic-details, .reading-contents').forEach((details) => {
    details.addEventListener('toggle', () => {
      const body = details.querySelector('.disclosure-body, .topic-body, nav');
      if (!body) return;
      if (!details.open) { stop(body); return; }
      animate(body, [{ opacity: 0.4, transform: 'translateY(-4px)' }, { opacity: 1, transform: 'translateY(0)' }], { duration: 180, easing: 'ease-out' });
    });
  });
  document.addEventListener('focusin', (event) => {
    const group = event.target.closest('[data-reveal]');
    if (group) { stop(group); seen.add(group); observer?.unobserve(group); }
  });
  window.addEventListener('scroll', scheduleScrollUI, { passive: true });
  window.addEventListener('resize', scheduleScrollUI, { passive: true });
  window.addEventListener('pageshow', () => { updateScrollUI(); installReveals(); });
  window.addEventListener('pagehide', () => {
    active.forEach((animation) => animation.cancel());
    active.clear();
    observer?.disconnect();
  });
  motion.addEventListener('change', updateMotionPreference);
  if (article) {
    article.addEventListener('load', scheduleScrollUI, true);
    if (window.ResizeObserver) new ResizeObserver(scheduleScrollUI).observe(article);
    document.fonts?.ready?.then(scheduleScrollUI);
  }
  updateMotionPreference();
  updateScrollUI();
  const portrait = document.querySelector('.home-hero .portrait-frame');
  if (portrait && !location.hash && window.scrollY < 12) {
    animate(portrait, [{ opacity: 0.65, transform: 'translateY(8px)' }, { opacity: 1, transform: 'translateY(0)' }], { duration: 380, easing: 'ease-out' });
  }
})();
