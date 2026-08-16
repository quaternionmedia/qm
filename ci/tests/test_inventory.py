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


def build_with(monkeypatch, tmp_path, repos, roster_names=()):
    monkeypatch.setattr(inventory, "host_repositories", lambda org: repos)
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
    assert resolved in loc["clones"].values()


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
