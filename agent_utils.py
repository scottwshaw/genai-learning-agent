#!/usr/bin/env python3
"""Shared helpers for research and evaluation workflows."""

from __future__ import annotations

import json
import re
import sys
import time
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path


DEFAULT_RUBRIC_PATH = Path(__file__).parent / "evaluation" / "daily-brief-rubric.md"


def retry_on_overload(fn, max_attempts=5, label="api"):
    """Retry a callable on HTTP 529 (API overloaded) with exponential backoff."""
    for attempt in range(max_attempts):
        try:
            return fn()
        except Exception as e:
            if getattr(e, "status_code", None) == 529 and attempt < max_attempts - 1:
                wait = 30 * (2 ** attempt)
                print(
                    f"[{label}] API overloaded (529), retrying in {wait}s "
                    f"(attempt {attempt + 1}/{max_attempts})...",
                    file=sys.stderr,
                    flush=True,
                )
                time.sleep(wait)
            else:
                raise
    raise RuntimeError(f"[{label}] All {max_attempts} retry attempts exhausted")


def load_rubric_dimensions(rubric_path: Path = DEFAULT_RUBRIC_PATH) -> list[dict]:
    """Load rubric dimensions from the YAML frontmatter of a rubric markdown file."""
    text = rubric_path.read_text()
    match = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not match:
        raise ValueError(f"No YAML frontmatter found in {rubric_path}")

    frontmatter = match.group(1)
    dimensions = []
    current: dict | None = None

    for line in frontmatter.splitlines():
        line = line.rstrip()
        if line.startswith("  - key:"):
            if current is not None:
                dimensions.append(current)
            current = {"key": line.split(":", 1)[1].strip()}
        elif current is not None and line.startswith("    label:"):
            current["label"] = line.split(":", 1)[1].strip().strip('"')
        elif current is not None and line.startswith("    weight:"):
            current["weight"] = int(line.split(":", 1)[1].strip())

    if current is not None:
        dimensions.append(current)

    if not dimensions:
        raise ValueError(f"No dimensions found in frontmatter of {rubric_path}")
    return dimensions


@dataclass
class Topic:
    index: int
    slug: str
    label: str
    focus: str
    count: int
    sources: list[dict] | None = None


def _load_topics(topics_file: Path) -> list[dict]:
    payload = json.loads(topics_file.read_text())
    topics = payload.get("topics", [])
    if not topics:
        raise ValueError(f"No topics found in {topics_file}")
    return topics


def current_topic_index(state_file: Path, topic_count: int) -> int:
    if not state_file.exists():
        return 0
    raw = state_file.read_text().strip()
    if raw.isdigit():
        idx = int(raw)
        if 0 <= idx < topic_count:
            return idx
    return 0


def resolve_topic(topics_file: Path, state_file: Path, requested: str | None = None) -> Topic:
    topics = _load_topics(topics_file)
    count = len(topics)

    if not requested:
        idx = current_topic_index(state_file, count)
    elif requested.isdigit():
        idx = int(requested) - 1
        if not 0 <= idx < count:
            raise ValueError(f"--topic {requested} is out of range (1-{count})")
    else:
        idx = next((i for i, topic in enumerate(topics) if topic["slug"] == requested), -1)
        if idx == -1:
            raise ValueError(f"Topic '{requested}' not found in {topics_file.name}")

    topic = topics[idx]
    return Topic(
        index=idx,
        slug=topic["slug"],
        label=topic["label"],
        focus=topic["focus"],
        count=count,
        sources=topic.get("sources"),
    )


def next_topic_index(topic: Topic) -> int:
    return (topic.index + 1) % topic.count


def previous_brief_date(briefs_dir: Path, topic_slug: str, fallback_days: int = 14) -> str:
    matches = sorted(briefs_dir.glob(f"*-{topic_slug}.md"))
    if matches:
        return matches[-1].name.removesuffix(f"-{topic_slug}.md")
    return (date.today() - timedelta(days=fallback_days)).isoformat()


