"""Tests for the org inventory, mostly about what it must not emit.

An earlier version wrote 34 private repository names and 28 absolute paths
containing an operator's username into the working tree of a public repository.
It was one command from being pushed. These tests exist so that cannot recur
quietly: every one of them fails if the redaction is weakened.

The host is never called. Every case feeds `build`-shaped data directly, so the
suite answers the same way on a machine with no credential.
"""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import pytest

CI_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(CI_DIR))

import inventory  # noqa: E402
from inventory import LOCAL, PRIVATE, PUBLIC, assign_references, local_clone  # noqa: E402

ORG = "testorg"


def strings(obj) -> list[str]:
    """Every string value anywhere in a structure.

    Assertions walk this rather than `json.dumps`. Serialising doubles every
    backslash in a Windows path, so a substring test for the raw path against
    the serialised blob silently passes even when the path is present. Three of
    these tests were inert that way, in a suite whose whole subject is a
    privacy leak.
    """
    if isinstance(obj, str):
        return [obj]
    if isinstance(obj, dict):
        return [s for k, v in obj.items() for s in strings(k) + strings(v)]
    if isinstance(obj, (list, tuple)):
        return [s for v in obj for s in strings(v)]
    return []


def contains(obj, needle: str) -> bool:
    return any(needle in s for s in strings(obj))


def repo(name, private=False, created="2020-01-01T00:00:00Z", **kw):
    return {"name": name, "isPrivate": private, "isFork": False, "isArchived": False,
            "createdAt": created, "updatedAt": "2026-01-01T00:00:00Z",
            "primaryLanguage": None, "diskUsage": 1, **kw}


def build_with(monkeypatch, tmp_path, repos, roster_names=(), commits=None):
    monkeypatch.setattr(inventory, "host_repositories", lambda org: repos)
    # `build` gained a second host call for the default branch dates. Without
    # this every case in this file would shell out to gh, and the promise at
    # the top of the page -- that the suite answers the same on a machine with
    # no credential -- would be quietly false.
    monkeypatch.setattr(inventory, "default_branch_commits",
                        lambda org: commits or {})
    roster = tmp_path / "workspace.yaml"
    roster.write_text(
        "repositories:\n" + "".join(f"  - name: {n}\n" for n in roster_names) or "repositories: []\n",
        encoding="utf-8",
    )
    return inventory.build(ORG, roster, [tmp_path])


# --- what the document must never contain ----------------------------------


def test_a_private_repository_name_never_reaches_the_public_file(monkeypatch, tmp_path):
    pub, priv, _ = build_with(monkeypatch, tmp_path, [repo("client-secret-name", private=True)])
    assert not contains(pub, "client-secret-name")
    assert contains(priv, "client-secret-name"), "the private file is where it belongs"


def test_a_public_repository_name_is_kept(monkeypatch, tmp_path):
    """Redaction that hid public names would make the census unreadable."""
    pub, _, _ = build_with(monkeypatch, tmp_path, [repo("qm")])
    assert contains(pub, "qm")


def test_no_absolute_path_reaches_the_document(monkeypatch, tmp_path):
    """`make_workspace.py` already states this rule; this one broke it once."""
    pub, _, _ = build_with(monkeypatch, tmp_path, [repo("qm"), repo("p", private=True)])
    blob = json.dumps(pub)
    assert str(tmp_path) not in blob
    assert "C:\\\\Users" not in blob and "/home/" not in blob


def test_the_document_declares_that_it_redacts(monkeypatch, tmp_path):
    """A reader must be able to tell the names are withheld, not absent."""
    pub, _, _ = build_with(monkeypatch, tmp_path, [repo("p", private=True)])
    g = pub["generator"]
    assert g["private_repository_names_listed"] is False
    assert g["absolute_paths_written"] is False
    assert "private-NN" in g["private_repositories_referenced_as"]


def test_private_repositories_are_counted_not_dropped(monkeypatch, tmp_path):
    """Omitting them would be the easy fix and a census nobody can act on."""
    pub, _, _ = build_with(monkeypatch, tmp_path,
                        [repo("a"), repo("p1", private=True), repo("p2", private=True)])
    assert pub["totals"]["private"] == 2
    assert pub["totals"]["on_host"] == 3
    assert len(pub["repositories"]) == 3


