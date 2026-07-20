# Enterprise GenAI Adoption — Research Brief (2026-07-20)

## Key Developments

- **Agentic AI now directly decides bank capital allocations**
  - **What changed:** JPMorgan built AI agents that beat a 60/40 stock-bond portfolio and its own rules-based model in 20-year backtests.
  - **Why it matters:** Agentic AI is moving from research assistant to capital-allocation decision-maker inside a systemically important bank.
  - *Sources: [1]*

- **JPMorgan publicly rations expensive AI models to control rising token spend**
  - **What changed:** CFO Jeremy Barnum said the bank now matches model cost to task difficulty rather than defaulting to frontier models.
  - **Why it matters:** A top-tier bank has turned FinOps-style model tiering into a named, board-level cost discipline.
  - *Sources: [2]*

- **HBR research finds AI is breaking the "modular firm" playbook**
  - **What changed:** New research shows companies can decompose work with AI far faster than they can recombine it into value.
  - **Why it matters:** Reframes the workforce-adoption bottleneck from tool access to enterprise integration and governance authority.
  - *Sources: [3]*

## Notable Papers / Models / Tools

| Item | Date | Source | Summary |
|------|------|--------|---------|
| "The AI Resilience Gap: Bringing Artificial Intelligence Inside the Operational Resilience Perimeter" (arXiv:2607.07359) | July 8, 2026 | [4] | Jonathan Shelby, University of Oxford — Tier 1 affiliated. Proposes the AI Resilience Framework (dependency mapping, criticality-substitutability tiering, AI-specific impact tolerances, fallback doctrine, provider-concentration management). See Key Development and Technical Deep-Dive. |
| "Governing Generative AI Across Financial Institutions: An SR 26-2-Compatible Framework for Generative AI Risk Control" (arXiv:2607.04103) | v1 July 5 / v3 July 16, 2026 | [5] | Original v1 listed Citigroup and Florida State University affiliation; the July 16 revision lists most authors as independent researchers — affiliation now unclear. Proposes the Generative AI Control Framework (GAICF) to close the gap left by SR 26-2, which explicitly excludes generative and agentic AI from formal U.S. bank model-risk-management scope. |
| "U.S. and Japanese Companies Struggle with Different Parts of AI Adoption" — HBR | July 13, 2026 | [6] | Balasubramanian, Asaba, Bala & Joshi. Contrasts "wide but shallow" U.S. AI deployment against Japan's slower but often deeper implementation, citing divergent adoption-rate measurements (McKinsey vs. Yano Research Institute) as a caution against comparing headline adoption percentages across measurement methodologies. |
| Forrester Consulting / FPT Corporation global AI scaling study | Published July 8, widely reported July 15, 2026 | [7] | 397 global decision-makers surveyed; 51% allocate at least 5% of IT budget to AI but only 26% consider their organization advanced in operationalizing it. `[Vendor marketing — FPT-commissioned Forrester Consulting study]` |
| BIS Working Papers No. 1367, "The AI investment race" | July 14, 2026 | [8] | Rungcharoenkitkul (BIS). Models the AI capex boom as a winner-take-most contest financed by debt and circular equity stakes, estimating over-investment at roughly 1.5–3x the efficient level. Primary owner is AI Infrastructure & Geopolitics; referenced here for its direct tension with enterprise AI spend forecasts — see Landscape Trends. |

*Note: No pre-retrieved scholarly candidates were supplied for this cycle. arXiv:2607.07359 and arXiv:2607.04103 were sourced through independent research and evaluated against the recency gate and affiliation-verification rules.*

## Technical Deep-Dive

The Oxford paper's central move is to separate two governance logics that enterprise risk teams currently conflate: trustworthiness and resilience. Frameworks like the EU AI Act, ISO/IEC 42001, and the NIST AI RMF ask whether an AI system is safe, fair, transparent, and validated. None of them ask whether a firm can keep an important business service running when that AI system degrades, becomes unavailable, or turns out to be practically irreplaceable. The paper argues these are structurally distinct exposures — continuity under severe-but-plausible disruption, substitutability of the AI component, and concentration of dependency on a handful of frontier-model suppliers — and that a system can score well on every trustworthy-AI checklist while still being an unmanaged single point of failure for a regulated business process [4].

