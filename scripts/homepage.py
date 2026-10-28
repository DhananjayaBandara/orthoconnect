"""Homepage-only navigation and presentation components; no clinical content."""

from html import escape
import json
from pathlib import Path


def banner_carousel():
    config = json.loads((Path(__file__).resolve().parents[1] / 'content/home-carousel.json').read_text())
    slides = config['slides']
    items, dots = [], []
    for index, slide in enumerate(slides):
        current = index == 0
        srcset = ', '.join(f'{variant["src"]} {variant["width"]}w' for variant in slide['variants'])
        state = ' is-active' if current else ''
        inactive = '' if current else ' aria-hidden="true" inert'
        loading = 'loading="eager" fetchpriority="high"' if current else 'loading="lazy" fetchpriority="low"'
        desktop = slide['desktop']
        desktop_source = f'<source media="(min-width: 761px)" type="image/webp" srcset="{escape(desktop["src"], quote=True)} {desktop["width"]}w" sizes="100vw" width="{desktop["width"]}" height="{desktop["height"]}">'
        items.append(f'''<div class="banner-slide{state}" id="home-banner-{index + 1}" role="group" aria-roledescription="slide" aria-label="{index + 1} of {len(slides)}" data-banner-title="{escape(slide['title'], quote=True)}"{inactive}><a class="banner-slide-link" href="{escape(slide['href'], quote=True)}"><picture>{desktop_source}<source type="image/webp" srcset="{escape(srcset, quote=True)}" sizes="(min-width: 1672px) 1672px, 100vw"><img src="{escape(slide['src'], quote=True)}" alt="{escape(slide['alt'], quote=True)}" width="{slide['width']}" height="{slide['height']}" {loading} decoding="async"></picture></a></div>''')
        dots.append(f'<button class="banner-dot" type="button" data-banner-dot="{index}" aria-label="Show slide {index + 1}: {escape(slide["title"], quote=True)}" aria-controls="home-banner-{index + 1}"' + (' aria-current="true"' if current else '') + '><span aria-hidden="true"></span></button>')
    first = slides[0]
    return f'''<section class="banner-carousel" data-banner-carousel data-banner-interval="{config['interval_ms']}" aria-label="OrthoConnect highlights" aria-roledescription="carousel"><div class="banner-viewport" id="home-banner-viewport">{''.join(items)}</div><div class="banner-dots" data-banner-controls role="group" aria-label="Choose a banner" hidden>{''.join(dots)}</div><p class="visually-hidden" data-banner-status aria-live="off" aria-atomic="true">Slide 1 of {len(slides)}: {escape(first['title'])}</p></section>'''


def body_region_selector():
    # Shared destinations are intentional: the existing Conditions page groups
    # shoulder/elbow. Spine has a dedicated supplied article rather than a card.
    regions = [
        ('shoulder', 'Shoulder', 'conditions.html#shoulder-elbow', 106, 103),
        ('elbow', 'Elbow', 'conditions.html#shoulder-elbow', 88, 193),
        ('hand', 'Wrist & hand', 'conditions.html#hand-wrist', 69, 259),
        ('spine', 'Spine', 'articles/en-adult-spine.html', 150, 155),
        ('hip', 'Hip', 'conditions.html#hip', 177, 255),
        ('knee', 'Knee', 'conditions.html#knee', 176, 344),
        ('ankle', 'Foot & ankle', 'conditions.html#foot-ankle', 178, 419),
    ]
    markers, links = [], []
    for number, (key, label, url, x, y) in enumerate(regions, 1):
        markers.append(f'<a class="region-marker region-{key}" href="{url}" data-region="{key}" style="--region-x:{x / 3:.3f}%;--region-y:{y / 4.6:.3f}%" aria-label="Explore {escape(label.lower())} information"><span aria-hidden="true">{number:02}</span></a>')
        links.append(f'<li><a href="{url}" data-region="{key}"><span class="region-number" aria-hidden="true">{number:02}</span><span>{escape(label)}</span><span class="region-arrow" aria-hidden="true">↗</span></a></li>')
    return '''<div class="body-explorer" data-body-explorer>
<div class="body-visual"><p class="eyebrow">EXPLORE BY BODY REGION</p><div class="body-map">
<svg viewBox="0 0 300 460" aria-hidden="true" focusable="false">
<circle class="body-orbit" cx="150" cy="230" r="143"/>
<circle class="body-orbit" cx="150" cy="230" r="110"/>
<circle class="body-head" cx="150" cy="44" r="25"/>
<path class="body-outline" d="M136 69v15l-32 12q-15 5-20 26L65 242q-3 18 8 22 11 3 15-13l21-98 4 75-5 25 16 177q1 16 14 16 12 0 12-16l1-150h5l5 150q0 16 13 16 13 0 13-17l5-176-5-25 4-75 21 98q4 16 15 13 11-4 8-22l-19-120q-5-21-20-26l-32-12V69"/>
<path class="body-detail" d="M150 94v119m-24 26q24 14 48 0m-49 100h20m19 0h20"/>
</svg>''' + ''.join(markers) + '''</div><p class="body-caption">Choose a numbered region or use the links.</p></div>
<nav class="region-navigation" aria-label="Explore information by body region"><h3>Where would you like to start?</h3><p>Find educational information about the area that interests you.</p><ol class="region-list">''' + ''.join(links) + '''</ol><p class="small muted">Educational navigation. Some topics await clinical review or service-scope confirmation.</p></nav></div>'''


