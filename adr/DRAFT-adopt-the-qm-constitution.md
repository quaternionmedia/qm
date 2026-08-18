# ADR-XXXX — Adopt the QM constitution, with its open conflicts named

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-08-18 |
| **Pends on** | Ratification, and the outbound licence class for this project — see §6 and the conflict table. A human decides both. |

## Context

Carlos is a browser workspace for sketching rigs of real gear: a FastAPI
service rendering a rack of devices declared as JSON, with a versioned
interchange format, a radial menu implementing `quaternionmedia/rad`'s
interaction contract, and a seam other applications can call over REST.

It carries the QM governance machinery — the corpus is vendored at
`governance/qm` on this project's own branch, the seed workflows run in CI,
`AGENTS.md` is the discovery file — and the fork procedure requires an adoption
record before the project may be described as governed. This is that record.

Two things about the shape of the adoption are worth a reader's attention
before the decision.

**The pin is the branch, not a hash.** `governance/qm` is a submodule on
`project/carlos`, created from the corpus's `main`. `git log --first-parent` on
that branch is the statement of which org state was adopted and when; bumping
the pin is merging `main` into it. Nothing here hand-maintains a commit id,
because a document that records its own pin is wrong the moment the pin moves.

**Adoption is not compliance, and the corpus says so.** The obligations table
in `adr/README.md` distinguishes projects that carry governance from those that
do not — never compliant projects from non-compliant ones. Several obligations
below are unmet. Naming a gap is not waiving it; a project that cannot satisfy
one says so here, with what compliance would look like.

## Decision

**Carlos adopts the Quaternion Media constitution by reference**, at the state
its `governance/qm` branch records, on the terms below.

**§1 — Org records bind; project records may tighten, never relax.** Where this
project's practice contradicts an org record, the contradiction is recorded in
the table under *Conflicts* rather than resolved by local preference. A genuine
exception is an amendment ratified at org level, and this record proposes none.

**§2 — The baseline component audit.** Every component in a deployed runtime
path, with its licence:

| Component | Version | Licence | Disposition |
|---|---|---|---|
| FastAPI | 0.116.1 | MIT | Keep. The service framework |
| Jinja2 | 3.1.6 | BSD-3-Clause | Keep. Server-side templating |
| pydantic | 2.11.7 | MIT | Keep. Validates the catalogue, the patch format and the seam |
| TinyDB | 4.8.2 | MIT | **Conflict.** Keep for now; see the table |
| uvicorn | 0.35.0 | BSD-3-Clause | Keep. The ASGI server |
| Click | 8.2.1 | BSD-3-Clause | Keep. The house stack's CLI tool, used by `tools/cli.py` |

Development-only, not in a deployed runtime path: pytest (MIT), Playwright and
`pytest-playwright` (Apache-2.0). The frontend ships no third-party runtime
dependency at all: no CDN reference, no bundled library, and a test asserts the
first of those.

Every component in the runtime path is permissively licensed. **No copyleft
component is in a deployed path**, which is what makes §6's open question a
question about this project's own outbound licence rather than about anything
it depends on.

**§3 — The seam protocol.** The interop seam is REST + JSON with an OpenAPI
description, and `GET /api/cadence` declares per endpoint what calling it costs
a peer and how long the answer stays quotable. Replaceability: a peer is named
by an environment variable holding its base URL, never by a committed address,
and every outbound endpoint declares its side effect. Outbound calls are
*planned* and never sent by this build; a guard refuses any HTTP client in
`src/`, which is how that stays true rather than being remembered.

**§4 — Instance identity.** `/healthz` reports the instance, the process
serving, the port actually bound and the resolved database path, so a collector
can attribute a measurement. The monitoring-seam record's discovery mechanism —
bind port 0 and write a run-file — is **declined**: it governs services a
monitor watches in the internal control plane, and Carlos is a browser
application whose predictable address is the point of it. A collector must be
told where to look.

**§5 — One executable walkthrough.** `walkthrough/` is five pages run by the
ordinary test command, four hermetic and one runtime-bound. Screenshots are
byproducts of the run that asserts the behaviour they show, recorded and never
compared. The record's decision 7 — evidence of a run on the default branch —
is unmet, and cannot be met by a file: nothing here is pushed.

**§6 — The outbound licence class is not decided here.** The declared licence
is MIT; the outbound-licensing record puts services at AGPL-3.0-or-later. This
record names the conflict and routes the decision to its own record rather than
picking silently, because it is a decision about what this project *is* rather
than about how it is governed.

### Conflicts

Each row is a contradiction with an org record, with what established it. None
is waived.

