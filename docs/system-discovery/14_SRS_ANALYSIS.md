# 14 — SRS and Documentation Analysis

Evidence legend: **CONFIRMED · INFERRED · DOCUMENTED · NOT IMPLEMENTED · UNKNOWN**.

> ## ⚠ The SRS, reverse-engineering and architecture specifications were **not available**
> No requirement in this repository's analysis has been taken from — or attributed to — a document that was not read. **No SRS content was invented.** Where the brief asked for SRS-based comparison, this document records the gap and builds only on (a) the task brief and (b) the repository's own documentation, each clearly labelled.

## 1. Availability of reference documents

| Document | Expected by brief | Result | How searched |
|---|---|---|---|
| `orthopaedic-lk-reverse-engineering-spec.md` | yes | **NOT FOUND** | `find` by name in repo; filename-only search of parent project folder (depth 4) |
| `orthopaedic-lk-refined-srs-v2.md` | yes | **NOT FOUND** | same |
| `orthopaedic-lk-technical-architecture-spec-v2.md` | yes | **NOT FOUND** | same |
| `Dr_Suneth_De_Silva_Website_Profile_Content.docx` | yes | **NOT FOUND** | same (`*.docx` anywhere → none) |
| `CLAUDE.md` | created if absent | **Absent before this task** | created by this task |
| `README.md`, `content/README.md`, `ASSET-SOURCES.md`, `docs/*.md` (6) | — | **Present and read in full** | — |

**Please provide the four missing documents.** The only name match found near the repo was the **directory** `../orthopaedic-lk-content-archive-toolkit/` (the legacy-article scrape toolkit), which is not a specification.

### 1.1 Documents the repository *refers to* that are not in the repository
| Referenced item | Referenced by | Status |
|---|---|---|
| `v4-OrthoConnect-Prototype-v2` (prototype; source of the 8-item nav and page structure; includes `admin.html` and CMS pages that were excluded) | `README.md` | **Not found** anywhere nearby |
| `questionnaire.md` ("source of business facts and services") | `README.md`, `docs/…` | Exists at `../questionnaire.md`; **not read** (outside the repository) |
| `Dr_Suneth_De_Silva_Unified_Link_Verifier/VERIFICATION_RESULTS.json` | `content/site.json`, `check_clinics.py` | Exists; read only through the project's own checker |
| `orthopaedic-lk-content-archive-toolkit/` | `import_articles.py`, `check_article_migration.py` | Exists; read only through the project's own checker |
| "separate WordPress checkout" (Playwright was borrowed from it) | `docs/homepage-review.md` | **Not found**; implies a WordPress working copy exists elsewhere |

### 1.2 Candidate documents outside the repository (not read — please confirm if they may be used)
`../website-build-files/build-prompt.md`, `../website-build-files/sitemap.md`, `../questionnaire.md`. They may contain requirement-like material (a build prompt, a sitemap, business facts). Reading them was withheld because the brief scoped document study to "the repository".

## 2. Requirement sources actually available

| Source | Nature | Reliability |
|---|---|---|
| **Task brief** (this engagement) | A checklist of public/admin features to investigate; states tech assumptions (PHP/MySQL), domain `orthoconnect.lk`, and that `orthopaedic.lk` is historical terminology | Authoritative for the engagement; **contradicted by the code** on stack |
| `README.md` (170 lines) | Feature table, behaviours, verification claims, hosting | DOCUMENTED; partially verified; some drift (see §5) |
| `content/README.md` | Editing rules, data contracts, governance policy | DOCUMENTED; verified against code |
| `docs/*.md` | Dated validation records (25–28 Oct) | Historical snapshots — numbers vary and some statements are superseded |
| `ASSET-SOURCES.md` | Asset provenance and licensing statements | DOCUMENTED |
| The code and the passing checkers | What is actually enforced | CONFIRMED |

## 3. Requirements extracted from the repository's own documentation (DOCUMENTED; *not* SRS)

These are the closest thing to "requirements" the repo contains. They are cited by short IDs `R-xx` and traced in `15_REQUIREMENTS_TRACEABILITY.md`.

