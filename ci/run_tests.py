#!/usr/bin/env python3
"""Run this corpus's tests, the way CI runs them, and nowhere else.

Org-level tooling, copied nowhere. There is one way to run the tests and this
is it:

    uv run qm test

WHY THIS EXISTS. Before it, there were three ways and no canonical one: CI's
`python -m pytest project-seed/ci/tests ci/tests -q`, `pyproject.toml`'s
`testpaths`, and whatever an operator typed. One session used four different
invocations in a single afternoon -- `python -m pytest`, `uv run --with pytest
pytest`, `uv run --extra preflight --with pytest pytest`, and a bare `pytest` --
each of which can collect a different set. `--with pytest` was redundant every
time, since the `preflight` and `dev` extras already carry it.

That is not a style problem. `pyproject.toml`'s own comment says a run that
collected one suite and not the other "would report green over half the
tooling", and an invocation improvised per-run is exactly how that happens.

THE PATHS ARE CI'S, LITERALLY. The argument list below is the one
`.github/workflows/ci-tooling-tests.yml` passes. If the two drift, a local pass
stops predicting a remote one, which is the failure this whole file is against.
`ci/tests/test_run_tests.py` asserts they match by reading the workflow.

WHAT THIS CANNOT DO. It runs the same *arguments* as CI, not the same
*environment*: a different interpreter, a different platform, and no runner
image. A local pass is evidence, not proof -- one defect found on 2026-08-15 was
invisible locally precisely because `uv run` installs this package and the
runner does not.

BOTH SUITES ALWAYS RUN, and extra arguments are added rather than substituted.
`qm test -- ci/tests/test_x.py` runs everything *and* that file again; narrowing
is `-k`. That is deliberate: a route that let you run a subset would let a
subset be reported as a pass, which is the thing `testpaths` exists to prevent.

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
SUITES = ("project-seed/ci/tests", "ci/tests")
BASE_ARGS = ("-q",)


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
