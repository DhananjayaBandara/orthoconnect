# 07 — Frontend Architecture

Evidence legend: **CONFIRMED · INFERRED · DOCUMENTED · NOT IMPLEMENTED · UNKNOWN**.
Line references are to the files at `f4903c9`. **Never hand-edit the generated `*.html`** — edit the generator/JSON and rebuild.

## 1. How the visual interface is assembled

```
content/*.json ─┐
Python templates ├─► scripts/build_site.py ─► write_page() ─► <page>.html (single minified-style line per section)
assets/icons ────┘                                   │
                                                     ├─ <head>: meta, preload font, tokens.css, main.css, [home.css], effects.css, deferred JS
                                                     └─ <body data-page="…">: inline SVG sprite → skip link → header → [progress bar] → <main id="main"> → footer → mobile bar
```

`write_page()` (`build_site.py` L346-371) is the only place that emits the document skeleton:

| Part | Detail | Evidence |
|---|---|---|
| Doctype / language | `<!doctype html><html lang="en|si">` — `si` for the 21 Sinhala articles (49 en / 21 si pages) | CONFIRMED |
| Meta | `charset`, `viewport`, **`robots: noindex,nofollow`**, `description` (page summary), `theme-color #12334b`, `<title>… | OrthoConnect</title>`, favicon = the logo JPEG | CONFIRMED |
| Font preload | `noto-sans-regular.ttf` (or Sinhala Regular for `lang=si`) | CONFIRMED |
| Styles | `tokens.css` → `main.css` → (`home.css` on the homepage) → `effects.css`. *Note the order:* `home.css` is injected via `article_script` **before** `effects.css` | CONFIRMED |
| Scripts | `main.js` (+ `articles.js` / `clinics.js` / `home.js`) then `effects.js`, all `defer` | CONFIRMED |
| Body | `id="top" data-page="<active>"`; the 3.6 KB SVG sprite is **inlined in every page** (ids rewritten to `icon-*`) so `file://` works | CONFIRMED |
| Nested pages | `aria-current="page"` becomes `"location"` for reading pages; reading-progress bar markup is added; all URLs are rewritten relative to the page's directory | CONFIRMED |

Missing from `<head>` (CONFIRMED): canonical, Open Graph/Twitter, JSON-LD, hreflang, manifest, apple-touch-icon, CSP/referrer meta.

## 2. Page templates

| Template | Pages | Built by |
|---|---|---|
| **Home** | `index.html` | `home()` — banner carousel + hero + 5 sections + photo callout |
| **Inner page with title band** | About, Conditions, Treatments, Patient Information, Clinics, Articles, Contact, Privacy, Terms | `page_title()` (breadcrumb, eyebrow, H1, intro, optional section motif) + section(s) + `cta()` |
| **Library/listing** | Conditions, Treatments, Patient Information (`library_page()`), Articles (`article_listing()`), Clinics (`clinics()`) | filter form + grid + empty state |
| **Reading page** | 56 pages | `reading_page()` / `article_reading_page()` — header band, sticky "On this page" sidebar + article column, related cards, CTA |
| **Focused layouts** | Privacy, Terms (`.legal-layout`), 404 (`.not-found`) | — |
| **Aliases** | 3 | verbatim copies |

## 3. Shared components

| Component | Generator function | CSS | JS |
|---|---|---|---|
| Header + nav + CTA + menu toggle | `header()` | `.site-header`, `.primary-navigation`, `.menu-toggle` (main.css L56-70) | `main.js` L5-43 |
| Footer + mobile action bar | `footer()` | `.site-footer` (L23), `.mobile-actions` (L370) | `main.js` L153 |
| Buttons (`primary`, `outline`, `booking`) | `button()` | `.button*` (L39) | — |
| Icon (SVG `<use>`) | `icon()` | `.icon`, `.icon-large` | — |
| Section heading, CTA band | `section_head()`, `cta()` | `.section-heading`, `.cta-band` (L111) | — |
| Breadcrumb / page title | `page_title()`, reading `breadcrumbs` | `.page-title`, `.breadcrumbs` (L116-117) | `articles.js` rewrites return links |
| Topic / reading / article cards | `topic_card()`, `reading_card()`, `article_card()` | `.topic-card` (L94), `.article-library-card` | filters in `main.js` / `articles.js` |
| Clinic card + provider buttons | `clinic_card()` | `.clinic-card` (L305), `.button-booking` | `clinics.js` |
| Filter forms | `library_filters()`, `article_filters()`, `clinics()` form | `.filters`, `.article-controls` (L184), `.clinic-filters` (L292) | as above |
| FAQ / topic disclosure | `<details class="faq-item|topic-details">` | `.faq-item` (L284) | `effects.js` animates; `main.js` opens on hash |
| Empty state / notices | `.empty-state`, `.notice`, `.emergency-note` | L274, L289, L340 | toggled via `hidden` |
| Reading layout (sidebar + article, tables, figures, callouts) | `reading_page()`, `render_blocks()` | `.reading-layout` (L225), `.reading-table-wrap` (L259), `.reading-inline-figure` (L247) | scroll-spy `main.js` L105-151 |
| Banner carousel / resource carousel / body explorer / journey / photo callout | `homepage.py` | `home.css` (L7, L23, L82, L132, L141, L165) | `home.js` |

