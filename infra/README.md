# Infrastructure — Research Agent on Hetzner

Runs a daily GenAI research agent plus a Flask annotation web app on a Hetzner CX23 VPS (Ubuntu 24.04). Both services are Docker containers managed by systemd. The annotation web app is accessible from your phone via Tailscale — no open ports, no domain required.

## Prerequisites

- [Terraform](https://developer.hashicorp.com/terraform/install) >= 1.0
- [1Password CLI](https://developer.1password.com/docs/cli/get-started/) (`op`) installed and signed in
- [Tailscale](https://tailscale.com/download) installed on any device you want to reach the web app from
- A Hetzner Cloud account with an API token in 1Password

## 1Password Setup

### Hetzner API token (Terraform only, local use)

| Vault | Item | Field |
|-------|------|-------|
| `Private` | `HETZNER_API_KEY` | `credential` |
| `Private` | `Hetzner From Personal Laptop` | `public key` |

### Application secrets (vault: `research-agent`)

| Item | Field | Value |
|------|-------|-------|
| `ANTHROPIC_API_KEY` | `credential` | Anthropic API key |
| `OC_GITHUB_TOKEN` | `credential` | GitHub PAT with `repo` scope |
| `TAILSCALE_AUTH_KEY` | `password` | Tailscale auth key (reusable, one-off) |

These three secrets are fetched on your Mac at deploy time and never touch the server in plaintext. See "How secrets work" below.

## Provision the Server

```bash
export HCLOUD_TOKEN=$(op item get 'HETZNER_API_KEY' --vault Private --fields credential --reveal)
export TF_VAR_ssh_public_key=$(op item get 'Hetzner From Personal Laptop' --vault Private --fields 'public key' --reveal)
cd infra/terraform
terraform init
terraform apply
```

Terraform creates a `cx23` server, a firewall (SSH inbound only; no 80/443), and a cloud-init script that installs Docker, fail2ban, the 1Password CLI, the GitHub CLI, and clones the repo into `/opt/research-agent/repo`.

## Deploy

```bash
cd infra/scripts
./deploy.sh
```

All three biometric prompts for 1Password fire up front. After you approve them the rest is unattended.

### Stages (in order)

| Stage | What it does |
|-------|-------------|
| `cloud-init` | Polls until cloud-init finishes (up to 5 min) |
| `copy` | SCPs systemd units, Dockerfiles, and `git-askpass.sh` to the server |
| `build` | Builds `research-agent:latest` and `research-agent-web:latest` on the server |
| `creds` | Pipes each secret over SSH into `systemd-creds encrypt`; places encrypted blobs under `/etc/research-agent/`; unsets variables from memory |
| `timer` | `daemon-reload` + `enable --now research-agent.timer` |
| `web` | Copies `web-app.service` and `web-start.sh`, then `enable --now web-app` |
| `tailscale` | Installs Tailscale if absent, authenticates with the auth key, configures `tailscale serve` to proxy HTTPS to `localhost:5001` |

### Resuming a failed deploy

If a stage fails you can skip everything before it:

```bash
./deploy.sh --from creds      # re-encrypt secrets only
./deploy.sh --from tailscale  # re-run just the Tailscale stage
./deploy.sh --help            # list all stages
```

Secrets are always fetched from 1Password first regardless of `--from`, then execution jumps to the named stage.

## How Secrets Work

1. `deploy.sh` calls `op read 'op://research-agent/<ITEM>/<field>'` on your Mac — secrets exist only in shell variables.
2. Each secret is piped over SSH into `sudo systemd-creds encrypt --name=<name> - /etc/research-agent/<name>`.
3. The resulting blobs are machine-bound (encrypted with a key derived from the host's TPM/machine-id). Root:root 600.
4. The systemd units declare `LoadCredentialEncrypted=<name>:/etc/research-agent/<name>`. At runtime systemd decrypts and exposes each credential as a file in `$CREDENTIALS_DIRECTORY`.
5. `research-agent.service` gets `anthropic-api-key` and `github-pat`. `web-app.service` gets `github-pat`.

**If you restore to a new host** the encrypted blobs from the old machine are useless. Run `./deploy.sh --from creds` after rebuilding to re-encrypt against the new machine.

## Services

### `research-agent.timer` + `research-agent.service`

- Timer fires daily at 07:00 UTC, `Persistent=true` (catches up if the server was down), up to 5-minute random jitter.
- Service is `Type=oneshot`, runs as the `agent` user.
- Executes `/opt/research-agent/repo/research-agent/run-agent.sh` inside the `research-agent:latest` Docker container.
- Timeout: 30 minutes (research + critic + revision + push can take a while).

### `web-app.service`

- Long-running Flask app (`Type=simple`, `Restart=on-failure`).
- `web-start.sh` is the entrypoint: it reads `github-pat` from `$CREDENTIALS_DIRECTORY`, clones the repo into `/opt/research-agent/web-repo` on first start, then runs the `research-agent-web:latest` container on port 5001.
- Credentials are passed into the container via a bind-mounted file (`/run/secrets/github-pat`), never on the Docker command line.

## Annotation Web App

- Separate git clone at `/opt/research-agent/web-repo` — isolated from the research agent's clone so concurrent pushes don't conflict.
- After annotating, the web app commits to the `annotations` branch and opens a PR. You merge it manually on GitHub.
- Access via Tailscale: install Tailscale on your phone, sign in with your Apple ID, browse to the `https://research-agent.<tailnet>.ts.net` URL printed at the end of deploy.

## Useful SSH Commands

```bash
SERVER=$(cd infra/terraform && terraform output -raw server_ip)

# Check timer
ssh deploy@$SERVER 'systemctl status research-agent.timer'

# Manual run
ssh deploy@$SERVER 'sudo systemctl start research-agent'

# Watch research agent logs
ssh deploy@$SERVER 'journalctl -u research-agent -f'

# Check web app
ssh deploy@$SERVER 'systemctl status web-app'

# Watch web app logs
ssh deploy@$SERVER 'journalctl -u web-app -f'

# Check Tailscale proxy
ssh deploy@$SERVER 'tailscale serve status'
```

## File Layout on Server

```
/opt/research-agent/
  repo/                         # Git clone (bind-mounted into agent container)
    research-agent/
      run-agent.sh              # Entry point called by research-agent.service
    briefs/                     # Generated research briefs
    .topic-index                # Round-robin topic state
  web-repo/                     # Separate git clone for the web app
    web/app.py                  # Flask annotation app
    briefs/                     # Read-only view of briefs (same content, separate clone)
  scripts/
    web-start.sh                # Wrapper called by web-app.service
    git-askpass.sh              # Git credential helper (reads from /run/secrets/github-pat)
  Dockerfile                    # Agent image (python:3.12-slim + anthropic + jq + git)
  Dockerfile.web                # Web image (python:3.12-slim + flask + gh CLI)

/etc/research-agent/
  anthropic-api-key             # systemd-creds blob (machine-bound, root:root 0600)
  github-pat                    # systemd-creds blob (machine-bound, root:root 0600)

/etc/systemd/system/
  research-agent.service        # Oneshot service (runs agent container)
  research-agent.timer          # Daily 07:00 UTC, Persistent=true
  web-app.service               # Persistent Flask annotation app
```

## Credential Rotation

### Rotate the Anthropic key or GitHub PAT

1. Update the value in 1Password (`research-agent` vault).
2. Re-run the creds stage — this fetches the new value and re-encrypts it on the server:
   ```bash
   cd infra/scripts && ./deploy.sh --from creds
   ```
3. Restart the affected service:
   ```bash
   ssh deploy@$SERVER 'sudo systemctl restart research-agent.timer'
   ssh deploy@$SERVER 'sudo systemctl restart web-app'
   ```

### Rotate the Tailscale auth key

1. Generate a new key at https://login.tailscale.com/admin/settings/keys.
2. Update `TAILSCALE_AUTH_KEY` in the `research-agent` 1Password vault.
3. Re-run the Tailscale stage:
   ```bash
   cd infra/scripts && ./deploy.sh --from tailscale
   ```

## Disaster Recovery

Code and briefs live in GitHub — a VPS loss loses nothing except the encrypted credential blobs (which are machine-bound and useless on a new host anyway).

To rebuild from scratch:

```bash
cd infra/terraform && terraform apply   # provision new VPS
cd ../scripts && ./deploy.sh            # full deploy (re-clones repo, re-encrypts secrets)
```

## Security Notes

- **SSH**: key-only (`PasswordAuthentication no`), no root login, fail2ban aggressive mode (3 retries, 1h ban), Hetzner firewall (SSH inbound only; ports 80/443 closed — Tailscale handles HTTPS).
- **Web app**: reachable only via Tailscale; Tailscale membership (Apple ID SSO) is the auth gate.
- **Users**: `deploy` (sudo, your SSH user), `agent` (system user, runs services, no sudo).
- **Secrets**: encrypted at rest via `systemd-creds` (machine-specific key). Exposed to services only via `$CREDENTIALS_DIRECTORY`. Never written to disk in plaintext, never passed on command lines.
- **Docker**: containers run as the `agent` uid, `--rm` flag, no privileged mode.
- **Updates**: `unattended-upgrades` enabled for automatic security patches.

## Destroy

```bash
export HCLOUD_TOKEN=$(op item get 'HETZNER_API_KEY' --vault Private --fields credential --reveal)
cd infra/terraform
terraform destroy
```
