"""Functional tests for the brief annotation app."""

import os
from datetime import datetime, timedelta
from pathlib import Path

import pytest

os.environ["TOPICS_FILE"] = str(Path(__file__).resolve().parent.parent / "topics.json")


@pytest.fixture
def briefs_dir(tmp_path):
    today = datetime.now().strftime("%Y-%m-%d")
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    old = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

    d = tmp_path / f"{today}-agentic-systems"
    d.mkdir()
    (d / "brief.md").write_text(
        "# Agentic Systems — Research Brief (2026-05-27)\n\n"
        "## Key Developments\n\n"
        "- **[First KD headline]**\n"
        "  - **What changed:** Something happened.\n"
        "  - **Why it matters:** It is important.\n"
        "  - *Sources: [1]*\n\n"
        "- **[Second KD headline]**\n"
        "  - **What changed:** Another thing.\n"
        "  - **Why it matters:** Also important.\n"
        "  - *Sources: [2]*\n\n"
        "## Notable Papers / Models / Tools\n\n"
        "| Item | Date | Source | Summary |\n"
        "|------|------|--------|---------|\n"
        "| Paper A | May 2026 | [3] | A summary |\n\n"
        "## Technical Deep-Dive\n\n"
        "### The Deep Dive Heading\n\n"
        "Some deep dive content here.\n\n"
        "## Landscape Trends\n\n"
        "- **A trend is emerging.** Details about the trend.\n\n"
        "- **Another trend.** More details here.\n\n"
        "## Sources\n\n"
        "1. CNAS Report (May 2026) — https://example.com/cnas-report [Tier 1 — Policy research]\n"
        "2. TechCrunch (May 2026) — https://example.com/techcrunch-article [Tier 2 — Tech news]\n"
        "3. arXiv (May 2026) — https://example.com/paper-a [Tier 1 — Peer-reviewed]\n"
    )
    d2 = tmp_path / f"{yesterday}-models-and-market"
    d2.mkdir()
    (d2 / "brief.md").write_text(
        "# Models & Market — Research Brief\n\n"
        "## Key Developments\n\n"
        "- **[Some headline]**\n"
        "  - **What changed:** Something.\n"
        "  - **Why it matters:** Important.\n"
        "  - *(TechCrunch, May 2026)*\n\n"
        "## Sources\n\n"
        "- https://example.com/old-source [Tier 2 — Tech news]\n"
    )
    d3 = tmp_path / f"{old}-enterprise-genai-adoption"
    d3.mkdir()
    (d3 / "brief.md").write_text("# Old brief\n\nStale.")

    return tmp_path


@pytest.fixture
def client(briefs_dir):
    os.environ["BRIEFS_DIR"] = str(briefs_dir)
    import app as app_module
    app_module.BRIEFS_DIR = Path(str(briefs_dir))
    app_module.app.config["TESTING"] = True
    with app_module.app.test_client() as client:
        yield client


class TestBriefQueue:
    """Viewing the brief queue."""

    def test_shows_briefs_from_the_last_7_days(self, client):
        """Given briefs from today and yesterday exist,
        when I visit the queue,
        then I see both briefs listed."""
        resp = client.get("/")
        assert resp.status_code == 200
        html = resp.data.decode()
        assert "Agentic Systems" in html
        assert "Models &amp; Market" in html

    def test_excludes_briefs_older_than_7_days(self, client):
        """Given a brief from 30 days ago exists,
        when I visit the queue,
        then I do not see it."""
        resp = client.get("/")
        html = resp.data.decode()
        assert "Enterprise GenAI Adoption" not in html