## 4. CSS architecture

**Four hand-written files, no preprocessor, no framework** (990 lines, ≈78 KiB):

| File | Lines | Scope | Notes |
|---|---:|---|---|
| `styles/tokens.css` | 140 | `:root` design tokens (118) + one `@media (max-width:760px)` override | single source of design constants |
| `styles/main.css` | 524 | `@font-face` ×4; reset; layout; **all shared components**; reading layout; print | one monolith, organised by short section comments (L56, 61, 71, 153, 183, 222) |
| `styles/effects.css` | 103 | hover/focus feedback, header shadow, reveals, progress bar, reduced-motion, fine-pointer hover | loaded **after** `main.css` on every page |
| `styles/home.css` | 223 | homepage-only components | loaded only on `index.html` |

* **Naming:** kebab-case, component-prefixed (BEM-lite without `__`/`--`), state classes `is-active|is-open|is-previous|is-scrolled`, mode classes `js-enabled`, `motion-reduced`.
* **Specificity discipline:** only 15 `!important` in total; 11 `z-index` declarations using 7 distinct values (tokens `--z-header: 20`, `--z-menu: 30`, plus `calc()` offsets and 0/1/2).
* **Inline styles:** only 7 on the homepage — the `--region-x/y` custom properties positioning body-map markers.
* **Progressive enhancement via the `hidden` attribute:** JS reveals filter forms/controls (`form.hidden = false`), so no-JS users never see inert controls.
* **Print:** `@media print` in all three non-token files.

### 4.1 Design tokens (`tokens.css`)

**Palette**

| Token | Hex | Role | Contrast vs white (computed WCAG 2.x) |
|---|---|---|---|
| `--color-ink` | `#17364b` | headings | 12.61 |
| `--color-navy` | `#12334b` | header/CTA panels, `theme-color` | 13.12 (white on navy) |
| `--color-text` | `#455b69` | body text | 7.11 |
| `--color-muted` | `#5b6d7a` | secondary text | 5.37 (4.98 on `#f4f7f8`) |
| `--color-teal` / `-dark` | `#007575` / `#006263` | links, primary buttons, focus ring | 5.52 / 7.17 |
| `--color-accent` | `#bf4c32` | coral accent, booking focus | 4.89 (white on accent 4.89). Accent on `--color-accent-light` `#fcf0eb` computes to 4.38 (AA-large only), but that pairing is **not used for text**: `--color-accent-light` is only the `.emergency-note` background (`main.css:340`), where the accent appears as a border |
| `--color-teal-light`, `-line` | `#e6f2f0`, `#bddbd6` | tints/borders | teal on teal-light 4.82 |
| `--color-surface`, `-hero`, `-border` | `#f4f7f8`, `#eef5f4`, `#dce5e8` | backgrounds | — |
| `--color-dark-text`, `-line`, `-accent` | `#c6d8e2`, `#355166`, `#88d2c8` | footer/dark panels | 8.95 on navy |

**Typography:** `--font-body: 'Noto Sans','Noto Sans Sinhala',Arial,sans-serif`; sizes from `0.75rem` to `clamp(2.25rem,4.3vw,3.5rem)`; reading text `1.125rem / 1.85`; Sinhala line-height `2`; weights 400/700 only; negative tracking on headings (`-0.045em … -0.012em`) and `0.12em` on eyebrow labels.

**Spacing scale:** `--space-1 … --space-16` (0.25 rem … 6 rem), `--section-space: clamp(3rem,5.7vw,5rem)`, `--page-gutter: clamp(1.25rem,4vw,2.5rem)`, container `75rem`, reading article `46rem` + sidebar `17.5rem` + gap `4rem`.

**Other:** radii (4/8/12 px, pill), three shadows, transition `160ms ease`, `--tap-size: 2.75rem` (44 px), `--focus-width: 3px`, `--header-height: 7.25rem` (5.75rem ≤760 px), logo framing tokens (`--logo-source-*` crop the white margin of the supplied JPEG without altering it).