# --- references have to be stable ------------------------------------------


def test_references_follow_creation_order():
    private = [repo("newer", True, "2024-01-01T00:00:00Z"),
               repo("older", True, "2020-01-01T00:00:00Z")]
    refs = assign_references(private, ORG)
    assert refs["older"]["ref"] == "private-01"
    assert refs["newer"]["ref"] == "private-02"


def test_a_new_repository_does_not_renumber_the_existing_ones():
    """A reference in a six-month-old document must still point at the same
    repository. Ordering by name or by hash would shift every number."""
    before = assign_references(
        [repo("a", True, "2020-01-01T00:00:00Z"), repo("z", True, "2021-01-01T00:00:00Z")], ORG)
    after = assign_references(
        [repo("a", True, "2020-01-01T00:00:00Z"), repo("z", True, "2021-01-01T00:00:00Z"),
         repo("aaa", True, "2026-01-01T00:00:00Z")], ORG)
    assert before["a"]["ref"] == after["a"]["ref"] == "private-01"
    assert before["z"]["ref"] == after["z"]["ref"] == "private-02"
    assert after["aaa"]["ref"] == "private-03"


def test_the_label_is_readable_and_names_the_org():
    refs = assign_references([repo("x", True)], "quaternionmedia")
    assert refs["x"]["label"] == "quaternionmedia private repo 1"


def test_every_private_row_carries_a_reference_and_a_label(monkeypatch, tmp_path):
    pub, _, _ = build_with(monkeypatch, tmp_path,
                        [repo(f"p{i}", private=True, created=f"202{i}-01-01T00:00:00Z")
                         for i in range(3)])
    for row in pub["repositories"]:
        assert row["ref"].startswith("private-")
        assert "private repo" in row["label"]
        assert "name" not in row


# --- the key ----------------------------------------------------------------


def test_the_key_warns_that_it_must_not_leave_the_machine(monkeypatch, tmp_path):
    _, priv, _ = build_with(monkeypatch, tmp_path, [repo("p", private=True)])
    assert "do not commit" in priv["warning"].lower()


def test_the_key_maps_every_reference(monkeypatch, tmp_path):
    pub, priv, loc = build_with(monkeypatch, tmp_path,
                          [repo("p1", private=True, created="2020-01-01T00:00:00Z"),
                           repo("p2", private=True, created="2021-01-01T00:00:00Z")])
    refs = {r['ref'] for r in pub['repositories']}
    assert refs == set(priv['references'])


def test_the_two_sensitive_files_are_gitignored_and_the_public_one_is_not():
    """The file split is the control; this is the second layer, checked because
    a gitignore line is easy to lose in a merge.

    Asked of git rather than of the file's text: the .gitignore explains the
    split in a comment that names all three files, so a substring search finds
    every one of them and proves nothing.
    """
    def ignored(name: str) -> bool:
        return subprocess.run(["git", "check-ignore", "-q", name],
                              cwd=CI_DIR.parent).returncode == 0

    assert ignored(PRIVATE)
    assert ignored(LOCAL)
    assert not ignored(PUBLIC), "the public file must remain committable"


# --- local presence ---------------------------------------------------------


def test_cloned_here_is_a_boolean_not_a_path(monkeypatch, tmp_path):
    (tmp_path / "here" / ".git").mkdir(parents=True)
    pub, _, _ = build_with(monkeypatch, tmp_path, [repo("here")])
    row = pub["repositories"][0]
    assert row["cloned_here"] is True
    assert not any(isinstance(v, str) and str(tmp_path) in v for v in row.values())


def test_an_uncloned_repository_reads_false_not_missing(monkeypatch, tmp_path):
    pub, _, _ = build_with(monkeypatch, tmp_path, [repo("elsewhere")])
    assert pub["repositories"][0]["cloned_here"] is False


def test_local_clone_needs_a_git_directory(tmp_path):
    (tmp_path / "notarepo").mkdir()
    assert local_clone("notarepo", None, [tmp_path]) is None


