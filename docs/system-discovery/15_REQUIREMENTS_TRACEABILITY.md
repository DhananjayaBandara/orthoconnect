# 15 — Requirements Traceability Matrix

Evidence legend: **CONFIRMED · INFERRED · DOCUMENTED · NOT IMPLEMENTED · UNKNOWN**.
Status values (as specified): **Implemented · Partially implemented · Not implemented · Not applicable · Cannot verify · Requires client confirmation**.

> **Important — what the IDs mean.** The SRS (`orthopaedic-lk-refined-srs-v2.md`) and the other reference documents were **not available** (`14_SRS_ANALYSIS.md`). These rows therefore do **not** carry SRS requirement numbers.
> * **BRIEF-nn** — items from the engagement brief's feature checklist (§2, §6) and stack assumptions.
> * **R-nn** — requirements stated in the repository's own documentation (`README.md`, `content/README.md`, `docs/*.md`).
> * **NFR-nn** — non-functional statements (repository docs or brief categories).
> * **G-nn** — content-governance obligations stated in the docs.
>
> When the SRS is supplied, add a column mapping each row to its SRS ID and add SRS-only rows; do not assume any row below is an SRS requirement.
> "Implemented" means the behaviour exists in source **and** is covered by a passing check or verified by inspection in this investigation. It does **not** mean clinically reviewed or client-approved.

## A. Public-facing features (brief §6)

| Requirement ID | Requirement | Source document | Current implementation | Evidence | Status | Gap |
|---|---|---|---|---|---|---|
| BRIEF-01 | Homepage | Brief §6 | `index.html`: banner carousel, profile hero, expertise, conditions + body-region explorer, treatments, clinics + journey, resources carousel, photo callout | `build_site.py:138-158`; `homepage.py`; `check_site.py` PASS; `check_home_banners_dom.cjs` 79 | **Implemented** | Hero/About facts are hard-coded copy needing client sign-off |
| BRIEF-02 | Navigation incl. responsive navigation | Brief §6 | 8-item header nav, active state, skip link, mobile menu with `inert`/Esc/outside-click; no-JS fallback list; footer nav; mobile bottom bar | `build_site.py:52-71`; `main.js:5-43`; `main.css:63-70,370-380`; `check_site.py:104-109`; `check_effects_dom.cjs` | **Implemented** | No real-browser pass since 25 Oct (historic) |
| BRIEF-03 | Doctor profile | Brief §6 | `about.html`: portrait, 5-paragraph profile, qualification cards, CTA | `build_site.py:161-168`; `site.json` `qualifications` | **Implemented** | Wording must be confirmed against the (missing) profile `.docx` / questionnaire — **Requires client confirmation** |
| BRIEF-04 | Professional qualifications | Brief §6 | 6 cards (MBBS; MD Orthopaedic Surgery; MRCSEd; MRC Oxford Hip diploma; MRC Oxford Foot & Ankle diploma; UK hip & knee training); 3 hero pills | `site.json:44-81`; `build_site.py:140` | **Implemented** | Credentials not independently verifiable (**Cannot verify**); facts duplicated in 4 places |
| BRIEF-05 | Medical services | Brief §6 | Home "key areas" (hip & knee; fracture & trauma; limb reconstruction) + Treatments listing | `build_site.py:143-147`; `treatments.html` | **Partially implemented** | 3 treatments flagged "SERVICE SCOPE TO CONFIRM" (foot & ankle, paediatric, non-operative) — **Requires client confirmation** |
| BRIEF-06 | Conditions and treatments | Brief §6 | 9 conditions (expandable, search/category filter) and 8 treatment pages | `site.json:82-205`; `library_page()`; 8 `content/treatments/*.json` | **Partially implemented** | All `draft`; treatment pages are 2 short paragraphs each; 5 conditions `pending` |
| BRIEF-07 | Medical information | Brief §6 | 8 patient guides + 6 FAQs + 40 articles | `content/patient-information/*.json`; `site.json` `faqs`; `content/articles/*.json` | **Partially implemented** | All drafts, unreviewed (G-01); guides intentionally contain no doses/timetables |
| BRIEF-08 | Hospital information | Brief §6 | 18 centres with name, optional branch/locality and booking buttons | `site.json` `clinics`; `clinic_card()` | **Partially implemented** | No addresses, telephones, maps (by policy); 2 centres have no locality |
| BRIEF-09 | Consultation schedules | Brief §6 | Not shown; visitors are sent to the provider's session list | `README.md` §Consultation directory; no schedule data | **Not implemented** | Deliberate: schedules/fees/availability belong to providers. **Requires client confirmation** if on-site schedules are expected |
| BRIEF-10 | Appointment-related actions | Brief §6 | "Find a Consultation" CTAs; provider deep links; booking help/change guidance | `clinics.html`, `contact.html`; `check_clinics.py` PASS | **Partially implemented** | No on-site booking/request (by design, W-X3). Interpretation of the requirement **Requires client confirmation** |
| BRIEF-11 | Contact information | Brief §6 | Contact page with booking help, change-appointment guidance, preparation link, emergency note | `build_site.py:249-251` | **Partially implemented** | No public telephone, e-mail, address — "public contacts were not supplied" (README) — **Requires client confirmation** |
| BRIEF-12 | Telephone links | Brief §6 | None | 0 `tel:` in 70 pages; sprite has unused `phone` icon | **Not implemented** | Needs a public number from the client |
| BRIEF-13 | WhatsApp integration | Brief §6 | None (only banner artwork/alt mention "optional WhatsApp enquiries") | 0 `wa.me`/`whatsapp` links | **Not implemented** | Needs number + policy/privacy update |
| BRIEF-14 | Maps and directions | Brief §6 | None | 0 map links; no addresses in data | **Not implemented** | Needs verified addresses/coordinates per centre |
| BRIEF-15 | External booking services | Brief §6 | eChannelling ×13, Doc990 ×13 deep links on 18 cards | `clinic_directory.py`; `check_clinics.py` PASS vs verifier report | **Implemented** | Links last verified 2026-10-25; liveness **Cannot verify** now |
| BRIEF-16 | Footer | Brief §6 | Identity, nav, consultation block, disclaimer, policy links, year | `build_site.py:65-71` | **Implemented** | — |
| BRIEF-17 | Legal and privacy pages | Brief §6 | `privacy.html`, `terms.html` (6 sections each) | `build_site.py:254-276` | **Implemented** | Production legal/privacy review not recorded — **Requires client confirmation** |

