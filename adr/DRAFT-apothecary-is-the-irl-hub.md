# ADR-XXXX — Apothecary Is the irl Family's Hub, Importing hearth's Coordinator

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-11-05 |
| **Pends on** | hearth's first tag, a person's act: until it is cut, `qm-hearth` is a git source at a pinned revision and this record's §2 is half met |

## Context

The corpus's family record gives show control and instruments each a hub, and `irl`
had none. A family's members are separate apps; a hub hands each its part of whatever
fires and keeps what each answered. hearth holds the contract for that, `family/1`,
and the coordinator as one text, and its adoption record says a coordinator runs inside
an exemplar's app, whose own record owns that seam. This is that record.

apothecary holds the site, the machines, the cameras and the evidence log already.
It takes dependencies, and everything it runs stays on the machine it runs on, by the
stays-local guard.

## Decision

§1. apothecary is the `irl` family's hub. It answers the hub's routes of `family/1` at
`/family/`, as `apothecary` of `irl`.

§2. The coordinator is imported from `qm-hearth`, never copied: at a pinned revision
until hearth's first tag, and at a version from then on.

§3. A member is on this machine. The table is `family.json` in the state folder, and a
member at any other address is left out and said. The stays-local guard is what holds
this; the table only says so sooner.

§4. Only a member of `irl` is hosted in the hub's process. A member of any other family
is named by URL, because two families meet across a protocol.

§5. The conformance version replayed is pinned in `tests/test_family_hub.py`, which runs
`hearth check --hub` against a real port. The corpus's `ci/interop-registry.yaml` reads
that pin, and `uv run qm interop` compares it with what hearth publishes.

## Consequences

- A hold sent to carlos from the server is a delivery through the hub, kept in its
  audit. `apothecary rig` runs outside the server and sends directly.
- apothecary takes `qm-hearth` and, through it, `httpx` as runtime dependencies.
- A change to `family/1` reaches this repository at its next dependency bump, and its
  suite is what says so.
- The audit is in memory, and a restart or a changed table starts it empty. An outcome
  kept in the evidence log is the hub's plan, and is not decided here.

## Alternatives considered

1. **A project of its own, as ShowRunner is to show-control.** Lost: a new repository
   would need the blueprint, the machines and the evidence log, each of which is
   already here, and would share nothing with apothecary but a seam it does not need.
   A reader could reasonably want the hub separable; that is the first revision trigger.
2. **Copy the coordinator with `hearth fork`.** Lost: a copy is for a maintainer who
   takes no dependency, and apothecary takes them. It would add a digest to hold and a
   text to keep from drifting, and gain nothing.
3. **Keep sending to carlos directly and register only.** Lost: a registry row claims
   a version replayed, so a row with nothing behind it would be false, and the sends
   would stay outside any audit.

## Revision triggers

- hearth's first tag, which moves `Pends on` and the dependency to a version.
- A member that has to live on another machine, which the stays-local record would
  have to allow first.
- The hub's code growing to where it would be better apart from the rest of apothecary.

## Amendments

*None.*
