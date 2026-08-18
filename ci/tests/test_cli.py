"""Tests for the `qm` governance CLI.

The CLI's whole contract is that it *dispatches* and decides nothing, so the
tests are mostly about what it must not do: form a verdict, change an exit
status, or run somewhere that is not the corpus.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

CI_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(CI_DIR))

import cli  # noqa: E402

CORPUS = CI_DIR.parent


def run(*args: str, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(CI_DIR / "cli.py"), *args],
        capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=str(cwd),
    )


# --- it decides nothing ----------------------------------------------------


def test_the_cli_forms_no_verdict():
    """No document parsing and no child processes. A subcommand that recomputed
    a verdict would be a second definition of a governance rule.

    Asserted on the imports rather than on substrings: the route table names
    `gate-status.json`, and a substring check for "json" fails on a filename
    while a module that genuinely parsed one could import it under an alias.
    """
    import ast

    tree = ast.parse((CI_DIR / "cli.py").read_text(encoding="utf-8"))
    imported = {
        node.module.split(".")[0] if isinstance(node, ast.ImportFrom) and node.module
        else alias.name.split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in getattr(node, "names", [])
    }
    assert not imported & {"json", "yaml", "subprocess", "urllib", "requests"}


def test_the_exit_status_is_the_module_s_own():
    class Module:
        __name__ = "fake"

        @staticmethod
        def main(argv):
            return 42

    assert cli.call_main(Module, []) == 42


def test_a_main_without_argv_still_receives_its_arguments():
    """Two seed scripts read sys.argv themselves. Adapting is the wrapper's job."""
    seen = {}

    class Module:
        __name__ = "fake"

        @staticmethod
        def main():
            seen["argv"] = list(sys.argv)
            return 0

    before = list(sys.argv)
    assert cli.call_main(Module, ["--flag", "value"]) == 0
    assert seen["argv"][1:] == ["--flag", "value"]
    assert sys.argv == before, "sys.argv must be restored"


def test_sys_argv_is_restored_even_when_the_module_raises():
    class Module:
        __name__ = "fake"

        @staticmethod
        def main():
            raise RuntimeError("boom")

    before = list(sys.argv)
    with pytest.raises(RuntimeError):
        cli.call_main(Module, ["x"])
    assert sys.argv == before


def test_it_runs_without_the_package_installed():
    """CI invokes `python ci/cli.py` and installs nothing.

    `uv run qm` installs the package first, so an `import ci.foo` that only
    resolves when installed works locally and fails on the runner -- which is
    exactly how this was found, on the first pull request that let a workflow
    near it.

    `-S` skips `site`, so site-packages is not on the path and the installed
    distribution is invisible. Without the path insertion in cli.py the import
    fails outright.

    Asserted on the import failure rather than on exit 0: the routed command's
    own verdict depends on corpus state, and a test that failed whenever an
    unrelated record went out of pair would be noise dressed as a regression.
    """
    result = subprocess.run(
        [sys.executable, "-S", str(CI_DIR / "cli.py"), "restatements"],
        capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=str(CORPUS),
    )
    assert "ModuleNotFoundError" not in result.stderr, result.stderr
    assert "No module named 'ci'" not in result.stderr, result.stderr


# --- it runs in the corpus, or not at all ----------------------------------


def test_the_corpus_root_is_found_from_a_subdirectory():
    assert cli.corpus_root(CI_DIR) == CORPUS


def test_outside_the_corpus_it_refuses_rather_than_writing_somewhere_else(tmp_path: Path):
    """Every generator path is corpus-relative; running elsewhere writes there."""
    result = run("docs", "check", cwd=tmp_path)
    assert result.returncode == 2
    assert "not inside the QM corpus" in result.stderr


def test_a_directory_with_only_one_marker_is_not_the_corpus(tmp_path: Path):
    """A fork that copied the seed has records/ and no charter."""
    (tmp_path / "records").mkdir()
    assert cli.corpus_root(tmp_path) is None


# --- the surface -----------------------------------------------------------


def test_help_lists_every_command():
    result = run("--help", cwd=CORPUS)
    assert result.returncode == 0
    for command in ("docs", "gates", "tags", "restatements", "slot", "branch",
                    "preflight", "brief"):
        assert command in result.stdout


def test_no_arguments_prints_help_rather_than_doing_something():
    result = run(cwd=CORPUS)
    assert result.returncode == 0
    assert "usage: qm" in result.stdout


def test_an_unknown_command_exits_two_and_says_so():
    result = run("ratify", cwd=CORPUS)
    assert result.returncode == 2
    assert "unknown command 'ratify'" in result.stderr


def test_an_unknown_docs_subcommand_exits_non_zero():
    assert run("docs", "publish", cwd=CORPUS).returncode == 2


def test_every_route_names_a_module_that_exists():
    """A route to a module nobody wrote is a command that fails at the prompt."""
    for command, (module, is_seed, _) in cli.ROUTES.items():
        directory = CORPUS / ("project-seed/ci" if is_seed else "ci")
        assert (directory / f"{module}.py").is_file(), f"{command} -> {module}"
    for command, (module, _) in cli.DOCS_ROUTES.items():
        assert (CORPUS / "ci" / f"{module}.py").is_file(), f"docs {command} -> {module}"


def test_flags_reach_the_underlying_module():
    """`--state` belongs to doc_dashboard, and the CLI must not swallow it."""
    result = run("docs", "states", "--state", "nonsense", cwd=CORPUS)
    assert result.returncode == 2
    assert "vocabulary is closed" in result.stderr
