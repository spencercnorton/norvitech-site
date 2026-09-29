#!/usr/bin/env python3
"""nav.py: the header and footer of every page on norvitech.com, from the lists below.

    scripts/nav.py      rewrite the header, footer and product row of every page
                        in docs/, and docs/sitemap.xml

The pages are hand-written HTML with no build step, so this file is the one
place the site's navigation is written down. A page under docs/<slug>/ of a
product in PRODUCTS carries that product's header: the NorviTech mark, the
product's name, its menus, its one action and its own repository, and nothing
about the rest of the site. Every other page carries the site header:
Projects, Consulting, About and GitHub. The footer is the same on every page,
and so is the row of every product at the foot of a product's page, with the
page's own product marked.

check.py refuses a page whose header, footer or row of products is not what
this renders, a product's home page without that row, a product page that
none of its product's menus links, and a #fragment that no page carries.

The sitemap is every page's canonical URL, sorted, so a new page is listed the
next time this runs.

Adding a product: an entry in PRODUCTS, its page at docs/<slug>/index.html
(copy a sibling's), then run this; every menu, footer, row and the sitemap follow.
"""
from __future__ import annotations

import html
import re
import sys
from pathlib import Path

DOCS = Path(__file__).resolve().parent.parent / "docs"
SITEMAP = DOCS / "sitemap.xml"
GH = "https://github.com/spencercnorton"

# The site header, after its Projects menu.
SITE = [("Consulting", "/consulting/"), ("About", "/about/"), ("GitHub", GH)]


def support(slug: str) -> list[tuple[str, str]]:
    """Every product takes questions the same three ways, on its own repository."""
    return [("Issues", f"{GH}/{slug}/issues/new/choose"),
            ("Discussions", f"{GH}/{slug}/discussions"),
            ("Report a vulnerability", f"{GH}/{slug}/security/advisories/new")]


