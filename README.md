# GenAI Learning Agent

A daily research agent that scans the web for the latest developments across six GenAI topic areas, produces structured markdown briefs, and commits them to this repo. Runs on a Hetzner VPS via systemd timer, containerised with Docker, secrets from 1Password.

## How it works

The agent runs daily on a remote server. Each run:

1. Picks the next topic in a round-robin rotation (6 topics, one per day)
2. Loads recent briefs as context (last ~28 runs across all topics) to avoid repetition and enable cross-topic synthesis
3. Calls the Anthropic API with extended thinking and web search to research new developments
4. Optionally runs a **critic/revision loop**: a second model call checks the brief against a compliance checklist (format, source tiers, topic boundaries, pillar balance) using structured tool output, then a revision call fixes any violations
5. Saves a structured markdown brief to `briefs/`, commits, pushes, and opens a PR

## Topics (6, rotating daily)

| # | Topic | Focus |
|---|-------|-------|
| 1 | Safety, Assurance & Governance | Alignment research, dangerous capability evaluations, guardrails, agentic supervision, governance frameworks |
| 2 | Enterprise GenAI Adoption | Case studies, ROI, analyst forecasts, regulated industries |
| 3 | Agentic Systems | Frameworks, protocols (MCP/A2A), memory, AgentOps |
| 4 | Models & Market | Frontier model releases, benchmarks, pricing, competitive landscape |
| 5 | LLM Production Infrastructure | LLMOps, observability, evals, inference optimisation, serving |
| 6 | AI Infrastructure & Geopolitics | Semiconductors, energy, data centres, sovereign compute, export controls |

## Architecture

```
research.sh                  # Main orchestrator — topic resolution, prompt rendering, API call, commit
  ├── common.sh              # Shared shell boilerplate (Python resolution, topic resolution)
  ├── agent_cli.py           # CLI tool for topic resolution, prompt rendering, scoring reports
  ├── agent_utils.py         # Shared Python utilities (retry logic, prompt rendering, data models)
  └── run_research.py        # Anthropic API caller — generation, critic, revision

eval.sh                      # Eval runner — generates a brief, scores it, optionally compares two runs
  └── score_brief.py         # Model-based rubric scorer

run-remote.sh                # Server-side wrapper — branch creation, Docker run, push, PR creation
```

### Pipeline phases

1. **Research & generation** (`run_research.py`): Extended thinking + web search. The model performs dedicated searches for each priority source listed in `topics.json`, then synthesises findings into a structured brief.

2. **Critic** (optional, `ENABLE_CRITIC=1`): A second API call checks the brief against the compliance checklist in `prompts/critic-prompt.md`. Returns structured violations via tool use (`report_violations`).

3. **Revision** (triggered by critic failures): A third API call rewrites the brief to fix specific violations while preserving content.

### Priority source searching

Each topic in `topics.json` defines priority sources (e.g., AISI, METR, Anthropic Research for the safety topic). The research prompt instructs the model to run at least two dedicated searches per source using different strategies (site search + name-based search) before general topic research.

## Local development

### Prerequisites

- Python 3, jq
- An Anthropic API key

### Install

```bash
git clone <repo>
cd genai-learning-agent
python3 -m venv .venv
.venv/bin/pip install anthropic
```

### Run locally

```bash
ANTHROPIC_API_KEY=sk-ant-... ./research.sh --no-commit
```

With the critic/revision pipeline:
```bash
ANTHROPIC_API_KEY=sk-ant-... ENABLE_CRITIC=1 ./research.sh --no-commit
```

Override topic (by slug or index):
```bash
ANTHROPIC_API_KEY=sk-ant-... ./research.sh --topic-slug safety-assurance-and-governance --no-commit
```

### Run evals

Generate and score a brief:
```bash
ANTHROPIC_API_KEY=sk-ant-... ./eval.sh --topic safety-assurance-and-governance
```

Score an existing brief:
```bash
ANTHROPIC_API_KEY=sk-ant-... ./eval.sh --topic safety-assurance-and-governance --brief path/to/brief.md
```

