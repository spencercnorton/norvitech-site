#!/usr/bin/env python3
"""build_indigo.py: Indigo's pages on norvitech.com, from one public Indigo tag.

    scripts/build_indigo.py --indigo DIR --ref vX.Y.Z [--videos DIR] [--zip FILE]
    scripts/build_indigo.py --indigo DIR --ref vX.Y.Z-rc.N --stable vX.Y.Z [...]

--indigo is a clone of github.com/spencercnorton/indigo checked out at --ref.
--ref is a release, or a release candidate while one is out: then the pages are
the candidate's, its zip is the main download, and --stable names the release
offered beside it. A beta is never built: the site links releases and release
candidates only.
Everything under docs/indigo/ is (re)written from it:

  index.html                      the product page (scripts/indigo/landing.html)
  guide/index.html                docs/guide/README.md
  guide/<page>/index.html         docs/guide/<page>.md, in the guide's own order
  guide/settings-file/index.html  docs/SETTINGS.md
  changelog/index.html            CHANGELOG.md
  guide/images/, screenshots/     the pictures those pages show
  videos/                         --videos DIR: <name>.mp4 with <name>.png posters

Every Markdown file goes through GitHub's own renderer, so a page reads exactly
like the repository file it came from; links between them become site links and
anything else in the repository links GitHub at --ref. The header and footer
come from scripts/nav.py, which check.py holds every page to; a release that
adds a guide page fails check.py until Indigo's menus there list it. The row
of products comes from there too, and docs/sitemap.xml is rewritten at the end
from every page's canonical URL. Run scripts/check.py afterwards.

--zip is the release's Indigo-<ref>.zip; its size and SHA-256 go on the
download button. GITHUB_TOKEN or GH_TOKEN, if set, raises the renderer's rate limit.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import posixpath
import re
import shutil
import struct
import sys
import time
import urllib.request
from pathlib import Path, PurePosixPath

from nav import footer, header, siblings, write_sitemap

SITE = Path(__file__).resolve().parent.parent
DOCS = SITE / "docs"
OUT = DOCS / "indigo"
TEMPLATES = Path(__file__).resolve().parent / "indigo"
REPO = "spencercnorton/indigo"
BASE = "https://norvitech.com"

# Pages that are not in docs/guide but belong with it on the site.
EXTRA = {"docs/SETTINGS.md": ("guide/settings-file/", "Settings files"),
         "CHANGELOG.md": ("changelog/", "Changelog")}
# A page whose first paragraph does not say what the page is gets its own words.
DESCRIPTIONS = {"CHANGELOG.md": "What changed in each Indigo release, newest first: "
                                "new screens and settings, fixes and documentation."}
PICTURES = (".png", ".jpg", ".jpeg", ".webp")


def render(markdown: str, token: str | None) -> str:
    """GitHub's rendering of one Markdown document, as a repository file shows it."""
    headers = {"Accept": "application/vnd.github+json", "Content-Type": "application/json",
               "User-Agent": "norvitech-site-indigo-builder"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = json.dumps({"text": markdown, "mode": "markdown"}).encode()
    for attempt in range(4):
        try:
            req = urllib.request.Request("https://api.github.com/markdown", data=body,
                                         headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read().decode("utf-8")
        except OSError:
            if attempt == 3:
                raise
            time.sleep(2 ** attempt)
    raise AssertionError("unreachable")


def regular(path: Path, root: Path) -> Path:
    """path, if it is a regular file inside root: a symlink in a release could
    otherwise put any local file on the public site."""
    real, base = path.resolve(), root.resolve()
    if path.is_symlink() or not path.is_file() or base not in real.parents:
        raise SystemExit(f"not a regular file in the release: {path}")
    return path


def guide_order(indigo: Path) -> list[str]:
    """The guide's pages in the order its index links them; every page must be linked."""
    guide = indigo / "docs/guide"
    index = (guide / "README.md").read_text(encoding="utf-8")
    order: list[str] = []
    for m in re.finditer(r'(?:href="|\]\()([a-z0-9-]+)\.md[")#]', index):
        if m.group(1) != "README" and m.group(1) not in order:
            order.append(m.group(1))
    present = sorted(p.stem for p in guide.glob("*.md") if p.stem != "README")
    missing = sorted(set(present) - set(order))
    if missing:
        raise SystemExit(f"docs/guide/README.md does not link {missing}; the site follows its order")
    return ["README"] + [n for n in order if n in present]


def site_path(repo_path: str, pages: dict[str, str]) -> str | None:
    """Where a repository path lives on the site, or None to link GitHub."""
    if repo_path in pages:
        return pages[repo_path]
    for prefix, target in (("docs/guide/images/", "/indigo/guide/images/"),
                           ("docs/screenshots/", "/indigo/screenshots/")):
        if repo_path.startswith(prefix) and repo_path.lower().endswith(PICTURES):
            return target + repo_path[len(prefix):]
    return None


def link(href: str, source: str, pages: dict[str, str], ref: str) -> str:
    """A link as written in `source` (a repository path), rewritten for the site."""
    if href.startswith(BASE + "/"):
        return href[len(BASE):]  # the docs link this site: here, that is a site link
    if re.match(r"^[a-z][a-z0-9+.-]*:", href) or href.startswith(("#", "//")):
        return href
    path, _, fragment = href.partition("#")
    fragment = f"#{fragment}" if fragment else ""
    if not path:
        return fragment
    base = posixpath.dirname(source)
    joined = path if path.startswith("/") else posixpath.join(base, path)
    target = posixpath.normpath(joined).lstrip("/")
    if target == ".." or target.startswith("../"):
        raise SystemExit(f"{source}: link {href!r} leaves the repository")
    here = site_path(target, pages)
    if here:
        return here + fragment
    kind = "tree" if path.endswith("/") or "." not in posixpath.basename(target) else "blob"
    return f"https://github.com/{REPO}/{kind}/{ref}/{target}{fragment}"


def png_size(path: Path) -> tuple[int, int] | None:
    head = path.read_bytes()[:24]
    if head[:8] == b"\x89PNG\r\n\x1a\n" and head[12:16] == b"IHDR":
        return struct.unpack(">II", head[16:24])
    return None


def transform(fragment: str, source: str, pages: dict[str, str], ref: str,
              indigo: Path) -> tuple[str, str]:
    """(title, body): GitHub's HTML made into a site page body."""
    # GitHub wraps each heading with its permalink; the site gives the heading the id.
    fragment = re.sub(
        r'<div class="markdown-heading"><h([1-6])\b[^>]*>(.*?)</h\1>'
        r'<a id="user-content-([^"]+)" class="anchor"[^>]*>.*?</a></div>',
        lambda m: f'<h{m.group(1)} id="{m.group(3)}">{m.group(2)}</h{m.group(1)}>', fragment, flags=re.S)
    if "markdown-heading" in fragment or "user-content-" in fragment:
        raise SystemExit(f"{source}: GitHub heading markup this builder does not know")
    fragment = fragment.replace("<markdown-accessiblity-table>", "").replace("</markdown-accessiblity-table>", "")
    fragment = re.sub(r'\s+style="max-width: 100%;"', "", fragment)
    fragment = re.sub(r'\s+target="_blank" rel="noopener noreferrer"', "", fragment)
    fragment = re.sub(r'\s+rel="nofollow"', "", fragment)
    # The guide's own breadcrumb line: the site draws its own.
    fragment = re.sub(r'^<p><a href="(?:README\.md|\.\./guide/README\.md)">Indigo guide</a>[^<]*</p>\n', "", fragment)
    # The page title is the first h1; the page header carries it.
    title = "Indigo"
    m = re.search(r"<h1[^>]*>(.*?)</h1>\n?", fragment, re.S)
    if m:
        title = html.unescape(re.sub(r"<[^>]+>", "", m.group(1))).strip()
        fragment = fragment[:m.start()] + fragment[m.end():]

    def relink(m: re.Match) -> str:
        attr, value = m.group(1), html.unescape(m.group(2))
        return f'{attr}="{html.escape(link(value, source, pages, ref), quote=True)}"'

    fragment = re.sub(r'\b(href|src)="([^"]*)"', relink, fragment)
    fragment = re.sub(r'(<a href="/[^"]*">[^<]*</a>) on norvitech\.com', r"\1", fragment)

    def picture(m: re.Match) -> str:
        tag = m.group(0)
        src = re.search(r'src="([^"]*)"', tag)
        if not src or not src.group(1).startswith("/indigo/"):
            return tag
        rel = src.group(1)[len("/indigo/"):]
        repo = ("docs/guide/images/" + rel[len("guide/images/"):]) if rel.startswith("guide/images/") \
            else ("docs/screenshots/" + rel[len("screenshots/"):])
        size = png_size(indigo / repo)
        extra = ' loading="lazy" decoding="async"'
        width = re.search(r'\bwidth="([^"]*)"', tag)
        if size and width and width.group(1).isdigit() and "height=" not in tag:
            w = int(width.group(1))
            extra += f' height="{round(size[1] * w / size[0])}"'
        elif size and not width:
            extra += f' width="{size[0]}" height="{size[1]}"'
        return tag[:-1].rstrip("/").rstrip() + extra + ">"

    fragment = re.sub(r"<img\b[^>]*>", picture, fragment)
    fragment = re.sub(r"<table>", '<div class="table"><table>', fragment)
    fragment = re.sub(r"</table>", "</table></div>", fragment)
    return title, fragment.strip()


APP = {"@type": "SoftwareApplication", "name": "Indigo", "url": f"{BASE}/indigo/",
       "applicationCategory": "UtilitiesApplication", "operatingSystem": "Nintendo GameCube"}
AUTHOR = {"@type": "Person", "name": "Spencer Norton", "url": f"{BASE}/about/"}
PUBLISHER = {"@type": "Organization", "name": "NorviTech", "url": f"{BASE}/",
             "logo": f"{BASE}/assets/logo.svg", "sameAs": ["https://github.com/spencercnorton"]}


def breadcrumbs(trail: list[tuple[str, str]]) -> dict:
    """schema.org BreadcrumbList for (name, site path) from the top down."""
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": n, "name": name, "item": BASE + path}
        for n, (name, path) in enumerate(trail, 1)]}


