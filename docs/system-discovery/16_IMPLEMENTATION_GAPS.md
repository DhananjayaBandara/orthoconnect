# 16 — Implementation Gaps, Discrepancies and Drift

Evidence legend: **CONFIRMED · INFERRED · DOCUMENTED · NOT IMPLEMENTED · UNKNOWN**.
"Gap" = something required, expected, or implied that is missing, incomplete, inconsistent or unverified. Severity is the impact **if the site were launched as-is** (today it is `noindex` and draft-labelled, which mitigates several items). "Decision" says who must act; nothing here has been changed.

## 1. Content and governance gaps (G-C)

| ID | Gap | Evidence | Severity | Decision |
|---|---|---|---|---|
| **G-C01** | **No clinically reviewed content.** 56/56 reading pages `status: "draft"`, no author/reviewer/date | `content/*/*.json` aggregate | **High** | Clinician |
| G-C02 | **Treatment and guide pages are skeletal**: 8 treatments = 2 short paragraphs each (16 total); 8 guides = ~2 paragraphs + a list each. The depth lives only in the imported archive articles | JSON block counts | Medium | Client to supply the "longer drafts" (README) |
| G-C03 | **Service scope unconfirmed**: treatments `foot-ankle-procedures`, `paediatric-procedures`, `non-operative-care`; conditions `shoulder-elbow`, `hand-wrist`, `foot-ankle`, `paediatric`, `arthritis` | `pending: true` | Medium | Clinician |
| **G-C04** | **Provenance/rights of legacy content.** 40 articles + 251 images come from `orthopaedic.lk` (WordPress; "a different legacy practice" per repo docs; "historical terminology" per brief). First-person passages, branded/watermarked X-rays, other-practice credentials retained | `docs/article-migration-review.md` §4; `archive` blocks | **High** | Client/Legal |
| G-C05 | **Known copy errors**: adult hip & foot/ankle articles contain "shoulder/arm wording that appears copied from another topic"; Sinhala overview has mismatched headings/images (e.g. trigger-finger/wrist diagrams beside child dislocation topics) | `docs/article-migration-review.md` §2-3 | **High** | Clinician |
| G-C06 | **Overlapping English children's articles** (`en-children-shoulder` ⟷ `en-children-upper-arm`, 14 shared paragraphs; repeated numbered lists) | same §1 | Low–Medium | Editorial |
| G-C07 | Sinhala summaries, taxonomy labels and UI strings never reviewed by a native speaker | same §5 | Medium | Editorial |
| G-C08 | **No public contact details** (phone, WhatsApp, e-mail, address) | README | Medium | Client |
| G-C09 | **Credential claims unverifiable** here (MBBS, MD, MRCSEd, MRC Oxford diplomas with Distinction, 24 months UK training); source documents missing | `site.json`; missing `.docx` | Medium | Client |
| G-C10 | **Third-party marks** (eChannelling, Doc990, WhatsApp) baked into banner #4 artwork; no permission recorded | `ASSET-SOURCES.md` | Low–Medium | Client |
| G-C11 | Stock-photo credits intentionally not displayed on pages (kept only in internal records) — confirm this satisfies the licence/attribution stance | `ASSET-SOURCES.md` | Low | Client |
| G-C12 | Qualification wording changed across commits ("JBJS MRC Oxford" → "MRC Oxford") with no recorded source verification | commits `45d0ebc`, `a45dd5e` | Low | Client |

## 2. Functional gaps (G-F)

| ID | Gap | Evidence | Severity | Note |
|---|---|---|---|---|
| G-F01 | Telephone link / click-to-call | 0 `tel:` | Medium | needs number |
| G-F02 | WhatsApp contact | 0 links; only artwork | Medium | needs number + policy update |
| G-F03 | Maps / directions / addresses | 0 | Medium | needs verified data |
| G-F04 | Consultation schedules / fees | none (policy) | Low | delegated to providers |
| G-F05 | On-site appointment request or enquiry form | removed demo | Low | design decision (privacy) |
| G-F06 | Admin/CMS, authentication, roles, dashboard | none (excluded) | Medium for non-technical editing | A developer is required for every copy change |
| G-F07 | Whole-site search | per-listing filters only | Low | — |
| G-F08 | Tamil language | none | Unknown | Doc990 links open Tamil provider pages for 4 centres |
| G-F09 | Site chrome not localised on Sinhala pages | `lang="en"` wrappers | Low | — |
| G-F10 | Print/PDF handout of guides | print CSS exists; not verified | Low | — |

## 3. Launch / SEO gaps (G-S)

| ID | Gap | Evidence | Severity at launch |
|---|---|---|---|
| **G-S01** | **`noindex,nofollow` on all 70 pages** (hard-coded) | `build_site.py:365` | **High** (site invisible to search) — intentional today |
| G-S02 | No canonical URLs; 3 duplicate alias pages | 0/70 pages | Medium |
| G-S03 | No `sitemap.xml` / `robots.txt` | file check | Medium |
| G-S04 | No Open Graph/Twitter metadata, no JSON-LD (Physician/MedicalBusiness/BreadcrumbList) | grep | Medium |
| **G-S05** | **`orthoconnect.lk` unconfigured**: no CNAME, no absolute URLs, no mention anywhere | grep | **High** for go-live |
| G-S06 | Favicon is the logo JPEG only (no ICO / PNG set / manifest) | `<head>` | Low |
| G-S07 | Privacy/Terms are generic; "production legal review" not recorded | `docs/clinic-validation.md` | Medium |

## 4. Technical gaps (G-T)

