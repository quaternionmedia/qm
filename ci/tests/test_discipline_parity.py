"""The parity check, and the live files it guards.

Two kinds of test here, and both matter. The first group builds synthetic files
and asserts the check's own behaviour -- that it fails on a rule present in one
file and absent from the other, which is the state it exists to catch. The
second asserts the property against the repository as it actually stands, so
this fails when someone edits a real AGENTS.md rather than only when someone
edits the checker.

Written after a session in which a rule the author personally broke turned out
to live only in an optional vendor adapter, and so reached no fork at all.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

CI_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = CI_DIR.parent
sys.path.insert(0, str(CI_DIR))

from check_discipline_parity import (  # noqa: E402
    CORPUS_AGENTS,
    SEED_AGENTS,
    SHARED_ANCHORS,
    main,
    missing_anchors,
)


def _write_pair(root: Path, corpus_text: str, seed_text: str) -> None:
    (root / CORPUS_AGENTS).write_text(corpus_text, encoding="utf-8")
    seed = root / SEED_AGENTS
    seed.parent.mkdir(parents=True, exist_ok=True)
    seed.write_text(seed_text, encoding="utf-8")


def _all_rules() -> str:
    return "\n".join(f"- {anchor}" for anchor in SHARED_ANCHORS)


def test_both_files_carrying_every_rule_passes(tmp_path: Path) -> None:
    _write_pair(tmp_path, _all_rules(), _all_rules())
    assert main(["--root", str(tmp_path)]) == 0


def test_a_rule_missing_from_the_seed_fails(tmp_path: Path) -> None:
    """The state this check exists for: added here, never shipped to a fork."""
    dropped = SHARED_ANCHORS[-1]
    seed = "\n".join(f"- {a}" for a in SHARED_ANCHORS if a != dropped)
    _write_pair(tmp_path, _all_rules(), seed)
    assert main(["--root", str(tmp_path)]) == 1


def test_a_rule_missing_from_the_corpus_fails(tmp_path: Path) -> None:
    """The reverse also fails -- the seed is not the junior copy."""
    dropped = SHARED_ANCHORS[0]
    corpus = "\n".join(f"- {a}" for a in SHARED_ANCHORS if a != dropped)
    _write_pair(tmp_path, corpus, _all_rules())
    assert main(["--root", str(tmp_path)]) == 1


def test_a_missing_file_fails_rather_than_reporting_clean(tmp_path: Path) -> None:
    """An absent file must not read as an absent violation.

    A check that passes when it cannot find its subject is the shape this
    corpus keeps finding in its own tooling.
    """
    (tmp_path / CORPUS_AGENTS).write_text(_all_rules(), encoding="utf-8")
    assert main(["--root", str(tmp_path)]) == 1


def test_matching_is_case_insensitive() -> None:
    """One file opens a rule as a sentence, the other states it mid-clause."""
    assert missing_anchors("NEVER THROUGH A PIPE", ["never through a pipe"]) == []


def test_a_line_break_inside_an_anchor_still_matches() -> None:
    """Both files wrap prose, and they wrap in different places.

    The first run of this check reported a rule missing from the seed when the
    seed carried it across a line break -- a finding about column widths
    wearing the costume of a finding about governance.
    """
    wrapped = "and check a signal before reading\n   it.**"
    assert missing_anchors(wrapped, ["a signal before reading it"]) == []


@pytest.mark.parametrize("relative", [CORPUS_AGENTS, SEED_AGENTS])
def test_the_live_file_carries_every_shared_rule(relative: str) -> None:
    """Against the repository, not a fixture.

    Without this the suite only fails when someone edits the checker, and the
    thing being guarded is the two documents.
    """
    path = REPO_ROOT / relative
    assert path.is_file(), f"{relative} not found at {path}"
    missing = missing_anchors(path.read_text(encoding="utf-8"), SHARED_ANCHORS)
    assert not missing, f"{relative} is missing: {missing}"
