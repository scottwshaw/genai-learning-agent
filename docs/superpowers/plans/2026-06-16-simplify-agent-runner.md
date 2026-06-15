# Simplify Agent Runner — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the three-script server execution chain with a single `run-agent.sh` that works both locally and on the server, eliminating runtime 1Password calls.

**Architecture:** New `run-agent.sh` at repo root handles credential resolution (env vars first, then systemd-creds), runs `research.sh` in a Docker container with a read-only repo mount, and handles git branch/commit/push/PR on the host. Old `infra/scripts/run-agent.sh` and `run-remote.sh` are deleted. Systemd service and deploy script updated to match.

**Tech Stack:** Bash, Docker, systemd, systemd-creds

**Spec:** `docs/superpowers/specs/2026-06-16-simplify-agent-runner-design.md`

---

**Important context for all tasks:**

- The repo root is `/Users/scottshaw/Documents/Development/ResearchAgent/genai-learning-agent`
- `common.sh` provides `REPO_ROOT`, `resolve_topic`, `TOPIC_SLUG`, `TOPIC_LABEL`, etc.
- `research.sh --topic-slug SLUG --no-commit` runs research without git operations, writes to `eval-runs/`
- `research.sh --topic-slug SLUG` (without `--no-commit`) writes to `briefs/<date>-<slug>/brief.md`, commits, and advances `.topic-index`
- `research.sh --output-file FILE --topic-slug SLUG` writes to the specified file, skips git commit and index advancement
- The container must never commit or advance `.topic-index` (read-only mount). In server mode, use `--output-file` to direct output to `briefs/`. In local mode, use `--no-commit` (output goes to `eval-runs/`).
- `git-askpass.sh` echoes `$GITHUB_PAT` — used for git push auth. Lives at `infra/scripts/git-askpass.sh` and is already deployed to `/opt/research-agent/scripts/` on the server.
- These are shell scripts and systemd configs — TDD does not apply. Test by reading the scripts, checking syntax with `bash -n`, and verifying the deploy flow makes sense.

**File map:**

- Create: `run-agent.sh` (repo root) — single containerised runner, replaces both old scripts
- Delete: `run-remote.sh` — merged into new `run-agent.sh`
- Delete: `infra/scripts/run-agent.sh` — no longer needed
- Modify: `infra/systemd/research-agent.service` — new ExecStart, new credentials
- Modify: `infra/scripts/deploy.sh` — encrypt actual secrets, stop copying run-agent.sh

---

### Task 1: Create new run-agent.sh

**Files:**
- Create: `run-agent.sh` (repo root)
- Delete: `run-remote.sh`

- [ ] **Step 1: Create run-agent.sh**

Create `run-agent.sh` at the repo root with the following content:

