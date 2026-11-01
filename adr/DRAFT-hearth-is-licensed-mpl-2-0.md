# ADR-XXXX — hearth is licensed MPL-2.0

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-11-01 |
| **Pends on** | Nothing — ready for ratification |

## Context

The corpus's `records/DRAFT-outbound-licensing.md` licenses QM's work by
kind: services AGPL-3.0-or-later (§4), single-file visualization deliverables
MPL-2.0 (§5), and embeddable libraries and client SDKs MPL-2.0 per library,
named in that project's own record and never as a default (§6). hearth is a
library: members import `hearth.Member` and its hosts, and an exemplar
imports or copies `hearth.coordinator`. Three of the members it is imported
into are MIT from before the corpus, and the services the corpus plans are
AGPL.

## Decision

hearth, distributed as `qm-hearth`, is licensed **MPL-2.0** under §6 of the
outbound record, without Exhibit B, so it combines into QM's AGPL services and
into the members' permissive code alike. Copyright is Quaternion Media's
(§0). The declaration is `REUSE.toml`: MPL-2.0 for every file of hearth's
own; CC0-1.0 for the seed's copy-forward files, `AGENTS.md` and its two
pointers, as the corpus licenses them (§2); Apache-2.0 for the seed's
workflows and editor files (§3). `LICENSE` and `LICENSES/` carry the texts,
`pyproject.toml` names the expression, and `reuse lint` is the gate.

## Consequences

- A file-level copyleft: a modified copy of a hearth file, the coordinator
  copied into an exemplar included, stays MPL-2.0 and open, while the
  exemplar's own files beside it take the exemplar's licence. §6's concession
  stands: a proprietary consumer may add files beside hearth's.
- A dependency under a stronger copyleft cannot enter hearth's runtime path
  without this record changing.

## Alternatives considered

1. **AGPL-3.0-or-later**, as a service (§4). Lost: hearth serves nothing of
   its own; it runs inside members and exemplars, and AGPL would reach into
   every member's code, three of which are MIT.
2. **MIT**, as the members are. Lost: it is outside the outbound record's
   clauses, so it would need an amendment there, and it would let a modified
   coordinator ship closed, which the copy model makes likely.

## Revision triggers

- A hearth server of its own that a show machine runs, which §4 of the
  outbound record would call a service.
- A change to the outbound record's §6.

## Amendments

*None.*
