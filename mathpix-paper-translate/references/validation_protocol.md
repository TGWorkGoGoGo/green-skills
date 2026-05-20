# Validation Protocol

Run this checklist before delivering any translated Mathpix Markdown file.

## 1. Run the structural validator

Use:

```powershell
python "${SKILL_DIR}\scripts\normalize_mathpix_footnotes.py" --input "<draft-or-final.md>"
python "${SKILL_DIR}\scripts\validate_mathpix_translation.py" --source "<source.md>" --target "<draft-or-final.md>" --report "<output-dir>\04-validation.json"
```

Treat validator errors as blocking. Do not deliver the file until errors are cleared.

## 2. Fix errors in this priority order

1. Protected-span mismatches:
   - code fences
   - inline code
   - display math
   - inline math
   - image URLs or HTML image tags
   - link targets
2. Table geometry mismatches:
   - missing tables
   - changed row counts
   - changed column counts
3. Footnote mismatches:
   - non-canonical footnote syntax
   - missing definitions
   - missing references
   - changed whitelist counts
   - multiline footnote definitions not yet flattened
   - stray leading numeric markers still left inside footnote definitions
4. Structural count mismatches:
   - paragraphs
   - headings by level
   - list items
5. Render warnings:
   - unmatched fences
   - unmatched display math fences
   - unresolved temporary anchors
   - placeholder text that still needs a decision

## 3. Perform manual checks after the script passes

- Spot-check the title, abstract, first body section, one method section, one results section, and the reference list.
- Review the footnote audit in `04-validation.json`:
  - valid definition ids
  - body reference ids
  - unresolved numeric superscripts
  - suspicious undefined markers
  - first-use ordering
- Review the footnote syntax audit in `04-validation.json`:
  - malformed body markers
  - malformed definition lines
- Review the footnote definition audit in `04-validation.json`:
  - multiline definition ids
  - blank-line definition ids
  - redundant leading marker ids
  - mismatched leading markers
- Confirm the final file uses only canonical footnote syntax:
  - body reference: `[^n]`
  - definition: `[^n]: content`
- Confirm every table still renders with aligned pipes and the same number of cells per row.
- Confirm every figure or image line still points to the original path or URL.
- Confirm every displayed formula remains intact and visually separated.
- Confirm citation strings, DOI values, author names, and publication years were not accidentally translated or corrupted.
- Confirm no temporary anchors such as `⟦P001⟧` remain.

## 4. Accept only when all release conditions hold

- The validator returns zero errors.
- No warning indicates a probable render failure or content loss.
- The translated file exists at `translation.md`.
- `04-validation.json` reflects the final candidate, not an older draft.
