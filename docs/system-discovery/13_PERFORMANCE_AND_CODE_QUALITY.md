# 13 — Performance, Accessibility, SEO, Code Quality and Testing

Evidence legend: **CONFIRMED · INFERRED · DOCUMENTED · NOT IMPLEMENTED · UNKNOWN**.
Severity: **Critical · High · Medium · Low · Informational**. Measurements were taken from the working tree (uncompressed). No browser or network profiling was possible, so all load estimates are **INFERRED** from file sizes and markup.

## 1. Performance

### 1.1 Measured asset weight (CONFIRMED)

| Asset group | Files | Size | Notes |
|---|---:|---:|---|
| Article images | 251 | **23.27 MiB** | 244 JPEG + 7 PNG; median 52 KiB; 9 files > 500 KiB; 2 > 1 MiB (largest 1,466 KiB PNG) |
| Fonts (TTF) | 4 | **1.60 MiB** | not WOFF2, not subset |
| Banner WebP (12) | 12 | 1.29 MiB | each page view loads ≤ 1 desktop or 1 mobile banner initially |
| Banner PNG originals | 4 | 7.06 MiB | `<img>` fallback inside `<picture>` only |
| Stock + logo + portrait | 12 | 1.52 MiB | portrait 173 KiB, logo 83 KiB |
| `docs/previews` PNGs | 8 | 5.22 MiB | historical, published |
| HTML (70 pages) | 70 | 1.46 MiB | `articles.html` 92 KB; `index.html` 39.7 KB |
| CSS (4) / runtime JS (5) | 9 | 78 KiB / 30 KiB | unminified |
| JSON content | 66 | 0.68 MiB | published |

### 1.2 Estimated first-load cost (INFERRED)
Homepage (desktop): HTML 39 KiB + CSS ≈78 KiB + JS ≈21 KiB + fonts ≈1,005 KiB (Regular preloaded; Bold used by headings) + portrait 173 KiB + logo 83 KiB + first banner ≈78 KiB ⇒ **≈1.4–1.5 MiB uncompressed** before transfer compression (the `<picture>` PNG fallback is **not** fetched by WebP-capable browsers). An inner English page ≈0.8 MiB; a long article adds lazy images (worst case 1.9 MiB on `si-adult-osteoporosis`, 9 images). A Sinhala page also needs Sinhala fonts (+≈0.6 MiB), and so does `articles.html` because it lists Sinhala titles (INFERRED).

### 1.3 Findings

| ID | Sev | Finding | Evidence | Suggestion (not implemented) |
|---|---|---|---|---|
| **P-01** | **Medium** | Fonts shipped as four full TTFs (1.6 MiB); ≈1 MiB required on every English page | `assets/fonts/*.ttf`; `main.css:1-4` | WOFF2 + Latin/Sinhala subsetting (typically a 70–90 % reduction) |
| P-02 | Low | A handful of very large archive images; kept byte-identical by policy (no recompression) | `docs/article-migration-review.md` §Images | Decide whether lossless optimisation is acceptable to the client |
| P-03 | Low | No minification of CSS/JS | file sizes | Optional; host gzip already helps |
| P-04 | Low | Every page inlines a 3.6 KB SVG sprite | `write_page` | Trade-off for `file://` support; acceptable |
| P-05 | Low | `articles.html` = 92 KB (40 cards each with a long `data-search` blob) | file size | Acceptable; could move index to JSON if it grows |
| P-06 | Informational | 12.3 MiB of published files are never rendered (banner PNG originals, preview PNGs) | §1.1 | Consider excluding from the published artefact |
| P-07 | Informational | 3 alias pages duplicate 74 KB | `cmp` | Redirect/canonical when indexing is enabled |
| P-08 | Low | No asset fingerprinting / long-term caching strategy; cache headers are platform-controlled (values UNKNOWN) | `<head>` | Query-string or hashed names if caching issues appear |
| P-09 | Low | Render-blocking: 3–4 sequential stylesheets, no critical-CSS inlining | `write_page` | Fine on HTTP/2; revisit only if LCP is poor |

### 1.4 Good practice already present (CONFIRMED)
`loading="lazy"` + `decoding="async"` below the fold; intrinsic `width`/`height` on every image (layout-shift control, enforced by `check_site.py`); `fetchpriority="high"` on the LCP candidate; responsive `srcset`/`<picture>` with WebP; deferred scripts; single font preload; `font-display: swap`; no third-party requests; carousel timers pause when hidden/off-screen; `prefers-reduced-motion` honoured; passive scroll listeners with `requestAnimationFrame` throttling; `IntersectionObserver`/`ResizeObserver` instead of polling.

### 1.5 Database/query efficiency
Not applicable — no database.

## 2. Accessibility

