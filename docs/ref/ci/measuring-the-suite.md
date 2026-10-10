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

## What it is not

It is not a gate. It prints a comparison and exits zero whatever it finds:
`records/DRAFT-a-check-is-evidence-only-after-it-has-failed.md` rejects a
mutation-score threshold, because a number that fails a build gets gamed and a
number a person reads gets discussed.

A module whose tests depend on where the module sits on disk cannot be measured
by the mutator, which runs against a copy in a temporary directory: its
baseline is red before any mutant is applied. The trio demo is one, and its
mutations are applied by hand.
