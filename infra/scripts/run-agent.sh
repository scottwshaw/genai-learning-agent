#!/usr/bin/env bash
# =============================================================================
# run-agent.sh — Bootstrap wrapper (deployed once to /opt/research-agent/scripts/)
# =============================================================================
# Called by systemd (research-agent.service). Reads credentials, pulls the
# latest repo, then hands off to run-remote.sh in the repo for all app logic.
#
# This script should rarely need updating. All research logic lives in the
# repo and is kept current via git pull.
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
# 3. Pull latest repo (prompt tweaks, script changes pushed from Mac)
# ---------------------------------------------------------------------------
export GIT_ASKPASS="${SCRIPTS_DIR}/git-askpass.sh"
export GH_TOKEN="$GITHUB_PAT"

cd "$REPO_DIR"

# Ensure we're on main before pulling (clean up from any prior failed run)
git checkout main 2>/dev/null || true

log "Pulling latest changes..."
git pull --ff-only

# ---------------------------------------------------------------------------
# 4. Hand off to repo script for all application logic
# ---------------------------------------------------------------------------
exec ./run-remote.sh
