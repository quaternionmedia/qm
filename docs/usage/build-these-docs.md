# Build these docs

Run the documentation site on your machine.

## Prerequisites

The site is built with [Zensical](https://zensical.org). Dependencies are managed with [uv](https://docs.astral.sh/uv/):

```bash
uv sync
```

## Serve locally

```bash
uv run zensical serve
```

The site runs at `http://localhost:8000` and rebuilds when you save a file.

## Build the static site

```bash
uv run zensical build --clean
```

This writes the site to `site/`, which is not committed. On a push to `main`, the workflow `.github/workflows/docs.yml` builds and deploys the site to GitHub Pages.

## Preview a project's pictures from a branch { #preview-a-projects-pictures-from-a-branch }

A project page shows only the pictures its project's default branch holds, so a page whose pictures are still on a pull request in that project shows them as waiting. To see it as it will look, build a preview with the pictures taken from the branch:

```bash
uv run qm cookbook --preview .preview --ref alfred=<branch>
uv run --extra docs zensical serve -f .preview/zensical.toml -a 127.0.0.1:8400
```

The first command copies `docs/`, `includes/` and `zensical.toml` into `.preview/`, which git ignores, and regenerates the family and project pages there, alfred's pictures taken from the commit `<branch>` points at. It reads the host, so it needs `gh` signed in. The second serves that copy at `http://127.0.0.1:8400`; alfred's page is `http://127.0.0.1:8400/projects/alfred/`. `--ref` takes a branch, a tag or a commit, and repeats for more projects. A page whose pictures come from a ref says it is a preview, and nothing under `docs/` or `includes/` is written: `--ref` without `--preview` is refused.

## Where things are

- Source pages: `docs/` (`about/`, `usage/`, `ref/`), and the generated `families/` and `projects/`; the front page includes its showcase from the generated `includes/`
- The showcase: `ci/showcase.yaml`, the pictures a person picked for each project
- The showgraphs: `docs/show/`, the graphs codecartographer drew, each subject's pictures beside its `show.json`
- Configuration: `zensical.toml` — site metadata, navigation, theme, and Markdown extensions

## The family and project pages

Every page under `docs/families/` and `docs/projects/`, and every snippet under `includes/`, is written by one command:

```bash
uv run qm cookbook docs/families --site --write
```

It reads four sources, and a page is changed by changing one of them, never the page:

- `families.json`, the families and their members, generated from the family [record](../ref/glossary.md#record){ .glossary-term };
- `status/inventory.yaml`, the org's public repositories as the host describes them, and which listed pictures each default branch holds;
- `ci/showcase.yaml`, the **showcase**: pictures a person picked, each a file on the project's own default branch, with a one-sentence caption. A picture the default branch does not hold yet is held back; preview it as above;
- `docs/show/`, the **showgraphs**: graphs a tool drew, written with `uv run codecarto show export` in codecartographer. Each subject's `show.json` says what was drawn, from which commits, by which tool at which commit, and when, and the page prints that beneath the pictures.

A project's version on its page comes from whether the [corpus](../ref/glossary.md#corpus){ .glossary-term } has a `project/<name>` branch, so run the command in a clone that has fetched every branch.

`--check` in place of `--write` lists the pages that no longer match their sources. The `docs-audit` workflow runs it on every pull request that touches the pages or their sources, and fails on any. The rules behind the pages are in [the project-page record](https://github.com/quaternionmedia/qm/blob/main/records/DRAFT-a-project-page-shows-what-was-picked-and-what-was-drawn.md).

## Add a page

A family or project page is not added by hand: it appears when the roster names the family or the project, and the command above runs.

For any other page:

1. Create the `.md` file under `docs/`.
2. Add its path to the `nav` list in `zensical.toml`. A page not listed there does not appear in the navigation.
3. Commit and open a pull request, like any other change.

## Linking rules

- Links **between docs pages** are relative paths to the `.md` file: `../ref/namespaces.md`.
- Links **to anything outside `docs/`** — records, [handbook](../ref/glossary.md#handbook){ .glossary-term } pages, source files — use the full GitHub URL: `https://github.com/quaternionmedia/qm/blob/main/...`. The site build cannot reach files outside `docs/`.

## Related

- [zensical.toml](https://github.com/quaternionmedia/qm/blob/main/zensical.toml) — the site configuration
- [Zensical documentation](https://zensical.org/docs/) — configuration reference
