#!/usr/bin/env python3
"""Import the read-only legacy archive into independent, editable draft sources.

This is a migration command, not part of the normal site build. Existing imports
are protected unless --replace is explicitly supplied. No network is used.
"""

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import shutil

ROOT = Path(__file__).resolve().parents[1]
IMAGE = re.compile(r'!\[([^\]]*)\]\(([^\s)]+)(?:\s+"[^"]*")?\)')
PROMPT = re.compile(r'(?:(?:My|Your) Problem Is Not Listed\s*\??|Please send us your (?:inquery|problem)\.?|Please contact us\.?)', re.I)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def content_language(text, language):
    # English alt text and wholly English passages need their own language tag
    # inside a Sinhala document. Sinhala text is never transliterated/normalised.
    if language == 'si' and re.search('[a-zA-Z]', text) and not re.search('[\u0d80-\u0dff]', text):
        return {'lang': 'en'}
    return {}


def parse_article(path, row, assets, descriptions, archive):
    raw = path.read_text(encoding='utf-8')
    if not raw.startswith('---\n') or 'archive_status: scraped-review-required' not in raw:
        raise ValueError(f'Expected a completed archive export: {path}')
    frontmatter, body = raw[4:].split('\n---', 1)
    sections = [{'id': 'overview', 'heading': 'හැඳින්වීම' if row['language'] == 'si' else 'Overview', 'blocks': []}]
    current = sections[0]
    events = []
    counts = Counter()
    # Some source pages start at H3, rather than H2. Promote their outermost
    # heading level; preserve heading text and the relative section order.
    heading_levels = [len(m[1]) for m in re.finditer(r'^(#{2,6}) ', body, re.M)]
    base_level = min(heading_levels, default=2)
    section_count = sub_count = 0
    removed_title = False

    for chunk in re.split(r'\n\s*\n', body.strip()):
        chunk = chunk.strip()
        if not chunk:
            continue
        if chunk.startswith('# ') and not removed_title:
            removed_title = True
            continue
        if chunk.startswith('**Original source:**') or chunk.startswith('> Archival copy'):
            continue
        if re.search(r'lorem ipsum', chunk, re.I):
            events.append({'reason': 'placeholder', 'text': chunk})
            continue
        if PROMPT.fullmatch(chunk):
            events.append({'reason': 'legacy-enquiry-prompt', 'text': chunk})
            continue
        if re.fullmatch(r'-{3,}', chunk):
            events.append({'reason': 'formatting-separator', 'text': chunk})
            continue

        matches = list(IMAGE.finditer(chunk))
        if matches:
            # The only linked content images in this archive are a two-image
            # gallery. Keep both local figures, without links to remote JPEGs.
            residue = IMAGE.sub('', chunk)
            residue = re.sub(r'https://[^\s)]+', '', residue)
            if residue.strip(' \n\t-[]()'):
                raise ValueError(f'Unexpected mixed image/text block in {path}: {chunk[:100]}')
            for match in matches:
                source = (path.parent / match[2]).resolve()
                if not source.is_relative_to((archive / 'images').resolve()) or not source.is_file():
                    raise ValueError(f'Missing or unsafe archived image: {source}')
                sha = digest(source)
                description = descriptions[sha]
                asset = assets[sha]
                metadata = next((m for m in row['_images'] if (archive / m['relative_path']).resolve() == source), None)
                if not metadata or not metadata.get('downloaded'):
                    raise ValueError(f'Missing image provenance: {source}')
                asset['sources'].append({'article_id': row['id'], 'archive_file': source.relative_to(archive).as_posix(), 'url': metadata['source_url']})
                current['blocks'].append({'type': 'image', 'src': asset['file'], **description})
                counts['images'] += 1
            if '[' in residue:
                events.append({'reason': 'gallery-formatting', 'text': 'Linked gallery retained as local inline figures, in source order.'})
            continue

        heading = re.fullmatch(r'(#{2,6})\s+(.+)', chunk)
        if heading:
            text = heading[2]
            language = content_language(text, row['language'])
            if len(heading[1]) == base_level:
                section_count += 1
                current = {'id': f'section-{section_count:02}', 'heading': text, 'blocks': [], **language}
                sections.append(current)
            else:
                sub_count += 1
                current['blocks'].append({'type': 'heading', 'id': f'subsection-{sub_count:02}', 'text': text, **language})
            counts['headings'] += 1
            continue

        lines = chunk.splitlines()
        ordered = re.match(r'^(\d+)\.\s+', lines[0])
        unordered = re.match(r'^[-*+]\s+', lines[0])
        if ordered or unordered:
            pattern = r'^\d+\.\s+(.+)' if ordered else r'^[-*+]\s+(.+)'
            items = []
            for line in lines:
                match = re.match(pattern, line)
                if match:
                    items.append(match[1])
                elif items:
                    items[-1] += '\n' + line
                else:
                    raise ValueError(f'Unsupported list in {path}')
            block = {'type': 'list', 'ordered': bool(ordered), 'items': items}
            if ordered and int(ordered[1]) != 1:
                block['start'] = int(ordered[1])
            block.update(content_language(' '.join(items), row['language']))
            previous = current['blocks'][-1] if current['blocks'] else None
            continues = previous and previous['type'] == 'list' and previous.get('ordered') == block['ordered'] and previous.get('lang') == block.get('lang')
            if continues and (not ordered or block.get('start', 1) == previous.get('start', 1) + len(previous['items'])):
                # Blank lines between numbered items do not create separate
                # one-item lists. A restart at 1 remains a separate source list.
                previous['items'].extend(items)
            else:
                current['blocks'].append(block)
            counts['list_items'] += len(items)
            continue

        block = {'type': 'paragraph', 'text': chunk, **content_language(chunk, row['language'])}
        if len(chunk) < 180 and (chunk.endswith('?') or re.match(r'^(?:What|How|Who|When|Why|Any|Can|Is|Will|My)\b', chunk) and len(chunk) < 85):
            block['question'] = True
        current['blocks'].append(block)
        counts['paragraphs'] += 1

    extracted = re.search(r'^extracted_utc: "([^"]+)"', frontmatter, re.M)
    return [s for s in sections if s['blocks'] or s['id'] != 'overview'], events, dict(counts), extracted[1] if extracted else None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive', nargs='?', type=Path, default=ROOT.parent / 'orthopaedic-lk-content-archive-toolkit')
    parser.add_argument('--replace', action='store_true', help='explicitly replace existing imported drafts and the generated migration report')
    args = parser.parse_args()
    archive = args.archive.resolve()
    plan = read_json(ROOT / 'content/article-import-plan.json')
    manifest = read_json(archive / 'manifest.json')
    combined = (archive / 'ALL-ARTICLES.md').read_text(encoding='utf-8')
    source_ids = [r['id'] for r in manifest]
    if len(source_ids) != 40 or len(set(source_ids)) != 40 or set(source_ids) != {r['source_id'] for r in plan['imports']}:
        raise ValueError('Manifest and migration plan must account for all 40 source entries exactly once')
    if set(re.findall(r'^\*\*Article ID:\*\* (.+)$', combined, re.M)) != set(source_ids):
        raise ValueError('Combined archive and individual source inventory disagree')
    if not args.replace and any((ROOT / 'content/articles' / (r['id'] + '.json')).exists() for r in plan['imports']):
        raise ValueError('Imported drafts already exist. Normal edits belong in content/articles; use --replace only for a deliberate re-import.')

    descriptions = read_json(ROOT / 'content/article-image-descriptions.json')
    assets = {}
    for row in manifest:
        row['_images'] = read_json(archive / 'metadata' / (row['id'] + '.images.json'))
        for metadata in row['_images']:
            source = archive / metadata['relative_path']
            sha = digest(source)
            if sha not in descriptions:
                raise ValueError(f'Image needs a checked description: {source}')
            assets.setdefault(sha, {'file': f'assets/images/articles/{sha[:20]}{source.suffix.lower()}', 'sha256': sha, 'bytes': source.stat().st_size, 'sources': [], '_source': source})

    taxonomy = read_json(ROOT / 'content/article-taxonomy.json')
    manifest_by_id = {row['id']: row for row in manifest}
    imports = []
    records = []
    all_events = []
    icon_for_region = {'hip': 'hip', 'knee': 'knee', 'spine': 'assessment', 'neck': 'assessment'}
    for entry in plan['imports']:
        row = manifest_by_id[entry['source_id']]
        relative_source = Path('english' if row['language'] == 'en' else 'sinhala') / (row['id'] + '.md')
        path = archive / relative_source
        sections, events, counts, extracted = parse_article(path, row, assets, descriptions, archive)
        item = {
            'id': entry['id'], 'title': row['title'] if row['group'] != 'overview' else 'ළමා පිටුව',
            'summary': entry['summary'], 'category': taxonomy['topics'][entry['topics'][0]][row['language']],
            'icon': icon_for_region.get(entry['body_regions'][0], 'fracture'),
            'lang': row['language'], 'audiences': entry['audiences'], 'body_regions': entry['body_regions'], 'topics': entry['topics'],
            'keywords': [row['note']], 'status': 'draft', 'author': None, 'reviewed_by': None, 'reviewed_on': None,
            'sections': sections, 'references': [], 'related_items': [],
            'archive': {'source_id': row['id'], 'url': row['url'], 'file': relative_source.as_posix(), 'sha256': digest(path), 'original_title': row['title'], 'extracted_utc': extracted},
        }
        if row['group'] == 'overview':
            item['format'] = 'guide'
            item['guide_items'] = [r['id'] for r in plan['imports'] if r['source_id'].startswith('si-children-')]
        imports.append(item)
        records.append({'source_id': row['id'], 'id': item['id'], 'source_url': row['url'], 'source_file': relative_source.as_posix(), 'source_sha256': digest(path), 'destination': f'articles/{item["id"]}.html', 'counts': counts, 'outcome': 'guide-with-full-source' if row['group'] == 'overview' else 'separate-draft'})
        all_events.extend({'source_id': row['id'], **event} for event in events)

    all_items = imports
    for item in all_items:
        # Match related articles by shared subject/region and audience, in the
        # same language. This is not a translation-pair inference.
        candidates = [r for r in all_items if r['id'] != item['id'] and r['lang'] == item['lang'] and set(r['audiences']) & set(item['audiences']) and (set(r['topics']) & set(item['topics']) or set(r['body_regions']) & set(item['body_regions']))]
        candidates.sort(key=lambda r: -(3 * len(set(r['body_regions']) & set(item['body_regions'])) + 2 * len(set(r['topics']) & set(item['topics']))))
        old = list(item.get('related_items', []))
        for related in candidates[:3]:
            reference = {'kind': 'articles', 'id': related['id']}
            if reference not in old:
                old.append(reference)
        item['related_items'] = old

    # Validate the entire import before writing any website sources or assets.
    from article_library import validate_articles
    validate_articles(all_items)
    for asset in assets.values():
        target = ROOT / asset['file']
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            shutil.copyfile(asset['_source'], target)
        if digest(target) != asset['sha256']:
            raise ValueError(f'Copied asset checksum mismatch: {target}')
        del asset['_source']
        asset['sources'] = list({json.dumps(source, sort_keys=True): source for source in asset['sources']}.values())
    for item in all_items:
        write_json(ROOT / 'content/articles' / (item['id'] + '.json'), item)
    site = read_json(ROOT / 'content/site.json')
    site['articles'] = [{'id': item['id'], 'content': f'content/articles/{item["id"]}.json'} for item in imports]
    site['retired_articles'] = plan.get('retired_articles', [])
    write_json(ROOT / 'content/site.json', site)
    write_json(ROOT / 'content/article-assets.json', {'assets': list(assets.values())})
    write_json(ROOT / 'content/article-migration.json', {'archive_manifest_sha256': digest(archive / 'manifest.json'), 'combined_archive_sha256': digest(archive / 'ALL-ARTICLES.md'), 'articles': records, 'events': all_events, 'retired_articles': site['retired_articles']})
    write_report(records, imports, all_events, assets, site['retired_articles'])
    print(f'Imported only the {len(imports)} archive entries; copied {len(assets)} distinct images for {sum(r["counts"]["images"] for r in records)} source placements.')
    print('Archive remains read-only. Rebuild with: python3 -B scripts/build_site.py')


