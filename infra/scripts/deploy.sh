#!/usr/bin/env bash
# =============================================================================
# deploy.sh — One-shot server setup after terraform apply
# =============================================================================
# Waits for cloud-init, copies project files, builds the Docker image,
# places the 1Password service account token, and enables the systemd timer.
#
# Run from: infra/scripts/
# Prerequisites: terraform apply has completed, server is reachable via SSH.
#
# Resuming a failed deploy:
#   ./deploy.sh                  # full deploy
#   ./deploy.sh --from tailscale # skip straight to the Tailscale stage
# Secrets are always fetched from 1Password first (they live only in memory),
# then deployment jumps to the named stage. See --help for the stage list.
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INFRA_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
TERRAFORM_DIR="${INFRA_DIR}/terraform"

# ---------------------------------------------------------------------------
# 0. Argument parsing — optional resume point
# ---------------------------------------------------------------------------
# Ordered list of skippable stages. Secret-fetching always runs first and is
# deliberately NOT in this list.
ALL_STAGES=(cloud-init copy build creds timer web tailscale)

usage() {
    cat <<EOF
Usage: $(basename "$0") [--from STAGE]

Runs the full deploy by default. Secrets are always fetched from 1Password
first (they live only in memory), then deployment proceeds.

  --from STAGE   Skip everything before STAGE so you can resume a failed
                 deploy without rerunning earlier steps. Secrets are still
                 fetched first. Stages, in order:
                   ${ALL_STAGES[*]}
  -h, --help     Show this help.

Examples:
  $(basename "$0")                   # full deploy
  $(basename "$0") --from tailscale  # re-run just the Tailscale stage
EOF
}

START_STAGE=""
case "${1:-}" in
    "") ;;
    --from)
        START_STAGE="${2:-}"
        if [[ -z "$START_STAGE" ]]; then
            echo "ERROR: --from requires a stage name."; echo; usage; exit 1
        fi
        ;;
    -h|--help) usage; exit 0 ;;
    *) echo "ERROR: unknown argument: $1"; echo; usage; exit 1 ;;
esac

if [[ -n "$START_STAGE" ]]; then
    _valid=0
    for _s in "${ALL_STAGES[@]}"; do [[ "$_s" == "$START_STAGE" ]] && _valid=1; done
    if [[ "$_valid" == "0" ]]; then
        echo "ERROR: unknown stage '$START_STAGE'. Valid stages: ${ALL_STAGES[*]}"
        exit 1
    fi
fi

# should_run STAGE -> true once we've reached START_STAGE (or always, if no
# --from was given). Earlier stages are silently skipped.
_reached=0
should_run() {
    [[ -z "$START_STAGE" ]] && return 0
    [[ "$_reached" == "1" ]] && return 0
    if [[ "$1" == "$START_STAGE" ]]; then _reached=1; return 0; fi
    return 1
}

# ---------------------------------------------------------------------------
# 1. Get server IP from Terraform
# ---------------------------------------------------------------------------
SERVER_IP="$(cd "$TERRAFORM_DIR" && terraform output -raw server_ip)"
if [[ -z "$SERVER_IP" ]]; then
    echo "ERROR: Could not read server_ip from Terraform output."
    echo "Have you run 'terraform apply'?"
    exit 1
fi

SSH_USER="deploy"
SSH_CMD="ssh -o StrictHostKeyChecking=accept-new ${SSH_USER}@${SERVER_IP}"

echo "Server IP: ${SERVER_IP}"
echo "SSH user:  ${SSH_USER}"
[[ -n "$START_STAGE" ]] && echo "Resuming from stage: ${START_STAGE}"
echo ""

# ---------------------------------------------------------------------------
# 1b. Gather ALL secrets from 1Password up front (approve every prompt now,
#     then walk away — nothing else needs interaction)
# ---------------------------------------------------------------------------
echo "Fetching secrets from 1Password — approve all prompts now..."
ANTHROPIC_KEY="$(op read 'op://research-agent/ANTHROPIC_API_KEY/credential')"
GH_PAT="$(op read 'op://research-agent/OC_GITHUB_TOKEN/credential')"
TS_AUTHKEY="$(op read 'op://research-agent/TAILSCALE_AUTH_KEY/password')"
# RESEARCH_EMAIL_ADDRESS is an email item: address = username @ server
OPENALEX_MAILTO_SECRET="$(op read 'op://research-agent/RESEARCH_EMAIL_ADDRESS/username')@$(op read 'op://research-agent/RESEARCH_EMAIL_ADDRESS/server')"

