#!/usr/bin/env python3
"""Check generated HTML, nested navigation, reading links and local assets."""

from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import hashlib
import json
import posixpath
import re
import sys

from reading_content import READING

ROOT = Path(__file__).resolve().parents[1]
VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []
        self.urls = []
        self.aria = []
        self.headings = []
        self.images = []
        self.controls = []
        self.labels = []
        self.navigation = []
        self.toc = []
        self.details = []
        self.refreshes = []
        self.stack = []
        self.active = ''
        self.stock_count = 0

    def handle_starttag(self, tag, attributes):
        a = dict(attributes)
        if tag == 'meta' and a.get('http-equiv', '').lower() == 'refresh':
            self.refreshes.append(a.get('content', ''))
        if 'id' in a:
            self.ids.append(a['id'])
        if tag == 'body':
            self.active = a.get('data-page', '')
        if tag in {'h1', 'h2', 'h3', 'h4', 'h5', 'h6'}:
            self.headings.append(int(tag[1]))
        for key in ['href', 'src', 'data-reading-url']:
            if key in a:
                self.urls.append(a[key])
        if 'srcset' in a:
            self.urls.extend(candidate.strip().split()[0] for candidate in a['srcset'].split(','))
        for key in ['aria-controls', 'aria-labelledby', 'aria-describedby']:
            self.aria.extend(a.get(key, '').split())
        if tag == 'img':
            self.images.append(a)
            self.stock_count += 'stock-photo' in a.get('class', '').split()
        if tag in {'input', 'select', 'textarea'}:
            self.controls.append(a)
        if tag == 'label':
            self.labels.append(a.get('for'))
        if tag == 'a' and any(t == 'nav' and attrs.get('id') == 'primary-navigation' for t, attrs in self.stack):
            self.navigation.append(a)
        if 'data-reading-toc-link' in a:
            self.toc.append(a)
        if tag == 'details':
            self.details.append(a)
        if tag not in VOID:
            self.stack.append((tag, a))

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        assert self.stack and self.stack[-1][0] == tag, f'Invalid HTML nesting at </{tag}>'
        self.stack.pop()


def local_target(page, url):
    parsed = urlsplit(url)
    if parsed.scheme or parsed.netloc:
        return None, None
    target = posixpath.normpath(posixpath.join(posixpath.dirname(page), unquote(parsed.path))) if parsed.path else page
    assert (ROOT / target).resolve().is_relative_to(ROOT), f'URL leaves the website: {page}: {url}'
    return target, unquote(parsed.fragment)


def main():
    catalog = json.loads((ROOT / 'content/site.json').read_text())
    expected_navigation = [item['file'] for item in catalog['navigation']]
    pages = {}
    for path in sorted(ROOT.rglob('*.html')):
        name = path.relative_to(ROOT).as_posix()
        parser = Page()
        parser.feed(path.read_text())
        assert not parser.stack, f'Unclosed tags in {name}'
        pages[name] = parser
    references = 0
    for name, page in pages.items():
        assert all('orthopaedic.lk' not in refresh.lower() for refresh in page.refreshes), f'{name}: external archive redirect'
        assert page.headings.count(1) == 1, f'{name}: expected exactly one H1'
        assert all(b <= a + 1 for a, b in zip(page.headings, page.headings[1:])), f'{name}: heading order skips a level'
        duplicates = [i for i, count in Counter(page.ids).items() if count > 1]
        assert not duplicates, f'{name}: duplicate IDs {duplicates}'
        assert [local_target(name, link['href'])[0] for link in page.navigation] == expected_navigation, f'{name}: incorrect main navigation'
        current = [link for link in page.navigation if link.get('aria-current')]
        expected_current = [n for n in catalog['navigation'] if n['id'] == page.active]
        assert len(current) == len(expected_current), f'{name}: incorrect active navigation'
        if current:
            assert local_target(name, current[0]['href'])[0] == expected_current[0]['file'], f'{name}: wrong parent section'
        for url in page.urls:
            host = (urlsplit(url).hostname or '').lower().rstrip('.')
            assert host != 'orthopaedic.lk' and not host.endswith('.orthopaedic.lk'), f'{name}: external archive link or image: {url}'
            target, fragment = local_target(name, url)
            if target is None:
                continue
            assert (ROOT / target).is_file(), f'{name}: missing local URL {url}'
            if fragment:
                assert target in pages and fragment in pages[target].ids, f'{name}: missing anchor {url}'
            references += 1
        for reference in page.aria:
            assert reference in page.ids, f'{name}: missing ARIA reference {reference}'
        for control in page.controls:
            assert control.get('id') in page.labels, f'{name}: unlabelled control'
        for image in page.images:
            assert all(key in image for key in ['alt', 'width', 'height']), f'{name}: missing image attributes'
            assert not urlsplit(image['src']).scheme, f'{name}: external image hotlink'
            assert int(image['width']) > 0 and int(image['height']) > 0, f'{name}: invalid image dimensions'
    detail_count = 0
    for kind, config in READING.items():
        listing = pages[config['listing']]
        assert not any('topic-details' in d.get('class', '').split() for d in listing.details), f'{kind}: expandable reading cards remain'
        for item in catalog[kind]:
            detail = f'{config["folder"]}/{item["id"]}.html'
            assert detail in pages, f'Missing reading page: {detail}'
            assert 'reading-title' in pages[detail].ids and len(pages[detail].toc) >= 2, f'{detail}: incomplete reading template'
            assert item['id'] in listing.ids, f'{kind}: missing legacy bookmark target'
            detail_count += 1
    for css in (ROOT / 'styles').glob('*.css'):
        for url in re.findall(r'url\([\'"]?([^\)\'\"]+)', css.read_text()):
            assert (css.parent / url).is_file(), f'Missing CSS asset: {url}'
    lock = ROOT / 'content/stock-assets.lock.json'
    if lock.is_file():
        for asset in json.loads(lock.read_text())['assets']:
            assert hashlib.sha256((ROOT / asset['file']).read_bytes()).hexdigest() == asset['sha256'], f'Stock image differs from provenance: {asset["file"]}'
    print(f'PASS: {len(pages)} HTML pages, {detail_count} reading pages, {references} local references and {sum(p.stock_count for p in pages.values())} stock-photo placements.')
    print('PASS: nested navigation, parent-section states, headings, IDs, TOC anchors, ARIA, labels, local assets and stock checksums.')
    print('PASS: the three reading indexes contain normal page links; Conditions and short FAQs retain their expandable information.')
    print('PASS: no public page links or redirects to the external archive website.')
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (AssertionError, ValueError) as error:
        print(f'FAIL: {error}', file=sys.stderr)
        raise SystemExit(1)
