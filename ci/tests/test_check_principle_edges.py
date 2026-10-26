"""The charter declares its own shape, and `none` is a first-class answer.

A stated edge must be stated from both ends, and an unstated one costs a reason.
An edge is never required, so the charter is never made connected by effort.
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
    """A one-sided edge is refused: delta says it orders beta and beta says
    nothing, so a reader arriving at beta never learns it is ordered.

    Mutation: drop the inverse and this fails.
    """
    one_sided = charter(principle("alpha", "orders beta"),
                        principle("beta", ENOUGH))
    problems = edges.check(one_sided)

    assert any("does not declare `ordered-by alpha` back" in p for p in problems), \
        problems


def test_both_ends_stated_is_clean():
    paired = charter(principle("alpha", "orders beta"),
                     principle("beta", "ordered-by alpha"))
    assert edges.check(paired) == []


def test_a_symmetric_kind_pairs_with_itself():
    """`shares-teeth` has no direction: sharing is mutual and there is nothing
    to name."""
    shared = charter(principle("alpha", "shares-teeth beta"),
                     principle("beta", "shares-teeth alpha"))
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
    """`none` costs a reason. If it were free, every principle would drift to
    it; if an edge were required, the cheapest declaration would be an
    invented one. Charging `none` a reason makes the honest answer the lazy
    one.

    Mutation: drop the length bar and this fails.
    """
    shrug = charter(principle("alpha", "none"))
    problems = edges.check(shrug)

    assert any("gives no reason worth the name" in p for p in problems), problems


def test_none_with_a_label_is_still_a_shrug():
    labelled = charter(principle("alpha", "none — n/a"))
    assert edges.check(labelled) != []


def test_none_with_a_reason_is_a_complete_declaration():
    """Isolation is a signal to check, not a defect. A principle that genuinely
    constrains nothing says so and is done."""
    assert edges.check(charter(principle("alpha", ENOUGH))) == []


# --- the vocabulary is closed ---------------------------------------------------


def test_a_kind_outside_the_vocabulary_is_refused():
    """A free string would let a typo become a category — the reason
    `composition.RELATIONS` is closed, and this is a second instance of that
    same earned structure rather than a new one.

    Mutation: accept any word and this fails.
    """
    loose = charter(principle("alpha", "relates-to beta"), principle("beta", ENOUGH))
    problems = edges.check(loose)

    assert any("is not one of the declared kinds" in p for p in problems), \
        problems


def test_an_edge_to_a_principle_that_does_not_exist_is_refused():
    dangling = charter(principle("alpha", "orders no-such-principle"))
    assert any("not a principle" in p for p in edges.check(dangling)), \
        edges.check(dangling)


def test_an_edge_to_itself_is_refused():
    selfish = charter(principle("alpha", "orders alpha"))
    assert any("edge to itself" in p for p in edges.check(selfish)), \
        edges.check(selfish)


def test_a_principle_that_declares_nothing_is_refused():
    """A principle with no declaration at all is refused.

    Mutation: treat a missing line as `none` and this fails.
    """
    silent = charter("## alpha — A thing\n\nSome prose, and no declaration.\n")
    assert any("no edges line at all" in p for p in edges.check(silent)), \
        edges.check(silent)


def test_two_declarations_are_refused():
    twice = charter("## alpha — A thing\n\n↔ Edges: none — one\n\n"
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
    """Isolated principles are a passing state when they declare `none`: a
    check that forced them to connect would manufacture edges.
    """
    text = Path("PRINCIPLES.md").read_text(encoding="utf-8")
    reasoned = [name for name, _t, body in edges.principles(text)
                if not edges.declared(body)[0] and edges.declared(body)[1]]
    assert reasoned, "no principle declares `none`, which would be suspicious"


@pytest.mark.parametrize("value,kind", [
    ("orders beta", "orders"),
    ("rests-on kappa, bears sigma", "rests-on"),
])
def test_a_declaration_parses_to_its_kinds(value, kind):
    parsed, reason, complaint = edges.declared(f"↔ Edges: {value}\n")
    assert complaint is None
    assert reason is None
    assert parsed[0][0] == kind


def test_main_runs_against_the_charter():
    """`test_every_gate_is_exercised` requires something to execute every
    module with a `main()`."""
    assert edges.main() == 0


# --- a principle is addressed by its name, never by its position --------------


# Built rather than written, so this file carries no ordinal reference of its
# own -- the guard under test scans `ci/`, and would otherwise flag the very
# fixtures that prove it works.
ORDINAL_FORM = "P" + "16"


def write_record(root: Path, body: str) -> None:
    (root / "records").mkdir(parents=True, exist_ok=True)
    (root / "records" / "DRAFT-x.md").write_text(body, encoding="utf-8")


def test_an_ordinal_principle_reference_in_a_binding_document_is_refused(tmp_path: Path):
    """An ordinal addresses a position: insert a principle above it and every
    reference below resolves, silently and well-formed, to the wrong
    principle.

    Mutation: drop the `ordinal_references` call from `main` and this fails.
    """
    write_record(tmp_path, 'This rests on ' + ORDINAL_FORM + '\n')
    problems = edges.ordinal_references(tmp_path)
    assert any("addresses a principle as" in p for p in problems), problems


def test_the_root_template_and_charter_are_scanned(tmp_path: Path):
    """The record template is what every new record copies its rows from, and
    the charter is what every row names; an ordinal in either is copied or
    cited onward.

    Mutation: drop `"TEMPLATE.md"` from `BINDING` and this fails on the
    template; drop `"PRINCIPLES.md"` and it fails on the charter.
    """
    for name in ("TEMPLATE.md", "PRINCIPLES.md"):
        (tmp_path / name).write_text("e.g. " + ORDINAL_FORM + "\n", encoding="utf-8")
        problems = edges.ordinal_references(tmp_path)
        assert any(p.startswith(name + ":") for p in problems), (name, problems)
        (tmp_path / name).unlink()


def test_an_annotated_ordinal_is_allowed(tmp_path: Path):
    """A document naming the form in order to forbid it is not breaking it."""
    write_record(tmp_path, 'Never write ' + ORDINAL_FORM + '  principle-name: allow "names the form in order to refuse it"\n')
    assert edges.ordinal_references(tmp_path) == []


def test_an_annotation_with_no_reason_is_the_check_turned_off(tmp_path: Path):
    write_record(tmp_path, 'Never write ' + ORDINAL_FORM + '  principle-name: allow ""\n')
    problems = edges.ordinal_references(tmp_path)
    assert any("empty one is the check turned off" in p for p in problems), problems


def test_a_perspective_is_left_as_its_author_wrote_it(tmp_path: Path):
    """A retrospective is dated, attributed opinion, and editing one falsifies it."""
    (tmp_path / "perspectives").mkdir(parents=True)
    (tmp_path / "perspectives" / "2026-01-01-a.md").write_text(
        'We leaned on ' + ORDINAL_FORM + '\n', encoding="utf-8"
    )
    assert edges.ordinal_references(tmp_path) == []


def test_a_file_scope_annotation_covers_a_colliding_vocabulary(tmp_path: Path):
    """The letter-and-number form is not reserved to the charter: a plan
    that numbers its own work packages the same way is annotated once, at
    file scope, rather than line by line.

    Mutation: delete the file-scope branch from `ordinal_references` and this
    fails.
    """
    (tmp_path / "plans").mkdir(parents=True)
    (tmp_path / "plans" / "a-plan.md").write_text(
        '# A plan\n\n<!-- principle-name: allow "its own work packages, not charter principles" -->\n\n### ' + ORDINAL_FORM + ' -- do the thing\nBlocks on ' + ORDINAL_FORM + '.\n',
        encoding="utf-8",
    )
    assert edges.ordinal_references(tmp_path) == []


def test_a_file_scope_annotation_with_no_reason_does_not_cover(tmp_path: Path):
    (tmp_path / "plans").mkdir(parents=True)
    (tmp_path / "plans" / "a-plan.md").write_text(
        '# A plan\n\n<!-- principle-name: allow "" -->\n\nRests on ' + ORDINAL_FORM + '.\n',
        encoding="utf-8",
    )
    assert edges.ordinal_references(tmp_path) != []