```bash
#!/usr/bin/env bash
# =============================================================================
# run-agent.sh — Run research agent in Docker
# =============================================================================
# Runs research.sh inside a Docker container. Works both locally (credentials
# from environment) and on the server (credentials from systemd-creds).
#
# Local:  ANTHROPIC_API_KEY=sk-... ./run-agent.sh --topic safety-assurance-and-governance
# Server: systemd sets CREDENTIALS_DIRECTORY; GITHUB_PAT triggers full git flow
# =============================================================================

set -euo pipefail
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/common.sh"

LOG_PREFIX="[run-agent]"
log() { echo "${LOG_PREFIX} $(date '+%Y-%m-%d %H:%M:%S') $*"; }

# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------
NO_COMMIT=false
TOPIC_SLUG_OVERRIDE=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --no-commit)
            NO_COMMIT=true
            shift
            ;;
        --topic)
            TOPIC_SLUG_OVERRIDE="${2:?--topic requires a number or slug}"
            shift 2
            ;;
        *)
            echo "Usage: $0 [--topic N|SLUG] [--no-commit]" >&2
            exit 1
            ;;
    esac
done

# ---------------------------------------------------------------------------
# 1. Resolve credentials (env vars first, then systemd-creds)
# ---------------------------------------------------------------------------
if [[ -z "${ANTHROPIC_API_KEY:-}" ]]; then
    if [[ -n "${CREDENTIALS_DIRECTORY:-}" ]] && [[ -f "${CREDENTIALS_DIRECTORY}/anthropic-api-key" ]]; then
        ANTHROPIC_API_KEY="$(cat "${CREDENTIALS_DIRECTORY}/anthropic-api-key")"
    else
        log "ERROR: ANTHROPIC_API_KEY not set and no systemd credentials available"
        exit 1
    fi
fi

if [[ -z "${GITHUB_PAT:-}" ]]; then
    if [[ -n "${CREDENTIALS_DIRECTORY:-}" ]] && [[ -f "${CREDENTIALS_DIRECTORY}/github-pat" ]]; then
        GITHUB_PAT="$(cat "${CREDENTIALS_DIRECTORY}/github-pat")"
    fi
fi

export ANTHROPIC_API_KEY
# GITHUB_PAT intentionally not exported — only used by this script for git ops

# If no GITHUB_PAT, force --no-commit
if [[ -z "${GITHUB_PAT:-}" ]]; then
    NO_COMMIT=true
fi

# ---------------------------------------------------------------------------
# 2. Server mode: pull latest code and create branch
# ---------------------------------------------------------------------------
DATE="$(date +%Y-%m-%d)"

if [[ "$NO_COMMIT" == false ]]; then
    export GIT_ASKPASS="${REPO_ROOT}/infra/scripts/git-askpass.sh"
    export GH_TOKEN="$GITHUB_PAT"
    export GITHUB_PAT

    cd "$REPO_ROOT"
    git checkout main 2>/dev/null || true

    log "Pulling latest changes..."
    git pull --ff-only

    resolve_topic "$TOPIC_SLUG_OVERRIDE"
    BRANCH="research/${DATE}-${TOPIC_SLUG}"

    git branch -D "$BRANCH" 2>/dev/null || true
    log "Creating branch: ${BRANCH}"
    git checkout -b "$BRANCH"
else
    resolve_topic "$TOPIC_SLUG_OVERRIDE"
fi

# ---------------------------------------------------------------------------
# 3. Run the containerised research agent
# ---------------------------------------------------------------------------
log "Starting research container..."

mkdir -p "${REPO_ROOT}/briefs" "${REPO_ROOT}/eval-runs"

CONTAINER_ARGS=(--topic-slug "$TOPIC_SLUG")
if [[ "$NO_COMMIT" == false ]]; then
    # Server mode: direct output to briefs/ via --output-file (skips git commit
    # and index advancement inside the container — the host handles both)
    BRIEF_DIR="${REPO_ROOT}/briefs/${DATE}-${TOPIC_SLUG}"
    mkdir -p "$BRIEF_DIR"
    BRIEF_FILE="${BRIEF_DIR}/brief.md"
    CONTAINER_ARGS+=(--output-file "/workspace/briefs/${DATE}-${TOPIC_SLUG}/brief.md")
else
    # Local mode: --no-commit sends output to eval-runs/
    CONTAINER_ARGS+=(--no-commit)
fi

docker run --rm \
    --read-only \
    --tmpfs /tmp \
    --user "$(id -u):$(id -g)" \
    -e ANTHROPIC_API_KEY \
    -e ENABLE_CRITIC=1 \
    -v "${REPO_ROOT}:/workspace:ro" \
    -v "${REPO_ROOT}/briefs:/workspace/briefs" \
    -v "${REPO_ROOT}/eval-runs:/workspace/eval-runs" \
    research-agent:latest \
    ./research.sh "${CONTAINER_ARGS[@]}"

log "Research container finished"

# ---------------------------------------------------------------------------
# 4. Server mode: commit, push, create PR, clean up
# ---------------------------------------------------------------------------
if [[ "$NO_COMMIT" == false ]]; then
    if [[ ! -f "$BRIEF_FILE" ]]; then
        log "ERROR: Expected brief not found at $BRIEF_FILE"
        git checkout main
        exit 1
    fi

    cd "$REPO_ROOT"

    git add "$BRIEF_FILE"

    if git diff --cached --quiet; then
        log "Nothing new to commit"
    else
        git commit -m "research(${DATE}): ${TOPIC_LABEL}

Daily brief on '${TOPIC_LABEL}' (area $((TOPIC_IDX + 1))/${TOPIC_COUNT}).
Generated by learning-agent on $(hostname)."
        log "Committed: research(${DATE}): ${TOPIC_LABEL}"
    fi

    # Advance topic index
    echo "$TOPIC_NEXT_IDX" > "$STATE_FILE"

    log "Pushing branch..."
    git push -u origin "$BRANCH"

    log "Creating pull request..."
    gh pr create \
        --title "research(${DATE}): ${TOPIC_LABEL}" \
        --body "Daily research brief on **${TOPIC_LABEL}** (${DATE}).

Generated automatically by the research agent." \
        --base main

    log "Pull request created"

    git checkout main
    git branch -d "$BRANCH"
fi

log "Done"
```

