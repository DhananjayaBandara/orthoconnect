# 08 — Backend Architecture (the Python build-time "backend")

Evidence legend: **CONFIRMED · INFERRED · DOCUMENTED · NOT IMPLEMENTED · UNKNOWN**.

> **There is no runtime backend.** The brief expects PHP request handling, sessions, authentication, a database and e-mail. None exists (0 `.php` files; no server process of any kind). The only "backend" is a **build-time Python program** that renders static HTML. Everything below describes that program. PHP-specific topics are answered explicitly in §9.

## 1. Execution model

```
python3 -B scripts/build_site.py          (≥ Python 3.12; stdlib only)
 └─ import-time:   load content/site.json → load_reading_catalog() → validate_articles() → validate_clinics()
 └─ main():        render 11 pages  +  56 reading pages  →  write_page() each  →  copy 3 aliases  →  delete retired article pages
 └─ output:        "Generated 11 public pages, 56 reading pages and 3 compatibility routes."
```

* **Idempotent and deterministic** — a fresh run is byte-identical to the committed files (CONFIRMED by executing in a scratch copy).
* **Fail-fast before writing:** validation happens at import (`build_site.py` L19-23) so a bad catalog aborts before the first `write_text`. (Alias copying and stale-page deletion occur after the page writes, but only read generated files.)
* **No network, no subprocess** (except `download_images.py`, which runs the build after a network step).
* **Paradigm:** procedural/functional modules; module-level constants loaded at import (`DATA`, `TAXONOMY`, `MANIFEST`, `DESIGN`); no classes in the generator (only `HTMLParser` subclasses in checkers); no type hints.

## 2. Module responsibilities and public functions

### `scripts/build_site.py` (407 lines) — orchestrator and page templates
| Function (line) | Purpose |
|---|---|
| `e()` (26) | `html.escape(str(v), quote=True)` — used for all dynamic text |
| `icon()`, `button()`, `brand()` (30-49) | Atomic markup helpers (`<svg><use>`, anchors, logo) |
| `stock_photo()` (34) | Builds `<img srcset>` from available 640/1280 variants; returns `''` if files are missing (graceful fallback) |
| `nav_links()`, `header()`, `footer()` (52-71) | Chrome. `nav_links` marks `aria-current="page"`; its `footer` parameter is unused |
| `section_head()`, `cta()`, `page_title()`, `booking_note()` (77-97) | Section scaffolding |
| `featured_clinics()`, `clinic_card()` (100-117) | Clinic cards with provider buttons, search blob, descriptive `aria-label` |
| `article_preview()`, `treatment_preview()` (120-135) | Homepage preview cards |
| `home()` (138-158) | Composes the entire homepage; **hard-codes** hero text, qualification pills, expertise cards, featured article/guide IDs |
| `qualifications()`, `about()` (161-168) | About page; **hard-codes** five prose paragraphs |
| `library_filters()`, `reading_card()`, `topic_card()`, `library_page()` (171-229) | Listing pages for conditions/treatments/guides |
| `booking_steps()`, `clinics()` (232-243) | Clinics page and filter form |
| `contact()`, `policy()`, `not_found()` (249-280) | Contact, Privacy, Terms (copy hard-coded), 404 |
| `reading_page()` (283-343) | Treatment / guide reading pages (articles delegate to `article_library`) |
| `write_page()` (346-371) | Document skeleton, per-page asset selection, URL rewriting, file write |
| `main()` (374-403) | Page list, alias map `{services→treatments, medical-information→patient-information, hospitals→clinics}`, retired-article cleanup |

### `scripts/reading_content.py` (183 lines)
| Function | Purpose / rules |
|---|---|
| `READING` (14-18) | Maps content kind → folder/label/listing/nav-id: `articles→articles`, `treatments→treatments`, **`guides→patient-information`** |
| `safe_language()` (23) | Regex-validates language tags (`[a-zA-Z]{2,8}(-…)*`) |
| `load_reading_catalog()` (29-78) | For each reference: ID must be a lowercase-hyphen slug, `content` path must equal `content/<folder>/<id>.json`, no duplicates; JSON must have `title/summary/category/icon/sections`; `status ∈ {draft, reviewed}`; `reviewed` ⇒ `reviewed_by`+`reviewed_on` (not future); section IDs valid/unique and not `title`/`further-reading`; sub-heading IDs unique; every `related_items` target must exist |
| `reading_url()` / `resolve_content_url()` (81-96) | `kind/id.html`; upgrades `listing.html#id` fragments to the dedicated page |
| `rewrite_page_urls()` (99-126) | Regex rewrite of `href`/`src`/`srcset`/`data-reading-url` into **paths relative to the page directory** (no `<base>` tag) |
| `image_dimensions()` (129-142) | Image must be local, under `assets/images/`, an existing file; JPEG via stdlib SOF parser, PNG via IHDR |
| `render_blocks()` (145-183) | Renders `paragraph|heading|list|image|table|callout`; **escapes all text**; requires alt text, matching table columns, positive list `start`; unknown type → `ValueError` |

