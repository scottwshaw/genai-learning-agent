# Enterprise GenAI Adoption — Research Brief (2026-05-28)

> **Quiet-week note:** KD1 this period is Tier 2-only. The Federal Reserve FEDS Note (Apr 3, 2026) has been promoted to a Tier 1 Key Development below. Analytical weight has been shifted to Technical Deep-Dive and Landscape Trends accordingly.

---

## Key Developments

- **Big Four consulting converges on Claude, creating silent vendor lock-in**
  - **What changed:** KPMG announced a 276,000-employee Claude rollout, making it the third Big Four firm to standardize on a single model.
  - **Why it matters:** Enterprise buyers of Big Four services now inherit a Claude dependency without explicitly negotiating it.
  - *(Digital Applied analysis, May 2026; corroborated by vendor announcements)* [Tier 2 sources only]

- **Federal Reserve documents 18% US firm AI adoption, C-suite perception gap**
  - **What changed:** A Federal Reserve staff note found roughly 18% of US firms used AI by end 2025.
  - **Why it matters:** A persistent gap between C-suite and worker perceptions of AI productivity gains suggests enterprise adoption rates are overstated.
  - *(Federal Reserve Board FEDS Note, Apr 3, 2026)* [Tier 1 — Federal Reserve staff paper]

---

## Notable Papers / Models / Tools

| Item | Date | Source | Summary |
|------|------|--------|---------|
| "Measuring Agents in Production" (arXiv:2512.04123) | Dec 2, 2025 | arXiv — unaffiliated preprint, unverified | First large-scale empirical study of production AI agents: 306 practitioners surveyed, 20 in-depth case studies across 26 domains. Key finding: 68% of production agents run at most 10 steps before human intervention; 70% use prompting over fine-tuning; reliability remains the top development challenge across all deployment contexts. |
| "Towards a Science of AI Agent Reliability" (arXiv:2602.16666) | Feb 18, 2026 | arXiv — unaffiliated preprint, unverified | Proposes 12 reliability metrics across four dimensions (consistency, robustness, predictability, safety) for agentic systems. Evaluates 14 agentic models across two benchmarks; finds capability gains have yielded only small reliability improvements — directly relevant to regulated-industry deployment gates. |
| Federal Reserve FEDS Note: "Monitoring AI Adoption in the US Economy" | Apr 3, 2026 | Federal Reserve Board staff paper | Authoritative triangulation of US enterprise AI adoption using three nationally representative surveys (BTOS, RPS, SBU). Finds ~18% of firms using AI by end 2025; documents a persistent gap between senior leaders' and workers' perceptions of AI productivity gains; notes social-desirability bias may inflate C-suite adoption reporting. |
| McKinsey: "Redesigning Technology Workforce for the Agentic AI Era" | Apr 6, 2026 | McKinsey Technology Practice | Primary research piece drawing on McKinsey Global Tech Agenda (n=large-enterprise leaders). Frames three CIO decisions: what talent to hire, what to build vs. train agents to do, which vendor partnerships deliver ROI. Finds two-thirds of top-performing firms have CIOs "very involved" in enterprise strategy vs. 52% elsewhere. |
| KPMG Q1 2026 AI Quarterly Pulse (Banking sector focus) | Mar 31, 2026 | KPMG US | Sector-specific Pulse covering banking, asset management, PE. Finds 65% of leaders now cite difficulty scaling use cases as a top ROI barrier — up sharply from 33% last quarter — and 62% cite skills gaps (up from 25%). The one-quarter doubling of scaling barriers is the clearest data point yet that the enterprise AI bottleneck has shifted from access to execution. |

---

## Technical Deep-Dive

**The procurement lock-in embedded in Big Four AI standardization**

The convergence of Deloitte (Oct 2025, ~470K employees), PwC (May 14, 30K certified), and KPMG (May 19, 276K rollout) on Claude as their primary AI reasoning layer — combined with SAP's announcement that Joule runs on Claude (May 12), and Salesforce's Agentforce embedding Claude through the Einstein Trust Layer — creates a structural feature of enterprise AI procurement that most procurement teams have not explicitly modeled: the platform-to-model bundle.

For the roughly 65% of large enterprises that prefer incumbent solutions for trust and integration reasons (per Q1 2026 data), the practical consequence is that buying SAP Joule, Salesforce Agentforce, or engaging a Big Four consulting firm for AI transformation now implicitly commits that enterprise to Claude-governed outputs, Claude token economics, and Claude's data-handling agreements — even when the procurement decision was nominally about the ERP or the consulting partner, not the model. The model-selection step has been silently absorbed upstream. This dynamic is consistent with the Federal Reserve FEDS Note (Apr 3, 2026) finding that only ~18% of US firms were actively using AI by end 2025: the enterprises now adopting at scale are doing so predominantly through platform and services bundles that obscure model-level choices, rather than through direct model contracts — a pathway that further compresses explicit model governance.

