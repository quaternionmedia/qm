"""Two tools answer one question, and they must answer it the same way.

`uv run qm devloop` and `uv run qm workspace` both report how many roster
repositories are on this disk. They disagreed: devloop said 34 of 34 while the
workspace said 33 of 34 and named the one it could not find.

Neither was reading the other wrong. devloop read the *committed* roster, where
a private entry carries a `ref` and no `name`, and its missing-check began
`if not name: continue` -- so every private entry fell out of the denominator's
missing side and could never be reported absent. The workspace resolved the
same roster through `roster.merge_private`, so it knew the name, looked, and
found nothing.

`records/DRAFT-a-disagreement-is-a-delta.md` says a disagreement between two
views is a delta rather than an error. That is right when both views are
honest. This one was a defect in one of them, and the way to tell the
difference is to have something compare them -- which is what this file is.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

CI_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(CI_DIR))

import devloop  # noqa: E402
import roster  # noqa: E402


def test_a_private_roster_entry_is_counted_as_missing_when_it_is_not_on_disk():
    """**THE DEFECT, AT THE SMALLEST SCALE THAT SHOWS IT.**

    An entry with no `name` is unresolved, not absent from the question. The
    old code skipped it, so a roster of one private repository that was nowhere
    on the disk reported nothing missing.

    Mutation: restore `if not name or name in found: continue` and this fails.
    """
    entries = [{"ref": "private-99", "paths": []}]
    result = devloop.checkout({"repositories": []}, entries, [], deep=False)
    assert result["missing_from_disk"], "a nameless entry was dropped from the count"
    assert result["roster_cloned_here"] == 0


def test_a_nameless_entry_is_never_named_in_the_output():
    """Counting it must not print it. The reference is what may be shown."""
    entries = [{"ref": "private-99", "paths": []}]
    result = devloop.checkout({"repositories": []}, entries, [], deep=False)
    assert "private-99" in " ".join(result["missing_from_disk"])


def test_both_views_load_the_roster_through_the_same_loader():
    """The durable form of the fix.

    Comparing the two rendered numbers would need both tools run against one
    disk, which is a slow test that says different things on different
    machines. Asserting they share a loader is the property that made them
    agree, and it fails the moment one of them grows its own again.
    """
    source = (CI_DIR / "devloop.py").read_text(encoding="utf-8")
    workspace = (CI_DIR / "make_workspace.py").read_text(encoding="utf-8")
    assert "from roster import" in source, "devloop stopped using the shared loader"
    assert "from roster import" in workspace, "make_workspace stopped using it"
    # And devloop must not go back to reading the committed file directly for
    # the roster it counts, which is precisely how the two came apart.
    assert 'load_yaml(WORKSPACE).get("repositories")' not in source


@pytest.mark.parametrize("entry,expected", [
    ({"name": "public-thing"}, "public-thing"),
    ({"ref": "private-99"}, "private-99"),
    ({}, "<unnamed>"),
])
def test_label_answers_for_both_shapes(entry, expected):
    """`roster.label` is the reason a nameless entry can be counted at all."""
    assert roster.label(entry) == expected