if [[ -z "$ANTHROPIC_KEY" ]]; then echo "ERROR: Failed to fetch Anthropic API key from 1Password."; exit 1; fi
if [[ -z "$GH_PAT" ]];        then echo "ERROR: Failed to fetch GitHub PAT from 1Password.";        exit 1; fi
if [[ -z "$TS_AUTHKEY" ]];    then echo "ERROR: Failed to fetch Tailscale auth key from 1Password."; exit 1; fi
if [[ "$OPENALEX_MAILTO_SECRET" == "@" || "$OPENALEX_MAILTO_SECRET" == @* || "$OPENALEX_MAILTO_SECRET" == *@ ]]; then
    echo "ERROR: Failed to compose research email from 1Password (RESEARCH_EMAIL_ADDRESS username/server)."; exit 1
fi
echo "All secrets fetched — you can walk away now."
echo ""

# ---------------------------------------------------------------------------
# Stage functions (each maps to a name in ALL_STAGES)
# ---------------------------------------------------------------------------

# 2. Wait for cloud-init to finish (timeout after 5 minutes)
stage_cloud-init() {
    echo "Waiting for cloud-init to finish..."
    local TIMEOUT=300
    local ELAPSED=0
    local INTERVAL=10
    local STATUS

    while true; do
        STATUS="$(${SSH_CMD} "cloud-init status 2>/dev/null" 2>/dev/null || echo "pending")"

        if echo "$STATUS" | grep -q "done"; then
            echo "cloud-init finished successfully."
            break
        elif echo "$STATUS" | grep -q "error"; then
            echo "ERROR: cloud-init reported an error."
            echo "Check logs: ${SSH_CMD} 'sudo cat /var/log/cloud-init-output.log'"
            exit 1
        fi

        if (( ELAPSED >= TIMEOUT )); then
            echo "ERROR: cloud-init did not finish within ${TIMEOUT}s."
            echo "Check status: ${SSH_CMD} 'cloud-init status'"
            exit 1
        fi

        echo "  cloud-init still running... (${ELAPSED}s / ${TIMEOUT}s)"
        sleep "$INTERVAL"
        ELAPSED=$(( ELAPSED + INTERVAL ))
    done
    echo ""
}

# 3. Copy files to server
stage_copy() {
    echo "Copying systemd units..."
    ${SSH_CMD} "sudo mkdir -p /etc/research-agent"
    scp "${INFRA_DIR}/systemd/research-agent.service" "${SSH_USER}@${SERVER_IP}:/tmp/"
    scp "${INFRA_DIR}/systemd/research-agent.timer" "${SSH_USER}@${SERVER_IP}:/tmp/"
    ${SSH_CMD} "sudo mv /tmp/research-agent.service /tmp/research-agent.timer /etc/systemd/system/"

    echo "Copying scripts..."
    scp "${INFRA_DIR}/scripts/git-askpass.sh" "${SSH_USER}@${SERVER_IP}:/tmp/"
    ${SSH_CMD} "sudo mv /tmp/git-askpass.sh /opt/research-agent/scripts/ && \
                sudo chmod +x /opt/research-agent/scripts/git-askpass.sh && \
                sudo chown agent:agent /opt/research-agent/scripts/*"

    echo "Copying Dockerfiles..."
    scp "${INFRA_DIR}/docker/Dockerfile" "${SSH_USER}@${SERVER_IP}:/tmp/"
    scp "${INFRA_DIR}/docker/Dockerfile.web" "${SSH_USER}@${SERVER_IP}:/tmp/"
    ${SSH_CMD} "sudo mv /tmp/Dockerfile /tmp/Dockerfile.web /opt/research-agent/"
    echo ""
}

# 4. Build Docker images
stage_build() {
    echo "Building agent Docker image..."
    ${SSH_CMD} "sudo docker build -t research-agent:latest /opt/research-agent/"
    echo "Building web app Docker image..."
    ${SSH_CMD} "sudo docker build -t research-agent-web:latest -f /opt/research-agent/Dockerfile.web /opt/research-agent/"
    echo "Docker images built."
    echo ""
}

