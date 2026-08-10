# ADR-XXXX — QM Constitution Adoption Scope for dossier

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-08-09 |
| **Pends on** | Two outbound-licensing inputs the org has not settled for this project's shape, both named in §9 below: (a) which class of the outbound-licensing record dossier's own code falls into, given that it is a local-first CLI and TUI that also ships a FastAPI application; (b) whether the existing MIT grant and its individual copyright holder are replaced under that record's §0. This ADR fixes every other disposition regardless, so a reader has one place to look rather than re-deriving the set once those two land. |

## Context

dossier is a documentation-standardization tool: it parses project
documentation and GitHub metadata into a SQLModel store and presents it
through a Click CLI, a Textual TUI, and a FastAPI application. It is
local-first — a `uv`-managed tool run against a SQLite file on the operator's
own machine — and ships no container image and no deployment pipeline.

It is adopting this corpus for a specific reason, and the reason shapes the
scope clause below. dossier is intended to become the surface on which this
org reads its own governance: `governance-status.yaml` and
`harness-status.json` are generated in the corpus and rendered somewhere, and
dossier is where. A tool that reports on adoption while unadopted is an
inconsistency that erodes the reporting, so adoption comes first.

**Commits this record was written against**, per the discipline record's §7:
dossier `origin/main` at `f055376`, and the corpus at this branch's parent
`b94d910` (`main`). Every factual claim below carries the command that
established it. Two facts are marked as inference where no command settles
them.

**What the pinned corpus contains.** Ten records, all `Proposed`:
`git ls-tree --name-only b94d910 records/` returns
`build-the-seam-buy-the-engines`, `contribution-and-sponsorship-policy`,
`decision-record-discipline`, `house-stack`, `human-only-contributorship`,
`ide-integrated-governance-discovery`,
`open-license-exclusion-and-upstream-remediation`, `outbound-licensing`,
`seams-on-standard-protocols`, `version-tags-are-claims`. This ADR
dispositions all ten.

dossier predates its adoption of this corpus, so the discipline record's §5
applies: this record's substance is the enumeration of every known conflict,
each naming what it violates, what compliance would look like, and how it is
pinned. Enumeration is not a waiver, no schedule is offered, and scope is
frozen per open conflict.

## Decision

1. **Decision-record discipline — adopted in full, in effect from this ADR
   forward.** This project's `adr/` directory is `project-seed/adr/` copied
   verbatim onto branch `project/dossier` of the corpus repository, with the
   seed comment deleted from the README as that comment instructs
   (`git diff --no-index project-seed/adr/TEMPLATE.md adr/TEMPLATE.md` is
   empty; the README diff is the three comment lines and nothing else). The
   lint runs from the submodule via `.github/workflows/adr-lint.yml`, copied
   verbatim from the seed.

2. **Open-license exclusion — adopted; the dependency set clears §1 and the
   §4 gate is wired in this round.** Every one of the 44 distributions in the
   locked environment declares an OSI-approved licence and none is
   source-available or proprietary (audit table under Consequences). §4's
   enforcement path for this project is the dependency-manifest gate and only
   that one: dossier presents a single runtime shape, a Python package, and
   builds no image, so the SBOM-per-image obligation does not arise. Wiring
   it is part of this adoption round rather than deferred.

3. **Seams on standard protocols — adopted, with one open conflict.** dossier
   reaches GitHub at `https://api.github.com` over HTTPS with JSON
   (`BASE_URL` in `src/dossier/parsers/github.py:230`), using `httpx`. REST
   and JSON are named seam protocols, but the *API surface* is a single
   vendor's, and the replaceability test asks whether a from-scratch
   implementation of the seam alone would need no change on dossier's side.
   It would: the client is written against GitHub's specific endpoints,
   pagination and rate-limit headers. Conflict C4 below.

4. **Build the seam, buy the engines — adopted; the boundary is named.**
   dossier's seam is the parser layer, the SQLModel schema and the
   command surface. Its bought engines are SQLite (store, reached over SQL),
   GitHub (metadata, reached over its API, subject to C4), and Textual
   (terminal rendering, subject to C2). Nothing here is written that an
   engine should own upstream.

