# Brief Annotation App — Requirements

## Purpose

Capture the user's opinions, reactions, and observations on individual items within daily research briefs. Each annotation includes the user's voice and curated reference links suitable for use in reader-facing output. Annotations accumulate over time and serve as raw material for a future weekly newsletter or blog post (compilation format TBD — out of scope for v1).

## Users

Single user (the brief author). No authentication in v1, but the app must be usable on a remote server accessed from a mobile phone, so auth will be needed before deployment.

## Core Concepts

### Brief

A markdown file in `briefs/` following the existing format. Each brief covers one topic on one date. The app reads briefs directly from the filesystem — it does not generate or modify them.

### Item

A discrete unit within a brief that can be individually annotated. Item types:

| Type | How identified in markdown |
|------|---------------------------|
| Key Development | Bulleted block starting with `**[Headline]**` under `## Key Developments` |
| Notable Paper/Model/Tool | Row in the markdown table under `## Notable Papers / Models / Tools` |
| Technical Deep-Dive | Full content under `## Technical Deep-Dive` (treated as one item) |
| Landscape Trend | Individual bullet under `## Landscape Trends` |
| Vendor Entry | Individual bullet or paragraph under `## Vendor Landscape` |

The Sources section is not annotatable.

### Annotation

User-provided reaction to a single item, comprising a rating, free-text commentary, and curated reference links. The annotation — especially the text and links — is intended as raw material for reader-facing output (newsletter, blog post), not just private notes.

#### Fields

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| Rating | enum: skip, note, highlight | Yes | Default is unrated (no annotation). Skip = not interesting. Note = worth capturing. Highlight = strong reaction, definitely revisit. |
| Text | free text | No | The user's reaction, opinion, observation, or thread to pull. Written in the user's voice. No length limit. |
| Links | list of {url, label} | No | Curated reference links for this item. Pre-populated from the brief's sources; fully editable by the user. |

#### Link Pre-Population

Each item type has a different strategy for extracting initial links:

