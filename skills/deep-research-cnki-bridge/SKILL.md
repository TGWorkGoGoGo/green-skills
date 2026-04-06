---
name: deep-research-cnki-bridge
description: This skill should be used when the user asks to "根据 deep research 结果补中文文献", "按英文经典文献反推中文文献", "为这篇综述补权威中文引文", or wants to supplement a Deep Research draft with authoritative CNKI-based Chinese citations and GB/T 7714-2015 author-year references.
---

# Deep Research CNKI Bridge

## Overview

Bridge a Deep Research draft to authoritative Chinese literature from CNKI.
Run `versioned_patch` as the default workflow: patch the manuscript into a versioned derivative under `output/`.
Build `output/cnki_supplement_report.md` only when the user explicitly asks for report-only output.
When patching, never overwrite the original draft. Always create a numbered derivative copy in `output/` and a companion patch log.

## Core Workflow

### 1. Normalize the input and lock the mode

Accept either a markdown path or pasted manuscript text.
Treat `versioned_patch` as the default mode whenever a draft path or manuscript text is supplied.
Enter `report_only` mode only when the user explicitly asks for a supplement report without modifying the manuscript.
Use these mode labels internally:

- `versioned_patch`
- `report_only`

### 2. Scan citation gaps

Start with `$cnki-citation-gap-scanner` or follow its rules directly.
Extract only mandatory Chinese citation gaps with this output schema:

- `section`
- `paragraph_excerpt`
- `claim_type`
- `china_context`
- `english_anchor_refs`
- `suggested_keywords`

Mark a paragraph only when it makes a China-specific claim that currently lacks strong Chinese support, not merely because it mentions China.
Treat any user-supplied debug draft as a one-off fixture for the current run only. Do not generalize its topic, section structure, or claim mix to future tasks.

### 3. Retrieve and rank CNKI candidates

Continue with `$cnki-authority-retriever` or follow its rules directly.
Run two retrieval channels for every gap:

1. Topic retrieval.
   Start with `search_cnki(query, search_type=主题)`.
   If the result set is thin, retry in order with `关键词`, then `摘要`.
2. English-anchor retrieval.
   Extract classic English anchor references from the nearby paragraph or reference list, then run CNKI `全文` searches in this order:
   - original English title
   - `first_author + title keywords`
   - `first_author + coauthor`

Merge and deduplicate the two channels, then rank candidates with the fixed order:

1. `A+ > A > B > 其他来源`
2. `双通道命中 > 单通道命中`
3. `cited_count` descending
4. paragraph-level relevance
5. newer year first

Treat the whitelist in `references/journal_tiers.md` as binding.
Use fallback journals only when no suitable whitelist hit exists for the claim and the fallback source is a CSSCI-source journal.
If no whitelist or CSSCI-source journal can support the claim, stop at insufficiency rather than widening to non-journal material.

### 4. Build author-year snippets and GB entries

Continue with `$cnki-gb-author-year-applier` or follow its rules directly.
Prepare these outputs:

- `citation_snippets`
- `gb_entries`
- optional patched markdown

Apply at most two Chinese citations per claim cluster:

1. one strongest whitelist paper
2. one mechanism or data complement if needed

Keep the manuscript's existing English author-year system intact.
Do not globally rewrite existing in-text citations.

### 5. Deliver the result

In report mode, write `output/cnki_supplement_report.md` with the four required blocks from `references/report_blocks.md`:

1. `citation gaps`
2. `ranked CNKI candidates`
3. `ready-to-paste citation snippets`
4. `ready-to-paste GB entries`

In patch mode:

- insert the selected Chinese author-year snippets into the matched paragraphs
- when sentence-level rewriting is needed, organize the integration by research viewpoints, mechanisms, empirical cuts, identification strategies, debates, or China-specific contexts
- avoid using `国内外研究` as the default organizing index unless the user explicitly asks for that framing
- before finalizing the derivative markdown, scan for Deep Research inline citation artifacts such as `citeturn15view3turn17search0turn9view0`
- treat these artifacts as transport markers rather than valid citations: they typically begin with `cite`, contain one or more `turn...` segments, and end with ``
- remove Deep Research inline citation artifacts globally from the patched manuscript while keeping the surrounding prose, author-year citations, and bibliography text unchanged
- leave non-citation Deep Research markers such as `entity...` and `image_group...` untouched unless the user explicitly asks for a broader cleanup pass
- append the new Chinese GB entries to the existing references section
- never reorder or reformat the existing English bibliography
- write the patched manuscript to a new versioned file instead of the source path
- create a companion patch log that records source path, derived file path, inserted clusters, added references, any Deep Research citation-marker cleanup actions, and any metadata flags
- follow the naming and increment rules in `references/versioning.md`

## Quality Gates

- Use CNKI as the only verification and metadata source for Chinese literature in this workflow.
- Do not call Crossref for Chinese-source validation.
- Keep journal articles only.
- Treat CSSCI-source journals as the minimum fallback floor once the whitelist is exhausted.
- Treat the fixed local CSSCI list maintained by `$cnki-authority-retriever` as the canonical fallback universe for this workflow.
- Exclude theses, books, conference proceedings, newspapers, and publisher records without exception.
- Surface insufficiency explicitly with `whitelist_not_found`, `fallback_used`, or `metadata_incomplete`.
- Do not silently add weak or generic Chinese literature that does not support the exact claim.
- In direct integration mode, avoid reducing the literature structure to a generic `国内外研究` split; prefer claim-relevant argumentative indexes such as mechanism, viewpoint, identification strategy, empirical scope, or debate.

## Resources

- `references/workflow.md`: stage-by-stage orchestration details and handoff rules
- `references/journal_tiers.md`: fixed whitelist and tier ordering
- `references/report_blocks.md`: required report structure and patch-mode constraints
- `references/versioning.md`: safe writeback and version-management rules for direct integration
- `references/integration_style.md`: writing-style rules for stitching CNKI evidence into a Deep Research draft