5. **House stack — adopted, with two open conflicts.** FastAPI, SQLModel,
   Click, httpx, Alembic and pytest are the blessed set exactly, and SQLite
   is the named default for a single-node tool. Two components sit outside
   it: Textual and Trogon (C2), and the `uv` + `hatchling` packaging
   toolchain against the record's named PDM (C3). Both are §2 additions,
   which that record places at **org level** — so neither is this ADR's to
   settle, and naming them here is the whole available move.

6. **Contribution and sponsorship — adopted mechanically, inactive today.**
   No build-time source in `uv.lock` is anything other than a release
   artifact: `git show origin/main:uv.lock | grep -E 'source = \{ (git|path|directory|url)'`
   returns nothing. There is no carried patch to register.

7. **Human-only contributorship — adopted, and already the case.** No commit
   reachable from `origin/main` carries a `Co-Authored-By` trailer
   (`git log origin/main --format='%(trailers:key=Co-Authored-By)' | grep -c .`
   returns `0`), and the history has one author. The obligation going forward
   is on sessions, not on a remediation.

8. **IDE-integrated governance discovery — adopted, wired in this round, with
   one collision resolved by preserving content.** dossier carried a real
   `.github/copilot-instructions.md` with project-specific content while the
   seed ships that path as a symlink to `AGENTS.md`. The existing content is
   folded into `AGENTS.md` below its marked line rather than deleted, and the
   pointer files become symlinks. dossier's `.gitignore` excluded `.vscode/`
   wholesale, which would have swallowed the seed's editor config; the fix is
   a negation per swallowed path.

9. **Outbound licensing — adopted in mechanism, pending in class.** §12's
   machinery is wired in this round: a `LICENSES/` directory, `REUSE.toml`
   covering the paths that cannot carry a header, and `reuse lint` in
   reporting mode until this project's licensing pass is done. What is *not*
   settled, and is this ADR's `Pends on`:
   - **Which class dossier falls into.** §4 places services and control
     planes under AGPL-3.0-or-later; §5 and §6 place single-file
     visualizations and named embeddable libraries under MPL-2.0. dossier is
     a local-first CLI and TUI, which none of those classes obviously
     describes, and it also ships a FastAPI application that a reader could
     fairly call a service. The record does not settle it and this ADR
     declines to pick.
   - **Whose name is on the grant.** §0 places copyright in Quaternion
     Media. dossier's `LICENSE` reads `Copyright (c) 2026 Peter Kagstrom`
     and `pyproject.toml` names the same individual as author and
     maintainer. Conflict C1.
   - §9's inbound grant — a DCO sign-off plus the express relicensing
     permission — is absent. Conflict C5.

10. **Version tags are claims — adopted, with nothing yet to claim.**
    `git tag -l` in dossier returns nothing. `pyproject.toml` declares
    `version = "0.1.0"`, which is a package version rather than a cut tag,
    so the record binds the first tag this project cuts and conflicts with
    nothing today.

11. **Scope of what dossier asserts.** dossier **renders** governance
    documents; it does not decide governance. It reads `governance-status.yaml`
    and `harness-status.json` as generated inputs, displays them with their
    own `generated_at`, and never writes back to them. A fact those documents
    do not carry is a change to the generator in the corpus, reviewed once,
    rather than a computation in the renderer — a convenience computation
    here would be a second definition of a governance rule. Where a document
    reports `{unknown: <reason>}`, dossier renders unknown and keeps the
    reason; unknown is never rendered as blank and never as healthy. This
    clause binds the view work that follows adoption.

### The conflict table

Per the discipline record's §5. Each row names the conflict, the record it
violates, what compliance would look like, and how it is pinned. A row is not
a waiver and carries no schedule; scope is frozen per row while it is open.

