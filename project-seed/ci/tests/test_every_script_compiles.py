"""Every script in `ci/` is syntactically valid Python.

This runs whenever the suite runs, so nobody has to remember to parse a script
after editing it. It uses `compile` rather than an import: importing a module
runs it, needs every dependency present, and turns a missing optional package
into a syntax failure, while `compile` answers whether the file parses, in a
fork that has installed nothing.

There is one case per property, not one per file: a failure names every
offending file and line in one message.

What this does not check: that a script works, that its imports resolve, or
that it does what its name says. Those are the other tests here; this is the
floor. Parsing deeper than "does it parse" belongs to `codecartographer`, the
org's parsing tool, which a governance gate does not import: a fork that has
not installed it would fail. `docs/ref/ci/gates-and-checks.md` describes the
compile floor.
"""

from __future__ import annotations

from pathlib import Path

SEED_CI = Path(__file__).resolve().parent.parent


def scripts() -> list[Path]:
    """Every Python file a fork runs out of the submodule.

    Sorted so a failure names files in the same order on every machine.
    """
    return sorted(
        path
        for path in SEED_CI.rglob("*.py")
        if "__pycache__" not in path.parts
    )


def test_there_are_scripts_to_check():
    """The glob matches something: a glob that matched nothing would make
    every check below vacuous, and a vacuous check reports green.

    Mutation: point `scripts()` at an empty directory and this fails.
    """
    found = scripts()
    assert len(found) > 5, f"only {len(found)} script(s) found under {SEED_CI}"


def test_every_script_parses():
    """Mutation: introduce a syntax error in any script here and this fails,
    naming it and the line."""
    broken = []
    for script in scripts():
        try:
            compile(script.read_text(encoding="utf-8"), str(script), "exec")
        except SyntaxError as error:
            broken.append(
                f"{script.relative_to(SEED_CI).as_posix()}:{error.lineno}: "
                f"{error.msg}")

    assert not broken, "these do not parse:\n  " + "\n  ".join(broken)


def test_no_script_indents_with_tabs():
    """Tabs mixed with spaces parse in some files and raise `TabError` in
    others, depending on what is above them, so the failure appears in a file
    nobody just edited. A docstring written through a shell can gain a real tab
    from an escaped `\\t`.

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
                f"{script.relative_to(SEED_CI).as_posix()}: line(s) {lines[:5]}")

    assert not offenders, ("these indent with tabs:\n  "
                           + "\n  ".join(offenders))
