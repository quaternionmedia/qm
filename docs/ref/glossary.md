# Glossary

The words this corpus uses in a narrower sense than ordinary English, the ones it uses in more than one sense, and the ones it avoids. Read the first table first: those are the ones that cost time. Where a definition here and a record disagree, the record is what the organisation decided and this page is repaired.

This page is written, not generated: a definition is a decision about language, and nothing can derive it from the tree.

## Words with more than one meaning

The column on the right tells the senses apart.

| Word | Sense | Told apart by |
|---|---|---|
| **draft** | a record before ratification (`DRAFT-*.md`) | it is a filename prefix |
| | a pull request that is **unfinished, or stacked** on another open one | GitHub's draft flag. Never a holding pen for finished work against the real target |
| | anything untagged — `main`, a branch, a local build | `records/DRAFT-version-tags-are-claims.md` §4. Asserts nothing |
| **review** | the gates running on a pull request | mechanical, and the pull request is an audit record |
| | a human reading a change set before a `v*` tag | the **only** human review of shipped work |
| | reading all records in one sitting for contradiction | `handbook/handoffs/semantic-review-of-the-records.md` |
| **gate** | a CI check that can fail a pull request | listed in `handbook/gates.md` |
| | a **human** gate — ratification, or the version tag | there are exactly two, and no CI check is one |
| **phase** | where a project sits on the release ladder (`v0.0.1`) | `ci/workspace.yaml`, `records/DRAFT-project-phase-ladder.md` |
| | a delta's lifecycle step (`brainstorm` … `complete`) | dossier's `DeltaNote.phase` |
| **delta** | a unit of intended work in dossier | `ProjectDelta` |
| | the difference between two disk measurements | the disk tooling's own vocabulary. Collides by name only |
| **status** | a record's `Proposed` / `Accepted` | its header table |
| | a perspective's `Unreviewed` … `Declined` | the index in `perspectives/README.md`, which is the authority |
| | a generated document's freshness | `generated_at` plus a staleness budget |
| **seed** | `project-seed/` — what a project adopts | some files are **copied**, some are **run in place** |
| | not a synonym for "template": a copied file forks, a run-in-place file does not | `handbook/propagation-runbook.md` |
| **loose end** | something the org started and has not finished, joined from the documents that each hold part of it | `loose-ends.json`. Not called a "review item": *review* already carries three senses |

## Definitions

