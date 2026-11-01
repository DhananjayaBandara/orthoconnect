# 02 — Business Context

Evidence legend: **CONFIRMED · INFERRED · DOCUMENTED · NOT IMPLEMENTED · UNKNOWN**.
No SRS was supplied (see `14_SRS_ANALYSIS.md`). Everything below is derived from the implementation and the repository's own documentation.

## 1. The problem the system solves

A consultant orthopaedic surgeon in Sri Lanka consults at **many hospitals** (18 documented centres across Colombo, Gampaha and surrounding districts plus Badulla). Patients need to (a) trust who the surgeon is, (b) understand their problem in their own language, and (c) find *which hospital* to attend and *how to book* — without the surgeon's practice having to run its own booking system.

OrthoConnect solves this by being a **credible, calm, information-first front door** that hands the actual booking off to the two channelling platforms the doctor already uses (**eChannelling** and **Doc990 / doc.lk**). INFERRED from page structure; DOCUMENTED in `README.md` §Consultation directory.

| Perspective | Description |
|---|---|
| **Business** | Professional online presence → patient trust → qualified appointment demand routed to existing channels. No operational load on the practice: no inbox, no forms, no schedule maintenance. |
| **Technical** | A zero-runtime-dependency static site; correctness is enforced at *build time* by validators and a check suite instead of at request time by a server. |

## 2. Services and information presented

| Offering | Where | State |
|---|---|---|
| Doctor profile & qualifications (6 cards) | `about.html` | Live content; credentials are site claims, **UNKNOWN** if independently verified |
| Areas of expertise: hip & knee surgery; fracture & trauma care; limb reconstruction | Home (`build_site.py` `home()` `interests`) | Live content |
| Conditions (9 topics) | `conditions.html` | 4 stated as in-scope, **5 flagged `pending`** (shoulder & elbow, hand & wrist, foot & ankle, paediatric, arthritis) |
| Treatments (8 topics) | `treatments.html` + 8 pages | All `draft`; **3 flagged `pending` scope** (foot & ankle procedures, paediatric procedures, non-operative care); each only ~2 short paragraphs |
| Patient guides (8) + 6 FAQs | `patient-information.html` + 8 pages | All `draft`; short question-led guides, deliberately **no doses/timetables/individual instructions** |
| Articles (40: 19 EN, 21 SI) | `articles.html` + 40 pages | All `draft`; long-form, imported from legacy archive with 390 image placements |
| Clinic directory (18 centres, 26 provider links) | `clinics.html` (+ Home/Contact excerpts) | Live; links last verified **2026-10-25** (UNKNOWN today) |
| Booking help, change/cancel guidance, emergency note | `contact.html`, FAQs | Live content |
| Privacy and Terms | `privacy.html`, `terms.html` | Live content; **production legal review not recorded** (DOCUMENTED) |

## 3. Users and their needs (INFERRED personas)

| Persona | Need | Served by |
|---|---|---|
| **New patient** with hip/knee/fracture problem | "Is this the right surgeon? Where and how do I book?" | Home hero → About → Clinics → provider button |
| **Patient preparing for surgery** | Plain-language preparation/recovery questions | Patient Information guides, Treatments |
| **Sinhala-speaking reader** | Material in Sinhala with proper typography | Articles (21 SI), local Noto Sans Sinhala, localised reading UI |
| **Parent/caregiver of a child** | Paediatric fracture/deformity information | 20 children-tagged articles + Sinhala children's guide |
| **Existing patient** with an appointment | How to change/cancel; what to bring | Contact page, consultation FAQ |
| **Mobile user** | One-handed access to booking | Fixed bottom bar "Booking help / Find a clinic" (`footer()`), responsive nav |
| **Person in an emergency** | Not to wait on the website | Contact page "For emergencies, seek urgent care" |
| **Maintainer / doctor's delegate** | Update copy without a CMS | JSON files + rebuild (`content/README.md`) |

## 4. Core business processes

### 4.1 Appointment booking (externalised)
1. Visitor chooses a hospital on **Clinics & Appointments**.
2. Clicks **eChannelling** and/or **Doc990** on that hospital's card — a normal same-tab link to the *doctor-and-hospital sessions page* on the provider.
3. Provider shows sessions, takes personal details and payment, and confirms the appointment.
4. Changes/cancellations/refunds are handled through the provider or hospital shown on the booking confirmation.

OrthoConnect never sees any of this data (CONFIRMED: no forms, no network calls, no storage). It also **does not guarantee** a link leads to an available session — the copy says so explicitly.

### 4.2 Content lifecycle (maintainer-driven)
`edit JSON / template → python3 -B scripts/build_site.py → run 3 checkers → commit generated HTML with its sources → push to main → GitHub Pages publishes`. Rollback = revert commit, rebuild, push (DOCUMENTED, `README.md`).

