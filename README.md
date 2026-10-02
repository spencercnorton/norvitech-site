<h1 align="center">norvitech.com</h1>

<p align="center">
  <strong>The front door of the NorviTech Suite.</strong><br>
  Plain HTML pages, shared styles and one script, served by GitHub Pages from <code>docs/</code>.
</p>

<p align="center">
  <a href="https://norvitech.com"><img alt="NorviTech Suite" src="https://img.shields.io/badge/NorviTech-Suite-FD8024.svg"></a>
  <a href="https://github.com/spencercnorton/norvitech-site/tags"><img alt="Latest release" src="https://img.shields.io/github/v/tag/spencercnorton/norvitech-site?label=release&sort=semver"></a>
  <a href="LICENSE"><img alt="MIT licence" src="https://img.shields.io/badge/licence-MIT-blue.svg"></a>
  <a href="https://buy.stripe.com/8x26oH2U44f65TRe574wM04"><img alt="Donate" src="https://img.shields.io/badge/donate-Stripe-635bff.svg?logo=stripe&logoColor=white"></a>
</p>

This repository is the source of [norvitech.com](https://norvitech.com): the
illustrated project overview, one page per app, a handful of guides, and the shared brand
assets every NorviTech README embeds. It is deliberately plain — no framework, no build step, no
analytics, and exactly one script — so a change is a diff you can read in full.

## What it does

**A visual overview of the whole suite.** The front page pairs real product
screenshots with short, controllable recordings. Featured releases lead into
an always-visible project grid and the APT install block. `scripts/check.py`
requires every product in the navigation registry to appear exactly once, so
adding a project cannot silently leave the homepage behind. `docs/<app>/` is
that app's own page and guides; `docs/about/` is Spencer.

**A header that follows the page.** On a product's pages the header is about
that product alone: its sections, its documentation, how to get it and its
repository, in the same places for every product. Everywhere else it is
Projects, Consulting, About and GitHub. `scripts/nav.py` holds the list of
products and every menu as data and writes each page's header, footer and row
of products from it, so adding a product is one entry there plus its page.
The menus are native `<details>` elements, and `scripts/check.py` refuses a
page whose header, footer or row is not what `nav.py` renders for it.

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

**Consulting.** [Discern Analytics 2.0 (DA2) consulting](https://norvitech.com/consulting/) —
report builds, scheduled extracts, dashboards and training for hospitals on Oracle
Health (Cerner) Millennium, with six guides:
[DA2 vs Discern Explorer](https://norvitech.com/consulting/da2-vs-discern-explorer/),
[automating scheduled DA2 extracts](https://norvitech.com/consulting/automating-da2-extracts/),
[inflated DA2 totals](https://norvitech.com/consulting/da2-inflated-totals/),
[DA2 date windows and time zones](https://norvitech.com/consulting/da2-dates-and-time-zones/),
[DA2 data into Google, Azure or a warehouse](https://norvitech.com/consulting/da2-to-google-azure-warehouse/) and
[DA2 on the Continuum and CommunityWorks domains](https://norvitech.com/consulting/da2-on-continuum-and-communityworks/).

**Findable by crawlers and assistants alike.** Every indexable page declares a
canonical URL, is listed in `docs/sitemap.xml` (which `check.py` keeps in sync),
and carries one `application/ld+json` block describing what it is. Nothing on a
page is rendered by script, so a crawler that never runs JavaScript sees all of it.

**One script, and the page works without it.** `docs/site.js` plays short
previews only while visible, provides pause controls, drives the copy button,
and ticks a clock that reads from [our public NTP service](https://time.globalentry.systems/).
Reduced motion leaves playback in the visitor's hands. With JavaScript off,
projects remain visible, videos retain native controls, the command remains
selectable text, and the clock does not appear. `scripts/check.py` refuses a second script, an
inline one, an `on*` handler, or anything loaded from another host, so what
executes here stays one reviewable file.

**Light and dark** follow the visitor's system setting; the glass panels fall
back to solid ones where `backdrop-filter` is unavailable or the visitor asked
for reduced transparency; fluid page gutters use the available width from phones to wide desktops.

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
python3 scripts/check.py      # what CI runs: tag balance, links and #fragments, one same-origin script, no e-mail, generated navigation
python3 scripts/nav.py        # after changing the navigation: rewrite every header, footer, product row and the sitemap
```

Indigo's pages are generated from each stable Indigo release, never edited by hand:

```bash
python3 scripts/build_indigo.py --indigo <clone at vX.Y.Z> --ref vX.Y.Z --videos <dir> --zip Indigo-vX.Y.Z.zip
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
  <a href="https://github.com/spencercnorton/conductor">Conductor</a> ·
  <a href="https://github.com/spencercnorton/norvi-os">NorviOS</a> ·
  <a href="https://github.com/spencercnorton/indigo">Indigo</a> ·
  <a href="https://github.com/spencercnorton/roadtrack">Road Track</a> ·
  <a href="https://norvitech.com">norvitech.com</a>
</p>
