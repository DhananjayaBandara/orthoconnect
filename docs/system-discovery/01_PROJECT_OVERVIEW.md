# 01 — Project Overview

Evidence legend: **CONFIRMED · INFERRED · DOCUMENTED · NOT IMPLEMENTED · UNKNOWN** (defined in `00_EXECUTIVE_SUMMARY.md`).

## 1. Identity

| Property | Value | Evidence |
|---|---|---|
| Project name | **OrthoConnect** (brand shown in header/footer/`<title>` suffix) | CONFIRMED — `scripts/build_site.py` `write_page()` |
| Subject / client | **Dr. Suneth De Silva, Consultant Orthopaedic Surgeon** | CONFIRMED — hero, About, footer |
| Category | Medical / professional-healthcare presence site (patient information + appointment routing) | CONFIRMED |
| Official domain (per brief) | `https://orthoconnect.lk` | Brief only — **absent from the repository** (CONFIRMED by `grep`) |
| Documented live host | `https://dhananjayabandara.github.io/orthoconnect/` | DOCUMENTED — `README.md` §GitHub Pages (not fetched live) |
| Git remote | `git@github.com:DhananjayaBandara/orthoconnect.git` | CONFIRMED |
| Branches | `main` (+ 2 merged feature branches `update/doctor-professional-profile`, `update/about-page-simplification`) | CONFIRMED |
| Commits / authors | 8 commits, 1 author (GitHub user *DhananjayaBandara*) | CONFIRMED — `git shortlog` |
| Licence | **No LICENSE file**; footer states "© 2026 OrthoConnect. All rights reserved." Bundled Noto fonts are OFL (`assets/fonts/LICENSE.txt`). | CONFIRMED |
| Primary language of UI | English; reading pages may be Sinhala (`lang="si"`, 21 articles) | CONFIRMED |

## 2. What the project is

A **static public website** whose HTML is **generated at build time by a Python script** and then committed. Visitors receive plain HTML/CSS/JS from a static host; there is no application server, database, session, or API. Interactive behaviour (menus, carousels, filters) is vanilla JavaScript layered on top of pages that are complete and readable without it.

The repository's own words (`README.md`): *"A standalone static HTML, CSS and vanilla JavaScript website… No installation, API, build step or Internet connection is needed to view the website."*

## 3. Stakeholders and users

| Stakeholder | Role | Evidence |
|---|---|---|
| Dr. Suneth De Silva | Client; subject of the site; named clinical reviewer ("These educational drafts are awaiting Dr. De Silva's review") | CONFIRMED — `build_site.py:218`, reading-page templates |
| Dhananjaya Bandara | Sole committer, repository owner, de-facto maintainer/developer | CONFIRMED — git history |
| Patients & prospective patients (adults) | Primary audience: find the doctor, read about conditions/treatments, locate a clinic, book | INFERRED — page structure and copy |
| Parents/caregivers of children | Audience for the 20 articles tagged `children` (7 English + 13 Sinhala, incl. the overview guide and one article tagged for both audiences) | CONFIRMED — `content/articles/*.json` `audiences`; `docs/article-validation.md` |
| Sinhala-language readers | 21 Sinhala articles, Sinhala fonts, localised reading UI | CONFIRMED |
| Hospitals / channelling centres (18) | Venues where consultations occur; named in directory | CONFIRMED — `content/site.json` |
| eChannelling and Doc990 (doc.lk) | External booking providers that actually take bookings | CONFIRMED — `scripts/clinic_directory.py` |
| Search engines | Currently **excluded** (`noindex,nofollow`) | CONFIRMED |
| Editorial / clinical reviewer role | Needed to move drafts to `reviewed`; no workflow tooling exists beyond JSON fields | CONFIRMED — `content/README.md` |

Operators: **UNKNOWN** beyond the single developer. Hosting operator is GitHub (DOCUMENTED).

## 4. Objectives (as evidenced)

Derived from `README.md`, `docs/*.md` and generated copy — not from an SRS (none supplied):

1. Present the surgeon's profile and qualifications accurately, **without inventing** years, registrations, testimonials, patient counts, or treatment guarantees (`README.md` §Consultation directory).
2. Provide **educational content** in plain language (conditions, treatments, patient guides, 40 articles), clearly labelled as draft where clinical review is pending.
3. **Route patients to booking** at specific hospitals via provider deep links — not to take bookings itself.
4. Serve **Sinhala and English** readers with independent collections.
5. Remain **dependency-free and privacy-preserving**: no cookies, storage, analytics, third-party scripts or hotlinked assets (privacy page claims this; verified true).
6. Work **without JavaScript** and by **opening files directly** (`file://`).

## 5. Scope

