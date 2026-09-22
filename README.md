<h1 align="center">norvitech.com</h1>

<p align="center">
  <strong>The front door of the NorviTech Suite.</strong><br>
  Seven HTML pages and one stylesheet, served by GitHub Pages from <code>docs/</code>.
</p>

<p align="center">
  <a href="https://norvitech.com"><img alt="NorviTech Suite" src="https://img.shields.io/badge/NorviTech-Suite-FD8024.svg"></a>
  <a href="https://github.com/spencercnorton/norvitech-site/tags"><img alt="Latest release" src="https://img.shields.io/github/v/tag/spencercnorton/norvitech-site?label=release&sort=semver"></a>
  <a href="LICENSE"><img alt="MIT licence" src="https://img.shields.io/badge/licence-MIT-blue.svg"></a>
  <a href="https://buy.stripe.com/8x26oH2U44f65TRe574wM04"><img alt="Donate" src="https://img.shields.io/badge/donate-Stripe-635bff.svg?logo=stripe&logoColor=white"></a>
</p>

This repository is the source of [norvitech.com](https://norvitech.com): the
suite overview, one card per app, and the shared brand assets every NorviTech
README embeds. It is deliberately plain — no scripts, no build step, no
analytics — so a change is a diff you can read in full.

## What it does

**One card per app, one page per app.** `docs/index.html` lists every app in
the suite with its one-line pitch, licence, platform and links; `docs/<app>/`
is that app's own page — what it does, how to install it, where its data
lives, its documentation — written from its README. `docs/about/` is Spencer.
The Apps menu in the header is a native `<details>` element, so it needs no
script. Light and dark follow the visitor's system setting; the glass panels
fall back to solid ones where `backdrop-filter` is unavailable or the visitor
asked for reduced transparency; the layout works from phone width up.

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
python3 scripts/check.py      # what CI runs: tag balance, links, no scripts, no e-mail, one shared header/footer
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
