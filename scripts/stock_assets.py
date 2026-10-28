"""Shared, dependency-free stock-asset paths and JPEG metadata reading."""

from pathlib import Path
import json
import struct

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = json.loads((ROOT / 'content/stock-images.json').read_text())
WIDTHS = (640, 1280)


def jpeg_dimensions(path):
    """Read a JPEG's SOF dimensions without recompressing or editing its pixels."""
    data = Path(path).read_bytes()
    if not data.startswith(b'\xff\xd8'):
        raise ValueError(f'Not a JPEG: {path}')
    offset = 2
    sof = {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}
    while offset < len(data):
        if data[offset] != 0xFF:
            raise ValueError(f'Invalid JPEG marker: {path}')
        while offset < len(data) and data[offset] == 0xFF:
            offset += 1
        if offset >= len(data):
            break
        marker = data[offset]
        offset += 1
        if marker in {0xD8, 0xD9, 0x01} or 0xD0 <= marker <= 0xD7:
            continue
        if offset + 2 > len(data):
            break
        length = struct.unpack_from('>H', data, offset)[0]
        if length < 2 or offset + length > len(data):
            raise ValueError(f'Truncated JPEG segment: {path}')
        if marker in sof and length >= 8:
            height, width = struct.unpack_from('>HH', data, offset + 3)
            if width and height:
                return width, height
        if marker == 0xDA:
            break
        offset += length
    raise ValueError(f'JPEG has no valid dimensions: {path}')


def image_path(record, width):
    stem = record['stem']
    if not stem or any(c not in 'abcdefghijklmnopqrstuvwxyz0123456789-' for c in stem):
        raise ValueError('Invalid stock-image filename')
    return ROOT / 'assets/images' / f'{stem}-{width}.jpg'


def available_variants(key):
    record = MANIFEST['images'].get(key)
    if not record:
        return []
    variants = []
    for requested_width in WIDTHS:
        path = image_path(record, requested_width)
        if path.is_file():
            width, height = jpeg_dimensions(path)
            variants.append((path.relative_to(ROOT).as_posix(), width, height))
    return variants
