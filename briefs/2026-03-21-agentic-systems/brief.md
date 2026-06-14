# Agentic Systems — Research Brief
**Date:** 2026-03-21
**Topic Area:** Agentic Systems (#3)
**Focus:** Frameworks, multi-agent, tool use, planning

---

## Overview

Agentic AI has moved from research curiosity to mainstream infrastructure concern in early 2026. The defining shift: individual capable agents are now table stakes — the hard problems are coordination, memory, and interoperability between agents built on different stacks. Three threads dominate current activity: protocol standardisation (MCP and A2A), memory architecture, and the maturation of long-horizon planning runtimes.

---

## Key Developments

### 1. MCP Becomes the Tool-Connectivity Standard

Anthropic's **Model Context Protocol (MCP)** has crossed from niche adoption to genuine industry standard. As of February 2026:

- **97 million monthly SDK downloads** (Python + TypeScript combined)
- **6,400+ registered MCP servers** in the official registry (still in preview)
- Adopted by every major AI provider: Anthropic, OpenAI, Google, Microsoft, Amazon
- Google DeepMind's Demis Hassabis described it as *"rapidly becoming an open standard for the AI agentic era"*

MCP solves the agent-to-tool connectivity problem: a single protocol for giving any LLM access to external tools, data sources, and services. Production pain points remain (auth, versioning, observability), but the ecosystem momentum is now self-reinforcing.

**Why it matters:** Teams that built proprietary tool-call layers in 2024-25 are now migrating to MCP to access the ecosystem rather than maintain bespoke integrations.

---

### 2. Google's A2A Protocol: Agent-to-Agent Interoperability

While MCP handles agent-to-tool, **Google's Agent-to-Agent (A2A) protocol** handles agent-to-agent communication — a different and complementary problem.

Key mechanics:
- Each A2A agent publishes an **Agent Card** at `/.well-known/agent-card.json` describing its name, capabilities, and endpoint
- Agents can discover and delegate tasks to each other regardless of underlying framework
- Complements MCP rather than competing with it (MCP = tools; A2A = peer agents)

Context: Gartner predicts **40% of enterprise applications will embed task-specific AI agents by end of 2026**, up from <5% in 2025. Without an interoperability layer, organisations face a fragmentation problem as agents proliferate across departments and vendors. A2A is Google's answer to that lock-in risk.

**Tension to watch:** MCP vs A2A is not a zero-sum competition, but enterprise architects are currently deciding how to layer both protocols — and which to prioritise when they overlap.

---

### 3. LangChain Deep Agents: Structured Runtime for Long-Horizon Tasks

LangChain released **Deep Agents** (March 2026), a structured runtime addressing a specific failure mode: agents that lose coherence or context over multi-step, long-running tasks.

Core features:
- **Planning layer:** Explicit task decomposition before execution, rather than on-the-fly chaining
- **Filesystem-based context management:** Large context offloaded to storage, not crammed into the active prompt window — avoids context window bloat and cost blowout
- **Context isolation:** Sub-tasks run in isolated sandboxes (v0.4 introduced fully isolated sandbox execution)
- **Pluggable memory backends:** S3, local disk, or in-memory; composite routing so `/memories/` can use persistent cross-thread storage while working files stay local

This is a direct response to production complaints about LangChain/LangGraph agents becoming unreliable at scale. The filesystem-as-working-memory pattern is a significant architectural departure from pure in-context approaches.

---

### 4. Memory Architecture: From Sessions to Persistent Graphs

Memory is emerging as a first-class design concern rather than an afterthought. Key patterns in use:

| Memory Type | Description | Tools |
|---|---|---|
| **Working memory** | Active context window, prompt-managed | All frameworks |
| **Episodic memory** | Session transcripts, retrieved by similarity | Letta, mem0 |
| **Semantic/graph memory** | Structured knowledge graphs, evolving over time | Cognee, Zep |
| **Procedural memory** | Learned preferences, task-specific heuristics | Agent fine-tuning |

**MemMA** (arxiv, March 2026) proposes a multi-agent coordination framework for the memory cycle itself — using dedicated agents to manage memory writing, retrieval, and self-repair when downstream task failures reveal stale or incorrect memories. Notable because it treats memory corruption as a first-class failure mode, not just a retrieval problem.

**Anthropic** made consumer memory free for all Claude users in March 2026 and introduced a memory import tool for transferring histories from other providers — a competitive play that commoditises basic memory and shifts differentiation to quality.

---

### 5. Framework Landscape: Consolidation Starting

The framework proliferation of 2024-25 is starting to rationalise. Current leading options:

- **LangGraph** — best for stateful, checkpointed workflows; strong for long-running web scraping and data pipelines
- **AutoGen** (Microsoft) — better for interactive, exploratory research tasks; strong multi-agent conversation model
- **CrewAI** — role-based agent collaboration; popular for business process automation
- **Deep Agents (LangChain)** — new entrant focused on long-horizon reliability
- **Mastra** — TypeScript-first, gaining traction with frontend/fullstack teams

Differentiation is shifting from "can it call tools" (solved) to **state management, failure recovery, cost control, and observability**.

---

### 6. AI Planning for Web Agents

A recent arxiv paper (*AI Planning Framework for LLM-Based Web Agents*, March 2026) formalises planning for autonomous web agents. Key finding: naive LLM-driven planning degrades in multi-step web tasks because agents treat each step independently rather than maintaining goal coherence. The proposed framework injects classical AI planning techniques (goal decomposition, state tracking) into the LLM loop, improving success rates on complex navigation tasks.

Practical relevance: browser automation and web research agents are a major enterprise use case, and this paper offers a blueprint for making them more reliable.

---

## Emerging Themes

**Protocol convergence is the story of H1 2026.** MCP (tools) + A2A (agents) form a complementary pair that, if widely adopted, could do for agentic AI what HTTP did for the web — a shared substrate that enables ecosystem growth without requiring everyone to agree on implementation details.

**Memory is the unsolved hard problem.** Context windows keep growing, but the interesting work is now on structured, persistent, evolvable memory — not just "what fits in 200k tokens." MemMA's framing of memory-as-infrastructure (with its own maintenance cycle and failure modes) is a useful mental model.

**Reliability over capability.** The market is signalling that enterprises don't need *more capable* agents — they need *more reliable* ones. LangChain Deep Agents, LangGraph's checkpointing, and AutoGen's conversation model all respond to this. Expect evaluation and observability tooling to grow accordingly.

---

## Recommended Reading

- [MCP vs A2A: Complete Guide 2026](https://dev.to/pockit_tools/mcp-vs-a2a-the-complete-guide-to-ai-agent-protocols-in-2026-30li)
- [LangChain Deep Agents release (MarkTechPost)](https://www.marktechpost.com/2026/03/15/langchain-releases-deep-agents-a-structured-runtime-for-planning-memory-and-context-isolation-in-multi-step-ai-agents/)
- [MemMA: Multi-Agent Memory Coordination (arxiv)](https://arxiv.org/html/2603.18718v1)
- [AI Planning Framework for LLM Web Agents (arxiv)](https://arxiv.org/html/2603.12710)
- [Google A2A Protocol — Developer's Guide](https://developers.googleblog.com/developers-guide-to-ai-agent-protocols/)
- [Rise of MCP in the Agentic Era (The Next Web)](https://thenextweb.com/news/rise-of-model-context-protocol-in-the-agentic-era)

---

*Brief generated by Spot · 2026-03-21*
