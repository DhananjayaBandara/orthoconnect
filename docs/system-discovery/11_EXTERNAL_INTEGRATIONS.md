# 11 — External Integrations

Evidence legend: **CONFIRMED · INFERRED · DOCUMENTED · NOT IMPLEMENTED · UNKNOWN**.

> **Key distinction:** OrthoConnect has **no API integrations at runtime**. Every external relationship is either (a) a plain **hyperlink** the visitor clicks, (b) **development-time tooling**, or (c) **hosting**. Nothing is fetched by the site's own code (no `fetch`/XHR/WebSocket/iframe/embed; `check_clinics_dom.cjs` even replaces `window.fetch` with a function that throws, to prove the directory makes no network requests).

External-host sweep of every shipped HTML/CSS/JS file (CONFIRMED): `www.doc.lk` (30 anchors), `www.echannelling.com` (28), `www.nhs.uk` (11), and the W3C SVG namespace URI (a string, not a request). Nothing else.

## 1. Integration register

| ID | Provider | Purpose | Method | Type | Status |
|---|---|---|---|---|---|
| I-01 | **eChannelling** — `www.echannelling.com` | Doctor-and-hospital session pages where patients book | Deep hyperlinks, same tab, 13 centres | Hyperlink | **Implemented** |
| I-02 | **Doc990** — `www.doc.lk` | Same, second provider | Deep hyperlinks, same tab, 13 centres | Hyperlink | **Implemented** |
| I-03 | **NHS UK** — `www.nhs.uk` | Authoritative further reading on 11 reading pages | Hyperlinks, new tab, `rel="noopener noreferrer"` | Hyperlink | **Implemented** |
| I-04 | **GitHub Pages** | Static hosting of the repo root | Branch publish, `.nojekyll`, HTTPS enforced | Hosting | DOCUMENTED |
| I-05 | **GitHub Actions** | Sample Jekyll-to-Pages workflow | `.github/workflows/jekyll-gh-pages.yml` | CI/CD | File present; README says **disabled**; actual state UNKNOWN |
| I-06 | **Pexels** (`images.pexels.com`) | Five licensed lifestyle photographs | `scripts/download_images.py` (HTTPS GET, dev-time only) | Dev tooling | **Implemented**; downloaded 2026-10-25; not run here |
| I-07 | **AAOS OrthoInfo** | "Broad conceptual references" for 3 original SVG illustrations | URLs recorded in `content/design.json` / `ASSET-SOURCES.md` only — **not rendered on any page** | Provenance note | Documentation only |
| I-08 | **Legacy `orthopaedic.lk`** (WordPress) | Source of the 40 articles and 251 images | Offline scrape in sibling folder → importer; URLs kept as internal provenance | Content origin | Never linked/hot-linked (enforced by `check_site.py`) |
| I-09 | **Link-verifier toolkit** (`Dr_Suneth_De_Silva_Unified_Link_Verifier`) | Captured and verified the 26 booking URLs | Offline; report SHA-256 stored in `site.json` | Dev process (external) | Run once, 2026-10-25 |
| I-10 | W3C namespace `http://www.w3.org/2000/svg` | SVG `xmlns` attribute | Literal string | n/a | Not an integration |

## 2. Booking providers (I-01, I-02) — detail

| Aspect | eChannelling | Doc990 |
|---|---|---|
| Relevant files | `content/site.json` `clinics[].booking_links.echannelling`; `scripts/clinic_directory.py`; `bs:clinic_card()`; `scripts/check_clinics.py` | same, key `doc990` |
| URL contract (enforced at build) | `https://www.echannelling.com/doctor-search/<doctorId>/sessions?doctorId=<same id>&hospitalCode=H<digits>…`; stored fields `hospital_code`, `verification_status ∈ {captured_from_browser_navigation, captured_from_href, manually_verified}` | `https://www.doc.lk/[si/\|tm/]channel/<digits>`; stored `channel_id`, `verification_status ∈ {browser_verified, manually_verified}` |
| Actual data | 13 links, all `captured_from_browser_navigation`, one doctor ID for all (hard-coded in the validator and in `check_clinics.py`) | 13 links, all `browser_verified`: **7 default-language, 4 Tamil (`/tm/`), 2 Sinhala (`/si/`)** |
| Auth | none (public pages) | none |
| Data exchanged | none — a normal browser navigation; visitor leaves the site | none |
| Referrer policy | `rel="external noreferrer"` ⇒ no `Referer` sent | same |
| Failure handling | None at runtime. A broken/changed link shows the provider's own error. No monitoring, no fallback, no "last checked" display. | same |
| Freshness | `last_checked_utc = 2026-10-25T07:21:28+00:00` for **all 26** links — liveness **UNKNOWN today** | same |
| Dependency risk | URL scheme/ID change, provider outage, provider terms about deep-linking (UNKNOWN) | Language-variant paths are preserved verbatim by policy (`content/README.md`: "do not change Doc990 language paths without checking the destination") — the visitor may land on a **Tamil or Sinhala** provider page from an English site (UX consideration) |

