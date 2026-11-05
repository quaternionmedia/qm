# Handoff - ShowStopper simultaneous-run participant

**Goal.** Measure ShowStopper as the timing/stopwatch surface and determine whether its state can be driven or observed safely during simultaneous show-control activity.

**Stamp.** 2026-09-21. Checkout: `fix/textual-containers` at `66ab4f3`, level with `origin/fix/textual-containers`.

## Current evidence

- The README describes a simple stopwatch for show timing.
- The repository has a Python project manifest but no discoverable test suite or CI workflow.
- The current branch is active work and includes a Textual/container change.

## Run contract

Start the application in an isolated terminal/session. If it is interactive-only, use a human-operated timing script or a deterministic Textual test harness rather than claiming headless success. Record start/stop timestamps, displayed elapsed time, and any control/event interface.

## Measurement questions

1. Is elapsed-time behavior stable over the duration of the experiment?
2. Can concurrent cue/control traffic affect timer state or input handling?
3. Is there any machine-readable seam for ShowRunner or another participant, or is this only a local UI?

## Evidence still needed

Identify the supported entry point and whether a non-interactive smoke test exists. Add or run a minimal timing assertion before including ShowStopper in quantitative efficacy comparisons.

## Limits

Without a protocol or deterministic UI harness, ShowStopper can be included in qualitative operator observations only, not in automated end-to-end success rates.
