# 20 — Architectural Decisions and Open Questions

Evidence legend: **CONFIRMED · INFERRED · DOCUMENTED · NOT IMPLEMENTED · UNKNOWN**.
This file separates **what was decided and built** (§1–3) from **what is unresolved** (§4–6) and from **options for discussion** (§7). §7 is *not* the existing architecture and is *not* a plan.

## 1. Confirmed architectural decisions (as built)

| ID | Decision | Rationale (stated or inferred) | Consequences | Evidence |
|---|---|---|---|---|
| **AD-01** | **Static output; no server, database, sessions or admin** | "No installation, API, build step or Internet connection is needed to view the website" | Zero runtime attack surface and cost; no on-site booking, forms, CMS UI | CONFIRMED — absence scans; `README.md` |
| **AD-02** | **Python-stdlib generator with committed output** | Dependency-free maintainer tooling; GitHub Pages serves committed files | Reproducible byte-for-byte; PR diffs contain generated HTML; correctness depends on running local checks | CONFIRMED — executed rebuild diff |
| **AD-03** | **One JSON document per reading page**, hub `site.json`, typed blocks | Long drafts editable independently; stable IDs; safe rendering | Clear migration path to any CMS; hub coupling | CONFIRMED — `content/README.md`, `reading_content.py` |
| **AD-04** | **Validate everything before writing any file** | Never ship half-built or malformed pages | Early, specific errors | CONFIRMED — `build_site.py:19-23` |
| **AD-05** | **GitHub Pages branch publishing from repo root with `.nojekyll`** | Simple hosting; Jekyll not wanted | Entire root published (S-01); platform limits on headers | DOCUMENTED — README; `.nojekyll` CONFIRMED |
| **AD-06** | **Draft-by-default, `noindex,nofollow`, visible "educational draft" labels** | No clinical approval exists; avoid implying review | Site invisible to search; blocks launch until deliberately changed | CONFIRMED — `build_site.py:365`; labels in templates |
| **AD-07** | **Privacy by construction**: no cookies, storage, analytics, third-party scripts; filter state in the URL | Patient trust; legal simplicity | No usage insight; policy text must stay in sync | CONFIRMED |
| **AD-08** | **Booking delegated to providers via validated deep links**; missing providers omitted; same-tab; no intermediate dialog | Doctor already uses eChannelling/Doc990; avoid handling patient data | Link rot is the main operational risk; integrity depends on repo access | CONFIRMED — `clinic_directory.py`, `check_clinics.py` |
| **AD-09** | **Progressive enhancement and `file://` support via pure relative URLs; `hidden`/`.js-enabled` pattern** | Resilience, offline review, project-path hosting | URL rewriting complexity; aliases and 404 use relative URLs | CONFIRMED |
| **AD-10** | **Local assets only** (self-hosted fonts, images, SVG sprite); no hotlinks | Privacy, reliability | Heavier repo; TTF fonts unoptimised | CONFIRMED |
| **AD-11** | **Legacy articles imported byte-faithfully with provenance and an independent conservation audit**; importer kept separate from the normal build | Avoid silent editorial changes; traceability | Legal/attribution questions remain; audit needs the archive | CONFIRMED |
| **AD-12** | **Legacy routes as full-page copies, not redirects** | Works without JS/HTTP redirects | Duplicate content once indexed | CONFIRMED — `cmp` identical |
| **AD-13** | **"Do not invent facts" policy** — omit unknown localities, contacts, fees, schedules, bylines, review dates | Medical-site credibility | Sparse contact/clinic data | DOCUMENTED + enforced in code |
| **AD-14** | **Prototype CMS/admin excluded**; sample clinics/booking demos removed | Public-only scope "as requested" | Maintainer-only editing | DOCUMENTED; `check_clinics.py:76-79` enforces |
| **AD-15** | **Independent Sinhala and English article collections** (no inferred translation pairs); native Sinhala typography and strings | Source content is not a translation set | No hreflang; chrome English-only | CONFIRMED — `article_library.TEXT`, README |
| **AD-16** | **Hand-written design system on tokens; no framework; original SVG illustrations; motion respects `prefers-reduced-motion`** | Control, size, accessibility | Single large `main.css`; dead selectors accumulate | CONFIRMED |
| **AD-17** | **Verification by purpose-built audits** (structure, clinics, archive conservation) plus jsdom suites instead of CI | Works in restricted sandboxes; evidence trail in `docs/` | No automated gate | CONFIRMED |