class TestBriefView:
    """Viewing a rendered brief."""

    def test_renders_brief_markdown_as_html(self, client):
        """Given a brief exists,
        when I visit its URL,
        then I see the markdown rendered as HTML."""
        today = datetime.now().strftime("%Y-%m-%d")
        resp = client.get(f"/brief/{today}-agentic-systems")
        assert resp.status_code == 200
        html = resp.data.decode()
        assert "<h1>Agentic Systems" in html
        assert "Key Developments" in html

    def test_returns_404_for_nonexistent_brief(self, client):
        """Given no brief with this filename exists,
        when I visit its URL,
        then I get a 404."""
        resp = client.get("/brief/nonexistent")
        assert resp.status_code == 404

    def test_clicking_queue_link_renders_brief(self, client, briefs_dir):
        """Given a list of briefs in the queue,
        when I click on a brief,
        then the brief is rendered as its markdown specifies."""
        import re

        # Visit the queue and extract the first brief link
        queue_resp = client.get("/")
        href = re.search(r'href="(/brief/[^"]+)"', queue_resp.data.decode()).group(1)

        # Follow the link
        brief_resp = client.get(href)
        assert brief_resp.status_code == 200
        html = brief_resp.data.decode()

        # The markdown heading is rendered as an HTML heading
        assert "<h1>" in html


    def test_source_links_are_clickable(self, client):
        """Given a rendered brief with a Sources section containing URLs,
        when I view the brief,
        then each URL is a clickable link."""
        today = datetime.now().strftime("%Y-%m-%d")
        resp = client.get(f"/brief/{today}-agentic-systems")
        html = resp.data.decode()
        assert 'href="https://example.com/cnas-report"' in html
        assert 'href="https://example.com/techcrunch-article"' in html


class TestOlderBriefFormat:
    """Viewing briefs that use the old citation format (no numbered references)."""

    def test_older_brief_shows_no_refs_notice(self, client):
        """Given a brief with old-style sources (no numbered references),
        when I view it,
        then I see a notice that references are not available."""
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        resp = client.get(f"/brief/{yesterday}-models-and-market")
        html = resp.data.decode()
        assert "older brief" in html.lower()


class TestBriefItemHighlighting:
    """Hovering over items in a rendered brief."""

    def test_each_item_is_wrapped_as_hoverable(self, client):
        """Given a rendered brief with Key Developments and Landscape Trends,
        when I view the brief,
        then each item is wrapped in an element with class 'item'
        so that it highlights on hover."""
        today = datetime.now().strftime("%Y-%m-%d")
        resp = client.get(f"/brief/{today}-agentic-systems")
        html = resp.data.decode()
        assert html.count('class="item"') == 5  # 2 KDs + 1 deep dive + 2 trends
        assert 'class="item-row"' in html  # paper table row

    def test_item_has_hover_style(self, client):
        """Given CSS is loaded,
        when an item exists on the page,
        then a hover rule is defined for it."""
        resp = client.get("/static/style.css")
        css = resp.data.decode()
        assert ".item:hover" in css


class TestReferenceHover:
    """Hovering over an item shows its source references."""

    def test_item_includes_source_data_for_hover(self, client):
        """Given a brief with numbered [N] references in Key Developments,
        when I view the brief,
        then each item's wrapper includes a data-sources attribute
        containing the resolved source text for its references."""
        today = datetime.now().strftime("%Y-%m-%d")
        resp = client.get(f"/brief/{today}-agentic-systems")
        html = resp.data.decode()
        assert 'data-sources="' in html

    def test_item_source_data_contains_resolved_text(self, client):
        """Given a KD citing [1],
        when I view the brief,
        then its data-sources attribute contains the source text from entry 1."""
        today = datetime.now().strftime("%Y-%m-%d")
        resp = client.get(f"/brief/{today}-agentic-systems")
        html = resp.data.decode()
        assert "CNAS Report" in html.split('data-sources="')[1].split('"')[0]

    def test_source_data_includes_reference_number(self, client):
        """Given a KD citing [1],
        when I view the brief,
        then its data-sources attribute prefixes the source text with [1]."""
        today = datetime.now().strftime("%Y-%m-%d")
        resp = client.get(f"/brief/{today}-agentic-systems")
        html = resp.data.decode()
        first_attr = html.split('data-sources="')[1].split('"')[0]
        assert "[1]" in first_attr

    def test_source_tooltip_contains_clickable_link(self, client):
        """Given a KD citing [1] whose source has a URL,
        when I view the brief,
        then the item contains a tooltip link opening the URL in a new tab."""
        today = datetime.now().strftime("%Y-%m-%d")
        resp = client.get(f"/brief/{today}-agentic-systems")
        html = resp.data.decode()
        assert 'class="source-tooltip"' in html
        assert 'href="https://example.com/cnas-report"' in html
        assert 'target="_blank"' in html

    def test_hover_style_exists_for_source_tooltip(self, client):
        """Given CSS is loaded,
        when a source tooltip could appear,
        then a CSS rule for .source-tooltip exists."""
        resp = client.get("/static/style.css")
        css = resp.data.decode()
        assert ".source-tooltip" in css


