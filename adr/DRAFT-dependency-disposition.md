# ADR-XXXX — frizzle's dependency disposition and packaging tool

| | |
|---|---|
| **Status** | Draft |
| **Date** | 2026-08-16 |
| **Pends on** | frizzle's outbound licence identifier, which the adoption record defers to spawn |

## Context

frizzle is a Python 3.13 service: an MQTT dispatcher that journals the bus,
adds work-queue semantics on top of a fire-and-forget transport, and writes a
`bus-status` collector document. It stands on FastAPI, SQLModel/Pydantic and
pytest, all of which the house-stack record names.

It also stands on five things the house-stack record does not name, and one
thing the record names differently:

- **uv**, where the record says PDM, "with a committed lockfile".
- **typer**, where the record says Click for CLIs.
- **aiomqtt**, **structlog**, **prometheus-client** and **uuid6**, which the
  record does not mention at all.

The house-stack record's §2 is unambiguous about what that costs: "A
dependency outside the set appearing in review without a linked record fails
review." This record is that link.

The record also names this exact situation as one of its own revision
triggers — "A QM project is found standing on a packaging tool other than the
blessed one" — and says it is "answered the same way rather than by defending
the current text." Its Context notes the set records PDM "because that is what
QM builds with; a project standing on uv would be the same trigger firing in
the other direction." loopwall's `DRAFT-dependency-disposition.md` runs on uv
and states it, with the licence gate reading `uv.lock`.

The outbound-licensing record additionally requires a baseline component audit
at adoption: every component in a deployed runtime path, its licence, and its
disposition.

## Decision

**§1. frizzle stands on uv, and says so.** The lockfile is `uv.lock`,
committed. `uv sync` is the install path and `uv run` is the entry point in
the README, in `AGENTS.md`, and in CI. This is a divergence from the
house-stack record's packaging entry, taken deliberately and recorded here
rather than left to be discovered in review.

**§2. The divergence is registered against the house-stack record's own
revision trigger**, not asserted as an exception to it. frizzle does not claim
uv is better than PDM. It claims only that frizzle is standing on uv today,
that migrating it is work with no current benefit to weigh against the cost,
and that the org-level question of which tool the house stack names is a
question for the house-stack record to answer at org level — where a second
project on uv is evidence, and this record is one of the two.

**§3. typer is used for the CLI in place of Click.** typer is a typed wrapper
over Click and resolves to Click at runtime, so the divergence is narrower
than it reads: the blessed dependency is present, reached through a typed
facade. No separate migration is proposed.

**§4. Baseline component audit.** frizzle's **direct** dependencies, their
licences as published in distribution metadata, and their disposition. The
transitive set is covered in §4b, which is the part the open-license record
actually asks for:

| Component | Version | Licence | Runtime path | Disposition |
|---|---|---|---|---|
| fastapi | 0.141.1 | MIT | yes | Keep — house stack names it |
| uvicorn | 0.52.2 | BSD-3-Clause | yes | Keep — FastAPI's server |
| sqlmodel | 0.0.39 | MIT | yes | Keep — house stack names it |
| pydantic | 2.13.4 | MIT | yes | Keep — house stack names it |
| aiosqlite | 0.22.1 | MIT | yes | Keep — SQLite async driver; house stack permits SQLite for single-node tools |
| aiomqtt | 2.5.1 | BSD-3-Clause | yes | Keep, with the seam named in §5 |
| structlog | 26.1.0 | MIT OR Apache-2.0 | yes | Keep — structured logs are what the collector emits |
| prometheus-client | 0.26.0 | Apache-2.0 AND BSD-2-Clause | yes | Keep — `/metrics` is the monitoring seam |
| typer | 0.27.1 | MIT | yes | Keep per §3 |
| uuid6 | 2025.0.1 | MIT | yes | Keep — the envelope contract mandates UUIDv7 ids |
| pytest | 9.1.1 | MIT | no (dev) | Keep — house stack names it |
| pytest-asyncio | 1.4.0 | Apache-2.0 | no (dev) | Keep |
| httpx | 0.28.1 | BSD-3-Clause | no (dev) | Keep — house stack names it |

**§4b. The transitive set.** The open-license record asks for libraries
"transitive, SBOM-surfaced", not just the direct ones. `uv.lock` resolves to
**43 packages**; §4's thirteen are the direct subset. Reading licence metadata
across all 43 finds every licence OSI-approved, and **two that carry copyleft
options**:

