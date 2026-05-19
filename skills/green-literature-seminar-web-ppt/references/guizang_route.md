# Guizang Web PPT Route for Literature Seminars

## Output Contract

Use this structure unless the user gives a stronger naming requirement:

```text
output/
  {paper_slug}_guizang_ppt/
    index.html
    images/
      01_cover.png
      03_figure_1.png
      ...
  {paper_slug}_speech.md
figures/
  fig_01_{slug}.png
  fig_02_{slug}.png
logs/
  {paper_slug}_qa.md
```

The HTML deck is the primary presentation artifact. It must work by opening `index.html` in a browser. Keep asset paths relative to `index.html`.

## Dependency Preflight

Before reading the paper or copying templates, resolve the guizang skill root:

```powershell
$guizangCandidates = @(
  "$env:USERPROFILE\.codex\skills\magazine-web-ppt",
  "$env:USERPROFILE\.codex\skills\guizang-ppt-skill",
  "$env:USERPROFILE\.agents\skills\magazine-web-ppt",
  "$env:USERPROFILE\.agents\skills\guizang-ppt-skill"
)
$guizangRoot = $guizangCandidates | Where-Object { Test-Path -LiteralPath (Join-Path $_ 'SKILL.md') } | Select-Object -First 1
$guizangRoot
```

If `$guizangRoot` is empty, install the dependency:

```powershell
npx skills add op7418/guizang-ppt-skill -g -y
```

The source repo is `https://github.com/op7418/guizang-ppt-skill`. If the Skills CLI is unavailable, use `$skill-installer` with repo `op7418/guizang-ppt-skill`. Re-run the path check after installation. Continue only when these files exist under the resolved root:

```text
SKILL.md
assets/template-swiss.html
assets/template.html
scripts/validate-swiss-deck.mjs
```

## Duration Scaling

Use this table as a starting point, then adjust for paper complexity:

| Duration | Slides | Speech script length |
|---:|---:|---:|
| 5 min | 5-6 | 900-1300 Chinese characters |
| 10 min | 8-10 | 2300-2800 Chinese characters |
| 15 min | 11-14 | 3400-4200 Chinese characters |
| 20 min | 15-18 | 4600-5600 Chinese characters |

For other durations, use about 0.8-1.0 slides per minute and about 220-260 Chinese characters per minute.

## Paper Reading Checklist

Extract these items before building slides:

- Bibliographic facts: title, authors, journal or venue, year, DOI.
- Research question and why it matters.
- Prior view or benchmark the paper responds to.
- Core mechanism in one sentence.
- Model variables, assumptions, and key equations worth explaining.
- Data source or empirical setting.
- Main results, propositions, or estimated quantities.
- Original figures and tables that best support the seminar narrative.
- Limitations, open questions, and possible extensions.

When a DOI is present and the output includes references, verify metadata through Crossref. If verification is unavailable, state that in the final note.

## Figure and Table Extraction

Use original paper visuals only when they clarify the argument. Crop narrowly:

- Remove excess page whitespace and unrelated surrounding text.
- Preserve figure captions when the caption is necessary for interpretation.
- Prefer PNG for charts, tables, equations, and screenshots.
- Save the first extracted version in `figures/`.
- Copy the final web-ready version into `output/{paper_slug}_guizang_ppt/images/`.
- Use filenames such as `03_figure_1_symmetric_network.png`.

For dense tables, rebuild the key numbers as native HTML table or KPI blocks when that improves legibility. Keep the original source note on the slide.

## Guizang Template Use

1. Read `{guizangRoot}\SKILL.md`.
2. For technical literature, default to Swiss Style:
   - Copy `assets/template-swiss.html` to `output/{paper_slug}_guizang_ppt/index.html`.
   - Use `references/layouts-swiss.md` and `references/swiss-layout-lock.md`.
   - Use `scripts/validate-swiss-deck.mjs` for structural validation.
3. For an explicitly requested magazine/e-ink tone:
   - Copy `assets/template.html`.
   - Use `references/layouts.md` and `references/themes.md`.
4. Do not mix classes or layout fragments between the two guizang styles.
5. Replace all placeholders immediately after copying the template, including page title metadata and `SLIDES_HERE`.
6. Use `data-image-slot` on local images when the Swiss validator expects it.

## Slide Composition Rules

For a research seminar, the deck should feel like an argument, not a paper dump:

- One main claim per slide.
- Put formulas only when they advance the verbal explanation.
- Rebuild formulas or compact tables as editable HTML where practical.
- Original figures should be accompanied by a short interpretation, source, and takeaway.
- Use section rhythm sparingly: cover, problem, mechanism, evidence, implications, discussion.
- Avoid top-right badges such as `文献阅读 10min`.
- Keep short navigation text on one line when it has only a few Chinese characters.

## Visual QA Checklist

Inspect the rendered deck slide by slide:

- Text boxes: no overlap, clipping, forced two-line labels, or hidden overflow.
- Images: no broken paths, no blurred key labels, no excessive crop margins.
- Figure/table captions: readable and correctly tied to the visual.
- Equations: readable on a projector and visually aligned with explanation text.
- Contrast: text has enough contrast against backgrounds and figure overlays.
- Layout: no accidental collisions with footer, navigation, page numbers, or source notes.
- Browser behavior: keyboard navigation, wheel/touch navigation, and index overlay still work.

## Validation Commands

Adapt paths as needed:

```powershell
node {guizangRoot}\scripts\validate-swiss-deck.mjs output\{paper_slug}_guizang_ppt\index.html
rg -n "\[必填\]|TODO|SLIDES_HERE|文献阅读 10min" output\{paper_slug}_guizang_ppt\index.html output\{paper_slug}_speech.md
rg -n "src=\"images/" output\{paper_slug}_guizang_ppt\index.html
```

For final browser QA, open `output/{paper_slug}_guizang_ppt/index.html` and review all slides visually. If a local dev server is more reliable for browser tooling, run one from the deck directory and report the URL only for review, keeping `index.html` as the artifact.