- [ ] **Step 2: Make it executable**

Run: `chmod +x run-agent.sh`

- [ ] **Step 3: Check syntax**

Run: `bash -n run-agent.sh`
Expected: No output (no syntax errors)

- [ ] **Step 4: Delete run-remote.sh**

Run: `git rm run-remote.sh`

- [ ] **Step 5: Commit**

```bash
git add run-agent.sh
git commit -m "feat: new run-agent.sh replaces run-remote.sh and infra bootstrap

Single script for containerised research runs. Credentials from env vars
(local) or systemd-creds (server). GITHUB_PAT absent implies --no-commit.
Container mounts repo read-only with briefs/ and eval-runs/ overlaid writable."
```

---

### Task 2: Update systemd service

**Files:**
- Modify: `infra/systemd/research-agent.service`

- [ ] **Step 1: Update the service file**

Replace the contents of `infra/systemd/research-agent.service` with:

```ini
[Unit]
Description=Daily GenAI Research Agent
Wants=network-online.target
After=network-online.target

[Service]
Type=oneshot
User=agent
Group=agent

ExecStart=/opt/research-agent/repo/run-agent.sh

# Secrets are encrypted at rest using a machine-specific key (via systemd-creds).
# Only systemd on this specific machine can decrypt them. Placed at deploy time.
LoadCredentialEncrypted=anthropic-api-key:/etc/research-agent/anthropic-api-key
LoadCredentialEncrypted=github-pat:/etc/research-agent/github-pat

# Research + critic + revision + push can take 20+ minutes
TimeoutStartSec=1800

StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

Key changes from the old version:
- `ExecStart` now points to `/opt/research-agent/repo/run-agent.sh` (the repo copy, updated via git pull) instead of `/opt/research-agent/scripts/run-agent.sh` (the deployed copy)
- Credentials are `anthropic-api-key` and `github-pat` instead of `op-token`

- [ ] **Step 2: Check syntax**

Run: `grep -c '^\[' infra/systemd/research-agent.service`
Expected: `3` (Unit, Service, Install sections)

- [ ] **Step 3: Commit**

```bash
git add infra/systemd/research-agent.service
git commit -m "feat: systemd service runs repo run-agent.sh with actual secrets

ExecStart points to /opt/research-agent/repo/run-agent.sh instead of the
deployed bootstrap script. Credentials are the actual API keys, not the
1Password service account token."
```

---

### Task 3: Update deploy.sh

**Files:**
- Modify: `infra/scripts/deploy.sh`
- Delete: `infra/scripts/run-agent.sh`

- [ ] **Step 1: Remove the run-agent.sh copy step from deploy.sh**

In `infra/scripts/deploy.sh`, replace the "Copying scripts..." block (which copies `run-agent.sh` and `git-askpass.sh` to `/opt/research-agent/scripts/`):

Find this block:
```bash
echo "Copying scripts..."
scp "${INFRA_DIR}/scripts/run-agent.sh" "${SSH_USER}@${SERVER_IP}:/tmp/"
scp "${INFRA_DIR}/scripts/git-askpass.sh" "${SSH_USER}@${SERVER_IP}:/tmp/"
${SSH_CMD} "sudo mv /tmp/run-agent.sh /tmp/git-askpass.sh /opt/research-agent/scripts/ && \
            sudo chmod +x /opt/research-agent/scripts/run-agent.sh /opt/research-agent/scripts/git-askpass.sh && \
            sudo chown agent:agent /opt/research-agent/scripts/*"
