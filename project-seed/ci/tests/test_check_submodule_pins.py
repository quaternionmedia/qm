"""Tests for the submodule-pin check.

**EVERY CASE HERE IS BUILT, NOT MOCKED.** Real repositories, real remotes, real
fetches over `file://` URLs. The defect this check exists for -- a pin that
resolves on one machine and nowhere else -- is precisely a disagreement between
what git does locally and what it does elsewhere, and a mocked fetch cannot
disagree with anything.

The two verdicts that must never collapse into each other are `unpushed` and
`unreadable`. The check this replaced reported both as one failure, in an error
whose own text admitted it could not tell them apart.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

CI_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(CI_DIR))

from check_submodule_pins import (  # noqa: E402
    OK, UNPUSHED, UNREADABLE, LOCAL_URL, as_https, is_remote_url, main,
)

TOOL = CI_DIR / "check_submodule_pins.py"


def git(*args: str, cwd: Path) -> str:
    done = subprocess.run(["git", *args], cwd=str(cwd), capture_output=True,
                          text=True, encoding="utf-8", errors="replace")
    assert done.returncode == 0, f"git {' '.join(args)}\n{done.stdout}{done.stderr}"
    return done.stdout


def commit(repo: Path, name: str) -> str:
    (repo / name).write_text(name, encoding="utf-8")
    git("add", "-A", cwd=repo)
    git("-c", "commit.gpgsign=false", "commit", "-q", "-m", name, cwd=repo)
    return git("rev-parse", "HEAD", cwd=repo).strip()


def new_repo(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    git("init", "-q", "-b", "main", cwd=path)
    git("config", "user.email", "t@example.com", cwd=path)
    git("config", "user.name", "T", cwd=path)
    return path


@pytest.fixture()
def world(tmp_path: Path):
    """A parent repository with one submodule, and a real remote for it.

    Returns (parent, child, remote_url). The child's remote holds one commit;
    the caller decides what the parent pins.
    """
    remote = tmp_path / "remote.git"
    git("init", "-q", "--bare", "-b", "main", str(remote), cwd=tmp_path)

    child = new_repo(tmp_path / "child")
    commit(child, "first.txt")
    git("remote", "add", "origin", remote.as_uri(), cwd=child)
    git("push", "-q", "origin", "main", cwd=child)

    parent = new_repo(tmp_path / "parent")
    commit(parent, "readme.txt")
    git("-c", "protocol.file.allow=always", "submodule", "add", "-q",
        remote.as_uri(), "child", cwd=parent)
    git("-c", "commit.gpgsign=false", "commit", "-q", "-m", "add child",
        cwd=parent)

    # **THE SUBMODULE THE PARENT PINS IS `parent/child`, NOT THE CLONE ABOVE.**
    # `git submodule add` clones the remote afresh into the parent. Committing
    # in the other directory moves a repository nothing points at, and the
    # parent then has nothing to stage -- which is how this fixture was wrong
    # the first time, and it failed as "nothing to commit" rather than as
    # anything naming the cause.
    sub = parent / "child"
    git("config", "user.email", "t@example.com", cwd=sub)
    git("config", "user.name", "T", cwd=sub)
    return parent, sub, remote.as_uri()


def verdicts(parent: Path) -> dict[str, str]:
    import check_submodule_pins as mod
    return {
        row["path"]: row["verdict"]
        for row in (mod.inspect(parent, sha, path)
                    for sha, path in mod.submodules(parent))
    }


# --- the two that must never collapse ----------------------------------------


def test_a_pin_that_is_on_the_remote_is_ok(world):
    """The control. Without it, every case below is satisfiable by failing
    everything."""
    parent, _, _ = world
    assert verdicts(parent) == {"child": OK}


def test_a_commit_that_was_never_pushed_is_a_failure(world):
    """**THE ONE THIS EXISTS FOR.** A commit made inside the submodule and not
    pushed: the parent pins it, it resolves here, and it resolves nowhere else.
    `codecartographer` shipped exactly this and a fresh clone could not have
    checked itself out.

    The remote is readable, so there is no ambiguity to hide behind.

    Mutation: report `unreadable` when the fetch fails and this fails.
    """
    parent, child, _ = world
    local_only = commit(child, "never-pushed.txt")
    git("add", "child", cwd=parent)
    git("-c", "commit.gpgsign=false", "commit", "-q", "-m", "bump", cwd=parent)

    assert verdicts(parent) == {"child": UNPUSHED}
    assert main(["--root", str(parent)]) == 1
    # And it names the commit, so the reader knows which one to push.
    import check_submodule_pins as mod
    rows = [mod.inspect(parent, sha, path)
            for sha, path in mod.submodules(parent)]
    assert rows[0]["sha"].startswith(local_only[:8])


def test_a_remote_nobody_here_can_read_is_unknown_and_not_a_failure(world):
    """**THE FALSE RED THIS REMOVES.** A private submodule is unreadable to an
    unauthenticated runner, and so is a deleted one. Failing on that made a
    project permanently red for a reason nothing was wrong with, and a check
    that is always red is one people stop reading.

    Mutation: return `unpushed` when the remote cannot be read and this fails.
    """
    parent, _, _ = world
    gone = (parent.parent / "not-there.git").as_uri()
    git("config", "-f", ".gitmodules", "submodule.child.url", gone, cwd=parent)

    assert verdicts(parent) == {"child": UNREADABLE}
    assert main(["--root", str(parent)]) == 0


def test_unknown_is_reported_rather_than_passed_silently(world, capsys):
    """Exit 0 is not the same as nothing to say. A pin nobody could check must
    be visible in the output, or the run reads as a clean bill of health.

    Mutation: print nothing for the unreadable case and this fails.
    """
    parent, _, _ = world
    gone = (parent.parent / "not-there.git").as_uri()
    git("config", "-f", ".gitmodules", "submodule.child.url", gone, cwd=parent)

    main(["--root", str(parent)])
    printed = capsys.readouterr().out
    assert "unreadable" in printed
    assert "could not be checked" in printed


# --- the other ways a pin goes unresolvable ----------------------------------


def test_a_filesystem_url_is_a_failure(world):
    """A path is not a remote. It resolves where it was typed and nowhere else,
    and in CI it fails as a missing directory rather than as anything naming the
    cause."""
    parent, child, _ = world
    git("config", "-f", ".gitmodules", "submodule.child.url", str(child),
        cwd=parent)

    assert verdicts(parent) == {"child": LOCAL_URL}
    assert main(["--root", str(parent)]) == 1


def test_an_ssh_url_is_tried_as_https_too():
    """A runner has no SSH key, so the canonical SSH remote -- which is what the
    fork procedure writes -- would read as unpushed for every project.

    Mutation: stop translating and this fails.
    """
    assert as_https("git@github.com:o/r.git") == "https://github.com/o/r.git"
    assert as_https("ssh://git@github.com/o/r.git") == "https://github.com/o/r.git"
    assert as_https("https://github.com/o/r.git") == "https://github.com/o/r.git"


def test_a_url_form_is_judged_by_shape_not_by_reachability():
    assert is_remote_url("https://github.com/o/r.git")
    assert is_remote_url("git@github.com:o/r.git")
    assert is_remote_url("file:///tmp/x.git")
    assert not is_remote_url("../sibling")
    assert not is_remote_url("C:\\\\Users\\\\peter\\\\repos\\\\x")


def test_a_repository_with_no_submodules_is_clean(tmp_path: Path):
    """And says so, rather than printing an empty report that reads as a pass
    over submodules that were never looked at."""
    lone = new_repo(tmp_path / "lone")
    commit(lone, "only.txt")
    assert main(["--root", str(lone)]) == 0


# --- the entry point ---------------------------------------------------------


def test_the_command_line_exits_non_zero_on_an_unpushed_pin(world):
    """The tests above call `inspect` directly. This is the path CI and a person
    actually run, and wiring it wrong would leave every one of them green while
    the check did nothing.
    """
    parent, child, _ = world
    commit(child, "never-pushed.txt")
    git("add", "child", cwd=parent)
    git("-c", "commit.gpgsign=false", "commit", "-q", "-m", "bump", cwd=parent)

    done = subprocess.run([sys.executable, str(TOOL), "--root", str(parent)],
                          capture_output=True, text=True, encoding="utf-8",
                          errors="replace")
    assert done.returncode == 1, done.stdout + done.stderr
    assert "nobody else could resolve" in done.stderr


def test_json_carries_the_verdict_for_each_pin(world):
    """So a dashboard reads the verdict rather than parsing prose."""
    import json
    parent, _, _ = world
    done = subprocess.run(
        [sys.executable, str(TOOL), "--root", str(parent), "--json"],
        capture_output=True, text=True, encoding="utf-8", errors="replace")
    payload = json.loads(done.stdout)
    assert payload["submodules"][0]["verdict"] == OK
    assert payload["submodules"][0]["path"] == "child"
