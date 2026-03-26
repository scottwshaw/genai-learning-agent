#!/usr/bin/env bash
# =============================================================================
# eval.sh — Side-by-side evaluation of research agent variants
# =============================================================================
# Runs two research agent configurations against the same topic prompt and
# scores each output against the rubric. Results are stored in eval-runs/ and
# never committed to git or written to briefs/.
#
# Usage:
#   ./eval.sh [options]
#
# Options:
#   --topic SLUG         Topic slug to evaluate (default: current rotation topic)
#   --model-a MODEL      Model for run A (default: claude-opus-4-6)
#   --model-b MODEL      Model for run B (default: claude-sonnet-4-6)
#   --prompt-a FILE      Prompt template for run A (default: prompts/research-prompt.md)
#   --prompt-b FILE      Prompt template for run B (default: same as A)
#   --label-a TEXT       Human label for run A (default: model name)
#   --label-b TEXT       Human label for run B (default: model name)
#   --single             Run only variant A (no comparison)
#   --score-only FILE    Score an existing brief, skip generation (sets --single)
#   --no-score           Generate briefs but skip scoring
#   --scoring-model M    Model to use for rubric scoring (default: claude-opus-4-6)
#
# Environment:
#   ANTHROPIC_API_KEY    Required
#
# Outputs (in eval-runs/YYYYMMDD-HHMMSS/):
#   config.md            Session config summary
#   run-a.md             Brief from variant A
#   run-b.md             Brief from variant B (if not --single)
#   scores-a.json        Rubric scores for A (if not --no-score)
#   scores-b.json        Rubric scores for B (if not --single/--no-score)
#   comparison.md        Side-by-side comparison report (if not --single)
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AGENT_CLI="$SCRIPT_DIR/agent_cli.py"

# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------
TOPIC_SLUG=""
MODEL_A="claude-opus-4-6"
MODEL_B="claude-sonnet-4-6"
PROMPT_A="$SCRIPT_DIR/prompts/research-prompt.md"
PROMPT_B=""
LABEL_A=""
LABEL_B=""
SINGLE=false
SCORE_ONLY_FILE=""
BRIEF_A_FILE=""
BRIEF_B_FILE=""
NO_SCORE=false
SCORING_MODEL="${SCORING_MODEL:-claude-opus-4-6}"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --topic)        TOPIC_SLUG="${2:?--topic requires a slug}";    shift 2 ;;
        --model-a)      MODEL_A="${2:?--model-a requires a value}";    shift 2 ;;
        --model-b)      MODEL_B="${2:?--model-b requires a value}";    shift 2 ;;
        --prompt-a)     PROMPT_A="${2:?--prompt-a requires a file}";   shift 2 ;;
        --prompt-b)     PROMPT_B="${2:?--prompt-b requires a file}";   shift 2 ;;
        --label-a)      LABEL_A="${2:?--label-a requires a value}";    shift 2 ;;
        --label-b)      LABEL_B="${2:?--label-b requires a value}";    shift 2 ;;
        --single)       SINGLE=true;                                    shift   ;;
        --score-only)   SCORE_ONLY_FILE="${2:?--score-only requires a file}"; SINGLE=true; shift 2 ;;
        --brief-a)      BRIEF_A_FILE="${2:?--brief-a requires a file}"; shift 2 ;;
        --brief-b)      BRIEF_B_FILE="${2:?--brief-b requires a file}"; shift 2 ;;
        --no-score)     NO_SCORE=true;                                  shift   ;;
        --scoring-model) SCORING_MODEL="${2:?--scoring-model requires a value}"; shift 2 ;;
        *)
            echo "Unknown option: $1" >&2
            echo "Usage: $0 [--topic SLUG|N] [--model-a MODEL] [--model-b MODEL]" >&2
            echo "          [--prompt-a FILE] [--prompt-b FILE] [--label-a TEXT] [--label-b TEXT]" >&2
            echo "          [--single] [--score-only FILE] [--no-score] [--scoring-model MODEL]" >&2
            echo "          [--brief-a FILE --brief-b FILE]  # score existing briefs, skip generation" >&2
            exit 1
            ;;
    esac
done

# Default prompt-b to prompt-a if not set
PROMPT_B="${PROMPT_B:-$PROMPT_A}"

# Default labels to model names
LABEL_A="${LABEL_A:-$MODEL_A}"
LABEL_B="${LABEL_B:-$MODEL_B}"

