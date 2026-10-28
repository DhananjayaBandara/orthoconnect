#!/usr/bin/env node
'use strict';

// Optional real-browser verification; the website has no runtime dependencies.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { chromium } = require(process.env.ORTHOCONNECT_PLAYWRIGHT_MODULE || 'playwright');
const root = path.resolve(__dirname, '..');
const url = process.env.ORTHOCONNECT_PREVIEW_URL || 'http://127.0.0.1:8765/';
const screenshots = process.env.ORTHOCONNECT_SCREENSHOT_DIR;
let assertions = 0;
const errors = [];

function check(condition, message) {
  assert.ok(condition, message);
  assertions += 1;
}

async function open(browser, options = {}) {
  const context = await browser.newContext(options);
  const page = await context.newPage();
  page.on('pageerror', (error) => errors.push(error.message));
  page.on('response', (response) => {
    if (response.status() >= 400) errors.push(`${response.status()} ${response.url()}`);
  });
  await page.goto(url);
  await page.evaluate(() => document.fonts.ready);
  return { context, page };
}

async function settle(page) {
  // Smooth-scroll duration depends on distance. Wait for actual scroll motion
  // to settle rather than assuming a fixed animation duration.
  await page.waitForFunction(() => new Promise((resolve) => {
    let previous;
    let still = 0;
    function frame() {
      const track = document.querySelector('.resource-track');
      const position = `${window.scrollY}:${track?.scrollLeft}`;
      still = position === previous ? still + 1 : 0;
      previous = position;
      if (still >= 8) resolve(true);
      else requestAnimationFrame(frame);
    }
    requestAnimationFrame(frame);
  }), null, { timeout: 5000 });
  await page.waitForTimeout(200); // The debounced live-region announcement.
}

async function capture(page, name) {
  if (!screenshots) return;
  // Visit actual lazy images before a full-page capture, including the cards
  // initially outside the horizontal viewport. Restore the initial view.
  for (const img of await page.locator('main img').all()) {
    // Inactive banners are intentionally hidden; their images are warmed by
    // the slideshow instead of scrolling a hidden element into view.
    if (await img.evaluate((image) => Boolean(image.closest('.banner-slide')))) continue;
    await img.scrollIntoViewIfNeeded();
    await img.evaluate((image) => image.decode());
  }
  await page.locator('.resource-track').evaluate((track) => track.scrollTo({ left: 0, behavior: 'instant' }));
  await page.evaluate(() => window.scrollTo({ top: 0, behavior: 'instant' }));
  await settle(page);
  fs.mkdirSync(screenshots, { recursive: true });
  await page.screenshot({ path: path.join(screenshots, `homepage-${name}.png`), fullPage: true });
}

