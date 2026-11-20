#!/usr/bin/env python3
"""What the suite costs and what it catches, in one reading.

    uv run --extra dev qm posture
    uv run --extra dev qm posture --baseline
    uv run --extra dev qm posture --against .qm-posture.json

A suite has a cost (wall clock, and the share of it spent building fixtures)
and a yield (whether it notices when the code is wrong). This reports the two
side by side and never prints one without the other. The yield is measured by
breaking things: `qm mutate` breaks each watched module on purpose and reports
which mutants the tests noticed, per charter
`a-check-is-evidence-after-it-fails`.

This is not a gate. It prints a comparison and exits zero whatever it finds;
`records/DRAFT-a-check-is-evidence-only-after-it-has-failed.md` rejects a
mutation-score threshold. `docs/ref/ci/measuring-the-suite.md` explains the two
numbers and how to read them.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

CORPUS = Path(__file__).resolve().parent.parent

# Where a baseline lives by default: inside the repository, so it travels
# between machines as a committed reading.
DEFAULT_BASELINE = CORPUS / ".qm-posture.json"

SUITES = ("project-seed/ci/tests", "ci/tests")

# Modules whose yield is worth measuring, with the tests that should notice.
# A list, not a sweep: mutating everything takes too long to run often. These
# are the modules where a silent regression would be expensive.
WATCHED: tuple[tuple[str, str], ...] = (
    ("project-seed/ci/adr_lint.py", "project-seed/ci/tests/test_adr_lint.py"),
    ("project-seed/ci/check_pr_base.py", "project-seed/ci/tests/test_check_pr_base.py"),
    ("ci/check_restatements.py", "ci/tests/test_check_restatements.py"),
    ("ci/check_mathematics.py", "ci/tests/test_check_mathematics.py"),
    # It runs in every fork, so a defect here is a defect in every project at
    # once.
    ("project-seed/ci/check_placeholders.py",
     "project-seed/ci/tests/test_check_placeholders.py"),
)

SLOW = 1.0
"""Seconds. A test above this is worth a reason. Not a limit -- some tests are
legitimately slow -- but an unexplained one is usually a fixture doing work that
could be done once."""


@dataclass
class Suite:
    """What one run of the suite cost."""

    wall: float = 0.0
    tests: int = 0
    setup: float = 0.0
    """Seconds spent in fixtures: work repeated per test, and the cheapest
    thing to remove without removing an assertion."""

    slowest: list[tuple[str, float]] = field(default_factory=list)

    @property
    def setup_share(self) -> float:
        return (self.setup / self.wall * 100) if self.wall else 0.0


@dataclass
class Yield:
    """What breaking one module established."""

    module: str
    mutants: int = 0
    caught: int = 0
    survived: int = 0
    unreadable: str = ""

    @property
    def score(self) -> float:
        return (self.caught / self.mutants * 100) if self.mutants else 0.0


def measure_suite(paths: tuple[str, ...] = SUITES) -> Suite:
    """Run the suite once and read the cost off it."""
    started = time.monotonic()
    done = subprocess.run(
        [sys.executable, "-m", "pytest", *paths, "-q", "--durations=0", "-p",
         "no:randomly"],
        cwd=CORPUS, capture_output=True, text=True, encoding="utf-8",
        errors="replace",
    )
    wall = time.monotonic() - started

    found = Suite(wall=wall)
    if done.returncode != 0:
        # A reading from a failed run is not a reading: a broken suite would
        # look like a fast one.
        tail = "\n".join(done.stdout.strip().splitlines()[-15:])
        raise SystemExit(
            f"posture: the suite did not pass, so there is nothing to measure "
            f"(pytest exit {done.returncode}).\n{tail}")

    # The last match, not the first: some tests run pytest inside a subprocess
    # (`ci/tests/test_mutate.py` does) and their summaries are captured into
    # this output. The suite's own summary is the last one printed.
    counted = re.findall(r"(\d+) passed", done.stdout)
    found.tests = int(counted[-1]) if counted else 0

    for line in done.stdout.splitlines():
        row = re.match(r"^([0-9.]+)s\s+(setup|call|teardown)\s+(\S+)", line.strip())
        if not row:
            continue
        seconds, phase, where = float(row.group(1)), row.group(2), row.group(3)
        if phase == "setup":
            found.setup += seconds
        elif phase == "call" and seconds >= SLOW:
            found.slowest.append((where, seconds))

    found.slowest.sort(key=lambda pair: -pair[1])
    return found


def measure_yield(module: str, tests: str) -> Yield:
    """Break one module through the declared route and read the result.

    Through `qm mutate`, not by editing a copy, so a mutation that matches
    nothing is reported, the module is restored when something raises, and the
    run can be reproduced.
    """
    found = Yield(module=module)
    done = subprocess.run(
        [sys.executable, str(CORPUS / "ci" / "cli.py"), "mutate", module,
         "--tests", tests],
        cwd=CORPUS, capture_output=True, text=True, encoding="utf-8",
        errors="replace",
    )
    text = done.stdout + done.stderr

    # The declared summary line, cross-checked against the markers: two
    # independent reads, and a disagreement is reported as unreadable rather
    # than resolved. `qm mutate` prints one `N/M killed` line and one bracketed
    # marker per mutant.
    summary = re.search(r"(\d+)\s*/\s*(\d+)\s+killed", text)
    marked_killed = len(re.findall(r"\[killed", text))
    marked_survived = len(re.findall(r"\[SURVIVED", text))

    if not summary:
        found.unreadable = (text.strip().splitlines() or ["no output"])[-1][:160]
        return found

    found.caught = int(summary.group(1))
    found.mutants = int(summary.group(2))
    found.survived = found.mutants - found.caught

    # The markers contradict only when they account for every mutant. Output
    # can be truncated (by a pipe, a capture limit, a caller keeping the tail),
    # and a partial marker list is less evidence, not a disagreement.
    counted = marked_killed + marked_survived
    complete = counted == found.mutants
    if complete and marked_killed != found.caught:
        found.unreadable = (
            f"the summary says {found.caught}/{found.mutants} killed and the "
            f"markers show {marked_killed} killed, {marked_survived} survived")
        found.mutants = 0
    return found


def report(suite: Suite, yields: list[Yield], baseline: dict | None) -> None:
    print("TEST POSTURE")
    print("=" * 72)
    print(f"  {suite.tests} tests in {suite.wall:.1f}s")
    print(f"  fixtures  {suite.setup:.1f}s  ({suite.setup_share:.0f}% of the run)")
    print(f"  over {SLOW:g}s  {len(suite.slowest)} test(s)")

    if baseline:
        was = baseline.get("suite", {})
        print()
        print("  against the baseline")
        _delta("wall clock", was.get("wall"), suite.wall, "s", lower_is_better=True)
        _delta("fixtures", was.get("setup"), suite.setup, "s", lower_is_better=True)
        _delta("tests", was.get("tests"), suite.tests, "", lower_is_better=False)

    if suite.slowest:
        print()
        print("  SLOWEST -- each of these is a question, not a fault")
        for where, seconds in suite.slowest[:8]:
            print(f"    {seconds:6.2f}s  {where}")

    print()
    print("  YIELD -- mutants the tests noticed")
    for found in yields:
        if found.unreadable:
            print(f"    {found.module:<44} could not be read: {found.unreadable}")
            continue
        print(f"    {found.module:<44} {found.caught}/{found.mutants} "
              f"({found.score:.0f}%)")
        if baseline:
            before = (baseline.get("yields") or {}).get(found.module)
            if before is not None and abs(before - found.score) >= 1:
                direction = "up" if found.score > before else "DOWN"
                print(f"    {'':<44} {direction} from {before:.0f}%")

    print()
    print("  Cost and yield are read together. A run that got faster and caught")
    print("  less did not get better; the fastest possible suite is no suite.")


def _delta(label: str, before, now: float, unit: str, lower_is_better: bool) -> None:
    if before is None:
        print(f"    {label:<12} {now:.1f}{unit}  (no baseline)")
        return
    change = now - before
    if abs(change) < (0.05 if unit == "s" else 0.5):
        print(f"    {label:<12} {now:.1f}{unit}  unchanged")
        return
    better = (change < 0) if lower_is_better else (change > 0)
    word = "better" if better else "worse"
    print(f"    {label:<12} {before:.1f}{unit} -> {now:.1f}{unit}  "
          f"({change:+.1f}{unit}, {word})")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="qm posture",
        description=("What the suite costs and what it catches, together. "
                     "Cost is wall clock and fixture time; yield is the share "
                     "of deliberate breakages the tests noticed."),
        epilog=("Exits zero whatever it finds. This is a reading to discuss, "
                "not a gate to satisfy — a number that fails a build gets "
                "gamed."),
    )
    parser.add_argument(
        "--baseline", action="store_true",
        help="write this run as the baseline future runs are compared against")
    parser.add_argument(
        "--against", metavar="PATH", type=Path, default=DEFAULT_BASELINE,
        help="the baseline to compare with (default: %(default)s)")
    parser.add_argument(
        "--no-yield", action="store_true",
        help=("skip the mutation runs. Faster, and it reports half a picture — "
              "which is why it is not the default"))
    parser.add_argument(
        "--json", action="store_true", dest="as_json",
        help="the reading as one JSON document")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    baseline = None
    if args.against and args.against.is_file() and not args.baseline:
        try:
            baseline = json.loads(args.against.read_text(encoding="utf-8"))
        except Exception:                          # noqa: BLE001
            baseline = None

    suite = measure_suite()
    yields = [] if args.no_yield else [
        measure_yield(module, tests) for module, tests in WATCHED]

    if args.as_json:
        print(json.dumps({
            "suite": asdict(suite),
            "yields": {y.module: y.score for y in yields},
        }, indent=2))
    else:
        report(suite, yields, baseline)

    if args.baseline:
        args.against.write_text(json.dumps({
            "suite": {"wall": suite.wall, "tests": suite.tests,
                      "setup": suite.setup},
            "yields": {y.module: y.score for y in yields if not y.unreadable},
        }, indent=2) + "\n", encoding="utf-8")
        print(f"\n  baseline written to {args.against}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
