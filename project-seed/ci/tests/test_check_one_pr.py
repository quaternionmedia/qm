"""Tests for the stack check: no pull request is ready while stacked.

Every test here names a state the check must call bad, or a state it must call
good, and asserts the exit status rather than the wording. The exit status is
the contract: a check that prints the right paragraph and returns 0 enforces
nothing, and that failure has reached this seed six times.

The pull request lists are fed in as JSON rather than fetched, because the
thing under test is the stacking rule, not gh. The fetch has its own hazards --
pagination and decoding -- and those are asserted separately where they can be
asserted honestly.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from conftest import CI_DIR, ENV, run_tool

REPO = "owner/name"


def pr(number: int, author: str, base: str = "main", head: str | None = None,
       bot: bool = False, draft: bool = False, title: str = "A change",
       head_repo: str | None = REPO) -> dict:
    return {
        "number": number,
        "title": title,
        "draft": draft,
        "base": {"ref": base},
        "head": {"ref": head or f"branch-{number}",
                 "repo": {"full_name": head_repo} if head_repo else None},
        "user": {"login": author, "type": "Bot" if bot else "User"},
    }


def check(tmp_path: Path, prs: list[dict], *args: str):
    path = tmp_path / "prs.json"
    path.write_text(json.dumps(prs), encoding="utf-8")
    return run_tool(
        "check_one_pr.py", "--repo", REPO, "--from-json", str(path), *args,
        cwd=tmp_path,
    )


def stack(ready_child: bool) -> list[dict]:
    """#1 on main, #2 cut from #1's branch and based on it."""
    return [pr(1, "ada", head="feat/a"),
            pr(2, "ada", base="feat/a", head="feat/b", draft=not ready_child)]


def test_parallel_ready_prs_from_one_contributor_pass(tmp_path: Path) -> None:
    """Independent changes are independent pull requests. No count."""
    result = check(tmp_path, [pr(1, "ada"), pr(2, "ada"), pr(3, "ada", base="develop")])
    assert result.returncode == 0, result.stdout + result.stderr


def test_a_stack_with_only_the_bottom_ready_passes(tmp_path: Path) -> None:
    result = check(tmp_path, stack(ready_child=False))
    assert result.returncode == 0, result.stdout + result.stderr


def test_a_ready_pr_stacked_on_an_open_one_fails(tmp_path: Path) -> None:
    result = check(tmp_path, stack(ready_child=True))
    assert result.returncode == 1, result.stdout + result.stderr
    assert "#2" in result.stdout and "#1" in result.stdout


def test_a_three_deep_stack_fails_on_each_ready_upper_pr(tmp_path: Path) -> None:
    prs = stack(ready_child=False) + [pr(3, "ada", base="feat/b", head="feat/c")]
    result = check(tmp_path, prs, "--json")
    assert result.returncode == 1, result.stdout + result.stderr
    assert [v["numbers"] for v in json.loads(result.stdout)["violations"]] == [[3]]


def test_a_parent_owned_by_someone_else_still_counts(tmp_path: Path) -> None:
    """The base chain is what orders the merges, whoever cut each branch."""
    prs = [pr(1, "grace", head="feat/a"), pr(2, "ada", base="feat/a")]
    assert check(tmp_path, prs).returncode == 1


def test_a_fork_branch_sharing_a_name_is_not_a_parent(tmp_path: Path) -> None:
    """A fork's branch cannot be a base in this repository."""
    prs = [pr(1, "grace", head="feat/a", head_repo="grace/name"),
           pr(2, "ada", base="feat/a")]
    assert check(tmp_path, prs).returncode == 0


def test_a_long_lived_base_with_no_open_pr_is_a_real_target(tmp_path: Path) -> None:
    """project/<name> bases here are targets, not stack parents."""
    prs = [pr(1, "ada", base="project/alfred"), pr(2, "ada", base="project/datum"),
           pr(3, "ada", base="project/alfred")]
    assert check(tmp_path, prs).returncode == 0