def _summarize_brief(text: str) -> str:
    """Extract only Key Developments and Notable Papers/Models/Tools sections.

    Keeps the H1 title line and the two sections needed for deduplication.
    Drops Technical Deep-Dive, Landscape Trends, Vendor Landscape, and Sources.
    """
    lines = text.split("\n")
    out: list[str] = []
    # Keep sections whose H2 heading starts with these prefixes
    keep_prefixes = ("## Key Developments", "## Key Releases",
                     "## Notable Papers")
    keeping = False

    for line in lines:
        # Always keep the H1 title line
        if line.startswith("# ") and not line.startswith("## "):
            out.append(line)
            keeping = False
            continue
        # H2 heading: decide whether to keep this section
        if line.startswith("## "):
            keeping = any(line.startswith(p) for p in keep_prefixes)
        if keeping:
            out.append(line)

    return "\n".join(out).strip()


def recent_briefs_context(briefs_dir: Path, limit: int = 28) -> tuple[int, str]:
    briefs = sorted(briefs_dir.glob("*.md"))[-limit:]
    if not briefs:
        return 0, "(No prior briefs exist yet — this is the first run.)"

    parts = []
    for brief in briefs:
        summary = _summarize_brief(brief.read_text())
        parts.append(f"### {brief.stem}\n{summary}\n\n---\n")
    return len(briefs), "\n".join(parts).rstrip()


def render_research_prompt(
    prompt_template: Path,
    run_date: str,
    topic: Topic,
    previous_date: str,
    recent_count: int,
    recent_content: str,
) -> str:
    base = prompt_template.read_text()
    topic_sources = ""
    if topic.sources:
        lines = [f"- {s['name']} — {s['url']}" for s in topic.sources]
        topic_sources = "\n".join(lines)

    substitutions = {
        "{{DATE}}": run_date,
        "{{TOPIC_LABEL}}": topic.label,
        "{{PREVIOUS_BRIEF_DATE}}": previous_date,
        "{{TOPIC_FOCUS}}": topic.focus,
        "{{TOPIC_SOURCES}}": topic_sources,
    }
    for placeholder, value in substitutions.items():
        base = base.replace(placeholder, value)
    base = base.rstrip()
    return (
        f"{base}\n\n---\n\n"
        f"## CONTEXT: Recent Briefs (Last {recent_count} Runs Across All Topics)\n\n"
        "The following briefs represent what has already been covered in recent days.\n"
        "Use them to: avoid repeating developments already surfaced; track how trends are "
        "evolving across the full landscape; spot connections that cross topic boundaries.\n\n"
        f"{recent_content}\n"
    )


def ensure_learning_log(learning_log: Path, topics_file: Path) -> bool:
    if learning_log.exists():
        return False

    topics = _load_topics(topics_file)
    lines = [
        "# GenAI Learning Log",
        "",
        "Tracks daily research briefs to ensure broad topic coverage and avoid repetition.",
        "The agent rotates through the configured priority areas in round-robin order.",
        "",
        "## Priority Areas",
        "",
        "| # | Area | Focus |",
        "|---|------|-------|",
    ]
    for index, topic in enumerate(topics, start=1):
        lines.append(f"| {index} | {topic['label']} | {topic['focus']} |")
    lines += [
        "",
        "## Research History",
        "",
        "| Date | Topic | Brief |",
        "|------|-------|-------|",
        "",
    ]
    learning_log.write_text("\n".join(lines))
    return True


def compute_weighted_score(scores: dict, dimensions: list[dict]) -> float:
    total = 0.0
    for dim in dimensions:
        entry = scores.get(dim["key"], {})
        score = entry.get("score", 0) if isinstance(entry, dict) else 0
        total += score * dim["weight"] / 5
    return round(total, 1)


def format_score_report(result: dict, topic_label: str, brief_file: str, dimensions: list[dict]) -> str:
    scores = result["scores"]
    weighted = result.get("weighted_score", compute_weighted_score(scores, dimensions))

    lines = [
        f"# Brief Evaluation: {Path(brief_file).name}",
        f"**Topic:** {topic_label}",
        f"**Overall Score:** {weighted}/100",
        "",
        "## Scorecard",
        "| Dimension | Weight | Score | Pts |",
        "|-----------|--------|-------|-----|",
    ]
    for dim in dimensions:
        entry = scores.get(dim["key"], {})
        score = entry.get("score", "—") if isinstance(entry, dict) else "—"
        pts = round(score * dim["weight"] / 5, 1) if isinstance(score, int) else "—"
        lines.append(f"| {dim['label']} | {dim['weight']}% | {score}/5 | {pts} |")
    lines.append(f"| **TOTAL** | **100%** | | **{weighted}** |")

    lines += ["", "## Dimension Rationale"]
    for dim in dimensions:
        entry = scores.get(dim["key"], {})
        score = entry.get("score", "—") if isinstance(entry, dict) else "—"
        rationale = entry.get("rationale", "") if isinstance(entry, dict) else ""
        lines.append(f"**{dim['label']}** ({score}/5): {rationale}")
        lines.append("")

    lines += [
        "## Overall Assessment",
        result.get("overall_observations", ""),
        "",
        f"**Top Strength:** {result.get('top_strength', '')}",
        f"**Top Weakness:** {result.get('top_weakness', '')}",
    ]
    return "\n".join(lines)


