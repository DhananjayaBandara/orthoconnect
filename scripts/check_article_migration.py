#!/usr/bin/env python3
"""Check archive conservation independently of the importer, using stdlib only."""

import argparse
from collections import Counter
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re

from article_library import validate_articles

ROOT = Path(__file__).resolve().parents[1]
IMAGE = re.compile(r'!\[[^\]]*\]\(([^\s)]+)(?:\s+"[^"]*")?\)')


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compact(text):
    # Preserve every non-whitespace Unicode character, without transliteration.
    return ''.join(text.split())


def source_stream(path, events):
    raw = path.read_text(encoding='utf-8').split('\n---', 1)[1]
    raw = re.sub(r'^\s*# [^\n]+\n', '', raw, count=1)
    raw = re.sub(r'^\*\*Original source:\*\*[^\n]+\n?', '', raw, flags=re.M)
    raw = re.sub(r'^> Archival copy[^\n]+\n?', '', raw, flags=re.M)
    for event in events:
        reason = event['reason']
        if reason == 'gallery-formatting':
            continue
        omitted = event['text']
        assert omitted in raw, f'Logged omission not in source: {path}'
        if reason == 'placeholder':
            assert 'lorem ipsum' in omitted.lower()
        elif reason == 'legacy-enquiry-prompt':
            assert re.fullmatch(r'(?:My|Your) Problem Is Not Listed\s*\??|Please send us your (?:inquery|problem)\.?|Please contact us\.?', omitted, re.I)
        else:
            assert reason == 'formatting-separator' and re.fullmatch('-{3,}', omitted)
        raw = raw.replace(omitted, '', 1)
    hashes = []

    def image_token(match):
        digest = sha((path.parent / match[1]).resolve())
        hashes.append(digest)
        return f'IMAGE[{digest}]'

    raw = IMAGE.sub(image_token, raw)
    # Remove only Markdown structure, retaining the complete text/image stream.
    raw = re.sub(r'^\s*- \[(IMAGE\[[a-f0-9]+\])\]\(https://[^)]+\)', r'\1', raw, flags=re.M)
    raw = re.sub(r'^#{2,6}\s+', '', raw, flags=re.M)
    raw = re.sub(r'^\d+\.\s+', '', raw, flags=re.M)
    return compact(raw), hashes


def imported_stream(item):
    text = []
    hashes = []
    for section in item['sections']:
        if section['id'] != 'overview':
            text.append(section['heading'])
        for block in section['blocks']:
            if block['type'] in {'paragraph', 'heading'}:
                text.append(block['text'])
            elif block['type'] == 'list':
                text.extend(block['items'])
            elif block['type'] == 'image':
                digest = sha(ROOT / block['src'])
                hashes.append(digest)
                text.append(f'IMAGE[{digest}]')
                assert len(block['alt']) >= 8 and not block['alt'].isdigit() and block.get('lang') == 'en', 'Image description/language missing'
            else:
                raise AssertionError(f'Unexpected migrated block: {block["type"]}')
    return compact(''.join(text)), hashes


