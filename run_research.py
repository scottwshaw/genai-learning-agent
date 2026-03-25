#!/usr/bin/env python3
"""
run_research.py — Calls the Anthropic API with web search to generate a research brief.
Reads the research prompt from stdin, writes the final brief to stdout.
Diagnostic logs go to stderr (captured by research.sh into agent.log).

Setup:
    pip install anthropic

Environment variables:
    ANTHROPIC_API_KEY   (required)
    ANTHROPIC_MODEL     (optional, default: claude-opus-4-6)
"""

import os
import sys

try:
    import anthropic
except ImportError:
    print("ERROR: anthropic package not installed. Run: pip install anthropic", file=sys.stderr)
    sys.exit(1)


def log(msg):
    print(f"[run_research] {msg}", file=sys.stderr, flush=True)


def main():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY environment variable not set", file=sys.stderr)
        sys.exit(1)

    prompt = sys.stdin.read().strip()
    if not prompt:
        print("ERROR: No prompt received on stdin", file=sys.stderr)
        sys.exit(1)

    model = os.environ.get("ANTHROPIC_MODEL", "claude-opus-4-6")
    client = anthropic.Anthropic(api_key=api_key)

    log(f"Starting: model={model}, prompt_chars={len(prompt)}")

    messages = [{"role": "user", "content": prompt}]

    # web_search_20250305 is a server-side tool — Anthropic executes searches on its
    # infrastructure; no separate search API key required on the client.
    tools = [{"type": "web_search_20250305", "name": "web_search"}]

    for iteration in range(20):  # safety cap on agentic loop iterations
        log(f"API call #{iteration + 1}")

        response = client.messages.create(
            model=model,
            max_tokens=8096,
            tools=tools,
            messages=messages,
        )

        log(f"stop_reason={response.stop_reason}, blocks={len(response.content)}")

        # Collect all text blocks from this response turn
        text_parts = [
            block.text
            for block in response.content
            if getattr(block, "type", None) == "text"
        ]

        if response.stop_reason == "end_turn":
            output = "\n".join(text_parts).strip()
            if not output:
                print("ERROR: Model returned no text content", file=sys.stderr)
                sys.exit(1)
            print(output)
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
            print("\n".join(text_parts).strip())
            return

        else:
            log(f"Unexpected stop_reason: {response.stop_reason} — outputting available text")
            print("\n".join(text_parts).strip())
            return

    print("ERROR: Hit maximum iteration limit (20)", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