class TestTableReferenceHover:
    """Hovering over a Notable Papers row shows its source references."""

    def test_table_row_has_source_tooltip(self, client):
        """Given a Notable Papers row citing [3],
        when I view the brief,
        then the row contains a tooltip with the resolved source text."""
        today = datetime.now().strftime("%Y-%m-%d")
        resp = client.get(f"/brief/{today}-agentic-systems")
        html = resp.data.decode()
        assert "arXiv" in html.split('class="item-row"')[1].split("</tr>")[0]
        assert 'class="source-tooltip"' in html.split('class="item-row"')[1].split("</tr>")[0]


class TestItemKeys:
    """Each item in a rendered brief has a data-item-key attribute."""

    def test_key_developments_have_item_keys(self, client):
        """Given a brief with 2 Key Developments,
        when I view the brief,
        then they have data-item-key='key-developments/0' and 'key-developments/1'."""
        today = datetime.now().strftime("%Y-%m-%d")
        resp = client.get(f"/brief/{today}-agentic-systems")
        html = resp.data.decode()
        assert 'data-item-key="key-developments/0"' in html
        assert 'data-item-key="key-developments/1"' in html

    def test_landscape_trends_have_item_keys(self, client):
        """Given a brief with 2 Landscape Trends,
        when I view the brief,
        then they have data-item-key='landscape-trends/0' and 'landscape-trends/1'."""
        today = datetime.now().strftime("%Y-%m-%d")
        resp = client.get(f"/brief/{today}-agentic-systems")
        html = resp.data.decode()
        assert 'data-item-key="landscape-trends/0"' in html
        assert 'data-item-key="landscape-trends/1"' in html

    def test_notable_papers_rows_have_item_keys(self, client):
        """Given a brief with a Notable Papers table,
        when I view the brief,
        then each row has data-item-key='notable-papers/0'."""
        today = datetime.now().strftime("%Y-%m-%d")
        resp = client.get(f"/brief/{today}-agentic-systems")
        html = resp.data.decode()
        assert 'data-item-key="notable-papers/0"' in html

    def test_deep_dive_has_item_key(self, client):
        """Given a brief with a Technical Deep-Dive,
        when I view the brief,
        then it has data-item-key='technical-deep-dive/0'."""
        today = datetime.now().strftime("%Y-%m-%d")
        resp = client.get(f"/brief/{today}-agentic-systems")
        html = resp.data.decode()
        assert 'data-item-key="technical-deep-dive/0"' in html


class TestAnnotation:
    """Annotating items in a brief."""

    def test_post_saves_annotation(self, client, briefs_dir):
        """Given a brief exists,
        when I POST an annotation,
        then it is saved to annotations.json."""
        import json
        today = datetime.now().strftime("%Y-%m-%d")
        dirname = f"{today}-agentic-systems"
        resp = client.post(
            f"/brief/{dirname}/annotate",
            json={"item_key": "key-developments/0", "interesting": True},
        )
        assert resp.status_code == 200
        annotations = json.loads((briefs_dir / dirname / "annotations.json").read_text())
        assert annotations["key-developments/0"]["interesting"] is True

    def test_post_toggles_annotation(self, client, briefs_dir):
        """Given an annotation exists,
        when I POST a different value,
        then it is updated."""
        today = datetime.now().strftime("%Y-%m-%d")
        dirname = f"{today}-agentic-systems"
        client.post(f"/brief/{dirname}/annotate", json={"item_key": "key-developments/0", "interesting": True})
        client.post(f"/brief/{dirname}/annotate", json={"item_key": "key-developments/0", "interesting": False})
        import json
        annotations = json.loads((briefs_dir / dirname / "annotations.json").read_text())
        assert annotations["key-developments/0"]["interesting"] is False

    def test_post_returns_404_for_nonexistent_brief(self, client):
        """Given no brief directory exists,
        when I POST an annotation,
        then I get 404."""
        resp = client.post("/brief/nonexistent/annotate", json={"item_key": "key-developments/0", "interesting": True})
        assert resp.status_code == 404


