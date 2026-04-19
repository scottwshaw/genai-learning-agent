#!/usr/bin/env bash
# =============================================================================
# run-agent.sh — Daily research agent wrapper
# =============================================================================
# Called by systemd (research-agent.service). Fetches secrets from 1Password,
# runs the containerised research agent, then pushes results as a PR.
#
# Secrets flow:
#   1Password SA token (systemd LoadCredential) → op read → env vars → container
#   PAT never touches disk — git auth via GIT_ASKPASS, gh auth via GH_TOKEN.
# =============================================================================

set -euo pipefail

REPO_DIR="/opt/research-agent/repo"
SCRIPTS_DIR="/opt/research-agent/scripts"
LOG_PREFIX="[run-agent]"

log() { echo "${LOG_PREFIX} $(date '+%Y-%m-%d %H:%M:%S') $*"; }

# ---------------------------------------------------------------------------
# 1. Read 1Password service account token from systemd credential
# ---------------------------------------------------------------------------
if [[ -z "${CREDENTIALS_DIRECTORY:-}" ]]; then
    log "ERROR: CREDENTIALS_DIRECTORY not set — must be run via systemd"
    exit 1
fi

export OP_SERVICE_ACCOUNT_TOKEN
OP_SERVICE_ACCOUNT_TOKEN="$(cat "${CREDENTIALS_DIRECTORY}/op-token")"

# ---------------------------------------------------------------------------
# 2. Fetch secrets from 1Password (memory only, never written to disk)
# ---------------------------------------------------------------------------
log "Fetching secrets from 1Password..."

ANTHROPIC_API_KEY="$(op read "op://research-agent/ANTHROPIC_API_KEY/credential")"
GITHUB_PAT="$(op read "op://research-agent/OC_GITHUB_TOKEN/credential")"

if [[ -z "$ANTHROPIC_API_KEY" || -z "$GITHUB_PAT" ]]; then
    log "ERROR: Failed to fetch one or more secrets from 1Password"
    exit 1
fi

export ANTHROPIC_API_KEY GITHUB_PAT

# ---------------------------------------------------------------------------
# 3. Pull latest changes (prompt tweaks pushed from Mac)
# ---------------------------------------------------------------------------
export GIT_ASKPASS="${SCRIPTS_DIR}/git-askpass.sh"
export GH_TOKEN="$GITHUB_PAT"

cd "$REPO_DIR"

# Ensure we're on main before pulling (clean up from any prior failed run)
git checkout main 2>/dev/null || true

log "Pulling latest changes..."
git pull --ff-only

# ---------------------------------------------------------------------------
# 4. Determine today's topic for the branch name
# ---------------------------------------------------------------------------
DATE="$(date +%Y-%m-%d)"
TOPIC_SLUG="$(python3 agent_cli.py resolve-topic \
    --topics-file topics.json \
    --state-file .topic-index \
    | jq -r '.slug')"
BRANCH="research/${DATE}-${TOPIC_SLUG}"

# Delete stale branch from a prior failed run if it exists
git branch -D "$BRANCH" 2>/dev/null || true

log "Creating branch: ${BRANCH}"
git checkout -b "$BRANCH"

# ---------------------------------------------------------------------------
# 5. Run the containerised research agent
# ---------------------------------------------------------------------------
log "Starting research container..."

docker run --rm \
    --read-only \
    --tmpfs /tmp \
    -e ANTHROPIC_API_KEY \
    -e ENABLE_CRITIC=1 \
    -v "${REPO_DIR}:/workspace" \
    research-agent:latest \
    ./research.sh

log "Research container finished"

# ---------------------------------------------------------------------------
# 6. Push branch and create PR
# ---------------------------------------------------------------------------
log "Pushing branch..."
git push -u origin "$BRANCH"

log "Creating pull request..."
TOPIC_LABEL="$(python3 agent_cli.py resolve-topic \
    --topics-file topics.json \
    --state-file .topic-index \
    | jq -r '.label')"

gh pr create \
    --title "research(${DATE}): ${TOPIC_LABEL}" \
    --body "Daily research brief on **${TOPIC_LABEL}** (${DATE}).

Generated automatically by the research agent." \
    --base main

log "Pull request created"

# ---------------------------------------------------------------------------
# 7. Clean up — return to main for next run
# ---------------------------------------------------------------------------
git checkout main
git branch -d "$BRANCH"

log "Done"
