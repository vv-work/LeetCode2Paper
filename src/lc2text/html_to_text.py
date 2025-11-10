from html.parser import HTMLParser
from html import unescape


class _TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self._chunks = []
        self._block_tags = {
            "p",
            "div",
            "section",
            "article",
            "header",
            "footer",
            "li",
            "ul",
            "ol",
            "pre",
            "code",
            "h1",
            "h2",
            "h3",
            "h4",
            "h5",
            "h6",
        }
        self._newline_pending = False

    def handle_starttag(self, tag, attrs):
        if tag in {"br"}:
            self._emit("\n")
        if tag in {"li"}:
            self._emit("- ")

    def handle_endtag(self, tag):
        if tag in self._block_tags:
            self._emit("\n")

    def handle_data(self, data):
        text = unescape(data)
        if not text.strip():
            return
        self._emit(text)

    def _emit(self, s: str):
        if s == "\n":
            # collapse multiple blank lines
            if self._chunks and self._chunks[-1].endswith("\n\n"):
                return
            # ensure at most double newline
            if self._chunks and self._chunks[-1].endswith("\n"):
                self._chunks[-1] += "\n"
            else:
                self._chunks.append("\n")
        else:
            self._chunks.append(s)

    def get_text(self) -> str:
        out = "".join(self._chunks)
        # normalize newlines and trim
        lines = [ln.rstrip() for ln in out.splitlines()]
        # remove leading/trailing blank lines
        while lines and not lines[0]:
            lines.pop(0)
        while lines and not lines[-1]:
            lines.pop()
        return "\n".join(lines) + ("\n" if lines else "")


def html_to_text(html: str) -> str:
    parser = _TextExtractor()
    parser.feed(html)
    return parser.get_text()

