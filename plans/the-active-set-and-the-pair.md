# Plan — the active set, and the pair

**What this is.** One cohesive picture across three questions that turned out to
be one question: which repositories are being worked on, what every local
handoff still holds, and what `dossier` and `qmcp` need before they can carry
units of work across projects.

They are one question because the answer to all three is the same mechanism.
`records/DRAFT-a-disagreement-is-a-delta.md` says a disagreement between two
views of one address is a unit of work. *Which repositories are active* is a
claim; *which repositories moved* is a measurement; the gap between them is a
delta. That is the same shape as `qmcp` and `dossier` disagreeing about an
invocation, and it wants the same machinery.

**What this is not.** A decision. Everything below that needs a human is marked,
and nothing here ratifies, merges, pushes or tags.

**Stamped 2026-08-19, `qm` `main` at `f899dff`, this page written on
`evolve/active-repos`.** Figures below name the command that produced them, per
`records/DRAFT-few-integers-in-durable-text.md` rule 2. Re-derive rather than
quote.

---

## Part A — the handoffs, read against today's tree

`handbook/handoffs/README.md` is the index and it is stamped 2026-08-14. Several
of its rows describe work that has since landed. Read against the three
repositories on 2026-08-19, the queue sorts into three groups.

### Spent — the work landed, and the page now describes a state that is gone

| page | what closed it |
|---|---|
| `dossier-delta-review.md` | the delta entity is on `dossier` `main`; the two alembic heads are reconciled and a `009_delta_tables` revision sits in the chain |
| `qmcp-flows-as-deltas.md` | `qmcp deltas` exists and emits payloads in dossier's column names; steps 1–3 of its four-step path are done |
| `harness-next-test.md` | the harness is on `main` and has been exercised by sessions that did not build it |
| `governance-status-generator.md` | built; what remains is the seam contract, which belongs in the record rather than the queue |
| `two-views-one-dataset.md` items 1 and 3 | both projects parse and emit addresses; `qmcp/addresses.py` and dossier's own implementation each run the shared vectors |

Per the routing rule at the top of that index — *delete a page when its work
lands* — these are pages to remove, not pages to annotate.

### Live — the work is real and unfinished

| page | what is actually left |
|---|---|
| `two-views-one-dataset.md` item 2 | pre-grammar branch rows in a dossier database were written by slugging code and cannot be recovered into addresses. Migrate from the refs, or record that they are re-synced rather than converted |
| `two-views-one-dataset.md` item 4 | each dashboard rendering the other's rows. Blocked on nothing now |
| `apply-the-main-ruleset.md` | one command, and an agent must never run it |
| `semantic-review-of-the-records.md` | the one milestone requirement no check can measure |
| `semantic-review-session.md` | the method for the above |
| `disk-tooling.md` items 1, 2, 4 | three policy decisions; item 3 is answered |
| `the-active-four.md` | this session's predecessor, and the state it names is still the state |

### Superseded — true when written, and about a model the corpus has replaced

`session-2026-08-12.md`, `session-2026-08-15.md`, `for-a-stronger-model.md`,
`governance-loop-poc.md`, `two-gate-and-tag-teeth.md`. Each is sound on its own
subject. Their standing value is the *method* they record, and by
`handbook/style-guide.md` that belongs in the runbook or a retrospective rather
than in a queue somebody picks up cold.

### Outside `qm`

Four handoffs live in other repositories and none is indexed anywhere:
`datum/HANDOFF.md`, `codecartographer/HANDOFF.md`,
`codecartographer/docs/llm/RAD_INTEGRATION_HANDOFF.md`, and
`factorio-sysops/docs/HANDOFF-MULTI-REPO.md`. They are project-local and belong
in their projects. **One of them is a problem** — see Part B's finding on `rad`.

---

## Part B — repository activity

### The question, and why the roster could not answer it

`ci/workspace.yaml` held its categories as four **comment headers**. Nothing
could read them, nothing could check them, and only one of the four was
genuinely a claim about attention — the other three were dated observations
written as prose. A measurement in a comment goes stale silently, which is what
had happened.

`records/DRAFT-project-phase-ladder.md` §4 already settles the shape: the claim
and the evidence are separate documents and neither may be derived from the
other. `attention` is to activity what `phase` is to the ladder.

### The three axes

