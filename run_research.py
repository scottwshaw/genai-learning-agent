#!/usr/bin/env python3
"""
run_research.py — Calls the Anthropic API with web search to generate a research brief.
Reads the research prompt from stdin, writes the final brief to stdout.
Diagnostic logs go to stderr (captured by research.sh into agent.log).

Setup:
    pip install anthropic

Environment variables:
    ANTHROPIC_API_KEY   (required)
    ANTHROPIC_MODEL     (optional, default: claude-sonnet-4-6)
"""

import os
import re
import sys
import time

try:
    import anthropic
except ImportError:
    print("ERROR: anthropic package not installed. Run: pip install anthropic", file=sys.stderr)
    sys.exit(1)


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


def main():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY environment variable not set", file=sys.stderr)
        sys.exit(1)

    prompt = sys.stdin.read().strip()
    if not prompt:
        print("ERROR: No prompt received on stdin", file=sys.stderr)
        sys.exit(1)

    model = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-6")
    client = anthropic.Anthropic(api_key=api_key)

    # Budget for extended thinking — keeps all deliberation out of the output text.
    # The extract_text() helper already filters to type=="text" blocks, so thinking
    # blocks are automatically excluded from the final brief.
    thinking_budget = int(os.environ.get("THINKING_BUDGET", "20000"))
    max_tokens = int(os.environ.get("MAX_TOKENS", "32000"))

    log(f"Starting: model={model}, prompt_chars={len(prompt)}, thinking_budget={thinking_budget}, max_tokens={max_tokens}")

    messages = [{"role": "user", "content": prompt}]

    # web_search_20250305 is a server-side tool — Anthropic executes searches on its
    # infrastructure; no separate search API key required on the client.
    tools = [{"type": "web_search_20250305", "name": "web_search"}]

    for iteration in range(20):  # safety cap on agentic loop iterations
        log(f"API call #{iteration + 1}")

        # Retry on transient overload (529) with exponential backoff
        response = None
        for attempt in range(5):
            try:
                # Use streaming to avoid SDK timeout on long requests,
                # then collect the full response at the end.
                with client.messages.stream(
                    model=model,
                    max_tokens=max_tokens,
                    thinking={
                        "type": "enabled",
                        "budget_tokens": thinking_budget,
                    },
                    tools=tools,
                    messages=messages,
                ) as stream:
                    response = stream.get_final_message()
                break
            except anthropic.APIStatusError as e:
                if e.status_code == 529 and attempt < 4:
                    wait = 30 * (2 ** attempt)  # 30s, 60s, 120s, 240s
                    log(f"API overloaded (529), retrying in {wait}s (attempt {attempt + 1}/5)...")
                    time.sleep(wait)
                else:
                    raise
        if response is None:
            log("ERROR: All retry attempts exhausted")
            sys.exit(1)

        log(f"stop_reason={response.stop_reason}, blocks={len(response.content)}")
        text_output = extract_text(response)

        if response.stop_reason == "end_turn":
            # With extended thinking enabled, text blocks should contain only
            # the brief, but the model sometimes emits reasoning/draft prose
            # before the H1. Strip anything before the first line-start H1.
            brief, preamble_len = strip_preamble(text_output)
            if preamble_len == 0 and not text_output.lstrip().startswith("# "):
                log("ERROR: No H1 heading found in model output — refusing to write broken brief")
                log(f"[raw output head] {text_output[:1000]}")
                sys.exit(2)
            if preamble_len > 0:
                log(f"[stripped preamble, {preamble_len} chars] {text_output[:500]}")
            print(brief)
            return

        if response.stop_reason == "tool_use":
            # Add this assistant turn to the conversation history
            messages.append({"role": "assistant", "content": response.content})

            # Build tool_result acknowledgements for every tool_use block.
            # For the server-side web_search tool, Anthropic executes the search
            # and embeds results in the response content. We read those results
            # back from any paired tool_result blocks already present; if none
            # are found (shouldn't happen with web_search) we send an empty ack
            # so the model can continue.
            tool_results = []
            for block in response.content:
                block_type = getattr(block, "type", None)
                if block_type == "tool_use":
                    log(f"tool_use: {block.name}({block.input})")
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": "",  # server-side tool; result already in response
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
            print(brief)
            return

        else:
            log(f"Unexpected stop_reason: {response.stop_reason} — outputting available text")
            brief, preamble_len = strip_preamble(text_output)
            if preamble_len > 0:
                log(f"[stripped preamble, {preamble_len} chars] {text_output[:500]}")
            print(brief)
            return

    print("ERROR: Hit maximum iteration limit (20)", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
