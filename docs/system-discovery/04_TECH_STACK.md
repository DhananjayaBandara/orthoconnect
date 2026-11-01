# 04 — Technology Stack

Evidence legend: **CONFIRMED · INFERRED · DOCUMENTED · NOT IMPLEMENTED · UNKNOWN**.

## 1. Stack at a glance

| Layer | Technology | Version / requirement | Evidence |
|---|---|---|---|
| Delivered site | **HTML5** (generated), **CSS3** (hand-written, custom properties + grid), **vanilla JavaScript** (no framework, no bundler) | Evergreen browsers (see §4) | CONFIRMED |
| Build tool ("backend") | **Python, standard library only** | **≥ 3.12** required (PEP 701 f-strings with backslashes/nested quotes at `build_site.py:53`); author's machine **3.14.4** (`__pycache__/*.cpython-314.pyc`) | CONFIRMED (syntax) + DOCUMENTED (README: "Python 3.12+") |
| Content store | **JSON files** (UTF-8, `ensure_ascii=False`) | — | CONFIRMED |
| Hosting | **GitHub Pages**, `main` branch, root folder, `.nojekyll`, HTTPS enforced | — | DOCUMENTED (`README.md`); not verified live |
| CI/CD | One sample **GitHub Actions** workflow (Jekyll build → Pages) — README says it is **disabled** in Actions | `actions/checkout@v4`, `configure-pages@v5`, `jekyll-build-pages@v1`, `upload-pages-artifact@v3`, `deploy-pages@v5` | CONFIRMED (file) / DOCUMENTED (disabled; UNKNOWN actual state) |
| Fonts | **Noto Sans** and **Noto Sans Sinhala**, Regular + Bold, **TTF**, self-hosted | SIL OFL (`assets/fonts/LICENSE.txt`) | CONFIRMED |
| Images | JPEG, PNG, WebP, SVG (hand-drawn icon sprite + 3 illustrations) | — | CONFIRMED |
| Tests (optional, dev-only) | Python audit scripts; **Node** scripts using **jsdom** and **Playwright** (neither declared nor installed in the repo) | Node v22.23.3 and jsdom 26.1.0 used in this investigation | CONFIRMED |
| Source control | Git + GitHub (pull-request merges) | — | CONFIRMED |

## 2. What is **not** in the stack (CONFIRMED by absence)

| Technology named in the brief or commonly assumed | Present? |
|---|---|
| PHP (any version), Composer | **No** — 0 `.php`, no `composer.*` |
| MySQL / MariaDB / any SQL | **No** — 0 `.sql`, no connection code |
| WordPress / CMS | **No** (the *legacy* `orthopaedic.lk` was WordPress: its image URLs contain `/wp-content/uploads/2020/11/` — see `content/article-assets.json`) |
| Node/npm manifests (`package.json`, lockfiles) | **No** — Node used only for optional tests, with unpinned external modules |
| Python dependency manifest (`requirements.txt`, `pyproject.toml`) | **No** — stdlib only |
| CSS/JS framework (Bootstrap, Tailwind, React, jQuery…) | **No** |
| Bundler, minifier, transpiler, linter, formatter, TypeScript | **No** |
| Docker, Makefile, task runner, `.env` files | **No** |
| Analytics, tag managers, chat widgets, CDNs, Google Fonts/Maps, reCAPTCHA | **No** (host sweep: only `www.doc.lk`, `www.echannelling.com`, `www.nhs.uk`, W3C namespace URI) |

## 3. Python modules and standard-library usage

| Module (`scripts/`) | Standard-library modules imported |
|---|---|
| `build_site.py` | `html.escape`, `pathlib`, `json`, `re`, `datetime.date` (inline), `urllib.parse.urlsplit` (inline) |
| `reading_content.py` | `datetime`, `html`, `pathlib`, `json`, `posixpath`, `re`, `struct`, `urllib.parse` |
| `article_library.py` | `datetime`, `html`, `json`, `pathlib`, `urllib.parse` |
| `homepage.py` | `html`, `json`, `pathlib` |
| `clinic_directory.py` | `datetime`, `re`, `urllib.parse` |
| `stock_assets.py` | `pathlib`, `json`, `struct` (JPEG SOF parser) |
| `visual_design.py` | `html`, `pathlib`, `hashlib`, `json` |
| `import_articles.py` | `argparse`, `collections`, `hashlib`, `json`, `pathlib`, `re`, `shutil` |
| `download_images.py` | `argparse`, `datetime`, `hashlib`, `json`, `pathlib`, `subprocess`, `sys`, `tempfile`, `urllib.error`, `urllib.request` |
| `check_site.py` | `collections`, `html.parser`, `pathlib`, `urllib.parse`, `hashlib`, `json`, `posixpath`, `re`, `sys` |
| `check_clinics.py` | `collections`, `html.parser`, `pathlib`, `urllib.parse`, `hashlib`, `json`, `re` |
| `check_article_migration.py` | `argparse`, `collections`, `hashlib`, `html.parser`, `json`, `pathlib`, `re` |