## 2. Existing architectural compromises

| ID | Compromise | Why it exists | Cost |
|---|---|---|---|
| CO-01 | Core copy (home, about, contact, policies, featured IDs) lives in Python, not JSON | Faster to build; markup and copy together | Non-developers can't edit; facts duplicated in 4 places |
| CO-02 | Generated HTML committed to git | Pages serves committed files; no build step on host | Stale-output risk with no CI |
| CO-03 | Checks depend on sibling folders at fixed paths | Evidence lives outside the repo | Fresh clones can't verify |
| CO-04 | Whole repo root published | Simplest Pages setup | Internal files public |
| CO-05 | Banner carousel has no pause button | Explicit user request (2 s, no controls) | Likely WCAG 2.2.2 gap |
| CO-06 | `noindex` hard-coded constant | Safety default | Launch needs a code change + rebuild of 73 files |
| CO-07 | Archive images kept byte-identical (no recompression) | Provenance fidelity | Heavy pages (≤1.9 MiB images) |
| CO-08 | Fonts are the system-package TTFs | "copied from the installed system font package" | 1.6 MiB; no subsetting |
| CO-09 | Alias duplicates instead of redirects | Hosting can't redirect | Canonical needed later |
| CO-10 | Stale sibling copy of the project kept beside the repo | Pre-git working folder | Wrong-tree edits |

## 3. Intended/assumed vs actual architecture

| Aspect | Brief / assumption | Actual |
|---|---|---|
| Runtime | PHP application | Static files |
| Persistence | MySQL/MariaDB | JSON in git |
| Admin | Possibly (brief asks to investigate) | None, excluded |
| Hosting | `orthoconnect.lk` | GitHub Pages project URL documented; domain unconfigured |
| Content origin | Doctor-supplied profile `.docx`, SRS | `questionnaire.md` + archive of `orthopaedic.lk` |
| Target architecture | A "technical architecture spec v2" exists (possibly proposing WordPress — **UNKNOWN**, not read) | None implemented |
| SEO | Likely required | Deliberately disabled |

## 4. Open technical questions

| ID | Question | Why it matters |
|---|---|---|
| TQ-01 | Are GitHub Pages settings as documented (source branch/root, HTTPS enforced, custom domain, sample workflow disabled)? | Determines what is actually live (S-01, S-05) |
| TQ-02 | Is branch protection / required review enabled on `main`? | Booking-link integrity (S-04) |
| TQ-03 | Do all 26 booking links still resolve to the doctor's sessions? | Core journey |
| TQ-04 | Does the current UI pass a real-browser and device pass (320–1920 px, touch, keyboard), including Sinhala shaping? | Last evidence is 25 Oct, pre-redesign |
| TQ-05 | What are the intended browser-support and performance budgets? | Fonts/images decisions |
| TQ-06 | Should internal docs, scripts, provenance JSON be excluded from the published artefact? | S-01 |
| TQ-07 | Should the stdlib-only Python approach be kept if the site grows (templating, content schemas, CI)? | Maintainability |
| TQ-08 | Where does a PHP/MySQL/WordPress system referenced by the brief and by `docs/homepage-review.md` ("separate WordPress checkout") actually live? | Possibly the real "existing implementation" |

## 5. Decisions requiring client approval

