"""Tests for the stack lister: every open pull request, and the stack it sits in.

A stacked pull request may be ready (handbook/async-contract.md 1), so the
exit status is 0 whatever stands stacked, and non-zero only when the list
could not be read. What the tests assert is the list: which pull request is
found stacked on which, in the JSON a reader consumes and in the lines a
person reads.

The pull request lists are fed in as JSON rather than fetched, because the
thing under test is the base chain, not gh. The fetch has its own hazards --
pagination and decoding -- and those are asserted separately where they can be
asserted honestly.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

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


def stacked(tmp_path: Path, prs: list[dict], *args: str) -> list[tuple[int, int]]:
    """(number, parent) for each stacked pull request the JSON names."""
    result = check(tmp_path, prs, "--json", *args)
    assert result.returncode == 0, result.stdout + result.stderr
    return [(s["number"], s["parent"]) for s in json.loads(result.stdout)["stacked"]]


def test_parallel_prs_from_one_contributor_are_none_stacked(tmp_path: Path) -> None:
    """Independent changes are independent pull requests. No count."""
    prs = [pr(1, "ada"), pr(2, "ada"), pr(3, "ada", base="develop")]
    assert stacked(tmp_path, prs) == []
    assert "None is stacked" in check(tmp_path, prs).stdout


@pytest.mark.parametrize("ready_child", [True, False])
def test_a_stacked_pr_is_listed_on_its_parent_ready_or_draft(
        tmp_path: Path, ready_child: bool) -> None:
    """Ready is not a fault in a stack: the exit status is 0 either way.

    Mutation: return 1 from `report` when a stacked pull request is ready, and
    the ready case goes red.
    """
    result = check(tmp_path, stack(ready_child))
    assert result.returncode == 0, result.stdout + result.stderr
    kind = "ready" if ready_child else "draft"
    assert f"#2 [{kind}] ada: feat/b -> feat/a (on #1)" in result.stdout
    assert "1 stacked on another open pull request" in result.stdout
    assert stacked(tmp_path, stack(ready_child)) == [(2, 1)]


def test_a_three_deep_stack_names_each_parent(tmp_path: Path) -> None:
    prs = stack(ready_child=True) + [pr(3, "ada", base="feat/b", head="feat/c")]
    assert stacked(tmp_path, prs) == [(2, 1), (3, 2)]


def test_a_parent_owned_by_someone_else_still_counts(tmp_path: Path) -> None:
    """The base chain is what orders the merges, whoever cut each branch."""
    prs = [pr(1, "grace", head="feat/a"), pr(2, "ada", base="feat/a")]
    assert stacked(tmp_path, prs) == [(2, 1)]


def test_a_fork_branch_sharing_a_name_is_not_a_parent(tmp_path: Path) -> None:
    """A fork's branch cannot be a base in this repository."""
    prs = [pr(1, "grace", head="feat/a", head_repo="grace/name"),
           pr(2, "ada", base="feat/a")]
    assert stacked(tmp_path, prs) == []


def test_a_long_lived_base_with_no_open_pr_is_a_real_target(tmp_path: Path) -> None:
    """project/<name> bases here are targets, not stack parents."""
    prs = [pr(1, "ada", base="project/alfred"), pr(2, "ada", base="project/datum"),
           pr(3, "ada", base="project/alfred")]
    assert stacked(tmp_path, prs) == []


def test_bot_prs_are_counted_as_automation_and_not_listed(tmp_path: Path) -> None:
    prs = [pr(1, "ada", head="feat/a"),
           pr(2, "dependabot[bot]", base="feat/a", bot=True),
           pr(3, "renovate[bot]", bot=True)]
    result = check(tmp_path, prs)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "(1 human, 2 automation)" in result.stdout
    assert "dependabot" not in result.stdout
    assert stacked(tmp_path, prs) == []


