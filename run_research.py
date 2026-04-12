#!/usr/bin/env python3
"""
run_research.py — Calls the Anthropic API with web search to generate a research brief.
Reads the research prompt from stdin, writes the final brief to stdout.
Diagnostic logs go to stderr (captured by research.sh into agent.log).

Setup:
    pip install anthropic

Environment variables:
    ANTHROPIC_API_KEY        (required)
    ANTHROPIC_MODEL          (optional, default: claude-sonnet-4-6)
    THINKING_BUDGET          (optional, default: 20000)
    MAX_TOKENS               (optional, default: 32000)
    ENABLE_CRITIC            (optional, set to "1" or "true" to enable critic loop)
    CRITIC_MODEL             (optional, default: same as ANTHROPIC_MODEL)
    CRITIC_THINKING_BUDGET   (optional, default: 8000)
"""

import json
import os
import re
import sys
import time
from pathlib import Path

try:
    import anthropic
except ImportError:
    print("ERROR: anthropic package not installed. Run: pip install anthropic", file=sys.stderr)
    sys.exit(1)

SCRIPT_DIR = Path(__file__).resolve().parent


def log(msg):
    print(f"[run_research] {msg}", file=sys.stderr, flush=True)


def extract_text(response) -> str:
    return "\n".join(
        block.text for block in response.content
        if getattr(block, "type", None) == "text"
    ).strip()


def strip_preamble(text_output: str) -> tuple[str, int]:
    """Anchor on the first line-start H1 heading and return (brief, preamble_len).

    ``^# \\S`` (hash, space, non-whitespace at line start) reliably matches a
    markdown H1 without colliding with inline ``#1``/``#2`` in reasoning prose.
    Returns the original text unchanged with preamble_len=0 if no H1 is found.
    """
    match = re.search(r"^# \S", text_output, re.MULTILINE)
    if match is None:
        return text_output, 0
    marker = match.start()
    return text_output[marker:].strip(), marker


def call_api(client, model, max_tokens, messages, thinking_budget,
             tools=None, label="api"):
    """Make an API call with retry-on-529 and streaming.

    Returns the final response message, or exits on exhausted retries.
    """
    kwargs = dict(
        model=model,
        max_tokens=max_tokens,
        thinking={"type": "enabled", "budget_tokens": thinking_budget},
        messages=messages,
    )
    if tools:
        kwargs["tools"] = tools

    response = None
    for attempt in range(5):
        try:
            with client.messages.stream(**kwargs) as stream:
                response = stream.get_final_message()
            break
        except anthropic.APIStatusError as e:
            if e.status_code == 529 and attempt < 4:
                wait = 30 * (2 ** attempt)
                log(f"[{label}] API overloaded (529), retrying in {wait}s (attempt {attempt + 1}/5)...")
                time.sleep(wait)
            else:
                raise

    if response is None:
        log(f"[{label}] ERROR: All retry attempts exhausted")
        sys.exit(1)

    return response


def load_prompt(name: str) -> str:
    """Load a prompt template from prompts/ directory."""
    path = SCRIPT_DIR / "prompts" / name
    return path.read_text()


CRITIC_TOOL = {
    "name": "report_violations",
    "description": "Report compliance violations found in the brief.",
    "input_schema": {
        "type": "object",
        "properties": {
            "pass": {
                "type": "boolean",
                "description": "True if no violations found, false otherwise.",
            },
            "violation_count": {
                "type": "integer",
                "description": "Number of violations found.",
            },
            "violations": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "rule": {
                            "type": "string",
                            "enum": [
                                "non_event_rule", "topic_boundary",
                                "format_structure", "word_count",
                                "sentence_simplicity", "source_tier_flag",
                                "quiet_week", "vendor_source_gate",
                                "cross_topic_requirement",
                                "prior_brief_callback",
                                "comparative_claim", "section_structure",
                            ],
                        },
                        "location": {"type": "string"},
                        "description": {"type": "string"},
                        "fix_suggestion": {"type": "string"},
                    },
                    "required": ["rule", "location", "description",
                                 "fix_suggestion"],
                },
            },
        },
        "required": ["pass", "violation_count", "violations"],
    },
}


