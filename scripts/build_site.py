#!/usr/bin/env python3
"""Generate the standalone static pages from shared, local templates and copy.

The output needs no Python, build tool, package installation or server.
Run this file only when changing the shared templates or content/site.json.
"""

from html import escape
from pathlib import Path
import json
import re
from stock_assets import MANIFEST as STOCK, available_variants
from reading_content import READING, SLUG, load_reading_catalog, reading_url, resolve_content_url, rewrite_page_urls, render_blocks
from article_library import article_card, article_listing, article_reading_page, validate_articles, TEXT as ARTICLE_TEXT
from homepage import banner_carousel, body_region_selector, consultation_journey, guide_preview, resource_carousel, home_cta
from clinic_directory import PROVIDERS, validate_clinics
from visual_design import page_motif, treatment_illustration, reading_progress

ROOT = Path(__file__).resolve().parents[1]
DATA = load_reading_catalog(json.loads((ROOT / 'content/site.json').read_text()), ROOT)
validate_articles(DATA['articles'])
validate_clinics(DATA['clinics'], DATA['clinic_directory'])
NAV = DATA['navigation']


def e(value):
    return escape(str(value), quote=True)


def icon(name, extra=''):
    return f'<svg class="icon {extra}" aria-hidden="true"><use href="#icon-{e(name)}"></use></svg>'


def stock_photo(key, sizes='(max-width: 760px) 100vw, 40vw', loading='lazy'):
    variants = available_variants(key)
    if not variants:
        return ''
    record = STOCK['images'][key]
    src, width, height = variants[-1]
    srcset = ', '.join(f'{path} {w}w' for path, w, h in variants)
    return f'<img class="stock-photo stock-photo-{e(key)}" src="{e(src)}" srcset="{e(srcset)}" sizes="{e(sizes)}" alt="{e(record["alt"])}" width="{width}" height="{height}" loading="{e(loading)}" decoding="async">'


def button(label, href='clinics.html', style='primary', arrow=True):
    return f'<a class="button button-{style}" href="{e(href)}">{e(label)}{icon("arrow") if arrow else ""}</a>'


def brand():
    return '<a class="brand" href="index.html" aria-label="OrthoConnect home"><span class="logo-frame"><img class="logo-image" src="assets/images/orthoconnect-logo.jpeg" alt="OrthoConnect" width="1254" height="1254"></span></a>'


def nav_links(active, footer=False):
    return ''.join(f'<a href="{n["file"]}"{chr(32) + "aria-current=\"page\"" if n["id"] == active else ""}>{e(n["label"])}</a>' for n in NAV)


def header(active):
    return f'''<a class="skip-link" href="#main">Skip to content</a>
<header class="site-header" lang="en"><div class="container header-inner">
{brand()}
<nav class="primary-navigation" id="primary-navigation" aria-label="Main navigation">{nav_links(active)}</nav>
<div class="header-actions"><a class="button button-primary header-cta" href="clinics.html">{icon('calendar')}<span>Find a Consultation</span></a><button class="icon-button menu-toggle" type="button" aria-label="Open navigation" aria-expanded="false" aria-controls="primary-navigation">{icon('menu')}</button></div>
</div></header>'''


def footer(active):
    return f'''<footer class="site-footer" lang="en"><div class="container"><div class="footer-grid">
<div class="footer-identity">{brand()}<p><strong>Dr. Suneth De Silva</strong><br>Consultant Orthopaedic Surgeon</p><p>Expert care. Better movement.<br>A clear route to consultation.</p></div>
<div><h2 class="footer-title">Explore OrthoConnect</h2><nav class="footer-navigation" aria-label="Footer navigation">{nav_links(active, True)}</nav></div>
<div class="footer-consultation"><h2 class="footer-title">Clinics &amp; appointments</h2><p>Find a consultation location and choose an approved hospital or channelling provider.</p><a class="text-link" href="clinics.html">Find a Consultation {icon('arrow')}</a><p class="footer-medical-note">General educational information. Individual diagnosis and treatment require a medical consultation.</p></div>
</div><div class="footer-bottom"><p>© <span data-year>2026</span> OrthoConnect. All rights reserved.</p><nav aria-label="Policy links"><a href="privacy.html">Privacy policy</a><a href="terms.html">Terms &amp; medical information</a><a href="#top">Back to top ↑</a></nav></div></div></footer>
<nav class="mobile-actions" aria-label="Quick consultation actions"><a href="contact.html">{icon('info')}<span>Booking help</span></a><a href="clinics.html">{icon('calendar')}<span>Find a clinic</span></a></nav>'''





def section_head(eyebrow, title, intro='', link=None):
    action = f'<a class="text-link" href="{e(link[1])}">{e(link[0])} {icon("arrow")}</a>' if link else ''
    return f'<div class="section-heading"><div><p class="eyebrow">{e(eyebrow)}</p><h2>{title}</h2>{f"<p class=\"section-intro\">{intro}</p>" if intro else ""}</div>{action}</div>'


def cta(title='A consultation starts with understanding your concerns.'):
    return f'<section class="section section-soft"><div class="container"><div class="cta-band"><div><p class="eyebrow">YOUR NEXT STEP</p><h2>{e(title)}</h2><p>Explore the information relevant to you, then choose a consultation location and booking channel.</p></div>{button("Find a Consultation")}</div></div></section>'


