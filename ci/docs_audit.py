#!/usr/bin/env python3
"""Audit the published documentation: does it rebuild, and is it accurate.

    uv run qm docs audit

WHY. `docs.yml` triggers on push and deploys straight to Pages, so the build
*is* the deploy: a pull request never establishes that the site still rebuilds,
and the first evidence of a broken build is a broken published site. Separately,
nothing checks that what the docs say matches the corpus they document.

TWO DIMENSIONS, AND THEY FAIL DIFFERENTLY.

  rebuild    the site config parses and the build inputs are all present. A
             config only one parser accepts is a rebuild that works until the
             day it does not.
  accuracy   every link resolves, every corpus path named exists, and no docs
             page silently duplicates a corpus document.

WHAT THIS CANNOT DO. It does not run the site generator -- that needs the
generator installed, and it belongs in the workflow where the real build
happens. This checks the inputs the build reads and the claims the pages make.
A green result here means the build has what it needs and the pages point at
things that exist. It does not mean a page is *correct*; that is reading.
"""

from __future__ import annotations

import argparse
import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# `[text](target)` where target is not a URL, mail link, or pure anchor.
LINK = re.compile(r"\[[^\]]*\]\(\s*(?!https?://|mailto:|#)([^)\s#]+)(?:#[^)\s]*)?\s*\)")

# A repo path named in a code span, the same shape check_restatements reads.
CITED = re.compile(r"`([A-Za-z0-9_][A-Za-z0-9_./-]*\.(?:md|py|ya?ml|json|toml))`")

# A corpus document a docs page might shadow. Basename collision is crude and
# deliberate: it catches the case that matters -- two pages with the same name
# in two places, which is how a reader ends up with two answers.
CORPUS_DIRS = ("handbook", "records", "perspectives")


def load_config(root: Path) -> list[str]:
    """The site config must parse with a standard parser, not only its own."""
    config = root / "zensical.toml"
    if not config.is_file():
        return [f"{config.name} is missing; the build has no configuration"]
    try:
        tomllib.load(config.open("rb"))
    except Exception as exc:
        return [
            f"zensical.toml is not valid TOML: {exc}. The site generator's own "
            f"parser may accept it and nothing else will -- a config one tool "
            f"reads is a rebuild that works until that tool changes"
        ]
    return []


def check_links(root: Path, docs: Path) -> list[str]:
    problems = []
    for page in sorted(docs.rglob("*.md")):
        rel = page.relative_to(root).as_posix()
        text = page.read_text(encoding="utf-8", errors="replace")
        for match in LINK.finditer(text):
            target = match.group(1)
            # Resolved against the page, then against the repo root: a docs
            # page legitimately points at both its siblings and at the corpus.
            if (page.parent / target).exists() or (root / target).exists():
                continue
            problems.append(f"{rel}: link `{target}` resolves to nothing")
    return problems


def check_citations(root: Path, docs: Path) -> list[str]:
    problems = []
    for page in sorted(docs.rglob("*.md")):
        rel = page.relative_to(root).as_posix()
        text = page.read_text(encoding="utf-8", errors="replace")
        for match in CITED.finditer(text):
            cited = match.group(1)
            if "/" not in cited and any(root.rglob(cited)):
                continue
            if (root / cited).exists() or (page.parent / cited).exists():
                continue
            problems.append(f"{rel}: names `{cited}`, which is not in the repository")
    return problems


def check_duplicates(root: Path, docs: Path) -> list[str]:
    """A docs page sharing a basename with a corpus document, uncited.

    Two pages called `glossary.md` in two directories is how a reader gets two
    answers and no way to tell which governs. Citing the corpus one clears it:
    that makes the docs page a view of something, rather than a rival.
    """
    corpus: dict[str, str] = {}
    for directory in CORPUS_DIRS:
        for path in (root / directory).rglob("*.md"):
            corpus.setdefault(path.name, path.relative_to(root).as_posix())

    problems = []
    for page in sorted(docs.rglob("*.md")):
        twin = corpus.get(page.name)
        if not twin or page.name in ("index.md", "README.md"):
            continue
        text = page.read_text(encoding="utf-8", errors="replace")
        if twin in text:
            continue
        problems.append(
            f"{page.relative_to(root).as_posix()}: shares a name with `{twin}` "
            f"and does not cite it. Two documents with one name give a reader "
            f"two answers and no way to tell which governs"
        )
    return problems


def audit(root: Path) -> dict[str, list[str]]:
    docs = root / "docs"
    if not docs.is_dir():
        return {"rebuild": [f"{docs} does not exist; there is nothing to publish"]}
    pages = list(docs.rglob("*.md"))
    if not pages:
        return {"rebuild": [f"{docs} holds no pages; an empty site would publish clean"]}
    return {
        "rebuild": load_config(root),
        "accuracy: links": check_links(root, docs),
        "accuracy: citations": check_citations(root, docs),
        "accuracy: duplicates": check_duplicates(root, docs),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", default=str(ROOT))
    parser.add_argument("--strict", action="store_true",
                        help="exit non-zero on any finding (default: rebuild only)")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    results = audit(root)

    total = 0
    for dimension, problems in results.items():
        mark = "ok  " if not problems else "FAIL"
        print(f"{mark} {dimension}: {len(problems)} finding(s)")
        for problem in problems:
            print(f"       - {problem}")
        total += len(problems)

    rebuild_broken = bool(results.get("rebuild"))
    print(f"\n{total} finding(s) across {len(results)} dimension(s).")
    print("The site generator is not run here -- that happens in the workflow, "
          "against the real build. This checks what the build reads and what "
          "the pages claim.")

    if rebuild_broken or (args.strict and total):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
