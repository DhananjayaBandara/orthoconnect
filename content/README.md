# Editing articles, treatments and patient guides

Each reading page has one independent JSON source file:

| Section | Source | Generated page |
| --- | --- | --- |
| Articles | `content/articles/<id>.json` | `articles/<id>.html` |
| Treatments | `content/treatments/<id>.json` | `treatments/<id>.html` |
| Patient Information | `content/patient-information/<id>.json` | `patient-information/<id>.html` |

`content/site.json` lists source-file references for these three sections. It continues to own conditions, qualifications, FAQs and the documented clinic directory. A draft's title, summary, category, body, references and related pages live together in its own source file. Generated HTML files should not be edited directly.

## Revise an existing draft

1. Open the relevant JSON file and edit its title, summary, sections and content blocks.
2. Retain the stable `id` and section IDs so existing links continue to work.
3. Keep `status` as `draft` while clinical review is pending. Populate authorship, reviewer and review-date fields only with verified information. Updating metadata is a manual publishing decision; this static build is not a staff authentication or approval system.
4. Run `python3 -B scripts/build_site.py` from the website directory. The generator updates the reading pages, listings, home-page links and compatibility pages.
5. Open the generated reading page and check the full article and its mobile layout.

Existing short draft copy has been moved without inventing lengthy medical content. Add the doctor's longer drafts to the appropriate source files when available.

## Metadata

- `id`: stable lowercase identifier with hyphens; also the page filename.
- `title`, `category`, `summary`, `icon`: the listing card and reading-page introduction. Keep the summary concise.
- `keywords`: optional array of search terms. Listing search uses the title, category, summary and these keywords; it does not embed entire long articles into the listing page.
- `lang`: `en` or `si` for articles. The two collections are independent, with local Sinhala fonts and native Sinhala reading controls. Language selection does not imply translation pairs.
- Article-only required classification: non-empty `audiences`, `body_regions` and `topics` arrays containing keys from `content/article-taxonomy.json`. Audience may contain both `adult` and `children` when the source addresses both groups. Taxonomy labels are bilingual; body-region and subject filters are separate.
- `archive`: imported articles retain the original source ID, source URL, source filename, SHA-256, original title and extraction timestamp as internal provenance. These fields do not generate public source links or redirects. The complete article and images are hosted locally. This metadata does not establish authorship or clinical approval.
- `format: "guide"` and `guide_items`: the Sinhala child overview links to the 11 child articles; all its source sections remain below the navigation.
- `status`: `draft` or `reviewed`. Reviewed content requires a named `reviewed_by` and valid, non-future `reviewed_on` date in `YYYY-MM-DD` format.
- `author`: optional verified author name. No doctor byline is inferred automatically.
- `pending`: retain `true` where the independently offered service scope is unconfirmed. Clinical review of educational text and confirmation of an offered service are separate decisions.
- `lead_image`: one of `park-movement`, `everyday-movement`, `consultation-notes` or `outdoor-walking`; the existing local stock-photo manifest controls the image and its attribution. Omit for a reading page without a lead photograph.
- `references`: HTTPS resources, each with `label` and `url`.
- `related_items`: entries such as `{"kind":"treatments","id":"hip-replacement"}`. Valid kinds are `articles`, `treatments` and `guides`.

## Sections and content blocks

A section consists of a stable `id`, a `heading` and a `blocks` array. Every section heading becomes an H2 and an entry in “On this page”. A `heading` block adds an H3 and a nested contents entry.

Example structure (replace the illustrative text with reviewed copy):

```json
{
  "id": "overview",
  "heading": "Overview",
  "blocks": [
    {"type": "paragraph", "text": "Article paragraph goes here."},
    {"type": "heading", "id": "key-questions", "text": "Key questions"},
    {"type": "list", "items": ["First discussion point", "Second discussion point"]}
  ]
}
```

Supported blocks:

| Type | Fields | Result |
| --- | --- | --- |
| `paragraph` | `text`, optional `question: true` | An escaped text paragraph; a question can receive visual emphasis without rewriting its text. |
| `heading` | `id`, `text` | H3 with a stable link and nested contents entry. |
| `list` | `items`, optional `ordered: true`, optional positive integer `start` | Bulleted or numbered list, preserving original starting numbers. |
| `image` | `src`, `alt`, optional `caption` | Local JPEG or PNG, with intrinsic dimensions. The complete inline image is displayed without cropping. |
| `table` | `caption`, `headers`, `rows` | Accessible table with column headings and horizontal scrolling on small screens. Every row must have the same number of cells as the headers. |
| `callout` | `text`, optional `title` | A restrained highlighted note. |

A block may also include `lang` for a passage in a different language. English image descriptions use `lang: "en"`, including inside Sinhala articles. Text is treated as text, not executable HTML or Markdown. Use a separate block for each paragraph. Images must live under `assets/images/`, and need descriptive alt text and the appropriate reuse rights.

## Add a new reading page

1. Create the source file in the appropriate folder, using an existing draft as a structural example. Replace its ID, metadata, sections and related links with the new draft's details.
2. Add a reference to the appropriate list in `content/site.json`, for example:

```json
{"id": "new-topic", "content": "content/articles/new-topic.json"}
```

3. Rebuild. The new page and listing card are generated automatically.

Do not rename an established ID without updating its source reference and related links. The build fails on missing required metadata, duplicate section IDs, invalid related pages or unsafe resource paths before writing any pages.

## Navigation and old links

The eight main navigation items remain listing/overview pages. Reading pages highlight their parent section, include Home → Section → Topic breadcrumbs, and link back to the section. Related-reading cards and consultation links appear below the article.

