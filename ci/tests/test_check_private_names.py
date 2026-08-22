"""The private-name check, and the false reading its first version produced.

A plain substring search reported `inventory-public.json` as carrying a private
name. It carries a *public* repository three characters longer whose name
contains the private one -- so the file whose entire guarantee is that it holds
no private name appeared to break that guarantee, by the check rather than by
the file. Most of these tests are about boundaries.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

CI_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(CI_DIR))

from check_private_names import main, pattern, private_names, scan  # noqa: E402

SECRET = "a-private-repo"


def repo_at(tmp_path: Path, files: dict[str, str]) -> Path:
    """A real git repository, because the check reads `git ls-files`.

    A directory walk would report untracked and ignored files, which are
    exactly the files allowed to carry these names.
    """
    for rel, text in files.items():
        path = tmp_path / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(["git", "add", "-A"], cwd=tmp_path, check=True)
    return tmp_path


# --- boundaries -------------------------------------------------------------


@pytest.mark.parametrize(
    "text, matches",
    [
        (f"the {SECRET} repository", True),
        (f"{SECRET}", True),
        (f"qm/{SECRET}/ci", True),
        (f"quaternionmedia/{SECRET}.git", True),
        (f"{SECRET}-docs", False),
        (f"data{SECRET}", False),
        (f"{SECRET}2", False),
        (f"x{SECRET}x", False),
    ],
    ids=["in-prose", "alone", "in-a-path", "in-a-url",
         "longer-suffix", "longer-prefix", "digit-suffix", "surrounded"],
)
def test_a_longer_name_containing_the_private_one_is_not_a_match(text, matches):
    assert bool(pattern(SECRET).search(text)) is matches


# --- what it reads ----------------------------------------------------------


def test_a_tracked_file_carrying_the_name_is_found(tmp_path: Path):
    root = repo_at(tmp_path, {"handbook/page.md": f"see {SECRET} for details\n"})
    assert scan(root, {SECRET}) == [("handbook/page.md", SECRET)]


def test_an_untracked_file_is_not_scanned(tmp_path: Path):
    """The companions holding these names are untracked by design."""
    root = repo_at(tmp_path, {"tracked.md": "nothing here\n"})
    (root / "untracked.md").write_text(f"{SECRET}\n", encoding="utf-8")
    assert scan(root, {SECRET}) == []


def test_a_clean_tree_reports_nothing(tmp_path: Path):
    root = repo_at(tmp_path, {"a.md": "alfred and datum\n"})
    assert scan(root, {SECRET}) == []


def test_a_binary_file_does_not_stop_the_scan(tmp_path: Path):
    root = repo_at(tmp_path, {"note.md": f"{SECRET}\n"})
    (root / "blob.bin").write_bytes(b"\x00\x01\x02\xff")
    subprocess.run(["git", "add", "-A"], cwd=root, check=True)
    assert ("note.md", SECRET) in scan(root, {SECRET})


# --- where the names come from ---------------------------------------------


def test_names_are_read_from_both_companions(tmp_path: Path):
    inv = tmp_path / "inventory-private.json"
    inv.write_text(json.dumps({"repositories": [{"name": "from-json"}]}), encoding="utf-8")
    ws = tmp_path / "workspace-private.yaml"
    ws.write_text(yaml.safe_dump({"repositories": [{"name": "from-yaml"}]}), encoding="utf-8")
    assert private_names((inv, ws)) == {"from-json", "from-yaml"}


def test_a_missing_companion_contributes_nothing(tmp_path: Path):
    assert private_names((tmp_path / "nope.json",)) == set()


def test_an_entry_without_a_name_is_skipped(tmp_path: Path):
    """The public inventory's private entries carry `ref` and no name at all."""
    path = tmp_path / "inventory-private.json"
    path.write_text(json.dumps({"repositories": [{"ref": "private-01"}]}), encoding="utf-8")
    assert private_names((path,)) == set()


# --- the three states -------------------------------------------------------


def test_no_source_is_unverified_and_says_so(tmp_path: Path, capsys, monkeypatch):
    monkeypatch.setattr("check_private_names.SOURCES", (tmp_path / "absent.json",))
    assert main(["--root", str(tmp_path)]) == 0
    assert capsys.readouterr().out.startswith("unverified")


def test_unverified_fails_under_strict(tmp_path: Path, monkeypatch):
    """A machine holding the companions should not silently skip the check."""
    monkeypatch.setattr("check_private_names.SOURCES", (tmp_path / "absent.json",))
    assert main(["--root", str(tmp_path), "--strict"]) == 1


def test_a_hit_exits_non_zero_without_printing_the_name(tmp_path: Path, capsys, monkeypatch):
    """Printing it here would put it in a log, which is the thing prevented one
    layer along."""
    source = tmp_path / "inventory-private.json"
    source.write_text(json.dumps({"repositories": [{"name": SECRET}]}), encoding="utf-8")
    root = repo_at(tmp_path / "tree", {"page.md": f"{SECRET}\n"})
    monkeypatch.setattr("check_private_names.SOURCES", (source,))

    assert main(["--root", str(root)]) == 1
    captured = capsys.readouterr()
    assert "found" in captured.err
    assert SECRET not in captured.err
    assert SECRET not in captured.out