def test_clone_paths_go_only_to_the_local_file(monkeypatch, tmp_path):
    """A path is a fact about one operator's disk, not about the org."""
    (tmp_path / "here" / ".git").mkdir(parents=True)
    pub, _, loc = build_with(monkeypatch, tmp_path, [repo("here")])
    resolved = str((tmp_path / "here").resolve())
    assert not contains(pub, resolved)
    assert resolved in [entry["path"] for entry in loc["clones"].values()]


def test_the_local_file_warns_it_must_not_be_committed(monkeypatch, tmp_path):
    _, _, loc = build_with(monkeypatch, tmp_path, [repo("a")])
    assert "do not commit" in loc["warning"].lower()


# --- the host layer ---------------------------------------------------------


def test_an_unreadable_host_is_unknown_not_empty(monkeypatch, tmp_path):
    """A census nobody could take must not read as an org with no repositories."""
    monkeypatch.setattr(inventory, "host_repositories",
                        lambda org: {"unknown": "no credential"})
    roster = tmp_path / "w.yaml"
    roster.write_text("repositories: []\n", encoding="utf-8")
    pub, priv, loc = inventory.build(ORG, roster, [tmp_path])
    assert "unknown" in pub["host"]
    assert pub["repositories"] == []
    assert priv == {} and loc == {}


# --- the activity axes ------------------------------------------------------
#
# Each test below names the mutation that makes it fail, because a test written
# against a signal only ever observed green has been watched rather than
# tested. The mutations were run: every assertion here went red on the change
# it names, and the two that did not were rewritten until they did.


def at(stamp: str) -> datetime:
    return datetime.fromisoformat(stamp.replace("Z", "+00:00"))


NOW = at("2026-08-19T00:00:00Z")


def host_row(**kw) -> dict:
    return {"archived": False, "default_branch_commit_at": None, **kw}


# recency: measured, and only from the default branch --------------------------


def test_a_commit_inside_the_live_window_is_live():
    row = host_row(default_branch_commit_at="2026-08-18T00:00:00Z")
    assert inventory.recency_of(row, NOW) == "live"


def test_a_commit_past_the_live_window_is_quiet():
    """Mutation: widen LIVE_DAYS past 60 and this returns `live`."""
    row = host_row(default_branch_commit_at="2026-06-18T00:00:00Z")
    assert inventory.recency_of(row, NOW) == "quiet"


def test_a_commit_past_a_year_is_cold():
    """Mutation: raise QUIET_DAYS past 800 and this returns `quiet`."""
    row = host_row(default_branch_commit_at="2024-01-11T00:00:00Z")
    assert inventory.recency_of(row, NOW) == "cold"


def test_archived_beats_a_commit_from_yesterday():
    """The host has said the repository is closed. A recent commit on a branch
    somebody forgot to stop pushing to does not reopen it.

    Mutation: check the date before the archived flag and this returns `live`.
    """
    row = host_row(archived=True, default_branch_commit_at="2026-08-18T00:00:00Z")
    assert inventory.recency_of(row, NOW) == "archived"


def test_a_repository_with_no_commit_date_is_unknown_and_never_cold():
    """`cold` would be a claim that nothing has happened. Nobody looked.

    Mutation: return `cold` on a missing date and this fails -- which is the
    substitution that would make an empty read look like a dormant repository.
    """
    assert inventory.recency_of(host_row(), NOW) == "unknown"


def test_an_unparseable_commit_date_is_unknown_rather_than_an_exception():
    assert inventory.recency_of(
        host_row(default_branch_commit_at="not a date"), NOW) == "unknown"


# attention: a claim, and silence is not one ---------------------------------


def test_a_stated_attention_is_carried_through():
    assert inventory.attention_of({"attention": "retired"}) == "retired"


def test_an_absent_attention_is_unstated_and_not_dormant():
    """Mutation: default to `dormant` and this fails.

    `dormant` says nobody is working on it. `unstated` says nobody answered
    the question. A roster that turns the second into the first grows claims
    no human made, which is the substitution `phase_source` already refuses.
    """
    assert inventory.attention_of({"name": "qm"}) == "unstated"


