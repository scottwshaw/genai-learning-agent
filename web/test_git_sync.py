"""Tests for git sync operations (PR-based workflow)."""

from pathlib import Path
from unittest.mock import call, patch, MagicMock

import pytest

import git_sync


def _mock_run(returncode=0, stdout="", stderr=""):
    """Build a MagicMock that looks like a CompletedProcess."""
    m = MagicMock()
    m.returncode = returncode
    m.stdout = stdout
    m.stderr = stderr
    return m


class TestPull:
    """Pulling latest briefs from remote."""

    def test_pull_fetches_and_pulls_main_when_on_main(self, tmp_path):
        """Given the repo is on the main branch,
        when pull() is called,
        then it fetches origin and does git pull --ff-only origin main."""
        with patch("git_sync.subprocess.run") as mock_run:
            mock_run.side_effect = [
                _mock_run(stdout=""),                          # git fetch
                _mock_run(stdout="main\n"),                    # git branch --show-current
                _mock_run(stdout="Already up to date.\n"),     # git pull --ff-only
            ]
            result = git_sync.pull(tmp_path)

        calls = mock_run.call_args_list
        assert calls[0] == call(
            ["git", "fetch", "origin"],
            cwd=tmp_path, capture_output=True, text=True,
        )
        assert calls[1] == call(
            ["git", "branch", "--show-current"],
            cwd=tmp_path, capture_output=True, text=True,
        )
        assert calls[2] == call(
            ["git", "pull", "--ff-only", "origin", "main"],
            cwd=tmp_path, capture_output=True, text=True,
        )
        assert "Already up to date" in result

    def test_pull_fetches_and_merges_main_when_on_annotations_branch(self, tmp_path):
        """Given the repo is on the annotations branch,
        when pull() is called,
        then it fetches origin and merges origin/main into the branch."""
        with patch("git_sync.subprocess.run") as mock_run:
            mock_run.side_effect = [
                _mock_run(),                                    # git fetch
                _mock_run(stdout="annotations\n"),              # git branch --show-current
                _mock_run(stdout="abc123\n"),                    # git ls-remote (branch exists)
                _mock_run(stdout="Merge made.\n"),              # git merge origin/main
            ]
            result = git_sync.pull(tmp_path)

        calls = mock_run.call_args_list
        assert calls[2] == call(
            ["git", "ls-remote", "--heads", "origin", "annotations"],
            cwd=tmp_path, capture_output=True, text=True,
        )
        assert calls[3] == call(
            ["git", "merge", "origin/main", "--no-edit"],
            cwd=tmp_path, capture_output=True, text=True,
        )
        assert "Merge made" in result

    def test_pull_switches_to_main_when_annotations_branch_deleted_remotely(self, tmp_path):
        """Given the repo is on annotations but that branch no longer exists on remote,
        when pull() is called,
        then it checks out main, deletes the local annotations branch, and pulls main."""
        with patch("git_sync.subprocess.run") as mock_run:
            mock_run.side_effect = [
                _mock_run(),                                    # git fetch
                _mock_run(stdout="annotations\n"),              # git branch --show-current
                _mock_run(stdout=""),                           # git ls-remote (branch gone)
                _mock_run(),                                    # git checkout main
                _mock_run(),                                    # git branch -D annotations
                _mock_run(stdout="Updated.\n"),                 # git pull --ff-only
            ]
            result = git_sync.pull(tmp_path)

        calls = mock_run.call_args_list
        assert calls[3] == call(
            ["git", "checkout", "main"],
            cwd=tmp_path, capture_output=True, text=True,
        )
        assert calls[4] == call(
            ["git", "branch", "-D", "annotations"],
            cwd=tmp_path, capture_output=True, text=True,
        )
        assert calls[5] == call(
            ["git", "pull", "--ff-only", "origin", "main"],
            cwd=tmp_path, capture_output=True, text=True,
        )
        assert "Updated" in result