| axis | kind | where | values |
|---|---|---|---|
| `attention` | a claim | `ci/workspace.yaml` | `active`, `queued`, `dormant`, `retired`, `external`; absent is `unstated`, and a repository the roster omits is `unrostered` |
| `recency` | measured | `inventory-public.json` | `archived`, `live`, `quiet`, `cold`, `unknown` |
| `risk` | measured, machine-scoped | `inventory-local.json` | `unpushed:<n>`, `dirty:<n>`, `pin-drift`, `clean`, `unreadable:<reason>` |

**An absent `attention` is `unstated`, never `dormant`.** `dormant` says nobody
is working on it; `unstated` says nobody answered the question. Collapsing the
second into the first grows the roster claims no human made — the substitution
`phase_source` already refuses.

**`unreadable` is not `clean`.** A repository nobody could inspect has an unknown
amount of work at stake.

**`risk` never reaches the committable file.** Unpushed counts and dirty counts
describe one operator's disk. `ci/inventory.py`'s own docstring records why the
split is a file boundary rather than a filter.

### The field the recency axis reads, and the two it refuses

This is the load-bearing part, because the obvious choices are both wrong.

`updatedAt` moves when anybody edits a description or a topic. `pushedAt` moves
on a push to **any** ref — a tag, a bot branch, a Pages deploy, a bulk sweep.
Measured on 2026-08-19 with

```sh
gh api graphql -f query='{ organization(login:"quaternionmedia") {
  repositories(first:100, orderBy:{field:PUSHED_AT, direction:DESC}) {
    nodes { name pushedAt updatedAt
      defaultBranchRef { target { ... on Commit { committedDate } } } } } } }'
```

three repositories reported `pushedAt` within one hour of each other while their
default branches had last moved in 2025, 2023 and 2023. A classification built
on `pushedAt` calls a three-year-dormant repository active, confidently and
every time.

So `recency` reads `defaultBranchRef.target.committedDate`. It is still not the
whole answer — it cannot see work on another branch, and it cannot see work that
never left a disk. That is what the `risk` axis is for.

### What the risk axis found

`uv run qm inventory`, 2026-08-19, reading the clones in this workspace:

- **`rad` holds commits on `evolve/rad-v1` that exist on no remote**, and the
  local branch is *ahead of a branch that still exists on the host* — the one
  reading with no benign explanation. Among them is
  `adr/DRAFT-rad-host-integration-standard.md`. Verified absent from `main`,
  `origin/main` and `origin/evolve/rad-v1` with `git ls-tree -r --name-only`.

  **`codecartographer/docs/llm/RAD_INTEGRATION_HANDOFF.md` is committed, in
  another repository, and opens by deferring to that document**: *"Where this
  page and the standard disagree, the standard wins and this page is a bug."*
  The standard it defers to exists on one disk. Anybody following that link
  gets nothing.

- **`alfred` holds the largest body of work at stake in the workspace** —
  several branches on no remote, a dirty tree, and a modified `governance/qm`
  submodule pointer. Its `origin/main` last moved in January 2024
  (`git log -1 origin/main`). This is not a dormant repository; it is a dormant
  *host copy* of an active one.

- **`qmetronome` carries a `v0.0.25` tag on no remote.** In a corpus where
  `records/DRAFT-version-tags-are-claims.md` makes the tag one of the two human
  gates, a tag nobody can fetch is a release claim nobody can check.

- Two repositories the corpus governs — each with a `project/<name>` branch in
  this repository — were absent from the roster, so `qm inventory` reported them
  under *"the corpus cannot see these"* while the corpus was propagating into
  them.

### One defect the axes exposed in the corpus's own tooling

`ci/inventory.py` carries **its own roster loader**, and `ci/roster.py` exists
precisely to stop that: its docstring records that four generators reading
`entry["name"]` broke at once when private entries became nameless, and that
loading therefore lives in one place with `name` guaranteed. `inventory.py`
never adopted it, so its private entries were dropped and the corpus reported
repositories it had rostered as invisible to itself.

**The fix is to delete the duplicate loader, not to repair it.** That is the
outstanding item below.

---

## Part C — `dossier` and `qmcp` as the harness/dashboard standard

### What is true today, established by running it

| | |
|---|---|
| `dossier` suite | `uv run pytest -q`, 2026-08-19: passes with no skips, so the tag-determinism gate would accept it |
| `qmcp` suite | same command and date: passes, **with skips**, so `qmcp` cannot be tagged |
| addresses | both parse and emit the corpus grammar; neither imports the other |
| the seam | `qmcp dashboard --json` and `qmcp deltas` cross to `dossier harness ingest` and `dossier deltas ingest` |
| disagreement | `dossier.harness.plan` already reports `differs` rather than overwriting, which is the record's rule implemented |