def run_critic(client, model, brief, topic_label, topic_focus,
               thinking_budget) -> dict | None:
    """Check a brief against the compliance checklist using structured tool output."""
    template = load_prompt("critic-prompt.md")
    prompt = (template
              .replace("{{TOPIC_LABEL}}", topic_label)
              .replace("{{TOPIC_FOCUS}}", topic_focus)
              .replace("{{BRIEF}}", brief))

    messages = [{"role": "user", "content": prompt}]
    tools = [CRITIC_TOOL]

    log("Critic: running compliance check...")
    max_tokens = thinking_budget + 8192
    response = call_api(client, model, max_tokens, messages, thinking_budget,
                        tools=tools, label="critic")
    log(f"Critic: stop_reason={response.stop_reason}, blocks={len(response.content)}")

    # Extract the tool_use block with structured JSON
    for block in response.content:
        if getattr(block, "type", None) == "tool_use" and block.name == "report_violations":
            return block.input

    log("Critic: ERROR — no report_violations tool call in response")
    text = extract_text(response)
    if text:
        log(f"Critic: [text output head] {text[:500]}")
    return None


def run_revision(client, model, brief, violations_json, topic_label,
                 date_str, thinking_budget) -> str:
    """Revise a brief to fix specific violations. Returns revised brief text."""
    template = load_prompt("revision-prompt.md")
    prompt = (template
              .replace("{{TOPIC_LABEL}}", topic_label)
              .replace("{{DATE}}", date_str)
              .replace("{{VIOLATIONS}}", json.dumps(violations_json, indent=2))
              .replace("{{BRIEF}}", brief))

    messages = [{"role": "user", "content": prompt}]

    max_tokens = thinking_budget + 16000
    log("Revision: rewriting brief to fix violations...")
    response = call_api(client, model, max_tokens, messages, thinking_budget,
                        label="revision")
    log(f"Revision: stop_reason={response.stop_reason}, blocks={len(response.content)}")

    text = extract_text(response)
    revised, preamble_len = strip_preamble(text)
    if preamble_len > 0:
        log(f"Revision: [stripped preamble, {preamble_len} chars]")
    return revised


def generate_brief(client, model, prompt, max_tokens, thinking_budget, tools):
    """Run the main research loop (web search + generation). Returns brief text."""
    messages = [{"role": "user", "content": prompt}]

    for iteration in range(20):  # safety cap on agentic loop iterations
        log(f"API call #{iteration + 1}")

        response = call_api(client, model, max_tokens, messages,
                            thinking_budget, tools=tools, label="research")

        log(f"stop_reason={response.stop_reason}, blocks={len(response.content)}")
        text_output = extract_text(response)

        if response.stop_reason == "end_turn":
            brief, preamble_len = strip_preamble(text_output)
            if preamble_len == 0 and not text_output.lstrip().startswith("# "):
                log("ERROR: No H1 heading found in model output — refusing to write broken brief")
                log(f"[raw output head] {text_output[:1000]}")
                sys.exit(2)
            if preamble_len > 0:
                log(f"[stripped preamble, {preamble_len} chars] {text_output[:500]}")
            return brief

        if response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})

            tool_results = []
            for block in response.content:
                block_type = getattr(block, "type", None)
                if block_type == "tool_use":
                    log(f"tool_use: {block.name}({block.input})")
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": "",
                    })
                elif block_type == "tool_result":
                    log("tool_result block present in response (server-side execution)")

            if tool_results:
                messages.append({"role": "user", "content": tool_results})

        elif response.stop_reason == "max_tokens":
            log("WARNING: hit max_tokens — outputting partial response")
            brief, preamble_len = strip_preamble(text_output)
            if preamble_len > 0:
                log(f"[stripped preamble, {preamble_len} chars] {text_output[:500]}")
            return brief

        else:
            log(f"Unexpected stop_reason: {response.stop_reason} — outputting available text")
            brief, preamble_len = strip_preamble(text_output)
            if preamble_len > 0:
                log(f"[stripped preamble, {preamble_len} chars] {text_output[:500]}")
            return brief

    print("ERROR: Hit maximum iteration limit (20)", file=sys.stderr)
    sys.exit(1)


