#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path


def count_words(text: str) -> int:
    cleaned = re.sub(r"[#*`\[\]()>|_~\-]", " ", text)
    cjk = re.findall(r"[\u4e00-\u9fff\u3400-\u4dbf\uf900-\ufaff]", cleaned)
    latin = re.findall(r"[A-Za-z0-9]+", cleaned)
    return len(cjk) + len(latin)


def extract_frontmatter(text: str):
    if not text.startswith("---\n"):
        return "", text
    lines = text.splitlines(keepends=True)
    if len(lines) < 3:
        return "", text
    for idx in range(1, len(lines)):
        if lines[idx].strip() == "---":
            frontmatter = "".join(lines[: idx + 1]).rstrip("\n")
            rest = "".join(lines[idx + 1 :]).lstrip("\n")
            return frontmatter, rest
    return "", text


def is_fence_start(line: str):
    return re.match(r"^(```+|~~~+)", line.strip())


def is_table_divider(line: str) -> bool:
    return bool(
        re.match(r"^\s*\|?(?:\s*:?-+:?\s*\|)+\s*:?-+:?\s*\|?\s*$", line)
    )


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

        fence_match = is_fence_start(line)
        if fence_match:
            flush()
            fence = fence_match.group(1)
            fence_char = fence[0]
            fence_len = len(fence)
            block = [line]
            i += 1
            while i < len(lines):
                block.append(lines[i])
                candidate = lines[i].strip()
                if candidate.startswith(fence_char * fence_len):
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

        if re.match(r"^#{1,6}\s+", stripped):
            flush()
            blocks.append({"kind": "heading", "text": line.rstrip()})
            i += 1
            continue

        if "|" in line and i + 1 < len(lines) and is_table_divider(lines[i + 1]):
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


def group_chunks(blocks, max_words: int):
    chunks = []
    current = []
    current_words = 0
    for block in blocks:
        words = count_words(block["text"])
        if current and current_words + words > max_words:
            chunks.append({"blocks": current, "words": current_words})
            current = [block]
            current_words = words
        else:
            current.append(block)
            current_words += words
    if current:
        chunks.append({"blocks": current, "words": current_words})
    return chunks


def main():
    parser = argparse.ArgumentParser(
        description="Split a Mathpix Markdown document into translation-safe chunks."
    )
    parser.add_argument("source", help="Source markdown file")
    parser.add_argument("--output-dir", dest="output_dir", help="Output directory")
    parser.add_argument("--max-words", dest="max_words", type=int, default=2600)
    args = parser.parse_args()

    source = Path(args.source)
    text = source.read_text(encoding="utf-8")
    frontmatter, body = extract_frontmatter(text)
    blocks = split_blocks(body)
    chunks = group_chunks(blocks, args.max_words)

    root = Path(args.output_dir) if args.output_dir else source.parent
    chunk_dir = root / "chunks"
    chunk_dir.mkdir(parents=True, exist_ok=True)

    if frontmatter:
        (chunk_dir / "frontmatter.md").write_text(frontmatter + "\n", encoding="utf-8")

    for index, chunk in enumerate(chunks, start=1):
        path = chunk_dir / f"chunk-{index:02d}.md"
        content = "\n\n".join(block["text"] for block in chunk["blocks"]).rstrip() + "\n"
        path.write_text(content, encoding="utf-8")

    manifest = {
        "source": str(source),
        "output_dir": str(chunk_dir),
        "chunk_count": len(chunks),
        "max_words": args.max_words,
        "words_per_chunk": [chunk["words"] for chunk in chunks],
        "frontmatter": bool(frontmatter),
    }
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
