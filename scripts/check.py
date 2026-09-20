#!/usr/bin/env python3
"""The site's only test: every page parses with balanced tags, every relative link
resolves inside docs/, and nothing executable or tracking got in.
"""
from __future__ import annotations

import re
import sys
from html.parser import HTMLParser
from pathlib import Path

DOCS = Path(__file__).resolve().parent.parent / "docs"
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}


class Check(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.stack: list[str] = []
        self.refs: list[str] = []
        self.errors: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag == "script":
            self.errors.append("<script> is not allowed")
        if tag not in VOID:
            self.stack.append(tag)
        for k, v in attrs:
            if k in ("href", "src") and v:
                self.refs.append(v)

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if not self.stack or self.stack[-1] != tag:
            self.errors.append(f"unbalanced </{tag}> (open: {self.stack[-3:]})")
        else:
            self.stack.pop()


def main() -> int:
    bad = 0
    for page in sorted(DOCS.glob("*.html")):
        p = Check()
        p.feed(page.read_text(encoding="utf-8"))
        errors = list(p.errors)
        if p.stack:
            errors.append(f"unclosed at EOF: {p.stack}")
        for ref in p.refs:
            if ref.startswith(("http://", "https://", "#", "mailto:")):
                if ref.startswith("mailto:"):
                    errors.append(f"mailto link {ref}")
                continue
            target = DOCS / ref.lstrip("/").split("#")[0]
            if not target.exists():
                errors.append(f"dead link {ref}")
        for e in errors:
            print(f"{page.name}: {e}")
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
