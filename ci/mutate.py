#!/usr/bin/env python3
"""Break a module on purpose and see whether its tests notice.

    uv run qm mutate ci/rulesets.py
    uv run qm mutate ci/rulesets.py --list          # the mutants, without running
    uv run qm mutate ci/rulesets.py --check         # exit non-zero on a survivor

WHY A ROUTE AND NOT A SCRIPT. `ci/lane-registry.yaml` records it plainly under
`development-loop`: every mutation result this corpus has quoted was produced by
an ad-hoc script written into a scratchpad and thrown away, which is the same
defect as a hand-run check reported as CI -- a number nobody else can reproduce.
This is the reproduction. It is a route so that the claim "these tests
discriminate" carries a command.

WHAT A SURVIVING MUTANT MEANS. The module was changed and every test still
passed. Either a test is missing, or the change makes no behavioural difference
-- an *equivalent* mutant, which is a normal outcome and not a defect. This tool
cannot tell the two apart, so it reports survivors and judges none of them.

WHAT IT CANNOT SEE.

  * Any defect no textual operator below expresses. The operators are a floor.
  * Whether the test that killed a mutant is the test that should have. A suite
    can kill a mutant by accident, through an unrelated assertion or a crash.
  * A module whose tests it was not pointed at. `--tests` defaults to the
    obvious filename and says so; a module with tests elsewhere reports as
    having none rather than silently running a smaller suite.

WHY IT COPIES RATHER THAN EDITS IN PLACE. A tool that mutates a tracked file and
restores it afterwards leaves the file broken if it is interrupted, and this
corpus has already had one aside-and-back move that would have done real damage
had the middle command failed. Every mutant is run against a copy of the working
tree in a temporary directory, staged once per sweep. See `stage` for what is
left out and why it is the whole tree rather than `ci/`.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# One-for-one textual substitutions. Each is a change that a correct test suite
# should notice. `return None` -> `return []` is first because it is the one
# this harness was written for: an empty list is a real answer -- "nothing is
# applied" -- and a failed call that returns one reports an unreachable host as
# an unprotected repository.
OPERATORS: tuple[tuple[str, str], ...] = (
    ("return None", "return []"),
    ("return []", "return None"),
    ("is not None", "is None"),
    ("is None", "is not None"),
    ("!=", "=="),
    ("==", "!="),
    (" not ", " "),
    (" and ", " or "),
    (" or ", " and "),
    ("True", "False"),
    ("False", "True"),
    (" >= ", " > "),
    (" <= ", " < "),
)


@dataclass(frozen=True)
class Mutant:
    line: int
    was: str
    now: str
    text: str

    def label(self) -> str:
        return f"line {self.line:>4}  {self.was!r} -> {self.now!r}   {self.text.strip()[:60]}"


def code_lines(source: str) -> set[int]:
    """The 1-indexed lines that are code, not comment and not docstring.

    Mutating a docstring produces a mutant no test can kill and no reader
    should have to dismiss. The scan is a toggle on triple quotes, which is
    enough for this corpus's style and wrong for a line holding two of them --
    stated here rather than discovered by someone reading a strange survivor.
    """
    live: set[int] = set()
    in_doc = False
    for number, line in enumerate(source.splitlines(), start=1):
        stripped = line.strip()
        fences = stripped.count('"""') + stripped.count("'''")
        if in_doc:
            if fences:
                in_doc = False
            continue
        if fences == 1:
            in_doc = True
            continue
        if not stripped or stripped.startswith("#") or fences >= 2:
            continue
        live.add(number)
    return live


def mutants(source: str) -> list[Mutant]:
    """Every single-substitution mutant of this source, in file order.

    One substitution per mutant, and only the first occurrence on a line: two
    changes at once make a survivor impossible to attribute.
    """
    live = code_lines(source)
    found: list[Mutant] = []
    for number, line in enumerate(source.splitlines(), start=1):
        if number not in live:
            continue
        for was, now in OPERATORS:
            if was in line:
                found.append(Mutant(number, was, now, line))
    return found


