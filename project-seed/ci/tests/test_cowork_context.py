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


def test_pushed_work_with_no_local_branch_is_reported(repo: Path) -> None:
    """A fresh clone has one local branch, and pushed work must still show.

    This is the case a `refs/heads` scan cannot see: work that was pushed and
    has no pull request is invisible to the slot check too, so a brief that
    misses it reports a clean repository over a branch full of waiting work.
    """
    upstream = repo.parent / "upstream.git"
    git(repo, "clone", "--bare", "-q", str(repo), str(upstream))
    git(repo, "remote", "set-url", "origin", str(upstream))

    git(repo, "checkout", "-q", "-b", "evolve/pushed-elsewhere")
    write(repo / "theirs.md", "their work\n")
    commit_all(repo, "their commit")
    git(repo, "push", "-q", "origin", "evolve/pushed-elsewhere")

    # The state a clone that never made the branch is in: the remote-tracking
    # ref exists, the local branch does not.
    git(repo, "checkout", "-q", "main")
    git(repo, "branch", "-q", "-D", "evolve/pushed-elsewhere")

    text = brief(repo)
    assert "origin/evolve/pushed-elsewhere" in text
    assert "1 commit(s) not on main" in text


def test_a_branch_and_its_remote_ref_are_reported_once(repo: Path) -> None:
    """The ordinary case: `foo` and `origin/foo` are one piece of work."""
    upstream = repo.parent / "upstream2.git"
    git(repo, "clone", "--bare", "-q", str(repo), str(upstream))
    git(repo, "remote", "set-url", "origin", str(upstream))

    git(repo, "checkout", "-q", "-b", "other/session")
    write(repo / "theirs.md", "their work\n")
    commit_all(repo, "their commit")
    git(repo, "push", "-q", "origin", "other/session")
    git(repo, "checkout", "-q", "main")

    text = brief(repo)
    assert text.count("other/session:") == 1
    assert "origin/other/session:" not in text


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


def test_a_generated_document_is_reported_with_its_age(repo: Path) -> None:
    """A session that cannot see the age quotes the number anyway."""
    write(repo / "PRINCIPLES.md", "# Charter\n")
    write(
        repo / "harness-status.json",
        '{"schema": 1, "generated_at": "2026-01-01T00:00:00Z", "repositories": []}\n',
    )
    commit_all(repo, "documents")
    text = brief(repo)
    assert "harness-status.json" in text
    assert "past its 24h budget" in text
    assert "re-derive any figure you act on" in text


def test_a_fresh_document_is_not_reported_as_stale(repo: Path) -> None:
    from datetime import datetime, timezone

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    write(repo / "PRINCIPLES.md", "# Charter\n")
    write(
        repo / "harness-status.json",
        f'{{"schema": 1, "generated_at": "{now}", "repositories": []}}\n',
    )
    commit_all(repo, "documents")
    text = brief(repo)
    assert "within its 24h budget" in text
    assert "past its 24h budget" not in text


def test_an_absent_document_is_named_rather_than_omitted(repo: Path) -> None:
    """A missing row reads as a document with nothing in it."""
    write(repo / "PRINCIPLES.md", "# Charter\n")
    commit_all(repo, "charter")
    text = brief(repo)
    assert "`harness-status.json` — **absent**" in text
    assert "do not assume clean" in text


def test_a_document_without_a_stamp_is_age_unknown_not_age_zero(repo: Path) -> None:
    """mtime would say 'minutes old' in every fresh clone, which is every session."""
    write(repo / "PRINCIPLES.md", "# Charter\n")
    write(repo / "harness-status.json", '{"schema": 1, "repositories": []}\n')
    commit_all(repo, "documents")
    text = brief(repo)
    assert "**Age unknown**" in text
    assert "treat every figure in it as unverified" in text
