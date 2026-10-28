"""Bilingual article taxonomy, listing controls and independent reading pages."""

from datetime import date
from html import escape
import json
from pathlib import Path
from urllib.parse import urlsplit

from reading_content import render_blocks, reading_url, resolve_content_url, safe_language

ROOT = Path(__file__).resolve().parents[1]
TAXONOMY = json.loads((ROOT / 'content/article-taxonomy.json').read_text(encoding='utf-8'))
TEXT = {
    'en': {
        'articles': 'Articles', 'home': 'Home', 'read': 'Read article', 'guide': 'Topic guide',
        'draft': 'Educational draft', 'pending': 'Clinical review pending', 'reviewed': 'Reviewed information',
        'recorded': 'Clinical review recorded', 'author': 'Author', 'reviewer': 'Reviewed by',
        'contents': 'On this page', 'navigation': 'Reading navigation', 'return': 'Back to articles',
        'related': 'Related reading', 'continue': 'CONTINUE READING', 'links': 'Further reading',
        'scope': 'Service scope awaiting confirmation',
        'note': 'This educational draft is awaiting clinical review. Discuss treatment options and availability at your consultation.',
        'choose': 'Explore children’s topics', 'guide_intro': 'Choose a topic to read more, or continue through the overview below.',
        'consultation': 'Find a consultation', 'consultation_intro': 'Choose a location and explore the available booking options.',
        'next': 'YOUR NEXT STEP', 'cta': 'Discuss your questions at a consultation.',
        'several': 'Several body regions',
    },
    'si': {
        'articles': 'ලිපි', 'home': 'මුල් පිටුව', 'read': 'ලිපිය කියවන්න', 'guide': 'මාතෘකා මඟපෙන්වීම',
        'draft': 'අධ්‍යාපනික කෙටුම්පත', 'pending': 'වෛද්‍ය සමාලෝචනය අපේක්ෂිතයි', 'reviewed': 'සමාලෝචිත තොරතුරු',
        'recorded': 'වෛද්‍ය සමාලෝචනය සටහන් කර ඇත', 'author': 'කර්තෘ', 'reviewer': 'සමාලෝචනය කළේ',
        'contents': 'මෙම ලිපියේ අන්තර්ගතය', 'navigation': 'ලිපිය තුළ සැරිසැරීම', 'return': 'ලිපි ලැයිස්තුවට ආපසු',
        'related': 'ආශ්‍රිත කියවීම්', 'continue': 'තවදුරටත් කියවන්න', 'links': 'වැඩිදුර කියවීම්',
        'scope': 'ප්‍රතිකාර සේවා තහවුරු කළ යුතුය',
        'note': 'මෙම අධ්‍යාපනික කෙටුම්පත වෛද්‍ය සමාලෝචනය අපේක්ෂාවෙන් පවතී. ප්‍රතිකාර විකල්ප සහ ඒවා ලබා ගත හැකි ආකාරය ඔබේ වෛද්‍ය හමුවේදී සාකච්ඡා කරන්න.',
        'choose': 'ළමා මාතෘකාවක් තෝරන්න', 'guide_intro': 'වැඩිදුර කියවීමට මාතෘකාවක් තෝරන්න, නැතහොත් පහත දළ විස්තරය කියවන්න.',
        'consultation': 'වෛද්‍ය හමුවක් සොයන්න', 'consultation_intro': 'ස්ථානයක් තෝරා වෙන් කරවා ගැනීමේ විකල්ප බලන්න.',
        'next': 'ඔබේ ඊළඟ පියවර', 'cta': 'ඔබේ ප්‍රශ්න වෛද්‍ය හමුවකදී සාකච්ඡා කරන්න.',
        'several': 'ශරීරයේ ප්‍රදේශ කිහිපයක්',
    },
}


def e(value):
    return escape(str(value), quote=True)


def label(group, key, language='en'):
    return TAXONOMY[group][key][language]


def validate_articles(items):
    known = {item['id'] for item in items}
    if len(known) != len(items):
        raise ValueError('Article IDs must be unique')
    for item in items:
        if item.get('lang') not in TEXT:
            raise ValueError(f'Article language must be en or si: {item["id"]}')
        for group in ('audiences', 'body_regions', 'topics'):
            values = item.get(group)
            if not isinstance(values, list) or not values or len(values) != len(set(values)) or any(value not in TAXONOMY[group] for value in values):
                raise ValueError(f'Invalid {group}: {item["id"]}')
        if any(slug not in known or slug == item['id'] for slug in item.get('guide_items', [])):
            raise ValueError(f'Invalid topic-guide destination: {item["id"]}')