**Unused tokens (7):** `--color-navy-deep`, `--color-overlay`, `--dialog-width`, `--enquiry-dialog-width`, `--radius-large`, `--shadow-dialog`, `--space-11` (leftovers from removed prototype dialogs).

### 4.2 Responsive breakpoints

| Width | CSS use | JS counterpart |
|---|---|---|
| ≤ 359/360 px | extra-small tweaks (`main.css`, `home.css`) | — |
| ≤ 540 px | stack buttons/filters | — |
| ≤ 600 px | homepage carousel card sizing | — |
| **≤ 760 / ≥ 761 px** | **primary mobile/desktop split**: tokens override, grids collapse, banner artwork swap (`<source media="(min-width:761px)">`) | — |
| ≤ 900 px | secondary grid collapse | — |
| ≤ 1000 px | home layout | — |
| **≤ 1040 / ≥ 1041 px** | reading layout: sidebar beside article vs collapsible contents above | `main.js` L109 `matchMedia('(min-width:1041px)')` |
| **≤ 1190 / ≥ 1191 px** | primary nav collapses to the menu toggle | `main.js` L7 `matchMedia('(min-width:1191px)')` |
| `hover:hover and pointer:fine` | lift-on-hover only for fine pointers | — |
| `prefers-reduced-motion` | disable transitions/animations | `matchMedia` in `effects.js`, `home.js` |
| `print` | simplified print layout | — |

## 5. JavaScript architecture

**Five small, dependency-free, `'use strict'` scripts; no modules, no build, no globals other than the `js-enabled` class.** Hooks are **`data-*` attributes**, not CSS classes, so styling refactors cannot break behaviour. State is held in the **DOM and the URL**, never in storage.

| Script | Lines | Pages | Responsibilities |
|---|---:|---|---|
| `main.js` | 155 | all | adds `js-enabled`; menu open/close with `inert`, Esc, outside-click, focus-out; generic **listing filters** (`[data-filter-scope]`: search + category + reset + count + empty state); **hash forwarding** (`location.replace` to the dedicated page for legacy `#id` bookmarks, or open/scroll `<details>`); **reading contents scroll-spy** with `aria-current="location"`; footer year |
| `effects.js` | 138 | all | header `.is-scrolled` toggle; reading-progress bar maths; one-time reveals on home/about groups via `IntersectionObserver`; `<details>` open animation; live reduced-motion handling; cancels animations on `pagehide` |
| `articles.js` | 147 | articles listing + 40 articles | **listing:** read/write `lang`,`audience`,`region`,`topic`,`q` (whitelisted/regex-validated, `q` ≤160), compute counts (EN/SI), `history.replaceState`, propagate `library=<query>` into every `[data-article-link]` and set `[data-article-return]`; **reading pages:** restore the originating selection for breadcrumbs / related / return / nav item |
| `clinics.js` | 72 | clinics, hospitals | word-prefix search + location + platform filter, URL sync (`q`,`location`,`platform`), counts, empty state; unhides the form |
| `home.js` | 195 | home | banner carousel state machine (see below); body-explorer hover/focus pairing; resource carousel (scroll buttons, keys, announcements, focus scroll containment) |

**Banner carousel state machine** (`home.js` L5-114): `playing = !reducedMotion && !hovered && !focused && !touch && inView && !document.hidden`; each state change calls `schedule()` which sets/clears a single `setTimeout(interval)`; `show(i)` keeps the outgoing slide painted (`.is-previous`), toggles `inert`/`aria-hidden` on inactive slides, upgrades `loading` of the next image to `eager`, and announces only on manual change (`aria-live` flips between `off` while playing and `polite` otherwise).

**Data-attribute API (selection)**

| Group | Attributes |
|---|---|
| Generic filters | `data-filter-scope`, `data-filter-form`, `data-search-input`, `data-category-filter`, `data-results-count`, `data-empty-state`, `data-clear-filters` |
| Reading | `data-reading-url`, `data-reading-contents`, `data-reading-toc-link`, `data-reading-progress(-fill)` |
| Articles | `data-article-library|form|count|empty|reset|search|grid|link|return`, `data-language|audiences|regions|topics|search` |
| Clinics | `data-clinic-directory|form|count|empty`, `data-clear-clinic-filters`, `data-location|platforms|search`, `data-booking-provider` |
| Home | `data-banner-carousel|interval|dot|controls|status|title|index|playing|ready`, `data-body-explorer`, `data-region`, `data-resource-carousel`, `data-carousel-controls|status|ready` |
| Misc | `data-year`, `data-page` (on `<body>`), `data-reveal`, `data-treatment-illustration` |