The proposed AI Resilience Framework operationalizes this distinction through five mechanisms: dependency mapping from AI components to named "important business services"; a criticality-substitutability matrix that tiers AI dependencies by how hard they would be to replace under stress; extension of existing impact-tolerance regimes to AI-specific failure modes, notably silent degradation rather than binary outage; a "fallback doctrine" that explicitly tests whether a stated fallback (e.g., reverting to a legacy system or manual process) actually works at the required scale and speed, versus being a fictional control that exists only on paper; and explicit management of provider concentration risk across the small number of frontier-model vendors most firms now depend on [4].

The significance for this audience is regulatory timing, not novelty of concept. The paper documents that UK authorities are already closing this gap from the supervisory side: the Financial Policy Committee has flagged AI concentration as a systemic risk, the Critical Third Parties regime is positioned to bring major AI and cloud providers within direct supervisory reach, and a recent joint statement reframed frontier AI as a resilience issue rather than purely a governance one — while the FCA has signaled no bespoke AI rulebook is coming [4]. The practical implication the paper draws is stark: firms waiting for AI-specific resilience rules will discover the applicable obligations were already in force under the existing operational-resilience regime [4].

Limitations are real: this is a single-author, UK-centric conceptual paper (cs.CR) extending a companion analysis of the UK cyber-resilience stack, with no reported firm-level pilot or empirical validation of the criticality-substitutability tiering in production. Its regulatory mapping is jurisdiction-specific (FPC, Critical Third Parties, FCA/PRA operational resilience rules) and would need adaptation for SR 26-2-style U.S. model-risk regimes or EU DORA, though the underlying substitutability-and-concentration logic likely generalizes [4].

## Landscape Trends

- **[Enterprise GenAI Adoption × Safety, Assurance & Governance]** The FSB's Sound Practices consultation (covered in the 2026-07-03 brief) drew reinforcing but non-substantive follow-up: Federal Reserve remarks from Vice Chair Bowman on July 7 and July 14 restate the same comment deadline and G20 finalization timeline without new content [9], reinforcing rather than advancing the prior gap — stasis, not a new development.
- **[Enterprise GenAI Adoption × AI Infrastructure & Geopolitics]** BIS's warning that AI capex is running 1.5–3x the efficient level on debt-financed, circular capital [8] sits in direct tension with Gartner's $2.59T 2026 AI spend forecast highlighted in the 2026-07-03 brief [13] — a widening gap between macro-prudential caution and analyst spend momentum that enterprise budget owners should watch as a leading indicator of vendor pricing and financing stability.
- **[Enterprise GenAI Adoption × Agentic Systems]** JPMorgan's live test of capital-allocation agents [1] gives concrete stakes to diagnostic concerns raised in academic FS-agent benchmarks (e.g., CLQT [14], covered in the 2026-07-04 Agentic Systems brief) that return-over-window metrics are confounded by market path — the bank's own caveat that backtests are not proof of live outperformance echoes that exact critique.
- **Cost governance is becoming an executive-level discipline, not an engineering afterthought.** JPMorgan's public model-tiering policy [2] extends the pattern flagged in DataRobot's June survey (2026-06-27 brief) that 72% of practitioners find operating AI costlier than building it [15] — cost-aware model routing is now surfacing on bank earnings calls, not just in platform documentation.
- **Standards stability remains an unresolved procurement risk.** OpenTelemetry's GenAI semantic conventions remain in non-stable "Development" status as of mid-July, with dual-emission via `OTEL_SEMCONV_STABILITY_OPT_IN` still the only production mitigation [10] — teams building observability pipelines on `gen_ai.*` attributes continue to carry schema-migration risk with no committed stabilization date.