Structural baseline is strong and machine-checked (`07_FRONTEND_ARCHITECTURE.md` §7). The project documents that **no complete accessibility audit** has been done.

| ID | Sev | Finding | Evidence | Note |
|---|---|---|---|---|
| **A-02** | **Medium** | The homepage banner carousel **auto-advances every 2 s (1 s cross-fade) indefinitely with no persistent pause/stop control** — a likely WCAG 2.2.2 (Pause, Stop, Hide, Level A) gap. Mitigations: pauses on hover, focus, touch, hidden tab and off-screen; fully disabled under `prefers-reduced-motion`; dots/keys/swipe for manual control. Mouse-less/touch users without a held touch cannot pause it. | `home.js:29-35`; `docs/homepage-carousel.md` ("pause/play buttons have been removed at the user's request") | Requires an explicit client/accessibility decision. 2 s is also short for reading text baked into banner images |
| A-03 | Low | Banner artwork contains embedded text and third-party logos; meaning is conveyed through long `alt` strings | `content/home-carousel.json` | Images of text (WCAG 1.4.5, AA) — acceptable if equivalent text exists |
| A-04 | Low | Sinhala shaping, line-height (2.0) and wrapping not verified in any real browser | `docs/article-validation.md` §Browser limits | Needs a manual pass with a native reader |
| A-05 | Low | Header/footer/nav remain English on Sinhala pages (correctly tagged `lang="en"`) | `article_library.py`, `write_page` | Localisation gap rather than a violation |
| A-06 | Low | No automated a11y tooling (axe, pa11y, Lighthouse) and no recorded screen-reader pass | repo | Add to CI/checklist |
| A-07 | Low | Fixed mobile action bar + sticky header could obscure content/focus targets at small sizes; documented as "to verify" | `docs/visual-design-validation.md` | Browser check at 320–390 px |
| A-08 | Informational | Core colour pairs all ≥ 4.5:1 (computed); the only sub-4.5 pair (accent on accent-light = 4.38) is not used for text | `07_…` §4.1 | — |
| A-09 | Informational | Skip link, landmarks, one H1, no heading skips, labelled controls, `aria-current`, focus ring 3 px, 44 px tap token, `inert` for hidden carousel/menu content, polite live regions | `check_site.py`, CSS, JS | — |

## 3. SEO and discoverability (by design: **not indexed**)

| ID | Status | Finding | Evidence |
|---|---|---|---|
| SEO-01 | **By design** | `noindex,nofollow` on 70/70 pages, a hard-coded constant | `build_site.py:365` |
| SEO-02 | NOT IMPLEMENTED | No `<link rel="canonical">`; three alias pages are exact duplicates | 0/70 pages; `cmp` |
| SEO-03 | NOT IMPLEMENTED | No `sitemap.xml`, no `robots.txt` | file check |
| SEO-04 | NOT IMPLEMENTED | No Open Graph/Twitter cards, no social image; favicon = the logo JPEG only (no ICO/PNG sizes, no apple-touch-icon, no manifest) | grep |
| SEO-05 | NOT IMPLEMENTED | No structured data (e.g. Physician / MedicalBusiness / MedicalWebPage / BreadcrumbList) though breadcrumbs exist visually | grep |
| SEO-06 | Implemented | Unique `<title>` and `<meta name=description>` per page; one H1; logical headings; descriptive alt text; clean flat URLs; `lang` set (`en`/`si`) | generator + audit |
| SEO-07 | n/a | No `hreflang`; EN and SI collections are deliberately independent (no translation pairs) | `content/README.md` |
| SEO-08 | Risk | Near-duplicate content: two overlapping English children's articles; Sinhala overview vs individual articles; legacy text reused from another domain (duplicate-content/attribution) | `docs/article-migration-review.md` |
| SEO-09 | NOT IMPLEMENTED | Canonical domain `orthoconnect.lk` absent from the repo | grep |

## 4. Maintainability and code quality

