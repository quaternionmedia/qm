#!/usr/bin/env python3
"""Run this corpus's tests, the way CI runs them, and nowhere else.

Org-level tooling, copied nowhere. There is one way to run the tests and this
is it:

    uv run qm test

An improvised invocation can collect a different set of tests, and a run that
collects one suite and not the other reports green over half the tooling
(`pyproject.toml` says so beside `testpaths`). This is the one invocation.

The paths are CI's: the argument list below is the one
`.github/workflows/ci-tooling-tests.yml` passes, and
`ci/tests/test_run_tests.py` asserts they match by reading the workflow, so a
local pass predicts a remote one.

What this cannot do: run CI's *environment*. It runs the same arguments under a
different interpreter, platform and image, so a local pass is evidence, not
proof; `uv run` installs this package and the runner does not.

Both suites always run, and extra arguments are added rather than substituted:
`qm test -- ci/tests/test_x.py` runs everything *and* that file again, and
narrowing is `-k`, so a subset is never reported as the suite's pass.
`docs/ref/ci/measuring-the-suite.md` describes the test command.

Usage:
    uv run qm test
    uv run qm test -- -k restatements      # narrow by name, not by path
    python ci/run_tests.py
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Exactly what ci-tooling-tests.yml runs. Changing one without the other is the
# drift the module docstring names, and a test reads the workflow to catch it.
SUITES = ("project-seed/ci/tests", "ci/tests", "walkthrough")
# `--doctest-glob` and `walkthrough` named on the command line, not left to
# `testpaths`. records/DRAFT-one-executable-walkthrough.md measured it: pytest
# ignores `testpaths` the moment it receives a path argument, and this
# invocation always passes paths -- so a testpaths-wired walkthrough would be
# collected by nobody and stay green forever.
# `-n auto` is a deliberate default and not a hidden one: `main` prints the
# whole command before running it, so an operator sees the workers and can
# override with `qm test -- -n 0`. It is a default because the parallel run is
# several times faster, and a slow gate is one people skip between runs.
#
# This tuple and `.github/workflows/ci-tooling-tests.yml`'s pytest line are
# asserted equal by `ci/tests/test_run_tests.py`.
BASE_ARGS = ("-q", "--doctest-glob=*.md", "-n", "auto")


def main(argv: list[str] | None = None) -> int:
    extra = list(argv or [])
    # `--` separates our arguments from pytest's, so `qm test -- -k foo` works
    # without this module having to know pytest's option surface.
    if extra and extra[0] == "--":
        extra = extra[1:]

    args = [sys.executable, "-m", "pytest", *SUITES, *BASE_ARGS, *extra]
    print("running the suites CI runs:\n  " + " ".join(args[1:]) + "\n", flush=True)

    proc = subprocess.run(args, cwd=str(ROOT))

    print(
        "\nThis ran CI's arguments, not CI's environment -- a different "
        "interpreter, platform, and no runner image.\nA local pass is evidence, "
        "not proof.",
        file=sys.stderr,
    )
    return proc.returncode


if __name__ == "__main__":
    sys.exit(main())