class TestAnnotationDisplay:
    """Viewing briefs reflects saved annotations."""

    def test_annotated_item_has_interesting_attribute(self, client, briefs_dir):
        """Given an item is annotated as interesting,
        when I view the brief,
        then the item has data-interesting='true'."""
        import json
        today = datetime.now().strftime("%Y-%m-%d")
        dirname = f"{today}-agentic-systems"
        ann_path = briefs_dir / dirname / "annotations.json"
        ann_path.write_text(json.dumps({"key-developments/0": {"interesting": True}}))

        resp = client.get(f"/brief/{today}-agentic-systems")
        html = resp.data.decode()
        assert 'data-interesting="true"' in html

    def test_brief_page_includes_js(self, client):
        """Given a brief page,
        when I view it,
        then it includes brief.js for interactivity."""
        today = datetime.now().strftime("%Y-%m-%d")
        resp = client.get(f"/brief/{today}-agentic-systems")
        html = resp.data.decode()
        assert "brief.js" in html


class TestSyncButtons:
    """Pull and Save & Push buttons on the queue page."""

    def test_queue_page_has_pull_button(self, client):
        """Given the queue page,
        when I load it,
        then a Pull button is present."""
        resp = client.get("/")
        assert b"Pull" in resp.data

    def test_queue_page_has_save_push_button(self, client):
        """Given the queue page,
        when I load it,
        then a Save & Push button is present."""
        resp = client.get("/")
        assert b"Save" in resp.data and b"Push" in resp.data

    def test_sync_pull_route_exists(self, client):
        """Given the sync pull route,
        when I POST to it,
        then it returns 200 with ok=True."""
        from unittest.mock import patch
        with patch("git_sync.subprocess.run") as mock_run:
            from unittest.mock import MagicMock
            mock_run.return_value = MagicMock(stdout="Already up to date.\n", stderr="")
            resp = client.post("/sync/pull")
        assert resp.status_code == 200
        assert resp.get_json()["ok"] is True

    def test_sync_push_route_exists(self, client):
        """Given the sync push route,
        when I POST to it,
        then it returns 200 with ok=True."""
        from unittest.mock import patch, MagicMock
        with patch("git_sync.subprocess.run") as mock_run:
            mock_run.side_effect = [
                MagicMock(),  # git add
                MagicMock(returncode=0),  # git diff (nothing to commit)
            ]
            resp = client.post("/sync/push")
        assert resp.status_code == 200
        assert resp.get_json()["ok"] is True


class TestBriefTables:
    """Rendering markdown tables in briefs."""

    def test_tables_render_as_html_tables(self, client):
        """Given a brief with a markdown table,
        when I view the brief,
        then it renders as an HTML table element."""
        today = datetime.now().strftime("%Y-%m-%d")
        resp = client.get(f"/brief/{today}-agentic-systems")
        html = resp.data.decode()
        assert "<table>" in html


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

    def test_unreviewed_brief_has_no_reviewed_class(self, client):
        """Given a brief has no annotations,
        when I visit the queue,
        then that brief's list item does not have the 'reviewed' class."""
        resp = client.get("/")
        html = resp.data.decode()
        assert 'class="brief-item"' in html
        # Make sure not all items got the reviewed class
        assert 'brief-item reviewed' not in html

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

    def test_unreviewed_brief_has_empty_reviewed_attribute(self, client):
        """Given a brief has not been reviewed,
        when I view the brief,
        then data-reviewed is empty."""
        today = datetime.now().strftime("%Y-%m-%d")
        resp = client.get(f"/brief/{today}-agentic-systems")
        html = resp.data.decode()
        assert 'data-reviewed=""' in html

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