This matters most in regulated financial services for two reasons. First, model governance obligations under FINRA Rule 3110 (supervisory obligation for GenAI outputs, as surfaced in the 2026-05-05 brief) and the emerging EU AI Act Annex III high-risk classification guidance (surfaced in the 2026-05-21 Safety brief) require enterprises to understand and document the AI system configuration, including the underlying model. A vendor-bundled model is harder to audit, harder to swap under adverse findings, and harder to version-control across regulatory reporting cycles. Second, the commercial lock-in vector is compounded by Anthropic's $1.5B JV with Blackstone and Goldman Sachs (May 4) — the same financial institutions that are both enterprise AI buyers and now Anthropic equity partners, creating potential conflicts of interest in vendor evaluation processes that compliance functions should flag.

The independent analysis finding that market reaction to DeployCo's May 11 launch included estimated declines of 3–5% in major IT services firm equities on announcement day (per Digital Applied, corroborated by The Next Web May 12) confirms that the capital markets read this as a structural, not marginal, threat to the incumbent SI model. Enterprise CIOs evaluating AI transformation engagements should now explicitly distinguish between three contractual relationships previously treated as one: the model provider contract, the platform contract, and the implementation partner contract — each carrying different lock-in timelines, different regulatory disclosure obligations, and different renegotiation dynamics at renewal. McKinsey's build-vs-buy framing (Apr 6, 2026) reinforces this: the CIOs at top-performing firms who are "very involved" in enterprise strategy are precisely those positioned to make this three-way distinction explicit before contract execution, rather than discovering bundled dependencies at renewal.

*Note: This analysis is anchored by the Federal Reserve FEDS Note (Apr 3, 2026) on US enterprise AI adoption rates and McKinsey's primary research on build-vs-buy CIO decisions (Apr 6, 2026) as Tier 1 sources. Market share figures for Anthropic are drawn from Tier 2 vendor survey data (Ramp AI Index); treat directional signals as hypothesis-generating rather than confirmed fact.*

---

## Landscape Trends

- **[Enterprise GenAI Adoption × AI Infrastructure & Geopolitics]** Gartner's Q1 2026 forecast revision to $2.59T total AI spend in 2026 (covered in the 2026-05-23 brief as a KD) characterizes enterprise direct spend as still in "tactical ROI" phase — meaning the vast majority of the spend surge is vendor- and hyperscaler-driven, not enterprise-originating. This divergence is now visible in corporate earnings: the KPMG Q1 Pulse finds 93% of leaders believe GenAI has enhanced their competitive position, yet only 29% report significant organizational ROI. The gap between infrastructure build-out (geopolitics/AI infrastructure topic) and enterprise value capture (this topic) is widening, not closing — Gartner explicitly calls 2026 "the inflection year" for enterprise spend to catch up, but the current data suggests the mechanisms for that catch-up (workflow redesign, data readiness, governance) remain lagging.

- **[Enterprise GenAI Adoption × Safety, Assurance & Governance]** The EU AI Act Omnibus provisional agreement reached May 7 (covered in the 2026-05-10 and 2026-05-21 Safety briefs) defers Annex III high-risk obligations to December 2027, giving regulated financial services firms roughly 18 months to build compliant AI governance before enforcement. However, Gartner's separate prediction that 50% of GenAI deployments will require explainability tracing by 2028 (surfaced in the 2026-05-02 LLM Production Infrastructure brief) is on a faster track. Enterprises embedding Claude through Big Four or platform vendors who do not own the model's traceability layer face a structural conflict: the governance obligation runs to them, but the interpretability tools are controlled by the upstream model provider.

- The scaling barrier trajectory documented in the KPMG Q1 2026 Pulse — difficulty scaling use cases jumping from 33% to 65% as a top ROI barrier in a single quarter — directly reinforces the "micro-productivity trap" pattern first surfaced in the 2026-05-05 brief and repeated as a Key Development in 2026-05-11 and 2026-05-17. Each successive brief has added a different analytical lens (HBR: workflow redesign deficit; McKinsey: productivity gains competed away; Gartner: layoffs not delivering ROI), but the underlying data is consistent: individual productivity gains do not compound into organizational ROI without deliberate operating model change. The KPMG data adds a time-series dimension: this barrier is *accelerating*, not stabilizing.

- **[Enterprise GenAI Adoption × Agentic Systems]** The empirical data from "Measuring Agents in Production" (arXiv:2512.04123) — showing 68% of deployed agents cap out at 10 steps before requiring human intervention, and 74% rely primarily on human evaluation — frames the build-vs-buy decision differently than vendor marketing suggests. Enterprises buying packaged agentic platforms are purchasing autonomous framing but deploying heavily human-in-the-loop reality. The operational gap between vendor capability claims and production deployment patterns suggests that enterprise evaluators should demand empirical deployment telemetry (step counts, human override rates, escalation frequencies) rather than benchmark scores when selecting agentic platforms — a procurement standard the LLM observability and evaluation community is positioned to help define.

