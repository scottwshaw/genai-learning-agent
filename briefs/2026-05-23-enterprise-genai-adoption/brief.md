# Enterprise GenAI Adoption — Research Brief (2026-05-23)

## Key Developments

- **Gartner upgrades worldwide AI spending forecast to $2.59 trillion, but warns enterprises haven't yet scaled their own spend**
  - **What changed:** Gartner's May 19 forecast raised worldwide AI spending to $2.59 trillion (+47% YoY), with AI model spending alone growing 110% in 2026.
  - **Why it matters:** Spending is dominated by hyperscalers and vendors — enterprises are described as "yet to flex their spending potential," signaling the enterprise deployment wave is still ahead of current capital flows.
  - *(Gartner press release, May 19, 2026)*

- **Cohere acquires Reliant AI, marking first sovereign-AI vertical bet on regulated biopharma**
  - **What changed:** Cohere acquired Reliant AI (biopharma analytics, Montreal/Berlin) on May 19, integrating proprietary biomedical datasets into its sovereign enterprise platform.
  - **Why it matters:** Combining sovereign deployment architecture with regulated-industry domain data addresses the two most cited barriers to healthcare AI adoption: data privacy and domain specificity.
  - *(BNN Bloomberg / BusinessWire / The Canadian Press, May 19, 2026)* [Tier 2 sources only]

- **PYMNTS sector survey finds financial services leads all industries in AI task deployment — but avoids customer-facing growth tools**
  - **What changed:** A March 2026 survey of 60 large-enterprise technology executives found financial services reached high adoption on 27 of 75 AI-supported tasks versus 10 for healthcare.
  - **Why it matters:** Financial services AI is concentrated in structured back-office functions; customer-facing tools like KYC and churn prediction remain underdeveloped, exposing a growth gap.
  - *(PYMNTS Intelligence Enterprise AI Benchmark Report, May 2026)* [Tier 2 sources only]

## Notable Papers / Models / Tools

