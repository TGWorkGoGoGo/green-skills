#!/usr/bin/env python3
import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

FOOTNOTE_DEF_RE = re.compile(r"(?m)^\s*\[\^\s*(\d+)\s*]\s*:\s*(.*)$")
CANONICAL_BODY_REF_RE = re.compile(r"\[\^\d+]")
BODY_REF_RE = re.compile(r"\[\^\s*(\d+)\s*]")
FOOTNOTE_LIKE_RE = re.compile(r"\[\s*\^[^\]\n]*]")
CANONICAL_DEF_LINE_RE = re.compile(r"^\[\^\d+]:(?: .*)?$")
INLINE_CODE_RE = re.compile(r"`[^`\n]+`")
INLINE_MATH_RE = re.compile(r"(?<!\$)\$(?!\$)([^$\n]+?)(?<!\\)\$(?!\$)")
HEADING_RE = re.compile(r"^(#{1,6})\s+")
LIST_ITEM_RE = re.compile(r"^\s*(?:[-+*]|\d+\.)\s+")
FENCE_RE = re.compile(r"^(```+|~~~+)")
TABLE_DIVIDER_RE = re.compile(r"^\s*\|?(?:\s*:?-+:?\s*\|)+\s*:?-+:?\s*\|?\s*$")
TEMP_ANCHOR_RE = re.compile(r"⟦P\d+⟧")


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

        fence_match = FENCE_RE.match(stripped)
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

        if HEADING_RE.match(stripped):
            flush()
            blocks.append({"kind": "heading", "text": line.rstrip()})
            i += 1
            continue

        if FOOTNOTE_DEF_RE.match(line):
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

        if "|" in line and i + 1 < len(lines) and TABLE_DIVIDER_RE.match(lines[i + 1]):
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


def strip_footnote_definitions(text: str):
    lines = text.splitlines()
    kept = []
    i = 0
    while i < len(lines):
        if not FOOTNOTE_DEF_RE.match(lines[i]):
            kept.append(lines[i])
            i += 1
            continue
        i += 1
        while i < len(lines):
            nxt = lines[i]
            if nxt.strip() == "":
                i += 1
                continue
            if nxt.startswith("    ") or nxt.startswith("\t"):
                i += 1
                continue
            break
    return "\n".join(kept)


def count_table_columns(line: str) -> int:
    stripped = line.strip()
    if stripped.startswith("|"):
        stripped = stripped[1:]
    if stripped.endswith("|"):
        stripped = stripped[:-1]
    return len(stripped.split("|"))


def table_signatures(blocks):
    signatures = []
    for block in blocks:
        if block["kind"] != "table":
            continue
        rows = [line for line in block["text"].splitlines() if line.strip()]
        signatures.append(
            {
                "rows": len(rows),
                "cols": [count_table_columns(line) for line in rows],
            }
        )
    return signatures


def heading_counts(blocks):
    counts = Counter()
    for block in blocks:
        if block["kind"] != "heading":
            continue
        match = HEADING_RE.match(block["text"])
        if match:
            counts[len(match.group(1))] += 1
    return dict(sorted(counts.items()))


def list_item_count(text: str) -> int:
    return sum(1 for line in text.splitlines() if LIST_ITEM_RE.match(line))


def markdown_image_urls(text: str):
    return re.findall(r"!\[[^\]]*]\(([^)]+)\)", text)


def html_img_srcs(text: str):
    return re.findall(r"<img\b[^>]*\bsrc\s*=\s*[\"']([^\"']+)[\"']", text, flags=re.I)


def link_urls(text: str):
    return re.findall(r"(?<!!)\[[^\]]+]\(([^)]+)\)", text)


def unmatched_fence_count(text: str) -> int:
    stack = []
    for line in text.splitlines():
        match = FENCE_RE.match(line.strip())
        if not match:
            continue
        marker = match.group(1)
        if stack and marker[0] == stack[-1][0] and len(marker) >= stack[-1][1]:
            stack.pop()
        else:
            stack.append((marker[0], len(marker)))
    return len(stack)


def unmatched_display_math_count(text: str) -> int:
    return len(re.findall(r"(?m)^\s*\$\$\s*$", text)) % 2


def inline_dollar_marker_count(text: str) -> int:
    count = 0
    idx = 0
    while idx < len(text):
        if text[idx] != "$":
            idx += 1
            continue
        if idx > 0 and text[idx - 1] == "\\":
            idx += 1
            continue
        if idx + 1 < len(text) and text[idx + 1] == "$":
            idx += 2
            continue
        count += 1
        idx += 1
    return count


