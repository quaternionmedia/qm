# QM-XXXX — Outbound Licensing of QM Work

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-08-08 |
| **Pends on** | Nothing — ready for ratification |
| **Principle** | P1 — ownership is the deliverable; P2 — commons-first economics; P7 — public by default |

## Context

The open-license record fixes what QM may consume. Nothing states what QM's
own work is licensed under, and no repository on any branch of this corpus
carries a licence file. A public repository with no licence grants no rights
beyond reading, so P7's default publishes the artifact and withholds the
commons — the opposite of what publishing it was for.

The gap is not theoretical. This corpus's fork procedure instructs an adopting
project to copy `TEMPLATE.md`, `project-seed/adr/`, `project-seed/ci/` and
`project-seed/ide/` verbatim into its own repository, including a client's,
with no terms attached. The seed workflow says so in its own header. Read
literally, the open-license record's §1 also binds QM's own components, which
makes every unlicensed QM artifact a violation of the rule QM wrote. The
reference project demonstrates it: the streaming design plan gives its own
service a License column reading `ours`, which names nothing, while the same
plan requires the build to fail on any licence outside the allowlist.

Delivery mechanism, not preference, decides which licence holds a guarantee.
A self-hosted service is never conveyed, so a copyleft whose trigger is
distribution fires on nothing. A single-file HTML deliverable is one file, so
a file-scoped rule and a whole-work rule coincide. A library exists to be
embedded in work QM does not control. A fork carries someone else's code. A
template exists to be copied without obligation. One licence across all of
them either blocks the consulting practice or surrenders the guarantee it
exists to hold, so this record sets a licence per artifact class and states
which class is the weak one.

Two constraints shape the choice beyond openness. QM contributes upstream in
the target community's language and idiom, and an outbound licence must not
obstruct that. QM also sells to clients, and a licence that reaches into a
client's own product is a licence the client declines.

## Decision

0. **Copyright in QM work is held by Quaternion Media.** Every notice, SPDX
   header and attribution string names the entity, not an individual
   contributor, and the §8 inbound grant is what routes a contributor's
   rights to it.
1. **Corpus prose** — this constitution's records, charter, README, handbook
   and registers — is licensed **CC-BY-SA-4.0**. Share-alike keeps a
   derivative constitution open; attribution is the same accountability trail
   the human-only contributorship record protects. `perspectives/` is
   excluded, per §11.
2. **Copy-forward prose templates** — `TEMPLATE.md`, `project-seed/adr/`, and
   `project-seed/ide/AGENTS.md` — are licensed **CC0-1.0**. These exist to be
   copied verbatim into repositories QM does not govern. Terms that follow
   the copy would export QM's licence into a client's repository and make the
   fork procedure a legal review.
3. **Executable seed files** — `project-seed/ci/`, and the checked-in editor
   configuration under `project-seed/ide/.vscode/` — are licensed
   **Apache-2.0**. Same copy-forward requirement as §2, but CC0 grants no
   patent licence and is not fit for executable content.
4. **QM services and control planes** are licensed **AGPL-3.0-or-later**.
   Network use is the delivery mechanism for a self-hosted service, and
   AGPL §13 is the only clause among the candidates that fires on it.
5. **Single-file HTML and JS visualization deliverables** are licensed
   **MPL-2.0**. The file boundary and the deliverable boundary are the same
   object here, so modified copies and host pages that inline the file stay
   open, while a page embedding it as a separate asset is a Larger Work and
   is untouched.
6. **Embeddable libraries and client SDKs** may be licensed **MPL-2.0**, per
   library, named in that project's own record, never as a default. Exhibit B
   ("Incompatible With Secondary Licenses") is not attached, so such a library
   stays combinable into QM's own AGPL services. **This clause concedes that a
   proprietary consumer may add files alongside and ship a closed product.**
   It is the one place the guarantee is deliberately thin, and the per-library
   record is what keeps the concession narrow enough to see.
7. **Hardware.** Board designs — schematics, layouts, footprint and symbol
   libraries, fabrication outputs — are licensed **CERN-OHL-S-2.0**, the
   reciprocal hardware licence with the clearest source-availability
   obligation on a modified design. Hardware documentation is
   **CC-BY-SA-4.0**, matching §1. **Firmware, host software and mechanical
   designs take a permissive licence where the target ecosystem's
   contribution path requires one**, named in that project's own record with
   the ecosystem stated; MIT for an ESPHome or Home Assistant integration is
   the case that prompted this clause. This is an org-level term, not a
   project waiver: a project selecting it is applying this record rather
   than relaxing it.
   Licensing hardware is necessary and is not sufficient. A published design
   carrying a sole-source part in a package no accessible process can place
   is legally open and practically unbuildable, so a project shipping
   hardware records its sourcing and fabrication constraints alongside the
   grant. Openness here is a reproducibility property that a licence alone
   does not deliver.
8. **Forks and carried patches, including a fork promoted to a maintained QM
   project, keep the upstream's licence unchanged.** QM's default never
   displaces the licence of code QM received.
9. **Code QM contributes upstream carries the target's licence at the moment
   of contribution.** Every QM repository takes contributions under a
   Developer Certificate of Origin sign-off together with an express grant
   permitting QM to license the contribution under any OSI-approved licence
   for the purpose of upstream contribution. Without the inbound grant the
   outbound promise is unenforceable the moment a third party contributes.
