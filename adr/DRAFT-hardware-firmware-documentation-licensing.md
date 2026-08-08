# ADR-XXXX — Licensing for Board Designs, Firmware, Enclosures and Documentation

| | |
|---|---|
| **Status** | Draft |
| **Date** | 2026-08-07 |
| **Pends on** | Whether this belongs at project level or as an amendment to the org open-license record |

## Context

The org's *Open-License Exclusion and Upstream-Contribution Remediation*
record fixes a criterion in terms of OSI-approved and FSF-free licenses, and
its enforcement path is a machine-generated license report checked against an
encoded allowlist. Both the criterion and the enforcement assume software.

This project's primary artifacts are not all software. A KiCad schematic and
board layout, an OpenSCAD enclosure, and a bill of materials are copyrightable
works that OSI does not review and that dependency-license tooling does not
see. A project that runs the software gate and stops there would satisfy the
letter of the org record while leaving its principal deliverable unlicensed —
which under P1 means unownable, since a recipient with no license grant cannot
modify or redistribute the thing they hold.

The org record's precedence rule permits a project to add constraints on top of
an org record and forbids waiving one. Adding a hardware clause adds
constraints, so a project record is within bounds. The argument for taking it
to org level is that the next hardware project meets the identical question,
and the org corpus's own README treats two projects asking the same question as
the signal that a clause is needed rather than repeated exceptions.

The apothecary repository, whose parts library this project extends, is MIT.

## Decision

1. **Board designs** — schematics, layouts, footprint and symbol libraries,
   fabrication outputs — are licensed **CERN-OHL-S-2.0**. Reciprocal, matching
   the org record's stance that copyleft is acceptable and contractually
   handled rather than technically avoided, and it is the hardware license with
   the clearest source-availability obligation on modified designs.
2. **Firmware and host software** are licensed **MIT**, matching apothecary and
   keeping the ESPHome and Home Assistant ecosystems' contribution paths
   frictionless.
3. **Enclosure and mechanical designs** are licensed **MIT**, matching
   apothecary, which is where they live. Mechanical work that is inseparable
   from a board design — a carrier whose geometry is derived directly from the
   layout — follows the board under CERN-OHL-S-2.0 and stays in this
   repository as a fabrication input rather than as an apothecary part. The
   boundary is stated in each part's module docstring.
4. **Documentation** is licensed **CC-BY-SA-4.0**.
5. **Every file carries an SPDX identifier**, and the repository is REUSE-
   compliant. Compliance is checked in CI; an unlicensed file fails the build.
   This is the enforcement mechanism the org record's software path gets from
   its dependency-license report, supplied for the artifacts that report cannot
   see.
6. **The bill of materials carries a sourcing constraint rather than a license
   constraint**: every line item has two or more independent sources, or a
   documented drop-in alternate footprint. A single-source component requires
   an exception record naming its exit plan and a revision trigger, by analogy
   with the seams record's treatment of single-implementation APIs.
7. **Vendor design files are not vendored under an incompatible grant.** A
   manufacturer's reference schematic, symbol, footprint or 3D model enters the
   repository only where its terms permit redistribution and modification;
   otherwise it is referenced and rebuilt.

## Consequences

- Everything a recipient needs to rebuild, modify and redistribute the physical
  product is granted explicitly, which is what P1 asks and what the software-
  only gate does not deliver.
- CERN-OHL-S is reciprocal, and that is a deliberate cost: a commercial
  integrator who modifies the board must publish their modifications. Some
  integrators will decline on that basis. The org record's position on copyleft
  makes that an accepted cost rather than a problem to design around.
- Two licenses across one repository creates a real boundary question for
  mechanical parts derived from board geometry. Clause 3 resolves it per file,
  which costs a judgement call per part and is preferable to a single permissive
  license that would weaken the board grant.
- Obligation created: a REUSE check in CI, SPDX headers as a review item, and
  a `LICENSES/` directory holding the full texts.
- Clause 6 constrains component selection in a way that will occasionally cost
  a better part. That is the same trade the seams record makes, applied to
  silicon.

## Alternatives considered

1. **CERN-OHL-P (permissive) for the boards.** It lost on reciprocity: the
   commons-first principle treats a private modification as a debt against the
   commons the business stands on, and a permissive hardware license makes that
   debt legal and invisible. CERN-OHL-P remains the right choice for a
   reference design intended for wide unmodified reuse, which this is not.
2. **CERN-OHL-W (weakly reciprocal).** It lost by falling between the two
   without a use case here; its reason to exist is permitting combination with
   differently-licensed hardware in one product, and the project's boards are
   whole units.
3. **A single license across the whole repository**, whether MIT or
   CERN-OHL-S. It lost twice over: MIT applied to boards abandons reciprocity,
   and CERN-OHL-S applied to firmware would obstruct upstream contribution into
   MIT- and Apache-licensed ecosystems, contradicting the org record's
   remediation-by-upstream-contribution clause.
4. **Defer licensing until first release.** It lost because collaborators and
   forks appear before releases do, and a grant that arrives late does not
   cover what was already distributed.
5. **Pursue OSHWA certification.** Not rejected — deferred. It is a
   certification mark rather than a license, so it decides nothing this record
   decides, and it is a reasonable step once a board has shipped.

## Revision triggers

- The org open-license record is amended to cover hardware, at which point this
  record's clauses 1 through 5 are either subsumed or become the project's
  tightening on top of it.
- CERN-OHL-S-2.0 is superseded by a later version, or a court decision
  materially changes how its reciprocity clause is read.
- A second QM project reaches the same licensing question — the corpus's own
  standard for when a clause belongs at org level.
- A single-source component under clause 6 goes end-of-life, exercising the
  exception mechanism for the first time.

## Amendments

*None.*