def test_a_value_outside_the_vocabulary_is_unstated():
    """A typo must not become a category. Mutation: pass the value through
    unchecked and `attention: activ` silently becomes its own bucket."""
    assert inventory.attention_of({"attention": "activ"}) == "unstated"


def test_a_repository_missing_from_the_roster_is_unrostered():
    assert inventory.attention_of(None) == "unrostered"


# risk: machine-scoped, and unreadable is not clean ---------------------------


def test_an_uninspectable_clone_is_unreadable_and_never_clean():
    """Mutation: return `["clean"]` when the clone is unreadable and this fails.

    A repository nobody could look at has an unknown amount of work at stake.
    Reporting that as nothing at stake is how a governance dashboard goes green
    because its query returned empty.
    """
    risk = inventory.risk_of({"readable": False, "reason": "not cloned here"})
    assert risk == ["unreadable:not cloned here"]
    assert "clean" not in risk


def test_risk_flags_hold_at_once_rather_than_replacing_each_other():
    """Mutation: return the first flag instead of the list and this fails.
    One repository here carries all three."""
    assert inventory.risk_of({
        "readable": True, "local_only_commits": 45,
        "dirty_entries": 7, "submodule_pin_dirty": True,
    }) == ["unpushed:45", "dirty:7", "pin-drift"]


def test_a_clean_clone_says_clean():
    assert inventory.risk_of({
        "readable": True, "local_only_commits": 0,
        "dirty_entries": 0, "submodule_pin_dirty": False,
    }) == ["clean"]


# the roster's private entries ------------------------------------------------


def test_a_ref_only_roster_entry_is_found_by_its_reference(tmp_path):
    """A private repository is rostered as `ref: private-NN` and no name.

    Keying the roster on `name` alone dropped all three of them, so the corpus
    reported repositories it had rostered under "the corpus cannot see these",
    and the activity view called them unrostered. Mutation: filter on
    `e.get("name")` again and this fails.
    """
    roster = tmp_path / "workspace.yaml"
    roster.write_text(
        "repositories:\n"
        "  - name: qm\n"
        "  - ref: private-32\n"
        "    attention: dormant\n",
        encoding="utf-8",
    )
    by_name, by_ref, problem = inventory.roster_names(roster)
    assert problem is None
    # `roster.load` guarantees `name`, standing the reference in when the
    # gitignored companion is absent -- so the entry is reachable both ways and
    # neither index can silently lose it.
    assert set(by_name) == {"qm", "private-32"}
    assert set(by_ref) == {"private-32"}
    assert inventory.attention_of(by_ref["private-32"]) == "dormant"


def test_a_private_repository_in_the_roster_is_counted_as_rostered(monkeypatch, tmp_path):
    """The end-to-end form of the case above, through `build`."""
    roster = tmp_path / "workspace.yaml"
    roster.write_text("repositories:\n  - ref: private-01\n", encoding="utf-8")
    monkeypatch.setattr(inventory, "host_repositories",
                        lambda org: [repo("secret", private=True)])
    monkeypatch.setattr(inventory, "default_branch_commits", lambda org: {})
    pub, _, _ = inventory.build(ORG, roster, [tmp_path])
    assert pub["totals"]["in_roster"] == 1
    assert pub["totals"]["on_host_not_in_roster"] == 0
    assert pub["repositories"][0]["attention"] == "unstated"


# pagination: the defect this corpus has already shipped once -----------------


def test_every_page_of_a_paginated_response_is_read():
    """`gh api graphql --paginate` emits one document per page, not one array.

    Reading only the first would return 100 of 111 repositories and report the
    remainder as absent -- the same shape as the `gh api` call this corpus
    already recorded as returning a hundred of a hundred and nine.

    Mutation: return `[docs[0]]` from decode_stream and this fails.
    """
    stream = '{"page": 1}\n{"page": 2}  {"page": 3}'
    assert [d["page"] for d in inventory.decode_stream(stream)] == [1, 2, 3]


