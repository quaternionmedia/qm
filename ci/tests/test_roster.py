"""The roster loader, and the `name` guarantee every consumer depends on.

`ci/workspace.yaml` carries a private repository as a bare `ref`. Four
generators read `entry["name"]` directly, so the redaction broke all of them at
once -- and a KeyError was the lucky outcome. The unlucky one is a consumer
reading `entry.get("name")` and writing `None` into a committed document.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

CI_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(CI_DIR))

from roster import label, load, merge_private  # noqa: E402
from roster import redact  # noqa: E402

PUBLIC = [
    {"name": "alfred", "role": "project", "paths": ["qm/alfred"]},
    {"ref": "private-32", "role": "project"},
]

COMPANION = {
    "repositories": [
        {"ref": "private-32", "name": "a-private-repo", "paths": ["qm/a-private-repo"]}
    ]
}


def companion_at(tmp_path: Path, data=COMPANION) -> Path:
    path = tmp_path / "workspace-private.yaml"
    path.write_text(yaml.safe_dump(data), encoding="utf-8")
    return path


# --- the guarantee ----------------------------------------------------------


def test_every_entry_has_a_name_with_the_companion(tmp_path: Path):
    merged = merge_private(PUBLIC, companion_at(tmp_path))
    assert all(e["name"] for e in merged)
    assert merged[1]["name"] == "a-private-repo"


def test_every_entry_has_a_name_without_the_companion(tmp_path: Path):
    """A fresh clone, another machine, and every CI runner. `name` is the ref."""
    merged = merge_private(PUBLIC, tmp_path / "absent.yaml")
    assert all(e["name"] for e in merged)
    assert merged[1]["name"] == "private-32"


def test_a_consumer_reading_name_directly_does_not_raise(tmp_path: Path):
    """The failure this exists to stop: four generators read entry["name"]."""
    for companion in (companion_at(tmp_path), tmp_path / "absent.yaml"):
        for entry in merge_private(PUBLIC, companion):
            assert entry["name"]  # not a KeyError, and not None


def test_no_entry_is_dropped(tmp_path: Path):
    """A roster silently two short reads exactly like a roster of everything."""
    assert len(merge_private(PUBLIC, tmp_path / "absent.yaml")) == len(PUBLIC)


def test_paths_arrive_only_from_the_companion(tmp_path: Path):
    """The committed roster must not carry a private repository's paths either:
    a path is a directory name, and a directory name is the repository name."""
    without = merge_private(PUBLIC, tmp_path / "absent.yaml")
    assert not without[1].get("paths")
    with_it = merge_private(PUBLIC, companion_at(tmp_path))
    assert with_it[1]["paths"] == ["qm/a-private-repo"]


def test_a_public_entry_is_untouched_by_the_companion(tmp_path: Path):
    merged = merge_private(PUBLIC, companion_at(tmp_path))
    assert merged[0] == PUBLIC[0]


def test_a_companion_ref_matching_nothing_is_ignored(tmp_path: Path):
    path = companion_at(tmp_path, {"repositories": [{"ref": "private-99", "name": "x"}]})
    merged = merge_private(PUBLIC, path)
    assert merged[1]["name"] == "private-32"


def test_an_empty_companion_does_not_erase_the_roster(tmp_path: Path):
    path = companion_at(tmp_path, {"repositories": []})
    assert len(merge_private(PUBLIC, path)) == len(PUBLIC)


# --- labelling --------------------------------------------------------------


@pytest.mark.parametrize(
    "entry, expected",
    [
        ({"name": "alfred"}, "alfred"),
        ({"ref": "private-32"}, "private-32"),
        ({"name": "alfred", "ref": "private-32"}, "alfred"),
        ({}, "<unnamed>"),
    ],
    ids=["public", "private", "both-prefers-name", "neither"],
)
def test_label_never_raises(entry, expected):
    assert label(entry) == expected


# --- the committed roster itself -------------------------------------------


def test_the_committed_roster_names_no_private_repository():
    """The regression. Two names sat here from 2b50bd6 while
    status/inventory.yaml redacted the same two repositories."""
    document = yaml.safe_load((CI_DIR / "workspace.yaml").read_text(encoding="utf-8"))
    for entry in document["repositories"]:
        if entry.get("ref", "").startswith("private-"):
            assert "name" not in entry, (
                f"{entry['ref']} carries a name in the committed roster"
            )
            assert "paths" not in entry, (
                f"{entry['ref']} carries paths, and a path is a directory name"
            )


def test_the_real_roster_loads_and_every_entry_is_named():
    for entry in load():
        assert entry.get("name")


class _Wrapper:
    """Stands in for a generator's `Unknown(reason)`, without importing it."""

    __slots__ = ("reason",)

    def __init__(self, reason: str) -> None:
        self.reason = reason


def test_redact_reaches_a_string_inside_a_wrapper():
    """**THE HOLE THAT WENT THROUGH ONCE.**

    `redact` walks dicts, lists and strings, so a value of any other type fell
    out of the bottom untouched. A generator grew a wrapper for facts it could
    not establish, its reason interpolated a repository name, and two private
    names reached a committed generated document while every field the redactor
    knew about was clean.

    Mutation: delete the attribute loop from `redact` and this fails.
    """
    entry = {"name": "secret", "records_dir": _Wrapper("secret has no workflow to read")}
    out = redact(entry, "secret", "private-99")
    assert out["name"] == "private-99"
    assert out["records_dir"].reason == "private-99 has no workflow to read"


def test_redact_leaves_a_wrapper_with_no_string_alone():
    """A value that carries no redactable string is returned as it was, rather
    than being mangled into one."""
    marker = object()
    assert redact(marker, "secret", "private-99") is marker
