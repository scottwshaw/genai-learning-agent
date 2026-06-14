# GenAI Products & Platforms — Research Brief (2026-03-17)

## Key Developments

- **OpenAI launches GPT-5.4** (Mar 5): Most capable model yet with native computer-use, 1M-token context, and 75% on OSWorld-Verified (surpassing human performance at 72.4%). Ships in Pro and Thinking variants. Priced at $2.50/$15 per 1M tokens.
- **NVIDIA unveils Agent Toolkit at GTC 2026** (Mar 16): Open agent development platform comprising NemoClaw secure runtime, AI-Q deep research blueprint, and Nemotron 3 Super model. 17 launch partners including Adobe, Salesforce, SAP, ServiceNow, and CrowdStrike.
- **Anthropic slashes Opus pricing 67%** (Feb 5): Claude Opus 4.6 released at $5/$25 per 1M tokens (down from $15/$75 for Opus 4.1), with full 1M-token context at standard pricing — eliminating the long-context premium.
- **Google ships Gemini 3.1 Pro** (Feb 19): Tops 12 of 18 tracked benchmarks, including 77.1% on ARC-AGI-2 (up from 31.1%) and record 94.3% on GPQA Diamond. Priced aggressively at $2/$12 per 1M tokens.
- **Salesforce launches Agentforce 360 for AWS** (early 2026): Co-built with AWS, runs on Bedrock with Claude and Nova models, available exclusively in AWS Marketplace. MCP and A2A interop in pilot.

## Notable Papers / Models / Tools