Combinations (asserted by `check_clinics.py:74-75`): 8 centres with both providers, 5 eChannelling-only, 5 Doc990-only.

**Branding:** the fourth homepage banner (supplied artwork) embeds eChannelling, Doc990 and "optional WhatsApp" logos/graphics (`ASSET-SOURCES.md`). Permission to display those marks is **UNKNOWN**; no WhatsApp link exists.

## 3. NHS UK reference links (I-03)
4 distinct URLs, 11 placements: `…/having-surgery/` on all 8 patient guides; `…/arthroscopy/`, `…/hip-replacement/`, `…/knee-replacement/` on the matching treatment pages. All open in a new tab with `rel="noopener noreferrer"`; HTTPS enforced by the generator (`build_site.py:318`). Failure mode: link rot at the NHS site; no runtime effect.

## 4. Hosting and CI (I-04, I-05)
See `17_DEPLOYMENT_AND_ENVIRONMENT.md`. Key facts: publish source is **branch `main`, folder `/`**; the built-in "pages build and deployment" job publishes committed files and **does not run the generator or checks** (README); the retained Jekyll workflow would build `./` with Jekyll into `_site` and deploy via `actions/deploy-pages` — a *different* pipeline that README says is disabled to avoid competing deployments.

## 5. Pexels (I-06)
`download_images.py`: HTTPS GET to `https://images.pexels.com/photos/<id>/pexels-photo-<id>.jpeg?auto=compress&cs=tinysrgb&w=<640|1280>` with a custom `User-Agent`; accepts only `image/jpeg`, ≤ 20 MiB, ≥ 320×200; stages in a temp dir and replaces files only after **all** downloads pass; writes `content/stock-assets.lock.json` (source, photographer, licence URL, dimensions, SHA-256) and rebuilds. Licence: Pexels licence (free to use; attribution recorded internally, **not displayed** — captions/credits were removed from pages). No checksum is pinned *before* download (trust-on-first-use).

## 6. Legacy archive and verifier (I-08, I-09)
Neither is called by the site. They are **inputs to maintainer commands** and **evidence for audits** that live in sibling folders:

| Folder | Read by | If absent |
|---|---|---|
| `../Dr_Suneth_De_Silva_Unified_Link_Verifier/VERIFICATION_RESULTS.json` | `check_clinics.py` | Check passes with "exact external-source comparison skipped" |
| `../orthopaedic-lk-content-archive-toolkit/` | `check_article_migration.py`, `import_articles.py` | **Both fail** (`FileNotFoundError`) — a fresh clone cannot complete the documented verification |

## 7. Integrations explicitly searched for and **not found**

| Candidate | Result |
|---|---|
| WhatsApp (`wa.me`, `api.whatsapp.com`) | 0 links. Only the banner *artwork* and its alt text mention optional WhatsApp enquiries (`content/home-carousel.json`) |
| Google Maps / OpenStreetMap / directions | 0 |
| Google Fonts / any CDN | 0 — fonts are local TTFs |
| Google Analytics / Tag Manager / Meta Pixel / Hotjar / Clarity | 0 |
| E-mail/SMS gateways, newsletter, CRM | 0 |
| Social media links/embeds, YouTube | 0 |
| reCAPTCHA / payment gateways | 0 |
| Search-engine verification tags | 0 |

## 8. Dependency-risk summary
| Risk | Level | Note |
|---|---|---|
| Booking-link rot (26 links verified once) | **Medium** | Core user journey ends at these links; add periodic re-verification |
| Provider branding in banner artwork | Low–Medium | Seek permission or replace artwork (client decision) |
| Doc990 language-variant landings | Low | Confirm intent with client |
| GitHub as sole host/CI | Low | Standard; platform limits apply (general knowledge, not from the repo) |
| Sibling-folder coupling of checks | Medium (maintainability) | See AW-04 |
