# Handoff - joe simultaneous-run participant

**Goal.** Measure Joe's audio pipeline/API and browser surface while the instrument and show-control participants run concurrently.

**Stamp.** 2026-09-21. Checkout: `docs/onboarding-hardening` at `9e70fc9`, level with `origin/docs/onboarding-hardening`.

## Current evidence

- The README documents `uv run joe dev` for Vite on `:3000` and the API on `:8000`, plus `uv run joe run` for the pipeline.
- Python tests and Playwright E2E tests exist; the repository has no GitHub Actions workflow in this checkout.
- The current branch contains filename validation hardening and is active work, so record the exact branch in every run.

## Run contract

Run frontend and backend on reserved ports, then exercise one fixed input through `joe run`. Use a scratch input/output directory and record the API health response, pipeline completion, browser console, and output hashes.

## Measurement questions

1. Does the pipeline produce the same output alone and under concurrent control traffic?
2. Do API latency, browser errors, or file locks change when the other members are active?
3. Does audio processing contend for CPU or disk with ShowRunner/Carlos?

## Evidence still needed

Run `uv run pytest -q` and the relevant smoke/E2E command before the full experiment. Establish a clean baseline output and avoid the untracked notebook/worktree state from being part of the claim.

## Limits

Joe's pipeline is not evidence that the performer-display family is healthy; measure its API, browser, and batch output as separate signals.
