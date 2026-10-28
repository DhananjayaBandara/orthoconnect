#!/usr/bin/env python3
"""Download the selected Pexels images locally, validate, then rebuild the site.

Run from a terminal with Internet access. Requires Python 3.12+ and no packages.
Existing assets and HTML are left untouched if any required download fails.
"""

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from stock_assets import MANIFEST, ROOT, WIDTHS, image_path, jpeg_dimensions


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Check the expected local JPEGs without using the network.')
    parser.add_argument('--force', action='store_true', help='Download again even if an image already exists.')
    args = parser.parse_args()
    images_dir = ROOT / 'assets/images'
    images_dir.mkdir(parents=True, exist_ok=True)
    records = []
    pending = []
    for key, record in MANIFEST['images'].items():
        if not str(record['pexels_id']).isdigit():
            raise ValueError('Invalid Pexels photo ID')
        for width in WIDTHS:
            path = image_path(record, width)
            valid = False
            if path.is_file():
                try:
                    jpeg_dimensions(path)
                    valid = True
                except ValueError:
                    pass
            records.append((key, record, width, path))
            if not valid or args.force:
                pending.append((key, record, width, path))
    if args.check:
        for key, record, width, path in records:
            if path.is_file():
                try:
                    w, h = jpeg_dimensions(path)
                    print(f'OK: {path.name} ({w} × {h})')
                except ValueError:
                    print(f'INVALID: {path.name}')
            else:
                print(f'MISSING: {path.name}')
        return 1 if pending else 0

    # Stage every required file before replacing any existing photo or page.
    with tempfile.TemporaryDirectory(prefix='orthoconnect-stock-') as staging:
        downloaded = []
        for index, (key, record, width, destination) in enumerate(pending, 1):
            url = f'https://images.pexels.com/photos/{record["pexels_id"]}/pexels-photo-{record["pexels_id"]}.jpeg?auto=compress&cs=tinysrgb&w={width}'
            print(f'Downloading {index}/{len(pending)}: {destination.name}', flush=True)
            request = Request(url, headers={'User-Agent': 'OrthoConnect asset downloader/1.0', 'Accept': 'image/jpeg'})
            try:
                with urlopen(request, timeout=25) as response:
                    content_type = response.headers.get_content_type()
                    if content_type not in {'image/jpeg', 'image/jpg'}:
                        raise ValueError(f'Expected JPEG, received {content_type}')
                    data = response.read(20 * 1024 * 1024 + 1)
                if len(data) > 20 * 1024 * 1024:
                    raise ValueError('Image exceeds the 20 MB limit')
                temp_path = Path(staging) / destination.name
                temp_path.write_bytes(data)
                actual_width, actual_height = jpeg_dimensions(temp_path)
                if actual_width < 320 or actual_height < 200:
                    raise ValueError('Downloaded image is too small')
                downloaded.append((temp_path, destination))
            except (HTTPError, URLError, OSError, ValueError) as error:
                print(f'\nDownload failed: {error}', file=sys.stderr)
                print('Run this command in a terminal with public Internet access. Existing photos and HTML were not changed.', file=sys.stderr)
                return 1
        for temp_path, destination in downloaded:
            destination.write_bytes(temp_path.read_bytes())

    provenance = []
    for key, record, requested_width, path in records:
        width, height = jpeg_dimensions(path)
        provenance.append({
            'key': key, 'file': path.relative_to(ROOT).as_posix(),
            'source': record['source'], 'photographer': record['photographer'],
            'license': MANIFEST['license'], 'width': width, 'height': height,
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
        })
    (ROOT / 'content/stock-assets.lock.json').write_text(json.dumps({
        'downloaded_at': datetime.now(timezone.utc).isoformat(),
        'assets': provenance,
    }, ensure_ascii=False, indent=2) + '\n')
    subprocess.run([sys.executable, str(ROOT / 'scripts/build_site.py')], check=True)
    print(f'\nReady: {len(MANIFEST["images"])} stock photos in {len(records)} local image files. Open {ROOT / "index.html"}.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
