#!/usr/bin/env python3
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
MD_PATH = ROOT / "LeetCode75List.md"


def normalize_category_name(name: str) -> str:
    # Replace slashes with space-dash-space for readability first
    name = name.strip()
    # Convert to underscores, removing punctuation we don't want in folder names
    # Keep letters, numbers, and spaces/"/" for now, then normalize
    name = name.replace("/", " ")
    name = name.replace("'", "")
    # Collapse non-alnum to single underscore
    name = re.sub(r"[^A-Za-z0-9]+", "_", name)
    name = name.strip("_")
    return name


def parse_markdown(lines: list[str]):
    # Returns list of tuples: (category_name, [(title, difficulty), ...])
    categories = []
    cur_cat = None
    cur_items = None
    i = 0
    # heuristics: known headings to skip at top
    junk = {"LeetCode 75", "4", "/", "75"}
    difficulties = {"Easy", "Medium", "Hard"}
    known_categories = {
        "Array / String",
        "Two Pointers",
        "Sliding Window",
        "Prefix Sum",
        "Hash Map / Set",
        "Stack",
        "Queue",
        "Linked List",
        "Binary Tree - DFS",
        "Binary Tree - BFS",
        "Binary Search Tree",
        "Graphs - DFS",
        "Graphs - BFS",
        "Heap / Priority Queue",
        "Binary Search",
        "Backtracking",
        "DP - 1D",
        "DP - Multidimensional",
        "Bit Manipulation",
        "Trie",
        "Intervals",
        "Monotonic Stack",
    }

    pending_title = None
    while i < len(lines):
        line = lines[i].strip()
        i += 1
        if not line or line in junk:
            continue

        if line in known_categories:
            cur_cat = line
            cur_items = []
            categories.append((cur_cat, cur_items))
            pending_title = None
            continue

        # If we don't yet have a category, skip until we find one
        if cur_cat is None:
            continue

        # Problem title/difficulty pairs under current category
        if line in difficulties:
            if pending_title is not None:
                cur_items.append((pending_title, line))
                pending_title = None
            else:
                # Stray difficulty; ignore
                pass
        else:
            # treat as title
            # If there was a previous pending title without difficulty, commit it with empty difficulty
            if pending_title is not None:
                cur_items.append((pending_title, ""))
            pending_title = line

    # flush pending title if any
    if pending_title is not None and cur_items is not None:
        cur_items.append((pending_title, ""))

    # Clean up categories if any accidental empty categories
    categories = [(c, items) for (c, items) in categories if items]
    return categories


def format_markdown(categories: list[tuple[str, list[tuple[str, str]]]]) -> str:
    out = []
    out.append("# LeetCode 75\n")
    global_idx = 1
    for ci, (cat, items) in enumerate(categories, start=1):
        out.append(f"\n## {ci:02d}. {cat}\n")
        for title, diff in items:
            diff_suf = f" — {diff}" if diff else ""
            out.append(f"{global_idx:02d}. {title}{diff_suf}\n")
            global_idx += 1
    out.append("")
    return "\n".join(out)


def ensure_category_folders(categories: list[tuple[str, list[tuple[str, str]]]]):
    for ci, (cat, _items) in enumerate(categories, start=1):
        safe = normalize_category_name(cat)
        folder = ROOT / f"{ci:02d}_{safe}"
        folder.mkdir(parents=True, exist_ok=True)


def main():
    raw = MD_PATH.read_text(encoding="utf-8").splitlines()
    cats = parse_markdown(raw)
    if not cats:
        raise SystemExit("No categories parsed from LeetCode75List.md")
    # Write formatted Markdown
    MD_PATH.write_text(format_markdown(cats), encoding="utf-8")
    # Ensure folders
    ensure_category_folders(cats)
    print(f"Rewrote {MD_PATH.name} and created category folders.")


if __name__ == "__main__":
    main()
