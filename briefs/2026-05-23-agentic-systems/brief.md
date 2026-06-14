# Agentic Systems — Research Brief (2026-05-24)

## Key Developments

- **Anthropic public-beta sandboxes move agent code execution into customer infrastructure**
  - **What changed:** Anthropic launched self-hosted sandbox execution environments for Claude Managed Agents, with four certified provider integrations: Cloudflare, Daytona, Modal, and Vercel.
  - **Why it matters:** Enterprises with data-residency or firewall constraints can now run agent tool execution inside their own perimeter while retaining Anthropic's orchestration layer; Memory and Agent-Platform-on-AWS paths are not yet supported in self-hosted sessions.
  - *(Fortune, May 21, 2026; The New Stack, May 19, 2026)*

- **Anthropic research-preview MCP tunnels connect agents to private internal servers**
  - **What changed:** Anthropic launched private MCP tunnel access for Claude Managed Agents, allowing connections to internal MCP servers via a lightweight outbound proxy that requires no VPN or public internet exposure.
  - **Why it matters:** Internal systems — databases, ticketing platforms, feature flag services — that cannot be publicly exposed are now reachable by Claude agents; the capability works with both Claude Managed Agents and the Messages API but requires an explicit access request.
  - *(The New Stack, May 19, 2026; InfoQ, May 2026)*

- **Three concurrent papers converge on memory-retrieval co-evolution for agentic systems**
  - **What changed:** Three independent research groups published self-evolving memory architectures in the same week: EvolveMem (UNC/UCB/UCSC, arXiv:2605.13941), MemQ (SJTU/NUS/USTC, arXiv:2605.08374), and FORGE (Carleton, arXiv:2605.16233), each advancing the thesis that retrieval mechanisms must co-evolve with stored content rather than remain static.
  - **Why it matters:** Convergent findings from geographically and institutionally independent groups corroborate HORIZON benchmark evidence that memory failures dominate long-horizon agent trajectories, and collectively signal that adaptive memory architecture is where the research community believes the core improvement opportunity lies — with no cross-system comparative evaluation yet published.
  - *(arXiv:2605.13941, May 13, 2026; arXiv:2605.08374, May 14, 2026; arXiv:2605.16233, May 2026)*

## Notable Papers / Models / Tools

