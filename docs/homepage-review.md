# Homepage design review — 25 October 2026

The enhanced homepage is ready for design review. Open `index.html` directly, or serve this directory using the command in the README. The other 69 generated HTML files remain byte-identical to the pre-change snapshot. Only the homepage includes the new stylesheet and script.

## Changes

- Soft teal/cream hero gradients, the existing decorative knee outline, an arched portrait frame, and restrained interaction feedback. The supplied portrait and complete original logo are unchanged.
- A numbered SVG/CSS body-region navigator with seven matching text links. Shoulder and elbow intentionally share the existing Conditions destination; spine opens the supplied English spine article. Existing six condition summaries remain available.
- Three consultation steps linking to existing location, booking and preparation information. Sample clinic notices, booking dialogs and transient enquiry behaviour are preserved.
- A manual resource carousel containing the existing three article previews and three patient guides. It shows three cards on desktop and a partial next card on mobile, supports native horizontal touch scrolling, previous/next buttons, keyboard browsing and focus visibility, and announces the visible range. No cards are cloned or automatically advanced. Without JavaScript, all six cards form a regular grid and the inactive controls remain hidden.
- A locally hosted, credited walking photograph in the consultation callout, plus guide thumbnails. The callout keeps its text on a solid panel.

## Image and illustration sources

The new walking photograph is by [Noelle Otto on Pexels](https://www.pexels.com/photo/old-couple-walking-while-holding-hands-906111/), under the [Pexels licence](https://www.pexels.com/license/). The source and licence pages were checked for this change. The 640px and 1280px local JPEG variants are approximately 56 KiB and 174 KiB, use responsive source selection, and load lazily below the fold. Credits, dimensions and SHA-256 checksums are retained in `content/stock-assets.lock.json`; the source, alternative text and photographer are in `content/stock-images.json`.

Existing thumbnail photography and the fracture illustration are reused. The body silhouette is original navigation artwork; the decorative knee outline comes from the existing sprite. No diagnostic or procedure diagram has been added. Future clinical diagrams should receive clinical review before publication. Existing educational drafts and review labels are preserved.

## Validation

- `python3 -B scripts/build_site.py`: 70 routes rebuilt from source.
- `python3 -B scripts/check_site.py`: passed for all 70 routes, 56 reading pages, 5,597 local references and 35 stock-photo placements.
- `python3 -B scripts/check_article_migration.py`: all 40 imported articles, their text/order, 390 image placements and 251 original image checksums remain intact.
- `python3 -B scripts/download_images.py --check`: all ten expected stock JPEGs passed.
- JavaScript syntax checks passed for the new interaction and browser-check scripts.
- `scripts/check_homepage.browser.cjs`: **43 assertions passed in actual Chrome**, using the already installed Playwright package from the separate WordPress checkout. No dependency was installed into this site.

Browser checks cover desktop and mobile layouts; page overflow at 320, 360, 390, 760, 1024 and 1440 CSS pixels; body-region navigation and focus; 44px marker targets; carousel buttons, arrow/Home/End keys and focus scrolling; an actual emulated touch swipe; reduced motion; JavaScript-disabled access; direct-file opening; and existing booking/enquiry previews. No JavaScript errors or failed HTTP resources were observed. The source photographs and the rendered homepage hero, navigator, resource cards and callout were visually inspected at desktop and mobile sizes.

Saved previews: [desktop](previews/homepage-desktop.png) and [mobile](previews/homepage-mobile.png). Full-page browser captures can show fixed mobile controls at the capture viewport boundary.

To repeat the optional browser check, start the preview server, then point the checker to an existing Playwright installation:

```sh
python3 -m http.server 8765 --bind 127.0.0.1
```

In a second terminal:

```sh
ORTHOCONNECT_PLAYWRIGHT_MODULE=/absolute/path/to/playwright \
ORTHOCONNECT_SCREENSHOT_DIR=docs/previews \
node scripts/check_homepage.browser.cjs
```

The checker defaults to locally installed Google Chrome. Set `ORTHOCONNECT_BROWSER_CHANNEL` or `ORTHOCONNECT_PREVIEW_URL` if needed. The site itself needs no Node packages.

These checks cover the homepage enhancements and relevant navigation/booking regressions. They are not a complete accessibility, clinical, or browser audit of every reading page. Design changes to the remaining routes and publication are outside this review stage.

## Source files

`scripts/homepage.py` contains the homepage components, composed by `scripts/build_site.py`. `styles/home.css` and `scripts/home.js` contain the scoped presentation and interactions. Existing shared CSS, shared JavaScript, clinical content JSON and archived article assets are unchanged. To revise the design, edit these source files and rebuild; do not hand-edit generated HTML.
