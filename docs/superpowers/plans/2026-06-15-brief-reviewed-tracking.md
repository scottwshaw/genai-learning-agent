# Brief Reviewed Tracking — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Let users mark briefs as reviewed, with visual feedback on the queue page.

**Architecture:** Reuses the existing `annotations.json` per-brief storage and the `/brief/<dirname>/annotate` POST endpoint. A `_reviewed` key is stored alongside item-level annotations (e.g. `{"_reviewed": {"interesting": true}}`). The queue page reads this flag to add a CSS class; the brief view adds a toggle button via JS.

**Tech Stack:** Python/Flask, Jinja2 templates, vanilla JS, CSS

**Spec:** `docs/superpowers/specs/2026-06-15-brief-reviewed-tracking-design.md`

---

**Important context for all tasks:**

- Tests run from `web/`: `cd web && python -m pytest`
- The test fixture in `test_app.py` sets `app_module.BRIEFS_DIR` and `os.environ["BRIEFS_DIR"]` to a `tmp_path`
- The existing annotate endpoint does: `data = request.get_json(); item_key = data.pop("item_key"); save_annotation(brief_dir, item_key, data)` — so POSTing `{"item_key": "_reviewed", "interesting": true}` stores `{"_reviewed": {"interesting": true}}` in annotations.json
- CSS already has `.brief-item.reviewed { opacity: 0.5; }` at `web/static/style.css:90-92` — no new queue-page CSS needed

**File map:**

- Modify: `web/app.py` — `get_recent_briefs()` loads annotations, `brief()` passes reviewed state
- Modify: `web/templates/queue.html` — conditionally adds `reviewed` class
- Modify: `web/templates/brief.html` — adds `data-reviewed` attribute and button container
- Modify: `web/static/brief.js` — adds Mark Reviewed toggle button
- Modify: `web/static/style.css` — adds styling for the reviewed toggle button
- Modify: `web/test_app.py` — new test class for reviewed tracking

---

### Task 1: get_recent_briefs returns reviewed flag

**Files:**
- Modify: `web/test_app.py`
- Modify: `web/app.py:216-233` (`get_recent_briefs`)

- [ ] **Step 1: Write the failing test**

Add to `web/test_app.py`, after the `TestBriefQueue` class:

```python
class TestBriefReviewedTracking:
    """Tracking which briefs have been reviewed."""

    def test_reviewed_brief_is_flagged_in_queue(self, client, briefs_dir):
        """Given a brief has been marked as reviewed in annotations.json,
        when I visit the queue,
        then that brief's list item has the 'reviewed' class."""
        import json
        today = datetime.now().strftime("%Y-%m-%d")
        dirname = f"{today}-agentic-systems"
        ann_path = briefs_dir / dirname / "annotations.json"
        ann_path.write_text(json.dumps({"_reviewed": {"interesting": True}}))

        resp = client.get("/")
        html = resp.data.decode()
        assert 'class="brief-item reviewed"' in html
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd web && python -m pytest test_app.py::TestBriefReviewedTracking::test_reviewed_brief_is_flagged_in_queue -v`
Expected: FAIL — `'class="brief-item reviewed"' not in html` because `get_recent_briefs` doesn't return a `reviewed` flag and the template doesn't use it.

- [ ] **Step 3: Implement get_recent_briefs with reviewed flag**

In `web/app.py`, modify `get_recent_briefs` to load annotations and include the reviewed state:

```python
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
```

Then modify `web/templates/queue.html` — change the `<li>` to conditionally add the `reviewed` class:

```html
<li class="brief-item{{ ' reviewed' if brief.reviewed else '' }}">
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd web && python -m pytest test_app.py::TestBriefReviewedTracking::test_reviewed_brief_is_flagged_in_queue -v`
Expected: PASS

- [ ] **Step 5: Write test for unreviewed brief**

Add to `TestBriefReviewedTracking` in `web/test_app.py`:

```python
    def test_unreviewed_brief_has_no_reviewed_class(self, client):
        """Given a brief has no annotations,
        when I visit the queue,
        then that brief's list item does not have the 'reviewed' class."""
        resp = client.get("/")
        html = resp.data.decode()
        assert 'class="brief-item"' in html
        # Make sure not all items got the reviewed class
        assert 'brief-item reviewed' not in html
```