def structured(graph: list[dict]) -> str:
    """The page's one structured-data block (check.py allows exactly one)."""
    doc = json.dumps({"@context": "https://schema.org", "@graph": graph}, indent=2, ensure_ascii=False)
    doc = doc.replace("</", "<\\/")  # text in a <script> must never close it
    return '<script type="application/ld+json">\n' + doc + "\n</script>"


def page_data(title: str, text: str, url: str, trail: list[tuple[str, str]], body: str) -> str:
    """A guide page: a TechArticle about Indigo, and where it sits on the site."""
    article = {"@type": "TechArticle", "headline": title, "description": text, "url": BASE + url,
               "inLanguage": "en", "about": APP, "author": AUTHOR, "publisher": PUBLISHER,
               "isPartOf": {"@type": "WebSite", "name": "NorviTech", "url": f"{BASE}/"}}
    picture = re.search(r'<img\b[^>]*\bsrc="(/indigo/[^"]+)"', body)
    if picture:
        article["image"] = BASE + picture.group(1)
    return structured([article, breadcrumbs(trail)])


def landing_data(landing: str, description_text: str, ref: str) -> str:
    """The product page: Indigo itself, its place on the site, and the questions it answers."""
    section = landing.split('id="features"', 1)[1].split('id="videos"', 1)[0]
    features = [html.unescape(re.sub(r"<[^>]+>", "", m)) for m in re.findall(r"<h3>(.*?)</h3>", section)]
    app = {**APP, "description": description_text, "applicationSubCategory": "Homebrew",
           "softwareRequirements": "A Nintendo GameCube that already runs Swiss (PicoBoot, PicoLoader, "
                                   "FlippyDrive, GC Loader or the like) and reads an SD card (SD2SP2, "
                                   "SD Gecko or the loader's own slot), or a Wii with GameCube ports in "
                                   "GameCube mode.",
           "@id": f"{BASE}/indigo/#app", "featureList": features,
           "license": "https://www.gnu.org/licenses/old-licenses/gpl-2.0.html",
           "isAccessibleForFree": True, "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
           "isBasedOn": {"@type": "SoftwareSourceCode", "name": "Swiss",
                         "codeRepository": "https://github.com/emukidid/swiss-gc"},
           "sameAs": [f"https://github.com/{REPO}"],
           "softwareVersion": ref[1:], "downloadUrl": f"https://github.com/{REPO}/releases/tag/{ref}",
           "softwareHelp": f"{BASE}/indigo/guide/", "screenshot": f"{BASE}/indigo/screenshots/home.png",
           "image": f"{BASE}/assets/og-indigo.png", "author": AUTHOR, "publisher": PUBLISHER}
    questions = [{"@type": "Question", "name": html.unescape(re.sub(r"<[^>]+>", "", q)).strip(),
                  "acceptedAnswer": {"@type": "Answer",
                                     "text": html.unescape(re.sub(r"<[^>]+>", "", a)).strip()}}
                 for q, a in re.findall(r"<details><summary>(.*?)</summary><p>(.*?)</p></details>", landing, re.S)]
    # The code is its own thing in schema.org: a SoftwareSourceCode whose product is the app.
    source = {"@type": "SoftwareSourceCode", "name": "Indigo", "codeRepository": f"https://github.com/{REPO}",
              "programmingLanguage": "C", "license": app["license"], "targetProduct": {"@id": app["@id"]}}
    graph = [app, source, breadcrumbs([("NorviTech", "/"), ("Indigo", "/indigo/")])]
    if questions:
        graph.append({"@type": "FAQPage", "mainEntity": questions})
    return structured(graph)


