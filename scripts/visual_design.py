"""Shared, local artwork and reading UI; clinical content remains independent."""

from html import escape
from pathlib import Path
from hashlib import sha256
import json

ROOT = Path(__file__).resolve().parents[1]
DESIGN = json.loads((ROOT / 'content/design.json').read_text())


def page_motif(name, icon):
    glyph = DESIGN['page_motifs'].get(name)
    if not glyph:
        return ''
    return f'<div class="page-title-art" aria-hidden="true">{icon(glyph)}<span class="motif-orbit motif-orbit-one"></span><span class="motif-orbit motif-orbit-two"></span><span class="motif-dot"></span></div>'


def treatment_illustration(slug, loading='lazy'):
    record = DESIGN['treatment_illustrations'].get(slug)
    if not record:
        return ''
    path = ROOT / record['src']
    if not path.resolve().is_relative_to(ROOT / 'assets/illustrations') or path.suffix != '.svg' or not path.is_file():
        raise ValueError(f'Invalid local treatment illustration: {slug}')
    if sha256(path.read_bytes()).hexdigest() != record['sha256']:
        raise ValueError(f'Treatment illustration differs from its provenance: {slug}')
    return f'<div class="treatment-illustration" data-treatment-illustration="{escape(slug, quote=True)}"><img src="{escape(record["src"], quote=True)}" alt="{escape(record["alt"], quote=True)}" width="{record["width"]}" height="{record["height"]}" loading="{loading}" decoding="async"></div>'


def reading_progress():
    return '<div class="reading-progress" data-reading-progress aria-hidden="true" hidden><span class="reading-progress-fill" data-reading-progress-fill></span></div>'
