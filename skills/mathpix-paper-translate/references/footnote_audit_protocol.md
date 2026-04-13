# Footnote Audit Protocol

Run this audit before translation and again before final delivery.

## 1. Build the valid-id whitelist

- Collect every trailing footnote definition id from `[^n]:`.
- Treat this set as the only authoritative whitelist for numeric footnotes.

## 2. Scan the body for all note-like markers

Check three classes of markers in the body:

1. Standard Markdown references such as `[^1]`
2. Mathpix superscript markers such as `${ }^{1}$` or `${}^{1}$`
3. Suspicious pseudo markers such as `[^23]` that are not defined anywhere

## 3. Normalize true notes

- If a numeric superscript id belongs to the whitelist, convert it to `[^n]`.
- Keep author-affiliation superscripts like `${ }^{\mathrm{a}}$` unchanged.
- Do not convert anything inside formulas, code, tables, or links unless it is clearly a body footnote marker.
- Accept only canonical Markdown footnote syntax in the final file:
  - body marker: `[^n]`
  - definition line: `[^n]: content`

## 4. Remove or flag pseudo footnotes

- If a body marker id is not in the whitelist, treat it as suspicious.
- When it behaves like a page-number artifact from Mathpix, remove it and repair spacing.
- If it cannot be safely classified, keep it in the working draft, mark it in the audit report, and resolve it before delivery.

## 5. Verify numbering and placement

- Confirm the first appearance order of valid footnotes in the body matches the intended numbering logic.
- Confirm every valid body marker points to exactly one definition.
- Confirm there is no definition id that is accidentally skipped, duplicated, or renumbered in the translation.
- Confirm note markers remain attached to the correct sentence or clause after translation.
- Confirm no non-canonical forms remain, including `[ ^1 ]`, `[^ 1]`, `[^1 ]`, `[^1] : ...`, or `[^1]:...`.
- Confirm each final `[^n]:` definition is flattened to one physical Markdown line so the renderer does not turn continuation lines into code blocks.
- Confirm a definition does not begin with a stray numeric marker, such as `[^2]: ${ }^{2}$ ...` or `[^3]: ${ }^{2}$ ...`.

## 6. Accept only when all footnote checks pass

- No body marker remains without a matching definition.
- No non-canonical footnote syntax remains; only `[^n]` and `[^n]: content` are allowed.
- No unresolved numeric superscript marker remains when it should be a Markdown footnote reference.
- No suspicious page-number-like marker remains in the final translation.
- No multiline or stray-marker footnote definition remains in the final translation.
