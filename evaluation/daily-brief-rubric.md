---
dimensions:
  - key: recency_novelty
    label: "Recency And Novelty"
    weight: 20
  - key: topic_boundary
    label: "Topic Boundary Discipline"
    weight: 15
  - key: cross_topic_synthesis
    label: "Cross-Topic Trend Synthesis"
    weight: 10
  - key: source_quality
    label: "Source Quality And Source Discipline"
    weight: 15
  - key: executive_scanability
    label: "Executive Scanability Of Key Developments"
    weight: 10
  - key: controlled_depth
    label: "Controlled Technical Depth In Deep-Dive And Landscape Trends"
    weight: 5
  - key: audience_relevance
    label: "Audience Relevance"
    weight: 10
  - key: analytical_strength
    label: "Analytical Strength And Synthesis"
    weight: 10
  - key: format_compliance
    label: "Format Compliance And Structural Execution"
    weight: 5
---

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

### 3. Cross-Topic Trend Synthesis — 10%

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
- Comparative claims such as "leading", "most complete", or "best-in-class" are either avoided or explicitly supported by strong independent evidence.

**Score 3**

- Source quality is mixed.
- Some important points rely too much on vendor or secondary reporting.
- Source tiers are mostly respected but not consistently.
- One or more comparative or market-judgment claims rely on weak or vendor-adjacent evidence.

**Score 1**

- Weak or promotional sources drive the brief.
- Major claims lack credible support.
- The brief shows little discipline in source weighting.
- Vendor positioning language is repeated as if it were established fact.

**What to look for**

- Are analytical claims supported by high-quality evidence?
- Is vendor content treated as fact-reporting, not proof?
- Are comparative claims backed by independent evidence, or are they just vendor framing?

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

### 6. Executive Scanability Of Key Developments — 10%

Assesses whether the top section functions as a fast executive scan rather than a compressed long-form summary. Judge scan efficiency, not raw sentence count alone.

**Score 5**

- Each `Key Developments` item is quickly skimmable.
- Headlines communicate significance, not just events.
- The body under each headline is concise and efficient; `2-3` short sentences can still score highly if each sentence does distinct work.
- Each item includes only the essential fact, why it matters, and a small number of supporting details or numbers.
- Detailed mechanism, caveats, and extended evidence are deferred to the `Technical Deep-Dive`, `Landscape Trends`, tables, or sources.
- Bullets avoid redundancy, repeated source setup, and mini-deep-dive behavior.
- A brief should not receive `5` if any `Key Developments` item reads like a mini-essay or requires rereading to extract the point.

**Score 3**

- Headlines are strong, but several items contain extra setup, repeated framing, or more detail than needed for a scan section.
- Some bullets read like compressed mini-essays, include too many metrics, or begin duplicating later sections.
- A reader can understand the section, but not quickly.
- This is the default score when the section is readable overall but inefficient to scan.

**Score 2**

- Most `Key Developments` items require sustained reading because they combine multiple implications, repeated factual setup, or too much supporting detail.
- Strong headlines are doing most of the readability work while the body text remains hard to scan.
- Multiple bullets would be better split between `Key Developments` and later sections.

**Score 1**

- `Key Developments` reads like a set of mini-essays.
- Multiple items are long enough that the section no longer supports rapid scanning.
- Important points are buried in explanatory prose rather than surfaced immediately.

**What to look for**

- Can an AI-literate executive skim the section in under `90` seconds?
- Does each item state the point before the evidence?
- Is the section efficient to scan, or does it require rereading because of redundancy or stacked implications?
- Do not award a high score based on strong bolded headlines alone; evaluate the full body text under each bullet.
- Do not penalize a bullet just for having `3` concise sentences; penalize redundancy, repeated setup, and detail that belongs later in the brief.
- If one or more bullets clearly function as compressed deep-dives, cap the score at `3`; if this is true for most bullets, score `2` or below.

### 7. Controlled Technical Depth In Deep-Dive And Landscape Trends — 5%

Assesses whether the `Technical Deep-Dive` and `Landscape Trends` are substantively useful without becoming overloaded, implementation-level, or repetitive.

**Score 5**

- The `Technical Deep-Dive` adds real substance beyond the top section.
- `Landscape Trends` stays analytical and synthetic rather than re-reporting the same facts.
- Technical detail is informative, precise, and appropriately scoped for a senior AI leader or senior ML engineer.
- The references, not the prose, carry the burden of exhaustive detail.

**Score 3**

- The section quality is mixed: useful overall, but either too thin, too detailed, or somewhat repetitive.
- Some material that belongs in the sources or table is pulled into the prose unnecessarily.

**Score 1**

- The deep-dive is either superficial or overloaded.
- `Landscape Trends` mostly repeats earlier sections.
- The prose reads more like release notes, a product explainer, or an implementation document than a strategic brief.

**What to look for**

- Does the deep-dive teach the reader something meaningful beyond the top bullets?
- Is the detail concentrated where it is most valuable?
- Do `Landscape Trends` synthesize rather than restate?

### 8. Analytical Strength And Synthesis — 10%

Assesses whether the brief interprets developments and explains why they matter, rather than merely summarizing announcements or papers.

**Score 5**

- The brief consistently explains significance, implications, and signals.
- It synthesizes across sources rather than restating them.
- Trend statements are specific and defensible.
- It avoids overclaiming; comparative judgments are carefully scoped and evidenced.

**Score 3**

- Some analysis is present, but parts of the brief remain descriptive.
- Significance is stated unevenly or too generically.
- Some conclusions are stronger than the cited evidence warrants.

**Score 1**

- The brief mostly summarizes events.
- It does not show much judgment, synthesis, or interpretation.
- Or it makes sweeping leadership or maturity claims that are not defensible from the evidence.

**What to look for**

- Does the brief tell the reader what matters and why?
- Are conclusions drawn from evidence rather than asserted vaguely?
- Does the brief distinguish "important product signal" from "category leader" or "market winner"?

### 9. Format Compliance And Structural Execution — 5%

Assesses whether the brief follows the required structure and uses each section properly.

**Score 5**

- All required sections are present and correctly used.
- `Key Developments`, `Technical Deep-Dive`, `Landscape Trends`, and `Sources` all perform their intended roles.
- `Key Developments` summarizes rather than absorbing the work of the `Technical Deep-Dive` or `Landscape Trends`.
- The brief is easy to scan and internally coherent.
- Do not award `5` if the top section is structurally correct but functionally overloaded.

**Score 3**

- Minor format deviations or uneven section quality.
- One section is structurally correct but doing too much of another section's job.
- Structure is mostly intact but some sections underperform.

**Score 1**

- Missing sections, incorrect structure, or clear misuse of the template.

**What to look for**

- Did the model follow the brief format exactly?
- Are sections distinct, or do they collapse into the same kind of content?
- Do any `Key Developments` bullets function like mini deep-dives?
- If `Key Developments` is doing the work of the deep-dive, reduce this score even if the headings are present.

## Suggested Weighted Scorecard

- Recency And Novelty: `20`
- Topic Boundary Discipline: `15`
- Cross-Topic Trend Synthesis: `10`
- Source Quality And Source Discipline: `15`
- Executive Scanability Of Key Developments: `10`
- Controlled Technical Depth In Deep-Dive And Landscape Trends: `5`
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
- Did it avoid unsupported "leading / most complete / best-in-class" claims?
- Was the top of the brief genuinely scannable, not just well-headlined?
- Was the deep-dive and landscape analysis substantive without becoming excessive?
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