class TestCommitAndPush:
    """Committing and pushing annotation changes via PR workflow."""

    def test_nothing_to_commit_when_no_staged_changes(self, tmp_path):
        """Given no annotation files changed,
        when commit_and_push() is called,
        then it returns 'Nothing to commit.' without committing."""
        with patch("git_sync.subprocess.run") as mock_run:
            mock_run.side_effect = [
                _mock_run(),                                    # git fetch
                _mock_run(stdout="abc123\n"),                   # git ls-remote (branch exists)
                _mock_run(stdout="annotations\n"),              # git branch --show-current
                _mock_run(),                                    # git pull --ff-only origin annotations
                _mock_run(),                                    # git merge origin/main
                _mock_run(),                                    # git add
                _mock_run(returncode=0),                        # git diff --cached (no changes)
            ]
            result = git_sync.commit_and_push(tmp_path)

        assert result == "Nothing to commit."

    def test_creates_new_branch_and_pr_when_no_remote_branch(self, tmp_path):
        """Given the annotations branch does not exist on the remote,
        when commit_and_push() is called with changes,
        then it creates a new branch, commits, pushes, and creates a PR."""
        with patch("git_sync.subprocess.run") as mock_run, \
             patch("git_sync._load_gh_token", return_value="ghp_test123"):
            mock_run.side_effect = [
                _mock_run(),                                    # git fetch
                _mock_run(stdout=""),                           # git ls-remote (no branch)
                _mock_run(),                                    # git checkout main
                _mock_run(),                                    # git pull --ff-only
                _mock_run(),                                    # git checkout -B annotations
                _mock_run(),                                    # git add
                _mock_run(returncode=1),                        # git diff --cached (has changes)
                _mock_run(),                                    # git commit
                _mock_run(stdout="pushed\n"),                   # git push -u
                _mock_run(stdout="https://github.com/…/pull/1\n"),  # gh pr create
            ]
            result = git_sync.commit_and_push(tmp_path)

        calls = mock_run.call_args_list
        # Should create a fresh branch from main
        assert calls[2] == call(
            ["git", "checkout", "main"],
            cwd=tmp_path, capture_output=True, text=True, check=True,
        )
        assert calls[4] == call(
            ["git", "checkout", "-B", "annotations"],
            cwd=tmp_path, capture_output=True, text=True, check=True,
        )
        # Should commit
        assert calls[7] == call(
            ["git", "commit", "-m", "annotate: save session"],
            cwd=tmp_path, check=True,
        )
        # Should push with -u
        assert calls[8] == call(
            ["git", "push", "-u", "origin", "annotations"],
            cwd=tmp_path, capture_output=True, text=True, check=True,
        )
        # Should create PR with gh
        gh_call = calls[9]
        assert gh_call[0][0][:3] == ["gh", "pr", "create"]
        assert "pushed" in result

    def test_pushes_to_existing_branch_without_creating_pr(self, tmp_path):
        """Given the annotations branch already exists on the remote,
        when commit_and_push() is called with changes,
        then it pushes to the existing branch without creating a new PR."""
        with patch("git_sync.subprocess.run") as mock_run:
            mock_run.side_effect = [
                _mock_run(),                                    # git fetch
                _mock_run(stdout="abc123\trefs/heads/annotations\n"),  # git ls-remote (exists)
                _mock_run(stdout="annotations\n"),              # git branch --show-current
                _mock_run(),                                    # git pull --ff-only origin annotations
                _mock_run(),                                    # git merge origin/main
                _mock_run(),                                    # git add
                _mock_run(returncode=1),                        # git diff --cached (has changes)
                _mock_run(),                                    # git commit
                _mock_run(stdout="pushed\n"),                   # git push -u
            ]
            result = git_sync.commit_and_push(tmp_path)

        calls = mock_run.call_args_list
        # Should NOT create a PR (only 9 calls, no gh pr create)
        assert len(calls) == 9
        assert "pushed" in result

    def test_fresh_branch_creation_survives_stale_local_branch(self, tmp_path):
        """Given the annotations branch was deleted remotely (PR merged)
        but a stale local annotations branch still exists,
        when commit_and_push() is called,
        then it uses checkout -B so branch creation resets the stale branch
        instead of failing with 'branch already exists'."""
        with patch("git_sync.subprocess.run") as mock_run, \
             patch("git_sync._load_gh_token", return_value="ghp_test123"):
            mock_run.side_effect = [
                _mock_run(),                                    # git fetch
                _mock_run(stdout=""),                           # git ls-remote (branch gone)
                _mock_run(),                                    # git checkout main
                _mock_run(),                                    # git pull --ff-only
                _mock_run(),                                    # git checkout -B annotations
                _mock_run(),                                    # git add
                _mock_run(returncode=1),                        # git diff --cached (has changes)
                _mock_run(),                                    # git commit
                _mock_run(stdout="pushed\n"),                   # git push -u
                _mock_run(stdout="https://github.com/…/pull/3\n"),  # gh pr create
            ]
            git_sync.commit_and_push(tmp_path)

        calls = mock_run.call_args_list
        assert calls[4] == call(
            ["git", "checkout", "-B", "annotations"],
            cwd=tmp_path, capture_output=True, text=True, check=True,
        )

    def test_creates_fresh_branch_after_previous_pr_merged(self, tmp_path):
        """Given the previous annotations branch was merged and deleted,
        when commit_and_push() is called,
        then it creates a fresh annotations branch from main."""
        with patch("git_sync.subprocess.run") as mock_run, \
             patch("git_sync._load_gh_token", return_value="ghp_test123"):
            mock_run.side_effect = [
                _mock_run(),                                    # git fetch
                _mock_run(stdout=""),                           # git ls-remote (branch gone)
                _mock_run(),                                    # git checkout main
                _mock_run(),                                    # git pull --ff-only
                _mock_run(),                                    # git checkout -B annotations
                _mock_run(),                                    # git add
                _mock_run(returncode=1),                        # git diff --cached (has changes)
                _mock_run(),                                    # git commit
                _mock_run(stdout="pushed\n"),                   # git push -u
                _mock_run(stdout="https://github.com/…/pull/2\n"),  # gh pr create
            ]
            result = git_sync.commit_and_push(tmp_path)

        calls = mock_run.call_args_list
        # Should create branch from main (same path as no remote branch)
        assert calls[2] == call(
            ["git", "checkout", "main"],
            cwd=tmp_path, capture_output=True, text=True, check=True,
        )
        assert calls[4] == call(
            ["git", "checkout", "-B", "annotations"],
            cwd=tmp_path, capture_output=True, text=True, check=True,
        )
        # Should create PR
        gh_call = calls[9]
        assert gh_call[0][0][:3] == ["gh", "pr", "create"]