def apply_mutant(source: str, mutant: Mutant) -> str:
    lines = source.splitlines(keepends=True)
    target = lines[mutant.line - 1]
    lines[mutant.line - 1] = target.replace(mutant.was, mutant.now, 1)
    return "".join(lines)


def stage(workdir: Path, root: Path = ROOT) -> Path:
    """A byte-for-byte copy of the working tree, minus history and caches.

    THE WHOLE TREE, NOT JUST `ci/`. Staging only the tooling directory was the
    first shape of this and it was wrong: a test that reads a registry, a
    record, or a curriculum outside `ci/` fails in the staged copy, the baseline
    goes red, and the sweep refuses to score a suite that is fine. It costs one
    copy per sweep rather than one per mutant, because only the module under
    test is rewritten inside the loop.

    `.git` IS COPIED, and that was learned the same way. A test exercising a
    real `git rev-parse` finds no repository in a tree staged without it, the
    baseline goes red, and the sweep refuses to score a suite that is fine. It
    is the largest thing copied and it is copied once per sweep.

    Binary copies. A text-mode copy on Windows rewrites every line ending, and
    the diff then measures the copier. Symlinks are followed rather than
    recreated -- `CLAUDE.md` and friends are real symlinks here, and creating
    one on Windows needs a privilege a test run should not require.
    """
    destination = workdir / "tree"
    shutil.copytree(
        root, destination, symlinks=False, ignore_dangling_symlinks=True,
        ignore=shutil.ignore_patterns(
            "site", "__pycache__", "*.pyc", ".venv", "node_modules",
            ".pytest_cache", ".mypy_cache", ".ruff_cache",
        ),
    )
    return destination


def run_tests(tests: Path, workdir: Path) -> subprocess.CompletedProcess:
    """One pytest run, with no bytecode written and no cache read.

    `-B` IS LOad-BEARING, and finding out why cost a session. CPython validates
    a cached `.pyc` against the source's size and its mtime *truncated to whole
    seconds*. A mutant that swaps `==` for `!=` changes neither: mutants written
    within the same second are byte-identical to the cache's key, so the second
    one imports the first one's bytecode and the harness scores a run of code
    that was never executed. It shows up as a mutant that is killed on one sweep
    and survives on the next, over an unchanged tree, which reads as flakiness
    rather than as a wrong number.
    """
    return subprocess.run(
        [sys.executable, "-B", "-m", "pytest", str(tests), "-q", "-x",
         "-p", "no:cacheprovider"],
        cwd=str(workdir), capture_output=True, text=True,
        encoding="utf-8", errors="replace",
    )


def default_tests(module: Path, root: Path = ROOT) -> Path:
    return root / "ci" / "tests" / f"test_{module.stem}.py"


