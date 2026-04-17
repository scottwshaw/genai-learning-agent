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
scp "${INFRA_DIR}/scripts/run-agent.sh" "${SSH_USER}@${SERVER_IP}:/tmp/"
scp "${INFRA_DIR}/scripts/git-askpass.sh" "${SSH_USER}@${SERVER_IP}:/tmp/"
${SSH_CMD} "sudo mv /tmp/run-agent.sh /tmp/git-askpass.sh /opt/research-agent/scripts/ && \
            sudo chmod +x /opt/research-agent/scripts/run-agent.sh /opt/research-agent/scripts/git-askpass.sh && \
            sudo chown agent:agent /opt/research-agent/scripts/*"

echo "Copying Dockerfile..."
scp "${INFRA_DIR}/docker/Dockerfile" "${SSH_USER}@${SERVER_IP}:/tmp/"
${SSH_CMD} "sudo mv /tmp/Dockerfile /opt/research-agent/"

echo ""

# ---------------------------------------------------------------------------
# 4. Build Docker image
# ---------------------------------------------------------------------------
echo "Building Docker image on server (this may take a minute)..."
${SSH_CMD} "sudo docker build -t research-agent:latest /opt/research-agent/"
echo "Docker image built."
echo ""

# ---------------------------------------------------------------------------
# 5. Place 1Password service account token
# ---------------------------------------------------------------------------
echo "Fetching 1Password service account token..."
OP_TOKEN="$(op item get 'Service Account Auth Token: research-agent' --vault research-agent --fields credential --reveal)"

if [[ -z "$OP_TOKEN" ]]; then
    echo "ERROR: Failed to fetch SA token from 1Password."
    exit 1
fi

# Encrypt the token via systemd-creds on the server.
# The plaintext is piped through stdin — never appears in a command line or on disk.
echo "$OP_TOKEN" | ${SSH_CMD} "sudo systemd-creds encrypt --name=op-token - /etc/research-agent/op-token && \
    sudo chmod 600 /etc/research-agent/op-token && \
    sudo chown root:root /etc/research-agent/op-token"
echo "Token encrypted and placed."
echo ""

# ---------------------------------------------------------------------------
# 6. Enable and start the timer
# ---------------------------------------------------------------------------
echo "Enabling systemd timer..."
${SSH_CMD} "sudo systemctl daemon-reload && \
            sudo systemctl enable --now research-agent.timer"
echo ""

# ---------------------------------------------------------------------------
# 7. Verify
# ---------------------------------------------------------------------------
echo "=== Timer status ==="
${SSH_CMD} "systemctl status research-agent.timer --no-pager" || true
echo ""
echo "=== Deployment complete ==="
echo ""
echo "Useful commands:"
echo "  ssh ${SSH_USER}@${SERVER_IP} 'systemctl status research-agent.timer'     # check timer"
echo "  ssh ${SSH_USER}@${SERVER_IP} 'sudo systemctl start research-agent'       # manual run"
echo "  ssh ${SSH_USER}@${SERVER_IP} 'journalctl -u research-agent -f'           # watch logs"
echo "  ssh ${SSH_USER}@${SERVER_IP} 'cat /opt/research-agent/repo/agent.log'    # app log"