### 3.1 Business and stakeholder requirements
* Present the surgeon accurately, **without invented** years, registrations, testimonials, counts, fees, schedules or guarantees (`README.md` §Consultation directory, §Verification).
* Route patients to real, verified, hospital-specific booking pages on eChannelling/Doc990; booking and payment remain with providers.
* Publish educational content labelled as draft until clinically reviewed; keep "service scope" confirmation separate from "clinical review".
* Use the supplied logo and portrait **unchanged** (byte-identical).
* Do not link to or redirect to the legacy archive website; keep archive URLs internal.
* Exclude the prototype's staff CMS, `admin.html`, and CMS-created pages.

### 3.2 Functional requirements
* Eight-item main navigation, each opening its own HTML page; active state rendered in HTML.
* Pages: Home, About, Conditions, Treatments, Patient Information, Clinics & Appointments, Articles, Contact, Privacy, Terms, 404, plus legacy aliases.
* 18 consultation centres / 26 links, search + location + platform filters, shareable URLs.
* 40 articles in independent Sinhala/English collections with language/audience/region/topic/text filters and shareable URLs.
* 56 dedicated reading pages with breadcrumbs, contents, related reading, draft status.
* Homepage banner carousel (4 banners in order, 2 s, crossfade, no captions/arrows/pause button) and a manual resource carousel.

### 3.3 Non-functional requirements (as stated)
| Category | Statement | Source |
|---|---|---|
| Portability | Works by opening `index.html` directly; relative URLs; works under `/orthoconnect/` | README |
| Progressive enhancement | Content visible without JS; filters hidden without JS | README, `docs/*` |
| Privacy | No cookies, browser storage, analytics or tracking; filter state in URL | README, `privacy.html` |
| Accessibility | Semantic structure, skip link, ARIA, reduced motion — **"not a complete accessibility audit"** | README, `docs/article-validation.md` |
| Performance | Local WebP/PNG fallback banners, lazy images, no framework | `docs/homepage-carousel.md` |
| Typography | Local Noto Sans + Noto Sans Sinhala | README |
| Security | HTTPS-only external links; escaped content; no executable HTML from drafts | `content/README.md` |
| Maintainability | Edit JSON/templates, never generated HTML; rebuild; run checks | README |

### 3.4 Roles
Only implicit: **visitor** (all pages), **maintainer** (JSON + rebuild), **clinical reviewer** (sets `reviewed_by/on`). No in-system roles or permissions exist.

### 3.5 Constraints
No server; Python 3.12+ for builds; GitHub Pages hosting; draft/noindex until review; no personal contact details until supplied.

### 3.6 Open decisions (stated or evident in the docs)
1. Overlapping English child articles — merge/retire? (`article-migration-review.md` §1)
2. Sinhala child overview vs 11 articles; mismatched headings/images. (§2)
3. Clinical accuracy corrections required of the clinician. (§3)
4. Attribution/reuse of legacy text and images. (§4)
5. Sinhala summaries/UI wording review; audience double-tagging. (§5)
6. Service-scope confirmation (3 treatments, 5 conditions).
7. Whether/when to add public telephone/WhatsApp/e-mail.
8. Production privacy/legal review (`clinic-validation.md`).
9. Hosting/domain (brief says `orthoconnect.lk`; repo documents only the github.io project URL).

### 3.7 Client-approval dependencies
Items 3, 4, 6, 7, 8, 9 above; approval to publish drafts; approval to remove `noindex`; approval for provider logos in banner artwork; approval of qualification claims.

### 3.8 Future-expansion hints in the docs
"Add the doctor's longer drafts… when available"; "Personal contact actions should be added only after public contact details are supplied"; "Future clinical diagrams should receive clinical review"; "Reviewed content requires a named reviewer and date".

## 4. Categories requested by the brief — status of evidence

