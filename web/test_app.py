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

    (tmp_path / f"{today}-agentic-systems.md").write_text(
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
        "| Paper A | May 2026 | [arXiv](https://example.com/paper-a) | A summary |\n\n"
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
    (tmp_path / f"{yesterday}-models-and-market.md").write_text(
        "# Models & Market — Research Brief\n\n"
        "## Key Developments\n\n"
        "- **[Some headline]**\n"
        "  - **What changed:** Something.\n"
        "  - **Why it matters:** Important.\n"
        "  - *(TechCrunch, May 2026)*\n\n"
        "## Sources\n\n"
        "- https://example.com/old-source [Tier 2 — Tech news]\n"
    )
    (tmp_path / f"{old}-enterprise-genai-adoption.md").write_text("# Old brief\n\nStale.")

    return tmp_path


@pytest.fixture
def client(briefs_dir):
    os.environ["BRIEFS_DIR"] = str(briefs_dir)
    from app import app
    app.config["TESTING"] = True
    with app.test_client() as client:
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
        resp = client.get(f"/brief/{today}-agentic-systems.md")
        assert resp.status_code == 200
        html = resp.data.decode()
        assert "<h1>Agentic Systems" in html
        assert "Key Developments" in html

    def test_returns_404_for_nonexistent_brief(self, client):
        """Given no brief with this filename exists,
        when I visit its URL,
        then I get a 404."""
        resp = client.get("/brief/nonexistent.md")
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
        resp = client.get(f"/brief/{today}-agentic-systems.md")
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
        resp = client.get(f"/brief/{yesterday}-models-and-market.md")
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
        resp = client.get(f"/brief/{today}-agentic-systems.md")
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
        resp = client.get(f"/brief/{today}-agentic-systems.md")
        html = resp.data.decode()
        assert 'data-sources="' in html

    def test_item_source_data_contains_resolved_text(self, client):
        """Given a KD citing [1],
        when I view the brief,
        then its data-sources attribute contains the source text from entry 1."""
        today = datetime.now().strftime("%Y-%m-%d")
        resp = client.get(f"/brief/{today}-agentic-systems.md")
        html = resp.data.decode()
        assert "CNAS Report" in html.split('data-sources="')[1].split('"')[0]

    def test_source_data_includes_reference_number(self, client):
        """Given a KD citing [1],
        when I view the brief,
        then its data-sources attribute prefixes the source text with [1]."""
        today = datetime.now().strftime("%Y-%m-%d")
        resp = client.get(f"/brief/{today}-agentic-systems.md")
        html = resp.data.decode()
        first_attr = html.split('data-sources="')[1].split('"')[0]
        assert "[1]" in first_attr

    def test_hover_style_exists_for_source_tooltip(self, client):
        """Given CSS is loaded,
        when a source tooltip could appear,
        then a CSS rule for .source-tooltip exists."""
        resp = client.get("/static/style.css")
        css = resp.data.decode()
        assert ".source-tooltip" in css


class TestBriefTables:
    """Rendering markdown tables in briefs."""

    def test_tables_render_as_html_tables(self, client):
        """Given a brief with a markdown table,
        when I view the brief,
        then it renders as an HTML table element."""
        today = datetime.now().strftime("%Y-%m-%d")
        resp = client.get(f"/brief/{today}-agentic-systems.md")
        html = resp.data.decode()
        assert "<table>" in html