def page_title(name, title, intro, eyebrow):
    image_key = STOCK['page_titles'].get(name)
    photo = stock_photo(image_key) if image_key else ''
    picture = f'<figure class="page-title-photo">{photo}</figure>' if photo else ''
    motif = page_motif(name, icon) if not photo else ''
    layout = ' page-title-with-photo' if photo else ''
    illustrated = ' page-title-illustrated' if motif else ''
    return f'<section class="page-title{illustrated}"><div class="container{layout}"><div class="page-title-copy"><nav class="breadcrumbs" aria-label="Breadcrumb"><a href="index.html">Home</a><span aria-hidden="true">/</span><span aria-current="page">{e(name)}</span></nav><p class="eyebrow">{e(eyebrow)}</p><h1>{e(title)}</h1><p class="page-intro">{e(intro)}</p></div>{picture}{motif}</div></section>'


def booking_note():
    return f'<div class="notice booking-note">{icon("info")}<p>Consultation dates, availability and final fees are confirmed by the hospital or booking provider.</p></div>'


def featured_clinics():
    return [next(c for c in DATA['clinics'] if c['id'] == cid) for cid in DATA['clinic_directory']['featured_ids']]


def clinic_card(c, filters=False):
    providers = [p for p in PROVIDERS if p in c['booking_links']]
    search = ' '.join(filter(None, [c['name'], c.get('branch'), c['location'], c['source_name']]))
    filtering = f' data-location="{e(c["location"] or "")}" data-platforms="{e(" ".join(providers))}" data-search="{e(search)}"' if filters else ''
    actions = []
    identity = ', '.join(filter(None, [c['name'], c.get('branch'), c['location']]))
    for provider in providers:
        link = c['booking_links'][provider]
        label = PROVIDERS[provider]
        accessible = f'View sessions and book via {label} at {identity}'
        actions.append(f'<a class="button button-booking" href="{e(link["url"])}" rel="external noreferrer" data-booking-provider="{e(provider)}" aria-label="{e(accessible)}">{e(label)}{icon("arrow")}</a>')
    locality = ' · '.join(filter(None, [c.get('branch'), c['location']]))
    location_html = f'<p class="clinic-address">{icon("pin")}<span>{e(locality)}</span></p>' if locality else ''
    return f'''<article class="clinic-card{' clinic-filterable' if filters else ''}" id="clinic-{e(c['id'])}"{filtering}><span class="square-icon">{icon('hospital','icon-large')}</span><h3>{e(c['name'])}</h3>{location_html}<div class="clinic-booking"><p class="clinic-booking-label">View sessions &amp; book through:</p><div class="clinic-card-actions">{''.join(actions)}</div></div></article>'''


def article_preview(item):
    language = item.get('lang', 'en')
    text = ARTICLE_TEXT[language]
    url = reading_url('articles', item)
    image_key = STOCK['article_previews'].get(item['id'])
    photo = stock_photo(image_key) if image_key else ''
    visual = photo or f'{icon(item["icon"],"article-illustration")}<span>{e(item["category"])}</span>'
    photo_class = ' article-art-photo' if photo else ''
    return f'<article class="article-card" lang="{language}"><a class="article-art{photo_class}" href="{url}" aria-label="{e(text["read"])}: {e(item["title"])}">{visual}</a><div class="article-copy"><p class="eyebrow">{e(item["category"])} <span class="topic-status">{e(text["draft"])}</span></p><div class="article-badges"><span class="article-chip">{"සිංහල" if language == "si" else "English"}</span></div><h3><a href="{url}">{e(item["title"])}</a></h3><p>{e(item["summary"])}</p><a class="text-link" href="{url}">{e(text["read"])} {icon("arrow")}</a></div></article>'


def treatment_preview(item, number):
    visual = treatment_illustration(item['id']) or icon(item['icon'], 'condition-icon')
    extra = ' treatment-preview-illustrated' if item['id'] in ('hip-replacement', 'knee-replacement', 'arthroscopy') else ''
    status = 'EDUCATIONAL DRAFT' if item['status'] == 'draft' else 'REVIEWED INFORMATION'
    return f'<article class="treatment-preview{extra}"><span class="item-number">0{number}</span>{visual}<span class="topic-status">{status}</span><h3>{e(item["title"])}</h3><p>{e(item["summary"])}</p><a class="text-link" href="{reading_url("treatments", item)}">Read treatment information {icon("arrow")}</a></article>'