Style: **procedural/functional**; the only classes are `HTMLParser` subclasses in the checkers. No type hints. No third-party imports anywhere.

## 4. Browser/platform requirements (INFERRED from API usage)

Runtime JS uses: optional chaining, `Array.prototype.at(-1)`, `queueMicrotask`, `URLSearchParams`, `history.replaceState`, `toggleAttribute`, **`inert`**, `replaceChildren`, `matchMedia`, `IntersectionObserver`, `ResizeObserver`, **`Element.animate`**, `document.fonts.ready`, `pointer`/`touch` events, `String.prototype.normalize`, `pageshow`/`popstate`. CSS uses: custom properties, `clamp()`/`min()`/`max()`, CSS grid, `aspect-ratio`, `object-fit`, `:is()/:where()`, `scroll-snap`, `position: sticky`, `100dvh` (inside `@supports`), `env()`, `prefers-reduced-motion`, `@media print`.

⇒ Targets **current evergreen browsers (≈2022+)**. No transpilation, no polyfills, no explicit browser-support statement (UNKNOWN). Optional enhancements degrade gracefully (feature checks in `effects.js` L27, L74).

Notably absent: `<dialog>`, `fetch`, `localStorage`, service workers, web manifest.

## 5. Fonts, icons, imagery

| Asset class | Details |
|---|---|
| Fonts | `noto-sans-{regular,bold}.ttf` (≈501/504 KiB), `noto-sans-sinhala-{regular,bold}.ttf` (≈300/332 KiB); `font-display: swap`; only Regular is `<link rel=preload>`ed (Sinhala Regular on `lang=si` pages) — `main.css` L1-4, `bs:write_page` L359 |
| Icons | Single inline SVG sprite, **23 symbols** (4 unused: `check`, `clock`, `mail`, `phone`), injected into **every** page with ids prefixed `icon-` — `assets/icons/sprite.svg`, `bs:write_page` L347-349 |
| Illustrations | 3 original SVGs (hip, knee, arthroscopy), SHA-256 pinned in `content/design.json` |
| Photography | 5 Pexels photos × 2 widths (640/1280), credits in `content/stock-images.json`, hashes in `content/stock-assets.lock.json`; 251 archive images (244 JPEG + 7 PNG) in `assets/images/articles/` |
| Banners | 4 × (PNG 1672×941 original + WebP 768 + WebP 1672 + WebP 1920×700 desktop) |

## 6. Development tooling actually referenced

| Tool | Where referenced | Pinned? | Needed for |
|---|---|---|---|
| Python 3.12+ | all scripts, README | No | build, checks |
| Node.js | `*.cjs` | No | optional tests |
| jsdom | `ORTHOCONNECT_JSDOM_MODULE`, `ARTICLE_JSDOM_MODULE` | **No** (path to an existing install) | DOM suites |
| Playwright + Google Chrome | `ORTHOCONNECT_PLAYWRIGHT_MODULE`, `ORTHOCONNECT_BROWSER_CHANNEL` (default `chrome`) | **No** | `check_homepage.browser.cjs` |
| `python3 -m http.server` | README | n/a | local preview (verified working) |
| Pillow (WebP/Lanczos) | `ASSET-SOURCES.md` (one-off image resizing) | n/a | **not in repo**; one-time asset preparation |
| librsvg | `docs/visual-design-validation.md` | n/a | one-time visual inspection |

## 7. Version summary used in this investigation
Python 3.14.4 · Node v22.23.3 · jsdom 26.1.0 (borrowed from an unrelated local project via the documented env var; nothing installed) · git (system).
