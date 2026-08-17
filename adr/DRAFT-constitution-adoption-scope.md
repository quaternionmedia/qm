# ADR-XXXX — frizzle adopts the QM constitution, and what that covers

| | |
|---|---|
| **Status** | Draft |
| **Date** | 2026-08-16 |
| **Pends on** | frizzle's outbound licence identifier (§3), and the spawn actions in §7 that need push access to the qm remote |

## Context

frizzle is the QM bus dispatcher: journal, work-queue semantics and collector
over an MQTT transport. (The plan also names a rule engine; none is
implemented, and the README says so rather than letting the description imply
otherwise.) It was decided on 2026-08-13 and built
as a local scaffold to prove the dispatcher design and the three cookbook
recipes before paying the cost of the spawn ceremony.

frizzle is the first repository intended to be born from `project-seed`. Every
adopter so far was retrofitted, so this adoption is also the seed's first live
test — plan ledger N1 asks for every friction point to be recorded, and §8 of
this record is that list.

The order of events matters for reading this record honestly. The scaffold was
written first and the governance artifacts applied to it afterwards. That makes
frizzle a project that predates its adoption of the corpus, in the sense the
fork handbook means, and it is why §2 is a conflict table rather than a
declaration of compliance. A repository is not compliant because it copied the
seed.

This record is written against the qm corpus as read from a local working
tree checked out on `project/loopwall`. **The pin is not verifiable from that
tree.** The kickoff bundle stamps itself `qm@104361a`; that object does not
resolve in the clone this record was written from, whose `origin/main` tip
(`b94d910`, 2026-08-08) predates the bundle's own stamp date, and which is in
turn behind the real remote (`fde5dfc`). The discipline record's evidence
clause exists so staleness is checkable, and a pin that resolves to nothing
defeats it while appearing to satisfy it. **Re-derive the pin from a freshly
fetched qm before relying on any claim here about corpus content**, and record
the resolved SHA in its place at spawn.

Every org record in the corpus is `Proposed`; none is ratified, pending qm's
own second-code-owner condition. Nothing here can therefore cite a ratified
record, and this record stays a draft alongside them.

## Decision

**§1. frizzle adopts the Quaternion Media constitution** as vendored at
`governance/qm`, pinned to the `project/frizzle` branch of the qm repository.
frizzle's own records live on that branch and are not copied into this
repository's git history.

**§2. Known conflicts with org records, and their disposition.** Each row is a
conflict this adoption inherits, what it violates, and what compliance looks
like.

| Conflict | Record violated | Reproduction | Compliance looks like | Pinned by |
|---|---|---|---|---|
| No `governance/qm` submodule is mounted | fork handbook steps 1–3 | `git submodule status` is empty | Submodule at `governance/qm`, `branch = project/frizzle` in `.gitmodules`, canonical remote URL | §7.1 — needs the branch to exist on the qm remote |
| Records staged in-repo at `frizzlekickoff/records-for-qm/` | corpus README: a project's `adr/` lives on its qm branch | The directory exists | The two drafts on `project/frizzle`; the directory deleted | §7.2, and that directory's own README |
| Outbound licence identifier undecided | outbound-licensing §12 | `REUSE.toml` declares `LicenseRef-QM-Undecided` | A decided identifier, `LICENSES/` holding its text, `reuse-lint` blocking | §3 |
| `reuse lint` runs non-blocking | outbound-licensing §12 | `continue-on-error: true` in the workflow | The flag removed, in the same change that sets §3 | §3 |
| No per-file SPDX headers | outbound-licensing §12 | `grep -r SPDX-License-Identifier src/` is empty | Headers stamped once the identifier is known; `REUSE.toml` retained for symlinks, `uv.lock` and JSON | §3 — stamping a guess would be rewritten wholesale |
| uv and typer, against the house stack's PDM and Click | house-stack §1–§2 | `uv.lock` at the repository root | An org-level answer to the packaging trigger, or migration | `DRAFT-dependency-disposition.md` §1–§3 |
| No SBOM gate | open-license §4 | `.github/workflows/` has no SBOM job | An SBOM gate per container image. frizzle ships no image, so none is owed today; adding a Dockerfile adds this obligation beside the manifest gate, not instead of it | Revision triggers |
| Upstream scan is partial | open-license §4 | `license-gate.yml` runs quarterly but reads installed metadata | A scan that also watches pinned upstreams for archive status and licence-file changes, which reading local metadata cannot see | §7.4 |
| frizzle absent from `governance-status.yaml` and `harness-status.json` | spawn checklist step 6 | frizzle appears in neither | Registered in both | §7.3 |
| No control-plane instance record | build-the-seam | No such record exists | A record naming what frizzle's seam owns and refuses to own, with size-smell thresholds | §5 |
| Contract documents are drafts expecting revision | — | `contract/envelope-v0.md` says so | v0 revised from the rad PoC, or frozen deliberately | Revision triggers |