- [ ] **Step 6: Run test to verify it passes**

Run: `cd web && python -m pytest test_app.py::TestBriefReviewedTracking -v`
Expected: Both tests PASS

- [ ] **Step 7: Run full test suite**

Run: `cd web && python -m pytest -v`
Expected: All tests PASS

- [ ] **Step 8: Commit**

```bash
git add web/app.py web/templates/queue.html web/test_app.py
git commit -m "feat: show reviewed status on queue page"
```

---

### Task 2: Brief view exposes reviewed state

**Files:**
- Modify: `web/test_app.py`
- Modify: `web/app.py:242-259` (`brief` route)
- Modify: `web/templates/brief.html`

- [ ] **Step 1: Write the failing test**

Add to `TestBriefReviewedTracking` in `web/test_app.py`:

```python
    def test_brief_page_has_reviewed_data_attribute(self, client, briefs_dir):
        """Given a brief has been marked as reviewed,
        when I view the brief,
        then the page has data-reviewed='true'."""
        import json
        today = datetime.now().strftime("%Y-%m-%d")
        dirname = f"{today}-agentic-systems"
        ann_path = briefs_dir / dirname / "annotations.json"
        ann_path.write_text(json.dumps({"_reviewed": {"interesting": True}}))

        resp = client.get(f"/brief/{dirname}")
        html = resp.data.decode()
        assert 'data-reviewed="true"' in html
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd web && python -m pytest test_app.py::TestBriefReviewedTracking::test_brief_page_has_reviewed_data_attribute -v`
Expected: FAIL — `'data-reviewed="true"' not in html`

- [ ] **Step 3: Implement — pass reviewed state to brief template**

In `web/app.py`, modify the `brief()` route. After `annotations = load_annotations(brief_dir)`, extract the reviewed flag and pass it to the template:

```python
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
```

In `web/templates/brief.html`, add `data-reviewed` to the `<main>` element:

```html
<main class="brief-content" data-dirname="{{ filename }}" data-reviewed="{{ 'true' if reviewed else '' }}">
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd web && python -m pytest test_app.py::TestBriefReviewedTracking::test_brief_page_has_reviewed_data_attribute -v`
Expected: PASS

- [ ] **Step 5: Write test for unreviewed brief's data attribute**

Add to `TestBriefReviewedTracking` in `web/test_app.py`:

```python
    def test_unreviewed_brief_has_empty_reviewed_attribute(self, client):
        """Given a brief has not been reviewed,
        when I view the brief,
        then data-reviewed is empty."""
        today = datetime.now().strftime("%Y-%m-%d")
        resp = client.get(f"/brief/{today}-agentic-systems")
        html = resp.data.decode()
        assert 'data-reviewed=""' in html
```

- [ ] **Step 6: Run to verify it passes**

Run: `cd web && python -m pytest test_app.py::TestBriefReviewedTracking -v`
Expected: All tests in the class PASS

- [ ] **Step 7: Run full test suite**

Run: `cd web && python -m pytest -v`
Expected: All tests PASS

- [ ] **Step 8: Commit**

```bash
git add web/app.py web/templates/brief.html web/test_app.py
git commit -m "feat: expose reviewed state in brief view"
```

---

### Task 3: Mark Reviewed toggle button

**Files:**
- Modify: `web/static/brief.js`
- Modify: `web/static/style.css`
- Modify: `web/test_app.py`

- [ ] **Step 1: Write the failing test for the annotate endpoint accepting _reviewed**

Add to `TestBriefReviewedTracking` in `web/test_app.py`:

```python
    def test_post_reviewed_annotation(self, client, briefs_dir):
        """Given a brief exists,
        when I POST a _reviewed annotation,
        then it is saved to annotations.json."""
        import json
        today = datetime.now().strftime("%Y-%m-%d")
        dirname = f"{today}-agentic-systems"
        resp = client.post(
            f"/brief/{dirname}/annotate",
            json={"item_key": "_reviewed", "interesting": True},
        )
        assert resp.status_code == 200
        annotations = json.loads((briefs_dir / dirname / "annotations.json").read_text())
        assert annotations["_reviewed"]["interesting"] is True
```

