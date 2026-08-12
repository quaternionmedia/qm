# Build these docs

Running the documentation site locally.

## Prerequisites

The site is built with [Zensical](https://zensical.org), which requires Python. The project uses `uv` for dependency management.

```bash
# Install uv if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh

# Sync dependencies
uv sync
```

## Serve locally

```bash
uv run zensical serve
```

The site builds and runs on `http://localhost:8000`. It watches for changes and rebuilds automatically.

## Build for deployment

```bash
uv run zensical build --clean
```

This generates the static site in `site/`, which is deployed to GitHub Pages by `.github/workflows/docs.yml` on push to `main` or `docs`.

## Configuration

The site config lives in `zensical.toml`. Key settings:

- `site_url` — where the docs are published (GitHub Pages)
- `site_name` — "QM Governance"
- `docs_dir` — "docs" (the source directory)
- `nav` — the navigation structure and page order
- Extensions — pymdownx for syntax highlighting, admonitions, superfences (mermaid), etc.

## Editing the docs

All source files are in `docs/`:

```
docs/
├── index.md          landing page
├── about/            explanation and background
├── usage/            tutorials and how-tos
├── cookbook/         practical recipes
└── ref/              reference material
```

Edit a `.md` file, save it, and the local server rebuilds automatically.

## Adding a new page

1. Create the `.md` file in the appropriate directory
2. Add an entry to the `nav` in `zensical.toml`
3. Commit and push

The workflow `.github/workflows/docs.yml` deploys on push to `main` or `docs`.

## Related

- [zensical.toml](https://github.com/quaternionmedia/qm/blob/main/zensical.toml) — the site configuration
- [.github/workflows/docs.yml](https://github.com/quaternionmedia/qm/blob/main/.github/workflows/docs.yml) — the deployment workflow
- [Zensical docs](https://zensical.org/docs/) — Zensical configuration and features
