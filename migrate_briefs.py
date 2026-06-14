#!/usr/bin/env python3
"""Migrate flat brief .md files into per-brief directories."""

import sys
from pathlib import Path


def migrate_briefs(briefs_dir: Path):
    for f in sorted(briefs_dir.glob("*.md")):
        dest_dir = briefs_dir / f.stem
        dest_dir.mkdir(exist_ok=True)
        f.rename(dest_dir / "brief.md")


if __name__ == "__main__":
    briefs_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("briefs")
    migrate_briefs(briefs_dir)
    print(f"Migrated briefs in {briefs_dir}")