class ArticleHTML(HTMLParser):
    def __init__(self, filename=None, section_ids=()):
        super().__init__()
        self.language = None
        self.robots = ''
        self.cards = []
        self.returns = []
        self.guide_links = 0
        self.has_guide = False
        self.in_guide = False
        self.filename = filename
        self.section_ids = set(section_ids)
        self.seen_sections = set()
        self.body_stream = []
        self.capture_section = None
        self.skip_overview_heading = False

    def handle_starttag(self, tag, attributes):
        a = dict(attributes)
        if tag == 'section' and a.get('id') in self.section_ids:
            self.capture_section = a['id']
            self.seen_sections.add(a['id'])
        if tag == 'h2' and self.capture_section == 'reading-overview':
            self.skip_overview_heading = True
        if tag == 'img' and self.capture_section:
            path = (ROOT / self.filename).parent / a['src']
            self.body_stream.append(f'IMAGE[{sha(path)}]')
        if tag == 'html':
            self.language = a.get('lang')
        if tag == 'meta' and a.get('name') == 'robots':
            self.robots = a['content']
        if tag == 'article' and 'filterable-item' in a.get('class', '').split():
            self.cards.append(a)
        if 'data-article-return' in a:
            self.returns.append(a)
        if tag == 'section' and a.get('id') == 'reading-topic-guide':
            self.has_guide = self.in_guide = True
        if self.in_guide and 'data-article-link' in a:
            self.guide_links += 1

    def handle_endtag(self, tag):
        if tag == 'h2':
            self.skip_overview_heading = False
        if tag == 'section':
            self.in_guide = False
            self.capture_section = None

    def handle_data(self, data):
        if self.capture_section and not self.skip_overview_heading:
            self.body_stream.append(data)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive', nargs='?', type=Path, default=ROOT.parent / 'orthopaedic-lk-content-archive-toolkit')
    archive = parser.parse_args().archive
    evidence = read(ROOT / 'content/article-migration.json')
    manifest = read(archive / 'manifest.json')
    assert sha(archive / 'manifest.json') == evidence['archive_manifest_sha256'], 'Archive manifest changed'
    assert sha(archive / 'ALL-ARTICLES.md') == evidence['combined_archive_sha256'], 'Combined archive changed'
    assert len(evidence['articles']) == len(manifest) == 40
    assert {r['source_id'] for r in evidence['articles']} == {r['id'] for r in manifest}
    site = read(ROOT / 'content/site.json')
    items = [read(ROOT / row['content']) for row in site['articles']]
    validate_articles(items)
    assert len(items) == 40 and Counter(i['lang'] for i in items) == {'en': 19, 'si': 21}
    by_id = {item['id']: item for item in items}
    images = []
    for record in evidence['articles']:
        item = by_id[record['id']]
        path = archive / record['source_file']
        assert sha(path) == record['source_sha256'] == item['archive']['sha256'], f'Archive text changed: {path}'
        assert item['status'] == 'draft' and not any(item.get(key) for key in ('author', 'reviewed_by', 'reviewed_on'))
        events = [e for e in evidence['events'] if e['source_id'] == record['source_id']]
        source_text, source_images = source_stream(path, events)
        target_text, target_images = imported_stream(item)
        if source_text != target_text:
            position = next((i for i, (a, b) in enumerate(zip(source_text, target_text)) if a != b), min(len(source_text), len(target_text)))
            raise AssertionError(f'{record["source_id"]}: content/order differs at {position}: source={source_text[max(0, position-40):position+80]!r}; target={target_text[max(0, position-40):position+80]!r}')
        assert source_images == target_images, f'Image order differs: {record["source_id"]}'
        images.extend(target_images)
        section_ids = {'reading-' + section['id'] for section in item['sections']}
        page = ArticleHTML(record['destination'], section_ids)
        html = (ROOT / record['destination']).read_text(encoding='utf-8')
        page.feed(html)
        assert page.seen_sections == section_ids, f'Generated page is missing article sections: {record["source_id"]}'
        assert compact(''.join(page.body_stream)) == target_text, f'Generated page is missing full text/images or changes their order: {record["source_id"]}'
        assert not re.search(r'>\s*(?:Original article|මුල් ලිපිය)\s*<', html), f'External original-article label remains: {record["source_id"]}'
        assert page.language == item['lang'] and 'noindex' in page.robots
        assert len(page.returns) == 2
        if item['lang'] == 'si':
            assert 'මෙම ලිපියේ අන්තර්ගතය' in html and 'ලිපි ලැයිස්තුවට ආපසු' in html
            assert 'noto-sans-sinhala-regular.ttf' in html
        if item.get('format') == 'guide':
            assert len(item['guide_items']) == page.guide_links == 11 and page.has_guide
    assert len(images) == 390 and len(set(images)) == 251
    source_lists = {
        'en-children-shoulder': [(1, 3), (1, 7)],
        'en-children-upper-arm': [(1, 3), (1, 2), (3, 2), (1, 7), (1, 7)],
        'si-adult-osteoporosis': [(1, 4)],
    }
    for slug, expected_lists in source_lists.items():
        lists = [b for section in by_id[slug]['sections'] for b in section['blocks'] if b['type'] == 'list']
        assert [(b.get('start', 1), len(b['items'])) for b in lists] == expected_lists, f'Original list groups/numbering lost: {slug}'
    assets = read(ROOT / 'content/article-assets.json')['assets']
    assert {a['sha256'] for a in assets} == set(images)
    for asset in assets:
        assert sha(ROOT / asset['file']) == asset['sha256']
        assert asset['sources'], f'Missing image provenance: {asset["file"]}'
        for source in asset['sources']:
            assert sha(archive / source['archive_file']) == asset['sha256']
    retired = set(evidence['retired_articles'])
    assert len(retired) == 5 and retired == set(site['retired_articles'])
    assert not retired & set(by_id)
    assert {p.stem for p in (ROOT / 'content/articles').glob('*.json')} == set(by_id), 'Unlisted or dummy article sources remain'
    assert {p.stem for p in (ROOT / 'articles').glob('*.html')} == set(by_id), 'Unlisted or dummy article pages remain'
    for slug in retired:
        assert not (ROOT / 'articles' / (slug + '.html')).exists()
        assert not (ROOT / 'content/articles' / (slug + '.json')).exists()
        assert not any(slug in page.read_text(encoding='utf-8') for page in ROOT.rglob('*.html')), f'Dummy article reference remains: {slug}'
    listing = ArticleHTML()
    listing.feed((ROOT / 'articles.html').read_text(encoding='utf-8'))
    assert len(listing.cards) == 40
    for card in listing.cards:
        item = by_id[card['id']]
        assert card['lang'] == card['data-language'] == item['lang']
        assert json.loads(card['data-audiences']) == item['audiences']
        assert json.loads(card['data-regions']) == item['body_regions']
        assert json.loads(card['data-topics']) == item['topics']
    report = (ROOT / 'docs/article-migration-review.md').read_text(encoding='utf-8')
    assert all(record['source_id'] in report and record['destination'] in report for record in evidence['articles'])
    print('PASS: all 40 sources retain their substantive Unicode text, headings, list contents and image positions/order, allowing only logged omissions.')
    print('PASS: all 40 generated reading pages contain the full article text and local images in their original order.')
    print('PASS: exactly 40 classified articles (19 English, 21 Sinhala), 390 image placements, 251 original image checksums/provenance records; all five dummy articles and their links removed.')
    print('PASS: draft/noindex states, no invented bylines/reviews, Sinhala reading controls/fonts, 11 guide links and complete migration inventory.')


if __name__ == '__main__':
    main()