def article_filters(items):
    def options(group, values):
        return ''.join(f'<option value="{e(key)}">{e(label(group, key))} / {e(label(group, key, "si"))}</option>' for key in TAXONOMY[group] if key in values)

    regions = {key for item in items for key in item['body_regions']}
    topics = {key for item in items for key in item['topics']}
    languages = [('all', 'All languages', 'en'), ('si', 'සිංහල', 'si'), ('en', 'English', 'en')]
    choices = ''.join(f'<label class="language-choice" for="article-language-{value}" lang="{language}"><input id="article-language-{value}" type="radio" name="lang" value="{value}"{" checked" if value == "all" else ""}><span>{text}</span></label>' for value, text, language in languages)
    return f'''<form class="article-controls" id="article-filters" role="search" aria-label="Find articles" data-article-form>
<fieldset class="article-languages"><legend>Language / <span lang="si">භාෂාව</span></legend><div class="language-options">{choices}</div></fieldset>
<div class="article-filter-fields"><div class="field article-search"><label for="article-search">Search articles / <span lang="si">ලිපි සොයන්න</span></label><input id="article-search" name="q" type="search" maxlength="160" placeholder="Topic or keyword · මාතෘකාව හෝ වචනය" data-article-search></div>
<div class="field"><label for="article-audience">Audience / <span lang="si">පාඨක කාණ්ඩය</span></label><select id="article-audience" name="audience"><option value="all">All audiences / සියලු දෙනා</option>{options('audiences', TAXONOMY['audiences'])}</select></div>
<div class="field"><label for="article-region">Body region / <span lang="si">ශරීර ප්‍රදේශය</span></label><select id="article-region" name="region"><option value="all">All regions / සියලු ප්‍රදේශ</option>{options('body_regions', regions)}</select></div>
<div class="field"><label for="article-topic">Topic / <span lang="si">මාතෘකාව</span></label><select id="article-topic" name="topic"><option value="all">All topics / සියලු මාතෘකා</option>{options('topics', topics)}</select></div>
<button class="button button-outline" type="reset">Reset filters / <span lang="si">යළි සකසන්න</span></button></div></form>
<p class="results-count" aria-live="polite" aria-atomic="true" data-article-count>{len(items)} articles · {sum(i['lang'] == 'en' for i in items)} English · <span lang="si">{sum(i['lang'] == 'si' for i in items)} සිංහල</span></p>
<noscript><p>All articles are listed below. Open any article to read it. / <span lang="si">සියලු ලිපි පහතින් ඇත. කියවීමට ලිපියක් තෝරන්න.</span></p></noscript>'''


def article_card(item, icon, listing=False, context_language='en'):
    language = item['lang']
    text = TEXT[language]
    url = reading_url('articles', item)
    status = text['draft'] if item['status'] == 'draft' else text['reviewed']
    badges = f'<span class="article-chip" lang="{language}">{"සිංහල" if language == "si" else "English"}</span>'
    badges += ''.join(f'<span class="article-chip">{e(label("audiences", key, language))}</span>' for key in item['audiences'])
    if item.get('format') == 'guide':
        badges += f'<span class="article-chip article-chip-guide">{e(text["guide"])}</span>'
    region_names = [label('body_regions', key, language) for key in item['body_regions']]
    region = ', '.join(region_names) if len(region_names) <= 2 else text['several']
    search_terms = [item['title'], item['summary'], item['category'], *item.get('keywords', [])]
    for group in ('audiences', 'body_regions', 'topics'):
        search_terms.extend(label(group, key, lang) for key in item[group] for lang in ('en', 'si'))
    attrs = ''
    if listing:
        attrs = f' id="{e(item["id"])}" data-reading-url="{e(url)}" data-language="{language}" data-audiences="{e(json.dumps(item["audiences"]))}" data-regions="{e(json.dumps(item["body_regions"]))}" data-topics="{e(json.dumps(item["topics"]))}" data-search="{e(" ".join(search_terms))}"'
    return f'''<article class="topic-card reading-card article-library-card{" filterable-item" if listing else ""}" lang="{language}"{attrs}><div class="topic-card-top">{icon(item['icon'], 'condition-icon')}<span class="topic-status">{e(status)}</span></div><div class="article-badges">{badges}</div><p class="eyebrow">{e(item['category'])}</p><h3><a href="{e(url)}" data-article-link>{e(item['title'])}</a></h3><p>{e(item['summary'])}</p><p class="article-region" title="{e(', '.join(region_names))}">{e(region)}</p><a class="text-link reading-card-link" href="{e(url)}" data-article-link aria-label="{e(text['read'])}: {e(item['title'])}">{e(text['read'])} {icon('arrow')}</a></article>'''