def write_report(records, imports, events, assets, retired):
    taxonomy = read_json(ROOT / 'content/article-taxonomy.json')
    labels = lambda group, values: ', '.join(taxonomy[group][value]['en'] for value in values)
    lines = [
        '# Article migration review', '',
        '## Scope and outcome', '',
        'This local, noindex draft preview contains **exactly the 40 supplied archive entries (19 English, 21 Sinhala)**. The five earlier dummy articles have been removed from the catalog, source files, generated pages, home previews and related links. The Sinhala children’s overview is one of the 40 entries, presented as a topic guide with its complete source material retained beneath the guide links. It is not counted twice.', '',
        'The archive was read only. The importer checked ALL-ARTICLES.md against the individual-file manifest and used the individual UTF-8 Markdown files as the text authority. `content/article-migration.json` records source checksums, exact omitted blocks, outcomes and the retired article IDs. `content/article-assets.json` records the local image checksums and original image URLs. The normal build uses editable article JSON; it never re-imports the archive.', '',
        '## Decisions requiring editorial review', '',
        '1. **Overlapping English child articles:** en-children-01 and en-children-03 share 14 substantial paragraphs, including the humerus and supracondylar sections. Both remain separate drafts. The upper-arm article also contains additional material and repeated numbered complication lists. Choose the eventual article boundaries and reconcile the unique content before merging or retiring a route.',
        '2. **Sinhala child guide:** si-overview-01 now links to all 11 individual Sinhala child topics. Its original text, headings and images remain in their original order below the new navigation. Compare the versions before consolidating: the overview includes material absent or worded differently in the individual articles. Some source headings and images appear mismatched (for example, trigger-finger and wrist diagrams alongside child dislocation topics). They are preserved for review rather than silently substituted.',
        '3. **Clinical accuracy:** all imports remain drafts, with no author, reviewer or review date assigned. Review absolute treatment statements, exact recovery/operation timings, comparative claims about alternative treatment, statistical claims and outdated wording. The adult hip and foot/ankle sources contain shoulder/arm wording that appears copied from another topic. It has been preserved and requires correction by the clinician.',
        '4. **Attribution and images:** the archive describes a different legacy practice. Do not infer authorship or offered services for the new doctor. First-person source passages and branded X-rays remain in the full local articles, with a draft notice. Source URLs are retained only in internal migration/provenance records; the website does not display an original-article link or direct readers to the archive website. Confirm attribution, image reuse and clinical relevance before release; do not erase watermarks or transfer legacy credentials.',
        '5. **Language and classification:** native Sinhala titles and substantive copy are preserved. New summaries, controls and taxonomy labels need a Sinhala editorial check. The complex-fracture article is tagged for both adults and children because its source explicitly discusses both; audience-filter counts therefore overlap.',
        '## Complete archive inventory', '',
        '| Source ID | Article | Language | Audience | Body region | Topic | Original URL | Destination | Outcome |',
        '| --- | --- | --- | --- | --- | --- | --- | --- | --- |',
    ]
    for record, item in zip(records, imports):
        outcome = 'Topic guide + complete source retained' if item.get('format') == 'guide' else 'Separate draft; overlap pending review' if record['source_id'] in {'en-children-01', 'en-children-03'} else 'Separate draft'
        lines.append(f'| {record["source_id"]} | {item["title"]} | {item["lang"]} | {labels("audiences", item["audiences"])} | {labels("body_regions", item["body_regions"])} | {labels("topics", item["topics"])} | [Source]({record["source_url"]}) | [Preview](../{record["destination"]}) | {outcome} |')
    lines += ['', '## Removed dummy articles', '', 'The following prototype articles were removed at the user’s request. Their source JSON and generated HTML files are deleted; these are retirement records, not live links:', '']
    lines.extend(f'- `{slug}`' for slug in retired)
    lines += ['', 'The import command creates only the 40 supplied articles. The normal build also removes stale HTML files for these explicitly retired IDs. Related-reading references point to supplied articles where there is a matching subject; other dummy references are removed.', '', '## Article metadata', '', 'The children’s guide uses the Sinhala display title `ළමා පිටුව`. Its original mixed-language archive title remains in the article’s `archive.original_title` provenance field. No source-body text is omitted by this display-title change.']
    lines += ['', '## Removal and formatting log', '', 'Exact omitted text is recorded in `content/article-migration.json`; the originals remain in the unchanged archive. No substantive clinical paragraph or source image was removed.', '', '| Source ID | Reason | Removed text or formatting change |', '| --- | --- | --- |']
    for event in events:
        text = event['text'].replace('\n', ' ').replace('|', '\\|')
        lines.append(f'| {event["source_id"]} | {event["reason"]} | {text} |')
    totals = Counter(event['reason'] for event in events)
    lines += ['', f'Logged changes: {dict(totals)}. Archive headings starting at H3 are promoted to H2 where necessary; text and order are unchanged. Original list numbering is retained. Image-only gallery bullets become local figures, with provenance retained.', '', '## Images', '', f'The 390 original image placements resolve to {len(assets)} distinct byte-identical assets. Each is copied once under `assets/images/articles/` and retains its original bytes. Image descriptions were checked against contact sheets. Their English alternative text carries `lang="en"`, including inside Sinhala pages. Inline figures preserve their full aspect ratios; no image is cropped, retouched or rebranded.', '', '## Build and verification', '', 'Run from the website folder:', '', '```sh', 'python3 -B scripts/build_site.py', 'python3 -B scripts/check_site.py', 'python3 -B scripts/check_article_migration.py', '```', '', 'Open `articles.html` directly, or serve this directory with `python3 -m http.server 8080 --bind 127.0.0.1` and open `http://127.0.0.1:8080/articles.html`.', '', 'Filter state is carried in shareable query parameters (`lang`, `audience`, `region`, `topic`, `q`). Article links carry the originating query in `library`; breadcrumbs and return links restore that query without cookies or browser storage. Direct Sinhala reading links return to the Sinhala collection by default.', '', 'Validation results and environment limits are recorded in `docs/article-validation.md`. No publication or deployment was performed.', '', '## Maintenance', '', 'Edit `content/articles/<id>.json`, then rebuild. The importer is a separate migration tool: it refuses to overwrite existing imports unless `--replace` is explicitly provided. A deliberate re-import regenerates imported drafts and this report, so preserve editorial changes before using that option.', '',
    ]
    destination = ROOT / 'docs/article-migration-review.md'
    destination.parent.mkdir(exist_ok=True)
    destination.write_text('\n'.join(lines), encoding='utf-8')


if __name__ == '__main__':
    main()
