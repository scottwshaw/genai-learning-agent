#!/usr/bin/env bash
# =============================================================================
# eval.sh — Evaluate one research run, with optional comparison
# =============================================================================
# Default behavior is a single eval run: generate one brief (or use an existing
# brief), then score it against the rubric. Comparison is optional and layered
# on top of the single-run flow.
#
# Usage:
#   ./eval.sh [options]
#
# Primary run options:
#   --topic SLUG|N       Topic to evaluate (default: current rotation topic)
#   --model MODEL        Model for the primary run (default: claude-sonnet-4-6)
#   --prompt FILE        Prompt template for the primary run
#                        (default: prompts/research-prompt.md)
#   --label TEXT         Human label for the primary run (default: model name)
#   --brief FILE         Score an existing brief instead of generating one
#
# Optional comparison:
#   --compare-model M    Generate and score a comparison run with model M
#   --compare-prompt F   Prompt template for the comparison run
#                        (default: same as primary)
#   --compare-label T    Human label for the comparison run
#   --compare-brief F    Compare against an existing brief instead of generating
#
# General options:
#   --no-score           Generate brief(s) but skip scoring
#   --scoring-model M    Model to use for rubric scoring
#
# Outputs (in eval-runs/YYYYMMDD-HHMMSS/):
#   config.md            Session config summary
#   run.md               Primary brief
#   scores.json          Primary rubric score
#   scores.md            Primary rubric score report
#   compare.md           Comparison brief (if comparison enabled)
#   compare-scores.json  Comparison rubric score (if comparison enabled)
#   compare-scores.md    Comparison rubric score report (if comparison enabled)
#   comparison.md        Side-by-side comparison report (if both scored)
# =============================================================================

set -euo pipefail

# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------
TOPIC_SLUG=""
MODEL="claude-sonnet-4-6"
PROMPT=""  # default set after sourcing common.sh
LABEL=""
BRIEF_FILE=""

COMPARE_MODEL=""
COMPARE_PROMPT=""
COMPARE_LABEL=""
COMPARE_BRIEF_FILE=""

NO_SCORE=false
SCORING_MODEL="${SCORING_MODEL:-claude-opus-4-6}"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --topic)          TOPIC_SLUG="${2:?--topic requires a slug or index}"; shift 2 ;;
        --model)          MODEL="${2:?--model requires a value}"; shift 2 ;;
        --prompt)         PROMPT="${2:?--prompt requires a file}"; shift 2 ;;
        --label)          LABEL="${2:?--label requires a value}"; shift 2 ;;
        --brief)          BRIEF_FILE="${2:?--brief requires a file}"; shift 2 ;;
        --compare-model)  COMPARE_MODEL="${2:?--compare-model requires a value}"; shift 2 ;;
        --compare-prompt) COMPARE_PROMPT="${2:?--compare-prompt requires a file}"; shift 2 ;;
        --compare-label)  COMPARE_LABEL="${2:?--compare-label requires a value}"; shift 2 ;;
        --compare-brief)  COMPARE_BRIEF_FILE="${2:?--compare-brief requires a file}"; shift 2 ;;
        --no-score)       NO_SCORE=true; shift ;;
        --scoring-model)  SCORING_MODEL="${2:?--scoring-model requires a value}"; shift 2 ;;
        *)
            echo "Unknown option: $1" >&2
            echo "Usage: $0 [--topic SLUG|N] [--model MODEL] [--prompt FILE] [--label TEXT] [--brief FILE]" >&2
            echo "          [--compare-model MODEL] [--compare-prompt FILE] [--compare-label TEXT]" >&2
            echo "          [--compare-brief FILE] [--no-score] [--scoring-model MODEL]" >&2
            exit 1
            ;;
    esac
done

# ---------------------------------------------------------------------------
# Shared setup (python, jq, agent_cli, topic resolution helper)
# ---------------------------------------------------------------------------
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/common.sh"

# ---------------------------------------------------------------------------
# Defaults that depend on REPO_ROOT
# ---------------------------------------------------------------------------
PROMPT="${PROMPT:-$REPO_ROOT/prompts/research-prompt.md}"
LABEL="${LABEL:-$MODEL}"
COMPARE_PROMPT="${COMPARE_PROMPT:-$PROMPT}"

COMPARE_ENABLED=false
if [[ -n "$COMPARE_MODEL" ]] || [[ -n "$COMPARE_BRIEF_FILE" ]]; then
    COMPARE_ENABLED=true
fi

if [[ "$COMPARE_ENABLED" == true ]]; then
    if [[ -n "$COMPARE_MODEL" ]] && [[ -n "$COMPARE_BRIEF_FILE" ]]; then
        echo "[ERROR] Use either --compare-model or --compare-brief, not both." >&2
        exit 1
    fi
    if [[ -n "$COMPARE_BRIEF_FILE" ]]; then
        COMPARE_LABEL="${COMPARE_LABEL:-$(basename "$COMPARE_BRIEF_FILE")}"
    else
        COMPARE_LABEL="${COMPARE_LABEL:-$COMPARE_MODEL}"
    fi
