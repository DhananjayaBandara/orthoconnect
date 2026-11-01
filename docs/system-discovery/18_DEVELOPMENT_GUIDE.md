# 18 — Development Guide

Evidence legend: **CONFIRMED · INFERRED · DOCUMENTED · NOT IMPLEMENTED · UNKNOWN**.
Commands marked ✅ were **executed during this investigation** (in a scratch copy, never in the original tree). Commands marked 📄 are documented but were not run here.

> **Before modifying any application code, consult the relevant system-discovery documentation and inspect the affected implementation. Preserve existing architectural decisions unless an explicitly approved change requires otherwise.**
> **Do not assume that a documented requirement is implemented. Verify implementation in the source code.**

## 1. Mental model (read this first)

```
content/*.json  +  copy inside scripts/*.py   ──►   python3 -B scripts/build_site.py   ──►   *.html  (committed)
                                                         │                                      │
                                              validates before writing                 served as-is by GitHub Pages
```
* **Source of truth:** `content/**/*.json` and the Python templates. **Generated HTML is output** — never edit it.
* **There is no PHP, database or admin.** Don't look for `include`s or SQL.
* **Quality gates are scripts you run yourself** (there is no CI): `check_site.py`, `check_clinics.py`, `check_article_migration.py`, plus optional Node suites.
* **Everything is relative-URL based** so pages work from `file://`, from `/orthoconnect/` and from a domain root.

## 2. One-time setup

```sh
git clone git@github.com:DhananjayaBandara/orthoconnect.git && cd orthoconnect
python3 --version          # must be ≥ 3.12 (f-string syntax). ✅ 3.14.4 used here
```
Nothing to install for building. For the **full** verification you also need, **next to** the repo directory:

| Sibling folder | Needed by | Without it |
|---|---|---|
| `../Dr_Suneth_De_Silva_Unified_Link_Verifier/` | `check_clinics.py` | check still passes, prints "comparison skipped" |
| `../orthopaedic-lk-content-archive-toolkit/` | `check_article_migration.py`, `import_articles.py` | **both fail**; `check_article_migration.py` accepts the archive path as an argument |

Optional Node tooling (not declared anywhere): `jsdom` for the four DOM suites; `playwright` + Chrome for the browser suite.

## 3. Everyday commands