```

Replace with (only copies `git-askpass.sh` — `run-agent.sh` now lives in the repo):
```bash
echo "Copying scripts..."
scp "${INFRA_DIR}/scripts/git-askpass.sh" "${SSH_USER}@${SERVER_IP}:/tmp/"
${SSH_CMD} "sudo mv /tmp/git-askpass.sh /opt/research-agent/scripts/ && \
            sudo chmod +x /opt/research-agent/scripts/git-askpass.sh && \
            sudo chown agent:agent /opt/research-agent/scripts/*"
```

- [ ] **Step 2: Verify the secrets section is already correct**

The secrets section (step 5) in `deploy.sh` was already updated earlier in this session to encrypt `anthropic-api-key` and `github-pat` instead of the 1Password service account token. Verify that section reads:

```bash
echo "Fetching Anthropic API key..."
ANTHROPIC_KEY="$(op read 'op://research-agent/ANTHROPIC_API_KEY/credential')"
```

and encrypts as `anthropic-api-key` (not `op-token`).

- [ ] **Step 3: Delete the old infra/scripts/run-agent.sh**

Run: `git rm infra/scripts/run-agent.sh`

- [ ] **Step 4: Check deploy.sh syntax**

Run: `bash -n infra/scripts/deploy.sh`
Expected: No output (no syntax errors)

- [ ] **Step 5: Commit**

```bash
git add infra/scripts/deploy.sh
git commit -m "feat: deploy.sh stops copying run-agent.sh, removes old bootstrap

run-agent.sh now lives in the repo and is kept current via git pull.
Deploy only copies git-askpass.sh to /opt/research-agent/scripts/."
```

---

### Task 4: Verification and cleanup

- [ ] **Step 1: Verify no references to old scripts remain**

Run: `grep -r "run-remote\.sh" --include="*.sh" --include="*.service" --include="*.md" . | grep -v "docs/superpowers/" | grep -v ".git/"`

Expected: No matches (or only in docs/specs/plans which are historical).

Run: `grep -r "infra/scripts/run-agent" --include="*.sh" --include="*.service" --include="*.md" . | grep -v "docs/superpowers/" | grep -v ".git/"`

Expected: Only `deploy.sh` references to `git-askpass.sh` in the same directory, no references to `run-agent.sh` in `infra/scripts/`.

- [ ] **Step 2: Verify run-agent.sh uses GIT_ASKPASS correctly**

The new `run-agent.sh` sets `GIT_ASKPASS` to `${REPO_ROOT}/infra/scripts/git-askpass.sh`. On the server, `REPO_ROOT` is `/opt/research-agent/repo`, so this resolves to `/opt/research-agent/repo/infra/scripts/git-askpass.sh` — the repo copy. But `deploy.sh` also copies `git-askpass.sh` to `/opt/research-agent/scripts/`. Both paths work; the repo copy is preferred since it stays current with git pull.

Verify the path exists: `ls -la infra/scripts/git-askpass.sh`
Expected: File exists and is executable.

- [ ] **Step 3: Verify the systemd service ExecStart path will work**

The service runs `ExecStart=/opt/research-agent/repo/run-agent.sh`. On the server, the repo is cloned to `/opt/research-agent/repo`. After `git pull`, the new `run-agent.sh` will be at that path. Confirm `run-agent.sh` is at the repo root:

Run: `ls -la run-agent.sh`
Expected: Executable file at repo root.

- [ ] **Step 4: Run full syntax check on all changed scripts**

Run: `bash -n run-agent.sh && bash -n infra/scripts/deploy.sh && echo "All OK"`
Expected: `All OK`

- [ ] **Step 5: Final commit if any fixes were needed**

Only if earlier steps revealed issues that were fixed.
