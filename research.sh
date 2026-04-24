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
CRITIC_BRIEF=""         # --brief FILE        : skip generation, run critic on existing brief

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
        --brief)
            CRITIC_BRIEF="${2:?--brief requires a file path}"
            shift 2
            ;;
        *)
            echo "Unknown option: $1" >&2
            echo "Usage: $0 [--reset|--topics|--no-commit]" >&2
            echo "       $0 [--topic N|SLUG] [--no-commit]   # N is 1-based topic number" >&2
            echo "       $0 --eval-output FILE [--topic-slug SLUG] [--prompt-file FILE]" >&2
            echo "       $0 --brief FILE [--no-commit]        # critic-only on existing brief" >&2
            exit 1
            ;;
    esac
done

# ---------------------------------------------------------------------------
# Shared setup (python, jq, agent_cli, topic resolution helper)
# ---------------------------------------------------------------------------
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/common.sh"

# ---------------------------------------------------------------------------
# Local paths and settings
# ---------------------------------------------------------------------------
BRIEFS_DIR="$REPO_ROOT/briefs"
LEARNING_LOG="$REPO_ROOT/learning-log.md"
LOG_FILE="$REPO_ROOT/agent.log"
PROMPT_TEMPLATE="$REPO_ROOT/prompts/research-prompt.md"
DATE="$(date +%Y-%m-%d)"
MODEL="${ANTHROPIC_MODEL:-claude-sonnet-4-6}"

# ---------------------------------------------------------------------------
# Remaining prerequisite checks
# ---------------------------------------------------------------------------
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
resolve_topic "$TOPIC_SLUG_OVERRIDE"

# In eval mode use the caller-specified output path; otherwise use briefs/
if [[ -n "$EVAL_OUTPUT" ]]; then
    BRIEF_FILE="$EVAL_OUTPUT"
else
    BRIEF_FILE="$BRIEFS_DIR/${DATE}-${TOPIC_SLUG}.md"
fi

log "=========================================="
log "Daily GenAI Learning Agent starting"
log "Topic ($((TOPIC_IDX + 1))/${TOPIC_COUNT}): $TOPIC_LABEL"
log "Output: $BRIEF_FILE"
log "=========================================="

# ---------------------------------------------------------------------------
# Critic-only mode: skip generation, run critic→revise on existing brief
# ---------------------------------------------------------------------------
if [[ -n "$CRITIC_BRIEF" ]]; then
    if [[ ! -f "$CRITIC_BRIEF" ]]; then
        log "ERROR: Brief file not found: $CRITIC_BRIEF"
        exit 1
    fi
    BRIEF_FILE="$CRITIC_BRIEF"
    log "Critic-only mode: running critic on $CRITIC_BRIEF"
    if ! ENABLE_CRITIC=1 ANTHROPIC_MODEL="$MODEL" \
        "$PYTHON_BIN" "$REPO_ROOT/run_research.py" --brief "$CRITIC_BRIEF" \
        > "${CRITIC_BRIEF%.md}-revised.md" 2>>"$LOG_FILE"; then
        log "ERROR: critic run failed"
        exit 1
    fi
    REVISED_SIZE="$(wc -c < "${CRITIC_BRIEF%.md}-revised.md")"
    log "Revised brief saved (${REVISED_SIZE} bytes): ${CRITIC_BRIEF%.md}-revised.md"
    exit 0
fi

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
    | ANTHROPIC_MODEL="$MODEL" "$PYTHON_BIN" "$REPO_ROOT/run_research.py" \
    --topic-label "$TOPIC_LABEL" --date "$DATE" --topic-focus "$TOPIC_FOCUS" \
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
if [[ -z "$EVAL_OUTPUT" ]] && [[ "$NO_COMMIT" == false ]]; then
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
    echo "$TOPIC_NEXT_IDX" > "$STATE_FILE"
    NEXT_LABEL="$(jq -r ".topics[$TOPIC_NEXT_IDX].label" "$TOPICS_FILE")"
    log "Next topic: $NEXT_LABEL (index $TOPIC_NEXT_IDX)"
fi

# ---------------------------------------------------------------------------
# Git commit  (skipped in eval mode)
# ---------------------------------------------------------------------------
if [[ -n "$EVAL_OUTPUT" ]]; then
    log "Eval mode: brief written to $EVAL_OUTPUT (no commit, no log update, no index advance)"
elif [[ "$NO_COMMIT" == true ]]; then
    log "Skipping git commit (--no-commit flag set). Brief saved but not staged."
else
    cd "$REPO_ROOT"

    git add "$BRIEF_FILE" "$LEARNING_LOG"

    # Only commit if there are staged changes (guards against edge cases)
    if git diff --cached --quiet; then
        log "Nothing new to commit (unexpected — brief already tracked?)"
    else
        git commit -m "research(${DATE}): ${TOPIC_LABEL}

Daily brief on '${TOPIC_LABEL}' (area $((TOPIC_IDX + 1))/${TOPIC_COUNT}).
Generated by learning-agent on $(hostname)."
        log "Git committed: research(${DATE}): ${TOPIC_LABEL}"
    fi
fi

if [[ -n "$EVAL_OUTPUT" ]]; then
    log "Done (eval mode)."
elif [[ "$LOCK_ROTATION" == true ]]; then
    log "Done (rotation locked via --topic; .topic-index not advanced)."
else
    log "Done. Run $(( TOPIC_NEXT_IDX + 1 ))/${TOPIC_COUNT} next time: $NEXT_LABEL"
fi
log "=========================================="
