"""Tests for agent_utils brief directory support."""

from pathlib import Path

import httpx
import pytest

import agent_utils

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


class TestRetryOnOverload:
    """Retrying API calls that fail for recoverable reasons."""

    def test_retries_on_connection_reset(self, monkeypatch):
        """Given a call that raises a transport error once then succeeds,
        when it is retried,
        then the successful result is returned."""
        monkeypatch.setattr(agent_utils.time, "sleep", lambda s: None)
        calls = {"n": 0}

        def flaky():
            calls["n"] += 1
            if calls["n"] == 1:
                raise httpx.ReadError("[Errno 54] Connection reset by peer")
            return "ok"

        result = agent_utils.retry_on_overload(flaky, label="test")

        assert result == "ok"
        assert calls["n"] == 2

    def test_does_not_retry_other_errors(self, monkeypatch):
        """Given a call that raises a non-retryable error,
        when it runs,
        then the error propagates immediately."""
        monkeypatch.setattr(agent_utils.time, "sleep", lambda s: None)
        calls = {"n": 0}

        def broken():
            calls["n"] += 1
            raise ValueError("bad input")

        with pytest.raises(ValueError):
            agent_utils.retry_on_overload(broken, label="test")

        assert calls["n"] == 1

    def test_still_retries_on_529(self, monkeypatch):
        """Given a call that raises a 529 overload error once,
        when it is retried,
        then the successful result is returned."""
        monkeypatch.setattr(agent_utils.time, "sleep", lambda s: None)
        calls = {"n": 0}

        class Overloaded(Exception):
            status_code = 529

        def flaky():
            calls["n"] += 1
            if calls["n"] == 1:
                raise Overloaded()
            return "ok"

        result = agent_utils.retry_on_overload(flaky, label="test")

        assert result == "ok"
