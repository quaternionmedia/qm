# ADR-XXXX — QM Constitution Adoption Scope for a Factorio Mod

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-07-04 |
| **Pends on** | Org-level ratification of the QM constitution records themselves — every record in the adopted corpus is still filed `DRAFT-*` at the pinned commit, so nothing is formally `Accepted` for this project to adopt yet. This ADR fixes *this project's* disposition against that corpus regardless, so a future reader has one place to look rather than re-deriving it once org ratification lands. |

## Context

factorio-sysops vendors the org's constitution as a submodule at `governance/qm`,
on this project's dedicated branch `project/factorio-sysops`. This project is a
**Factorio mod** — Lua source (`sysadmin-poc/`) running entirely inside another
company's proprietary game engine (Factorio, by Wube Software), distributed
through the Factorio Mod Portal and/or a public GitHub repository, with no
server, no container image, no build pipeline, and no runtime the org operates.
Its only "dependency manager" is `info.json`'s `dependencies` array, which
declares other Factorio mods, not language-level packages — there is no
npm/pip/cargo-equivalent ecosystem here to run a license-report tool against.

This is the org's first Factorio-modding project, but not its first
non-server-shaped one: qmetronome (a sideloaded Android app) already
established the pattern of a project-specific adoption-scope ADR resolving
gaps the reference (self-hosted server) shape doesn't transfer, rather than
straining the literal language to fit or silently going non-compliant. Several
of qmetronome's specific findings — the platform-mandated-stack carve-out
(P5/house-stack), the closed-platform-is-out-of-scope framing for the OS
underneath a client app — recur here structurally, even though the concrete
platform (Factorio, not Android) and language (Lua, not Kotlin) differ.

factorio-sysops has two sibling projects sharing this constitution and a
`qm-factorio.code-workspace` dev layout: **datafactorio** (an optional consumer
of this mod's IT-infrastructure JSON export, per
`docs/DATAFACTORIO-INTEGRATION.md`) and **factorio-server** (a Docker/ZeroTier
dedicated server this mod can be deployed to for multiplayer testing). Each is
a separate repository; nothing here imports source from either.

## Decision

1. **Decision-record discipline — adopted in full, in effect starting with this
   ADR.** This project's `adr/` directory, its Draft → Proposed → Accepted
   lifecycle, and its squash/append-only rules govern from here forward.
2. **Open-license exclusion — adopted, scoped to what a Factorio mod actually
   ships.** The rule applies to this project's own Lua source and vendored
   assets (hand-authored + programmatically-generated PNG icons/sprites via
   `scripts/generate-icons.py`/`generate-sprites.py`, run with Pillow — MIT/
   HPND-licensed, a build-time tool, never shipped). **Explicitly out of
   scope:** the record's deployment/provenance language (SBOM-per-image,
   digest-pinned base images, offline mirrors, internal CA) — there is no
   image and no server here; the "runtime" is Factorio itself, running on
   whichever machine a player installs the mod on. **Named rather than
   silently excluded:** Factorio, the base game, is proprietary
   (commercially licensed by Wube Software) and is the platform this mod runs
   on top of — structurally identical to qmetronome's disposition that the
   Android OS underneath a sideloaded app is out of the exclusion rule's
   scope. The mod itself is the owned, open artifact; the host game engine
   isn't, and was never a candidate for §3 upstream-contribution remediation
   any more than an OS kernel would be.
