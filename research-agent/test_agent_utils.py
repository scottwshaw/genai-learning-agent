"""Tests for agent_utils brief directory support."""

from pathlib import Path

import pytest

from agent_utils import previous_brief_date, recent_briefs_context


class TestPreviousBriefDate:
    """Finding the most recent brief date for a topic."""

    def test_finds_date_from_directory_layout(self, tmp_path):
        """Given a brief in directory layout,
        when previous_brief_date is called,
        then it returns the date from the directory name."""
        d = tmp_path / "2026-06-04-safety-assurance"
        d.mkdir()
        (d / "brief.md").write_text("# Brief")

        result = previous_brief_date(tmp_path, "safety-assurance")

        assert result == "2026-06-04"

    def test_returns_latest_when_multiple_exist(self, tmp_path):
        """Given multiple briefs for a topic,
        when previous_brief_date is called,
        then it returns the most recent date."""
        for date in ["2026-06-01", "2026-06-04"]:
            d = tmp_path / f"{date}-safety-assurance"
            d.mkdir()
            (d / "brief.md").write_text("# Brief")

        result = previous_brief_date(tmp_path, "safety-assurance")

        assert result == "2026-06-04"


class TestRecentBriefsContext:
    """Loading recent briefs for prompt context."""

    def test_loads_briefs_from_directory_layout(self, tmp_path):
        """Given briefs in directory layout,
        when recent_briefs_context is called,
        then it returns their content with directory names as headings."""
        d = tmp_path / "2026-06-04-safety-assurance"
        d.mkdir()
        (d / "brief.md").write_text(
            "# Safety Brief\n\n"
            "## Notable Papers / Models / Tools\n\n"
            "| Item | Summary |\n|------|------|\n| Paper A | Good |\n"
        )

        count, content = recent_briefs_context(tmp_path)

        assert count == 1
        assert "2026-06-04-safety-assurance" in content
        assert "Paper A" in content