def sweep(module: Path, tests: Path, root: Path = ROOT, out=print):
    """Run every mutant. Returns (survivors, errored, total).

    Three outcomes, not two. A run that neither passed nor failed produced no
    verdict about its mutant, and folding it into either bucket is a number
    stating something nobody measured.
    """
    source = module.read_text(encoding="utf-8")
    candidates = mutants(source)
    relative_module = module.relative_to(root).as_posix()
    relative_tests = tests.relative_to(root).as_posix()

    with tempfile.TemporaryDirectory() as raw:
        workdir = Path(raw)
        staged = stage(workdir, root)
        staged_module = staged / relative_module
        staged_tests = staged / relative_tests

        # The baseline, asserted rather than assumed. A suite that is already
        # red kills every mutant for free and the sweep proves nothing -- this
        # corpus has published one mutation result produced exactly that way.
        baseline = run_tests(staged_tests, staged)
        if baseline.returncode != 0:
            out(f"{relative_tests} does not pass unmutated. Nothing was measured.")
            out(baseline.stdout.strip()[-2000:])
            raise SystemExit(2)
        out(f"baseline green: {relative_tests} passes against {relative_module}")
        out(f"{len(candidates)} mutants\n")

        survivors: list[Mutant] = []
        errored: list[tuple[Mutant, int]] = []
        for index, mutant in enumerate(candidates, start=1):
            mutated = apply_mutant(source, mutant)
            # A mutation that does not change the text makes its mutant
            # unkillable, and the tool then reports a suite as weak when the
            # suite is fine -- the stale-bytecode defect inverted. Asserted
            # rather than assumed, because both failures look like a survivor.
            if mutated == source:
                out(f"mutant {index} changed nothing: {mutant.label()}")
                raise SystemExit(2)
            staged_module.write_text(mutated, encoding="utf-8")
            if staged_module.read_text(encoding="utf-8") != mutated:
                out(f"mutant {index} did not reach {staged_module}. Nothing was measured.")
                raise SystemExit(2)
            result = run_tests(staged_tests, staged)
            # Exit 1 is the only status that means a test failed. pytest also
            # exits non-zero when it collected nothing (5), was misinvoked (4),
            # errored internally (3) or was interrupted (2). Counting those as
            # kills is how a suite that never ran reports a good score, so they
            # are their own bucket: the run produced no verdict, and a mutant
            # with no verdict is not a mutant that was caught.
            # One branch decides the bucket and the label together. Computing
            # them from two conditions lets the printed line and the counted
            # result disagree, and the printed line is what a reader believes.
            if result.returncode not in (0, 1):
                errored.append((mutant, result.returncode))
                state = f"error {result.returncode}"
            elif result.returncode == 0:
                survivors.append(mutant)
                state = "SURVIVED"
            else:
                state = "killed "
            out(f"  [{state}] {index:>3}/{len(candidates)}  {mutant.label()}")
        staged_module.write_text(source, encoding="utf-8")

    return survivors, errored, len(candidates)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("module", help="the module to break, e.g. ci/rulesets.py")
    parser.add_argument("--tests", default=None,
                        help="the tests that should notice (default: ci/tests/test_<module>.py)")
    parser.add_argument("--list", action="store_true",
                        help="print the mutants and run nothing")
    parser.add_argument("--check", action="store_true",
                        help="exit non-zero if any mutant survives")
    args = parser.parse_args(argv)

    module = Path(args.module)
    if not module.is_absolute():
        module = ROOT / module
    if not module.is_file():
        raise SystemExit(f"{args.module}: not a file.")

    # ROOT is read here rather than taken from the default argument: a default
    # binds at definition, so a caller that redirects the root would be given
    # the real repository's test file for a module it never named.
    tests = Path(args.tests) if args.tests else default_tests(module, ROOT)
    if not tests.is_absolute():
        tests = ROOT / tests
    if not tests.is_file():
        raise SystemExit(
            f"{tests}: no tests. A module with tests elsewhere must name them "
            f"with --tests; running a smaller suite silently would report a "
            f"score for something nobody measured."
        )

    if args.list:
        for mutant in mutants(module.read_text(encoding="utf-8")):
            print(mutant.label())
        return 0

    survivors, errored, total = sweep(module, tests, ROOT)
    judged = total - len(errored)
    print()
    print(f"{judged - len(survivors)}/{judged} killed, of {total} mutants.")
    if survivors:
        print("\nSurvived -- either a missing test, or a change with no "
              "behavioural difference. This tool cannot tell which:")
        for mutant in survivors:
            print(f"  {mutant.label()}")
    if errored:
        print("\nNo verdict -- pytest neither passed nor failed, so these are "
              "counted in neither column:")
        for mutant, code in errored:
            print(f"  exit {code}  {mutant.label()}")
    print("\nA killed mutant means some test noticed, not that the right one "
          "did. Operators are textual and are a floor, not a coverage claim.")
    return 1 if ((survivors or errored) and args.check) else 0


if __name__ == "__main__":
    sys.exit(main())