### `scripts/article_library.py` (174 lines)
`TEXT` (13-40) EN/SI UI strings · `validate_articles()` (51-63): unique IDs, language ∈ {en, si}, non-empty unique taxonomy keys that exist, valid guide targets · `article_filters()`, `article_card()`, `article_listing()` (66-112) · `article_reading_page()` (115-174): localised labels, status chips, optional guide navigation (`guide_items`), TOC, HTTPS-only references, return links (`data-article-return`), related cards (same-language first), CTA.

### `scripts/homepage.py` (75) · `clinic_directory.py` (53) · `stock_assets.py` (62) · `visual_design.py` (32)
See `05_FILE_STRUCTURE.md` §3.1 and `03_FUNCTIONALITY_CATALOGUE.md`. `validate_clinics()` is the strictest rule set in the codebase (BR-03/04/05 in `02_BUSINESS_CONTEXT.md`) and also rejects URLs with userinfo, ports or fragments, and requires a timezone-aware `last_checked_utc` that is not in the future.

### Maintenance commands
| Script | Behaviour |
|---|---|
| `import_articles.py` | Reads a sibling Markdown archive (`manifest.json`, `ALL-ARTICLES.md`, `english/`, `sinhala/`, `images/`, `metadata/`), cross-checks inventories, parses Markdown with regexes (headings→sections, lists, images→local figures, drops logged placeholders/enquiry prompts), copies images by SHA-256 name, generates related-article links by shared region/topic (not translation pairs), **writes** `content/articles/*.json`, `content/site.json`, `content/article-assets.json`, `content/article-migration.json` and **`docs/article-migration-review.md`**. Refuses to run if drafts exist unless `--replace`. |
| `download_images.py` | `--check` = offline presence/size check. Otherwise stages all missing Pexels downloads (type = JPEG, ≤20 MB, ≥320×200), only then replaces files, writes `content/stock-assets.lock.json`, and runs `build_site.py` via `subprocess` |

## 3. Request processing, sessions, auth — **not applicable**
| Topic | Finding |
|---|---|
| GET/POST handling | No server. The browser issues GETs for static files; GitHub Pages answers. |
| Sessions / cookies | None set or read (CONFIRMED: no `document.cookie`, no `Set-Cookie` source) |
| Authentication / authorization | None. No users, roles, passwords or tokens exist. |
| Input validation | Only **build-time** validation of maintainer-authored files (see §2) and **client-side** whitelisting of URL parameters (`articles.js`, `clinics.js`) |
| Output escaping | All dynamic strings pass through `e()` / `escape()`; block text never interpreted as HTML (CONFIRMED) |
| Error handling | Python: `ValueError`/`AssertionError` with specific messages, process exits non-zero; checkers print `FAIL:`. JS: `try/catch` only around `history.replaceState` (restricted on `file://`) |
| Logging | `print()` summaries only |
| E-mail / SMS | None |
| File handling | Read JSON/images; write HTML; path-traversal guards via `Path.resolve().is_relative_to(...)` (`reading_content.py:134`, `visual_design.py:24`); SHA-256 verification of illustrations and stock files |
| External integrations | None at runtime. Build-time: Pexels HTTPS download only |

