"""The curriculum, and the reconcile that has to be optimistic and still refuse.

Every test builds its own documents in a temporary tree. The three that read the
committed `curriculum/org.yaml` say so, and they are the ones that would catch a
document being renamed out from under a unit.

THE RECONCILE IS THE PART UNDER TEST. Its three properties pull against each
other and each is asserted separately: accepted by default (optimistic), writes
nothing without being told (optional), and refuses exactly three things and no
fourth (governance-aware). A test that only checked the happy path would pass
against a reconciler that accepted everything, which is the failure mode a
merge tool has.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

CI_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(CI_DIR))

from curriculum import (  # noqa: E402
    ACCEPTED, CONFLICT, PRESENT, REFUSED, declared_status, load, main, merged,
    problems, reconcile, render, render_reconcile,
)

ROOT = CI_DIR.parent

RECORD = """# QM-XXXX — A Record

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-08-16 |

## Context
"""


def unit(uid: str = "one", teaches: str = "doc.md", **kw) -> dict:
    base = {"id": uid, "teaches": teaches, "after_this_you_can": "do a thing"}
    base.update(kw)
    return base


def curriculum(*units: dict, scope: str = "org") -> dict:
    return {"schema": 1, "id": "test", "scope": scope, "audience": "somebody",
            "units": list(units)}


def docs(tmp_path: Path, **files: str) -> Path:
    for name, text in files.items():
        path = tmp_path / name.replace("__", "/")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    return tmp_path


def write_yaml(path: Path, data: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    return path


def verdict_of(verdicts: list[dict], uid: str) -> str:
    return next(v["verdict"] for v in verdicts if v["id"] == uid)


# --- reading a document's own Status -----------------------------------------


def test_a_records_status_is_read_from_its_header(tmp_path):
    root = docs(tmp_path, **{"r.md": RECORD})
    assert declared_status(root / "r.md") == "Proposed"


def test_a_document_with_no_status_row_is_none_not_unknown(tmp_path):
    """Most documents here are not records. That is a different fact from a
    record whose Status could not be read, and collapsing the two would let a
    unit claim a Status for a handbook page."""
    root = docs(tmp_path, **{"h.md": "# A Handbook Page\n\nProse.\n"})
    assert declared_status(root / "h.md") is None


def test_a_document_that_is_not_there_is_none(tmp_path):
    assert declared_status(tmp_path / "absent.md") is None


# --- the three refusals ------------------------------------------------------


def test_a_unit_citing_a_document_that_is_not_there_is_refused(tmp_path):
    found = problems(curriculum(unit(teaches="gone.md")), tmp_path)
    assert any("is not there" in p for p in found)


def test_a_unit_claiming_a_status_the_record_does_not_carry_is_refused(tmp_path):
    """Teaching a Proposed record as Accepted asserts what no human did."""
    root = docs(tmp_path, **{"r.md": RECORD})
    found = problems(curriculum(unit(teaches="r.md", status_claimed="Accepted")), root)
    assert any("says `Proposed`" in p for p in found)


def test_a_unit_claiming_a_status_for_a_non_record_is_refused(tmp_path):
    root = docs(tmp_path, **{"h.md": "# Page\n"})
    found = problems(curriculum(unit(teaches="h.md", status_claimed="Proposed")), root)
    assert any("carries no Status row" in p for p in found)


def test_a_matching_status_claim_is_accepted(tmp_path):
    root = docs(tmp_path, **{"r.md": RECORD})
    assert problems(curriculum(unit(teaches="r.md", status_claimed="Proposed")), root) == []


def test_a_status_claim_is_compared_case_insensitively(tmp_path):
    root = docs(tmp_path, **{"r.md": RECORD})
    assert problems(curriculum(unit(teaches="r.md", status_claimed="proposed")), root) == []


def test_omitting_the_status_claim_is_allowed(tmp_path):
    """A weaker unit is not a false one. Requiring the field would push authors
    to guess it, and a guessed Status is the thing being prevented."""
    root = docs(tmp_path, **{"r.md": RECORD})
    assert problems(curriculum(unit(teaches="r.md")), root) == []


def test_a_project_curriculum_teaching_an_org_document_is_refused(tmp_path):
    """Precedence runs one way. Citing an org record is fine; owning it inverts it."""
    root = docs(tmp_path, **{"records__DRAFT-x.md": RECORD})
    found = problems(
        curriculum(unit(teaches="records/DRAFT-x.md"), scope="project"), root)
    assert any("which is the org's" in p for p in found)


def test_a_project_curriculum_teaching_its_own_adr_is_fine(tmp_path):
    root = docs(tmp_path, **{"adr__DRAFT-local.md": RECORD})
    assert problems(curriculum(unit(teaches="adr/DRAFT-local.md"), scope="project"), root) == []


def test_an_org_curriculum_teaching_an_org_document_is_fine(tmp_path):
    root = docs(tmp_path, **{"records__DRAFT-x.md": RECORD})
    assert problems(curriculum(unit(teaches="records/DRAFT-x.md")), root) == []


# --- ordering ----------------------------------------------------------------


def test_a_prerequisite_that_is_not_a_unit_is_refused(tmp_path):
    root = docs(tmp_path, **{"doc.md": "# d\n"})
    found = problems(curriculum(unit(prerequisites=["ghost"])), root)
    assert any("not a unit" in p for p in found)


def test_a_prerequisite_that_comes_later_is_refused(tmp_path):
    """Order is the artifact. A path whose steps are out of order is not a path."""
    root = docs(tmp_path, **{"doc.md": "# d\n"})
    found = problems(
        curriculum(unit("first", prerequisites=["second"]), unit("second")), root)
    assert any("comes after it" in p for p in found)


def test_a_unit_that_is_its_own_prerequisite_is_refused(tmp_path):
    root = docs(tmp_path, **{"doc.md": "# d\n"})
    found = problems(curriculum(unit("one", prerequisites=["one"])), root)
    assert any("its own prerequisite" in p for p in found)


def test_two_units_with_one_id_are_refused(tmp_path):
    root = docs(tmp_path, **{"doc.md": "# d\n"})
    found = problems(curriculum(unit("one"), unit("one")), root)
    assert any("duplicate unit id" in p for p in found)


# --- the reconcile: optimistic -----------------------------------------------


def test_an_unseen_incoming_unit_is_accepted_without_being_asked_about(tmp_path):
    root = docs(tmp_path, **{"doc.md": "# d\n"})
    verdicts = reconcile(curriculum(unit("base")), curriculum(unit("new")), root)
    assert verdict_of(verdicts, "new") == ACCEPTED


def test_an_identical_unit_is_present_rather_than_a_conflict(tmp_path):
    root = docs(tmp_path, **{"doc.md": "# d\n"})
    verdicts = reconcile(curriculum(unit("same")), curriculum(unit("same")), root)
    assert verdict_of(verdicts, "same") == PRESENT


def test_merging_appends_every_accepted_unit_and_keeps_the_base(tmp_path):
    root = docs(tmp_path, **{"doc.md": "# d\n"})
    base = curriculum(unit("base"))
    verdicts = reconcile(base, curriculum(unit("new")), root)
    out = merged(base, verdicts)
    assert [u["id"] for u in out["units"]] == ["base", "new"]


def test_the_base_is_never_mutated_by_a_reconcile(tmp_path):
    """The reconcile reports what integrating would cost. It must be safe to run
    before deciding to do it."""
    root = docs(tmp_path, **{"doc.md": "# d\n"})
    base = curriculum(unit("base"))
    before = yaml.safe_dump(base, sort_keys=True)
    merged(base, reconcile(base, curriculum(unit("new")), root))
    assert yaml.safe_dump(base, sort_keys=True) == before


# --- the reconcile: a conflict is neither accepted nor dropped ---------------


def test_a_differing_unit_with_the_same_id_is_a_conflict(tmp_path):
    root = docs(tmp_path, **{"doc.md": "# d\n", "other.md": "# o\n"})
    verdicts = reconcile(
        curriculum(unit("one", teaches="doc.md")),
        curriculum(unit("one", teaches="other.md")), root)
    assert verdict_of(verdicts, "one") == CONFLICT


def test_a_conflict_names_the_fields_that_differ(tmp_path):
    root = docs(tmp_path, **{"doc.md": "# d\n", "other.md": "# o\n"})
    verdicts = reconcile(
        curriculum(unit("one", teaches="doc.md")),
        curriculum(unit("one", teaches="other.md")), root)
    assert "teaches" in verdicts[0]["why"][0]


def test_a_conflicting_unit_does_not_reach_the_merged_output(tmp_path):
    """Kept, reported, and not applied. Silently overwriting the base would be
    the reconcile deciding something a person has to."""
    root = docs(tmp_path, **{"doc.md": "# d\n", "other.md": "# o\n"})
    base = curriculum(unit("one", teaches="doc.md"))
    out = merged(base, reconcile(base, curriculum(unit("one", teaches="other.md")), root))
    assert [u["teaches"] for u in out["units"]] == ["doc.md"]


def test_a_conflict_is_not_silently_dropped_from_the_report(tmp_path):
    root = docs(tmp_path, **{"doc.md": "# d\n", "other.md": "# o\n"})
    verdicts = reconcile(
        curriculum(unit("one", teaches="doc.md")),
        curriculum(unit("one", teaches="other.md")), root)
    assert "one" in render_reconcile(verdicts, Path("base.yaml"), Path("other.yaml"))


# --- the reconcile: governance-aware, and no fourth refusal ------------------


def test_an_incoming_unit_citing_nothing_is_refused_not_accepted(tmp_path):
    root = docs(tmp_path, **{"doc.md": "# d\n"})
    verdicts = reconcile(curriculum(unit("base")), curriculum(unit("bad", teaches="gone.md")), root)
    assert verdict_of(verdicts, "bad") == REFUSED


def test_a_refused_unit_does_not_reach_the_merged_output(tmp_path):
    root = docs(tmp_path, **{"doc.md": "# d\n"})
    base = curriculum(unit("base"))
    out = merged(base, reconcile(base, curriculum(unit("bad", teaches="gone.md")), root))
    assert [u["id"] for u in out["units"]] == ["base"]


def test_an_incoming_project_unit_claiming_an_org_document_is_refused(tmp_path):
    root = docs(tmp_path, **{"records__DRAFT-x.md": RECORD, "doc.md": "# d\n"})
    verdicts = reconcile(
        curriculum(unit("base")),
        curriculum(unit("grab", teaches="records/DRAFT-x.md"), scope="project"), root)
    assert verdict_of(verdicts, "grab") == REFUSED


def test_an_unusual_but_legitimate_unit_is_not_refused(tmp_path):
    """The guard pass: only three things are refusals. A unit with extra fields,
    no prerequisites and no status claim is odd and legal, and a reconciler that
    got strict here would be one nobody runs."""
    root = docs(tmp_path, **{"doc.md": "# d\n"})
    odd = unit("odd", note="a field nothing reads", prerequisites=[])
    verdicts = reconcile(curriculum(unit("base")), curriculum(odd), root)
    assert verdict_of(verdicts, "odd") == ACCEPTED


# --- the reconcile: optional -------------------------------------------------


def test_a_reconcile_writes_nothing_unless_told(tmp_path, capsys):
    root = docs(tmp_path, **{"doc.md": "# d\n"})
    base = write_yaml(root / "base.yaml", curriculum(unit("base")))
    other = write_yaml(root / "other.yaml", curriculum(unit("new")))
    out = root / "merged.yaml"
    assert main(["--file", str(base), "--root", str(root), "--merge", str(other)]) == 0
    assert not out.exists()
    assert "Nothing was written" in capsys.readouterr().out


def test_write_produces_the_merged_file(tmp_path):
    root = docs(tmp_path, **{"doc.md": "# d\n"})
    base = write_yaml(root / "base.yaml", curriculum(unit("base")))
    other = write_yaml(root / "other.yaml", curriculum(unit("new")))
    out = root / "merged.yaml"
    assert main(["--file", str(base), "--root", str(root), "--merge", str(other),
                 "--write", str(out)]) == 0
    assert [u["id"] for u in yaml.safe_load(out.read_text(encoding="utf-8"))["units"]] \
        == ["base", "new"]


def test_a_refusal_reds_the_run_only_under_check(tmp_path):
    """Reporting is not judging. The reconcile has to be readable before anyone
    decides to act on it, so a refusal alone does not fail the command."""
    root = docs(tmp_path, **{"doc.md": "# d\n"})
    base = write_yaml(root / "base.yaml", curriculum(unit("base")))
    other = write_yaml(root / "other.yaml", curriculum(unit("bad", teaches="gone.md")))
    argv = ["--file", str(base), "--root", str(root), "--merge", str(other)]
    assert main(argv) == 0
    assert main([*argv, "--check"]) == 1


def test_an_empty_curriculum_is_refused_rather_than_reconciling_clean(tmp_path):
    path = write_yaml(tmp_path / "empty.yaml", {"schema": 1, "units": []})
    with pytest.raises(SystemExit):
        load(path)


# --- what the output actually says -------------------------------------------


def test_the_listing_prints_every_unit_in_order():
    """A reading order printed as an empty list is the tool losing the artifact."""
    text = render(curriculum(unit("first"), unit("second")), Path("org.yaml"))
    assert "1. first" in text and "2. second" in text
    assert "2 unit(s)" in text


def test_a_unit_with_no_prerequisites_says_nothing_rather_than_blank():
    text = render(curriculum(unit("first")), Path("org.yaml"))
    assert "after               nothing" in text


def test_the_reconcile_summary_counts_each_verdict(tmp_path):
    """The four counts are the line a reader acts on before reading the detail."""
    root = docs(tmp_path, **{"doc.md": "# d\n", "other.md": "# o\n"})
    base = curriculum(unit("keep", teaches="doc.md"), unit("clash", teaches="doc.md"))
    other = curriculum(
        unit("keep", teaches="doc.md"),
        unit("clash", teaches="other.md"),
        unit("fresh", teaches="doc.md"),
        unit("bad", teaches="gone.md"),
    )
    text = render_reconcile(reconcile(base, other, root), Path("b.yaml"), Path("o.yaml"))
    assert "1 accepted" in text
    assert "1 already present" in text
    assert "1 conflicting" in text
    assert "1 refused" in text


def test_the_written_file_keeps_each_unit_field_in_the_order_written(tmp_path):
    """Sorted keys would churn every diff of a file whose whole point is order."""
    root = docs(tmp_path, **{"doc.md": "# d\n"})
    base = write_yaml(root / "base.yaml", curriculum(unit("base")))
    other = write_yaml(root / "other.yaml", curriculum(unit("new")))
    out = root / "merged.yaml"
    main(["--file", str(base), "--root", str(root), "--merge", str(other),
          "--write", str(out)])
    body = out.read_text(encoding="utf-8")
    assert body.index("- id: base") < body.index("teaches:")


def test_the_written_file_keeps_non_ascii_unescaped(tmp_path):
    """This corpus's prose is full of em dashes. Escaped, they are unreadable."""
    root = docs(tmp_path, **{"doc.md": "# d\n"})
    base = write_yaml(root / "base.yaml", curriculum(unit("base")))
    other = write_yaml(
        root / "other.yaml",
        curriculum(unit("new", after_this_you_can="resolve a clash — without asking")))
    out = root / "merged.yaml"
    main(["--file", str(base), "--root", str(root), "--merge", str(other),
          "--write", str(out)])
    assert "—" in out.read_text(encoding="utf-8")


# --- the committed org curriculum --------------------------------------------


def test_the_committed_curriculum_teaches_only_documents_that_exist():
    """If this fails, a document was renamed and the reading path now opens
    nothing. It is the one check here that reads the repository."""
    assert problems(load(ROOT / "curriculum" / "org.yaml")) == []


def test_the_committed_curriculum_starts_with_no_prerequisites():
    units = load(ROOT / "curriculum" / "org.yaml")["units"]
    assert not units[0].get("prerequisites")


def test_every_committed_unit_says_what_a_reader_can_then_do():
    for entry in load(ROOT / "curriculum" / "org.yaml")["units"]:
        assert entry.get("after_this_you_can", "").strip()