def body_reference_ids(text: str):
    body = strip_footnote_definitions(text)
    return BODY_REF_RE.findall(body)


def malformed_body_markers(text: str):
    body = strip_footnote_definitions(text)
    raw = FOOTNOTE_LIKE_RE.findall(body)
    return [marker for marker in raw if not CANONICAL_BODY_REF_RE.fullmatch(marker)]


def malformed_definition_lines(text: str):
    bad = []
    for line in text.splitlines():
        if not line.startswith("[^"):
            continue
        if FOOTNOTE_DEF_RE.match(line) and not CANONICAL_DEF_LINE_RE.fullmatch(line.rstrip()):
            bad.append(line.rstrip())
    return bad


def footnote_definition_ids(text: str):
    return FOOTNOTE_DEF_RE.findall(text)


def note_sort_key(note_id: str):
    return (0, int(note_id)) if note_id.isdigit() else (1, note_id)


def footnote_audit(text: str):
    defined_ids = [note_id for note_id, _ in footnote_definition_ids(text)]
    refs = body_reference_ids(text)
    known_refs = [note_id for note_id in refs if note_id in set(defined_ids)]
    unknown_refs = [note_id for note_id in refs if note_id not in set(defined_ids)]
    first_order = []
    seen = set()
    for note_id in known_refs:
        if note_id in seen:
            continue
        seen.add(note_id)
        first_order.append(note_id)
    return {
        "defined_ids": sorted(set(defined_ids), key=note_sort_key),
        "body_reference_ids": refs,
        "effective_reference_counts": dict(Counter(known_refs)),
        "unknown_reference_ids": sorted(set(unknown_refs), key=note_sort_key),
        "first_occurrence_order": first_order,
        "sequential_first_use": first_order == sorted(first_order, key=note_sort_key),
        "numeric_superscript_ids": [],
        "unresolved_numeric_superscripts": [],
    }


def build_metrics(text: str):
    _, body = extract_frontmatter(text)
    blocks = split_blocks(body)
    non_code_or_math = "\n\n".join(
        block["text"] for block in blocks if block["kind"] not in {"fence", "display_math"}
    )
    para_count = sum(1 for block in blocks if block["kind"] == "paragraph")
    footnote_defs = [note_id for note_id, _ in footnote_definition_ids(body)]
    return {
        "paragraph_count": para_count,
        "heading_counts": heading_counts(blocks),
        "table_signatures": table_signatures(blocks),
        "list_item_count": list_item_count(non_code_or_math),
        "raw_footnote_definitions": footnote_defs,
        "footnote_definition_mode": "raw",
        "footnote_definitions": footnote_defs,
        "footnote_reference_counts": dict(Counter(body_reference_ids(body))),
        "footnote_audit": footnote_audit(body),
        "footnote_syntax_audit": {
            "malformed_body_markers": malformed_body_markers(body),
            "malformed_definition_lines": malformed_definition_lines(body),
        },
        "footnote_definition_audit": {
            "multiline_definition_ids": [],
            "blank_line_definition_ids": [],
            "redundant_leading_marker_ids": [],
            "mismatched_leading_markers": {},
        },
        "code_fence_blocks": [block["text"] for block in blocks if block["kind"] == "fence"],
        "display_math_blocks": [block["text"] for block in blocks if block["kind"] == "display_math"],
        "inline_code": INLINE_CODE_RE.findall(non_code_or_math),
        "inline_math": INLINE_MATH_RE.findall(non_code_or_math),
        "markdown_image_urls": markdown_image_urls(body),
        "html_img_srcs": html_img_srcs(body),
        "link_urls": link_urls(body),
        "unmatched_fence_count": unmatched_fence_count(body),
        "unmatched_display_math_count": unmatched_display_math_count(body),
        "inline_dollar_marker_count": inline_dollar_marker_count(non_code_or_math),
        "contains_temp_anchor": bool(TEMP_ANCHOR_RE.search(body)),
        "contains_missing_definition_placeholder": "[原文缺失定义，按标注保留]" in body,
    }


def compare_sequence(name, left, right, errors):
    if left != right:
        errors.append(f"{name} mismatch")


