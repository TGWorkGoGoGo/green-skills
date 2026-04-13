#!/usr/bin/env python3
import argparse
import json
import re
import sys
from pathlib import Path

FOOTNOTE_START_RE = re.compile(r"^\s*\[\^\s*([^\]]+)\s*]\s*:\s*(.*)$")


def extract_frontmatter(text: str):
    if not text.startswith("---\n"):
        return "", text
    lines = text.splitlines(keepends=True)
    for idx in range(1, len(lines)):
        if lines[idx].strip() == "---":
            return "".join(lines[: idx + 1]), "".join(lines[idx + 1 :])
    return "", text


def extract_leading_numeric_marker_id(text: str):
    patterns = [
        r"^\$\{\s*\}\^\{\s*(\d+)\s*\}\$\s*",
        r"^\$\{\}\^\{\s*(\d+)\s*\}\$\s*",
        r"^\$\{\s*\}\^\s*(\d+)\$\s*",
        r"^\^\s*(\d+)\s*",
    ]
    for pattern in patterns:
        match = re.match(pattern, text)
        if match:
            return match.group(1)
    return None


def remove_leading_numeric_marker(text: str):
    patterns = [
        r"^\$\{\s*\}\^\{\s*\d+\s*\}\$\s*",
        r"^\$\{\}\^\{\s*\d+\s*\}\$\s*",
        r"^\$\{\s*\}\^\s*\d+\$\s*",
        r"^\^\s*\d+\s*",
    ]
    cleaned = text
    for pattern in patterns:
        cleaned, count = re.subn(pattern, "", cleaned, count=1)
        if count:
            return cleaned.lstrip(), True
    return text, False


def render_canonical_footnote_definition(note_id: str, content: str):
    content = content.strip()
    return f"[^{note_id}]: {content}".rstrip() if content else f"[^{note_id}]:"


def normalize_footnotes(text: str):
    frontmatter, body = extract_frontmatter(text)
    lines = body.splitlines()
    normalized_lines = []
    footnote_count = 0
    flattened_count = 0
    removed_leading_marker_count = 0
    changed_ids = []
    i = 0

    while i < len(lines):
        match = FOOTNOTE_START_RE.match(lines[i])
        if not match:
            normalized_lines.append(lines[i])
            i += 1
            continue

        note_id = match.group(1).strip()
        parts = [match.group(2).strip()]
        block_line_count = 1
        i += 1

        while i < len(lines):
            nxt = lines[i]
            if nxt.strip() == "":
                block.append(nxt)
                block_line_count += 1
                i += 1
                continue
            if nxt.startswith("    ") or nxt.startswith("\t"):
                parts.append(nxt.strip())
                block_line_count += 1
                i += 1
                continue
            break

        combined = " ".join(part for part in parts if part)
        leading_marker_id = extract_leading_numeric_marker_id(combined)
        if leading_marker_id is not None:
            combined, removed = remove_leading_numeric_marker(combined)
            if removed:
                removed_leading_marker_count += 1
        normalized_line = render_canonical_footnote_definition(note_id, combined)
        normalized_lines.append(normalized_line)

        footnote_count += 1
        if block_line_count > 1:
            flattened_count += 1
        if block_line_count > 1 or leading_marker_id is not None:
            changed_ids.append(note_id)

    normalized_body = "\n".join(normalized_lines)
    output = frontmatter + normalized_body if frontmatter else normalized_body
    if text.endswith("\n") and not output.endswith("\n"):
        output += "\n"
    return output, {
        "footnote_count": footnote_count,
        "flattened_count": flattened_count,
        "removed_leading_marker_count": removed_leleading_marker_count,
        "changed_ids": changed_ids,
    }


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Normalize Mathpix-style Markdown footnote definitions into canonical "
            "Markdown syntax: [^n]: content."
        )
    )
    parser.add_argument("--input", required=True, help="Markdown file to normalize")
    parser.add_argument("--output", help="Optional output path; defaults to input path")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output) if args.output else input_path

    text = input_path.read_text(encoding="utf-8")
    normalized, report = normalize_footnotes(text)
    output_path.write_text(normalized, encoding="utf-8")

    print(json.dumps(report, ensure_ascii=False, indent=2))
    sys.exit(0)


if __name__ == "__main__":
    main()
