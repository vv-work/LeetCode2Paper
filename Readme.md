# LeetCode2Text

A simple Python CLI to convert LeetCode problem pages into clean, readable text or Markdown you can save or print.

Status: initial scaffold. The CLI provides a minimal HTML-to-text conversion and file I/O. URL fetching/parsing is planned but not implemented yet.

## Quick Start

- Python 3.9+
- No external dependencies

```
PYTHONPATH=src python -m lc2text --help
PYTHONPATH=src python -m lc2text from-file path/to/leetcode.html -o problem.md
```

## Commands

- `from-file`: Convert a saved HTML file into plain text or Markdown. Use `-o` to write to a file, or omit to print to stdout.
- `from-url` (planned): Fetch a LeetCode problem by URL and convert. This will require authentication-aware fetching and robust parsing.

## Development

Project layout:

```
src/
  lc2text/
    __init__.py
    cli.py
    html_to_text.py
```

Run locally:

```
python -m lc2text from-file sample.html -o out.txt
```

## Roadmap

- Add robust URL fetching and cookie/session support
- Improve HTML parsing to capture title, description, examples, constraints
- Output Markdown and optional LaTeX
- Add tests
