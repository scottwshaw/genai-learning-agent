"""Git sync operations for annotation persistence.

Uses a PR-based workflow: annotations are committed to a long-lived
'annotations' branch with an open PR, rather than pushing directly to main.
"""

import os
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

BRANCH = "annotations"


def _load_gh_token() -> str:
    """Load GitHub PAT for gh CLI authentication."""
    path = "/run/secrets/github-pat"
    if os.path.exists(path):
        return open(path).read().strip()
    return os.environ.get("GH_TOKEN", "")


def _run(cmd, cwd, **kwargs):
    """Run a subprocess command with common defaults."""
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, **kwargs)


def pull(repo_root: Path = REPO_ROOT) -> str:
    """Fetch from origin and update the working tree.

    - On main: pull --ff-only origin main
    - On annotations: merge origin/main to pick up new briefs
    - If annotations branch was deleted remotely (PR merged): switch back to main
    """
    _run(["git", "fetch", "origin"], cwd=repo_root)

    branch = _run(
        ["git", "branch", "--show-current"], cwd=repo_root
    ).stdout.strip()

    if branch == BRANCH:
        # Check if the branch still exists on the remote
        ls = _run(
            ["git", "ls-remote", "--heads", "origin", BRANCH], cwd=repo_root
        )
        if ls.stdout.strip():
            # Branch exists remotely -- merge origin/main to pick up new briefs
            r = _run(
                ["git", "merge", "origin/main", "--no-edit"], cwd=repo_root
            )
            return r.stdout + r.stderr
        else:
            # Branch was deleted remotely (PR merged) -- switch back to main
            _run(["git", "checkout", "main"], cwd=repo_root)
            _run(["git", "branch", "-D", BRANCH], cwd=repo_root)
            r = _run(
                ["git", "pull", "--ff-only", "origin", "main"], cwd=repo_root
            )
            return r.stdout + r.stderr
    else:
        # On main (or any other branch) -- just pull
        r = _run(
            ["git", "pull", "--ff-only", "origin", "main"], cwd=repo_root
        )
        return r.stdout + r.stderr


def commit_and_push(repo_root: Path = REPO_ROOT) -> str:
    """Commit annotation changes and push via PR workflow.

    - If annotations branch exists on remote: check it out and push to it
    - If not: create a fresh branch from main, push, and open a PR
    """
    _run(["git", "fetch", "origin"], cwd=repo_root)

    # Check if annotations branch exists on remote
    ls = _run(
        ["git", "ls-remote", "--heads", "origin", BRANCH], cwd=repo_root
    )
    branch_exists_remotely = bool(ls.stdout.strip())

    if branch_exists_remotely:
        # Switch to annotations branch if not already on it
        current = _run(
            ["git", "branch", "--show-current"], cwd=repo_root
        ).stdout.strip()
        if current != BRANCH:
            _run(
                ["git", "checkout", BRANCH],
                cwd=repo_root, check=True,
            )
        _run(["git", "pull", "--ff-only", "origin", BRANCH], cwd=repo_root)
        _run(["git", "merge", "origin/main", "--no-edit"], cwd=repo_root)
    else:
        # Create fresh branch from up-to-date main
        _run(["git", "checkout", "main"], cwd=repo_root, check=True)
        _run(["git", "pull", "--ff-only", "origin", "main"], cwd=repo_root)
        _run(["git", "checkout", "-b", BRANCH], cwd=repo_root, check=True)

    # Stage and check for changes
    subprocess.run(["git", "add", "--", "briefs/"], cwd=repo_root, check=True)
    r = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=repo_root)
    if r.returncode == 0:
        return "Nothing to commit."

    # Commit and push
    subprocess.run(
        ["git", "commit", "-m", "annotate: save session"],
        cwd=repo_root, check=True,
    )
    out = _run(
        ["git", "push", "-u", "origin", BRANCH],
        cwd=repo_root, check=True,
    )

    # Create PR if this is a new branch
    if not branch_exists_remotely:
        token = _load_gh_token()
        env = {**os.environ, "GH_TOKEN": token} if token else None
        _run(
            [
                "gh", "pr", "create",
                "--title", "Annotations",
                "--body", "Accumulated annotation saves.",
                "--base", "main",
            ],
            cwd=repo_root,
            env=env,
        )

    return out.stdout + out.stderr