| Item Type | Pre-population strategy |
|-----------|------------------------|
| Key Development | Match the inline citation `*(Source name, Date)*` against URLs in the brief's Sources section. Pre-fill matching URLs with the source name as label. |
| Notable Paper/Model/Tool | Extract the URL from the Source column of the table row. Use the Item name as label. |
| Technical Deep-Dive | The deep-dive subject must appear in Key Developments (per the brief's coherence rule). Pre-fill with the same links as the corresponding KD. |
| Landscape Trend | Match any inline URLs or source references. For references to prior briefs (e.g., "the 2026-05-09 brief"), resolve to the brief filepath and use a label like "AI Infrastructure & Geopolitics brief, 2026-05-09". |
| Vendor Entry | Match vendor names and product references against URLs in the Sources section. |

Pre-populated links are a starting point. The user can remove irrelevant links, edit labels, and add links not present in the brief (external articles, GitHub issues, internal docs, etc.).

### Reviewed Brief

A brief the user has finished annotating. Marking a brief as "done" records a timestamp and advances the queue. A reviewed brief can be reopened to add or edit annotations.

## Functional Requirements

### Brief Queue

- The queue shows all briefs that are not marked "done": unreviewed briefs and partially annotated briefs.
- On first use (no briefs reviewed yet), the queue is seeded with all briefs from the past 7 days.
- After first use, any new brief appearing in `briefs/` is automatically added to the queue.
- The queue is ordered chronologically (oldest first).
- The landing page shows the queue with: date, topic, number of items, annotation count (if partially annotated), and reviewed status.
- The user can click any brief in the queue to open it — skipping around does not remove earlier briefs from the queue.
- Reviewed briefs drop off the queue but remain accessible from an "All briefs" view where annotations can be revisited or edited.

### Brief View

- The brief is rendered as styled HTML from its source markdown, preserving the reading experience.
- Each annotatable item is visually distinct and clickable/tappable.
- Tapping an item expands an inline annotation panel below the item containing:
  - Three rating buttons (skip / note / highlight) — tap to select, tap again to deselect.
  - A text area for the annotation.
  - A links section showing pre-populated links, each with a URL and editable label. Each link has a remove button. An "Add link" button appends a blank URL + label row.
  - A save button.
- Saving collapses the panel. The item shows a visual indicator of its rating (e.g., colored left border: grey for skip, blue for note, gold for highlight).
- Previously saved annotations (including links) are pre-filled when reopening an item's panel.
- A "Done" button at the bottom marks the brief as reviewed and returns to the queue.

### Annotation Persistence

- Annotations are saved to a local SQLite database.
- Saves are immediate (no batch submit for the whole brief).
- Annotations can be edited after the brief is marked as reviewed.
- The database file is gitignored.

### Brief Parsing

- The parser reads a brief markdown file and extracts items by section and type.
- Each item retains its raw markdown for re-rendering.
- The parser extracts the Sources section and builds a lookup of URLs and source names for link pre-population.
- For each item, the parser runs the type-specific link pre-population strategy described above.
- The parser targets the current brief format only, as defined in `prompts/research-prompt.md`. Legacy brief formats do not need to be supported. Existing briefs will not change after creation.
- If a section is missing or empty (e.g., no Vendor Landscape), it is simply omitted.

## Non-Functional Requirements

### Simplicity

- Minimal dependencies: Flask, a markdown renderer (mistune), SQLite (stdlib).
- No JavaScript framework. Vanilla JS for interaction (expand/collapse panels, submit via fetch).
- No build step.
- Single-command startup: `python web/app.py` or similar.

### Mobile Readiness

- The brief is a single-column document — the layout must work on phone screens without horizontal scrolling.
- Annotation controls (rating buttons, text area, link editing) must be finger-friendly: large tap targets, no hover-dependent interactions.
- Responsive CSS, no framework required.

### Remote Deployment (future)

- The app must be deployable on a remote server (the existing DigitalOcean droplet used for brief generation).
- v1 runs locally. Remote deployment and authentication are deferred but the architecture should not preclude them (e.g., no hardcoded localhost assumptions in the code).

## Data Model

```
briefs
  id            INTEGER PRIMARY KEY
  filename      TEXT UNIQUE
  topic         TEXT
  date          DATE
  reviewed_at   DATETIME NULL

items
  id            INTEGER PRIMARY KEY
  brief_id      INTEGER REFERENCES briefs(id)
  type          TEXT (kd, paper, deep_dive, trend, vendor)
  headline      TEXT
  body_md       TEXT
  position      INTEGER

annotations
  id            INTEGER PRIMARY KEY
  item_id       INTEGER UNIQUE REFERENCES items(id)
  rating        TEXT (skip, note, highlight)
  text          TEXT
  created_at    DATETIME
  updated_at    DATETIME

annotation_links
  id            INTEGER PRIMARY KEY
  annotation_id INTEGER REFERENCES annotations(id)
  url           TEXT
  label         TEXT
  position      INTEGER
```

One annotation per item (UNIQUE on item_id). Rating changes and text edits update the existing row. Links are stored in a separate table to allow multiple links per annotation, ordered by position.

## File Structure

```
web/
  app.py              Flask app — routes, startup
  brief_parser.py     Parse brief markdown into items, render HTML with annotation hooks
  models.py           SQLite schema, data access functions
  templates/
    queue.html        Landing page — brief queue with progress
    brief.html        Rendered brief with inline annotation UI
  static/
    style.css         Responsive styles, rating indicators, annotation panels
    app.js            Expand/collapse, annotation submit, rating toggle, link editing
```

Database file: `web/annotations.db` (gitignored)

## Out of Scope for v1

- Weekly compilation / newsletter generation
- Authentication or multi-user support
- Brief generation or editing from the web UI
- Full-text search across annotations
- Export or API access to annotations
- Tagging or categorization beyond the three-level rating
