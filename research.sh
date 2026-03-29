#!/usr/bin/env bash
# =============================================================================
# research.sh — Daily GenAI Learning Agent
# =============================================================================
# Runs daily via cron. Uses the Anthropic API (via run_research.py) with web
# search to research the latest GenAI developments across 6 topic areas, saves
# a markdown brief to briefs/, updates learning-log.md, and commits via git.
#
# ANTHROPIC_API_KEY must be set in the environment at invocation time.
# It is never stored on disk. Inject it via cron, SSH, or a secrets manager:
#   ANTHROPIC_API_KEY=sk-ant-... ./research.sh
#   ssh user@host "ANTHROPIC_API_KEY=sk-ant-... /path/to/research.sh"
#
# SETUP:
#   1. pip install anthropic
#   2. chmod +x research.sh
#   3. Run once manually to verify: ANTHROPIC_API_KEY=sk-ant-... ./research.sh --no-commit
#   4. Add to crontab (e.g. 07:00 daily), injecting the key:
#        0 7 * * * ANTHROPIC_API_KEY=sk-ant-... /path/to/research.sh >> /path/to/agent.log 2>&1
#
# PREREQUISITES:
#   - python3 + anthropic package (pip install anthropic)
#   - jq (apt install jq / brew install jq)
# =============================================================================

set -euo pipefail

# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------
RESET_MODE=false
LIST_TOPICS=false
NO_COMMIT=false
EVAL_OUTPUT=""          # --eval-output FILE  : write brief here; skip all side effects
TOPIC_SLUG_OVERRIDE=""  # --topic-slug SLUG / --topic N : override rotation
LOCK_ROTATION=false     # set true when topic is manually selected (don't advance index)
PROMPT_FILE_OVERRIDE="" # --prompt-file FILE  : override prompt template

while [[ $# -gt 0 ]]; do
    case "$1" in
        --reset)
            RESET_MODE=true
            shift
            ;;
        --topics)
            LIST_TOPICS=true
            shift
            ;;
        --no-commit)
            NO_COMMIT=true
            shift
            ;;
        --topic)
            # Accepts a 1-based index (1-6) or a topic slug
            TOPIC_SLUG_OVERRIDE="${2:?--topic requires a number or slug}"
            LOCK_ROTATION=true
            shift 2
            ;;
        --eval-output)
            EVAL_OUTPUT="${2:?--eval-output requires a file path}"
            shift 2
            ;;
        --topic-slug)
            # Internal flag used by eval.sh; rotation always locked in eval mode
            TOPIC_SLUG_OVERRIDE="${2:?--topic-slug requires a slug}"
            shift 2
            ;;
        --prompt-file)
            PROMPT_FILE_OVERRIDE="${2:?--prompt-file requires a file path}"
            shift 2
            ;;
        *)
            echo "Unknown option: $1" >&2
            echo "Usage: $0 [--reset|--topics|--no-commit]" >&2
            echo "       $0 [--topic N|SLUG] [--no-commit]   # N is 1-based topic number" >&2
            echo "       $0 --eval-output FILE [--topic-slug SLUG] [--prompt-file FILE]" >&2
            exit 1
            ;;
    esac
done

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AGENT_CLI="$SCRIPT_DIR/agent_cli.py"
BRIEFS_DIR="$SCRIPT_DIR/briefs"
LEARNING_LOG="$SCRIPT_DIR/learning-log.md"
STATE_FILE="$SCRIPT_DIR/.topic-index"
LOG_FILE="$SCRIPT_DIR/agent.log"
TOPICS_FILE="$SCRIPT_DIR/topics.json"
PROMPT_TEMPLATE="$SCRIPT_DIR/prompts/research-prompt.md"
DATE="$(date +%Y-%m-%d)"
MODEL="${ANTHROPIC_MODEL:-claude-sonnet-4-6}"

# ---------------------------------------------------------------------------
# Prerequisite checks
# ---------------------------------------------------------------------------
if ! command -v jq &>/dev/null; then
    echo "[ERROR] 'jq' is required but not found. Install with: apt install jq  OR  brew install jq" >&2
    exit 1
fi

if [[ ! -f "$TOPICS_FILE" ]]; then
    echo "[ERROR] topics.json not found at $TOPICS_FILE" >&2
    exit 1
fi

if [[ -n "$PROMPT_FILE_OVERRIDE" ]]; then
    PROMPT_TEMPLATE="$PROMPT_FILE_OVERRIDE"
fi

if [[ ! -f "$PROMPT_TEMPLATE" ]]; then
    echo "[ERROR] Prompt template not found at $PROMPT_TEMPLATE" >&2
    exit 1
fi