| ID | Decision | Dependency |
|---|---|---|
| CD-01 | Reuse (or not) of legacy `orthopaedic.lk` text and images; attribution; watermarked X-rays; first-person passages | OQ-02 |
| CD-02 | Clinical review workflow and reviewer(s); who signs off the 56 drafts and corrects the known copy errors | G-C01, G-C05 |
| CD-03 | Service-scope confirmations (3 treatments, 5 conditions) | G-C03 |
| CD-04 | Public contact details and whether to add telephone, WhatsApp, e-mail, address/map | G-F01-03 |
| CD-05 | Domain, hosting platform and launch date; lifting `noindex`; SEO scope | G-S01-05 |
| CD-06 | Carousel pause control vs the "no controls" instruction; banner timing | A-02 |
| CD-07 | Use of eChannelling/Doc990/WhatsApp marks in banner artwork | G-C10 |
| CD-08 | Privacy policy and Terms legal review | G-S07 |
| CD-09 | Languages (Tamil? localised chrome?) | G-F08-09 |
| CD-10 | Analytics yes/no (would change privacy posture and policy) | NFR-13 |
| CD-11 | Verification of qualification wording | G-C09, G-C12 |
| CD-12 | Whether to publish or keep private the engineering documentation set | S-01 |

## 6. Open questions to the developer/client (summary list)

| ID | Question |
|---|---|
| OQ-01 | Is the intended future platform PHP/MySQL (or WordPress), or is the static/Python approach the approved direction? Where is any existing PHP system? |
| **OQ-02** | **What is `orthopaedic.lk`? The brief says historical terminology for this project; `docs/article-migration-review.md` says "a different legacy practice… do not infer authorship". Who owns the 40 articles and 251 images, and is reuse permitted?** |
| OQ-03 | Please supply `orthopaedic-lk-reverse-engineering-spec.md`, `orthopaedic-lk-refined-srs-v2.md`, `orthopaedic-lk-technical-architecture-spec-v2.md`, `Dr_Suneth_De_Silva_Website_Profile_Content.docx`, and the prototype `v4-OrthoConnect-Prototype-v2`; may `questionnaire.md` and `website-build-files/*` be read? |
| OQ-04 | What is the DNS/hosting plan for `orthoconnect.lk` (registrar, TLS, GitHub Pages custom domain vs another host)? |
| OQ-05 | Should `docs/system-discovery/` be committed to this (published) repository? |
| OQ-06 | Which SEO requirements apply, and when should `noindex` be lifted? |
| OQ-07 | Which public contact channels may be shown? |
| OQ-08 | Who clinically reviews content, and on what timeline? |
| OQ-09 | Which languages are required beyond English/Sinhala? |
| OQ-10 | Is a persistent carousel pause control acceptable to the client? |
| OQ-11 | Who owns booking-link maintenance, and at what cadence? |
| OQ-12 | May CI and branch protection be added? |
| OQ-13 | Should the stale `orthoconnect-lk-website/` folder be archived/deleted? |
| OQ-14 | Where are the original supplied logo/portrait files (to confirm byte-equality)? |
| OQ-15 | What is the licensing intent for the repository (no LICENSE file)? |

## 7. Options for discussion (informational — not the existing architecture, not a recommendation to change)

| Option | Sketch | Pros | Cons / unknowns |
|---|---|---|---|
| **A. Keep the SSG, add guardrails** | CI that rebuilds and diffs, runs the three audits (and DOM suites); allow-listed publish artefact; branch protection; WOFF2 fonts; schema validation; move copy to JSON | Smallest change, preserves privacy and zero-runtime-risk posture | Still developer-edited; clinician workflow remains manual |
| **B. SSG + Git-based editorial UI** | Keep the JSON model, add a hosted editorial layer for clinicians | Non-developer editing without a server stack | New dependency/vendor; auth model needed |
| **C. Migrate to WordPress (PHP/MySQL)** | Map `reading_draft` → custom post type, `taxonomy_key` → taxonomies, `clinic`/`booking_link` → custom fields, Sinhala/English via a multilingual plugin | Familiar CMS, built-in roles/review workflow; matches the brief's PHP/MySQL framing | Large rewrite; hosting, patching and security burden; the current privacy/zero-attack-surface benefits are lost; **no evidence in the repo that this has been approved or started** |

The content model in `09_DATABASE_ARCHITECTURE.md` is deliberately CMS-agnostic, so any option can reuse it. Choose only after OQ-01 and the missing architecture spec are resolved.

## 8. How to maintain this record
Record new decisions as `AD-nn` with context, decision, consequences and evidence. When an open question is answered, move it to §1 or §5 with the date and source. Never record an unverified claim as CONFIRMED.
