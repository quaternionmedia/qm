# Handoff - leo simultaneous-run participant

**Goal.** Measure Leo as the performer-display web surface, including its setlist/filter workflow, while upstream control traffic is active.

**Stamp.** 2026-09-21. Checkout: `setlist` at `8dce16c`, level with `origin/setlist`; untracked `irealforms.ipynb` is present.

## Current evidence

- The README documents `uv run leo quickstart`, `uv run leo test`, and `uv run leo playwright-test`.
- The repository has CI, deployment, publish, and label workflows.
- The local suite previously collected 34 tests and passed; browser coverage is a separate concern.

## Run contract

Run Leo on its documented non-default development port where the CLI supports it, or reserve its default explicitly and record the collision check. Use a fixed setlist and scripted browser actions. Record render readiness, filter/setlist selection latency, browser console errors, and network requests.

## Measurement questions

1. Does Leo render the same setlist and filter state alone and under concurrent cue traffic?
2. Do browser frame delays, failed requests, or state divergence increase in the full run?
3. Does the untracked notebook affect reproducibility or is it unrelated working material?

## Evidence still needed

Run the Python suite and a focused Playwright smoke test from the exact branch. Decide whether `irealforms.ipynb` is intentional, ignored, or missing from the handoff before using the tree as evidence.

## Limits

A browser page loading is not a performer-display success. The plan must capture state assertions and timing, not screenshots alone.
