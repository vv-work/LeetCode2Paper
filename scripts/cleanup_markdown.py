#!/usr/bin/env python3
"""
Bulk-clean Markdown files in this repo by:
- Removing lines that link to the Chinese version: lines containing "[中文文档]("
- Removing standalone empty paragraphs: lines equal to "<p>&nbsp;</p>"
- Removing span tags but keeping their inner text: <span ...> and </span>
- Trimming trailing whitespace
- Collapsing multiple consecutive blank lines to a single blank line

Run from repo root: python3 scripts/cleanup_markdown.py
"""
from __future__ import annotations

import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]


def clean_content(text: str) -> str:
    # Remove lines with the Chinese link
    lines = text.splitlines()
    out_lines = []
    for line in lines:
        if "[中文文档](" in line:
            continue
        if line.strip() == "<p>&nbsp;</p>":
            continue
        # Remove <span ...> and </span> but keep inner text
        no_span = re.sub(r"</?span\b[^>]*>", "", line)
        # Trim trailing whitespace
        out_lines.append(no_span.rstrip())

    # Collapse multiple blank lines
    compact_lines = []
    blank_streak = 0
    for line in out_lines:
        if line.strip() == "":
            blank_streak += 1
        else:
            blank_streak = 0
        # Keep at most one blank line in a row
        if blank_streak <= 1:
            compact_lines.append(line)

    # Remove leading/trailing blank lines
    # Trim leading
    while compact_lines and compact_lines[0].strip() == "":
        compact_lines.pop(0)
    # Trim trailing
    while compact_lines and compact_lines[-1].strip() == "":
        compact_lines.pop()

    return "\n".join(compact_lines) + ("\n" if compact_lines else "")


def main() -> None:
    md_files = list(ROOT.rglob("*.md"))
    changed = 0
    for path in md_files:
        # Skip Obsidian or hidden folders if any
        parts = {p.name for p in path.parents}
        if ".git" in parts or ".obsidian" in parts:
            continue
        original = path.read_text(encoding="utf-8")
        cleaned = clean_content(original)
        if cleaned != original:
            path.write_text(cleaned, encoding="utf-8")
            changed += 1
    print(f"Cleaned {changed} Markdown files.")


if __name__ == "__main__":
    main()

