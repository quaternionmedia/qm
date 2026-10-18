# ADR-XXXX — Adopt the QM constitution, naming each obligation it creates and its state

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-10-13 |
| **Pends on** | graphbase's visibility: graphbase is a private repository named throughout this public project and its public records, which the policy `no-private-name-in-a-public-artifact` forbids, and the corpus's roster does not list it. Making it public, or recording an exception, is the owner's decision. Also the disposition of `mongo:7` in the Compose stack, which §1 of the open-license record excludes (row 1) — the owner's decision as well |
| **Principle** | `ownership-is-the-deliverable`; `seams-on-standard-protocols`; `build-the-seam-buy-the-engines`; `show-it-by-running-it` |

## Context

codecartographer adopts the QM constitution by reference. Its `governance/qm`
submodule tracks this project's branch, `project/codecartographer`, and the
project's records live in that branch's `adr/`. The org records create
obligations that nothing generates automatically; `adr/README.md` lists them
under "What the org records oblige this project to produce", and says a
project is compliant when they exist, not because it copied the directory.
None of them is ticked anywhere.

The runtime shapes the obligations apply to:

- a FastAPI backend in Python, locked by `pyproject.toml` and `uv.lock`;
- a TypeScript frontend built with Vite, locked by `web/package.json` and
  `web/package-lock.json`;
- a Docker Compose stack: the `codecarto` image (`codecarto/Dockerfile`, on
  `tiangolo/uvicorn-gunicorn:python3.11`, installing `codecarto/requirements.txt`)
  and `mongo:7`.

At runtime the backend reaches GitHub — its REST API, raw file content and
repository archives — and MongoDB when `MONGODB_URI` names one. It vendors two
QM repositories as submodules, `governance/qm` and graphbase.

`adr/README.md` also says what to do about an obligation a project cannot
meet yet: say so in the adoption record, with what compliance would look
like. Naming a gap is not waiving it.

## Decision

codecartographer adopts the QM constitution by reference, and this record is
its adoption record. Each obligation the org records create is named below
with its state at codecartographer 00ce9de and what closes it. A row is met
only when its closing artifact exists on codecartographer's `main`; until
then the project carries the governance machinery with that gap open, and
this table is where the gap is said.

| # | Obligation | Record | State at 00ce9de | What closes it |
|---|---|---|---|---|
| 1 | **Baseline component audit** | open-license | **Open.** No audit exists. One finding is known without it: `docker-compose.yml` runs `mongo:7`, MongoDB Community Server, whose licence is the Server Side Public License (`LICENSE-Community.txt` in `mongodb/mongo`). §1 excludes SSPL, with no waivers and no opt-ins, so this component's disposition is owed and is in `Pends on` | A table in this record of every component in a deployed runtime path — the Python runtime closure, the npm `dependencies`, the image's base, `mongo:7`, graphbase — with its licence and disposition, taken from the gates' generated reports rather than typed |
| 2 | **Licence gates, cumulatively** | open-license §4 | **Open.** `reuse-lint.yml` checks the licensing of this repository's own files, which is a different question. Nothing reports the licences of dependencies | An SBOM gate for the `codecarto` image, and a dependency-manifest gate for each of Python (`uv.lock`) and npm (`web/package-lock.json`): each generated, normalized to SPDX, compared with a generated allowlist, failing on an unknown declaration, and with the dependency groups the runtime closure is taken from named here (§5) |
| 3 | **Service inventory** | open-license §6 | **Open.** Not written. The services: GitHub (REST API, raw content, archives), reached as GitHub serves them; MongoDB, as a hosted service whenever `MONGODB_URI` names one rather than the Compose container | A list in this record of each service, the seam it is reached over, its answer to the ownability test, and the residual exposure stated |
| 4 | **Quarterly upstream scan** | open-license §4 | **Open.** No scheduled job watches pinned upstreams. Dependabot opens version bumps, which watches something else | A scheduled workflow watching the pinned upstreams for licence-file changes and archive status |
| 5 | **Seam protocol named** | seams | **Partly met.** *The window reads what cargo wrote* names cargo's documented JSON forms as its seam. The records that select GitHub and MongoDB name no protocol and answer no replaceability test | Each record selecting a third-party component names the protocol it is reached over and answers the replaceability test; where only one implementation exists, seams §3's exception record |
| 6 | **Control-plane instance record** | build-the-seam | **Open.** No record names what codecartographer's seam owns | One record naming what the seam owns and refuses to own, with size-smell thresholds as revision triggers — or saying the project has no control plane, and why |
| 7 | **Risk register** | open-license, seams | **Open.** Governance and abandonment risk is recorded nowhere | A section — here or in a design document — recording that risk for each selected component |
| 8 | **Carried patches registered** | contribution | **Met.** No build-time source in `uv.lock` or `web/package-lock.json` is anything but a release artifact, so `registers/carried-patches.md` needs no row. graphbase is pinned to a commit on an unmerged branch, but it is a QM repository rather than a patch against an upstream (*Formalize the graphbase submodule interface; keep it a submodule*) | Re-checked at every governance pin bump |
| 9 | **One executable walkthrough** | one-executable-walkthrough | **Open.** There is no `walkthrough/` | `walkthrough/NN-<slug>.md` pages executed by the ordinary Python test command with `walkthrough/` named on the command line, and a run observed passing on `main` |

## Consequences

- The table is re-checked whenever the governance pin is bumped, because
  `adr/README.md` asks for that and because a propagation can add an
  obligation. A row moves to met in the same change that lands its closing
  artifact.
- Until rows 1 and 2 close, a dependency with an excluded licence can enter a
  runtime path unseen. `mongo:7` shows such a component is already in one.
- Row 5's GitHub answer may make a seams §3 exception record owed: GitHub's
  REST API is reached as GitHub serves it, and the replaceability test asks
  whether a from-scratch implementation of the seam alone would do.
- While graphbase stays private inside a public project, CI cannot read it.
  The governance workflows check out `governance/qm` alone because a runner
  cannot fetch graphbase, and the submodule check reports graphbase's pin as
  unchecked. Every public record that names it, this one included, collides
  with the policy in `Pends on`.

## Alternatives considered

1. **Close every obligation before adopting.** Rejected: the adoption already
   happened — the submodule and the project branch exist — and `adr/README.md`
   calls a project carrying the machinery with an open gap instantiated rather
   than improvised. Holding this record until every row closes would hide the
   gaps it exists to show.
2. **Tick the obligations table in `adr/README.md` instead of writing a
   record.** Rejected: the table is the seed's list of what is owed. A tick
   carries no state and no closing artifact, and the seed names the adoption
   record as where a project says what it cannot satisfy yet.
3. **Type the baseline audit into this record now.** Not taken: §4 requires
   the reports to be generated, never hand-compiled, and a typed table written
   before the gates exist would be a second account of the dependencies for
   the gates to contradict.

## Revision triggers

- A row's closing artifact lands on codecartographer's `main` — that row is
  restated as met.
- A governance pin bump brings an org record that adds or changes an
  obligation.
- graphbase's visibility is decided, or `mongo:7`'s disposition is — a
  `Pends on` input is then answered.
- A licence gate, once wired, fails on a component already in a runtime path —
  row 1's audit is then incomplete.

## Amendments

*None.*