def compare_metrics(source_metrics, target_metrics):
    errors = []
    warnings = []

    if source_metrics["paragraph_count"] != target_metrics["paragraph_count"]:
        errors.append(
            f"paragraph count mismatch: source={source_metrics['paragraph_count']} "
            f"target={target_metrics['paragraph_count']}"
        )

    if source_metrics["heading_counts"] != target_metrics["heading_counts"]:
        errors.append(
            f"heading count mismatch: source={source_metrics['heading_counts']} "
            f"target={target_metrics['heading_counts']}"
        )

    if source_metrics["list_item_count"] != target_metrics["list_item_count"]:
        errors.append(
            f"list item count mismatch: source={source_metrics['list_item_count']} "
            f"target={target_metrics['list_item_count']}"
        )

    if source_metrics["table_signatures"] != target_metrics["table_signatures"]:
        errors.append("table geometry mismatch")

    compare_sequence("code fence blocks", source_metrics["code_fence_blocks"], target_metrics["code_fence_blocks"], errors)
    compare_sequence(
        "display math blocks",
        source_metrics["display_math_blocks"],
        target_metrics["display_math_blocks"],
        errors,
    )
    compare_sequence("markdown image urls", source_metrics["markdown_image_urls"], target_metrics["markdown_image_urls"], errors)
    compare_sequence("html image srcs", source_metrics["html_img_srcs"], target_metrics["html_img_srcs"], errors)
    compare_sequence("link urls", source_metrics["link_urls"], target_metrics["link_urls"], errors)

    if source_metrics["inline_code"] != target_metrics["inline_code"]:
        errors.append("inline code spans mismatch")

    if len(source_metrics["inline_math"]) != len(target_metrics["inline_math"]):
        warnings.append(
            f"inline math grouping changed: source={len(source_metrics['inline_math'])} "
            f"target={len(target_metrics['inline_math'])}"
        )

    source_defs = set(source_metrics["footnote_definitions"])
    target_defs = set(target_metrics["footnote_definitions"])
    missing_defs = sorted(source_defs - target_defs, key=note_sort_key)
    extra_defs = sorted(target_defs - source_defs, key=note_sort_key)
    if missing_defs:
        errors.append(f"missing footnote definitions in target: {missing_defs}")
    if extra_defs:
        warnings.append(f"extra footnote definitions in target: {extra_defs}")

    if target_metrics["footnote_audit"]["unknown_reference_ids"]:
        errors.append(
            "target contains undefined body footnote markers: "
            f"{target_metrics['footnote_audit']['unknown_reference_ids']}"
        )

    if target_metrics["footnote_syntax_audit"]["malformed_body_markers"]:
        errors.append(
            "target contains non-canonical body footnote syntax: "
            f"{target_metrics['footnote_syntax_audit']['malformed_body_markers']}"
        )

    if target_metrics["footnote_syntax_audit"]["malformed_definition_lines"]:
        errors.append(
            "target contains non-canonical footnote definition syntax: "
            f"{target_metrics['footnote_syntax_audit']['malformed_definition_lines']}"
        )

    if source_metrics["unmatched_fence_count"] != target_metrics["unmatched_fence_count"]:
        errors.append("unmatched fenced block markers changed")

    if target_metrics["unmatched_display_math_count"]:
        errors.append("target contains unmatched display math fences")

    if target_metrics["inline_dollar_marker_count"] % 2 != 0:
        errors.append("target contains unmatched inline math markers")

    if target_metrics["contains_temp_anchor"]:
        errors.append("target still contains temporary anchors")

    if target_metrics["contains_missing_definition_placeholder"]:
        warnings.append("target contains placeholder footnote definitions")

    return errors, warnings


def main():
    parser = argparse.ArgumentParser(
        description="Validate a translated Mathpix Markdown file against its source."
    )
    parser.add_argument("--source", required=True, help="Source markdown path")
    parser.add_argument("--target", required=True, help="Translated markdown path")
    parser.add_argument("--report", help="Optional JSON report path")
    args = parser.parse_args()

    source_text = Path(args.source).read_text(encoding="utf-8")
    target_text = Path(args.target).read_text(encoding="utf-8")

    source_metrics = build_metrics(source_text)
    target_metrics = build_metrics(target_text)
    errors, warnings = compare_metrics(source_metrics, target_metrics)

    report = {
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
        "source_metrics": source_metrics,
        "target_metrics": target_metrics,
    }

    if args.report:
        report_path = Path(args.report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps(report, ensure_ascii=False, indent=2))
    sys.exit(0 if not errors else 1)


if __name__ == "__main__":
    main()