def test_default_branch_commits_reads_names_from_every_page(monkeypatch):
    def two_pages(cmd, **kw):
        page = lambda name, date: json.dumps({"data": {"organization": {
            "repositories": {"nodes": [
                {"name": name, "defaultBranchRef": {"target": {"committedDate": date}}}
            ]}}}})
        return subprocess.CompletedProcess(
            cmd, 0, page("first", "2026-01-01T00:00:00Z")
            + "\n" + page("second", "2026-02-02T00:00:00Z"), "")

    monkeypatch.setattr(inventory.subprocess, "run", two_pages)
    dates = inventory.default_branch_commits(ORG)
    assert dates == {"first": "2026-01-01T00:00:00Z",
                     "second": "2026-02-02T00:00:00Z"}


def test_a_repository_with_no_default_branch_gets_a_date_of_none(monkeypatch):
    """An empty repository has no default branch ref. It must arrive as None
    and become `unknown`, never as a missing key that reads as cold."""
    monkeypatch.setattr(inventory.subprocess, "run", lambda cmd, **kw:
                        subprocess.CompletedProcess(cmd, 0, json.dumps({"data": {
                            "organization": {"repositories": {"nodes": [
                                {"name": "empty", "defaultBranchRef": None}]}}}}), ""))
    assert inventory.default_branch_commits(ORG) == {"empty": None}


def test_a_failed_host_call_is_an_unknown_rather_than_an_empty_mapping(monkeypatch):
    """Mutation: return `{}` on failure and every repository silently becomes
    `recency: unknown` with nothing saying the host was never reached."""
    monkeypatch.setattr(inventory.subprocess, "run", lambda cmd, **kw:
                        subprocess.CompletedProcess(cmd, 1, "", "gh: not logged in"))
    result = inventory.default_branch_commits(ORG)
    assert "unknown" in result and "not logged in" in result["unknown"]


# the disagreement between the two axes --------------------------------------


def test_a_repository_claimed_active_whose_branch_is_cold_is_a_disagreement():
    assert inventory.disagrees({"attention": "active", "recency": "cold"})


def test_a_repository_claimed_retired_that_is_moving_is_a_disagreement():
    assert inventory.disagrees({"attention": "retired", "recency": "live"})


def test_a_live_repository_the_roster_omits_is_a_disagreement():
    """This is the one that found two repositories the corpus governs and the
    roster did not list."""
    assert inventory.disagrees({"attention": "unrostered", "recency": "live"})


def test_agreement_is_not_reported_as_a_disagreement():
    """Mutation: return a reason unconditionally and this fails -- which is the
    check that reports every row as a finding and therefore none."""
    assert inventory.disagrees({"attention": "active", "recency": "live"}) is None
    assert inventory.disagrees({"attention": "unstated", "recency": "cold"}) is None


# what must not leak, now that the local file carries more ---------------------


def test_risk_and_unpushed_counts_stay_out_of_the_public_file(monkeypatch, tmp_path):
    """Unpushed counts and dirty counts describe one operator's disk. The split
    is a file boundary, not a filter, so they must never be built into the
    committable document at all.

    Mutation: put `risk` on the public row and this fails.
    """
    roster = tmp_path / "workspace.yaml"
    roster.write_text("repositories:\n  - name: qm\n", encoding="utf-8")
    monkeypatch.setattr(inventory, "host_repositories", lambda org: [repo("qm")])
    monkeypatch.setattr(inventory, "default_branch_commits", lambda org: {})
    monkeypatch.setattr(inventory, "local_clone", lambda *a: str(tmp_path))
    monkeypatch.setattr(inventory, "local_signals", lambda clone: {
        "readable": True, "local_only_commits": 45, "dirty_entries": 7,
        "submodule_pin_dirty": True, "local_only_by_ref": []})
    pub, _, loc = inventory.build(ORG, roster, [tmp_path])
    # Scanned over the rows, not the whole document: the generator block names
    # the risk vocabulary in prose, and a scan of the file matched that
    # sentence and passed while proving nothing -- which is the inert check
    # this corpus has shipped before.
    assert not contains(pub["repositories"], "unpushed")
    assert not contains(pub["repositories"], "pin-drift")
    assert not contains(pub["totals"], "unpushed")
    assert contains(loc["clones"], "unpushed:45"), "the local file is where it belongs"
