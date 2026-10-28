# Local assets and stock-photo sources

## Included

- `assets/images/dr-suneth-de-silva.jpeg`: user-supplied professional portrait, copied unchanged from `v2/client details/profile-image.jpeg`.
- `assets/images/orthoconnect-logo.jpeg`: user-supplied logo, copied unchanged from `v2/orthoconnect-logo.jpeg`.
- Noto Sans regular and bold: copied from the installed system font package. The package copyright and license notice is included in `assets/fonts/LICENSE.txt`.
- Icons and joint illustrations: original SVG line work created for this design. Joint drawings are simple visual cues rather than diagnostic or procedural diagrams.

## Supplied homepage banners — 28 October 2026

The four PNGs supplied for the homepage carousel were copied byte for byte from the outer `carossel images/` directory, in the requested order:

| Supplied filename | Local original |
| --- | --- |
| `1 Orthopaedic Surgeon Clinic Banner.png` | `assets/images/home-banners/01-surgeon.png` |
| `2 Expert Orthopaedic Care for Better Mobility.png` | `assets/images/home-banners/02-services.png` |
| `3 Trusted Orthopaedic Information Banner.png` | `assets/images/home-banners/03-information.png` |
| `4 Trusted Healthcare Appointments Banner.png` | `assets/images/home-banners/04-consultation.png` |

All originals are 1672 × 941 pixels. `content/home-carousel.json` records each original SHA-256, source filename, dimensions, alt text and local responsive variants. The `-768.webp` and `-1672.webp` copies were created with Pillow/Lanczos resizing and WebP quality 90; they retain the complete banner composition, including all text and portraits. The four full-size WebP files total 700,452 bytes, compared with 7,404,488 bytes for the original PNGs. The browser selects a local WebP source with a PNG fallback; there are no remote image requests.

The later supplied desktop artwork, `01-carousel-1920x700.webp` through `04-carousel-1920x700.webp`, was copied unchanged from `/home/dhananjaya/Downloads/` into `assets/images/home-banners/`. Each file is 1920 × 700 pixels; the four files total 402,960 bytes. The `desktop` record for each slide in `content/home-carousel.json` retains its source filename, SHA-256 and dimensions. At viewport widths of 761 px and above, the first matching `<picture>` source selects this wide desktop artwork. The frame follows its 1920:700 proportions, and `contain` preserves the complete artwork when screen height is limited. At narrower widths, the earlier images and their responsive variants remain in use.

These are supplied artwork, with no new authorship or licence attributed. The fourth banner's embedded platform logos and optional WhatsApp artwork remain part of the image. Its banner link opens the existing clinic directory; no WhatsApp contact, account, hospital schedule or separate provider action has been inferred from the artwork. The site's original logo and separate approved portrait retain their existing bytes.

## Free-stock selections

All five photographs below have been downloaded and included as local JPEG files at 640 and 1280 pixels wide using `scripts/download_images.py`; the rebuilt pages display these local files. Source credits, dimensions and checksums are recorded in `content/stock-assets.lock.json`.

