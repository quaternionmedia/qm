"""Every script in `ci/` is syntactically valid Python.

**THIS EXISTS BECAUSE IT WAS BEING DONE BY HAND.** After each edit to a script
here, somebody was typing `python -c "import ast; ast.parse(open(...).read())"`
and reading the word `parses`. That check is real and it was correct; what was
wrong is where it lived. A check performed from memory is performed when
somebody remembers, and the person most likely to forget is the one who has just
made a large edit — which is exactly when it matters.

**WHY A TEST AND NOT A COMMAND.** A command is one more thing to know about;
`AGENTS.md` item 16 is the corpus's own finding that a rule which loses on
readership does not govern. This runs whenever anybody runs the suite, which is
before every pull request, and nobody has to be told.

**WHY `compile` AND NOT AN IMPORT.** Importing a module runs it: it would need
every dependency present, would execute module-level work, and would turn a
missing optional package into a syntax failure. `compile` answers exactly the
question being asked — is this parseable — and answers it for a fork that has
installed nothing.

**AND WHY ONE CASE PER PROPERTY, NOT ONE PER FILE.** This was parameterised over
every script: 41 ids for a floor check that has never legitimately failed, and
175 in the corpus twin. A sweep should name every offender in one message rather
than produce one failure per file for a reader to collect one at a time. What is
lost is the filename in the test *id*; it is in the failure message instead,
with the line number, which is where it is more useful.

WHAT THIS DOES NOT CHECK. That a script works, that its imports resolve, or
that it does what its name says. Those are the other tests here. This is the
floor: a file that does not parse cannot be any of the above, and it fails in a
way that is otherwise found by a person at the worst moment.

**DEEPER PARSING IS NOT THIS FILE'S JOB, AND NOT THIS REPOSITORY'S.**
`codecartographer` is the org's parsing and abstraction tool — ASTs, lexicons,
abstraction layers, graphs. It is a *project*, and this is the *governance
corpus* those projects adopt: a gate here that imported a project would invert
the dependency and would fail in every fork that has not installed it. So the
rule is the boundary, not the technique — syntax questions a fork must answer
alone use the standard library, and anything richer than "does it parse" belongs
in the tool built for it.
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
    """**THE GUARD ON THE GUARD.** A glob that matched nothing would make every
    check below vacuous, and a vacuous check reports green — the empty-suite
    failure this corpus keeps finding.

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
    others, depending on what is above them — so the failure appears in a file
    nobody just edited.

    Not hypothetical: a docstring written through a shell gained a real tab from
    an escaped `\\t` five times in one session.

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
