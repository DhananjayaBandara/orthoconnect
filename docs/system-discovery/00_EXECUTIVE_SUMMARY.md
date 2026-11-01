# 00 — Executive Summary

> **Investigation date:** 2026-11-01 · **Repository:** `DhananjayaBandara/orthoconnect` · **Branch / HEAD:** `main` @ `f4903c9`
> **Nature of this work:** read-only reverse-engineering. No application file was modified. All executable verification was done on a copy in a scratch directory.

> ### ⚠ PUBLICATION WARNING — read before committing this folder
> The README documents that GitHub Pages publishes **the repository root** (`Deploy from a branch → main → / (root)`, with a root `.nojekyll`). There is no build/publish allow-list. Anything committed under `docs/system-discovery/` — including the security assessment (`12_SECURITY_ASSESSMENT.md`) — would therefore be **publicly retrievable by URL**. These documents are intentionally **uncommitted**. Decide where they should live (a private repo, a wiki, or a folder excluded from publishing) before committing. See finding **S-01** in `12_SECURITY_ASSESSMENT.md`.

## Evidence legend (used in every document)

| Label | Meaning |
|---|---|
| **CONFIRMED** | Directly verified in source code, or by executing a check during this investigation |
| **INFERRED** | Strongly suggested by implementation evidence but not directly demonstrated |
| **DOCUMENTED** | Stated in project documentation (README, `docs/`, `content/README.md`) but not independently verified |
| **NOT IMPLEMENTED** | Described/expected, but no implementation exists |
| **UNKNOWN** | Insufficient evidence |

---

## 1. The headline: the project is not what the brief assumed

The brief describes an existing implementation in **HTML, CSS, PHP, JavaScript and MySQL/MariaDB**. **That is not what this repository contains.**

| Brief assumption | Reality in this repository | Evidence |
|---|---|---|
| PHP application | **No PHP anywhere.** 0 `*.php` files. | CONFIRMED — `find` for `*.php`; `grep -r '\.php'` over all tracked text → 0 hits |
| MySQL / MariaDB | **No database.** 0 `*.sql`, no DB driver, no connection code. | CONFIRMED — see `09_DATABASE_ARCHITECTURE.md` |
| Server-side processing, sessions, auth, forms | **None.** No runtime server code. The three `<form>` types are client-side filters whose `submit` is `preventDefault()`-ed; no `fetch`/XHR anywhere. | CONFIRMED — `scripts/*.js`, generated HTML |
| Admin interface | **None.** The prototype's `admin.html` / CMS pages were explicitly excluded. | DOCUMENTED — `README.md` §Public pages |
| Production domain `orthoconnect.lk` | **Not referenced anywhere** in the repository (no `CNAME`, no canonical tags, no absolute URLs). The documented host is `https://dhananjayabandara.github.io/orthoconnect/`. | CONFIRMED (absence) + DOCUMENTED (host) |

**What it actually is:** a **buildless-at-runtime static website** — 70 pre-generated HTML pages plus CSS, ~30 KiB of vanilla JavaScript and local assets — **produced by a Python 3.12+ standard-library generator** (`scripts/build_site.py`) from JSON content files and hard-coded templates. Generated HTML is committed to git; GitHub Pages serves it as-is.

