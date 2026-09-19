"""Tests for the canonical test route.

The point of `qm test` is that there is one invocation, and that it is CI's. So
the load-bearing test here reads the workflow and asserts they still agree — if
they drift, a local pass stops predicting a remote one, and every other test in
this repository becomes less trustworthy without saying so.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

CI_DIR = Path(__file__).resolve().parent.parent
CORPUS = CI_DIR.parent
sys.path.insert(0, str(CI_DIR))

from run_tests import BASE_ARGS, SUITES, main  # noqa: E402

WORKFLOW = CORPUS / ".github" / "workflows" / "ci-tooling-tests.yml"


def workflow_pytest_command() -> str:
    """The `run:` line in ci-tooling-tests.yml that invokes pytest."""
    doc = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))
    for job in (doc.get("jobs") or {}).values():
        for step in job.get("steps") or []:
            run = step.get("run") or ""
            if "pytest" in run and "pip install" not in run:
                return " ".join(run.split())
    raise AssertionError("no pytest step found in ci-tooling-tests.yml")


def test_the_suites_match_the_ones_ci_runs():
    """The whole contract. Drift here silently decouples local from remote."""
    command = workflow_pytest_command()
    for suite in SUITES:
        assert suite in command, f"{suite} is not in CI's command: {command}"


def test_ci_runs_no_suite_this_route_omits():
    """The reverse direction: a suite added to CI and not here would be
    uncollected locally, which is how half a tree goes unchecked."""
    command = workflow_pytest_command()
    for token in re.findall(r"\b[\w./-]+/tests\b", command):
        assert token in SUITES, f"CI runs {token}, which `qm test` does not"


def test_both_suites_are_present_because_one_would_be_half_the_tooling():
    assert {"project-seed/ci/tests", "ci/tests"} <= set(SUITES)


def test_the_walkthrough_is_named_on_the_command_line():
    """records/DRAFT-one-executable-walkthrough.md §2, measured there: pytest
    ignores `testpaths` the moment it receives a path argument, and this
    invocation always passes paths. A walkthrough wired through `testpaths`
    would be collected by nobody and stay green forever."""
    assert "walkthrough" in SUITES


def test_the_suite_paths_exist():
    for suite in SUITES:
        assert (CORPUS / suite).is_dir(), f"{suite} is not a directory"


def test_the_base_arguments_are_quiet_and_the_doctest_glob_and_nothing_else():
    """Anything beyond these is a default an operator did not choose and cannot
    see. `--doctest-glob=*.md` is here because the walkthrough pages *are* the
    executable -- without it they are collected and no example runs, which is
    the silent-green failure the record is against."""
    assert BASE_ARGS == ("-q", "--doctest-glob=*.md")


def test_extra_arguments_reach_pytest(capsys, monkeypatch):
    """`qm test -- -k foo` must not be swallowed by the route."""
    seen = {}

    class Result:
        returncode = 0

    def fake_run(args, **kwargs):
        seen["args"] = args
        return Result()

    monkeypatch.setattr("run_tests.subprocess.run", fake_run)
    assert main(["--", "-k", "restatements"]) == 0
    assert seen["args"][-2:] == ["-k", "restatements"]


def test_the_separator_itself_is_not_passed_on(monkeypatch):
    seen = {}

    class Result:
        returncode = 0

    def fake_run(args, **kwargs):
        seen["args"] = args
        return Result()

    monkeypatch.setattr("run_tests.subprocess.run", fake_run)
    main(["--", "-k", "x"])
    assert "--" not in seen["args"]


def test_the_exit_status_is_pytest_s_own(monkeypatch):
    """A route that flattened a failure to 0 would report green over a red suite."""
    class Result:
        returncode = 3

    monkeypatch.setattr("run_tests.subprocess.run", lambda *a, **k: Result())
    assert main([]) == 3


def test_it_says_a_local_pass_is_not_proof(capsys, monkeypatch):
    class Result:
        returncode = 0

    monkeypatch.setattr("run_tests.subprocess.run", lambda *a, **k: Result())
    main([])
    assert "not proof" in capsys.readouterr().err
