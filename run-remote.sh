#!/usr/bin/env bash
# =============================================================================
# run-remote.sh — Research agent application logic (lives in the repo)
# =============================================================================
# Called by the bootstrap script (run-agent.sh) after credentials are loaded
# and the repo is up to date. All env vars (ANTHROPIC_API_KEY, GITHUB_PAT,
# GIT_ASKPASS, GH_TOKEN) are already exported by the bootstrap.
#
# This script handles: topic resolution, branch creation, Docker run,
# push, and PR creation.
# =============================================================================

set -euo pipefail
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/common.sh"

LOG_PREFIX="[run-remote]"
log() { echo "${LOG_PREFIX} $(date '+%Y-%m-%d %H:%M:%S') $*"; }

# ---------------------------------------------------------------------------
# 1. Determine today's topic (resolved once, used everywhere)
# ---------------------------------------------------------------------------
DATE="$(date +%Y-%m-%d)"
resolve_topic
BRANCH="research/${DATE}-${TOPIC_SLUG}"

# Delete stale branch from a prior failed run if it exists
git branch -D "$BRANCH" 2>/dev/null || true

log "Creating branch: ${BRANCH}"
git checkout -b "$BRANCH"

# ---------------------------------------------------------------------------
# 2. Run the containerised research agent
# ---------------------------------------------------------------------------
log "Starting research container..."

docker run --rm \
    --read-only \
    --tmpfs /tmp \
    --user "$(id -u):$(id -g)" \
    -e ANTHROPIC_API_KEY \
    -e ENABLE_CRITIC=1 \
    -v "${REPO_ROOT}:/workspace" \
    research-agent:latest \
    ./research.sh --topic-slug "$TOPIC_SLUG"

log "Research container finished"

# ---------------------------------------------------------------------------
# 3. Push branch and create PR
# ---------------------------------------------------------------------------
log "Pushing branch..."
git push -u origin "$BRANCH"

log "Creating pull request..."
gh pr create \
    --title "research(${DATE}): ${TOPIC_LABEL}" \
    --body "Daily research brief on **${TOPIC_LABEL}** (${DATE}).

Generated automatically by the research agent." \
    --base main

log "Pull request created"

# ---------------------------------------------------------------------------
# 4. Clean up — return to main for next run
# ---------------------------------------------------------------------------
git checkout main
git branch -d "$BRANCH"

log "Done"
