# Translation Protocol

Use this protocol whenever translating a Mathpix-generated academic Markdown file into Chinese.

## Defaults

- `STRICT=true`
- `EMOJI_TITLES=true`
- `REPORT=off`

If the user explicitly disables emoji headings or asks for a different delivery format, honor that request. Otherwise use these defaults.

## Phase 0: Protect content and structure

Apply these rules throughout the translation.

- Follow the zero-loss rule. Do not omit, merge, summarize, or skip any source text characters unless this protocol explicitly allows it.
- Preserve paragraph count, list-item count, heading hierarchy, and table row and column counts.
- Keep Markdown image paths and HTML image attributes unchanged. Translate only image alt text inside `![Alt](...)`.
- Keep every `$...$` and `$$...$$` LaTeX body unchanged.
- Keep fenced code blocks and inline code unchanged. Translate only prose outside them.
- Preserve Markdown syntax for headings, lists, tables, quotes, links, and footnotes.
- Lock final footnotes to canonical Markdown only:
  - body reference must be exactly `[^n]`
  - definition must be exactly `[^n]: content`
  - never output `[ ^n ]`, `[^ n]`, `[^n ]`, `[^n] : content`, or `[^n]:content`
- Use temporary alignment anchors only internally. Remove every anchor before writing the final draft.

## Phase 1: Build the footnote whitelist

Scan the full source and collect every footnote definition number that matches:

```regex
(?m)^\s*\[\^\s*(\d+)\s*\]\s*:
```

Treat the resulting set as whitelist `W`. Do not print the whitelist in the final translation.

Also collect:

- every body-side `[^n]` marker
- every Mathpix superscript-style numeric marker such as `${ }^{1}$`
- every suspicious marker whose id is not in `W`

Use these findings to prepare a footnote audit before translating.

## Phase 2: Clean the body and translate it

### 2.1 Remove pseudo footnotes from the body

- If `[^m]` is immediately attached to surrounding text and `m` is not in `W`, treat it as a stray page-number marker from Mathpix.
- Delete that marker and keep one space where needed to avoid merged words.
- Keep every `[^n]` where `n` is in `W`.

### 2.2 Normalize superscript-style note references

- Convert `${}^{k}$`, `${ }^{k}$`, and plain-text `^k` into `[^k]` only when `k` is in `W`.
- Do not convert anything inside formulas, code, variable names, or obvious exponent contexts.
- Keep non-numeric author-affiliation superscripts unchanged.
- Before leaving this phase, rewrite every valid body-side note marker into the exact string form `[^k]`.

### 2.3 Translate the body

- Use scholarly but readable Chinese.
- Keep technical abbreviations, URLs, company names, journal names, and citation metadata as needed.
- Prefer full-width Chinese parentheses in prose. Do not touch parentheses inside formulas, code, or link targets.
- If `EMOJI_TITLES=true`, rewrite headings as:
  - `# 📘 ...`
  - `## 🔍 ...`
- Preserve table pipes, alignment rows, and column counts. Translate only visible cell text.
- Keep figure and table captions near their original positions.

### 2.4 Run an internal coverage check

Before moving on:

- Compare non-empty paragraph counts between source and draft.
- Compare list-item counts between source and draft.
- Compare table counts and each table's row and column counts.
- Compare whitelisted footnote reference counts.

If any check fails, repair the draft before continuing.

## Phase 3: Translate footnotes and reconcile references

### 3.1 Translate footnote definitions

- Translate each `[^n]:` definition in whitelist order.
- Always deliver each final definition as one physical Markdown line in the exact form `[^n]: content`.
- If Mathpix wrapped one definition across several indented lines, translate the full content and then flatten it back into a single line before delivery.
- If a definition begins with a stray marker such as `${ }^{1}$` inside `[^1]:` or `[^3]: ${ }^{2}$ ...`, remove that leading numeric marker from the definition text.
- Do not convert LaTeX expressions inside footnotes into Markdown footnote references.
- Translate visible prose inside footnotes, but keep links, DOI strings, and structural punctuation intact.
- Do not leave extra spaces inside `[^n]`, before `:`, or between `:` and the content.

### 3.2 Enforce bidirectional consistency

- Ensure `Set(body references)` equals `Set(footnote definitions)` after the pseudo-footnote cleanup in Phase 2.
- Ensure each defined footnote is referenced at least once unless the source already contains an unreferenced definition.
- If the body contains a real `[^m]` reference but the source lacks a matching definition, append:

```markdown
[^m]: [原文缺失定义，按标注保留]
```

- Never renumber or silently delete a genuine footnote definition.

### 3.3 Run a final alignment check

Recheck paragraph, list, table, and footnote alignment. Keep repairing until the draft is structurally aligned.

## Phase 4: Deliver and continue safely

- Output only the translated Markdown file contents. Do not add explanatory prose inside the file.
- Before the final validation pass, run `scripts/normalize_mathpix_footnotes.py` on `03-draft.md` or the current candidate file.
- If the response must be continued later, resume from the latest complete semantic boundary.
- When the user only says `继续`, continue from the existing draft without repeating translated content.

## Output files

Use this layout inside the output directory:

- `01-analysis.md`: terminology, tone, and risk notes
- `02-prompt.md`: condensed working instructions for the current document
- `03-draft.md`: assembled full translation before the last validation pass
- `04-validation.json`: validator output
- `translation.md`: final validated translation
