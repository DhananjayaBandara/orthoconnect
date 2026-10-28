# OrthoConnect — complete public website

A standalone static HTML, CSS and vanilla JavaScript website. The eight-item navigation and public page structure follow the supplied `v4-OrthoConnect-Prototype-v2`. Business facts and services come from the outer `questionnaire.md`. Educational copy remains labelled for clinical review. The staff CMS demonstration is excluded, as requested.

## Open the website

Open `index.html` directly in a modern browser. All pages, fonts, images and icons are local. No installation, API, build step or Internet connection is needed to view the website. An Internet connection is needed to open external booking providers and further-reading links.

For an HTTP preview, run this command from this directory:

```sh
python3 -m http.server 8080 --bind 127.0.0.1
```

Then open <http://127.0.0.1:8080>.

## GitHub Pages

The hosted website is at <https://dhananjayabandara.github.io/orthoconnect/>.

GitHub Pages publishes the committed static files automatically when changes are pushed to `main`. In [the Pages settings](https://github.com/DhananjayaBandara/orthoconnect/settings/pages), the source is **Deploy from a branch**, branch **main**, folder **/ (root)**, with HTTPS enforced. The root `.nojekyll` marker tells GitHub to serve the existing HTML and assets without Jekyll processing.

For future updates, edit the source JSON or shared templates, run `python3 -B scripts/build_site.py`, run the verification commands below, and commit the generated HTML alongside its sources before pushing. GitHub's built-in **pages build and deployment** job publishes those committed files; it does not run the Python generator or the local checks. The earlier sample Jekyll workflow is retained in the repository and disabled in Actions to avoid competing deployments. To roll back content, revert its commit on `main` and push the rebuilt, checked files.

Relative links and local assets support the `/orthoconnect/` project path. All clinical draft labels and existing `noindex,nofollow` metadata remain in place. Hosting the drafts does not establish clinical review or approval.

## Public pages

| Navigation or route | File | Content and behaviour |
| --- | --- | --- |
| Home | `index.html` | Four supplied banners with automatic transitions, profile hero, original portrait, qualification pills, quick links, three expertise areas, six condition previews, three treatment previews, two real clinic cards with hospital-specific booking links, body-region navigation, consultation journey, six manually browsable article/guide cards, and a photographic consultation callout. |
| About | `about.html` | Professional profile, four qualifications, UK fellowship, training overview and areas of practice. Unverified years, registrations and additional qualifications are omitted. |
| Conditions | `conditions.html` | Nine body-region/type categories, keyword search, category filtering, reset/empty states and expandable topic information. |
| Treatments | `treatments.html` | Searchable cards linking to eight independent treatment reading pages, related conditions and a separate limb-reconstruction callout. |
| Patient Information | `patient-information.html` | Searchable cards linking to eight independent guide pages, plus six short booking/website FAQs. No medication doses or individual recovery instructions. |
| Clinics & Appointments | `clinics.html` | 18 documented centres; hospital/town search, location and platform filters, shareable result URLs, conditional eChannelling/Doc990 links and booking guidance. |
| Articles | `articles.html` | Exactly the 40 supplied articles. Independent Sinhala and English collections, language/audience/body-region/topic filters, Unicode search, shareable filter URLs and separate reading pages. The five earlier dummy articles are removed. |
| Contact | `contact.html` | Working clinic booking links, guidance for appointment changes, consultation preparation and emergency guidance. |
| Privacy | `privacy.html` | Notice describing browsing, URL filter state, local assets and external booking providers. |
| Terms | `terms.html` | Educational-information, external appointment booking and website terms. |
| Recovery | `404.html` | Page-not-found content with working home and consultation routes. |
| Older public routes | `services.html`, `medical-information.html`, `hospitals.html` | Complete aliases for Treatments, Patient Information and Clinics. They work without JavaScript redirects. |

Every top navigation link opens its own HTML page. Active-page states are rendered in the HTML. Home-page treatment and article previews link directly to the new reading pages. Conditions retain their expandable topics. Old reading-topic fragment links remain usable and forward to their dedicated reading page when JavaScript is available. The prototype's `admin.html` and custom CMS-created `page.html` routes are outside the selected public-only scope.

## Dedicated reading pages

The site has 70 generated HTML files: the existing 14 public/compatibility routes plus 56 reading pages.

| Section | Reading pages | Example |
| --- | --- | --- |
| Articles | 40 (19 English, 21 Sinhala) | `articles/en-adult-hip.html`, `articles/si-adult-hip-replacement.html` |
| Treatments | 8 | `treatments/hip-replacement.html` |
| Patient Information | 8 | `patient-information/preparing-for-surgery.html` |

Each reading page has Home → Section → Topic breadcrumbs, a concise introduction, explicit draft/review status, an optional local lead photograph with source attribution, an uninterrupted article column, section anchors, related reading, a return-to-list link and consultation links. Authorship and review dates are displayed only when entered; no doctor byline or review date is inferred.

The “On this page” list stays beside the article on desktop and moves above it as a collapsible contents list on smaller screens. Article bodies support H2/H3 headings, paragraphs, lists, full-aspect-ratio inline JPEG/PNG images with captions, accessible tables and highlighted notes. The existing short FAQs remain accordions.

Each draft has its own source file under `content/articles/`, `content/treatments/` or `content/patient-information/`. Original copy and questions are preserved; archived placeholder paragraphs and old enquiry prompts are omitted with an exact removal log. See `content/README.md` for the editing guide and block format. Sinhala articles use local Noto Sans Sinhala fonts, native reading controls and explicit language metadata. The collections are independent; no translation pairs are inferred.

The Sinhala children’s overview links to 11 individual topics and retains its original text beneath the navigation. Overlapping English children’s Shoulder and Upper Arm articles remain separate drafts pending editorial reconciliation. The complete 40-entry inventory, existing-draft comparison and unresolved decisions are in [docs/article-migration-review.md](docs/article-migration-review.md). The hosted reading pages retain their clinical draft status.

Every imported article is available in full with its locally hosted images. There are no public links or redirects to the archive website and no “Original article” links. Original source URLs are retained only in internal provenance and migration records.

Filter state is carried in the URL, without cookies or browser storage. For example, `articles.html?lang=si&audience=adult&region=hip&topic=joint-replacement` opens the Sinhala adult hip-replacement selection. Reading links carry that selection into breadcrumbs, related articles and the return link. Both collections and the complete reading pages remain available without JavaScript.

## Original branding

The header, footer and favicon use `assets/images/orthoconnect-logo.jpeg`, the unchanged supplied OrthoConnect image. There is no recreated wordmark, appended `.lk`, recolouring or substituted logo. CSS frames only the outer white margin while retaining the complete supplied symbol, wordmark and tagline. Desktop and mobile framing was checked against the coloured artwork bounds.

The approved portrait is also copied unchanged. The website retains the navy, teal, coral, local Noto Sans, restrained cards and line illustrations from the initial visual direction.

## Files and editing

- `styles/tokens.css`: all palette, font, spacing, sizing, radius, shadow and motion tokens.
- `styles/main.css`: shared page layout, responsive components, focus states, reduced-motion and print styles.
- `scripts/main.js`: navigation, filters, deep links, native dialogs and transient enquiry interaction.
- `scripts/homepage.py`, `styles/home.css`, `scripts/home.js`: homepage-only banner slideshow, visual components, body-region cues and manual resource carousel. The generator includes these assets only on the homepage.
- `content/home-carousel.json`: ordered banner images, links, alt text, source checksums and the autoplay interval in milliseconds; currently `2000` (two seconds).
- `scripts/check_home_banners_dom.cjs`: deterministic banner timer/interaction and asset checks using an optional existing `jsdom` installation. See `docs/homepage-carousel.md`.
- `scripts/check_homepage.browser.cjs`: optional real-Chrome interaction and responsive checks; see `docs/homepage-review.md`.
- `content/stock-images.json`: five selected Pexels photographs, source/photographer records and page placements.
- `scripts/download_images.py`: downloads two local JPEG sizes per stock photograph, validates them, records provenance and rebuilds every page. No additional Python packages are needed.
- `scripts/stock_assets.py`: dependency-free JPEG metadata and local-asset availability checks. Missing stock photos retain the existing illustration layout.
- `content/site.json`: qualifications, condition copy, FAQs, documented clinic records and booking-link provenance, and references to individual article/treatment/guide source files.
- `content/articles/`, `content/treatments/`, `content/patient-information/`: 56 independent draft files with their metadata, sections, references and related items.
- `content/article-taxonomy.json`: bilingual audience, body-region and topic labels.
- `scripts/article_library.py`, `scripts/articles.js`: article templates, controls and URL-based browsing context.
- `scripts/import_articles.py`: separate, read-only archive import command; never run automatically by a normal build. It protects existing imports unless `--replace` is explicitly supplied.
- `content/article-migration.json`, `content/article-assets.json`: source checksums, exact omissions, retired dummy-article IDs and archived-image provenance.
- `scripts/check_article_migration.py`, `scripts/check_articles_dom.cjs`: content-conservation audit and optional DOM interaction checks.
- `content/README.md`: instructions for editing long drafts, adding content blocks and adding new reading pages.
- `scripts/reading_content.py`: source validation, safe content-block rendering, dedicated reading URLs and nested relative-link handling.
- `content/design.json`, `scripts/visual_design.py`, `assets/illustrations/`: section motifs, original procedure-topic artwork and shared reading-progress markup.
- `styles/effects.css`, `scripts/effects.js`: shared interaction feedback, optional entrances, reading progress and reduced-motion handling.
- `scripts/check_effects_dom.cjs`: optional enhancement/fallback logic tests with mocked browser APIs; not rendering evidence.
- `scripts/clinic_directory.py`, `scripts/clinics.js`: clinic data validation and optional browser-local search/location/platform filtering.
- `scripts/check_clinics.py`, `scripts/check_clinics_dom.cjs`: source-to-page booking-link checks and optional DOM interaction checks.
- `scripts/check_site.py`: dependency-free audit of generated pages, local URLs, navigation, contents anchors, labels, assets and stock-photo checksums.
- `scripts/build_site.py`: optional maintenance generator for all static HTML pages. Run `python3 scripts/build_site.py` after editing shared templates or JSON copy. The generator uses Python 3.12+ standard-library features; the generated website needs only a browser.
- `assets/images`, `assets/fonts`, `assets/icons`: local supplied images, licensed fonts and original interface illustrations. The SVG sprite is embedded in each HTML document to support direct file opening.

## Consultation directory and educational copy

`content/site.json` contains 18 documented consultation centres imported from the supplied `Dr_Suneth_De_Silva_Unified_Link_Verifier/VERIFICATION_RESULTS.json` report, dated 25 October 2026. There are 26 recorded hospital-specific links: eight centres have both providers, five have an eChannelling link only and five have a Doc990 link only. Missing links are omitted, not presented as unavailable platforms. Buttons navigate in the same tab to the recorded doctor-and-hospital sessions page. Links do not guarantee a bookable session.

The Clinics page and `hospitals.html` compatibility route show the complete alphabetical directory. Search matches word prefixes (so Ragama does not match Maharagama); search, location and platform filters intersect. The `q`, `location` and `platform` URL parameters restore the result selection after reload or returning from a provider. All cards and links remain usable without JavaScript; optional filters stay hidden in that case. The homepage and Contact page reuse selected entries from the same dataset.

There are no sample clinics, fabricated schedules, mock booking dialogs or enquiry forms. Personal telephone, WhatsApp and email actions are omitted because public contacts were not supplied. Contact now provides booking links and guidance for managing existing appointments. Unknown clinic localities are left unset; no addresses, fees, dates, video consultations or availability claims are inferred from the existence of a booking page.

The questionnaire remains the source for the doctor's documented services and qualifications. Educational content retains its actual review/service-scope labels. No testimonials, patient counts, operation counts, unverified credential dates or treatment guarantees are invented. Clinical draft/noindex states remain unchanged; replacing booking links does not establish clinical approval or deployment.

See [the clinic validation record](docs/clinic-validation.md) for current evidence and [content/README.md](content/README.md) for maintaining the dataset.

## Verification and limits

The site audit covers all 70 HTML routes, including 56 reading pages: explicit nesting, one H1 per page, heading order, eight main navigation destinations, parent-section states, nested relative links, contents anchors, local image/srcset paths, ARIA references, labels and image attributes. The original logo and portrait remain unchanged. Current checks and limits are recorded in [docs/article-validation.md](docs/article-validation.md); this is not a complete accessibility audit.

The archive audit independently compares the source text/image stream with the imported JSON and generated reading pages. All 40 articles retain their substantive Unicode text, headings, list contents and original image positions, allowing only recorded omissions. The five dummy article source files and pages are deleted, and no generated page links to them. All 390 archived image placements resolve to 251 byte-identical local assets with original source records.

After editing or rebuilding, run:

```sh
python3 -B scripts/check_site.py
python3 -B scripts/check_clinics.py
python3 -B scripts/check_article_migration.py
```

DOM interaction checks exercise combined filters, counts, resets, Sinhala search, share/return URLs, guide links, history-event handling and direct-file preview. The optional checker requires an installed `jsdom` test module; the website itself requires no packages. The original article-migration run did not verify browser rendering, native keyboard interaction, Sinhala font shaping or responsive geometry. Earlier homepage enhancements have historical real-Chrome checks and screenshots in `docs/homepage-review.md`. Those screenshots predate the clinic replacement and are not evidence for the current booking UI. Clinic checks are recorded in `docs/clinic-validation.md`; the subsequent visual enhancement checks and browser-verification limit are in `docs/visual-design-validation.md`. See `docs/article-validation.md` for the earlier article checks.

## Stock photography

Five selected Pexels photographs are now downloaded and integrated, each at 640 and 1280 pixels wide. All ten local JPEG files are in `assets/images`; source credits, dimensions and checksums are recorded in `content/stock-assets.lock.json`. The pages have been rebuilt with the photographs.

To restore missing stock files and rebuild the pages, run this command from a terminal with Internet access:

```sh
python3 /home/dhananjaya/Documents/projects/orthopaedic-medical/orthoconnect/orthoconnect-lk-website/scripts/download_images.py
```

It downloads five selected photographs at 640 and 1280 pixels wide, validates JPEG metadata, saves all ten images into `assets/images`, records sources and hashes in `content/stock-assets.lock.json`, and rebuilds all public routes. If a download fails, existing image files and pages are left untouched.

The homepage uses the locally hosted walking-couple photograph by Noelle Otto in a split consultation callout, with copy on a solid navy panel. The seven main inner-page title areas use low-contrast section-specific SVG motifs beside their text. The three main treatment previews, their listing cards and their reading pages use original procedure-specific SVG topic illustrations instead of generic lifestyle photos. Lifestyle photographs remain in mobility/preparation contexts, two English article previews and 13 other treatment/guide reading pages. All 40 supplied articles retain their original inline figures. The supplied portrait and logo remain unchanged. Photographer credits and provenance remain in the internal asset records. Policy and error pages keep focused layouts. Images retain descriptive alt text and intrinsic dimensions; below-the-fold images load lazily.

To check whether all stock files are present without using the network:

```sh
python3 scripts/download_images.py --check
```

All 19 actual stock-photo placements across the public and reading routes are checked for local image/srcset references, alt text and dimensions. Earlier source photographs/homepage crops have historical visual checks. The current original SVG illustrations were rendered and inspected independently; the updated pages have not received a browser rendering pass in this restricted session. The supplied logo and portrait still match their pre-edit bytes.

`questionnaire.md` remains unchanged in the outer directory. The reference prototype has not been modified.

## Homepage design review

The homepage begins with the four supplied banners in order, advancing every two seconds with a smooth one-second crossfade and looping back to the first. Desktop widths of 761 px and above use the supplied `01`–`04-carousel-1920x700.webp` images. The carousel fills the window width, and its desktop frame follows the 1920:700 proportions while preserving the full artwork without cropping. If screen height is unusually limited, the complete desktop image fits within the available frame. Narrower views retain the earlier images and their existing fit. There are no captions, arrow buttons or playback buttons. Slide dots, keyboard navigation and touch swipes support manual browsing. Hover, focus, background tabs and scrolling the carousel out of view pause autoplay; reduced motion disables autoplay. Each banner links to the relevant existing page. All supplied files remain unchanged. See [the carousel maintenance and validation notes](docs/homepage-carousel.md) for current checks and browser-verification limits.

The earlier homepage enhancements are recorded for reference; the saved screenshots predate the clinic-directory update. They include the existing portrait with a soft illustrated backdrop, numbered body-region links, a three-step consultation journey, a six-card resource carousel and a credited lifestyle photograph. The resource carousel is manual, supports touch and keyboard input, respects reduced motion, and becomes a normal grid without JavaScript. See [the review and validation notes](docs/homepage-review.md) and [desktop](docs/previews/homepage-desktop.png) / [mobile](docs/previews/homepage-mobile.png) previews.

## Shared visual enhancements

All 70 generated routes load the shared effects stylesheet/script. Card/button feedback, selected filter transitions, navigation underline feedback and a fixed-height header shadow are consistent across the site. Mobile menu opening/closing transitions keep hidden links inert, retain Escape focus return and close when keyboard focus leaves the header.

Optional scroll entrances run once on selected homepage/About groups. Hero text, clinic controls and reading content stay immediately available. Content is visible before JavaScript; missing IntersectionObserver or animation APIs simply omit the visual effect. Changing the reduced-motion preference cancels active animations and disables pending entrances. Native FAQ/topic disclosures receive optional opening feedback.

All 56 reading pages include a quiet decorative progress bar, hidden without JavaScript. Progress is calculated over the article itself and recalculated on scrolling, resize, image load, font readiness and history restoration. Reading contents continue to track the current section. The About timeline preserves the existing documented milestones and uses numbered cards without invented dates.

See [docs/visual-design-validation.md](docs/visual-design-validation.md) for executed checks, current verification limits and the original artwork references. Earlier screenshots are historical and do not show this update.
