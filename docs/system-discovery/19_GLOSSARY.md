# 19 — Glossary

Terms are defined **as used in this project**. Source of each definition is the code or documentation of the repository unless marked *(general)*.

## A. Business and domain terms

| Term | Meaning |
|---|---|
| **OrthoConnect** | The brand and website for Dr. Suneth De Silva's practice presence; header/footer/title suffix. |
| **Dr. Suneth De Silva** | Consultant Orthopaedic Surgeon, the subject/client of the site and the named clinical reviewer of drafts. |
| **Consultant Orthopaedic Surgeon** | Senior specialist surgeon treating bone, joint and soft-tissue conditions *(general)*. |
| **MBBS / MD (Orthopaedic Surgery) / MRCSEd** | Qualifications as shown on the About page: medical degree (University of Colombo); postgraduate specialist qualification (Postgraduate Institute of Medicine, University of Colombo); membership of the Royal College of Surgeons of Edinburgh. The site's claims; not independently verified here. |
| **MRC Oxford diploma courses (Hip Surgery; Foot & Ankle Surgery)** | Two courses shown as "Distinction in final assessment". Wording shortened from "JBJS MRC Oxford" in commit `a45dd5e`. |
| **International Surgical Training Programme (ISTP)** | The Royal College of Surgeons of England programme through which the site says 24 months of UK training were completed (King's Mill Hospital, Sherwood Forest Hospitals NHS Foundation Trust). |
| **Channelling / channelling centre** | Sri Lankan usage: booking a consultation with a specific doctor at a specific hospital or centre. |
| **eChannelling** | External booking provider, `www.echannelling.com`. Doctor-and-hospital "sessions" pages are deep-linked. |
| **Doc990** | External booking provider at `www.doc.lk` (page paths `/channel/<id>`, `/si/channel/<id>` Sinhala, `/tm/channel/<id>` Tamil). |
| **Provider** | Either of the two booking platforms (`PROVIDERS` in `clinic_directory.py`). |
| **Session (booking)** | A scheduled consultation slot listed on a provider's page for the doctor at a hospital. Not the same as a web session (there are none). |
| **Hospital code** | eChannelling hospital identifier `H<digits>` in the URL query (`hospitalCode`). |
| **Channel ID** | Doc990 numeric identifier in the URL path. |
| **Clinic / centre** | One of the 18 consultation venues in `site.json` `clinics` (the code says "clinic"; legacy route says "hospitals"). |
| **Featured clinics** | The two cards shown on Home and Contact: Asia Hospital (Maharagama) and Hemas Hospital (Thalawathugoda) — `clinic_directory.featured_ids`. |
| **Deep link** | A URL that opens the provider's page for this doctor at this hospital rather than a generic search. |
| **Verification status / `last_checked_utc`** | How and when a booking URL was confirmed by the external verifier toolkit (`2026-10-25T07:21:28+00:00`). |
| **Verifier / Unified Link Verifier** | External toolkit (sibling folder) that captured and verified the 26 URLs; output `VERIFICATION_RESULTS.json`, whose SHA-256 is recorded in `site.json`. |
| **Service scope (`pending`)** | Whether the doctor has confirmed he offers a service. Shown as "SERVICE SCOPE TO CONFIRM". Independent of clinical review of the text. |
| **Clinical review** | Sign-off of educational text by a clinician; recorded as `status: "reviewed"`, `reviewed_by`, `reviewed_on`. Currently zero pages. |
| **Educational draft** | The label for any page with `status: "draft"`. |
| **Limb reconstruction / difficult fracture healing** | Assessment of fractures that fail to unite or heal abnormally and selected deformity problems (site copy). |
| **Legacy archive / `orthopaedic.lk`** | WordPress-based former website whose 40 articles and 251 images were scraped into a sibling archive and imported. The repo docs call it "a different legacy practice"; the brief calls the name historical terminology for this project — **unresolved** (`14_SRS_ANALYSIS.md` X-02). |
| **`orthoconnect.lk`** | The production domain named in the brief; referenced nowhere in the repository. |
| **Prototype (`v4-OrthoConnect-Prototype-v2`)** | Earlier design/structure reference (not in the repo) from which the 8-item navigation derives; included staff CMS pages that were excluded. |
| **Questionnaire** | `../questionnaire.md`, stated source of "business facts and services" (not read). |
| **SRS** | Software Requirements Specification — expected as `orthopaedic-lk-refined-srs-v2.md`; **not supplied**. |

## B. Content-model terms

| Term | Meaning |
|---|---|
| **Reading page** | A dedicated long-form page generated from one JSON draft: article, treatment, or patient guide (56 total). |
| **Kind** | `articles`, `treatments`, or `guides` — keys of `READING`. *Guides* map to the `patient-information/` folder and the "Patient Information" nav item. |
| **Draft file** | `content/<folder>/<id>.json`, one per reading page. |
| **Catalog / hub** | `content/site.json` — lists IDs and file references plus site-wide data. |
| **Section / block** | A reading page has sections (`id`, `heading`, `blocks`); blocks are typed: `paragraph`, `heading`, `list`, `image`, `table`, `callout`. |
| **Lead image** | Optional key (`park-movement`, `everyday-movement`, `consultation-notes`, `outdoor-walking`) selecting a stock photo for the page header. |
| **Taxonomy** | `article-taxonomy.json`: **audiences** (adult, children), **body regions** (14), **topics** (13), each with English and Sinhala labels. |
| **Topic guide (`format: "guide"`)** | The Sinhala children's overview article that links to 11 child articles and retains its full original text. Not to be confused with a *patient guide*. |
| **Interleaved listing** | Unfiltered article view alternates English and Sinhala cards; implies no translation relationship. |
| **Archive block / provenance** | `archive` object on imported articles (source ID, legacy URL, file, SHA-256, original title, extraction time). Internal only. |
| **Retired articles** | Five dummy prototype articles whose IDs are kept in `retired_articles` so stale pages are deleted. |
| **Conservation audit** | `check_article_migration.py`: proves imported text and image order equals the archive except logged omissions. |
| **Omission event** | Logged removal at import: placeholder (3), legacy enquiry prompt (26), gallery formatting (1), separator (1). |
| **Alias route** | `services.html`, `medical-information.html`, `hospitals.html` — byte-identical copies of their targets. |
| **Fragment forwarding** | Turning `listing.html#id` into the dedicated page URL (build-time rewrite + runtime `location.replace`). |
| **Library context (`library` parameter)** | Query-string carrying the article filters from the listing into reading-page links so "return" restores the selection. |

## C. Technical terms

| Term | Meaning |
|---|---|
| **Static site generator (SSG)** | Program that renders pages at build time; here `scripts/build_site.py`. *(general + project)* |
| **Generated HTML** | The 70 committed `.html` files; never hand-edited. |
| **Progressive enhancement** | Pages are complete without JS; JS adds filters, carousels, menus. |
| **`.js-enabled`** | Class added to `<html>` by `main.js`; CSS uses it to show JS-only controls. |
| **`data-*` hook** | Attribute (e.g. `data-article-form`) JS uses to find elements; independent of CSS classes. |
| **`hidden` toggle** | Controls rendered `hidden` and unhidden by JS so no-JS users never see inert UI. |
| **`inert`** | HTML attribute that removes subtree from focus/AT; used for inactive banner slides and the closed mobile menu. |
| **Design tokens** | CSS custom properties in `tokens.css` (118) for colour, type, spacing, sizes, motion. |
| **Sprite** | `assets/icons/sprite.svg`, inlined in every page; ids rewritten to `icon-<name>`. |
| **Banner / carousel** | Homepage 4-slide auto-rotating component (`home.js`); distinct from the manual **resource carousel**. |
| **Body-region explorer** | SVG human outline with 7 numbered markers linking to conditions. |
| **Reduced motion** | `prefers-reduced-motion: reduce` user preference honoured in CSS and JS. |
| **jsdom suite / DOM suite** | Node tests that load generated pages in jsdom and evaluate the shipped scripts. |
| **Browser suite** | Playwright+Chrome test (`check_homepage.browser.cjs`). |
| **Sibling folder** | A directory next to the repo that scripts read (verifier, archive). |
| **Publish boundary** | What GitHub Pages serves — currently the entire repo root. |
| **`.nojekyll`** | Marker making Pages serve files as-is. |
| **`noindex,nofollow`** | Robots meta on every page keeping the site out of search results. |
| **Canonical URL** | `<link rel="canonical">` — absent. |
| **CSP** | Content-Security-Policy; none set. |
| **WCAG** | Web Content Accessibility Guidelines; no conformance level is claimed by the project. |
| **SHA-256** | Hash used to pin assets, illustrations, archive sources and the verifier report. |
| **ADR** | Architectural decision record (`20_…`). |
| **PR** | Pull request — the observed merge workflow (#1, #2). |
| **Noto Sans / Noto Sans Sinhala** | Self-hosted fonts (SIL OFL), TTF, Regular + Bold. |
| **Pexels** | Source of five licensed stock photographs (dev-time download). |
| **`si` / `en`** | Language codes used in `lang` attributes, filters and file-name prefixes (`si-…`, `en-…`). |
| **Evidence labels** | CONFIRMED, INFERRED, DOCUMENTED, NOT IMPLEMENTED, UNKNOWN (defined in `00_…`). |
