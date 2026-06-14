#!/usr/bin/env bash
# =============================================================================
# web-start.sh — Bootstrap wrapper for the annotation web app
# =============================================================================
# Called by systemd (web-app.service). Reads the 1Password service account
# token from systemd credentials, fetches GITHUB_PAT, then starts Flask.
# Credentials are memory-only; nothing is written to disk.
# =============================================================================

set -euo pipefail

REPO_DIR="/opt/research-agent/repo"
SCRIPTS_DIR="/opt/research-agent/scripts"

if [[ -z "${CREDENTIALS_DIRECTORY:-}" ]]; then
    echo "ERROR: CREDENTIALS_DIRECTORY not set — must be run via systemd" >&2
    exit 1
fi

export OP_SERVICE_ACCOUNT_TOKEN
OP_SERVICE_ACCOUNT_TOKEN="$(cat "${CREDENTIALS_DIRECTORY}/op-token")"

export GITHUB_PAT
GITHUB_PAT="$(op read "op://research-agent/OC_GITHUB_TOKEN/credential")"

export GIT_ASKPASS="${SCRIPTS_DIR}/git-askpass.sh"
export GH_TOKEN="$GITHUB_PAT"

# Ensure git identity is set (needed for annotation commits)
git -C "$REPO_DIR" config user.name "Annotation Agent"
git -C "$REPO_DIR" config user.email "agent@noreply"

exec python3 "${REPO_DIR}/web/app.py"
