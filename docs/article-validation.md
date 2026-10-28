# Bilingual article preview validation

## Result

The local preview contains **70 HTML pages**, including **56 reading pages**. The Articles library contains **exactly the 40 supplied archive entries: 19 English and 21 Sinhala**. The five dummy article sources, pages and links are removed. The Sinhala child overview is counted once, as a guide with its complete source text retained.

All imported articles remain drafts. All generated pages retain `noindex,nofollow`. No publication or deployment was performed.

## Checks completed

| Check | Result |
| --- | --- |
| Existing baseline before changes | Passed: 35 HTML pages, 21 reading pages and 2,604 local references. |
| Current site audit | Passed: 70 HTML pages, 56 reading pages, 5,541 local references and 31 stock-photo placements. |
| Structural coverage | One H1 per page, heading order, nesting, unique IDs, eight main-navigation destinations, active parent sections, relative links, contents anchors, ARIA references, form labels, image dimensions and local image references pass. |
| Source conservation | All 40 archived articles retain their substantive Unicode text, source headings, list contents, and image order and positions. The checker independently compares the complete sequence from the archive to the saved JSON and to the actual generated HTML reading pages. |
| Article destinations | No public page links or redirects to the external archive website. “Original article” links are removed. All 40 imported articles and all 390 image placements are available locally; source URLs remain only in internal provenance records. |
| Recorded omissions | Three placeholder paragraphs and 26 standalone legacy enquiry-prompt blocks are omitted. One separator and one image-gallery block receive documented formatting changes. Exact omissions are recorded in `content/article-migration.json` and the review report. |
| List semantics | Consecutive numbered items form real lists. A source paragraph interrupts the treatment-options list in the English child upper-arm article; its continuation correctly starts at 3. Repeated complication lists remain separate for editorial review. |
| Images | All 390 source placements resolve to 251 byte-identical local JPEG/PNG files. All copied files fully decode. Source paths, original image URLs and SHA-256 checksums are recorded. |
| Archive integrity | All 458 archive files match their pre-edit content hashes. The archive was not modified. |
| Preserved content | All 40 supplied article bodies and metadata are unchanged apart from related links. All 261 local image files, including supplied branding and archive illustrations, are byte-identical. Treatment and patient-guide clinical copy is unchanged; related links are updated. |
| Dummy removal | All five dummy JSON sources and generated pages are deleted. No generated HTML page contains their IDs or links. Home previews point to supplied articles; related links reference supplied articles where the subject matches. |
| Sinhala structure | All 21 Sinhala documents have the correct document language, local Sinhala font preload, native reading controls, native summaries and titles, and explicitly tagged English image alternative text. |
| Child guide | Eleven links lead to the individual Sinhala child topics, followed by the retained overview body. |
| DOM interactions | Passed: 42 assertions covering collection counts, combined filters, Sinhala search, canonical Unicode equivalents, English discovery keywords, empty/reset states, URL sharing, header/footer/breadcrumb/return links, related-link context, guide links, direct-file paths and invalid filter values. |
| Navigation state | DOM checks cover a fresh shared URL, a return URL, simulated `popstate` and `pageshow` events, and a restricted History API fallback. No cookies, local storage or session storage are used. |
| Syntax and styles | JavaScript syntax and Python AST checks pass. Both CSS files parse; all 116 referenced design tokens resolve. |
| Rebuild | A repeated build leaves all 70 HTML files byte-identical. An isolated re-import retains exactly the supplied 40 articles, and rebuilding removes five deliberately seeded stale dummy pages. |
| Import protection | The migration command refuses to overwrite existing imported drafts unless `--replace` is explicitly supplied. |

Audience filters intentionally overlap for one article: the Sinhala complex-fracture source explicitly discusses both adults and children. Thus All audiences shows 40 entries, Adults shows 21, and Children shows 20. Sinhala Children includes the 11 individual child articles, the guide and that shared-audience article (13 entries).

Changes outside Articles consist of the shared styles, the existing fragment-link helper, the home-page article previews, and updated article cards in related-reading sections. The non-article clinical source copy is unchanged.

## Reproduce the checks

From the website directory:

```sh
python3 -B scripts/build_site.py
python3 -B scripts/check_site.py
python3 -B scripts/check_article_migration.py
node --check scripts/main.js
node --check scripts/articles.js
```

The migration audit expects the read-only archive in the sibling `orthopaedic-lk-content-archive-toolkit` directory. It also accepts an archive path as its argument.

The interaction checks use `jsdom` as an optional verification dependency. They were run using an already installed module, selected through `ARTICLE_JSDOM_MODULE`; no runtime package dependency was added to the website. If jsdom is resolvable locally:

```sh
node scripts/check_articles_dom.cjs
```

Otherwise set `ARTICLE_JSDOM_MODULE` to the absolute path of an installed jsdom module before running that command. These are DOM checks, not browser-rendering tests.

## Browser and local-server limits

Google Chrome was found, but Playwright could not launch it: Crashpad reports `setsockopt: Operation not permitted`, followed by `SIGTRAP`. A local HTTP preview could not be started in this execution environment because socket creation raises `PermissionError: [Errno 1] Operation not permitted`.

Consequently, **no browser screenshots or visual/browser-interaction pass are claimed**. The CSS contains responsive layouts and Sinhala typography rules, and those files and language/font references were checked structurally. Actual font shaping, clipping, native keyboard behaviour, responsive geometry, browser Back/Forward behaviour and image presentation require a browser check outside this restricted environment.

## Open the preview

Open `articles.html` directly in your browser. All content, scripts, fonts and images are local.

For an HTTP preview, run this in an unrestricted terminal:

```sh
cd /home/dhananjaya/Documents/projects/orthopaedic-medical/orthoconnect/orthoconnect-lk-website
python3 -m http.server 8080 --bind 127.0.0.1
```

Then open `http://127.0.0.1:8080/articles.html`.

Examples to check:

- `articles.html?lang=si&audience=adult&region=hip&topic=joint-replacement` should show only the Sinhala hip-replacement article.
- `articles.html?lang=en&audience=children` should show seven English child articles.
- `articles.html?lang=si&topic=bone-health` should show the Sinhala osteoporosis article.
- `articles.html?lang=si&audience=children&topic=joint-replacement` should show the empty state; resetting should restore all 40 entries.
- Open a filtered result, follow related reading, then use the breadcrumb or return link: the original selection should be restored.

## Remaining visual and editorial review

- Check desktop, tablet and narrow mobile widths for card wrapping, filter widths, horizontal overflow and full-aspect-ratio images.
- Check Sinhala heading and paragraph shaping, line spacing and wrapping using the supplied local font.
- Check native keyboard navigation through the radio controls, filters and contents links, and listen to the changing result count if using a screen reader.
- Exercise real browser Back/Forward and direct-file navigation, including opening articles in new tabs.
- Review the Sinhala summaries and interface wording, the overlapping English child articles, the retained child-overview variants, legacy attribution/image reuse and clinical copy. Specific decisions and the complete source inventory are in `docs/article-migration-review.md`.