## B. Administrative features (brief §6)

| Requirement ID | Requirement | Source document | Current implementation | Evidence | Status | Gap |
|---|---|---|---|---|---|---|
| BRIEF-20 | Authentication (login/logout), session management | Brief §6 | None | no server code; no cookies/storage | **Not implemented** | Prototype CMS excluded by design; none needed for a static site |
| BRIEF-21 | User management, roles & permissions | Brief §6 | None | — | **Not implemented** | — |
| BRIEF-22 | Dashboard / settings | Brief §6 | None | — | **Not implemented** | — |
| BRIEF-23 | Content management / CRUD | Brief §6 | Developer-operated: edit JSON → rebuild → check → commit | `content/README.md`; `build_site.py` | **Not implemented** (as an interface) | Non-technical editing impossible; `content/README.md`: "not a staff authentication or approval system" |
| BRIEF-24 | Form submissions and server-side validation | Brief §6 | No submission forms; build-time validators only | forms are filters; `<form action>` absent | **Not implemented** | By design (privacy) |
| BRIEF-25 | File uploads | Brief §6 | None | FAQ: "no medical-file upload facility" | **Not implemented** | By design |

## C. Technology and deployment assumptions (brief §2)

| Requirement ID | Requirement | Source | Current implementation | Evidence | Status | Gap |
|---|---|---|---|---|---|---|
| BRIEF-30 | Implementation in PHP | Brief §2 | Python build tool + static output | 0 `.php` | **Not applicable** | Brief/code mismatch (X-01) — **Requires client confirmation** where any PHP system lives |
| BRIEF-31 | MySQL / MariaDB persistence | Brief §2 | None | no SQL | **Not applicable** | — |
| BRIEF-32 | Production domain `orthoconnect.lk` | Brief §2 | Not present; github.io project URL documented | 0 occurrences; no `CNAME` | **Not implemented** | DNS/CNAME/TLS and absolute-URL decisions (canonical, sitemap) |
| BRIEF-33 | Study of reverse-engineering spec, SRS v2, architecture spec v2, profile `.docx` | Brief §2, §13 | Documents missing | search | **Cannot verify** | Please supply |
| BRIEF-34 | Treat `orthopaedic.lk` as historical terminology and flag it | Brief §2 | Flagged: 44 files; 0 pages; see `14_…` §6 | `grep` | **Implemented** (flagged) | Meaning of the term conflicts across sources (X-02) |

