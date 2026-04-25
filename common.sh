#!/usr/bin/env bash
# =============================================================================
# common.sh — Shared setup for research agent scripts
# =============================================================================
# Source this from any script in the repo root. Provides:
#   REPO_ROOT      — absolute path to the repository root
#   PYTHON_BIN     — path to python3 (venv-aware)
#   AGENT_CLI      — path to agent_cli.py
#   TOPICS_FILE    — path to topics.json
#   STATE_FILE     — path to .topic-index
#   resolve_topic  — function that sets TOPIC_* variables
# =============================================================================

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AGENT_CLI="$REPO_ROOT/agent_cli.py"
TOPICS_FILE="$REPO_ROOT/topics.json"
STATE_FILE="$REPO_ROOT/.topic-index"

# ---------------------------------------------------------------------------
# Resolve python3 — prefer the project venv if present
# ---------------------------------------------------------------------------
if [[ -x "$REPO_ROOT/.venv/bin/python3" ]]; then
    PYTHON_BIN="$REPO_ROOT/.venv/bin/python3"
else
    PYTHON_BIN="$(command -v python3 2>/dev/null || true)"
fi
if [[ -z "$PYTHON_BIN" ]]; then
    echo "[ERROR] 'python3' not found. Create a venv: python3 -m venv .venv && .venv/bin/pip install anthropic" >&2
    exit 1
fi

# ---------------------------------------------------------------------------
# Prerequisite checks
# ---------------------------------------------------------------------------
if ! command -v jq &>/dev/null; then
    echo "[ERROR] 'jq' is required but not found. Install with: apt install jq  OR  brew install jq" >&2
    exit 1
fi

if [[ ! -f "$AGENT_CLI" ]]; then
    echo "[ERROR] agent_cli.py not found at $AGENT_CLI" >&2
    exit 1
fi

# ---------------------------------------------------------------------------
# resolve_topic [SLUG_OR_INDEX]
# Sets: TOPIC_INFO_JSON, TOPIC_SLUG, TOPIC_LABEL, TOPIC_FOCUS,
#        TOPIC_IDX, TOPIC_NEXT_IDX, TOPIC_COUNT
# ---------------------------------------------------------------------------
resolve_topic() {
    local topic_args=()
    if [[ -n "${1:-}" ]]; then
        topic_args=(--topic "$1")
    fi
    TOPIC_INFO_JSON="$("$PYTHON_BIN" "$AGENT_CLI" resolve-topic \
        --topics-file "$TOPICS_FILE" \
        --state-file "$STATE_FILE" \
        ${topic_args[@]+"${topic_args[@]}"})"
    TOPIC_SLUG="$(printf '%s' "$TOPIC_INFO_JSON" | jq -r '.slug')"
    TOPIC_LABEL="$(printf '%s' "$TOPIC_INFO_JSON" | jq -r '.label')"
    TOPIC_FOCUS="$(printf '%s' "$TOPIC_INFO_JSON" | jq -r '.focus')"
    TOPIC_IDX="$(printf '%s' "$TOPIC_INFO_JSON" | jq -r '.index')"
    TOPIC_NEXT_IDX="$(printf '%s' "$TOPIC_INFO_JSON" | jq -r '.next_index')"
    TOPIC_COUNT="$(printf '%s' "$TOPIC_INFO_JSON" | jq -r '.count')"
}