fi

NEEDS_GENERATION=false
if [[ -z "$BRIEF_FILE" ]] || ([[ "$COMPARE_ENABLED" == true ]] && [[ -z "$COMPARE_BRIEF_FILE" ]]); then
    NEEDS_GENERATION=true
fi

NEEDS_API_KEY=false
if [[ "$NEEDS_GENERATION" == true ]] || [[ "$NO_SCORE" == false ]]; then
    NEEDS_API_KEY=true
fi

if [[ "$NEEDS_API_KEY" == true ]] && [[ -z "${ANTHROPIC_API_KEY:-}" ]]; then
    echo "[ERROR] ANTHROPIC_API_KEY environment variable is not set." >&2
    exit 1
fi

# ---------------------------------------------------------------------------
# Resolve topic
# ---------------------------------------------------------------------------
resolve_topic "$TOPIC_SLUG"

SESSION_ID="$(date +%Y%m%d-%H%M%S)"
EVAL_DIR="$REPO_ROOT/eval-runs/$SESSION_ID"
if [[ -e "$EVAL_DIR" ]]; then
    SESSION_ID="${SESSION_ID}-$$"
    EVAL_DIR="$REPO_ROOT/eval-runs/$SESSION_ID"
fi
mkdir -p "$EVAL_DIR"

PRIMARY_BRIEF_OUT="$EVAL_DIR/run.md"
PRIMARY_SCORE_OUT="$EVAL_DIR/scores.json"
PRIMARY_SCORE_REPORT_OUT="$EVAL_DIR/scores.md"
PRIMARY_METADATA_OUT="$EVAL_DIR/run.metadata.json"
PRIMARY_PROMPT_DIFF_OUT="$EVAL_DIR/run.prompt.diff.patch"
COMPARE_BRIEF_OUT="$EVAL_DIR/compare.md"
COMPARE_SCORE_OUT="$EVAL_DIR/compare-scores.json"
COMPARE_SCORE_REPORT_OUT="$EVAL_DIR/compare-scores.md"
COMPARE_METADATA_OUT="$EVAL_DIR/compare.metadata.json"
COMPARE_PROMPT_DIFF_OUT="$EVAL_DIR/compare.prompt.diff.patch"
RECORDED_AT="$(date '+%Y-%m-%d %H:%M:%S')"
GIT_HEAD="$(git -C "$REPO_ROOT" rev-parse HEAD 2>/dev/null || echo "")"

log() { echo "[eval $SESSION_ID] $*"; }

log "=========================================="
log "Eval session starting"
log "Topic: $TOPIC_LABEL ($TOPIC_SLUG)"
log "Output: $EVAL_DIR"
log "=========================================="

write_config() {
    {
        echo "# Eval Session: $SESSION_ID"
        echo ""
        echo "**Date:** $(date '+%Y-%m-%d %H:%M:%S')"
        echo "**Topic:** $TOPIC_LABEL (\`$TOPIC_SLUG\`)"
        echo ""
        echo "## Primary Run"
        echo ""
        echo "| Field | Value |"
        echo "|-------|-------|"
        echo "| Label | $LABEL |"
        echo "| Model | $MODEL |"
        echo "| Prompt | $(basename "$PROMPT") |"
        if [[ -n "$BRIEF_FILE" ]]; then
            echo "| Source | existing brief: $(basename "$BRIEF_FILE") |"
        else
            echo "| Source | generated |"
        fi
        echo ""
        if [[ "$COMPARE_ENABLED" == true ]]; then
            echo "## Comparison Run"
            echo ""
            echo "| Field | Value |"
            echo "|-------|-------|"
            echo "| Label | $COMPARE_LABEL |"
            if [[ -n "$COMPARE_BRIEF_FILE" ]]; then
                echo "| Source | existing brief: $(basename "$COMPARE_BRIEF_FILE") |"
                echo "| Model | *(not run)* |"
                echo "| Prompt | *(not run)* |"
            else
                echo "| Source | generated |"
                echo "| Model | $COMPARE_MODEL |"
                echo "| Prompt | $(basename "$COMPARE_PROMPT") |"
            fi
            echo ""
        fi
        echo "**Scoring model:** $SCORING_MODEL"
    } > "$EVAL_DIR/config.md"
}

