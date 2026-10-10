# Handoff - wolf simultaneous-run participant

**Goal.** Establish whether Wolf can join the instruments/control wave and identify its actual runtime seam before measuring concurrency.

**Stamp.** 2026-09-21. Checkout: `main` at `d960d10`, level with `origin/main`.

## Current evidence

- The README calls Wolf a realtime control server and documents `./wolf install`, `./wolf build`, and `./wolf run`.
- The repository has no CI workflow or discoverable test suite.
- The latest local commit is from 2021, so startup and protocol compatibility are open questions.

## Run contract

Run the documented install/build/start sequence in an isolated checkout. Record the process, listening ports, browser/API endpoint, and any external MIDI or OBS dependencies. Do not count a successful shell command as a running service; probe the endpoint and inspect logs.

## Measurement questions

1. Does Wolf start and remain responsive on its own?
2. Does it share or contend for MIDI/network resources with Holophonor, Ludwig, or Carlos?
3. Does simultaneous traffic produce queue growth, dropped messages, or stale state?

## Evidence still needed

Confirm the script's dependencies and actual health endpoint. If startup is impossible on this machine, capture the failure and classify it as an environment or maintenance blocker before excluding Wolf from the efficacy denominator.

## Limits

Because the code is dormant and untested, a full-run failure cannot be attributed to simultaneity until an isolated baseline succeeds.