def format_score_comparison_row(scores_a: dict, scores_b: dict, dim: dict) -> str:
    score_a = scores_a.get(dim["key"], {}).get("score", 0)
    score_b = scores_b.get(dim["key"], {}).get("score", 0)
    pts_a = round(score_a * dim["weight"] / 5, 1)
    pts_b = round(score_b * dim["weight"] / 5, 1)
    delta = round(pts_b - pts_a, 1)
    delta_str = f"+{delta}" if delta > 0 else str(delta)
    return (
        f"| {dim['label']} | {dim['weight']}% | {score_a}/5 | {pts_a} | "
        f"{score_b}/5 | {pts_b} | {delta_str} |"
    )


def render_comparison_markdown(
    session_id: str,
    topic_label: str,
    label_a: str,
    label_b: str,
    model_a: str,
    model_b: str,
    prompt_a: str,
    prompt_b: str,
    scoring_model: str,
    result_a: dict,
    result_b: dict,
    dimensions: list[dict],
) -> str:
    score_a = result_a["weighted_score"]
    score_b = result_b["weighted_score"]
    if score_a > score_b:
        winner = f"Run A ({label_a}) — {score_a} vs {score_b}"
    elif score_b > score_a:
        winner = f"Run B ({label_b}) — {score_b} vs {score_a}"
    else:
        winner = f"Tie — {score_a} each"

    lines = [
        f"# Eval Comparison — {session_id}",
        "",
        f"**Topic:** {topic_label}",
        f"**Winner:** {winner}",
        "",
        "## Configuration",
        "",
        "| | Run A | Run B |",
        "|--|-------|-------|",
        f"| Label | {label_a} | {label_b} |",
        f"| Model | {model_a} | {model_b} |",
        f"| Prompt | {prompt_a} | {prompt_b} |",
        "",
        "## Score Comparison",
        "",
        "| Dimension | Wt | A | A pts | B | B pts | Delta |",
        "|-----------|-----|---|-------|---|-------|-------|",
    ]
    for dim in dimensions:
        lines.append(format_score_comparison_row(result_a["scores"], result_b["scores"], dim))

    total_delta = round(score_b - score_a, 1)
    total_delta_str = f"+{total_delta}" if total_delta > 0 else str(total_delta)
    lines.append(f"| **TOTAL** | **100%** | | **{score_a}** | | **{score_b}** | **{total_delta_str}** |")
    lines += [
        "",
        f"## Run A — {label_a}",
        "",
        f"**Score:** {score_a}/100",
        "",
        f"**Top Strength:** {result_a.get('top_strength', '')}",
        "",
        f"**Top Weakness:** {result_a.get('top_weakness', '')}",
        "",
        f"**Overall:** {result_a.get('overall_observations', '')}",
        "",
        f"## Run B — {label_b}",
        "",
        f"**Score:** {score_b}/100",
        "",
        f"**Top Strength:** {result_b.get('top_strength', '')}",
        "",
        f"**Top Weakness:** {result_b.get('top_weakness', '')}",
        "",
        f"**Overall:** {result_b.get('overall_observations', '')}",
        "",
        "---",
        f"*Session: {session_id} | Scoring model: {scoring_model}*",
        "",
    ]
    return "\n".join(lines)


def render_eval_metadata_block(metadata: dict) -> str:
    ordered_keys = [
        "session_id",
        "recorded_at",
        "role",
        "topic_slug",
        "topic_label",
        "label",
        "model",
        "prompt_path",
        "prompt",
        "git_head",
        "prompt_git_commit",
        "prompt_git_status",
        "prompt_diff",
        "source_type",
        "source_file",
        "scoring_model",
    ]
    lines = ["<!-- eval-metadata"]
    for key in ordered_keys:
        value = metadata.get(key)
        if value not in (None, ""):
            lines.append(f"{key}: {value}")
    lines.append("-->")
    return "\n".join(lines)
