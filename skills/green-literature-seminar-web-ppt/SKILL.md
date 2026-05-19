---
name: green-literature-seminar-web-ppt
description: Use when preparing Chinese literature-reading group meeting materials from a paper/PDF and a presentation duration, producing a guizang-ppt-skill single-file horizontal web PPT plus Markdown speech script. First verify guizang-ppt-skill is installed; if missing, help install it. Ask for duration when it is missing. This workflow uses web PPT only and excludes PPTX/PowerPoint output.
---

# Green Literature Seminar Web PPT

## Use Case

Use this skill when the user wants group-meeting preparation from an original academic paper, usually a PDF, and expects a Chinese presentation deck plus an oral script. The output route is the `guizang-ppt-skill` web deck route: a single horizontal-slide HTML file with local figure assets and a matching Markdown speech script.

Do not use the Presentations plugin or create `.pptx` artifacts under this skill. If the user later asks for PPTX separately, treat that as a separate task.

## Required Inputs

Before authoring, confirm these inputs are available:

- Literature source: original PDF or equivalent full paper file.
- Presentation duration: explicit `# min`, such as `10 min` or `15 分钟`.
- Output language: default to Chinese.
- Audience: default to graduate seminar in economics, management, or a related field.

If duration is missing, ask the user for the target number of minutes and pause. If the source file is missing or inaccessible, ask for the file path or attachment.

## Dependency Check

Before any paper extraction or deck authoring, confirm the guizang web PPT skill is installed. Check the known local paths first:

- `C:\Users\tsaig\.codex\skills\magazine-web-ppt\SKILL.md`
- `C:\Users\tsaig\.codex\skills\guizang-ppt-skill\SKILL.md`
- `C:\Users\tsaig\.agents\skills\magazine-web-ppt\SKILL.md`
- `C:\Users\tsaig\.agents\skills\guizang-ppt-skill\SKILL.md`

If none exists, help the user install it before continuing:

1. Install directly from `https://github.com/op7418/guizang-ppt-skill`:
   `npx skills add op7418/guizang-ppt-skill -g -y`
2. If the Skills CLI is unavailable, use `$skill-installer` with repo `op7418/guizang-ppt-skill`.
3. After installation, re-run the path check and continue only when `SKILL.md`, the selected template, and the validator script are accessible.
4. If installation fails, report the command output and ask the user to confirm local network or GitHub access.

When installation succeeds during the current session, direct file access to the installed skill path is enough for this workflow, even if a full Codex restart would be needed for implicit skill invocation.

## Workflow

1. Run the dependency check above and resolve the guizang skill root.
2. Resolve the source file and create working folders: `output/`, `figures/`, `tmp/`, and `logs/` as needed. Use snake_case filenames.
3. Read the paper deeply enough to support a seminar narrative: title, authors, year, research question, mechanism, model or method, data, core results, limitations, and discussion points.
4. Read visual evidence from the paper. When figures or tables matter, extract or crop only the needed regions, minimize empty margins, save PNGs as `figures/fig_{n:02d}_{slug}.png`, then copy the final assets used by the deck into `output/{paper_slug}_guizang_ppt/images/`.
5. Scale the slide plan to the requested duration. Use about 0.8-1.0 slides per minute for technical papers and about 220-260 Chinese characters per minute in the speech script. For a 10-minute report, use 8-10 slides and about 2300-2800 Chinese characters.
6. Use the guizang route. Read the resolved `SKILL.md`, then load only the relevant template and references. For technical or data-heavy literature, default to Swiss Style with `assets/template-swiss.html`, `references/layouts-swiss.md`, and `references/swiss-layout-lock.md`. Use the magazine/e-ink style only when the user explicitly requests that tone.
7. Build `output/{paper_slug}_guizang_ppt/index.html` from the selected guizang template. Keep images in the deck-local `images/` folder and use relative paths.
8. Write `output/{paper_slug}_speech.md`. Headings must map one-to-one to slide numbers, for example `# 第1页 研究问题`.
9. Add source notes and references where needed. For academic references, use APA 7 and verify DOI metadata through Crossref when available.
10. Run the web deck validation and visual QA listed in `references/guizang_route.md`. Fix issues before handoff.

## Content Shape

For most journal-paper group meetings, use this narrative spine:

1. Why this paper matters.
2. The puzzle or empirical/theoretical tension.
3. The paper's mechanism in plain language.
4. The formal model, identification strategy, or key data structure.
5. Main propositions or results.
6. Evidence from original figures and tables.
7. Quantitative meaning or managerial/economic implication.
8. Limitations, extensions, and discussion questions.

Avoid trying to reproduce every proof. Prioritize a clear reading path that a seminar audience can follow in the requested time.

## Deliverables

Default deliverables:

- `output/{paper_slug}_guizang_ppt/index.html`
- `output/{paper_slug}_guizang_ppt/images/`
- `output/{paper_slug}_speech.md`

Optional support files when useful:

- `figures/fig_{n:02d}_{slug}.png`
- `logs/{paper_slug}_qa.md`

Final response should include the produced paths, verification status, how to open the deck, and assumptions.

## Quality Bar

The web deck must be usable as a live seminar deck:

- No visible placeholder text, broken image paths, or template-only content.
- No PPTX outputs under this skill.
- No top-right label like `文献阅读 10min` unless the user explicitly asks for it.
- All visible text must be readable on a projector; avoid text below 18px equivalent.
- Check each slide for text overlap, clipped text, accidental line breaks, and cramped navigation labels.
- Cropped original figures and tables should have minimal blank margins and remain legible.
- The speech script must match slide numbers exactly and fit the requested duration.

See `references/guizang_route.md` for the detailed deck-building and QA procedure.
