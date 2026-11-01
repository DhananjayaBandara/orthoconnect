# 21 — Visual System Map

Evidence legend: **CONFIRMED · INFERRED · DOCUMENTED · NOT IMPLEMENTED · UNKNOWN**.
All diagrams describe the **actual** implementation (or are labelled DOCUMENTED / NOT PRESENT). None depicts a future architecture. The detailed diagrams live next to the text that explains them; this page holds the **master map**, the **consolidated user journey**, and an **index**.

## 1. Master system map

```mermaid
flowchart TB
    subgraph users["External users"]
        patient(["Patient or caregiver<br/>Sinhala or English reader"])
        maint(["Maintainer<br/>single developer"])
        clin(["Clinician reviewer<br/>no in-system role"])
    end

    subgraph hosting["Hosting boundary - GitHub, DOCUMENTED"]
        pages["GitHub Pages<br/>serves the whole repo root"]
    end

    subgraph frontend["Frontend - 70 static HTML pages"]
        pubs["11 public pages"]
        reading["56 reading pages<br/>40 articles, 8 treatments, 8 guides"]
        alias["3 alias copies"]
        jsf["5 runtime JS files"]
        cssf["4 CSS files"]
    end

    subgraph build["Build-time backend - Python 3.12+ standard library"]
        gen["build_site.py plus 6 helper modules"]
        audits["3 Python audits plus Node suites"]
    end

    subgraph data["Data layer - files only"]
        json["66 JSON files<br/>site hub, drafts, config, provenance"]
        media["Assets<br/>251 article images, banners, stock photos, fonts, SVG"]
    end

    subgraph ext["External providers - links only"]
        ech["eChannelling<br/>13 centres"]
        d990["Doc990 - doc.lk<br/>13 centres"]
        nhs["NHS UK<br/>11 reference links"]
        pex["Pexels<br/>dev-time download only"]
    end

    auth["Authentication and authorization<br/>NOT PRESENT"]
    db["Database<br/>NOT PRESENT"]

    maint --> gen
    clin -.->|review decisions entered by hand| json
    json --> gen
    media --> gen
    gen --> pubs
    gen --> reading
    gen --> alias
    gen --> audits
    pubs --> pages
    reading --> pages
    alias --> pages
    jsf --> pages
    cssf --> pages
    patient -->|HTTPS GET| pages
    patient -->|follows booking links| ech
    patient -->|follows booking links| d990
    patient -->|follows reference links| nhs
    gen -.-> pex
    auth -.- pages
    db -.- gen
```

Reading the map: data flows left-to-right through the **build**, not through a server. At run time the only arrows are *visitor ↔ static host* and *visitor → external provider*. Authentication and database boxes are drawn only to show their **absence**.

## 2. Consolidated user journey

```mermaid
flowchart LR
    subgraph s1["Discover"]
        a1["Home: banner, hero, key areas"] --> a2["About: qualifications"]
    end
    subgraph s2["Understand"]
        b1["Conditions and Treatments"] --> b2["Patient guides and FAQs"]
        b1 --> b3["Articles in English or Sinhala, with filters"]
    end
    subgraph s3["Choose"]
        c1["Clinics and Appointments"] --> c2["Filter by town or platform"]
    end
    subgraph s4["Book - on the provider site"]
        d1["Doctor sessions page"] --> d2["Choose a session, details, payment"] --> d3["Provider confirmation"]
    end
    subgraph s5["Afterwards"]
        e1["Contact: change or cancel guidance"]
        e2["Consultation guide: what to bring"]
    end
    a1 --> c1
    a2 --> b1
    b2 --> c1
    b3 --> c1
    c2 --> d1
    d3 --> e1
    d3 --> e2
```

Not drawn because **NOT IMPLEMENTED**: telephone, WhatsApp, e-mail, map/directions, on-site appointment request, account login.

## 3. Diagram index

| # | Diagram | Type | Location |
|---|---|---|---|
| D1 | System context | flowchart | `06_SYSTEM_ARCHITECTURE.md` §2 |
| D2 | High-level component architecture | flowchart | `06_…` §3 |
| D3 | Detailed module and data dependencies | flowchart | `06_…` §4 |
| D4 | Runtime page → asset composition | flowchart | `06_…` §5 |
| D5 | Content model (JSON, not a database) | ER diagram | `09_DATABASE_ARCHITECTURE.md` §3.1 |
| D6 | Data lifecycle and provenance | flowchart | `09_…` §2 |
| D7 | Site navigation | flowchart | `10_WORKFLOWS_AND_DATA_FLOWS.md` §2 |
| D8 | Find a clinic and follow a booking link | sequence | `10_…` §3 |
| D9 | Discover and read articles | sequence | `10_…` §4 |
| D10 | Legacy bookmark forwarding | sequence | `10_…` §7 |
| D11 | Edit content and rebuild | flowchart | `10_…` §8 |
| D12 | Legacy archive import | flowchart | `10_…` §9 |
| D13 | Publish to GitHub Pages | sequence | `10_…` §10 |
| D14 | Runtime data flow | flowchart | `10_…` §11 |
| D15 | Deployment architecture | flowchart | `17_DEPLOYMENT_AND_ENVIRONMENT.md` §7 |
| D16 | Master system map | flowchart | this page §1 |
| D17 | Consolidated user journey | flowchart | this page §2 |

## 4. Rendering note
Diagrams are Mermaid fenced blocks, valid for GitHub's renderer and common Mermaid viewers. They were written by hand and **were not rendered in this environment** (no Mermaid renderer available); if one fails to render, the surrounding tables carry the same information in text.