# ---------------------------------------------------------------------------
# Prerequisite checks
# ---------------------------------------------------------------------------
if [[ -z "${ANTHROPIC_API_KEY:-}" ]]; then
    echo "[ERROR] ANTHROPIC_API_KEY environment variable is not set." >&2
    exit 1
fi

if ! command -v jq &>/dev/null; then
    echo "[ERROR] 'jq' is required but not found." >&2
    exit 1
fi

if [[ -x "$SCRIPT_DIR/.venv/bin/python3" ]]; then
    PYTHON_BIN="$SCRIPT_DIR/.venv/bin/python3"
else
    PYTHON_BIN="$(command -v python3 2>/dev/null || true)"
fi
if [[ -z "$PYTHON_BIN" ]]; then
    echo "[ERROR] python3 not found." >&2
    exit 1
fi

if [[ ! -f "$AGENT_CLI" ]]; then
    echo "[ERROR] agent_cli.py not found at $AGENT_CLI" >&2
    exit 1
fi

# ---------------------------------------------------------------------------
# Resolve topic slug (default: current rotation topic)
# ---------------------------------------------------------------------------
TOPICS_FILE="$SCRIPT_DIR/topics.json"
STATE_FILE="$SCRIPT_DIR/.topic-index"
TOPIC_ARGS=()
if [[ -n "$TOPIC_SLUG" ]]; then
    TOPIC_ARGS=(--topic "$TOPIC_SLUG")
fi
TOPIC_INFO_JSON="$("$PYTHON_BIN" "$AGENT_CLI" resolve-topic \
    --topics-file "$TOPICS_FILE" \
    --state-file "$STATE_FILE" \
    "${TOPIC_ARGS[@]}")"
TOPIC_SLUG="$(printf '%s' "$TOPIC_INFO_JSON" | jq -r '.slug')"
TOPIC_LABEL="$(printf '%s' "$TOPIC_INFO_JSON" | jq -r '.label')"

# ---------------------------------------------------------------------------
# Create session directory
# ---------------------------------------------------------------------------
SESSION_ID="$(date +%Y%m%d-%H%M%S)"
EVAL_DIR="$SCRIPT_DIR/eval-runs/$SESSION_ID"
mkdir -p "$EVAL_DIR"

log() { echo "[eval $SESSION_ID] $*"; }

log "=========================================="
log "Eval session starting"
log "Topic: $TOPIC_LABEL ($TOPIC_SLUG)"
log "Output: $EVAL_DIR"
log "=========================================="

# ---------------------------------------------------------------------------
# Write session config
# ---------------------------------------------------------------------------
{
    echo "# Eval Session: $SESSION_ID"
    echo ""
    echo "**Date:** $(date '+%Y-%m-%d %H:%M:%S')"
    echo "**Topic:** $TOPIC_LABEL (\`$TOPIC_SLUG\`)"
    echo ""
    echo "## Variant Configuration"
    echo ""
    echo "| | Run A | Run B |"
    echo "|--|-------|-------|"
    if [[ "$SINGLE" == true ]]; then
        echo "| Label | $LABEL_A | *(not run)* |"
        echo "| Model | $MODEL_A | *(not run)* |"
        echo "| Prompt | $(basename "$PROMPT_A") | *(not run)* |"
    else
        echo "| Label | $LABEL_A | $LABEL_B |"
        echo "| Model | $MODEL_A | $MODEL_B |"
        echo "| Prompt | $(basename "$PROMPT_A") | $(basename "$PROMPT_B") |"
    fi
    echo ""
    echo "**Scoring model:** $SCORING_MODEL"
} > "$EVAL_DIR/config.md"

# ---------------------------------------------------------------------------
# Helper: run one research variant
# ---------------------------------------------------------------------------
run_variant() {
    local label="$1"
    local model="$2"
    local prompt_file="$3"
    local out_file="$4"

    log "Running variant $label (model=$model, prompt=$(basename "$prompt_file"))..."
    ANTHROPIC_MODEL="$model" \
        "$SCRIPT_DIR/research.sh" \
        --eval-output "$out_file" \
        --topic-slug "$TOPIC_SLUG" \
        --prompt-file "$prompt_file" \
        2> >(sed "s/^/  [${label}] /" >&2)

    if [[ ! -f "$out_file" ]]; then
        echo "[ERROR] Variant $label did not produce output at $out_file" >&2
        exit 1
    fi

    local size
    size="$(wc -c < "$out_file")"
    log "Variant $label complete: $size bytes -> $out_file"
}

