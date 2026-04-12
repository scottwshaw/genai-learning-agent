You are revising a research brief to fix specific compliance violations identified by a reviewer. Fix **only** the listed violations. Do not rewrite compliant sections, add new research, remove correctly-included developments, or change the analytical framing of content that was not flagged.

The brief's topic is **{{TOPIC_LABEL}}**.
Today's date is {{DATE}}.

## Rules for Revision

**Removal rules (these are mandatory — the item must be deleted from Key Developments, not softened):**

- `non_event_rule` → **Remove the bullet entirely** from Key Developments.
- `topic_boundary` → **Remove the bullet entirely** from Key Developments.
- `vendor_source_gate` → **Remove the bullet entirely** from Key Developments. A Key Development sourced only from the vendor's own materials (blog, docs, release notes, GitHub, package registry) cannot be fixed by rewording — it must be removed. Move the factual content to `Notable Papers / Models / Tools` or `Vendor Landscape` if not already there.
- `quiet_week` → Reduce Key Developments to at most 2 items. Remove the least significant bullets first. Add a quiet-week note at the top of the section.

For any removed Key Development: if it contains useful context, you may add a brief mention in `Landscape Trends` — but only if it fits naturally. Do not force it.

**Rewrite rules (fix in place):**

- `word_count` → Cut the field to under 20 words. Prefer cutting detail over compressing with semicolons or em-dashes.
- `format_structure` → Fix the headline to 8–12 words stating a consequence or signal, not an event name.
- `sentence_simplicity` → Rewrite as a single independent clause. Drop the second fact.
- `source_tier_flag` → Add `[Tier 2 sources only]` to the source parenthetical.
- `cross_topic_requirement` → Add bold `[Topic A × Topic B]` tags to at least 2 Landscape Trends bullets, ensuring they genuinely name two topics and trace a cross-topic connection.
- `prior_brief_callback` → Add a reference to a prior brief pattern in one Landscape Trends bullet.
- `comparative_claim` → Weaken to scoped language or remove the claim. Do not invent Tier 1 evidence.

Preserve the exact markdown structure, section order, and formatting of all unflagged content.

## Output Discipline

Your output must begin **immediately** with:

`# {{TOPIC_LABEL}} — Research Brief ({{DATE}})`

No preamble. No commentary. No "Here is the revised brief." Just the revised brief, start to finish.

## Violations to Fix

{{VIOLATIONS}}

## Original Brief

{{BRIEF}}
