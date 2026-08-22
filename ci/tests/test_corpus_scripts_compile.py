"""Every script in this corpus's own `ci/` is syntactically valid Python.

The corpus half of `project-seed/ci/tests/test_every_script_compiles.py`, which
covers what forks run. Same reasoning, different directory: a fork never sees
`ci/`, and this corpus never runs its own gates out of the submodule.

**WHY TWO FILES RATHER THAN ONE PARAMETERISED OVER BOTH ROOTS.** A fork gets the
seed suite and nothing else. A single file living in `ci/tests` would leave every
fork unchecked; a single file in `project-seed/ci/tests` reaching up into `ci/`
would fail in every fork, where that directory does not exist.

**AND WHY ONE CASE PER PROPERTY RATHER THAN ONE PER FILE.** This began as
`@pytest.mark.parametrize` over every script -- 175 cases in one file, an eighth
of the corpus's whole test count, for a floor check that has never legitimately
failed. Two things were wrong with that:

- **175 ids is noise.** A reader scanning the suite learns nothing from
  `test_the_script_parses[disk_status.py]` repeated eighty-seven times.
- **A sweep should report every offender at once.** Parameterised, three broken
  files are three separate failures a reader collects one at a time. Collapsed,
  the assertion names all three in one message, which is what somebody fixing
  them actually wants.

What is lost is the failing filename in the *test id*. It is in the failure
message instead, with the line number, which is where it is more useful.
"""

from __future__ import annotations

from pathlib import Path

CI = Path(__file__).resolve().parent.parent


def scripts() -> list[Path]:
    """Every Python file this corpus runs, excluding the seed (covered there)."""
    return sorted(
        path
        for path in CI.rglob("*.py")
        if "__pycache__" not in path.parts
    )


def test_there_are_scripts_to_check():
    """A glob that matched nothing would make every check below vacuous, and a
    vacuous check reports green.

    Mutation: point `scripts()` at an empty directory and this fails.
    """
    found = scripts()
    assert len(found) > 10, f"only {len(found)} script(s) found under {CI}"


def test_every_script_parses():
    """Mutation: introduce a syntax error in any script here and this fails,
    naming the file and the line."""
    broken = []
    for script in scripts():
        try:
            compile(script.read_text(encoding="utf-8"), str(script), "exec")
        except SyntaxError as error:
            broken.append(f"{script.relative_to(CI).as_posix()}:{error.lineno}: "
                          f"{error.msg}")

    assert not broken, "these do not parse:\n  " + "\n  ".join(broken)


def test_no_script_indents_with_tabs():
    """A real tab reached a docstring here through an escaped `\\t` in a shell
    heredoc, five times in one session. Tabs mixed with spaces parse in some
    files and raise `TabError` in others depending on what is above them, so the
    failure appears in a file nobody just edited.

    Mutation: put a tab at the start of an indented line and this fails.
    """
    offenders = []
    for script in scripts():
        lines = [
            number
            for number, line in enumerate(
                script.read_text(encoding="utf-8").splitlines(), start=1)
            if line[: len(line) - len(line.lstrip())].count("\t")
        ]
        if lines:
            offenders.append(
                f"{script.relative_to(CI).as_posix()}: line(s) {lines[:5]}")

    assert not offenders, ("these indent with tabs:\n  "
                           + "\n  ".join(offenders))
