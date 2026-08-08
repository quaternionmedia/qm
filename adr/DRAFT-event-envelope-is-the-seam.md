# ADR-XXXX — The Event Envelope Is the Seam

| | |
|---|---|
| **Status** | Draft |
| **Date** | 2026-08-07 |
| **Pends on** | Nothing — ready to be argued |

## Context

The system's central requirement is generational: a control installed against
today's need must keep working as the need grows, and a consumer written today
must keep working against a module built years later. Physical controls fail
this routinely. A vendor's two-button remote and its later four-button remote
speak different payloads, and the automation written for one does not survive
the other.

Two places could carry that compatibility guarantee. It could live in the
transport — pick a protocol whose device model is extensible, and inherit its
compatibility rules. Or it could live in a payload schema that QM owns, carried
over whatever transport is convenient.

Placing it in the transport means inheriting that ecosystem's device-type
model. Every candidate transport models a switch as a fixed device type with a
fixed cluster or attribute set, and adding an axis means becoming a different
device type — which is exactly the discontinuity to avoid. It also binds the
compatibility guarantee to one ecosystem's release cadence.

Under QM's *Build the seam, buy the engines*, the ordering rule asks which
engine should own a capability before defaulting to the seam. No engine should
reasonably own a cross-transport compatibility guarantee for a device family
that does not exist yet. That is seam logic by the doctrine's own definition.

## Decision

1. **A single versioned event envelope is the project's interface**, defined as
   Pydantic models in the house stack, with JSON Schema emitted as a build
   artifact and golden vectors checked into the repository.
2. **Fields:** `src` (stable identity, equal to the MQTT topic path), `seq`
   (monotonic, for loss and replay detection), `caps` (the set of axes this
   module can ever emit), `action`, `ch`; and the optional axes `level`, `vec`,
   `color`, `batt`. Optional axes are absent rather than null when unused.
3. **Compatibility rules, and they are absolute:**
   - Fields are added, never removed and never repurposed.
   - Unknown fields are ignored by consumers, never treated as errors.
   - A module advertises `caps` at announce time, before emitting any event, so
     a consumer can present an appropriate interface without waiting for a
     rich event to arrive.
4. **Every transport carries this envelope**, either directly (MQTT, USB-serial
   diagnostics) or by a documented, lossless-where-possible projection (BTHome
   object IDs, Zigbee cluster attributes, MIDI note and controller numbers).
   Each projection is documented in `schema/projections/` with its own vectors,
   and a projection that cannot carry an axis states which axis it drops.
5. **CI fails on any schema change that breaks a checked-in vector**, and on
   any consumer-compatibility test in which a schema-pinned consumer errors on
   a capability-extended event.

## Consequences

- The forward-compatibility claim becomes testable rather than aspirational.
  Clause 5 is what makes this record worth ratifying; without it the rules in
  clause 3 are a style guide.
- Transport choice becomes reversible late, including after hardware exists.
  The same board can move from MQTT to Zigbee to a Matter bridge without the
  consumer side changing, which is the seams doctrine paying out.
- Accepted cost: the projections are real work, and some are lossy. A BTHome
  broadcast has a tight payload budget and will not carry a full colour object
  and a position vector in one advertisement. Documenting the loss is the
  obligation; pretending it does not exist is the failure mode.
- Accepted cost: an envelope with optional axes is weaker typing than a set of
  narrow message types. Consumers must branch on `caps` rather than on a type
  tag. This is the price of the generational guarantee and it is paid on
  purpose.
- Obligation created: `schema/` is versioned independently of firmware and
  hardware, and its version appears in every announce payload.

## Alternatives considered

1. **Adopt a transport's native device model as the interface** — Matter's
   Generic Switch, or Zigbee's on/off and level clusters. It lost because the
   compatibility guarantee would then be that ecosystem's to give, on that
   ecosystem's schedule, and because adding an axis means changing device type,
   which is the discontinuity this project exists to remove. It also assumes a
   single ecosystem, which the seams doctrine refuses.
2. **A family of narrow message types**, one per capability, with consumers
   subscribing to the ones they understand. It lost on the identity problem: a
   module that gains an axis emits a new type, and every consumer's binding to
   that physical button breaks even though the button did not move. Narrow
   types are better engineering in isolation and worse engineering for this
   requirement.
3. **No schema; publish raw values and let each deployment write its own
   mapping.** It lost because it relocates the compatibility problem into every
   deployment's automation layer, where it is invisible, untested, and lost
   whenever the person who wrote it moves on.
4. **A binary encoding (CBOR, Protobuf) as the canonical form**, with JSON as a
   debug view. It lost on legibility and on the barrier-to-entry requirement: a
   contributor with a shell and an MQTT client must be able to read an event
   without tooling. Binary encodings remain available as projections under
   clause 4 where a transport's payload budget demands one.

## Revision triggers

- A third optional axis is added within twelve months of the second — evidence
  that the flat envelope needs a subtype mechanism rather than another field.
- A projection is found to drop an axis that a deployed consumer depends on.
- A transport is adopted whose payload budget cannot carry the mandatory
  fields, which would force either a mandatory-field reduction or that
  transport's rejection.

## Amendments

*None.*