| ID | Sev | Observation | Evidence |
|---|---|---|---|
| M-01 | Medium | **Content split** between JSON and Python templates; doctor facts repeated in 4 places | `build_site.py:139-168`; `site.json`; `home-carousel.json` |
| M-02 | Medium | One 46 KB generator module with single-line f-strings of 1,000+ characters; hard to review and diff; requires Python ≥ 3.12 only because of nested-quote f-strings | `build_site.py:53,141,165,243` |
| M-03 | Low | Dead/orphaned CSS (7), unused tokens (7), unused icons (4), dead generator branches | `05_FILE_STRUCTURE.md` §6 |
| M-04 | Medium | **Documentation drift**: README still describes "JBJS MRC Oxford" and an About "UK fellowship / timeline" removed in `a45dd5e`; README:139 runs a script in a stale sibling folder; counts of "local references" differ between docs (5,226 / 5,364 / 5,384 / 5,541 / 5,597) and the current audit says 5,386; historic screenshots predate the UI | `README.md`, `docs/*.md` |
| M-05 | Medium | No dependency manifests for Node test tools; Python version only in prose | repo |
| M-06 | Medium | No CI executing the checks; sibling-folder coupling makes full verification impossible from a fresh clone | AW-01, AW-04 |
| M-07 | Low | Naming inconsistency: `guides` (code/data) vs `patient-information` (folder/nav) vs "Patient Information"; `hospitals`/`clinics`; `services`/`treatments`; `medical-information` alias | `reading_content.py:14-18`, `build_site.py:392` |
| M-08 | Low | Heuristic `question: true` flags (265 blocks) were inferred by regex at import time | `import_articles.py:146` |
| M-09 | Low | `import_articles.py --replace` can overwrite editorial changes and `docs/article-migration-review.md` | `import_articles.py:169,279` |
| M-10 | Low | Repetition in CSS card recipes and in the four jsdom test harnesses | CSS, `.cjs` |
| M-11 | Informational | Positive: strict validation, explicit error messages, small pure helpers, security-conscious escaping, comments explaining intent, provenance recorded for all assets, deterministic build | — |

## 5. Testing

| Suite | Type | Scope | Assertions | Result here | Dependencies | Known limits |
|---|---|---|---|---|---|---|
| `check_site.py` | Python audit | structure, nav parity, headings, IDs, anchors, ARIA refs, labels, images, local URLs, CSS `url()`, stock hashes, no archive links | 70 pages / 5,386 refs | **PASS** | stdlib | Not a full a11y audit |
| `check_clinics.py` | Python audit | clinic data ↔ pages ↔ verifier report; provider combos; prototype wording absent; alias identical | — | **PASS** (with sibling report) | sibling folder (optional) | Does not test live links |
| `check_article_migration.py` | Python audit | 40 articles' text/image stream vs archive; hashes; provenance; guide links; dummy removal | — | **PASS** (with sibling archive) | sibling archive (**required**) | Can't run on a fresh clone |
| `check_clinics_dom.cjs` | jsdom | filters, URL/history, no-JS fallback, 70-page nav | **250** | **PASS** | jsdom | Mocks layout |
| `check_articles_dom.cjs` | jsdom | combined filters, Unicode search, URL context | **42** | **PASS** | jsdom | — |
| `check_effects_dom.cjs` | jsdom | nav inert/focus, reveals, reduced motion, 70-page integration | **257** | **PASS** | jsdom | Observers/animation mocked |
| `check_home_banners_dom.cjs` | jsdom | banner order, timer, keys, swipe, visibility, fallback, asset hashes | **79** | **PASS** | jsdom | Timers mocked |
| `check_homepage.browser.cjs` | Playwright + Chrome | real layout, overflow at 6 widths, touch, reduced motion, outbound-nav interception | 43+ (historic) | **NOT RUN** | Playwright, Chrome | Last real run pre-dates clinic/banner/effects work |
| `node --check` ×10 | syntax | all JS/CJS | — | **PASS** | Node | — |
| `download_images.py --check` | offline | 10 stock JPEGs | — | **PASS** | — | — |

**Coverage assessment:** content/structure integrity — **excellent**; behaviour logic — **good** (628 DOM assertions); visual/responsive rendering, Sinhala typography, real keyboard/touch behaviour, performance budgets, accessibility tooling, link liveness — **absent or stale**. No unit tests of generator functions; no regression snapshots (although byte-identical rebuild acts as a coarse snapshot test).

## 6. Technical-debt register

| ID | Debt | Sev | Effort (rough) |
|---|---|---|---|
| T-01 | No CI gate (rebuild-diff + audits) | **High** (for integrity of booking links) | S |
| T-02 | Content embedded in Python; duplicated profile facts | Medium | M |
| T-03 | Undeclared dev dependencies; sibling-folder coupling; no fresh-clone path | Medium | S–M |
| T-04 | Documentation drift and stale historical numbers/screenshots | Medium | S |
| T-05 | Fonts not optimised | Medium | S |
| T-06 | Carousel accessibility (no pause) | Medium | S |
| T-07 | Dead CSS/JS/tokens/icons/branches | Low | S |
| T-08 | Alias duplicates; `noindex` hard-coded constant; no SEO scaffolding | Medium at launch | M |
| T-09 | Giant f-strings; no template engine | Low–Medium | M–L |
| T-10 | Stale sibling copy `orthoconnect-lk-website/` (risk of editing the wrong tree) | Low | S |
| T-11 | Test boilerplate duplication; no unit tests | Low | M |
| T-12 | Published internal artefacts (S-01/S-02) | Medium | S |

(Effort: S ≤ 0.5 day, M ≈ 1–3 days, L > 3 days — rough orders of magnitude, **not** commitments.)
