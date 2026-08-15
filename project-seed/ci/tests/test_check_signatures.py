"""Tests for the commit-signature check.

Real repositories, real commits, and no real key: signing is simulated by
`gpg.format=ssh` with a throwaway key where the platform allows it, and every
other case is driven through `judge()` with the statuses git reports. That split
is deliberate -- the range logic and the verdict table are what break, and both
are testable without a keyring.

Exit status is the contract. A signature check that prints the right paragraph
and returns 0 attests nothing.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from conftest import commit_all, git, run_tool, write

from importlib import import_module
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
judge = import_module("check_signatures").judge
commits_in_range = import_module("check_signatures").commits_in_range


def check(repo: Path, *args: str):
    return run_tool("check_signatures.py", *args, cwd=repo)


# --- the verdict table ------------------------------------------------------


@pytest.mark.parametrize("status", ["G", "U", "X", "Y", "R"])
def test_a_signature_present_passes(status: str):
    """`U` is the ordinary state on any runner without the signer's key.

    Failing it would fail every correctly-signed commit on the one machine that
    matters, which is how a signature check gets switched off.
    """
    assert judge([("abc", status, "subject")], allow_untrusted=True) == []


@pytest.mark.parametrize("status", ["N", "E", "B"])
def test_an_absent_bad_or_uncheckable_signature_fails(status: str):
    assert len(judge([("abc", status, "subject")], allow_untrusted=True)) == 1


def test_untrusted_can_be_refused_explicitly():
    assert len(judge([("abc", "U", "s")], allow_untrusted=False)) == 1


def test_a_bad_signature_fails_even_when_untrusted_is_allowed():
    """`B` is a signature that does not verify. That is worse than none."""
    assert len(judge([("abc", "B", "s")], allow_untrusted=True)) == 1


def test_a_mixed_range_reports_only_the_failures():
    rows = [("a", "G", "s"), ("b", "N", "s"), ("c", "G", "s"), ("d", "N", "s")]
    assert [r[0] for r in judge(rows, allow_untrusted=True)] == ["b", "d"]


# --- the range --------------------------------------------------------------


def test_only_the_commits_the_branch_adds_are_checked(repo: Path):
    """Inherited history is not the branch author's to re-sign.

    Every commit in this fixture is unsigned. If the check read whole history
    it would fail a branch that added nothing, which is a gate nobody can
    satisfy.
    """
    base = git(repo, "rev-parse", "HEAD")
    git(repo, "checkout", "-q", "-b", "evolve/thing")
    rows, problem = commits_in_range(base, "HEAD", cwd=str(repo))
    assert problem is None
    assert rows == []


def test_a_branch_that_adds_only_merges_has_nothing_to_attest(repo: Path):
    """A merge carries the signature of whoever pressed the button."""
    base = git(repo, "rev-parse", "HEAD")
    git(repo, "checkout", "-q", "-b", "side")
    write(repo / "s.md", "x\n")
    commit_all(repo, "side work")
    git(repo, "checkout", "-q", "main")
    git(repo, "merge", "-q", "--no-ff", "--no-edit", "side")
    rows, _ = commits_in_range(f"{base}", "HEAD", cwd=str(repo))
    assert all("Merge" not in subject for _, _, subject in rows)


def test_an_unreadable_range_is_a_failure_not_a_pass(repo: Path):
    result = check(repo, "--base-ref", "refs/heads/nope", "--head-ref", "HEAD")
    assert result.returncode == 1
    assert "could not read" in result.stdout + result.stderr


def test_a_range_that_adds_nothing_passes_and_says_so(repo: Path):
    base = git(repo, "rev-parse", "HEAD")
    result = check(repo, "--base-ref", base, "--head-ref", "HEAD")
    assert result.returncode == 0
    assert "nothing to check" in result.stdout


# --- the entry point --------------------------------------------------------


def test_unsigned_commits_fail_the_branch(repo: Path):
    """The fixture signs nothing, which is the case this check exists for."""
    base = git(repo, "rev-parse", "HEAD")
    git(repo, "checkout", "-q", "-b", "evolve/thing")
    write(repo / "a.md", "x\n")
    commit_all(repo, "unsigned work")

    result = check(repo, "--base-ref", base, "--head-ref", "HEAD")
    assert result.returncode == 1
    assert "no signature" in result.stdout


def test_the_failure_names_the_act_it_exists_for(repo: Path):
    """Disabling signing is the cheapest way to make this pass, so it is named."""
    base = git(repo, "rev-parse", "HEAD")
    git(repo, "checkout", "-q", "-b", "evolve/thing")
    write(repo / "a.md", "x\n")
    commit_all(repo, "unsigned work")

    result = check(repo, "--base-ref", base, "--head-ref", "HEAD")
    assert "Do not disable signing" in result.stderr


def test_base_ref_is_required(repo: Path):
    """Defaulting it would let the check run over a range nobody chose."""
    assert check(repo, "--head-ref", "HEAD").returncode != 0
