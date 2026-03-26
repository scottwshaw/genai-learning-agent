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
eval.sh                  # Eval runner (single-run first, optional comparison)
run_research.py          # Anthropic API caller (reads prompt from stdin)
score_brief.py           # Model-based rubric scorer
agent_cli.py             # Shared CLI for eval/research helpers
agent_utils.py           # Shared helper functions and renderers
topics.json              # Topic definitions and focus areas
prompts/
  research-prompt.md     # Research prompt template
briefs/
  YYYY-MM-DD-<slug>.md   # Daily research briefs
eval-runs/
  YYYYMMDD-HHMMSS/       # Eval session outputs
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

`eval.sh` is now built around a single evaluated run. Comparison is optional.

### Generate and score one run

Single-run eval is the default:

```bash
ANTHROPIC_API_KEY=sk-ant-... ./eval.sh \
  --topic llm-production-infrastructure \
  --model claude-sonnet-4-6 \
  --label sonnet-baseline
```

Use a numeric topic index if you prefer:

```bash
ANTHROPIC_API_KEY=sk-ant-... ./eval.sh \
  --topic 2 \
  --model claude-sonnet-4-6 \
  --label sonnet-test
```

### Score an existing brief

Score an existing brief:

```bash
ANTHROPIC_API_KEY=sk-ant-... ./eval.sh \
  --topic llm-production-infrastructure \
  --brief eval-runs/20260326-153316/run.md
```

If you already have a brief and only want to copy it into a new eval run with metadata, skip scoring:

```bash
./eval.sh \
  --topic llm-production-infrastructure \
  --brief eval-runs/20260326-153316/run.md \
  --no-score
```

### Compare only when needed

Optional comparison is explicit:

```bash
ANTHROPIC_API_KEY=sk-ant-... ./eval.sh \
  --topic llm-production-infrastructure \
  --model claude-opus-4-6 \
  --label primary \
  --compare-model claude-sonnet-4-6 \
  --compare-label challenger
```

You can also compare against an existing brief instead of generating the second run:

```bash
ANTHROPIC_API_KEY=sk-ant-... ./eval.sh \
  --topic llm-production-infrastructure \
  --model claude-opus-4-6 \
  --label primary \
  --compare-brief eval-runs/20260326-153316/run.md \
  --compare-label previous-run
```

### Eval outputs

Each eval session creates `eval-runs/YYYYMMDD-HHMMSS/` with some or all of:

- `config.md`: session summary
- `run.md`: primary brief
- `run.metadata.json`: machine-readable metadata for the primary brief
- `scores.json`: primary score output
- `scores.md`: readable Markdown score report
- `compare.md`: comparison brief when enabled
- `compare.metadata.json`: comparison metadata when enabled
- `compare-scores.json`: comparison score output when enabled
- `compare-scores.md`: readable Markdown score report for the comparison run
- `comparison.md`: side-by-side comparison report when both runs are scored

Each generated eval brief also includes an embedded metadata block at the top so
the brief remains self-describing if it gets copied elsewhere.

### Prompt provenance

For generated eval runs, the metadata records prompt provenance using git:

- repo `HEAD` at eval time
- the last commit touching the prompt file
- whether the prompt file was `clean`, `modified`, or `untracked`
- a saved diff patch when the prompt file had uncommitted changes

This gives you enough information to reconstruct which prompt version produced a
brief without copying the entire prompt into the eval output.
