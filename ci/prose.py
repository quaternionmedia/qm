#!/usr/bin/env python3
"""The first thing a stranger reads, from every entry point, side by side.

WHAT THIS IS FOR. `handbook/style-guide.md` asks that the opening of anything a
newcomer meets be a real sentence in words they already have. That rule was
written after this corpus's own landing page was found opening with a colon and
three abstractions and no verb -- accurate, and unreadable to anybody who did
not already understand it.

Nothing can check whether prose is clear. What a program can do is put the
opening lines of every entry point on one screen, so a person reads them
together rather than one at a time months apart, and flag the few patterns that
are mechanically visible and that the style guide names.

WHAT A FLAG IS AND IS NOT. A flag is a place to look. Every one of them is
legitimate somewhere: a sentence can be long and clear, an opening can name a
house word because the word is the subject. The flags are ordered by how often
they have actually indicated a problem here, and none of them fails anything.
This tool exits zero unless it cannot read a file.

WHAT IT CANNOT SEE. Whether the sentence is true. Whether the reader needed a
different fact first. Whether the words are the reader's words -- it holds a
list of this corpus's own house vocabulary and knows nothing about anybody
else's. And prose after the opening, which is most of the page: this reads the
first sentence and the first paragraph, because that is where a reader decides
whether to continue.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

# Words this corpus uses in a narrow sense. A reader who has not been told what
# they mean cannot use a sentence that leans on them. The glossary is the
# authority; this is the subset that has appeared in an opening line.
HOUSE_WORDS = (
    "corpus", "record", "ratify", "ratification", "gate", "delta", "phase",
    "propagate", "propagation", "seed", "adopt by reference", "binds",
    "invariant", "namespace", "restatement", "precedence",
)

# Files that are somebody's first contact, in the order they usually arrive.
ENTRY_POINTS = (
    "README.md",
    "docs/index.md",
    "docs/usage/getting-started.md",
    "walkthrough/01-*.md",
)

SENTENCE_END = re.compile(r"(?<=[.!?])\s")


@dataclass(frozen=True)
class Flag:
    """A place to look, never a verdict."""

    label: str
    detail: str


@dataclass
class Opening:
    path: Path
    heading: str
    first_sentence: str
    first_paragraph: str
    flags: list[Flag]


def strip_markup(text: str) -> str:
    """Prose as a reader hears it, not as markdown spells it."""
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = re.sub(r"\*\*([^*]*)\*\*", r"\1", text)
    text = re.sub(r"\*([^*]*)\*", r"\1", text)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    return text.strip()


def prose_lines(text: str) -> list[str]:
    """The lines of a document that are prose, in order.

    Everything that only looks like prose is removed first: front matter,
    fenced code, HTML blocks, badge rows, headings, quotes, tables, admonition
    markers and list items. This is a strip-then-scan rather than a
    skip-as-you-go because the latter was wrong three times in a row -- it
    skipped a fence's opening line and then quoted the code inside it, quoted a
    row of badges as a first sentence, and treated bold text at line start as a
    bullet. Each fix revealed the next.
    """
    lines = text.splitlines()
    if lines and lines[0].strip() == "---":
        closing = next((i for i, line in enumerate(lines[1:], 1)
                        if line.strip() == "---"), 0)
        lines = lines[closing + 1:]

    kept: list[str] = []
    in_fence = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            kept.append("")
            continue
        if in_fence:
            continue
        if not stripped:
            kept.append("")
            continue
        if stripped.startswith(("#", "|", "!", "<", "=== ", ":::", "    ")):
            kept.append("")
            continue
        # A blockquote is read. It is often the tagline directly under the
        # title, which makes it the first thing a stranger meets even though
        # markdown treats it as an aside.
        if stripped.startswith(">"):
            kept.append(stripped.lstrip("> ").strip())
            continue
        if re.match(r"^([-*+]|\d+\.)\s", stripped):
            kept.append("")
            continue
        if re.fullmatch(r"(\s*\[!\[[^\]]*\]\([^)]*\)\]\([^)]*\))+\s*", stripped):
            kept.append("")
            continue
        kept.append(stripped)
    return kept


def opening_of(path: Path) -> tuple[str, str, str]:
    """The heading, the first sentence of prose, and the paragraph it sits in.

    A page whose first paragraph is a heading, a badge row or a code block has
    not started talking yet, and that is the finding rather than an error.
    """
    text = path.read_text(encoding="utf-8")
    heading = next((line.lstrip("# ").strip() for line in text.splitlines()
                    if line.startswith("# ")), "")

    paragraph: list[str] = []
    for line in prose_lines(text):
        if not line:
            if paragraph:
                break
            continue
        paragraph.append(line)

    body = strip_markup(" ".join(paragraph))
    first = SENTENCE_END.split(body)[0] if body else ""
    return heading, first.strip(), body


def flags_for(sentence: str, paragraph: str) -> list[Flag]:
    """Patterns the style guide names, in the order they have actually bitten."""
    found: list[Flag] = []
    if not sentence:
        return [Flag("no prose", "The page opens with a heading, a list or a "
                                "table. A reader has not been told anything yet.")]

    # The failure that produced the rule: a colon and a list of nouns, no verb.
    if ":" in sentence and sentence.index(":") < len(sentence) * 0.4:
        found.append(Flag(
            "colon early",
            "An opening that names the subject and then lists what it contains "
            "is usually not a sentence. Read it aloud and see whether it has a "
            "verb."))

    words = re.findall(r"[A-Za-z']+", sentence)
    if len(words) > 32:
        found.append(Flag(
            "long first sentence",
            f"{len(words)} words. A first sentence is the one place length "
            "costs most, because the reader has no reason yet to stay with it."))

    punctuation = sum(sentence.count(mark) for mark in ("—", " - ", ";", "(", ":"))
    if punctuation >= 2:
        found.append(Flag(
            "stacked punctuation",
            "Dashes, semicolons and parentheticals in one opening usually mean "
            "two sentences are hiding in it."))

    lowered = sentence.lower()
    house = sorted({word for word in HOUSE_WORDS if word in lowered})
    if house:
        found.append(Flag(
            "house vocabulary",
            "Uses " + ", ".join(house) + " before the reader has been given "
            "them. The glossary defines these; an opening line cannot rely on "
            "the glossary having been read."))

    if not re.search(r"\byou\b|\byour\b|\bwe\b|\?", paragraph, re.I):
        found.append(Flag(
            "no reader",
            "The opening paragraph never addresses anybody or asks anything. "
            "This is weak evidence on its own and worth reading twice."))
    return found


def entry_points(root: Path, patterns: tuple[str, ...] = ENTRY_POINTS) -> list[Path]:
    found: list[Path] = []
    for pattern in patterns:
        if "*" in pattern:
            found.extend(sorted(root.glob(pattern)))
        elif (root / pattern).is_file():
            found.append(root / pattern)
    return found


def read(root: Path, patterns: tuple[str, ...] = ENTRY_POINTS) -> list[Opening]:
    openings = []
    for path in entry_points(root, patterns):
        heading, sentence, paragraph = opening_of(path)
        openings.append(Opening(
            path=path.relative_to(root) if path.is_absolute() else path,
            heading=heading,
            first_sentence=sentence,
            first_paragraph=paragraph,
            flags=flags_for(sentence, paragraph),
        ))
    return openings


def render(openings: list[Opening]) -> str:
    if not openings:
        return ("No entry points found. This repository has no README, no docs\n"
                "landing page and no walkthrough, which is itself the finding.")

    lines = [
        "The first thing a stranger reads, from each entry point.",
        "",
        "Read the sentences below as a set. Nothing here fails: a flag is a",
        "place to look, and every pattern flagged is legitimate somewhere.",
        "",
    ]
    for opening in openings:
        lines.append(f"--- {opening.path}")
        lines.append(f"    heading:  {opening.heading or '(none)'}")
        lines.append(f"    opens:    {opening.first_sentence or '(no prose)'}")
        for flag in opening.flags:
            lines.append(f"      [{flag.label}] {flag.detail}")
        if not opening.flags:
            lines.append("      nothing flagged -- which is not the same as clear")
        lines.append("")

    lines.append("What this cannot see: whether the sentence is true, whether the")
    lines.append("reader needed a different fact first, and everything after the")
    lines.append("opening. Read the pages.")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Show the opening of every entry point, side by side.")
    parser.add_argument("--root", type=Path, default=Path("."),
                        help="repository to read (default: the working directory)")
    parser.add_argument("--path", action="append", dest="paths",
                        help="an entry point to read instead of the defaults; "
                             "repeatable, and globs are allowed")
    args = parser.parse_args(argv)

    patterns = tuple(args.paths) if args.paths else ENTRY_POINTS
    print(render(read(args.root, patterns)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