def test_bot_detected_by_login_when_type_says_user(tmp_path: Path) -> None:
    """The list endpoint has been seen to report app authors as type User.

    The bot's pull request is stacked, so trusting the type alone lists an
    account's queue among people's work.
    """
    entries = [pr(1, "ada", head="feat/a"), pr(2, "dependabot[bot]", base="feat/a")]
    assert entries[1]["user"]["type"] == "User"
    result = check(tmp_path, entries)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "(1 human, 1 automation)" in result.stdout
    assert stacked(tmp_path, entries) == []


def test_contributor_filter_lists_that_login_only(tmp_path: Path) -> None:
    """`qm stacks` is a contributor's own list; the parent is found anyway."""
    prs = [pr(1, "grace", head="feat/a"), pr(2, "ada", base="feat/a"), pr(3, "grace")]
    result = check(tmp_path, prs, "--contributor", "ada")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "#2 [ready] ada" in result.stdout and "#3" not in result.stdout
    assert stacked(tmp_path, prs, "--contributor", "ada") == [(2, 1)]
    assert stacked(tmp_path, prs, "--contributor", "grace") == []


def test_json_output_carries_every_open_pr_under_a_filter(tmp_path: Path) -> None:
    """A reader counting a repository's queue counts all of it."""
    result = check(tmp_path, stack(ready_child=True), "--json", "--contributor", "grace")
    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert [p["number"] for p in payload["open_prs"]] == [1, 2]
    assert payload["stacked"] == []


def test_json_output_names_the_parent_and_its_branch(tmp_path: Path) -> None:
    result = check(tmp_path, stack(ready_child=True), "--json")
    assert result.returncode == 0, result.stdout + result.stderr
    assert json.loads(result.stdout)["stacked"] == [
        {"number": 2, "author": "ada", "base": "feat/a", "parent": 1}]


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
    assert result.returncode == 0, result.stdout + result.stderr
    # The closing line is printed after every title: reaching it is the proof
    # the report was not cut short.
    assert "1 stacked on another open pull request" in result.stdout


def test_no_open_prs_is_none_stacked(tmp_path: Path) -> None:
    result = check(tmp_path, [])
    assert result.returncode == 0, result.stdout + result.stderr
    assert "None is stacked" in result.stdout


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


def test_without_a_credential_the_fetch_names_the_login_not_an_api_failure(monkeypatch):
    """`gh` without a credential exits 4 and says `gh auth login` under a
    line about getting started; wrapped in *gh api ... failed* that reads as
    the host refusing the repository. The check names the missing credential
    itself and stops.

    Mutation: drop the credential branch from `fetch_open_prs`, and the
    message is the api failure again.
    """
    sys.path.insert(0, str(CI_DIR))
    import check_one_pr

    def no_credential(*args, **kwargs):
        return subprocess.CompletedProcess(
            args, 4, "",
            "To get started with GitHub CLI, please run:  gh auth login\n"
            "Alternatively, populate the GH_TOKEN environment variable with a "
            "GitHub API authentication token.\n")

    monkeypatch.setattr(check_one_pr.subprocess, "run", no_credential)
    with pytest.raises(SystemExit) as stopped:
        check_one_pr.fetch_open_prs(REPO)
    message = str(stopped.value)
    assert message.startswith("check_one_pr: no host credential"), message
    assert "gh auth login" in message
    assert "failed" not in message


def test_without_gh_installed_the_fetch_names_the_install_not_a_traceback(monkeypatch):
    """A machine with no `gh` on its path raised `FileNotFoundError` out of the
    subprocess call, a traceback that names neither the tool nor the remedy.
    The check names what it needs and stops.

    Mutation: drop the `FileNotFoundError` branch from `fetch_open_prs`, and the
    exception escapes as itself.
    """
    sys.path.insert(0, str(CI_DIR))
    import check_one_pr

    def no_gh(*args, **kwargs):
        raise FileNotFoundError(2, "No such file or directory", "gh")

    monkeypatch.setattr(check_one_pr.subprocess, "run", no_gh)
    with pytest.raises(SystemExit) as stopped:
        check_one_pr.fetch_open_prs(REPO)
    message = str(stopped.value)
    assert message.startswith("check_one_pr: `gh` is not installed"), message
    assert "https://cli.github.com" in message
    assert "gh auth login" in message