def test_bot_prs_are_counted_as_automation_and_not_judged(tmp_path: Path) -> None:
    result = check(
        tmp_path,
        [pr(1, "ada", head="feat/a"),
         pr(2, "dependabot[bot]", base="feat/a", bot=True),
         pr(3, "renovate[bot]", bot=True)],
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "(1 human, 2 automation)" in result.stdout


def test_bot_detected_by_login_when_type_says_user(tmp_path: Path) -> None:
    """The list endpoint has been seen to report app authors as type User.

    The bot's pull request is ready and stacked, so trusting the type alone
    produces a violation against an account no contributor can act on.
    """
    entries = [pr(1, "ada", head="feat/a"), pr(2, "dependabot[bot]", base="feat/a")]
    assert entries[1]["user"]["type"] == "User"
    result = check(tmp_path, entries)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "(1 human, 1 automation)" in result.stdout


def test_contributor_filter_scopes_the_exit_status(tmp_path: Path) -> None:
    """A PR author is failed for their own stack, never for someone else's."""
    prs = stack(ready_child=True) + [pr(3, "grace")]
    assert check(tmp_path, prs, "--contributor", "grace").returncode == 0
    assert check(tmp_path, prs, "--contributor", "ada").returncode == 1


def test_other_contributors_are_still_listed_under_a_filter(tmp_path: Path) -> None:
    """Scoping the exit status must not hide the queue from the reader."""
    result = check(tmp_path, [pr(1, "ada"), pr(2, "grace")], "--contributor", "grace")
    assert "ada" in result.stdout


def test_json_output_carries_the_violation_and_the_status(tmp_path: Path) -> None:
    result = check(tmp_path, stack(ready_child=True), "--json")
    assert result.returncode == 1, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["violations"] == [
        {"author": "ada", "base": "feat/a", "numbers": [2], "parent": 1}]


def test_json_output_is_empty_of_violations_when_clean(tmp_path: Path) -> None:
    result = check(tmp_path, stack(ready_child=False), "--json")
    assert result.returncode == 0, result.stdout + result.stderr
    assert json.loads(result.stdout)["violations"] == []


def test_a_title_that_is_not_ascii_does_not_kill_the_report(tmp_path: Path) -> None:
    """Real data, from a real repository: an emoji in a pull request title.

    The output encoding is pinned to cp1252 for this test, because that is the
    console a Windows contributor actually has and it is the only configuration
    in which the hazard exists. Left to the default, the tool prints the emoji
    fine on any developer machine and the test proves nothing -- which is what
    it did before this line was added.
    """
    path = tmp_path / "prs.json"
    path.write_text(
        json.dumps(
            [pr(1, "ada", head="feat/a", title="\N{WHITE SQUARE BUTTON} Gridfinity"),
             pr(2, "ada", base="feat/a", title="\N{WHITE SQUARE BUTTON} on top")]
        ),
        encoding="utf-8",
    )
    result = subprocess.run(
        [
            sys.executable,
            str(CI_DIR / "check_one_pr.py"),
            "--repo",
            "owner/name",
            "--from-json",
            str(path),
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=str(tmp_path),
        env={**ENV, "PYTHONIOENCODING": "cp1252"},
    )
    assert "UnicodeEncodeError" not in result.stderr, result.stderr
    assert result.returncode == 1, result.stdout + result.stderr


def test_no_open_prs_is_not_a_violation(tmp_path: Path) -> None:
    result = check(tmp_path, [])
    assert result.returncode == 0, result.stdout + result.stderr


def test_an_empty_repo_name_names_the_configuration_not_a_404(tmp_path: Path) -> None:
    """Outside a pull request event, `${{ github.repository }}` is empty.

    The request then becomes `repos//pulls` and GitHub answers 404 — a message
    about a missing repository, for a step that ran without its event context.
    """
    result = run_tool("check_one_pr.py", "--repo", "", cwd=tmp_path)
    assert result.returncode != 0
    combined = result.stdout + result.stderr
    assert "must be owner/name" in combined
    assert "event context" in combined


def test_a_repo_name_missing_its_owner_is_refused(tmp_path: Path) -> None:
    result = run_tool("check_one_pr.py", "--repo", "qm", cwd=tmp_path)
    assert result.returncode != 0
    assert "must be owner/name" in (result.stdout + result.stderr)
