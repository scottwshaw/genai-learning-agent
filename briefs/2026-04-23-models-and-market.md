# Models & Market — Research Brief (2026-04-23)

## Key Developments

- **Claude Opus 4.7 posts record SWE-bench scores at unchanged API price**
  - **What changed:** Anthropic released Claude Opus 4.7 on April 16 with 87.6% SWE-bench Verified and 64.3% SWE-bench Pro.
  - **Why it matters:** Teams building production coding agents gain independently validated capability improvements at the same API price.
  - *(Anthropic; Vellum independent benchmark analysis; GitHub Copilot changelog, April 16, 2026)* [Tier 2 sources only]

- **Meta's proprietary Muse Spark ends the lab's open-weight model tradition**
  - **What changed:** Meta Superintelligence Labs released Muse Spark on April 8 — a proprietary, closed-weight model that supersedes the open Llama series.
  - **Why it matters:** The shift signals that even labs with open-source identities are closing their best models as closed competitors pull ahead.
  - *(CNBC; Fortune; Meta AI blog, April 8, 2026)*

- **Google expands role from API provider to Apple's Foundation Model builder**
  - **What changed:** Google's Cloud Next '26 keynote on April 22 confirmed Google is developing Apple's next-generation Foundation Models on Gemini technology.
  - **Why it matters:** Gemini embedding into Apple's AI substrate extends Google's model influence to more than a billion iOS devices.
  - *(Google Cloud Next keynote; 9to5Mac, April 22, 2026)* [Tier 2 sources only]

---

## Notable Papers / Models / Tools