| Item | Date | Source | Summary |
|------|------|--------|---------|
| Gartner AI Spending Forecast (1Q26 update) | May 19, 2026 | [Gartner Newsroom](https://www.gartner.com/en/newsroom/press-releases/2026-05-19-gartner-forecasts-worldwide-ai-spending-to-grow-47-percent-in-2026) | $2.59T total AI spending in 2026, 47% YoY; AI infrastructure >45% of total; AI model spending +110%; AI software +60%; Gartner characterizes enterprises as still in tactical-ROI phase; full report: Forecast: AI Spending, Worldwide, 2025-2030, 1Q26 |
| PYMNTS Intelligence Enterprise AI Benchmark (May 2026 edition) | May 2026 | [PYMNTS](https://www.pymnts.com/study_posts/financial-services-pulls-ahead-in-the-enterprise-ai-race/) | 60 senior tech execs at $1B+ US enterprises; FS leads with 27/75 high-adoption tasks; FS budget increases (85%) vs healthcare (60%); data quality top FS barrier (30%); revenue recognition leads at 65% adoption; KYC at 20% — exposing gap between risk automation and growth tools |
| Cohere acquires Reliant AI | May 19, 2026 | [BusinessWire](https://www.businesswire.com/news/home/20260519725513/en/Cohere-Acquires-Reliant-AI-to-Expand-Sovereign-Enterprise-AI-for-the-Global-Biopharma-and-Healthcare-Sectors) / [BNN Bloomberg](https://www.bnnbloomberg.ca/business/2026/05/19/cohere-buys-biopharma-analytics-firm-reliant-ai/) | Integrates Reliant AI's biomedical datasets, NLP/RL team (DeepMind/Google Brain backgrounds), and Reliant Tabular analytics into Cohere North; co-occurs with pending Cohere–Aleph Alpha merger; extends Cohere sovereign vertical stack beyond FS and telecom |
| Google I/O 2026 — enterprise AI and Workspace Intelligence | May 19–20, 2026 | [Google Cloud Blog](https://cloud.google.com/blog/products/ai-machine-learning/innovations-from-google-io-26-on-google-cloud) / [eWeek](https://www.eweek.com/news/google-io-gemini-agentic-ai-era-2026/) | Gemini 3.5 Flash GA; Antigravity 2.0 connected to Agent Platform with Google Cloud enterprise security and compliance; Workspace Intelligence semantic layer; Gemini Spark (24/7 background agent) for Gemini Enterprise customers; Google processes 3.2 quadrillion tokens/month across products (+7× YoY) |
| McKinsey "AI Productivity Gains and the Performance Paradox" | ~May 1, 2026 | [McKinsey Strategy & Corporate Finance](https://www.mckinsey.com/capabilities/strategy-and-corporate-finance/our-insights/where-ai-will-create-value-and-where-it-wont) | Argues 94% of companies see no significant AI value despite near-universal deployment; productivity gains "accelerate existing work" without redesigning workflows; McKinsey hosted a webinar discussion on May 21 on moving "from productivity to durable competitive advantage" |
| METR Productivity Survey: Technical Workers (349 respondents) | May 11, 2026 | [METR Blog](https://metr.org/blog/2026-05-11-ai-usage-survey/) | Median self-reported 2× value gain from AI tools in March 2026 vs 1.3× in March 2025; METR's own staff reported lowest gains of any subgroup; cautions that speed measures likely overstate value; survey design explicitly distinguishes speed uplift from value uplift |
| Dell'Acqua et al., "Navigating the Jagged Technological Frontier" | 2026 | [Organization Science](https://openalex.org/W7135096569) | Peer-reviewed BCG/Harvard field experiment (20 citations); AI assistance improves performance on some knowledge tasks while worsening it on others within the same workflow — confirms AI advantage is task-specific, not universal |

## Technical Deep-Dive

**The "AI Paradox" in Enterprise Deployment: Evidence and Mechanism**

The McKinsey "AI Productivity Gains and the Performance Paradox" paper, published in late April/early May 2026, offers the most analytically precise account available this cycle of why enterprises are struggling to translate near-universal AI adoption into enterprise-level financial impact. The paper draws on McKinsey's own 2025 global survey data showing that 94% of companies report no significant value from AI — despite 88% deploying it in at least one business function — and frames this as a structural problem, not a tool-selection problem.

The core mechanism McKinsey identifies is technology-layer decoupling: most deployed AI applications "accelerate existing work" without redesigning underlying workflows. JPMorgan's real-time fraud detection and BMW's computer vision quality inspection are cited as examples that reduce manual effort and improve consistency while leaving line-shaft layouts — to use the electricity-era analogy the paper invokes — largely unchanged. The breakthrough cases, like Siemens' AI-coordinated predictive maintenance and production planning, emerge when AI is embedded across entire processes, not bolted on top of them. The paper uses Solow's "productivity paradox" of the 1980s computer era as an explicit structural analogue.

This framing is independently corroborated by METR's May 11 productivity survey (349 technical workers), which finds that while technical workers self-report a median 2× value gain, METR's own researchers — who are most familiar with controlled-trial evidence on AI productivity — report the lowest gains of any subgroup. The survey also explicitly distinguishes speed uplift from value uplift, noting that speed metrics systematically overstate enterprise value because they capture task acceleration rather than workflow-level contribution. This parallels findings from METR's 2025 controlled trial, which found developers using AI tools were 19% *slower* on the tasks they submitted (though with known selection effects that make this a lower bound).

The PYMNTS sector benchmark data from this cycle adds an important sector-specific dimension: financial services organizations have achieved deep deployment in structured, auditable back-office tasks (revenue recognition at 65%, credit risk assessment at 60%) but KYC adoption sits at only 20% and A/B experimentation at 10% — precisely the customer-growth and insight-generation tasks where AI should compound value. This pattern suggests the paradox operates partly through rational risk-aversion: enterprises are deploying AI where errors are observable and containable, and withholding it where outcomes are harder to audit, thereby systematically underinvesting in the AI applications that would create differentiated market positions. The Gartner forecast released the same week confirms the macro-level expression of this: AI spending grows 47% in 2026, but the headline is vendor- and hyperscaler-driven; enterprises "show limited appetite for using AI to drive disruptive enterprise change."

## Landscape Trends

- **[Enterprise GenAI Adoption × Safety, Assurance & Governance]** The McKinsey "Performance Paradox" framing and the METR productivity survey findings, taken together with the CCAF finding from the May 11 brief that 76% of large financial institutions cannot measure AI deployment value, suggest a structural measurement crisis is now a first-order enterprise problem — not merely a methodological gap. This is directly relevant to governance: enterprises cannot build meaningful AI risk management programs when they cannot measure what the AI is actually contributing. The Safety/Governance story (EU high-risk classification guidelines, METR Frontier Risk Report) may be creating requirements enterprises cannot yet operationalize because their measurement infrastructure does not yet exist.

- **[Enterprise GenAI Adoption × Models & Market]** The Models & Market story from the May 19 brief (OpenAI DeployCo at $4B, Anthropic's $1.5B JV with Blackstone/Goldman) reflects the same strategic insight as the McKinsey paradox: the competitive constraint is not model quality but implementation execution. Labs are now explicitly purchasing the deployment layer to capture revenue that pure model supply will not generate. The PYMNTS sector data (FS leads task adoption but underinvests in growth use cases) suggests the opportunity is significant — particularly for vendors who can bring both domain expertise and governance controls, which is precisely what the Cohere/Reliant AI acquisition targets.

- **Prior-brief callback — the "organizational failure mode" pattern is intensifying.** The Stanford Digital Economy Lab finding (April 2026 brief) that 95% of enterprise AI failures stem from organizational factors, not model capability, is now being reinforced from multiple independent directions this cycle: Gartner's explicit statement that enterprises remain in "tactical AI initiatives with incremental improvements," McKinsey's formal model of the Solow-style paradox, and METR's survey showing that the researchers most experienced with rigorous AI evaluation are the least optimistic about AI's productivity contribution. The thesis is hardening from an empirical observation (Stanford, April) to a structurally endorsed diagnosis (Gartner + McKinsey + METR, May).

- **[Enterprise GenAI Adoption × Agentic Systems]** Google I/O 2026's Workspace Intelligence and Gemini Spark announcements (Antigravity 2.0 with enterprise compliance, background agents in Gmail/Docs/Keep) represent the most direct attempt by a hyperscaler to operationalize the "workflow redesign" prescription that McKinsey and the Stanford playbook both recommend — not by selling a model, but by embedding agents into the daily digital context enterprise workers already inhabit. Whether Google's Workspace incumbency advantage converts into adoption evidence is currently unknown; independent productivity evidence for Gemini Enterprise is limited to vendor-reported Q1 paid MAU growth (+40% QoQ, Cloud Next '26), which is insufficient for claims about enterprise value creation.

- **Sovereign and domain-specific deployment is emerging as the operative architecture for regulated industries.** The Cohere/Reliant AI acquisition, occurring alongside the pending Cohere/Aleph Alpha merger, signals that the competitive moat in healthcare and biopharma AI is not general model capability but the combination of sovereign deployment (data residency, private infrastructure) with domain-specific datasets and regulatory workflows. This is structurally different from horizontal platform competition; it implies regulated-industry enterprises will increasingly route GenAI procurement through domain-specialized vendors with an explicit sovereign deployment story, rather than through hyperscaler-native APIs alone.

## Vendor Landscape

- **Cohere** acquired Reliant AI (biopharma analytics) on May 19, adding proprietary biomedical datasets and a specialized NLP/RL team into its sovereign AI platform. This extends Cohere's regulated-industry vertical stack (previously FS and telecom) into life sciences. Occurring alongside the pending Cohere–Aleph Alpha merger, this represents a material strategic pivot toward domain-specialized regulated-industry AI rather than horizontal enterprise LLM competition. [Tier 2 — vendor announcement; acquisition fact independently covered by BNN Bloomberg and The Canadian Press]

- **Google** extended its Gemini Enterprise platform at I/O 2026 (May 19–20) with Antigravity 2.0 connected to Agent Platform (inheriting Google Cloud enterprise compliance terms), Workspace Intelligence (semantic context layer across Workspace apps), Gemini Spark (background personal agent for enterprise), and a Managed Agents API for custom agents inside Google-hosted environments. Enterprise rollouts are staggered to summer 2026. Claimed token volume: 3.2 quadrillion/month (+7× YoY across all Google products). [Tier 2 — vendor announcement]

- **Gartner** (Tier 1 analyst) placed AI squarely in the "Trough of Disillusionment" as of its May 19 forecast — with the explicit prediction that in 2026, AI will most commonly be sold to enterprises by incumbent software providers rather than purchased as part of new strategic initiatives.

## Sources

- https://www.gartner.com/en/newsroom/press-releases/2026-05-19-gartner-forecasts-worldwide-ai-spending-to-grow-47-percent-in-2026 [Tier 1 — Analyst report: Gartner]
- https://www.pymnts.com/study_posts/financial-services-pulls-ahead-in-the-enterprise-ai-race/ [Tier 2 — Tech news / industry survey]
- https://www.businesswire.com/news/home/20260519725513/en/Cohere-Acquires-Reliant-AI-to-Expand-Sovereign-Enterprise-AI-for-the-Global-Biopharma-and-Healthcare-Sectors [Tier 2 — Vendor announcement]
- https://www.bnnbloomberg.ca/business/2026/05/19/cohere-buys-biopharma-analytics-firm-reliant-ai/ [Tier 2 — Tech news]
- https://cloud.google.com/blog/products/ai-machine-learning/innovations-from-google-io-26-on-google-cloud [Tier 2 — Vendor announcement]
- https://blog.google/innovation-and-ai/technology/ai/google-io-2026-all-our-announcements/ [Tier 2 — Vendor announcement]
- https://www.mckinsey.com/capabilities/strategy-and-corporate-finance/our-insights/where-ai-will-create-value-and-where-it-wont [Tier 1 — Analyst report: McKinsey]
- https://metr.org/blog/2026-05-11-ai-usage-survey/ [Tier 1 — Independent evaluation org]
- https://thenextweb.com/news/mckinsey-ai-productivity-paradox-enterprise-roi-capex [Tier 1 — Independent journalism]
- https://openalex.org/W7135096569 [Tier 1 — Peer-reviewed: Organization Science]
- https://www.pymnts.com/artificial-intelligence-2/2026/financial-services-firms-lead-enterprise-ai-adoption-as-85percent-boost-budgets/ [Tier 2 — Tech news]
- https://www.eweek.com/news/google-io-gemini-agentic-ai-era-2026/ [Tier 2 — Tech news]
- https://www.hpcwire.com/bigdatawire/this-just-in/gartner-forecasts-worldwide-ai-spending-to-grow-47-in-2026/ [Tier 1 — arXiv unaffiliated — not applicable; Tier 2 — Tech news, corroborating Gartner Tier 1 release]
- https://www.jbs.cam.ac.uk/faculty-research/centres/alternative-finance/publications/2026-global-ai-in-financial-services-report/ [Tier 1 — Institutional research: Cambridge Centre for Alternative Finance / BIS / IMF]
- https://www.trendingtopics.eu/cohere-acquires-reliant-ai-just-weeks-after-the-merger-with-aleph-alpha/ [Tier 2 — Tech news]
