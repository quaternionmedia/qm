"""A family is a claim, and the set of families is read from the record.

The check that matters here is not that a claim resolves. It is that the tool
holds no list of its own: this corpus has found four generators in one week
whose hardcoded scope made them report on their own scaffolding, and a second
copy of the families would have been the fifth.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import families  # noqa: E402

TABLE = """# A record

## §3 — The performing estate is three families

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
    """**THE EMPTY-SET CASE, WHICH IS HOW A CHECK STOPS CHECKING.**

    With no families declared, every roster claim would be compared against
    nothing and pass. That is the exact shape of the index check this corpus
    found inert after its whole life, and of three scope lists beside it.

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
    """**THE LEAK THE FIRST WRITE PRODUCED.**

    `roster.load` merges the uncommitted private companion, so on a machine
    that has it a private entry arrives carrying its real name. A writer using
    `roster.label` -- which prefers `name` -- serialises that into a committed
    file. Three names reached `families.json` this way and
    `uv run qm private-names` is what caught them.

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

