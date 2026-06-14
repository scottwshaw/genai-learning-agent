"""Annotation persistence for research briefs."""

import json
from pathlib import Path

ANNOTATIONS_FILE = "annotations.json"


def load_annotations(brief_dir: Path) -> dict:
    path = brief_dir / ANNOTATIONS_FILE
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def save_annotation(brief_dir: Path, item_key: str, data: dict) -> None:
    annotations = load_annotations(brief_dir)
    annotations[item_key] = data
    (brief_dir / ANNOTATIONS_FILE).write_text(json.dumps(annotations, indent=2) + "\n")
