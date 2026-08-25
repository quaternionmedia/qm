"""Link the first use of a glossary term on each page to its definition.

**A GLOSSARY NOBODY ARRIVES AT IS A PAGE, NOT A GLOSSARY.** P11 says governance
finds the reader rather than the reverse, and the same argument applies one layer
down: a reader meeting `knot` in a record does not stop, open the reference
section, and search. They guess, and a corpus whose words carry precise meanings
is exactly the kind where guessing is expensive.

**FIRST USE PER PAGE, AND NOTHING ELSE.** Linking every occurrence produces a
page of underlines, which is a different way of being unreadable. The first is
where a reader is deciding whether they know the word; the fourth is noise.

**IT IS A FIXED POINT, AND THAT IS THE PROPERTY WORTH HAVING.** Running this
twice changes nothing, because an already-linked occurrence is not a bare one.
That is what makes it safe to ride the ordinary command (P12) rather than being a
release step somebody remembers: drift arrives as an uncommitted diff nobody can
miss, and a second run is never a second edit.

WHAT IT WILL NOT TOUCH, AND WHY EACH IS EXCLUDED. Code spans and fenced blocks --
`delta` inside a command is not the word. Headings -- a linked heading breaks its
own anchor. Existing link text and URLs -- nesting a link inside a link produces
markup no renderer agrees about. The glossary pages themselves, which would link
to their own definitions.

WHAT THIS CANNOT DO. Know whether the word is being used in the glossary's sense.
`gate` in a record means a CI check; `gate` in a sentence about an airport does
not, and this cannot tell. The mitigation is that the corpus's terms are
technical and the first use per page is a low enough dose that a wrong link is
cheap -- but it is a real limit and the check prints it.
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
        # **ALREADY LINKED ANYWHERE MEANS DONE, AND THIS IS WHAT MAKES IT
        # A FIXED POINT.** The first version linked the first *bare* use,
        # which is not the first use: after a run the first occurrence is a
        # link and therefore masked, so the second becomes the new first
        # bare one and the next run links that too. It rewrote seventeen
        # pages on its second pass and would have gone on linking one more
        # occurrence per run forever.
        #
        # The docstring claimed idempotence before the code had it, and
        # running it twice is what found that -- P16 applied to a
        # generator.
        if f"glossary.md#{anchor})" in text:
            continue

        # Word boundaries, and the term's own capitalisation is preserved --
        # replacing `Corpus` with `corpus` would edit prose to suit a lookup.
        pattern = re.compile(rf"\b{re.escape(term)}\b", re.IGNORECASE)
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
    return [p for p in sorted(DOCS.rglob("*.md")) if p not in SKIP]


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