if [[ ! -f "$AGENT_CLI" ]]; then
    echo "[ERROR] agent_cli.py not found at $AGENT_CLI" >&2
    exit 1
fi

# ---------------------------------------------------------------------------
# Reset mode — wipe state and briefs for a clean test run
# ---------------------------------------------------------------------------
if [[ "$RESET_MODE" == true ]]; then
    echo "WARNING: This will permanently delete all research briefs, the learning log, and all state."
    read -r -p "Are you sure you want to reset? [y/N] " confirm
    if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
        echo "Reset cancelled."
        exit 0
    fi
    echo "Resetting state..."
    rm -f "$STATE_FILE"
    rm -f "$LEARNING_LOG"
    rm -rf "$BRIEFS_DIR"
    rm -f "$LOG_FILE"
    echo "Deleted: .topic-index, learning-log.md, briefs/, agent.log"
    echo "Run ./research.sh to start fresh."
    exit 0
fi

# ---------------------------------------------------------------------------
# Resolve python3 — prefer the project venv if present
# ---------------------------------------------------------------------------
if [[ -x "$SCRIPT_DIR/.venv/bin/python3" ]]; then
    PYTHON_BIN="$SCRIPT_DIR/.venv/bin/python3"
else
    PYTHON_BIN="$(command -v python3 2>/dev/null || true)"
fi
if [[ -z "$PYTHON_BIN" ]]; then
    echo "[ERROR] 'python3' not found. Create a venv: python3 -m venv .venv && .venv/bin/pip install anthropic" >&2
    exit 1
fi

if [[ -z "${ANTHROPIC_API_KEY:-}" ]]; then
    echo "[ERROR] ANTHROPIC_API_KEY environment variable is not set." >&2
    exit 1
fi

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

# ---------------------------------------------------------------------------
# List topics mode
# ---------------------------------------------------------------------------
if [[ "$LIST_TOPICS" == true ]]; then
    "$PYTHON_BIN" "$AGENT_CLI" list-topics \
        --topics-file "$TOPICS_FILE" \
        --state-file "$STATE_FILE"
    exit 0
fi

# ---------------------------------------------------------------------------
# Initialization
# ---------------------------------------------------------------------------
mkdir -p "$BRIEFS_DIR"

if [[ ! -f "$LEARNING_LOG" ]]; then
    log "Initializing learning-log.md"
    "$PYTHON_BIN" "$AGENT_CLI" ensure-learning-log \
        --learning-log "$LEARNING_LOG" \
        --topics-file "$TOPICS_FILE" \
        >/dev/null
fi

# ---------------------------------------------------------------------------
# Determine today's topic
# ---------------------------------------------------------------------------
TOPIC_ARGS=()
if [[ -n "$TOPIC_SLUG_OVERRIDE" ]]; then
    TOPIC_ARGS=(--topic "$TOPIC_SLUG_OVERRIDE")
fi

TOPIC_INFO_JSON="$("$PYTHON_BIN" "$AGENT_CLI" resolve-topic \
    --topics-file "$TOPICS_FILE" \
    --state-file "$STATE_FILE" \
    ${TOPIC_ARGS[@]+"${TOPIC_ARGS[@]}"})"
IDX="$(printf '%s' "$TOPIC_INFO_JSON" | jq -r '.index')"
NEXT_IDX="$(printf '%s' "$TOPIC_INFO_JSON" | jq -r '.next_index')"
NUM_TOPICS="$(printf '%s' "$TOPIC_INFO_JSON" | jq -r '.count')"
TOPIC_SLUG="$(printf '%s' "$TOPIC_INFO_JSON" | jq -r '.slug')"
TOPIC_LABEL="$(printf '%s' "$TOPIC_INFO_JSON" | jq -r '.label')"

# In eval mode use the caller-specified output path; otherwise use briefs/
if [[ -n "$EVAL_OUTPUT" ]]; then
    BRIEF_FILE="$EVAL_OUTPUT"
else
    BRIEF_FILE="$BRIEFS_DIR/${DATE}-${TOPIC_SLUG}.md"
fi

log "=========================================="
log "Daily GenAI Learning Agent starting"
log "Topic ($((IDX + 1))/${NUM_TOPICS}): $TOPIC_LABEL"
log "Output: $BRIEF_FILE"
log "=========================================="

# Skip if today's brief already exists (idempotent re-runs) — skipped in eval mode
if [[ -z "$EVAL_OUTPUT" ]] && [[ -f "$BRIEF_FILE" ]]; then
    log "Brief already exists for today ($BRIEF_FILE). Skipping research."
    log "Delete the file to force a re-run."
    exit 0
fi