class TestExtractStarredItems:
    """Extracting starred items from a brief's markdown."""

    def test_extracts_starred_key_development(self):
        """Given brief markdown with 2 Key Developments and KD 0 starred,
        when extract_starred_items is called,
        then it returns only the first KD under 'Key Developments'."""
        import app as app_module

        md = (
            "# Topic — Research Brief (2026-06-14)\n\n"
            "## Key Developments\n\n"
            "- **[First headline]**\n"
            "  - **What changed:** Something happened.\n"
            "  - **Why it matters:** It is important.\n"
            "  - *Sources: [1]*\n\n"
            "- **[Second headline]**\n"
            "  - **What changed:** Another thing.\n"
            "  - **Why it matters:** Also important.\n"
            "  - *Sources: [2]*\n\n"
            "## Sources\n\n"
            "1. Source one\n"
            "2. Source two\n"
        )
        annotations = {"key-developments/0": {"interesting": True}}
        result = app_module.extract_starred_items(md, annotations)
        assert "Key Developments" in result
        assert len(result["Key Developments"]) == 1
        assert "First headline" in result["Key Developments"][0]
        assert "Second headline" not in result["Key Developments"][0]

    def test_extracts_starred_landscape_trend(self):
        """Given brief markdown with 2 Landscape Trends and trend 1 starred,
        when extract_starred_items is called,
        then it returns only the second trend under 'Landscape Trends'."""
        import app as app_module

        md = (
            "# Topic — Research Brief (2026-06-14)\n\n"
            "## Landscape Trends\n\n"
            "- **First trend.** Details.\n\n"
            "- **Second trend.** More details.\n\n"
            "## Sources\n\n"
            "1. A source\n"
        )
        annotations = {"landscape-trends/1": {"interesting": True}}
        result = app_module.extract_starred_items(md, annotations)
        assert "Landscape Trends" in result
        assert len(result["Landscape Trends"]) == 1
        assert "Second trend" in result["Landscape Trends"][0]

    def test_extracts_starred_notable_paper(self):
        """Given a brief with a Notable Papers table and row 0 starred,
        when extract_starred_items is called,
        then it returns the table header and the starred row."""
        import app as app_module

        md = (
            "# Topic — Research Brief (2026-06-14)\n\n"
            "## Notable Papers / Models / Tools\n\n"
            "| Item | Date | Source | Summary |\n"
            "|------|------|--------|---------|\n"
            "| Paper A | Jun 2026 | [1] | Summary A |\n"
            "| Paper B | Jun 2026 | [2] | Summary B |\n\n"
            "## Sources\n\n"
            "1. Source one\n"
            "2. Source two\n"
        )
        annotations = {"notable-papers/0": {"interesting": True}}
        result = app_module.extract_starred_items(md, annotations)
        assert "Notable Papers / Models / Tools" in result
        assert len(result["Notable Papers / Models / Tools"]) == 1
        assert "Paper A" in result["Notable Papers / Models / Tools"][0]
        assert "Paper B" not in result["Notable Papers / Models / Tools"][0]

    def test_extracts_starred_deep_dive(self):
        """Given a brief with a Technical Deep-Dive and it is starred,
        when extract_starred_items is called,
        then it returns the deep dive content."""
        import app as app_module

        md = (
            "# Topic — Research Brief (2026-06-14)\n\n"
            "## Technical Deep-Dive\n\n"
            "### Some Heading\n\n"
            "Deep dive content here.\n\n"
            "## Sources\n\n"
            "1. A source\n"
        )
        annotations = {"technical-deep-dive/0": {"interesting": True}}
        result = app_module.extract_starred_items(md, annotations)
        assert "Technical Deep-Dive" in result
        assert "Deep dive content" in result["Technical Deep-Dive"][0]

    def test_returns_empty_when_nothing_starred(self):
        """Given brief markdown with no starred annotations,
        when extract_starred_items is called,
        then it returns an empty dict."""
        import app as app_module

        md = (
            "# Topic — Research Brief (2026-06-14)\n\n"
            "## Key Developments\n\n"
            "- **[A headline]**\n"
            "  - **What changed:** Something.\n\n"
            "## Sources\n\n"
            "1. A source\n"
        )
        annotations = {}
        result = app_module.extract_starred_items(md, annotations)
        assert result == {}

    def test_ignores_reviewed_annotation(self):
        """Given only a _reviewed annotation,
        when extract_starred_items is called,
        then it returns an empty dict (reviewed is not a starred item)."""
        import app as app_module

        md = (
            "# Topic — Research Brief (2026-06-14)\n\n"
            "## Key Developments\n\n"
            "- **[A headline]**\n"
            "  - **What changed:** Something.\n\n"
            "## Sources\n\n"
            "1. A source\n"
        )
        annotations = {"_reviewed": {"interesting": True}}
        result = app_module.extract_starred_items(md, annotations)
        assert result == {}

    def test_includes_resolved_references(self):
        """Given a starred KD citing [1] and [2],
        when extract_starred_items is called,
        then the item text includes the resolved source lines."""
        import app as app_module

        md = (
            "# Topic — Research Brief (2026-06-14)\n\n"
            "## Key Developments\n\n"
            "- **[First headline]**\n"
            "  - **What changed:** Something happened.\n"
            "  - **Why it matters:** It is important.\n"
            "  - *Sources: [1], [2]*\n\n"
            "## Sources\n\n"
            "1. AISI Report (Jun 2026) — https://example.com/aisi [Tier 1 — Research]\n"
            "2. TechCrunch (Jun 2026) — https://example.com/tc [Tier 2 — News]\n"
        )
        annotations = {"key-developments/0": {"interesting": True}}
        result = app_module.extract_starred_items(md, annotations)
        item = result["Key Developments"][0]
        assert "https://example.com/aisi" in item
        assert "https://example.com/tc" in item
        assert "AISI Report" in item

    def test_references_not_duplicated_from_other_items(self):
        """Given two KDs citing different sources and only KD 1 starred,
        when extract_starred_items is called,
        then only KD 1's references appear, not KD 0's."""
        import app as app_module

        md = (
            "# Topic — Research Brief (2026-06-14)\n\n"
            "## Key Developments\n\n"
            "- **[First headline]**\n"
            "  - *Sources: [1]*\n\n"
            "- **[Second headline]**\n"
            "  - *Sources: [2]*\n\n"
            "## Sources\n\n"
            "1. Source one — https://example.com/one\n"
            "2. Source two — https://example.com/two\n"
        )
        annotations = {"key-developments/1": {"interesting": True}}
        result = app_module.extract_starred_items(md, annotations)
        item = result["Key Developments"][0]
        assert "Source two" in item
        assert "Source one" not in item


