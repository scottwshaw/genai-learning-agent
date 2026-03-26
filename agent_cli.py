#!/usr/bin/env python3
"""Thin CLI for shared research/eval helpers."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from agent_utils import (
    compute_weighted_score,
    ensure_learning_log,
    format_score_report,
    next_topic_index,
    previous_brief_date,
    recent_briefs_context,
    render_comparison_markdown,
    render_eval_metadata_block,
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


def command_annotate_brief(args: argparse.Namespace) -> int:
    metadata = {
        "session_id": args.session_id,
        "recorded_at": args.recorded_at,
        "role": args.role,
        "topic_slug": args.topic_slug,
        "topic_label": args.topic_label,
        "label": args.label,
        "model": args.model,
        "prompt_path": args.prompt_path,
        "prompt": Path(args.prompt).name if args.prompt else "",
        "git_head": args.git_head,
        "prompt_git_commit": args.prompt_git_commit,
        "prompt_git_status": args.prompt_git_status,
        "prompt_diff": args.prompt_diff,
        "source_type": args.source_type,
        "source_file": args.source_file,
        "scoring_model": args.scoring_model,
    }
    brief_path = Path(args.brief)
    original = brief_path.read_text()
    annotated = f"{render_eval_metadata_block(metadata)}\n\n{original.lstrip()}"
    brief_path.write_text(annotated)
    metadata_path = Path(args.metadata_output)
    metadata_path.write_text(json.dumps(metadata, indent=2) + "\n")
    return 0


def command_render_score_report(args: argparse.Namespace) -> int:
    result = json.loads(Path(args.score_json).read_text())
    result["weighted_score"] = result.get("weighted_score", compute_weighted_score(result["scores"]))
    output = format_score_report(result, args.topic_label, args.brief_file)
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

    annotate_parser = subparsers.add_parser("annotate-brief")
    annotate_parser.add_argument("--brief", required=True)
    annotate_parser.add_argument("--metadata-output", required=True)
    annotate_parser.add_argument("--session-id", required=True)
    annotate_parser.add_argument("--recorded-at", required=True)
    annotate_parser.add_argument("--role", required=True)
    annotate_parser.add_argument("--topic-slug", required=True)
    annotate_parser.add_argument("--topic-label", required=True)
    annotate_parser.add_argument("--label", required=True)
    annotate_parser.add_argument("--model")
    annotate_parser.add_argument("--prompt")
    annotate_parser.add_argument("--prompt-path")
    annotate_parser.add_argument("--git-head")
    annotate_parser.add_argument("--prompt-git-commit")
    annotate_parser.add_argument("--prompt-git-status")
    annotate_parser.add_argument("--prompt-diff")
    annotate_parser.add_argument("--source-type", required=True)
    annotate_parser.add_argument("--source-file")
    annotate_parser.add_argument("--scoring-model", required=True)
    annotate_parser.set_defaults(func=command_annotate_brief)

    score_report_parser = subparsers.add_parser("render-score-report")
    score_report_parser.add_argument("--score-json", required=True)
    score_report_parser.add_argument("--brief-file", required=True)
    score_report_parser.add_argument("--topic-label", required=True)
    score_report_parser.add_argument("--output", required=True)
    score_report_parser.set_defaults(func=command_render_score_report)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
