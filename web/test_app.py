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
        "# Agentic Systems\n\nSome content.\n\n## Sources\n\n"
        "- https://example.com/paper1 [Tier 1 — Peer-reviewed]\n"
        "- https://example.com/paper2 [Tier 2 — Vendor announcement]\n"
    )
    (tmp_path / f"{yesterday}-models-and-market.md").write_text("# Models & Market\n\nMore content.")
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
        assert "<h1>Agentic Systems</h1>" in html
        assert "Some content." in html

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
        assert 'href="https://example.com/paper1"' in html
        assert 'href="https://example.com/paper2"' in html