| Item | Date | Source | Summary |
|------|------|--------|---------|
| GPT-5.4 | Mar 5 | [OpenAI](https://openai.com/index/introducing-gpt-5-4/) | First GPT with native computer-use; 1M context; 83% on GDPval; 33% fewer hallucinations vs GPT-5.2 |
| Gemini 3.1 Pro | Feb 19 | [Google DeepMind](https://deepmind.google/models/model-cards/gemini-3-1-pro/) | 2x reasoning boost over Gemini 3 Pro; 77.1% ARC-AGI-2; 2887 Elo LiveCodeBench Pro; 1M context / 64K output |
| Claude Opus 4.6 | Feb 5 | [Anthropic](https://releasebot.io/updates/anthropic) | 67% price cut; full 1M context at standard pricing; improved CoT transparency for safety |
| Claude Sonnet 4.6 | Feb 17 | Anthropic | $3/$15 per 1M tokens; 1M context GA |
| NVIDIA NemoClaw | Mar 16 | [NVIDIA](https://nvidianews.nvidia.com/news/ai-agents) | Open-source secure agent runtime with sandboxing, least-privilege access, and privacy router |
| NVIDIA AI-Q Blueprint | Mar 16 | NVIDIA | Enterprise deep-research agent blueprint; #1 on Deep Research Bench I and II; distributed via LangChain |
| Nemotron 3 Super | Mar 16 | NVIDIA | Open model; part of broader Nemotron family (Ultra, Omni, VoiceChat coming) |
| GPT-5.3 Codex | Feb 5 | OpenAI | Agentic coding model; $2/$10 per 1M tokens; 25% faster than GPT-5.2 |
| Agentforce 360 for AWS | Early 2026 | [Salesforce](https://www.salesforce.com/news/stories/agentforce-360-for-aws-announcement/) | Salesforce agents on AWS infra via Bedrock; MCP/A2A interop; multi-model support |
| Microsoft 365 E7 | GA May 1 | [Microsoft](https://learn.microsoft.com/en-us/partner-center/announcements/2026-march) | "Human-led, agent-operated enterprise" suite; includes Microsoft Agent 365 |

## Technical Deep-Dive

### GPT-5.4: Native Computer Use and Tool Search

GPT-5.4's most technically significant advance is its native computer-use capability — the first general-purpose OpenAI model to interact directly with desktop software through screenshots, mouse commands, and keyboard inputs. On OSWorld-Verified, which measures end-to-end desktop task completion, GPT-5.4 achieves 75.0% success rate, leaping from GPT-5.2's 47.3% and, notably, exceeding human performance at 72.4%. This is accomplished through a dual approach: the model can both write code to operate computers via libraries like Playwright (structured automation) and issue raw mouse/keyboard commands in response to screenshots (visual grounding), selecting whichever modality fits the task.

The model also introduces "Tool Search," an internal retrieval mechanism that dynamically selects relevant tool definitions rather than stuffing all available tools into every prompt. In internal testing, this reduced token usage by 47% on tool-heavy workflows while preserving KV-cache hits, making agentic workflows substantially faster and cheaper. Combined with the 1M-token context window (922K input / 128K output), this makes GPT-5.4 particularly suited to long-running agentic tasks that involve many tool calls across extended sessions.

On the reliability front, GPT-5.4 produces individual claims that are 33% less likely to be false compared to GPT-5.2, and full responses are 18% less likely to contain any errors. OpenAI also highlights a safety property: the model's ability to strategically control its chain-of-thought is low, meaning it cannot easily hide reasoning — a desirable property for alignment monitoring. The model ships in three tiers: standard GPT-5.4 ($2.50/$15), GPT-5.4 Pro ($30/$180) for maximum capability, and a Thinking variant with extended reasoning.

## Implications & Trends

- **The pricing war has reached a new phase.** Anthropic's 67% Opus price cut, Google's $2/$12 frontier pricing, and OpenAI's competitive GPT-5.4 tiers signal that frontier-model pricing is converging toward commodity levels. The simultaneous elimination of long-context premiums by multiple providers suggests context length is no longer a differentiator — it's table stakes.
- **Agents are the new platform battle.** NVIDIA's Agent Toolkit (with 17 enterprise partners), Salesforce's Agentforce 360, Microsoft's Agent 365, and Zoom's agentic platform all launched within weeks of each other. The competitive axis has shifted from "best model" to "best agent infrastructure" — runtime security (NemoClaw), interoperability (MCP/A2A), and enterprise governance are the new differentiators.
- **Computer use is crossing the human-performance threshold.** GPT-5.4 surpassing human baselines on OSWorld-Verified is a milestone for autonomous desktop agents. Combined with NVIDIA's NemoClaw sandboxing and least-privilege controls, the stack for deploying computer-use agents in enterprise settings is materializing rapidly — expect production deployments in regulated industries within months.

## Sources

- [Introducing GPT-5.4 — OpenAI](https://openai.com/index/introducing-gpt-5-4/)
- [OpenAI launches GPT-5.4 with Pro and Thinking versions — TechCrunch](https://techcrunch.com/2026/03/05/openai-launches-gpt-5-4-with-pro-and-thinking-versions/)
- [OpenAI launches GPT-5.4, its most powerful model — Fortune](https://fortune.com/2026/03/05/openai-new-model-gpt5-4-enterprise-agentic-anthropic/)
- [GPT-5.4 sets new records on professional benchmarks — The Next Web](https://thenextweb.com/news/openai-gpt-54-launch-computer-use-benchmarks)
- [GPT-5.4 Intelligence & Performance Analysis — Artificial Analysis](https://artificialanalysis.ai/models/gpt-5-4)
- [Gemini 3.1 Pro Model Card — Google DeepMind](https://deepmind.google/models/model-cards/gemini-3-1-pro/)
- [Gemini 3.1 Pro Benchmarks, Pricing & Guide — DigitalApplied](https://www.digitalapplied.com/blog/google-gemini-3-1-pro-benchmarks-pricing-guide)
- [Anthropic Just Killed the Long-Context Premium — Medium](https://medium.com/@KlarBrief/anthropic-just-killed-the-long-context-premium-and-the-pricing-war-for-ai-infrastructure-got-real-dacb1c1b44b5)
- [Anthropic Release Notes March 2026 — Releasebot](https://releasebot.io/updates/anthropic)
- [NVIDIA Ignites Next Industrial Revolution — NVIDIA Newsroom](https://nvidianews.nvidia.com/news/ai-agents)
- [NVIDIA Debuts Agent Toolkit and NemoClaw — HotHardware](https://hothardware.com/news/nvidia-debuts-agent-toolkit-and-nemoclaw-at-gtc)
- [NVIDIA launches enterprise AI agent platform — VentureBeat](https://venturebeat.com/technology/nvidia-launches-enterprise-ai-agent-platform-with-adobe-salesforce-sap-among)
- [At GTC 2026, NVIDIA Stakes Its Claim on Autonomous Agent Infrastructure — Futurum Group](https://futurumgroup.com/insights/at-gtc-2026-nvidia-stakes-its-claim-on-autonomous-agent-infrastructure/)
- [Salesforce Agentforce 360 for AWS Announcement — Salesforce](https://www.salesforce.com/news/stories/agentforce-360-for-aws-announcement/)
- [Zoom expands enterprise agentic AI platform — Zoom](https://news.zoom.com/ec26-agentic-ai-platform-announcements/)
- [IBM and NVIDIA Expanded Collaboration at GTC 2026 — IBM Newsroom](https://newsroom.ibm.com/2026-03-16-ibm-and-nvidia-announce-expanded-collaboration-at-gtc-2026-to-advance-ai-for-the-enterprise)
- [Microsoft March 2026 Partner Announcements — Microsoft Learn](https://learn.microsoft.com/en-us/partner-center/announcements/2026-march)
- [LLM API Pricing Comparison 2026](https://pricepertoken.com/)
- [AI API Pricing Comparison 2026 — IntuitionLabs](https://intuitionlabs.ai/articles/ai-api-pricing-comparison-grok-gemini-openai-claude)