| # | Conflict | Violates | What compliance looks like | Pinned by |
|---|---|---|---|---|
| C1 | `LICENSE` and `pyproject.toml` place copyright in an individual, `Copyright (c) 2026 Peter Kagstrom` | outbound §0 | Both name Quaternion Media, with §8's inbound grant routing the contributor's rights to it | `reuse lint` reports the declared holder once §12 is wired; no test asserts the entity, because the entity is a human decision this ADR does not make |
| C2 | Textual and Trogon are imported by seam code (`src/dossier/tui/app.py`) and are outside the blessed set | house-stack §1, §2 | An **org-level** record adding a TUI framework to the blessed set, weighing the alternatives the set already covers | Not testable. The house-stack gate is review, and the record placing additions at org level is what makes this unfixable inside this project |
| C3 | Packaging is `uv` + `hatchling`; the blessed set names PDM | house-stack §1 | An org-level amendment naming the packaging tool, or a migration | Not testable. `uv.lock` is committed, so the record's *lockfile* requirement is met and only the tool differs |
| C4 | The GitHub client is written against one vendor's API surface, not a multiply-implemented seam | seams §1, §2 | Either a seam a second implementation could satisfy unchanged, or a project-level exception record under §3 naming the exit plan and an expiry-style revision trigger | Not testable today. A test would have to run the client against a second implementation, which is the work the conflict describes |
| C5 | No DCO sign-off and no express relicensing grant on inbound contributions | outbound §9 | A DCO check in CI and the grant stated in `docs/contributing.md` | A CI check, once added; absent today |
| C6 | No licence gate ran on any path before this round | open-license §4 | A generated, SPDX-normalized dependency-manifest report failing on anything outside the allowlist | Closed by this round: the gate is wired. The row stays until a run has been seen to fail on a bad input |
| C7 | No REUSE compliance: no `LICENSES/`, no `REUSE.toml`, no SPDX headers | outbound §12 | `reuse lint` passing as a required check | Closed in mechanism by this round; `reuse lint` runs in reporting mode until the licensing pass finishes, which C1 blocks |
| C8 | No service inventory existed | open-license §6 | The inventory written down, with the ownability test answered per service | Closed by this round; the inventory is under Consequences. It is a reviewed document, not a scanner output, and it goes stale by design |

C6, C7 and C8 close in this round. C1 through C5 stay open, and C7's
remaining half waits on C1.

## Consequences

- **Baseline component audit**, required by the open-license record at
  adoption. Compiled by reading the `METADATA` of every distribution in the
  locked environment — `.venv/Lib/site-packages/*.dist-info`, preferring
  `License-Expression`, falling back to `License` and then to the
  `Classifier: License ::` line. 44 distributions installed, 44 `name =`
  entries in `uv.lock`, and **zero with no declaration of any kind**.

  | Direct runtime dependency | Version | Declared licence |
  |---|---|---|
  | alembic | 1.18.1 | MIT |
  | click | 8.3.1 | BSD-3-Clause |
  | fastapi | 0.128.0 | MIT |
  | httpx | 0.28.1 | BSD-3-Clause |
  | pyyaml | 6.0.3 | MIT |
  | sqlmodel | 0.0.31 | MIT |
  | textual | 7.3.0 | MIT |
  | trogon | 0.6.0 | MIT |
  | uvicorn | 0.40.0 | BSD-3-Clause |

  Across the whole locked set the declarations resolve to MIT (28 across two
  spellings), BSD-3-Clause (9 across two spellings), Apache-2.0 (3 across two
  spellings), and one each of PSF-2.0 (`typing_extensions`), MPL-2.0
  (`certifi`), BSD-2-Clause, and `MIT AND Python-2.0` (`greenlet`). Every one
  is OSI-approved; nothing source-available or proprietary is in the tree.

- **The audit reproduces the normalization problem §4 names, in this
  project.** The same licence arrives in several spellings — `MIT` and
  `MIT License`, `BSD-3-Clause` and `BSD License`, `Apache-2.0` and
  `Apache Software License`. A gate comparing raw strings against an
  allowlist would fail honest packages here, which is why §4 requires
  normalization to SPDX identifiers before comparison rather than leaving
  each project to discover it.

- **Licence compatibility of the combination**, per §7 of the open-license
  record: `certifi` is MPL-2.0 and reaches the runtime through `httpx`.
  MPL-2.0 is file-scoped and imposes nothing on a work that merely depends on
  it, so it does not constrain what dossier's own artifact may be licensed
  under. That disposition holds under any of the classes the `Pends on`
  weighs, so §7 does not add a third open question.