## D. Requirements stated in repository documentation

| Requirement ID | Requirement | Source document | Current implementation | Evidence | Status | Gap |
|---|---|---|---|---|---|---|
| R-01 | Each of the 8 nav items opens its own HTML page; active state rendered in HTML | README §Public pages | Yes | `check_site.py:104-109` PASS | **Implemented** | — |
| R-02 | Nav/page structure follows `v4-OrthoConnect-Prototype-v2` | README intro | Prototype not available | — | **Cannot verify** | Supply prototype |
| R-03 | Clinic directory: 18 centres, 26 links; search + location + platform filters; shareable URLs; no-JS full list | README; `docs/clinic-validation.md` | Yes | `clinics.js`; `check_clinics_dom.cjs` 250 | **Implemented** | — |
| R-04 | Provider URLs exactly equal the supplied verification report | `content/README.md` | Yes | `check_clinics.py` PASS (executed with report) | **Implemented** | Report is from 2026-10-25 |
| R-05 | 40 articles (19 EN / 21 SI), independent collections, 5 filters, Unicode search, shareable URLs, return links restore selection | README; `docs/article-validation.md` | Yes | `articles.js`; `check_articles_dom.cjs` 42; `check_article_migration.py` PASS | **Implemented** | Sinhala wording/shaping unreviewed in browser |
| R-06 | 56 reading pages: breadcrumbs, contents, related reading, status labels, consultation links | README §Dedicated reading pages | Yes | `reading_page()`, `article_reading_page()`; `check_site.py` | **Implemented** | — |
| R-07 | Homepage banners: 4 in order, 2 s autoplay, 1 s fade, dots/keys/swipe, pauses (hover/focus/hidden/off-screen/touch), reduced-motion off, no captions/arrows/pause button | `docs/homepage-carousel.md` | Yes | `home.js`; `check_home_banners_dom.cjs` 79 | **Implemented** | Accessibility consequence — see A-02 |
| R-08 | Manual resource carousel (6 cards), grid without JS | README | Yes | `home.js:132-195` | **Implemented** | — |
| R-09 | Legacy routes `services.html`, `medical-information.html`, `hospitals.html` work without redirects | README | Byte-identical copies | `cmp`; `check_clinics.py:80` | **Implemented** | Duplicate-content risk when indexing is enabled |
| R-10 | 404 page with working home & consultation routes | README | Yes | `not_found()` | **Implemented** | Unstyled on nested missing paths |
| R-11 | Old `#fragment` links forward to dedicated pages | README | Build-time rewrite + runtime `location.replace` | `reading_content.py:85-96`; `main.js:86-103` | **Implemented** | — |
| R-12 | Logo and portrait used unchanged | README §Original branding | Single commit each since added; no later modification | `git log` per file | **Implemented** | Equality to the supplied originals **Cannot verify** (originals not in repo) |
| R-13 | No testimonials, patient/operation counts, fees, schedules, availability or guarantees | README §Consultation directory | None found on non-article pages | regex sweep of page text (4 false-positive hits only) | **Implemented** | Legacy articles are unreviewed text |
| R-14 | No public link/redirect to the legacy archive site | README; `content/README.md` | None | `check_site.py:99,112` PASS; 0 pages mention it | **Implemented** | — |
| R-15 | Inline images local, JPEG/PNG, alt text, intrinsic dimensions, lazy-loaded | `content/README.md` | Yes | `reading_content.py:129-170`; `check_site.py:124-127` | **Implemented** | — |
| R-16 | `status` draft/reviewed; reviewed requires reviewer + non-future date; no inferred bylines | `content/README.md` | Enforced | `reading_content.py:49-55` | **Implemented** | 0 reviewed |
| R-17 | Original treatment illustrations hash-pinned | `content/README.md` | Enforced | `visual_design.py:26` | **Implemented** | Not clinically reviewed |
| R-18 | Stock photos local, 640/1280 px, credited internally, restorable via script | README §Stock photography | Yes | `download_images.py --check` PASS | **Implemented** | — |
| R-19 | Consistent shared visual effects on all 70 routes; honour reduced motion | `docs/visual-design-validation.md` | Yes | `check_effects_dom.cjs` 257 | **Implemented** | Rendering not browser-verified |

