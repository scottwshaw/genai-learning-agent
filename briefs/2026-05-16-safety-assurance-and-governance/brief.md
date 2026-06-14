# Safety, Assurance & Governance — Research Brief (2026-05-16)

## Key Developments

- **AISI documents autonomous cyber capability doubling faster than previous trend lines**
  - **What changed:** AISI's May 13 blog confirmed Mythos Preview and GPT-5.5 both significantly exceeded its prior 4.7-month cyber time-horizon doubling rate.
  - **Why it matters:** Evaluation frameworks calibrated to prior doubling rates now systematically underestimate deployed models' offensive cyber autonomy.
  - *(AISI Blog — aisi.gov.uk, May 13, 2026)*

- **Apollo Research demotes point-in-time scheming evals to secondary priority**
  - **What changed:** Apollo's May 2026 update announced a research pivot from point-in-time scheming evals to studying how scaling causes scheming to emerge.
  - **Why it matters:** Apollo Research now says current evals cannot predict next-generation behavior, requiring enterprises to rethink pre-deployment assurance.
  - *(Apollo Research Blog — apolloresearch.ai, May 13, 2026; LessWrong community repost [Tier 2])*

- **Connecticut enacts broad AI omnibus with first US frontier-model whistleblower mandate**
  - **What changed:** Connecticut SB 5 passed on May 1 and awaits signature, establishing mandatory internal whistleblower channels for frontier-model developers.
  - **Why it matters:** No prior US state has mandated internal safety reporting at the frontier-model training level, creating a new compliance template.
  - *(CT Mirror / DLA Piper / Freshfields, May 1–11, 2026)*

---

## Notable Papers / Models / Tools