| Component | Version | Licence | Note |
|---|---|---|---|
| `paho-mqtt` | 2.1.0 | `EPL-2.0 OR BSD-3-Clause` | aiomqtt's transport — squarely in the runtime path. Dual-licensed, so BSD-3-Clause may be taken |
| `certifi` | 2026.7.22 | `MPL-2.0` | Weak copyleft, file-scope. Reached via httpx/httpcore; no frizzle source is a derivative of it |

Neither constrains frizzle's outbound identifier: MPL-2.0 is file-scope, and
`paho-mqtt` is dual-licensed so the BSD-3-Clause branch may be taken. This is
the reasoning the adoption record's §3 relies on when it defers that
identifier — stated here in full, because "these are all permissive" is the
kind of summary that is easy to assert and wrong in exactly the two cases
that matter.

This table is a snapshot. The licence gate regenerates it from `uv.lock`, so
it is checked by a machine rather than re-asserted by a human.

**§5. Seam protocol.** frizzle reaches its broker over **MQTT 3.1.1/5**, a
published protocol with multiple independent implementations, through aiomqtt.
The replaceability test: `src/frizzle/broker.py` is the only module that
imports aiomqtt, and it is deliberately thin — connect, publish an envelope,
iterate envelopes. Replacing the client library is a rewrite of one file
against an unchanged protocol. Replacing the *broker* costs nothing in frizzle
at all, because frizzle speaks MQTT and not Mosquitto.

**§6. Service inventory.** frizzle depends on exactly one third-party service
in a runtime path: an **MQTT broker** (Mosquitto in the moat deployment, and a
local container in development). The ownability test is answered: QM runs the
broker itself, on its own cluster, from a chart in moat. There is no
third-party hosted service, no vendor account, and no API key anywhere in a
frizzle runtime path. Nothing else qualifies — the journal is a local SQLite
file and the metrics surface is scraped, not pushed.

**§7. No carried patches.** No dependency is a `git+` URL, a vendored fork, or
a build-time patch. There is nothing to register in
`registers/carried-patches.md`. This clause is a claim to be re-checked when a
dependency is added, not a permanent property.

## Consequences

- The licence gate reads `uv.lock`, as loopwall's does. A gate written against
  a PDM lockfile does not apply to this repository, and the gate obligation is
  discharged against the manifest frizzle actually has.
- The house-stack record has a second project's worth of evidence pointing at
  its packaging entry. Two projects on uv is a fact the org record should
  answer at org level; this record does not answer it, and does not pretend to.
- A contributor who "fixes" frizzle toward PDM without amending this record has
  made an unrecorded change to a recorded decision. `AGENTS.md` says so at the
  point of contact.
- §4/§4b are snapshots with a date on them. They are extended when a component
  is added, and they are not evidence about any commit but the one carrying
  them. The licence gate regenerates §4b from `uv.lock`, so drift is a failing
  check rather than a stale table nobody re-reads.
- §7's emptiness is the useful part of it: it is a searched-and-found-nothing,
  not an unasked question.

## Alternatives considered

1. **Migrate frizzle to PDM.** The literal reading of the house-stack record,
   and it would close the divergence outright. It loses because the record's
   own revision-trigger clause says a project found on another packaging tool
   is a trigger to answer at org level, "rather than by defending the current
   text" — and because the migration is real work whose only benefit is
   matching a sentence that the same record invites re-examining. If the org
   answers the trigger by keeping PDM, frizzle migrates then, with a decision
   behind it.

2. **Say nothing and ship on uv.** What most projects do, and what the audits
   keep finding. It loses on §2 of the house-stack record: an out-of-set
   dependency without a linked record fails review. Silence here is the drift
   the record exists to catch.

3. **Claim a project-level exception to the house-stack record.** It loses on
   the precedence rule in the corpus README: a project record may add
   constraints on top of a QM record, never waive one. A genuine exception is
   an amendment to the org record, ratified at org level. This record is
   therefore written as evidence feeding a trigger, not as a waiver.

4. **Replace typer with Click directly.** Rejected as churn: typer resolves to
   Click, so the blessed dependency is already in the tree, and the CLI's
   type-annotated option definitions would be rewritten by hand for no
   behavioural gain.

## Revision triggers

- The house-stack record's packaging entry is amended, in either direction —
  frizzle then matches it or amends this record.
- A dependency is added to frizzle that is not in the §4 table. The table is
  extended in the same change.
- Any component in §4 relicenses, is archived, or loses its maintainer.
- The quarterly upstream scan reports a licence-file change on a pinned
  upstream.
- aiomqtt stops tracking the MQTT specification, or a second module in frizzle
  acquires a direct aiomqtt import — either one breaks the §5 replaceability
  claim.
- frizzle acquires a dependency on a hosted third-party service, which would
  make §6's answer stop being "QM runs it".

## Amendments

*None.*