| Category | Evidence available | Gap |
|---|---|---|
| Business requirements | §3.1 | SRS absent |
| Stakeholder requirements | §3.1, `01_PROJECT_OVERVIEW.md` | SRS absent |
| Functional requirements | §3.2 + brief §6 checklist | SRS IDs unknown |
| Non-functional requirements | §3.3 | No quantified targets anywhere (no performance/availability/SLA numbers) |
| User roles | §3.4 | — |
| User journeys | `10_WORKFLOWS_AND_DATA_FLOWS.md` | Prototype absent |
| System constraints / technical requirements | §3.5, `04_TECH_STACK.md` | Brief's PHP/MySQL conflicts with code |
| Security requirements | none stated beyond §3.3 | SRS absent |
| Performance requirements | none quantified | SRS absent |
| SEO requirements | **none stated** (site is deliberately `noindex`) | SRS absent — likely to exist |
| Accessibility requirements | qualitative only; no WCAG level stated | SRS absent |
| Privacy requirements | §3.3 | Legal basis UNKNOWN |
| Deployment requirements | README: GitHub Pages; brief: `orthoconnect.lk` | **Conflict / gap** |
| Future expansion | §3.8 | SRS absent |

## 5. Conflicts between sources (recorded, not resolved)

| # | Statement A | Statement B | Resolution status |
|---|---|---|---|
| X-01 | **Brief:** existing implementation is HTML/CSS/**PHP**/JS/**MySQL** | **Code:** static HTML/CSS/JS generated by Python; no PHP/SQL | Code is the evidence; **client to explain** where the PHP system (if any) lives |
| X-02 | **Brief:** `orthopaedic.lk` is older terminology for this project; production domain is `orthoconnect.lk` | **`docs/article-migration-review.md` §4:** the archive "describes a different legacy practice… do not infer authorship or offered services for the new doctor" | **Unresolved — critical** (ownership of 40 articles / 251 images) |
| X-03 | **Brief:** `orthoconnect.lk` is the official domain | **Repo:** domain appears nowhere; README documents `dhananjayabandara.github.io/orthoconnect/`; no CNAME | Unresolved |
| X-04 | **Brief:** doctor content source is a `.docx` profile document | **README:** business facts come from `questionnaire.md` | Unresolved (neither read) |
| X-05 | **README (L32, L168):** About shows "JBJS MRC Oxford" diplomas, a "UK fellowship" and an "About timeline" | **Code/`site.json` (HEAD):** institution = "MRC Oxford"; fellowship/timeline section removed in `a45dd5e` | README stale |
| X-06 | **README L139:** run `…/orthoconnect-lk-website/scripts/download_images.py` | **Reality:** that folder is a stale copy; correct command is `python3 scripts/download_images.py` | README wrong |
| X-07 | **`docs/*.md` (25–28 Oct):** "No publication or deployment was performed"; "local, noindex draft preview"; "no usable Git metadata" | **README (29 Oct+):** site is hosted on GitHub Pages; Git history exists | Historical vs current |
| X-08 | **`docs/homepage-review.md`:** sample clinic notices/booking dialogs are preserved | **`docs/clinic-validation.md`:** they were removed; `check_clinics.py` forbids them | Superseded |
| X-09 | **Docs:** "All 70 routes… 5,226 / 5,364 / 5,384 / 5,541 / 5,597 local references" | **Executed audit today:** 5,386 | Counts are time-dependent snapshots |
| X-10 | **Doc statement (`docs/visual-design-validation.md`):** About page has "numbered timeline cards" | **HEAD:** removed | Superseded |

## 6. The `orthopaedic.lk` ↔ `orthoconnect.lk` terminology flag
Per the brief, `orthopaedic.lk` references are treated as **historical terminology and flagged for review**. Inventory (CONFIRMED):
* `orthopaedic.lk` appears in **44 tracked files**: all 40 `content/articles/*.json` (`archive.url`), `content/article-assets.json`, `content/article-migration.json`, `docs/article-migration-review.md`, `scripts/check_site.py` (rules forbidding links to it).
* It appears in **0 generated HTML pages** (and the audit forbids it).
* `orthoconnect.lk` appears in **0 files**.
* Consequence: the *only* place the old domain survives is **internal provenance**, but the *content* it supplied is the bulk of the site — see X-02.

## 7. SRS-compliance conclusion
**Cannot be assessed.** The matrix in `15_REQUIREMENTS_TRACEABILITY.md` therefore traces the brief's checklist and the repository's own documented requirements; every row that would need an SRS statement is marked **Cannot verify** or **Requires client confirmation**.
