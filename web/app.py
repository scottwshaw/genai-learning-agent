#!/usr/bin/env python3
import json
import os
import re
from datetime import datetime, timedelta
from html import escape as _html_escape
from pathlib import Path

from flask import Flask, Response, abort, jsonify, render_template, request
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

_SECTION_SLUGS = {
    "Key Developments": "key-developments",
    "Landscape Trends": "landscape-trends",
    "Notable Papers / Models / Tools": "notable-papers",
    "Technical Deep-Dive": "technical-deep-dive",
}


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


def _extract_url(source_text):
    """Extract the first URL from a source entry."""
    m = re.search(r'https?://\S+', source_text)
    return m.group(0) if m else None


def _source_attr(item_html, sources):
    """Build a data-sources attribute from [N] refs found in the item HTML."""
    refs = list(dict.fromkeys(int(n) for n in re.findall(r'\[(\d+)\]', item_html)))
    texts = [f"[{n}] {sources[n]}" for n in refs if n in sources]
    if not texts:
        return ""
    return f' data-sources="{_html_escape("; ".join(texts))}"'


def _source_tooltip_html(item_html, sources):
    """Build a tooltip div with clickable source links for an item."""
    refs = list(dict.fromkeys(int(n) for n in re.findall(r'\[(\d+)\]', item_html)))
    entries = [(n, sources[n]) for n in refs if n in sources]
    if not entries:
        return ""
    lines = []
    for n, text in entries:
        url = _extract_url(text)
        label = _html_escape(f"[{n}] {text}")
        if url:
            lines.append(f'<a href="{_html_escape(url)}" target="_blank" rel="noopener">{label}</a>')
        else:
            lines.append(f"<span>{label}</span>")
    return '<div class="source-tooltip">' + "<br>".join(lines) + "</div>"


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
            slug = _SECTION_SLUGS.get(section_name, "")
            result.append(_wrap_top_level_items(part, sources, slug))
        elif section_name in _TABLE_ITEM_SECTIONS:
            slug = _SECTION_SLUGS.get(section_name, "")
            result.append(_wrap_table_rows(part, sources, slug))
        elif section_name in _BLOCK_ITEM_SECTIONS:
            slug = _SECTION_SLUGS.get(section_name, "")
            attr = _source_attr(part, sources)
            tooltip = _source_tooltip_html(part, sources)
            result.append(f'<div class="item" data-item-key="{slug}/0"{attr}>{part}{tooltip}</div>')
        else:
            result.append(part)
    return ''.join(result)


def _wrap_top_level_items(html: str, sources: dict, section_slug: str = "") -> str:
    """Wrap only the top-level <li> elements (depth 1) with <div class="item">."""
    output = []
    ul_depth = 0
    item_index = 0
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
            tooltip = _source_tooltip_html(li_content, sources)
            key_attr = f' data-item-key="{section_slug}/{item_index}"' if section_slug else ""
            output.append(f'<div class="item"{key_attr}{attr}>')
            output.append(li_content)
            output.append(tooltip)
            output.append('</div>')
            item_index += 1
        else:
            output.append(html[i])
            i += 1
    return ''.join(output)


def _wrap_table_rows(html: str, sources: dict, section_slug: str = "") -> str:
    """Add class="item-row" and source tooltips to each <tbody> <tr>."""
    in_tbody = False
    in_row = False
    row_lines = []
    row_index = 0
    result = []
    for line in html.split('\n'):
        if '<tbody>' in line:
            in_tbody = True
            result.append(line)
        elif '</tbody>' in line:
            in_tbody = False
            result.append(line)
        elif in_tbody and line.strip() == '<tr>':
            in_row = True
            key_attr = f' data-item-key="{section_slug}/{row_index}"' if section_slug else ""
            row_lines = [line.replace('<tr>', f'<tr class="item-row"{key_attr}>')]
        elif in_row and '</tr>' in line:
            in_row = False
            row_lines.append(line)
            row_html = '\n'.join(row_lines)
            tooltip = _source_tooltip_html(row_html, sources)
            if tooltip:
                row_html = row_html.replace('</tr>', f'<td class="tooltip-cell">{tooltip}</td></tr>')
            result.extend(row_html.split('\n'))
            row_index += 1
        elif in_row:
            row_lines.append(line)
        else:
            result.append(line)
    return '\n'.join(result)



def _apply_annotations(html: str, annotations: dict) -> str:
    """Inject annotation data attributes into items based on their data-item-key."""
    for key, data in annotations.items():
        if data.get("interesting") is True:
            html = html.replace(
                f'data-item-key="{key}"',
                f'data-item-key="{key}" data-interesting="true"',
            )
    return html


def get_recent_briefs(days=7):
    cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    briefs = []
    for path in sorted(BRIEFS_DIR.glob("*/brief.md")):
        dirname = path.parent.name
        parts = dirname.split("-", 3)
        if len(parts) < 4:
            continue
        date = f"{parts[0]}-{parts[1]}-{parts[2]}"
        if date < cutoff:
            continue
        slug = parts[3]
        from annotations import load_annotations
        annotations = load_annotations(path.parent)
        reviewed = annotations.get("_reviewed", {}).get("interesting", False)
        briefs.append({
            "filename": dirname,
            "date": date,
            "topic": TOPIC_LABELS.get(slug, slug),
            "reviewed": reviewed,
        })
    return briefs


_SLUG_TO_SECTION = {v: k for k, v in _SECTION_SLUGS.items()}


