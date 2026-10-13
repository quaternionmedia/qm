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
LINK = re.compile(r"\[[^\]]*\]\(\s*(?!https?://|mailto:|#)([^)\s#]+)(?:#([^)\s]*))?\s*\)")

# A heading becomes an anchor by lowercasing and joining words with hyphens.
# This mirrors the site generator rather than importing it, so it is an
# approximation -- close enough to catch a fragment naming nothing, and it
# says so when it complains.
HEADING = re.compile(r"^#{1,6}\s+(.+?)\s*$", re.M)
EXPLICIT_ANCHOR = re.compile(r"\{\s*#([A-Za-z0-9_-]+)\s*\}")


def anchors_in(text: str) -> set[str]:
    """Every fragment a page offers: explicit `{ #id }` and heading slugs."""
    found = set(EXPLICIT_ANCHOR.findall(text))
    for heading in HEADING.findall(text):
        cleaned = EXPLICIT_ANCHOR.sub("", heading)
        cleaned = re.sub(r"[`*_\[\]()]", "", cleaned)
        found.add(re.sub(r"[^a-z0-9]+", "-", cleaned.lower()).strip("-"))
    return found

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
            target, fragment = match.group(1), match.group(2)
            resolved = (page.parent / target).resolve()

            # A relative link is published, so it has to land inside the site.
            # This check used to accept any target that existed anywhere in the
            # repository, on the reasoning that a docs page legitimately points
            # at the corpus. On disk that is true; on the built site it is a
            # 404, because only `docs/` is published. `docs/index.md` linked
            # `../handbook/glossary.md`, the file existed, the check passed and
            # the published link was dead -- while the same page linked the
            # same glossary correctly a few lines further down.
            if resolved.is_file() or resolved.is_dir():
                try:
                    resolved.relative_to(docs.resolve())
                except ValueError:
                    problems.append(
                        f"{rel}: link `{target}` leaves the site. It resolves on "
                        f"disk and 404s once published, because only `docs/` is "
                        f"deployed. Link the page under `docs/` that covers it, "
                        f"or use the full https://github.com/... URL.")
                    continue

                # A fragment naming nothing lands the reader at the top of the
                # page instead of at the thing they clicked, which reads as the
                # link having worked. The regex used to discard the fragment
                # entirely, so this was never checked.
                if fragment and resolved.is_file():
                    available = anchors_in(
                        resolved.read_text(encoding="utf-8", errors="replace"))
                    if fragment not in available:
                        problems.append(
                            f"{rel}: link `{target}#{fragment}` names no anchor "
                            f"on that page, so it opens at the top. Add "
                            f"`{{ #{fragment} }}` there, or link a heading that "
                            f"exists. (Anchor slugs are approximated here, not "
                            f"taken from the site generator.)")
                continue

            # A repo-root-relative target that is not under `docs/` is the same
            # mistake spelled differently.
            if (root / target).exists():
                problems.append(
                    f"{rel}: link `{target}` points outside the published site. "
                    f"Use a page under `docs/`, or the full GitHub URL.")
                continue

            problems.append(f"{rel}: link `{target}` resolves to nothing")
    return problems


def check_citations(root: Path, docs: Path) -> list[str]:
    problems = []
    for page in sorted(docs.rglob("*.md")):
        rel = page.relative_to(root).as_posix()
        text = page.read_text(encoding="utf-8", errors="replace")
        # A path that is the visible text of a link pointing at another
        # repository is that repository's file, not a claim about this one.
        # Without this, a docs page citing `qmcp/cookbook/delta.py` beside a
        # link to qmcp was reported as naming a file that does not exist here,
        # which is true and not a defect.
        elsewhere = set(re.findall(
            r"\[`([^`]+)`\]\(https?://[^)]*\)", text))

        for match in CITED.finditer(text):
            cited = match.group(1)
            if cited in elsewhere:
                continue
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
