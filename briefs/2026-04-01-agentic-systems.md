#4262 confirms GA was expected "around end of March" but hasn't shipped yet as of April 1; multiple RC versions have been released (rc3 through rc6).

4. **OpenClaw security crisis** — Ongoing from late January through March (nine CVEs in four days during March 18-21), with the "Agents of Chaos" research paper from Harvard/MIT identifying 11 failure patterns. This was covered in prior briefs partially but the March 18-21 CVE flood is new.

The most significant new developments since March 26 are:
- **LiteLLM supply chain attack** (March 24) — this is the most impactful new development, directly hitting the agent framework dependency chain
- **Google ADK Java 1.0** (March 30) — brings A2A-native enterprise Java agent framework to GA
- **Microsoft Agent Framework GA slipping past Q1** — still RC at April 1, despite "end of March" promise
- **OpenClaw CVE flood March 18-21** — new since the March 26 brief

For Key Developments, I need to check what was covered before March 26 in prior briefs:
- The March 26 Agentic Systems brief covered: Foundry Agent Service GA, MCP roadmap enterprise gaps, τ-Voice benchmark, AgentCore Policy GA
- The OpenClaw security crisis was first mentioned in the March 25 LLM Production Infrastructure brief (Opik plugin mentions it) but was not a Key Development. The March 26 brief mentioned it in passing.
- LiteLLM supply chain attack on March 24 was mentioned in the March 25 LLM Production Infrastructure brief (as a security advisory note in the ADK docs), but was not a Key Development there and is primary Agentic Systems territory due to its cascade into agent frameworks.

# Agentic Systems — Research Brief (2026-04-01)

## Key Developments

- **A supply chain attack on LiteLLM exposed credential-theft risk across nearly every Python agent framework simultaneously**
  - **What changed:** On March 24, threat actor TeamPCP compromised LiteLLM PyPI packages (v1.82.7/1.82.8), deploying a credential-stealing backdoor across frameworks including CrewAI, Mem0, DSPy, and Opik as transitive dependencies.
  - **Why it matters:** The AI agent dependency graph now represents a concentrated, credential-rich attack surface that security teams have not yet treated as critical infrastructure.
  - *(InfoQ, Trend Micro, LiteLLM Security Update — March 24–26, 2026)*

- **Google ADK reaches stable Java 1.0, embedding A2A natively and expanding the production agent ecosystem to enterprise Java shops**
  - **What changed:** Google shipped ADK for Java 1.0.0 on March 30, with native A2A protocol support, human-in-the-loop tooling, and session management backed by Vertex AI or Firestore.
  - **Why it matters:** Stable, production-grade A2A support in Java signals the agent interoperability layer is becoming accessible to enterprise technology stacks beyond Python.
  - *(Google Developers Blog, March 30, 2026)*

- **Microsoft Agent Framework missed its Q1 GA target, leaving AutoGen migration plans in limbo as RC releases accumulate**
  - **What changed:** Despite a public "end of March" GA commitment in GitHub discussions, the Microsoft Agent Framework remains at RC6 as of April 1; breaking changes continue across RC cycles.
  - **Why it matters:** Enterprises planning AutoGen or Semantic Kernel migrations cannot commit production timelines until a stable GA contract exists, delaying the consolidation wave.
  - *(Microsoft Agent Framework GitHub discussions/releases, March–April 2026)* [Tier 2 sources only]

- **Nine OpenClaw CVEs in four days (March 18–21), including a 9.9 critical, confirm that rapidly-adopted local agents are a new class of enterprise security exposure**
  - **What changed:** Nine CVEs were publicly disclosed for OpenClaw between March 18 and 21, including a privilege-escalation critical scoring 9.9 CVSS, with 156 total security advisories now on record.
  - **Why it matters:** Shadow-deployed local agents with broad system access represent a security perimeter breach that traditional endpoint and identity tools cannot detect.
  - *(OpenClawAI security blog, Dark Reading, SecurityScorecard — March 2026)*

---

## Notable Papers / Models / Tools