`dossier/walkthrough/04-the-pair.md` and `qmcp/walkthrough/01-the-harness.md`
both execute, so neither can have drifted from the code.

### Gap zero, which this plan had not named — done

**The seam was verified on both sides against fixtures each side had written
itself.** The harness built its test databases with hand-written `CREATE TABLE`;
the control panel hand-wrote the payload as a dict. Neither fixture had ever met
the other side, both suites were green, and both carried a status string the
harness's enum has never contained.

Running the real emitter into the real reader once found a live defect: a
harness whose database is missing the tables it reads reported its counts as
zero, and the reader coerced and stored them, so **a harness nobody could
measure was recorded as a harness with nothing wrong**. Both sides had named
that exact hazard in their own docstrings, and both had written down the same
wrong mitigation — that the table count tells an idle harness from a broken one.
It does not: a database of unrelated tables reports one like any other.

What replaced the fixtures is `project-seed/harness-payload-vectors.json`,
shipped through the governance submodule like the address vectors, with every
payload in it generated by the real emitter reading a database built from the
real models. Each side runs the same cases against its own real code and neither
imports the other.

The convention was already in this corpus — `harness-status.json`'s reading
block says unknown is a value, says why, and is not zero, not empty and not
compliant. The seam had not adopted it. Payload schema 2 does, and the reader
refuses such a payload rather than storing a fiction.
`perspectives/2026-08-19-two-fixtures-that-agreed-with-nothing.md` is the
retrospective.

**Ordering, because the change spans three repositories.** The corpus commit
carrying the vectors lands first; each project then bumps its pin and its tests
start running against the contract. Until a pin moves, the new tests in that
project fail with a message naming the absent file — deliberately a failure and
not a skip, because a green skip is how a repository comes to believe it is
conformant to something it never ran.

### The four gaps, in the order they unblock each other

**1. `qmcp deltas` emits the wrong subject.** Run today it emits the *steps of a
cookbook pipeline* — `summarizer`, `risk_assessor`, `test_planner`. Those are a
demonstration that the step↔delta correspondence holds. They are not this
project's units of work, so the payload that crosses the seam carries an example
rather than a state. *Done* looks like `qmcp deltas` emitting what qmcp is
actually doing, with the pipeline form kept behind its existing `--pipeline`
flag and named as the demonstration it is.

**2. The human-in-the-loop queue does not cross the seam.** `qmcp` holds
`human_requests` and `human_responses` as tables, and the dashboard payload
carries only their **totals**. So the control panel can say how many requests
are outstanding and cannot say *which*, cannot address one, and cannot show it
beside the work it blocks. For a pair whose whole claim is human-in-the-loop,
this is the gap that matters most. *Done* looks like each request crossing as an
addressed row — `<owner>/<repo>/human-request/<id>` — with the address linking
it to the delta it blocks.

**3. Only one project emits deltas.** "Deltas across projects" needs more than
one emitter. `dossier deltas from-prs` already derives units of work for the
whole org from the host side, so the two meet on the address: one row observed
from the host, one claimed by the harness, the same address. Where they differ,
that is a delta by the record, and `uv run qm divergence` is the mechanism.
*Done* looks like a second project emitting, and the two sides reconciling on
address rather than on filename.

**4. The payloads are files a person copies.** Named as the gap in both
walkthroughs, so no page needs rewriting first. *Done* looks like one side
obtaining the other's state without a filename on a command line, with every
harness figure still carrying how old it is.

**5. The payload carries the operator's absolute database path**, and the
control panel stores it. `qmcp dashboard --json` emits `database` as a full
filesystem path, including the username on a Windows machine, and
`HarnessSnapshot.database` keeps it. The payload is a file a person copies, and
copying it into a pull request publishes that path. This corpus already refuses
the same thing elsewhere — `ci/inventory.py` splits by file boundary so an
absolute path cannot reach a committable document, and its suite asserts it. The
seam has no such guard. The vectors carry a placeholder in that field rather
than a real path, which keeps the contract clean and does not fix the live
payload. **Whether to keep the field, hash it, or reduce it to a basename is a
decision with a consumer on the other side**, so this session recorded it rather
than taking it.

### What must not be built

**A resolver.** The grammar deliberately says nothing about existence, and
folding a lookup in would make every render depend on a network call.

**A winner.** `records/DRAFT-a-disagreement-is-a-delta.md` §1–4: neither value is
discarded, identity is the address plus the field, detection opens at
`brainstorm`, and convergence is reported and never closed.

