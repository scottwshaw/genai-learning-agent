# Agentic Systems — Research Brief (2026-05-29)

## Key Developments

- **MCP stateless redesign locks in, forcing immediate production migration.**
  - **What changed:** 
The MCP 2026-07-28 RC locked May 21, making the protocol stateless and removing the session-initialization handshake.

  - **Why it matters:** 
Any MCP server that required sticky sessions now needs migration before the July 28 final spec.

  - *(MCP Blog / AAIF, May 21, 2026)*

- **NSA formally designates MCP attack classes as production security risk.**
  - **What changed:** 
The NSA's AI Security Center released a Cybersecurity Information Sheet on MCP security risks on May 20, 2026.

  - **Why it matters:** 
The advisory names active attack surfaces in MCP, elevating it from a developer concern to a regulated-infrastructure risk.

  - *(NSA AISC / QA Financial / Resultsense, May 20–26, 2026)*

- **Empirical work shows execution harness outweighs model choice for agent reliability.**
  - **What changed:** 
Controlled harness variation alone lifted a fixed agent from 52.8% to 66.5% on Terminal-Bench 2.0.

  - **Why it matters:** 
Teams optimising agents through model upgrades may be misallocating effort, as harness engineering is the binding variable.

  - *(arXiv:2605.26112 — unaffiliated preprint, unverified; arXiv:2605.27922 — unaffiliated, unverified; arXiv:2605.24220 — NVIDIA Research; open review survey picrew.github.io; MindStudio/Endor Labs benchmark, May 2026)*

---

## Notable Papers / Models / Tools