Desktop contents navigation stays beside the article. On screens up to 1040px wide it moves above the article and collapses when JavaScript is available. Native section links and the complete article body remain usable without JavaScript.

Existing `articles.html#topic`, `treatments.html#topic` and `patient-information.html#topic` bookmarks continue to identify their listing card. With JavaScript, those old bookmarks open the dedicated reading page. Without JavaScript, the card's normal “Read” link remains available. Newly generated links point directly to the dedicated pages.

Article filter state lives in the shareable query parameters `lang`, `audience`, `region`, `topic` and `q`. Ordinary article links carry that state in a `library` parameter, so breadcrumbs, related articles and return links restore the selection. There are no cookies or browser-storage records. A direct Sinhala reading URL defaults to the Sinhala collection; a link from the unfiltered library returns to All languages.

## Archive migration and checks

The archive import is complete. Edit the individual JSON files for normal maintenance. `scripts/import_articles.py` is a separate migration command and refuses to overwrite existing imports unless `--replace` is explicitly supplied. Re-importing regenerates imported drafts and the migration report; preserve editorial changes before doing so.

`content/article-import-plan.json` records the original classification/summary plan. `content/article-image-descriptions.json` records the descriptions checked against image contact sheets. These are import inputs; changing them alone does not change already imported article JSON.

The Articles collection now contains only the 40 supplied archive entries (19 English and 21 Sinhala). The five dummy article sources and pages have been deleted, and their content snapshots have been removed from the migration evidence. Their IDs remain only as retirement records. `content/site.json` lists them under `retired_articles`, so the generator removes any stale HTML files for those IDs. Re-importing the archive creates only the supplied 40 entries and does not recreate the dummy articles.

`content/article-migration.json` records exact omissions and source checksums. `content/article-assets.json` records each byte-identical image copy and its source URLs. `docs/article-migration-review.md` contains the complete inventory, reconciliation and unresolved editorial decisions.

After a normal rebuild, run:

```sh
python3 -B scripts/check_site.py
python3 -B scripts/check_article_migration.py
```

The second command checks this draft migration against the read-only sibling archive. It compares the full text/image sequence independently of the importer and permits only logged placeholder/enquiry-prompt omissions and documented Markdown formatting changes. If substantive copy is later edited following clinical review, update the migration evidence and the audit expectations deliberately rather than treating an archive mismatch as a reason to undo the review.

Optional interaction checks are in `scripts/check_articles_dom.cjs`; they require `jsdom` as a test dependency, or an installed module selected through `ARTICLE_JSDOM_MODULE`. These checks do not establish browser rendering or mobile/font-shaping quality. See `docs/article-validation.md` for the validation record and remaining browser checks.

## Maintain clinics and booking links

`content/site.json` owns the clinic records and `clinic_directory` provenance. Home, Clinics, Contact and the `hospitals.html` alias all use these records. Each clinic has a stable `id`, a patient-facing `name`, a nullable `location`, optional `branch`, original `source_name`, and `booking_links` keyed by `echannelling` and/or `doc990`.

Each booking link records its exact `url`, `verification_status` and `last_checked_utc`, plus `hospital_code` for eChannelling or `channel_id` for Doc990. Use the real doctor-and-hospital sessions destination captured in the supplied report. Do not shorten the eChannelling query, substitute a generic search page, fabricate a missing provider link or change Doc990 language paths without checking the destination. A provider's presence does not mean sessions are available.

The directory metadata records the source report filename, toolkit, report timestamp and SHA-256; `featured_ids` selects the homepage/Contact cards. The initial import is the 25 October 2026 report with 18 centres and 26 links. Exact destination comparison in `scripts/check_clinics.py` uses the original sibling report when present; it explicitly reports when that comparison is unavailable. If a new verification report changes the inventory, update the maintained records, provenance and expected coverage together.

Leave unknown localities as `null`. Names are retained from the source; do not infer a town, street address, recurring timetable, fee or video offering. Public availability, session dates and final charges are handled on the booking provider's page. Personal contact actions should be added only after public contact details are supplied.

After editing, rebuild and validate:

```sh
python3 -B scripts/build_site.py
python3 -B scripts/check_site.py
python3 -B scripts/check_clinics.py
```

For optional interaction checks, use an existing jsdom installation:

```sh
ORTHOCONNECT_JSDOM_MODULE=/absolute/path/to/node_modules/jsdom node scripts/check_clinics_dom.cjs
```

These DOM checks do not verify rendered layout, native keyboard behaviour or live booking-platform availability.

## Visual design and original artwork

`content/design.json` maps the seven public section headers to existing decorative SVG motifs and the three featured treatment topics to original local illustrations. These are broad visual identifiers, not implant specifications or surgical instructions. Their `status` remains `draft`, independently of layout changes. Each illustration records its original-artwork provenance, reference, dimensions and SHA-256. The original stock-photo and archive provenance records are retained.

Artwork is rendered by `scripts/visual_design.py` in the homepage cards, treatment listing/related cards and corresponding treatment reading pages. The three treatment sources omit their former generic `lead_image`; other reading sources retain their existing photographs. To edit an illustration, change its SVG and update its hash/provenance deliberately. Rebuild and run the site, clinic and article checks. `styles/effects.css` and `scripts/effects.js` own the shared visual effects; generated HTML is not hand-edited.

Run optional enhancement logic checks with an existing jsdom installation:

```sh
ORTHOCONNECT_JSDOM_MODULE=/absolute/path/to/node_modules/jsdom node scripts/check_effects_dom.cjs
```

Geometry, observers and animation APIs are mocked in those checks. They establish logic/fallback behaviour, not actual rendering or clinical approval of artwork.
