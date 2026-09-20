# Contributing to the NorviTech site

Thanks for your interest. This site is a small project with one maintainer, so
the process is deliberately light — but a few things are fixed.

## How changes land

This GitHub repository is a **release mirror**: every commit on `main` is a
tagged release built from a private development tree, and `main` only ever
moves forward by a release. That has two consequences for contributors:

- Pull requests are reviewed **here**, but they are not merged here. An
  accepted change is applied to the development tree and ships in the next
  tagged release; the pull request is then closed with a reference to that
  release, and you keep the credit in the release notes.
- Please do not rebase your pull request onto anything but `main`.

## Before you start

- **Bugs** — open a [bug report](https://github.com/spencercnorton/norvitech-site/issues/new/choose).
  A report with reproduction steps, versions and a scrubbed log excerpt is
  usually fixed faster than a pull request that arrives without one.
- **Changes to the page** — open a feature request first. The site is
  deliberately plain: one HTML file, one stylesheet, no scripts, no build
  step; an idea that needs more than that needs a conversation before code.
- **Security** — never in a public issue. Use
  [private vulnerability reporting](https://github.com/spencercnorton/norvitech-site/security/advisories/new);
  see [SECURITY.md](SECURITY.md).

## Working on the code

```bash
python3 -m http.server -d docs 8000   # then open http://localhost:8000
python3 scripts/check.py              # what CI runs: tag balance, links, no scripts
```

- Everything under `docs/` is served as-is by GitHub Pages; there is no build
  step, and nothing outside `docs/` reaches the site.
- Keep a change to one concern. A pull request that fixes a bug and
  reformats a file is two pull requests.
- Tests: a bug fix carries a regression test; a feature carries the smallest
  test that fails without it.
- Commits carry a `Signed-off-by:` line (`git commit -s`, the Developer
  Certificate of Origin). There is no CLA.
- No secrets, hostnames, personal data or screenshots of a real desktop in
  the diff — the export gate rejects them and the pull request will be sent
  back.

## Out of scope

So nobody wastes an evening on it, this site will not accept:

- analytics, tracking or cookies of any kind
- JavaScript, a framework or a static-site generator
- a blog, a comments system or anything that stores visitor data

## Pull request checklist

The template asks for what changed, why, and how it was tested, plus a
confirmation that the diff carries no secrets, machine names or personal
paths. Fill it in — it is what the reviewer reads first.

## Licence

By contributing you agree that your contribution is licensed under the
[MIT licence](LICENSE) that covers the project.
