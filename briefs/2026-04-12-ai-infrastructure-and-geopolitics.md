# AI Infrastructure & Geopolitics — Research Brief (2026-04-12)

## Key Developments

- **The Strait of Hormuz crisis has exposed TSMC's LNG dependency as a direct AI supply-chain vulnerability**
  - **What changed:** Iran's closure of the Strait since March 4 cut off ~30% of Taiwan's LNG supply; TSIA formally called for helium and LNG strategic reserves as Taiwan's stockpile fell to roughly 11 days.
  - **Why it matters:** Any production slowdown at TSMC directly throttles the global pipeline for Nvidia GPUs, AMD AI chips, and all advanced AI silicon.
  - *(Tom's Hardware / Atlantic Council / TSIA, April 8–9, 2026)*

- **TSMC reported 45% YoY March revenue growth on April 10, confirming AI demand has not yet hit a supply ceiling**
  - **What changed:** TSMC disclosed March 2026 revenue of NT$415.19 billion — a 45.2% YoY and 30.7% sequential increase — with Q1 2026 totalling NT$1,134.10 billion, beating Bloomberg consensus.
  - **Why it matters:** Record demand met by a booked-out foundry confirms that AI compute supply is constrained at the wafer level, not the capital or demand level.
  - *(TSMC official filing / SemiWiki / Invezz, April 10, 2026)*

- **BIS staffing attrition is creating a bureaucratic bottleneck that now threatens the chip export expansion Trump wants**
  - **What changed:** Bloomberg reported on April 10 that licensing bottlenecks and staff attrition at the Bureau of Industry and Security are undermining the administration's goal of boosting global US chip sales.
  - **Why it matters:** Even where policy permits exports — to the Middle East, to allied nations — the administrative machinery to approve them is degrading, creating delays that advantage non-US suppliers.
  - *(Bloomberg, April 10, 2026)*

- **NSW fast-tracked A$51.9 billion in data center projects via its Investment Delivery Authority, the largest sovereign AI infrastructure commitment in the Asia-Pacific**
  - **What changed:** The NSW government endorsed 15 data center projects worth A$51.9 billion through its Investment Delivery Authority on approximately March 27, including NextDC's S7 facility and the S4 and S5 campuses.
  - **Why it matters:** Paired with the federal government's March 23 Expectations framework, Australia now has both approved project pipelines and regulatory conditions for sovereign AI infrastructure at meaningful scale.
  - *(NSW Government / W.Media / Govtech Review, March 27, 2026)*

---

## Notable Papers / Models / Tools

| Item | Date | Source | Summary |
|------|------|--------|---------|
| TSMC March 2026 Revenue Disclosure | Apr 10, 2026 | [TSMC Official / SemiWiki](https://semiwiki.com/forum/threads/tsmc-march-2026-revenue-report.24915/) | NT$415.19B in March; Q1 total NT$1,134.10B (+35.1% YoY); beats consensus; full earnings call April 16 expected to address LNG/supply chain risk |
| Bloomberg: BIS Staffing & Chip Export Bottleneck | Apr 10, 2026 | [Bloomberg](https://www.bloomberg.com/news/articles/2026-04-10/trump-s-ai-chip-export-push-stymied-by-bureaucratic-bottleneck) | BIS tasked with Nvidia Middle East/China vetting plus tariff industry probes simultaneously; staffing attrition undermining licensing throughput |
| Anthropic 3.5 GW Google TPU Deal (Broadcom SEC Filing) | Apr 7, 2026 | [TechCrunch](https://techcrunch.com/2026/04/07/anthropic-compute-deal-google-broadcom-tpus/) / [The Register](https://www.theregister.com/2026/04/07/broadcom_google_chip_deal_anthropic_customer/) | Broadcom SEC filing reveals Anthropic committed to 3.5 GW of next-gen TPU capacity starting 2027; tripling October 2025 deal; US-domiciled; conditioned on Anthropic's commercial performance |
| NSW IDA: 15 Data Center Projects Endorsed | ~Mar 27, 2026 | [NSW Government](https://www.nsw.gov.au/ministerial-releases/data-centre-investment-sustainable-development) / [W.Media](https://w.media/nsw-moves-15-data-centres-worth-aud-51-9bn-into-ida-pipeline/) | A$51.9 billion endorsed pipeline; NextDC S7/S4/S5, Stockland/EdgeConneX Kemps Creek, Stack Infrastructure Penrith among projects; ~A$40.7B of proposals rejected as speculative |
| Australian Federal Expectations for Data Centres & AI | Mar 23, 2026 | [Dept. Industry Science and Resources](https://www.industry.gov.au/publications/expectations-data-centres-and-ai-infrastructure-developers) | Non-binding but policy-enforceable national expectations: sovereignty, energy transition, water security, local capability investment required for preferential regulatory access |
| 2026 Strait of Hormuz Crisis — AI Infrastructure Implications | Mar–Apr 2026 | [Atlantic Council](https://www.atlanticcouncil.org/blogs/energysource/the-iran-war-tests-taiwans-energy-resilience/) / [Tom's Hardware](https://www.tomshardware.com/tech-industry/taiwanese-chip-makers-call-on-government-to-stockpile-helium-lng-tsia-pleads-for-strategic-supplies-as-us-and-iran-sign-ceasefire-in-middle-east) | Qatar helium shutdown threatens chip manufacturing; TSMC has ~11 days strategic LNG; Taiwan imports ~30% of LNG through strait; TSIA urges government reserves |
| TSMC Advanced Capacity Booked Through 2028 | Mar 31, 2026 | [Dataconomy](https://dataconomy.com/2026/03/31/tsmcs-advanced-chip-capacity-is-booked-out-through-2028/) | 2nm and 3nm fully booked; Apple holds 50%+ of early 2nm allocation; TSMC suspended new 3nm kick-offs |
| Broadcom: Google TPU v7 "Ironwood" Design Agreement | Apr 6, 2026 | [FinancialContent](https://markets.financialcontent.com/stocks/article/marketminute-2026-4-9-broadcom-cemented-as-ai-infrastructure-backbone-with-landmark-2031-google-and-anthropic-deals) | Broadcom confirmed as lead design partner for Google's 7th-gen TPU; 3nm process; 4× performance over prior generation; long-term supply deal through 2031 |

---

## Technical Deep-Dive

**The Strait of Hormuz Crisis as an AI Infrastructure Stress Test**

The Strait of Hormuz closure since March 4 has revealed that the global AI semiconductor supply chain contains a second-order energy vulnerability that most infrastructure risk analyses had underweighted: TSMC's dependence on Qatari LNG. 
Taiwan manufactures roughly 90% of the world's most advanced semiconductors and imports approximately one-third of its LNG from Middle Eastern suppliers.
 
Taiwan shut down its last nuclear power plant in May 2025 and now relies on imports for over 95% of its energy needs, with approximately 11 days of strategic LNG supplies — the fuel used by more than 40% of its power plants — and no helium stockpiles.


The vulnerability has two components. The first is power stability: TSMC's advanced fabs require uninterrupted electricity to maintain fabrication yields. 
The LNG and sulfuric acid threats cut close to the core of TSMC's business model because advanced fabs depend on highly reliable power, and an estimated 11-day LNG gap could raise the risk of power curbs that interrupt production at precisely the time TSMC is supplying high-value AI chips.
 The second is helium — a non-substitutable process gas used in cooling and lithography. 
Helium is vital to chip fabrication and plays a key role in both cooling and lithography; Qatar accounts for about one-third of the world's helium supply, and Taiwan imports it from the United States and Qatar, which are abundant in natural gas fields.


The crisis is directly compounding an already capacity-constrained foundry environment. 
TSMC's advanced manufacturing capacity is fully booked through 2028, with major customers like Nvidia, Apple, AMD, and Qualcomm having reserved all slots for its 2-nanometer process, while the 3nm node has reached full utilization.
 
Nvidia alone is said to have booked a majority of TSMC's CoWoS capacity through 2027, and TSMC plans to quadruple CoWoS output to around 130,000 wafers per month by late 2026.


The immediate operational implication for enterprise AI teams is indirect but real: any disruption to TSMC's production schedule propagates into GPU waitlists and delays for the Vera Rubin generation of chips. 
Taiwan has secured sufficient LNG supplies to meet consumption needs through April, but the expected summer surge in electricity demand could create severe energy shortages if shipments through the Strait of Hormuz do not resume soon.
 
The Taiwan Semiconductor Industry Association has called on the government to build a strategic supply of helium and LNG; TSIA SVP Cliff Hou stated that the association supports the government's decision to reopen nuclear power plants to have more stable energy supplies.
 The April 8 ceasefire — under which the Strait technically reopened but Iran continued levying tolls above $1 million per vessel — has not yet resolved the supply shortfall. 
On April 8, a temporary ceasefire was agreed that was to involve the re-opening of the strait; however, by the following day the Strait of Hormuz remained "effectively closed, with Iran limiting the number of ships that can cross and charging tolls of over $1 million per ship."
 This situation means TSMC's April 16 Q1 earnings call — which will address energy contingency planning and supply chain resilience — is the single most important near-term signal for AI compute availability.

---

## Landscape Trends

- **[AI Infrastructure & Geopolitics × Models & Market]** The Anthropic 3.5 GW TPU deal — disclosed only through a Broadcom SEC filing rather than Anthropic's own announcement — is the clearest signal yet that frontier AI labs are securing infrastructure at sovereign-scale power commitments years in advance. 
The October 2025 predecessor deal established the baseline of more than 1 gigawatt from one million TPUs, and the expansion to 3.5 gigawatts in under six months underscores how rapidly demand for Claude has outstripped initial projections.
 
Broadcom's filing revealed that Anthropic, starting in 2027, "will access through Broadcom approximately 3.5 gigawatts as part of the multiple gigawatts of next generation TPU-based AI compute capacity committed by Anthropic," with full deployment contingent on Anthropic's continued commercial success.
 The implication for enterprise teams: compute access is now a strategic dependency variable — not just a cost variable — that shapes which model providers can sustain frontier capability over a five-year horizon.

- **[AI Infrastructure & Geopolitics × Safety, Assurance & Governance]** Australia's dual-track approach — federal Expectations (March 23) plus NSW's A$51.9 billion IDA pipeline (March 27) — is the most concrete post-March-30 development for sovereign AI compute in the Asia-Pacific, but it is structured around governance conditions rather than just capacity. 
The Expectations do not replace existing laws or create new regulatory obligations; instead, they operate as a policy lens through which Commonwealth regulatory assessments and investment facilitation decisions are prioritised, with proposals that align closely more likely to receive coordinated and timely regulatory consideration.
 
The next phase of data center expansion will be negotiated, not assumed, shifting the bottleneck from capital to compliance.
 For regulated Australian enterprises, this means hyperscaler GPU-enabled regions remain months to years away, but the neocloud and colocaton path (Sharon AI, NextDC M4, CDC) is accelerating with genuine government backing.

- **Prior brief callback (March 25 brief):** The March 25 brief noted that Commerce's withdrawal of the draft global chip permit rule left US export policy toward allied nations "in regulatory limbo." 
That limbo has now worsened: Bloomberg's April 10 report confirms that BIS — the agency responsible for both Nvidia's Middle East export vetting and the industry tariff probes — is experiencing staffing attrition and lacks clear policy direction, creating licensing bottlenecks that now threaten even approved chip sales.
 Rather than resolving the March uncertainty, the situation has deteriorated: the enforcement capacity gap is now the binding constraint on US export expansion, not just the policy framework gap.

- **[AI Infrastructure & Geopolitics × Enterprise GenAI Adoption]** The TSMC capacity crunch is no longer abstract for enterprise AI teams: 
Broadcom has identified TSMC's output as a chokepoint for the entire supply chain, with Apple estimated to hold over 50% of the early 2nm allocation for 2026 and 2027, which limits availability for other customers.
 Combined with the Hormuz energy risk, enterprises building GPU procurement roadmaps for 2027 onward should treat chip availability as a planning constraint with multi-year lead times, not a spot-market assumption. The SemiAnalysis note (via CNBC January 2026) that TSMC's "silicon shield" will remain strong through the end of the decade suggests no rapid diversification to Samsung or Intel Foundry will bridge the gap.

- **The BIS capacity crisis maps onto a broader pattern of institutional under-resourcing across AI governance.** The April 10 Bloomberg report on BIS staffing attrition is a US-specific instance of a pattern the Safety & Governance briefs have been tracking since March: 
Trump's goal of significantly boosting global sales of American AI chips risks being undermined by licensing bottlenecks, staffing attrition and a lack of policy direction at the federal agency that oversees exports of billions of dollars in sensitive US technology.
 The CSA's April 2 finding that NIST AI agent standards are 12+ months from completion belongs to the same dynamic: the institutions charged with governing AI infrastructure expansion are under-resourced relative to the pace of that expansion.

---

## Vendor Landscape

- **Broadcom** has been confirmed through a Broadcom SEC filing as the lead design partner for Google's next-generation TPU ("Ironwood," 7th-gen, 3nm process), and as the implementation layer delivering 3.5 GW of that compute to Anthropic from 2027. A separate 10 GW co-development deal with OpenAI announced in October 2025 makes Broadcom the common silicon implementation layer for both leading US frontier labs — a structural competitive position against Nvidia. Broadcom shares rose over 6% on April 7.

- **NextDC** secured NSW IDA endorsement for three projects (S7 Eastern Creek, S4 Fairfield, S5 Ryde) as part of the A$51.9 billion tranche. The S7 facility, co-developed with OpenAI, targets up to 650 MW of Tier IV capacity. NextDC's M4 Fishermans Bend (Melbourne, 150 MW liquid-cooled) received final approval in January 2026 and is the current leading near-term Blackwell-density location in sovereign Australian territory.

- **Sharon AI / Lenovo** (covered in March 30 brief): the 1,000-GPU B200 Melbourne cluster at NEXTDC M3 remains the only confirmed Blackwell-class sovereign Australian deployment known to be in delivery. The Sharon AI + Cisco 1,024-GPU Blackwell Ultra Secure AI Factory (February 23) represents a second near-term option for enterprises requiring Australian sovereign GPU capacity ahead of hyperscaler regions.

---

## Sources

- https://semiwiki.com/forum/threads/tsmc-march-2026-revenue-report.24915/ [Tier 2 — Tech news / TSMC official filing]
- https://www.bloomberg.com/news/articles/2026-04-10/trump-s-ai-chip-export-push-stymied-by-bureaucratic-bottleneck [Tier 1 — Independent journalism]
- https://techcrunch.com/2026/04/07/anthropic-compute-deal-google-broadcom-tpus/ [Tier 1 — Independent journalism]
- https://www.theregister.com/2026/04/07/broadcom_google_chip_deal_anthropic_customer/ [Tier 1 — Independent journalism]
- https://www.nsw.gov.au/ministerial-releases/data-centre-investment-sustainable-development [Tier 2 — Government announcement]
- https://w.media/nsw-moves-15-data-centres-worth-aud-51-9bn-into-ida-pipeline/ [Tier 2 — Tech news]
- https://www.industry.gov.au/publications/expectations-data-centres-and-ai-infrastructure-developers [Tier 2 — Government policy document]
- https://www.atlanticcouncil.org/blogs/energysource/the-iran-war-tests-taiwans-energy-resilience/ [Tier 1 — Independent journalism / think tank]
- https://www.tomshardware.com/tech-industry/taiwanese-chip-makers-call-on-government-to-stockpile-helium-lng-tsia-pleads-for-strategic-supplies-as-us-and-iran-sign-ceasefire-in-middle-east [Tier 2 — Tech news]
- https://dataconomy.com/2026/03/31/tsmcs-advanced-chip-capacity-is-booked-out-through-2028/ [Tier 2 — Tech news]
- https://www.ibtimes.com.au/tsmc-shares-surge-past-2000-twd-ai-demand-fuels-record-q1-revenue-surge-1866048 [Tier 2 — Tech/finance news]
- https://markets.financialcontent.com/stocks/article/marketminute-2026-4-9-broadcom-cemented-as-ai-infrastructure-backbone-with-landmark-2031-google-and-anthropic-deals [Tier 2 — Tech news]
- https://www.tomshardware.com/tech-industry/broadcom-expands-anthropic-deal-to-3-5gw-of-google-tpu-capacity-from-2027 [Tier 2 — Tech news]
- https://winbuzzer.com/2026/04/09/anthropic-triples-google-tpu-deal-to-35gw-as-revenue-hits-30-xcxwbn/ [Tier 2 — Tech news]
- https://www.cnbc.com/2026/04/10/china-taiwan-reunification-cross-strait-relations-trump-visit-may-.html [Tier 1 — Independent journalism]
- https://www.ussc.edu.au/powering-the-cloud-data-centres-and-the-future-of-australias-grid [Tier 1 — Independent research (US Studies Centre)]
- https://www.hsfkramer.com/insights/2026-03/national-expectations-for-the-development-of-data-centres-and-ai-infrastructure-have-been-released-what-you-need-to-know [Tier 2 — Legal/policy analysis]
- https://en.wikipedia.org/wiki/2026_Strait_of_Hormuz_crisis [Tier 2 — Aggregated news; cross-checked against primary sources]
- https://www.indmoney.com/blog/us-stocks/us-iran-war-threatening-taiwan-world-semiconductor-chip-supply [Tier 2 — Financial news]
- https://finance.yahoo.com/markets/stocks/articles/geopolitical-tension-puts-tsmc-valuation-140635317.html [Tier 2 — Financial analysis]
- https://www.wccftech.com/tsmc-is-set-to-talk-about-the-biggest-risk-it-faces-with-chip-production/ [Tier 2 — Tech news]
- https://www.cnbc.com/2026/01/19/us-taiwan-chip-deal-silicon-shield-tsmc-trump-tapei-ai-semiconductor-supply-chain.html [Tier 1 — Independent journalism]
- https://www.bis.doc.gov/index.php/about-bis/newsroom/press-releases [Tier 2 — Government (BIS official)]
- https://www.mordorintelligence.com/industry-reports/australia-hyperscale-data-center-market [Tier 3 — Vendor/analyst marketing; used only for factual project timeline cross-checks]
