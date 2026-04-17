# Infrastructure — Research Agent on Hetzner

Deploys the research agent to a Hetzner CX22 VPS. Runs daily via systemd timer, containerised with Docker, secrets fetched from 1Password at runtime.

## Prerequisites

- [Terraform](https://developer.hashicorp.com/terraform/install) >= 1.0
- [1Password CLI](https://developer.1password.com/docs/cli/get-started/) (`op`) installed locally
- A Hetzner Cloud account with an API token stored in 1Password
- A 1Password service account (see below)
- An SSH key pair (defaults to `~/.ssh/id_ed25519`)

## 1Password Setup

### Hetzner API Token (local use)

Stored in your personal vault. Used only when running Terraform from your Mac.

- Item: `HETZNER_API_KEY` in `Private` vault — `credential` field

### Service Account Vault

Create a vault called `ResearchAgent` with two items:

| Item name | Field | Value |
|-----------|-------|-------|
| `anthropic-api-key` | `credential` | Your Anthropic API key |
| `github-pat` | `credential` | GitHub PAT with `repo` scope |

Then create a **Service Account** in your 1Password account:

1. Go to 1password.com → Settings → Service Accounts
2. Create a new service account
3. Grant it **read-only** access to the `ResearchAgent` vault only
4. Copy the service account token — you'll need it during deploy

## Deploy

### 1. Provision the server

```bash
export HCLOUD_TOKEN=$(op item get 'HETZNER_API_KEY' --vault Private --fields credential --reveal)
export TF_VAR_ssh_public_key=$(op item get 'Hetzner From Personal Laptop' --vault Private --fields 'public key' --reveal)
cd infra/terraform
terraform init
terraform apply
```

### 2. Deploy application files

```bash
cd infra/scripts
./deploy.sh
```

This will:
- Wait for cloud-init to finish (timeout: 5 min)
- Copy systemd units, scripts, and Dockerfile to the server
- Build the Docker image
- Prompt you for the 1Password service account token
- Enable the systemd timer

### 3. Verify

```bash
SERVER=$(cd ../terraform && terraform output -raw server_ip)
ssh deploy@$SERVER systemctl status research-agent.timer
```

### 4. Test run

```bash
ssh deploy@$SERVER sudo systemctl start research-agent.service
ssh deploy@$SERVER journalctl -u research-agent -f
```

## Day-to-Day Operations

### Check timer status
```bash
ssh deploy@$SERVER systemctl status research-agent.timer
```

### View logs
```bash
# Orchestration logs (systemd/wrapper)
ssh deploy@$SERVER journalctl -u research-agent --since today

# Application logs (research.sh / API calls)
ssh deploy@$SERVER cat /opt/research-agent/repo/agent.log
```

### Manual run
```bash
ssh deploy@$SERVER sudo systemctl start research-agent.service
```

### Update prompts or scripts
Push changes to the GitHub repo. The wrapper runs `git pull` before each run, so changes are picked up automatically.

### Rebuild Docker image
Only needed if Python dependencies change:
```bash
ssh deploy@$SERVER sudo docker build -t research-agent:latest /opt/research-agent/
```

### Rotate the 1Password service account token
```bash
# 1. Create a new service account token in 1Password web UI
# 2. Re-encrypt it on the server:
ssh deploy@$SERVER
echo "NEW_TOKEN_HERE" | sudo systemd-creds encrypt --name=op-token - /etc/research-agent/op-token
# 3. Revoke the old token in 1Password web UI
```

### Destroy
```bash
export HCLOUD_TOKEN=$(op item get 'HETZNER_API_KEY' --vault Private --fields credential --reveal)
cd infra/terraform
terraform destroy
```

## Security

- **SSH**: key-only, no root login, fail2ban, Hetzner firewall (SSH inbound only)
- **Users**: `deploy` (sudo, your SSH user), `agent` (unprivileged, runs the service)
- **Secrets**: 1Password SA token is the only credential on disk, encrypted at rest via `systemd-creds` (machine-specific key). Exposed to the service via `LoadCredentialEncrypted`. API key and PAT exist only in memory at runtime.
- **Docker**: `--rm`, `--read-only`, `--tmpfs /tmp`, no privileged mode
- **Updates**: unattended-upgrades enabled for automatic security patches

## File Layout on Server

```
/opt/research-agent/
  repo/                    # Git clone (bind-mounted into container)
    briefs/                # Generated research briefs
    agent.log              # Application log
    .topic-index           # Round-robin state
  scripts/
    run-agent.sh           # Wrapper script (systemd calls this)
    git-askpass.sh         # Git credential helper (echoes $GITHUB_PAT)
  Dockerfile               # Built locally on the server

/etc/research-agent/
  op-token                 # 1Password SA token (encrypted via systemd-creds, root:root 0600)

/etc/systemd/system/
  research-agent.service   # Oneshot service
  research-agent.timer     # Daily at 07:00 UTC
```
