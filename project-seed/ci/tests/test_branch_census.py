"""What a branch census must tell apart before anybody deletes anything.

Real repositories with a real remote, never a mock. Everything this tool
reports is a fact about refs, and the two errors it exists to avoid are beliefs
about git: that a branch ahead by zero commits holds nothing, and that a branch
ahead by one holds something. A mock encodes whichever belief its author had.

Two branches can each carry a single unpushed commit of the same age and be
identical in every count `rev-list` produces, while one has already landed by
another route and the other is work on one disk.
`test_a_cherry_picked_branch_is_not_counted_as_loss` and
`test_a_branch_with_its_own_work_is_counted_as_loss` are those two.

The mutations, per `a-check-is-evidence-after-it-fails`, quoted as they printed:

  `unique_commits` counting every cherry line instead of only the `+` ones

    AssertionError: a branch whose patch is already upstream was reported as
    loss
    assert 1 == 0

  `origin/HEAD` not skipped

    AssertionError: 'HEAD' should not be reported as a branch
    assert 'HEAD' not in {'HEAD': Branch(name='HEAD', kind='merged', ...)}

  the gate counting branches rather than branches with unique work

    AssertionError:   LOCAL -- never pushed; deleting the clone deletes the work
    assert 1 == 0

  the unpushed count ignored, so a stranded branch reads as ordinary

    AssertionError: assert 'ahead' == 'stranded'

With author and committer dates pinned by the fixture environment,
`git cherry-pick` of a tip onto its own parent reproduces the original sha, so
the branch would become an ancestor of `main` and the assertions would hold
vacuously. Both cherry-pick tests amend the message after picking: same patch,
different commit, which is the state being tested.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

CI_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(CI_DIR))

import branch_census as bc  # noqa: E402

from conftest import ENV, git, write  # noqa: E402


def commit(repo: Path, name: str, text: str) -> str:
    write(repo / name, text)
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", f"add {name}")
    return git(repo, "rev-parse", "HEAD")


@pytest.fixture
def pair(tmp_path: Path):
    """A bare remote and a clone of it, which is what CI and a laptop have.

    The seed suite's shared `repo` fixture points `origin` at itself, so it has
    no `refs/remotes/origin/*` to read. Everything here is about the difference
    between a local ref and its remote, so that fixture cannot be reused.
    """
    upstream = tmp_path / "upstream.git"
    work = tmp_path / "work"
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(upstream)],
                   check=True, env=ENV)
    subprocess.run(["git", "clone", "-q", str(upstream), str(work)],
                   check=True, env=ENV)
    git(work, "config", "user.email", "t@example.invalid")
    git(work, "config", "user.name", "Test")
    commit(work, "README.md", "start\n")
    git(work, "push", "-q", "origin", "main")
    return work


def census(repo: Path) -> dict[str, bc.Branch]:
    return {b.name: b for b in bc.census(str(repo))}


# --- the two that look identical to a commit count --------------------------


def test_a_cherry_picked_branch_is_not_counted_as_loss(pair):
    """A branch whose commit was applied to `main` under a different sha is
    ahead by one and holds nothing. Reported as loss, it teaches a reader that
    the census cries wolf.
    """
    git(pair, "checkout", "-q", "-b", "picked")
    tip = commit(pair, "feature.txt", "work\n")
    git(pair, "checkout", "-q", "main")
    git(pair, "cherry-pick", tip)
    # The sha must differ and the patch must not: with the fixture's pinned
    # dates, a cherry-pick of the tip onto its own parent reproduces the
    # original sha and the test would assert nothing. Amending the message
    # changes the commit and leaves the patch identical.
    git(pair, "commit", "-q", "--amend", "-m", "landed by another route")
    git(pair, "push", "-q", "origin", "main")

    branch = census(pair)["picked"]

    assert branch.kind == bc.LOCAL
    assert branch.ahead == 1, "it is genuinely ahead by one commit"
    assert branch.unique == 0, (
        "a branch whose patch is already upstream was reported as loss")
    assert "nothing unique" in "; ".join(branch.notes)


def test_a_branch_with_its_own_work_is_counted_as_loss(pair):
    git(pair, "checkout", "-q", "-b", "mine")
    commit(pair, "only-here.txt", "work nobody else has\n")
    git(pair, "checkout", "-q", "main")

    branch = census(pair)["mine"]

    assert branch.kind == bc.LOCAL
    assert branch.unique == 1
    assert "not upstream by patch" in "; ".join(branch.notes)


# --- the class a merged-branch listing cannot see ---------------------------


def test_a_pushed_branch_with_newer_local_commits_is_stranded(pair):
    """A remote ref fully merged into `main`, which `git branch -r --merged`
    lists as safe to delete, while the clone holds commits nobody else can
    fetch.
    """
    git(pair, "checkout", "-q", "-b", "shared")
    commit(pair, "shared.txt", "pushed\n")
    git(pair, "push", "-q", "-u", "origin", "shared")
    commit(pair, "later.txt", "only on this disk\n")
    git(pair, "checkout", "-q", "main")

    branch = census(pair)["shared"]

    assert branch.kind == bc.STRANDED
    assert branch.unpushed == 1
    assert branch.unique >= 1
    assert "not on origin" in "; ".join(branch.notes)


def test_a_fully_merged_remote_branch_holds_nothing(pair):
    git(pair, "checkout", "-q", "-b", "landed")
    commit(pair, "landed.txt", "work\n")
    git(pair, "push", "-q", "-u", "origin", "landed")
    git(pair, "checkout", "-q", "main")
    git(pair, "merge", "-q", "--no-ff", "-m", "merge landed", "landed")
    git(pair, "push", "-q", "origin", "main")
    git(pair, "fetch", "-q", "origin")

    branch = census(pair)["landed"]

    assert branch.kind == bc.MERGED
    assert branch.ahead == 0


def test_the_default_branch_is_not_reported_as_a_branch(pair):
    """It is the thing everything else is measured against."""
    assert "main" not in census(pair)


def test_the_remote_head_pointer_is_not_reported_as_a_branch(pair):
    """`origin/HEAD` is a symbolic ref. Counted, it duplicates the default
    branch under a name nobody pushed and nobody can delete."""
    git(pair, "remote", "set-head", "origin", "main")
    assert "HEAD" not in census(pair), (
        "'HEAD' should not be reported as a branch")


# --- what the exit status promises ------------------------------------------


def run(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(CI_DIR / "branch_census.py"), "--repo", str(repo),
         *args],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        env=ENV)


def test_the_gate_fires_only_on_work_that_would_be_lost(pair):
    """A branch that is unpushed and patch-equivalent must not fail the gate.

    This is the summary line's contract as well as the exit code's: counting
    branches rather than branches-with-unique-work turns every stale local
    branch into a red run.
    """
    git(pair, "checkout", "-q", "-b", "picked")
    tip = commit(pair, "feature.txt", "work\n")
    git(pair, "checkout", "-q", "main")
    git(pair, "cherry-pick", tip)
    # The sha must differ and the patch must not: see the cherry-pick test
    # above.
    git(pair, "commit", "-q", "--amend", "-m", "landed by another route")
    git(pair, "push", "-q", "origin", "main")

    clean = run(pair, "--fail-on-stranded")
    assert clean.returncode == 0, clean.stdout + clean.stderr
    assert "Nothing unique is held only in this clone" in clean.stdout

    git(pair, "checkout", "-q", "-b", "mine")
    commit(pair, "only-here.txt", "real work\n")
    git(pair, "checkout", "-q", "main")

    dirty = run(pair, "--fail-on-stranded")
    assert dirty.returncode == 1
    assert "mine" in dirty.stderr
    assert "picked" not in dirty.stderr


def test_the_census_never_takes_a_delete_flag():
    """A census that can also destroy is one somebody runs in a hurry.

    Asserted against the parser rather than the docstring, because a promise
    in prose is not a promise.
    """
    refused = run(Path("."), "--delete")
    assert refused.returncode != 0
    assert "unrecognized arguments" in refused.stderr


def test_automation_branches_are_summarised_rather_than_listed(pair):
    """Dependabot rows, one per branch, would push the branches a person must
    decide about off the top of a terminal."""
    for n in range(3):
        git(pair, "checkout", "-q", "-b", f"dependabot/uv/thing-{n}")
        commit(pair, f"bot{n}.txt", "bump\n")
    git(pair, "checkout", "-q", "main")

    text = bc.render(list(bc.census(str(pair))))

    assert "3 automation branch(es), not listed" in text
    assert "dependabot/uv/thing-0" not in text


def test_a_repository_with_only_a_default_branch_says_so(pair):
    assert "No branches besides the default" in bc.render(
        list(bc.census(str(pair))))