## Vendor Landscape

FINOS continued building out its financial-services AI governance stack: the FINOS AI Fund (founding members DTCC, Morgan Stanley, RBC, NatWest) and Project OSERA (Deutsche Bank, Goldman Sachs, Morgan Stanley, RBC, TD Bank Group) both launched in late June, with FDC3 3.0 security and observability features previewed for a near-term release as of the July 6 FINOS community update [11]. Separately, NiCE announced Banco do Brasil's deployment of NiCE Copilot for agentic customer-engagement workflows across its relationship-banking teams — a vendor press release with no independent performance data disclosed [12].

## Sources

1. Bloomberg (July 9, 2026) — https://www.bloomberg.com/news/articles/2026-07-09/jpmorgan-builds-ai-agents-that-beat-60-40-portfolio-in-backtests [Tier 1 — independent journalism]
2. Bloomberg (July 14, 2026) — https://www.bloomberg.com/news/articles/2026-07-14/jpmorgan-urges-staff-to-avoid-deploying-pricey-ai-for-easy-tasks [Tier 1 — independent journalism]
3. Harvard Business Review (July 2026) — https://hbr.org/2026/07/ai-adoption-is-testing-modular-firms [Tier 1 — independent journalism/research]
4. arXiv:2607.07359, Shelby, University of Oxford (July 8, 2026) — https://arxiv.org/abs/2607.07359 [Tier 1 — institutionally affiliated preprint]
5. arXiv:2607.04103, v1–v3 (July 5–16, 2026) — https://arxiv.org/abs/2607.04103 [Affiliation unclear across versions — treated as unverified]
6. Harvard Business Review (July 13, 2026) — https://hbr.org/2026/07/u-s-and-japanese-companies-struggle-with-different-parts-of-ai-adoption-and-offer-different-lessons-for-making-it-work [Tier 1 — independent journalism/research]
7. BusinessWire / MarketScale (July 8–15, 2026) — https://www.businesswire.com/news/home/20260708088519/en/FPT-Releases-Global-Study-on-Scaling-Enterprise-AI [Tier 3 — vendor-commissioned study, flagged]
8. BIS Working Papers No. 1367 (July 14, 2026) — https://www.bis.org/publ/work1367.htm [Tier 1 — standards/analyst body]
9. Federal Reserve Board / FSB (July 7 & July 14, 2026) — https://www.federalreserve.gov/newsevents/speech/bowman20260707a.htm [Tier 1 — regulator primary source]
10. OpenTelemetry semantic-conventions releases and docs (accessed July 2026) — https://github.com/open-telemetry/semantic-conventions/releases [Tier 1 — standards body]
11. FINOS (June 23 – July 6, 2026) — https://www.finos.org/press/finos-launches-ai-fund [Tier 2 — foundation press]
12. BusinessWire / NiCE (July 14, 2026) — https://www.businesswire.com/news/home/20260714494675/en/Banco-do-Brasil-Embeds-Agentic-AI-into-Core-Workflows-to-Strengthen-Relationship-Banking-and-Customer-Engagement [Tier 2 — vendor press release]
13. Gartner (April 2026) — https://www.gartner.com/en/newsroom/press-releases/2026-04-15-gartner-forecasts-worldwide-ai-spending-to-reach-2-59-trillion-in-2026 [Tier 2 — analyst press release, as cited in 2026-07-03 brief]
14. arXiv:2607.03871, "CLQT: A Benchmark for Financial-Services Agentic Reasoning" (July 4, 2026) — https://arxiv.org/abs/2607.03871 [Tier 1 — academic preprint, as cited in 2026-07-04 Agentic Systems brief]
15. DataRobot, "State of AI Costs" survey (June 2026) — https://www.datarobot.com/resources/state-of-ai-costs-2026/ [Tier 2 — vendor-commissioned survey, as cited in 2026-06-27 brief]
