# Changelog

## Unreleased

- Establish GitHub pull requests as the development workflow, with privacy checks.
- Add deployment, configuration, security, upgrade and recovery documentation.
- Add five illustrated operations guides and a Conductor product page.
- Generate the row of products at the foot of each product's page from the
  navigation list, so every row now includes Conductor, and check it.
- Keep Conductor and the deployment guides in the navigation list itself.
- Describe the home page without listing products, which had left out Indigo and Conductor.
- Bring the Indigo page builder into this repository, so Indigo's pages are
  regenerated here from each stable release; it reproduces the current pages exactly.
- `scripts/nav.py` also writes the sitemap from every page's canonical URL.
- Indigo's clips play like the short animations they are: each loops while it is
  on screen, has a pause button, and fades into the page instead of sitting in a
  black player; with reduced motion they keep their controls.
- Indigo's "What it does" is now Features, and each card links as a whole.
- Indigo's page links only releases: no Beta card or channel, and release notes
  go to the latest release.
- Indigo's install directions were checked against the code and each loader's
  documentation (PicoLoader, FlippyDrive, chips with Swiss in flash, the games
  folder, Wii). The builder can correct a release's own docs where a reader acts
  on them, and does for 1.25.0, which starts a stock Swiss kept as `z.dol`.

