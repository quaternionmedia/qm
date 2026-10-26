# Handoff - midiphonor simultaneous-run participant

**Goal.** Establish whether midiphonor can participate in the performing-family run and measure its effect without treating an unavailable browser client as a passing service.

**Stamp.** 2026-09-21. Checkout: `main` at `407e6c3`, level with `origin/main`.

## Current evidence

- The README identifies Midiphonor as a Tone.js Holophonor implementation.
- `package.json` declares version `0.0.1` and its `test` script intentionally exits with `Error: no test specified`.
- No local test suite or CI workflow was found.

## Run contract

Treat this as a browser client, not a backend. First establish whether it can build and load against a controlled host. Record the browser URL, asset build command, and any WebSocket/HTTP target it attempts to reach. Do not infer a live connection from a successful static page load.

## Measurement questions

1. Does the client build and load repeatedly?
2. Does it connect to the same Holophonor target alone and during the full run?
3. Does concurrent traffic change frame rate, audio timing, connection loss, or browser errors?

## Evidence still needed

Run the package's declared build/test commands, add a browser smoke path if this participant is kept, and capture the target protocol and browser-console output before the full experiment. A failing placeholder test is a baseline finding, not an efficacy result.

## Limits

This participant cannot prove end-to-end simultaneous performance without a real browser and audio context. The experiment must report it as unverified if those prerequisites are absent.
