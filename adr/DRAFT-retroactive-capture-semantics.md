# ADR-XXXX — Retroactive ring capture, first-cycle semantics

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-07-16 |
| **Pends on** | Nothing architectural — filed Proposed rather than Accepted only because ratification is a human action per the org's own process; ratifies together with `PLAN.md` |

## Context

Nothing is prepped in advance; the video of a loop is a camera take of the
pass in which it was recorded. Detection of "a loop was just recorded" may
lag the moment itself (auto-inference confirms after the fact; even a
footswitch is pressed near, not before, the downbeat). The capture mechanism
must therefore work backwards in time.

## Decision

Cameras record continuously into a rolling segment ring (tmpfs). A capture
request names a bar window; the extractor cuts `[t(bar_a)+offset,
t(bar_b)+offset)` on **realized** bar timestamps from the shared monotonic
timeline — tempo ramps during the take are captured correctly by
construction — and re-encodes once to exact cycle duration. Capture
semantics are **first-cycle**: the clip is the first full pattern cycle of
the take, beginning at the cycle boundary (pre-first-note silence shows the
performer about to play). Later overdub cycles exist in audio only.
Replacement is by explicit gesture; every take is kept in the session
artifact.

## Consequences

The largest aesthetic compromise in the system: live loopists build texture
across overdub passes, and the wall will systematically show sparse first
passes. Accepted for v1 as the honest, deterministic semantic; the session
keeps all material a future compositor would need.

## Alternatives considered

1. **Record-forward on trigger** (start the camera when told) — rejected:
   loses the start of every retroactively detected take, and couples capture
   correctness to detection latency.
2. **Multi-cycle stitch or picture-in-picture compositing of overdub
   passes** — deferred: real design space, real cost, and it changes the
   aesthetic contract; nothing in the ring architecture forecloses it.

## Revision triggers

A compositing design is ratified · F3 (record-pass echo, `VERIFICATION.md`)
fails in the V-track, which demotes auto-detection and may motivate an
Nth-cycle capture option on the footswitch path.

## Amendments

*None.*
