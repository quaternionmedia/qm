"""Every runnable module is executed by some test, or says why not.

Tests here are named for their subject rather than their module:
`harness_status.py` is exercised by `test_harness_dashboard.py`, `gate_status.py`
by `test_gate_tooling.py`. Under that convention an untested module and one
tested elsewhere look identical in the directory, so this finds, for every
module with a `main`, a test that runs it.

Execution, not mention: the patterns below all mean *this test runs that code*
(an import, a call to its `main`, or an invocation by filename). A test that
names a module in a comment is not a test of it, and matching the bare name
would inflate the count.

What this cannot do: tell whether the test that runs a module *checks*
anything about it. `qm posture` answers that by mutation; this is the cheaper
floor.

Exemptions carry a reason. A module listed in `UNEXERCISED` is a known gap, not
an excused one, and an entry with no reason fails.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

CI = Path(__file__).resolve().parent.parent
CORPUS = CI.parent

# Modules nothing executes yet, each with why. Shrink this list rather than grow
# it: a module added here rather than tested is a decision somebody writes down,
# which is the point of the reason being mandatory. A module described as having
# "no logic of its own" can still hold a defect only a test catches.
UNEXERCISED: dict[str, str] = {}


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


def test_something_executes_every_runnable_module():
    """One case, every gap: the failure names every uncovered module in one
    message.

    Mutation: delete a module's tests without listing it in `UNEXERCISED` and
    this fails, naming it.
    """
    gaps = []
    for module in runnable():
        relative = module.relative_to(CORPUS).as_posix()
        if relative in UNEXERCISED:
            continue
        if not executes(module):
            gaps.append(relative)

    assert not gaps, (
        "these have a main() and no test runs them:\n  "
        + "\n  ".join(gaps)
        + "\n\nEither add a test, or add each to UNEXERCISED with the reason "
          "-- a gap nobody wrote down is a gap nobody can close."
    )


def test_every_exemption_carries_a_reason():
    """An exemption without a reason is an excuse.

    Mutation: add an entry with an empty reason and this fails.
    """
    for module, reason in UNEXERCISED.items():
        assert len(reason.strip()) > 40, f"{module}: the reason is a label"


def test_no_exemption_names_a_module_that_is_now_tested():
    """An exemption left behind after
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
