# Handoff - carlos simultaneous-run participant

**Goal.** Use Carlos as the controlled browser-workspace participant and verify that concurrent control traffic does not corrupt its rack state or database identity.

**Stamp.** 2026-09-21. Checkout: `fix/dials-cable-ends-and-scroll` at `3e8800f`, level with `origin/fix/dials-cable-ends-and-scroll`.

## Current evidence

- The documented loop is `uv run carlos check`, then `uv run carlos dev`; the default port is `4186` and `CARLOS_PORT` overrides it.
- `/healthz` reports the answering instance, port, and resolved database path.
- The repository has tests, browser tests, walkthroughs, and CI.

## Run contract

Start Carlos on a reserved port and a scratch `CARLOS_DB`. Verify `/healthz` before every measurement. Use the same seeded patch and scripted knob/cable operations in baseline and concurrent waves.

## Measurement questions

1. Does rack state remain identical under repeated isolated and concurrent runs?
2. Does response latency or browser error rate change when the other services are active?
3. Does any apparent result come from an old process, shared database, or wrong working directory?

## Evidence still needed

Run `uv run carlos check` before the experiment and save its instance/health response. Record process cleanup and port-free evidence after each wave.

## Limits

Carlos is a browser workspace, not proof that the audio/control devices behind other repositories are functioning. Its database and browser state are separate metrics.