def description(body: str, fallback: str) -> str:
    for m in re.finditer(r"<p\b[^>]*>(.*?)</p>", body, re.S):
        text = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", m.group(1)))).strip()
        if len(text) > 60:
            return text if len(text) <= 158 else text[:155].rsplit(" ", 1)[0] + "…"
    return fallback


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--indigo", required=True, type=Path, help="Indigo clone at --ref")
    ap.add_argument("--ref", required=True, help="the release (vX.Y.Z) or release candidate (vX.Y.Z-rc.N) the pages show")
    ap.add_argument("--stable", help="with a release candidate as --ref: the release offered beside it, e.g. v1.25.0")
    ap.add_argument("--videos", type=Path, help="directory of <name>.mp4 + <name>.png")
    ap.add_argument("--zip", type=Path, help="the release's Indigo-<ref>.zip, for size and SHA-256")
    args = ap.parse_args()
    indigo, ref = args.indigo.resolve(), args.ref
    m = re.fullmatch(r"v(\d+)\.(\d+)\.(\d+)(-rc\.\d+)?", ref)
    if not m:
        raise SystemExit("--ref must be a release (vX.Y.Z) or a release candidate (vX.Y.Z-rc.N)")
    rc, base = bool(m.group(4)), ".".join(m.groups()[:3])
    stable = args.stable
    if rc != bool(stable) or (stable and not (
            re.fullmatch(r"v\d+\.\d+\.\d+", stable)
            and tuple(map(int, stable[1:].split("."))) < tuple(map(int, m.groups()[:3])))):
        raise SystemExit("--stable goes with a release candidate as --ref, and names an older release")
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")

    names = guide_order(indigo)
    pages = {f"docs/guide/{n}.md": ("/indigo/guide/" if n == "README" else f"/indigo/guide/{n}/")
             for n in names}
    pages.update({src: f"/indigo/{dst}" for src, (dst, _) in EXTRA.items()})
    pages["README.md"] = "/indigo/"

    sources = [f"docs/guide/{n}.md" for n in names] + list(EXTRA)
    rendered: dict[str, tuple[str, str]] = {}
    for src in sources:
        md = regular(indigo / src, indigo).read_text(encoding="utf-8")
        rendered[src] = transform(render(md, token), src, pages, ref, indigo)
    rendered["docs/guide/README.md"] = ("Indigo guide", rendered["docs/guide/README.md"][1])
    if rc:  # a candidate's changes still sit under Unreleased: say what they are
        title, body = rendered["CHANGELOG.md"]
        rendered["CHANGELOG.md"] = (title, body.replace('<h2 id="unreleased">Unreleased</h2>',
                                                        f'<h2 id="unreleased">{base} release candidate</h2>', 1))

    if OUT.exists():
        shutil.rmtree(OUT)
    written: list[Path] = []
    OUT.mkdir(parents=True)
    videos: list[str] = []
    if args.videos:
        (OUT / "videos").mkdir(parents=True)
        for mp4 in sorted(args.videos.glob("*.mp4")):
            posters = [mp4.with_suffix(".png"), mp4.with_name(mp4.stem + "-poster.png")]
            poster = next((p for p in posters if p.is_file()), None)
            if not poster:
                raise SystemExit(f"{mp4.name} has no poster ({posters[0].name} or {posters[1].name})")
            # Same guard as the release's pictures: a symlink here could publish any local file.
            for f, name in ((regular(mp4, args.videos), mp4.name), (regular(poster, args.videos), mp4.stem + ".png")):
                shutil.copyfile(f, OUT / "videos" / name)
                written.append(OUT / "videos" / name)
            videos.append(mp4.stem)

    page_tpl = (TEMPLATES / "page.html").read_text(encoding="utf-8")
    nav_guide = [(src, pages[src], rendered[src][0]) for src in sources if src.startswith("docs/guide/")]
    nav_ref = [(src, pages[src], rendered[src][0]) for src in EXTRA]

    def nav(current: str) -> str:
        def item(src: str, url: str, title: str) -> str:
            label = "Overview" if src == "docs/guide/README.md" else title
            mark = ' aria-current="page"' if src == current else ""
            return f'<li><a href="{url}"{mark}>{html.escape(label)}</a></li>'
        return ("<p>Guide</p>\n<ul>\n" + "\n".join(item(*x) for x in nav_guide) + "\n</ul>\n"
                "<p>Reference</p>\n<ul>\n" + "\n".join(item(*x) for x in nav_ref) + "\n</ul>")

    flow = [src for src, _, _ in nav_guide + nav_ref]
    for i, src in enumerate(flow):
        title, body = rendered[src]
        url = pages[src]
        crumbs = '<a href="/#suite">Suite</a> / <a href="/indigo/">Indigo</a>'
        trail = [("NorviTech", "/"), ("Indigo", "/indigo/")]
        if url != "/indigo/guide/":
            crumbs += ' / <a href="/indigo/guide/">Guide</a>' if src.startswith("docs/guide/") else ""
            trail += [("Guide", "/indigo/guide/")] if src.startswith("docs/guide/") else []
        trail.append((title, url))
        # What a search result shows: the page, then where it belongs.
        head = ("Indigo guide · NorviTech" if url == "/indigo/guide/" else
                f"{title} · Indigo guide · NorviTech" if src.startswith("docs/guide/") else
                f"{title} · Indigo · NorviTech")
        summary = DESCRIPTIONS.get(src) or description(body, f"{title}: the Indigo guide.")
        pager = []
        if i > 0:
            p = flow[i - 1]
            pager.append(f'<a class="prev" href="{pages[p]}"><small>Previous</small>{html.escape(rendered[p][0])}</a>')
        if i + 1 < len(flow):
            n = flow[i + 1]
            pager.append(f'<a class="next" href="{pages[n]}"><small>Next</small>{html.escape(rendered[n][0])}</a>')
        out = page_tpl.format(
            title=html.escape(title), head=html.escape(head), crumbs=crumbs, nav=nav(src), body=body,
            pager="\n".join(pager), canonical=BASE + url, description=html.escape(summary),
            structured=page_data(title, summary, url, trail, body),
            source=html.escape(f"https://github.com/{REPO}/blob/{ref}/{src}"),
            edit=html.escape(f"https://github.com/{REPO}/edit/beta/{src}"),  # changes go to beta, never main
            path=html.escape(src), ref=html.escape(ref), header=header(url), footer=footer())
        target = DOCS / url.lstrip("/") / "index.html"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(out, encoding="utf-8")

    zip_url = f"https://github.com/{REPO}/releases/download/{ref}/Indigo-{ref}.zip"
    zip_size, zip_sum = "the SD card zip", "listed on the release"
    if args.zip:
        zip_size = f"{args.zip.stat().st_size / 1e6:.1f} MB"
        zip_sum = f"<code>{hashlib.sha256(args.zip.read_bytes()).hexdigest()[:16]}…</code>"
    name = f"Indigo {base} release candidate" if rc else f"Indigo {base}"
    blurb = (f"{base} as it is meant to ship, for a last round of testing before it does." if rc
             else "The release for everyday use.")
    stable_card = ""
    if stable:
        stable_card = (f'  <div class="glass"><h3>Indigo {stable[1:]}</h3><p>The current release, for everyday use.'
                       f'</p><p class="cta"><a class="secondary" href="https://github.com/{REPO}/releases/'
                       f'download/{stable}/Indigo-{stable}.zip">Indigo-{stable}.zip</a></p><p class="meta"><a '
                       f'href="https://github.com/{REPO}/releases/tag/{stable}">Release notes</a></p></div>\n')
    guide_cards = "\n".join(
        f'  <a class="glass" href="{url}"><strong>{html.escape(title)}</strong></a>'
        for src, url, title in nav_guide[1:] + nav_ref)
    landing = (TEMPLATES / "landing.html").read_text(encoding="utf-8")
    for key, value in {"{{header}}": header("/indigo/"), "{{footer}}": footer(), "{{ref}}": ref,
                       "{{name}}": name, "{{blurb}}": blurb, "{{stable}}\n": stable_card,
                       "{{zip_url}}": zip_url, "{{zip_size}}": zip_size,
                       "{{zip_sum}}": zip_sum, "{{guide_cards}}": guide_cards,
                       "{{siblings}}": siblings("/indigo/")}.items():
        landing = landing.replace(key, value)
    summary = html.unescape(re.search(r'<meta name="description" content="([^"]*)">', landing).group(1))
    landing = landing.replace("{{structured}}", landing_data(landing, summary, ref))
    landing = re.sub(r"\{\{video:([a-z-]+)\|([^|]*)\|([^}]*)\}\}",
                     lambda m: video_or_picture(m.group(1), m.group(2), m.group(3), videos), landing)
    if "{{" in landing:
        raise SystemExit("landing.html: unfilled placeholder " + re.search(r"\{\{[^}]*\}\}", landing).group(0))
    (OUT / "index.html").write_text(landing, encoding="utf-8")

    # Only the pictures a page shows are copied: the site pins every file it
    # carries, so an unused README animation would be weight for nothing.
    shown = set()
    for page in OUT.rglob("index.html"):
        shown.update(re.findall(r'(?:src|href|poster)="/indigo/((?:guide/images|screenshots)/[^"#]+)"',
                                page.read_text(encoding="utf-8")))
    out_root = OUT.resolve()
    for rel in sorted(shown):
        # A path in a page is data from the release: refuse any that climbs out,
        # and prove the destination stays under docs/indigo/ before writing.
        if ".." in PurePosixPath(rel).parts:
            raise SystemExit(f"picture path {rel!r} climbs out of its folder")
        repo = ("docs/guide/images/" + rel[len("guide/images/"):]) if rel.startswith("guide/images/") \
            else "docs/screenshots/" + rel[len("screenshots/"):]
        target = (OUT / rel).resolve()
        target.relative_to(out_root)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(regular(indigo / repo, indigo), target)
        written.append(target)
    write_sitemap()
    big = [p for p in written if p.stat().st_size > 8 << 20]
    if big:
        raise SystemExit(f"over 8 MiB, re-encode for a quick page: {[str(p) for p in big]}")
    print(f"indigo {ref}: {len(flow)} pages, {len(written)} files "
          f"({sum(p.stat().st_size for p in written) / 1e6:.1f} MB), {len(videos)} videos")
    return 0


def video_or_picture(name: str, fallback: str, alt: str, videos: list[str]) -> str:
    """A clip when --videos had it, else the README's own picture of the same thing.
    Clips are short and silent: site.js loops each one while it is on screen and
    gives it a pause button. Without site.js, or with reduced motion, it keeps
    these native controls and plays only when asked."""
    if name in videos:
        return (f'<div class="clip"><video controls muted loop playsinline preload="none" '
                f'poster="/indigo/videos/{name}.png" aria-label="{html.escape(alt, quote=True)}">'
                f'<source src="/indigo/videos/{name}.mp4" type="video/mp4"></video></div>')
    return f'<img src="{fallback}" alt="{html.escape(alt, quote=True)}" loading="lazy" decoding="async">'


if __name__ == "__main__":
    sys.exit(main())
