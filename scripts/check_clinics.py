#!/usr/bin/env python3
"""Check the public directory against the supplied doctor/hospital booking report."""

from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, parse_qs
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT.parent / 'Dr_Suneth_De_Silva_Unified_Link_Verifier/VERIFICATION_RESULTS.json'


class Clinics(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.cards = []
        self.card = None
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'article' and 'clinic-card' in attrs.get('class', '').split():
            self.card = {'id': attrs['id'], 'links': []}
            self.cards.append(self.card)
        if self.card is not None and tag == 'a' and 'data-booking-provider' in attrs:
            self.card['links'].append(attrs)

    def handle_endtag(self, tag):
        if tag == 'article':
            self.card = None


def main():
    data = json.loads((ROOT / 'content/site.json').read_text())
    records = data['clinics']
    assert len(records) == 18, 'Expected all 18 supplied centres; sample clinics must be removed'
    assert len({c['id'] for c in records}) == len(records), 'Clinic IDs must be unique'
    assert all('Sample' not in c['name'] for c in records), 'Sample clinic remains'
    assert not any('day' in c or 'time' in c or 'address' in c for c in records), 'Unsupported sample schedules/addresses remain'
    reference = json.loads(REFERENCE.read_text()) if REFERENCE.exists() else None
    if reference:
        source = {c['name']: c for c in reference['locations']}
        assert {c['source_name'] for c in records} == set(source), 'Centres differ from supplied report'
        assert data['clinic_directory']['source_sha256'] == hashlib.sha256(REFERENCE.read_bytes()).hexdigest()
        for clinic in records:
            for provider in ('echannelling', 'doc990'):
                expected = source[clinic['source_name']].get(f'{provider}_url')
                actual = clinic['booking_links'].get(provider, {}).get('url')
                assert actual == expected, f'Wrong {provider} destination for {clinic["source_name"]}'
            assert clinic['location'] == (source[clinic['source_name']]['location'] if source[clinic['source_name']]['location'] not in {'Not verified', 'Location unverified'} else None)
    for filename in ('clinics.html', 'hospitals.html', 'index.html', 'contact.html'):
        page = Clinics((ROOT / filename).read_text())
        expected = records if filename in {'clinics.html', 'hospitals.html'} else [next(c for c in records if c['id'] == cid) for cid in data['clinic_directory']['featured_ids']]
        assert [c['id'] for c in page.cards] == [f'clinic-{c["id"]}' for c in expected], f'{filename}: missing, duplicated or incorrectly ordered clinics'
        for card, record in zip(page.cards, expected):
            assert {a['data-booking-provider']: a['href'] for a in card['links']} == {p: link['url'] for p, link in record['booking_links'].items()}, f'{filename}: incorrect platform buttons'
            for link in card['links']:
                assert link.get('target', '_self') == '_self', 'Booking must use normal same-tab navigation'
                assert record['name'] in link.get('aria-label', ''), 'Accessible booking name must identify clinic'
                url = urlsplit(link['href'])
                assert url.scheme == 'https'
                if link['data-booking-provider'] == 'echannelling':
                    assert url.hostname == 'www.echannelling.com'
                    assert url.path == '/doctor-search/D10651/sessions'
                    query = parse_qs(url.query)
                    assert query['doctorId'] == ['D10651']
                    assert query['hospitalCode'] == [record['booking_links']['echannelling']['hospital_code']]
                else:
                    assert url.hostname == 'www.doc.lk'
                    assert re.fullmatch(r'/(?:si/|tm/)?channel/' + re.escape(record['booking_links']['doc990']['channel_id']), url.path)
    combinations = Counter(tuple(c['booking_links']) for c in records)
    assert combinations == {('echannelling', 'doc990'): 8, ('echannelling',): 5, ('doc990',): 5}
    for path in ROOT.rglob('*.html'):
        html = path.read_text()
        assert not re.search(r'Sample Consultation|SAMPLE CLINIC|Sample consultation details|design preview|booking-channel demonstration|enquiry preview|appointments@example\.invalid|\+94 XX|Illustrative weekly|preview only|dummy data', html, re.I), f'{path}: prototype content remains'
        assert not re.search(r'<dialog\b|data-contact=|data-enquiry=|data-booking=', html), f'{path}: inert prototype controls remain'
    assert (ROOT / 'hospitals.html').read_bytes() == (ROOT / 'clinics.html').read_bytes(), 'Legacy directory must match'
    print('PASS: 18 real centres, 26 hospital-specific booking links; correct platform buttons on directory, alias, home and contact.')
    print('PASS: no sample clinics, fake schedules, placeholder contacts or demonstration dialogs in generated pages.')
    print('PASS: exact destinations match the supplied verification report.' if reference else 'NOTE: original verification report unavailable; exact external-source comparison skipped.')


if __name__ == '__main__':
    main()