| ID | Gap | Evidence | Severity |
|---|---|---|---|
| **G-T01** | **No CI gate**: nothing rebuilds and diffs, runs audits, or protects booking links | only a disabled Jekyll sample | **High** (integrity) |
| G-T02 | Undeclared dev dependencies (jsdom, Playwright, Chrome, Pillow); no `package.json`/`requirements` | — | Medium |
| G-T03 | Two checkers + importer require sibling folders; fresh clone cannot run full verification | `check_clinics.py:13`, `check_article_migration.py:139`, `import_articles.py:157` | Medium |
| G-T04 | Fonts unoptimised (1.6 MiB TTF) | `13_…` P-01 | Medium |
| G-T05 | Carousel lacks a persistent pause/stop (WCAG 2.2.2) | `13_…` A-02 | Medium |
| G-T06 | Real-browser suite not run since before the clinic/banner/effects work; no screenshots of current UI; Sinhala shaping unverified | `docs/*` | Medium |
| G-T07 | No link-liveness monitoring for 26 booking URLs + 4 NHS URLs | — | Medium |
| G-T08 | 404 page unstyled on nested missing URLs | relative URLs | Low |
| G-T09 | Dead code: 7 orphaned CSS classes, 7 unused tokens, 4 unused icons, dead generator branches, dead `.training-timeline`/`.fellowship-layout` selectors in JS/CSS | `05_…` §6 | Low |
| G-T10 | `import_articles.py --replace` can destroy editorial changes | `import_articles.py:169` | Medium |
| G-T11 | Content duplicated in Python and JSON; doctor facts in 4 places | `13_…` M-01 | Medium |
| G-T12 | No accessibility tooling / performance budget / visual regression | — | Low–Medium |

## 5. Documentation drift and inconsistencies (G-D)

| ID | Drift | Evidence | Fix owner |
|---|---|---|---|
| **G-D01** | README About row still lists "JBJS MRC Oxford… UK fellowship, training overview" | `README.md:32` vs `site.json` ("MRC Oxford"), `about()` | Maintainer |
| G-D02 | README/docs describe an "About timeline" (numbered milestone cards) removed in `a45dd5e`; CSS and `effects.js` selectors remain | `README.md:168`; `docs/visual-design-validation.md:15`; `effects.js:66` | Maintainer |
| G-D03 | README tells you to run `…/orthoconnect-lk-website/scripts/download_images.py` (stale sibling copy, absolute path) | `README.md:139` | Maintainer |
| G-D04 | Validation docs carry time-specific counts (5,226 / 5,364 / 5,384 / 5,541 / 5,597 refs; 31/35/19 stock placements); today 5,386 / 19 | `docs/*.md` | Maintainer (mark as historical) |
| G-D05 | `docs/*.md` say "No publication or deployment was performed", "local, noindex draft preview", "no usable Git metadata" — superseded by hosting + git | `docs/article-validation.md`, `clinic-validation.md`, `visual-design-validation.md` | Maintainer |
| G-D06 | Local absolute paths (`/home/…`, `/tmp/…`) in 5 published docs | S-02 | Maintainer |
| G-D07 | Historical screenshots in `docs/previews/` predate the current UI | `README.md` | Maintainer |
| G-D08 | No documentation of the actual publish source/settings beyond prose; no mention of `orthoconnect.lk` | README | Maintainer |
| G-D09 | `docs/article-migration-review.md` is **generated** by the importer — manual edits would be lost on `--replace` | `import_articles.py:248-281` | Maintainer |

## 6. Requirements/document gaps (G-R)

| ID | Gap | Note |
|---|---|---|
| **G-R01** | Four reference documents missing (reverse-engineering spec, refined SRS v2, architecture spec v2, profile `.docx`) | Blocks SRS compliance and traceability |
| G-R02 | Prototype `v4-OrthoConnect-Prototype-v2` missing | R-02 cannot be verified |
| G-R03 | `questionnaire.md` and `website-build-files/*` exist outside the repo but were not read | Pending permission |
| G-R04 | Brief/code mismatch on stack (PHP/MySQL) and domain | X-01, X-03 |
| G-R05 | A "separate WordPress checkout" is referenced but absent | `docs/homepage-review.md` |

## 7. Operational/governance gaps (G-O)

| ID | Gap | Note |
|---|---|---|
| G-O01 | GitHub settings (branch protection, required reviews, Pages source, enforce HTTPS, whether the sample workflow is disabled) cannot be verified from the repo | UNKNOWN |
| G-O02 | Whole repo root is published (S-01); no publish allow-list | decide boundary |
| G-O03 | Sample Jekyll workflow retained | S-05 |
| G-O04 | Stale sibling working copy `orthoconnect-lk-website/` (5 files behind) may be edited by mistake | archive or delete (client/maintainer) |
| G-O05 | No CODEOWNERS, issue/PR templates, CONTRIBUTING, LICENSE, SECURITY policy | maintainer |
| G-O06 | No backup/restore plan beyond git; no incident process for a bad booking link | maintainer |

## 8. Discrepancies between *intended* and *actual* system
| Intended / assumed (brief) | Actual (code) |
|---|---|
| PHP application with MySQL | Static site generated by Python; no DB |
| Possible WordPress target architecture (inferred from "technical architecture spec", "WordPress checkout", legacy site) | No WordPress code exists here |
| `orthoconnect.lk` production domain | Not wired anywhere |
| Admin/CMS | Explicitly excluded |
| SRS-level SEO, contact, map, WhatsApp features | Not implemented / deliberately omitted |
| Approved, reviewed medical content | All drafts |