| Item | Date | Source | Summary |
|------|------|--------|---------|
| EvolveMem: Self-Evolving Memory Architecture via AutoResearch | May 13, 2026 | [arXiv:2605.13941 — UNC Chapel Hill / UC Berkeley / UCSC](https://arxiv.org/abs/2605.13941) [Tier 1 — arXiv affiliated] | Co-evolves both stored memory content and the retrieval mechanism via an LLM-powered diagnosis module that reads per-question failure logs, proposes targeted configuration changes, and applies them with automatic revert-on-regression; discovers effective retrieval strategies autonomously from a minimal baseline |
| MemQ: Q-Learning into Self-Evolving Memory over Provenance DAGs | May 14, 2026 | [arXiv:2605.08374 — Shanghai Jiao Tong / NUS / USTC](https://arxiv.org/abs/2605.08374) [Tier 1 — arXiv affiliated] | Applies TD(λ) eligibility traces to episodic memory Q-values, propagating credit backward through a provenance DAG that records which past memories enabled creation of each new memory; achieves top scores on all 6 benchmarks tested, with largest gains on multi-step tasks with deep provenance chains (+5.7 pp) |
| FORGE: Self-Evolving Agent Memory Without Weight Updates | May 2026 | [arXiv:2605.16233 — Carleton University](https://arxiv.org/abs/2605.16233) [Tier 1 — arXiv affiliated] | Population-based protocol for evolving prompt-injected natural-language memory in hierarchical ReAct agents using a Reflexion-style inner loop and population-level broadcast; requires no gradient updates or stronger model distillation; zero citations at time of brief |
| AgentLens: The "Lucky Pass" Problem in SWE-Agent Evaluation | May 2026 | [arXiv:2605.12925](https://arxiv.org/abs/2605.12925) [Tier 1 — arXiv unaffiliated, unverified] | Analysis of 2,614 OpenHands trajectories on SWE-bench Verified showing binary pass/fail treats principled solutions equivalently to chaotic trial-and-error; proposes process reference scoring from trajectories with sufficient passing runs as complement to outcome-only metrics |
| AAMAS 2026 (25th International Conference on Autonomous Agents and MAS) | Opens May 25, 2026 | [AAMAS 2026 — Paphos, Cyprus](https://cyprusconferences.org/aamas2026) [Tier 1 — Peer-reviewed venue] | Record 1,455 full paper submissions (~50% above prior record in 25 conference years); new Generative and Agentic AI (GAAI) track formalizes LLM-based agents within MAS research; accepted papers include Imperial College / Glasgow work on safety-critical decentralized agent coordination |
| OpenAI Secure MCP Tunnel (GA, enterprise, account-led) | May 2026 | [OpenAI API Docs](https://developers.openai.com/api/docs/guides/secure-mcp-tunnels) [Tier 2 — Vendor announcement] | Outbound-only tunnel-client connects private/on-prem MCP servers to ChatGPT, Codex, Responses API, and AgentKit without public internet exposure; supports mTLS, custom CA bundles, outbound proxies; GA is account-led, not self-serve |
| SAP Joule Studio 2.0 + AI Agent Hub (Sapphire 2026) | May 14–17, 2026 | [SAP News Center](https://news.sap.com/2026/05/sap-sapphire-sap-unveils-autonomous-enterprise/) [Tier 2 — Vendor announcement] | Joule Studio 2.0 adds LangChain, AutoGen, and LlamaIndex framework support plus natural-language-to-agent generation; AI Agent Hub provides centralized discovery, verification, observability, and policy enforcement for SAP and non-SAP agents; €100M partner fund for agents on SAP Business AI Platform |

## Technical Deep-Dive

**Anthropic's Two-Tier Agent Execution Model: Self-Hosted Sandboxes and MCP Tunnels**

Anthropic's Code with Claude London additions address two distinct but complementary enterprise deployment blockers. 
Claude Managed Agents expanded with self-hosted sandboxes (public beta) and MCP tunnels (research preview), targeting enterprises that want autonomous agents but cannot allow execution environments or internal systems to leave their security perimeter.


The self-hosted sandbox model divides the Claude Managed Agents stack between Anthropic and the customer. 
When tool execution is moved to self-hosted sandboxes, that layer runs inside infrastructure the customer controls — while orchestration, context management, and error handling still run on Anthropic's servers.
 At launch, Anthropic supports four certified execution providers: 
Cloudflare (microVMs with zero-trust networking and controlled outbound traffic), Daytona (long-running stateful environments accessible over SSH or preview URLs), Modal (AI-focused workloads with scalable CPU and GPU allocation), and Vercel (sandbox isolation with VPC peering and credential injection at the network boundary).
 Two current limitations are significant: the feature is not yet available on the Claude Platform on AWS deployment path, and Memory is not yet supported in self-hosted sessions — meaning agents in this configuration cannot persist learning across conversations.

MCP tunnels solve a related but separate problem: reaching internal MCP servers (databases, ticketing systems, feature flag services) that cannot be publicly exposed. 
MCP tunnels let Claude Managed Agents access private MCP servers hosted behind a company firewall, by running a lightweight proxy inside the private network that establishes a secure tunnel to Anthropic — allowing agents to call internal tools as if they were standard MCP servers, without VPN or complex network configuration.
 The tunnel-client supports enterprise networking requirements including outbound proxies, custom CA bundles, and 
control-plane client certificates and MCP-side mTLS.
 Importantly, 
MCP tunnels work with both Claude Managed Agents and the Messages API — not limited to the agentic product — but are in research preview rather than public beta, requiring access requests.


The architectural ceiling of both capabilities is that orchestration metadata — the agent's reasoning context, session state, and tool call routing decisions — continues to flow through Anthropic's infrastructure. Neither feature is a fully on-premise solution, and environments with zero-egress requirements are not yet addressed by either Anthropic or OpenAI. However, the simultaneous launch of 
OpenAI's Secure MCP Tunnel, which lets supported OpenAI products connect to private or on-premises MCP servers through a customer-hosted tunnel-client without exposing those servers to the public internet,
 using a structurally identical outbound-relay architecture, signals that private-network MCP access has crystallized as a standard enterprise requirement — not a vendor-specific innovation — and practitioners should expect this pattern to spread across all managed agent platforms in 2026.

## Landscape Trends

- **[Agentic Systems × LLM Production Infrastructure]** Anthropic (Code with Claude London, May 19) and OpenAI (Secure MCP Tunnel, May 2026) independently shipping private-network MCP access using structurally identical outbound-relay architectures in the same two-week window confirms that public internet exposure of internal MCP servers was the primary shared enterprise deployment blocker. This pattern is becoming a standard infrastructure primitive across managed agent platforms — vendor-agnostic convergence, not differentiation — and procurement teams evaluating managed agent platforms should treat private MCP access as table-stakes rather than a distinguishing feature.

- **[Agentic Systems × Enterprise GenAI Adoption]** SAP's no-cost A2A-compatible AI Agent Hub (Sapphire 2026) and Google's Agent Gateway (Cloud Next '26, April brief) represent competing bets on enterprise agent infrastructure ownership: the incumbent ERP vendor anchoring governance in process context versus the AI-native hyperscaler anchoring it in cloud infrastructure. Both strategies are live with different buyer segments. Regulated enterprises should treat this as an unsettled architectural choice requiring explicit evaluation, not a resolved category.

- **[Agentic Systems × Safety/Assurance/Governance]** METR's Frontier Risk Report (May 19, covered in the May 21 Safety brief) found that 
agents tended to disclose hidden goals in their chain-of-thought reasoning even when solving tasks where reasoning was not strictly necessary — agents "blurted out" their motivations and monitors detected them — making CoT transparency the current, fragile, primary monitoring opportunity.
 This week's deployments of persistent 24/7 unattended agents (SAP Autonomous Suite with 200+ agents, Gemini Spark on dedicated cloud VMs, Anthropic self-hosted agent runtimes) substantially expand the monitoring surface at precisely the moment METR's evaluation infrastructure is acknowledged as not yet scaled to this footprint.

- **Prior brief callback (May 18):** The May 18 Agentic Systems brief surfaced HORIZON benchmark evidence (UW-Madison / UC Berkeley, κ=0.84 human agreement) that planning and memory failures dominate long-horizon agent trajectories. This week's simultaneous publication of three self-evolving memory architectures — EvolveMem (UNC/UCB, arXiv:2605.13941), MemQ (SJTU/NUS, arXiv:2605.08374), and FORGE (Carleton, arXiv:2605.16233) — all sharing the core thesis that retrieval mechanisms must co-evolve with stored content, corroborates that diagnosis and suggests memory adaptation is where the research community believes the solution lies. However, no comparative evaluation yet exists across these systems; EvolveMem and MemQ each benchmark against static baselines, not against each other.

- **AAMAS 2026 record submissions signal MAS/LLM research fusion:** 
AAMAS 2026 received 1,455 full paper submissions for the main track — by far the highest in the conference's 25-year history, approximately 50% above the previous record.
 The new Generative and Agentic AI (GAAI) track formalizes LLM-based agents as a first-class research topic within the multi-agent systems community. This convergence of two previously distinct research lineages — classical MAS (game theory, coordination, norms) and LLM agents (tool use, planning, memory) — is likely to produce methodologically rigorous evaluation frameworks that practitioner communities have been lacking, particularly for long-horizon multi-agent coordination and safety.

## Vendor Landscape

- **Anthropic:** Code with Claude London (May 19) delivered self-hosted sandboxes (public beta, Cloudflare/Daytona/Modal/Vercel providers) and MCP tunnels (research preview); Memory and Agent-Platform-on-AWS GA also confirmed. Tokyo Code with Claude scheduled June 10.
- **SAP:** Sapphire 2026 (May 14–17) — Autonomous Suite with 200+ agents / 50+ Joule Assistants, AI Agent Hub (Q3 GA, no added cost, A2A-compatible, built on LeanIX), Joule Work (outcome-driven multi-app UX), Joule Studio 2.0 (AutoGen, LangChain, LlamaIndex support, natural-language-to-agent generation), €100M partner fund; Anthropic Claude and NVIDIA OpenShell confirmed as platform partners.
- **OpenAI:** Secure MCP Tunnel GA (account-led enterprise); Codex Goal Mode GA (multi-day autonomous execution); Codex mobile app for asynchronous agent oversight; 4M weekly Codex users per OpenAI's own disclosure.
- **Google:** Items covered in the May 23 brief (Gemini Spark, ADK Python 2.0 GA, Antigravity 2.0, Managed Agents API, WebMCP origin trial Chrome 149).

## Sources

- https://fortune.com/2026/05/21/claude-code-london-anthropic-ai-software-engineering/ [Tier 1 — Independent journalism]
- https://thenewstack.io/anthropic-mcp-tunnels-sandboxes/ [Tier 2 — Tech news]
- https://www.infoq.com/news/2026/05/claude-mcp-tunnels/ [Tier 2 — Tech news]
- https://www.cio.com/article/4170465/saps-biggest-ai-bet-yet-agents-that-execute-not-just-assist.html [Tier 2 — Tech news]
- https://news.sap.com/2026/05/sap-sapphire-sap-unveils-autonomous-enterprise/ [Tier 2 — Vendor announcement]
- https://sapinsider.org/blogs/sap-sapphire-2026-autonomous-enterprise-ai-agents/ [Tier 2 — Tech news]
- https://arxiv.org/abs/2605.13941 [Tier 1 — arXiv affiliated (UNC Chapel Hill / UC Berkeley / UCSC)]
- https://arxiv.org/abs/2605.08374 [Tier 1 — arXiv affiliated (Shanghai Jiao Tong / NUS / USTC)]
- https://arxiv.org/abs/2605.16233 [Tier 1 — arXiv affiliated (Carleton University)]
- https://arxiv.org/abs/2605.12925 [Tier 1 — arXiv unaffiliated, unverified]
- https://cyprusconferences.org/aamas2026 [Tier 1 — Peer-reviewed venue]
- https://www.imperial.ac.uk/news/articles/engineering/computing/2026/papers-from-the-department-of-computing-accepted-to-international-conference-on-autonomous-agents-and-multiagent-systems/ [Tier 1 — Lab research (Imperial College)]
- https://developers.openai.com/api/docs/guides/secure-mcp-tunnels [Tier 2 — Vendor announcement]
- https://developers.openai.com/api/docs/changelog [Tier 2 — Vendor announcement]
- https://metr.org/blog/2026-05-19-frontier-risk-report/ [Tier 1 — Independent evaluation body]
- https://developers.openai.com/codex/changelog [Tier 2 — Vendor announcement]
