# Handoff - holophonor simultaneous-run participant

**Goal.** Measure Holophonor as the looping/instrument hub while the surrounding clients and control surfaces run together.

**Stamp.** 2026-09-21. Checkout: `main` at `dd8d9db`, level with `origin/main`.

## Current evidence

- The README describes a plugin-based live-looping architecture with hardware and network controllers.
- Installation is `pip install -e holophonor/`; the documented launcher is `holophonor`.
- The repository has CI and release workflows but no discoverable test suite.

## Run contract

Start it as the hub on an explicitly assigned non-default port or endpoint if the launcher supports that. Record the actual bound port, plugin list, audio/MIDI devices, and network listeners. Use a controlled or stubbed device layer for the first run; do not connect destructive or live hardware until the process stays healthy in isolation.

## Measurement questions

1. Does the hub keep its loop clock and audio callback healthy with no clients?
2. Does adding Midiphonor and the control clients increase latency, dropouts, or reconnects?
3. Which device/plugin failures are local setup failures rather than simultaneous-run effects?

## Evidence still needed

Run the documented install and launcher, identify the supported health signal, and capture one baseline loop trace. Add a repeatable smoke command if none exists before interpreting a full run.

## Limits

A process staying alive is insufficient evidence for audio efficacy. Record callback underruns, loop drift, CPU, memory, and network errors separately from HTTP/process availability.
