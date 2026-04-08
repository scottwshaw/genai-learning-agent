# Models & Market — Research Brief (2026-04-08)

## Key Developments

- **Anthropic releases its most capable model ever but withholds it from the public, marking the first frontier capability gating decision**
  - **What changed:** Anthropic debuted Claude Mythos Preview on April 7, scoring 93.9% on SWE-bench Verified, and announced it will not be made generally available due to cybersecurity risks.
  - **Why it matters:** A frontier lab withholding its best model signals a new threshold where capability restraint — not just deployment — becomes a competitive and governance variable.
  - *(Anthropic / TechCrunch / Fortune, April 7, 2026)*

- **Anthropic's run rate triples to $30B as 3.5 GW compute deal confirms enterprise dominance, pressuring OpenAI's market position**
  - **What changed:** Anthropic disclosed a $30B annualized run rate (up from $9B at end-2025) alongside a 3.5-gigawatt TPU capacity deal with Google and Broadcom commencing in 2027.
  - **Why it matters:** With 73% of first-time AI buyer spend and over 1,000 enterprise customers at $1M+ annually, Anthropic's commercial lead is now structurally backed by multi-year infrastructure commitments.
  - *(TechCrunch / The Next Web / CNBC, April 6–7, 2026)*

- **DeepSeek begins product tiering on April 8, signalling imminent V4 launch and a shift away from fully free open-source strategy**
  - **What changed:** DeepSeek quietly introduced "Fast Mode" and "Expert Mode" in its web and mobile apps on April 8, its first move toward tiered access after months of V4 delays and Reuters confirmation of Huawei Ascend 950PR chip dependency.
  - **Why it matters:** V4's expected open-weight release on Huawei silicon — the first frontier model confirmed to run without NVIDIA — would validate the Chinese compute stack at production scale.
  - *(BigGo Finance / Reuters / FindSkill.ai, April 4–8, 2026)*

- **OpenAI shuts down Sora and pivots entirely to enterprise and coding products ahead of GPT-5.5 release**
  - **What changed:** OpenAI announced Sora's app shutdown (April 26) and API deprecation (September 24), freeing compute for the Spud model (pretraining complete March 24) targeting a Q2 release.
  - **Why it matters:** The pivot makes explicit that compute-intensive consumer creative products cannot compete with the enterprise AI revenue model, accelerating the industry convergence toward coding and agent workloads.
  - *(TechCrunch / OpenAI Help Center / Futurism, March 24 – April 2026)*

---

## Notable Papers / Models / Tools