# In Projects-menu and footer order. slug is the page's folder under docs/ and
# the name of its GitHub repository; note is its line in the Projects menu;
# action is the one thing a visitor came to do. A menu is (label, [(label, href)]),
# and every page under docs/<slug>/ must be in one of them.
PRODUCTS = [
    dict(slug="helios", name="Helios", note="A desktop for your coding agents",
         action=("Install", "/helios/#install"), menus=[
             ("Overview", [("What it does", "/helios/#features"),
                           ("Three providers", "/helios/#providers"),
                           ("Where your data lives", "/helios/#data")]),
             ("Docs", [("Compared with a terminal", "/helios/vs-terminal/"),
                       ("User guide", f"{GH}/helios/blob/main/docs/user-guide.md"),
                       ("Agent setup", f"{GH}/helios/blob/main/docs/agent-setup.md"),
                       ("Changelog", f"{GH}/helios/blob/main/CHANGELOG.md"),
                       *support("helios")])]),
    dict(slug="bitagent", name="BitAgent", note="DHT crawler and indexer for the *arr stack",
         action=("Install", "/bitagent/#install"), menus=[
             ("Overview", [("What BitAgent adds", "/bitagent/#features"),
                           ("The dashboard", "/bitagent/#dashboard")]),
             ("Docs", [("Deployment guide", "/bitagent/guide/"),
                       ("BitAgent and bitmagnet", "/bitagent/vs-bitmagnet/"),
                       ("Architecture", f"{GH}/bitagent/blob/main/docs/concepts/architecture.md"),
                       ("DHT crawler", f"{GH}/bitagent/blob/main/docs/concepts/dht-crawler.md"),
                       ("Classification", f"{GH}/bitagent/blob/main/docs/concepts/classification.md"),
                       ("Dashboard guide", f"{GH}/bitagent/blob/main/docs/ui-guide.md"),
                       ("Private tracker mode", f"{GH}/bitagent/blob/main/docs/integrations/private-tracker-mode.md"),
                       ("Security", f"{GH}/bitagent/blob/main/docs/operations/security.md"),
                       ("Monitoring", f"{GH}/bitagent/blob/main/docs/operations/monitoring.md")]),
             ("Reference", [("Torznab API", f"{GH}/bitagent/blob/main/docs/reference/torznab-api.md"),
                            ("GraphQL API", f"{GH}/bitagent/blob/main/docs/reference/graphql-api.md"),
                            ("Metrics", f"{GH}/bitagent/blob/main/docs/reference/metrics.md"),
                            ("Improvements over upstream", f"{GH}/bitagent/blob/main/docs/project/improvements.md"),
                            ("Legal disclaimer", f"{GH}/bitagent/blob/main/docs/legal/disclaimer.md"),
                            *support("bitagent")])]),
    dict(slug="xnote", name="XNote", note="Sticky notes for GNOME",
         action=("Install", "/xnote/#install"), menus=[
             ("Overview", [("What it does", "/xnote/#features"),
                           ("Where your data lives", "/xnote/#data")]),
             ("Docs", [("Deployment guide", "/xnote/guide/"),
                       ("User guide", f"{GH}/xnote/blob/main/docs/user-guide.md"),
                       ("Development", f"{GH}/xnote/blob/main/docs/development.md"),
                       ("Changelog", f"{GH}/xnote/blob/main/CHANGELOG.md"),
                       *support("xnote")])]),
    dict(slug="xnote-placement", name="XNote Placement", note="Notes back where you left them",
         action=("Install", "/xnote-placement/#install"), menus=[
             ("Docs", [("Why Wayland won't place a window", "/xnote-placement/wayland-window-placement/"),
                       ("How it works", f"{GH}/xnote-placement#documentation"),
                       ("Changelog", f"{GH}/xnote-placement/blob/main/CHANGELOG.md"),
                       *support("xnote-placement")])]),
    dict(slug="snipsnap", name="SnipSnap", note="Screenshots on GNOME Wayland",
         action=("Install", "/snipsnap/#install"), menus=[
             ("Overview", [("What it does", "/snipsnap/#features"),
                           ("Where your data lives", "/snipsnap/#data")]),
             ("Docs", [("Deployment guide", "/snipsnap/guide/"),
                       ("Screenshots on GNOME Wayland", "/snipsnap/wayland-screenshots/"),
                       ("The GNOME Shell bridge", f"{GH}/snipsnap/blob/main/docs/gnome-shell-bridge.md"),
                       ("Changelog", f"{GH}/snipsnap/blob/main/CHANGELOG.md"),
                       *support("snipsnap")])]),
    dict(slug="conductor", name="Conductor", note="Live TV and DVR for Plex",
         action=("Deploy", "/conductor/guide/"), menus=[
             ("Docs", [("Overview", "/conductor/"),
                       ("Deployment guide", "/conductor/guide/"),
                       ("Release procedure", f"{GH}/conductor/blob/main/docs/RELEASING.md"),
                       *support("conductor")])]),
    dict(slug="norvi-os", name="NorviOS", note="The NorviTech look for Ubuntu",
         action=("Install", "/norvi-os/#install"), menus=[
             ("Docs", [("Deployment guide", "/norvi-os/guide/"),
                       ("How it works", f"{GH}/norvi-os/blob/main/docs/how-it-works.md"),
                       ("Changelog", f"{GH}/norvi-os/blob/main/CHANGELOG.md"),
                       *support("norvi-os")])]),
    # Indigo's guide is generated from each release by build_indigo.py. When a
    # release adds a page, check.py fails until it is listed here.
    dict(slug="indigo", name="Indigo", note="Swiss for GameCube, rebuilt",
         action=("Download", "/indigo/#downloads"), menus=[
             ("Overview", [("Features", "/indigo/#features"),
                           ("See it in action", "/indigo/#videos"),
                           ("Releases", "/indigo/#channels"),
                           ("Questions", "/indigo/#faq")]),
             ("Guide", [("Guide overview", "/indigo/guide/"),
                        ("Install", "/indigo/guide/install/"),
                        ("Controls", "/indigo/guide/controls/"),
                        ("Home", "/indigo/guide/home/"),
                        ("Library", "/indigo/guide/library/"),
                        ("Game details", "/indigo/guide/game-details/"),
                        ("Cheats", "/indigo/guide/cheats/"),
                        ("Settings", "/indigo/guide/settings/"),
                        ("Make it yours", "/indigo/guide/personalize/"),
                        ("Source", "/indigo/guide/source/"),
                        ("System", "/indigo/guide/system/"),
                        ("Memory Cards", "/indigo/guide/memory-cards/"),
                        ("Posters", "/indigo/guide/posters/"),
                        ("Troubleshooting", "/indigo/guide/troubleshooting/")]),
             ("Reference", [("Settings files", "/indigo/guide/settings-file/"),
                            ("Changelog", "/indigo/changelog/"),
                            ("Release notes", f"{GH}/indigo/releases/latest"),
                            *support("indigo")])]),
]

BRAND = '<a class="brand" href="/"><img src="/assets/logo.svg" alt="" width="40" height="28"><span>NorviTech</span></a>'
CLOCK = """<a class="clock" id="clock" href="https://time.globalentry.systems/">
      <time data-face>--:--:--</time>
      <span data-note></span>
    </a>"""
CHROME = re.compile(r'<(header|footer) class="masthead">.*?</\1>', re.S)
SIBLINGS = re.compile(r'<nav class="siblings"[^>]*>.*?</nav>', re.S)
CANONICAL = re.compile(r'<link rel="canonical" href="([^"]+)">')