**A comparison over every field both sides hold.** Which fields are compared is
a declaration. The record names comparing each side's own observation timestamp
as the failure mode.

---

## The list

Ordered by what unblocks what. Nothing here is started without saying so.

### Governance repairs found by reviewing — all done, in commit `01c3cfe`

Recorded because *how* they were found is the transferable part: none came from
a check. Every one came from reading the corpus before writing against it.

1. **`ci/inventory.py` carried a second roster loader.** `ci/roster.py` exists
   because four generators broke at once when private entries became nameless,
   and `inventory.py` never adopted it, so its private entries were dropped. The
   first attempt repaired the duplicate; the fix is that the duplicate is gone.
2. **`handbook/generated-documents.md` named a file that does not exist** —
   `inventory.json`, where the generator writes three files and none has that
   name — and carried a copy of a count the document holds, which is
   `records/DRAFT-few-integers-in-durable-text.md` rule 3 in the page that
   indexes the generated documents.
3. **`ci/workspace-private.yaml` had two references swapped** against the
   creation order `ci/inventory.py` assigns them by, so a reference in the
   roster and the same reference in `governance-status.yaml` denoted different
   repositories. Repaired; the file is gitignored, so nothing was committed. Its
   own header asserts it matches `inventory-private.json`, and that assertion
   was false.
4. **The `attention` vocabulary got a record** —
   `records/DRAFT-attention-is-a-claim-activity-is-measured.md` — because it is
   an org-level claim binding every roster row, exactly parallel to
   `records/DRAFT-project-phase-ladder.md`, and
   `records/DRAFT-governance-arrives-as-a-mechanism.md` §1 refuses a binding
   rule that arrives as prose alone.
5. **Figures in the new docstrings** became relations pointing at the
   perspective that holds them with their query and their date.

### Found while running the gates, and not yet done

6. **The `private-names` gate checks against a companion it does not date.**
   `uv run qm private-names` reports clean and names how many private names it
   checked, without saying when that list was generated. The org has gained
   private repositories since the companion on this disk was written, so a name
   made private after it would not be in the list the gate checks, and the gate
   would report clean for a name it has never heard of. Nothing is leaking today
   — the newest private repository's name appears in no tracked file, checked
   with `git grep`. The repair is cheap and the value is that the gate's blind
   spot appears in its own output: print the companion's `generated_at`, and
   refuse rather than pass when it is older than its own staleness budget.
   `records/DRAFT-going-private-is-an-act-with-obligations.md` places the duty
   on whoever flips the switch, which is why this is a visibility gap and not a
   missing watcher.
7. **`uv run qm config` reports violations that predate this work.** Every status
   document sits at the repository root where `handbook/config-standard.md`
   puts them under `status/`. It is a sweep across many files, it is not a gate,
   and it is named here so it stops being rediscovered.

### Then

6. `rad`'s unpushed branch, and the standard another repository already defers
   to. **A human's call** — pushing somebody's branch is not an agent's.
7. `alfred`'s at-risk work. **A human's call**, same reason, larger.
8. `qmetronome`'s local-only tag. **A human's call**: it is a release claim.
9. `qmcp`'s skips, which are missing optional dependencies rather than missing
   paths — dossier's method does not transfer.
10. The four pair gaps above, in order.

### Blocked on a human, and named so it stops being invisible

- Ratifying anything. Every record everywhere is `Proposed`, and that waits on a
  second active code owner.
- Applying the `main` ruleset — `handbook/handoffs/apply-the-main-ruleset.md`.
- Whether the two newly-rostered repositories should be cloned into this
  workspace at all.
- Whether `rad`'s records move onto its `project/rad` branch.

## What could not be verified

*Partly resolved.* The `pushedAt` movement on repositories whose default
branches have not moved in years was unexplained when this page was written. For
one of them the cause was then established: `carlos` moved from `quiet` to `live`
between two runs twenty minutes apart, and
`gh api graphql` on the repository showed a real commit on its default branch in
that window, authored by this operator — a concurrent session adopting
governance. For the other two it remains unestablished, and a sweep, a mirror
and a bot all produce the same signal. The recency axis does not depend on the
answer: it depends on the field not answering the question, which is
established.

*This is also the axis working.* The transition was caught by re-running the
measurement, not by anybody knowing about the other session.

*Inference, not fact.* `patch-id` was tried as a way to tell merged work from
unmerged and rejected, because this corpus's seed-refresh commits are
byte-identical to each other by construction and it matched across unrelated
branches. It was not tried against a rebase-then-merge, which is the case it
would be for.