def article_listing(items, icon):
    # Interleave independent collections so the initial mixed view introduces
    # both languages. Position does not imply a translation relationship.
    english = [item for item in items if item['lang'] == 'en']
    sinhala = [item for item in items if item['lang'] == 'si']
    ordered = [group[index] for index in range(max(len(english), len(sinhala))) for group in (english, sinhala) if index < len(group)]
    cards = ''.join(article_card(item, icon, listing=True) for item in ordered)
    return f'''<section class="section"><div class="container" data-article-library><div class="section-heading"><div><p class="eyebrow">ORTHOPAEDIC READING</p><h2>Find an article / <span lang="si">ලිපියක් තෝරන්න</span></h2><p class="section-intro">Explore independent Sinhala and English articles for adults and children. Choose a language, body region or topic to narrow the collection.</p><p class="article-draft-label">Draft educational information. Clinical review pending. / <span lang="si">අධ්‍යාපනික කෙටුම්පත්. වෛද්‍ය සමාලෝචනය අපේක්ෂිතයි.</span></p></div></div>{article_filters(items)}<div class="grid grid-three topic-grid" data-article-grid>{cards}</div><div class="empty-state" data-article-empty hidden><h3>No matching articles / <span lang="si">ගැළපෙන ලිපි නොමැත</span></h3><p>Try another keyword or reset your filters. / <span lang="si">වෙනත් වචනයක් සොයන්න හෝ පෙරහන් යළි සකසන්න.</span></p><button class="button button-outline" type="button" data-article-reset>Reset filters / <span lang="si">යළි සකසන්න</span></button></div></div></section>'''


