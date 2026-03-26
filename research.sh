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
BRIEFS_DIR="$SCRIPT_DIR/briefs"
LEARNING_LOG="$SCRIPT_DIR/learning-log.md"
STATE_FILE="$SCRIPT_DIR/.topic-index"
LOG_FILE="$SCRIPT_DIR/agent.log"
TOPICS_FILE="$SCRIPT_DIR/topics.json"
PROMPT_TEMPLATE="$SCRIPT_DIR/prompts/research-prompt.md"
DATE="$(date +%Y-%m-%d)"
MODEL="${ANTHROPIC_MODEL:-claude-opus-4-6}"

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
# Topic rotation (round-robin, driven by topics.json)
# ---------------------------------------------------------------------------
NUM_TOPICS="$(jq '.topics | length' "$TOPICS_FILE")"

get_topic_index() {
    if [[ -f "$STATE_FILE" ]]; then
        local val
        val="$(cat "$STATE_FILE")"
        # Validate it's a number in range
        if [[ "$val" =~ ^[0-9]+$ ]] && (( val < NUM_TOPICS )); then
            echo "$val"
            return
        fi
    fi
    echo "0"
}

# ---------------------------------------------------------------------------
# List topics mode
# ---------------------------------------------------------------------------
if [[ "$LIST_TOPICS" == true ]]; then
    CURRENT_IDX="$(get_topic_index)"
    echo "Topics (round-robin order):"
    for i in $(seq 0 $(( NUM_TOPICS - 1 ))); do
        label="$(jq -r ".topics[$i].label" "$TOPICS_FILE")"
        if (( i == CURRENT_IDX )); then
            echo "  -> $(( i + 1 )). $label  [next]"
        else
            echo "     $(( i + 1 )). $label"
        fi
    done
    exit 0
fi

# ---------------------------------------------------------------------------
# Initialization
# ---------------------------------------------------------------------------
mkdir -p "$BRIEFS_DIR"

if [[ ! -f "$LEARNING_LOG" ]]; then
    log "Initializing learning-log.md"
    cat > "$LEARNING_LOG" <<'LOGEOF'
# GenAI Learning Log

Tracks daily research briefs to ensure broad topic coverage and avoid repetition.
The agent rotates through six priority areas in round-robin order.

## Priority Areas

| # | Area | Focus |
|---|------|-------|
| 1 | Safety, Assurance & Governance | Governance frameworks, regulation, auditing, compliance |
| 2 | Enterprise GenAI Adoption | Case studies, ROI, large-scale deployments, vendor landscape |
| 3 | Agentic Systems | Frameworks, multi-agent, tool use, planning |
| 4 | Frontier Research | Latest papers & model releases from major labs |
| 5 | GenAI Products & Platforms | New releases, enterprise platforms, API updates |
| 6 | MLOps & LLMOps | Deployment, monitoring, fine-tuning infra, evaluation |
| 7 | Inference Optimization | Quantization, serving, latency, hardware kernels |

## Research History

| Date | Topic | Brief |
|------|-------|-------|
LOGEOF
fi

# ---------------------------------------------------------------------------
# Determine today's topic
# ---------------------------------------------------------------------------
IDX="$(get_topic_index)"

# --topic / --topic-slug override: resolve to an index
if [[ -n "$TOPIC_SLUG_OVERRIDE" ]]; then
    FOUND_IDX=""
    # Accept 1-based numeric index (e.g. --topic 3)
    if [[ "$TOPIC_SLUG_OVERRIDE" =~ ^[0-9]+$ ]]; then
        N=$(( TOPIC_SLUG_OVERRIDE - 1 ))
        if (( N >= 0 && N < NUM_TOPICS )); then
            FOUND_IDX="$N"
        else
            echo "[ERROR] --topic $TOPIC_SLUG_OVERRIDE is out of range (1-${NUM_TOPICS})" >&2
            exit 1
        fi
    else
        # Accept slug string
        for i in $(seq 0 $(( NUM_TOPICS - 1 ))); do
            if [[ "$(jq -r ".topics[$i].slug" "$TOPICS_FILE")" == "$TOPIC_SLUG_OVERRIDE" ]]; then
                FOUND_IDX="$i"
                break
            fi
        done
        if [[ -z "$FOUND_IDX" ]]; then
            echo "[ERROR] Topic slug '$TOPIC_SLUG_OVERRIDE' not found in topics.json" >&2
            exit 1
        fi
    fi
    IDX="$FOUND_IDX"