# 5. Place secrets (fetched from 1Password on the dev machine, encrypted on server)
stage_creds() {
    echo "$ANTHROPIC_KEY" | ${SSH_CMD} "sudo systemd-creds encrypt --name=anthropic-api-key - /etc/research-agent/anthropic-api-key && \
        sudo chmod 600 /etc/research-agent/anthropic-api-key && \
        sudo chown root:root /etc/research-agent/anthropic-api-key"
    echo "Anthropic API key encrypted and placed."
    echo ""

    echo "$GH_PAT" | ${SSH_CMD} "sudo systemd-creds encrypt --name=github-pat - /etc/research-agent/github-pat && \
        sudo chmod 600 /etc/research-agent/github-pat && \
        sudo chown root:root /etc/research-agent/github-pat"
    echo "GitHub PAT encrypted and placed."
    echo ""

    echo "$OPENALEX_MAILTO_SECRET" | ${SSH_CMD} "sudo systemd-creds encrypt --name=openalex-mailto - /etc/research-agent/openalex-mailto && \
        sudo chmod 600 /etc/research-agent/openalex-mailto && \
        sudo chown root:root /etc/research-agent/openalex-mailto"
    echo "OpenAlex mailto encrypted and placed."
    echo ""

    unset ANTHROPIC_KEY GH_PAT OPENALEX_MAILTO_SECRET
}

# 6. Enable and start the timer
stage_timer() {
    echo "Enabling systemd timer..."
    ${SSH_CMD} "sudo systemctl daemon-reload && \
                sudo systemctl enable --now research-agent.timer"
    echo ""
}

# 7. Deploy annotation web app
stage_web() {
    echo "Deploying annotation web app..."

    scp "${INFRA_DIR}/systemd/web-app.service" "${SSH_USER}@${SERVER_IP}:/tmp/"
    scp "${INFRA_DIR}/scripts/web-start.sh" "${SSH_USER}@${SERVER_IP}:/tmp/"
    ${SSH_CMD} "sudo mv /tmp/web-app.service /etc/systemd/system/ && \
                sudo mv /tmp/web-start.sh /opt/research-agent/scripts/ && \
                sudo chmod +x /opt/research-agent/scripts/web-start.sh && \
                sudo chown agent:agent /opt/research-agent/scripts/web-start.sh && \
                sudo systemctl daemon-reload && \
                sudo systemctl enable --now web-app"
    echo "Web app enabled."
    echo ""
}

# 8+9. Ensure Tailscale is installed, authenticated, and proxying to Flask
stage_tailscale() {
    echo "Checking Tailscale installation..."
    if ! ${SSH_CMD} "command -v tailscale >/dev/null 2>&1"; then
        echo "Tailscale not found — installing..."
        ${SSH_CMD} "curl -fsSL https://tailscale.com/install.sh | sudo sh"
        echo "Tailscale installed."
    else
        echo "Tailscale already installed."
    fi
    echo ""

    # Always re-authenticate. TS_AUTHKEY was fetched up front.
    echo "Authenticating Tailscale..."
    printf '%s' "$TS_AUTHKEY" | ${SSH_CMD} "sudo tailscale up --authkey=file:/dev/stdin"
    echo "Tailscale authenticated."
    unset TS_AUTHKEY

    echo "Configuring Tailscale serve..."
    ${SSH_CMD} "sudo tailscale serve --bg http://localhost:5001"

    local WEB_URL
    WEB_URL="$(${SSH_CMD} "tailscale status --json 2>/dev/null | jq -r '.Self.DNSName // empty'" 2>/dev/null || true)"
    echo "Web app URL: https://${WEB_URL}"
    echo ""
}

# 10. Verify (always runs at the end)
stage_verify() {
    echo "=== Timer status ==="
    ${SSH_CMD} "systemctl status research-agent.timer --no-pager" || true
    echo ""
    echo "=== Web app status ==="
    ${SSH_CMD} "systemctl status web-app --no-pager" || true
    echo ""
    echo "=== Deployment complete ==="
    echo ""
    echo "Useful commands:"
    echo "  ssh ${SSH_USER}@${SERVER_IP} 'systemctl status research-agent.timer'     # check timer"
    echo "  ssh ${SSH_USER}@${SERVER_IP} 'sudo systemctl start research-agent'       # manual run"
    echo "  ssh ${SSH_USER}@${SERVER_IP} 'journalctl -u research-agent -f'           # watch logs"
    echo "  ssh ${SSH_USER}@${SERVER_IP} 'systemctl status web-app'                  # check web app"
    echo "  ssh ${SSH_USER}@${SERVER_IP} 'journalctl -u web-app -f'                  # web app logs"
    echo "  ssh ${SSH_USER}@${SERVER_IP} 'tailscale serve status'                    # check HTTPS proxy"
}

# ---------------------------------------------------------------------------
# Drive the stages (each is skipped until START_STAGE is reached)
# ---------------------------------------------------------------------------
for stage in "${ALL_STAGES[@]}"; do
    if should_run "$stage"; then
        "stage_${stage}"
    fi
done

stage_verify