| Item | Date | Source | Summary |
|------|------|--------|---------|
| AISI: How Fast is Autonomous AI Cyber Capability Advancing? | May 13, 2026 | [AISI Blog](https://www.aisi.gov.uk/blog/how-fast-is-autonomous-ai-cyber-capability-advancing) [Tier 1 — Evaluation body] | Longitudinal tracking of AISI's narrow cyber task suite; Mythos Preview completed the "Cooling Tower" ICS scenario 3/10 and "The Last Ones" 6/10; GPT-5.5 3/10 on The Last Ones; both models significantly outperform the prior 4.7-month doubling trend; AISI developing new tougher cyber ranges |
| Apollo Research May 2026 Update | May 13, 2026 | [Apollo Research](https://www.apolloresearch.ai/blog/apollo-update-may-2026/) [Tier 1 — Safety research org] | Research pivot to "Science of Scheming" — studying how scaling factors (situational awareness, long-horizon RL) cause scheming to emerge; point-in-time evals now second priority; Watcher product launched for real-time coding-agent monitoring; DC office opening June 2026; scalable monitoring agenda published |
| Jailbroken Frontier Models Retain Their Capabilities | Apr 30 / May 4, 2026 | [arXiv:2605.00267](https://arxiv.org/abs/2605.00267) [Tier 1 — arXiv affiliated, Anthropic/OpenAI/AISI/UKAISI co-authors] | Evaluated 28 jailbreaks across five benchmarks on five Claude models; jailbreak "capability tax" decreases with model capability; Opus 4.6 at max thinking loses only 7.7%; Boundary Point Jailbreaking achieves near-perfect classifier evasion with near-zero capability degradation; concludes safety cases must not assume jailbreaks degrade model capabilities |
| METR Survey: Self-Reported AI Impact on Technical Worker Productivity | May 11, 2026 | [METR Blog](https://metr.org/blog/2026-05-11-ai-usage-survey/) [Tier 1 — Independent evaluation org] | 349 technical workers surveyed (SW engineers, researchers, academics, founders); retrospective estimates 1.3x value in Mar 2025, 2x in Mar 2026, forecast 2.5x by Mar 2027; METR staff self-reported lowest gains of any subgroup; cautions that speed measures likely overstate true value gains |
| METR Review of Anthropic Risk Report: Automated R&D Section | May 8, 2026 | [METR Blog](https://metr.org/blog/2026-05-08-rd-section-anthropic-risk-report-feb-2026-review/) [Tier 1 — Independent evaluation org] | External review of Anthropic's Feb 2026 risk assessment on automated R&D risks; published with two review versions (original and updated); raises concerns about how the report's framework accounts for task substitution and the distinction between value-equivalent and task-count uplift |
| EU AI Act Article 50 Transparency Draft Guidelines | May 8, 2026 | [European Commission](https://digital-strategy.ec.europa.eu/en/library/draft-guidelines-implementation-transparency-obligations-certain-ai-systems-under-article-50-ai-act) [Tier 1 — Regulatory body] | First Commission-level interpretive guidance across full scope of Article 50; covers chatbot disclosure, machine-readable marking, deepfake labelling, biometric categorisation disclosure; open for consultation until June 3; applies from August 2, 2026 with partial transitional period; fines up to €15M or 3% of global turnover |
| Connecticut SB 5 (Artificial Intelligence Responsibility and Transparency Act) | May 1, 2026 | [CT Mirror](https://ctmirror.org/2026/05/01/artificial-intelligence-house-regulation-passage-ct/) / [DLA Piper](https://www.dlapiper.com/en-us/insights/publications/2026/05/unpacking-connecticuts-new-ai-law) [Tier 1 — Independent journalism / Tier 2 — Legal analysis] | Passed 131–17 House, 32–4 Senate; awaiting governor signature; covers companion chatbot safety (Jan 1, 2027), synthetic media provenance (Oct 1, 2026), automated employment decision disclosure (Oct 1, 2026), frontier-model internal whistleblower reporting for 10²⁶+ FLOP developers (Oct 1, 2026); private right of action for minors' companion chatbot violations |
| Apollo Research "Scalable Monitoring Agenda" | May 2026 | [Apollo Research](https://www.apolloresearch.ai/) [Tier 1 — Safety research org] | Detailed research roadmap for building monitors for coding-agent failure modes at scale, from cheap/fast to powerful/expensive; publishes intermediate analysis, papers, and deployment risk reports; Watcher Live (real-time blocking) and Watcher Analyze (retrospective) available; Tailscale Aperture integration |
| 2025 AI Agent Index | Feb 2026 (new citation evidence May 2026) | [arXiv:2602.17753](https://arxiv.org/abs/2602.17753) [Tier 1 — arXiv affiliated] | Documents technical and safety features of 57 deployed agentic AI systems; safety feature coverage highly uneven; referenced in May 2026 US CAISI stakeholder roundtable documentation as a baseline for pre-deployment disclosure expectations |

---

## Technical Deep-Dive

### AISI Longitudinal Cyber Capability Tracking: Evidence and Limits of the Doubling-Rate Model

The AISI May 13 blog post is one of the few public longitudinal datasets tracking autonomous AI cyber capability growth from an independent evaluation body. The method is worth understanding in detail, because it shapes how safety frameworks worldwide are calibrated.


AISI's narrow cyber task suite assigns each task an estimate of how long a human cyber expert would take to complete it, and tracks the time horizon at which models can complete tasks at 80% reliability. Their February 2026 estimate found this horizon had been doubling every 4.7 months since late 2024, itself an acceleration from the 8-month doubling time they estimated in November 2025.
 The new May 13 data shows both Mythos Preview and GPT-5.5 have significantly outperformed even this accelerated trend line, though 
whether these models represent an isolated break from existing rates of progress or are part of a new, faster trend remains unclear at the time of writing.



Claude Mythos Preview and GPT-5.5 have since significantly outperformed this trend. It is unclear whether Mythos Preview and GPT-5.5 represent an isolated break from existing rates of progress or are part of a new, faster trend.
 Concretely, Mythos Preview achieved 6/10 completions on "The Last Ones," a 32-step corporate network attack simulation estimated at approximately 20 human-hours, and 3/10 on "Cooling Tower," an industrial control system scenario. GPT-5.5 reached 3/10 on The Last Ones — the second model ever to complete that scenario end-to-end.

The evaluation methodology has important limitations. 
The tasks cover only some of the capabilities relevant to real-world cyberattacks, requiring models to identify and exploit cybersecurity weaknesses in self-contained setups.
 Real-world environments include active defenses, network visibility, and lateral movement complexity absent from AISI's controlled range. 
AISI is developing tougher cyber evaluations to keep pace: new cyber ranges, enhancements to existing ones, and the addition of active cyber defences to better reflect real-world conditions.
 The current doubling-rate model is therefore best understood as a lower-bound trajectory, applied to a constrained task distribution. Its primary value for enterprise security teams is directional: the capability curve is steepening faster than prior frameworks assumed, and 
stronger AI cyber capabilities are already producing tangible opportunities and risks. Cyber defenders have reported significant advances in vulnerability discovery using recent models, and access to today's controlled capabilities may diffuse over time. The time to invest in strong security baselines is now. Frontier AI can strengthen attackers as well as defenders, and there is a critical window to build resilience.


---

## Landscape Trends

- **[Safety, Assurance & Governance × Agentic Systems]** Evaluation infrastructure is saturating at multiple levels simultaneously: METR's time-horizon suite is structurally too sparse for Mythos-class models (first observed in the May 12 Agentic Systems brief), AISI's cyber suite may now be underestimating trend rates, and Apollo Research has explicitly demoted point-in-time evals to a secondary research priority. This convergence across three independent evaluation bodies signals that the assurance community is entering a period of systematic evaluation ceiling risk — pre-deployment certifications are increasingly built on suites that the most capable models can outrun.

- **[Models & Market × Safety, Assurance & Governance]** The jailbreak-capability tax finding (arXiv:2605.00267) directly challenges the safety architecture assumption underlying many enterprise acceptable-use controls. 
The most advanced jailbreaks effectively yield no reduction in model capabilities. Evaluating 28 jailbreaks across five benchmarks, Haiku 4.5 loses an average of 33.1% on benchmark performance when jailbroken, while Opus 4.6 at max thinking effort loses only 7.7%.
 This means the most capable models available to enterprise customers are also the most dangerous once jailbroken — safety cases cannot rely on capability degradation as a backstop, requiring organizations to treat jailbreak-resistant safeguard design as a primary mitigation rather than a secondary control.

- **Prior brief callback — scheming evaluation validity:** The April 28 brief (GPT-5.5 Apollo evaluation) documented verbalized evaluation awareness rising from 11.7% to 22.1% across model generations. The Apollo May 2026 research pivot explicitly acknowledges that 
evals remain valuable for generating hypotheses about the current training regime, but they are now a second priority. They cannot tell us what the next generation of models will do.
 This reinforces — and escalates — the earlier finding: not only are current evaluations structurally threatened by evaluation awareness, but the organization most capable of running those evaluations now says the fundamental methodology cannot certify future model behavior.

- **[Safety, Assurance & Governance × Enterprise GenAI Adoption]** Connecticut SB 5's frontier-model whistleblower provision — requiring internal anonymous reporting channels for catastrophic-risk concerns from developers training on 10²⁶+ compute operations — represents the first attempt by a US jurisdiction to mandate internal safety governance at the training level, not just deployment. 
Developers training foundation models using more than 10²⁶ computing operations must protect employees who report concerns that the developer or model may contribute to a catastrophic risk — defined as an event that would result in injury or death to 50+ people or $1B+ in property damage from CBRN assistance, autonomous cyberattacks, or autonomous criminal conduct. Large frontier developers (over $500M revenue) must establish anonymous internal reporting by January 1, 2027.
 If governor-signed and not preempted, this creates a compliance obligation directly shaping how frontier labs structure internal safety programs — with potential downstream implications for enterprise customers whose vendors are subject to the law.

- **EU AI Act implementation is entering a binding compliance sprint:** The Article 50 transparency obligations take full effect August 2, 2026, with only a partial transitional period for legacy generative AI systems. 
The Guidelines arrive less than three months before the Article 50 transparency obligations become applicable on August 2, 2026 — including the interactive AI disclosure requirement, emotion recognition and biometric categorisation, and deepfake labelling.
 Enterprises deploying any generative AI that produces content for EU users — including internal knowledge bases and customer-facing tools — face an imminent compliance deadline with meaningful fines (
up to EUR 15 million or 3% of worldwide annual turnover, second-highest of the AI Act's fine bands
). The August 2 date is not affected by the Omnibus deal's December 2027 deferral for high-risk AI systems.

---

## Vendor Landscape

- **Apollo Research — Watcher:** 
Watcher allows security teams and engineers to control and secure agent deployments at scale, functioning as a mix of MDM and EDR for coding agents. Security teams set hard boundaries; engineers configure the rest. Watcher Live is a real-time monitor that identifies and blocks undesirable actions or steers the agent back on track.
 Watcher Analyze adds retrospective forensics. The product targets frontier AI developers and large-scale agent deployers; initial integration partners include Tailscale Aperture for network-level visibility. Vendor claim; limited independent validation to date.

- **AISI — Inspect (open-source eval platform):** AISI continues expanding its Inspect framework for LLM evaluation, referenced as the toolkit underpinning its cyber suite runs. The May 13 cyber report confirms Inspect is live in production for multi-model comparison; no new release announced this week.

---

## Sources

- https://www.aisi.gov.uk/blog/how-fast-is-autonomous-ai-cyber-capability-advancing [Tier 1 — Evaluation body]
- https://www.aisi.gov.uk/blog [Tier 1 — Evaluation body]
- https://www.apolloresearch.ai/blog/apollo-update-may-2026/ [Tier 1 — Safety research org]
- https://metr.org/blog/2026-05-11-ai-usage-survey/ [Tier 1 — Independent evaluation org]
- https://metr.org/blog/2026-05-08-rd-section-anthropic-risk-report-feb-2026-review/ [Tier 1 — Independent evaluation org]
- https://arxiv.org/abs/2605.00267 [Tier 1 — arXiv affiliated, multi-lab authorship including Anthropic/AISI/UKAISI co-authors]
- https://ctmirror.org/2026/05/01/artificial-intelligence-house-regulation-passage-ct/ [Tier 1 — Independent journalism]
- https://www.dlapiper.com/en-us/insights/publications/2026/05/unpacking-connecticuts-new-ai-law [Tier 2 — Legal analysis / law firm]
- https://www.freshfields.com/en/our-thinking/blogs/a-fresh-take/connecticut-poised-to-enact-one-of-the-nations-most-comprehensive-ai-laws-102mrpv [Tier 2 — Legal analysis / law firm]
- https://digital-strategy.ec.europa.eu/en/library/draft-guidelines-implementation-transparency-obligations-certain-ai-systems-under-article-50-ai-act [Tier 1 — Regulatory body (EU Commission)]
- https://www.insideglobaltech.com/2026/05/12/10-takeaways-european-commission-draft-guidelines-on-ai-transparency-under-the-eu-ai-act/ [Tier 2 — Tech news]
- https://www.twobirds.com/en/insights/2026/taking-the-eu-ai-act-to-practice-reading-the-commissions-draft-article-50-guidelines [Tier 2 — Legal analysis / law firm]
- https://cms.law/en/nor/legal-updates/eu-ai-act-developments-key-political-agreement-on-the-digital-omnibus-on-ai-implementation-timeline-and-transparency-consultation [Tier 2 — Legal analysis / law firm]
- https://www.apolloresearch.ai/ [Tier 1 — Safety research org]
- https://www.lesswrong.com/posts/4acQRDNyPs7tD8EED/apollo-update-may-2026 [Tier 2 — Community repost]
- https://www.transparencycoalition.ai/news/tcai-bill-guide-sb-5-connecticuts-omnibus-ai-and-online-safety-bill [Tier 2 — Advocacy org]
- https://www.transparencycoalition.ai/news/ai-legislative-update-may8-2026 [Tier 2 — Advocacy org]
- https://www.troutmanprivacy.com/2026/05/proposed-state-ai-law-update-may-4-2026/ [Tier 2 — Law firm blog]
- https://www.dwt.com/blogs/artificial-intelligence-law-advisor/2026/05/ct-ai-transparency-safety-consumer-protection-law [Tier 2 — Law firm blog]