def _resolve_refs(item_text: str, sources: dict) -> str:
    """Append resolved source lines for any [N] citations found in item_text."""
    refs = list(dict.fromkeys(int(n) for n in re.findall(r'\[(\d+)\]', item_text)))
    resolved = [f"  - [{n}] {sources[n]}" for n in refs if n in sources]
    if not resolved:
        return item_text
    return item_text.rstrip() + '\n' + '\n'.join(resolved)


def extract_starred_items(md: str, annotations: dict) -> dict:
    """Extract only the starred (interesting) items from brief markdown.

    Returns {section_name: [item_text, ...]} for sections that have starred items.
    """
    starred_keys = {
        k for k, v in annotations.items()
        if k != "_reviewed" and v.get("interesting")
    }
    if not starred_keys:
        return {}

    sources = _parse_sources(md)
    sections = re.split(r'^## ', md, flags=re.MULTILINE)
    parsed = {}
    for section in sections[1:]:
        heading, _, body = section.partition('\n')
        heading = heading.strip()
        slug = _SECTION_SLUGS.get(heading)
        if not slug:
            continue
        relevant = [k for k in starred_keys if k.startswith(slug + "/")]
        if not relevant:
            continue
        indices = {int(k.split("/")[1]) for k in relevant}

        if heading in _LIST_ITEM_SECTIONS:
            items = []
            current_lines = []
            for line in body.split('\n'):
                if line.startswith('- **'):
                    if current_lines:
                        items.append('\n'.join(current_lines))
                    current_lines = [line]
                elif current_lines:
                    current_lines.append(line)
            if current_lines:
                items.append('\n'.join(current_lines))
            parsed[heading] = [
                _resolve_refs(items[i], sources)
                for i in sorted(indices) if i < len(items)
            ]

        elif heading in _TABLE_ITEM_SECTIONS:
            lines = [l for l in body.strip().split('\n') if l.strip()]
            header_line = lines[0] if lines else ""
            sep_line = lines[1] if len(lines) > 1 else ""
            data_rows = lines[2:]
            selected = [data_rows[i] for i in sorted(indices) if i < len(data_rows)]
            if selected:
                table = header_line + '\n' + sep_line + '\n' + '\n'.join(selected)
                parsed[heading] = [_resolve_refs(table, sources)]

        elif heading in _BLOCK_ITEM_SECTIONS:
            if 0 in indices:
                parsed[heading] = [_resolve_refs(body.strip(), sources)]

    return parsed


def compile_weekly_markdown() -> str:
    """Compile starred items from the last 7 days into a single markdown document."""
    from annotations import load_annotations

    briefs = get_recent_briefs()
    dates = [b["date"] for b in briefs]
    date_min = min(dates) if dates else datetime.now().strftime("%Y-%m-%d")
    date_max = max(dates) if dates else datetime.now().strftime("%Y-%m-%d")

    lines = [f"# Weekly Research Compilation — {date_min} to {date_max}\n"]
    has_content = False

    for brief_info in briefs:
        brief_dir = BRIEFS_DIR / brief_info["filename"]
        md = (brief_dir / "brief.md").read_text()
        annotations = load_annotations(brief_dir)
        starred = extract_starred_items(md, annotations)
        if not starred:
            continue
        has_content = True
        lines.append(f"\n---\n")
        lines.append(f"## {brief_info['topic']} ({brief_info['date']})\n")
        for section_name, items in starred.items():
            lines.append(f"### {section_name}\n")
            for item in items:
                lines.append(item.rstrip() + "\n")

    if not has_content:
        lines.append("\nNo starred items in the last 7 days.\n")

    return "\n".join(lines)


@app.route("/")
def queue():
    briefs = get_recent_briefs()
    return render_template("queue.html", briefs=briefs)


@app.route("/compilation/weekly")
def weekly_compilation():
    md = compile_weekly_markdown()
    today = datetime.now().strftime("%Y-%m-%d")
    return Response(
        md,
        mimetype="text/markdown",
        headers={
            "Content-Disposition": f'attachment; filename="weekly-compilation-{today}.md"'
        },
    )


@app.route("/brief/<path:dirname>")
def brief(dirname):
    brief_dir = BRIEFS_DIR / dirname
    path = brief_dir / "brief.md"
    if not path.is_file():
        abort(404)
    md = path.read_text()
    has_refs = _has_numbered_sources(md)
    sources = _parse_sources(md) if has_refs else {}
    from annotations import load_annotations
    annotations = load_annotations(brief_dir)
    reviewed = annotations.get("_reviewed", {}).get("interesting", False)
    renderer = mistune.create_markdown(plugins=['url', 'table'])
    html = renderer(md)
    html = _wrap_items(html, sources)
    html = _apply_annotations(html, annotations)
    if not has_refs:
        html = '<p class="no-refs-notice">Older brief — numbered references not available.</p>\n' + html
    return render_template("brief.html", content=html, filename=dirname, reviewed=reviewed)


@app.route("/brief/<path:dirname>/annotate", methods=["POST"])
def annotate(dirname):
    brief_dir = BRIEFS_DIR / dirname
    if not (brief_dir / "brief.md").is_file():
        abort(404)
    from annotations import save_annotation
    data = request.get_json()
    item_key = data.pop("item_key")
    save_annotation(brief_dir, item_key, data)
    return jsonify(ok=True)


@app.route("/sync/pull", methods=["POST"])
def sync_pull():
    from git_sync import pull
    msg = pull()
    return jsonify(ok=True, message=msg)


@app.route("/sync/push", methods=["POST"])
def sync_push():
    from git_sync import commit_and_push
    msg = commit_and_push()
    return jsonify(ok=True, message=msg)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
