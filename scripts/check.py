#!/usr/bin/env python3
"""The site's only test: every page parses with balanced tags, every relative link
resolves inside docs/, nothing executable or tracking got in — no script tag,
no inline handler, no embedded document, no resource loaded from another host —
and every page carries the same header and footer, since there is no build step
to keep the menu in sync.
"""
from __future__ import annotations

import re
import sys
from html.parser import HTMLParser
from pathlib import Path

DOCS = Path(__file__).resolve().parent.parent / "docs"
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
FORBIDDEN_TAGS = {"script", "iframe", "object", "embed", "applet", "frame"}
# Elements whose src/href fetch a resource when the page loads; only same-site paths may appear.
LOADING_TAGS = {"img", "source", "video", "audio", "track", "picture", "input"}
LOADING_RELS = {"stylesheet", "icon", "preload", "prefetch", "modulepreload", "manifest", "apple-touch-icon"}


class Check(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.stack: list[str] = []
        self.refs: list[str] = []
        self.errors: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag in FORBIDDEN_TAGS:
            self.errors.append(f"<{tag}> is not allowed")
        if tag not in VOID:
            self.stack.append(tag)
        rel = set((dict(attrs).get("rel") or "").lower().split())
        loads = tag in LOADING_TAGS or (tag == "link" and rel & LOADING_RELS)
        for k, v in attrs:
            if k.startswith("on"):
                self.errors.append(f"<{tag} {k}=…> inline handler")
            if k in ("href", "src", "srcset", "poster", "data") and v:
                # srcset is a comma-separated list of "<url> <descriptor>" candidates
                urls = [c.strip().split()[0] for c in v.split(",") if c.strip()] if k == "srcset" else [v.strip()]
                for url in urls:
                    if url.lower().startswith("javascript:"):
                        self.errors.append(f"<{tag} {k}> javascript: URL")
                    if loads and re.match(r"(?i)^(https?:)?//", url):
                        self.errors.append(f"<{tag} {k}={url}> loads from another host")
                    self.refs.append(url)

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if not self.stack or self.stack[-1] != tag:
            self.errors.append(f"unbalanced </{tag}> (open: {self.stack[-3:]})")
        else:
            self.stack.pop()


CHROME = re.compile(r"<(header|footer) class=\"masthead\">.*?</\1>", re.S)


def main() -> int:
    bad = 0
    chrome: dict[str, str] = {}
    for page in sorted(DOCS.rglob("*.html")):
        p = Check()
        text = page.read_text(encoding="utf-8")
        p.feed(text)
        errors = list(p.errors)
        for m in CHROME.finditer(text):
            first = chrome.setdefault(m.group(1), m.group(0))
            if m.group(0) != first:
                errors.append(f"<{m.group(1)}> differs from the first page's")
        if set(chrome) - {m.group(1) for m in CHROME.finditer(text)}:
            errors.append("missing the shared header or footer")
        if p.stack:
            errors.append(f"unclosed at EOF: {p.stack}")
        for ref in p.refs:
            if ref.startswith(("http://", "https://", "#", "mailto:")):
                if ref.startswith("mailto:"):
                    errors.append(f"mailto link {ref}")
                continue
            target = DOCS / ref.lstrip("/").split("#")[0].split(" ")[0]
            if not target.exists():
                errors.append(f"dead link {ref}")
        for e in errors:
            print(f"{page.relative_to(DOCS)}: {e}")
        bad += len(errors)
    for f in DOCS.rglob("*"):
        if f.is_file() and f.suffix in {".html", ".css", ".svg", ".txt"}:
            if re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", f.read_text(encoding="utf-8")):
                print(f"{f.relative_to(DOCS)}: e-mail address")
                bad += 1
    print("ok" if not bad else f"{bad} problem(s)")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