### In scope (implemented)
Public pages (Home, About, Conditions, Treatments, Patient Information, Clinics & Appointments, Articles, Contact, Privacy, Terms, 404), 56 reading pages, 3 legacy alias routes, clinic directory with provider deep links, bilingual article library, build/validation tooling.

### Explicitly out of scope (per repo docs) — CONFIRMED absent
- Staff CMS demonstration, `admin.html`, custom `page.html` routes (prototype features excluded "as requested").
- Sample clinics, fabricated schedules, mock booking dialogs, enquiry forms.
- Personal telephone, WhatsApp and e-mail actions (no public contacts supplied).
- Fees, addresses, recurring timetables, video consultations, availability claims.
- Testimonials, patient/operation counts, unverified credential dates.
- File uploads, accounts, payments, medical-record handling.

### Not mentioned anywhere (UNKNOWN whether in scope)
Tamil language, appointment reminders, online payments, analytics, newsletter, blog beyond the 40 archived articles, multi-doctor support.

## 6. System boundary

```
INSIDE THE REPOSITORY                               OUTSIDE (referenced, not controlled)
─────────────────────────────────────────────       ───────────────────────────────────────────
content/*.json  ──►  scripts/*.py  ──►  *.html      eChannelling · Doc990 (booking)
(site data & drafts)  (generator)      styles/ scripts/ assets/    NHS UK (reference links)
                                                    GitHub Pages (hosting) · GitHub Actions (sample)
                                                    Pexels (dev-time image download only)
                                                    Sibling folders on the developer's machine:
                                                      questionnaire.md · link-verifier report ·
                                                      orthopaedic.lk article archive · banners · prototype
```

## 7. Repository lineage and related artefacts

The repo's scripts and docs depend on **sibling folders in the parent directory** (not part of the repo):

| Artefact | Location (relative to repo) | Role | In repo? |
|---|---|---|---|
| `v4-OrthoConnect-Prototype-v2` | not found | Visual/structural reference for the 8-item nav and page structure | **NO** — not found anywhere nearby |
| `questionnaire.md` | `../questionnaire.md` | Source of "business facts and services" (README) | No — **not read** (outside repo) |
| `Dr_Suneth_De_Silva_Unified_Link_Verifier/` | `../` | Produced `VERIFICATION_RESULTS.json` (generated `2026-10-25T07:21:28+00:00`, SHA-256 recorded in `site.json`) — origin of all 26 booking URLs | No — read only by `check_clinics.py` |
| `orthopaedic-lk-content-archive-toolkit/` | `../` | Read-only scrape (2,271 files) of the legacy `orthopaedic.lk` WordPress site; origin of the 40 articles | No — read by `import_articles.py` / `check_article_migration.py` |
| `carossel images/` (sic) | `../` | Original banner artwork (4 PNG + 4 WebP) | No — copied into `assets/images/home-banners/` |
| `orthoconnect-lk-website/` | `../` | **Earlier non-git working copy** — differs from the repo in 5 files (`about.html`, `content/site.json`, `README.md`, `scripts/build_site.py`, `styles/main.css`) and lacks `.github/`, `.gitignore`, `.nojekyll`. The repo is canonical; the sibling is stale. | No — but **`README.md:139` hard-codes a path into it** |
| `website-build-files/` | `../` | `build-prompt.md`, `sitemap.md` — possibly requirement-like documents | No — **not read** (outside repo; see `14_SRS_ANALYSIS.md`) |

## 8. Development timeline (git + file evidence)

| Date (UTC+05:30) | Event | Evidence |
|---|---|---|
| ≈2026-10-24 → 10-28 | Development occurs **outside git** (file mtimes from 24 Oct; docs say "no usable Git metadata") | INFERRED — mtimes; `docs/clinic-validation.md` |
| 2026-10-28 19:52 | `Initial commit` (README stub) | `git log` |
| 2026-10-28 19:57 | `feat: add OrthoConnect static website and bilingual article library` (whole site, 460+ files) | `git show --stat` |
| 2026-10-28 20:17 | Sample Jekyll GitHub Actions workflow added | `e06d25c` |
| 2026-10-28 20:24 | `ci: configure static GitHub Pages publishing` (`.nojekyll`, README Pages section) | `3566d68` |
| 2026-10-29 19:44–19:49 | PR #1 — doctor profile/qualifications (adds 2 MRC Oxford diplomas, 3-column qualification grid) | `45d0ebc`, `3562fc3` |
| 2026-10-30 09:38–09:39 | PR #2 — About simplification (removes UK-fellowship timeline section; "JBJS MRC Oxford" → "MRC Oxford") | `a45dd5e`, `f4903c9` |

## 9. How to read the rest of this documentation set
Start with `00_EXECUTIVE_SUMMARY.md`, then `06_SYSTEM_ARCHITECTURE.md` (the mental model), then `18_DEVELOPMENT_GUIDE.md` if you intend to change anything.