| Conflict | Record | What established it, and what is left |
|---|---|---|
| Packaging is `uv`; the blessed tool is PDM | house-stack §1 | **Do not write a project exception.** Three QM projects stand on `uv` — carlos, loopwall, sqlmodel-ui — which fires that record's own revision trigger. This is an org-level amendment, not a local waiver |
| Store is TinyDB | house-stack §1, seams | The blessed default is PostgreSQL, or SQLite for single-node tools, reached over SQL. TinyDB has no protocol seam and fails the replaceability test. Named patch persistence is blocked on this and is deliberately not built |
| Declared licence is MIT | outbound-licensing §4 | Services are AGPL-3.0-or-later. The declared licence is a reviewed output, not an inherited default. See §6 |
| No SPDX headers, no `LICENSES/` | outbound-licensing §12 | What `reuse-lint` fails on. Three files carry copyright information and the rest do not; `python -m reuse lint` counts what is left. Blocked on the class question above, because the headers state the answer |
| Frontend is plain modular JavaScript with no build step | house-stack §1 | The set names mithril with a parcel build. Carlos ships no build step at all, which is neither the blessed answer nor a recorded exception |
| `static/anime-shim.js` is a local stand-in | house-stack §1 | The set names vendored `anime.js`; this is a 25-line reimplementation covering the three properties this app animates. Neither vendored nor the named library |
| No dependency-manifest licence gate | open-license §4 | Required per package ecosystem shipped. This project ships one, Python, and has none |
| No service inventory | open-license §6 | No scanner produces it, which is why it is written down. This project reaches no third-party service in a runtime path, and that sentence is the inventory until one appears |
| No quarterly upstream scan | open-license §4 | No scheduled job watches the pinned upstreams for licence changes or archive status |
| No control-plane record | build-the-seam §4 | Names what the seam owns and refuses to own, with size-smell thresholds. §3 above states the seam; the thresholds are not written |
| Discovery is declined | monitoring-seam §4 | See §4. The requirement it serves is met another way; the mechanism is not adopted |
| Decision 7 unmet | one-executable-walkthrough §7 | A page that ran where nobody merges has not run. `.github/workflows/tests.yml` exists to produce the evidence and cannot until something is pushed |

Two obligations are **met**: the seam protocol is named with its replaceability
answer (§3), and no build-time patch is carried, so the org carried-patch
register has nothing to receive from this project.

The **risk register** is this table. Governance and abandonment risk for the
selected components is low and stated: every one is a widely used, permissively
licensed package with an active upstream, and the two that carry real risk are
TinyDB — recorded above as failing the replaceability test — and the frontend's
absence of a build step, which is a maintenance risk rather than a licensing
one.

## Consequences

- Carlos may be described as **carrying** QM governance, and may not be
  described as a fully governed QM project while rows above are open. The local
  statement of that is `GOVERNANCE.md`, which stays the working surface;
  this record is the decision behind it.
- The seed gates run on every pull request and three fail today. Two of the
  three — `submodule-check` and `signature-check` — resolve on the first push.
  `reuse-lint` does not, and is gated on §6.
- Adopting `uv` and `unittest`-shaped tests under pytest costs nothing to
  reverse and is recorded rather than hidden, which is the point of the table.
- **Cost accepted:** named patch persistence stays unbuilt while the datastore
  conflict is open. The feature is wanted and the store is the wrong one, so
  building it now would be building it twice.
- **Cost accepted:** the licensing pass is a file-by-file change that grows with
  the project, and deferring it makes it larger. It is deferred anyway, because
  a header states an answer this record does not have.

## Alternatives considered

1. **Adopt with project exceptions written for each conflict.** Rejected: an
   exception is a local waiver of an org record, and at least one of these —
   packaging on `uv` — is a case where three projects stand on the same answer
   and the org record's own revision trigger has fired. Writing a local
   exception would convert an org-level amendment into a project's private
   habit, and would do it quietly.

2. **Settle every conflict before adopting.** Rejected: it inverts the
   dependency. The obligations table is a checklist a project works through
   *after* it carries the machinery, and the corpus is explicit that carrying
   governance with named gaps is the instantiated state rather than the
   improvised one. Waiting would also mean the gates do not run while the gaps
   are open, which is exactly backwards.

3. **Do not adopt; keep the machinery and skip the record.** Rejected: the fork
   procedure requires the record, and without it the conflict table lives only
   in `GOVERNANCE.md` — a working document with no ratification step. A
   contradiction with an org record that nobody ratified a position on is a
   contradiction nobody owns.

4. **Adopt and decide the licence class here.** Rejected under authoring rule 1
   and rule 5: it is a second decision, and it is genuinely undecided. Deciding
   it inside an adoption record would settle by stealth the one question a
   reader of this project most needs to see argued.

## Revision triggers

- The outbound licence class is decided, in either direction. This record's §6
  and two table rows are then restated by the record that decides it.
- Named patch persistence is wanted enough to build, which forces the datastore
  conflict rather than deferring it.
- A fourth QM project adopts `uv`, or the org amends the house stack. Either
  resolves the packaging row without a local exception.
- Anything in the runtime path stops being permissively licensed, or its
  upstream is archived. The audit in §2 is then re-run rather than trusted.
- The family's harness needs to enumerate Carlos instances, which forces the
  discovery mechanism declined in §4.
- A second runtime shape appears — a container image, a published package —
  which makes the licence gate obligation two obligations rather than one.

## Amendments

*None.*
