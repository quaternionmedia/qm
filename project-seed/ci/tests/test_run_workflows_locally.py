"""The local workflow runner, which is only useful if it can report failure.

This tool exists so a claim of "CI is green" is produced by executing the
pipeline rather than by running commands that resemble it. That makes its own
correctness load-bearing in an unusual way: when it is wrong, it does not
produce a wrong answer, it produces a *false reassurance*, and the person
reading it stops looking.

It has been wrong exactly that way. It ran steps under plain `bash` where
GitHub Actions runs `bash -e`, so a step whose first command failed carried on
and was reported PASS -- while printing the failure into the log nobody reads
when the summary says PASS.
"""

from __future__ import annotations

from pathlib import Path

from conftest import commit_all, run_tool, write


def workflow(body: str) -> str:
    return (
        "name: T\non:\n  push:\n    branches: [main]\n  pull_request:\n\n"
        "jobs:\n  j:\n    runs-on: ubuntu-latest\n    steps:\n" + body
    )


def test_a_step_whose_first_command_fails_is_reported_as_failure(repo: Path):
    """The defect that made every 'all steps passed' claim unsound.

    Under plain `bash` this script exits 0, because the last command succeeded.
    Under `bash -e`, which is what Actions uses, it exits non-zero at the first
    failure. The runner must agree with Actions, not with bash's default.
    """
    write(
        repo / ".github" / "workflows" / "t.yml",
        workflow(
            "      - name: fails first, succeeds after\n"
            "        run: |\n"
            "          git rev-parse --verify definitely-no-such-ref\n"
            '          echo "carried on regardless"\n'
        ),
    )
    commit_all(repo, "add a workflow whose first command fails")
    result = run_tool("run_workflows_locally.py", cwd=repo)
    assert result.returncode == 1, (
        "a step whose first command fails must be reported FAIL; "
        f"got exit {result.returncode}\n{result.stdout}"
    )
    assert "FAIL" in result.stdout


def test_a_genuinely_passing_step_is_reported_as_pass(repo: Path):
    write(
        repo / ".github" / "workflows" / "t.yml",
        workflow("      - name: fine\n        run: echo ok\n"),
    )
    commit_all(repo, "add a passing workflow")
    result = run_tool("run_workflows_locally.py", cwd=repo)
    assert result.returncode == 0, result.stdout
    assert "PASS" in result.stdout


def test_a_branch_filter_that_does_not_match_skips_rather_than_passes(repo: Path):
    """A skipped workflow must not be counted as a passing one."""
    write(
        repo / ".github" / "workflows" / "t.yml",
        (
            "name: T\non:\n  pull_request:\n    branches: ['project/**']\n\n"
            "jobs:\n  j:\n    runs-on: ubuntu-latest\n    steps:\n"
            "      - name: never runs here\n        run: exit 1\n"
        ),
    )
    commit_all(repo, "add a project-only workflow")
    result = run_tool("run_workflows_locally.py", "--base-ref", "main", cwd=repo)
    assert result.returncode == 0, result.stdout
    assert "SKIP" in result.stdout


def test_a_remote_qualified_base_ref_still_matches_the_branch_filter(repo: Path):
    """`--base-ref origin/main` is the documented example and must work.

    GitHub only ever populates github.base_ref with a bare branch name, so
    passing a remote-qualified ref through verbatim made the filter compare
    'origin/main' against 'main', skip every workflow, and report success
    having run nothing.
    """
    # The pull_request trigger must carry a branches filter, or base_ref is
    # never consulted and this test proves nothing. An earlier version of this
    # fixture omitted it and passed against the unfixed tool.
    write(
        repo / ".github" / "workflows" / "t.yml",
        (
            "name: T\non:\n  pull_request:\n    branches: [main]\n\n"
            "jobs:\n  j:\n    runs-on: ubuntu-latest\n    steps:\n"
            "      - name: should run\n        run: echo ran\n"
        ),
    )
    commit_all(repo, "add a main-targeted workflow")
    result = run_tool("run_workflows_locally.py", "--base-ref", "origin/main", cwd=repo)
    assert "SKIP" not in result.stdout, (
        "a remote-qualified base ref must be normalised, not skipped:\n" + result.stdout
    )
    assert result.returncode == 0, result.stdout


def test_a_workflow_name_with_an_emoji_does_not_crash_the_runner(repo: Path):
    """Names are data the tool reads, so it has to survive them.

    A crash mid-report reads as the workflow failing rather than the tool
    failing, which is the worst shape for a tool whose job is saying what failed.
    """
    write(
        repo / ".github" / "workflows" / "t.yml",
        "name: \U0001f9ea Test\non:\n  pull_request:\n\njobs:\n  j:\n    runs-on: ubuntu-latest\n"
        "    steps:\n      - name: \U0001f52c run\n        run: echo ok\n",
    )
    commit_all(repo, "add a workflow named with an emoji")
    result = run_tool("run_workflows_locally.py", cwd=repo)
    assert "Traceback" not in result.stderr, result.stderr
    assert result.returncode == 0, result.stdout + result.stderr


def test_no_workflows_at_all_is_not_a_pass(repo: Path):
    result = run_tool("run_workflows_locally.py", cwd=repo)
    assert result.returncode != 0, (
        "an empty workflows directory must not report success -- that is "
        "indistinguishable from a pipeline that ran and passed"
    )


# --- working-directory decides where a step runs ---------------------------


def test_a_step_runs_in_its_working_directory(repo: Path):
    """Ignoring `working-directory` runs the command somewhere else.

    Found in codecartographer: `npm ci` with `working-directory: web` ran in
    the repository root and reported "no package-lock.json" about a file that
    exists one directory down. A confident failure, in a step that passes in
    CI.
    """
    write(repo / "sub" / "marker.txt", "here\n")
    write(
        repo / ".github" / "workflows" / "t.yml",
        workflow(
            "      - name: look for the marker\n"
            "        working-directory: sub\n"
            "        run: test -f marker.txt\n"
        ),
    )
    commit_all(repo, "add a workflow with a working-directory")
    result = run_tool("run_workflows_locally.py", cwd=repo)
    assert result.returncode == 0, (
        "the step should have run inside sub/, where the marker is\n"
        f"{result.stdout}"
    )
    assert "PASS" in result.stdout


def test_the_wrong_directory_would_have_been_noticed(repo: Path):
    """The same check, inverted: run it at the root and it must fail.

    Without this the test above passes for the wrong reason -- a command that
    succeeds anywhere proves nothing about where it ran.
    """
    write(repo / "sub" / "marker.txt", "here\n")
    write(
        repo / ".github" / "workflows" / "t.yml",
        workflow(
            "      - name: look for the marker at the root\n"
            "        run: test -f marker.txt\n"
        ),
    )
    commit_all(repo, "add a workflow without a working-directory")
    result = run_tool("run_workflows_locally.py", cwd=repo)
    assert result.returncode == 1, (
        "marker.txt is in sub/, so a root-relative test must fail\n"
        f"{result.stdout}"
    )


def test_a_working_directory_that_does_not_exist_is_a_failure_not_a_pass(repo: Path):
    """Silently running at the root would be the reassuring wrong answer."""
    write(
        repo / ".github" / "workflows" / "t.yml",
        workflow(
            "      - name: nowhere\n"
            "        working-directory: no-such-dir\n"
            "        run: echo ok\n"
        ),
    )
    commit_all(repo, "add a workflow pointing at a missing directory")
    result = run_tool("run_workflows_locally.py", cwd=repo)
    assert result.returncode == 1, result.stdout
    assert "working-directory does not exist" in result.stdout