3. **House stack — the mechanism is adopted, the blessed list is not; this is
   the second confirming instance of the platform-mandated carve-out.** Lua is
   Factorio's mandated modding language — there is no Python-native (or any
   other) path to a mod the game will load. The org record's own carve-out
   language ("client- or platform-mandated stacks... recorded in the
   engagement, never imported as house drift") already covers this exactly,
   generalized from qmetronome's finding. House preference continues to
   govern what QM builds when there's a choice; a game engine's loader is an
   external decider the same way a mobile OS is.
4. **Seams on standard protocols — adopted as doctrine, with one concrete
   instance today.** The mod's optional IT-infrastructure export to
   datafactorio is a file-based JSON contract (`game.write_file()` to
   `script-output/datafactorio/`, keyed `"source": "sysadmin"`) — no RCON, no
   network call, no source-level reference to datafactorio's code. This mod
   has zero networked integrations today (no backend API, no analytics, no
   telemetry) — the record is adopted for if/when that changes, not retrofitted
   onto nothing.
5. **Build the seam, buy the engines — not applicable, stated rather than
   silently skipped.** A single mod with no external services to orchestrate
   has no control-plane/engine split in the doctrine's sense. `control.lua` is
   event-handling glue against the Factorio API, not a seam over bought
   engines. Same disposition as qmetronome, same reasoning.
6. **Contribution and sponsorship policy — adopted mechanically, currently
   inactive.** No dependency is patched at build time (there is effectively no
   dependency tree to patch); nothing to register in
   `governance/qm/registers/carried-patches.md` today.
7. **Public by default (handbook policy) — adopted.** This project ships as a
   public GitHub repository (`quaternionmedia/factorio-sysops`) and, at
   release, on the public Factorio Mod Portal. No credentials or embargoed
   material exist in this repo today.

## Consequences

- Gap-closing dispositions were needed in §2 and §3 (deployment language
  scoped out; platform-mandated stack named), the same shape of gap qmetronome
  hit first — this is evidence the gap is a recurring pattern for
  non-server-shaped projects generally, not a one-off, which is exactly what
  the qmetronome perspective (`perspectives/claude-sonnet-4-6-2026-06-27-
  mobile-cross-platform-governance.md`) predicted should be watched for.
- No license-report tooling is wired in CI for this project: there is no
  language-level package manager to report against. CI here is the ADR lint
  only (`project-seed/ci/adr-lint.yml`), which is a complete, honest
  disposition of the enforcement clause for this ecosystem — not an omission.
- No carried-patch register entry is needed today (§6).
- This ADR is the natural place to update if the mod ever gains a networked
  feature (§4 becomes live), vendors an actual third-party Lua library
  distributed outside Factorio's own mod-dependency mechanism (§2's scope
  would need re-examination), or the project publishes to the Mod Portal for
  the first time (§7's disposition should be confirmed against the Portal's
  own terms).

## Alternatives considered

1. **Adopt every record literally, as written for a server project** —
   rejected: there is no image, deployment, or control plane to hang SBOM/
   GitOps language on; forcing the literal text onto a shape it wasn't written
   for is compliance theater, not compliance — the same reasoning qmetronome's
   ADR already established for this org.
2. **Treat qmetronome's ADR as sufficient by analogy and skip a
   factorio-sysops-specific one** — rejected: the platform differs (Factorio
   vs. Android), the language differs (Lua vs. Kotlin), and the specific
   proprietary-platform disposition (§2) needs its own recorded reasoning even
   though the *shape* of the argument transfers; P6 requires the decision to
   exist here, not be inferred from a sibling project's record.
3. **Leave the Python asset-generation scripts unaddressed in the license
   scope** — rejected: they are real build-time tooling (Pillow) even though
   they never ship; naming them and their license explicitly is cheaper than a
   future reader wondering whether they were overlooked.

## Revision triggers

- Any org record in the pinned corpus is ratified (`Accepted`, numbered
  `QM-NNNN`) — re-check this ADR's dispositions still match the ratified text.
- The mod is published to the Factorio Mod Portal for the first time —
  confirm §7's public-by-default disposition against the Portal's own
  distribution terms.
- factorio-sysops ever vendors a third-party Lua library outside Factorio's
  own mod-dependency declarations, or gains any networked integration — §2/§4
  become live and need re-evaluation against the specific dependency/protocol.
- A second Factorio-modding (or similar closed-game-engine) QM project exists —
  re-examine whether §2/§3's dispositions here should generalize into the org
  corpus itself, the same way a second mobile project would test qmetronome's
  proposal.
- The `governance/qm` submodule pin is bumped — re-verify this ADR's
  dispositions still match the new pinned text.

## Amendments

*None.*
