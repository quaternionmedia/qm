"""Tests for the one-open-PR-per-repository-per-contributor check.

Every test here names a state the check must call bad, or a state it must call
good, and asserts the exit status rather than the wording. The exit status is
the contract: a check that prints the right paragraph and returns 0 enforces
nothing, and that failure has reached this seed six times.

The pull request lists are fed in as JSON rather than fetched, because the
thing under test is the counting rule, not gh. The fetch has its own hazards --
pagination and decoding -- and those are asserted separately where they can be
asserted honestly.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from conftest import CI_DIR, ENV, run_tool


def pr(number: int, author: str, base: str = "main", bot: bool = False,
       draft: bool = False, title: str = "A change") -> dict:
    return {
        "number": number,
        "title": title,
        "draft": draft,
        "base": {"ref": base},
        "user": {"login": author, "type": "Bot" if bot else "User"},
    }


def check(tmp_path: Path, prs: list[dict], *args: str):
    path = tmp_path / "prs.json"
    path.write_text(json.dumps(prs), encoding="utf-8")
    return run_tool(
        "check_one_pr.py",
        "--repo",
        "owner/name",
        "--from-json",
        str(path),
        *args,
        cwd=tmp_path,
    )


def test_one_pr_per_contributor_passes(tmp_path: Path) -> None:
    result = check(tmp_path, [pr(1, "ada")])
    assert result.returncode == 0, result.stdout + result.stderr


def test_two_prs_from_one_contributor_fail(tmp_path: Path) -> None:
    result = check(tmp_path, [pr(1, "ada"), pr(2, "ada")])
    assert result.returncode == 1, result.stdout + result.stderr
    assert "#1" in result.stdout and "#2" in result.stdout


def test_two_contributors_with_one_each_pass(tmp_path: Path) -> None:
    """The rule is per contributor. Two people are two queues, not one."""
    result = check(tmp_path, [pr(1, "ada"), pr(2, "grace")])
    assert result.returncode == 0, result.stdout + result.stderr


def test_bot_prs_are_counted_as_automation_not_against_a_human(tmp_path: Path) -> None:
    """A contributor cannot close Dependabot's PR to make room for their own.

    Asserted on the reported split rather than the exit status: two PRs from
    two different logins never collide anyway, so an exit status of 0 here
    would hold whether or not the tool classified anything.
    """
    result = check(
        tmp_path,
        [pr(1, "ada"), pr(2, "dependabot[bot]", bot=True), pr(3, "renovate[bot]", bot=True)],
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "(1 human, 2 automation)" in result.stdout


def test_bot_detected_by_login_when_type_says_user(tmp_path: Path) -> None:
    """The list endpoint has been seen to report app authors as type User.

    Two PRs from the *same* bot login, so trusting the type alone produces a
    real violation against an account no contributor can act on. One PR would
    prove nothing: it would pass under either rule.
    """
    entries = [pr(1, "dependabot[bot]"), pr(2, "dependabot[bot]")]
    assert all(e["user"]["type"] == "User" for e in entries)
    result = check(tmp_path, entries)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "(0 human, 2 automation)" in result.stdout


def test_two_bot_prs_do_not_fail_the_check(tmp_path: Path) -> None:
    result = check(
        tmp_path,
        [pr(1, "dependabot[bot]", bot=True), pr(2, "dependabot[bot]", bot=True)],
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_drafts_count(tmp_path: Path) -> None:
    """Drafts are the normal state here, so exempting them exempts everything."""
    result = check(tmp_path, [pr(1, "ada", draft=True), pr(2, "ada", draft=True)])
    assert result.returncode == 1, result.stdout + result.stderr


def test_different_bases_still_share_one_slot_by_default(tmp_path: Path) -> None:
    """The rule is per repository. Branching differently does not buy a slot."""
    result = check(tmp_path, [pr(1, "ada", base="main"), pr(2, "ada", base="develop")])
    assert result.returncode == 1, result.stdout + result.stderr


def test_per_base_glob_gives_each_matching_base_its_own_slot(tmp_path: Path) -> None:
    result = check(
        tmp_path,
        [pr(1, "ada", base="project/alfred"), pr(2, "ada", base="project/datum")],
        "--per-base",
        "project/*",
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_per_base_does_not_exempt_bases_outside_the_glob(tmp_path: Path) -> None:
    """The exemption is the glob, not 'bases differ'.

    Two PRs to main are two PRs to main however many project branches exist.
    """
    result = check(
        tmp_path,
        [pr(1, "ada", base="main"), pr(2, "ada", base="main")],
        "--per-base",
        "project/*",
    )
    assert result.returncode == 1, result.stdout + result.stderr


def test_two_prs_against_the_same_exempted_base_still_fail(tmp_path: Path) -> None:
    """The glob buys one slot per base, not unlimited slots on a matching base."""
    result = check(
        tmp_path,
        [pr(1, "ada", base="project/alfred"), pr(2, "ada", base="project/alfred")],
        "--per-base",
        "project/*",
    )
    assert result.returncode == 1, result.stdout + result.stderr


def test_the_applied_exemption_is_printed(tmp_path: Path) -> None:
    """An exemption nobody can see in the output has stopped being one."""
    result = check(
        tmp_path, [pr(1, "ada", base="project/alfred")], "--per-base", "project/*"
    )
    assert "project/*" in result.stdout


def test_contributor_filter_scopes_the_exit_status(tmp_path: Path) -> None:
    """A PR author is failed for their own queue, never for someone else's."""
    prs = [pr(1, "ada"), pr(2, "ada"), pr(3, "grace")]
    assert check(tmp_path, prs, "--contributor", "grace").returncode == 0
    assert check(tmp_path, prs, "--contributor", "ada").returncode == 1


def test_other_contributors_are_still_listed_under_a_filter(tmp_path: Path) -> None:
    """Scoping the exit status must not hide the queue from the reader."""
    result = check(
        tmp_path, [pr(1, "ada"), pr(2, "grace")], "--contributor", "grace"
    )
    assert "ada" in result.stdout


def test_json_output_carries_the_violation_and_the_status(tmp_path: Path) -> None:
    result = check(tmp_path, [pr(1, "ada"), pr(2, "ada")], "--json")
    assert result.returncode == 1, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["violations"] == [{"author": "ada", "base": "", "numbers": [1, 2]}]


def test_json_output_is_empty_of_violations_when_clean(tmp_path: Path) -> None:
    result = check(tmp_path, [pr(1, "ada")], "--json")
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
            [pr(1, "ada", title="\N{WHITE SQUARE BUTTON} Gridfinity"), pr(2, "ada")]
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
