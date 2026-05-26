#!/usr/bin/env python3
"""
score_brief.py — Score a research brief against the rubric using Claude.

Usage:
    python3 score_brief.py <brief_file> [options]

Options:
    --rubric FILE        Rubric file (default: evaluation/daily-brief-rubric.md)
    --topic-label LABEL  Topic label for context
    --output json|text   Output format (default: json)

Environment:
    ANTHROPIC_API_KEY    Required
    SCORING_MODEL        Model to use (default: claude-opus-4-6)
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

from agent_utils import compute_weighted_score, format_score_report, load_rubric_dimensions, retry_on_overload

try:
    import anthropic
except ImportError:
    print("ERROR: anthropic package not installed. Run: pip install anthropic", file=sys.stderr)
    sys.exit(1)


AUDIENCE_CONTEXT = """The intended reader is a senior ML engineer in regulated financial services who runs LLM \
observability, evaluation, and governance at enterprise scale. They care about:
- Tools, platforms, and practices for running and governing GenAI in production
- Standards stabilization events (e.g., OTel semconv going stable) that change procurement/integration decisions
- Compliance and regulatory implications of GenAI developments
- Interoperability milestones that reduce vendor lock-in
- Security advisories and breaking changes that require immediate attention
They do NOT care about: model training internals, low-level hardware, or academic novelty without operational impact."""


def build_scoring_prompt(brief: str, rubric: str, topic_label: str, dimensions: list[dict]) -> str:
    dim_lines = "\n".join(
        f'    "{d["key"]}": {{ "score": <1-5 integer>, "rationale": "<1-2 sentence justification>" }}'
        for d in dimensions
    )
    return f"""You are an expert evaluator assessing a GenAI research brief.

## Topic
{topic_label}

## Target Audience
{AUDIENCE_CONTEXT}

## Rubric
{rubric}

## Instructions
Score the brief on each rubric dimension using the 1-5 scale defined above. Judge the brief through the lens of the target audience — a development that is well-sourced but irrelevant to the reader's operational concerns should not score well on Audience Relevance or Operational Actionability.

Return ONLY a valid JSON object — no markdown fences, no extra prose.

## Required JSON format
{{
  "scores": {{
{dim_lines}
  }},
  "overall_observations": "<3-5 sentences on key strengths and weaknesses, judged against the target audience's needs>",
  "top_strength": "<the single most notable strength>",
  "top_weakness": "<the single most significant gap for the target reader>"
}}

## Brief to Evaluate
{brief}"""
def main():
    parser = argparse.ArgumentParser(description="Score a research brief using Claude")
    parser.add_argument("brief_file", help="Path to the brief markdown file")
    parser.add_argument("--rubric", default=None, help="Path to rubric file")
    parser.add_argument("--topic-label", default="(unknown topic)", help="Topic label")
    parser.add_argument("--output", choices=["json", "text"], default="json")
    args = parser.parse_args()

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("[ERROR] ANTHROPIC_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    model = os.environ.get("SCORING_MODEL", os.environ.get("ANTHROPIC_MODEL", "claude-opus-4-6"))

    rubric_path = Path(args.rubric or (Path(__file__).parent / "evaluation" / "daily-brief-rubric.md"))
    dimensions = load_rubric_dimensions(rubric_path)
    rubric = rubric_path.read_text()
    brief = Path(args.brief_file).read_text()

    prompt = build_scoring_prompt(brief, rubric, args.topic_label, dimensions)

    client = anthropic.Anthropic(api_key=api_key)
    print(f"[score_brief] Scoring with {model}...", file=sys.stderr)

    response = retry_on_overload(
        lambda: client.messages.create(
            model=model,
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}],
        ),
        label="scoring",
    )

    raw = response.content[0].text.strip()

    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw, re.DOTALL)
        if match:
            result = json.loads(match.group(1))
        else:
            print(f"[ERROR] Could not parse JSON from model response:\n{raw}", file=sys.stderr)
            sys.exit(1)

    result["weighted_score"] = compute_weighted_score(result["scores"], dimensions)
    result["brief_file"] = str(args.brief_file)
    result["topic_label"] = args.topic_label

    if args.output == "json":
        print(json.dumps(result, indent=2))
    else:
        print(format_score_report(result, args.topic_label, args.brief_file, dimensions))


if __name__ == "__main__":
    main()