## 4. Data validation matrix (build time)
| Subject | Rule | Location |
|---|---|---|
| Reading IDs / section IDs / sub-heading IDs | `[a-z0-9]+(-[a-z0-9]+)*`, unique | `reading_content.py` |
| Source path | exactly `content/<folder>/<id>.json` | L38-40 |
| Language tag | ASCII BCP-47-like pattern | L19-26 |
| Review metadata | reviewer + valid past/today date when `reviewed` | L49-55 |
| Article taxonomy | audiences/body_regions/topics non-empty, unique, known | `article_library.py:58-61` |
| Guide links | targets exist, not self | L62-63 |
| Outbound references | `https` scheme only | `build_site.py:318`, `article_library.py:151` |
| Inline images | local, under `assets/images/`, JPEG/PNG, alt required | `reading_content.py:129-170` |
| Tables | caption + equal column counts | L172-174 |
| Clinics | see BR-03…05 | `clinic_directory.py` |
| Illustrations | SHA-256 equals `design.json` | `visual_design.py:26` |
| Retired articles | valid slugs and absent from catalog | `build_site.py:375-377` |

## 5. Error-handling and robustness observations
* Validation errors are explicit and early; messages name the offending ID/path.
* `stock_photo()` and `treatment_illustration()` degrade (return `''`) if files are missing, **except** an illustration whose hash differs (raises).
* `rewrite_page_urls()` is regex-based on generated markup — correct for current output, but any future inline attribute containing the text `href=`/`src=` in escaped body copy could in principle be rewritten; text is escaped (`&quot;` …), so quotes cannot form attributes (INFERRED safe).
* `date.today()` is used for validation (reviewed-date-in-future check) — the only time-dependent input; it does not affect output.
* Windows path semantics, locales and Python < 3.12 are unsupported (syntax).

## 6. Outputs written (for reference when reasoning about diffs)
`index.html` … `404.html` (11), `articles/*.html` (40), `treatments/*.html` (8), `patient-information/*.html` (8), aliases (3); **deletes** `articles/<retired-id>.html` for the 5 retired IDs. Nothing else is written by `build_site.py`.

## 7. Backend-style risks and technical debt
| ID | Observation | Severity |
|---|---|---|
| B-01 | Giant f-strings (>1,000 chars) make diffs and reviews hard; no template engine | Medium (maintainability) |
| B-02 | Copy/facts hard-coded in code (duplicated qualifications, descriptions, featured IDs) | Medium |
| B-03 | `topic_card()` retains dead branches; `library_page` config has an unreachable `articles` entry; unused `footer` parameter | Low |
| B-04 | Module-level I/O at import time hinders reuse in tests | Low |
| B-05 | Regex-based Markdown parsing in the importer is archive-specific | Low (one-off) |
| B-06 | `import_articles.py --replace` silently overwrites editorial changes and a docs file | Medium (operational hazard) |
| B-07 | Python ≥ 3.12 only; no version guard or friendly error | Low |

## 8. Dead-end search results (evidence of absence)
A word-boundary, case-insensitive `grep` across `scripts/*.{py,js,cjs}` (executed in this investigation) found **no application use** of: `cookie`, `login`, `jwt`, `token`, `api_key`, `mysql`, `sqlite`, `psycopg`, `flask`, `django`, `smtp`, `sendmail`, `os.system`, `exec`. The remaining hits are benign and fully accounted for:

| Term | Hits | Meaning |
|---|---|---|
| `password` | 1 | `url.password` in `clinic_directory.py:26` — *rejects* booking URLs that embed credentials |
| `session` | 1 | the English word "sessions" in the booking-steps copy ("…to view Dr. De Silva's sessions at that hospital", `build_site.py:233`), not an auth session |
| `requests` | 1 | an error message in `check_clinics_dom.cjs:22` ("…must not make network requests") |
| `subprocess` | 2 | `download_images.py` import + the call that runs `build_site.py` |
| `eval` | 9 | `dom.window.eval(...)` in the four jsdom **test** scripts, used to run the project's own `main.js`/`effects.js`/etc. inside jsdom — never in shipped code |

## 9. PHP-oriented checklist from the brief
| Item | Answer |
|---|---|
| PHP version requirement | **Not applicable** — no PHP. Python ≥ 3.12 is the only language requirement. |
| Procedural vs OO PHP | n/a |
| `include`/`require` graph | n/a (Python `import` graph in `06_SYSTEM_ARCHITECTURE.md` §4) |
| Database access / queries | n/a |
| GET/POST, sessions | n/a |
| SQL injection, CSRF, session fixation, auth bypass, unsafe uploads | **Not applicable** (no such surfaces) — see `12_SECURITY_ASSESSMENT.md` §4 |
