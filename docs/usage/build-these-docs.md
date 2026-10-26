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
- Configuration: `zensical.toml` — site metadata, navigation, theme, and Markdown extensions

## Add a page

1. Create the `.md` file under `docs/`.
2. Add its path to the `nav` list in `zensical.toml`. A page not listed there does not appear in the navigation.
3. Commit and open a pull request, like any other change.

## Linking rules

- Links **between docs pages** are relative paths to the `.md` file: `../ref/namespaces.md`.
- Links **to anything outside `docs/`** — records, [handbook](../ref/glossary.md#handbook){ .glossary-term } pages, source files — use the full GitHub URL: `https://github.com/quaternionmedia/qm/blob/main/...`. The site build cannot reach files outside `docs/`.

## Related

- [zensical.toml](https://github.com/quaternionmedia/qm/blob/main/zensical.toml) — the site configuration
- [Zensical documentation](https://zensical.org/docs/) — configuration reference