run_brief() {
    local label="$1"
    local model="$2"
    local prompt_file="$3"
    local out_file="$4"

    log "Running $label (model=$model, prompt=$(basename "$prompt_file"))..."
    ANTHROPIC_MODEL="$model" \
        "$REPO_ROOT/research.sh" \
        --eval-output "$out_file" \
        --topic-slug "$TOPIC_SLUG" \
        --prompt-file "$prompt_file" \
        2> >(sed "s/^/  [${label}] /" >&2)

    if [[ ! -f "$out_file" ]]; then
        echo "[ERROR] $label did not produce output at $out_file" >&2
        exit 1
    fi

    local size
    size="$(wc -c < "$out_file")"
    log "$label complete: $size bytes -> $out_file"
}

use_existing_brief() {
    local source_file="$1"
    local dest_file="$2"
    local label="$3"

    cp "$source_file" "$dest_file"
    log "Using existing $label brief: $source_file"
}

score_brief_file() {
    local label="$1"
    local brief_file="$2"
    local scores_file="$3"
    local report_file="$4"

    log "Scoring $label..."
    SCORING_MODEL="$SCORING_MODEL" \
        "$PYTHON_BIN" "$REPO_ROOT/score_brief.py" \
        "$brief_file" \
        --topic-label "$TOPIC_LABEL" \
        --output json \
        > "$scores_file" \
        2> >(sed "s/^/  [score-${label}] /" >&2)

    if [[ ! -f "$scores_file" ]]; then
        echo "[ERROR] Scoring $label failed" >&2
        exit 1
    fi
    "$PYTHON_BIN" "$AGENT_CLI" render-score-report \
        --score-json "$scores_file" \
        --brief-file "$brief_file" \
        --topic-label "$TOPIC_LABEL" \
        --output "$report_file"
    log "$label score: $(jq '.weighted_score' "$scores_file")/100"
}

annotate_brief_file() {
    local brief_file="$1"
    local metadata_file="$2"
    local role="$3"
    local label="$4"
    local model="$5"
    local prompt_file="$6"
    local source_type="$7"
    local source_file="${8:-}"
    local prompt_git_commit="${9:-}"
    local prompt_git_status="${10:-}"
    local prompt_diff="${11:-}"

    local cmd=(
        "$PYTHON_BIN" "$AGENT_CLI" annotate-brief
        --brief "$brief_file" \
        --metadata-output "$metadata_file" \
        --session-id "$SESSION_ID" \
        --recorded-at "$RECORDED_AT" \
        --role "$role" \
        --topic-slug "$TOPIC_SLUG" \
        --topic-label "$TOPIC_LABEL" \
        --label "$label" \
        --source-type "$source_type" \
        --scoring-model "$SCORING_MODEL"
    )
    if [[ -n "$model" ]]; then
        cmd+=(--model "$model")
    fi
    if [[ -n "$prompt_file" ]]; then
        cmd+=(--prompt "$prompt_file")
        cmd+=(--prompt-path "$prompt_file")
    fi
    if [[ -n "$GIT_HEAD" ]]; then
        cmd+=(--git-head "$GIT_HEAD")
    fi
    if [[ -n "$prompt_git_commit" ]]; then
        cmd+=(--prompt-git-commit "$prompt_git_commit")
    fi
    if [[ -n "$prompt_git_status" ]]; then
        cmd+=(--prompt-git-status "$prompt_git_status")
    fi
    if [[ -n "$prompt_diff" ]]; then
        cmd+=(--prompt-diff "$prompt_diff")
    fi
    if [[ -n "$source_file" ]]; then
        cmd+=(--source-file "$source_file")
    fi
    "${cmd[@]}"
}

capture_prompt_provenance() {
    local prompt_file="$1"
    local diff_out="$2"
    local prompt_git_path="$prompt_file"
    local prompt_commit_ref=""
    local prompt_status_ref=""
    local prompt_diff_ref=""

    if [[ "$prompt_git_path" == "$REPO_ROOT/"* ]]; then
        prompt_git_path="${prompt_git_path#$REPO_ROOT/}"
    fi

    if git -C "$REPO_ROOT" ls-files --error-unmatch -- "$prompt_git_path" >/dev/null 2>&1; then
        prompt_commit_ref="$(git -C "$REPO_ROOT" rev-list -1 HEAD -- "$prompt_git_path" 2>/dev/null || true)"
        if ! git -C "$REPO_ROOT" diff --quiet -- "$prompt_git_path"; then
            prompt_status_ref="modified"
            git -C "$REPO_ROOT" diff -- "$prompt_git_path" > "$diff_out"
            prompt_diff_ref="$diff_out"
        else
            prompt_status_ref="clean"
            rm -f "$diff_out"
        fi
    else
        prompt_status_ref="untracked"
        rm -f "$diff_out"
    fi

    printf '%s\n%s\n%s\n' "$prompt_commit_ref" "$prompt_status_ref" "$prompt_diff_ref"
}

write_config

