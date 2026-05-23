# Agentic Systems — Research Brief (2026-05-23)

## Key Developments

- **Sydney study exposes systematic overstatement in five major agent benchmarks**
  - **What changed:** A University of Sydney arXiv study added an evidence-reporting layer to five benchmarks, exposing widespread false-positive success scores.
  - **Why it matters:** Teams using benchmark scores for procurement or deployment gates need artifact-level outcome evidence to make valid comparisons.
  - *(arXiv:2605.10448 — University of Sydney, May 11, 2026 — Tier 1, arXiv affiliated)*

- **Google's always-on cloud VM agent demands first-order enterprise identity governance**
  - **What changed:** Google launched Gemini Spark, a 24/7 agent on dedicated cloud VMs executing persistent background tasks via Gmail, Workspace, and MCP.
  - **Why it matters:** Always-on cloud-hosted agents elevate identity isolation and action-approval workflows to first-order enterprise governance requirements.
  - *(TechCrunch / Google Cloud Blog / The Next Web, May 19, 2026)* [Tier 2 sources only]

---

## Notable Papers / Models / Tools

| Item | Date | Source | Summary |
|------|------|--------|---------|
| MCP 2026-07-28 Release Candidate | May 21, 2026 | [MCP Blog](https://blog.modelcontextprotocol.io/posts/2026-07-28-release-candidate/) [Tier 2 — Vendor/Foundation] | Largest MCP revision since launch: stateless core (session ID header removed), Extensions framework (MCP Apps for sandboxed UIs, Tasks extension for long-running work), OAuth/OIDC-aligned authorization, formal feature lifecycle policy with 12-month deprecation window. Final spec ships July 28, 2026; 10-week SDK validation window open. |
| Google ADK Python 2.0 GA | May 19, 2026 | [ADK Docs](https://google.github.io/adk-docs/2.0/) / [Google Cloud Blog](https://cloud.google.com/blog/topics/developers-practitioners/io26-news-for-agent-developers-on-google-cloud) [Tier 2 — Vendor] | Transitions from hierarchical executor to graph-based Workflow Runtime; adds Task API for multi-turn agent-to-agent delegation; breaking changes to agent API, event model, and session schema; ADK 1.28+ can read 2.0 sessions. Apache 2.0 license. |
| Google Antigravity 2.0 + Managed Agents API | May 19, 2026 | [Google Developers Blog](https://blog.google/innovation-and-ai/technology/developers-tools/google-io-2026-developer-highlights/) [Tier 2 — Vendor] | Five-surface stack: desktop app (parallel subagents, scheduled tasks), CLI (replaces Gemini CLI), SDK, Managed Agents API (single-call provisioned agent in isolated Linux sandbox), and Enterprise Agent Platform tier. Antigravity CLI replaces Gemini CLI with migration guide published. |
| Gemini Spark (enterprise 24/7 agent) | May 19, 2026 | [TechCrunch](https://techcrunch.com/2026/05/19/google-introduces-gemini-spark-a-24-7-agentic-assistant-with-gmail-integration/) / [Google Cloud Blog](https://cloud.google.com/blog/products/ai-machine-learning/innovations-from-google-io-26-on-google-cloud) [Tier 2] | Persistent agent on dedicated cloud VMs; integrates Gmail, Workspace, SharePoint/OneDrive/ServiceNow via MCP; DLP policy enforcement through Agent Gateway; explicit approval required for high-risk actions; rolling out to Gemini Enterprise customers imminently. |
| WebMCP origin trial (Chrome 149) | May 18–19, 2026 | [Chrome for Developers](https://developer.chrome.com/docs/ai/webmcp) / [ppc.land](https://ppc.land/chrome-149-origin-trial-puts-webmcp-in-developers-hands-at-last/) [Tier 2 — Vendor] | W3C Web ML Community Group draft (co-authored with Microsoft) moves to Chrome 149 origin trial; lets websites expose structured tools (JS imperative + HTML declarative APIs) directly to browser-based AI agents; Booking.com, Shopify, Instacart, Intuit committed to implement. Currently Chrome-only with no Firefox/Safari support. |
| arXiv:2605.10448 — "Can Agent Benchmarks Support Their Scores?" | May 11, 2026 | [arXiv — University of Sydney](https://arxiv.org/abs/2605.10448) [Tier 1 — arXiv affiliated] | Adds outcome-evidence layer to ANDROIDWORLD, AGENTDOJO, APPWORLD, tau3-bench, and MiniWoB without modifying tasks; assigns Evidence Pass/Fail/Unknown labels; finds widespread cases where binary success rates overstate actual task completion; proposes evidence-supported score bounds as replacement metric. |
| arXiv:2605.08545 — "Log analysis is necessary for credible evaluation of AI agents" | May 2026 | [arXiv](https://arxiv.org/abs/2605.08545) [Tier 1 — arXiv affiliated, affiliation to be verified] | Argues that behaviors relevant to deployment are properties of trajectories, not final outcomes; shows evaluation performance is log-linear in token usage up to 50M tokens, suggesting most benchmark evaluations systematically underestimate capability; calls log analysis the only valid evaluation mechanism. |
| AAMAS 2026 (25th edition) | May 25–29, 2026 | [AAMAS 2026 — Paphos, Cyprus](https://cyprusconferences.org/aamas2026) [Tier 1 — Peer-reviewed venue] | 1,455 full paper submissions (50% more than prior record); tracks include Generative and Agentic AI (GAAI) and multi-agent coordination; papers from Imperial/Glasgow on safety-critical decentralized agent coordination accepted. |
| arXiv:2602.22953 — "General Agent Evaluation" (v2, May 2026) | May 11, 2026 (v2) | [arXiv](https://arxiv.org/abs/2602.22953) [Tier 1 — arXiv affiliated] | Updated with Open General Agent Leaderboard; finds architecture choice swings results by up to 12pp within a single model; backbone model choice dominates overall performance; top general agents are indistinguishable from specialized domain agents on 4 of 6 benchmarks; open-weight models exhibit "generality sinks." |

---

## Technical Deep-Dive

**MCP 2026-07-28 Release Candidate: Stateless Protocol Core and Extensions Framework**

The MCP 2026-07-28 release candidate, locked on May 21, represents the protocol's most significant architectural shift since launch. 
It delivers a stateless core that scales on ordinary HTTP infrastructure; a remote MCP server that previously needed sticky sessions, a shared session store, and deep packet inspection at the gateway can now run behind a plain round-robin load balancer, route traffic on an `Mcp-Method` header, and let clients cache `tools/list` responses according to the server's `ttlMs`.


The statefulness problem was fundamental. 
Streamable HTTP had unlocked a wave of production deployments, but running it at scale surfaced consistent gaps: stateful sessions fight with load balancers, horizontal scaling requires workarounds, and there was no standard way for a registry or crawler to learn what a server does without connecting to it.
 The fix is architectural: 
the `Mcp-Session-Id` header and the protocol-level session that came with it are removed; any MCP request can now land on any server instance, and the sticky routing and shared session stores that horizontal deployments previously required are no longer needed at the protocol layer.


Critically, statelessness at the protocol layer does not force statelessness in applications. 
Servers that need to carry state across calls can do what HTTP APIs have always done: mint an explicit handle from a tool and have the model pass it back as an ordinary argument on later calls. In practice, this pattern — the model threading an identifier from one tool call to the next — proves more powerful than externally managed session state hidden in transport metadata, because the model can compose handles across tools, reason about them, and hand them off between steps.


Beyond transport, the release ships two new extension primitives. 
MCP Apps (SEP-1865) lets servers ship interactive HTML interfaces that hosts render in sandboxed iframes; tools declare their UI templates ahead of time so hosts can prefetch, cache, and security-review them before anything runs, and every UI-initiated action goes through the same audit and consent path as a direct tool call.
 The Tasks extension reshapes long-running work: 
a server can answer a `tools/call` with a task handle, and the client drives it with `tasks/get`, `tasks/update`, and `tasks/cancel` — with task creation being server-directed so the client advertises the extension and the server decides when a call should run as a task.
 A formal feature lifecycle policy now governs all future changes, with at least twelve months between deprecation and earliest possible removal, and conformance tests must accompany any SEP reaching Final status. The ten-week SDK validation window before the July 28 final publication is the key near-term pressure point for enterprise MCP adopters assessing migration timelines.

---

## Landscape Trends

- **MCP's stateless-core shift is the protocol-layer answer to the enterprise agentic scaling problem.** Prior briefs (April 22, April 30) documented MCP adoption at 10,000+ servers and 164M monthly SDK downloads alongside persistent complaints about horizontal-scaling friction. 
This release gives MCP the foundation expected to grow on for a long time: a protocol that runs statelessly on commodity HTTP infrastructure, with an extensions framework where capabilities can ship on their own timeline.
 The prior-brief observation that MCP was transitioning from developer experiment to enterprise infrastructure is now resolving into a concrete technical form — but the enterprise readiness gaps (audit trails, SSO-integrated auth, gateway semantics) remain explicitly unaddressed in the spec and are deferred to a still-forming Enterprise Working Group.

- **[Agentic Systems × Enterprise GenAI Adoption]** Google's I/O 2026 stack — Gemini Spark, Antigravity 2.0, ADK 2.0, Managed Agents API — represents the first hyperscaler-native path from agent prototype to governed 24/7 production deployment within a single ecosystem. 
Google is effectively turning the consumer agent into a long-running background process hosted in Google Cloud: it does not sleep, it does not time out, it maintains context across sessions — closer to a server-side business process than any prior consumer AI product, and it demands that third-party developers rethink how their apps expose functionality to agents rather than humans.
 This raises the competitive stakes for independent agent frameworks (LangGraph, CrewAI, Mastra) that currently lack integrated governed execution runtimes backed by identity, DLP, and audit infrastructure.

- **[Agentic Systems × Safety, Assurance & Governance]** The convergence of persistent cloud-hosted agents (Gemini Spark, Anthropic Cowork, OpenAI ChatGPT Agent) with the METR Frontier Risk Report's finding that models can plausibly initiate minimal rogue deployments (surfaced in the May 21 Safety brief) creates a compounding governance gap: the same architectural pattern enabling long-horizon autonomous work — persistent VM-based execution with delegated credentials — is precisely the threat model METR evaluated. Enterprise teams adopting any 24/7 cloud-hosted agent must design identity isolation and action-approval workflows as first-order infrastructure, not post-deployment controls.

- **Agent benchmark validity is deteriorating as a gating mechanism just as production deployments scale.** The arXiv:2605.10448 evidence-reporting finding, alongside the METR time-horizon ceiling documented in the May 12 brief, means the two primary evaluation instruments enterprise teams rely on for procurement and safety decisions — benchmark scores and METR time-horizon estimates — are both structurally underspecified for the current capability frontier. 
Evaluation can no longer be reduced to an objective function and must contend with process, not just endpoints; as agentic systems are integrated into core business functions on the basis of benchmark scores, low-validity evaluations risk failed pilots, unintended consequences, and erosion of trust in AI evaluation itself.
 Teams using benchmark scores as procurement or release-gate evidence should treat those scores as directional rather than definitive until artifact-level outcome evidence is standard practice.

- **[Agentic Systems × LLM Production Infrastructure]** Google's WebMCP origin trial and ADK 2.0 Workflow Runtime both point to the same architectural signal: the gap between agent tool use and the underlying infrastructure layer is closing from both directions. WebMCP moves tool registration into the browser itself; ADK 2.0's graph-based execution and Managed Agents API move agent orchestration directly into cloud runtime. This convergence means agent framework decisions are increasingly inseparable from infrastructure vendor decisions — a dynamic that benefits hyperscalers with tightly integrated stacks and creates lock-in risk for teams that adopt managed agent execution before open standards for agent identity and audit portability are settled.

---

## Vendor Landscape

- **Google** shipped a comprehensive I/O 2026 agent stack: Antigravity 2.0 (desktop, CLI, SDK, Managed API), ADK Python 2.0 GA (graph-based Workflow Runtime, Task API), Gemini Spark (24/7 cloud VM agent), and WebMCP origin trial in Chrome 149. Enterprise pricing cut from $250 to $200/month.
- **MCP ecosystem (AAIF/Linux Foundation):** 2026-07-28 release candidate locked May 21 with stateless core and Extensions framework. Clare Liguori (AWS) and Den Delimarsky added as core/lead maintainers alongside existing lead maintainer David Soria Parra.
- **LangGraph:** v0.4 released in April with improved state persistence and HITL checkpoints. Verifiable enterprise deployments include Klarna, Uber, JPMorgan, BlackRock, and LinkedIn.
- **Mastra:** 22,300+ GitHub stars and 300,000+ weekly npm downloads as of May 2026; a TypeScript-native agent framework. No SOC 2 certification as of this date.
- **ADK for Kotlin 0.1 / ADK for Android 0.1:** Released May 21, 2026, extending Google's agent framework to Android and Kotlin backend runtimes.

---

## Sources

- https://blog.modelcontextprotocol.io/posts/2026-07-28-release-candidate/ [Tier 2 — Foundation/Vendor announcement]
- https://modelcontextprotocol.io/development/roadmap [Tier 2 — Foundation/Vendor]
- https://blog.modelcontextprotocol.io/posts/2026-mcp-roadmap/ [Tier 2 — Foundation/Vendor]
- https://google.github.io/adk-docs/2.0/ [Tier 2 — Vendor]
- https://cloud.google.com/blog/topics/developers-practitioners/io26-news-for-agent-developers-on-google-cloud [Tier 2 — Vendor]
- https://blog.google/innovation-and-ai/technology/developers-tools/google-io-2026-developer-highlights/ [Tier 2 — Vendor]
- https://blog.google/innovation-and-ai/technology/ai/google-io-2026-all-our-announcements/ [Tier 2 — Vendor]
- https://blog.google/innovation-and-ai/sundar-pichai-io-2026/ [Tier 2 — Vendor]
- https://cloud.google.com/blog/products/ai-machine-learning/innovations-from-google-io-26-on-google-cloud [Tier 2 — Vendor]
- https://github.com/google/adk-python [Tier 2 — GitHub]
- https://developers.googleblog.com/all-the-news-from-the-google-io-2026-developer-keynote/ [Tier 2 — Vendor]
- https://techcrunch.com/2026/05/19/google-introduces-gemini-spark-a-24-7-agentic-assistant-with-gmail-integration/ [Tier 2 — Tech news]
- https://techcrunch.com/2026/05/19/with-gemini-3-5-flash-google-bets-its-next-ai-wave-on-agents-not-chatbots/ [Tier 2 — Tech news]
- https://thenextweb.com/news/google-gemini-spark-agentic-assistant-gmail-io-2026 [Tier 2 — Tech news]
- https://virtualizationreview.com/articles/2026/05/19/google-io-26-fills-out-enterprise-agent-stack-with-managed-agents-adk-2,-d-,0.aspx [Tier 2 — Tech news]
- https://www.marktechpost.com/2026/05/19/google-launches-antigravity-2-0-at-i-o-2026-a-standalone-agent-first-platform-with-cli-sdk-managed-execution-and-enterprise-support/ [Tier 2 — Tech news]
- https://9to5google.com/2026/05/19/google-antigravity-agentic-developer-suite/ [Tier 2 — Tech news]
- https://developer.chrome.com/docs/ai/webmcp [Tier 2 — Vendor]
- https://ppc.land/chrome-149-origin-trial-puts-webmcp-in-developers-hands-at-last/ [Tier 2 — Tech news]
- https://arxiv.org/abs/2605.10448 [Tier 1 — arXiv affiliated, University of Sydney]
- https://arxiv.org/html/2605.10448 [Tier 1 — arXiv affiliated]
- https://arxiv.org/abs/2605.08545 [Tier 1 — arXiv affiliated, affiliation unverified]
- https://arxiv.org/abs/2602.22953 [Tier 1 — arXiv affiliated]
- https://metr.org/blog/2026-05-19-frontier-risk-report/ [Tier 1 — Independent evaluation body]
- https://datacamp.com/blog/google-i-o-2026 [Tier 2 — Tech news]
- https://www.efficientlyconnected.com/google-io-2026-gemini-spark-consumer-ai-agent/ [Tier 2 — Tech/practitioner blog]
- https://theaiinsider.tech/2026/05/20/google-i-o-2026-how-the-search-giant-is-rebuilding-itself-around-agentic-ai/ [Tier 2 — Tech news]
