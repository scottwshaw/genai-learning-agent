# Simplify Agent Runner

Collapse the three-script server execution chain into two scripts with clear responsibilities, eliminate runtime 1Password calls from the server, and pass secrets safely via systemd-creds.

## Problem

The current server flow uses three scripts: `infra/scripts/run-agent.sh` (bootstrap, fetches secrets via `op read`) → `run-remote.sh` (topic resolution, branch, docker run, push, PR). The `op read` calls require the 1Password CLI on the server, which violates the design principle that secrets are baked in at deploy time. The split between the three scripts is unclear and hard to test locally.

## Design

### Two scripts, clear responsibilities

**`research.sh`** (unchanged) — runs the research pipeline directly. Used for day-to-day local development and testing. No container, no git flow. Supports `--no-commit`, `--topic`, and all existing flags.

**`run-agent.sh`** (new, replaces both `infra/scripts/run-agent.sh` and `run-remote.sh`) — runs `research.sh` inside a Docker container with the full git flow around it. Used by systemd on the server and locally for integration testing.

### run-agent.sh behavior

**Credential resolution** (in order):
1. If `ANTHROPIC_API_KEY` is already in the environment → use it
2. Else if `CREDENTIALS_DIRECTORY` is set → read from `$CREDENTIALS_DIRECTORY/anthropic-api-key`
3. Else → error

Same pattern for `GITHUB_PAT` (from env, then `$CREDENTIALS_DIRECTORY/github-pat`), except `GITHUB_PAT` is optional. When absent, `--no-commit` is implied — brief goes to `eval-runs/`, no git operations.

**When `GITHUB_PAT` is present** (server mode):
1. `git pull --ff-only`
2. Create branch `research/<date>-<slug>`
3. `docker run` with `ANTHROPIC_API_KEY` and `--topic-slug` — container runs `research.sh`
4. Commit the brief
5. Push branch, create PR via `gh`
6. Clean up — return to main

**When `GITHUB_PAT` is absent** (local/test mode):
1. No git pull, no branch
2. `docker run` with `ANTHROPIC_API_KEY` and `--no-commit --topic-slug` — container runs `research.sh`, brief goes to `eval-runs/`
3. No push, no PR

Explicit `--no-commit` flag still supported and overrides even when `GITHUB_PAT` is present (for dry runs on the server).

**Local usage:**
```
ANTHROPIC_API_KEY=sk-ant-... ./run-agent.sh --topic safety-assurance-and-governance
```

### Secret safety

Secrets never touch disk on the server. The flow is:
1. `deploy.sh` fetches secrets from 1Password on the dev machine (where `op` CLI is installed)
2. Secrets are piped via SSH to `systemd-creds encrypt` on the server — encrypted at rest with a machine-specific key
3. At runtime, systemd decrypts them into `$CREDENTIALS_DIRECTORY` (tmpfs, memory-only)
4. `run-agent.sh` reads them from there, passes to Docker via `-e` env vars
5. Container process uses them, then is destroyed

No 1Password CLI on the server. No secrets in command lines, environment files, or persistent storage.

### Container security

The Docker container runs with:
- `--read-only` filesystem
- `--tmpfs /tmp` for temporary files
- `--user $(id -u):$(id -g)` to avoid root
- Only `ANTHROPIC_API_KEY` passed in (not `GITHUB_PAT`)
- Repo mounted read-only at `/workspace:ro`, with `briefs/` and `eval-runs/` overlaid read-write for output
- Topic resolution happens on the host; `--topic-slug` is passed to the container, so it never writes `.topic-index`

### Files changed

- **Delete:** `infra/scripts/run-agent.sh` — replaced by repo-root `run-agent.sh`
- **Delete:** `run-remote.sh` — merged into `run-agent.sh`
- **Create:** `run-agent.sh` (repo root) — single containerised runner
- **Modify:** `infra/systemd/research-agent.service` — `ExecStart` points to `/opt/research-agent/repo/run-agent.sh`, credentials load `anthropic-api-key` and `github-pat` instead of `op-token`
- **Modify:** `infra/scripts/deploy.sh` — encrypt actual secrets (`anthropic-api-key`, `github-pat`) instead of 1Password service account token; no longer copies `run-agent.sh` to `/opt/research-agent/scripts/`
- **Modify:** `common.sh` — no changes expected, but verify compatibility

## Scope

In scope:
- New `run-agent.sh` with credential resolution and implicit `--no-commit`
- Updated systemd service and deploy script
- Remove old scripts

Out of scope:
- Changes to `research.sh`
- Changes to the Docker image
- Changes to the web app container or its deployment
