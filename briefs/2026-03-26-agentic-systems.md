# Agentic Systems — Research Brief (2026-03-26)

## Key Developments

- **[The gap between agent capability and agent reliability is becoming the defining enterprise deployment risk, and a new open-source evaluation standard is trying to close it]** — On March 25, Solo.io launched `agentevals` at KubeCon EU, an OTel-native open-source project designed to evaluate non-deterministic agentic behavior end-to-end across any model or framework. Alongside it, Solo.io contributed `agentregistry` to the CNCF — a governance artefact for cataloguing and controlling deployed agents across an organisation. The significance is not Solo.io's tooling per se, but what the launch signals: the existing evaluation infrastructure built for LLMs (input-output comparison, single-turn benchmarks) is structurally inadequate for agentic loops, and the industry is now producing purpose-built alternatives. This framing is independently validated by a recent ACM Communications piece and pass^k reliability data showing agent success rates dropping from 60% on pass@1 to 25% on pass^8 — a brittleness current benchmarks largely hide. The `agentevals` project is early-stage and independently unvalidated at enterprise scale, but its OTel integration removes a key adoption barrier. (March 25, 2026 — Solo.io / GlobeNewsWire [Tier 2])

- **[MCP's own roadmap formally acknowledges it has enterprise-blocking gaps in auth, observability, and gateway behavior — validating the gap between adoption and production readiness]** — The MCP project's 2026 roadmap, published March 9 by lead maintainer David Soria Parra, explicitly frames enterprise readiness as one of four top priorities, listing audit trails, SSO-integrated auth, gateway/proxy semantics, and configuration portability as unsolved problems. Crucially, the maintainers note a dedicated Enterprise Working Group does not yet exist. This is significant because it represents the protocol's own governance acknowledging what production teams have been discovering organically: MCP at 97M monthly SDK downloads is a de-facto standard, but lacks the controls that compliance-sensitive organisations require before it can be treated as governed infrastructure. The WorkOS analysis of the roadmap observes that "most enterprise MCP deployments today cannot get through a security review" — vendor claim, not independently validated, but consistent with the pattern of MCP gateways (MintMCP, TrueFoundry) filling the gap with bolted-on auth and SOC 2 attestation. Teams should instrument for these gaps now rather than wait for the spec. (March 9, 2026 — MCP blog [Tier 1 — official project]; The New Stack [Tier 1 — independent journalism])

- **[Microsoft Foundry Agent Service reaching GA on March 16 represents the most complete production-grade agent deployment platform from any hyperscaler to date, with private networking for tool calls now a first-class enterprise control]** — The GA release ships end-to-end private networking with zero public egress extended to cover MCP servers, Azure AI Search, and data agents — meaning agentic tool calls no longer need to break out of a VNet. It also ships four authentication methods for MCP servers (key-based, Entra Agent Identity, Managed Identity, OAuth Identity Passthrough), continuous agent evaluation piped into Azure Monitor, and full multi-model flexibility (LangGraph, LangChain, LlamaIndex, or custom runtimes). The architecture is deliberately framework-agnostic — agents from different vendors can be mixed at the sub-task level. The operational importance is that the dominant blockers for enterprise agent deployment (network isolation, audit trails, identity controls for tool access) are now addressed in a GA product from a hyperscaler. Independent commentary from Redmond Magazine and Azure Weekly (Tier 2) confirms this as a material production readiness step, though real-world validation at regulated-enterprise scale is still limited. (March 16, 2026 — Microsoft Foundry Blog [Tier 2]; TechCommunity [Tier 2]; Redmond Magazine [Tier 2])

- **[LangChain's rebranding of Agent Builder to "LangSmith Fleet" and Deep Agents v0.5's async subagent support signal that the agent-operations layer is maturing beyond single-agent debugging into fleet management]** — On March 19, LangChain renamed LangSmith Agent Builder to LangSmith Fleet, framing the shift as recognising that enterprises no longer manage individual agents but fleets of specialised agents that need versioning, rollback, shared prompt libraries, and centralised monitoring. Deep Agents v0.5 (March 24) added async subagents — non-blocking background tasks that allow a parent agent to continue interacting with the user while subagents work concurrently. The same week, LangChain announced an NVIDIA integration combining LangGraph/Deep Agents with NVIDIA Dynamo and OpenShell sandboxing (March 16). LangSmith has processed over 15 billion traces and 100 trillion tokens across 300+ enterprise customers, giving these product moves meaningful deployment signal. The "fleet" framing is notable because it implies governance requirements (versioning, rollback, centralised oversight) that point toward the same AgentOps category discussed in the March 17 MLOps brief — now materialising in shipping tooling rather than conceptual frameworks. (March 16–24, 2026 — LangChain blog/changelog [Tier 2 — vendor announcement])

## Notable Papers / Models / Tools

| Item | Date | Source | Summary |
|------|------|--------|---------|
| Solo.io `agentevals` + `agentregistry` → CNCF | Mar 25, 2026 | [GlobeNewsWire](https://itbusinessnet.com/2026/03/solo-io-introduces-the-agentevals-open-source-project-to-bridge-the-production-reliability-gap-for-agentic-ai/) | OTel-native open-source agent evaluation: trajectory matching, LLM-as-judge, golden eval sets; agentregistry contributed to CNCF for agent governance |
| MCP 2026 Roadmap (official) | Mar 9, 2026 | [MCP Blog](http://blog.modelcontextprotocol.io/posts/2026-mcp-roadmap/) | Four priorities: transport scalability, agent communication, governance maturation, enterprise readiness (audit trails, SSO auth, gateway patterns) |
| Microsoft Foundry Agent Service GA | Mar 16, 2026 | [Microsoft Foundry Blog](https://devblogs.microsoft.com/foundry/foundry-agent-service-ga/) | Private VNet for MCP tool calls, multi-auth MCP support, continuous eval → Azure Monitor, multi-framework runtime (LangGraph, LlamaIndex, etc.) |
| LangSmith Fleet (formerly Agent Builder) | Mar 19, 2026 | [LangChain Changelog](https://changelog.langchain.com/) | Fleet management for multiple agents: versioning, rollback, shared prompt libraries, centralised monitoring |
| Deep Agents v0.5.0 | Mar 24, 2026 | [LangChain Changelog](https://docs.langchain.com/oss/python/releases/changelog) | Async subagents (non-blocking background tasks), multi-modal file support (PDF, audio, video), error propagation improvements |
| LangChain × NVIDIA Enterprise Agentic Platform | Mar 16, 2026 | [LangChain Blog](https://blog.langchain.com/nvidia-enterprise/) | LangGraph + Deep Agents + NVIDIA Dynamo + AI-Q Blueprint; NVIDIA OpenShell secure sandboxing; Nemotron Coalition membership |
| AWS AgentCore Policy (GA) | Mar 3, 2026 | [AWS Blog](https://aws.amazon.com/blogs/aws/amazon-bedrock-agentcore-adds-quality-evaluations-and-policy-controls-for-deploying-trusted-ai-agents/) | Fine-grained centralized policy for agent-tool interactions, operating outside agent code; episodic memory (learns from prior interactions); GA on March 3 |
| Microsoft Agent Framework RC3 (→ GA ~end-March) | Ongoing Mar 2026 | [GitHub](https://github.com/microsoft/agent-framework/releases) | RC3 shipped; GA expected end of March per maintainer GitHub discussion; successor to AutoGen + Semantic Kernel |
| MCP Dev Summit North America scheduled | Apr 2–3, 2026 | [Linux Foundation](https://www.linuxfoundation.org/press/linux-foundation-launches-the-agent2agent-protocol-project-to-enable-secure-intelligent-communication-between-ai-agents) | First major MCP community summit; signals protocol governance maturing toward standards body participation |

## Technical Deep-Dive

### MCP's Enterprise Readiness Gap: What the Protocol Itself Admits It Cannot Yet Do

The MCP 2026 roadmap, published March 9 by lead maintainer David Soria Parra, is the most operationally useful document of this cycle for teams responsible for governing agentic AI in production. Its significance is not in what it promises, but in what it formally acknowledges the protocol cannot yet do.


Enterprises deploying MCP at scale are running into a predictable set of problems: audit trails, SSO-integrated auth, gateway behavior, and configuration portability — and the roadmap notes this is the least defined of the four priorities, intentionally.
 The four problem statements listed are worth treating as a checklist for production readiness:

**Audit trails and observability.** 
The roadmap calls for end-to-end visibility into what a client requested and what a server did, in a form enterprises can feed into their existing logging and compliance pipelines.
 Today, 
teams building on MCP are stitching together custom logging, bolting on their own trace identifiers, and trying to reconstruct request chains after the fact — workable for prototypes, but falling apart during incident reviews or compliance audits.


**Enterprise-managed authentication.** 
The roadmap calls for paved paths away from static client secrets and toward SSO-integrated flows (Cross-App Access), so IT can manage MCP access the same way they manage everything else.
 The practical consequence: 
if an IT administrator cannot manage MCP server access from the same console where they manage everything else, adoption stalls at the security review.


**Gateway and proxy patterns.** 
The roadmap identifies well-defined behavior when a client routes through an intermediary as unsolved — including authorization propagation, session semantics, and what the gateway is allowed to see.
 This matters because most enterprise MCP deployments are not direct client-to-server connections. They route through API gateways, proxies, or service meshes — and none of these have defined MCP semantics today.

**Configuration portability.** 
The roadmap identifies "a way to configure a server once and have that configuration work across different MCP clients" as a gap.
 In practice this means that the same MCP server configured for Claude Desktop may not correctly carry its configuration to a Cursor integration or a LangGraph workflow — a fragmentation problem that multiplies with every new MCP client.

What makes this roadmap unusual — and credible — is its explicit acknowledgment of uncertainty. 
A dedicated Enterprise Working Group does not yet exist. The maintainers want the people experiencing these challenges first-hand to help define the work.
 This contrasts with vendor-driven standards processes where the requirements are written by the tool vendors, not the operators.

The implication for production teams is concrete: 
the pragmatic move for teams deploying MCP today is to build for these gaps in their own architecture now — implementing structured audit logging, avoiding hard dependencies on static secrets, and architecting network topology with the assumption that gateways will eventually have well-defined MCP behavior.
 The spec will catch up, but compliance audits won't wait for the spec.

The transport gap is also being worked actively. 
Streamable HTTP unlocked a wave of production deployments, but running it at scale has surfaced a consistent set of gaps: stateful sessions fight with load balancers, horizontal scaling requires workarounds, and there is no standard way for a registry or crawler to learn what a server does without connecting to it.
 The planned fix — stateless horizontal scaling plus `.well-known` server metadata cards — mirrors what REST APIs solved with OpenAPI specs and OIDC discovery documents. The precedent suggests this is solvable, but the timeline is uncertain.

## Landscape Trends

- **The agentic protocol stack is bifurcating into tool connectivity (MCP) and agent coordination (A2A), with both now having cross-hyperscaler adoption — but enterprise governance for both remains a work in progress.** MCP's 97M monthly downloads and formal acknowledgment of enterprise gaps, combined with A2A's 150+ Linux Foundation contributors and IBM's ACP merger, confirm that the protocol layer is settling. 
Backing from AWS, Google, Microsoft, Salesforce, SAP, and 150+ other organizations under Linux Foundation governance means A2A is not going away; IBM's ACP protocol merged in, Microsoft wired it into Copilot Studio, and Amazon Bedrock AgentCore added native support.
 What is not yet settled is governance: neither protocol has standardised audit trails, scoped delegation, or enterprise auth in shipped form. The gap between protocol adoption and protocol governance is widening.

- **Cloud hyperscalers are converging on a common architecture for production agent infrastructure: framework-agnostic runtimes + managed memory + policy controls external to agent code.** Microsoft Foundry Agent Service (private VNet for MCP tools, multi-auth support), 
AWS AgentCore Policy's general availability delivers governance capabilities designed to help enterprises manage AI agent behavior and access, with policy operating outside the agent code to enable stricter security without modifying agent logic.
 Both platforms treat policy as an out-of-band control layer that wraps agent behaviour without requiring agent code changes — a pattern that enables centralised governance of agents built by different teams on different frameworks. This is a significant architectural maturation signal.

- **Agent evaluation is entering a formative period analogous to where LLM observability was in 2023 — fragmented, under-specified, but rapidly attracting tooling investment.** Solo.io's `agentevals` launch, the CNCF `agentregistry` contribution, AWS's internal agentic evaluation framework blog post, and the ACM ARF framework paper all converge on the same diagnosis: 
enterprise tooling built around deterministic software and traditional LLM evaluation doesn't translate to AI agents executing in an agentic loop — what enterprises need is an evaluation framework for defining what good agent behavior looks like, measuring against it continuously, and detecting when behavioral drifts create negative or suboptimal outcomes.
 The market is pre-consolidation; no single tool or framework dominates. Trajectory evaluation (did the agent take the right steps?) is emerging as the necessary complement to outcome evaluation (did the task succeed?).

- **The "fleet management" framing for agent operations is gaining traction as enterprises move from individual agent deployments to portfolios of specialised agents.** LangSmith Fleet's emergence (from Agent Builder), ServiceNow's AI Control Tower, and AWS AgentCore's architecture all treat agent fleets as a first-class management unit — implying lifecycle management, versioning, rollback, and cross-agent governance. This cross-brief signal connects the March 17 MLOps observation about "AI runtime infrastructure" becoming a distinct layer with the March 21 agentic brief's framework landscape analysis: the focus has shifted from "can this agent call tools" to "can I govern, version, and recover a fleet of agents across the enterprise."

- **Protocol adoption is accelerating faster than protocol security tooling, creating a near-term governance risk surface that regulated enterprises should not ignore.** 
Shadow AI discovery commonly reveals employees using Claude, ChatGPT, and Cursor with direct database access via MCP, API keys hardcoded in repositories, and multiple teams running identical MCP servers without coordination — with no visibility into what data AI agents access or when.
 With EU AI Act transparency and GPAI enforcement timelines hardening (covered in the March 25 Safety brief), the MCP governance gap has a regulatory dimension: tool invocations by agents touching personal data may require audit trails that the protocol itself does not yet produce.

## Vendor Landscape

| Vendor | Event | Date | Details |
|--------|-------|------|---------|
| Microsoft | Foundry Agent Service GA | Mar 16, 2026 | Private VNet for MCP tool calls; 4 MCP auth modes; continuous eval → Azure Monitor; multi-framework runtime; 6 new regions added |
| Microsoft | Agent Framework RC3 (→ GA ~end-March) | Mar 2026 | Third RC shipped; GA targeted end-of-month; AutoGen + Semantic Kernel successor |
| LangChain | LangSmith Fleet + NVIDIA partnership | Mar 16–19, 2026 | Agent Builder → LangSmith Fleet rebrand; NVIDIA Dynamo/OpenShell integration; 1B cumulative framework downloads; 300+ enterprise LangSmith customers |
| Solo.io | `agentevals` open source + `agentregistry` → CNCF | Mar 25, 2026 | OTel-native agent trajectory evaluation; golden eval sets; community evaluator registry; launched at KubeCon EU |
| AWS | AgentCore Policy GA + episodic memory | Mar 3, 2026 | Fine-grained policy for agent-tool interactions outside agent code; episodic memory (experience-based learning); Evaluations still in preview |

## Sources

- https://itbusinessnet.com/2026/03/solo-io-introduces-the-agentevals-open-source-project-to-bridge-the-production-reliability-gap-for-agentic-ai/ [Tier 2 — Tech news]
- http://blog.modelcontextprotocol.io/posts/2026-mcp-roadmap/ [Tier 1 — Official project / primary source]
- https://modelcontextprotocol.io/development/roadmap [Tier 1 — Official project / primary source]
- https://thenewstack.io/model-context-protocol-roadmap-2026/ [Tier 1 — Independent journalism (The New Stack)]
- https://workos.com/blog/2026-mcp-roadmap-enterprise-readiness [Tier 2 — Tech news / vendor analysis]
- https://devblogs.microsoft.com/foundry/foundry-agent-service-ga/ [Tier 2 — Vendor announcement]
- https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/building-production-ready-secure-observable-ai-agents-with-real-time-voice-with-/4501074 [Tier 2 — Vendor announcement]
- https://redmondmag.com/articles/2026/03/17/microsoft-brings-production-ready-ai-agents-at-gtc.aspx [Tier 2 — Tech news]
- https://dev.to/htekdev/azure-weekly-foundry-agent-service-hits-ga-and-the-agentic-devops-era-officially-arrives-563l [Tier 2 — Tech news]
- https://blog.langchain.com/nvidia-enterprise/ [Tier 2 — Vendor announcement]
- https://changelog.langchain.com/ [Tier 2 — Vendor changelog]
- https://docs.langchain.com/oss/python/releases/changelog [Tier 2 — Vendor changelog / GitHub]
- https://github.com/microsoft/agent-framework/discussions/4262 [Tier 2 — GitHub]
- https://github.com/microsoft/agent-framework/releases [Tier 2 — GitHub]
- https://jangwook.net/en/blog/en/microsoft-agent-framework-ga-production-strategy/ [Tier 2 — Tech news]
- https://aws.amazon.com/blogs/aws/amazon-bedrock-agentcore-adds-quality-evaluations-and-policy-controls-for-deploying-trusted-ai-agents/ [Tier 2 — Vendor announcement]
- https://awsinsider.net/blogs/awsinsider-release-radar/2026/03/amazon-bedrock-agentcore.aspx [Tier 2 — Tech news]
- https://aws.amazon.com/blogs/aws/aws-weekly-roundup-amazon-connect-health-bedrock-agentcore-policy-gameday-europe-and-more-march-9-2026/ [Tier 2 — Vendor announcement]
- https://letsdatascience.com/blog/a2a-protocol-agent-to-agent [Tier 2 — Tech news]
- https://cacm.acm.org/blogcacm/proposed-framework-evaluates-the-accuracy-of-agentic-systems/ [Tier 1 — ACM / independent technical commentary]
- https://explore.n1n.ai/blog/introducing-langsmith-fleet-enterprise-agent-management-2026-03-20 [Tier 2 — Tech news]
- https://earezki.com/ai-news/2026-03-18-azure-weekly-foundry-agent-service-hits-ga-and-the-agentic-devops-era-officially-arrives/ [Tier 2 — Tech news]
