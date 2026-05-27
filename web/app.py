#!/usr/bin/env python3
import json
import os
from datetime import datetime, timedelta
from pathlib import Path

from flask import Flask, abort, render_template
import mistune

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
BRIEFS_DIR = Path(os.environ.get("BRIEFS_DIR", str(BASE_DIR / "briefs")))
TOPICS_FILE = os.environ.get("TOPICS_FILE", str(BASE_DIR / "topics.json"))


def load_topic_labels():
    with open(TOPICS_FILE) as f:
        data = json.load(f)
    return {t["slug"]: t["label"] for t in data["topics"]}


TOPIC_LABELS = load_topic_labels()


def get_recent_briefs(days=7):
    cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    briefs = []
    for path in sorted(BRIEFS_DIR.glob("*.md")):
        parts = path.stem.split("-", 3)
        if len(parts) < 4:
            continue
        date = f"{parts[0]}-{parts[1]}-{parts[2]}"
        if date < cutoff:
            continue
        slug = parts[3]
        briefs.append({
            "filename": path.name,
            "date": date,
            "topic": TOPIC_LABELS.get(slug, slug),
        })
    return briefs


@app.route("/")
def queue():
    briefs = get_recent_briefs()
    return render_template("queue.html", briefs=briefs)


@app.route("/brief/<path:filename>")
def brief(filename):
    path = BRIEFS_DIR / filename
    if not path.is_file():
        abort(404)
    md = path.read_text()
    renderer = mistune.create_markdown(plugins=['url'])
    html = renderer(md)
    return render_template("brief.html", content=html, filename=filename)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
