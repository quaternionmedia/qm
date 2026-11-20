"""Two views of the same branches, and the distinction that cost a real bug.

`git_view` is given a lookup in every test here, so nothing shells out to git
and no test passes because this clone happens to be in the state it asserts.
The two that read the committed document say so.

THE LOAD-BEARING TEST IS `unobservable`. Three of this corpus's project branches
are recorded under redacted names -- `origin/project/private-32` and two more --
which are placeholders rather than refs. Reading a ref git cannot resolve as a
disagreement turned them into three deltas no work could ever close, which is
the queue-fills-with-noise failure `records/DRAFT-a-disagreement-is-a-delta.md`
names as its own. It was found by running the thing end to end, not by testing.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

CI_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(CI_DIR))

from two_views import (  # noqa: E402
    DOCUMENT_VIEW,
    rev_parse,
    FIELDS,
    GIT_VIEW,
    address_of,
    document_view,
    git_view,
    reconcile,
    render,
    unobservable,
)

ROOT = CI_DIR.parent


def document(**refs: str) -> Path:
    """A status document holding the given ref -> commit pairs."""
    return {
        "projects": [
            {"name": name, "branch": {"ref": f"origin/project/{name}", "commit": commit}}
            for name, commit in refs.items()
        ]
    }


def written(tmp_path: Path, data: dict) -> Path:
    path = tmp_path / "status.yaml"
    path.write_text(yaml.safe_dump(data), encoding="utf-8")
    return path


# --- the address is the join between the two views ---------------------------


def test_a_ref_becomes_an_address_keeping_its_slashes():
    """The join is the grammar. A slug here and the address could not name the
    ref it came from, which is the defect the grammar exists for."""
    assert address_of("origin/project/datum") == "quaternionmedia/qm/branch/project/datum"


def test_only_the_remote_prefix_is_stripped():
    assert address_of("origin/evolve/a/b") == "quaternionmedia/qm/branch/evolve/a/b"


def test_a_ref_with_no_remote_prefix_is_taken_whole():
    assert address_of("project/datum") == "quaternionmedia/qm/branch/project/datum"


def test_the_document_view_is_keyed_by_address(tmp_path):
    view = document_view(written(tmp_path, document(datum="aaa")))
    assert list(view) == ["quaternionmedia/qm/branch/project/datum"]
    assert view["quaternionmedia/qm/branch/project/datum"]["commit"] == "aaa"


def test_a_project_with_no_branch_commit_is_skipped(tmp_path):
    """Half a row is not a view of anything, and comparing against a missing
    commit would report a disagreement with a value nobody recorded."""
    data = {"projects": [{"name": "x", "branch": {"ref": "origin/project/x"}},
                         {"name": "y", "branch": {}}]}
    assert document_view(written(tmp_path, data)) == {}


def test_a_missing_document_is_refused(tmp_path):
    with pytest.raises(SystemExit):
        document_view(tmp_path / "absent.yaml")


# --- the git view is keyed on what the document holds ------------------------


def test_the_git_view_answers_for_every_recorded_branch(tmp_path):
    recorded = document_view(written(tmp_path, document(a="aaa", b="bbb")))
    live = git_view(recorded, lookup=lambda ref: "zzz")
    assert set(live) == set(recorded)


def test_a_ref_git_cannot_resolve_becomes_an_empty_entry(tmp_path):
    recorded = document_view(written(tmp_path, document(a="aaa")))
    assert git_view(recorded, lookup=lambda ref: None) == {
        "quaternionmedia/qm/branch/project/a": {}}


def test_a_ref_git_knows_that_the_document_does_not_is_not_invented(tmp_path):
    """One view having never heard of a row is not a disagreement, and adding
    it would be the second view asserting something it never observed."""
    recorded = document_view(written(tmp_path, document(a="aaa")))
    live = git_view(recorded, lookup=lambda ref: "aaa")
    assert "quaternionmedia/qm/branch/project/unknown" not in live


# --- unobservable is not divergent -------------------------------------------


def test_an_unresolvable_ref_is_unobservable_rather_than_diverging(tmp_path):
    recorded = document_view(written(tmp_path, document(private_32="aaa")))
    live = git_view(recorded, lookup=lambda ref: None)
    assert unobservable(recorded, live) == list(recorded)
    assert reconcile(recorded, live) == []


def test_an_unobservable_address_never_becomes_a_delta(tmp_path):
    """Three deltas that no work could close is the failure this prevents."""
    recorded = document_view(written(tmp_path, document(a="aaa", b="bbb")))
    live = git_view(recorded, lookup=lambda ref: None)
    blind = set(unobservable(recorded, live))
    assert blind & {d.address for d in reconcile(recorded, live)} == set()


def test_a_resolvable_ref_is_not_unobservable(tmp_path):
    recorded = document_view(written(tmp_path, document(a="aaa")))
    live = git_view(recorded, lookup=lambda ref: "aaa")
    assert unobservable(recorded, live) == []


def test_unobservable_and_diverging_are_reported_separately(tmp_path):
    """A mixed run must not collapse the two counts into one number."""
    recorded = document_view(written(tmp_path, document(seen="aaa", hidden="bbb")))
    live = git_view(
        recorded,
        lookup=lambda ref: None if ref.endswith("hidden") else "moved")
    blind = unobservable(recorded, live)
    found = reconcile(recorded, live)
    assert [a.rsplit("/", 1)[-1] for a in blind] == ["hidden"]
    assert [d.address.rsplit("/", 1)[-1] for d in found] == ["seen"]


# --- the comparison itself ---------------------------------------------------


def test_a_moved_branch_is_one_divergence(tmp_path):
    recorded = document_view(written(tmp_path, document(a="aaa")))
    live = git_view(recorded, lookup=lambda ref: "bbb")
    found = reconcile(recorded, live)
    assert len(found) == 1
    assert (found[0].left, found[0].right) == ("aaa", "bbb")


def test_the_views_are_named_in_the_divergence(tmp_path):
    """A reader has to know which side said which; `left` and `right` do not."""
    recorded = document_view(written(tmp_path, document(a="aaa")))
    found = reconcile(recorded, git_view(recorded, lookup=lambda ref: "bbb"))
    assert (found[0].left_view, found[0].right_view) == (DOCUMENT_VIEW, GIT_VIEW)


def test_an_unmoved_branch_produces_nothing(tmp_path):
    recorded = document_view(written(tmp_path, document(a="aaa")))
    assert reconcile(recorded, git_view(recorded, lookup=lambda ref: "aaa")) == []


def test_only_the_commit_is_compared():
    """An over-broad field list is the failure mode the record names: both
    sides carry their own observation timestamp, and comparing those opens a
    delta on every run that nobody can act on."""
    assert FIELDS == ["commit"]


def test_the_document_only_ref_field_is_not_compared(tmp_path):
    """`ref` is in the document view and never in the git view. Comparing it
    would report every branch as diverging, forever."""
    recorded = document_view(written(tmp_path, document(a="aaa")))
    assert "ref" in recorded["quaternionmedia/qm/branch/project/a"]
    assert reconcile(recorded, git_view(recorded, lookup=lambda ref: "aaa")) == []


# --- the report --------------------------------------------------------------


def test_the_report_separates_the_two_counts(tmp_path):
    recorded = document_view(written(tmp_path, document(a="aaa", b="bbb")))
    live = git_view(recorded, lookup=lambda ref: None if ref.endswith("b") else "moved")
    text = render(recorded, reconcile(recorded, live), unobservable(recorded, live))
    assert "2 branch(es) recorded, 1 of them not resolvable" in text
    assert "1 compared on commit; 1 disagree" in text


def test_the_report_says_neither_view_is_correct(tmp_path):
    recorded = document_view(written(tmp_path, document(a="aaa")))
    text = render(recorded, reconcile(recorded, git_view(recorded, lookup=lambda r: "b")), [])
    assert "Neither view is treated as correct" in text
    assert "right-by-default" in text


def test_the_report_explains_an_unobservable_ref(tmp_path):
    recorded = document_view(written(tmp_path, document(a="aaa")))
    live = git_view(recorded, lookup=lambda ref: None)
    text = render(recorded, [], unobservable(recorded, live))
    assert "not observable here, and therefore not deltas" in text
    assert "One view unable to look is not two views disagreeing" in text


def test_agreement_is_stated_rather_than_left_blank(tmp_path):
    recorded = document_view(written(tmp_path, document(a="aaa")))
    text = render(recorded, [], [])
    assert "same commit in both" in text


# --- the committed document --------------------------------------------------


def test_the_committed_document_yields_only_well_formed_addresses():
    """The join between the two views is the grammar, so this is the assertion
    that they can be joined at all."""
    from addresses import parse

    view = document_view()
    assert view
    assert all(parse(address) is not None for address in view)
    assert all(parse(address).kind == "branch" for address in view)


def test_every_committed_entry_carries_the_ref_it_came_from():
    assert all("ref" in row for row in document_view().values())


# --- the one function that really talks to git -------------------------------
#
# Every test above injects a lookup, which is right -- and leaves `rev_parse`
# itself unexercised. A mutation pass found exactly that: three survivors, all
# of them the git call nothing ran. These read this repository deliberately, and
# assert shape rather than any particular commit, so they answer the same way in
# any clone.


def test_rev_parse_resolves_a_ref_this_repository_has():
    found = rev_parse("HEAD")
    assert found is not None
    assert len(found) == 40 and all(c in "0123456789abcdef" for c in found)


def test_rev_parse_returns_none_for_a_ref_that_does_not_exist():
    """None, not an empty string. An empty commit compares unequal to every
    real one and would open a delta saying two systems disagree when one of
    them was never asked."""
    assert rev_parse("refs/heads/no-such-branch-exists-here-2026") is None


def test_rev_parse_does_not_raise_on_a_ref_git_rejects_outright():
    """A malformed ref is a failed lookup, not a crash mid-sweep."""
    assert rev_parse("not a valid ref name") is None


def test_a_divergence_with_no_recorded_value_renders_a_placeholder(tmp_path):
    """A blank where a commit goes reads as a field that failed to print."""
    recorded = document_view(written(tmp_path, document(a="aaa")))
    recorded["quaternionmedia/qm/branch/project/a"]["commit"] = None
    found = reconcile(recorded, git_view(recorded, lookup=lambda ref: "bbb"))
    assert "-" in render(recorded, found, [])
