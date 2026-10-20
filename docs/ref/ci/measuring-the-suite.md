# Measuring the suite

A test suite has a **cost** and a **yield**, and the two are read together.

```sh
uv run qm posture                          # cost and yield, side by side
uv run qm posture --baseline               # record the reading as the baseline
uv run qm posture --against .qm-posture.json
uv run qm mutate <module> --tests <tests>  # break one module, see what notices
```

The source is `ci/test_posture.py`; the mutator is `ci/mutate.py`.

## Cost and yield

The cost is the wall clock, and the share of it spent building fixtures. The
yield is whether the suite notices when the code is wrong. Optimising either
alone makes the other worse unseen: a suite tuned only for speed catches less
(deleting tests is the fastest optimisation and the worst), and one tuned only
for yield grows until people stop running it. `qm posture` therefore never
prints one number without the other.

Fixture setup is the most actionable part of the cost: it is work repeated per
test, and the cheapest thing to remove without removing an assertion. A test
slower than a second is worth a reason, not a limit.

## The yield is measured by breaking things

Charter `a-check-is-evidence-after-it-fails`: a check is evidence only after it
has been seen to fail. A count of tests, a line-coverage percentage and a green
tick are all compatible with a suite that asserts nothing. `qm mutate` breaks a
module on purpose and reports which mutants the tests noticed; that number is
the yield.

The posture reading takes the score from the `N/M killed` summary line and
cross-checks it against the per-mutant markers. When both account for every
mutant and disagree, the score is reported as unreadable rather than guessed. A
marker list shorter than the mutant count (truncated by a pipe or a capture
limit) is less evidence, not a contradiction. A run that could not be read is
reported as unreadable, never as 0%.

Only a watched list of modules is mutated, because mutating everything takes
too long to run often. The list holds the modules where a silent regression
would be expensive, including [seed](../../ref/glossary.md#seed){ .glossary-term } scripts that run in every fork.

## Reading it

- A reading from a failed suite run is refused: a broken suite would look like
  a fast one.
- The test count is the last summary line pytest prints, because some tests run
  pytest in a subprocess and their summaries land in the same output.
- The baseline lives in the repository as `.qm-posture.json`, so it travels
  between machines.

## Running the suite

`uv run qm test` (`ci/run_tests.py`) is the one way to run the tests: the
argument list is the one `.github/workflows/ci-tooling-tests.yml` passes, and
`ci/tests/test_run_tests.py` asserts the two match. Both suites always run;
extra arguments are added rather than substituted, so narrowing is `-k` and a
subset is never reported as the suite's pass. It runs with `-n auto` and prints
the whole command first, so `qm test -- -n 0` overrides it. It runs CI's
arguments, not CI's environment, so a local pass is evidence rather than proof.

`ci/tests/test_every_gate_is_exercised.py` requires, for every module in `ci/`
with a `main`, a test that executes it: an import, a call to its `main`, or an
invocation by filename, never a mention. Tests are named for their subject
rather than their module, so this is the only way to tell an untested module
from one tested under another name. A module nothing executes is listed in
`UNEXERCISED` with a reason, and an entry is refused once a test runs the
module or the module is gone. It cannot tell whether a test checks anything;
the mutation score answers that.

## Mutation

`uv run qm mutate <module>` (`ci/mutate.py`) applies one-for-one textual
substitutions to a module and runs its tests against each mutant. A surviving
mutant means a test is missing or the change makes no behavioural difference;
the tool cannot tell which and judges none. Every mutant runs against a copy of
the working tree (with `.git`, without build outputs and caches) staged once
per [sweep](../../ref/glossary.md#sweep){ .glossary-term }, so an interruption never leaves a tracked file broken, and pytest
runs with `-B` and no cache so a mutant never imports an earlier mutant's
bytecode. `--tests` defaults to the obvious test file and says so. It cannot
see a defect no operator expresses, or whether the test that killed a mutant
is the one that should have.

## The family suite

`uv run qm family-suite` (`ci/family_suite.py`) runs the member suites of the
estate's families and adds the assertions that exist only across members. Each
tier needs more of the estate to have reported than the one above it:

| Tier | Needs | Asserts |
|---|---|---|
| shape | one family | every member that ran, ran something |
| cover | all families | every declared family had a member run |
| contract | all, plus the [seam](../../ref/glossary.md#seam){ .glossary-term } | every contract surface agrees across families |

A tier the batch cannot reach is printed `not reached` with what it would take,
never as passing. It names each failing test, not only a count. It runs sibling
clones, so it is advisory and local only.

## What it is not

It is not a gate. It prints a comparison and exits zero whatever it finds:
`records/DRAFT-a-check-is-evidence-only-after-it-has-failed.md` rejects a
mutation-score threshold, because a number that fails a build gets gamed and a
number a person reads gets discussed.

A module whose tests depend on where the module sits on disk cannot be measured
by the mutator, which runs against a copy in a temporary directory: its
baseline is red before any mutant is applied. The trio demo is one, and its
mutations are applied by hand.
