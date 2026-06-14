# Brief Reviewed Tracking

Track which briefs the user has finished reviewing so the queue page shows progress at a glance.

## Problem

The queue page lists all briefs from the last 7 days with no indication of which ones have been reviewed. After reviewing several briefs across sessions, there's no way to tell which are done and which still need attention.

## Design

### Reviewed state in annotations.json

Each brief already has an optional `annotations.json` for item-level star annotations. A new top-level key `_reviewed` (underscore-prefixed to distinguish from item keys like `key-developments/0`) stores the reviewed flag:

```json
{
  "_reviewed": true,
  "key-developments/0": { "interesting": true }
}
```

When `_reviewed` is absent or `false`, the brief is unreviewed. This piggybacks on the existing git sync mechanism — reviewed state pushes and pulls with everything else.

### Mark Reviewed button in the brief view

A toggle button in the brief view header area. When the brief is unreviewed, it shows "Mark Reviewed". When reviewed, it shows "Reviewed" in a checked/confirmed style. Tapping it toggles the state via a POST to the existing `/brief/<dirname>/annotate` endpoint with `{"item_key": "_reviewed", "interesting": true/false}`.

Implementation notes:
- The button lives in `brief.html`, wired up in `brief.js`
- On page load, the button reads the reviewed state from a data attribute on the page (set server-side from annotations.json)
- The POST reuses the existing annotate endpoint — `_reviewed` is just another key in annotations.json
- The payload uses the same `{"interesting": bool}` shape as star annotations. The field name is a minor mismatch in semantics but avoids changing the endpoint contract.

### Visual distinction on the queue page

On the queue page, reviewed briefs are visually dimmed:
- The `<li>` gets a `reviewed` class
- CSS applies reduced opacity and/or a checkmark indicator
- Briefs remain in the same list position (no reordering, no separate section)

Implementation notes:
- `app.py`'s `get_recent_briefs()` loads each brief's annotations.json to check for `_reviewed`
- The reviewed flag is passed to the template as a field on each brief dict
- `queue.html` conditionally adds the `reviewed` class

## Data flow

1. User opens a brief, reads it, taps "Mark Reviewed"
2. `brief.js` POSTs `{"item_key": "_reviewed", "interesting": true}` to `/brief/<dirname>/annotate`
3. `annotations.py` saves `{"_reviewed": {"interesting": true}}` into annotations.json
4. On the queue page, `get_recent_briefs()` reads annotations.json for each brief directory
5. Briefs with `_reviewed.interesting === true` render with the `reviewed` CSS class

## Scope

In scope:
- Toggle button in brief view
- Reviewed visual state on queue page
- Persistence via existing annotations.json and annotate endpoint

Out of scope:
- Filtering/hiding reviewed briefs
- Reviewed timestamps or history
- Bulk mark/unmark