def home():
    featured_articles = [next(i for i in DATA['articles'] if i['id'] == slug) for slug in ('en-adult-hip', 'si-adult-fractures', 'en-adult-knee')]
    facts = ''.join(f'<span class="qualification-pill">{e(t)}</span>' for t in ['MBBS (Colombo)','MD (Orthopaedic Surgery)','MRCSEd'])
    hero = f'''<section class="hero"><div class="container"><div class="hero-grid"><div class="hero-copy"><p class="eyebrow">ORTHOPAEDIC CARE · SRI LANKA</p><h1>Dr. Suneth De Silva</h1><p class="hero-designation">Consultant Orthopaedic Surgeon</p><p class="hero-intro">Specialist training in hip and knee surgery, with experience in orthopaedic trauma and limb reconstruction.</p><div class="hero-actions">{button('Find a Consultation')}{button('About Dr. De Silva','about.html','outline',False)}</div><div class="hero-facts">{facts}</div><nav class="hero-quicklinks" aria-label="Explore patient information"><a href="conditions.html">Explore conditions {icon('arrow')}</a><a href="treatments.html">Treatments &amp; surgery {icon('arrow')}</a><a href="patient-information.html">Patient information {icon('arrow')}</a></nav></div><div class="portrait-stage"><div class="portrait-backdrop" aria-hidden="true"></div><div class="portrait-frame"><img src="assets/images/dr-suneth-de-silva.jpeg" alt="Dr. Suneth De Silva in his academic gown outside the Fellows Entrance" width="1010" height="1557" fetchpriority="high"></div></div></div><div class="hero-bottom"><p>Explore Dr. De Silva’s experience, understand your options,<br>and find a consultation.</p><a class="button button-outline" href="contact.html">{icon('info')} Booking help</a></div></div></section>'''
    hero = hero.replace('<section class="hero">', '<section class="hero home-hero"><div class="hero-decoration" aria-hidden="true">' + icon('knee') + '</div>')
    interests = [
        ('hip','Hip & knee surgery','Assessment of hip and knee conditions, joint replacement, arthroscopy and selected ligament surgery.','treatments.html'),
        ('fracture','Fracture & trauma care','Assessment and treatment planning for fractures and injuries affecting bones and joints.','treatments.html#fracture-care'),
        ('reconstruction','Limb reconstruction','Assessment of difficult fracture healing and selected limb-reconstruction problems.','treatments.html#limb-reconstruction')]
    expertise = ''.join(f'<article class="expertise-card"><span class="square-icon">{icon(i,"icon-large")}</span><h3>{e(t)}</h3><p>{e(d)}</p><a class="text-link" href="{href}">Explore this area {icon("arrow")}</a></article>' for i,t,d,href in interests)
    cards = ''.join(f'<a class="condition-preview" href="conditions.html#{i["id"]}">{icon(i["icon"],"condition-icon")}<div><h3>{e(i["title"])}</h3><p>{e(i["summary"])}</p>{"<span class=\"topic-status\">EDUCATIONAL TOPIC</span>" if i.get("pending") else ""}</div>{icon("arrow")}</a>' for i in DATA['conditions'][:6])
    treatments = ''.join(treatment_preview(i, n) for n,i in enumerate(DATA['treatments'][:3],1))
    resources = [article_preview(i) for i in featured_articles]
    for slug in ('consultation-faq', 'walking', 'rehabilitation'):
        guide = next(i for i in DATA['guides'] if i['id'] == slug)
        resources.append(guide_preview(guide, stock_photo(guide['lead_image'], '(max-width: 600px) 80vw, (max-width: 1000px) 44vw, 360px'), icon, reading_url('guides', guide)))
    return banner_carousel() + hero + f'''<section class="section"><div class="container">{section_head('SPECIALIST AREAS','Key areas of expertise','Focused areas of practice, supported by specialist training.',('Meet Dr. De Silva','about.html'))}<div class="grid grid-three">{expertise}</div></div></section>
<section class="section home-conditions"><div class="container">{section_head('CONDITIONS & ASSESSMENT','Start with the problem<br>you want to understand.','Explore information by body region and type of concern.',('View all conditions','conditions.html'))}{body_region_selector()}<div class="grid grid-three conditions-preview-grid">{cards}</div></div></section>
<section class="section"><div class="container">{section_head('TREATMENTS & SURGERY','Explore treatment options','Understand the areas to discuss during an individual assessment.',('View all treatments','treatments.html'))}<div class="grid grid-three">{treatments}</div></div></section>
<section class="section section-soft home-clinics"><div class="container">{section_head('CLINICS & APPOINTMENTS','Find a clinic. Choose how to book.','Explore consultation locations and the available booking channels.',('View all clinics','clinics.html'))}{consultation_journey(icon)}<div class="grid grid-two clinic-preview-grid">{''.join(clinic_card(c) for c in featured_clinics())}</div>{booking_note()}</div></section>
<section class="section home-resources"><div class="container">{section_head('RESOURCES & ARTICLES','A little reading.<br>A clearer next step.','Independent Sinhala and English articles, plus guides to help you prepare for a consultation.',('View all articles','articles.html'))}{resource_carousel(resources, icon)}</div></section>''' + home_cta(stock_photo('walking-together', '(max-width: 760px) calc(100vw - 2.5rem), 560px'), button, icon)


def qualifications():
    return '<div class="qualifications-grid">' + ''.join(f'<article class="qualification-card">{icon(q["icon"],"icon-large")}<p class="eyebrow">{e(q["description"])}</p><h3>{e(q["title"])}</h3><p>{e(q["institution"])}</p></article>' for q in DATA['qualifications']) + '</div>'


def about():
    return page_title('About','About Dr. Suneth De Silva','Professional qualifications, UK hip and knee training, and areas of specialist interest.','MEET YOUR SPECIALIST') + f'''<section class="section"><div class="container about-profile"><figure class="about-portrait"><img src="assets/images/dr-suneth-de-silva.jpeg" alt="Dr. Suneth De Silva, Consultant Orthopaedic Surgeon" width="1010" height="1557"><figcaption>Dr. Suneth De Silva<br><span>Consultant Orthopaedic Surgeon</span></figcaption></figure><div class="prose"><p class="eyebrow">PROFESSIONAL PROFILE</p><h2>Specialist care.<br>A clear, considered approach.</h2><p>Dr. Suneth De Silva is a Consultant Orthopaedic Surgeon with focused expertise in hip and knee surgery, fracture and trauma care, and limb reconstruction.</p><p>He completed his MBBS at the University of Colombo and his MD in Orthopaedic Surgery through the Postgraduate Institute of Medicine, University of Colombo. His qualifications also include MRCSEd from the Royal College of Surgeons of Edinburgh.</p><p>He completed 24 months of specialist trauma and orthopaedic training in the United Kingdom through the International Surgical Training Programme of the Royal College of Surgeons of England. This included subspecialty training in hip and knee surgery at King’s Mill Hospital.</p><p>His fellowship experience included hip and knee reconstruction, joint replacement and soft-tissue knee surgery.</p>{button('Find a Consultation')}</div></div></section>
<section class="section section-soft"><div class="container">{section_head('QUALIFICATIONS','Qualifications & specialist training')}{qualifications()}</div></section>
<section class="section"><div class="container fellowship-layout"><div><p class="eyebrow">UK HIP & KNEE FELLOWSHIP</p><h2>International training.<br>Focused clinical interests.</h2><p class="section-intro">24 months of specialist training through the Royal College of Surgeons of England’s International Surgical Training Programme.</p><div class="fellowship-stat"><strong>24</strong><span>months of UK<br>specialist training</span></div></div><ol class="training-timeline"><li><h3>Medical & specialist qualifications</h3><p>MBBS and MD in Orthopaedic Surgery, University of Colombo.</p></li><li><h3>Professional surgical qualification</h3><p>MRCSEd, Royal College of Surgeons of Edinburgh.</p></li><li><h3>Hip & knee subspecialty training</h3><p>King’s Mill Hospital, United Kingdom, through the International Surgical Training Programme.</p></li><li><h3>Areas of practice</h3><p>Hip and knee surgery; fracture and orthopaedic trauma care; difficult fracture healing and selected limb reconstruction.</p></li></ol></div></section>''' + cta('Find the right place for your consultation.')