# ---------------------------------------------------------------------------
# Helper: score one brief
# ---------------------------------------------------------------------------
score_variant() {
    local label="$1"
    local brief_file="$2"
    local scores_file="$3"

    log "Scoring variant $label..."
    SCORING_MODEL="$SCORING_MODEL" \
        "$PYTHON_BIN" "$SCRIPT_DIR/score_brief.py" \
        "$brief_file" \
        --topic-label "$TOPIC_LABEL" \
        --output json \
        > "$scores_file" \
        2> >(sed "s/^/  [score-${label}] /" >&2)

    if [[ ! -f "$scores_file" ]]; then
        echo "[ERROR] Scoring variant $label failed" >&2
        exit 1
    fi
    local weighted
    weighted="$(jq '.weighted_score' "$scores_file")"
    log "Variant $label score: $weighted/100"
}

# ---------------------------------------------------------------------------
# Run variant(s)
# ---------------------------------------------------------------------------
if [[ -n "$BRIEF_A_FILE" ]] && [[ -n "$BRIEF_B_FILE" ]]; then
    # Score-only mode: use caller-supplied briefs, skip generation entirely
    cp "$BRIEF_A_FILE" "$EVAL_DIR/run-a.md"
    cp "$BRIEF_B_FILE" "$EVAL_DIR/run-b.md"
    log "Using existing briefs: $(basename "$BRIEF_A_FILE") and $(basename "$BRIEF_B_FILE")"
elif [[ -n "$SCORE_ONLY_FILE" ]]; then
    cp "$SCORE_ONLY_FILE" "$EVAL_DIR/run-a.md"
    log "Using existing brief: $SCORE_ONLY_FILE"
else
    run_variant "A" "$MODEL_A" "$PROMPT_A" "$EVAL_DIR/run-a.md"
    if [[ "$SINGLE" == false ]]; then
        run_variant "B" "$MODEL_B" "$PROMPT_B" "$EVAL_DIR/run-b.md"
    fi
fi

# ---------------------------------------------------------------------------
# Score variant(s)
# ---------------------------------------------------------------------------
if [[ "$NO_SCORE" == false ]]; then
    score_variant "A" "$EVAL_DIR/run-a.md" "$EVAL_DIR/scores-a.json"
    if [[ "$SINGLE" == false ]]; then
        score_variant "B" "$EVAL_DIR/run-b.md" "$EVAL_DIR/scores-b.json"
    fi
fi

# ---------------------------------------------------------------------------
# Generate comparison report (only when both variants ran and were scored)
# ---------------------------------------------------------------------------
if [[ "$SINGLE" == false ]] && [[ "$NO_SCORE" == false ]]; then
    log "Generating comparison report..."

    SCORE_A="$(jq '.weighted_score' "$EVAL_DIR/scores-a.json")"
    SCORE_B="$(jq '.weighted_score' "$EVAL_DIR/scores-b.json")"

    "$PYTHON_BIN" "$AGENT_CLI" render-comparison \
        --session-id "$SESSION_ID" \
        --topic-label "$TOPIC_LABEL" \
        --label-a "$LABEL_A" \
        --label-b "$LABEL_B" \
        --model-a "$MODEL_A" \
        --model-b "$MODEL_B" \
        --prompt-a "$PROMPT_A" \
        --prompt-b "$PROMPT_B" \
        --scoring-model "$SCORING_MODEL" \
        --scores-a "$EVAL_DIR/scores-a.json" \
        --scores-b "$EVAL_DIR/scores-b.json" \
        --output "$EVAL_DIR/comparison.md"

    log "Comparison report: $EVAL_DIR/comparison.md"
fi

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
log "=========================================="
log "Session complete: $EVAL_DIR"
echo ""
echo "Results:"
if [[ "$NO_SCORE" == false ]]; then
    echo "  Run A ($LABEL_A): $(jq '.weighted_score' "$EVAL_DIR/scores-a.json")/100"
    if [[ "$SINGLE" == false ]]; then
        echo "  Run B ($LABEL_B): $(jq '.weighted_score' "$EVAL_DIR/scores-b.json")/100"
        echo "  Comparison: $EVAL_DIR/comparison.md"
    fi
fi
echo "  Full outputs: $EVAL_DIR/"
log "=========================================="
