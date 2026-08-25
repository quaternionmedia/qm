"""The charter declares its own shape, and `none` is a first-class answer.

**THE HARD PART IS NOT REQUIRING EDGES — IT IS NOT MANUFACTURING THEM.** A graph
made connected by effort is worse than an honest sparse one, because it looks
checked. So the tests that matter here are the two in tension: a stated edge must
be stated from both ends, and an unstated one must cost a reason rather than a
shrug.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import check_principle_edges as edges  # noqa: E402


def charter(*blocks: str) -> str:
    return "# Charter\n\n" + "\n\n".join(blocks) + "\n"


def principle(name: str, declaration: str, title: str = "A thing") -> str:
    return f"## {name} — {title}\n\nSome prose.\n\n↔ Edges: {declaration}\n"


ENOUGH = ("none — nothing else in this charter turns on the answer, and an "
          "invented link would be ornament")


# --- both ends -----------------------------------------------------------------


def test_a_stated_edge_must_be_stated_from_both_ends():
    """THE ONE THIS EXISTS FOR.

    P4 has said it orders P2 since it was written, and P2 says nothing — so a
    reader arriving at P2 never learns it is ordered.

    Mutation: drop the inverse and this fails.
    """
    one_sided = charter(principle("P1", "orders P2"),
                        principle("P2", ENOUGH))
    problems = edges.check(one_sided)

    assert any("does not declare `ordered-by P1` back" in p for p in problems), \
        problems


def test_both_ends_stated_is_clean():
    paired = charter(principle("P1", "orders P2"),
                     principle("P2", "ordered-by P1"))
    assert edges.check(paired) == []


def test_a_symmetric_kind_pairs_with_itself():
    """`shares-teeth` has no direction: sharing is mutual and there is nothing
    to name."""
    shared = charter(principle("P1", "shares-teeth P2"),
                     principle("P2", "shares-teeth P1"))
    assert edges.check(shared) == []


def test_every_kind_has_an_inverse_that_is_itself_a_kind():
    """A closed vocabulary whose inverse table leaves the vocabulary is not
    closed.

    Mutation: add a kind without its inverse and this fails.
    """
    for kind, inverse in edges.INVERSES.items():
        assert inverse in edges.INVERSES, (kind, inverse)
        assert edges.INVERSES[inverse] == kind, (kind, inverse)


def test_a_symmetric_kind_is_its_own_inverse():
    for kind in edges.SYMMETRIC:
        assert edges.INVERSES[kind] == kind


# --- `none` costs a reason ------------------------------------------------------


def test_none_without_a_reason_is_refused():
    """THE OTHER ONE THIS EXISTS FOR.

    If `none` were free it would be the cheapest declaration, and every
    principle would drift to it. If an edge were required, the cheapest
    declaration would be an invented edge. Charging `none` a reason makes the
    honest answer the lazy one.

    Mutation: drop the length bar and this fails.
    """
    shrug = charter(principle("P1", "none"))
    problems = edges.check(shrug)

    assert any("gives no reason worth the name" in p for p in problems), problems


def test_none_with_a_label_is_still_a_shrug():
    labelled = charter(principle("P1", "none — n/a"))
    assert edges.check(labelled) != []


def test_none_with_a_reason_is_a_complete_declaration():
    """Isolation is a signal to check, not a defect. A principle that genuinely
    constrains nothing says so and is done."""
    assert edges.check(charter(principle("P1", ENOUGH))) == []


# --- the vocabulary is closed ---------------------------------------------------


def test_a_kind_outside_the_vocabulary_is_refused():
    """A free string would let a typo become a category — the reason
    `composition.RELATIONS` is closed, and this is a second instance of that
    same earned structure rather than a new one.

    Mutation: accept any word and this fails.
    """
    loose = charter(principle("P1", "relates-to P2"), principle("P2", ENOUGH))
    problems = edges.check(loose)

    assert any("is not one of the declared kinds" in p for p in problems), \
        problems


def test_an_edge_to_a_principle_that_does_not_exist_is_refused():
    dangling = charter(principle("P1", "orders P99"))
    assert any("not a principle" in p for p in edges.check(dangling)), \
        edges.check(dangling)


def test_an_edge_to_itself_is_refused():
    selfish = charter(principle("P1", "orders P1"))
    assert any("edge to itself" in p for p in edges.check(selfish)), \
        edges.check(selfish)


def test_a_principle_that_declares_nothing_is_refused():
    """Silence is the state this whole check exists to end.

    Mutation: treat a missing line as `none` and this fails.
    """
    silent = charter("## P1 — A thing\n\nSome prose, and no declaration.\n")
    assert any("no edges line at all" in p for p in edges.check(silent)), \
        edges.check(silent)


def test_two_declarations_are_refused():
    twice = charter("## P1 — A thing\n\n↔ Edges: none — one\n\n"
                    "↔ Edges: none — two\n")
    assert any("one is the shape" in p for p in edges.check(twice)), \
        edges.check(twice)


# --- the charter itself ----------------------------------------------------------


def test_the_real_charter_is_consistent_with_what_it_declares():
    """Not that the relationships are true — nothing here reads a principle."""
    text = Path("PRINCIPLES.md").read_text(encoding="utf-8")
    assert edges.check(text) == []


def test_the_real_charter_declares_for_every_principle():
    text = Path("PRINCIPLES.md").read_text(encoding="utf-8")
    found = edges.principles(text)
    assert len(found) >= 17

    for name, _title, body in found:
        _edges, reason, complaint = edges.declared(body)
        assert complaint is None, f"{name}: {complaint}"


def test_the_charter_is_allowed_to_be_sparse():
    """The measurement this check was built from: six of seventeen principles
    were isolated. Several still are, deliberately, and that is a passing state
    — a check that forced them to connect would be the ornament P15 refuses.
    """
    text = Path("PRINCIPLES.md").read_text(encoding="utf-8")
    reasoned = [name for name, _t, body in edges.principles(text)
                if not edges.declared(body)[0] and edges.declared(body)[1]]
    assert reasoned, "no principle declares `none`, which would be suspicious"


@pytest.mark.parametrize("value,kind", [
    ("orders P2", "orders"),
    ("rests-on P10, bears P17", "rests-on"),
])
def test_a_declaration_parses_to_its_kinds(value, kind):
    parsed, reason, complaint = edges.declared(f"↔ Edges: {value}\n")
    assert complaint is None
    assert reason is None
    assert parsed[0][0] == kind


def test_main_runs_against_the_charter():
    """`test_every_gate_is_exercised` requires something to execute every
    module with a `main()`, and it is what caught this file being absent."""
    assert edges.main() == 0
