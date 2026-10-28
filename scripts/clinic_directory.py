"""Validate the maintained clinic directory before generating any public pages."""

from datetime import datetime, timezone
import re
from urllib.parse import parse_qs, urlsplit

PROVIDERS = {'echannelling': 'eChannelling', 'doc990': 'Doc990'}


def validate_clinics(clinics, directory):
    ids = set()
    for clinic in clinics:
        cid = clinic['id']
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', cid) or cid in ids:
            raise ValueError(f'Invalid or duplicate clinic ID: {cid}')
        ids.add(cid)
        if not clinic['name'].strip() or not clinic['source_name'].strip():
            raise ValueError(f'Clinic name/source missing: {cid}')
        if clinic['location'] is not None and not clinic['location'].strip():
            raise ValueError(f'Clinic location must be a known locality or null: {cid}')
        links = clinic['booking_links']
        if not links or set(links) - PROVIDERS.keys():
            raise ValueError(f'Clinic needs a supported booking provider: {cid}')
        for provider, link in links.items():
            url = urlsplit(link['url'])
            if url.scheme != 'https' or url.username or url.password or url.port or url.fragment:
                raise ValueError(f'Invalid booking URL: {cid}/{provider}')
            checked = datetime.fromisoformat(link['last_checked_utc'])
            if checked.tzinfo is None or checked > datetime.now(timezone.utc):
                raise ValueError(f'Invalid link verification date: {cid}/{provider}')
            if provider == 'echannelling':
                query = parse_qs(url.query)
                code = link['hospital_code']
                valid = (
                    url.hostname == 'www.echannelling.com'
                    and url.path == '/doctor-search/D10651/sessions'
                    and query.get('doctorId') == ['D10651']
                    and re.fullmatch(r'H\d+', code)
                    and query.get('hospitalCode') == [code]
                    and link['verification_status'] in {'captured_from_browser_navigation', 'captured_from_href', 'manually_verified'}
                )
            else:
                channel_id = link['channel_id']
                valid = (
                    url.hostname == 'www.doc.lk'
                    and re.fullmatch(r'\d+', channel_id)
                    and re.fullmatch(r'/(?:si/|tm/)?channel/' + re.escape(channel_id), url.path)
                    and link['verification_status'] in {'browser_verified', 'manually_verified'}
                )
            if not valid:
                raise ValueError(f'Unconfirmed doctor/hospital booking URL: {cid}/{provider}')
    if not clinics or len(set(directory['featured_ids'])) != len(directory['featured_ids']) or not set(directory['featured_ids']) <= ids:
        raise ValueError('Featured clinics must identify unique entries in the directory')
