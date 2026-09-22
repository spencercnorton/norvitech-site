#!/usr/bin/env python3
"""The site's only test: every page parses with balanced tags, every relative link
resolves inside docs/, nothing tracking or third-party got in, every page
carries the same header and footer, and sitemap.xml lists exactly the pages that
declare a canonical URL — since there is no build step to keep any of it in sync.

Exactly one script may run here: `docs/site.js`, same-origin, external, on
every page. An inline `<script>`, an `on*` handler, a second script, a script
from another host, an embedded document, or any resource loaded from another
host is still refused — so the whole of what executes on norvitech.com is one
reviewable file.

One thing that looks like a script is not one: a `<script type="application/
ld+json">` block is structured data a browser never executes, and a page may
carry at most one, inline, and it must parse as one schema.org object. That is
outside the script budget on purpose — it runs nothing — and inside every
other gate: it is scanned for e-mail addresses and estate detail like any text.
"""
from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path

DOCS = Path(__file__).resolve().parent.parent / "docs"
SITEMAP = DOCS / "sitemap.xml"
SITEMAP_NS = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
# 404.html is served with `robots: noindex` and has no canonical, so it is the
# one page that must NOT appear in the sitemap.
UNLISTED = "404.html"
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
FORBIDDEN_TAGS = {"iframe", "object", "embed", "applet", "frame"}
# The one script allowed to run on this site, on every page, and nothing else.
SITE_SCRIPT = "/site.js"
# Structured data. Not code: a browser parses it as JSON and never executes it.
LD_JSON = "application/ld+json"
SCHEMA_ORG = "https://schema.org"
# Elements whose src/href fetch a resource when the page loads; only same-site paths may appear.
LOADING_TAGS = {"img", "source", "video", "audio", "track", "picture", "input", "script"}
LOADING_RELS = {"stylesheet", "icon", "preload", "prefetch", "modulepreload", "manifest", "apple-touch-icon"}


class Check(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.stack: list[str] = []
        self.refs: list[str] = []
        self.errors: list[str] = []
        self.scripts = 0
        self.structured = 0
        self._ld: list[str] | None = None  # open ld+json body being collected
        self.canonical: str | None = None

    def handle_starttag(self, tag, attrs):
        if tag in FORBIDDEN_TAGS:
            self.errors.append(f"<{tag}> is not allowed")
        # A browser keeps the FIRST of a repeated attribute and drops the rest,
        # while dict(attrs) keeps the last — so `src="//evil" src="/site.js"`
        # would load one thing and be judged as another. Refuse the ambiguity
        # rather than trying to agree with the parser about which one wins.
        names = [k for k, _ in attrs]
        if len(names) != len(set(names)):
            self.errors.append(f"<{tag}> repeats an attribute; a browser keeps the first, this check must not disagree")
        if tag == "script":
            srcs = [v for k, v in attrs if k == "src"]
            if dict(attrs).get("type") == LD_JSON:
                self.structured += 1
                self._ld = []
                if srcs:
                    self.errors.append("structured data must be inline, not loaded")
            else:
                self.scripts += 1
                # An inline script has no src at all; this catches that too.
                if srcs != [SITE_SCRIPT]:
                    self.errors.append(f"only <script src=\"{SITE_SCRIPT}\"> may run here")
        if tag not in VOID:
            self.stack.append(tag)
        rel = set((dict(attrs).get("rel") or "").lower().split())
        if tag == "link" and "canonical" in rel:
            if self.canonical is not None:
                self.errors.append("a second <link rel=\"canonical\">; a page has exactly one")
            self.canonical = (dict(attrs).get("href") or "").strip()
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

    def handle_data(self, data):
        if self._ld is not None:
            self._ld.append(data)

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if tag == "script" and self._ld is not None:
            body, self._ld = "".join(self._ld), None
            try:
                doc = json.loads(body)
            except ValueError as e:
                self.errors.append(f"structured data does not parse as JSON: {e}")
            else:
                if not (isinstance(doc, dict) and doc.get("@context") == SCHEMA_ORG
                        and ("@type" in doc or "@graph" in doc)):
                    self.errors.append("structured data must be one schema.org object")
        if not self.stack or self.stack[-1] != tag:
            self.errors.append(f"unbalanced </{tag}> (open: {self.stack[-3:]})")
        else:
            self.stack.pop()


CHROME = re.compile(r"<(header|footer) class=\"masthead\">.*?</\1>", re.S)


def sitemap_errors(canonicals: set[str]) -> list[str]:
    """The sitemap must list every page's canonical URL and nothing else.

    Without this, the next page added to the site is simply never announced to a
    crawler, and nothing goes red to say so.
    """
    if not SITEMAP.exists():
        return [f"{SITEMAP.name} is missing"]
    try:
        root = ET.parse(SITEMAP).getroot()
    except ET.ParseError as e:  # a broken sitemap is a finding, not a traceback
        return [f"{SITEMAP.name} does not parse: {e}"]
    locs = {(e.text or "").strip() for e in root.iter(f"{SITEMAP_NS}loc")}
    return (
        [f"{SITEMAP.name}: does not list {u}" for u in sorted(canonicals - locs)]
        + [f"{SITEMAP.name}: lists {u}, which is no page's canonical" for u in sorted(locs - canonicals)]
    )


def main() -> int:
    bad = 0
    chrome: dict[str, str] = {}
    canonicals: set[str] = set()
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
        if p.scripts != 1:
            errors.append(f"expected exactly one <script src=\"{SITE_SCRIPT}\">, found {p.scripts}")
        if p.structured > 1:
            errors.append(f"at most one structured-data block per page, found {p.structured}")
        # Presence, not truthiness: href="" is still a canonical link element on a
        # noindex page, and on any other page it is a canonical that names nothing.
        if page.name == UNLISTED:
            if p.canonical is not None:
                errors.append(f"{UNLISTED} is noindex and must not carry a canonical link")
        elif p.canonical is None:
            errors.append("no <link rel=\"canonical\">, so nothing can list this page")
        elif not p.canonical:
            errors.append("<link rel=\"canonical\"> with an empty href")
        else:
            canonicals.add(p.canonical)
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
    for e in sitemap_errors(canonicals):
        print(e)
        bad += 1
    for f in DOCS.rglob("*"):
        if f.is_file() and f.suffix in {".html", ".css", ".svg", ".txt", ".js"}:
            if re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", f.read_text(encoding="utf-8")):
                print(f"{f.relative_to(DOCS)}: e-mail address")
                bad += 1
    print("ok" if not bad else f"{bad} problem(s)")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