if [[ -n "$BRIEF_FILE" ]]; then
    use_existing_brief "$BRIEF_FILE" "$PRIMARY_BRIEF_OUT" "primary"
    annotate_brief_file "$PRIMARY_BRIEF_OUT" "$PRIMARY_METADATA_OUT" "primary" "$LABEL" "" "" "existing-brief" "$BRIEF_FILE"
else
    PRIMARY_PROMPT_COMMIT=""
    PRIMARY_PROMPT_STATUS=""
    PRIMARY_PROMPT_DIFF=""
    IFS=$'\n' read -r PRIMARY_PROMPT_COMMIT PRIMARY_PROMPT_STATUS PRIMARY_PROMPT_DIFF <<EOF
$(capture_prompt_provenance "$PROMPT" "$PRIMARY_PROMPT_DIFF_OUT")
EOF
    run_brief "$LABEL" "$MODEL" "$PROMPT" "$PRIMARY_BRIEF_OUT"
    annotate_brief_file "$PRIMARY_BRIEF_OUT" "$PRIMARY_METADATA_OUT" "primary" "$LABEL" "$MODEL" "$PROMPT" "generated" "" "$PRIMARY_PROMPT_COMMIT" "$PRIMARY_PROMPT_STATUS" "$PRIMARY_PROMPT_DIFF"
fi

if [[ "$COMPARE_ENABLED" == true ]]; then
    if [[ -n "$COMPARE_BRIEF_FILE" ]]; then
        use_existing_brief "$COMPARE_BRIEF_FILE" "$COMPARE_BRIEF_OUT" "comparison"
        annotate_brief_file "$COMPARE_BRIEF_OUT" "$COMPARE_METADATA_OUT" "comparison" "$COMPARE_LABEL" "" "" "existing-brief" "$COMPARE_BRIEF_FILE"
    else
        COMPARE_PROMPT_COMMIT=""
        COMPARE_PROMPT_STATUS=""
        COMPARE_PROMPT_DIFF=""
        IFS=$'\n' read -r COMPARE_PROMPT_COMMIT COMPARE_PROMPT_STATUS COMPARE_PROMPT_DIFF <<EOF
$(capture_prompt_provenance "$COMPARE_PROMPT" "$COMPARE_PROMPT_DIFF_OUT")
EOF
        run_brief "$COMPARE_LABEL" "$COMPARE_MODEL" "$COMPARE_PROMPT" "$COMPARE_BRIEF_OUT"
        annotate_brief_file "$COMPARE_BRIEF_OUT" "$COMPARE_METADATA_OUT" "comparison" "$COMPARE_LABEL" "$COMPARE_MODEL" "$COMPARE_PROMPT" "generated" "" "$COMPARE_PROMPT_COMMIT" "$COMPARE_PROMPT_STATUS" "$COMPARE_PROMPT_DIFF"
    fi
fi

if [[ "$NO_SCORE" == false ]]; then
    score_brief_file "$LABEL" "$PRIMARY_BRIEF_OUT" "$PRIMARY_SCORE_OUT" "$PRIMARY_SCORE_REPORT_OUT"
    if [[ "$COMPARE_ENABLED" == true ]]; then
        score_brief_file "$COMPARE_LABEL" "$COMPARE_BRIEF_OUT" "$COMPARE_SCORE_OUT" "$COMPARE_SCORE_REPORT_OUT"
    fi
fi

if [[ "$COMPARE_ENABLED" == true ]] && [[ "$NO_SCORE" == false ]]; then
    log "Generating comparison report..."
    "$PYTHON_BIN" "$AGENT_CLI" render-comparison \
        --session-id "$SESSION_ID" \
        --topic-label "$TOPIC_LABEL" \
        --label-a "$LABEL" \
        --label-b "$COMPARE_LABEL" \
        --model-a "$MODEL" \
        --model-b "${COMPARE_MODEL:-existing-brief}" \
        --prompt-a "$PROMPT" \
        --prompt-b "$COMPARE_PROMPT" \
        --scoring-model "$SCORING_MODEL" \
        --scores-a "$PRIMARY_SCORE_OUT" \
        --scores-b "$COMPARE_SCORE_OUT" \
        --output "$EVAL_DIR/comparison.md"
    log "Comparison report: $EVAL_DIR/comparison.md"
fi

log "=========================================="
log "Session complete: $EVAL_DIR"
echo ""
echo "Results:"
if [[ "$NO_SCORE" == false ]]; then
    echo "  $LABEL: $(jq '.weighted_score' "$PRIMARY_SCORE_OUT")/100"
    if [[ "$COMPARE_ENABLED" == true ]]; then
        echo "  $COMPARE_LABEL: $(jq '.weighted_score' "$COMPARE_SCORE_OUT")/100"
        echo "  Comparison: $EVAL_DIR/comparison.md"
    fi
fi
echo "  Full outputs: $EVAL_DIR/"
log "=========================================="