def library_filters(items, noun):
    categories = sorted({i['category'] for i in items})
    options = ''.join(f'<option value="{e(c)}">{e(c)}</option>' for c in categories)
    return f'<form class="filters library-filters" role="search" data-filter-form><div class="field search-field"><label for="library-search">Search {e(noun)}</label><input id="library-search" type="search" placeholder="Search by topic or keyword" data-search-input></div><div class="field"><label for="library-category">Category</label><select id="library-category" data-category-filter><option value="all">All categories</option>{options}</select></div><button class="button button-outline" type="reset">Reset filters</button></form><p class="results-count" aria-live="polite" aria-atomic="true" data-results-count>{len(items)} topics</p>'


def reading_card(item, kind, listing=False, context_language='en'):
    if kind == 'articles':
        return article_card(item, icon, listing, context_language)
    config = READING[kind]
    url = reading_url(kind, item)
    search = ' '.join([item['title'], item['category'], item['summary'], *item.get('keywords', [])])
    status = 'SERVICE SCOPE TO CONFIRM' if item.get('pending') else ('EDUCATIONAL DRAFT' if item['status'] == 'draft' else 'REVIEWED INFORMATION')
    identity = f' id="{e(item["id"])}" data-reading-url="{e(url)}"' if listing else ''
    filtering = f' data-category="{e(item["category"])}" data-search="{e(search)}"' if listing else ''
    language = item.get('lang', 'en')
    cross_language = f' lang="{e(language)}"' if language != context_language else ''
    language_badge = f'<div class="article-badges"><span class="article-chip">{"සිංහල" if language == "si" else "English"}</span></div>' if cross_language else ''
    illustration = treatment_illustration(item['id']) if kind == 'treatments' else ''
    glyph = '' if illustration else icon(item['icon'], 'condition-icon')
    return f'<article class="topic-card reading-card{" filterable-item" if listing else ""}"{cross_language}{identity}{filtering}>{illustration}<div class="topic-card-top">{glyph}<span class="topic-status">{status}</span></div>{language_badge}<p class="eyebrow">{e(item["category"])}</p><h3><a href="{e(url)}" lang="{e(language)}">{e(item["title"])}</a></h3><p>{e(item["summary"])}</p><a class="text-link reading-card-link" href="{e(url)}" aria-label="Read {config["singular"]}: {e(item["title"])}">Read {config["singular"]} {icon("arrow")}</a></article>'


def topic_card(item, kind):
    if kind in READING:
        return reading_card(item, kind, listing=True)
    description = ''.join(f'<p>{e(p)}</p>' for p in item.get('body',[]))
    if item.get('questions'):
        description = '<p>Use these questions as a starting point for a conversation with your treating team.</p><ul>' + ''.join(f'<li>{e(q)}</li>' for q in item['questions']) + '</ul><p>Follow the individual instructions provided by your treating team. This guide gives no medication doses, activity restrictions or recovery timetable.</p>'
    if item.get('source'):
        description += f'<a class="source-link" href="{e(item["source"])}" target="_blank" rel="noopener noreferrer">Further reading: {e(item["sourceLabel"])} {icon("external")}</a>'
    if item.get('related'):
        description += f'<a class="text-link" href="{e(item["related"])}">{e(item["relatedLabel"])} {icon("arrow")}</a>'
    if kind=='guides':
        description += '<a class="source-link" href="https://www.nhs.uk/tests-and-treatments/having-surgery/" target="_blank" rel="noopener noreferrer">Further reading: NHS guide to having surgery '+icon('external')+'</a>'
    status='SERVICE SCOPE TO CONFIRM' if item.get('pending') and kind=='treatments' else 'EDUCATIONAL DRAFT'
    search = ' '.join([item['title'],item['category'],item['summary'],*item.get('body',[]),*item.get('questions',[])])
    return f'<article class="topic-card filterable-item" data-category="{e(item["category"])}" data-search="{e(search)}"><div class="topic-card-top">{icon(item["icon"],"condition-icon")}<span class="topic-status">{status}</span></div><p class="eyebrow">{e(item["category"])}</p><h3>{e(item["title"])}</h3><p>{e(item["summary"])}</p><details class="topic-details" id="{e(item["id"])}"><summary>Read {"guide" if kind=='guides' else 'topic'} {icon('plus','disclosure-icon')}</summary><div class="topic-body"><span class="status-tag">Doctor review pending</span>{description}</div></details></article>'


