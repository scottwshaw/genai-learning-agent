# Daily Brief Evaluation Rubric

This rubric is designed to assess how well each brief fulfills the intent of the current research prompt, not just whether it is well-written. It emphasizes novelty, topic discipline, source quality, useful synthesis, and the right level of abstraction for a senior technical reader who also needs executive-scan readability.

## Scoring Method

Score each dimension on a `1-5` scale:

- `5` = excellent, consistently meets intent
- `4` = strong, minor gaps
- `3` = acceptable, mixed execution
- `2` = weak, materially misses intent
- `1` = poor, fails the dimension

Suggested overall score: weighted average out of `100`.

## Rubric Dimensions

### 1. Recency And Novelty — 20%

Assesses whether the brief surfaces genuinely new developments, with strong preference for the last 7-14 days, and avoids repeating material already covered in prior briefs.

**Score 5**

- Nearly all key items are recent and clearly newer than the prior coverage baseline.
- The brief avoids resurfacing previously covered developments unless there is a meaningful update.
- Newness is evident not just by date, but by substance.

**Score 3**

- Most items are recent, but one or more feel recycled or only marginally updated.
- Some novelty is present, but the brief does not consistently distinguish new developments from already-covered ones.

**Score 1**

- The brief substantially repeats prior material.
- Items are stale, weakly justified, or do not appear meaningfully new relative to previous briefs.

**What to look for**

- Does the brief actually answer "what changed since the previous brief date?"
- Are "new" items materially new, or just newly noticed?

### 2. Topic Boundary Discipline — 15%

Assesses whether the brief stays centered on its assigned topic and avoids poaching developments that belong primarily in another topic area.

**Score 5**

- The source mix and selected developments are clearly anchored in the assigned topic.
- Overlap with adjacent topics is minimal.
- If a development touches multiple domains, the brief explains the topic-specific angle clearly.

**Score 3**

- The brief is mostly on-topic but includes some items that feel better suited to another topic.
- Topic ownership is somewhat blurry.

**Score 1**

- The brief drifts heavily into another topic's territory.
- It reuses cross-topic news without a clear reason this topic should own it.

**What to look for**

- Could the same "new information" have appeared unchanged in another topic's brief?
- Is the brief discovering topic-specific developments, not just topic-adjacent news?

### 3. Cross-Topic Trend Synthesis — 15%

Assesses whether the brief uses other recent briefs to identify broader patterns without duplicating their discoveries.

**Score 5**

- The brief clearly distinguishes new topic-specific developments from broader cross-topic trends.
- It explicitly identifies when current developments reinforce, extend, or challenge patterns seen in other briefs.
- Cross-topic connections are analytical, not superficial.

**Score 3**

- Some cross-topic linkage is present, but it is generic or lightly developed.
- The brief notices broad patterns but does not articulate them sharply.

**Score 1**

- The brief is siloed and ignores broader trends, or it duplicates material from other briefs without adding cross-topic insight.

**What to look for**

- Does it say what this brief adds to a larger pattern?
- Does it connect trends across topics without re-reporting the same discoveries?

### 4. Source Quality And Source Discipline — 15%

Assesses whether the brief relies on strong sources appropriately and uses weaker sources only for limited factual purposes.

**Score 5**

- Key claims are grounded primarily in Tier 1 sources.
- Tier 2 sources are used carefully for factual developments only.
- Tier 3 sources are avoided or clearly flagged.
- Source selection reflects judgment, not convenience.

**Score 3**

- Source quality is mixed.
- Some important points rely too much on vendor or secondary reporting.
- Source tiers are mostly respected but not consistently.

**Score 1**

- Weak or promotional sources drive the brief.
- Major claims lack credible support.
- The brief shows little discipline in source weighting.

**What to look for**

- Are analytical claims supported by high-quality evidence?
- Is vendor content treated as fact-reporting, not proof?

### 5. Audience Relevance — 10%

Assesses whether the brief is useful to the intended reader: a senior ML engineer focused on observability, evaluation, governance, and production GenAI systems in enterprise settings.

**Score 5**