def critique_and_revise(client, brief, prompt, critic_model,
                        critic_thinking_budget):
    """Run critic→revise on a brief. Returns the (possibly revised) brief."""
    # Extract topic label and date from the brief's H1 line
    h1_match = re.match(r"^# (.+?) — Research Brief \((\d{4}-\d{2}-\d{2})\)",
                        brief)
    topic_label = h1_match.group(1) if h1_match else "Unknown"
    date_str = h1_match.group(2) if h1_match else ""

    # Extract topic focus from the original prompt if available
    topic_focus = ""
    if prompt:
        focus_match = re.search(r"Focus specifically on:\s*(.+?)(?:\n###|\n\n)",
                                prompt, re.DOTALL)
        topic_focus = focus_match.group(1).strip() if focus_match else ""

    critic_result = run_critic(client, critic_model, brief, topic_label,
                               topic_focus, critic_thinking_budget)

    if critic_result is None:
        log("Critic: failed to parse response — outputting original brief")
        return brief
    elif critic_result.get("pass", False) or critic_result.get("violation_count", 0) == 0:
        log("Critic: PASS — no violations found")
        return brief
    else:
        count = critic_result["violation_count"]
        violations = critic_result.get("violations", [])
        log(f"Critic: FAIL — {count} violation(s) found:")
        for v in violations:
            log(f"  [{v.get('rule', '?')}] {v.get('location', '?')}: "
                f"{v.get('description', '?')}")
        revised = run_revision(client, critic_model, brief, violations,
                               topic_label, date_str, critic_thinking_budget)
        log("Revision: complete — outputting revised brief")
        return revised


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Generate or critique a research brief")
    parser.add_argument("--brief", type=str, default=None,
                        help="Path to existing brief — skip generation, run critic only")
    args = parser.parse_args()

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY environment variable not set", file=sys.stderr)
        sys.exit(1)

    model = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-6")
    client = anthropic.Anthropic(api_key=api_key)

    enable_critic = os.environ.get("ENABLE_CRITIC", "").lower() in ("1", "true")
    critic_model = os.environ.get("CRITIC_MODEL", model)
    critic_thinking_budget = int(os.environ.get("CRITIC_THINKING_BUDGET", "8000"))

    if args.brief:
        # Critic-only mode: read existing brief, run critic→revise, output result
        brief_path = Path(args.brief)
        if not brief_path.exists():
            print(f"ERROR: {brief_path} not found", file=sys.stderr)
            sys.exit(1)
        brief = brief_path.read_text().strip()
        log(f"Critic-only mode: brief={args.brief}, model={critic_model}")
        brief = critique_and_revise(client, brief, "", critic_model,
                                    critic_thinking_budget)
        print(brief)
        return

    # Full generation mode: read prompt from stdin
    prompt = sys.stdin.read().strip()
    if not prompt:
        print("ERROR: No prompt received on stdin", file=sys.stderr)
        sys.exit(1)

    thinking_budget = int(os.environ.get("THINKING_BUDGET", "20000"))
    max_tokens = int(os.environ.get("MAX_TOKENS", "32000"))

    log(f"Starting: model={model}, prompt_chars={len(prompt)}, "
        f"thinking_budget={thinking_budget}, max_tokens={max_tokens}, "
        f"critic={'enabled (model=' + critic_model + ')' if enable_critic else 'disabled'}")

    tools = [{"type": "web_search_20250305", "name": "web_search"}]

    # --- Generate the brief ---
    brief = generate_brief(client, model, prompt, max_tokens,
                           thinking_budget, tools)

    # --- Critic loop (optional) ---
    if enable_critic:
        brief = critique_and_revise(client, brief, prompt, critic_model,
                                    critic_thinking_budget)

    print(brief)


if __name__ == "__main__":
    main()