def library_page(kind):
    if kind == 'articles':
        return page_title('Articles', 'Resources & articles', 'Independent Sinhala and English reading for adults and children.', 'ORTHOPAEDIC INSIGHTS') + article_listing(DATA['articles'], icon) + cta()
    config={
        'conditions': ('Conditions','Understand your condition','Patient-friendly introductions organised by body region and type of concern.','CONDITIONS & ASSESSMENT','Conditions by region & type','Explore the topics below. Educational categories do not establish a separate specialist service.'),
        'treatments': ('Treatments','Treatments & surgery','Explore treatment information and the questions to discuss at assessment.','TREATMENT OPTIONS','Surgical & non-operative treatment','Choose a topic to read the full treatment introduction. Individual suitability and any unconfirmed service scope require clinical assessment and confirmation.'),
        'guides': ('Patient Information','Information for your care journey','Prepare for a consultation and understand the questions to ask your treating team.','PATIENT INFORMATION','Before, after & beyond surgery','Open a guide for practical questions to discuss with your treating team. Your team provides individual instructions.'),
        'articles': ('Articles','Resources & articles','Plain-language introductions to orthopaedic questions and consultation decisions.','ORTHOPAEDIC INSIGHTS','Educational articles','Browse by topic and open an article to read more. These educational drafts are awaiting Dr. De Silva’s review.')
    }
    label,title,intro,eyebrow,heading,body=config[kind]
    items=DATA[kind]
    content=page_title(label,title,intro,eyebrow)
    content+=f'<section class="section"><div class="container" data-filter-scope data-filter-kind="library">{section_head(eyebrow,heading,e(body))}{library_filters(items,label.lower())}<div class="grid grid-three topic-grid">'+''.join(topic_card(i,kind) for i in items)+'</div><div class="empty-state" data-empty-state hidden><h3>No matching topics</h3><p>Try a different search or reset the filters to see all topics.</p><button class="button button-outline" type="button" data-clear-filters>Reset filters</button></div></div></section>'
    if kind=='treatments':
        content+=f'<section class="section section-soft" id="limb-reconstruction"><div class="container reconstruction-callout"><span class="square-icon">{icon("reconstruction","icon-large")}</span><div><p class="eyebrow">DIFFICULT FRACTURE HEALING</p><h2>Limb reconstruction & fracture healing</h2><p>Dr. De Silva also assesses fractures that have failed to unite or have healed abnormally, and selected limb-reconstruction problems.</p></div>{button("Find a Consultation")}</div></section>'
    if kind=='guides':
        faqs=''.join(f'<details class="faq-item"><summary>{e(f["question"])}{icon("plus","disclosure-icon")}</summary><div class="disclosure-body"><p>{e(f["answer"])}</p></div></details>' for f in DATA['faqs'])
        content+=f'<section class="section section-soft" id="faqs"><div class="container faq-layout"><div><p class="eyebrow">COMMON QUESTIONS</p><h2>Frequently asked<br>questions</h2><p class="section-intro">A straightforward guide to consultations, booking and using this website.</p>{button("Find a Consultation")}</div><div>{faqs}</div></div></section>'
    return content+cta()


def booking_steps():
    steps=[('Find your clinic','Choose a convenient hospital or channelling centre.'),('Choose how to book','Select the clinic’s eChannelling or Doc990 button to view Dr. De Silva’s sessions at that hospital.'),('Complete your booking','Choose an available session and complete your booking on the provider’s website. Check your confirmation before travelling.')]
    return '<ol class="booking-steps">'+''.join(f'<li><span>0{n}</span><div><h3>{e(t)}</h3><p>{e(b)}</p></div></li>' for n,(t,b) in enumerate(steps,1))+'</ol>'





def clinics():
    locations = ''.join(f'<option value="{e(location)}">{e(location)}</option>' for location in sorted({c['location'] for c in DATA['clinics'] if c['location']}))
    platforms = ''.join(f'<input type="radio" id="clinic-platform-{key}" name="platform" value="{key}"{" checked" if key == "all" else ""}><label for="clinic-platform-{key}">{label}</label>' for key, label in [('all', 'All platforms'), *PROVIDERS.items()])
    return page_title('Clinics & Appointments','Find a clinic. Choose how to book.','Find a convenient consultation location for Dr. Suneth De Silva, then choose a booking platform.','CLINICS & APPOINTMENTS') + f'''<section class="section"><div class="container" id="clinic-directory" data-clinic-directory>{section_head("CONSULTATION LOCATIONS","Where would you like to consult?")}<form class="clinic-filters" role="search" aria-label="Find a consultation clinic" data-clinic-form hidden><div class="clinic-filter-fields"><div class="field clinic-search-field"><label for="clinic-search">Search hospitals or towns</label><input id="clinic-search" name="q" type="search" maxlength="120" placeholder="Hospital name or town" autocomplete="off"></div><div class="field"><label for="clinic-location">Location</label><select id="clinic-location" name="location"><option value="all">All locations</option>{locations}</select></div></div><fieldset class="clinic-platforms"><legend>Booking platform</legend><div class="clinic-platform-options">{platforms}</div></fieldset><div class="clinic-filter-bottom"><p class="small muted">Select a platform to find clinics with that booking option.</p><button class="text-link" type="button" data-clear-clinic-filters>Clear filters</button></div></form><noscript><p class="small muted">All clinics are listed below. Choose a booking platform on your preferred clinic’s card to view sessions.</p></noscript><p class="results-count" data-clinic-count aria-live="polite" aria-atomic="true">Showing {len(DATA['clinics'])} clinics</p><div class="grid grid-two clinic-directory-grid">{''.join(clinic_card(c, True) for c in DATA['clinics'])}</div><div class="empty-state" data-clinic-empty hidden><h3>No matching clinics</h3><p>Try another hospital name or town, or clear your filters to see all clinics.</p><button class="button button-outline" type="button" data-clear-clinic-filters>Clear filters</button></div>{booking_note()}</div></section><section class="section section-soft"><div class="container booking-explainer"><div><p class="eyebrow">HOW TO BOOK</p><h2>Your next steps</h2><p class="section-intro">Choose a clinic, view the sessions and book with your preferred provider.</p><p class="booking-support">Already have an appointment? Use your booking confirmation to contact the hospital or booking provider about changes and cancellations.</p></div>{booking_steps()}</div></section>'''