- The brief consistently emphasizes operational, governance, platform, tooling, or enterprise significance.
- It filters developments through the reader's actual priorities.
- It avoids irrelevant fascination with low-level details unless they matter operationally.

**Score 3**

- The brief is partly relevant, but some emphasis drifts toward general AI news or research curiosity.
- Reader fit is present but not consistently sharp.

**Score 1**

- The brief does not feel tailored to the intended reader.
- It prioritizes the wrong kinds of developments.

**What to look for**

- Does the significance framing match the reader's role?
- Would this brief help someone making practical enterprise judgments?

### 6. AI-Executive Readability With Controlled Technical Depth — 15%

Assesses whether the brief operates at the right level of abstraction for a senior AI leader: easy to scan at the top, technically informative in the prose, but not overloaded or overly tool-parochial.

**Score 5**

- `Key Developments` are easy for an AI-literate executive to scan quickly.
- Standard field terminology is used precisely where it improves clarity.
- Headlines communicate significance, not just events.
- Technical details are informative without collapsing into release-note detail or implementation-level density.
- The deep-dive adds real substance without becoming an implementation document.
- The references, not the prose, carry the burden of exhaustive detail.

**Score 3**

- The brief is understandable for the intended audience, but some sections are too dense, too tool-specific, too thin, or too detailed.
- The abstraction level is inconsistent.

**Score 1**

- The brief is either too vague for an informed AI leader or too deep in the weeds to function as a strategic brief.
- Headlines read like changelogs or assume product-specific context without framing.

**What to look for**

- Can an AI-literate executive understand the top section quickly?
- Does the brief use standard field jargon productively rather than performatively?
- Can a technical reader still learn something meaningful without reading the sources?

### 7. Analytical Strength And Synthesis — 10%

Assesses whether the brief interprets developments and explains why they matter, rather than merely summarizing announcements or papers.

**Score 5**

- The brief consistently explains significance, implications, and signals.
- It synthesizes across sources rather than restating them.
- Trend statements are specific and defensible.

**Score 3**

- Some analysis is present, but parts of the brief remain descriptive.
- Significance is stated unevenly or too generically.

**Score 1**

- The brief mostly summarizes events.
- It does not show much judgment, synthesis, or interpretation.

**What to look for**

- Does the brief tell the reader what matters and why?
- Are conclusions drawn from evidence rather than asserted vaguely?

### 8. Format Compliance And Structural Execution — 5%

Assesses whether the brief follows the required structure and uses each section properly.

**Score 5**

- All required sections are present and correctly used.
- `Key Developments`, `Technical Deep-Dive`, `Landscape Trends`, and `Sources` all perform their intended roles.
- The brief is easy to scan and internally coherent.

**Score 3**

- Minor format deviations or uneven section quality.
- Structure is mostly intact but some sections underperform.

**Score 1**

- Missing sections, incorrect structure, or clear misuse of the template.

**What to look for**

- Did the model follow the brief format exactly?
- Are sections distinct, or do they collapse into the same kind of content?

## Suggested Weighted Scorecard

- Recency And Novelty: `20`
- Topic Boundary Discipline: `15`
- Cross-Topic Trend Synthesis: `15`
- Source Quality And Source Discipline: `15`
- AI-Executive Readability With Controlled Technical Depth: `15`
- Audience Relevance: `10`
- Analytical Strength And Synthesis: `10`
- Format Compliance And Structural Execution: `5`

Total: `100`

## Recommended Evaluation Questions

For each brief, an evaluator should be able to answer these quickly:

- Did this brief surface genuinely new information?
- Did it stay within its topic without duplicating another topic's discoveries?
- Did it connect to broader trends across topics where appropriate?
- Were the sources credible and used with discipline?
- Was the top of the brief readable to an AI-literate executive?
- Was the technical prose substantive without becoming excessive?
- Did the brief explain why the developments matter?
- Did it follow the required structure cleanly?

## Practical Interpretation

A strong brief should score well on both of these at once:

- `Topic Boundary Discipline`
- `Cross-Topic Trend Synthesis`

That combination is important because you want:

- orthogonal discovery across topics
- integrated understanding across the portfolio of briefs

You do not want:

- the same news item reappearing across topics
- isolated briefs that fail to reveal broader shifts
