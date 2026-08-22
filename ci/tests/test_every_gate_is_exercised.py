"""Every runnable module is executed by some test, or says why not.

**THE GAP THIS CLOSES IS NOT "UNTESTED MODULES" — IT IS THAT UNTESTED AND
TESTED-ELSEWHERE LOOKED IDENTICAL.** Tests here are named for their subject
rather than their module: `harness_status.py` is exercised by
`test_harness_dashboard.py`, `gate_status.py` by `test_gate_tooling.py`. That is
a good convention and it costs one thing — there is no way to look at a module
and tell whether anything runs it. Seventeen modules had no same-named test
file; thirteen were thoroughly covered under another name and four were covered
by nothing, and no reading of the directory could separate them.

`uv run qm posture` surfaced the first of them by trying to mutate a module
whose tests it could not find, which is the shape of finding this corpus keeps
recommending: the tool asked a question nobody had asked.

**EXECUTION, NOT MENTION.** A test that names a module in a comment is not a
test of it. The patterns below all mean *this test runs that code*: an import, a
call to its `main`, or an invocation by filename. Matching on the bare name
inflated the count by one here and would inflate it more as the corpus grows —
and an inflated coverage figure is worse than none, because it hides exactly the
module it claims.

**WHAT THIS CANNOT DO.** Tell whether the test that runs a module *checks*
anything about it. `qm posture` answers that by mutation, and charter P16 is why
the two are different questions. This is the cheaper floor: is there anything at
all.

EXEMPTIONS CARRY A REASON. A module listed in `UNEXERCISED` is a known gap, not
an excused one — an entry with no reason fails, because "unknown is a value,
never zero" applies to the corpus's own tooling before it applies to anything
else.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

CI = Path(__file__).resolve().parent.parent
CORPUS = CI.parent

# Modules nothing executes yet, each with why. **Shrink this list; do not grow
# it.** A new module added here rather than tested is a decision somebody should
# have to write down, which is the point of the reason being mandatory.
UNEXERCISED: dict[str, str] = {
    "ci/devloop.py": (
        "a developer convenience that shells out to the other gates; it has no "
        "logic of its own and its parts are tested where they live"
    ),
}


def runnable() -> list[Path]:
    """Every module in `ci/` with a `main`, which is what makes it runnable."""
    return sorted(
        path
        for path in CI.glob("*.py")
        if path.stem != "cli"
        and "__pycache__" not in path.parts
        and re.search(r"^def main", path.read_text(encoding="utf-8"), re.M)
    )


def executes(module: Path) -> list[str]:
    """Test files that actually run `module`, by any of the ways it can be run."""
    stem = re.escape(module.stem)
    pattern = re.compile(
        rf"(import\s+{stem}\b"          # import gate
        rf"|from\s+{stem}\s+import"     # from gate import x
        rf"|from\s+\S*\b{stem}\s+import"
        rf"|['\"]{stem}\.py['\"]"       # invoked by filename
        rf"|{stem}\.main\("             # main() called directly
        rf"|run_tool\(\s*['\"]{stem}"   # the seed helper
        rf"|import_module\(['\"]{stem})"
    )
    found = []
    tests = CI / "tests"
    named = tests / f"test_{module.stem}.py"
    if named.is_file():
        found.append(named.name)
    for candidate in sorted(tests.glob("test_*.py")):
        if candidate.name in found:
            continue
        if pattern.search(candidate.read_text(encoding="utf-8")):
            found.append(candidate.name)
    return found


def test_there_are_modules_to_check():
    """A glob that matched nothing would make every case below vanish.

    Mutation: point `runnable()` at an empty directory and this fails.
    """
    assert len(runnable()) > 20, f"only {len(runnable())} runnable module(s)"


@pytest.mark.parametrize("module", runnable(),
                         ids=lambda p: p.relative_to(CORPUS).as_posix())
def test_something_executes_the_module(module: Path):
    """One case per module, so a gap names the module rather than the sweep.

    Mutation: delete a module's tests without listing it in `UNEXERCISED` and
    this fails.
    """
    relative = module.relative_to(CORPUS).as_posix()
    if relative in UNEXERCISED:
        pytest.skip(f"known gap: {UNEXERCISED[relative]}")
    assert executes(module), (
        f"{relative} has a main() and no test runs it. Either add a test, or "
        f"add it to UNEXERCISED with the reason — a gap nobody wrote down is "
        f"a gap nobody can close."
    )


def test_every_exemption_carries_a_reason():
    """An exemption without a reason is an excuse.

    Mutation: add an entry with an empty reason and this fails.
    """
    for module, reason in UNEXERCISED.items():
        assert len(reason.strip()) > 40, f"{module}: the reason is a label"


def test_no_exemption_names_a_module_that_is_now_tested():
    """**THE ONE THAT KEEPS THE LIST SHRINKING.** An exemption left behind after
    somebody wrote the test turns into a permanent hole: the module is skipped
    forever and nobody notices it is covered.

    Mutation: write a test for an exempted module without removing its entry
    and this fails.
    """
    stale = [
        module for module in UNEXERCISED
        if (CORPUS / module).is_file() and executes(CORPUS / module)
    ]
    assert not stale, (
        f"these are exempted and now tested; remove them from UNEXERCISED: "
        f"{stale}"
    )


def test_no_exemption_names_a_module_that_no_longer_exists():
    """A list that outlives its subjects stops being read."""
    missing = [m for m in UNEXERCISED if not (CORPUS / m).is_file()]
    assert not missing, f"UNEXERCISED names modules that are gone: {missing}"