def consultation_journey(icon):
    steps = [
        ('pin', 'Choose a location', 'Find a convenient hospital or channelling centre.', 'clinics.html', 'Explore locations'),
        ('calendar', 'Select a booking channel', 'View the clinic’s eChannelling or Doc990 sessions. The provider confirms your appointment.', 'clinics.html', 'Understand booking'),
        ('book', 'Prepare for your visit', 'Read the consultation guide and note the questions you would like to ask.', 'patient-information/consultation-faq.html', 'Read the guide'),
    ]
    cards = ''.join(f'<li><span class="journey-step">0{n}</span><span class="journey-icon">{icon(glyph, "icon-large")}</span><h3>{title}</h3><p>{description}</p><a class="text-link" href="{url}">{label} {icon("arrow")}</a></li>' for n, (glyph, title, description, url, label) in enumerate(steps, 1))
    return f'<div class="journey-heading"><p class="eyebrow">A CLEAR NEXT STEP</p><h3>Your route to a consultation</h3></div><ol class="consultation-journey">{cards}</ol>'


def guide_preview(item, photo, icon, url):
    status = 'EDUCATIONAL DRAFT' if item['status'] == 'draft' else 'REVIEWED INFORMATION'
    return f'''<article class="article-card guide-preview" lang="en"><a class="article-art article-art-photo" href="{url}" aria-label="Read guide: {escape(item['title'])}">{photo}</a><div class="article-copy"><p class="eyebrow">PATIENT GUIDE <span class="topic-status">{status}</span></p><div class="article-badges"><span class="article-chip">English</span></div><h3><a href="{url}">{escape(item['title'])}</a></h3><p>{escape(item['summary'])}</p><a class="text-link" href="{url}">Read guide {icon('arrow')}</a></div></article>'''


def resource_carousel(cards, icon):
    items = ''.join(f'<li class="resource-slide">{card}</li>' for card in cards)
    return f'''<div class="resource-carousel" data-resource-carousel role="region" aria-label="Featured articles and patient guides"><div class="carousel-toolbar" data-carousel-controls hidden><p class="carousel-hint">Browse at your own pace <span aria-hidden="true">→</span></p><div class="carousel-buttons"><button class="icon-button carousel-previous" type="button" aria-label="Previous resources" aria-controls="home-resource-track" aria-disabled="true">{icon('arrow')}</button><button class="icon-button carousel-next" type="button" aria-label="Next resources" aria-controls="home-resource-track" aria-disabled="false">{icon('arrow')}</button></div></div><ul class="resource-track" id="home-resource-track">{items}</ul><div class="carousel-footer"><p class="carousel-status" data-carousel-status aria-live="polite" aria-atomic="true"></p><a class="text-link" href="patient-information.html">View all patient guides {icon('arrow')}</a></div></div>'''


def home_cta(photo, button, icon):
    return f'''<section class="section home-next-step"><div class="container"><div class="home-photo-callout"><div class="home-photo-copy"><p class="eyebrow">YOUR NEXT STEP</p><h2>A consultation starts with understanding your concerns.</h2><p>Explore the information relevant to you, then choose a consultation location and booking channel.</p>{button('Find a Consultation')}<a class="text-link" href="patient-information.html">Prepare for your visit {icon('arrow')}</a></div><figure class="home-lifestyle">{photo}</figure></div></div></section>'''
