#!/usr/bin/env bash
# =============================================================================
# deploy.sh — One-shot server setup after terraform apply
# =============================================================================
# Waits for cloud-init, copies project files, builds the Docker image,
# places the 1Password service account token, and enables the systemd timer.
#
# Run from: infra/scripts/
# Prerequisites: terraform apply has completed, server is reachable via SSH.
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INFRA_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
TERRAFORM_DIR="${INFRA_DIR}/terraform"

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
echo ""

# ---------------------------------------------------------------------------
# 2. Wait for cloud-init to finish (timeout after 5 minutes)
# ---------------------------------------------------------------------------
echo "Waiting for cloud-init to finish..."
TIMEOUT=300
ELAPSED=0
INTERVAL=10

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

# ---------------------------------------------------------------------------
# 3. Copy files to server
# ---------------------------------------------------------------------------
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

# ---------------------------------------------------------------------------
# 4. Build Docker images
# ---------------------------------------------------------------------------
echo "Building agent Docker image..."
${SSH_CMD} "sudo docker build -t research-agent:latest /opt/research-agent/"
echo "Building web app Docker image..."
${SSH_CMD} "sudo docker build -t research-agent-web:latest -f /opt/research-agent/Dockerfile.web /opt/research-agent/"
echo "Docker images built."
echo ""

# ---------------------------------------------------------------------------
# 5. Place secrets (fetched from 1Password on the dev machine, encrypted on server)
# ---------------------------------------------------------------------------
echo "Fetching Anthropic API key..."
ANTHROPIC_KEY="$(op read 'op://research-agent/ANTHROPIC_API_KEY/credential')"

if [[ -z "$ANTHROPIC_KEY" ]]; then
    echo "ERROR: Failed to fetch Anthropic API key from 1Password."
    exit 1
fi

echo "$ANTHROPIC_KEY" | ${SSH_CMD} "sudo systemd-creds encrypt --name=anthropic-api-key - /etc/research-agent/anthropic-api-key && \
    sudo chmod 600 /etc/research-agent/anthropic-api-key && \
    sudo chown root:root /etc/research-agent/anthropic-api-key"
echo "Anthropic API key encrypted and placed."
echo ""

echo "Fetching GitHub PAT..."
GH_PAT="$(op read 'op://research-agent/OC_GITHUB_TOKEN/credential')"

if [[ -z "$GH_PAT" ]]; then
    echo "ERROR: Failed to fetch GitHub PAT from 1Password."
    exit 1
fi

echo "$GH_PAT" | ${SSH_CMD} "sudo systemd-creds encrypt --name=github-pat - /etc/research-agent/github-pat && \
    sudo chmod 600 /etc/research-agent/github-pat && \
    sudo chown root:root /etc/research-agent/github-pat"
echo "GitHub PAT encrypted and placed."
echo ""

# ---------------------------------------------------------------------------
# 6. Enable and start the timer
# ---------------------------------------------------------------------------
echo "Enabling systemd timer..."
${SSH_CMD} "sudo systemctl daemon-reload && \
            sudo systemctl enable --now research-agent.timer"
echo ""

# ---------------------------------------------------------------------------
# 7. Deploy annotation web app
# ---------------------------------------------------------------------------
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

# ---------------------------------------------------------------------------
# 8. Ensure Tailscale is installed (fallback if cloud-init missed it)
# ---------------------------------------------------------------------------
echo "Checking Tailscale installation..."
if ! ${SSH_CMD} "command -v tailscale >/dev/null 2>&1"; then
    echo "Tailscale not found — installing..."
    ${SSH_CMD} "curl -fsSL https://tailscale.com/install.sh | sudo sh"
    echo "Tailscale installed."
else
    echo "Tailscale already installed."
fi
echo ""

# ---------------------------------------------------------------------------
# 9. Authenticate Tailscale and configure HTTPS proxy → Flask on port 5001
# ---------------------------------------------------------------------------
echo "Authenticating Tailscale..."
TS_AUTHKEY="$(op item get tailscale --vault Private --fields password --reveal)"
if [[ -z "$TS_AUTHKEY" ]]; then
    echo "ERROR: Failed to fetch Tailscale auth key from 1Password."
    exit 1
fi
${SSH_CMD} "sudo tailscale up --authkey=${TS_AUTHKEY}"
unset TS_AUTHKEY
echo "Tailscale authenticated."

echo "Configuring Tailscale serve..."
${SSH_CMD} "sudo tailscale serve --bg https / http://localhost:5001"

WEB_URL="$(${SSH_CMD} "tailscale status --json 2>/dev/null | jq -r '.Self.DNSName // empty'" 2>/dev/null || true)"
echo "Web app URL: https://${WEB_URL}"
echo ""

# ---------------------------------------------------------------------------
# 10. Verify
# ---------------------------------------------------------------------------
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
