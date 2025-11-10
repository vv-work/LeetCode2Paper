#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]


COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)


def clean_text(text: str) -> str:
    # Remove all HTML comments like <!-- problem:start --> ... <!-- ... -->
    text = COMMENT_RE.sub("", text)
    # Strip trailing whitespace per line
    lines = [ln.rstrip() for ln in text.splitlines()]
    # Collapse multiple blank lines to a single blank line
    out_lines: list[str] = []
    blank = False
    for ln in lines:
        if ln.strip() == "":
            if not blank:
                out_lines.append("")
                blank = True
            # else skip extra blanks
        else:
            out_lines.append(ln)
            blank = False
    # Trim leading/trailing blank lines
    while out_lines and out_lines[0] == "":
        out_lines.pop(0)
    while out_lines and out_lines[-1] == "":
        out_lines.pop()

    return "\n".join(out_lines) + ("\n" if out_lines else "")


def target_md_files() -> list[Path]:
    # All .md files under repo except inside .git, src, scripts
    files: list[Path] = []
    for p in ROOT.rglob("*.md"):
        if any(part in {".git", "src", "scripts"} for part in p.parts):
            continue
        files.append(p)
    return files


def main() -> None:
    files = target_md_files()
    changed = []
    for p in files:
        old = p.read_text(encoding="utf-8")
        new = clean_text(old)
        if new != old:
            p.write_text(new, encoding="utf-8")
            changed.append(p)
    print(f"Processed {len(files)} Markdown files; updated {len(changed)}.")
    for p in changed[:20]:
        print(f"- {p.relative_to(ROOT)}")
    if len(changed) > 20:
        print(f"... and {len(changed) - 20} more")


if __name__ == "__main__":
    main()

