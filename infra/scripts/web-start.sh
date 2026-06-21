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

# Mount the credential file directly into the container so the PAT
# never appears on the docker command line (visible via ps / systemctl status).
# The askpass script inside the container reads from this file.
CRED_FILE="${CREDENTIALS_DIRECTORY}/github-pat"

exec docker run --rm \
    --name research-agent-web \
    --user "$(id -u):$(id -g)" \
    -p 5001:5001 \
    -v "${REPO_DIR}:/workspace" \
    -v "${CRED_FILE}:/run/secrets/github-pat:ro" \
    -e BRIEFS_DIR=/workspace/briefs \
    -e TOPICS_FILE=/workspace/topics.json \
    -e GIT_ASKPASS=/workspace/infra/scripts/git-askpass.sh \
    -e GIT_AUTHOR_NAME="Annotation Agent" \
    -e GIT_AUTHOR_EMAIL="agent@noreply" \
    -e GIT_COMMITTER_NAME="Annotation Agent" \
    -e GIT_COMMITTER_EMAIL="agent@noreply" \
    research-agent-web:latest
