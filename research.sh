#!/usr/bin/env bash
# =============================================================================
# research.sh — Daily GenAI Learning Agent
# =============================================================================
# Runs daily via cron. Uses `claude -p` with web search to research the latest
# GenAI developments, saves a markdown brief to briefs/, updates learning-log.md
# with a round-robin topic tracker, and commits the results via git.
#
# SETUP:
#   1. chmod +x research.sh
#   2. Run once manually to initialize: ./research.sh
#   3. Add to crontab (e.g. 07:00 daily):
#        0 7 * * * /path/to/genai-learning-agent/research.sh >> /path/to/genai-learning-agent/agent.log 2>&1
#   4. Ensure `claude` is authenticated on the VM: claude auth login
# =============================================================================

set -euo pipefail

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BRIEFS_DIR="$SCRIPT_DIR/briefs"
LEARNING_LOG="$SCRIPT_DIR/learning-log.md"
STATE_FILE="$SCRIPT_DIR/.topic-index"
LOG_FILE="$SCRIPT_DIR/agent.log"
DATE="$(date +%Y-%m-%d)"
MODEL="claude-opus-4-6"

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
# Topic rotation (round-robin across 6 priority areas)
# ---------------------------------------------------------------------------
TOPIC_SLUGS=(
    "safety-and-alignment"
    "agentic-systems"
    "mlops"
    "inference-optimization"
    "frontier-research"
    "foundation-model-internals"
)

TOPIC_LABELS=(
    "Safety & Alignment"
    "Agentic Systems"
    "MLOps"
    "Inference Optimization"
    "Frontier Research"
    "Foundation Model Internals"
)

# Per-topic search focus injected into the research prompt
TOPIC_FOCUS=(
    "AI safety research, alignment techniques, RLHF/RLAIF advances, interpretability methods, red-teaming, constitutional AI, scalable oversight, and AI governance policy"
    "autonomous agent frameworks (LangGraph, AutoGen, CrewAI, etc.), multi-agent coordination, tool use, planning and reasoning, memory architectures, agent evaluation benchmarks, and agentic workflow design patterns"
    "LLMOps tooling, model deployment pipelines, experiment tracking, fine-tuning infrastructure, model monitoring and observability, evaluation frameworks, and production ML systems at scale"
    "LLM inference efficiency, quantization techniques (GPTQ, AWQ, GGUF), speculative decoding, KV cache optimization, hardware-specific kernel optimizations (FlashAttention, etc.), serving frameworks (vLLM, TGI, SGLang), and throughput/latency improvements"
    "latest research papers and preprints from OpenAI, Anthropic, Google DeepMind, Meta AI, Mistral, xAI, and other labs; new model releases; benchmark results; and significant technical breakthroughs published in the past two weeks"
    "transformer architecture innovations, attention mechanism variants, tokenization advances, pre-training techniques and curricula, scaling laws, mixture-of-experts designs, state-space models (Mamba, etc.), and other architectural research"
)

NUM_TOPICS="${#TOPIC_SLUGS[@]}"

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
| 1 | Safety & Alignment | Alignment techniques, interpretability, governance |
| 2 | Agentic Systems | Frameworks, multi-agent, tool use, planning |
| 3 | MLOps | LLMOps, deployment, monitoring, fine-tuning infra |
| 4 | Inference Optimization | Quantization, serving, latency, hardware kernels |
| 5 | Frontier Research | Latest papers & model releases from major labs |
| 6 | Foundation Model Internals | Architectures, attention, pre-training, scaling |

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

TOPIC_SLUG="${TOPIC_SLUGS[$IDX]}"
TOPIC_LABEL="${TOPIC_LABELS[$IDX]}"
TOPIC_FOCUS_TEXT="${TOPIC_FOCUS[$IDX]}"
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
# Build the research prompt
# ---------------------------------------------------------------------------
read -r -d '' RESEARCH_PROMPT <<PROMPTEOF || true
You are an expert GenAI research assistant producing a daily intelligence brief for a senior ML engineer.

Today's date is ${DATE}. Your task is to research the LATEST developments (ideally from the past 7-14 days, no older than 30 days unless seminal) in the following area:

**${TOPIC_LABEL}**

Focus specifically on: ${TOPIC_FOCUS_TEXT}

Use web search to find recent papers, blog posts, GitHub releases, announcements, and news. Prioritize primary sources (arXiv, official lab blogs, GitHub) over aggregators.

Produce a well-structured research brief in the following exact markdown format:

---

# ${TOPIC_LABEL} — Research Brief (${DATE})

## Key Developments

- [bullet: development with date, source, and 1-sentence explanation]
- (3–5 bullets, most significant recent items only)

## Notable Papers / Models / Tools

| Item | Date | Source | Summary |
|------|------|--------|---------|
(list each notable paper, model release, or tool with a brief description and link)

## Technical Deep-Dive

(Choose the single most technically interesting development from above. Explain it in 2–4 paragraphs with genuine technical depth — cover the mechanism, what's novel, why it matters, and any limitations. Be specific: include architecture details, benchmark numbers, or algorithmic insights where relevant.)

## Implications & Trends

- [bullet: what this development signals for the field]
- (2–3 bullets connecting recent developments to broader trajectories)

## Sources

(List every URL you found useful, one per line, with a brief label)

---

Be precise, cite sources, include publication/announcement dates, and prioritize recency. Do not pad with background information that hasn't changed recently — focus on what is *new*.
PROMPTEOF

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
log "Next topic: ${TOPIC_LABELS[$NEXT_IDX]} (index $NEXT_IDX)"

# ---------------------------------------------------------------------------
# Git commit
# ---------------------------------------------------------------------------
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

log "Done. Run $(( (NEXT_IDX) + 1 ))/${NUM_TOPICS} next time: ${TOPIC_LABELS[$NEXT_IDX]}"
log "=========================================="
