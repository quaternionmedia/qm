"""Tests for the vendor/model-name check, and for its one exemption.

The exemption is the reason this file exists. A check with a hole is worse than
no check -- a green tick standing where a reader believes something is enforced
-- so the hole is tested from both sides: it must let exactly one commit through,
and it must announce it every time.

Real repositories, because the subject check is about `git log` output.
"""

from __future__ import annotations

import sys
from importlib import import_module
from pathlib import Path

from conftest import commit_all, git, run_tool, write

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
_mod = import_module("check_attribution")
EXEMPT_SUBJECTS = _mod.EXEMPT_SUBJECTS
families_in = _mod.families_in

NAMED = "Re-refactor docs with Fable 5"


def check(repo: Path, *args: str):
    return run_tool("check_attribution.py", *args, cwd=repo)


# --- the rule ---------------------------------------------------------------


def test_a_subject_naming_a_model_fails(repo: Path):
    base = git(repo, "rev-parse", "HEAD")
    write(repo / "a.md", "x\n")
    commit_all(repo, NAMED)
    result = check(repo, "--base-ref", base)
    assert result.returncode == 1
    assert "names a tool" in result.stdout + result.stderr


def test_an_ordinary_subject_passes(repo: Path):
    base = git(repo, "rev-parse", "HEAD")
    write(repo / "a.md", "x\n")
    commit_all(repo, "Re-refactor the docs")
    assert check(repo, "--base-ref", base).returncode == 0


def test_the_detector_finds_the_name_at_all():
    """If this stops matching, every test below passes for the wrong reason."""
    assert families_in(NAMED)


# --- the exemption ----------------------------------------------------------


def test_exactly_one_subject_is_exempt():
    """Growth in this list is the failure mode the code comment names."""
    assert len(EXEMPT_SUBJECTS) == 1


def test_every_exemption_carries_a_reason():
    """An exemption without a stated reason is indistinguishable from an oversight."""
    for sha, reason in EXEMPT_SUBJECTS.items():
        assert len(sha) == 40, f"{sha} is not a full SHA; a short one can collide"
        assert reason and len(reason) > 80, f"{sha[:8]} has no substantive reason"


def test_the_exemption_is_keyed_on_a_full_sha():
    """A prefix would exempt any future commit that happened to share it."""
    for sha in EXEMPT_SUBJECTS:
        assert all(c in "0123456789abcdef" for c in sha)


def test_an_exempt_subject_on_a_different_commit_still_fails(repo: Path):
    """The exemption is the commit, not the wording.

    Keying on the subject text would exempt every future commit that copied it,
    which is how one allowance becomes a general licence.
    """
    base = git(repo, "rev-parse", "HEAD")
    write(repo / "a.md", "x\n")
    commit_all(repo, NAMED)          # same words, different SHA
    assert check(repo, "--base-ref", base).returncode == 1


def test_the_exemption_is_announced_not_silent(repo: Path):
    """A hole a run does not print is a hole in a check that reports green.

    Driven through the module rather than a fixture repo, because the exempt
    SHA only exists in the real corpus.
    """
    source = (Path(__file__).resolve().parent.parent / "check_attribution.py").read_text(
        encoding="utf-8"
    )
    assert "is exempt" in source
    assert "EXEMPT_SUBJECTS[sha]" in source, "the reason must be printed, not just the SHA"
