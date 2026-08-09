"""Tests for the session-brief builder.

The brief's only value is that a session can trust it instead of assuming, so
every test here is about a state the tool must not describe reassuringly. The
failures worth guarding are all the same shape: a fact that could not be
established, reported as the good value.

The submodule cases build real submodules rather than writing a `.gitmodules`
file, because the questions asked -- is it initialised, what commit is pinned,
is the URL fetchable -- are answered by git's index and not by that file.
"""

from __future__ import annotations

from pathlib import Path

from conftest import commit_all, git, run_tool, write


def brief(cwd: Path, *args: str) -> str:
    result = run_tool("cowork_context.py", "--offline", *args, cwd=cwd)
    assert result.returncode == 0, result.stdout + result.stderr
    return result.stdout


def add_submodule(parent: Path, child: Path, path: str, branch: str | None = None) -> None:
    git(parent, "-c", "protocol.file.allow=always", "submodule", "add", "-q", str(child), path)
    if branch:
        git(parent, "config", "-f", ".gitmodules", f"submodule.{path}.branch", branch)
    commit_all(parent, f"add submodule {path}")


def test_outside_a_git_repository_it_refuses(tmp_path: Path) -> None:
    """A brief about no repository would be a page of confident defaults."""
    result = run_tool("cowork_context.py", "--offline", cwd=tmp_path)
    assert result.returncode != 0
    assert "not inside a git repository" in (result.stdout + result.stderr)


def test_the_corpus_recognises_itself(repo: Path) -> None:
    write(repo / "PRINCIPLES.md", "# Charter\n")
    commit_all(repo, "charter")
    assert "this repository **is** the corpus" in brief(repo)


def test_a_repository_with_no_governance_says_unknown_not_adopted(repo: Path) -> None:
    """Absence of a submodule is not evidence of anything except absence."""
    text = brief(repo)
    assert "corpus mount: **unknown**" in text
    assert "has not adopted the constitution, or has adopted it by hand" in text


def test_the_governance_mount_is_found_by_url_not_by_being_first(
    repo: Path, tmp_path: Path
) -> None:
    """Reading `submodule status | head -1` once reported an unrelated pin.

    The unrelated submodule is added first here, so a tool that takes the first
    entry reports its commit as the governance pin and everything downstream is
    confidently wrong.
    """
    other = tmp_path / "otto"
    other.mkdir()
    git(other, "init", "-q", "-b", "main")
    write(other / "f.txt", "x")
    commit_all(other, "init")

    corpus = tmp_path / "qm"
    corpus.mkdir()
    git(corpus, "init", "-q", "-b", "main")
    write(corpus / "PRINCIPLES.md", "# Charter\n")
    corpus_head = commit_all(corpus, "init")

    add_submodule(repo, other, "vendor/otto")
    add_submodule(repo, corpus, "governance/qm", branch="project/thing")

    text = brief(repo)
    assert "corpus mounted at `governance/qm`" in text
    assert "project/thing" in text
    assert corpus_head[:12] in text


def test_an_uninitialised_submodule_is_named_as_such(repo: Path, tmp_path: Path) -> None:
    """Otherwise every governance file reads as missing rather than unread.

    A check that looks for AGENTS.md in an unpopulated submodule finds nothing
    and reports a project that has not adopted the constitution.
    """
    corpus = tmp_path / "qm"
    corpus.mkdir()
    git(corpus, "init", "-q", "-b", "main")
    write(corpus / "PRINCIPLES.md", "# Charter\n")
    commit_all(corpus, "init")
    add_submodule(repo, corpus, "governance/qm")

    git(repo, "submodule", "deinit", "-f", "governance/qm")
    text = brief(repo)
    # The remediation command, not the phrase: the handoffs section says "the
    # submodule is not initialised" too, when it cannot find the directory. An
    # assertion on the phrase alone passes against a tool that dropped this
    # check entirely, which is what it did before this line named the remedy.
    assert "git submodule update --init --recursive" in text
    assert "**the submodule is not initialised**" in text


def test_a_filesystem_submodule_url_is_flagged(repo: Path, tmp_path: Path) -> None:
    """It resolves locally and fails in CI, much later, as `not our ref`.

    Two QM projects have hit it, and one had never had a passing submodule
    check without anybody noticing that was the reason.
    """
    corpus = tmp_path / "qm"
    corpus.mkdir()
    git(corpus, "init", "-q", "-b", "main")
    write(corpus / "PRINCIPLES.md", "# Charter\n")
    commit_all(corpus, "init")
    add_submodule(repo, corpus, "governance/qm")

    text = brief(repo)
    assert "the URL is a filesystem path" in text


def test_no_workflows_is_unknown_rather_than_clean(repo: Path) -> None:
    text = brief(repo)
    assert "no `.github/workflows/`" in text
    assert "a repository with no gates is not a repository that passed them" in text


def test_workflows_are_listed_with_the_runner_caveat(repo: Path) -> None:
    write(repo / ".github" / "workflows" / "adr-lint.yml", "name: ADR lint\n")
    commit_all(repo, "workflow")
    text = brief(repo)
    assert "adr-lint.yml" in text
    assert "does not reproduce `uses:` steps" in text


def test_a_branch_with_no_upstream_says_nothing_is_on_a_remote(repo: Path) -> None:
    """Unpushed work read as pushed is how a session loses someone else's day."""
    git(repo, "checkout", "-q", "-b", "evolve/local-only")
    write(repo / "note.md", "local\n")
    commit_all(repo, "local work")
    text = brief(repo)
    assert "upstream: **none**" in text
    assert "nothing here is on a remote" in text


def test_uncommitted_work_is_flagged_as_possibly_not_yours(repo: Path) -> None:
    write(repo / "scratch.md", "someone else was here\n")
    text = brief(repo)
    assert "uncommitted changes: 1" in text
    assert "may not be yours" in text


def test_a_sibling_branch_is_reported(repo: Path) -> None:
    """A second session on this clone shows up as a branch with commits."""
    git(repo, "checkout", "-q", "-b", "other/session")
    write(repo / "theirs.md", "their work\n")
    commit_all(repo, "their commit")
    git(repo, "checkout", "-q", "main")

    text = brief(repo)
    assert "other/session" in text
    assert "1 commit(s) not on main" in text


def test_a_long_branch_list_says_how_many_it_left_off(repo: Path) -> None:
    """A list that silently stops reads as a complete one."""
    for index in range(12):
        git(repo, "checkout", "-q", "-b", f"branch-{index:02d}", "main")
        write(repo / f"f{index}.md", "x")
        commit_all(repo, f"commit {index}")
    git(repo, "checkout", "-q", "main")

    text = brief(repo)
    assert "…and 4 more, not listed" in text


def test_offline_reports_the_slot_as_unread_not_as_free(repo: Path) -> None:
    """The whole point: 'nothing was read' must never render as 'nothing wrong'."""
    text = brief(repo)
    assert "`--offline` was passed, so no pull request was read" in text
    assert "Your slot is free" not in text


def test_out_writes_the_same_text_it_printed(repo: Path) -> None:
    result = run_tool(
        "cowork_context.py", "--offline", "--out", ".harness/session-brief.md", cwd=repo
    )
    assert result.returncode == 0, result.stdout + result.stderr
    written = (repo / ".harness" / "session-brief.md").read_text(encoding="utf-8")
    assert written == result.stdout
