import argparse
import sys
from pathlib import Path

from .html_to_text import html_to_text


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write_text(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def cmd_from_file(args: argparse.Namespace) -> int:
    html = _read_text(Path(args.input))
    text = html_to_text(html)

    if args.output:
        _write_text(Path(args.output), text)
    else:
        sys.stdout.write(text)
    return 0


def cmd_from_url(args: argparse.Namespace) -> int:
    sys.stderr.write(
        "from-url is not implemented yet. Save the page as HTML and use from-file.\n"
    )
    return 2


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="lc2text", description="Convert LeetCode HTML to clean text"
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    pf = sub.add_parser("from-file", help="Convert a saved HTML file")
    pf.add_argument("input", help="Path to saved LeetCode HTML page")
    pf.add_argument("-o", "--output", help="Output file (default: stdout)")
    pf.set_defaults(func=cmd_from_file)

    pu = sub.add_parser("from-url", help="Fetch a URL (planned)")
    pu.add_argument("url", help="LeetCode problem URL")
    pu.set_defaults(func=cmd_from_url)

    return p


def main(argv=None) -> int:
    parser = build_parser()
    ns = parser.parse_args(argv)
    return ns.func(ns)


if __name__ == "__main__":
    raise SystemExit(main())

