# ADR-XXXX — Enclosure Parts Live in Apothecary

| | |
|---|---|
| **Status** | Draft |
| **Date** | 2026-08-08 |
| **Pends on** | Nothing — ready to be argued |

## Context

This project produces printable enclosure geometry: a core body carrying a
PCB, a pressed cap, a light pipe, a USB cable exit, and a family of mount
adapters. That geometry could live in this project's own repository, or
upstream in `quaternionmedia/apothecary`, which already exists as QM's
OpenSCAD generation toolkit and curated parts library.

Apothecary already holds the closest prior art in `parts/footpedal/`, and its
conventions — one folder per part, a Pydantic `BasePart` wrapper with a
`params_model`, category and tags, print settings, STL generation through its
CLI and API — are the conventions this geometry would otherwise reimplement.

QM's *Build the seam, buy the engines* carries an ordering rule: every new
capability first asks which engine should own it upstream before defaulting to
the seam, and seam logic is whatever no engine should reasonably own. A
parametric enclosure family is not seam logic by that definition. It is parts
in a parts library.

The counter-pressure is real and worth stating: two repositories that must move
together introduce a release-cadence dependency, and a contributor working on a
single board now touches two review queues.

## Decision

1. **All printable geometry for this project lands in
   `quaternionmedia/apothecary`**, as pull requests, in its existing
   `parts/<name>/` plus `apothecary/projects/parts/<name>.py` idiom. This
   project's repository holds no `.scad` files and no parts library.
2. **Parts are authored to be useful outside this project.** Every part takes a
   parameter model with defaults that produce a sensible object with no
   knowledge of this project's PCB, and carries `category`, `tags`,
   `description` and `print_settings` sufficient for apothecary's own browser.
   A part that only makes sense as this project's accessory belongs in this
   project, and the test is whether its defaults render something coherent.
3. **House constants are inherited, not restated.** Wall thickness, tolerance
   and cap radius follow `parts/footpedal/button.scad`'s existing values
   (`walls = 3`, `tolerence = .4`, `r = 12.5`), which are print-validated on QM
   hardware. A part needing different values states why in its module docstring.
4. **One core body, many mount adapters.** The mount is the part that varies
   across wall, desk, rack and stand; the core does not. A change that would
   fork the core body to serve a mount is a signal that the interface between
   them is wrong.
5. **This project depends on a released apothecary version**, pinned, and
   consumes parts through apothecary's CLI or API rather than by path. Geometry
   changes land upstream and arrive here by version bump, which is a reviewed
   commit rather than an ambient change.
6. **Apothecary's licensing governs the parts** — MIT, per that repository —
   and this project's hardware licensing record governs geometry that is
   inseparable from a board layout. The boundary is stated per part.

## Consequences

- The geometry gets apothecary's toolchain for free: parameter validation, STL
  generation, the viewer, the elephant-walk preview, and an existing test
  suite. None of that is rebuilt here.
- Apothecary gains a control-hardware category it does not have, which is the
  commons-first payoff: work done for one engagement becomes a library other
  people can use.
- **Accepted cost: a release-cadence dependency between two repositories.** A
  geometry fix needs an apothecary review, an apothecary release, and a version
  bump here. During active development that is friction on exactly the loop
  that iterates fastest — printing, measuring, adjusting.
- **Accepted cost: clause 2 constrains design.** Parts must be coherent
  standalone, which occasionally means a more general parameter model than this
  project needs, and a defaulting story for parameters this project always
  sets.
- Mitigation that makes the coupling survivable: parts are parametric and
  standalone by clause 2, so a core body remains useful to apothecary's users
  even if this project stalls. The dependency is one-directional.
- Obligation created: this project's CI verifies the pinned apothecary version
  can render each part it depends on, so an upstream change that breaks
  geometry fails here rather than at a printer.

## Alternatives considered

1. **Keep geometry in this project's repository.** It lost on the ordering
   rule: a parts library is an engine, apothecary is that engine, and building
   a second one inside the seam is the failure mode the doctrine names. It
   would also duplicate the wrapper, CLI, STL and viewer layers, and would
   strand the footpedal's print-validated constants in a repository this one
   cannot see.
2. **Keep geometry here during development, upstream it at first release.** It
   lost because "upstream it later" reliably becomes "upstream it never" once
   the local copy has diverged, and because the divergence is invisible while
   it is happening. Taking the friction in clause 5 up front is the smaller
   cost paid knowingly.
3. **Vendor apothecary as a submodule and develop parts inside this
   project's checkout.** It lost on review venue rather than on mechanics: the
   parts would be reviewed by this project's reviewers against this project's
   needs, producing exactly the accessory-shaped parts clause 2 exists to
   prevent, while wearing apothecary's directory structure.
4. **Split the difference: core body here, mount adapters upstream.** It lost
   because it puts the interface between core and mount across a repository
   boundary, which is the one interface clause 4 says must stay cheap to
   change.

## Revision triggers

- The release-cadence friction in Consequences measurably slows the print-and-
  measure loop, evidenced by geometry changes batching rather than shipping.
- Apothecary's part model changes such that clause 2's standalone requirement
  is no longer expressible.
- A second QM project needs the same core-plus-mount pattern, which would make
  the pattern itself a candidate for apothecary rather than a set of parts.
- This project's geometry stops being printable geometry — moulded, machined,
  or vendor-fabricated enclosures are outside what apothecary models.

## Amendments

*None.*
