# Handoff - ShowRunner simultaneous-run participant

**Goal.** Treat ShowRunner as the show-control hub and measure its API, event logging, and outbound integration behavior while the family is active together.

**Stamp.** 2026-09-21. Checkout: `integrate/2026-09-20` at `2b28210`, level with `origin/integrate/2026-09-20`.

## Current evidence

- The README documents `uv sync --all-extras`, `sr start`, and the default API port `8000`.
- The repository has test, documentation, and publish workflows plus unit/UI/E2E tests.
- The current branch is active integration work; do not substitute `main` results for this checkout.

## Run contract

Start ShowRunner on a reserved port and confirm its health/API response before adding clients. Exercise a fixed cue/script fixture. Record outbound OSC/HTTP destinations, event-log entries, request latency, and process resource usage.

## Measurement questions

1. Does the hub produce the same cue/event sequence alone and with all clients active?
2. Does outbound traffic, logging, or API latency degrade as clients are added?
3. Are failures caused by a missing integration seam rather than simultaneous load?

## Evidence still needed

Run `uv run pytest` and the documented lint command, then establish a baseline cue trace. Confirm which advertised tools are actual live wires in this checkout before assigning them efficacy scores.

## Limits

ShowRunner can be healthy while a peripheral protocol is absent. Score hub health, outbound delivery, and end-to-end receipt separately.
