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
