# deep-research-cnki-bridge

Bridge a Deep Research draft to authoritative CNKI-backed Chinese citations.

## What it does

- scans a Deep Research draft for China-facing citation gaps
- retrieves authoritative CNKI literature
- prepares GB/T 7714-2015 author-year supplements
- supports safe versioned patching under `output/`

## Install in Codex

```bash
git clone https://github.com/TGWorkGoGoGo/Codex20250924.git
mkdir -p ~/.codex/skills
cp -R Codex20250924/skills/deep-research-cnki-bridge ~/.codex/skills/
```

## Dependency

- CNKI MCP

## Main entry

- `SKILL.md`