def contact():
    support = f'''<article class="contact-channel"><span class="square-icon">{icon('calendar','icon-large')}</span><h3>Book a consultation</h3><p>Choose your preferred hospital and open its eChannelling or Doc990 sessions page.</p><a class="contact-link" href="clinics.html">Find a clinic {icon('arrow')}</a></article><article class="contact-channel"><span class="square-icon">{icon('message','icon-large')}</span><h3>Change an appointment</h3><p>For a change, cancellation or payment question, contact the hospital or booking provider using the details on your booking confirmation.</p></article><article class="contact-channel"><span class="square-icon">{icon('book','icon-large')}</span><h3>Prepare for your visit</h3><p>Read what to bring to your consultation and prepare the questions you would like to ask.</p><a class="contact-link" href="patient-information/consultation-faq.html">Read the consultation guide {icon('arrow')}</a></article>'''
    return page_title('Contact','Contact & appointment support','Book through your preferred clinic’s booking platform. For help with an existing appointment, contact the hospital or provider shown on your confirmation.','APPOINTMENT SUPPORT') + f'''<section class="section"><div class="container">{section_head("YOUR APPOINTMENT","How can we help?")}<div class="grid grid-three">{support}</div></div></section><section class="section section-soft"><div class="container">{section_head("CONSULTATION LOCATIONS","Find a clinic. Choose how to book.","View Dr. De Silva’s sessions at your preferred hospital.",("View all clinics","clinics.html"))}<div class="grid grid-two clinic-preview-grid">{''.join(clinic_card(c) for c in featured_clinics())}</div>{booking_note()}</div></section><section class="section"><div class="container"><div class="emergency-note">{icon("info","icon-large")}<div><h2>For emergencies, seek urgent care.</h2><p>Contact an appropriate hospital or emergency service. Do not wait for a consultation booking or an online reply.</p></div></div></div></section>'''


def policy(kind):
    if kind == 'privacy':
        name, title, intro = 'Privacy policy', 'Privacy policy', 'How OrthoConnect handles information when you browse and follow booking links.'
        sections = [
            ('Browsing this website', 'OrthoConnect provides information about Dr. Suneth De Silva and links to external consultation booking services. You can browse without creating an account or entering patient details.'),
            ('Search and filters', 'Clinic and article searches run in your browser. Filter choices may appear in the page address so you can share or return to the same results. This website does not save those choices in cookies or browser storage. Avoid entering personal or medical information into search fields.'),
            ('Appointments and payments', 'Selecting eChannelling or Doc990 opens the relevant provider’s website. That provider handles appointment details, personal information, payments and booking confirmations under its own privacy policy and terms.'),
            ('Medical reports and patient records', 'This website has no patient account, medical-record upload or appointment submission form. It does not collect medical reports or process payments.'),
            ('Cookies, assets and hosting', 'The website application does not set cookies or use analytics or advertising scripts. Fonts and images are hosted with the website. The hosting service may process standard request information, such as IP addresses, browser details and requested pages, to deliver and secure the website.'),
            ('External websites', 'Booking platforms and further-reading websites operate independently. Review their privacy policies before providing personal information. Contact the hospital or booking provider directly about information supplied during a booking.'),
        ]
    else:
        name, title, intro = 'Terms & medical information', 'Terms & medical information', 'Please read this before using the website or arranging a consultation.'
        sections = [
            ('Educational information', 'Website information supports an individual medical consultation. It does not provide a diagnosis or an individual treatment, medication or recovery plan. Educational drafts are labelled where clinical review is pending.'),
            ('Consultation and booking', 'OrthoConnect helps you find consultation locations and open the relevant eChannelling or Doc990 booking page. The hospital or provider manages availability, appointment confirmation, fees and payments. Opening a booking page does not itself confirm an appointment.'),
            ('Schedules, fees and changes', 'Consultation dates, times, availability and charges can change. Check the details on your selected booking platform and your appointment confirmation before travelling. For changes, cancellations or refunds, contact the hospital or booking provider shown on that confirmation.'),
            ('Services and treatment decisions', 'The website presents documented areas of practice and educational topics. A topic’s inclusion does not establish a separate specialist service. Treatment options and suitability require individual clinical assessment.'),
            ('Emergency care', 'For an emergency, contact an appropriate hospital or emergency service. Do not wait for a consultation booking or an online reply.'),
            ('Images and further reading', 'The portrait and logo were supplied for OrthoConnect. Images and written materials remain subject to their respective rights and licences. External educational links do not imply endorsement or affiliation.'),
        ]
    body = ''.join(f'<section class="legal-section"><h2>{e(h)}</h2><p>{e(b)}</p></section>' for h, b in sections)
    return page_title(name,title,intro,'WEBSITE INFORMATION') + f'<section class="section"><div class="container legal-layout"><aside class="legal-aside"><p>For appointments, select your clinic and continue to its booking provider.</p><a class="text-link" href="clinics.html">Find a clinic {icon("arrow")}</a><a class="text-link" href="contact.html">Booking help {icon("arrow")}</a></aside><div class="legal-copy">{body}</div></div></section>'