class TestCompileWeeklyMarkdown:
    """Compiling starred items across briefs into a single markdown document."""

    def test_compiles_starred_items_from_multiple_briefs(self, client, briefs_dir):
        """Given two briefs with starred annotations,
        when compile_weekly_markdown is called,
        then it returns markdown with starred items grouped by brief."""
        import json
        import app as app_module

        today = datetime.now().strftime("%Y-%m-%d")
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

        (briefs_dir / f"{today}-agentic-systems" / "annotations.json").write_text(
            json.dumps({"key-developments/0": {"interesting": True}})
        )
        (briefs_dir / f"{yesterday}-models-and-market" / "annotations.json").write_text(
            json.dumps({"key-developments/0": {"interesting": True}})
        )

        result = app_module.compile_weekly_markdown()
        assert "Weekly Research Compilation" in result
        assert "Agentic Systems" in result
        assert "Models" in result
        assert "First KD headline" in result
        assert "Some headline" in result

    def test_skips_briefs_with_no_starred_items(self, client, briefs_dir):
        """Given one brief with starred items and one without,
        when compile_weekly_markdown is called,
        then only the brief with starred items appears."""
        import json
        import app as app_module

        today = datetime.now().strftime("%Y-%m-%d")

        (briefs_dir / f"{today}-agentic-systems" / "annotations.json").write_text(
            json.dumps({"key-developments/0": {"interesting": True}})
        )

        result = app_module.compile_weekly_markdown()
        assert "Agentic Systems" in result
        assert "Models" not in result

    def test_returns_empty_message_when_nothing_starred(self, client, briefs_dir):
        """Given no briefs have starred items,
        when compile_weekly_markdown is called,
        then it returns a document indicating no starred items."""
        import app as app_module

        result = app_module.compile_weekly_markdown()
        assert "Weekly Research Compilation" in result
        assert "No starred items" in result

    def test_includes_date_range_in_heading(self, client, briefs_dir):
        """Given briefs from today and yesterday,
        when compile_weekly_markdown is called,
        then the heading includes the date range."""
        import json
        import app as app_module

        today = datetime.now().strftime("%Y-%m-%d")
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

        (briefs_dir / f"{today}-agentic-systems" / "annotations.json").write_text(
            json.dumps({"key-developments/0": {"interesting": True}})
        )

        result = app_module.compile_weekly_markdown()
        assert yesterday in result
        assert today in result


