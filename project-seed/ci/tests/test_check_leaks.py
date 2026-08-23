"""Tests for the leak check.

Every case builds a small repository and commits into it. The check reads
`git ls-files`, so a fixture that only writes files tests nothing — the thing
under test is what is *tracked*, which is what gets published.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

CI_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(CI_DIR))

from check_leaks import PLACEHOLDERS, findings, main, redact  # noqa: E402

TOOL = CI_DIR / "check_leaks.py"


def git(*args: str, cwd: Path) -> None:
    done = subprocess.run(["git", *args], cwd=str(cwd), capture_output=True,
                          text=True, encoding="utf-8", errors="replace")
    assert done.returncode == 0, f"git {' '.join(args)}\n{done.stdout}{done.stderr}"


@pytest.fixture()
def repo(tmp_path: Path) -> Path:
    where = tmp_path / "repo"
    where.mkdir()
    git("init", "-q", "-b", "main", cwd=where)
    git("config", "user.email", "t@example.com", cwd=where)
    git("config", "user.name", "T", cwd=where)
    return where


def commit(repo: Path, name: str, body: str) -> None:
    path = repo / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    git("add", "-A", cwd=repo)
    git("-c", "commit.gpgsign=false", "commit", "-q", "-m", name, cwd=repo)


def kinds(repo: Path) -> list[str]:
    found, _ = findings(repo)
    return [row["kind"] for row in found]


# --- the three that were actually found --------------------------------------


def test_a_home_path_names_the_account(repo: Path):
    """THE ONE THIS EXISTS FOR. Found in three repositories on 2026-08-23: a
    documented config, two screenshots, and a pasted traceback.

    Mutation: drop the home-path pattern and this fails.
    """
    commit(repo, "docs/setup.md", r'run it from C:\Users\pkagstrom\repos\thing')
    assert kinds(repo) == ["home-path"]


def test_a_shared_conversation_link_is_a_finding(repo: Path):
    """Anybody holding the link can read the conversation. It is not a
    credential, so no secret scanner looks for it."""
    commit(repo, "notes.md", "see https://claude.ai/share/7bbc74b5-7d95-4ca1")
    assert kinds(repo) == ["shared-conversation"]


def test_a_path_to_a_conversation_archive_is_a_finding(repo: Path):
    commit(repo, "notes.md", r"exported to C:\Users\x\Documents\claude_history\a.json")
    assert "conversation-archive" in kinds(repo)


# --- what it must not fire on ------------------------------------------------


def test_a_placeholder_account_is_fine(repo: Path):
    """`C:\\Users\\you` is what the docs already write and what the redaction
    produces. A check that rejected it would make the fix impossible."""
    commit(repo, "docs/settings.md", r"the database lives in C:\Users\you\.dossier")
    assert kinds(repo) == []


def test_a_rest_route_is_not_a_home_directory(repo: Path):
    """**THE FALSE POSITIVE THAT WOULD HAVE KILLED THIS CHECK.**
    `api.github.com/users/octocat/repos` matched while the pattern was
    case-insensitive. A check that fires on every GitHub URL is one people turn
    off, and then it catches nothing at all.

    Mutation: make the pattern case-insensitive again and this fails.
    """
    commit(repo, "tests/t.py", 'respx.get("https://api.github.com/users/octocat/repos")')
    assert kinds(repo) == []


def test_the_export_format_is_not_somebody_s_disk(repo: Path):
    """`conversations.json` names a format. `qmcp threads import
    <conversations.json>` is a command somebody has to be able to write down,
    and it appeared nine times in the repository whose job is importing it.

    Mutation: match the bare filename and this fails.
    """
    commit(repo, "README.md", "qmcp threads import <conversations.json> --source claude")
    assert kinds(repo) == []


def test_a_binary_is_not_read(repo: Path):
    """Reading every PNG as text finds nothing and costs the whole sweep."""
    commit(repo, "docs/x.png", "C:/Users/realname/somewhere")
    assert kinds(repo) == []


# --- the escape hatch, and its price ------------------------------------------


def test_a_stated_reason_allows_a_deliberate_example(repo: Path):
    """The check's own tests contain the thing it looks for. Without this they
    would be permanently red — a scan firing on the fixture that proves it
    works.

    Mutation: ignore the marker and this fails.
    """
    commit(repo, "tests/t.py",
           "# leaks: allow a fixture proving the check fires\n"
           r'BAD = r"C:\Users\realname\thing"')
    found, excused = findings(repo)
    assert found == []
    assert len(excused) == 1
    assert "fixture proving" in excused[0]["why"]


def test_an_exemption_is_reported_rather_than_silent(repo: Path, capsys):
    """**A CARVE-OUT THAT PRINTS NOTHING IS INDISTINGUISHABLE FROM A RULE
    NOBODY WROTE.** Silencing this check must stay visible.

    Mutation: stop printing the exemption count and this fails.
    """
    commit(repo, "tests/t.py",
           "# leaks: allow a fixture proving the check fires\n"
           r'BAD = r"C:\Users\realname\thing"')
    assert main(["--root", str(repo)]) == 0
    assert "allowed by a stated reason" in capsys.readouterr().out


def test_a_marker_with_no_reason_does_not_excuse_anything(repo: Path):
    """An exemption without a reason is an excuse."""
    commit(repo, "tests/t.py",
           "# leaks: allow\n" + r'BAD = r"C:\Users\realname\thing"')
    assert kinds(repo) == ["home-path"]


# --- how it reports -----------------------------------------------------------


def test_a_finding_is_never_printed_in_full(repo: Path, capsys):
    """**A SWEEP THAT ECHOES WHAT IT FOUND HAS PUBLISHED IT A SECOND TIME**,
    into a terminal and whatever reads that terminal.

    Mutation: print the match instead of `redact(match)` and this fails.
    """
    commit(repo, "docs/setup.md", r"C:\Users\averydistinctivename\repos")
    main(["--root", str(repo)])
    printed = capsys.readouterr().out
    assert "averydistinctivename" not in printed
    assert "ave" in printed          # enough to recognise


def test_redaction_keeps_enough_to_recognise():
    assert "averydistinctivename" not in redact("averydistinctivename")
    assert redact("ab").startswith("ab")


def test_a_clean_run_states_its_denominator(repo: Path, capsys):
    """`clean` against four files and `clean` against four hundred are the same
    word and not the same claim. `check_private_names.py` once knew 2 names of
    34 and reported `clean` throughout.

    Mutation: drop the file count and this fails.
    """
    commit(repo, "README.md", "nothing to see")
    assert main(["--root", str(repo)]) == 0
    printed = capsys.readouterr().out
    assert "clean" in printed
    assert "tracked file(s)" in printed
    assert "History is not read" in printed


def test_the_command_line_exits_non_zero_on_a_finding(repo: Path):
    """The path CI and a person actually run. Wiring it wrong would leave every
    test above green while the check did nothing."""
    commit(repo, "docs/setup.md", r"C:\Users\realname\repos")
    done = subprocess.run([sys.executable, str(TOOL), "--root", str(repo)],
                          capture_output=True, text=True, encoding="utf-8",
                          errors="replace")
    assert done.returncode == 1, done.stdout


def test_json_carries_findings_and_exemptions(repo: Path):
    import json

    commit(repo, "docs/setup.md", r"C:\Users\realname\repos")
    done = subprocess.run(
        [sys.executable, str(TOOL), "--root", str(repo), "--json"],
        capture_output=True, text=True, encoding="utf-8", errors="replace")
    payload = json.loads(done.stdout)
    assert payload["checked"] >= 1
    assert payload["findings"][0]["kind"] == "home-path"
    assert payload["exempted"] == []


def test_untracked_files_are_not_checked(repo: Path):
    """What is published is what is tracked. A check that read the working tree
    would fire on a developer's scratch file and teach them to ignore it."""
    commit(repo, "README.md", "clean")
    (repo / "scratch.md").write_text(r"C:\Users\realname\notes", encoding="utf-8")
    assert kinds(repo) == []


def test_placeholders_are_lowercase_so_the_comparison_works():
    """The lookup lowercases the account before comparing. An uppercase entry
    here would never match and would read as covered.
    """
    for name in PLACEHOLDERS:
        assert name == name.lower(), name
