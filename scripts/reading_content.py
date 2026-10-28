"""Independent reading drafts, safe content blocks and static nested routes."""

from datetime import date
from html import escape, unescape
from pathlib import Path
import json
import posixpath
import re
import struct
from urllib.parse import urlsplit, urlunsplit

from stock_assets import jpeg_dimensions

READING = {
    'articles': {'folder': 'articles', 'label': 'Articles', 'singular': 'article', 'listing': 'articles.html', 'active': 'articles'},
    'treatments': {'folder': 'treatments', 'label': 'Treatments', 'singular': 'treatment', 'listing': 'treatments.html', 'active': 'treatments'},
    'guides': {'folder': 'patient-information', 'label': 'Patient Information', 'singular': 'guide', 'listing': 'patient-information.html', 'active': 'patient-information'},
}
SLUG = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*')
LANGUAGE = re.compile(r'[a-zA-Z]{2,8}(?:-[a-zA-Z0-9]{1,8})*')


def safe_language(value):
    if not isinstance(value, str) or not LANGUAGE.fullmatch(value):
        raise ValueError(f'Invalid content language: {value!r}')
    return value


def load_reading_catalog(data, root):
    """Resolve one draft file per entry; fail before any page is generated."""
    seen = set()
    for kind, config in READING.items():
        expanded = []
        for reference in data[kind]:
            slug = reference['id']
            if not SLUG.fullmatch(slug):
                raise ValueError(f'Invalid reading-page ID: {slug}')
            expected = Path('content') / config['folder'] / f'{slug}.json'
            if reference['content'] != expected.as_posix():
                raise ValueError(f'Unexpected source path for {slug}')
            source = root / expected
            if source in seen:
                raise ValueError(f'Duplicate reading draft: {source}')
            seen.add(source)
            item = json.loads(source.read_text())
            if item['id'] != slug or not all(item.get(k) for k in ['title', 'summary', 'category', 'icon', 'sections']):
                raise ValueError(f'Missing required reading metadata in {source}')
            safe_language(item.get('lang', 'en'))
            if item.get('status') not in {'draft', 'reviewed'}:
                raise ValueError(f'Invalid review status in {source}')
            if item['status'] == 'reviewed':
                if not item.get('reviewed_by') or not item.get('reviewed_on'):
                    raise ValueError(f'Reviewed content needs reviewer and date: {source}')
                if date.fromisoformat(item['reviewed_on']) > date.today():
                    raise ValueError(f'Review date cannot be in the future: {source}')
            ids = {'title', 'further-reading'}
            for section in item['sections']:
                if not SLUG.fullmatch(section['id']) or section['id'] in ids:
                    raise ValueError(f'Invalid or repeated section ID in {source}')
                ids.add(section['id'])
                if not section.get('heading') or not isinstance(section.get('blocks'), list):
                    raise ValueError(f'A section needs a heading and blocks: {source}')
                for block in section['blocks']:
                    if block.get('type') == 'heading':
                        sub_id = block.get('id', '')
                        if not SLUG.fullmatch(sub_id) or sub_id in ids:
                            raise ValueError(f'Invalid or repeated subsection ID in {source}')
                        ids.add(sub_id)
            expanded.append(item)
        if len({i['id'] for i in expanded}) != len(expanded):
            raise ValueError(f'Duplicate {kind} IDs')
        data[kind] = expanded
    for kind in READING:
        for item in data[kind]:
            for related in item.get('related_items', []):
                if related['kind'] not in READING or not any(r['id'] == related['id'] for r in data[related['kind']]):
                    raise ValueError(f'Invalid related item in {kind}/{item["id"]}')
    return data


def reading_url(kind, item):
    return f'{READING[kind]["folder"]}/{item["id"]}.html'


def resolve_content_url(url, data):
    """Upgrade all old listing fragments to their dedicated reading page."""
    parsed = urlsplit(url)
    if parsed.scheme or parsed.netloc or not parsed.path or not parsed.fragment:
        return url
    aliases = {'services.html': 'treatments', 'medical-information.html': 'guides'}
    for kind, config in READING.items():
        if parsed.path == config['listing'] or aliases.get(parsed.path) == kind:
            target = next((i for i in data[kind] if i['id'] == parsed.fragment), None)
            if target:
                return urlunsplit(('', '', reading_url(kind, target), parsed.query, ''))
    return url