fi

NEXT_IDX=$(( (IDX + 1) % NUM_TOPICS ))

TOPIC_SLUG="$(jq -r ".topics[$IDX].slug" "$TOPICS_FILE")"
TOPIC_LABEL="$(jq -r ".topics[$IDX].label" "$TOPICS_FILE")"
TOPIC_FOCUS_TEXT="$(jq -r ".topics[$IDX].focus" "$TOPICS_FILE")"

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

# ---------------------------------------------------------------------------
# Determine previous brief date for the same topic (for recency filtering)
# ---------------------------------------------------------------------------
PREVIOUS_BRIEF_DATE="$(ls "$BRIEFS_DIR"/*-"${TOPIC_SLUG}".md 2>/dev/null \
    | sort | tail -1 \
    | xargs -I{} basename {} \
    | sed "s/-${TOPIC_SLUG}\.md//" \
    || echo "")"

if [[ -z "$PREVIOUS_BRIEF_DATE" ]]; then
    # No prior brief — default to 14 days ago
    PREVIOUS_BRIEF_DATE="$(date -d '14 days ago' +%Y-%m-%d 2>/dev/null \
        || date -v-14d +%Y-%m-%d)"
fi

log "Previous brief date for this topic: $PREVIOUS_BRIEF_DATE"

# ---------------------------------------------------------------------------
# Load recent briefs across ALL topics — used as a coverage baseline so the
# agent avoids repeating developments already surfaced in any brief, and can
# track trends holistically across the full landscape.
# We include the last 28 briefs (~4 full topic rotations / ~1 month of coverage).
# ---------------------------------------------------------------------------
RECENT_BRIEFS_CONTENT=""
RECENT_BRIEFS_COUNT=0
while IFS= read -r brief_path; do
    [[ -z "$brief_path" ]] && continue
    brief_name="$(basename "$brief_path" .md)"
    RECENT_BRIEFS_CONTENT+="### ${brief_name}
$(cat "$brief_path")

---

"
    RECENT_BRIEFS_COUNT=$(( RECENT_BRIEFS_COUNT + 1 ))
done < <(ls "$BRIEFS_DIR"/*.md 2>/dev/null | sort | tail -28 || true)

if [[ -z "$RECENT_BRIEFS_CONTENT" ]]; then
    RECENT_BRIEFS_CONTENT="(No prior briefs exist yet — this is the first run.)"
fi

log "Loaded ${RECENT_BRIEFS_COUNT} recent brief(s) as coverage context"

# ---------------------------------------------------------------------------
# Build the research prompt
# Prompt loaded from prompts/research-prompt.md — can also be used by API-based runners
# Recent briefs are appended after the template (avoids sed multiline issues).
# ---------------------------------------------------------------------------
RESEARCH_PROMPT="$(sed \
    -e "s/{{DATE}}/${DATE}/g" \
    -e "s/{{TOPIC_LABEL}}/${TOPIC_LABEL}/g" \
    -e "s/{{PREVIOUS_BRIEF_DATE}}/${PREVIOUS_BRIEF_DATE}/g" \
    -e "s|{{TOPIC_FOCUS}}|${TOPIC_FOCUS_TEXT}|g" \
    "$PROMPT_TEMPLATE")

---

## CONTEXT: Recent Briefs (Last ${RECENT_BRIEFS_COUNT} Runs Across All Topics)

The following briefs represent what has already been covered in recent days.
Use them to: avoid repeating developments already surfaced; track how trends are evolving across the full landscape; spot connections that cross topic boundaries.

${RECENT_BRIEFS_CONTENT}"

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