PROMPT_DATA_JSON="$("$PYTHON_BIN" "$AGENT_CLI" render-prompt \
    --prompt-template "$PROMPT_TEMPLATE" \
    --briefs-dir "$BRIEFS_DIR" \
    --date "$DATE" \
    --topics-file "$TOPICS_FILE" \
    --state-file "$STATE_FILE" \
    --topic "$TOPIC_SLUG")"
PREVIOUS_BRIEF_DATE="$(printf '%s' "$PROMPT_DATA_JSON" | jq -r '.previous_brief_date')"
RECENT_BRIEFS_COUNT="$(printf '%s' "$PROMPT_DATA_JSON" | jq -r '.recent_briefs_count')"
RESEARCH_PROMPT="$(printf '%s' "$PROMPT_DATA_JSON" | jq -r '.prompt')"

log "Previous brief date for this topic: $PREVIOUS_BRIEF_DATE"
log "Loaded ${RECENT_BRIEFS_COUNT} recent brief(s) as coverage context"

# ---------------------------------------------------------------------------
# Run research via Anthropic API (run_research.py)
# ANTHROPIC_API_KEY is read from the environment — never stored on disk.
# ---------------------------------------------------------------------------
log "Invoking: python3 run_research.py (model=$MODEL)"

if ! echo "$RESEARCH_PROMPT" \
    | ANTHROPIC_MODEL="$MODEL" "$PYTHON_BIN" "$SCRIPT_DIR/run_research.py" \
    > "$BRIEF_FILE" 2>>"$LOG_FILE"; then
    log "ERROR: run_research.py exited with non-zero status"
    # Remove partial output so a re-run starts fresh
    rm -f "$BRIEF_FILE"
    exit 1
fi

# Sanity-check: make sure we got meaningful output (>500 bytes)
BRIEF_SIZE="$(wc -c < "$BRIEF_FILE")"
if (( BRIEF_SIZE < 500 )); then
    log "ERROR: Output file is suspiciously small (${BRIEF_SIZE} bytes). Check agent.log."
    log "Content: $(cat "$BRIEF_FILE")"
    rm -f "$BRIEF_FILE"
    exit 1
fi

log "Brief saved (${BRIEF_SIZE} bytes): $BRIEF_FILE"

# ---------------------------------------------------------------------------
# Update learning log  (skipped in eval mode)
# ---------------------------------------------------------------------------
if [[ -z "$EVAL_OUTPUT" ]]; then
    BRIEF_BASENAME="$(basename "$BRIEF_FILE")"
    printf "| %s | %s | [%s](briefs/%s) |\n" \
        "$DATE" "$TOPIC_LABEL" "$BRIEF_BASENAME" "$BRIEF_BASENAME" \
        >> "$LEARNING_LOG"
    log "Updated learning-log.md"
fi

# ---------------------------------------------------------------------------
# Advance the topic index for tomorrow
# Skipped in eval mode or when topic was manually selected (--topic N|SLUG)
# ---------------------------------------------------------------------------
if [[ -z "$EVAL_OUTPUT" ]] && [[ "$LOCK_ROTATION" == false ]]; then
    echo "$NEXT_IDX" > "$STATE_FILE"
    NEXT_LABEL="$(jq -r ".topics[$NEXT_IDX].label" "$TOPICS_FILE")"
    log "Next topic: $NEXT_LABEL (index $NEXT_IDX)"
fi

# ---------------------------------------------------------------------------
# Git commit  (skipped in eval mode)
# ---------------------------------------------------------------------------
if [[ -n "$EVAL_OUTPUT" ]]; then
    log "Eval mode: brief written to $EVAL_OUTPUT (no commit, no log update, no index advance)"
elif [[ "$NO_COMMIT" == true ]]; then
    log "Skipping git commit (--no-commit flag set). Brief saved but not staged."
else
    cd "$SCRIPT_DIR"

    git add "$BRIEF_FILE" "$LEARNING_LOG"

    # Only commit if there are staged changes (guards against edge cases)
    if git diff --cached --quiet; then
        log "Nothing new to commit (unexpected — brief already tracked?)"
    else
        git commit -m "research(${DATE}): ${TOPIC_LABEL}

Daily brief on '${TOPIC_LABEL}' (area $((IDX + 1))/${NUM_TOPICS}).
Generated by learning-agent on $(hostname)."
        log "Git committed: research(${DATE}): ${TOPIC_LABEL}"
    fi
fi

if [[ -z "$EVAL_OUTPUT" ]]; then
    log "Done. Run $(( NEXT_IDX + 1 ))/${NUM_TOPICS} next time: $NEXT_LABEL"
else
    log "Done (eval mode)."
fi
log "=========================================="
