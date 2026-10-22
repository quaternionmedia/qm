"""Link the first use of a glossary term on each page to its definition.

Only the first use per page is linked: that is where a reader decides whether
they know the word, and linking every occurrence makes a page of underlines.

The pass is a fixed point: running it twice changes nothing, because an
already-linked term is done. It therefore rides the ordinary command
(`show-it-by-running-it`), and drift arrives as an uncommitted diff.

Left alone: code spans and fenced or indented code, headings (a linked heading
breaks its own anchor), existing link text and URLs, and the glossary pages
themselves.

What this cannot do: know whether the word is used in the glossary's sense.
`gate` in a record means a CI check, and `gate` in a sentence about an airport
does not. The check prints this limit. `docs/ref/ci/docs-tooling.md` describes
the pass.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

DOCS = Path("docs")
GLOSSARY = DOCS / "ref" / "glossary.md"

# `**Adoption by reference** { #adoption-by-reference }`
TERM = re.compile(r"^\*\*(?P<term>[^*]+)\*\*\s*\{\s*#(?P<anchor>[a-z0-9-]+)\s*\}",
                  re.MULTILINE)

# Pages that define the vocabulary, or point at it, rather than using it.
SKIP = {Path("docs/ref/glossary.md")}

# Pages another generator writes. `ci/cookbook.py --site` owns docs/families/,
# and two generators writing one page would each report the other's output as
# drift.
GENERATED = (Path("docs/families"),)

# The marker every generated link carries. It is what makes the pass a fixed
# point -- a second run sees a link, not a bare word -- and it is what the
# stylesheet hangs the colour on.
CLASS = "glossary-term"

# Regions a term inside is not the term: fenced code, inline code, headings,
# link text, URLs, image alts, and the attribute lists this file writes.
MASKS = (
    re.compile(r"^```.*?^```", re.MULTILINE | re.DOTALL),
    re.compile(r"^~~~.*?^~~~", re.MULTILINE | re.DOTALL),
    re.compile(r"`[^`\n]*`"),
    re.compile(r"^#{1,6} .*$", re.MULTILINE),
    re.compile(r"!?\[[^\]]*\]\([^)]*\)"),
    re.compile(r"\{[^}\n]*\}"),
    re.compile(r"^\s{0,3}(?:>\s*)?(?:!!!|\?\?\?)\s.*$", re.MULTILINE),
    re.compile(r"<[^>\n]+>"),
    # Indented code, markdown's other code form: the executable cookbook pages
    # write their doctests as four-space indented blocks, and a path inside a
    # `>>>` line must stay a path for the page to run.
    re.compile(r"(?:^(?:\t| {4,}).*$\n?)+", re.MULTILINE),
)


def terms(text: str) -> dict[str, str]:
    """`{term: anchor}`, longest first so `phase ladder` wins over `phase`."""
    found = {m.group("term").strip(): m.group("anchor")
             for m in TERM.finditer(text)}
    return dict(sorted(found.items(), key=lambda kv: -len(kv[0])))


def _masked(text: str) -> list[tuple[int, int]]:
    """Spans a term inside must be left alone."""
    spans = []
    for pattern in MASKS:
        spans.extend((m.start(), m.end()) for m in pattern.finditer(text))
    return spans


def _inside(spans: list[tuple[int, int]], at: int, end: int) -> bool:
    return any(start <= at and end <= stop for start, stop in spans)


def link_first(text: str, found: dict[str, str], depth: str) -> str:
    """Link the first bare use of each term. Idempotent by construction."""
    spans = _masked(text)
    for term, anchor in found.items():
        # Already linked anywhere means done, which is what makes the pass a
        # fixed point: after a run the first occurrence is a masked link, and
        # linking the first bare use would link one more occurrence per run.
        if f"glossary.md#{anchor})" in text:
            continue

        # A word boundary is not enough: `\b` treats `-`, `/`, `_` and `.` as
        # boundaries, so `seed` would match inside `project-seed/ci/...`. A term
        # joined to something by one of those is part of a compound or a path,
        # and a path is never the word.
        #
        # The term's own capitalisation is preserved: replacing `Corpus` with
        # `corpus` would edit prose to suit a lookup.
        pattern = re.compile(
            rf"(?<![\w\-/._]){re.escape(term)}(?![\w\-/._])",
            re.IGNORECASE)
        for match in pattern.finditer(text):
            if _inside(spans, match.start(), match.end()):
                continue
            seen = match.group(0)
            link = f"[{seen}]({depth}ref/glossary.md#{anchor}){{ .{CLASS} }}"
            text = text[:match.start()] + link + text[match.end():]
            spans = _masked(text)
            break
    return text


def _depth(page: Path) -> str:
    """How far back `ref/glossary.md` is from this page."""
    steps = len(page.relative_to(DOCS).parts) - 1
    return "../" * steps if steps else ""


def pages() -> list[Path]:
    return [p for p in sorted(DOCS.rglob("*.md"))
            if p not in SKIP and not any(g in p.parents for g in GENERATED)]


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    check_only = "--check" in argv

    if not GLOSSARY.is_file():
        print(f"glossary links: {GLOSSARY} is not here.", file=sys.stderr)
        return 1

    found = terms(GLOSSARY.read_text(encoding="utf-8"))
    if not found:
        print("glossary links: the glossary defines no terms, which is either "
              "a broken page or a changed format.", file=sys.stderr)
        return 1

    changed = []
    for page in pages():
        before = page.read_text(encoding="utf-8")
        after = link_first(before, found, _depth(page))
        if after != before:
            changed.append(page)
            if not check_only:
                page.write_text(after, encoding="utf-8")

    if check_only and changed:
        print("glossary links: these pages have unlinked first uses:")
        for page in changed:
            print(f"  {page}")
        print()
        print("Run `uv run qm glossary-links` and commit the result.")
        return 1

    linked = sum(page.read_text(encoding="utf-8").count(f".{CLASS}")
                 for page in pages())
    print(f"glossary links: {len(found)} term(s), {linked} first use(s) linked "
          f"across {len(pages())} page(s).")
    if changed and not check_only:
        print(f"  rewrote {len(changed)} page(s)")
    print("This does NOT check that the word is used in the glossary's sense -- "
          "`gate` at an airport is not a CI check, and nothing here can tell.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
