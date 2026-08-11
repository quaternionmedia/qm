"""Fixtures for the org-level governance tooling's tests.

NOT NAMED conftest.py, deliberately. pytest's default import mode puts each
test directory on sys.path, so two conftest.py files in one run collide on the
module name `conftest` and whichever sorts first wins -- the seed suite's
`from conftest import commit_all` then resolves to this file and fails to
import. Each suite passed alone; only running both together showed it, which
is what project-seed/ci/run_workflows_locally.py exists to make happen before
CI does it instead.

Real git repositories in a temp directory, never mocks -- the same reasoning as
project-seed/ci/tests/conftest.py, and for a tool that is even more thoroughly
*about* git than those. Every wrong answer this generator produced while it was
being written was a wrong belief about git: that `ls-tree` recurses, that any
merge commit is a propagation, that the corpus's own merges are not reachable
from a branch that took them. A mock encodes the belief and then agrees with it.

The GitHub layer is exercised through `--offline`, which is not a shortcut: it
is the configuration a fork pull request runs in, so the offline path is the one
most likely to be live in CI and the one whose unknowns must be visible.
"""

from __future__ import annotations

import os
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
    "GIT_AUTHOR_DATE": "2026-01-01T00:00:00+00:00",
    "GIT_COMMITTER_DATE": "2026-01-01T00:00:00+00:00",
    "GIT_CONFIG_GLOBAL": os.devnull,
    "GIT_CONFIG_SYSTEM": os.devnull,
    # Pinned so a document generated in a test is byte-stable. The generator
    # reads this; nothing else does. Its absence in real use is the point --
    # a real document must carry the real moment it was made.
    "GOVERNANCE_STATUS_NOW": "2026-01-01T00:00:00Z",
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


def run_tool(name: str, *args: str, cwd: Path, env: dict | None = None):
    """Invoke a tool as a subprocess, as CI does.

    Not an import-and-call: these are entry points whose exit status is the
    contract, and a check that prints the right words with the wrong exit code
    enforces nothing.
    """
    return subprocess.run(
        [sys.executable, str(CI_DIR / name), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=str(cwd),
        env={**ENV, **(env or {})},
    )


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def commit(repo: Path, message: str) -> str:
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "--allow-empty", "-m", message)
    return git(repo, "rev-parse", "HEAD")


TEMPLATE = "# ADR-XXXX — <title>\n\nSeed template body.\n"
SEED_README = (
    "# Architecture Decision Records\n\n"
    "<!-- SEED FILE: copy verbatim into this project's own branch\n"
    "     (project/<name>, created from main) and delete this comment. -->\n\n"
    "The project's own branch (`project/<name>`) carries these.\n"
)


def record(status: str = "Proposed", title: str = "A Record") -> str:
    return (
        f"# QM-XXXX — {title}\n\n"
        "| | |\n|---|---|\n"
        f"| **Status** | {status} |\n"
        "| **Date** | 2026-01-01 |\n\n"
        "## Context\n\nBody.\n\n## Amendments\n\n*None.*\n"
    )


@pytest.fixture
def corpus(tmp_path: Path) -> Path:
    """A corpus-shaped repository on `main` with the seed and two records."""
    repo = tmp_path / "corpus"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    write(repo / "project-seed" / "adr" / "TEMPLATE.md", TEMPLATE)
    write(repo / "project-seed" / "adr" / "README.md", SEED_README)
    write(repo / "records" / "DRAFT-one.md", record())
    write(repo / "records" / "DRAFT-two.md", record())
    commit(repo, "corpus: seed and two records")
    return repo


def add_project(repo: Path, name: str, *, template: str | None = None,
                readme: str | None = None, records: dict[str, str] | None = None) -> str:
    """Branch project/<name> off main and lay down a copied seed."""
    start = git(repo, "rev-parse", "main")
    git(repo, "checkout", "-q", "-b", f"project/{name}", start)
    write(repo / "adr" / "TEMPLATE.md", TEMPLATE if template is None else template)
    write(
        repo / "adr" / "README.md",
        readme if readme is not None else SEED_README.split("<!--")[0] + "Project records.\n",
    )
    for filename, text in (records or {"DRAFT-scope.md": record()}).items():
        write(repo / "adr" / filename, text)
    tip = commit(repo, f"{name}: adopt the seed")
    git(repo, "checkout", "-q", "main")
    return tip


def advance_corpus(repo: Path, n: int = 1, touch_seed: bool = False) -> str:
    """Move main forward, optionally changing the seed template as it goes."""
    git(repo, "checkout", "-q", "main")
    for i in range(n):
        if touch_seed:
            write(repo / "project-seed" / "adr" / "TEMPLATE.md", TEMPLATE + f"Line {i}.\n")
        else:
            write(repo / "records" / f"DRAFT-extra-{i}.md", record())
        commit(repo, f"corpus: change {i}")
    return git(repo, "rev-parse", "main")


def with_origin(repo: Path) -> Path:
    """Give the repo an `origin` pointing at itself and populate remote refs.

    actions/checkout always configures one, and the fallback to local branches
    exists for clones that have none. Both paths need a fixture; a suite that
    only ever exercises the fallback is testing the configuration CI never has.
    """
    git(repo, "remote", "add", "origin", str(repo))
    git(repo, "fetch", "-q", "origin")
    return repo