| Item | Date | Source | Summary |
|------|------|--------|---------|
| Google ADK Java 1.0.0 | Mar 30, 2026 | [Google Developers Blog](https://developers.googleblog.com/announcing-adk-for-java-100-building-the-future-of-ai-agents-in-java/) | First stable Java release of Google's Agent Development Kit; native A2A protocol, HITL, session management via Vertex AI / Firestore; model-agnostic |
| LiteLLM Supply Chain Attack (TeamPCP) | Mar 24, 2026 | [LiteLLM Security Update](https://docs.litellm.ai/blog/security-update-march-2026) / [InfoQ](https://www.infoq.com/news/2026/03/litellm-supply-chain-attack/) | v1.82.7/1.82.8 backdoored; credential stealer executed on Python startup via .pth file; affected CrewAI, DSPy, Mem0, Opik, and ~97M monthly download ecosystem |
| ADK Python Security Advisory (LiteLLM) | Mar 24, 2026 | [google.github.io/adk-docs](https://google.github.io/adk-docs/) | Google ADK Python issued emergency advisory for LiteLLM 1.82.7/1.82.8; users with eval/extensions extras required immediate upgrade and credential rotation |
| OpenClaw "CVE Flood" (nine CVEs, March 18–21) | Mar 18–21, 2026 | [OpenClawAI Blog](https://openclawai.io/blog/openclaw-cve-flood-nine-vulnerabilities-four-days-march-2026) | Nine CVEs in four days including 9.9 CVSS privilege escalation (CVE-2026-32048 sandbox escape); 156 total security advisories; Belgium's CCCS issued patch-immediately advisory |
| "Agents of Chaos" (arXiv preprint) | Mar 2026 | [Futurism](https://futurism.com/artificial-intelligence/openclaw-bots-security-disaster) / [Trending Topics EU](https://www.trendingtopics.eu/agents-of-chaos-study-reveals-11-critical-failure-patterns-in-openclaw-agents/) | Harvard/MIT-led red-team of OpenClaw agents identifies 11 failure categories including unauthorized data disclosure, identity spoofing, and cross-agent propagation of unsafe practices — *unaffiliated preprint, unverified* |
| Microsoft Agent Framework RC6 (GA pending) | Mar–Apr 2026 | [GitHub microsoft/agent-framework](https://github.com/microsoft/agent-framework/releases) | Sixth release candidate; breaking API changes continue (AgentExecutor context mode, OpenAI package extraction); GA date unconfirmed after missing end-of-March target |
| MCP Tool Annotations SEP Review | Mar–Apr 2026 | [MCP Blog](https://blog.modelcontextprotocol.io/) | Five independent SEPs proposing new tool annotations filed; blog post formalizes framework for evaluating risk-facing annotations; governance throughput improvement targeted |
| "Don't Let the Claw Grip Your Hand" (arXiv 2603.10387) | Mar 2026 | [arXiv 2603.10387](https://arxiv.org/html/2603.10387v1) | Two-phase security analysis of OpenClaw: 47 adversarial scenarios across 6 attack categories; baseline defense rate of 17%; HITL layer raises defense to 91.5% — *unaffiliated preprint, unverified* |

---

## Technical Deep-Dive

### LiteLLM Supply Chain Attack: How a Single PyPI Compromise Became a Risk Event for the Entire Agent Framework Ecosystem

The March 24 LiteLLM supply chain compromise is the most operationally significant security event in the AI agent ecosystem to date, and its architecture reveals a structural vulnerability that extends well beyond a single package.


On March 24, litellm — described as "the Python package that powers nearly every major AI agent framework" — was hit by a supply chain attack when two malicious versions (1.82.7 and 1.82.8) were published to PyPI after an attacker compromised the maintainer's publishing credentials. With 95 million downloads per month and direct dependencies from CrewAI, Browser-Use, Opik, DSPy, Mem0, Instructor, Guardrails, Agno, and Camel-AI, the blast radius was enormous.


The attack was the third in a coordinated multi-week campaign by the threat actor group TeamPCP. 
TeamPCP is behind a coordinated supply chain campaign that targeted Aqua Security's Trivy scanner (March 19), then Checkmarx's AST GitHub Actions (March 21), then LiteLLM (March 24). Their technique involves spoofing commits from legitimate maintainers, deploying encrypted credential stealers, and using harvested CI/CD credentials to attack downstream targets.


The attack mechanics exploited two separate injection vectors. 
Version 1.82.8 added a .pth file (litellm_init.pth) to the package, which executes automatically on any Python startup — no import needed. Python's site module automatically processes .pth files in site-packages every time the interpreter starts. Simply having the package installed means every python, pytest, or pip install command in that environment triggers the payload. No explicit import statement required.


The discovery vector is particularly instructive for enterprise teams. 
According to one account, all it took for a system to be compromised was launching a local MCP server through Cursor. This triggered the download of the latest LiteLLM package, which happened to have been compromised just minutes earlier.
 The victim never explicitly installed LiteLLM; it was pulled in as a transitive dependency by an MCP plugin in an AI coding tool. 
LiteLLM is everywhere — with 95 million monthly downloads and integrations across virtually every major AI agent framework, MCP server, and LLM orchestration tool. If you're working with AI, there's a good chance it's somewhere in your dependency tree, even if you never installed it directly.


The credential harvest was comprehensive. 
As Andrej Karpathy noted, the malware was capable of exfiltrating SSL and SSH keys, cloud provider credentials, Kubernetes configurations, Git credentials, API keys, shell history, and crypto wallets.
 The highest-risk targets are CI/CD pipelines, which typically hold org-wide API tokens and deployment keys and run unpinned pip installs on every build.

For enterprise AI teams, the incident crystallizes a previously theoretical risk into a confirmed attack pattern. Agent frameworks are uniquely attractive targets because they aggregate high-privilege credentials (LLM API keys, cloud IAM tokens, database credentials) alongside broad execution authority (shell access, file system operations, MCP tool calls). 
The productivity gains from AI tooling are real and massive. But the ecosystem around them — the package registries, the transitive dependency chains, the MCP servers, the agent frameworks — is a target-rich environment where a single compromised package can cascade into thousands of affected systems, each loaded with API keys and cloud credentials. The question isn't whether to adopt AI tooling; it's whether your security posture is ready for the reality that every library in your AI stack is a potential attack vector.


The immediate remediation is pinning. 
In the post-incident audit, repos using poetry.lock or uv.lock were completely protected — the lockfile pinned litellm to a safe version regardless of what was on PyPI. Repos doing bare pip install were vulnerable.
 For longer-term supply chain hygiene, the incident argues for treating AI framework dependencies with the same lock-file discipline applied to production application dependencies, which remains uncommon in the AI development ecosystem.

---

## Landscape Trends

- **The AI agent dependency graph is the new attack surface, and it is not treated like one.** The LiteLLM compromise demonstrates that the shared dependency layer underneath agent frameworks — LiteLLM, LangChain, MCP SDKs — holds credentials and execution authority that would be tightly controlled in any traditional production system. The same ecosystem behaviors that make agent tooling productive (easy transitive dependencies, rapid package updates, MCP server auto-installation) are precisely what made the TeamPCP campaign effective. Regulated enterprises must now treat AI framework dependency pinning as a security control, not a developer convenience.

- **A2A protocol adoption is accelerating in the enterprise Java and polyglot ecosystem, shifting interoperability from aspiration to buildable reality.** 
ADK for Java now natively supports the official Agent2Agent (A2A) protocol, using the official A2A Java SDK Client. Developers can resolve an AgentCard from a remote endpoint and wrap it in a RemoteA2AAgent, which acts exactly like a local agent and streams events natively back to the Runner.
 Combined with A2A's 150+ supporting organizations and Linux Foundation governance (covered in the March 26 brief), this represents the first time enterprise Java developers have a stable, GA-quality on-ramp to the A2A ecosystem — lowering the entry barrier for the large installed base of Java enterprise platforms.

- **The Microsoft Agent Framework GA slip reveals a broader pattern: platform consolidation in agent frameworks is lagging its announced timeline.** The "end of Q1 2026" GA target for the AutoGen + Semantic Kernel successor has not been met. 
As stated in GitHub discussions, GA was expected "around end of March," with releases happening "when we have meaningful items ready." Even as core packages reach GA, some packages will continue in preview/beta until their abstractions are stable.
 This means enterprises planning production AutoGen migrations must continue deferring hard commitments, and the promised single-SDK consolidation is not yet available for production use.

- **The OpenClaw security crisis is escalating into a governance pattern that will recur with any rapidly-adopted local agent platform.** 
The four-day CVE flood is not an anomaly — it is what happens when a project grows from enthusiast tool to infrastructure faster than its security surface can mature.
 With 300,000+ GitHub stars and integration into developer laptops and potentially corporate CI/CD pipelines, OpenClaw's security trajectory mirrors what happened with early container runtimes and early npm packages. The "Agents of Chaos" research and the arXiv security analysis (2603.10387) together show that the failure modes are architectural — they stem from agents having broad system access without formal permission boundaries, not from fixable individual CVEs. Enterprise security teams should treat any locally-deployed agent with shell and file system access as infrastructure-grade risk, requiring the same controls as production servers.

- **MCP's governance maturation is becoming operationally urgent as production adoption outpaces protocol standardization.** The MCP blog's post on tool annotations — noting five independent SEPs filed by the community in response to "sharper collective understanding of where risk actually lives in agentic workflows" — is an early signal that production deployments are surfacing risk patterns the protocol did not originally anticipate. 
Enterprises are deploying MCP and running into a predictable set of problems: audit trails, SSO-integrated auth, gateway behavior, and configuration portability.
 Until the Enterprise Working Group delivers formal specs (currently pre-RFC), teams building production MCP deployments must compensate architecturally — a point the March 26 brief identified and which remains unresolved.

---

## Vendor Landscape

| Vendor | Event | Date | Details |
|--------|-------|------|---------|
| Google | ADK Java 1.0.0 GA | Mar 30, 2026 | First stable Java release; native A2A, HITL, multi-session management; Vertex AI and Firestore session backends; model-agnostic |
| LiteLLM / BerriAI | Supply chain compromise; v1.83.0 patched release | Mar 24–25, 2026 | Malicious v1.82.7/1.82.8 quarantined in ~40 min; Mandiant engaged for IR; new CI/CD pipeline with stronger security gates; entire PyPI package briefly quarantined |
| Microsoft | Agent Framework still at RC6; GA slipped past Q1 | Mar–Apr 2026 | Sixth release candidate shipped; breaking API changes in core, OpenAI provider extraction; no GA announcement as of April 1 |
| OpenClaw / Edgerunner AI | Nine CVEs disclosed March 18–21; WarClaw defense-sector agent launched March 2026 | Mar 2026 | OpenClaw continues rapid CVE cycle; Edgerunner AI (veteran-founded) launched military-specific WarClaw agent citing safety concerns with frontier-model agents in defense contexts |
| Google | MCP Tool Annotations governance post | Mar–Apr 2026 | MCP blog post establishes framework for evaluating risk-facing annotations; five community SEPs under review |

---

## Sources

- https://developers.googleblog.com/announcing-adk-for-java-100-building-the-future-of-ai-agents-in-java/ [Tier 1 — Lab research (Google)]
- https://google.github.io/adk-docs/ [Tier 1 — Lab research (Google)]
- https://github.com/google/adk-java [Tier 2 — GitHub]
- https://www.heise.de/en/news/ADK-1-0-for-Java-released-Google-expands-framework-for-AI-agents-11241422.html [Tier 1 — Independent journalism (Heise)]
- https://docs.litellm.ai/blog/security-update-march-2026 [Tier 2 — Vendor announcement (LiteLLM/BerriAI)]
- https://www.infoq.com/news/2026/03/litellm-supply-chain-attack/ [Tier 1 — Independent journalism (InfoQ)]
- https://www.trendmicro.com/en_us/research/26/c/inside-litellm-supply-chain-compromise.html [Tier 1 — Independent technical research (Trend Micro)]
- https://www.trendmicro.com/en_us/research/26/c/teampcp-telnyx-attack-marks-a-shift-in-tactics.html [Tier 1 — Independent technical research (Trend Micro)]
- https://www.armosec.io/blog/litellm-supply-chain-attack-backdoor-analysis/ [Tier 2 — Tech news (ARMO)]
- https://futuresearch.ai/blog/litellm-pypi-supply-chain-attack/ [Tier 2 — Tech news (FutureSearch)]
- https://www.comet.com/site/blog/litellm-supply-chain-attack/ [Tier 2 — Vendor announcement (Comet/Opik)]
- https://openclawai.io/blog/openclaw-cve-flood-nine-vulnerabilities-four-days-march-2026 [Tier 2 — Tech news]
- https://www.darkreading.com/application-security/critical-openclaw-vulnerability-ai-agent-risks [Tier 1 — Independent journalism (Dark Reading)]
- https://pbxscience.com/openclaws-security-crisiseverything-you-need-to-know/ [Tier 2 — Tech news]
- https://futurism.com/artificial-intelligence/openclaw-bots-security-disaster [Tier 1 — Independent journalism (Futurism)]
- https://www.trendingtopics.eu/agents-of-chaos-study-reveals-11-critical-failure-patterns-in-openclaw-agents/ [Tier 2 — Tech news]
- https://arxiv.org/html/2603.10387v1 [Tier 1 — arXiv unaffiliated, unverified]
- https://github.com/microsoft/agent-framework/releases [Tier 2 — GitHub]
- https://github.com/microsoft/agent-framework/discussions/4262 [Tier 2 — GitHub]
- https://modelcontextprotocol.io/development/roadmap [Tier 2 — Official project roadmap]
- https://blog.modelcontextprotocol.io/ [Tier 2 — Official project blog]
- https://workos.com/blog/2026-mcp-roadmap-enterprise-readiness [Tier 2 — Tech news / analysis]
- https://thenewstack.io/model-context-protocol-roadmap-2026/ [Tier 1 — Independent journalism (The New Stack)]
- https://www.defenseone.com/technology/2026/04/startup-takes-different-approach-ai-assistants/412545/ [Tier 1 — Independent journalism (Defense One)]
- https://www.digitalapplied.com/blog/ai-agent-protocol-ecosystem-map-2026-mcp-a2a-acp-ucp [Tier 2 — Tech news]
- https://bonjoy.com/articles/what-is-mcp-model-context-protocol-enterprise-guide/ [Tier 2 — Tech news]
