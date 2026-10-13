"""The placeholder gate, which runs in every fork and had never been run here.

**A SEED FILE THAT NOTHING TESTS IS THE WORST KIND.** Every forking project
executes this out of the governance submodule, so a defect here is a defect in
twelve repositories at once — and `uv run qm posture` found it by asking which
modules no test executes. It had a docstring, a `main`, a place in the workflows,
and nothing had ever watched it refuse or pass.

THE TEST WORTH READING IS THE LAST ONE: a check that examined nothing must not
report clean. Everything above it is the rule; that one is the rule about the
rule, and it is the failure this whole corpus keeps rediscovering.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from conftest import run_tool, write


def seed_and_copy(tmp_path: Path, seed_text: str, copy_text: str,
                  name: str = "README.md") -> tuple[Path, Path]:
    """A seed original and the copy a project made of it."""
    seed_dir = tmp_path / "seed"
    copy_dir = tmp_path / "copy"
    write(seed_dir / name, seed_text)
    write(copy_dir / name, copy_text)
    return seed_dir, copy_dir


def run(tmp_path: Path, seed_dir: Path, copy_dir: Path, *extra: str):
    return run_tool("check_placeholders.py", "--seed", str(seed_dir),
                    "--copy", str(copy_dir), *extra, cwd=tmp_path)


# --- the rule -----------------------------------------------------------------


def test_a_copy_that_kept_the_placeholder_is_refused(tmp_path: Path):
    """THE ONE THAT MATTERS.

    Somebody opens `adr/README.md` on their project, reads "this project's own
    dedicated branch (`project/<name>`)", and learns nothing about which branch
    that is. The document is answering a question it was supposed to have
    answered.

    Mutation: return no failures when a copy keeps a declared placeholder and
    this fails.
    """
    seed, copy = seed_and_copy(
        tmp_path,
        "The branch is `project/<name>`.\n",
        "The branch is `project/<name>`.\n")
    result = run(tmp_path, seed, copy)

    assert result.returncode != 0
    said = result.stdout + result.stderr
    assert "still carries the placeholder" in said
    assert "being shown a template" in said


def test_a_copy_that_substituted_the_placeholder_passes(tmp_path: Path):
    """The whole point: the gate must be satisfiable by doing the right thing.

    Mutation: fail whenever the seed declares a placeholder and this fails.
    """
    seed, copy = seed_and_copy(
        tmp_path,
        "The branch is `project/<name>`.\n",
        "The branch is `project/datum`.\n")
    assert run(tmp_path, seed, copy).returncode == 0


def test_generic_prose_is_never_flagged(tmp_path: Path):
    """**THE REASON THERE IS NO ALLOWLIST.** `records/` saying "a
    `project/<name>` branch is never merged into `main`" is a statement about
    the namespace, not about one project — and no seed file is its source.

    A placeholder is a defect in a copy only if the *seed source of that copy*
    also has it.

    Mutation: flag every `<name>` regardless of the seed and this fails.
    """
    seed_dir = tmp_path / "seed"
    copy_dir = tmp_path / "copy"
    # The seed for this file declares nothing.
    write(seed_dir / "README.md", "Nothing templated here.\n")
    write(copy_dir / "README.md",
          "A `project/<name>` branch is never merged into `main`.\n")
    assert run(tmp_path, seed_dir, copy_dir).returncode == 0


def test_a_file_the_project_never_copied_is_not_its_problem(tmp_path: Path):
    """Pairing is by path. A seed file with no copy is not a finding about the
    project that did not take it."""
    seed_dir = tmp_path / "seed"
    copy_dir = tmp_path / "copy"
    write(seed_dir / "taken.md", "kept `<name>`\n")
    write(seed_dir / "not-taken.md", "also `<name>`\n")
    write(copy_dir / "taken.md", "kept `datum`\n")
    assert run(tmp_path, seed_dir, copy_dir).returncode == 0


def test_the_seed_banner_itself_is_not_a_finding(tmp_path: Path):
    """A copy that kept the SEED FILE banner is carrying an explanation, not a
    template — the banner is stripped before the body is read.

    Mutation: stop stripping the banner and this fails.
    """
    seed, copy = seed_and_copy(
        tmp_path,
        "<!-- SEED FILE: replace `<name>` -->\nThe branch is `project/<name>`.\n",
        "<!-- SEED FILE: replace `<name>` -->\nThe branch is `project/datum`.\n")
    assert run(tmp_path, seed, copy).returncode == 0


# --- what it tells the person who has to fix it -------------------------------


def test_it_names_the_file_the_line_and_the_seed_it_came_from(tmp_path: Path):
    """A finding that says only "a placeholder exists" leaves somebody grepping
    twelve repositories."""
    seed, copy = seed_and_copy(
        tmp_path,
        "line one\nThe branch is `project/<name>`.\n",
        "line one\nThe branch is `project/<name>`.\n")
    said = run(tmp_path, seed, copy).stdout + run(tmp_path, seed, copy).stderr

    assert "README.md:2" in said, said
    assert "COPY of" in said


def test_an_instance_name_becomes_the_suggested_substitution(tmp_path: Path):
    """Telling somebody to substitute *something* is worse than telling them
    what.

    Mutation: ignore `--instance` and this fails.
    """
    seed, copy = seed_and_copy(
        tmp_path,
        "`project/<name>`\n", "`project/<name>`\n")
    result = run(tmp_path, seed, copy, "--instance", "datum")
    said = result.stdout + result.stderr
    assert "<name> -> 'datum'" in said


def test_without_an_instance_it_still_says_what_to_do(tmp_path: Path):
    seed, copy = seed_and_copy(tmp_path, "`<name>`\n", "`<name>`\n")
    said = run(tmp_path, seed, copy).stdout + run(tmp_path, seed, copy).stderr
    assert "this project's own name" in said


# --- a check that examined nothing must not report clean ----------------------


def test_directories_that_pair_with_nothing_are_refused(tmp_path: Path):
    """**THE RULE ABOUT THE RULE.**

    Point this at the wrong directories and every file pairs with nothing, so
    every file passes, so the gate reports clean — while checking zero files.
    That is the exact shape this corpus keeps rediscovering: a green result
    measuring less than the reader thinks.

    Mutation: drop the `paired == 0` branch and this fails.
    """
    seed_dir = tmp_path / "seed"
    copy_dir = tmp_path / "copy"
    write(seed_dir / "a.md", "`<name>`\n")
    write(copy_dir / "somewhere-else.md", "`<name>`\n")

    result = run(tmp_path, seed_dir, copy_dir)
    assert result.returncode != 0
    said = result.stdout + result.stderr
    assert "must not report clean" in said


@pytest.mark.parametrize("missing", ["seed", "copy"])
def test_a_directory_that_is_not_there_is_named(tmp_path: Path, missing: str):
    """A path typo and a clean run must not look the same."""
    seed_dir = tmp_path / "seed"
    copy_dir = tmp_path / "copy"
    write(seed_dir / "a.md", "`<name>`\n")
    write(copy_dir / "a.md", "`datum`\n")
    (seed_dir if missing == "seed" else copy_dir).rename(
        tmp_path / f"{missing}-moved")

    result = run(tmp_path, seed_dir, copy_dir)
    assert result.returncode != 0
    assert "not a directory" in (result.stdout + result.stderr)
