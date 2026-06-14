"""Tests for git sync operations."""

from pathlib import Path
from unittest.mock import call, patch, MagicMock

import pytest

import git_sync


class TestPull:
    """Pulling latest briefs from remote."""

    def test_pull_runs_git_pull(self, tmp_path):
        """Given a repo root,
        when pull() is called,
        then it runs git pull --ff-only origin main."""
        with patch("git_sync.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(stdout="Already up to date.\n", stderr="")
            result = git_sync.pull(tmp_path)
        mock_run.assert_called_once_with(
            ["git", "pull", "--ff-only", "origin", "main"],
            cwd=tmp_path,
            capture_output=True,
            text=True,
        )
        assert "Already up to date" in result

    def test_pull_returns_combined_output(self, tmp_path):
        """Given git pull produces output,
        when pull() is called,
        then the combined stdout+stderr is returned."""
        with patch("git_sync.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(stdout="1 file changed\n", stderr="warning: something\n")
            result = git_sync.pull(tmp_path)
        assert "1 file changed" in result
        assert "warning: something" in result


class TestCommitAndPush:
    """Committing and pushing annotation changes."""

    def test_nothing_to_commit_when_no_staged_changes(self, tmp_path):
        """Given no annotation files changed,
        when commit_and_push() is called,
        then it returns 'Nothing to commit.' without committing."""
        with patch("git_sync.subprocess.run") as mock_run:
            # git add succeeds, git diff --cached returns 0 (no changes)
            mock_run.side_effect = [
                MagicMock(),  # git add
                MagicMock(returncode=0),  # git diff --cached (no changes)
            ]
            result = git_sync.commit_and_push(tmp_path)
        assert result == "Nothing to commit."
        assert mock_run.call_count == 2

    def test_commits_and_pushes_when_changes_exist(self, tmp_path):
        """Given annotation files have changed,
        when commit_and_push() is called,
        then it stages, commits, and pushes."""
        with patch("git_sync.subprocess.run") as mock_run:
            mock_run.side_effect = [
                MagicMock(),  # git add
                MagicMock(returncode=1),  # git diff --cached (changes exist)
                MagicMock(),  # git commit
                MagicMock(stdout="pushed\n", stderr=""),  # git push
            ]
            result = git_sync.commit_and_push(tmp_path)

        calls = mock_run.call_args_list
        assert calls[0] == call(["git", "add", "--", "briefs/"], cwd=tmp_path, check=True)
        assert calls[2] == call(
            ["git", "commit", "-m", "annotate: save session"],
            cwd=tmp_path, check=True,
        )
        assert calls[3] == call(
            ["git", "push", "origin", "main"],
            cwd=tmp_path, capture_output=True, text=True, check=True,
        )
        assert "pushed" in result
