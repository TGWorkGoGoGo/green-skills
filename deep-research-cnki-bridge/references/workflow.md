# Workflow Handoff

Use this skill as the orchestrator, not as a monolith.
Run the workflow in three internal stages and load the matching subskill when extra detail is needed.

## Stage A: Gap Scan

Goal: decide which paragraphs require Chinese citations.

Inputs:

- full draft
- existing reference list
- user request

Outputs:

- ordered gap list with the scanner schema

Use `$cnki-citation-gap-scanner` when the draft is long, messy, or mixes English and Chinese citations.

## Stage B: CNKI Retrieval

Goal: find authoritative Chinese literature for each gap through two channels.

Inputs:

- scanner output
- nearby paragraph text
- English anchor references

Outputs:

- ranked candidate set for every gap

Use `$cnki-authority-retriever` for the detailed retrieval and ranking logic.

## Stage C: Citation Application

Goal: turn ranked Chinese candidates into usable author-year snippets and GB entries.

Inputs:

- ranked CNKI candidate list
- original paragraph text
- current references section

Outputs:

- ready-to-paste snippets
- ready-to-paste GB entries
- optional patched markdown

Use `$cnki-gb-author-year-applier` for selection and formatting.

## Stage D: Versioned Writeback

Goal: integrate Chinese literature into the draft without overwriting the original file.

Inputs:

- source draft path
- selected snippets
- selected GB entries
- a draft path or manuscript text, unless the user explicitly requested `report_only`

Outputs:

- versioned patched markdown
- companion patch log

Follow `references/versioning.md` for output paths, version numbering, and non-overwrite behavior.
Follow `references/integration_style.md` for how to rewrite or stitch paragraphs during direct integration.
Before writing the final derivative file, run a marker-cleanup pass for Deep Research inline citation artifacts.
Treat strings like `citeturn15view3turn17search0turn9view0` as cleanup targets rather than citations.
Their common pattern is:

- prefix `cite`
- one or more `turn...` segments
- closing token ``

Remove these inline citation artifacts globally while preserving all surrounding prose and bibliography text.
Do not remove other Deep Research markers such as `entity...` or `image_group...` unless the user explicitly asks for broader marker cleanup.
Record the cleanup scope in the patch log, including whether only `cite...` markers were removed and, when practical, the number removed.

## Mode Switch

Default mode (`versioned_patch`):

- enter automatically when the user supplies a draft unless the user explicitly requests `report_only`
- create a versioned derived manuscript under `output/`
- integrate CNKI evidence by viewpoint, mechanism, empirical cut, or debate rather than defaulting to a `国内外研究` frame
- remove Deep Research inline citation artifacts of the form `cite...` before finalizing the derivative file
- append Chinese references after the existing bibliography entries
- write a companion patch log
- do not reorder English references

Report-only mode:

- build `output/cnki_supplement_report.md`
- do not change the manuscript
