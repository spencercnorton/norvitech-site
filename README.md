<h1 align="center">norvitech.com</h1>

<p align="center">
  <strong>The front door of the NorviTech Suite.</strong><br>
  Plain HTML pages, one stylesheet and one script, served by GitHub Pages from <code>docs/</code>.
</p>

<p align="center">
  <a href="https://norvitech.com"><img alt="NorviTech Suite" src="https://img.shields.io/badge/NorviTech-Suite-FD8024.svg"></a>
  <a href="https://github.com/spencercnorton/norvitech-site/tags"><img alt="Latest release" src="https://img.shields.io/github/v/tag/spencercnorton/norvitech-site?label=release&sort=semver"></a>
  <a href="LICENSE"><img alt="MIT licence" src="https://img.shields.io/badge/licence-MIT-blue.svg"></a>
  <a href="https://buy.stripe.com/8x26oH2U44f65TRe574wM04"><img alt="Donate" src="https://img.shields.io/badge/donate-Stripe-635bff.svg?logo=stripe&logoColor=white"></a>
</p>

This repository is the source of [norvitech.com](https://norvitech.com): the
suite spotlight, one page per app, a handful of guides, and the shared brand
assets every NorviTech README embeds. It is deliberately plain — no framework, no build step, no
analytics, and exactly one script — so a change is a diff you can read in full.

## What it does

**A spotlight, then one command, and nothing else.** The front page is a
carousel of each app actually running — the animations are the products' own
reviewed recordings — over a one-line install block that copies the whole APT
setup to the clipboard. That is the whole page: the prose sections that used
to explain the release process and the support routes were cut on 2026-09-22,
because every one of them is already said, per product, in the place someone
actually reads it. `docs/<app>/` is that app's own page (what it does, how to install
it, where its data lives, its documentation, written from its README) and
`docs/about/` is Spencer. The Apps menu in the header is a native `<details>`
element.

**Guides that answer the question before the product does.** Each explains the
platform problem first, says what the sanctioned answer costs, and only then
what the app does about it — with a section on when you should not use it:

- [Helios vs. Claude Code in a terminal](https://norvitech.com/helios/vs-terminal/) —
  same CLI underneath; what changes, and when the terminal is the right answer.
- [Screenshots on GNOME Wayland without a permission prompt](https://norvitech.com/snipsnap/wayland-screenshots/) —
  what the portal path costs, and drawing the selection inside the compositor.
- [Why Wayland will not let an app place its own window](https://norvitech.com/xnote-placement/wayland-window-placement/) —
  what the protocol withholds, and what has to live in GNOME Shell instead.
- [BitAgent and bitmagnet](https://norvitech.com/bitagent/vs-bitmagnet/) —
  what is still upstream's work, what the fork adds, and reasons to stay upstream.

**Findable by crawlers and assistants alike.** Every indexable page declares a
canonical URL, is listed in `docs/sitemap.xml` (which `check.py` keeps in sync),
and carries one `application/ld+json` block describing what it is. Nothing on a
page is rendered by script, so a crawler that never runs JavaScript sees all of it.

**One script, and the page works without it.** `docs/site.js` auto-advances
the spotlight, drives the copy button, and ticks a clock that reads its time
from [our own public NTP service](https://time.globalentry.systems/) rather
than the visitor's machine. With JavaScript off the carousel is still a
swipeable scroll-snap track, the command is still selectable text, and the
clock simply does not appear. `scripts/check.py` refuses a second script, an
inline one, an `on*` handler, or anything loaded from another host, so what
executes here stays one reviewable file.

**Light and dark** follow the visitor's system setting; the glass panels fall
back to solid ones where `backdrop-filter` is unavailable or the visitor asked
for reduced transparency; the layout runs from phone width to 1680 px.

**Shared brand assets.** `docs/assets/` holds the NorviTech mark, the README
banner (`banner.svg`) and the Open Graph card. Every product README hot-links
the banner from here, so the suite stays visually one thing.

**Served by GitHub Pages.** `main:/docs` is the site; `CNAME` names the
domain; `.nojekyll` keeps Pages from touching the files.

## Install

### Any platform — run it locally

```bash
git clone https://github.com/spencercnorton/norvitech-site.git
cd norvitech-site
python3 -m http.server -d docs 8000    # then open http://localhost:8000
```

## Contributing and support

- Bugs and feature requests: [open an issue](https://github.com/spencercnorton/norvitech-site/issues/new/choose). Questions: [Discussions](https://github.com/spencercnorton/norvitech-site/discussions).
- Security reports: [private vulnerability reporting](https://github.com/spencercnorton/norvitech-site/security/advisories/new) — see [SECURITY.md](SECURITY.md). There is no e-mail address; that is deliberate.
- Pull requests are welcome; read [CONTRIBUTING.md](CONTRIBUTING.md) first — this repository is a release mirror, and accepted changes ship in the next tagged release.
- If one of the NorviTech apps saves you time, you can [support its development](https://buy.stripe.com/8x26oH2U44f65TRe574wM04).

## Development

```bash
python3 scripts/check.py      # what CI runs: tag balance, links, one same-origin script, no e-mail, one shared header/footer
```

## Licence

[MIT](LICENSE) © Spencer Norton

---

<p align="center">
  <a href="https://norvitech.com"><img alt="Part of the NorviTech Suite — open-source apps for the Linux desktop and the self-hosted stack" src="https://norvitech.com/assets/banner.svg" width="640"></a>
</p>

<p align="center">
  <a href="https://github.com/spencercnorton/helios">Helios</a> ·
  <a href="https://github.com/spencercnorton/bitagent">BitAgent</a> ·
  <a href="https://github.com/spencercnorton/xnote">XNote</a> ·
  <a href="https://github.com/spencercnorton/xnote-placement">XNote Placement</a> ·
  <a href="https://github.com/spencercnorton/snipsnap">SnipSnap</a> ·
  <a href="https://norvitech.com">norvitech.com</a>
</p>
