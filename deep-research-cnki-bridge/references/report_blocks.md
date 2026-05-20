# Required Report Blocks

Write the report with exactly these four headings in this order:

## citation gaps

List one block per claim cluster with:

- `section`
- `paragraph_excerpt`
- `claim_type`
- `china_context`
- `english_anchor_refs`
- `suggested_keywords`

## ranked CNKI candidates

List candidates grouped by claim cluster with:

- title
- source
- year
- source tier
- retrieval channels
- cited count
- short fit note
- any flags such as `whitelist_not_found`, `fallback_used`, or `cssci_floor_unmet`

## ready-to-paste citation snippets

Provide narrative and parenthetical forms that can be pasted into the paragraph immediately.

## ready-to-paste GB entries

Provide GB/T 7714-2015 author-year journal entries only for the selected Chinese papers.

## Patch-Mode Constraint

If the user asks for direct insertion:

- patch only the matched paragraphs
- append new Chinese entries below the existing reference list
- do not renumber or reorder the English bibliography
- do not overwrite the source manuscript
- emit both a versioned patched file and a companion patch log
- use the naming rules from `references/versioning.md`