async function main() {
  const browser = await chromium.launch({ channel: process.env.ORTHOCONNECT_BROWSER_CHANNEL || 'chrome', headless: true });
  try {
    const { context, page } = await open(browser, { viewport: { width: 1440, height: 1000 } });
    const track = page.locator('.resource-track');
    const next = page.getByRole('button', { name: 'Next resources' });
    const previous = page.getByRole('button', { name: 'Previous resources' });
    check(await page.locator('.resource-slide').count() === 6, 'Six resources must remain available');
    check((await page.locator('[data-carousel-status]').textContent()).includes('1–3 of 6'), 'Desktop must show three resources');
    check(await previous.getAttribute('aria-disabled') === 'true', 'Previous must indicate the starting boundary');
    await next.click();
    await settle(page);
    check(await track.evaluate((element) => element.scrollLeft) > 200, 'Next must reveal additional resources');
    await previous.click();
    await settle(page);
    check(await track.evaluate((element) => element.scrollLeft) < 2, 'Previous must return to the first card');

    await track.focus();
    await page.keyboard.press('End');
    await settle(page);
    check(await next.getAttribute('aria-disabled') === 'true', 'End key must reach the last resources');
    await page.keyboard.press('Home');
    await settle(page);
    check(await track.evaluate((element) => element.scrollLeft) < 2, 'Home key must return to the start');
    await page.keyboard.press('ArrowRight');
    await settle(page);
    check(await track.evaluate((element) => element.scrollLeft) > 200, 'Arrow keys must browse the track');
    await page.keyboard.press('Home');
    await settle(page);
    await page.locator('.resource-slide:last-child h3 a').focus();
    check(await track.evaluate((element) => element.scrollLeft) > 500, 'Focused links in later cards must be brought into view');
    check(await page.locator('.resource-slide:last-child h3 a').evaluate((element) => element === document.activeElement), 'Carousel must preserve link focus');

    const shoulder = page.locator('.region-list [data-region="shoulder"]');
    await shoulder.focus();
    check(await page.locator('.region-marker.region-shoulder').evaluate((element) => element.classList.contains('is-active')), 'Keyboard focus must highlight the matching body marker');
    check(await shoulder.evaluate((element) => getComputedStyle(element).outlineStyle !== 'none'), 'Body-region links must have a visible focus indicator');
    for (const marker of await page.locator('.region-marker').all()) {
      const bounds = await marker.boundingBox();
      check(bounds.width >= 44 && bounds.height >= 44, 'Body markers must provide a 44px touch target');
    }
    await shoulder.click();
    await page.waitForURL('**/conditions.html#shoulder-elbow');
    check(await page.locator('#shoulder-elbow').getAttribute('open') !== null, 'Body-region navigation must reveal the matching condition');
    await page.goto(url);
    await page.locator('.region-list [data-region="spine"]').click();
    await page.waitForURL('**/articles/en-adult-spine.html');
    check(await page.locator('h1').count() === 1, 'Spine must open its existing reading page');
    await page.goto(url);

    check(await page.locator('.home-clinics .clinic-card').count() === 2, 'Home must feature two real clinics');
    check(await page.locator('.home-clinics [data-booking-provider="echannelling"]').count() === 1, 'Only Asia has a documented eChannelling link in the featured pair');
    check(await page.locator('.home-clinics [data-booking-provider="doc990"]').count() === 2, 'Both featured clinics have Doc990 links');
    check(await page.locator('dialog, [data-enquiry], [data-contact]').count() === 0, 'Demonstration dialogs and contact actions must be removed');

    await page.goto(new URL('clinics.html', url).href);
    check(await page.locator('.clinic-filterable:visible').count() === 18, 'Directory must show all 18 centres');
    await page.locator('#clinic-location').selectOption('Homagama');
    await page.locator('label[for="clinic-platform-doc990"]').click();
    check(await page.locator('.clinic-filterable:visible').count() === 1, 'Location and platform filters must intersect');
    check(await page.locator('.clinic-filterable:visible').getAttribute('id') === 'clinic-healan-hospitals-homagama', 'Healan is the documented Doc990 match');
    check(await page.locator('.clinic-filterable:visible [data-booking-provider]').count() === 2, 'Dual-provider cards retain both choices');
    await page.locator('#clinic-search').fill('Medihelp');
    check(await page.locator('[data-clinic-empty]').isVisible(), 'No-result state must be visible');
    await page.locator('[data-clinic-empty] [data-clear-clinic-filters]').click();
    check(await page.locator('.clinic-filterable:visible').count() === 18, 'Clear filters restores every centre');
    check(await page.locator('#clinic-search').evaluate((element) => element === document.activeElement), 'Clear returns keyboard focus to search');
    await page.locator('#clinic-search').fill('Ragama');
    check(await page.locator('.clinic-filterable:visible').count() === 2, 'Ragama must not include Maharagama');
    await page.reload();
    check(await page.locator('.clinic-filterable:visible').count() === 2, 'A reloaded URL must retain filters');

    // Test outbound same-tab navigation with local responses. No real booking
    // provider receives a request and no appointment is created.
    for (const provider of ['echannelling', 'doc990']) {
      const link = page.locator(`.clinic-filterable:visible [data-booking-provider="${provider}"]`).first();
      const destination = await link.getAttribute('href');
      await context.route(destination, (route) => route.fulfill({ status: 200, contentType: 'text/html', body: '<!doctype html><html lang="en"><title>Booking destination test</title><body>Sessions destination</body></html>' }));
      await link.click();
      await page.waitForURL(destination);
      check(page.url() === destination, 'Booking link must navigate to the exact hospital-specific destination');
      await page.goBack();
      check(await page.locator('.clinic-filterable:visible').count() === 2, 'Returning from a provider restores directory filters');
    }
    for (const width of [320, 360, 390, 540, 760, 768, 900, 1024, 1440]) {
      await page.setViewportSize({ width, height: 1000 });
      await page.evaluate(() => document.fonts.ready);
      check(await page.evaluate(() => document.documentElement.scrollWidth <= document.documentElement.clientWidth), `Directory must not overflow at ${width}px`);
      const columns = await page.locator('.clinic-directory-grid').evaluate((element) => getComputedStyle(element).gridTemplateColumns.split(' ').length);
      check(columns === (width <= 760 ? 1 : 2), `Expected responsive card columns at ${width}px`);
      for (const button of await page.locator('.clinic-filterable:visible [data-booking-provider]').all()) {
        const bounds = await button.boundingBox();
        check(bounds.width >= 44 && bounds.height >= 44, `Booking buttons must provide a 44px target at ${width}px`);
        check(await button.evaluate((element) => element.scrollWidth <= element.clientWidth), `Booking label must fit at ${width}px`);
      }
    }
    await page.goto(url);

    for (const [width, height] of [[320, 568], [360, 640], [390, 844], [740, 360], [760, 1000], [844, 390], [1024, 768], [1366, 768], [1440, 1000], [1912, 861]]) {
      await page.setViewportSize({ width, height });
      await page.evaluate(() => window.scrollTo({ top: 0, behavior: 'instant' }));
      await settle(page);
      check(await page.evaluate(() => document.documentElement.scrollWidth <= document.documentElement.clientWidth), `No page overflow at ${width}px`);
      const bannerBounds = await page.locator('[data-banner-carousel]').boundingBox();
      const viewportWidth = await page.evaluate(() => document.documentElement.clientWidth);
      check(Math.abs(bannerBounds.x) < 1 && Math.abs(bannerBounds.width - viewportWidth) < 1, `The banner must fill the window width at ${width} × ${height}`);
      const bottomActions = await page.locator('.mobile-actions').evaluate((element) => element.getBoundingClientRect().height);
      check(bannerBounds.y + bannerBounds.height <= height - bottomActions + 1, `The complete banner and dots must fit at ${width} × ${height}`);
      const imageBounds = await page.locator('.banner-slide.is-active img').boundingBox();
      check(Math.abs(imageBounds.width - viewportWidth) < 1, `The image must reach both window edges at ${width} × ${height}`);
      const desktopBanner = width >= 761;
      check(await page.locator('.banner-slide.is-active img').evaluate((element) => getComputedStyle(element).objectFit) === (desktopBanner ? 'contain' : 'cover'), 'Desktop banners must remain complete; mobile keeps its existing image fit');
      const selectedImage = await page.locator('.banner-slide.is-active img').evaluate((element) => element.currentSrc);
      check(selectedImage.includes('-carousel-1920x700.webp') === desktopBanner, `Artwork must match the desktop/mobile viewport at ${width}px`);
      check(await page.locator('[data-banner-carousel] .banner-toolbar, [data-banner-previous], [data-banner-next], [data-banner-playback]').count() === 0, 'Captions, arrows and playback buttons must remain removed');
    }
    await capture(page, 'desktop');
    await context.close();

    const mobile = await open(browser, { viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true });
    await mobile.page.getByRole('button', { name: 'Open navigation' }).click();
    check(await mobile.page.locator('.menu-toggle').getAttribute('aria-expanded') === 'true', 'Mobile menu must still open');
    await mobile.page.getByRole('button', { name: 'Close navigation' }).click();
    const mobileTrack = mobile.page.locator('.resource-track');
    await mobileTrack.scrollIntoViewIfNeeded();
    const bounds = await mobileTrack.boundingBox();
    check(await mobile.page.locator('.resource-slide').first().evaluate((element) => element.getBoundingClientRect().width) < bounds.width, 'Mobile must show a preview of the next card');
    const cdp = await mobile.context.newCDPSession(mobile.page);
    const startX = bounds.x + bounds.width - 25;
    const y = Math.min(650, Math.max(200, bounds.y + 180));
    await cdp.send('Input.dispatchTouchEvent', { type: 'touchStart', touchPoints: [{ x: startX, y }] });
    for (let step = 1; step <= 10; step += 1) {
      await cdp.send('Input.dispatchTouchEvent', { type: 'touchMove', touchPoints: [{ x: startX - step * 23, y }] });
      await mobile.page.waitForTimeout(20);
    }
    await cdp.send('Input.dispatchTouchEvent', { type: 'touchEnd', touchPoints: [] });
    await settle(mobile.page);
    check(await mobileTrack.evaluate((element) => element.scrollLeft) > 80, 'A real touch swipe must browse mobile resources');
    await capture(mobile.page, 'mobile');
    await mobile.context.close();

    const reduced = await open(browser, { viewport: { width: 1440, height: 1000 }, reducedMotion: 'reduce' });
    await reduced.page.getByRole('button', { name: 'Next resources' }).click();
    check(await reduced.page.locator('.resource-track').evaluate((element) => element.scrollLeft) > 200, 'Reduced-motion navigation must finish without smooth scrolling');
    check(await reduced.page.locator('.region-list a').first().evaluate((element) => getComputedStyle(element).transitionDuration === '0s'), 'Reduced motion must disable decorative transitions');
    const scroll = await reduced.page.locator('.resource-track').evaluate((element) => element.scrollLeft);
    await reduced.page.waitForTimeout(700);
    check(await reduced.page.locator('.resource-track').evaluate((element) => element.scrollLeft) === scroll, 'Carousel must stay still without user input');
    await reduced.context.close();

    const nojs = await open(browser, { javaScriptEnabled: false, viewport: { width: 390, height: 844 } });
    check(await nojs.page.locator('[data-carousel-controls]').isHidden(), 'Inert carousel controls must be hidden without JavaScript');
    check(await nojs.page.locator('.resource-slide').count() === 6, 'All six resources must remain available without JavaScript');
    check(await nojs.page.locator('.resource-track').evaluate((element) => getComputedStyle(element).display === 'grid'), 'Resources must become a normal grid without JavaScript');
    check(await nojs.page.evaluate(() => document.documentElement.scrollWidth <= document.documentElement.clientWidth), 'No-JavaScript mobile must not overflow');
    await nojs.page.locator('.region-list [data-region="hip"]').click();
    await nojs.page.waitForURL('**/conditions.html#hip');
    check(await nojs.page.locator('#hip').count() === 1, 'Body-region links must navigate without JavaScript');
    await nojs.context.close();

    const direct = await open(browser);
    await direct.page.goto(`file://${path.join(root, 'index.html')}`);
    check(await direct.page.locator('[data-resource-carousel]').getAttribute('data-carousel-ready') !== null, 'Direct-file preview must initialise the carousel');
    await direct.context.close();
    check(errors.length === 0, `No browser errors or failed HTTP resources: ${errors.join('; ')}`);
    console.log(`PASS: ${assertions} homepage browser assertions; desktop/mobile, touch, keyboard, reduced motion, no JavaScript, direct file, clinic filters and hospital-specific booking links.`);
    if (screenshots) console.log(`Previews: ${screenshots}`);
  } finally {
    await browser.close();
  }
}

main().catch((error) => { console.error(error); process.exitCode = 1; });
