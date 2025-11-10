#!/usr/bin/env python3
import re
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
LEET_README = ROOT / "leetcode" / "solution" / "README_EN.md"
LC_ROOT = ROOT / "leetcode"
LIST_MD = ROOT / "LeetCode75List.md"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def slugify(title: str) -> str:
    # Convert title to a filesystem-friendly folder name
    s = title.strip()
    s = re.sub(r"[\s/]+", "_", s)
    s = re.sub(r"[^A-Za-z0-9_\-\.]+", "", s)
    return s


def parse_topics_and_items(md: str):
    topics = []  # list of (topic_title, lines_idx_start, lines_idx_end)
    lines = md.splitlines()
    # Find topic headers and problem lines under them
    topic_map = {}
    current_topic = None
    topic_order = []
    items = []  # list of dict with topic, title, difficulty, line_idx

    # Map topic header numbering to folder names present in repo
    topic_dirs = {p.name: p for p in ROOT.iterdir() if p.is_dir() and re.match(r"^\d{2}_", p.name)}
    topic_num_to_dir = {name.split("_", 1)[0]: name for name in topic_dirs}

    header_re = re.compile(r"^##\s+(\d{2})\.\s+(.*)")
    item_re = re.compile(r"^\s*\d+\.\s+(.+?)\s+\u2014\s+(Easy|Medium|Hard)\s*$")
    # Support already-converted bullet lines: - [Title](link) — Difficulty
    item_link_re = re.compile(r"^\s*-\s*\[(.+?)\]\([^)]*\)\s+\u2014\s+(Easy|Medium|Hard)\s*$")
    # Note: \u2014 is '—' em-dash

    for idx, line in enumerate(lines):
        m = header_re.match(line.strip())
        if m:
            num, name = m.groups()
            dir_name = topic_num_to_dir.get(num)
            if not dir_name:
                dir_name = f"{num}_" + re.sub(r"[^A-Za-z0-9]+", "_", name).strip("_")
            current_topic = {
                "number": num,
                "name": name,
                "dir": dir_name,
            }
            topic_order.append(current_topic)
            continue
        m2 = item_re.match(line)
        m3 = item_link_re.match(line)
        if current_topic and (m2 or m3):
            if m2:
                title = m2.group(1)
                difficulty = m2.group(2)
            else:
                title = m3.group(1)
                difficulty = m3.group(2)
            items.append({
                "topic": current_topic,
                "title": title,
                "difficulty": difficulty,
                "line_idx": idx,
            })

    return lines, topic_order, items


def build_title_to_path_index(leetcode_index_md: str):
    # Parse lines like: |  1768  |  [Merge Strings Alternately](/solution/1700-1799/1768.Merge%20Strings%20Alternately/README_EN.md)  |  `Two Pointers`,`String`  |  Easy  |  Weekly Contest 229  |
    # Return dict title -> relative path under leetcode
    title_to_rel = {}
    link_re = re.compile(r"\[(.*?)\]\((/solution/.+?/README_EN\.md)\)")
    for line in leetcode_index_md.splitlines():
        if "README_EN.md" in line and "](/solution/" in line:
            m = link_re.search(line)
            if m:
                title, rel = m.groups()
                title_to_rel[title.strip()] = rel
    return title_to_rel


def extract_python_only(md: str) -> str:
    # Keep everything except language tabs that are not Python3/Python.
    # Prefer Python3 section if present; else Python.
    # Strategy: if tabs present, capture Python3 section including its code block(s), remove others.
    lines = md.splitlines()
    out = []
    in_tabs = False
    keep_mode = None  # None or 'py'
    i = 0
    has_tabs = any("<!-- tabs:start -->" in line for line in lines)

    if not has_tabs:
        return md  # nothing to slim

    # We will copy everything up to tabs:start, then only the Python section, then tabs:end
    while i < len(lines):
        line = lines[i]
        if "<!-- tabs:start -->" in line:
            in_tabs = True
            out.append(line)
            i += 1
            # scan to find Python3 header index; if not, 'Python'
            # Then when encountered other sections, skip until next '#### ' or tabs:end
            while i < len(lines):
                if lines[i].startswith("#### "):
                    header = lines[i][5:].strip()
                    # exact matches used by doocs: 'Python3', 'Python'
                    if header in ("Python3", "Python") and keep_mode is None:
                        keep_mode = 'py'
                        # write the header and subsequent lines until next header or tabs:end
                        out.append(lines[i])
                        i += 1
                        while i < len(lines) and not lines[i].startswith("#### ") and "<!-- tabs:end -->" not in lines[i]:
                            out.append(lines[i])
                            i += 1
                        # do not break: we need to continue to reach tabs:end to append it
                        continue
                    else:
                        # skip this section
                        i += 1
                        while i < len(lines) and not lines[i].startswith("#### ") and "<!-- tabs:end -->" not in lines[i]:
                            i += 1
                        continue
                elif "<!-- tabs:end -->" in lines[i]:
                    out.append(lines[i])
                    i += 1
                    break
                else:
                    # lines between tabs:start and first header — usually none
                    i += 1
            # after finishing tabs, continue copying the rest of the doc
            continue
        else:
            out.append(line)
            i += 1
    return "\n".join(out) + ("\n" if not out or not out[-1].endswith("\n") else "")


def main():
    if not LIST_MD.exists():
        print("LeetCode75List.md not found", file=sys.stderr)
        sys.exit(1)
    if not LEET_README.exists():
        print("leetcode/solution/README_EN.md not found", file=sys.stderr)
        sys.exit(1)

    list_lines, topics, items = parse_topics_and_items(read_text(LIST_MD))
    title_index = build_title_to_path_index(read_text(LEET_README))

    missing = []
    updates = []

    for it in items:
        title = it["title"]
        topic_dir = it["topic"]["dir"]
        rel = title_index.get(title)
        if not rel:
            missing.append(title)
            continue
        src_md = LC_ROOT / Path(unquote(rel.lstrip("/")))
        if not src_md.exists():
            missing.append(title)
            continue
        # Read and slim to Python-only
        content = read_text(src_md)
        py_only = extract_python_only(content)

        # Create flat file under topic dir: problem_name.md
        file_slug = slugify(title)
        dst_dir = ROOT / topic_dir
        write_text(dst_dir / f"{file_slug}.md", py_only)

        # Update list line to a local link to the flat file
        rel_link = f"{topic_dir}/{file_slug}.md"
        new_line = f"- [{title}]({rel_link}) — {it['difficulty']}"
        updates.append((it["line_idx"], new_line))

    # Apply updates to list file: replace in-memory lines at given indices
    for idx, new_line in updates:
        list_lines[idx] = new_line

    # Also strip numeric prefixes from problem lines not updated
    for i, line in enumerate(list_lines):
        if re.match(r"^\s*\d+\.\s+", line):
            # Preserve the rest, but this should have been updated; leave as-is if missing
            pass

    write_text(LIST_MD, "\n".join(list_lines) + "\n")

    if missing:
        print("Warning: could not find paths for titles:")
        for t in missing:
            print(" -", t)


if __name__ == "__main__":
    main()
