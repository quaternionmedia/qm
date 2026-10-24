"""A family is a claim, and the set of families is read from the record.

The tool holds no list of its own: a second copy of the families would be a
scope nothing checks.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import families  # noqa: E402

TABLE = """# A record

### §3 — The performing estate is three families

| family | drives | named public members |
|---|---|---|
| `show-control` | **the room** — cues and lighting | a; b |
| `instruments` | **the sound** — looping | c; d |
"""


def record(tmp_path: Path, text: str = TABLE) -> Path:
    path = tmp_path / "a-record.md"
    path.write_text(text, encoding="utf-8")
    return path


def test_the_families_come_from_the_record(tmp_path: Path):
    found = families.declared(record(tmp_path))
    assert set(found) == {"show-control", "instruments"}
    assert "the room" in found["show-control"]


def test_a_claim_naming_an_undeclared_family_is_refused(tmp_path: Path):
    """Mutation: drop the `family not in families` branch and this fails."""
    declared = families.declared(record(tmp_path))
    problems = families.problems([{"name": "x", "family": "not-a-family"}], declared)
    assert problems, "an undeclared family passed"
    assert "not-a-family" in problems[0]


def test_a_claim_naming_a_declared_family_passes(tmp_path: Path):
    declared = families.declared(record(tmp_path))
    assert families.problems([{"name": "x", "family": "instruments"}], declared) == []


def test_an_entry_with_no_family_is_unstated_not_a_problem(tmp_path: Path):
    """Silence means nobody answered, and a tool that read it as an answer
    would grow the roster claims nobody made."""
    declared = families.declared(record(tmp_path))
    assert families.problems([{"name": "x"}], declared) == []


def test_a_record_declaring_no_families_is_refused_rather_than_vacuously_clean(tmp_path: Path):
    """With no families declared, every roster claim would be compared
    against nothing and pass, so an empty declaration is refused.

    Mutation: return `[]` instead of a problem when `families` is empty, and
    this fails.
    """
    empty = families.declared(record(tmp_path, "# A record\n\nNo table here.\n"))
    assert empty == {}
    problems = families.problems([{"name": "x", "family": "anything"}], empty)
    assert problems, "an empty declared set reported clean"
    assert "nothing was checked" in problems[0]


def test_renaming_a_family_in_the_record_breaks_the_claim_visibly(tmp_path: Path):
    """The property the whole design is for: a rename dangles, it does not reaim."""
    renamed = record(tmp_path, TABLE.replace("`instruments`", "`sound-sources`"))
    declared = families.declared(renamed)
    assert families.problems([{"name": "x", "family": "instruments"}], declared)


def test_a_private_repository_is_written_by_reference_never_by_name():
    """`roster.load` merges the uncommitted private companion, so on a
    machine that has it a private entry arrives carrying its real name. A
    writer using `roster.label`, which prefers `name`, would serialise that
    into a committed file.

    Mutation: use `roster.label` in `document` instead of `publishable` and
    this fails.
    """
    entries = [{"ref": "private-99", "name": "the-real-name", "family": None}]
    out = families.document(entries, {"a-family": "something"})
    assert out["unstated"] == ["private-99"]
    assert "the-real-name" not in json.dumps(out)


def test_a_public_repository_is_written_by_name():
    entries = [{"name": "public-thing", "family": "a-family"}]
    out = families.document(entries, {"a-family": "something"})
    assert out["families"][0]["members"] == ["public-thing"]


def test_a_table_outside_section_three_declares_nothing(tmp_path):
    """A backticked first cell is a proxy for a family row; scanned over the
    whole record it would match any table anywhere, so a table outside §3
    declares nothing.

    Mutation: scan the whole text instead of the section and this fails.
    """
    body = "\n".join([
        "# R", "", "### §3 — families", "",
        "| family | drives | m |", "|---|---|---|",
        "| `real` | **x** | a |", "",
        "### §4 — other", "",
        "| a | b |", "|---|---|",
        "| `impostor` | y |", "",
    ])
    t = tmp_path / "r.md"
    t.write_text(body, encoding="utf-8")
    found = families.declared(t)
    assert "real" in found
    assert "impostor" not in found


def test_the_committed_record_declares_exactly_the_known_set():
    """The drift guard the adversarial pass showed was missing: nothing pinned
    the declared set, so a stray row would have shifted the vocabulary with
    no test noticing."""
    assert sorted(families.declared()) == [
        "civic", "core", "games", "infra", "instruments", "irl", "performer-display",
        "performing", "show-control"]


NESTED = """# A record