Compare two runs:
```bash
ANTHROPIC_API_KEY=sk-ant-... ./eval.sh \
  --topic safety-assurance-and-governance \
  --compare-model claude-sonnet-4-6 \
  --compare-label challenger
```

Eval outputs go to `eval-runs/YYYYMMDD-HHMMSS/` with scores, metadata, and the generated brief.

## Server deployment

The agent runs on a Hetzner CX23 VPS, provisioned with Terraform and configured via cloud-init. See [`infra/README.md`](infra/README.md) for full details.

### Quick deploy (from scratch)

```bash
# 1. Provision
export HCLOUD_TOKEN=$(op item get 'HETZNER_API_KEY' --vault Private --fields credential --reveal)
export TF_VAR_ssh_public_key=$(op item get 'Hetzner From Personal Laptop' --vault Private --fields 'public key' --reveal)
cd infra/terraform && terraform apply

# 2. Deploy (waits for cloud-init, builds Docker image, encrypts 1Password token, enables timer)
cd ../scripts && ./deploy.sh

# 3. Test
ssh deploy@$(cd ../terraform && terraform output -raw server_ip) sudo systemctl start research-agent
```

### How the server runs

1. **systemd timer** fires daily at 07:00 UTC
2. **`run-agent.sh`** (bootstrap): reads 1Password SA token from encrypted credential, fetches API key and GitHub PAT, pulls latest repo
3. **`run-remote.sh`** (repo): creates a branch, runs `research.sh` inside Docker with `ENABLE_CRITIC=1`, pushes, opens a PR
4. **Docker**: `python:3.12-slim` with `anthropic` SDK, `--read-only`, `--user $(id -u):$(id -g)` to avoid root-owned file problems

### Day-to-day operations

```bash
SERVER=$(cd infra/terraform && terraform output -raw server_ip)

# Check timer
ssh deploy@$SERVER systemctl status research-agent.timer

# View logs
ssh deploy@$SERVER journalctl -u research-agent --since today

# Manual run
ssh deploy@$SERVER sudo systemctl start research-agent

# Tear down and rebuild
cd infra/terraform && terraform destroy && terraform apply
cd ../scripts && ./deploy.sh
```

Prompt and script changes are picked up automatically — the bootstrap runs `git pull` before each research run.

## File structure

```
research.sh              # Main orchestrator
eval.sh                  # Eval runner
run-remote.sh            # Server-side branch/Docker/PR wrapper
common.sh                # Shared shell boilerplate
run_research.py          # Anthropic API caller (generation + critic + revision)
score_brief.py           # Model-based rubric scorer
agent_cli.py             # CLI for topic resolution, prompt rendering, scoring
agent_utils.py           # Shared Python utilities (retry, rendering, data models)
topics.json              # Topic definitions, focus areas, and priority sources
prompts/
  research-prompt.md     # Research prompt template
  critic-prompt.md       # Compliance checklist for critic
  revision-prompt.md     # Revision prompt template
  scoring-prompt.md      # Scoring rubric prompt
briefs/
  YYYY-MM-DD-<slug>.md   # Daily research briefs
eval-runs/
  YYYYMMDD-HHMMSS/       # Eval session outputs
evaluation/
  rubric.json            # Scoring dimensions and weights
infra/
  terraform/             # Hetzner server provisioning
  systemd/               # Service and timer units
  scripts/               # Bootstrap and deploy scripts
  docker/                # Dockerfile
learning-log.md          # Index of all briefs
.topic-index             # Round-robin state (gitignored)
agent.log                # Runtime log (gitignored)
```

## Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ANTHROPIC_API_KEY` | (required) | Anthropic API key |
| `ANTHROPIC_MODEL` | `claude-sonnet-4-6` | Model for research generation |
| `THINKING_BUDGET` | `20000` | Extended thinking token budget |
| `MAX_TOKENS` | `32000` | Max output tokens |
| `ENABLE_CRITIC` | (disabled) | Set to `1` or `true` to enable critic/revision loop |
| `CRITIC_MODEL` | same as `ANTHROPIC_MODEL` | Model for critic and revision |
| `CRITIC_THINKING_BUDGET` | `8000` | Thinking budget for critic/revision |
