# ADR-XXXX — Signal-Only Control: The Module Never Switches Mains

| | |
|---|---|
| **Status** | Draft |
| **Date** | 2026-08-07 |
| **Pends on** | Nothing — ready to be argued |

## Context

A button that controls a light can do so in one of two structurally different
ways: by interrupting the line conductor feeding that light, or by emitting a
signal that some other device acts on.

The first way is what a wall switch is, and it is what buyers expect when they
see a switch on a wall. It is also a regulated product. A device that
interrupts line voltage in a permanent installation in North America is subject
to NEC installation requirements and, in practice, to an NRTL listing
(UL 20 for general-use snap switches, UL 508 or UL 916 for related control
equipment). Listing is a per-design, per-fee, per-revision process. It is
incompatible with a project whose designs are published, forked, modified by
third parties, and printed on consumer FDM machines — because the listing
attaches to the exact tested configuration, and every fork breaks it.

The second way carries none of that burden, and it is also the more useful
behaviour for the stated problem: the target is a smart device that has lost
its physical control, and the actuation already exists inside that device.

There is a further constraint that survives the choice: a Class 2 or
signal-level circuit sharing an enclosure with line conductors is still subject
to separation and insulation requirements, and a 3D-printed body is not a
listed enclosure under any interpretation.

## Decision

1. **No design in this project interrupts, switches, or carries line voltage.**
   Inputs are dry contacts and low-voltage sensors. Outputs are radio,
   indication, and Class 2 signalling.
2. **Actuation is delegated to a listed device**: a listed relay module, a
   listed smart plug, a listed smart bulb, a listed load controller. The
   project's boards drive none of them electrically; they publish events the
   controlling system acts on.
3. **Where a module is installed in a wall box**, it is installed inside a
   listed box or behind a listed plate, and printed parts serve as cosmetic and
   mechanical elements only, never as the sole barrier between a person and a
   conductor. Documentation states this at the point of installation, not in a
   footnote.
4. **A "retrofit an existing switch" installation converts that switch to
   signal duty**: the existing switch's conductors are re-terminated to the
   module's dry-contact inputs by a qualified person, and the load it formerly
   fed is fed permanently or through a listed controller. This project supplies
   the module and the documentation; it does not supply an electrician.
5. **Bus and battery power only.** Modules are fed from USB-C at 5 V, from a
   listed Class 2 supply, or from a self-contained cell. No board in this
   project carries a line-voltage conversion stage. Where a fixed installation
   needs power at the module, that power arrives from a listed supply or a
   listed receptacle, and the cable run is Class 2 wiring.

## Consequences

- The project ships as open hardware, forkable and printable, with no listing
  that a fork invalidates. This is the decision's whole point.
- Accepted cost, stated plainly: **the product cannot be marketed as a
  replacement light switch.** A buyer who wants one switch that both looks like
  a switch and cuts the current needs a listed product downstream, so the total
  installed cost is higher than a single listed smart switch.
- Accepted cost: in a house with no smart actuation anywhere, the module is
  useless on its own. The system's value begins at "you already have a smart
  device with a bad physical story," which is a large market but not a
  universal one.
- The retrofit story gains something in exchange: a dumb switch converted to
  signal duty gains multi-press gestures, hold, and later the colour and
  position axes — behaviours a line-interrupting switch structurally cannot
  have, because it only has two states.
- Obligation created: an installation-safety section in the documentation, and
  a CI check that no schematic in `hardware/` contains a net class or component
  rated for mains. The check is crude and it is the teeth this record needs.

## Alternatives considered

1. **Design a line-switching variant and pursue an NRTL listing for it.** It
   lost on cost structure and on incompatibility with forking. The listing
   attaches to a tested configuration; the project's premise is that anyone may
   change the configuration. Those two facts cannot both be honoured, and the
   forkability is the deliverable.
2. **Design a line-switching variant and publish it as unlisted, for
   qualified installers only.** It lost on honesty. Publishing a mains design
   with a disclaimer moves risk onto whoever prints it while retaining the
   marketing benefit of the capability. The disclaimer is not a mitigation.
3. **Low-voltage-only, but with an integrated line-voltage supply stage** (so
   the module can be fed from the box it sits in). It lost because a converter
   stage puts line potential on the project's own board, which reintroduces the
   listing question through the back door for a convenience — avoiding a
   battery change — that a Class 2 supply also solves.
4. **Dry contacts driving a listed relay over a short pigtail, sold as one
   assembly.** It lost as a *default*; combining components into an assembly
   makes the assembler responsible for the combination. It remains available as
   an integrator's choice, documented as such, with that responsibility named.

## Revision triggers

- A published NRTL listing path emerges that accommodates parametric or
  user-modified designs, at a cost proportionate to a small open project.
- The jurisdictions the project is deployed in change what constitutes a
  regulated switching device.
- A project need arises for switching a load that is not line voltage — DC
  lighting, low-voltage architectural, stage or studio circuits — which this
  record does not govern and which would need its own.

## Amendments

*None.*
