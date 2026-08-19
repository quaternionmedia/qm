# Handbook — Glossary

**Routing.** Words this corpus uses in a narrower sense than ordinary English,
and words it uses in **more than one** sense. Read the second table first: those
are the ones that have actually cost time here.

**This page is written, not generated.** A definition is a decision about
language and nothing can derive it from the tree. It is an entry point, so
`ci/check_restatements.py` covers it like the others.

---

## Words with more than one meaning in this corpus

Each of these has bitten. The disambiguator is the column on the right.

| Word | Sense | Told apart by |
|---|---|---|
| **draft** | a record before ratification (`DRAFT-*.md`) | it is a filename prefix |
| | a pull request that is **unfinished** | GitHub's draft flag. Never a holding pen for finished work |
| | anything untagged — `main`, a branch, a local build | `records/DRAFT-version-tags-are-claims.md` §4. Asserts nothing |
| **review** | the gates running on a pull request | mechanical, and the PR is an audit record |
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
| **seed** | `project-seed/` — what a fork adopts | some files are **copied**, some are **run in place** |
| | not a synonym for "template": a copied file forks, a run-in-place file does not | `handbook/propagation-runbook.md` |

## Words with a narrow meaning here

| Word | Means |
|---|---|
| **corpus** | this repository. The org-level constitution every project adopts by reference |
| **project** | a repository that vendors the corpus at `governance/qm` and pins a `project/<name>` branch |
| **claim** | something a human asserted. Never derived from artifacts. `ci/workspace.yaml` is claims |
| **evidence** | something a generator measured, with a timestamp. `governance-status.yaml` is evidence |
| **unknown** | a fact that could not be established, spelled `{"unknown": "<reason>"}`. **Not** zero, not empty, not compliant |
| **advisory** | a gate that reports and cannot block a merge. Every gate here is advisory today |
| **mechanical** | a rule a script can fail you on. Its opposite is **customary** — written down and unenforced |
| **declared gap** | a rule named and deliberately not yet enforced, counted in `ci/pattern-registry.yaml` with `check_exists: false` |
| **debt** | something the corpus has decided not to fix and does count. The nine unsigned commits are debt |
| **slot** | one open pull request, per repository, per contributor. A sequencing constraint, not a bandwidth one |
| **propagate** | carry an org change from `main` into a `project/<name>` branch. One direction only |
| **restatement** | an entry point summarizing a decision a record owns. Costs a declared `Restated in` row |
| **citation** | naming a record's path without summarizing it. Free, and encouraged |
| **transient** | a document written to be deleted when its work lands. Everything in `handbook/handoffs/` |
| **standing** | a document with no lifecycle defined for its class. The absence of a state, not a state |
| **preflight** | running every workflow's real steps locally. `uv run --extra preflight qm preflight` |
| **ledger** | the running record of what each action was predicted to do and what it cost |
| **grandfathered** | exempt from a gate by a declared date because the remedy would be a forbidden act |

## Words this corpus deliberately avoids

| Avoided | Because | Say instead |
|---|---|---|
| "done" | the corpus has no definition a tool could read, so a completion figure is the most confidently wrong thing a dashboard can print | the observable state: `pushed`, `draft`, `ready` |
| "approved" | nothing here is approved; records are ratified and releases are tagged | `ratified`, or `tagged` |
| "verified" for a local run | the runner reproduces neither `uses:` steps, the image, nor secrets | "a local pass is evidence, not proof" |
| "all X are Y" in a record | a record states a requirement; a generator reports compliance, with a timestamp | "X **must be** Y", and name the document that measures it |
| "just" / "simply" | it hides the cost of the thing being described | say the cost |

## Two that read as synonyms and are not

**`main` is readiness. A `v` tag is governance.** Merging asserts the work is
ready to build on and nothing more. A tag asserts a human reviewed it, a human
manually tested it against its real runtime, and deterministic automated
validation passed.

**A check being green is not a rule being enforced.** Green means the check
ran and did not object. Whether it *could* have blocked the merge is the
enforcement layer, and `handbook/gates.md` reports that separately because
today the answer is no.