def url_of(page: Path) -> str:
    """The URL a file in docs/ is served at: docs/indigo/guide/index.html is /indigo/guide/."""
    parts = page.relative_to(DOCS).parts
    if parts[-1] == "index.html":
        return "/" + "".join(f"{p}/" for p in parts[:-1])
    return "/" + "/".join(parts)


def product(url: str) -> dict | None:
    return next((p for p in PRODUCTS if url.startswith(f"/{p['slug']}/")), None)


def link(label: str, href: str, url: str, cls: str = "", note: str = "") -> str:
    """One link; the one pointing at this very page says so."""
    attrs = (f' class="{cls}"' if cls else "") + f' href="{html.escape(href)}"'
    attrs += ' aria-current="page"' if href == url else ""
    small = f"<small>{html.escape(note)}</small>" if note else ""
    return f"<a{attrs}>{html.escape(label)}{small}</a>"


def menu(label: str, items: list[tuple], url: str) -> str:
    """A native <details>; sharing one name, the browser keeps one open at a time."""
    rows = "".join(f"          <li>{link(text, href, url, note=''.join(note))}</li>\n"
                   for text, href, *note in items)
    return (f'<details class="menu" name="nav">\n        <summary>{html.escape(label)}</summary>\n'
            f"        <ul>\n{rows}        </ul>\n      </details>")


def header(url: str) -> str:
    p = product(url)
    if p:
        name = link(p["name"], "/" + p["slug"] + "/", url, "product")
        lockup = f'{BRAND}\n    <span class="slash" aria-hidden="true">/</span>\n    {name}'
        label, parts = p["name"], [menu(m, items, url) for m, items in p["menus"]]
        parts += [link(*p["action"], url, "act"), link("GitHub", f"{GH}/{p['slug']}", url)]
    else:
        lockup, label = BRAND, "Site"
        parts = [menu("Projects", [(q["name"], f"/{q['slug']}/", q["note"]) for q in PRODUCTS], url)]
        parts += [link(text, href, url) for text, href in SITE]
    items = "".join(f"      {part}\n" for part in parts)
    return (f'<header class="masthead">\n  <div class="wrap">\n    {lockup}\n'
            f'    <span class="rule" aria-hidden="true"></span>\n'
            f'    <nav aria-label="{html.escape(label)}">\n{items}    </nav>\n'
            f"    {CLOCK}\n  </div>\n</header>")


def footer() -> str:
    links = [(p["name"], f"/{p['slug']}/") for p in PRODUCTS] + [("About", "/about/"), ("Consulting", "/consulting/")]
    items = "".join(f'      <a href="{href}">{html.escape(name)}</a>\n' for name, href in links)
    return (f'<footer class="masthead">\n  <div class="wrap">\n    <nav aria-label="Products">\n{items}    </nav>\n'
            f'    <p>NorviTech © Spencer Norton · <a href="{GH}/norvitech-site">Source</a> · <a href="{GH}">GitHub</a></p>\n'
            f"  </div>\n</footer>")


def siblings(url: str) -> str:
    """Every product, at the foot of a product's page; the page's own product marked."""
    here, rows = product(url), ""
    for p in PRODUCTS:
        mark = ' aria-current="page"' if p is here else ""
        rows += f'  <a class="glass" href="/{p["slug"]}/"{mark}>{html.escape(p["name"])}</a>\n'
    return f'<nav class="siblings" aria-label="Other apps">\n{rows}</nav>'


def stamp(page: Path, text: str) -> str:
    url = url_of(page)
    text = CHROME.sub(lambda m: header(url) if m.group(1) == "header" else footer(), text)
    return SIBLINGS.sub(lambda m: siblings(url), text)


def write_sitemap() -> bool:
    """docs/sitemap.xml: every page's canonical URL, sorted (404.html has none). True if it changed."""
    urls = sorted(m.group(1) for page in DOCS.rglob("*.html")
                  for m in [CANONICAL.search(page.read_text(encoding="utf-8"))] if m)
    rows = "".join(f"  <url><loc>{html.escape(u)}</loc></url>\n" for u in urls)
    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{rows}</urlset>\n')
    if SITEMAP.exists() and SITEMAP.read_text(encoding="utf-8") == xml:
        return False
    SITEMAP.write_text(xml, encoding="utf-8")
    return True


def main() -> int:
    changed = 0
    for page in sorted(DOCS.rglob("*.html")):
        text = page.read_text(encoding="utf-8")
        new = stamp(page, text)
        if new != text:
            page.write_text(new, encoding="utf-8")
            changed += 1
    print(f"{changed} page(s) restamped" + ("; sitemap.xml rewritten" if write_sitemap() else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
