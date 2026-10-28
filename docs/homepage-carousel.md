# Homepage banner carousel — 28 October 2026

The first homepage section below the shared header shows the four supplied banners in the requested order. The existing introduction and homepage sections follow it.

1. Orthopaedic surgeon profile → `about.html`.
2. Orthopaedic services → `treatments.html`.
3. Orthopaedic information → `patient-information.html`.
4. Consultation and appointments → `clinics.html`.

Desktop views use the newly supplied `01-carousel-1920x700.webp` through `04-carousel-1920x700.webp`, copied unchanged into `assets/images/home-banners/`. Each banner links to the corresponding page. Buttons and logos drawn inside the artwork remain image content; separate links or contacts have not been invented. Captions, counters, arrow buttons and pause/play buttons have been removed at the user's request. Only small slide dots remain below the image.

## Behaviour

Autoplay advances every two seconds with a 1000 ms ease-in-out crossfade and wraps from slide four to slide one. The outgoing slide remains fully painted below the incoming slide during the fade, preventing a flash of the background between images. Four slide dots support direct navigation. Left/right arrows and Home/End keys work while focus is inside the carousel. Horizontal touch gestures change banners while vertical gestures retain page scrolling. A completed swipe suppresses the incidental link click.

Autoplay pauses while the carousel has mouse hover or keyboard focus, when the document is hidden, while a touch is held, and when the carousel is off-screen. Leaving the interaction or returning to view starts a new full reading interval. Reduced-motion users have no autoplay or CSS fades and can navigate using the dots, keyboard or touch. Changes to the motion preference apply immediately.

Only the active slide is available to keyboard focus and assistive technology. Automatic rotation does not repeatedly announce slides. Manual navigation has a polite slide announcement. Without JavaScript, the first banner and its links remain usable and the inactive controls remain hidden. The lower article/guide carousel keeps its existing manual behaviour.

The carousel fills the window width without a maximum width or side margins. At widths of 761 px and above, the first matching `<picture>` source selects the new desktop image, and the frame follows the 1920:700 ratio. Desktop images use `object-fit: contain` so the complete image remains visible without stretching or cropping. At widths of 760 px and below, the existing responsive images, 1672:941 frame proportions and top-aligned `cover` fit remain in use.

Both layouts cap the frame height using the dynamic viewport height minus the header, the 44 px dots row and any fixed phone actions; `100vh` is the fallback for browsers without `100dvh`. JavaScript measures the actual header height and refreshes it on header/window resizing, with the existing responsive header token as the no-JavaScript fallback. On unusually short desktop windows, `contain` leaves space around the image to preserve its full contents. The supplied source images are unchanged.

Images have intrinsic dimensions, local WebP desktop/mobile sources and untouched PNG fallbacks. Each slide's `desktop` manifest record includes its path, 1920 × 700 dimensions, source filename and SHA-256. The four new desktop files total 402,960 bytes. The first image has high fetch priority; the next image is warmed before its turn. No package or third-party carousel library is needed by the website.

## Maintenance

Edit `content/home-carousel.json` to change the order, accessible titles, page links, alt text or `interval_ms`. The current value `2000` means two seconds. `scripts/homepage.py` renders the component, `scripts/home.js` handles the interaction, and `styles/home.css` handles its layout and fades. Regenerate the homepage with:

```sh
python3 -B scripts/build_site.py
python3 -B scripts/check_site.py
```

Do not hand-edit `index.html`. Restore the prior homepage by removing the `banner_carousel()` composition in `home()` and rebuilding; no inner-page content depends on this component.

## Executed verification and limits

- The site checker passes for all 70 generated routes, 56 reading pages, 5,384 local references and 19 existing stock-photo placements.
- The deterministic DOM check passes 79 assertions for desktop image checksums/dimensions/source priority, measured header height and resize updates, removed controls, banner order, original checksums/dimensions, responsive asset existence, two-second timer intervals, retained outgoing slide during fades, looping, slide dots, keyboard/swipe events, focus retention, reduced motion, document/intersection visibility and no-JavaScript fallback.
- The four desktop WebP files were decoded at 1920 × 700 and compared byte for byte with their Downloads originals. All earlier image assets retain their pre-change checksums.
- JavaScript syntax checks pass. The original logo, approved portrait, article assets and the 69 other HTML routes match the pre-change checksums.

The optional DOM test uses an already installed `jsdom` module; no dependency is added to the site:

```sh
ORTHOCONNECT_JSDOM_MODULE=/absolute/path/to/jsdom \
node scripts/check_home_banners_dom.cjs
```

This session denies local sockets with `PermissionError: [Errno 1] Operation not permitted`. Browser rendering, the visual fade, native keyboard/touch input and responsive geometry have not been verified. DOM event tests and CSS/source inspection do not establish those results. The optional `scripts/check_homepage.browser.cjs` includes desktop/mobile source selection, complete desktop image fit, full-width frame checks and viewport height limits at desktop, phone and landscape sizes, including the supplied 1912 × 861 screenshot size; these browser assertions have not been executed here. Earlier screenshots in `docs/previews/` predate this carousel. For a visual review, open `index.html` directly and inspect desktop/mobile artwork selection, all four images, the fade, dots, and reduced-motion behaviour. Nothing was published or deployed.