| Item | Date | Source | Summary |
|------|------|--------|---------|
| MCP 2026-07-28 Release Candidate | May 21, 2026 | [MCP Blog](https://blog.modelcontextprotocol.io/posts/2026-07-28-release-candidate/) [Tier 1 — Standards body] | Largest MCP revision since launch: stateless core removes session ID and initialize handshake; routing headers (Mcp-Method, Mcp-Name) enable gateway operation without body inspection; TTL-based caching (ttlMs/cacheScope); W3C Trace Context locked in _meta for OTel correlation; formal deprecation policy; final spec July 28, 2026; breaking changes require production migration |
| NSA AISC MCP Security CSI (U/OO/6030316-26) | May 20, 2026 | [NSA.gov](https://www.nsa.gov/Portals/75/documents/Cybersecurity/CSI_MCP_SECURITY.pdf) [Tier 1 — US government security body] | 17-page guidance naming serialization risks, trust boundary failures, unverified task propagation, and injection vulnerabilities as active MCP attack surfaces; recommends data-classification zone alignment, filtered egress proxies, DLP, and comprehensive tool-invocation logging; first intelligence-community advisory scoped to the MCP ecosystem |
| Rollout Cards: A Reproducibility Standard for Agent Research (arXiv:2605.12131) | May 12, 2026 | [arXiv — Nanyang Technological University / Deepflow](https://arxiv.org/abs/2605.12131) [Tier 1 — arXiv affiliated] | Structured audit of 50 agent training and evaluation repositories finds none report failed or skipped runs alongside headline scores; documents 37 cases where differing reporting rules change task-success, cost, or timing measurements for identical evidence; proposes Rollout Cards as a minimal structured disclosure standard |
| What Twelve LLM Agent Benchmark Papers Disclose About Themselves (arXiv:2605.21404) | May 20, 2026 | [arXiv — unaffiliated](https://arxiv.org/abs/2605.21404) [Tier 1 — arXiv, unaffiliated, unverified] | Pilot audit applying a five-field schema to 12 canonical agent benchmark papers; mean disclosure score 0.38/1.0 for agent benchmarks vs. 0.66 for classical static benchmarks; zero of the eight agent benchmark papers disclose inference cost in any form; scaffold and sampling settings routinely omitted |
| Polar: Agentic RL on Any Harness at Scale (arXiv:2605.24220) | May 22, 2026 | [arXiv — NVIDIA Research](https://arxiv.org/abs/2605.24220) [Tier 1 — arXiv affiliated] | RL rollout framework that treats the agent harness as a black box by proxying LLM API calls and reconstructing token-faithful trajectories; decouples I/O-heavy agent execution from GPU training, exposing asynchronous service endpoints; enables RL training on closed-source harnesses (Claude Code, OpenClaw) without harness modification |
| From Model Scaling to System Scaling: Scaling the Harness (arXiv:2605.26112) | May 25, 2026 | [arXiv — unaffiliated preprint, unverified](https://arxiv.org/abs/2605.26112) | Argues the agent harness — memory substrate, context constructor, skill routing, orchestration loop, and verification layer — is the binding reliability constraint for long-horizon tasks; proposes harness-level benchmarks measuring trajectory quality, memory hygiene, and context efficiency; introduces CheetahClaws reference harness benchmarked against Claude Code and OpenClaw |
| AAMAS 2026 (25th International Conference on Autonomous Agents and MAS) | May 25–29, 2026 | [IFAAMAS / Imperial College announcement](https://cyprusconferences.org/aamas2026) [Tier 1 — Peer-reviewed venue] | Record 1,455 full-paper submissions in 25 conference years; new Generative and Agentic AI (GAAI) track formalises LLM-based agents within MAS research; Imperial/Glasgow paper on safety-critical decentralised agent coordination accepted; proceedings appear this week |
| Harness-Bench (arXiv:2605.27922) | May 27, 2026 | [arXiv — unaffiliated, unverified](https://arxiv.org/abs/2605.27922) | Introduces controlled harness-variation methodology: fixes base model and task set, varies the execution harness (context management, tool schemas, permissions, tracing), and measures outcome deltas; designed to isolate execution-layer effects that benchmark suites currently aggregate away |
| EvolveMem (arXiv:2605.13941) | May 13, 2026 | [arXiv — UNC Chapel Hill / UC Berkeley / UCSC](https://arxiv.org/abs/2605.13941) [Tier 1 — arXiv affiliated] | Self-evolving memory architecture that co-evolves stored content and retrieval mechanisms via an LLM-powered diagnosis module; reads per-question failure logs, proposes targeted configuration changes, and applies them with automatic revert-on-regression (covered in prior brief 2026-05-23, included here for Notable Papers completeness) |

---

## Technical Deep-Dive

**MCP 2026-07-28: What the Stateless Redesign Actually Requires**

The MCP 2026-07-28 release candidate, locked May 21 with a July 28 final date, is a structural redesign that invalidates the session-initialization pattern used in all prior MCP deployments.
The headline change is that MCP is now stateless at the protocol layer, with six Specification Enhancement Proposals working together to complete the plan laid out in the "Future of MCP Transports" roadmap from December 2025.
 The practical problem being solved is well-documented: 
a two-pod deployment with round-robin load balancing would have pod A handle the initialize handshake and mint an Mcp-Session-Id, then the SDK's long-lived SSE GET would hash to pod B, which returned a 404 — the only workaround being LB stickiness, itself a protocol-level state workaround.


The structural changes are interlocking. 
The initialize handshake is gone: protocol version, client info, and capabilities now travel in `_meta` on every request, meaning any server instance can handle any request, and a production MCP server that previously required sticky sessions and a shared session store can now run behind a plain round-robin load balancer.
 Two additional changes complete the operational picture: 
the Streamable HTTP transport now requires Mcp-Method and Mcp-Name headers on every request, enabling load balancers, gateways, and rate-limiters to route on the operation without opening the request body.
 And 
list and resource read results now carry ttlMs and cacheScope fields modelled on HTTP Cache-Control, while W3C Trace Context propagation in `_meta` has locked-down key names — enabling a trace starting in a host application to follow a tool call through the MCP server as a single span tree in any OpenTelemetry backend.


For enterprise teams, the migration calculus is narrow but non-negotiable. 
Breaking changes are real — every production MCP server needs migration before July 28.
 The deprecation policy provides a 12-month window for deprecated features (Roots, Sampling, Logging), so existing tools, resources, and prompts continue to function. The immediate migration action item is audit-driven: 
teams need to check whether requests can move across server instances without losing context, locate hidden session dependencies, and ensure every server-side state item (repository path, browser session, deployment environment) has an explicit handle or scope the client can see, log, and pass back.


The NSA MCP advisory, released one day before the RC locked, creates a compounding obligation. The advisory explicitly names gaps that the 2026-07-28 spec begins to close (OAuth/OIDC hardening, routing header transparency) but does not fully resolve: 
for banks experimenting with agentic AI capable of autonomously executing workflows, the NSA warning makes clear that teams may increasingly need to validate runtime behaviour, permission boundaries, authentication logic, execution chains, and API interactions inside live operational environments — not just model accuracy or hallucination rates.
 Financial services teams planning MCP rollouts in H2 2026 should treat the July 28 final spec date as a procurement synchronisation point: any MCP server vendor that cannot demonstrate 2026-07-28 compliance by that date will be shipping a protocol revision behind the NSA's documented minimum baseline.

---

## Landscape Trends

- **The agent harness is becoming the primary reliability engineering surface — the framework choice is secondary.** A convergent body of work published in the past two weeks (arXiv:2605.26112, arXiv:2605.27922, arXiv:2605.24220, the Endor Labs benchmark cited by MindStudio) establishes empirically what practitioners have suspected: for long-horizon tasks, outcome variance attributable to harness configuration — context governance, tool schema design, retry logic, permission profiles — is comparable to or exceeds variance attributable to model choice. 
The emerging framing is the "binding-constraint thesis": for long-horizon tasks evaluated across comparable frontier models, benchmark variance may be driven as much by the execution harness as by the model itself.
 The operational implication is that teams optimising agent reliability primarily through model upgrades are likely misallocating effort. Procurement decisions should shift toward harness instrumentation, audit trail coverage, and execution-environment reproducibility.

- **[Agentic Systems × Safety, Assurance & Governance] MCP has crossed the threshold from developer protocol to regulated-infrastructure concern.** The NSA AISC advisory and the Five Eyes joint guidance on agentic AI (published April 30, 2026) together mark a transition: agent tool protocols are now subject to the same category of sovereign-security scrutiny as network protocols and cryptographic standards. 
This is the first formal intelligence-community security advisory scoped specifically to the MCP ecosystem, and MCP is now embedded in production AI workflows at major financial and legal institutions, meaning the NSA's findings describe active exposure in regulated industries where a breach carries compliance and liability consequences.
 The 2026-05-12 brief surfaced the academic attack surface (MCPInspect, ARGUS, bidirectional data-flow risks); the NSA advisory converts those academic findings into a compliance obligation. Financial services teams should treat MCP server vetting as a supply-chain security control, not an integration-ease decision.

- **[Agentic Systems × LLM Production Infrastructure] The MCP RC's OTel trace-context standardisation is the most underreported operational change in the release.** The prior brief pattern across LLM Production Infrastructure (2026-05-25 and earlier) consistently shows OTel GenAI semconv as the convergence point for agent observability. The MCP 2026-07-28 RC locks W3C Trace Context key names inside `_meta`, which means — for the first time — distributed traces can follow a tool call from host application through MCP client, through the MCP server, and into downstream services as a single correlated span tree in any OTel-compatible backend. This resolves a long-standing gap noted in the 2026-05-14 brief (Red Hat AI 3.4 / llm-d eval hub used MCP with OTel tracing but without protocol-level trace propagation standardisation). Enterprise observability teams should begin planning MCP-aware trace correlation pipelines ahead of the July 28 final spec.

- **Agent evaluation reproducibility is now a research crisis, not a practice gap.** The Rollout Cards paper (arXiv:2605.12131, Nanyang Technological University) and the benchmark audit paper (arXiv:2605.21404) converge on a finding that should concern anyone using agent benchmarks for procurement or capability claims: 
in a structured audit of 50 popular training and evaluation repositories, none report how many runs failed, errored, or were skipped alongside headline scores, and 37 cases exist where reporting rules can change task-success rates, cost/token accounting, or timing measurements for fixed evidence.
 The 2026-05-18 brief surfaced AgentLens ("lucky pass" problem in SWE-Agent evaluation); this week's papers systematise that finding and propose disclosure standards. The implication for regulated enterprise teams is that vendor-reported agent benchmark scores should be treated as indicative, not auditable, until rollout records and reporting rules are disclosed.

- **[Agentic Systems × Enterprise GenAI Adoption] GCHQ's agentic-AI cyber defence blueprint signals that agent deployment at national-infrastructure scale is moving from aspiration to funded programme.** The 2026-05-17 Enterprise GenAI brief documented Gartner's AI agent software forecast of $206B in 2026; the GCHQ announcement shows the demand signal extends to sovereign security budgets. 
GCHQ's system would use AI agents to detect and flag threats to critical national infrastructure, airlines, and telecoms firms, with a five-year operational target.
 For enterprise teams in critical sectors, this trajectory has a procurement consequence: supplier certification expectations for AI-agent security posture will tighten as the national capability comes online, and DORA-regulated firms in financial services should expect the FCA and PRA to reference NCSC agentic AI guidance in supervisory engagement through H2 2026.

---

## Vendor Landscape

**OpenAI Codex** shipped multiple CLI releases in the past week (v0.134.0 on May 26), with 
MCP setup improvements including per-server environment targeting and OAuth options for Streamable HTTP servers, and read-only MCP tools now able to run concurrently when they advertise `readOnlyHint`.
 The May 2026 Codex release cycle also formalised 
MultiAgentV2 configuration with thread caps, wait-time controls, root/subagent hints, and v2-specific depth handling
 — the first production-documented multi-agent concurrency configuration in the Codex runtime.

**SAP Joule Studio 2.0 and AI Agent Hub** (Sapphire 2026, May 14–17) added LangChain, AutoGen, and LlamaIndex framework support with natural-language-to-agent generation; the AI Agent Hub provides centralised discovery, verification, observability, and policy enforcement for SAP and non-SAP agents — a notable move toward multi-vendor agent governance at the enterprise application layer. [Tier 2 — Vendor announcement]

**AutoGen** has formally entered maintenance mode as confirmed across multiple independent sources; 
Microsoft Research's AutoGen project entered maintenance mode in late 2025 with v0.7.5 as the last meaningful release, the repository explicitly stating it will not receive new features, with Microsoft Agent Framework (MAF) as the recommended successor.
 Teams running AutoGen in production should initiate migration planning.

---

## Sources

- https://blog.modelcontextprotocol.io/posts/2026-07-28-release-candidate/ [Tier 1 — Standards body (AAIF/Linux Foundation)]
- https://www.nsa.gov/Press-Room/Press-Releases-Statements/Press-Release-View/Article/4496698/nsa-releases-security-design-considerations-for-ai-driven-automation-leveraging/ [Tier 1 — US government security body]
- https://www.nsa.gov/Portals/75/documents/Cybersecurity/CSI_MCP_SECURITY.pdf [Tier 1 — US government security body]
- https://arxiv.org/abs/2605.12131 [Tier 1 — arXiv affiliated (Nanyang Technological University)]
- https://arxiv.org/abs/2605.24220 [Tier 1 — arXiv affiliated (NVIDIA Research)]
- https://arxiv.org/abs/2605.13941 [Tier 1 — arXiv affiliated (UNC Chapel Hill / UC Berkeley / UCSC)]
- https://arxiv.org/abs/2605.26112 [Tier 1 — arXiv, unaffiliated, unverified]
- https://arxiv.org/abs/2605.27922 [Tier 1 — arXiv, unaffiliated, unverified]
- https://arxiv.org/abs/2605.21404 [Tier 1 — arXiv, unaffiliated, unverified]
- https://www.gchq.gov.uk/speech/gchq-annual-lecture-2026-as-delivered [Tier 1 — UK government intelligence body]
- https://www.infosecurity-magazine.com/news/gchq-keast-butler-cyber-action-ai/ [Tier 1 — Independent journalism]
- https://www.thestack.technology/gchq-teases-blueprint-for-agentic-ai-national-cyber-defense/ [Tier 1 — Independent journalism]
- https://qa-financial.com/nsa-warning-on-ai-automation-protocol-raises-fresh-testing-concerns-for-banks/ [Tier 1 — Independent journalism (QA Financial)]
- https://www.resultsense.com/news/2026-05-26-nsa-mcp-warning-banks-agentic-ai/ [Tier 2 — Industry news]
- https://mcp.directory/blog/mcp-2026-07-28-release-candidate [Tier 2 — Developer community analysis]
- https://aaif.io/blog/mcp-is-growing-up/ [Tier 2 — Standards body blog]
- https://developers.openai.com/codex/changelog [Tier 2 — Vendor changelog]
- https://news.sap.com/2026/05/sap-sapphire-sap-unveils-autonomous-enterprise/ [Tier 2 — Vendor announcement]
- https://cyprusconferences.org/aamas2026 [Tier 1 — Peer-reviewed venue]
- https://openreview.net/pdf?id=eONq7FdiHa [Tier 1 — Open review (Agent Harness Engineering survey)]
- https://picrew.github.io/LLM-Harness/ [Tier 2 — Developer community]
- https://futureagi.com/blog/crewai-vs-langgraph-vs-autogen-2026/ [Tier 2 — Developer community analysis]
