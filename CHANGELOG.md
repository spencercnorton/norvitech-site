# Changelog

## Unreleased

- Replace the homepage carousel with an illustrated, responsive project overview,
  featuring Indigo 2.0.1, the BitAgent dashboard and all eight current projects.
- Use the available page width with fluid gutters, and restore the MSc timeline label.
- Refresh the About project list and release-workflow description.
- Give animated previews pause controls, static posters, off-screen suspension and
  live reduced-motion support; clarify the NorviOS preview's development status.

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
- The Indigo pages can be built from a release candidate (`--ref vX.Y.Z-rc.N
  --stable vX.Y.Z`): the candidate is the main download, labelled as one, with
  the release beside it; the Features describe Indigo 2.0; the structured data
  names the version offered, and the changelog names its section.
- Indigo's pages are built from v2.0.1, the Latest release: its guide,
  pictures and changelog, the 2.0 clips (and a new one of the device picker),
  and the 2.0 share image and home page spotlight.
- `check.py` fails on any Indigo link that can lead to a beta: the list of
  releases, its feed, the tags or a `-beta` tag.

