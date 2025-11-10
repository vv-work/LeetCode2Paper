#!/usr/bin/env python3
from pathlib import Path
import shutil
import sys
import re

ROOT = Path(__file__).resolve().parents[1]


def is_topic_dir(p: Path) -> bool:
    return p.is_dir() and re.match(r"^\d{2}_", p.name) is not None


def main() -> int:
    removed = []
    skipped = []
    for topic in sorted([p for p in ROOT.iterdir() if is_topic_dir(p)]):
        for child in topic.iterdir():
            if child.is_dir():
                entries = list(child.iterdir())
                # remove only if the directory contains exactly one README.md (case-insensitive)
                if len(entries) == 1 and entries[0].is_file() and entries[0].name.lower() == "readme.md":
                    try:
                        entries[0].unlink(missing_ok=True)
                        child.rmdir()
                        removed.append(str(child))
                    except Exception as e:
                        print(f"Failed to remove {child}: {e}", file=sys.stderr)
                else:
                    skipped.append(str(child))
    if removed:
        print("Removed:")
        for p in removed:
            print(f" - {p}")
    else:
        print("No nested README-only folders found.")
    if skipped:
        print("Skipped (not README-only):", len(skipped))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