- The convergence of frontier model providers into the services layer (OpenAI DeployCo, Anthropic JV with Blackstone/Goldman) represents a structural challenge to the build-vs-buy decision that prior briefs have not fully surfaced: the "buy" path now includes a category of vendor that simultaneously sets model price, controls model capability roadmap, employs implementation engineers, and holds equity stakes with the enterprise's financial advisors. This vertical integration creates a conflict of interest surface that regulated financial services compliance functions have no established framework for evaluating. The gap between this emerging procurement reality and existing third-party risk management (TPRM) frameworks is the enterprise AI governance problem most likely to crystallize as a regulatory concern in H2 2026.

---

## Vendor Landscape

**Anthropic** continues consolidating the professional services delivery layer: three of four Big Four firms now standardized on Claude (Deloitte ~470K, KPMG ~276K, PwC ~30K certified); SAP Joule and Salesforce Agentforce both embed Claude as the primary reasoning engine. Ramp's April 2026 AI Index shows Anthropic at 34.4% business AI adoption share, narrowly overtaking OpenAI (32.3%) in enterprise wallet share for the first time.

**OpenAI** DeployCo (launched May 11, $4B+ PE-backed) is scaling its Forward Deployed Engineer model, targeting the same enterprise workflow integration market as Big Four and IT services firms. Incumbent IT services equities reportedly declined 3–5% on announcement day per independent analysis, suggesting the market reads this as a structural competitive threat.

**KPMG** acquired PrivateBlok (Feb 9, 2026) to accelerate multi-agent platform development; its Q1 2026 AI Pulse documents a 276K-employee Claude deployment alongside the launch of KPMG Workbench (50 agents in production, 1,000 in development), representing among the largest disclosed enterprise AI deployments.

**Cohere** acquired Reliant AI (May 19) to extend its sovereign vertical stack into biopharma and healthcare, co-occurring with a pending Cohere–Aleph Alpha merger that would strengthen its position for European regulated-industry procurement where data residency requirements favor non-US model providers.

---

## Sources

- https://www.gartner.com/en/newsroom/press-releases/2026-05-19-gartner-forecasts-worldwide-ai-spending-to-grow-47-percent-in-2026 [Tier 1 — Analyst research]
- https://www.federalreserve.gov/econres/notes/feds-notes/monitoring-ai-adoption-in-the-u-s-economy-20260403.html [Tier 1 — Federal Reserve staff paper]
- https://arxiv.org/abs/2512.04123 [Tier 1 — arXiv unaffiliated, unverified]
- https://arxiv.org/abs/2602.16666 [Tier 1 — arXiv unaffiliated, unverified]
- https://www.mckinsey.com/capabilities/mckinsey-technology/our-insights/designing-an-end-to-end-technology-workforce-for-the-ai-first-era [Tier 1 — Analyst primary research]
- https://www.mckinsey.com/featured-insights/themes/rewired-2-point-0-how-leading-companies-are-still-winning-with-ai [Tier 1 — Analyst primary research]
- https://www.globenewswire.com/news-release/2026/05/19/3297549/0/en/81-of-Enterprise-Technology-Leaders-Report-Production-Failures-from-AI-Generated-Code-New-Research-Shows.html [Tier 2 — Vendor survey]
- https://www.cloudbees.com/newsroom/enterprise-technology-leaders-report-production-failures-from-ai-generated-code [Tier 2 — Vendor announcement]
- https://www.digitalapplied.com/blog/enterprise-ai-agent-build-vs-buy-2026 [Tier 2 — Independent analysis]
- https://kpmg.com/us/en/media/news/q1-ai-pulse2026.html [Tier 2 — Vendor survey]
- https://kpmg.com/us/en/articles/2026/enterprise-ai-agents-strategy.html [Tier 2 — Vendor analysis]
- https://openai.com/index/openai-launches-the-deployment-company/ [Tier 2 — Vendor announcement]
- https://www.informationweek.com/machine-learning-ai/the-ai-infrastructure-boom-is-coming-for-enterprise-budgets [Tier 2 — Enterprise tech news]
- https://erp.today/openai-launches-deployment-company-to-bring-ai-into-enterprise-operations/ [Tier 2 — Enterprise tech news]
- https://www.businesswire.com/news/home/20260519725513/en/Cohere-Acquires-Reliant-AI-to-Expand-Sovereign-Enterprise-AI-for-the-Global-Biopharma-and-Healthcare-Sectors [Tier 2 — Vendor announcement]