**Adoption by reference** { #adoption-by-reference }
: The QM adoption model. A project's records live on a `project/<name>` branch of the corpus repository, and the project mounts the corpus as a git submodule checked out on that branch. Updates arrive by merge, never by copy. See [Architecture](../about/architecture.md).

**ADR** { #adr }
: A project-level decision record, numbered `ADR-NNNN` per project starting at 0001. See [Record precedence](precedence.md).

**Black box** { #black-box }
: A component whose behaviour cannot be decided in advance — for QM's purposes, a language model. `shrink-the-black-box` says it is never the check: it drafts the check and a person authors it. See [PRINCIPLES.md `shrink-the-black-box`](https://github.com/quaternionmedia/qm/blob/main/PRINCIPLES.md).

**Corpus** { #corpus }
: This repository and the shared rule set it holds: the constitution every QM project adopts.

**Crossing** { #crossing }
: Two deltas that interact at one point where neither contains the other, stated as `crosses`. Distinct from `part-of`, which composes, and `blocks`, which orders. See [records/DRAFT-deltas-compose.md](https://github.com/quaternionmedia/qm/blob/main/records/DRAFT-deltas-compose.md).

**Gate** { #gate }
: An automated check that can refuse a change. Gates are mechanical and always on; nobody invokes one. They are not the two *human* gates — ratification and the version tag — and no gate is a substitute for either. See [the gate index](https://github.com/quaternionmedia/qm/blob/main/handbook/gates.md).

**Handbook** { #handbook }
: QM's policy and procedure pages, in `handbook/`. Binding on QM's own conduct; a record always wins over a handbook page. See [Handbook index](handbook.md).

**Harness** { #harness }
: The tooling that coordinates work across concurrent agent sessions: the scripts in `project-seed/ci/` that establish what a session must know, the checks they run, and `status/harness.yaml`. The governance layer names no product — optional per-tool wrappers live in `adapters/`. See [handbook/generated-documents.md](https://github.com/quaternionmedia/qm/blob/main/handbook/generated-documents.md).

**Knot** { #knot }
: A cycle in the obligation graph where every edge imposes an order, so the ring has no first step. Untying one means a person chooses, or a stated relation gets cut. Distinct from a loop. See [records/DRAFT-a-knot-is-a-cycle-of-obligation.md](https://github.com/quaternionmedia/qm/blob/main/records/DRAFT-a-knot-is-a-cycle-of-obligation.md).

**Loop** { #loop }
: A cycle whose edges impose no order. Identical to a knot in a picture, and it constrains nothing — reporting it as a problem buries the real ones. Still a fact, and not a scheduling problem. See [records/DRAFT-a-knot-is-a-cycle-of-obligation.md](https://github.com/quaternionmedia/qm/blob/main/records/DRAFT-a-knot-is-a-cycle-of-obligation.md), which carries the measurement.

**Perspective** { #perspective }
: Dated, attributed, non-binding opinion in `perspectives/`: incidents, retrospectives, argued positions. See [Add a perspective](../usage/add-a-perspective.md).

**Phase ladder** { #phase-ladder }
: How a project reports its governance maturity, as a version number. `v0.0.0` (not adopted) and `v0.0.1` (adopted, however far along) are defined org-wide; higher rungs are defined by each project in its own records. See [records/DRAFT-project-phase-ladder.md](https://github.com/quaternionmedia/qm/blob/main/records/DRAFT-project-phase-ladder.md).

**Propagation** { #propagation }
: Merging `main` into a `project/<name>` branch to carry org changes to a project, through a `propagate/<name>-<date>` pull request. See [Propagate a change](../usage/propagate-a-change.md).

**Proposed** { #proposed }
: The status of a record that is drafted and waits for a human to ratify it. The decision is written down and is not yet final. Making one final is [ratification](#ratification), which needs a second person to agree. See [Ratification](ratification.md).

**Protocol** { #protocol }
: A wire format or interface with multiple independent implementations, which is what makes a component swappable. `seams-on-standard-protocols`'s replaceability test is stated against protocols rather than licences, because a proprietary protocol outlasts an open licence. See [records/DRAFT-seams-on-standard-protocols.md](https://github.com/quaternionmedia/qm/blob/main/records/DRAFT-seams-on-standard-protocols.md).

**QM record** { #qm-record }
: An org-level decision record, numbered `QM-NNNN` at ratification. Binds every project. See [Record precedence](precedence.md).

**Ratification** { #ratification }
: The human act that makes a record binding: Status flips to `Accepted`, the number is assigned, the index is updated. See [Ratification](ratification.md).

**Record** { #record }
: A decision document: one decision, with context, alternatives, consequences, and revision triggers. The only kind of document that binds. See [Draft a record](../usage/draft-a-record.md).

**Register** { #register }
: A living data file created by a record, such as [registers/carried-patches.md](https://github.com/quaternionmedia/qm/blob/main/registers/carried-patches.md). Binding as the creating record says.

**Seam** { #seam }
: The boundary where a third-party component connects to a QM system. Seams sit on standard protocols so any component behind them can be replaced. From the records [Seams on standard protocols](https://github.com/quaternionmedia/qm/blob/main/records/DRAFT-seams-on-standard-protocols.md) and [Build the seam, buy the engines](https://github.com/quaternionmedia/qm/blob/main/records/DRAFT-build-the-seam-buy-the-engines.md).

**Seed** { #seed }
: `project-seed/` — what a new project adopts. `ide/` (agent instructions and editor config) and the workflows in `ci/` are copied into the project; the checks those workflows run stay in `governance/qm/project-seed/ci/` and run in place; `adr/` (record template and index) becomes the records directory on the project's `project/<name>` branch. See [Propagate a change](../usage/propagate-a-change.md).

**Strand** { #strand }
: One line of work, possibly denoted by more than one address. `same-as` is what says two addresses are one strand; advancing one and not the other leaves the same work in two phases.

**Sweep** { #sweep }
: One change carried across every repository that needs it — one delta with many parts, rather than many pieces of work that resemble each other. The parts are `part-of` it, so the whole has a single state.

**Tangle** { #tangle }
: A cycle the relations form, reported and never broken. Refusing to store one makes the tool consistent and the record false, and the deletion gets made by whoever was least equipped to judge it.

**Workspace** { #workspace }
: A permanent branch (`workspace/<slug>`) for research that never merges back to `main`. Non-binding. See [Branch namespaces](namespaces.md).

## Words with a narrow meaning here

| Word | Means |
|---|---|
| **project** | a repository that vendors the corpus at `governance/qm` and pins a `project/<name>` branch |
| **claim** | something a human asserted. Never derived from artifacts. `ci/workspace.yaml` is claims |
| **evidence** | something a generator measured, with a timestamp. `status/governance.yaml` is evidence |
| **unknown** | a fact that could not be established, spelled `{"unknown": "<reason>"}`. **Not** zero, not empty, not compliant |
| **advisory** | a gate that reports and cannot block a merge. `handbook/gates.md` says which gates are |
| **mechanical** | a rule a script can fail you on. Its opposite is **customary** — written down and unenforced |
| **declared gap** | a rule named and deliberately not yet enforced, counted in `ci/pattern-registry.yaml` with `check_exists: false` |
| **debt** | something the corpus has decided not to fix and does count. Unsigned commits already in history are debt |
| **stack** | pull requests in series, each based on the branch of the one beneath it. Only the bottom is ready; the rest are drafts until it merges |
| **restatement** | an entry point summarizing a decision a record owns. Costs a declared `Restated in` row |
| **citation** | naming a record's path without summarizing it. Free, and encouraged |
| **transient** | a document written to be deleted when its work lands. Everything in `handbook/handoffs/` |
| **standing** | a document with no lifecycle defined for its class. The absence of a state, not a state |
| **preflight** | running every workflow's real steps locally. `uv run --extra preflight qm preflight` |
| **ledger** | the running record of what each action was predicted to do and what it cost |
| **grandfathered** | exempt from a gate by a declared date because the remedy would be a forbidden act |
| **carried** | a loose end somebody has picked up and is following. Still a loose end: it leaves the document when its subject changes, not when somebody says so |
| **dismissed** | a loose end somebody read and deliberately let go, with the reason. The other half of `carried`, and the only two dispositions there are |
| **open** | a loose end nobody has judged — **the absence of a claim, and it has no spelling**. Writing it down would turn "nobody has looked" into "somebody decided nothing", which are different facts about the same row |

## Words this corpus avoids

| Avoided | Because | Say instead |
|---|---|---|
| "done" | the corpus has no definition a tool could read, so a completion figure is the most confidently wrong thing a dashboard can print | the observable state: `pushed`, `draft`, `ready` |
| "approved" | nothing here is approved; records are ratified and releases are tagged | `ratified`, or `tagged` |
| "verified" for a local run | the runner reproduces neither `uses:` steps, the image, nor secrets | "a local pass is evidence, not proof" |
| "all X are Y" in a record | a record states a requirement; a generator reports compliance, with a timestamp | "X **must be** Y", and name the document that measures it |
| "just" / "simply" | it hides the cost of the thing being described | say the cost |

## Two that read as synonyms and are not

**`main` is readiness. A `v` tag is governance.** Merging asserts the work is ready to build on and nothing more. A tag asserts a human reviewed it, a human manually tested it against its real runtime, and deterministic automated validation passed.

**A check being green is not a rule being enforced.** Green means the check ran and did not object. Whether it *could* have blocked the merge is the enforcement layer, and `handbook/gates.md` reports that separately.

## Related

- [Branch namespaces](namespaces.md)
- [Record precedence](precedence.md)
- [PRINCIPLES.md](https://github.com/quaternionmedia/qm/blob/main/PRINCIPLES.md)
