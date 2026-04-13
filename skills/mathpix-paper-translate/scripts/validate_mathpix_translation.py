#!/usr/bin/env python3
import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

FOOTNOTE_START_RE = re.compile(r"^\s*\[\^\s*([^\]]+)\s*]\s*:\s*(.*)$")
CANONICAL_FOOTNOTE_REF_RE = re.compile(r"\[\^\d+\]")
CANONICAL_FOOTNOTE_DEF_LINE_RE = re.compile(r"^\[\^\d+\]:(?: .*)?$")
FOOTNOTE_LIKE_REF_RE = re.compile(r"\[\s*\^[^\]\n]*\]")
GLUED_PSEUDO_MARKER_PREFIX_RE = re.compile(r"^\[\^\d+\](?=\S)")


def extract_frontmatter(text: str):
    if not text.startswith("---\n"):
        return "", text
    lines = text.splitlines(keepends=True)
    for idx in range(1, len(lines)):
        if lines[idx].strip() == "---":
            return "".join(lines[: idx + 1]), "".join(lines[idx + 1 :])
    return "", text


def split_blocks(text: str):
    lines = text.splitlines()
    blocks = []
    current = []
    i = 0

    def flush(kind: str = "paragraph"):
        nonlocal current
        if current and any(line.strip() for line in current):
            blocks.append({"kind": kind, "text": "\n".join(current).rstrip()})
        current = []

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        fence_match = re.match(r"^(```+|~~~+)", stripped)
        if fence_match:
            flush()
            fence = fence_match.group(1)
            fence_char = fence[0]
            fence_len = len(fence)
            block = [line]
            i += 1
            while i < len(lines):
                block.append(lines[i])
                if lines[i].strip().startswith(fence_char * fence_len):
                    i += 1
                    break
                i += 1
            blocks.append({"kind": "fence", "text": "\n".join(block).rstrip()})
            continue

        if stripped == "$$":
            flush()
            block = [line]
            i += 1
            while i < len(lines):
                block.append(lines[i])
                if lines[i].strip() == "$$":
                    i += 1
                    break
                i += 1
            blocks.append({"kind": "display_math", "text": "\n".join(block).rstrip()})
            continue

        if re.match(r"^#{1,6}\s+", stripped):
            flush()
            blocks.append({"kind": "heading", "text": line.rstrip()})
            i += 1
            continue

        if re.match(r"^\[\^[^\]]+\]:", stripped):
            flush()
            block = [line]
            i += 1
            while i < len(lines):
                nxt = lines[i]
                if nxt.strip() == "":
                    block.append(nxt)
                    i += 1
                    continue
                if nxt.startswith("    ") or nxt.startswith("\t"):
                    block.append(nxt)
                    i += 1
                    continue
                break
            blocks.append({"kind": "footnote", "text": "\n".join(block).rstrip()})
            continue

        if "|" in line and i + 1 < len(lines) and re.match(
            r"^\s*\|?(?:\s*:?-+:?\s*\|)+\s*:?-+:?\s*\|?\s*$", lines[i + 1]
        ):
            flush()
            block = [line, lines[i + 1]]
            i += 2
            while i < len(lines) and lines[i].strip() and "|" in lines[i]:
                block.append(lines[i])
                i += 1
            blocks.append({"kind": "table", "text": "\n".join(block).rstrip()})
            continue

        if stripped == "":
            flush()
            i += 1
            continue

        current.append(line)
        i += 1

    flush()
    return blocks


def strip_glued_pseudo_marker_prefix(text: str):
    return GLUED_PSEUDO_MARKER_PREFIX_RE.sub("", text, count=1)


def paragraph_starts_with_lowercase_continuation(text: str):
    stripped = text.lstrip()
    return bool(stripped) and stripped[0].islower()


def paragraph_ends_with_terminal_punct(text: str):
    stripped = text.rstrip()
    return bool(stripped) and stripped[-1] in ".!?。！？:：;；”\"')]}》）"


def is_image_caption_paragraph(text: str):
    stripped = text.lstrip()
    return stripped.startswith("![](") or stripped.lower().startswith("<img")


def normalize_mathpix_artifact_blocks(blocks):
    normalized = []
    for block in blocks:
        if block["kind"] != "paragraph":
            normalized.append(block.copy())
            continue

        text = strip_glued_pseudo_marker_prefix(block["text"])
        merged = False
        if paragraph_starts_with_lowercase_continuation(text):
            if (
                normalized
                and normalized[-1]["kind"] == "paragraph"
                and not is_image_caption_paragraph(normalized[-1]["text"])
                and not paragraph_ends_with_terminal_punct(normalized[-1]["text"])
            ):
                normalized[-1]["text"] = (
                    normalized[-1]["text"].rstrip() + " " + text.lstrip()
                )
                merged = True
            elif (
                len(normalized) >= 2
                and normalized[-1]["kind"] == "paragraph"
                and is_image_caption_paragraph(normalized[-1]["text"])
                and normalized[-2]["kind"] == "paragraph"
                and not paragraph_ends_with_terminal_punct(normalized[-2]["text"])
            ):
                normalized[-2]["text"] = (
                    normalized[-2]["text"].rstrip() + " " + text.lstrip()
                )
                merged = True

        if not merged:
            normalized.append({"kind": "paragraph", "text": text})

    return normalized


def remove_block_kinds(blocks, kinds):
    kept = [block["text"] for block in blocks if block["kind"] not in kinds]
    return "\n\n".join(kept)


def count_table_columns(line: str) -> int:
    stripped = line.strip()
    if stripped.startswith("|"):
        stripped = stripped[1:]
    if stripped.endswith("|"):
        stripped = stripped:-1]
    return len([part for part in stripped.split("|")])


def extract_table_signatures(blocks):
    signatures = []
    for block in blocks:
        if block["kind"] != "table":
            continue
        rows = [line for line in block["text"].splitlines() if line.strip()]
        column_counts = [count_table_columns(line) for line in rows]
        signatures.append({"rows": len(rows), "cols": column_counts})
    return signatures


def extract_markdown_image_urls(text: str):
    return re.findall(r"!\[[^\]]*]\(([^)]+)\)", text)


def extract_html_img_srcs(text: str):
    return re.findall(r"<img\b[^>]*\bsrc\s*=\s*[\"']([^\"']+)[\"']", text, flags=re.I)


def extract_link_urls(text: str):
    return re.findall(r"(?<!!)\[[^\]]+\]\(([^)]+)\)", text)


def extract_inline_code(text: str):
    return re.findall(r"`[^`\n]+`", text)


def extract_inline_math(text: str):
    return re.findall(r"(?<!\$)\$(?!\$)([^\n$]+?)(?<!\\)\$(?!\$)", text)


def get_heading_counts(blocks):
    counts = Counter()
    for block in blocks:
        if block["kind"] != "heading":
            continue
        match = re.match(r"^(#{1,6})\s+", block["text"])
        if match:
            counts[len(match.group(1))] += 1
    return dict(sorted(counts.items()))


def count_list_items(text: str):
    count = 0
    for line in text.splitlines():
        if re.match(r"^\s*(?:[-+*]|\d+\.)\s+", line):
            count += 1
    return count


def extract_footnote_defs(text: str):
    return re.findall(r"(?m)^\s*\[\^\s*([^\]]+)\s*]\s*:", text)


def note_sort_key(note_id: str):
    return (0, int(note_id)) if note