"""Git sync operations for annotation persistence."""

import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def pull(repo_root: Path = REPO_ROOT) -> str:
    r = subprocess.run(
        ["git", "pull", "--ff-only", "origin", "main"],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )
    return r.stdout + r.stderr


def commit_and_push(repo_root: Path = REPO_ROOT) -> str:
    subprocess.run(["git", "add", "--", "briefs/"], cwd=repo_root, check=True)
    r = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=repo_root)
    if r.returncode == 0:
        return "Nothing to commit."
    subprocess.run(
        ["git", "commit", "-m", "annotate: save session"],
        cwd=repo_root,
        check=True,
    )
    out = subprocess.run(
        ["git", "push", "origin", "main"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=True,
    )
    return out.stdout + out.stderr