def article_reading_page(item, data, icon, card):
    language = item['lang']
    text = TEXT[language]
    is_draft = item['status'] == 'draft'
    status = text['draft'] if is_draft else text['reviewed']
    metadata = f'<span class="status-tag">{e(status)}</span><span>{e(text["pending"] if is_draft else text["recorded"])}</span>'
    metadata += f'<span class="article-chip">{"සිංහල" if language == "si" else "English"}</span>'
    metadata += ''.join(f'<span class="article-chip">{e(label("audiences", key, language))}</span>' for key in item['audiences'])
    if item.get('author'):
        metadata += f'<span>{e(text["author"])}: {e(item["author"])}</span>'
    if not is_draft:
        date.fromisoformat(item['reviewed_on'])
        metadata += f'<span>{e(text["reviewer"])}: {e(item["reviewed_by"])} · <time datetime="{e(item["reviewed_on"])}">{e(item["reviewed_on"])}</time></span>'
    if item.get('pending'):
        metadata += f'<span>{e(text["scope"])}</span>'
    contents = []
    sections = []
    if item.get('guide_items'):
        guide_records = [next(i for i in data['articles'] if i['id'] == slug) for slug in item['guide_items']]
        entries = ''.join(f'<li><a href="{e(reading_url("articles", record))}" data-article-link>{e(record["title"])} {icon("arrow")}</a></li>' for record in guide_records)
        sections.append(f'<section class="reading-section article-topic-guide" id="reading-topic-guide" tabindex="-1"><h2>{e(text["choose"])}</h2><p>{e(text["guide_intro"])}</p><ul>{entries}</ul></section>')
        contents.append(f'<li><a data-reading-toc-link href="#reading-topic-guide">{e(text["choose"])}</a></li>')
    for section in item['sections']:
        target = 'reading-' + section['id']
        section_language = safe_language(section.get('lang', language))
        sublinks = ''.join(f'<li><a data-reading-toc-link lang="{e(b.get("lang", section_language))}" href="#reading-{e(b["id"])}">{e(b["text"])}</a></li>' for b in section['blocks'] if b['type'] == 'heading')
        sublist = f'<ol>{sublinks}</ol>' if sublinks else ''
        contents.append(f'<li><a data-reading-toc-link lang="{section_language}" href="#{e(target)}">{e(section["heading"])}</a>{sublist}</li>')
        sections.append(f'<section class="reading-section" id="{e(target)}" tabindex="-1" lang="{section_language}"><h2>{e(section["heading"])}</h2>{render_blocks(section["blocks"], ROOT)}</section>')
    related = [(r['kind'], next(i for i in data[r['kind']] if i['id'] == r['id'])) for r in item.get('related_items', [])]
    related.sort(key=lambda record: record[1].get('lang', 'en') != language)
    # Archive metadata is internal provenance. Readers get the complete local
    # article and its images, without an external link to the archived website.
    references = item.get('references', [])
    links = []
    for reference in references:
        if urlsplit(reference['url']).scheme != 'https':
            raise ValueError('Article references must use HTTPS')
        links.append(f'<li><a href="{e(reference["url"])}" lang="{e(reference.get("lang", "en"))}" target="_blank" rel="noopener noreferrer">{e(reference["label"])} {icon("external")}</a></li>')
    if item.get('related') and resolve_content_url(item['related'], data) not in {reading_url(k, r) for k, r in related}:
        links.append(f'<li><a href="{e(item["related"])}" lang="en">{e(item["relatedLabel"])} {icon("arrow")}</a></li>')
    if links:
        contents.append(f'<li><a data-reading-toc-link href="#reading-further-reading">{e(text["links"])}</a></li>')
        sections.append(f'<section class="reading-section reading-references" id="reading-further-reading" tabindex="-1"><h2>{e(text["links"])}</h2><ul>{"".join(links)}</ul></section>')
    default_return = 'articles.html?lang=' + language
    breadcrumbs = f'<nav class="breadcrumbs" aria-label="{"Breadcrumb" if language == "en" else "පිටු මඟ"}"><a href="index.html">{e(text["home"])}</a><span aria-hidden="true">/</span><a href="{default_return}" data-article-return>{e(text["articles"])}</a><span aria-hidden="true">/</span><span aria-current="page">{e(item["title"])}</span></nav>'
    note = f'<aside class="article-draft-note"><p>{e(text["note"])}</p></aside>' if item.get('archive') and is_draft else ''
    heading = f'<header class="reading-header" lang="{language}"><div class="container">{breadcrumbs}<p class="eyebrow">{e(item["category"])}</p><h1 id="reading-title">{e(item["title"])}</h1><p class="reading-intro">{e(item["summary"])}</p><div class="reading-meta">{metadata}</div>{note}</div></header>'
    sidebar = f'<aside class="reading-sidebar" aria-label="{e(text["navigation"])}" lang="{language}"><details class="reading-contents" data-reading-contents open><summary>{e(text["contents"])} {icon("plus", "disclosure-icon")}</summary><nav aria-label="{e(text["contents"])}"><ol>{"".join(contents)}</ol></nav></details><div class="reading-consultation">{icon("calendar", "icon-large")}<h2>{e(text["consultation"])}</h2><p>{e(text["consultation_intro"])}</p><a class="button button-primary" href="clinics.html">{e(text["consultation"])} {icon("arrow")}</a></div></aside>'
    # Existing stock lead images are rendered by the shared generator callback;
    # archive images remain in their original inline positions.
    figure = item.get('_lead_figure', '')
    article = f'<article class="reading-article" aria-labelledby="reading-title" lang="{language}">{figure}{"".join(sections)}<div class="reading-return"><a class="text-link" href="{default_return}" data-article-return>← {e(text["return"])}</a></div></article>'
    related_html = ''
    if related:
        cards = ''.join(card(record, kind, context_language=language) for kind, record in related)
        columns = 'grid-two' if len(related) == 2 else 'grid-three' if len(related) >= 3 else 'reading-related-single'
        related_html = f'<section class="section section-soft" lang="{language}"><div class="container"><div class="section-heading"><div><p class="eyebrow">{e(text["continue"])}</p><h2>{e(text["related"])}</h2></div></div><div class="grid {columns}">{cards}</div></div></section>'
    cta = f'<section class="section section-soft" lang="{language}"><div class="container"><div class="cta-band"><div><p class="eyebrow">{e(text["next"])}</p><h2>{e(text["cta"])}</h2><p>{e(text["consultation_intro"])}</p></div><a class="button button-primary" href="clinics.html">{e(text["consultation"])} {icon("arrow")}</a></div></div></section>'
    return heading + f'<div class="container reading-layout">{sidebar}{article}</div>' + related_html + cta