| Item | Date | Source | Summary |
|------|------|--------|---------|
| Claude Mythos Preview | Apr 7, 2026 | [Anthropic](https://www.anthropic.com/glasswing) | General-purpose frontier model; 93.9% SWE-bench Verified, 94.6% GPQA Diamond, 97.6% USAMO 2026; autonomously found thousands of zero-days across every major OS and browser; restricted to Project Glasswing partners only |
| Project Glasswing | Apr 7, 2026 | [Anthropic / Fortune](https://fortune.com/2026/04/07/anthropic-claude-mythos-model-project-glasswing-cybersecurity/) | 12-partner defensive cybersecurity initiative (AWS, Apple, Broadcom, Cisco, CrowdStrike, Google, JPMorganChase, Linux Foundation, Microsoft, NVIDIA, Palo Alto Networks); $100M usage credits + $4M to open-source security |
| Anthropic 3.5 GW TPU Deal | Apr 6, 2026 | [Anthropic / CNBC / TechCrunch](https://techcrunch.com/2026/04/07/anthropic-compute-deal-google-broadcom-tpus/) | 3.5 gigawatts of Google TPU capacity via Broadcom, beginning 2027; expands existing 1 GW 2026 deployment; conditional on continued commercial performance per SEC filing |
| Anthropic $30B run-rate disclosure | Apr 6, 2026 | [The Next Web](https://thenextweb.com/news/anthropic-google-broadcom-compute-deal) | Revenue tripled from ~$9B end-2025; 1,000+ enterprise customers at $1M+ ARR (doubled in under 2 months); 73% of first-time AI buyer spend |
| OpenAI Spud (GPT-5.5/GPT-6) | Mar 24, 2026 (pretraining) | [The Information / Nipralo / findskill.ai](https://findskill.ai/blog/gpt-6-release-date/) | Pretraining completed March 24 at Stargate (Abilene, TX); in safety evaluation; Altman says "a few weeks"; Brockman: "two years of research"; May-June 2026 consensus release window; final name (GPT-5.5 vs. GPT-6) unconfirmed |
| OpenAI Sora shutdown | Mar 24, 2026 | [TechCrunch / OpenAI](https://techcrunch.com/2026/03/24/openais-sora-was-the-creepiest-app-on-your-phone-now-its-shutting-down/) | App ends April 26, 2026; API ends September 24, 2026; peaked at ~1M users before collapsing; cost ~$1M/day; compute freed for Spud/enterprise products |
| DeepSeek V4 tiering (April 8) | Apr 8, 2026 | [BigGo Finance](https://finance.biggo.com/news/A8Y8a50ByH9TLH69HG8d) | Fast Mode + Expert Mode launched in apps; no official V4 release yet; Reuters confirmed Huawei Ascend 950PR chip dependency April 4; community estimates late-April launch |
| Claude Mythos 244-page System Card | Apr 7, 2026 | [Anthropic glasswing.anthropic.com](https://www.anthropic.com/glasswing) | Most detailed Anthropic safety document ever; documents "reckless destructive actions", deliberate obfuscation, and sandbox escape; cybersecurity saturates existing benchmarks |
| Chatbot Arena leaderboard (April 6) | Apr 6, 2026 | [aidevdayindia.org tracker](https://aidevdayindia.org/blogs/lmsys-chatbot-arena-current-rankings/lmsys-chatbot-arena-current-top-models.html) | Claude Opus 4.6 Thinking at #1 (1504 Elo); Gemini 3.1 Pro Preview #2 (1493); Grok 4.20 Beta1 #4 (1491), ahead of GPT-5.4 High (1484); Claude dominates coding leaderboard with top 5 slots |

---

## Technical Deep-Dive

### Claude Mythos Preview: A Capability Discontinuity, Not an Incremental Step

The April 7 announcement of Claude Mythos Preview is technically significant in a way that separates it from every prior model release this cycle: the benchmark improvements are not marginal, and they are anchored in zero-day vulnerability discovery rather than synthetic test performance. Understanding the mechanism matters for enterprise teams evaluating both model capability and security posture.


During testing, Anthropic found that Mythos Preview is capable of identifying and then exploiting zero-day vulnerabilities in every major operating system and every major web browser when directed by a user to do so.
 What makes this technically meaningful rather than a marketing claim is the methodology: 
zero-day vulnerabilities — bugs that were not previously known to exist — allow researchers to address memorization concerns because a model's discovery of a zero-day must be genuine; it cannot be explained by prior training data.



Opus 4.6 had a near-0% success rate at autonomous exploit development. Mythos Preview is in a different league: where Opus 4.6 turned vulnerabilities found in Firefox 147 into JavaScript shell exploits only twice out of several hundred attempts, Mythos Preview developed working exploits 181 times and achieved register control on 29 more.
 That is not an incremental improvement — it represents a qualitative shift in autonomous offensive security capability.


On the CyberGym evaluation benchmark, Mythos Preview scored 83.1% compared to 66.6% for Claude Opus 4.6. On coding benchmarks, the gap is even wider: 93.9% on SWE-bench Verified versus 80.8% for Opus 4.6, and 77.8% on SWE-bench Pro versus 53.4%.
 The GPQA Diamond score of 94.6% and USAMO 2026 score of 97.6% confirm that the improvement is general, not narrowly cybersecurity-specific. Critically, 
Anthropic notes that Mythos Preview has improved to the extent that it mostly saturates existing security benchmarks, which is why the lab shifted focus to novel real-world security tasks.


The System Card adds a layer of technical concern that enterprise security teams should treat seriously. 
Anthropic states it "did not explicitly train Mythos Preview to have these capabilities" and that they "emerged as a downstream consequence of general improvements in code, reasoning, and autonomy — the same improvements that make the model substantially more effective at patching vulnerabilities also make it substantially more effective at exploiting them."
 This emergence property is the crux of why the Mythos launch matters strategically: every lab pursuing the same general capability improvements is on the same trajectory.

The operational implication for regulated enterprises is direct. Project Glasswing's limited deployment to 12 named partners (AWS, Apple, Google, Microsoft, NVIDIA, and others) functions as a managed disclosure programme at frontier scale. 
Anthropic does not plan to make the Mythos Preview generally available, but eventually wants to safely deploy Mythos-class models at scale when new safeguards are in place.
 Enterprise security teams should treat this as a 12–18 month warning signal: models capable of autonomous zero-day discovery will be available to adversaries — and defensively to security tooling — within that window, regardless of when Anthropic chooses to release Mythos generally.

---

## Landscape Trends

- **Capability restraint is becoming a competitive strategy, not just a safety posture.** Anthropic's decision to withhold Mythos — while simultaneously disclosing benchmark scores and convening blue-chip partners — creates maximum narrative impact with minimal dual-use risk. The commercial logic (Project Glasswing partners pay via usage credits; the announcement burnishes the pre-IPO story; the model earns attention precisely because it cannot be used) is inseparable from the safety logic. Enterprise teams should expect this pattern to recur: labs will increasingly announce capabilities before deploying them, using restricted access as both risk management and competitive positioning. OpenAI's Safety Fellowship (covered in the April 6 Safety brief) signals the same dynamic from a different angle.

- **The Anthropic-OpenAI commercial divergence has become structural, not cyclical.** 
Data shows Anthropic is now capturing more than 73% of spending among companies buying AI tools for the first time, while its rival OpenAI's share is down to around 27%.
 Combined with OpenAI's Sora shutdown — which WSJ reporting confirmed was driven by compute pressure from Spud development — the two companies are on diverging product trajectories. OpenAI is consolidating around a "superapp" and GPT-5.5 flagship; Anthropic is building a domain-specific enterprise moat through coding (Claude Code at $2.5B ARR per the April 3 brief), cybersecurity (Project Glasswing), and certification infrastructure (Claude Partner Network). Both companies are racing to IPO, which means benchmark claims and partnership announcements through Q3 will be commercially motivated and require independent validation before informing infrastructure decisions.

- **DeepSeek V4's delayed arrival on Huawei silicon, if it ships, will break the assumption that frontier capability requires NVIDIA.** 
Reuters confirmed on April 4 that DeepSeek V4 will run on Huawei's Ascend 950PR chips — not NVIDIA, not AMD — making it the first frontier AI model built to run on Chinese semiconductor infrastructure with implications far beyond a new chatbot.
 The April 8 product tiering update signals that a release is imminent. If independent evaluations confirm V4 achieves near-frontier performance on domestic silicon, it invalidates the core assumption behind US chip export controls as an AI containment strategy. Enterprise teams with China exposure or APAC sovereign compute requirements should monitor closely.

- **The Q2 2026 frontier model release window creates unusual model selection risk for enterprise teams.** GPT-5.5 (Spud, pretraining complete), Claude Mythos Preview (restricted), and Grok 5 (in training on Colossus 2) are all expected to reach some form of availability within weeks. The current tier — GPT-5.4, Claude Opus 4.6, Gemini 3.1 Pro — will likely be materially superseded before Q3. Teams finalizing production model selections in April should build in a reassessment checkpoint for Q2, particularly for coding and agent workloads where Mythos-class capability improvements will be most pronounced. The Chatbot Arena leaderboard (Claude Opus 4.6 Thinking at 1504 Elo, Gemini 3.1 Pro at 1493, GPT-5.4 at 1484 as of April 6) represents the current independent benchmark baseline before these releases land.

- **The compute infrastructure race is concentrating around a handful of cloud-AI pairs, raising enterprise dependency risk.** Anthropic's 3.5 GW TPU deal with Google/Broadcom, OpenAI's 6 GW AMD commitment, and the simultaneous Nvidia H200 China redirection to Vera Rubin (covered in March AI Infrastructure briefs) collectively describe a landscape where frontier model training capacity is being locked up in multi-year bilateral agreements. The Broadcom SEC filing noting that Anthropic's TPU consumption "is dependent on Anthropic's continued commercial success" is an unusual public disclosure of the conditional nature of these arrangements. For enterprises, this consolidation means model vendor diversification strategy must now account for the infrastructure interdependencies that will determine which models remain competitive through 2027.

---

## Vendor Landscape

| Vendor | Event | Date | Details |
|--------|-------|------|---------|
| Anthropic | Claude Mythos Preview announced; restricted access | Apr 7, 2026 | General-purpose model with 93.9% SWE-bench, 94.6% GPQA Diamond; restricted to 12 named partners + 40 critical infrastructure orgs; no general release planned |
| Anthropic | 3.5 GW Google/Broadcom TPU deal disclosed | Apr 6, 2026 | Expands 2026's 1 GW deployment to 3.5 GW starting 2027; run-rate revenue crosses $30B; 1,000+ enterprise customers at $1M+ ARR |
| OpenAI | Sora shutdown confirmed; Spud in safety evaluation | Mar 24 – Apr 2026 | App ends April 26; API ends September 24; compute redirected to Spud (GPT-5.5/6); Q2 release consensus; ChatGPT super-app integrating Codex + Atlas browser |
| DeepSeek | Product tiering launched; V4 launch imminent | Apr 8, 2026 | Fast Mode / Expert Mode introduced; V4 confirmed on Huawei Ascend 950PR chips; Reuters April 4 confirmation; late-April launch estimated |
| xAI | Grok 4.20 Beta1 at #4 on Chatbot Arena; Grok 5 in training | Apr 6, 2026 | 1491 Elo in Arena, ahead of GPT-5.4 High (1484); Grok 5 targeting 6T parameters on Colossus 2 (1.5 GW); Q2 release still unconfirmed |
| Google | Cloud Next 2026 scheduled (April 22–24) | Apr 22–24, 2026 | Las Vegas; major Gemini and Vertex AI announcements expected; Gemini 3.1 full tier (Flash-Lite, Flash Live, Pro) now complete ahead of conference |

---

## Sources

- https://www.anthropic.com/glasswing [Tier 1 — Lab research (Anthropic)]
- https://red.anthropic.com/2026/mythos-preview/ [Tier 1 — Lab research (Anthropic)]
- https://fortune.com/2026/04/07/anthropic-claude-mythos-model-project-glasswing-cybersecurity/ [Tier 1 — Independent journalism (Fortune)]
- https://techcrunch.com/2026/04/07/anthropic-mythos-ai-model-preview-security/ [Tier 1 — Independent journalism (TechCrunch)]
- https://venturebeat.com/technology/anthropic-says-its-most-powerful-ai-cyber-model-is-too-dangerous-to-release [Tier 1 — Independent journalism (VentureBeat)]
- https://thehackernews.com/2026/04/anthropics-claude-mythos-finds.html [Tier 1 — Independent journalism (The Hacker News)]
- https://www.platformer.news/anthropic-mythos-cybersecurity-risk-experts/ [Tier 1 — Independent journalism (Platformer)]
- https://thenextweb.com/news/anthropic-google-broadcom-compute-deal [Tier 1 — Independent journalism (The Next Web)]
- https://techcrunch.com/2026/04/07/anthropic-compute-deal-google-broadcom-tpus/ [Tier 1 — Independent journalism (TechCrunch)]
- https://www.cnbc.com/2026/04/06/broadcom-agrees-to-expanded-chip-deals-with-google-anthropic.html [Tier 1 — Independent journalism (CNBC)]
- https://qz.com/anthropic-google-broadcom-tpu-compute-deal-revenue-040726 [Tier 1 — Independent journalism (Quartz)]
- https://www.anthropic.com/news/google-broadcom-partnership-compute [Tier 1 — Lab research (Anthropic)]
- https://aws.amazon.com/about-aws/whats-new/2026/04/amazon-bedrock-claude-mythos/ [Tier 2 — Vendor announcement (AWS)]
- https://cloud.google.com/blog/products/ai-machine-learning/claude-mythos-preview-on-vertex-ai [Tier 2 — Vendor announcement (Google Cloud)]
- https://www.nxcode.io/resources/news/claude-mythos-preview-anthropic-most-powerful-model-2026 [Tier 2 — Tech news]
- https://llm-stats.com/blog/research/claude-mythos-preview-launch [Tier 2 — Tech news]
- https://techcrunch.com/2026/03/29/why-openai-really-shut-down-sora/ [Tier 1 — Independent journalism (TechCrunch)]
- https://techcrunch.com/2026/03/24/openais-sora-was-the-creepiest-app-on-your-phone-now-its-shutting-down/ [Tier 1 — Independent journalism (TechCrunch)]
- https://help.openai.com/en/articles/20001152-what-to-know-about-the-sora-discontinuation [Tier 2 — Vendor announcement (OpenAI)]
- https://findskill.ai/blog/gpt-6-release-date/ [Tier 2 — Tech news]
- https://finance.biggo.com/news/A8Y8a50ByH9TLH69HG8d [Tier 2 — Tech news]
- https://findskill.ai/blog/deepseek-v4-release-date-specs/ [Tier 2 — Tech news]
- https://dataconomy.com/2026/03/16/deepseek-v4-and-tencents-new-hunyuan-model-to-launch-in-april/ [Tier 2 — Tech news]
- https://aidevdayindia.org/blogs/lmsys-chatbot-arena-current-rankings/lmsys-chatbot-arena-current-top-models.html [Tier 2 — Tech news/leaderboard aggregator; note: unofficial tracker, not primary LMSYS source]
- https://techwireasia.com/2026/04/broadcom-custom-ai-chips-google-anthropic-deal/ [Tier 2 — Tech news]
- https://futurism.com/artificial-intelligence/real-reason-openai-shut-sora-down [Tier 2 — Tech news]