- **Service inventory**, required by §6 and producible by no scanner:

  | Service | Reached over | Ownability test | Residual exposure |
  |---|---|---|---|
  | GitHub REST API (`api.github.com`) | HTTPS + JSON, via `httpx` | Withdrawal or re-pricing is an **engineering project**, not a configuration change — the client is written against GitHub's endpoints, pagination and rate-limit headers | Stated plainly rather than treated as solved: this is C4, and a seam would make the provider replaceable without making the data ownable offline |

  No other third-party service is in a runtime path. The store is a local
  SQLite file; there is no hosted database, object store, identity provider,
  or CDN-loaded asset.

- **Obligations from the seed's table that this round does not satisfy**, so
  the absence is recorded rather than inferred: the quarterly upstream scan
  (open-license §4) is not scheduled, and no control-plane instance record
  exists yet. The risk register is this record's conflict table for now,
  which is what that obligation asks for at minimum.

- **A hazard for anyone running dossier's suite.** `tests/conftest.py:36`
  defines `pytest_configure`, which shells `dossier dev purge` against the
  operator's main database before the run. A session that runs the suite on a
  machine with real data in `./dossier.db` destroys it. This is not a
  conflict with any org record; it is recorded here because the gates this
  adoption wires will invite exactly that command.

- Cost accepted: five conflicts stay open with no dates against them, which
  the discipline record's §5 permits deliberately and its own Consequences
  name as the price. Three of the five (C2, C3, C4) cannot be closed inside
  this project at all — two need an org-level record and one needs an
  architecture change — so a schedule here would be a schedule for someone
  else's decision.

## Alternatives considered

1. **Adopt with a bare submodule and seed copy, and write the record later.**
   Rejected: it is the shape the fork procedure names as the common failure —
   three of nine adopting projects were missing at least one step and nothing
   reported it. The pin is the cheap part; the enumeration is the adoption.

2. **Settle the outbound licence class here, reading dossier's FastAPI
   application as a service under §4.** Rejected. The application is served
   locally rather than hosted, so AGPL §13's network trigger fires on
   nothing today, and picking AGPL on that reading would relicense the
   project by drafting. The drafting rules place an undecided input in
   `Pends on` rather than in a silent choice.

3. **Fix the copyright holder in passing while wiring `REUSE.toml`.**
   Rejected: whose name is on a grant is a legal and authorship decision, and
   the outbound record's §0 was answered for the corpus rather than for every
   repository. Changing it as a side effect of a mechanical licensing pass
   would make a decision nobody reviewed.

4. **Declare C2 and C3 compliant by reading Textual as an engine reached
   across a seam.** Rejected on the house-stack record's own words: §4 makes
   that boundary mechanical rather than a matter of framing, and a component
   imported into seam code is house stack. `src/dossier/tui/app.py` imports
   Textual directly. Relabelling it is exactly the move that clause exists to
   refuse.

5. **Make `reuse lint` blocking immediately.** Rejected for this round: it
   would fail on C1, a decision this ADR does not make, and a required check
   that cannot pass without a human ruling blocks every unrelated change.
   Reporting mode keeps the finding visible without holding the repository
   hostage to it.

6. **Wire the harness commands and the slot check as part of this adoption.**
   Rejected as unavailable rather than unwanted. Neither exists in the pinned
   corpus — `git ls-tree b94d910 project-seed/ide/.claude` is empty and there
   is no `ci/` directory at that commit. They reach dossier when the corpus
   change carrying them lands on `main` and this project's pin is bumped,
   which is the propagation path the runbook already describes.

## Revision triggers

- Either `Pends on` input is answered — the licence class, or the copyright
  holder. Both land here as dated amendments.
- Any org record in the pinned corpus is ratified, numbered `QM-NNNN` — every
  disposition above is re-checked against the ratified text.
- The `governance/qm` pin is bumped, which is also when the harness commands
  and the two status documents first reach this project.
- An org-level record adds a TUI framework or names a packaging tool — closes
  C2 or C3.
- dossier gains a container image or a hosted deployment — §4's SBOM path
  becomes live alongside the manifest gate, and the licence-class question in
  `Pends on` changes shape.
- dossier's GitHub client is run against a second implementation of that API
  surface — the evidence that C4 has a real seam rather than an assumed one.
- `reuse lint` reports a class violation that turns out to be the class table
  being wrong rather than the file.
- The conflict table goes a full pin-bump cycle without being read — the
  no-schedule stance is being used to park conflicts, which the discipline
  record names as its own revision trigger.

## Amendments

*None.*