Naming a gap is not waiving it. Every row above is open, and the table is
re-derived when the repository changes rather than left to rot — two rows were
closed by the licence gate landing, and a stale conflict table is a compliance
surface that lies in the reassuring direction.

**§3. The outbound licence is deferred to spawn, and the deferral is
mechanised.** The outbound-licensing record's class table assigns
`AGPL-3.0-or-later` to "QM services and control planes", which is the class
frizzle falls in. The spawn checklist reserves the decision for a human. Both
hold, so the repository declares `LicenseRef-QM-Undecided` — a no-grant notice
naming the hold as deliberate — in `REUSE.toml` alone, rather than stamping a
guessed identifier into every file. Setting the real identifier is then a
one-line edit plus a licence text, and the procedure is written into
`REUSE.toml` at the point of change. `reuse lint` passes clean, in reporting
mode. (No file count is quoted: it changes with every file added, and a stale
number inside a record is worse than no number. Run the command.)

**§4. Seed artifacts are carried in full, not partially.** `.github/workflows/`
carries `adr-lint.yml` and `submodule-check.yml` byte-identical to the seed.
`reuse-lint.yml` differs from the seed by one sanctioned decision — adding the
`continue-on-error: true` its own header instructs a project to add while its
licensing pass is unfinished — carried as eight added lines, the flag plus the
comment justifying it. That edit is row 4 of §2.
`.vscode/settings.json` and `extensions.json` are byte-identical to the seed.
`AGENTS.md` is the seed's with `<name>` substituted and project content added
below its marked line — plus two edits *above* it, which the seed's header does
not sanction: "vendored at" became "to be vendored at", and a note was added
saying the submodule is not mounted. The seed's text asserts a submodule that
does not exist, and sending a reader to `governance/qm/README.md` with no
warning is a worse failure than the deviation. Recorded here rather than left
for an audit to find. `CLAUDE.md` and `.github/copilot-instructions.md` are
git symlink objects at mode `120000`, and `.gitignore` carries the negations
that keep the `.vscode/` pair committable.

Three workflows the seed does not carry are added. `symlink-integrity.yml`,
adapted from qm's own root workflow because `project-seed/ci/` omits it and
degraded pointer files are the defect the propagation audits report most.
`tests.yml`, because a substantial suite with no CI running it is the exact
condition this project's own plan ledger criticises another repository for by
name. And `license-gate.yml` with `ci/license_gate.py`, the open-license
record's per-ecosystem dependency-manifest gate, which no seed file provides.
All three are tightenings, which the precedence rule permits; none is claimed
to be seed CI.

**§5. frizzle's seam, stated.** frizzle owns the bus's *memory and job
semantics*: journaling every envelope on `qm/#`, claim/ack/retry/dead-letter,
heartbeats, and the `bus-status` document. It refuses to own the view surface —
`/health`, `/metrics` and `/bus-status` are the whole HTTP contract, and no
dashboard opens a socket to the broker. It refuses to own orchestration, which
stays out of the qmcp server plane; frizzle integrates with qmcp as a client.
Size smells that trigger revision: a fourth HTTP route that serves a view; a
second module importing aiomqtt directly; a rule engine that grows
project-specific branches rather than reading rules as data. This clause is a
first statement and wants its own record, per the build-the-seam obligation.

**§6. Risk register.** Governance and abandonment risk for frizzle's selected
components lives in `DRAFT-dependency-disposition.md` §4–§6. The standing risks
this adoption carries: the moat Mosquitto chart is unverified inference, drafted
by reading moat's idiom rather than by deploying; broker auth and ACL design is
undecided and the development broker allows anonymous connections; and MQTT
round-trip latency against rad's tolerances is unmeasured.

**§7. The spawn actions this record pends on.** None can be taken without push
access to the qm remote or the GitHub organisation.

1. Create the `project/frizzle` branch on the qm remote; mount the submodule at
   `governance/qm` pinned to it.
2. Move both drafts in `frizzlekickoff/records-for-qm/` onto that branch beside
   the seed's `adr/README.md` and `adr/TEMPLATE.md`; delete the staging
   directory.
3. Register frizzle in `governance-status.yaml` and `harness-status.json`.
4. Wire the licence gates and the quarterly upstream scan.
5. Route the rest of `frizzlekickoff/` to where it belongs: `HANDOFF.md` to
   `handbook/handoffs/frizzle-kickoff.md` in qm, the kickoff perspective to a
   `perspective/2026-08-13-frizzle-kickoff` branch of qm, and
   `moat/charts-mosquitto/` to a PR against moat. None of it belongs in this
   repository's history once it has a home.

**§8. Seed friction, for plan ledger N1.** What the first spawn from the seed
actually cost, recorded because the pain is a deliverable:

