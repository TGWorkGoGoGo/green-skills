# Versioned Patch Rules

Use these rules whenever the workflow runs in `versioned_patch` mode.
Treat `versioned_patch` as the default mode unless the user explicitly asks for `report_only`.

## Non-Overwrite Principle

- Never write back to the original Deep Research file.
- Never overwrite an earlier patched file.
- Always create a new derived manuscript copy and a separate patch log.

## Output Location

Write patched outputs under `output/`.
If the directory does not exist, create it before writing.

## File Naming

For a source file named `{filename}.md`, write:

- patched draft: `output/{filename} - v#.md`
- patch log: `output/{filename} - v# - changes.md`

Use integer version labels such as `v1`, `v2`, `v3`.
Preserve the original filename stem instead of converting it to `snake_case`.

## Version Increment Logic

1. Start from `v1` when no earlier derived file exists for the same manuscript.
2. If derived files already exist in `output/`, increment from the highest existing version.
3. If the user supplies an already versioned file such as `{filename} - v2.md`, strip the trailing ` - v2` first, recover the base filename, then write the next version as `{filename} - v3.md`.
4. Never produce chained names such as `{filename} - v2 - v3.md`.

## Patch Log Minimum Contents

Record at least:

- source manuscript path
- patched manuscript path
- generation timestamp
- whether the source was an original draft or a prior versioned derivative
- paragraph clusters modified
- Chinese citations inserted per cluster
- GB entries appended
- any Deep Research citation-marker cleanup actions, including whether `cite...` markers were removed and, when practical, the removal count
- flags such as `whitelist_not_found`, `fallback_used`, and `metadata_incomplete`

## Reference-Section Rule

- If the source manuscript already has a references section, append only the new Chinese entries.
- If no references section exists, create one at the end of the derived file and record that action in the patch log.

## User-Facing Confirmation

When patch mode completes, explicitly report:

- the original file remained unchanged
- the path to the new patched version
- the path to the companion patch log
- whether Deep Research inline citation markers were cleaned from the derivative file