def not_found():
    return '<section class="section"><div class="container not-found"><p class="eyebrow">404 · PAGE NOT FOUND</p><h1>Let’s get you<br>to the right place.</h1><p>The page you’re looking for could not be found. Explore the website or find a consultation using the links below.</p><div class="hero-actions">'+button('Return home','index.html')+button('Find a Consultation','clinics.html','outline')+'</div></div></section>'


def reading_page(kind, item):
    if kind == 'articles':
        figure = ''
        photo = stock_photo(item.get('lead_image'), '(max-width: 1040px) calc(100vw - 2.5rem), 46rem', loading='eager')
        if photo:
            figure = f'<figure class="reading-figure" lang="en"><div class="reading-image">{photo}</div></figure>'
        return article_reading_page({**item, '_lead_figure': figure}, DATA, icon, reading_card)
    from datetime import date
    from urllib.parse import urlsplit

    config = READING[kind]
    language = item.get('lang', 'en')
    is_draft = item['status'] == 'draft'
    status = 'Educational draft' if is_draft else 'Reviewed information'
    state = 'Doctor review pending' if is_draft else 'Clinical review recorded'
    metadata = f'<span class="status-tag">{status}</span><span>{state}</span>'
    if item.get('pending'):
        metadata += '<span class="reading-scope">Service scope awaiting confirmation</span>'
    if item.get('author'):
        metadata += f'<span>Author: {e(item["author"])}</span>'
    if not is_draft:
        reviewed_date = date.fromisoformat(item['reviewed_on'])
        metadata += f'<span>Reviewed by {e(item["reviewed_by"])} · <time datetime="{e(item["reviewed_on"])}">{reviewed_date.strftime("%d %B %Y")}</time></span>'

    contents = []
    sections = []
    for section in item['sections']:
        target = 'reading-' + section['id']
        sublinks = ''.join(f'<li><a data-reading-toc-link href="#reading-{e(b["id"])}">{e(b["text"])}</a></li>' for b in section['blocks'] if b['type'] == 'heading')
        sublist = f'<ol>{sublinks}</ol>' if sublinks else ''
        contents.append(f'<li><a data-reading-toc-link href="#{e(target)}">{e(section["heading"])}</a>{sublist}</li>')
        sections.append(f'<section class="reading-section" id="{e(target)}" tabindex="-1"><h2>{e(section["heading"])}</h2>{render_blocks(section["blocks"], ROOT)}</section>')

    links = []
    for reference in item.get('references', []):
        if urlsplit(reference['url']).scheme != 'https':
            raise ValueError('Educational references must use HTTPS')
        links.append(f'<li><a href="{e(reference["url"])}" target="_blank" rel="noopener noreferrer">{e(reference["label"])} {icon("external")}</a></li>')
    related_records = [(r['kind'], next(i for i in DATA[r['kind']] if i['id'] == r['id'])) for r in item.get('related_items', [])]
    related_urls = {reading_url(k, r) for k, r in related_records}
    if item.get('related') and resolve_content_url(item['related'], DATA) not in related_urls:
        links.append(f'<li><a href="{e(item["related"])}">{e(item["relatedLabel"])} {icon("arrow")}</a></li>')
    if links:
        contents.append('<li><a data-reading-toc-link href="#reading-further-reading">Further reading &amp; links</a></li>')
        sections.append('<section class="reading-section reading-references" id="reading-further-reading" tabindex="-1"><h2>Further reading &amp; links</h2><ul>'+''.join(links)+'</ul></section>')

    photo = stock_photo(item.get('lead_image'), '(max-width: 1040px) calc(100vw - 2.5rem), 46rem', loading='eager')
    figure = treatment_illustration(item['id'], loading='eager') if kind == 'treatments' else ''
    if photo:
        figure = f'<figure class="reading-figure"><div class="reading-image">{photo}</div></figure>'

    contents_html = '<ol lang="'+e(language)+'">'+''.join(contents)+'</ol>'
    sidebar = f'''<aside class="reading-sidebar" aria-label="Reading navigation" lang="en"><details class="reading-contents" data-reading-contents open><summary>On this page {icon('plus','disclosure-icon')}</summary><nav aria-label="On this page">{contents_html}</nav></details><div class="reading-consultation">{icon('calendar','icon-large')}<h2>Find a consultation</h2><p>Choose a location and explore the available booking options.</p>{button('Find a Consultation')}</div></aside>'''
    heading = f'''<header class="reading-header"><div class="container"><nav class="breadcrumbs" aria-label="Breadcrumb" lang="en"><a href="index.html">Home</a><span aria-hidden="true">/</span><a href="{config['listing']}">{e(config['label'])}</a><span aria-hidden="true">/</span><span aria-current="page" lang="{e(language)}">{e(item['title'])}</span></nav><p class="eyebrow">{e(item['category'])}</p><h1 id="reading-title">{e(item['title'])}</h1><p class="reading-intro">{e(item['summary'])}</p><div class="reading-meta" lang="en">{metadata}</div></div></header>'''
    article = f'<article class="reading-article" aria-labelledby="reading-title" lang="{e(language)}">{figure}{"".join(sections)}<div class="reading-return" lang="en"><a class="text-link" href="{config["listing"]}">← Back to {e(config["label"])}</a></div></article>'
    related_html = ''
    if related_records:
        cards = ''.join(reading_card(record, related_kind) for related_kind, record in related_records)
        columns = 'grid-two' if len(related_records) == 2 else ('grid-three' if len(related_records) >= 3 else 'reading-related-single')
        related_html = f'<section class="section section-soft" lang="en"><div class="container">{section_head("CONTINUE READING","Related information")}<div class="grid {columns}">{cards}</div></div></section>'
    return heading + f'<div class="container reading-layout">{sidebar}{article}</div>' + related_html + cta()


