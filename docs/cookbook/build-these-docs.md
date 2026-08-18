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

## Where things are

- Source pages: `docs/` (`about/`, `usage/`, `cookbook/`, `ref/`)
- Configuration: `zensical.toml` — site metadata, navigation, theme, and Markdown extensions

## Add a page

1. Create the `.md` file under `docs/`.
2. Add its path to the `nav` list in `zensical.toml`. A page not listed there does not appear in the navigation.
3. Commit and open a pull request, like any other change.

## Linking rules

- Links **between docs pages** are relative paths to the `.md` file: `../ref/namespaces.md`.
- Links **to anything outside `docs/`** — records, handbook pages, source files — use the full GitHub URL: `https://github.com/quaternionmedia/qm/blob/main/...`. The site build cannot reach files outside `docs/`.

## Related

- [zensical.toml](https://github.com/quaternionmedia/qm/blob/main/zensical.toml) — the site configuration
- [Zensical documentation](https://zensical.org/docs/) — configuration reference