10. **Client-commissioned work** takes the clause matching its shape, is
    published in a public QM repository, and leaves the client holding the
    same rights as everyone else. A client requiring exclusivity is a scoping
    outcome. QM operates no proprietary-exception or commercial dual-licence
    programme.
11. **`perspectives/` carries no outbound grant.** The directory holds
    attributed opinion and primary-source transcripts substantially produced
    by language models under human direction, and QM's rights to relicense
    that material are not settled. It is marked all-rights-reserved rather
    than licensed under §1, and stays readable in a public repository without
    a grant QM may not be entitled to make. This is a statement about
    uncertain provenance, not a change to the standing of perspectives, which
    remain non-binding and citable by author and date. A perspective whose
    text is wholly human-authored may be moved under §1 by its author saying
    so in its own header.
12. **Enforcement.** Every QM repository is REUSE-compliant: a `LICENSES/`
    directory holding the SPDX text of each licence in use, an
    `SPDX-License-Identifier` on every file, unannotatable paths such as
    symlinks covered by `REUSE.toml`, and `reuse lint` as a required CI
    check. The repository declares its class in its adoption record, and a
    file whose SPDX expression falls outside the declared class fails the
    same check. The quarterly upstream scan the open-license record already
    mandates extends to QM's own repositories. Changes to this class table
    are amendments to this record.

## Consequences

- P7 gains legal effect. Publication becomes a grant rather than a gesture,
  and the fork procedure stops instructing projects to copy files they have
  no permission to copy.
- `reuse lint` is independent of runtime shape, so a project that cannot run
  an SBOM gate still gets an outbound gate that works identically. That
  answers the gap the qmetronome onramp retrospective names, where the
  open-license record's enforcement assumed a container.
- Clients operating a blanket AGPL prohibition are out of scope for service
  work. Cost accepted, on the same footing as the contribution clause the
  contribution and sponsorship record already carries.
- §6 is where the guarantee is thinnest, stated in the open rather than
  discovered later by a reader comparing the class table against MPL's own
  scope.
- Cost accepted: every repository needs a licensing pass before the check can
  block. This corpus has had one and its check blocks from the start. No
  other QM repository has been inventoried, so each runs `reuse lint` in
  reporting mode until its own pass is done, and this record is amended with
  the date the check becomes blocking org-wide.
- The symlinks this corpus ships cannot carry an SPDX header, since writing
  one writes into the target. They are covered by `REUSE.toml` instead, which
  is the mechanism REUSE provides for exactly this case.
- §11 leaves the most-read directory in the corpus without a grant, which is
  a visible cost. It is preferred to the alternative of asserting rights QM
  may not hold in order to make a licence table look complete.
- §7's permissive-firmware term is the one place this record blesses a
  permissive licence by default. It is bounded by requiring the target
  ecosystem to be named, so the clause cannot be reached for on preference.

## Alternatives considered

1. **MPL-2.0 as the org default** — rejected. Its copyleft is file-scoped:
   Mozilla's own FAQ states that a file containing no covered code is not a
   Modification even inside a Larger Work, and that covered code may be
   statically linked into a larger proprietary product. For a Python package,
   where the unit of reuse is the import rather than the file, a closed
   product consumes QM's work having triggered nothing. It survives at §5 and
   §6, where the file boundary is the real boundary.
2. **GPL-3.0-or-later for services** — rejected: hosting is not conveying, so
   the hole this record exists to close stays open while the full friction of
   strong copyleft is paid anyway.
3. **AGPL-3.0-or-later everywhere** — rejected: it reaches into the client's
   own product at exactly the classes QM ships to clients, and would make the
   embeddable deliverable unsellable.
4. **Apache-2.0 or MIT throughout** — rejected: no derivative-openness
   guarantee at all, which reduces P1 and P2 to descriptions of QM's habits.
   It genuinely removes all upstream-contribution friction; that is the
   benefit being traded away, and §8 is the cheaper way to buy it back.
5. **EUPL-1.2** — rejected on legibility rather than substance. Its
   distribution definition reaches network use and its appendix relicenses
   outward to GPL and AGPL, so it is close to fit; but neither Python
   packaging convention nor client counsel reads it fluently, and a licence
   nobody in the room can interpret is a licence that gets argued about.
6. **LGPL-3.0 for libraries** — rejected: its boundary is drawn at linking, a
   test that maps badly onto an interpreted import.
7. **CC0-1.0 for corpus prose** — rejected: it surrenders the attribution and
   share-alike that are the reason to license a constitution at all. Retained
   at §2 only where copying without obligation is the point.
8. **Dual licence with a paid proprietary exception** — rejected on
   internal consistency. It is the open-core shape whose collapse the
   open-license record cites as its founding evidence. QM cannot make MinIO
   the cautionary tale of its consumption doctrine and MinIO's model its
   production doctrine.
9. **Publish with no licence** — rejected: the state this record ends.

## Revision triggers

- A second client engagement lost on the §4 clause.
- A §6 library observed shipping inside a closed product with nothing
  flowing back — the concession is being used as a channel rather than an
  exception.
- Any licence named here held unenforceable in a jurisdiction QM contracts
  in.
- A second project asks the hardware-licensing question the datum project
  raised — the signal that the class table needs a hardware row at org level
  rather than repeated project-level answers.
- A third party adopts this corpus and asks to relicense a derivative.
- `reuse lint` reports a class violation that turns out to be the class table
  being wrong rather than the file.

## Amendments

*None.*
