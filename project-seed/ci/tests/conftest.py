"""Fixtures for the CI tooling's own tests.

These build real git repositories in a temp directory rather than mocking git.
The tools under test are almost entirely *about* git — what a merge-base is,
what a submodule pin points at, what a diff hunk looks like when a line is only
removed — and a mock of git would encode the same misunderstanding the tool
does, then agree with it.

That is not hypothetical. Every defect these tests exist for was a tool that
was internally consistent and wrong about git: an append-only check that asked
a superproject for a diff of a path inside a submodule, a ref qualifier whose
condition could never be true, a runner that used a different shell mode than
the one it was imitating. A mock would have passed all three.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

CI_DIR = Path(__file__).resolve().parent.parent
ENV = {
    **os.environ,
    "GIT_AUTHOR_NAME": "Test",
    "GIT_AUTHOR_EMAIL": "test@example.invalid",
    "GIT_COMMITTER_NAME": "Test",
    "GIT_COMMITTER_EMAIL": "test@example.invalid",
    "GIT_CONFIG_GLOBAL": os.devnull,
    "GIT_CONFIG_SYSTEM": os.devnull,
}


def git(repo: Path, *args: str) -> str:
    """Run git in `repo`, failing loudly. Never returns a silent empty string."""
    result = subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, text=True, env=ENV
    )
    if result.returncode != 0:
        raise AssertionError(
            f"git {' '.join(args)} failed in {repo}:\n{result.stdout}\n{result.stderr}"
        )
    return result.stdout.strip()


def run_tool(name: str, *args: str, cwd: Path) -> subprocess.CompletedProcess:
    """Invoke one of the seed CI tools as a subprocess, as CI does.

    Deliberately not an import-and-call: these tools are entry points whose exit
    status is the contract, and a check that reports the right text with the
    wrong exit code enforces nothing.

    The decoding is pinned to UTF-8 because the tools print this corpus's prose,
    which is full of em dashes, and because pull request titles carry whatever
    their author typed. Left to the platform default, a Windows run raises
    inside subprocess's reader thread and hands back `stdout=None` — so the
    assertion that fails is about a tool that ran perfectly.
    """
    return subprocess.run(
        [sys.executable, str(CI_DIR / name), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=str(cwd),
        env=ENV,
    )


def commit_all(repo: Path, message: str) -> str:
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "--allow-empty", "-m", message)
    return git(repo, "rev-parse", "HEAD")


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def record(status: str = "Proposed", body: str = "Context body line.\n") -> str:
    """A record with the header table shape the lint parses."""
    return (
        "# QM-XXXX — A Record\n\n"
        "| | |\n|---|---|\n"
        f"| **Status** | {status} |\n"
        "| **Date** | 2026-01-01 |\n\n"
        "## Context\n\n"
        f"{body}\n"
        "## Amendments\n\n*None.*\n"
    )


def index_for(numbers: list[int]) -> str:
    rows = "\n".join(f"| {n:04d} | A Record | Accepted | 2026-01-01 |" for n in numbers)
    return "| # | Title | Status | Date |\n|---|---|---|---|\n" + rows + "\n"


@pytest.fixture(scope="session")
def _repo_template(tmp_path_factory) -> Path:
    """One initialised repository, built once for the whole session.

    **BUILT ONCE AND COPIED, NOT BUILT PER TEST.** Ninety-odd tests take the
    `repo` fixture, and each build cost four `git` subprocesses -- init, remote
    add, add, commit. Measured on this machine that is about a sixth of a second
    per test, most of it process start, and it bought every test an identical
    repository.

    A git repository is a directory; copying one is a filesystem operation and
    costs a fraction of spawning git four times. The one thing a copy does not
    carry correctly is `origin`, which holds the *template's* absolute path --
    so `repo` rewrites it. That is one git call instead of four.
    """
    r = tmp_path_factory.mktemp("template") / "repo"
    r.mkdir()
    git(r, "init", "-q", "-b", "main")
    # A remote named `origin`, because actions/checkout always configures one
    # and the tools' ref handling is remote-list-dependent by design: a prefix
    # is only stripped when it names a remote that exists. A fixture without a
    # remote tests a configuration CI never has, and an earlier version of this
    # file did exactly that, then blamed the tool.
    git(r, "remote", "add", "origin", str(r))
    write(r / "README.md", index_for([]))
    (r / "records").mkdir()
    write(r / "records" / ".keep", "")
    commit_all(r, "init")
    return r


@pytest.fixture
def repo(tmp_path: Path, _repo_template: Path) -> Path:
    """An initialised repo with one commit, on branch `main`.

    A copy of the session template. Every test still gets its own repository on
    its own path — the sharing is of the *construction*, never of the state,
    and a test that commits into this one cannot be seen by any other.
    """
    r = tmp_path / "repo"
    shutil.copytree(_repo_template, r)
    # `origin` points at the template's path after a copy. Left alone, a test
    # that fetches or compares against `origin/` would silently read another
    # test's repository — which is exactly the cross-contamination a per-test
    # fixture exists to prevent.
    git(r, "remote", "set-url", "origin", str(r))
    return r