def write_page(filename,active,title,description,body,language='en'):
    sprite=(ROOT/'assets/icons/sprite.svg').read_text()
    symbols=sprite[sprite.index('>')+1:sprite.rindex('</svg>')]
    symbols=re.sub(r'id="([^"]+)"',r'id="icon-\1"',symbols)
    header_html = header(active)
    if language == 'si':
        header_html = header_html.replace('Skip to content', 'අන්තර්ගතයට යන්න')
    footer_html = footer(active)
    article_script = '<script src="scripts/articles.js" defer></script>' if active == 'articles' else ''
    if active == 'clinics':
        article_script += '<script src="scripts/clinics.js" defer></script>'
    if active == 'home':
        article_script += '<link rel="stylesheet" href="styles/home.css"><script src="scripts/home.js" defer></script>'
    preload_font = 'noto-sans-sinhala-regular.ttf' if language == 'si' else 'noto-sans-regular.ttf'
    if Path(filename).parent != Path('.'):
        header_html = header_html.replace('aria-current="page"', 'aria-current="location"')
        footer_html = footer_html.replace('aria-current="page"', 'aria-current="location"')
    progress_html = reading_progress() if Path(filename).parent != Path('.') else ''
    html=f'''<!doctype html>
<html lang="{e(language)}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="robots" content="noindex,nofollow"><meta name="description" content="{e(description)}"><meta name="theme-color" content="#12334b"><title>{e(title)} | OrthoConnect</title><link rel="icon" href="assets/images/orthoconnect-logo.jpeg" type="image/jpeg"><link rel="preload" href="assets/fonts/{preload_font}" as="font" type="font/ttf" crossorigin><link rel="stylesheet" href="styles/tokens.css"><link rel="stylesheet" href="styles/main.css"><script src="scripts/main.js" defer></script>{article_script}<link rel="stylesheet" href="styles/effects.css"><script src="scripts/effects.js" defer></script></head>
<body id="top" data-page="{e(active)}"><svg class="icon-sprite" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" focusable="false">{symbols}</svg>
{header_html}{progress_html}<main id="main" tabindex="-1">{body}</main>{footer_html}</body></html>'''
    html = rewrite_page_urls(html, filename, DATA)
    destination = ROOT / filename
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(html)


def main():
    retired = DATA.get('retired_articles', [])
    if any(not SLUG.fullmatch(slug) or any(item['id'] == slug for item in DATA['articles']) for slug in retired):
        raise ValueError('Retired article IDs must be valid and absent from the active catalog')
    pages=[
        ('index.html','home','Dr. Suneth De Silva · Consultant Orthopaedic Surgeon','Meet Dr. Suneth De Silva, explore orthopaedic conditions and treatments, and find a consultation.',home()),
        ('about.html','about','About Dr. Suneth De Silva','Professional profile, qualifications and 24 months of UK specialist training.',about()),
        ('conditions.html','conditions','Conditions & assessment','Explore orthopaedic information by body region and type of concern.',library_page('conditions')),
        ('treatments.html','treatments','Treatments & surgery','Hip and knee surgery, fracture care, limb reconstruction and educational treatment topics.',library_page('treatments')),
        ('patient-information.html','patient-information','Patient information','Question-based preparation and recovery guides, consultation information and FAQs.',library_page('guides')),
        ('clinics.html','clinics','Clinics & appointments','Find Dr. Suneth De Silva’s consultation clinics and view hospital-specific sessions on eChannelling or Doc990.',clinics()),
        ('articles.html','articles','Resources & articles','Independent Sinhala and English orthopaedic articles for adults and children, organised by body region and topic.',library_page('articles')),
        ('contact.html','contact','Contact & consultation support','Find consultation booking links and support for existing appointments.',contact()),
        ('privacy.html','privacy','Privacy policy','How OrthoConnect handles browsing, filters and external booking links.',policy('privacy')),
        ('terms.html','terms','Terms & medical information','Educational information, external consultation booking and use of OrthoConnect.',policy('terms')),
        ('404.html','404','Page not found','Find your way to OrthoConnect information and consultation options.',not_found()),
    ]
    detail_pages = [(reading_url(kind, item), READING[kind]['active'], item['title'], item['summary'], reading_page(kind, item), item.get('lang', 'en')) for kind in READING for item in DATA[kind]]
    aliases={'services.html':'treatments.html','medical-information.html':'patient-information.html','hospitals.html':'clinics.html'}
    for filename,active,title,description,body in pages:
        write_page(filename,active,title,description,body)
    for filename,active,title,description,body,language in detail_pages:
        write_page(filename,active,title,description,body,language)
    # Compatibility routes contain the complete target page, retaining hash links
    # and working even when JavaScript or HTTP redirects are unavailable.
    for alias,target in aliases.items():
        (ROOT/alias).write_text((ROOT/target).read_text())
    for slug in retired:
        (ROOT / 'articles' / f'{slug}.html').unlink(missing_ok=True)
    print(f'Generated {len(pages)} public pages, {len(detail_pages)} reading pages and {len(aliases)} compatibility routes.')


if __name__=='__main__':
    main()