The word "PHP/MySQL" in the brief most plausibly refers to something outside this repo (the legacy `orthopaedic.lk` site, which the repo's provenance data shows was a **WordPress** site; a "separate WordPress checkout" mentioned in `docs/homepage-review.md`; or the *proposed* architecture in the not-supplied technical architecture spec). **Which is UNKNOWN** — see `20_ARCHITECTURAL_DECISIONS_AND_OPEN_QUESTIONS.md`.

## 2. Documents that could not be located

None of the four expected reference documents exist in the repository, and a filename-only search of the surrounding project folders did not find them either:

| Expected document | Status |
|---|---|
| `orthopaedic-lk-reverse-engineering-spec.md` | **NOT FOUND** |
| `orthopaedic-lk-refined-srs-v2.md` | **NOT FOUND** |
| `orthopaedic-lk-technical-architecture-spec-v2.md` | **NOT FOUND** |
| `Dr_Suneth_De_Silva_Website_Profile_Content.docx` | **NOT FOUND** |

**Please provide them.** Consequently, SRS compliance **cannot be assessed** (`14_SRS_ANALYSIS.md`, `15_REQUIREMENTS_TRACEABILITY.md`); requirement rows in the traceability matrix are derived from the brief and the repo's own documentation and are labelled as such. No SRS content was invented.

## 3. System snapshot

| Item | Value | Evidence |
|---|---|---|
| Client / subject | Dr. Suneth De Silva, Consultant Orthopaedic Surgeon (Sri Lanka) | `index.html`, `scripts/build_site.py` |
| Architecture pattern | Custom **static-site generator (SSG)**; generated output committed; progressive-enhancement client JS | CONFIRMED |
| Tracked files / size | 470 tracked files (476 in working tree incl. 6 ignored `.pyc`); ≈44 MB working tree; `.git` ≈40 MB | CONFIRMED |
| Generated pages | **70 HTML**: 11 public + 3 alias copies + 56 reading pages (40 articles, 8 treatments, 8 patient guides) | CONFIRMED |
| Languages | English site chrome; articles in **English (19)** and **Sinhala (21)**; Tamil: none | CONFIRMED |
| Hand-written source | 12 Python files (1,843 lines), 5 runtime JS (707 lines), 4 CSS (990 lines), 5 Node test scripts (953 lines) | CONFIRMED |
| Content sources | 66 JSON files (56 reading drafts + 10 data/provenance files) | CONFIRMED |
| Runtime dependencies | **None** (no CDN, fonts, analytics, maps, frameworks) | CONFIRMED — external-host sweep |
| External services (links only) | eChannelling (13 centres), Doc990/doc.lk (13 centres), NHS UK reference links | CONFIRMED |
| Hosting | GitHub Pages, branch `main`, folder `/`, HTTPS enforced | DOCUMENTED (not verified live) |
| Search-engine visibility | **Excluded**: `noindex,nofollow` on 70/70 pages, hard-coded at `scripts/build_site.py:365` | CONFIRMED |
| Clinical review state | **0 of 56** reading pages reviewed — all `status: "draft"` | CONFIRMED |

## 4. What the system does (business view)

OrthoConnect is a **professional presence and patient-routing site**, not a booking system. It (1) introduces the surgeon and his qualifications, (2) publishes bilingual patient-education material, and (3) routes patients to **18 hospital consultation centres**, each with deep links (26 in total) to the doctor's session page on **eChannelling** and/or **Doc990**. Appointments, fees, schedules and payments are handled entirely by those providers. The site collects **no data** — no forms, accounts, uploads, cookies, storage or analytics.

## 5. Implementation status at a glance

| Area | Status |
|---|---|
| Public pages (Home, About, Conditions, Treatments, Patient Information, Clinics, Articles, Contact, Privacy, Terms, 404) | **Implemented** |
| Clinic directory with provider deep links, search and filters | **Implemented** |
| Bilingual article library (40) with URL-shareable filters | **Implemented** |
| Responsive navigation, homepage carousels, accessibility scaffolding | **Implemented** (DOM-tested; real-browser pass not re-run) |
| Telephone / WhatsApp / e-mail / address / map actions | **NOT IMPLEMENTED** (deliberately omitted — no public contacts supplied) |
| Consultation schedules, fees, on-site booking, payments | **NOT IMPLEMENTED** (delegated to providers by design) |
| Admin / CMS / authentication / database / PHP | **NOT IMPLEMENTED / not applicable** |
| SEO (indexing, canonical, sitemap, robots, structured data, OG tags) | **NOT IMPLEMENTED** (site is `noindex` by design) |
| Production domain `orthoconnect.lk` | **NOT IMPLEMENTED** in repo |
| Clinically reviewed content | **NOT IMPLEMENTED** — all 56 drafts unreviewed |

## 6. Verification performed during this investigation

All executed on a **scratch copy** (original untouched; `git status` clean afterwards):

| Check | Result |
|---|---|
| Fresh `python3 -B scripts/build_site.py` vs committed output | **Byte-identical** — committed HTML is exactly reproducible from sources |
| `scripts/check_site.py` | PASS — 70 pages, 56 reading pages, 5,386 local references, 19 stock-photo placements |
| `scripts/check_clinics.py` (with sibling verification report) | PASS — 18 centres, 26 links match the report exactly |
| `scripts/check_article_migration.py` (with sibling archive) | PASS — 40 articles, 390 image placements, 251 distinct images |
| 4 jsdom DOM suites (existing jsdom 26.1.0) | PASS — 250 + 42 + 257 + 79 = **628 assertions** (matches project docs exactly) |
| `node --check` on all 10 JS/CJS files; `download_images.py --check` | PASS |
| `python3 -m http.server` preview | Works (pages 200, missing page 404) |
| `scripts/check_homepage.browser.cjs` (real Chrome via Playwright) | **NOT RUN** — Playwright/Chrome not available; installs prohibited |

## 7. Top risks (prioritised)

| # | Risk | Severity | Where detailed |
|---|---|---|---|
| 1 | **Unreviewed clinical content**: 56/56 drafts; legacy text includes wording the repo itself flags as copied from another topic (hip & foot/ankle articles contain shoulder/arm wording) | **High** if published as-is; mitigated today by draft banners + `noindex` | `16_IMPLEMENTATION_GAPS.md` G-C01 |
| 2 | **Provenance / reuse rights of 40 articles & 251 images** scraped from `orthopaedic.lk` (WordPress). Repo docs call it "a different legacy practice"; the brief calls it an older name of this project. First-person text and branded X-rays retained. | **High** (legal/reputational) until resolved | `20_…` OQ-02 |
| 3 | **Whole repo root is published** → internal docs, scripts, provenance JSON and any added docs are public | **Medium** | `12_…` S-01 |
| 4 | **Not launch-ready by design**: `noindex`, no canonical/sitemap/robots/OG, no `orthoconnect.lk` configuration, no public contact details | **High** for go-live, none today | `17_…` §9 |
| 5 | **Documentation drift & stale copies** (README still describes removed About timeline and "JBJS MRC Oxford"; README hard-codes a path to a stale sibling folder) | Low–Medium | `13_…` |
| 6 | **Carousel auto-advances every 2 s with no persistent pause control** (potential WCAG 2.2.2 gap; removed at the user's request) | Medium (accessibility) | `13_…` A-02 |
| 7 | **Unoptimised fonts** (4 full TTFs, 1.6 MiB; no WOFF2/subsetting) | Medium (performance) | `13_…` P-01 |

## 8. Recommended next steps (priority order)

1. **Supply the four missing reference documents** and confirm whether `website-build-files/build-prompt.md`, `website-build-files/sitemap.md` and `questionnaire.md` (in the parent folder, *not read*) may be used as requirement sources.
2. **Resolve the `orthopaedic.lk` question** (ownership of the archived articles/images; permission to reuse) — it gates publication of 40 of the 56 reading pages.
3. **Decide the fate of `docs/system-discovery/`** (private location vs published) *before* any commit/push.
4. **Decide the target architecture**: continue the static/Python approach, or migrate (e.g. to WordPress/PHP as the brief hints). Nothing in the repo implies a migration has started.
5. **Clinical review workflow** for the 56 drafts; confirm service scope for the 3 "pending" treatments and 5 "pending" conditions.
6. **Production readiness package**: domain/CNAME, remove `noindex` deliberately, canonical + sitemap + robots, public contact details (if wanted), privacy/legal review.
7. **Hygiene fixes** (only after approval): purge dead CSS/JS selectors, fix README drift and absolute paths, add a CI job that runs the checks, consider WOFF2/subsetted fonts and a carousel pause control.

## 9. Document map

| File | Topic |
|---|---|
| `01_PROJECT_OVERVIEW.md` | Identity, stakeholders, scope, lineage |
| `02_BUSINESS_CONTEXT.md` | Business processes, users, journeys |
| `03_FUNCTIONALITY_CATALOGUE.md` | Every feature with implementation evidence |
| `04_TECH_STACK.md` | Actual technologies and versions |
| `05_FILE_STRUCTURE.md` | Full inventory and file responsibilities |
| `06_SYSTEM_ARCHITECTURE.md` | Architecture + context/component/detail diagrams |
| `07_FRONTEND_ARCHITECTURE.md` | HTML/CSS/JS, tokens, components |
| `08_BACKEND_ARCHITECTURE.md` | The Python build-time "backend" |
| `09_DATABASE_ARCHITECTURE.md` | No DB — the file-based content model |
| `10_WORKFLOWS_AND_DATA_FLOWS.md` | Journeys, flowcharts, sequence diagrams |
| `11_EXTERNAL_INTEGRATIONS.md` | eChannelling, Doc990, NHS, Pexels, GitHub |
| `12_SECURITY_ASSESSMENT.md` | Findings S-01…; PHP-class vulnerability checklist |
| `13_PERFORMANCE_AND_CODE_QUALITY.md` | Performance, a11y, maintainability, tests, debt |
| `14_SRS_ANALYSIS.md` | Document availability and requirement sources |
| `15_REQUIREMENTS_TRACEABILITY.md` | Requirement → implementation matrix |
| `16_IMPLEMENTATION_GAPS.md` | Gaps, discrepancies, drift |
| `17_DEPLOYMENT_AND_ENVIRONMENT.md` | How it runs and is published |
| `18_DEVELOPMENT_GUIDE.md` | Practical new-developer guide |
| `19_GLOSSARY.md` | Terms |
| `20_ARCHITECTURAL_DECISIONS_AND_OPEN_QUESTIONS.md` | ADRs, compromises, open questions |
| `21_VISUAL_SYSTEM_MAP.md` | Index of all diagrams + master map |