- [ ] **Step 2: Run test to verify it passes**

Run: `cd web && python -m pytest test_app.py::TestBriefReviewedTracking::test_post_reviewed_annotation -v`
Expected: PASS — the existing generic annotate endpoint already handles this. This test documents the contract.

- [ ] **Step 3: Add the Mark Reviewed button to brief.js**

Replace the contents of `web/static/brief.js` with:

```javascript
document.addEventListener("DOMContentLoaded", function () {
  var main = document.querySelector("[data-dirname]");
  var dirname = main.dataset.dirname;

  // Mark Reviewed toggle
  var reviewBtn = document.createElement("button");
  reviewBtn.className = "reviewed-toggle";
  var isReviewed = main.dataset.reviewed === "true";
  reviewBtn.textContent = isReviewed ? "✔ Reviewed" : "Mark Reviewed";
  if (isReviewed) reviewBtn.classList.add("is-reviewed");
  reviewBtn.addEventListener("click", function () {
    isReviewed = !isReviewed;
    fetch("/brief/" + dirname + "/annotate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ item_key: "_reviewed", interesting: isReviewed }),
    }).then(function () {
      reviewBtn.textContent = isReviewed ? "✔ Reviewed" : "Mark Reviewed";
      reviewBtn.classList.toggle("is-reviewed", isReviewed);
    });
  });
  main.insertBefore(reviewBtn, main.firstChild);

  // Star toggles for annotatable items
  document.querySelectorAll("[data-item-key]").forEach(function (el) {
    var btn = document.createElement("button");
    btn.className = "interesting-toggle";
    btn.textContent = el.dataset.interesting === "true" ? "★" : "☆";
    btn.addEventListener("click", function (e) {
      e.stopPropagation();
      var isInteresting = el.dataset.interesting !== "true";
      fetch("/brief/" + dirname + "/annotate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ item_key: el.dataset.itemKey, interesting: isInteresting }),
      }).then(function () {
        el.dataset.interesting = isInteresting ? "true" : "";
        btn.textContent = isInteresting ? "★" : "☆";
        el.classList.toggle("is-interesting", isInteresting);
      });
    });
    el.insertBefore(btn, el.firstChild);
  });
});
```

- [ ] **Step 4: Add CSS for the reviewed toggle button**

Add to the end of `web/static/style.css`:

```css
.reviewed-toggle {
    display: block;
    margin: 0 0 16px;
    padding: 8px 16px;
    font-size: 0.9rem;
    border: 1px solid #ccc;
    border-radius: 4px;
    background: #fff;
    cursor: pointer;
    color: #666;
}

.reviewed-toggle:active {
    background: #f0f0f0;
}

.reviewed-toggle.is-reviewed {
    background: #f0fdf4;
    border-color: #86efac;
    color: #166534;
}
```

- [ ] **Step 5: Run full test suite**

Run: `cd web && python -m pytest -v`
Expected: All tests PASS

- [ ] **Step 6: Commit**

```bash
git add web/static/brief.js web/static/style.css web/test_app.py
git commit -m "feat: add Mark Reviewed toggle button in brief view"
```

---

### Task 4: Manual verification

- [ ] **Step 1: Start the dev server**

Run: `cd web && python app.py`

- [ ] **Step 2: Verify queue page**

Open `http://localhost:5001/`. Confirm briefs are listed without reviewed styling.

- [ ] **Step 3: Verify Mark Reviewed button**

Click a brief. Confirm the "Mark Reviewed" button appears at the top. Click it — it should change to "✔ Reviewed" with a green background.

- [ ] **Step 4: Verify queue reflects reviewed state**

Go back to the queue. The brief you just marked should appear dimmed (reduced opacity).

- [ ] **Step 5: Verify toggle off**

Open the same brief again. The button should show "✔ Reviewed". Click it to un-mark. Go back to queue — it should appear normal again.
