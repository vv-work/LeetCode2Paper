#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
MD_PATH = ROOT / "LeetCode75List.md"


def extract_categories(md_text: str) -> list[str]:
    cats = []
    for line in md_text.splitlines():
        line = line.strip()
        if line.startswith("## "):
            # Format: "## NN. Category Name"
            try:
                after = line[3:].strip()
                num, name = after.split(".", 1)
                name = name.strip()
                cats.append(name)
            except Exception:
                continue
    return cats


def normalize_category_name(name: str) -> str:
    import re as _re
    name = name.strip().replace("/", " ").replace("'", "")
    name = _re.sub(r"[^A-Za-z0-9]+", "_", name).strip("_")
    return name


def intended_folders(categories: list[str]) -> set[str]:
    names = set()
    for idx, cat in enumerate(categories, start=1):
        safe = normalize_category_name(cat)
        names.add(f"{idx:02d}_{safe}")
    return names


def cleanup():
    md = MD_PATH.read_text(encoding="utf-8")
    cats = extract_categories(md)
    want = intended_folders(cats)
    # Only consider NN_* directories in repo root
    pat = re.compile(r"^\d{2}_.+")
    removed = []
    for p in ROOT.iterdir():
        if p.is_dir() and pat.match(p.name):
            if p.name not in want:
                # remove directory tree
                for sub in sorted(p.rglob("*"), reverse=True):
                    if sub.is_file() or sub.is_symlink():
                        sub.unlink(missing_ok=True)
                    elif sub.is_dir():
                        try:
                            sub.rmdir()
                        except OSError:
                            # Try again after removing contents
                            pass
                try:
                    p.rmdir()
                except OSError:
                    # Fallback: remove any leftover files then rmdir again
                    for sub in sorted(p.rglob("*"), reverse=True):
                        if sub.is_file() or sub.is_symlink():
                            sub.unlink(missing_ok=True)
                        elif sub.is_dir():
                            try:
                                sub.rmdir()
                            except OSError:
                                pass
                    p.rmdir()
                removed.append(p.name)
    return removed


def main():
    removed = cleanup()
    if removed:
        print("Removed:")
        for name in removed:
            print(f"- {name}")
    else:
        print("No unused category folders to remove.")


if __name__ == "__main__":
    main()