### §3 — The families, and which sits within which

| family | drives | within | named public members |
|---|---|---|---|
| `performing` | **a show** | — | v |
| `show-control` | **the room** | `performing` | a; b |
| `instruments` | **the sound** | `performing` | c; d |
| `irl` | **matter** | — | e |
"""


def test_within_comes_from_the_column_the_header_names(tmp_path: Path):
    parents = families.within(record(tmp_path, NESTED))
    assert parents == {"performing": None, "show-control": "performing",
                       "instruments": "performing", "irl": None}


def test_a_table_with_no_within_column_nests_nothing(tmp_path: Path):
    """The members column holds names too; read without the header, its first
    name would be taken for the outer family."""
    assert set(families.within(record(tmp_path)).values()) == {None}


def test_a_repository_may_claim_two_families(tmp_path: Path):
    path = record(tmp_path, NESTED)
    found = families.problems([{"name": "pedal", "family": ["irl", "instruments"]}],
                              families.declared(path), families.within(path))
    assert found == []


def test_one_undeclared_name_in_a_list_is_refused(tmp_path: Path):
    path = record(tmp_path, NESTED)
    found = families.problems([{"name": "x", "family": ["irl", "nowhere"]}],
                              families.declared(path), families.within(path))
    assert len(found) == 1 and "nowhere" in found[0]


def test_a_family_named_twice_is_refused(tmp_path: Path):
    path = record(tmp_path, NESTED)
    found = families.problems([{"name": "x", "family": ["irl", "irl"]}],
                              families.declared(path), families.within(path))
    assert found and "more than once" in found[0]


def test_a_family_beside_the_one_it_sits_within_is_refused(tmp_path: Path):
    """The inner claim already places the repository in the outer family.

    Mutation: drop the ancestor check in `problems` and this fails.
    """
    path = record(tmp_path, NESTED)
    found = families.problems([{"name": "x", "family": ["instruments", "performing"]}],
                              families.declared(path), families.within(path))
    assert found and "sits within performing" in found[0]


def test_a_within_naming_no_declared_family_is_refused(tmp_path: Path):
    path = record(tmp_path, NESTED.replace("| `irl` | **matter** | — |",
                                           "| `irl` | **matter** | `nowhere` |"))
    found = families.problems([], families.declared(path), families.within(path))
    assert found and "nowhere" in found[0]


def test_a_family_within_itself_is_refused(tmp_path: Path):
    path = record(tmp_path, NESTED.replace("| `performing` | **a show** | — |",
                                           "| `performing` | **a show** | `instruments` |"))
    found = families.problems([], families.declared(path), families.within(path))
    assert any("within itself" in p for p in found)


def test_everyone_in_an_inner_family_is_in_the_outer_one(tmp_path: Path):
    path = record(tmp_path, NESTED)
    entries = [{"name": "editor", "family": "performing"},
               {"name": "synth", "family": "instruments"},
               {"name": "pedal", "family": ["irl", "instruments"]}]
    out = families.document(entries, families.declared(path), families.within(path))
    by_name = {f["name"]: f for f in out["families"]}
    assert by_name["performing"]["members"] == ["editor"]
    assert by_name["performing"]["all_members"] == ["editor", "synth", "pedal"]
    assert by_name["performing"]["subfamilies"] == ["instruments", "show-control"]
    assert by_name["instruments"]["within"] == "performing"
    assert "pedal" in by_name["irl"]["members"]
    assert out["unstated"] == []