# --- two tiers, and the org collision ---------------------------------------
#
# Knowing all 34 private names rather than 2 turned this check from
# under-reporting into unusable: one private repository is named the same as
# the public organisation and matched 187 URLs, and several others are ordinary
# English words. Neither was a disclosure.

from check_private_names import ambiguous, occurrences, references  # noqa: E402


@pytest.mark.parametrize(
    "name, is_word",
    [
        ("zib", True), ("quix", True), ("blorpling", True),
        ("wobblyteapot", False),        # 12 letters
        ("wobbly-teapot", False),     # hyphenated
        ("qm2", False),                 # has a digit
    ],
    ids=["3-letters", "4-letters", "9-letters", "long", "hyphenated", "digit"],
)
def test_only_a_short_all_letter_name_is_ambiguous(name, is_word):
    assert ambiguous(name) is is_word


def test_a_distinctive_name_in_prose_is_a_finding(tmp_path: Path):
    """A handbook sentence listing repositories has no slash and no quotes, and
    is still a disclosure. Tiering on context alone demoted exactly this."""
    root = repo_at(tmp_path, {"page.md": "we adopted alfred, big-private-repo and datum\n"})
    hits = [h for h in occurrences(root, {"big-private-repo"}) if h["certain"]]
    assert len(hits) == 1


def test_an_ambiguous_name_in_prose_is_only_possible(tmp_path: Path):
    root = repo_at(tmp_path, {"page.md": "the rebuild blorpling is reported\n"})
    found = occurrences(root, {"blorpling"})
    assert found and not any(h["certain"] for h in found)


@pytest.mark.parametrize(
    "line",
    [
        "url = https://github.com/org/blorpling.git",
        'slug = "org/blorpling"',
        '  "name": "blorpling",',
        "branch: blorpling",
        "path = blorpling/ci",
    ],
    ids=["a-url", "a-slug", "a-json-field", "a-yaml-field", "a-path"],
)
def test_an_ambiguous_name_used_as_a_repository_is_a_finding(tmp_path: Path, line):
    root = repo_at(tmp_path, {"f.txt": line + "\n"})
    assert any(h["certain"] for h in occurrences(root, {"blorpling"}))


def test_a_name_equal_to_the_org_is_excluded(tmp_path: Path, monkeypatch):
    """Redacting it would redact the organisation, which is public by
    construction and in every URL in the tree."""
    source = tmp_path / "inventory-private.json"
    source.write_text(json.dumps({"references": {"private-08": "acme-org"}}), encoding="utf-8")
    monkeypatch.setattr("check_private_names.SOURCES", (source,))
    monkeypatch.setattr("check_private_names.ORG", "acme-org")
    assert private_names((source,)) == set()


def test_the_references_mapping_reads_both_companion_shapes(tmp_path: Path):
    """inventory-private.json stores ref -> name; the roster companion stores
    entries carrying both. Reading only the second knew 2 names of 34."""
    inv = tmp_path / "inventory-private.json"
    inv.write_text(json.dumps({"references": {"private-01": "from-json"}}), encoding="utf-8")
    ws = tmp_path / "workspace-private.yaml"
    ws.write_text(yaml.safe_dump(
        {"repositories": [{"ref": "private-02", "name": "from-yaml"}]}), encoding="utf-8")
    assert references((inv, ws)) == {"from-json": "private-01", "from-yaml": "private-02"}


def test_an_occurrence_is_redacted_before_it_is_returned(tmp_path: Path, monkeypatch):
    """Surfacing a leak by quoting it is the mistake this check exists to stop."""
    ws = tmp_path / "workspace-private.yaml"
    ws.write_text(yaml.safe_dump(
        {"repositories": [{"ref": "private-77", "name": SECRET}]}), encoding="utf-8")
    monkeypatch.setattr("check_private_names.SOURCES", (ws,))
    root = repo_at(tmp_path / "tree", {"page.md": f"url = https://x/{SECRET}.git\n"})
    hits = occurrences(root, {SECRET})
    assert hits and all(SECRET not in h["text"] for h in hits)
    assert "<private-77>" in hits[0]["text"]


def test_a_host_failure_is_none_rather_than_an_empty_set(monkeypatch):
    """An empty set means `no private repositories exist`, which reads as clean
    and is the most flattering possible wrong answer."""
    from check_private_names import host_names

    class Failed:
        returncode = 1
        stdout = ""

    monkeypatch.setattr("check_private_names.subprocess.run", lambda *a, **k: Failed())
    assert host_names("acme") is None


def test_private_names_reads_the_references_shape(tmp_path: Path):
    """inventory-private.json stores ref -> name under `references`, not under
    `repositories`. Reading only the latter knew 2 of 34 names, and every
    `clean` it reported meant `the roster's two names are absent`."""
    path = tmp_path / "inventory-private.json"
    path.write_text(json.dumps({"references": {"private-01": "hidden-repo"}}),
                    encoding="utf-8")
    assert private_names((path,)) == {"hidden-repo"}


def test_a_host_failure_with_output_is_still_none(monkeypatch):
    """A non-zero exit that also printed something must not be parsed. gh
    writes usage text on failure, and treating that as a repository list would
    hand the scan a set of nonsense names and call the result clean."""
    from check_private_names import host_names

    class Failed:
        returncode = 1
        stdout = "usage: gh api <endpoint>\n"

    monkeypatch.setattr("check_private_names.subprocess.run", lambda *a, **k: Failed())
    assert host_names("acme") is None