| Photo | Selected source | Visual intent |
| --- | --- | --- |
| Homepage consultation callout | [Noelle Otto — older couple walking while holding hands, Pexels](https://www.pexels.com/photo/old-couple-walking-while-holding-hands-906111/) | Warm everyday-movement context; explicitly illustrative, with no patient or treatment-result claim. |
| Mobility/preparation illustration | [Enric Cruz López — walking/jogging in a park, Pexels](https://www.pexels.com/photo/unrecognizable-woman-jogging-along-footpath-in-park-6039243/) | Natural daylight, movement, neutral presentation; no implied clinical procedure or patient outcome. |
| Hip and knee article art | [Legs of a person jogging, Pexels](https://www.pexels.com/photo/legs-of-person-jogging-5037293/) | Everyday movement with a restrained crop and no suggested affiliation with the doctor. |
| Consultation-information article art | [Open notebook and pen, Pexels](https://www.pexels.com/photo/opened-notebook-with-white-blank-pages-and-pen-on-table-9429448/) | Preparation and clarity, without introducing clinical claims. |
| Outdoor walking | [Elderly woman walking in a park, Pexels](https://www.pexels.com/photo/elderly-woman-walking-on-a-park-8795584/) | Everyday mobility across age groups; no implied testimonial or treatment result. |

The five downloaded source photographs were visually inspected. They show a couple walking together, outdoor jogging, jogging legs and shoes, an open notebook, and a woman walking with poles. These images provide lifestyle and consultation-preparation context. No stock image represents Dr. De Silva, one of his patients, a consultation location or a facility he uses.

## Download status and placements

Download complete: five photographs in ten local files. All files were decoded, checked against the provenance record, and verified in the generated HTML. There are 19 stock-photo placements across the primary pages, compatibility routes and 13 treatment/patient-guide reading pages; the three featured procedures now use original SVG topic art. The successful download time is recorded in `content/stock-assets.lock.json`.

Source pages were opened and checked: photographers are Noelle Otto (906111), Enric Cruz López (6039243), Ketut Subiyanto (5037293), Monstera Production (9429448), and Anastasia Shuraeva (8795584). Each source page identifies the image as free to use; see the [Pexels licence](https://www.pexels.com/license/) for the applicable terms.

`content/stock-images.json` records those sources, descriptive alt text and placements. `scripts/download_images.py` downloads local 640- and 1280-pixel JPEG variants and rebuilds the pages after validation. It must run from an execution environment with Internet access.

| Placement | Selected photograph |
| --- | --- |
| Home: consultation callout | Walking couple; Noelle Otto / Pexels credit retained in these asset records |
| Home: guide resources | Consultation notebook, walking with poles, and park-path photographs |
| Home: supplied adult hip article preview | Walking outdoors with poles |
| Home: knee article preview | Legs jogging outdoors |
| Thirteen treatment and patient-guide reading pages | One of the four photographs, selected by each draft's `lead_image` field; photographer attribution retained in these asset records |

The seven main inner-page title sections and their compatibility routes use decorative SVG motifs alongside their text; their former stock photographs and captions remain removed. Stock-photo captions and source credits are not displayed beneath website images; their provenance and licence records remain in this document and the content manifests. All listed image placements are present. The site contains no stock-image hotlinks or broken local image references. If a stock file is removed, rebuilding falls back to the illustration layout. The supplied portrait and complete OrthoConnect logo are unchanged. Earlier homepage crops were checked in Chrome; see the historical `docs/homepage-review.md`. That evidence predates the current visual enhancement; current limits are in `docs/visual-design-validation.md`.

## Archived article illustrations

The 40 imported archive entries retain 390 inline image placements. They resolve to 251 distinct JPEG/PNG assets, copied byte for byte into `assets/images/articles/`. Identical files are stored once; the source placement order is preserved. Images load locally and lazily, with intrinsic dimensions and their complete aspect ratios.

`content/article-assets.json` records the local filename, SHA-256, byte count, original archive paths, article IDs and original image URLs for each asset. These are archive provenance records, not an assertion of a new licence. Source markings and watermarks remain unchanged. Confirm reuse, attribution and clinical relevance during editorial review; see `docs/article-migration-review.md`.

Descriptions were checked against contact sheets of all 251 distinct images. Their English alternative text is explicitly tagged `lang="en"`, including inside Sinhala reading pages. The supplied logo and portrait are not used as replacements for archived clinical figures.

## Homepage graphics

The body-region silhouette and its numbered links are original SVG/CSS navigation artwork in `scripts/homepage.py` and `styles/home.css`. They indicate broad navigation regions, without diagnostic labels or procedural detail. The decorative hero knee outline reuses the existing SVG sprite unchanged. The three additional procedure-topic illustrations below are simplified original artwork and retain educational draft status; clinical review has not been recorded for them.

## Original procedure-topic illustrations — 28 October 2026

These three SVG files were created directly for OrthoConnect. No third-party figure was downloaded, copied or traced. Their colours, simplified shapes and framing identify the topic; they do not specify surgical technique, incision placement, implant geometry, a particular product or a treatment outcome. Their review status remains draft.

| File | Broad visual subject | Primary conceptual reference |
| --- | --- | --- |
| `assets/illustrations/hip-replacement.svg` | Socket cup, ball and stem | [AAOS OrthoInfo: Total hip replacement](https://www.orthoinfo.org/treatment/total-hip-replacement/) |
| `assets/illustrations/knee-replacement.svg` | Upper and lower knee implant components and spacer | [AAOS OrthoInfo: Total knee replacement](https://www.orthoinfo.org/treatment/total-knee-replacement/) |
| `assets/illustrations/arthroscopy.svg` | Slender camera instrument, knee joint and display | [AAOS OrthoInfo: Knee arthroscopy](https://www.orthoinfo.org/treatment/knee-arthroscopy/) |

The references establish the broad visual subjects, not approval of these drawings. `content/design.json` records source paths, intrinsic dimensions, English alt text, SHA-256 and provenance. Each image was rendered locally with librsvg and inspected at 640 × 400 pixels; this is asset inspection, not a browser layout pass. They replace the generic treatment-card photos and the corresponding three treatment reading-page lead photos. The existing lifestyle photographs remain intact for their other placements.
