#!/usr/bin/env bash
# =============================================================================
# run-agent.sh — Run research agent in Docker
# =============================================================================
# Runs research.sh inside a Docker container. Works both locally (credentials
# from environment) and on the server (credentials from systemd-creds).
#
# Local:  ANTHROPIC_API_KEY=sk-... ./run-agent.sh --topic safety-assurance-and-governance
# Server: systemd sets CREDENTIALS_DIRECTORY; GITHUB_PAT triggers full git flow
# =============================================================================

set -euo pipefail
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/common.sh"

LOG_PREFIX="[run-agent]"
log() { echo "${LOG_PREFIX} $(date '+%Y-%m-%d %H:%M:%S') $*"; }

# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------
NO_COMMIT=false
TOPIC_SLUG_OVERRIDE=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --no-commit)
            NO_COMMIT=true
            shift
            ;;
        --topic)
            TOPIC_SLUG_OVERRIDE="${2:?--topic requires a number or slug}"
            shift 2
            ;;
        *)
            echo "Usage: $0 [--topic N|SLUG] [--no-commit]" >&2
            exit 1
            ;;
    esac
done

# ---------------------------------------------------------------------------
# 1. Resolve credentials (env vars first, then systemd-creds)
# ---------------------------------------------------------------------------
if [[ -z "${ANTHROPIC_API_KEY:-}" ]]; then
    if [[ -n "${CREDENTIALS_DIRECTORY:-}" ]] && [[ -f "${CREDENTIALS_DIRECTORY}/anthropic-api-key" ]]; then
        ANTHROPIC_API_KEY="$(cat "${CREDENTIALS_DIRECTORY}/anthropic-api-key")"
    else
        log "ERROR: ANTHROPIC_API_KEY not set and no systemd credentials available"
        exit 1
    fi
fi

if [[ -z "${GITHUB_PAT:-}" ]]; then
    if [[ -n "${CREDENTIALS_DIRECTORY:-}" ]] && [[ -f "${CREDENTIALS_DIRECTORY}/github-pat" ]]; then
        GITHUB_PAT="$(cat "${CREDENTIALS_DIRECTORY}/github-pat")"
    fi
fi

# OpenAlex polite-pool email — optional; discovery falls back to the
# anonymous pool (worse rate limits) when absent.
if [[ -z "${OPENALEX_MAILTO:-}" ]]; then
    if [[ -n "${CREDENTIALS_DIRECTORY:-}" ]] && [[ -f "${CREDENTIALS_DIRECTORY}/openalex-mailto" ]]; then
        OPENALEX_MAILTO="$(cat "${CREDENTIALS_DIRECTORY}/openalex-mailto")"
    fi
fi
export OPENALEX_MAILTO="${OPENALEX_MAILTO:-}"

# Semantic Scholar API key — optional; anonymous access when absent.
if [[ -z "${SEMANTIC_SCHOLAR_API_KEY:-}" ]]; then
    if [[ -n "${CREDENTIALS_DIRECTORY:-}" ]] && [[ -f "${CREDENTIALS_DIRECTORY}/s2-api-key" ]]; then
        SEMANTIC_SCHOLAR_API_KEY="$(cat "${CREDENTIALS_DIRECTORY}/s2-api-key")"
    fi
fi
export SEMANTIC_SCHOLAR_API_KEY="${SEMANTIC_SCHOLAR_API_KEY:-}"

export ANTHROPIC_API_KEY
# GITHUB_PAT intentionally not exported — only used by this script for git ops

# If no GITHUB_PAT, force --no-commit
if [[ -z "${GITHUB_PAT:-}" ]]; then
    NO_COMMIT=true
fi

# ---------------------------------------------------------------------------
# 2. Server mode: pull latest code and create branch
# ---------------------------------------------------------------------------
DATE="$(date +%Y-%m-%d)"

