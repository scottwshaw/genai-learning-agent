#!/usr/bin/env python3
import json
import os
import re
from datetime import datetime, timedelta
from html import escape as _html_escape
from pathlib import Path

from flask import Flask, abort, render_template
import mistune

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
BRIEFS_DIR = Path(os.environ.get("BRIEFS_DIR", str(BASE_DIR / "briefs")))
TOPICS_FILE = os.environ.get("TOPICS_FILE", str(BASE_DIR / "topics.json"))


def load_topic_labels():
    with open(TOPICS_FILE) as f:
        data = json.load(f)
    return {t["slug"]: t["label"] for t in data["topics"]}


TOPIC_LABELS = load_topic_labels()

_LIST_ITEM_SECTIONS = {"Key Developments", "Landscape Trends"}
_TABLE_ITEM_SECTIONS = {"Notable Papers / Models / Tools"}
_BLOCK_ITEM_SECTIONS = {"Technical Deep-Dive"}


def _has_numbered_sources(md: str) -> bool:
    """Check if a brief uses numbered [N] references in its Sources section."""
    m = re.search(r'^## Sources\s*\n', md, re.MULTILINE)
    if not m:
        return False
    after = md[m.end():]
    return bool(re.match(r'\s*1\.', after))


def _parse_sources(md: str) -> dict:
    """Parse numbered sources from markdown into {number: text} dict."""
    m = re.search(r'^## Sources\s*\n', md, re.MULTILINE)
    if not m:
        return {}
    sources = {}
    for line in md[m.end():].split('\n'):
        match = re.match(r'(\d+)\.\s+(.+)', line)
        if match:
            sources[int(match.group(1))] = match.group(2).strip()
        elif line.strip().startswith('#'):
            break
    return sources


def _source_attr(item_html, sources):
    """Build a data-sources attribute from [N] refs found in the item HTML."""
    refs = list(dict.fromkeys(int(n) for n in re.findall(r'\[(\d+)\]', item_html)))
    texts = [f"[{n}] {sources[n]}" for n in refs if n in sources]
    if not texts:
        return ""
    return f' data-sources="{_html_escape("; ".join(texts))}"'


def _wrap_items(html: str, sources: dict) -> str:
    """Wrap annotatable items in each section with <div class="item">."""
    parts = re.split(r'(<h2>.*?</h2>)', html)
    result = []
    section_name = None
    for part in parts:
        m = re.match(r'<h2>(.*?)</h2>', part)
        if m:
            section_name = m.group(1).strip()
            result.append(part)
        elif section_name in _LIST_ITEM_SECTIONS:
            result.append(_wrap_top_level_items(part, sources))
        elif section_name in _TABLE_ITEM_SECTIONS:
            result.append(_wrap_table_rows(part))
        elif section_name in _BLOCK_ITEM_SECTIONS:
            attr = _source_attr(part, sources)
            result.append(f'<div class="item"{attr}>{part}</div>')
        else:
            result.append(part)
    return ''.join(result)


def _wrap_top_level_items(html: str, sources: dict) -> str:
    """Wrap only the top-level <li> elements (depth 1) with <div class="item">."""
    output = []
    ul_depth = 0
    i = 0
    while i < len(html):
        if html[i:].startswith('<ul>'):
            ul_depth += 1
            output.append('<ul>')
            i += 4
        elif html[i:].startswith('</ul>'):
            ul_depth -= 1
            output.append('</ul>')
            i += 5
        elif html[i:].startswith('<li>') and ul_depth == 1:
            # Find the matching </li> at this depth
            # We need to track nested <li> to find the right closing tag
            li_start = i
            i += 4  # skip <li>
            li_depth = 1
            while i < len(html) and li_depth > 0:
                if html[i:].startswith('<li>') or html[i:].startswith('<li '):
                    li_depth += 1
                    i += 4
                elif html[i:].startswith('</li>'):
                    li_depth -= 1
                    if li_depth == 0:
                        i += 5  # skip </li>
                        break
                    else:
                        i += 5
                else:
                    i += 1
            li_content = html[li_start:i]
            attr = _source_attr(li_content, sources)
            output.append(f'<div class="item"{attr}>')
            output.append(li_content)
            output.append('</div>')
        else:
            output.append(html[i])
            i += 1
    return ''.join(output)


def _wrap_table_rows(html: str) -> str:
    """Add class="item-row" to each <tbody> <tr>."""
    in_tbody = False
    lines = html.split('\n')
    result = []
    for line in lines:
        if '<tbody>' in line:
            in_tbody = True
        elif '</tbody>' in line:
            in_tbody = False
        if in_tbody and line.strip() == '<tr>':
            line = line.replace('<tr>', '<tr class="item-row">')
        result.append(line)
    return '\n'.join(result)



def get_recent_briefs(days=7):
    cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    briefs = []
    for path in sorted(BRIEFS_DIR.glob("*.md")):
        parts = path.stem.split("-", 3)
        if len(parts) < 4:
            continue
        date = f"{parts[0]}-{parts[1]}-{parts[2]}"
        if date < cutoff:
            continue
        slug = parts[3]
        briefs.append({
            "filename": path.name,
            "date": date,
            "topic": TOPIC_LABELS.get(slug, slug),
        })
    return briefs


@app.route("/")
def queue():
    briefs = get_recent_briefs()
    return render_template("queue.html", briefs=briefs)


@app.route("/brief/<path:filename>")
def brief(filename):
    path = BRIEFS_DIR / filename
    if not path.is_file():
        abort(404)
    md = path.read_text()
    has_refs = _has_numbered_sources(md)
    sources = _parse_sources(md) if has_refs else {}
    renderer = mistune.create_markdown(plugins=['url', 'table'])
    html = renderer(md)
    html = _wrap_items(html, sources)
    if not has_refs:
        html = '<p class="no-refs-notice">Older brief — numbered references not available.</p>\n' + html
    return render_template("brief.html", content=html, filename=filename)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