def rewrite_page_urls(html, filename, data):
    """Keep nested pages usable with HTTP and direct file opening, without base tags."""
    parent = Path(filename).parent.as_posix()

    def relative(value):
        value = resolve_content_url(value, data)
        parsed = urlsplit(value)
        if parsed.scheme or parsed.netloc or not parsed.path:
            return value
        local_path = parsed.path.lstrip('/')
        return urlunsplit(('', '', posixpath.relpath(local_path, parent), parsed.query, parsed.fragment))

    def replace(match):
        attr, quote, raw = match.group('attr', 'quote', 'value')
        value = unescape(raw)
        if attr == 'srcset':
            parts = []
            for candidate in value.split(','):
                path, *descriptor = candidate.strip().split()
                parts.append(' '.join([relative(path), *descriptor]))
            value = ', '.join(parts)
        else:
            value = relative(value)
        return f'{attr}={quote}{escape(value, quote=True)}{quote}'

    # Rewrite URL attributes in generated markup while preserving SVG attribute
    # case (including viewBox), inline symbol fragments and escaped article text.
    return re.sub(r'''(?<![\w-])(?P<attr>data-reading-url|srcset|href|src)=(?P<quote>["'])(?P<value>.*?)(?P=quote)''', replace, html)


def image_dimensions(root, source):
    parsed = urlsplit(source)
    if parsed.scheme or parsed.netloc or parsed.query or parsed.fragment:
        raise ValueError('Inline images must be local assets')
    path = (root / parsed.path).resolve()
    if not path.is_relative_to((root / 'assets/images').resolve()) or not path.is_file():
        raise ValueError(f'Inline image is not a local image asset: {source}')
    if path.suffix.lower() in {'.jpg', '.jpeg'}:
        return jpeg_dimensions(path)
    if path.suffix.lower() == '.png':
        header = path.read_bytes()[:24]
        if header[:8] == b'\x89PNG\r\n\x1a\n' and len(header) == 24:
            return struct.unpack('>II', header[16:24])
    raise ValueError(f'Inline images must be valid JPEG or PNG files: {source}')


def render_blocks(blocks, root):
    """Text is escaped; no executable or arbitrary HTML is accepted from drafts."""
    output = []
    e = lambda value: escape(str(value), quote=True)
    for block in blocks:
        kind = block['type']
        language = f' lang="{e(safe_language(block["lang"]))}"' if block.get('lang') else ''
        if kind == 'paragraph':
            question = ' class="reading-question"' if block.get('question') else ''
            output.append(f'<p{question}{language}>{e(block["text"])}</p>')
        elif kind == 'heading':
            output.append(f'<h3 id="reading-{e(block["id"])}" tabindex="-1"{language}>{e(block["text"])}</h3>')
        elif kind == 'list':
            tag = 'ol' if block.get('ordered') else 'ul'
            start = ''
            if tag == 'ol' and block.get('start', 1) != 1:
                if not isinstance(block['start'], int) or block['start'] < 1:
                    raise ValueError('Ordered lists need a positive start number')
                start = f' start="{block["start"]}"'
            output.append(f'<{tag}{language}{start}>' + ''.join(f'<li>{e(text)}</li>' for text in block['items']) + f'</{tag}>')
        elif kind == 'image':
            if not block.get('alt'):
                raise ValueError('Inline images require descriptive alt text')
            width, height = image_dimensions(root, block['src'])
            caption = f'<figcaption{language}>{e(block["caption"])}</figcaption>' if block.get('caption') else ''
            output.append(f'<figure class="reading-inline-figure"><img{language} src="{e(block["src"])}" alt="{e(block["alt"])}" width="{width}" height="{height}" loading="lazy" decoding="async">{caption}</figure>')
        elif kind == 'table':
            headers = block['headers']
            if not headers or not block.get('caption') or any(len(row) != len(headers) for row in block['rows']):
                raise ValueError('Tables need a caption and matching column counts')
            head = ''.join(f'<th scope="col">{e(h)}</th>' for h in headers)
            rows = ''.join('<tr>' + ''.join(f'<td>{e(v)}</td>' for v in row) + '</tr>' for row in block['rows'])
            output.append(f'<div class="reading-table-wrap" role="region" aria-label="{e(block["caption"])}" tabindex="0"><table{language}><caption>{e(block["caption"])}</caption><thead><tr>{head}</tr></thead><tbody>{rows}</tbody></table></div>')
        elif kind == 'callout':
            title = f'<strong>{e(block["title"])}</strong>' if block.get('title') else ''
            output.append(f'<aside class="reading-callout"{language}>{title}<p>{e(block["text"])}</p></aside>')
        else:
            raise ValueError(f'Unsupported reading content block: {kind}')
    return ''.join(output)
