"""Tests for brief directory migration."""

from pathlib import Path

import pytest

from migrate_briefs import migrate_briefs


class TestMigrateBriefs:
    """Migrating flat brief files into directories."""

    def test_moves_brief_into_directory(self, tmp_path):
        """Given a flat brief file exists,
        when migrate_briefs runs,
        then it moves into a directory as brief.md."""
        (tmp_path / "2026-06-04-safety-assurance.md").write_text("# Brief\nContent.")

        migrate_briefs(tmp_path)

        assert (tmp_path / "2026-06-04-safety-assurance" / "brief.md").read_text() == "# Brief\nContent."
        assert not (tmp_path / "2026-06-04-safety-assurance.md").exists()

    def test_skips_already_migrated(self, tmp_path):
        """Given a brief is already in directory form,
        when migrate_briefs runs,
        then it does nothing (idempotent)."""
        d = tmp_path / "2026-06-04-safety-assurance"
        d.mkdir()
        (d / "brief.md").write_text("# Brief\nContent.")

        migrate_briefs(tmp_path)

        assert (d / "brief.md").read_text() == "# Brief\nContent."

    def test_skips_non_brief_files(self, tmp_path):
        """Given non-brief files exist (e.g. .DS_Store),
        when migrate_briefs runs,
        then they are left alone."""
        (tmp_path / ".DS_Store").write_bytes(b"\x00\x00")
        (tmp_path / "2026-06-04-safety.md").write_text("# Brief")

        migrate_briefs(tmp_path)

        assert (tmp_path / ".DS_Store").exists()
        assert (tmp_path / "2026-06-04-safety" / "brief.md").exists()

    def test_migrates_multiple_briefs(self, tmp_path):
        """Given multiple flat brief files exist,
        when migrate_briefs runs,
        then all are migrated."""
        (tmp_path / "2026-06-04-safety.md").write_text("# Safety")
        (tmp_path / "2026-06-05-agentic.md").write_text("# Agentic")

        migrate_briefs(tmp_path)

        assert (tmp_path / "2026-06-04-safety" / "brief.md").read_text() == "# Safety"
        assert (tmp_path / "2026-06-05-agentic" / "brief.md").read_text() == "# Agentic"
