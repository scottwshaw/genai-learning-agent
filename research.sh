#!/usr/bin/env bash
# =============================================================================
# research.sh — Daily GenAI Learning Agent
# =============================================================================
# Runs daily via cron. Uses `claude -p` with web search to research the latest
# GenAI developments across 7 topic areas, saves a markdown brief to briefs/,
# updates learning-log.md with a round-robin topic tracker, and commits via git.
#
# SETUP:
#   1. chmod +x research.sh
#   2. Run once manually to initialize: ./research.sh
#   3. Add to crontab (e.g. 07:00 daily):
#        0 7 * * * /path/to/genai-learning-agent/research.sh >> /path/to/genai-learning-agent/agent.log 2>&1
#   4. Ensure `claude` is authenticated on the VM: claude auth login
#
# PREREQUISITES:
#   - jq (apt install jq / brew install jq)
#   - claude CLI (npm install -g @anthropic-ai/claude-code)
# =============================================================================

set -euo pipefail

# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------
RESET_MODE=false
LIST_TOPICS=false
NO_COMMIT=false
for arg in "$@"; do
    case "$arg" in
        --reset)
            RESET_MODE=true
            ;;
        --topics)
            LIST_TOPICS=true
            ;;
        --no-commit)
            NO_COMMIT=true
            ;;
        *)
            echo "Unknown option: $arg" >&2
            echo "Usage: $0 [--reset|--topics|--no-commit]" >&2
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
MODEL="claude-opus-4-6"

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
# Resolve `claude` binary
# Cron environments often have a minimal PATH, so we search common locations.
# ---------------------------------------------------------------------------
find_claude() {
    # Check PATH first
    if command -v claude &>/dev/null; then
        command -v claude
        return
    fi
    # Common install locations for npm global / nvm / claude installer
    local candidates=(
        "$HOME/.claude/local/claude"
        "$HOME/.npm-global/bin/claude"
        "$HOME/.nvm/versions/node/$(ls "$HOME/.nvm/versions/node" 2>/dev/null | sort -V | tail -1)/bin/claude"
        "/usr/local/bin/claude"
        "/usr/bin/claude"
        "$HOME/.local/bin/claude"
    )
    for c in "${candidates[@]}"; do
        if [[ -x "$c" ]]; then
            echo "$c"
            return
        fi
    done
    echo ""
}

CLAUDE_BIN="$(find_claude)"
if [[ -z "$CLAUDE_BIN" ]]; then
    echo "[ERROR] 'claude' binary not found. Run 'npm install -g @anthropic-ai/claude-code' and authenticate." >&2
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
NEXT_IDX=$(( (IDX + 1) % NUM_TOPICS ))

TOPIC_SLUG="$(jq -r ".topics[$IDX].slug" "$TOPICS_FILE")"
TOPIC_LABEL="$(jq -r ".topics[$IDX].label" "$TOPICS_FILE")"
TOPIC_FOCUS_TEXT="$(jq -r ".topics[$IDX].focus" "$TOPICS_FILE")"
BRIEF_FILE="$BRIEFS_DIR/${DATE}-${TOPIC_SLUG}.md"

log "=========================================="
log "Daily GenAI Learning Agent starting"
log "Topic ($((IDX + 1))/${NUM_TOPICS}): $TOPIC_LABEL"
log "Output: $BRIEF_FILE"
log "=========================================="

# Skip if today's brief already exists (idempotent re-runs)
if [[ -f "$BRIEF_FILE" ]]; then
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
# Run claude -p with web search
# ---------------------------------------------------------------------------
log "Invoking: $CLAUDE_BIN -p [prompt] --allowedTools WebSearch,WebFetch --model $MODEL"

if ! "$CLAUDE_BIN" -p "$RESEARCH_PROMPT" \
    --allowedTools "WebSearch,WebFetch" \
    --model "$MODEL" \
    --output-format text \
    > "$BRIEF_FILE" 2>>"$LOG_FILE"; then
    log "ERROR: claude -p exited with non-zero status"
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
# Update learning log
# ---------------------------------------------------------------------------
BRIEF_BASENAME="$(basename "$BRIEF_FILE")"
printf "| %s | %s | [%s](briefs/%s) |\n" \
    "$DATE" "$TOPIC_LABEL" "$BRIEF_BASENAME" "$BRIEF_BASENAME" \
    >> "$LEARNING_LOG"

log "Updated learning-log.md"

# ---------------------------------------------------------------------------
# Advance the topic index for tomorrow
# ---------------------------------------------------------------------------
echo "$NEXT_IDX" > "$STATE_FILE"
NEXT_LABEL="$(jq -r ".topics[$NEXT_IDX].label" "$TOPICS_FILE")"
log "Next topic: $NEXT_LABEL (index $NEXT_IDX)"

# ---------------------------------------------------------------------------
# Git commit
# ---------------------------------------------------------------------------
if [[ "$NO_COMMIT" == true ]]; then
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

log "Done. Run $(( NEXT_IDX + 1 ))/${NUM_TOPICS} next time: $NEXT_LABEL"
log "=========================================="