1. The spawn checklist names an Apache-2.0/CC-BY-SA-4.0 split as the house
   pattern and says to confirm against the outbound-licensing record. The
   record's class table says `AGPL-3.0-or-later` for services. A checklist that
   carries a guess next to an instruction to check will have the guess followed.
2. `symlink-integrity.yml` is not in `project-seed/ci/`, so the one mechanical
   guard against the most common adoption defect is not carried to projects.
   frizzle adapted qm's copy; the seed should ship it.
3. No `CONTRIBUTING.md` template exists anywhere in the corpus, though
   outbound-licensing §9 requires the DCO-plus-relicensing-grant terms in every
   QM repository. frizzle authored one from the record's text.
4. `.github/rulesets/apply.sh` iterates `[A-E]-*.json`, so the F ruleset — the
   version-tag gate, described in its own directory as the teeth of the
   version-tags record — is never applied.
5. `reuse-lint.yml` installs plain `reuse`, which aborts with
   `NoEncodingModuleError` on a machine without a system encoding-detection
   module. `reuse[charset-normalizer]` is the portable install.
6. Creating the pointer files as mode-`120000` objects on Windows works, and
   then a later `git add -A` silently stages their deletion, because
   `update-index --cacheinfo` writes the index and not the worktree. The
   handbook gives the creation command but not this ordering hazard.
7. The seed has no `.gitignore` guidance for a Python project, only qm's own.
   The negations for `.vscode/` are load-bearing and easy to lose.
8. `run_workflows_locally.py` does not run on Windows. It writes each `run:`
   block to a temp file and invokes it as `bash <path>`, and the Windows path
   reaches bash with its separators stripped —
   `/bin/bash: C:UserspeterAppDataLocalTemptmpXXXX.sh: No such file or
   directory`. Every step fails identically and none of them executes, so the
   output is indistinguishable from a repository whose workflows are all
   broken. The fork handbook makes this script the verification step for fork
   step 4, which means the documented way to check the work is unavailable to
   a Windows contributor, and its failure mode actively misleads. Each step
   was verified by running its logic directly instead.
9. `submodule-check.yml` guards nothing until the submodule is mounted. The
   spawn checklist already flags this against rad; it is equally true of any
   repository that copies the seed CI before mounting `governance/qm`, which
   is the order fork steps 4 and 1 imply. The workflow passes vacuously and
   reads as green.

## Consequences

- frizzle is governed from its first commit rather than retrofitted, which is
  what the spawn was for. The conflict table in §2 is what "governed" honestly
  amounts to on day one: eleven open rows, each with a stated shape for
  compliance.
- The deferral in §3 is cheap to close and expensive to get wrong. It costs a
  one-line edit at spawn and it avoids asserting a grant that is not yet QM's
  to assert.
- Every row in §2 and every item in §7 is a claim about a specific commit. They
  are re-derived before acting, not inherited.
- §8 is the seed's first real feedback. It is written for the ledger, and it is
  worth more than this repository is.

## Alternatives considered

1. **Spawn the repository first, then write the code.** The checklist's own
   order, and it would have avoided the retrofit shape §2 has to admit to. It
   lost to the constraint that the scaffold needed to prove the dispatcher
   design and the three recipes worked at all, and that none of that needed
   GitHub org access or a live cluster. Building first cost this record a
   conflict table; building second would have cost the design its evidence.

2. **Stamp `AGPL-3.0-or-later` now, on the record's class table alone.** It is
   very likely the right identifier and it would close four rows of §2 at once.
   It lost because the spawn checklist reserves the decision for a human, and
   because a guessed identifier stamped into every file is rewritten in every
   file when the decision lands.

3. **Put the records at `adr/` in this repository.** It would look compliant
   and need no remote access. It lost outright: the corpus README places a
   project's records on its qm branch, and an in-project `adr/` is one of the
   defects the propagation audits report. Staging them under a name that says
   they are staged is worse-looking and more honest.

4. **Defer adoption until the spawn session can do all of it.** It lost because
   the seed artifacts, the licensing pass and the conflict table are the
   expensive part of adoption and none of them needs the remote. The handbook's
   own summary is that a project can be correctly pinned and still be missing
   most of what adoption means; doing the pin last inverts that failure rather
   than repeating it.

## Revision triggers

- The `project/frizzle` branch is created and the submodule mounted — §2's
  first two rows close and this record is amended.
- The outbound licence identifier is decided — §3 closes.
- Any org record this adoption reads is ratified, or amended in a way that
  moves a §2 row.
- The rad proof-of-concept forces a revision to `contract/envelope-v0.md` or
  `contract/topics-v0.md`.
- frizzle acquires a second deployment shape, such as a container image, which
  adds an SBOM gate obligation to §7.4.
- A second repository is born from `project-seed`, making §8 comparable against
  another run rather than a single data point.

## Amendments

*None.*
