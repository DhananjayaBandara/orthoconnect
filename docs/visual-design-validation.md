# Shared UI and motion enhancements — 28 October 2026

All 70 static routes now load `styles/effects.css` and `scripts/effects.js`, generated from shared source templates. The website remains buildless at runtime, with local fonts/assets, no framework, animation package, tracking or remote image dependency.

## Implemented design

| Placement | Result |
| --- | --- |
| Homepage hero | Refined cream/teal gradient, preserved portrait/logo, short optional portrait-frame entrance. Name and primary actions remain immediately visible. |
| Seven main inner-page headers and aliases | Section-specific decorative SVG motifs alongside text; mobile headers use a quieter gradient and full-width copy. Privacy, terms and error pages retain focused layouts. |
| Shared cards | Consistent border/shadow feedback on hover and focus. Reading/treatment cards can lift slightly on fine pointers. Clinic booking controls remain stationary. |
| Buttons, links and filters | 180ms state transitions, pressed-button feedback and small directional arrow feedback. Provider buttons retain equal prominence. Filtering/count updates remain immediate. |
| Header and mobile navigation | Stable header height, scrolled-state shadow, active/hover underline feedback; mobile disclosure transitions with inert closed links, Escape focus return and close-on-focus-leave. |
| Homepage/About sections | Optional 340ms one-time entrances with 10px movement and short bounded group delays. Above-the-fold/anchor-restored groups skip entrances. |
| About training timeline | Numbered milestone cards preserving the existing documented qualifications/training and sequence. No dates or credentials were invented. |
| Native topic/FAQ disclosures | Optional 180ms content opening feedback and rotating disclosure icons; native details/summary semantics remain intact. Closing cancels hidden-content animation. |
| All 56 reading pages | Decorative article progress bar and refined current-section highlight. Content stays visible. Progress reacts to scroll, resize, article/image size changes, fonts and restored pages. |
| Homepage consultation callout | Existing licensed walking photograph paired with a solid navy copy panel and high-contrast text. |
| Three featured treatments | Original local SVG topic artwork for hip replacement, knee replacement and arthroscopy on home/listing/related cards and corresponding reading pages. Generic lifestyle-photo mappings and those three lead-photo fields are removed. |

Motion honours `prefers-reduced-motion`, including preference changes during an active animation. CSS motion is disabled and active Web Animations are cancelled; observers stop pending reveals. Missing animation/IntersectionObserver APIs omit optional effects. There is no permanent hidden reveal state: underlying content starts and remains visible. Clinic results, external booking controls and reading paragraphs/figures are outside reveal groups. Direct anchors and keyboard focus take precedence over entrances.

The three new illustrations are simplified topic identifiers, not surgical instructions, incision guidance or implant specifications. No third-party figure was copied or traced. Broad conceptual references are [AAOS hip replacement](https://www.orthoinfo.org/treatment/total-hip-replacement/), [AAOS knee replacement](https://www.orthoinfo.org/treatment/total-knee-replacement/) and [AAOS knee arthroscopy](https://www.orthoinfo.org/treatment/knee-arthroscopy/). Reference/provenance, dimensions, hashes and draft review status are in `content/design.json` and `ASSET-SOURCES.md`. Each SVG was rendered with librsvg and visually inspected at 640 × 400 pixels. That establishes asset inspection, not clinical approval or page rendering quality.

## Executed checks

- Generator and `scripts/check_site.py`: passed across all 70 routes, 56 reading pages and 5,364 local references; nesting, headings, navigation, anchors, labels, ARIA references and local assets validated.
- `scripts/check_clinics.py`: passed; all 18 centres and 26 exact doctor/hospital booking links retain their documented platform mapping on the directory, alias, homepage and Contact page.
- `scripts/check_article_migration.py`: passed; all 40 supplied articles retain substantive Unicode text, source image order/placements, provenance and accurate draft/noindex status.
- `scripts/check_clinics_dom.cjs`: all 250 assertions passed with the new shared effects script loaded, including navigation on all 70 pages.
- `scripts/check_articles_dom.cjs`: all 42 existing article interaction assertions passed with the effects script loaded.
- `scripts/check_effects_dom.cjs`: all 257 assertions passed for focus/inert navigation state, one-time entrances, reduced-motion changes, missing-API/anchor/no-JavaScript fallback, native-disclosure state, mocked progress geometry and all 70 page integrations.
- All four stylesheets parsed without CSS parser errors. JavaScript syntax checks passed.
- All 269 pre-existing assets remain byte-identical, including the supplied logo/portrait, stock JPEGs and archive figures. Three original SVG files were added.

The DOM checks use mocked observers, animation APIs and geometry. They verify logic/fallback behaviour, not rendering, actual focus traversal, native keyboard/touch input, Sinhala font shaping or real browser scroll restoration.

## Remaining verification boundary

Local socket creation fails with `PermissionError: [Errno 1] Operation not permitted` in this session. No current browser rendering pass or new page screenshots were produced. Earlier screenshots in `docs/previews/` predate this change. Responsive rules and animation timing are implemented, but their visual quality, clipping and motion feel still require a real desktop/mobile browser pass.

The pre-edit source/page archive is recorded in `/tmp/orthoconnect-visual-backup-path.txt`. It is a temporary rollback artifact, not a production backup. This checkout has no usable Git metadata, so changes remain local without a commit, push or PR. No hosting, publication state or clinical approval was changed.

## Repeat checks

```sh
python3 -B scripts/build_site.py
python3 -B scripts/check_site.py
python3 -B scripts/check_clinics.py
python3 -B scripts/check_article_migration.py
python3 -B scripts/download_images.py --check
ORTHOCONNECT_JSDOM_MODULE=/absolute/path/to/node_modules/jsdom node scripts/check_effects_dom.cjs
ORTHOCONNECT_JSDOM_MODULE=/absolute/path/to/node_modules/jsdom node scripts/check_clinics_dom.cjs
ARTICLE_JSDOM_MODULE=/absolute/path/to/node_modules/jsdom node scripts/check_articles_dom.cjs
```

Where local sockets/browser access are available, run the existing `scripts/check_homepage.browser.cjs` against a locally served site, followed by visual checks of the seven header motifs, treatment artwork, About timeline, native FAQ interaction, all three reading-page types, motion preferences and widths down to 320px. Verify that fixed controls do not obscure content and booking buttons remain immediately usable. The current source-level evidence does not replace that browser pass.

Motion follows the approach described in [W3C guidance on animation from interactions](https://www.w3.org/WAI/WCAG22/Understanding/animation-from-interactions.html); this is not a claim of a complete accessibility audit.
