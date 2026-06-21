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
WEB_REPO_DIR="/opt/research-agent/web-repo"
SCRIPTS_DIR="/opt/research-agent/scripts"

if [[ -z "${CREDENTIALS_DIRECTORY:-}" ]]; then
    echo "ERROR: CREDENTIALS_DIRECTORY not set — must be run via systemd" >&2
    exit 1
fi

# Mount the credential file directly into the container so the PAT
# never appears on the docker command line (visible via ps / systemctl status).
# The askpass script inside the container reads from this file.
CRED_FILE="${CREDENTIALS_DIRECTORY}/github-pat"

# Create a separate clone for the web app so it doesn't conflict
# with the research agent's repo when both push concurrently.
if [[ ! -d "$WEB_REPO_DIR/.git" ]]; then
    GIT_ASKPASS="$SCRIPTS_DIR/git-askpass.sh" GITHUB_PAT="$(cat "$CRED_FILE")" \
        git clone https://github.com/scottwshaw/genai-learning-agent.git "$WEB_REPO_DIR"
    chown -R "$(id -u):$(id -g)" "$WEB_REPO_DIR"
fi

exec docker run --rm \
    --name research-agent-web \
    --user "$(id -u):$(id -g)" \
    -p 5001:5001 \
    -v "${WEB_REPO_DIR}:/workspace" \
    -v "${CRED_FILE}:/run/secrets/github-pat:ro" \
    -e BRIEFS_DIR=/workspace/briefs \
    -e TOPICS_FILE=/workspace/topics.json \
    -e GIT_ASKPASS=/workspace/infra/scripts/git-askpass.sh \
    -e GIT_AUTHOR_NAME="Annotation Agent" \
    -e GIT_AUTHOR_EMAIL="agent@noreply" \
    -e GIT_COMMITTER_NAME="Annotation Agent" \
    -e GIT_COMMITTER_EMAIL="agent@noreply" \
    research-agent-web:latest