| Task | Command | Verified |
|---|---|---|
| Rebuild all pages | `python3 -B scripts/build_site.py` → "Generated 11 public pages, 56 reading pages and 3 compatibility routes." | ✅ |
| Structural audit | `python3 -B scripts/check_site.py` → PASS 70 pages / 56 reading / 5,386 refs / 19 stock placements | ✅ |
| Clinic audit | `python3 -B scripts/check_clinics.py` | ✅ |
| Article-conservation audit | `python3 -B scripts/check_article_migration.py [path/to/archive]` | ✅ (with sibling archive) |
| Offline stock-photo check | `python3 -B scripts/download_images.py --check` | ✅ |
| JS syntax | `for f in scripts/*.js scripts/*.cjs; do node --check "$f"; done` | ✅ |
| DOM suites | `ORTHOCONNECT_JSDOM_MODULE=/abs/path/to/node_modules/jsdom node scripts/check_clinics_dom.cjs` (also `check_effects_dom.cjs`, `check_home_banners_dom.cjs`); `ARTICLE_JSDOM_MODULE=… node scripts/check_articles_dom.cjs` | ✅ (250 / 257 / 79 / 42 assertions) |
| Real-browser suite | start a server, then `ORTHOCONNECT_PREVIEW_URL=http://127.0.0.1:8765/ ORTHOCONNECT_PLAYWRIGHT_MODULE=/abs/path/playwright node scripts/check_homepage.browser.cjs` | 📄 not run |
| Local preview | `python3 -B -m http.server 8080 --bind 127.0.0.1` then open <http://127.0.0.1:8080> | ✅ |
| Or just open | `index.html` in a browser (file://) | ✅ by design |

**Use `-B`** (as the README does) so Python doesn't write `__pycache__` (git-ignored anyway).

### Pre-commit routine
1. `python3 -B scripts/build_site.py`
2. `python3 -B scripts/check_site.py && python3 -B scripts/check_clinics.py && python3 -B scripts/check_article_migration.py`
3. `git status` — you should see **source files and the regenerated HTML changed together**. If generated HTML changed but no source did (or vice-versa), investigate.
4. (Recommended) `git diff --stat` to confirm no unrelated pages changed.

## 4. Where do I change…?

| I want to change… | Edit | Then |
|---|---|---|
| Home hero text, pills, expertise cards, featured article/guide IDs, section headings | `scripts/build_site.py` `home()` (L138-158) | rebuild |
| About prose | `scripts/build_site.py` `about()` (L165-168) | rebuild |
| Qualification cards | `content/site.json` → `qualifications` | rebuild |
| A condition card | `content/site.json` → `conditions` | rebuild |
| Privacy / Terms | `scripts/build_site.py` `policy()` (L254-276) | rebuild |
| Contact page | `build_site.py` `contact()` (L249-251) | rebuild |
| FAQ entries | `content/site.json` → `faqs` | rebuild |
| A treatment / guide / article | `content/<folder>/<id>.json` | rebuild |
| Navigation labels or order | `content/site.json` → `navigation` (+ page list in `main()` if adding a page) | rebuild; `check_site.py` compares nav on all pages |
| A clinic / booking link | `content/site.json` → `clinics` (+ `clinic_directory`) | see §5.4 |
| Homepage banners | `content/home-carousel.json` (+ images in `assets/images/home-banners/`) | rebuild |
| Stock photo placement | `content/stock-images.json` (`article_previews`, etc.) and a draft's `lead_image` | `download_images.py --check`, rebuild |
| Colours, type, spacing | `styles/tokens.css` | rebuild not needed for CSS-only changes, but run `check_site.py` (CSS `url()` check) |
| Component layout | `styles/main.css` (shared), `styles/home.css` (home only), `styles/effects.css` | — |
| Menu / filters / hash behaviour | `scripts/main.js`; articles → `articles.js`; clinics → `clinics.js`; home → `home.js`; motion → `effects.js` | run matching DOM suite |
| Icon | `assets/icons/sprite.svg` (add `<symbol id="name">`; ids are auto-prefixed `icon-`) then `icon('name')` | rebuild |
| Search-engine indexing flag | `build_site.py:365` (`noindex,nofollow`) | **needs explicit client approval** — see `17_…` §9 |

## 5. Recipes

### 5.1 Revise an existing reading page
Open `content/<folder>/<id>.json` → edit `title/summary/sections/blocks` → keep `id` and section `id`s → keep `status: "draft"` unless a **named reviewer and ISO date** exist → rebuild → open the page (desktop and a narrow window).
Block schema (`content/README.md`): `paragraph{text, question?}`, `heading{id,text}`, `list{items[],ordered?,start?}`, `image{src,alt,caption?}` (local JPEG/PNG under `assets/images/`), `table{caption,headers[],rows[][]}`, `callout{title?,text}`; any block may carry `lang`. **Text is escaped — no HTML or Markdown.**

### 5.2 Add a treatment or patient guide
Create `content/treatments/<id>.json` (or `patient-information/<id>.json`) from an existing file; add `{"id":"<id>","content":"content/<folder>/<id>.json"}` to `site.json` (`treatments` or `guides`) — **order matters** (the homepage shows the first three treatments). The page needs ≥ 2 contents entries (≥ 2 sections, or a section plus references) to pass `check_site.py` (L135).

### 5.3 Add an article
Same, in `content/articles/` with `lang` ∈ {en, si}, non-empty `audiences`, `body_regions`, `topics` from `content/article-taxonomy.json`. ⚠ `check_article_migration.py` is a **conservation audit of exactly the 40 imported articles** (it asserts 40 / 19 EN / 21 SI, and that every file in `content/articles/` is one of them). Adding a 41st article makes it fail **by design** — update its expectations deliberately (README: "update the migration evidence and the audit expectations deliberately").

### 5.4 Update a clinic or booking link
Edit the record in `content/site.json`: keep a stable lowercase-hyphen `id`; `name`, optional `branch`, `location` (`null` if unknown — **never guess**), `source_name`; per provider `url`, `verification_status`, `last_checked_utc` (timezone-aware, not in the future) and `hospital_code` (`H<digits>`, eChannelling) or `channel_id` (digits, Doc990). **Use the exact doctor-and-hospital sessions URL** — don't shorten the eChannelling query or change Doc990 `/si/` `/tm/` paths without checking the destination. Then rebuild + `check_site.py` + `check_clinics.py`. ⚠ `check_clinics.py` hard-codes **18 clinics and an 8/5/5 provider split** and the verifier report's SHA-256; if you legitimately change the inventory, update the audit's expectations, the `clinic_directory` provenance, and the documentation together.

### 5.5 Change the doctor's profile facts
They live in **four places** — keep them consistent: `site.json` `qualifications`; `build_site.py` hero pills (L140) and About prose (L166); `home-carousel.json` alt text; the About page's meta description in the page list inside `main()` (`build_site.py:380`, "…24 months of UK specialist training"). Only enter facts confirmed by the client; the policy is *no invented years, registrations or credentials*.

### 5.6 Add a content block type
Implement in `reading_content.render_blocks()` (escape everything), document it in `content/README.md`, add styles to `main.css`, and extend the checks. `callout` is a good template (its CSS currently has no content using it).

### 5.7 Replace a banner
Add the artwork (PNG original + WebP 768/1672 + WebP 1920×700 desktop), update `home-carousel.json` (paths, dimensions, SHA-256 of the original, alt text, `href`), rebuild, run `check_home_banners_dom.cjs`.

## 6. Conventions discovered

| Area | Convention |
|---|---|
| Python | stdlib only; module-level constants; small functions returning HTML strings; `e()`/`escape()` for **every** dynamic value; validate then write; raise `ValueError` with the offending ID; `python3 -B` |
| HTML (generated) | One logical section per line; semantic landmarks; `lang` on foreign-language fragments; `width`/`height`/`alt` on every image; IDs lowercase-hyphen |
| CSS | Tokens in `:root`; kebab-case component classes; state classes `is-*`; `[hidden]` + `.js-enabled` for progressive enhancement; reduced-motion and print blocks per file |
| JS | IIFE or top-level `'use strict'`; behaviour keyed on `data-*` attributes; no frameworks, no storage, no network; URL as state; feature-detect optional APIs |
| Content | Stable `id`; `status: draft`; `author/reviewed_*` only with verified data; unknown = `null`/omitted; Sinhala text never transliterated; English alt text inside Sinhala pages gets `lang="en"` |
| Commits | Imperative subject ("Update doctor profile and specialist qualifications"); one `feat:`/`ci:` conventional-style commit exists; changes arrive via feature branches `update/<topic>` merged by PR |
| Docs | README is user-facing and detailed; `docs/*.md` are dated validation records |

## 7. Debugging and troubleshooting

| Symptom / message | Likely cause |
|---|---|
| `SyntaxError` on `build_site.py` | Python < 3.12 |
| `ValueError: Unexpected source path for <id>` | `content` value isn't exactly `content/<folder>/<id>.json` |
| `Invalid or repeated section ID …` | section `id` not a slug, duplicated, or equals `title`/`further-reading` |
| `Invalid or repeated subsection ID …` | duplicate `heading` block id within a page |
| `Reviewed content needs reviewer and date` / `Review date cannot be in the future` | `status: reviewed` without valid metadata |
| `Unconfirmed doctor/hospital booking URL: <clinic>/<provider>` | host/path/ID mismatch or disallowed `verification_status` |
| `Invalid link verification date` | missing timezone offset or future timestamp |
| `Treatment illustration differs from its provenance` | SVG edited — update its `sha256` in `design.json` deliberately |
| `Inline image is not a local image asset` | image not under `assets/images/`, wrong type, or missing |
| `Inline images require descriptive alt text` | empty `alt` |
| `check_site.py: FAIL … missing local URL` / `missing anchor` | broken link/asset/ID in sources or generator |
| `check_site.py: … expected exactly one H1` / `heading order skips` | template/content heading structure |
| `FileNotFoundError … orthopaedic-lk-content-archive-toolkit` | sibling archive absent — pass its path |
| Nothing changes in the browser | cached CSS/JS (no fingerprinting) — hard-reload; or you edited generated HTML and then rebuilt |
| Filters do nothing on `file://` | History API restrictions are caught; filtering still works — check console for other errors |

**Browser debugging:** serve over HTTP; test `articles.html?lang=si&audience=adult&region=hip` and `clinics.html?q=ragama&platform=doc990`; disable JS to check fallbacks; emulate `prefers-reduced-motion`; check widths at 320, 390, 760/761, 1040/1041, 1190/1191.

## 8. Pitfalls and "do not" list
* ❌ Hand-editing any generated `*.html` (the next build silently reverts it).
* ❌ `python3 scripts/import_articles.py --replace` — overwrites imported drafts, `site.json`, provenance JSON **and `docs/article-migration-review.md`**, discarding editorial changes.
* ❌ Removing `noindex`, adding analytics/cookies/WhatsApp/forms/maps without client approval and a privacy-policy update.
* ❌ Inventing clinical facts, credentials, contact details, fees, schedules, review dates or bylines.
* ❌ Altering the supplied logo/portrait or archive images (they are meant to stay byte-identical).
* ❌ Editing in the stale sibling copy `../orthoconnect-lk-website/` — **this repo is canonical**.
* ❌ Adding `.html` files elsewhere in the tree (`check_site.py` audits every `*.html` it finds).
* ❌ Committing `docs/system-discovery/` before deciding the publish boundary (S-01).
* ⚠ Pages with fewer than 2 contents entries fail `check_site.py`.
* ⚠ Changing `site.json` keys requires coordinated edits in the generator, `check_site.py`, `check_clinics.py`, `check_article_migration.py`, `import_articles.py`.

## 9. Git and release workflow (observed)
Feature branch `update/<topic>` → commit **sources + regenerated HTML** → PR → merge commit into `main` (two PRs so far, one author). Publishing happens on merge/push to `main` (DOCUMENTED). `.gitignore` ignores `__pycache__/` and `*.py[cod]`. Remote: `git@github.com:DhananjayaBandara/orthoconnect.git`. Rollback: revert, rebuild, check, push.

## 10. Reading order for new engineers
`00` → `06` → `07`/`08` → `09` → `12` → this guide → `16`/`20` for what is unresolved.
