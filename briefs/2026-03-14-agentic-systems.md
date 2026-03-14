# Agentic Systems — Research Brief (2026-03-14)

## Key Developments

- **Microsoft Agent Framework hits Release Candidate** (Feb 19, 2026) — Microsoft merged AutoGen and Semantic Kernel into a single unified SDK; 1.0 GA expected by end of March 2026. AutoGen is now in maintenance mode. ([Microsoft DevBlog](https://devblogs.microsoft.com/foundry/microsoft-agent-framework-reaches-release-candidate/))
- **A2A Protocol v0.3 released** (early 2026) — Google's Agent2Agent protocol added gRPC transport, agent card signing for security, and expanded SDKs across Python, Go, JavaScript, Java, and .NET. Now hosted by the Linux Foundation with 150+ contributing organizations. ([Google Cloud Blog](https://cloud.google.com/blog/products/ai-machine-learning/agent2agent-protocol-is-getting-an-upgrade))
- **Multi-Agent Memory reframed as a computer architecture problem** (Mar 2026) — New arXiv paper proposes a three-layer memory hierarchy (I/O, cache, memory) for multi-agent systems, identifying cache sharing and structured access control as critical unsolved protocol gaps. ([arXiv 2603.10062](https://arxiv.org/abs/2603.10062))
- **CrewAI v1.10.1 ships native MCP and A2A support** (early 2026) — CrewAI (44.6k GitHub stars) now natively supports both Anthropic's Model Context Protocol and Google's A2A, enabling interoperable multi-agent workflows out of the box. ([OpenAgents comparison](https://openagents.org/blog/posts/2026-02-23-open-source-ai-agent-frameworks-compared))
- **WebArena benchmark scores reach ~60%** (2026) — Agent success rates jumped from 14% to ~60% in two years, driven by convergence on a modular Planner-Executor-Memory architecture pattern. ([ainativedev.io](https://ainativedev.io/news/8-benchmarks-shaping-the-next-generation-of-ai-agents))

## Notable Papers / Models / Tools

| Item | Date | Source | Summary |
|------|------|--------|---------|
| Multi-Agent Memory from a Computer Architecture Perspective | Mar 2026 | [arXiv 2603.10062](https://arxiv.org/abs/2603.10062) | Position paper proposing three-layer memory hierarchy for multi-agent systems, identifying cache-sharing and access-control as open protocol gaps |
| Microsoft Agent Framework RC | Feb 19, 2026 | [Microsoft DevBlog](https://devblogs.microsoft.com/foundry/microsoft-agent-framework-reaches-release-candidate/) | Unified successor to AutoGen + Semantic Kernel; stable API surface, GA imminent |
| A2A Protocol v0.3 | Early 2026 | [a2a-protocol.org](https://a2a-protocol.org/v0.3.0/specification/) | gRPC transport, agent card signing, expanded multi-language SDK support |
| Agent-Oriented Planning (AOP) | 2026 | [OpenReview](https://openreview.net/forum?id=EqcLAU6gyU) | Framework for fast task decomposition and allocation across agents with reward-model-based evaluation |
| Mem0 v2 | 2025–2026 | [arXiv 2504.19413](https://arxiv.org/abs/2504.19413) | Graph-enhanced memory architecture: 91% lower p95 latency, 90%+ token savings vs. full-context |
| OpenAI AgentKit | Oct 2025 (evolving) | [OpenAI](https://openai.com/index/introducing-agentkit/) | Visual Agent Builder, Connector Registry, ChatKit — drag-and-drop multi-agent workflow design |
| MALLVI | Feb 2026 | [arXiv 2602.16898](https://arxiv.org/abs/2602.16898) | Multi-agent framework for robotic manipulation: Decomposer, Localizer, Thinker, Reflector agents in closed-loop coordination |

## Technical Deep-Dive

### Multi-Agent Memory as Computer Architecture (arXiv 2603.10062)

The most architecturally interesting recent contribution reframes multi-agent memory through the lens of classical computer architecture. The paper, published March 2026, argues that as LLM-based multi-agent systems scale, their memory requirements exhibit the same locality, bandwidth, and consistency challenges that drove the development of CPU cache hierarchies and memory buses decades ago.

The proposed architecture defines three layers. The **Agent I/O layer** handles interfaces for ingesting external information (tool outputs, user messages, inter-agent signals). The **Agent Cache layer** provides fast, limited-capacity memory for immediate reasoning — analogous to L1/L2 cache, this stores the working set of facts and plans an agent needs for its current task. The **Agent Memory layer** offers large-capacity persistent storage optimized for retrieval, serving as the equivalent of main memory or disk, where long-term knowledge, episodic memories, and learned procedures accumulate.

What makes this more than a metaphor is the identification of two critical protocol gaps that have no satisfactory solution in existing frameworks. First, **cache sharing across agents**: when multiple agents collaborate, they need mechanisms to expose relevant portions of their working memory to peers without full context dumps — the multi-agent equivalent of cache coherence protocols (MESI, MOESI) in multiprocessor systems. Second, **structured memory access control**: agents must enforce read/write permissions on memory segments, preventing one agent from corrupting another's state while still enabling controlled collaboration. Current frameworks like LangGraph and CrewAI handle this ad hoc through shared state dictionaries, but lack formal access semantics.

The paper's significance lies in shifting the discourse from "how do we give agents memory" (largely solved by RAG and vector stores) to "how do we architect memory for systems of agents that must coordinate" — a problem that grows superlinearly with agent count. The framework is prescriptive rather than implemented, but it provides a principled vocabulary for the next generation of multi-agent orchestration libraries to build against. The parallel to computer architecture also suggests that proven solutions (write-back policies, directory-based coherence, memory-mapped I/O) may be directly adaptable.

## Implications & Trends

- **Protocol convergence is accelerating.** With A2A v0.3, MCP, and CrewAI natively supporting both, the agentic ecosystem is moving from fragmented framework-specific patterns toward interoperable protocols. Gartner predicts 40% of enterprise apps will embed AI agents by end of 2026, making this interoperability layer infrastructure-grade.
- **The "single SDK" consolidation wave is here.** Microsoft merging AutoGen + Semantic Kernel, OpenAI shipping AgentKit as a unified builder — the era of choosing between 5 competing abstractions is giving way to platform-level frameworks with batteries included. Expect similar consolidation from Google (Vertex AI Agent Builder) and AWS.
- **Memory is the new bottleneck.** As planning and tool-use capabilities mature (WebArena scores doubling), the limiting factor for long-horizon autonomous agents is shifting to memory architecture — how agents persist, share, and reason over accumulated context across multi-step workflows. The computer-architecture framing suggests this will become a first-class research area distinct from retrieval-augmented generation.

## Sources

- [Microsoft Agent Framework RC announcement](https://devblogs.microsoft.com/foundry/microsoft-agent-framework-reaches-release-candidate/)
- [Microsoft Agent Framework migration guide](https://devblogs.microsoft.com/agent-framework/migrate-your-semantic-kernel-and-autogen-projects-to-microsoft-agent-framework-release-candidate/)
- [InfoQ: MS Agent Framework RC](https://www.infoq.com/news/2026/02/ms-agent-framework-rc/)
- [A2A Protocol v0.3 specification](https://a2a-protocol.org/v0.3.0/specification/)
- [Google Cloud: A2A upgrade announcement](https://cloud.google.com/blog/products/ai-machine-learning/agent2agent-protocol-is-getting-an-upgrade)
- [A2A Developer Digest 2026-03-11](https://dev.to/eclaw/a2a-developer-digest-20260311-building-your-first-a2a-agent-1h56)
- [arXiv 2603.10062: Multi-Agent Memory from a Computer Architecture Perspective](https://arxiv.org/abs/2603.10062)
- [arXiv 2504.19413: Mem0 — Scalable Long-Term Memory](https://arxiv.org/abs/2504.19413)
- [arXiv 2602.16898: MALLVI multi-agent robotic manipulation](https://arxiv.org/abs/2602.16898)
- [Agent-Oriented Planning — OpenReview](https://openreview.net/forum?id=EqcLAU6gyU)
- [OpenAI: Introducing AgentKit](https://openai.com/index/introducing-agentkit/)
- [OpenAI Agents SDK docs](https://openai.github.io/openai-agents-python/)
- [OpenAgents: Framework comparison (Feb 2026)](https://openagents.org/blog/posts/2026-02-23-open-source-ai-agent-frameworks-compared)
- [Top 9 AI Agent Frameworks — Shakudo](https://www.shakudo.io/blog/top-9-ai-agent-frameworks)
- [8 benchmarks shaping next-gen AI agents](https://ainativedev.io/news/8-benchmarks-shaping-the-next-generation-of-ai-agents)
- [Memory for AI Agents — The New Stack](https://thenewstack.io/memory-for-ai-agents-a-new-paradigm-of-context-engineering/)
- [6 Best AI Agent Memory Frameworks 2026](https://machinelearningmastery.com/the-6-best-ai-agent-memory-frameworks-you-should-try-in-2026/)
