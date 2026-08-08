# ADR-XXXX — Apothecary Carries a Part Through Design, Visualization and Deployment

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-08-08 |
| **Pends on** | Whether this belongs here or in apothecary's own records, since it describes capability that repository would build |

## Context

Apothecary is QM's OpenSCAD generation toolkit and curated parts library. It
already does two of the three things a physical part needs across its life: it
**designs** — one folder per part, a Pydantic parameter model, print settings,
STL generation — and it **visualizes**, through its FastAPI viewer and preview
tooling. Enclosure geometry for this project lands there rather than here.

A printed part does not stop existing when the STL is generated. It gets
printed, it gets a board bolted into it, it goes on a desk or a wall, and then
it does something. Today the record of that part ends at the last thing
apothecary knows: a mesh. What the part *became* — which unit, where, running
what firmware, still reporting — lives in an entirely separate system, keyed by
nothing the part model can see.

That gap has a cost this project makes concrete. The `Params` model already
carries `pcb_x`, `pcb_y`, `cable_exit` and `gang`, which are assertions about a
physical object that will exist. Whether the object that got printed matches
them is currently checked by a person with calipers, once, and never again.

The envelope makes closing this loop cheap in a way it would not otherwise be.
A deployed module announces its identity, its capabilities, and its hardware
and firmware identifiers on a retained topic, in a documented schema, over a
protocol with many independent implementations. Anything that can subscribe can
know what is deployed. Apothecary would be a consumer of that seam, which is
the architecture working as designed rather than a new integration.

There is a real objection, and it is this project's own. The milestone's
anti-goals name "a web UI, dashboard, or configuration app" as out of scope
because Home Assistant is the engine, and this record must not become a licence
to build a second one. The distinction it draws is stated in clause 4 and is
the part most worth attacking.

## Decision

1. **Apothecary is the surface for a part across its whole life — design,
   visualization, and deployment awareness.** A part's record does not end at
   the mesh. Where instances of that part are deployed, apothecary can show
   which ones exist, what they report, and whether they are reachable.
2. **Deployment awareness is a projection of the event envelope, never a
   second data model.** Apothecary subscribes to the documented announce and
   availability topics and reads the schema this project publishes. It defines
   no device model of its own, stores no state a broker restart cannot rebuild
   from retained topics, and gains no privileged channel to a module.
3. **The link from a physical instance to a part is the `src` identity.** A
   deployed module's announce carries hardware and firmware identifiers and a
   stable `src`; a part in apothecary carries a name and parameters. The
   binding between them is data, declared by the deployer, and is never
   inferred from geometry.
4. **This is a build-and-verify surface, not an automation surface.** The
   boundary: apothecary answers *is the thing I designed real, present, and
   what I think it is* — the physical-design feedback loop closing. It does
   not answer *what should happen when someone presses it*, which is
   automation and belongs to Home Assistant. Concretely, apothecary may
   display announce and availability and may render a part with live state;
   it may not publish commands, hold automation rules, or become the thing a
   deployer configures behaviour in. A feature request that only makes sense
   as automation is a request for Home Assistant.
5. **The dependency direction is one-way and unchanged.** Apothecary depends
   on the published schema; this project depends on a pinned apothecary
   release for geometry. Apothecary never depends on this project's code, and
   a part remains useful to apothecary's users with no module deployed
   anywhere.
6. **None of this is in Milestone 1.** M1 ships a part, a board and an
   envelope. This record states the intended shape so that decisions taken now
   — the announce payload's contents, the retention rules, the `src` identity
   — are taken knowing what they are expected to support later.

## Consequences

- The physical-design feedback loop closes. A part that is wrong in a way only
  discovered after printing currently produces a note somewhere; it could
  produce a fact attached to the part.
- The envelope earns a consumer that is not a home-automation platform, which
  is the strongest available evidence that it is a seam rather than a Home
  Assistant integration wearing a schema. A second independent consumer is
  what makes the replaceability claim checkable.
- Apothecary gains a reason to care about identity and time, which it does not
  have today. That is a real increase in its scope and the honest cost of this
  record: a parts library that subscribes to a broker is a different kind of
  program than one that renders meshes, with a different failure surface.
- **Accepted cost, and the one to watch:** clause 4's boundary is a judgement
  call, and judgement calls drift. The pressure will be incremental and each
  step will be reasonable — a status light, then a toggle to test the light,
  then a rule about when the toggle fires. The second step is already across
  the line. Clause 4's concrete test is whether the feature publishes; a
  surface that only ever subscribes cannot become an automation platform by
  accident.
- Obligation created: the announce payload is now load-bearing for something
  beyond Home Assistant discovery, so removing or repurposing a field in it is
  a compatibility break for a second consumer. The envelope's additive rule
  already forbids that; this record is why it matters here.

## Alternatives considered

1. **Leave monitoring entirely to Home Assistant.** The strongest
   alternative, and it is what M1 does. It lost as a *permanent* position
   because Home Assistant answers a different question: it knows about
   entities and automations, and has no concept of the printed part, its
   parameters, or whether the object matches the model it came from. Asking a
   home-automation platform to close a CAD feedback loop is asking it to hold
   data it has no reason to model.
2. **Build the monitoring surface in this project rather than apothecary.** It
   lost on the ordering rule that put geometry in apothecary in the first
   place: the question is which engine should own a capability before it
   defaults to the seam, and a part's lifecycle belongs with parts. Building
   it here would also produce exactly the dashboard the anti-goals refuse.
3. **A third repository for deployment awareness.** It lost on the same
   ordering rule and on the coupling it would create: it would need both the
   part model and the schema, and would be the only place either is joined.
4. **Have apothecary read from Home Assistant's API rather than the broker.**
   It lost on the replaceability test. Home Assistant's API is a
   single-implementation interface; the broker and the envelope are not.
   Depending on the platform would make apothecary's feature contingent on a
   deployment choice this project deliberately refuses to require.
5. **Give apothecary its own agent on each module.** It lost immediately: it
   would put a second publisher on the device, a second protocol to maintain,
   and a privileged channel that clause 2 exists to refuse.

## Revision triggers

- Clause 4's boundary is argued over twice — evidence the line needs to be
  drawn mechanically rather than descriptively, or drawn somewhere else.
- Apothecary's part model changes such that an instance cannot be linked to a
  part by declared data, which would invalidate clause 3.
- A second consumer of the envelope appears that is neither a home-automation
  platform nor apothecary, which would make deployment awareness a general
  capability rather than a parts-library feature.
- Anything in this record is proposed for Milestone 1, which contradicts
  clause 6 and means either the milestone or this record has moved.
- Apothecary declines the capability, at which point the venue question in
  `Pends on` resolves against this shape entirely and the record is withdrawn
  rather than relocated.

## Amendments

*None.*
