#!/usr/bin/env bash
# =============================================================================
# web-start.sh — Bootstrap wrapper for the annotation web app
# =============================================================================
# Called by systemd (web-app.service). Reads credentials from systemd-creds,
# configures git, then runs the Flask app in a Docker container.
# Credentials are memory-only; nothing is written to disk.
# =============================================================================

set -euo pipefail

REPO_DIR="/opt/research-agent/repo"
SCRIPTS_DIR="/opt/research-agent/scripts"

if [[ -z "${CREDENTIALS_DIRECTORY:-}" ]]; then
    echo "ERROR: CREDENTIALS_DIRECTORY not set — must be run via systemd" >&2
    exit 1
fi

OP_TOKEN="$(cat "${CREDENTIALS_DIRECTORY}/op-token")"
GITHUB_PAT="$(cat "${CREDENTIALS_DIRECTORY}/github-pat")"

export GIT_ASKPASS="${SCRIPTS_DIR}/git-askpass.sh"
export GH_TOKEN="$GITHUB_PAT"

git -C "$REPO_DIR" config user.name "Annotation Agent"
git -C "$REPO_DIR" config user.email "agent@noreply"

exec docker run --rm \
    --name research-agent-web \
    -p 5001:5001 \
    -v "${REPO_DIR}:/workspace" \
    -e BRIEFS_DIR=/workspace/briefs \
    -e TOPICS_FILE=/workspace/topics.json \
    -e GITHUB_PAT="$GITHUB_PAT" \
    -e GH_TOKEN="$GITHUB_PAT" \
    -e OP_SERVICE_ACCOUNT_TOKEN="$OP_TOKEN" \
    -e GIT_ASKPASS=/workspace/infra/scripts/git-askpass.sh \
    research-agent-web:latest