if [[ "$NO_COMMIT" == false ]]; then
    export GIT_ASKPASS="${REPO_ROOT}/infra/scripts/git-askpass.sh"
    export GH_TOKEN="$GITHUB_PAT"
    export GITHUB_PAT

    cd "$REPO_ROOT"
    git checkout main 2>/dev/null || true

    log "Pulling latest changes..."
    git pull --ff-only

    resolve_topic "$TOPIC_SLUG_OVERRIDE"
    BRANCH="research/${DATE}-${TOPIC_SLUG}"

    git branch -D "$BRANCH" 2>/dev/null || true
    log "Creating branch: ${BRANCH}"
    git checkout -b "$BRANCH"
else
    resolve_topic "$TOPIC_SLUG_OVERRIDE"
fi

# ---------------------------------------------------------------------------
# 3. Run the containerised research agent
# ---------------------------------------------------------------------------
log "Starting research container..."

mkdir -p "${REPO_ROOT}/briefs" "${REPO_ROOT}/eval-runs"

CONTAINER_ARGS=(--topic-slug "$TOPIC_SLUG")
if [[ "$NO_COMMIT" == false ]]; then
    # Server mode: direct output to briefs/ via --output-file (skips git commit
    # and index advancement inside the container — the host handles both)
    BRIEF_DIR="${REPO_ROOT}/briefs/${DATE}-${TOPIC_SLUG}"
    mkdir -p "$BRIEF_DIR"
    BRIEF_FILE="${BRIEF_DIR}/brief.md"
    CONTAINER_ARGS+=(--output-file "/workspace/briefs/${DATE}-${TOPIC_SLUG}/brief.md")
else
    # Local mode: --no-commit sends output to eval-runs/
    CONTAINER_ARGS+=(--no-commit)
fi

touch "${REPO_ROOT}/agent.log"

docker run --rm \
    --read-only \
    --tmpfs /tmp \
    --user "$(id -u):$(id -g)" \
    -e ANTHROPIC_API_KEY \
    -e OPENALEX_MAILTO \
    -e SEMANTIC_SCHOLAR_API_KEY \
    -e ENABLE_CRITIC=1 \
    -v "${REPO_ROOT}:/workspace:ro" \
    -v "${REPO_ROOT}/briefs:/workspace/briefs" \
    -v "${REPO_ROOT}/eval-runs:/workspace/eval-runs" \
    -v "${REPO_ROOT}/agent.log:/workspace/agent.log" \
    research-agent:latest \
    ./research.sh "${CONTAINER_ARGS[@]}"

log "Research container finished"

# ---------------------------------------------------------------------------
# 4. Server mode: commit, push, create PR, clean up
# ---------------------------------------------------------------------------
if [[ "$NO_COMMIT" == false ]]; then
    if [[ ! -f "$BRIEF_FILE" ]]; then
        log "ERROR: Expected brief not found at $BRIEF_FILE"
        git checkout main
        exit 1
    fi

    cd "$REPO_ROOT"

    git add "$BRIEF_FILE"

    if git diff --cached --quiet; then
        log "Nothing new to commit"
    else
        git commit -m "research(${DATE}): ${TOPIC_LABEL}

Daily brief on '${TOPIC_LABEL}' (area $((TOPIC_IDX + 1))/${TOPIC_COUNT}).
Generated by learning-agent on $(hostname)."
        log "Committed: research(${DATE}): ${TOPIC_LABEL}"
    fi

    # Advance topic index
    echo "$TOPIC_NEXT_IDX" > "$STATE_FILE"

    log "Pushing branch..."
    git push -u origin "$BRANCH"

    log "Creating pull request..."
    gh pr create \
        --title "research(${DATE}): ${TOPIC_LABEL}" \
        --body "Daily research brief on **${TOPIC_LABEL}** (${DATE}).

Generated automatically by the research agent." \
        --base main

    log "Pull request created"

    git checkout main
    git branch -d "$BRANCH"
fi

log "Done"
