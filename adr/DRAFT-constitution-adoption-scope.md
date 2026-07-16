# ADR-XXXX — QM Constitution Adoption Scope for loopwall

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-07-16 |
| **Pends on** | Org-level ratification of the QM constitution records themselves — every record in the adopted corpus is still filed `DRAFT-*` at the pinned commit, so nothing is formally `Accepted` for this project to adopt yet. This ADR fixes *this project's* disposition against that corpus regardless, so a future reader has one place to look rather than re-deriving it once org ratification lands. Also pends the human decision on whether `quaternionmedia/loopwall` is public at creation (§7). |

## Context

loopwall vendors the org's constitution as a submodule at `governance/qm`,
pinned by this branch's ancestry to `main` tip `4541f92df9fc9a3b3b8c04358ec173687c5e35cb`
("Confirm and wire equal Windows/POSIX symlink treatment, not accepted
asymmetry"). Unlike the org's mobile-project precedent (qmetronome, whose
`adr/README.md` opens with "this project is a deliberate experiment, not a
clean instance"), loopwall is a much closer fit to the corpus's default
shape: a Python service with a control-plane/engine architecture is exactly
what the org records were extracted from (the streaming-infrastructure
project). This ADR records that fit disposition-by-disposition rather than
asserting it in prose, covering all eight records/policies in the pinned
snapshot (`records/DRAFT-decision-record-discipline.md`,
`records/DRAFT-open-license-exclusion-and-upstream-remediation.md`,
`records/DRAFT-seams-on-standard-protocols.md`,
`records/DRAFT-build-the-seam-buy-the-engines.md`,
`records/DRAFT-house-stack.md`,
`records/DRAFT-contribution-and-sponsorship-policy.md`,
`records/DRAFT-human-only-contributorship.md`,
`records/DRAFT-ide-integrated-governance-discovery.md`, plus
`handbook/public-by-default.md`), each already anticipated by `PLAN.md` §2
("Governance position") before this ADR existed.

## Decision

1. **Decision-record discipline — adopted in full, already in effect.**
   This directory (forked from `project-seed/adr/`), its
   Draft→Proposed→Accepted lifecycle, and its squash-before-ratification /
   append-only-after-ratification rule are how this ADR and its three
   sibling drafts (`DRAFT-ldp1-driver-seam.md`,
   `DRAFT-retroactive-capture-semantics.md`,
   `DRAFT-dependency-disposition.md`) are written. No further action beyond
   the CI lint job (`adr/README.md`'s CI enforcement section).
2. **Open-license exclusion — adopted, scoped to a single-host runtime.**
   The core rule (every shipped component carries an OSI-approved/FSF-free
   license, with named exceptions only) is fully discharged by
   `DRAFT-dependency-disposition.md`'s component table. Scoped: the
   deployment/provenance language (SBOM-*per-image*, digest-pinned base
   images, offline mirrors, internal CA, restore-verified backups) assumes a
   self-hosted server runtime this project doesn't have — loopwall runs as a
   single host process (`PLAN.md` §3: "Single host; one monotonic clock");
   the equivalent gate is a dependency-manifest-plus-allowlist check against
   `uv.lock`, named in `adr/README.md`'s CI enforcement section.
3. **Seams on standard protocols — adopted, already the project's central
   design decision.** `DRAFT-ldp1-driver-seam.md` is the seam-instance
   record; the replaceability test passes directly (three independent
   driver implementations named against one protocol: `cli`, `hapax`,
   `showrunner`).
4. **Build the seam, buy the engines — adopted, already stated in
   `PLAN.md` §2–§3.** The seam (LDP, scheduler, wall core) is built; the
   engines (FFmpeg, MediaMTX, Chromium, anime.js, the looper hardware) are
   bought, not written. No project-level seam-instance record beyond
   `DRAFT-ldp1-driver-seam.md` is needed — the driver boundary *is* the one
   seam this project has.
5. **House stack — adopted, clean fit, no carve-out needed.** Pydantic,
   FastAPI, Click, pytest are the exact blessed Python stack (`PLAN.md`
   §2). The renderer's vanilla ES modules plus vendored anime.js are not a
   departure from P5 either — "single-file HTML/JS for visualization
   deliverables" is named in the house-stack principle itself, not an
   exception to it.
6. **Contribution and sponsorship policy — adopted mechanically, currently
   inactive.** The org carried-patch register
   (`governance/qm/registers/carried-patches.md`) requires an entry for any
   build-time-patched dependency. loopwall carries none at scaffold time —
   nothing to register, but the obligation is adopted so a future patched
   dependency (e.g. a local FFmpeg patch) doesn't get missed.
7. **Public by default (handbook policy) — adopted.** `quaternionmedia/loopwall`
   is intended to be public on GitHub with public Actions runs, consistent
   with every other QM project; the one anticipated exception is stage/venue
   credentials (Hapax pairing, showrunner endpoints) at 1.0.0+, kept out of
   the repo by `D2` (secrets by reference only, per `HANDOFF.md`'s session
   protocol) rather than by closing the repo. If a broader reason to close
   any part of the repo emerges, it is named here as an amendment, not
   assumed silently.
8. **Human-only contributorship — adopted.** No commit in this submodule or
   in the loopwall repo proper names a model or a vendor `noreply@` address
   as author or co-author; tool involvement is disclosed as a `Tools:` note
   where an artifact calls for one (e.g. `perspectives/`), never as a
   byline.
9. **IDE-integrated governance discovery — adopted.** loopwall's own repo
   root carries `AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md`,
   `.vscode/settings.json`, and `.vscode/extensions.json`, copied from
   `project-seed/ide/` per the org record's §3, with project-specific
   setup/test commands filled in below `AGENTS.md`'s marked line.

## Consequences

- Every org record in the pinned snapshot has a stated, specific disposition
  against this project rather than an assumed blanket "adopted" — the point
  of this ADR existing at all (P6: decisions are documented or they didn't
  happen).
- No deferred cost or open carve-out is created by this ADR; §2 and §7 are
  the only two records needing a scope note rather than a direct 1:1 fit,
  and both are named plainly rather than smoothed over.
- This ADR is the natural place to revisit if loopwall ever gains a
  networked deployment shape (a second host, a container image) — at that
  point §2's dependency-manifest gate would be augmented or replaced by the
  org's default SBOM-per-image gate, not this ADR silently reinterpreted.

## Alternatives considered

1. **Adopt every record literally, including the SBOM-per-image language,
   by treating the single host as "an image of one"** — rejected: strains
   the record's own language for no enforcement benefit; a
   dependency-manifest-plus-allowlist gate against `uv.lock` catches the
   same class of problem (an unvetted dependency license) without inventing
   a fictional image build.
2. **Skip an adoption-scope ADR entirely, since `PLAN.md` §2 already maps
   every principle to an architecture decision** — rejected: `PLAN.md` §2 is
   a summary table inside the project's own design document, not this
   project's ADR corpus; per the org's own drafting-session handoff
   contract, the ADR corpus is what a cold session reads first, and it
   should not have to cross-reference a different document's summary table
   to find the project's adoption disposition.

## Revision triggers

- Any org record in the pinned corpus is ratified (`Accepted`, numbered
  `QM-NNNN`) — re-check whether this ADR's dispositions still match the
  ratified text.
- loopwall's runtime shape changes from a single host to a networked/
  multi-host deployment — §2's dependency-manifest gate is revisited against
  the org's default SBOM-per-image gate.
- loopwall ever vendors a build-time-patched dependency — §6's carried-patch
  register entry is no longer optional.
- The `governance/qm` submodule pin is bumped — re-verify this ADR's
  dispositions still match the new pinned text.

## Amendments

*None.*