No `innerHTML`, `eval`, `document.write`, `fetch`, storage, cookies or `postMessage` anywhere in the runtime scripts (CONFIRMED by grep; the only navigation sink is `location.replace`, whose argument comes from a build-time `data-*` attribute, not from user input).

## 6. Forms and interactive controls

| Form | Page(s) | Submission | Persistence |
|---|---|---|---|
| `form.library-filters` ×5 (Conditions, Treatments, Patient Info + 2 alias copies) | listings | `submit` → `preventDefault()` | none |
| `form.article-controls` ×1 | `articles.html` | `submit` → `preventDefault()` + `update()` | URL query only |
| `form.clinic-filters` ×2 (`clinics.html`, `hospitals.html`) | clinics | `submit` → `preventDefault()` | URL query only |

No `action` attributes; **no data ever leaves the browser** from these forms (CONFIRMED). Every control has a `<label for>` (asserted by `check_site.py` L122-123).

## 7. Accessibility implementation (CONFIRMED structurally; no full audit exists — DOCUMENTED)

| Practice | Evidence |
|---|---|
| Skip link, landmark structure (`header`, `nav` ×N with labels, `main#main tabindex=-1`, `footer`) | `header()`, `write_page` |
| Exactly one `<h1>` per page; no skipped heading levels | `check_site.py` L100-101 |
| Unique IDs; every `aria-controls/labelledby/describedby` target exists; every form control labelled | `check_site.py` L102-103, 120-123 |
| `aria-current` for active nav / TOC item | `nav_links()`, `main.js` L126-129 |
| All images have `alt`, `width`, `height`; none external | `check_site.py` L124-127 |
| Language tagging incl. Sinhala sections and English alt text inside Sinhala pages | generator + importer |
| Visible focus ring (3 px teal, 4 px offset), 44 px tap target token | `main.css` L22-23 |
| `prefers-reduced-motion` disables autoplay and CSS motion, cancels active animations | `home.js`, `effects.js`, all CSS |
| Carousels: only active slide focusable/announced (`inert`, `aria-hidden`), polite live regions, keyboard operation | `home.js` |
| Tables: caption, `scope="col"`, scroll region with `tabindex=0` + label | `render_blocks` L171-177 |
| Colour contrast of core token pairs ≥ 4.5:1 (one pair 4.38) | computed above |

**Gaps / risks:** no persistent pause control on a 2 s auto-rotating carousel (WCAG 2.2.2 — see `13_…` A-02); no real-screen-reader or real-browser keyboard verification recorded; Sinhala shaping/line-height not verified in a browser; site chrome not localised for Sinhala; `.reading-callout`/`.source-link` styles unexercised.

## 8. Images and asset loading

| Technique | Where |
|---|---|
| `width`/`height` on all `<img>` (prevents layout shift) | generator + check |
| `loading="lazy"` + `decoding="async"` below the fold; `loading="eager"`/`fetchpriority="high"` for first banner and hero portrait | `homepage.py` L17, `home()` hero |
| Responsive `srcset`/`sizes`; `<picture>` with WebP sources and PNG fallback | `stock_photo()`, `banner_carousel()` |
| Warm-up of next banner | `home.js` L53-56 |
| Local fonts with `font-display: swap`; one preload | `main.css` L1-4, `write_page` |
| Inline SVG sprite (no extra request) | `write_page` |
| **Not done:** WOFF2/subsetting, image resizing of archive figures (kept byte-identical by policy), CSS/JS minification, cache-busting | see `13_…` |

## 9. Repeated CSS, inline styles, unused CSS
See `05_FILE_STRUCTURE.md` §6: 7 orphaned classes (`.button-teal`, `.fellowship-layout`, `.fellowship-stat`, `.training-card`, `.training-timeline`, `.treatment-photo`, `.treatment-preview-with-photo`), 4 latent classes, 7 unused tokens. Repeated patterns include the card shadow/border recipe across `.topic-card`, `.clinic-card`, `.contact-channel`, `.qualification-card` (not factored into a shared class).

## 10. Browser compatibility considerations
Targets evergreen browsers (see `04_TECH_STACK.md` §4). `inert`, `Element.animate`, `:is()`, `dvh` and `Array.at` need ≈2022+ engines. Feature checks exist only for `IntersectionObserver`, `ResizeObserver`, `animate` and `History` restrictions on `file://`. No explicit support matrix (UNKNOWN). Real-browser verification was last recorded on 25 Oct 2026 for an earlier homepage, **before** the clinic replacement, banners and visual-effects work (DOCUMENTED).