### 4.3 Clinical-governance lifecycle (designed but un-exercised)
`draft` → (clinician review, named reviewer + date) → `reviewed`. The generator enforces the fields but there is **no workflow tooling, approvals, or audit trail** — "Updating metadata is a manual publishing decision; this static build is not a staff authentication or approval system" (`content/README.md`). Currently **0 reviewed**.

### 4.4 Provider-link verification (external, offline)
An external toolkit (`Dr_Suneth_De_Silva_Unified_Link_Verifier`) captured the 26 deep links on 2026-10-25. The repo stores `verification_status` and `last_checked_utc` per link and rejects malformed ones, but **nothing re-checks liveness**.

## 5. Business rules encoded in the code

| ID | Rule | Enforced at | Evidence |
|---|---|---|---|
| BR-01 | A reading page is `draft` or `reviewed`; `reviewed` needs a named reviewer and a non-future ISO date | build time | `scripts/reading_content.py:49-55` |
| BR-02 | Author byline appears only if explicitly set — never inferred | build time | `build_site.py:301`, `article_library.py:123` |
| BR-03 | Every clinic needs ≥1 supported provider; eChannelling URL must be `https`, host `www.echannelling.com`, doctor-sessions path, matching `doctorId`/`hospitalCode`; Doc990 URL must be host `www.doc.lk` with `/channel/<id>` (optionally `/si/` or `/tm/`) | build time | `scripts/clinic_directory.py:10-53` |
| BR-04 | A missing provider link is omitted, never shown as "unavailable" | design | `README.md`; `check_clinics.py:74-75` (8 both / 5 e-only / 5 d-only) |
| BR-05 | Unknown clinic locality stays `null` — no inference | build time | `clinic_directory.py:19-20`; `content/README.md` |
| BR-06 | "Clinical review" and "service scope confirmed" are separate decisions (`pending` flag) | content | `content/README.md`; label "SERVICE SCOPE TO CONFIRM" (`build_site.py:183`) |
| BR-07 | No page may link to, redirect to, or hot-link `orthopaedic.lk` | check time | `scripts/check_site.py:99,112` |
| BR-08 | External reference links must be HTTPS | build time | `build_site.py:318-319`; `article_library.py:151-152` |
| BR-09 | Inline content images must be local JPEG/PNG under `assets/images/`, with alt text and intrinsic size | build time | `reading_content.py:129-142,165-170` |
| BR-10 | Original treatment illustrations must match their recorded SHA-256 | build time | `scripts/visual_design.py:26-27` |
| BR-11 | Booking links navigate in the **same tab**, with no intermediate dialog | check time | `check_clinics.py:60-61` |
| BR-12 | The 40 supplied articles are conserved verbatim except logged omissions (3 placeholders, 26 legacy enquiry prompts, 2 formatting changes) | check time | `scripts/check_article_migration.py` |
| BR-13 | Pages never claim testimonials, counts, fees, schedules or availability | content policy | `README.md`; `check_clinics.py:76-79` blocks prototype wording |

## 6. Intended user journeys (summary)
Detailed flowcharts and sequence diagrams are in `10_WORKFLOWS_AND_DATA_FLOWS.md`.

| ID | Journey | Implemented? |
|---|---|---|
| J1 | Home → About → trust the surgeon | Yes |
| J2 | Home/Clinics → pick hospital → provider session page → book | Yes (booking itself external) |
| J3 | Articles → filter (language/audience/region/topic/search) → read → related → return with filters restored | Yes |
| J4 | Conditions/Treatments → search/filter → reading page → "Find a Consultation" | Yes |
| J5 | Contact → how to change an appointment / prepare / emergency | Yes (no phone/e-mail/WhatsApp/map) |
| J6 | Old bookmark `treatments.html#hip-replacement` → dedicated page | Yes (JS) |
| J7 | Telephone / WhatsApp / map-directions journeys named in the brief | **NOT IMPLEMENTED** |

## 7. Business constraints, assumptions and client dependencies

| # | Item | Type | Source |
|---|---|---|---|
| 1 | Clinical review of all 56 drafts, incl. correction of text the repo flags as copied from another topic | Client approval | `docs/article-migration-review.md` §3 |
| 2 | Confirmation of **service scope** for 3 treatments and 5 conditions | Client approval | `content/site.json` `pending` |
| 3 | Authorship/attribution and image-reuse rights for legacy `orthopaedic.lk` material; "do not erase watermarks or transfer legacy credentials" | Legal/Client | `docs/article-migration-review.md` §4 |
| 4 | Supply of public telephone/WhatsApp/e-mail (if desired) | Client input | `README.md` |
| 5 | Production privacy/legal review | Client/Legal | `docs/clinic-validation.md` |
| 6 | Reconciliation of overlapping English child articles; Sinhala wording check | Editorial | `docs/article-migration-review.md` §1,2,5 |
| 7 | Hosting/domain decision for `orthoconnect.lk` | Client/Tech | Brief; absent in repo |
| 8 | Applicability of Sri Lankan medical-advertising / data-protection rules is **UNKNOWN** and needs professional advice (not evidenced in the repo) | Legal | — |
