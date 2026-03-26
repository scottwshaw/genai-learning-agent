#!/usr/bin/env python3
"""Thin CLI for shared research/eval helpers."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from agent_utils import (
    compute_weighted_score,
    ensure_learning_log,
    next_topic_index,
    previous_brief_date,
    recent_briefs_context,
    render_comparison_markdown,
    render_research_prompt,
    resolve_topic,
)


def command_resolve_topic(args: argparse.Namespace) -> int:
    topic = resolve_topic(Path(args.topics_file), Path(args.state_file), args.topic)
    payload = {
        "index": topic.index,
        "next_index": next_topic_index(topic),
        "count": topic.count,
        "slug": topic.slug,
        "label": topic.label,
        "focus": topic.focus,
    }
    print(json.dumps(payload))
    return 0


def command_list_topics(args: argparse.Namespace) -> int:
    topics_file = Path(args.topics_file)
    state_file = Path(args.state_file)
    current = resolve_topic(topics_file, state_file, None)
    topics = json.loads(topics_file.read_text())["topics"]
    print("Topics (round-robin order):")
    for i, topic in enumerate(topics):
        marker = "  ->" if i == current.index else "    "
        suffix = "  [next]" if i == current.index else ""
        print(f"{marker} {i + 1}. {topic['label']}{suffix}")
    return 0


def command_ensure_learning_log(args: argparse.Namespace) -> int:
    created = ensure_learning_log(Path(args.learning_log), Path(args.topics_file))
    print(json.dumps({"created": created}))
    return 0


def command_render_prompt(args: argparse.Namespace) -> int:
    topic = resolve_topic(Path(args.topics_file), Path(args.state_file), args.topic)
    prev_date = previous_brief_date(Path(args.briefs_dir), topic.slug)
    recent_count, recent_content = recent_briefs_context(Path(args.briefs_dir))
    payload = {
        "previous_brief_date": prev_date,
        "recent_briefs_count": recent_count,
        "prompt": render_research_prompt(
            Path(args.prompt_template),
            args.date,
            topic,
            prev_date,
            recent_count,
            recent_content,
        ),
    }
    print(json.dumps(payload))
    return 0


def command_render_comparison(args: argparse.Namespace) -> int:
    result_a = json.loads(Path(args.scores_a).read_text())
    result_b = json.loads(Path(args.scores_b).read_text())
    result_a["weighted_score"] = result_a.get("weighted_score", compute_weighted_score(result_a["scores"]))
    result_b["weighted_score"] = result_b.get("weighted_score", compute_weighted_score(result_b["scores"]))
    output = render_comparison_markdown(
        session_id=args.session_id,
        topic_label=args.topic_label,
        label_a=args.label_a,
        label_b=args.label_b,
        model_a=args.model_a,
        model_b=args.model_b,
        prompt_a=Path(args.prompt_a).name,
        prompt_b=Path(args.prompt_b).name,
        scoring_model=args.scoring_model,
        result_a=result_a,
        result_b=result_b,
    )
    Path(args.output).write_text(output)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Shared CLI for research/eval helpers")
    subparsers = parser.add_subparsers(dest="command", required=True)

    resolve_topic_parser = subparsers.add_parser("resolve-topic")
    resolve_topic_parser.add_argument("--topics-file", required=True)
    resolve_topic_parser.add_argument("--state-file", required=True)
    resolve_topic_parser.add_argument("--topic")
    resolve_topic_parser.set_defaults(func=command_resolve_topic)

    list_topics_parser = subparsers.add_parser("list-topics")
    list_topics_parser.add_argument("--topics-file", required=True)
    list_topics_parser.add_argument("--state-file", required=True)
    list_topics_parser.set_defaults(func=command_list_topics)

    learning_log_parser = subparsers.add_parser("ensure-learning-log")
    learning_log_parser.add_argument("--learning-log", required=True)
    learning_log_parser.add_argument("--topics-file", required=True)
    learning_log_parser.set_defaults(func=command_ensure_learning_log)

    render_prompt_parser = subparsers.add_parser("render-prompt")
    render_prompt_parser.add_argument("--prompt-template", required=True)
    render_prompt_parser.add_argument("--briefs-dir", required=True)
    render_prompt_parser.add_argument("--date", required=True)
    render_prompt_parser.add_argument("--topics-file", required=True)
    render_prompt_parser.add_argument("--state-file", required=True)
    render_prompt_parser.add_argument("--topic")
    render_prompt_parser.set_defaults(func=command_render_prompt)

    comparison_parser = subparsers.add_parser("render-comparison")
    comparison_parser.add_argument("--session-id", required=True)
    comparison_parser.add_argument("--topic-label", required=True)
    comparison_parser.add_argument("--label-a", required=True)
    comparison_parser.add_argument("--label-b", required=True)
    comparison_parser.add_argument("--model-a", required=True)
    comparison_parser.add_argument("--model-b", required=True)
    comparison_parser.add_argument("--prompt-a", required=True)
    comparison_parser.add_argument("--prompt-b", required=True)
    comparison_parser.add_argument("--scoring-model", required=True)
    comparison_parser.add_argument("--scores-a", required=True)
    comparison_parser.add_argument("--scores-b", required=True)
    comparison_parser.add_argument("--output", required=True)
    comparison_parser.set_defaults(func=command_render_comparison)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
