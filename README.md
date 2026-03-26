# GenAI Learning Agent

A daily research agent that scans the web for the latest developments across six GenAI topic areas, produces structured markdown briefs, and commits them to this repo.

## How it works

`research.sh` runs daily (manually or via cron). It:
1. Picks the next topic in a round-robin rotation
2. Loads recent briefs as context (last ~28 runs across all topics) to avoid repetition and track trends
3. Calls the Anthropic API with web search to research new developments
4. Saves a structured markdown brief to `briefs/`
5. Updates `learning-log.md` and commits

## Topics (6, rotating daily)

| # | Topic | Focus |
|---|-------|-------|
| 1 | Safety, Assurance & Governance | Regulatory frameworks, compliance, alignment, auditing |
| 2 | Enterprise GenAI Adoption | Case studies, ROI, analyst forecasts, regulated industries |
| 3 | Agentic Systems | Frameworks, protocols (MCP/A2A), memory, AgentOps |
| 4 | Models & Market | Frontier model releases, benchmarks, pricing, competitive landscape |
| 5 | LLM Production Infrastructure | LLMOps, observability, evals, inference optimisation, serving |
| 6 | AI Infrastructure & Geopolitics | Semiconductors, energy, data centres, sovereign compute, export controls |

## Setup

### Prerequisites

- Python 3
- jq (`brew install jq` / `apt install jq`)
- An Anthropic API key (get one at [console.anthropic.com](https://console.anthropic.com))

### Install

```bash
git clone <repo>
cd genai-learning-agent

# Create venv and install the Anthropic SDK
python3 -m venv .venv
.venv/bin/pip install anthropic

chmod +x research.sh
```

### Run manually

```bash
ANTHROPIC_API_KEY=sk-ant-... ./research.sh
```

Test without committing:
```bash
ANTHROPIC_API_KEY=sk-ant-... ./research.sh --no-commit
```

Use a cheaper model for testing the plumbing:
```bash
ANTHROPIC_API_KEY=sk-ant-... ANTHROPIC_MODEL=claude-haiku-4-5-20251001 ./research.sh --no-commit
```

### Cron setup

The API key must be injected at invocation time — it is never stored on disk.

```cron
0 7 * * * ANTHROPIC_API_KEY=sk-ant-... /path/to/research.sh >> /path/to/agent.log 2>&1
```

### Remote/agent invocation

```bash
ssh user@host "ANTHROPIC_API_KEY=sk-ant-... /path/to/research.sh"
```

## File structure

```
research.sh              # Main script
run_research.py          # Anthropic API caller (reads prompt from stdin)
topics.json              # Topic definitions and focus areas
prompts/
  research-prompt.md     # Research prompt template
briefs/
  YYYY-MM-DD-<slug>.md   # Daily research briefs
learning-log.md          # Index of all briefs
.venv/                   # Python venv (gitignored)
.topic-index             # Round-robin state (gitignored)
agent.log                # Runtime log (gitignored)
```

## Other commands

```bash
./research.sh --topics   # Show topic rotation and which is next
./research.sh --reset    # Wipe all briefs and state (destructive)
```

## Eval runs

Single-run eval is the default:

```bash
ANTHROPIC_API_KEY=sk-ant-... ./eval.sh \
  --topic llm-production-infrastructure \
  --model claude-sonnet-4-6 \
  --label sonnet-baseline
```

Score an existing brief:

```bash
ANTHROPIC_API_KEY=sk-ant-... ./eval.sh \
  --topic llm-production-infrastructure \
  --brief eval-runs/20260326-153316/run.md
```

Optional comparison is explicit:

```bash
ANTHROPIC_API_KEY=sk-ant-... ./eval.sh \
  --topic llm-production-infrastructure \
  --model claude-opus-4-6 \
  --label primary \
  --compare-model claude-sonnet-4-6 \
  --compare-label challenger
```

Each eval brief now includes an embedded metadata block at the top, and the run
directory also contains `run.metadata.json` and `compare.metadata.json` when
applicable. Scored evals also write both JSON and Markdown score reports.