class TestWeeklyCompilationRoute:
    """GET /compilation/weekly returns a downloadable markdown file."""

    def test_returns_markdown_file(self, client, briefs_dir):
        """Given briefs with starred items exist,
        when I GET /compilation/weekly,
        then I get a 200 with a markdown file download."""
        import json

        today = datetime.now().strftime("%Y-%m-%d")
        (briefs_dir / f"{today}-agentic-systems" / "annotations.json").write_text(
            json.dumps({"key-developments/0": {"interesting": True}})
        )

        resp = client.get("/compilation/weekly")
        assert resp.status_code == 200
        assert resp.content_type == "text/markdown; charset=utf-8"
        assert "attachment" in resp.headers.get("Content-Disposition", "")
        assert "weekly-compilation-" in resp.headers.get("Content-Disposition", "")
        assert ".md" in resp.headers.get("Content-Disposition", "")

    def test_body_contains_starred_items(self, client, briefs_dir):
        """Given a brief with a starred KD,
        when I GET /compilation/weekly,
        then the response body contains that item."""
        import json

        today = datetime.now().strftime("%Y-%m-%d")
        (briefs_dir / f"{today}-agentic-systems" / "annotations.json").write_text(
            json.dumps({"key-developments/0": {"interesting": True}})
        )

        resp = client.get("/compilation/weekly")
        body = resp.data.decode()
        assert "First KD headline" in body

    def test_empty_compilation_still_downloads(self, client, briefs_dir):
        """Given no starred items,
        when I GET /compilation/weekly,
        then I still get a 200 with the empty-state message."""
        resp = client.get("/compilation/weekly")
        assert resp.status_code == 200
        assert "No starred items" in resp.data.decode()


class TestWeeklyCompilationButton:
    """Download button on the queue page."""

    def test_queue_page_has_compilation_link(self, client):
        """Given the queue page,
        when I load it,
        then there is a link to /compilation/weekly."""
        resp = client.get("/")
        html = resp.data.decode()
        assert '/compilation/weekly' in html


class TestFreeTextAnnotation:
    """Free-text annotation on items."""

    def test_saved_text_appears_as_data_attribute(self, client, briefs_dir):
        """Given an item has a text annotation saved,
        when I view the brief,
        then the item has a data-text attribute with the saved text."""
        import json
        today = datetime.now().strftime("%Y-%m-%d")
        dirname = f"{today}-agentic-systems"
        ann_path = briefs_dir / dirname / "annotations.json"
        ann_path.write_text(json.dumps({
            "key-developments/0": {"interesting": True, "text": "This is my reaction."}
        }))

        resp = client.get(f"/brief/{dirname}")
        html = resp.data.decode()
        assert 'data-text="This is my reaction."' in html

    def test_post_text_annotation_saves(self, client, briefs_dir):
        """Given a brief exists,
        when I POST an annotation with a text field,
        then the text is saved to annotations.json."""
        import json
        today = datetime.now().strftime("%Y-%m-%d")
        dirname = f"{today}-agentic-systems"
        resp = client.post(
            f"/brief/{dirname}/annotate",
            json={"item_key": "key-developments/0", "text": "My note here"},
        )
        assert resp.status_code == 200
        annotations = json.loads((briefs_dir / dirname / "annotations.json").read_text())
        assert annotations["key-developments/0"]["text"] == "My note here"

    def test_empty_text_not_in_data_attribute(self, client, briefs_dir):
        """Given an item has no text annotation,
        when I view the brief,
        then the item does not have a data-text attribute."""
        today = datetime.now().strftime("%Y-%m-%d")
        resp = client.get(f"/brief/{today}-agentic-systems")
        html = resp.data.decode()
        assert 'data-text=' not in html

    def test_brief_page_includes_annotation_panel_css(self, client):
        """Given CSS is loaded,
        when the stylesheet is fetched,
        then annotation-panel styles are defined."""
        resp = client.get("/static/style.css")
        css = resp.data.decode()
        assert ".annotation-panel" in css
