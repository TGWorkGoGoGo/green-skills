---
name: mathpix-paper-translate
description: Translate Mathpix-converted academic paper Markdown files from English to Chinese with a zero-loss workflow that preserves headings, tables, formulas, images, links, code, and footnotes. Use when a user provides a Mathpix-generated `.md` paper, asks to translate a journal article into Chinese without breaking Markdown rendering, wants continuation from a previous partial translation, or needs post-translation completeness and renderability validation.
---

# Mathpix Paper Translate

## Overview

Translate a Mathpix Markdown paper into Chinese while keeping the Markdown structure aligned with the source and still renderable. Preserve formulas, code, figure and image paths, tables, footnotes, and links; validate the final file before delivery.

`${SKILL_DIR}` means the directory containing this `SKILL.md`.

## Quick Start

1. Resolve the source `.md` file and create an output directory next to it as `{source-stem}-zh/`.
2. Read `references/translation_protocol.md`, `references/validation_protocol.md`, `references/footnote_audit_protocol.md`, and `references/fixed_glossary_en_zh.md`.
3. If the source is long (for example, more than 4000 English words), run:

```powershell
python "${SKILL_DIR}\scripts\chunk_mathpix_markdown.py" "<source.md>" --output-dir "<output-dir>" --max-words 2600
```

4. Save intermediate artifacts inside the output directory:
   - `01-analysis.md`
   - `02-prompt.md`
   - `03-draft.md`
   - `04-validation.json`
   - `translation.md`
5. Audit footnotes before translating. Build the whitelist of valid note ids, mark suspected pseudo footnotes, and normalize true note markers into canonical Markdown syntax only:
   - body reference: `[^n]`
   - footnote definition: `[^n]: content`
6. Translate section by section or chunk by chunk following the protocol. Reassemble the full draft into `03-draft.md`.
7. Normalize footnote definitions for stable Markdown rendering:

```powershell
python "${SKILL_DIR}\scripts\normalize_mathpix_footnotes.py" --input "<output-dir>\03-draft.md"
```

8. Run:

```powershell
python "${SKILL_DIR}\scripts\validate_mathpix_translation.py" --source "<source.md>" --target "<output-dir>\03-draft.md" --report "<output-dir>\04-validation.json"
```

9. Fix every reported error, rerun the footnote normalizer if needed, rerun the validator, then save the corrected final file as `translation.md`.

## Workflow

### 1. Prepare the workspace

- Use the source file as-is; do not normalize or rewrite it before translating.
- Place all generated files in `{source-dir}/{source-stem}-zh/`.
- Keep the source filename stem recognizable in the output directory for traceability.

### 2. Protect render-critical syntax

- Treat formulas, code fences, inline code, image URLs, HTML image tags, link targets, tables, canonical footnote markers, and heading levels as protected spans.
- Translate only visible prose. Keep URLs, DOI strings, LaTeX bodies, and code contents unchanged.
- Translate Markdown image alt text only inside `[]`; never edit the path inside `()`.

### 3. Translate with the protocol

- Follow `references/translation_protocol.md` exactly.
- Run the dedicated footnote checks in `references/footnote_audit_protocol.md` before translation and again before delivery.
- Hard-code final footnote syntax:
  - every body-side footnote must be `[^n]`
  - every definition line must be `[^n]: content`
  - do not leave spaces inside the brackets, do not insert a space before the colon, and do not omit the post-colon space when content exists
- After assembling the draft, run `scripts/normalize_mathpix_footnotes.py` so every final footnote definition is flattened into one Markdown line, rendered as `[^n]: content`, and stripped of any stray leading numeric marker.
- Apply the fixed glossary in `references/fixed_glossary_en_zh.md` before inventing new terms.
- Preserve paragraph alignment. Do not merge or split paragraphs, list items, footnote definitions, or table cells.
- Default to adding `📘` before H1 and `🔍` before H2 headings unless the user explicitly asks to disable emoji titles.

### 4. Resume safely

- If the user only says `继续`, resume from the last complete translated heading or paragraph boundary in the existing draft.
- Do not repeat already translated content.
- Keep using the same output directory and continue writing into `03-draft.md` or `translation.md`.

### 5. Validate before delivery

- Run the validator script on the final candidate.
- Read the footnote audit section in the validator report. Confirm numbering order, body-note alignment, and suspicious pseudo-footnotes have been resolved.
- Treat any non-canonical footnote syntax as blocking. Do not deliver if the validator reports anything other than body `[^n]` and definition `[^n]: content`.
- Read `references/validation_protocol.md` and manually inspect any warnings that the script cannot fully judge, especially translated tables, footnotes, and Mathpix-specific line breaks.
- Do not deliver the translation until the validator returns zero errors. Fix warnings whenever they indicate likely rendering or content-loss problems.

## Resources

### scripts/

- `chunk_mathpix_markdown.py`: Split long Mathpix Markdown files into translation-safe chunks without breaking frontmatter, code fences, display math, or tables.
- `normalize_mathpix_footnotes.py`: Flatten translated footnote definitions into render-stable single lines and remove stray leading numeric markers inside the definition text.
- `validate_mathpix_translation.py`: Compare source and target structure, check protected spans, and detect common Markdown render-breaking issues.

### references/

- `translation_protocol.md`: The zero-loss translation procedure adapted from the user's original workflow.
- `validation_protocol.md`: The pre-delivery checklist and repair priorities.
- `footnote_audit_protocol.md`: The dedicated workflow for validating numbering, body markers, and note definitions.
- `fixed_glossary_en_zh.md`: Mandatory glossary for recurring academic and carbon-market terms.
