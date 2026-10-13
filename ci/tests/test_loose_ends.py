"""The loose-ends document: one join of three committed sources, and a claim layer it reads and never writes.

WHAT IS TESTED IS THE CONTRACT. `judge()` is the whole of it -- `build()` and
the vector runner share it -- so the committed vectors are run here, the way
`test_addresses.py` runs the address vectors: a case that passes here is a
statement about the document a consumer receives. Then each thing the module's
docstring promises is held to: `open` has no spelling, an unrecognised
disposition leaves an item open, the register is read and never written, and
an unreadable source is recorded rather than dropped.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

CI_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(CI_DIR))

from loose_ends import (  # noqa: E402
    CLAIMS,
    DISPOSITIONS,
    SOURCES,
    VECTORS,
    build,
    judge,
    main,
    read_claims,
    render,
    run_vectors,
)

ROOT = CI_DIR.parent


# --- the conformance vectors -------------------------------------------------


def test_every_committed_vector_holds():
    assert run_vectors(ROOT) == []


def test_the_vectors_are_not_vacuous():
    cases = json.loads((ROOT / VECTORS).read_text(encoding="utf-8"))["cases"]
    assert len(cases) >= 6
    assert all(case.get("expect") for case in cases), "a case with nothing expected passes on anything"


def test_a_missing_vector_file_is_a_finding_and_not_a_pass(tmp_path):
    problems = run_vectors(tmp_path)
    assert problems and "nothing was checked" in problems[0]


def test_an_empty_vector_file_is_refused(tmp_path):
    where = tmp_path / VECTORS
    where.parent.mkdir(parents=True)
    where.write_text(json.dumps({"cases": []}), encoding="utf-8")
    assert run_vectors(tmp_path) and "vacuous" in run_vectors(tmp_path)[0]


# --- judge: the two dispositions, and open as the absence of both -------------


ITEM = {"kind": "stalled-thread", "address": "quaternionmedia/qm/pr/1"}
KEY = "stalled-thread:quaternionmedia/qm/pr/1"


def test_open_is_the_absence_of_a_claim():
    got = judge(ITEM, {})
    assert got["open"] and not got["has_claim"] and got["disposition"] is None


@pytest.mark.parametrize("disposition", DISPOSITIONS)
def test_a_recognised_disposition_closes_the_item(disposition):
    got = judge(ITEM, {KEY: {"disposition": disposition}})
    assert not got["open"] and got["has_claim"] and got["disposition"] == disposition


def test_an_unrecognised_disposition_leaves_the_item_open():
    # A misspelling that quietly closed a finding is the failure a register of
    # decisions can least afford.
    got = judge(ITEM, {KEY: {"disposition": "carreid"}})
    assert got["open"] and not got["has_claim"] and got["disposition"] is None


def test_a_claim_for_a_different_item_does_not_close_this_one():
    got = judge(ITEM, {"over-slot:quaternionmedia/qm": {"disposition": "carried"}})
    assert got["open"]


def test_the_item_addresses_its_subject_and_the_grammar_resolves_it():
    assert judge(ITEM, {})["address_parses"] is True
    assert judge({"kind": "x", "address": "not an address"}, {})["address_parses"] is False


# --- the register: read, never written ----------------------------------------


def test_the_committed_register_parses_and_every_disposition_is_recognised():
    claims = read_claims(ROOT)
    assert isinstance(claims, dict)
    for key, claim in claims.items():
        assert claim.get("disposition") in DISPOSITIONS, f"{key}: {claim}"


def test_an_absent_register_is_no_claims(tmp_path):
    assert read_claims(tmp_path) == {}


def test_an_unreadable_register_is_reported_not_dropped(tmp_path):
    (tmp_path / CLAIMS).parent.mkdir(parents=True, exist_ok=True)
    (tmp_path / CLAIMS).write_bytes(b"\xff\xfe\x00 not text")
    claims = read_claims(tmp_path)
    assert isinstance(claims, dict) and "unknown" in json.dumps(claims).lower()


def test_building_the_document_writes_nothing_back(tmp_path, monkeypatch):
    # Copy the real sources into a scratch root, build, and the register is
    # byte-for-byte what it was.
    for rel in (*SOURCES.values(), CLAIMS, VECTORS):
        src = ROOT / rel
        if src.exists():
            dst = tmp_path / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(src.read_bytes())
    before = (tmp_path / CLAIMS).read_bytes() if (tmp_path / CLAIMS).exists() else None
    document = build(tmp_path)
    after = (tmp_path / CLAIMS).read_bytes() if (tmp_path / CLAIMS).exists() else None
    assert before == after
    assert document["totals"]["loose_ends"] == len(document["loose_ends"])


def test_an_unreadable_source_is_recorded_as_unknown(tmp_path):
    document = build(tmp_path)          # no sources at all
    assert document["totals"]["sources_unreadable"] == len(SOURCES)
    assert document["totals"]["loose_ends"] == 0


# --- main: the four entry points --------------------------------------------


def test_vectors_flag_runs_the_committed_cases(monkeypatch, capsys):
    monkeypatch.chdir(ROOT)
    assert main(["--vectors"]) == 0
    assert "every case conforms" in capsys.readouterr().out


def test_vectors_flag_fails_when_a_case_disagrees(tmp_path, monkeypatch, capsys):
    where = tmp_path / VECTORS
    where.parent.mkdir(parents=True)
    where.write_text(json.dumps({"cases": [{
        "name": "wrong on purpose",
        "given": {"item": ITEM, "claims": {}},
        "expect": {"open": False},
    }]}), encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    assert main(["--vectors"]) == 1
    assert "wrong on purpose" in capsys.readouterr().err


def test_check_passes_against_a_document_it_just_wrote(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    assert main(["--write", "out.json"]) == 0
    assert main(["--check", "out.json"]) == 0
    assert "is current" in capsys.readouterr().out


def test_check_fails_when_the_committed_copy_has_drifted(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "stale.json").write_text(json.dumps({"totals": {"loose_ends": 99}}), encoding="utf-8")
    assert main(["--check", "stale.json"]) == 1
    assert "drifted" in capsys.readouterr().err


def test_check_against_a_missing_copy_says_to_write_it(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    assert main(["--check", "nothing.json"]) == 1
    assert "run --write" in capsys.readouterr().err


def test_markdown_render_names_the_totals(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    assert main(["--format", "md"]) == 0
    out = capsys.readouterr().out
    assert out.strip(), "an empty page is not a rendering"
    assert render(build(tmp_path)).strip() == out.strip()