## E. Non-functional requirements

| Requirement ID | Requirement | Source | Current implementation | Evidence | Status | Gap |
|---|---|---|---|---|---|---|
| NFR-01 | Works by opening files directly (`file://`) and under `/orthoconnect/` | README | Pure relative URLs | 0 root-relative URLs; DOM suites run `file://` cases | **Implemented** | — |
| NFR-02 | Usable without JavaScript | README, docs | Yes | DOM suites' no-JS cases; CSS `.js-enabled` scoping | **Implemented** | — |
| NFR-03 | No cookies, browser storage, analytics, tracking | README, `privacy.html` | None | JS/HTML sweeps | **Implemented** | Update policy if that ever changes |
| NFR-04 | Accessibility (semantics, skip link, ARIA, focus, reduced motion) | README | Strong structural baseline | `check_site.py`; CSS | **Partially implemented** | No audit/tooling/screen-reader pass; carousel pause gap (A-02) |
| NFR-05 | Performance (lazy images, local WebP, no framework) | `docs/homepage-carousel.md` | Mostly | §13 of this set | **Partially implemented** | Unoptimised fonts (P-01); no budgets |
| NFR-06 | Security (HTTPS-only external links, escaped content) | `content/README.md` | Yes | `12_…` §3 | **Implemented** | Hosting-level controls unmanaged (S-01, S-03, S-04) |
| NFR-07 | Maintainability: edit sources, rebuild, run checks | README | Documented workflow | executed | **Implemented** | No CI; docs drift (M-04) |
| NFR-08 | Sinhala typography with local fonts, `lang` tagging | README | Yes | `main.css:3-4`; `check_article_migration.py` | **Implemented** | Browser shaping unverified (A-04) |
| NFR-09 | SEO | Brief category (no source text) | Deliberately `noindex`; no canonical/sitemap/robots/OG/JSON-LD | `build_site.py:365` | **Not implemented** | Likely SRS requirement; **Requires client confirmation** |
| NFR-10 | Hosting on GitHub Pages with HTTPS | README | Documented | not fetched | **Cannot verify** | Live state unknown |
| NFR-11 | Browser-support matrix | — | None stated | — | **Requires client confirmation** | — |
| NFR-12 | Tamil language support | — | None | `lang` values only en/si | **Requires client confirmation** | Doc990 links to Tamil provider pages exist (4) |
| NFR-13 | Analytics/reporting | — | None | — | **Requires client confirmation** | Would change the privacy posture |
| NFR-14 | Availability/SLA, backups, monitoring | — | Git + GitHub only; no monitoring | — | **Cannot verify** | No targets stated |

## F. Governance obligations (stated in docs)

| Requirement ID | Requirement | Source | Status | Gap |
|---|---|---|---|---|
| G-01 | Clinical review of educational content before it is treated as reviewed | `content/README.md`, `docs/article-migration-review.md` | **Not implemented** | 0 of 56 reviewed; known copy errors flagged for the clinician |
| G-02 | Confirm service scope separately (`pending`) | `content/README.md` | **Requires client confirmation** | 3 treatments, 5 conditions |
| G-03 | Confirm attribution & reuse rights for archive text/images before release | `docs/article-migration-review.md` §4 | **Requires client confirmation** | 40 articles, 251 images, branded X-rays, first-person text |
| G-04 | Native review of Sinhala summaries/UI wording | `docs/article-migration-review.md` §5 | **Requires client confirmation** | — |
| G-05 | Reconcile overlapping English child articles; correct Sinhala overview mismatches | `docs/article-migration-review.md` §1-2 | **Requires client confirmation** | — |

## G. Summary counts
| Status | Rows |
|---|---:|
| Implemented | 32 |
| Partially implemented | 8 |
| Not implemented | 13 |
| Not applicable | 2 |
| Cannot verify | 4 |
| Requires client confirmation | 7 |
| **Total** | **66** |

(Counted programmatically from the status cells of the tables above. Each row carries its *primary* status; many "Implemented" rows also have a client-confirmation note in *Gap*.)
