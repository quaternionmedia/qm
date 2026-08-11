"""The PR provenance check, which exists because a branch is not its base.

The failure it was written for: a branch cut from a feature branch rather than
the base carries that branch's work, passes every content check, and arrives
under a title describing something much smaller. One such PR sat open with 20
commits and 46 files under a title describing a single CI check.

The tests below matter more than usual for one reason. This tool's own ref
qualifier was inverted -- it asked whether `base.split('/')[0]` contains a
slash, which the first segment of a split on slash never does, so every ref was
prefixed and `--base origin/main` resolved `origin/origin/main`. It went
unnoticed because every invocation happened to pass a bare name.
"""

from __future__ import annotations

from pathlib import Path

from conftest import commit_all, git, run_tool, write


def check(repo: Path, base: str, head: str, *extra: str):
    return run_tool(
        "check_pr_base.py", "--base", base, "--head", head, *extra, cwd=repo
    )


def _branch_with_commit(repo: Path, name: str, filename: str, from_ref: str = "main") -> None:
    git(repo, "checkout", "-q", "-b", name, from_ref)
    write(repo / filename, f"{filename}\n")
    commit_all(repo, f"work on {name}")
    git(repo, "checkout", "-q", "main")


def _publish(repo: Path) -> None:
    """Mirror local branches to `origin`, which for this fixture is the repo itself."""
    git(repo, "push", "-q", "--all", "origin")


def test_a_branch_cut_from_the_base_is_clean(repo: Path):
    _branch_with_commit(repo, "feature", "a.txt")
    _publish(repo)
    result = check(repo, "main", "feature")
    assert result.returncode == 0, result.stdout
    assert "== base tip" in result.stdout
    assert "1 commit" in result.stdout


def test_a_branch_stacked_on_another_branch_is_flagged(repo: Path):
    """The case the tool exists for.

    `stacked` is cut from `feature`, not from `main`. Its merge-base with main
    is still main's tip, because `feature` was itself cut from main -- so the
    merge-base test alone says nothing. What identifies it is that most of its
    commits already live on `feature`.
    """
    _branch_with_commit(repo, "feature", "a.txt")
    git(repo, "checkout", "-q", "-b", "stacked", "feature")
    write(repo / "b.txt", "b\n")
    commit_all(repo, "my own work")
    git(repo, "checkout", "-q", "main")
    _publish(repo)

    result = check(repo, "main", "stacked")
    assert result.returncode == 1, result.stdout
    assert "also live on another branch" in result.stdout
    assert "origin/feature" in result.stdout


def test_commits_already_on_the_default_branch_are_not_flagged(repo: Path):
    """A propagation PR carries the default branch's commits by definition.

    Flagging that would fire on every propagation while saying nothing, which
    is how a check becomes noise and then becomes ignored.
    """
    git(repo, "checkout", "-q", "-b", "long-lived")
    write(repo / "own.txt", "own\n")
    commit_all(repo, "the branch's own work")
    git(repo, "checkout", "-q", "main")
    write(repo / "org.txt", "org\n")
    commit_all(repo, "org-level work on main")
    git(repo, "checkout", "-q", "-b", "propagate", "long-lived")
    git(repo, "merge", "-q", "--no-edit", "main")
    git(repo, "checkout", "-q", "main")
    _publish(repo)

    result = check(repo, "long-lived", "propagate")
    assert result.returncode == 0, (
        "a propagation carrying main's commits must not be flagged:\n" + result.stdout
    )


def test_a_branch_behind_its_base_is_flagged(repo: Path):
    _branch_with_commit(repo, "stale", "a.txt")
    write(repo / "moved.txt", "moved\n")
    commit_all(repo, "base moves on")
    _publish(repo)
    result = check(repo, "main", "stale")
    assert result.returncode == 1, result.stdout
    assert "!= BASE TIP" in result.stdout or "behind" in result.stdout


def test_a_remote_qualified_base_is_not_double_prefixed(repo: Path):
    """`--base origin/main` must resolve `origin/main`, not `origin/origin/main`.

    The original condition asked whether the first path segment contained a
    slash. It never does, so every ref was prefixed unconditionally; the bug
    hid because every call site passed a bare name.
    """
    _branch_with_commit(repo, "feature", "a.txt")
    _publish(repo)
    result = check(repo, "origin/main", "origin/feature")
    assert "origin/origin" not in result.stdout + result.stderr, (
        "ref was double-prefixed:\n" + result.stdout + result.stderr
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_an_unknown_ref_fails_rather_than_reporting_clean(repo: Path):
    _publish(repo)
    result = check(repo, "main", "no-such-branch")
    assert result.returncode != 0
    assert "clean" not in result.stdout.lower()


def test_authors_are_reported_so_foreign_commits_are_visible(repo: Path):
    _branch_with_commit(repo, "feature", "a.txt")
    _publish(repo)
    result = check(repo, "main", "feature")
    assert "authors" in result.stdout
    assert "Test" in result.stdout
