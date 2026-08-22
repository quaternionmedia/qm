"""Tests for the commit-signature check.

The verdict table and the cutoff are driven through `judge()` with the statuses
git reports, because those are what break and neither needs a keyring. The range
logic runs against real repositories, because it is about git and a mock of git
would encode the same misunderstanding the tool does and then agree with it.

Exit status is the contract. A signature check that prints the right paragraph
and returns 0 attests nothing.
"""

from __future__ import annotations

import re
import sys
from importlib import import_module
from pathlib import Path

import pytest

from conftest import commit_all, git, run_tool, write

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
_mod = import_module("check_signatures")
judge = _mod.judge
commits_in_range = _mod.commits_in_range

TODAY = "2026-09-01"      # after any cutoff these tests set
LONG_AGO = "2020-01-01"


def check(repo: Path, *args: str):
    return run_tool("check_signatures.py", *args, cwd=repo)


def row(status: str, when: str = TODAY, sha: str = "abc", subject: str = "s"):
    return (sha, status, when, subject)


# --- the verdict table ------------------------------------------------------


@pytest.mark.parametrize("status", ["G", "U", "X", "Y", "R"])
def test_a_signature_present_passes(status: str):
    """`U` is the ordinary state on any runner without the signer's key.

    Failing it would fail every correctly-signed commit on the one machine that
    matters, which is how a signature check gets switched off.
    """
    assert judge([row(status)], allow_untrusted=True) == ([], [])


@pytest.mark.parametrize("status", ["N", "E", "B"])
def test_an_absent_bad_or_uncheckable_signature_fails(status: str):
    failing, _ = judge([row(status)], allow_untrusted=True)
    assert len(failing) == 1


def test_untrusted_can_be_refused_explicitly():
    failing, _ = judge([row("U")], allow_untrusted=False)
    assert len(failing) == 1


def test_a_bad_signature_fails_even_when_untrusted_is_allowed():
    """`B` is a signature that does not verify. That is worse than none."""
    failing, _ = judge([row("B")], allow_untrusted=True)
    assert len(failing) == 1


def test_a_mixed_range_reports_only_the_failures():
    rows = [row("G", sha="a"), row("N", sha="b"), row("G", sha="c"), row("N", sha="d")]
    failing, _ = judge(rows, allow_untrusted=True)
    assert [r[0] for r in failing] == ["b", "d"]


# --- the cutoff -------------------------------------------------------------


def test_an_unsigned_commit_before_the_cutoff_is_debt_not_failure():
    """History is not rewritten here, so a gate whose only remedy is a rewrite
    would be switched off within a week."""
    failing, grandfathered = judge([row("N", when=LONG_AGO)], allow_untrusted=True)
    assert failing == []
    assert len(grandfathered) == 1


def test_an_unsigned_commit_after_the_cutoff_fails():
    failing, grandfathered = judge([row("N", when=TODAY)], allow_untrusted=True)
    assert len(failing) == 1
    assert grandfathered == []


def test_a_signed_commit_before_the_cutoff_is_neither_failing_nor_debt():
    """The cutoff exempts unsigned history; it does not reclassify good work."""
    assert judge([row("G", when=LONG_AGO)], allow_untrusted=True) == ([], [])


def test_the_cutoff_is_a_parameter_so_moving_it_is_reviewable():
    rows = [row("N", when="2026-08-14")]
    assert judge(rows, allow_untrusted=True, enforced_from="2026-08-01")[0]
    assert judge(rows, allow_untrusted=True, enforced_from="2026-09-01")[1]


def test_debt_never_reads_as_a_signed_commit(repo: Path):
    """A summary saying "all N carry a signature" when some do not would be the
    check reporting success while attesting nothing."""
    base = git(repo, "rev-parse", "HEAD")
    git(repo, "checkout", "-q", "-b", "evolve/thing")
    write(repo / "a.md", "x\n")
    commit_all(repo, "unsigned work")

    result = check(repo, "--base-ref", base, "--head-ref", "HEAD",
                   "--enforced-from", "2099-01-01")
    assert result.returncode == 0
    assert "All 1 commit(s) carry a signature" not in result.stdout
    assert "0 of 1 commit(s) carry a signature" in result.stdout
    assert "does not go down" in result.stderr


# --- the range --------------------------------------------------------------


def test_only_the_commits_the_branch_adds_are_checked(repo: Path):
    """Inherited history is not the branch author's to re-sign."""
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
    rows, _ = commits_in_range(base, "HEAD", cwd=str(repo))
    assert all("Merge" not in r[3] for r in rows)


def test_every_row_carries_a_commit_date(repo: Path):
    """The cutoff needs it; a row without one would be exempted or failed at random."""
    base = git(repo, "rev-parse", "HEAD")
    git(repo, "checkout", "-q", "-b", "evolve/thing")
    write(repo / "a.md", "x\n")
    commit_all(repo, "work")
    rows, _ = commits_in_range(base, "HEAD", cwd=str(repo))
    assert len(rows) == 1
    assert re.match(r"^\d{4}-\d{2}-\d{2}T", rows[0][2]), rows[0]


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


def test_unsigned_commits_after_the_cutoff_fail_the_branch(repo: Path):
    base = git(repo, "rev-parse", "HEAD")
    git(repo, "checkout", "-q", "-b", "evolve/thing")
    write(repo / "a.md", "x\n")
    commit_all(repo, "unsigned work")

    result = check(repo, "--base-ref", base, "--head-ref", "HEAD",
                   "--enforced-from", "2000-01-01")
    assert result.returncode == 1
    assert "no signature" in result.stdout


def test_the_failure_names_the_act_it_exists_for(repo: Path):
    """Disabling signing is the cheapest way to make this pass, so it is named."""
    base = git(repo, "rev-parse", "HEAD")
    git(repo, "checkout", "-q", "-b", "evolve/thing")
    write(repo / "a.md", "x\n")
    commit_all(repo, "unsigned work")

    result = check(repo, "--base-ref", base, "--head-ref", "HEAD",
                   "--enforced-from", "2000-01-01")
    assert "Do not disable signing" in result.stderr


def test_base_ref_is_required(repo: Path):
    """Defaulting it would let the check run over a range nobody chose."""
    assert check(repo, "--head-ref", "HEAD").returncode != 0
