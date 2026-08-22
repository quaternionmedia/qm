"""Every script in this corpus's own `ci/` is syntactically valid Python.

The corpus half of `project-seed/ci/tests/test_every_script_compiles.py`, which
covers what forks run. Same reasoning, different directory: a fork never sees
`ci/`, and this corpus never runs its own gates out of the submodule.

**WHY TWO FILES RATHER THAN ONE PARAMETERISED OVER BOTH ROOTS.** A fork gets the
seed suite and nothing else. A single file living in `ci/tests` would leave every
fork unchecked; a single file in `project-seed/ci/tests` reaching up into `ci/`
would fail in every fork, where that directory does not exist. The duplication is
four lines and the alternative is a check that is wrong in one of the two places
it runs.
"""

from __future__ import annotations

from pathlib import Path

import pytest

CI = Path(__file__).resolve().parent.parent


def scripts() -> list[Path]:
    """Every Python file this corpus runs, excluding the seed (covered there)."""
    return sorted(
        path
        for path in CI.rglob("*.py")
        if "__pycache__" not in path.parts
    )


def test_there_are_scripts_to_check():
    """A glob that matched nothing would make every case below vanish, and a
    file with no cases passes silently.

    Mutation: point `scripts()` at an empty directory and this fails.
    """
    found = scripts()
    assert len(found) > 10, f"only {len(found)} script(s) found under {CI}"


@pytest.mark.parametrize("script", scripts(),
                         ids=lambda p: p.relative_to(CI).as_posix())
def test_the_script_parses(script: Path):
    """Mutation: introduce a syntax error in any script here and this fails."""
    try:
        compile(script.read_text(encoding="utf-8"), str(script), "exec")
    except SyntaxError as error:
        pytest.fail(f"{script.relative_to(CI).as_posix()} does not parse: "
                    f"line {error.lineno}, {error.msg}")


@pytest.mark.parametrize("script", scripts(),
                         ids=lambda p: p.relative_to(CI).as_posix())
def test_the_script_has_no_stray_tabs_in_indentation(script: Path):
    """A real tab reached a docstring here through an escaped `\t` in a shell
    heredoc, and the file failed to import with a message about indentation.

    Mutation: put a tab at the start of an indented line and this fails.
    """
    offenders = [
        number
        for number, line in enumerate(
            script.read_text(encoding="utf-8").splitlines(), start=1)
        if line[: len(line) - len(line.lstrip())].count("\t")
    ]
    assert not offenders, (
        f"{script.relative_to(CI).as_posix()} indents with tabs on "
        f"line(s) {offenders[:5]}")