| Item | Date | Source | Summary |
|------|------|--------|---------|
| Claude Opus 4.7 | Apr 16, 2026 | [Anthropic](https://www.anthropic.com) / [Vellum](https://www.vellum.ai/blog/claude-opus-4-7-benchmarks-explained) / [GitHub Copilot](https://github.blog/changelog/2026-04-16-claude-opus-4-7-is-generally-available/) | 87.6% SWE-bench Verified (+6.8pp), 64.3% SWE-bench Pro (new record); 78.0% OSWorld-Verified; xhigh effort level; task budgets beta; 3.75MP vision (3× resolution increase); new tokenizer uses 1–1.35× more tokens at same $5/$25 price |
| Meta Muse Spark | Apr 8, 2026 | [CNBC](https://www.cnbc.com/2026/04/08/meta-debuts-first-major-ai-model-since-14-billion-deal-to-bring-in-alexandr-wang.html) / [Meta AI](https://ai.meta.com/blog/introducing-muse-spark-msl/) | First Meta Superintelligence Labs model; proprietary/closed-weight; competitive but not leading on broad benchmarks; Contemplating mode orchestrates parallel reasoning agents; private API preview for select partners; scores 42.8 on HealthBench Hard (vs. GPT-5.4's 40.1) |
| OpenAI Codex unified super-app | Apr 16, 2026 | [Let's Data Science](https://letsdatascience.com/news/openai-updates-codex-superapp-with-desktop-control-6760e6b7) / [TestingCatalog](https://www.testingcatalog.com/openai-develops-unified-codex-app-and-new-scratchpad-feature/) | Desktop app merging ChatGPT, Codex coding agent, and Atlas browser into single interface; parallel agent execution; desktop automation and background control; 3M weekly Codex users |
| GPT-5.5 "Spud" — production testing detected | Apr 19–22, 2026 | Developer observations / [Polymarket](https://polymarket.com/event/gpt-5pt5-released-on) | Production-scale API testing observed April 19; Sam Altman tease "really excited for this week" on April 22; 86% Polymarket odds for April 23 release; pretraining complete since March 24 |
| Google Gemini Enterprise Agent Platform | Apr 22, 2026 | [Google Cloud blog](https://cloud.google.com/blog/topics/google-cloud-next/welcome-to-google-cloud-next26) / [The Next Web](https://thenextweb.com/news/google-cloud-next-ai-agents-agentic-era) | Vertex AI rebranded; first-party API throughput at 16B tokens/min (+60% QoQ); TPU 8t/8i dual-chip 8th generation announced; Gemini Enterprise app GA; $750M partner investment fund |
| Google gemini-embedding-2-preview | Apr 2026 | [Google AI changelog](https://ai.google.dev/gemini-api/docs/changelog) | First Google multimodal embedding model spanning text, image, video, audio, and PDF in unified embedding space; relevant for multimodal RAG pipelines |
| DeepSeek V4 — third delay, still unreleased | Apr 21, 2026 | [Reuters, Apr 3](https://www.reuters.com) / [FindSkill.ai](https://findskill.ai/blog/deepseek-v4-release-date-specs/) | Third consecutive missed window; V4-Lite live-tested on API nodes; Huawei Ascend 950PR dependency confirmed; community projects late-April/early-May; leaked SWE-bench Verified claim of ~81% not independently verified |

---

## Technical Deep-Dive

**Claude Opus 4.7: what changed architecturally and what it means for production teams**

Anthropic's Opus 4.7 is most notable not for its headline SWE-bench Verified score (87.6%, up 6.8 points) but for SWE-bench Pro, where the gain is 10.9 points — from 53.4% to 64.3%. SWE-bench Pro tests on harder, real-world software engineering tasks, and the scale of a single-version jump there suggests Anthropic has made targeted improvements to multi-step planning and precise instruction-following for complex engineering problems. Cursor's independently run CursorBench confirms a jump from 58% to 70% — a 12-point gain that early-access partner Warp and others corroborated with production traces. Critically, MCP-Atlas, which measures multi-turn tool-calling across complex workflows (the closest available proxy for production agentic task completion), shows Opus 4.7 leading GPT-5.4 by 9.2 points — the largest gap observed among available multi-step tool-calling benchmarks reviewed. The one documented regression is BrowseComp (multi-step web research), where Opus 4.7 dropped from 83.7% to 79.3%, while GPT-5.4 holds 89.3%. Teams running research-heavy agentic workflows should evaluate this gap before migrating.

The vision upgrade is architecturally significant for computer use deployments: Opus 4.7 accepts images up to 2,576 pixels on the long edge (approximately 3.75 megapixels, up from 1.15 megapixels), and coordinate output now maps 1:1 to actual pixel positions, eliminating the scale-factor conversion errors that caused missed clicks and navigation failures in Opus 4.6 computer use sessions. One early-access partner testing visual acuity for autonomous penetration testing reported accuracy jumping from 54.5% to 98.5%. OSWorld-Verified scores moved from 72.7% to 78.0%. For any workflow involving dense screenshots, technical diagrams, or UI navigation, this resolution change effectively makes Opus 4.7 a different-class model from its predecessor.

Two operational changes require attention for enterprise teams. First, the new task budgets feature (currently in beta, enabled via the `task-budgets-2026-03-13` beta header) allows an advisory token budget to be set across an entire agentic loop rather than per individual call. The minimum is 20,000 tokens; the feature is non-binding but guides the model's planning to complete tasks within the budget envelope — directly addressing the runaway token consumption risk in long-horizon autonomous agents. This is the most governance-relevant feature in the release for teams running compliance-sensitive workflows. Second, a breaking API change: setting `temperature`, `top_p`, or `top_k` to any non-default value now returns a 400 error — Anthropic has taken full control of sampling parameters. Combined with a new tokenizer that uses 1–1.35× more tokens per equivalent text input at the same sticker price ($5/$25), teams should replay representative production prompts before migrating; the effective cost increase could range from negligible to ~35% depending on content type.

---

## Landscape Trends

- **[Models & Market × Agentic Systems]** Frontier models are specializing by agentic workflow category rather than converging on a single dominant option. Opus 4.7's large lead on MCP-Atlas (multi-step tool-calling) and SWE-bench Pro but regression on BrowseComp, GPT-5.4's BrowseComp dominance but gap on SWE-bench Pro, and Gemini 3.1 Pro's multilingual and reasoning strengths together suggest enterprise teams building agentic pipelines need model-by-task-category evaluation strategies rather than single-model selection. Routing architectures that assign tasks by benchmark strength are no longer a premature optimization — they are increasingly the appropriate production design.

- **[Models & Market × AI Infrastructure & Geopolitics]** The open-weight frontier is contracting at the exact moment supply-chain constraints limit Chinese labs' ability to fill the gap. Meta's Muse Spark going proprietary, combined with DeepSeek V4's third consecutive delay (Huawei Ascend chip dependency as the confirmed bottleneck per Reuters), leaves Gemma 4 (Apache 2.0) and GLM-5.1 (MIT) as the only permissively licensed frontier-competitive options available today. This is a materially different landscape from the "open-weight parity" narrative that dominated Q1 2026 briefs, and enterprises planning self-hosted deployments should incorporate this supply uncertainty into their vendor risk assessments.

- **The April 8 Models & Market brief flagged Anthropic's two-tier capability strategy (Mythos Preview restricted, Opus available). The following two weeks confirm the strategy is hardening.** Opus 4.7 is now clearly the public tier — improved, available everywhere (Bedrock, Vertex, Foundry, Cortex, GitHub Copilot), and priced for volume — while Mythos Preview remains exclusively available to the 12 Project Glasswing partners. Anthropic is also rolling out cybersecurity safeguards to Opus 4.7 before expanding access on Mythos-class models, using the public tier as a capability proving ground. This deliberate tiering, now confirmed across two releases, is a new market structure where vendor "best available" is decoupled from vendor "best that exists" — with compliance implications for enterprise teams relying on benchmark claims.

- **[Models & Market × LLM Production Infrastructure]** Google Cloud Next's disclosure that first-party Gemini API throughput grew from 10 billion to 16 billion tokens per minute in a single quarter (+60% QoQ) is a leading indicator of where enterprise inference workloads are concentrating. As Google confirms Gemini as the substrate for both enterprise agent platforms and Apple Foundation Models, and given Anthropic's existing 3.5 GW TPU capacity commitment through Broadcom starting 2027, the model-layer economics are increasingly inseparable from Google's infrastructure pricing. Teams currently evaluating multi-year Claude commitments should monitor whether TPU 8i's inference efficiency gains (announced at Cloud Next) translate into Claude API price compression in H1 2027.

- **A Q2 2026 benchmark reshuffling is imminent.** GPT-5.5 (Spud) was detected in production-scale API testing on April 19 with high Polymarket odds for release this week; DeepSeek V4 is targeting late April with leaked SWE-bench Verified claims around 81% (unverified); and Gemini 4 is expected to be previewed at Google I/O on May 19. Any model capability assessment finalized today should be treated as provisional for at most 4–6 weeks. Enterprise teams in active procurement cycles should build model-agnostic evaluation pipelines rather than optimizing for any single model's current benchmark position.

---

## Vendor Landscape

- **Anthropic:** Claude Opus 4.7 GA on April 16 across all major platforms (Bedrock, Vertex, Foundry, Snowflake Cortex, GitHub Copilot); Mythos Preview remains restricted to Project Glasswing partners; task budgets beta provides first agentic token governance control. Anticipated IPO timeline (October 2026) creating commercial pressure to maintain benchmark leadership.
- **Google:** Gemini Enterprise Agent Platform launched at Cloud Next '26 (Vertex AI rebranded); Gemini API at 16B tokens/min; Apple Foundation Model partnership confirmed; TPU 8t (training) and TPU 8i (inference) 8th-generation chips announced; Gemini 3.1 Flash-Lite confirmed GA; $750M partner investment fund.
- **Meta:** Muse Spark released April 8 as first proprietary model from Meta Superintelligence Labs; powers Meta AI app (3B+ users); private API preview for select partners; Llama 4 remains available; open-source future versions of Muse promised but not committed to a timeline.
- **OpenAI:** Codex unified super-app (ChatGPT + Codex + Atlas browser) launched April 16; 3M weekly Codex users; GPT-5.5 (Spud) in production testing as of April 19 with imminent release expected; ChatGPT at approximately 900M weekly active users and 50M paying subscribers.
- **DeepSeek:** V4 still unreleased as of April 23 (third delay); V4-Lite live-tested on API nodes with developer reports of improved context recall; Huawei Ascend 950PR confirmed as primary inference hardware; late April or early May now the most commonly cited community estimate.

---

## Sources

- https://www.vellum.ai/blog/claude-opus-4-7-benchmarks-explained [Tier 2 — Tech news]
- https://github.blog/changelog/2026-04-16-claude-opus-4-7-is-generally-available/ [Tier 2 — GitHub]
- https://www.buildfastwithai.com/blogs/claude-opus-4-7-review-benchmarks-2026 [Tier 2 — Tech news]
- https://nerdleveltech.com/claude-opus-4-7-benchmarks-features-pricing [Tier 2 — Tech news]
- https://www.the-ai-corner.com/p/claude-opus-4-7-guide-benchmarks-2026 [Tier 2 — Tech news]
- https://www.cnbc.com/2026/04/08/meta-debuts-first-major-ai-model-since-14-billion-deal-to-bring-in-alexandr-wang.html [Tier 1 — Independent journalism]
- https://fortune.com/2026/04/08/meta-unveils-muse-spark-mark-zuckerberg-ai-push/ [Tier 1 — Independent journalism]
- https://techcrunch.com/2026/04/08/meta-debuts-the-muse-spark-model-in-a-ground-up-overhaul-of-its-ai/ [Tier 2 — Tech news]
- https://ai.meta.com/blog/introducing-muse-spark-msl/ [Tier 2 — Vendor announcement]
- https://about.fb.com/news/2026/04/introducing-muse-spark-meta-superintelligence-labs/ [Tier 2 — Vendor announcement]
- https://venturebeat.com/technology/goodbye-llama-meta-launches-new-proprietary-ai-model-muse-spark-first-since [Tier 2 — Tech news]
- https://cloud.google.com/blog/topics/google-cloud-next/welcome-to-google-cloud-next26 [Tier 2 — Vendor announcement]
- https://blog.google/innovation-and-ai/infrastructure-and-cloud/google-cloud/cloud-next-2026-sundar-pichai/ [Tier 2 — Vendor announcement]
- https://blog.google/innovation-and-ai/infrastructure-and-cloud/google-cloud/next-2026/ [Tier 2 — Vendor announcement]
- https://9to5mac.com/2026/04/22/google-teases-gemini-powered-siri-upgrade-during-cloud-next-keynote/ [Tier 2 — Tech news]
- https://thenextweb.com/news/google-cloud-next-ai-agents-agentic-era [Tier 2 — Tech news]
- https://oplexa.com/google-cloud-next-2026/ [Tier 2 — Tech news]
- https://ai.google.dev/gemini-api/docs/changelog [Tier 2 — Vendor announcement]
- https://findskill.ai/blog/deepseek-v4-release-date-specs/ [Tier 2 — Tech news]
- https://tokenmix.ai/blog/deepseek-v4-release-delay-huawei-chip-2026 [Tier 2 — Tech news]
- https://polymarket.com/event/gpt-5pt5-released-on [Tier 2 — Tech news]
- https://letsdatascience.com/news/openai-updates-codex-superapp-with-desktop-control-6760e6b7 [Tier 2 — Tech news]
- https://www.testingcatalog.com/openai-develops-unified-codex-app-and-new-scratchpad-feature/ [Tier 2 — Tech news]
- https://simonwillison.net/2026/Apr/8/muse-spark/ [Tier 2 — Practitioner blog]
- https://www.artificialintelligence-news.com/news/meta-muse-spark-ai-model-open-source/ [Tier 2 — Tech news]
