# Handoff - ludwig simultaneous-run participant

**Goal.** Measure Ludwig as a remote mixing endpoint without confusing console startup or hardware availability with concurrency efficacy.

**Stamp.** 2026-09-21. Checkout: `main` at `fe7ee65`, level with `origin/main`.

## Current evidence

- The README documents editable local installation with `pip install -e ludwig/` and the `ludwig` launcher.
- `setup.py` exposes `ludwig=ludwig.main:main`.
- No CI workflow or discoverable test suite was found.

## Run contract

Start Ludwig in isolation with a fake or explicitly selected mixer target where possible. Record its transport, target address, bound ports, and command acknowledgements. Keep real mixer hardware outside the first wave.

## Measurement questions

1. Does one command reach the intended mixer target and return an acknowledgement?
2. Does command latency or ordering change when Wolf, Carlos, and Holophonor are active?
3. Are failures caused by unavailable hardware, protocol mismatch, or shared-resource contention?

## Evidence still needed

Run the launcher and identify a deterministic health or command probe. If no safe fake target exists, define a dry-run adapter before measuring the full family.

## Limits

A no-hardware run measures process and protocol readiness only; it cannot establish real mixing efficacy.
