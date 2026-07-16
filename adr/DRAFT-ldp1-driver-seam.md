# ADR-XXXX — LDP/1 is the sole driver boundary

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-07-16 |
| **Pends on** | Nothing architectural — filed Proposed rather than Accepted only because ratification is a human action per the org's own process; ratifies together with `PLAN.md` |

## Context

The arrangement source varies by show: an internal CLI, a hardware looper
(Squarp Hapax over MIDI), a cue engine (ShowRunner). Core must be
deterministic, testable without hardware, and indifferent to the source. The
org's seams doctrine requires the boundary to sit on standard protocols.

## Decision

All arrangement truth enters core through one versioned protocol, LDP/1:
Pydantic-defined events (`hello`, `transport`, `track`, `accent`,
`capture_cue`, `clip_bind`, `scene`, `config_hint`) carried in-process as a
Python `Protocol` and on the wire as JSON over WebSocket at `/driver`,
token-authenticated, single-authority lock. Drivers declare capabilities at
handshake (clock authority, explicit vs inferred state, event vs scene
style); core adapts to capabilities, never to driver identity. All
source-specific inference (Hapax liveness and trigger heuristics) lives
inside the driver. Every driver's stream is JSONL-logged and replayable; a
conformance kit replays golden streams through core in CI.

## Consequences

The seam is designed at n=1 implemented consumers; there is a real risk it is
wrong-shaped and 0.1.0 pays protocol ceremony a single-purpose script would
not. Accepted deliberately, bounded by two facts: 0.1.0 exercises only the
minimal subset, and the wire format has no external consumer until 1.1.0, so
breaking changes are free until then.

## Alternatives considered

1. **Hapax-direct first, extract the seam later** (rule of three: abstract
   at the third consumer) — rejected: the second and third consumers are
   already named and dated, and untangling MIDI inference from core after
   the fact is the expensive direction.
2. **Per-driver adapters inside core** — rejected: moves inference into the
   deterministic zone and makes replay source-dependent.

## Revision triggers

The LDP/1 subset changes shape more than twice during the 0.1.0 build
(collapse to in-proc only, re-derive the wire format at 1.0.0) · a second
external consumer appears (freeze and version the wire format) · a hot-swap
or multi-driver design is ratified.

## Amendments

*None.*
