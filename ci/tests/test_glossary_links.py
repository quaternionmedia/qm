"""The first use of a term on a page reaches its definition, and only the first.

A reader meeting `knot` in a record guesses rather than searching, and a corpus
whose words carry precise meanings is where guessing is expensive
(`governance-finds-the-reader`, one layer down).

The pass is a fixed point: running it twice changes nothing, so it can ride the
ordinary command (`show-it-by-running-it`) rather than being a release step
somebody remembers.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import glossary_links as links  # noqa: E402

TERMS = {"knot": "knot", "phase ladder": "phase-ladder", "phase": "phase"}


def linked(text: str) -> str:
    return links.link_first(text, TERMS, "")


# --- the fixed point -------------------------------------------------------------


def test_running_it_twice_changes_nothing():
    """The second pass changes nothing.

    Mutation: link the first *bare* use instead of skipping a term already
    linked anywhere, and this fails — each pass links one more occurrence.
    """
    page = "A knot is a cycle. Another knot appears here. A third knot too.\n"

    once = linked(page)
    twice = linked(once)

    assert once != page, "nothing was linked at all"
    assert twice == once, "the pass is not a fixed point"


def test_only_the_first_use_is_linked():
    """Linking every occurrence is a page of underlines, which is a different
    way of being unreadable."""
    page = "A knot is a cycle. Another knot appears here.\n"
    assert linked(page).count("glossary.md#knot") == 1


def test_a_longer_term_wins_over_a_shorter_one_inside_it():
    """`phase ladder` is not `phase`, and a dictionary ordered by length is
    what keeps them apart.

    Mutation: iterate the terms in insertion order and this fails.
    """
    page = "The phase ladder is how a project reports maturity.\n"
    out = links.link_first(page, dict(sorted(TERMS.items(),
                                             key=lambda kv: -len(kv[0]))), "")
    assert "glossary.md#phase-ladder" in out
    assert "glossary.md#phase)" not in out


# --- what it will not touch ------------------------------------------------------


def test_a_term_inside_inline_code_is_left_alone():
    """`delta` in a command is not the word."""
    page = "Run `qm knot` and see.\n"
    assert linked(page) == page


def test_a_term_inside_a_fenced_block_is_left_alone():
    page = "Before.\n\n```\na knot here\n```\n\nAfter.\n"
    assert "glossary.md" not in linked(page)


def test_a_term_in_a_heading_is_left_alone():
    """A linked heading breaks its own anchor."""
    page = "## A knot in the graph\n\nProse.\n"
    assert linked(page) == page


def test_a_term_inside_an_existing_link_is_left_alone():
    """Nesting a link inside a link produces markup no renderer agrees
    about."""
    page = "See [the knot record](../records/knots.md) for more.\n"
    assert linked(page) == page


def test_a_term_in_a_url_is_left_alone():
    page = "See [details](https://example.test/knot/page) for more.\n"
    assert linked(page) == page


def test_the_glossary_itself_is_not_rewritten():
    """It would link to its own definitions."""
    assert links.GLOSSARY in links.SKIP or links.GLOSSARY not in links.pages()


# --- the shape of what it writes --------------------------------------------------


def test_the_link_carries_the_class_the_stylesheet_hangs_on():
    page = "A knot is a cycle.\n"
    out = linked(page)
    assert f"{{ .{links.CLASS} }}" in out


def test_the_prose_keeps_its_own_capitalisation():
    """Replacing `Knot` with `knot` would edit prose to suit a lookup.

    Mutation: use the glossary's spelling for the link text and this fails.
    """
    page = "Knot theory is not the subject here.\n"
    assert "[Knot]" in linked(page)


def test_the_path_climbs_out_of_a_nested_page():
    assert links._depth(Path("docs/index.md")) == ""
    assert links._depth(Path("docs/about/overview.md")) == "../"
    assert links._depth(Path("docs/a/b/c.md")) == "../../"


# --- the real pages ---------------------------------------------------------------


def test_the_real_glossary_parses_into_terms():
    found = links.terms(links.GLOSSARY.read_text(encoding="utf-8"))
    assert len(found) >= 17
    for term, anchor in found.items():
        assert term and anchor
        assert anchor.islower()


def test_the_terms_are_ordered_longest_first():
    found = list(links.terms(links.GLOSSARY.read_text(encoding="utf-8")))
    lengths = [len(t) for t in found]
    assert lengths == sorted(lengths, reverse=True)


def test_the_committed_pages_are_current():
    """`show-it-by-running-it`: regeneration rides the ordinary command, so drift arrives as an
    uncommitted diff nobody can miss."""
    assert links.main(["--check"]) == 0


def test_main_runs():
    """`test_every_gate_is_exercised` requires something to execute every
    module with a `main()`."""
    assert links.main(["--check"]) == 0


# --- markdown's other code form, and compounds ----------------------------------


def test_a_term_inside_an_indented_code_block_is_left_alone():
    """The executable cookbook pages write their doctests as four-space
    indented blocks, and a path inside a `>>>` line must stay a path for the
    page to run.

    Mutation: drop the indented-block mask and this fails.
    """
    page = (
        "Prose about a knot.\n\n"
        "    >>> import subprocess\n"
        "    >>> subprocess.run(['x', 'project-seed/ci/run.py'])\n\n"
        "More prose.\n"
    )
    out = links.link_first(page, {"seed": "seed"}, "")
    assert "project-seed/ci/run.py" in out, out


def test_a_term_joined_by_a_hyphen_or_slash_is_part_of_a_compound():
    """`\b` treats `-`, `/`, `_` and `.` as word boundaries, so `seed`
    would match inside `project-seed/ci/...` and `record` inside
    `record_review.py`. A path is never the word.

    Mutation: go back to `\b...\b` and this fails.
    """
    for compound in ("project-seed", "seed/ci", "a_seed", "seed.py",
                     "seed-thing"):
        page = f"Prose mentioning {compound} in passing.\n"
        assert links.link_first(page, {"seed": "seed"}, "") == page, compound


def test_the_word_on_its_own_is_still_linked():
    """The control. Excluding compounds is only right if the bare word still
    works -- otherwise the fix would have deleted the feature."""
    page = "The seed is what a fork adopts.\n"
    assert "glossary.md#seed" in links.link_first(page, {"seed": "seed"}, "")


def test_a_page_another_generator_writes_is_left_alone():
    """docs/families/ and docs/repos.md are written by `ci/cookbook.py --site`;
    linking terms there would make each generator report the other's output as
    drift.

    Mutation: empty `GENERATED`, or drop docs/repos.md from it, and this fails.
    """
    found = links.pages()
    assert not any(Path("docs/families") in page.parents for page in found)
    assert Path("docs/repos.md") not in found
