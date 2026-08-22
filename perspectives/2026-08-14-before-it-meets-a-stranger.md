# Before It Meets a Stranger

| | |
|---|---|
| **Date** | 2026-08-14 |
| **Author** | Peter Kagstrom |
| **Status** | Unreviewed |
| **Binds** | Nothing. `perspectives/` is opinion. |
| **Tools** | An assistant, across the session that built the CLI, the gate index and the state layer described here |

---

## What this answers

The corpus is approaching a milestone where people who did not build it read it:
alpha testers, other developers, power users. A second human code owner arrives
around the same time, which unblocks ratification — the stated reason every one
of the fourteen records is still `Proposed`.

Three properties start mattering that have not mattered so far. The corpus has
to be **cogent** to someone with no context, it has to hold its knowledge in
documents rather than in the memory of whoever was in the last session, and it
has to survive having its records actually ratified.

This is what the tooling built today says about how close it is, and what the
gap costs.

## What the session that produced this got right, so it is repeatable

The work improved partway through, and the change was not effort. It was this:

**Every finding got a mechanism, not a clause.** The version-tags record claimed
in its own §7 to be "mechanical rather than customary" and nothing read a tag;
it now has a checker, a workflow and an org-wide audit. The entry-point/record
divergence became `check_restatements.py`. The four state vocabularies became a
generated document. Nothing was added to any list of rules a session must
remember.

**The tools were believed over the prose, including my own.** `--check` caught a
document that listed a view written after itself, so it could never be
self-consistent. The mutation harness caught three of my own mistakes. The CLI
exposed two environment failures — a shell resolving to WSL under `uv run`, and
a venv with no pip — that had been invisible while every command happened to run
from one shell.

**A correction was taken as a correction.** The reviewer's one-line statement —
pull requests are audit into `main`, human review happens at tagged releases —
overturned an analysis I had already delivered with confidence. Reconciling it
took an hour. Defending it would have cost the milestone.

## Where the corpus actually stands

Measured on `evolve/governance-loop-poc` at `460d657`, not quoted from a page:

| | |
|---|---|
| Governed documents | 69 |
| Records | 14, **all `Proposed`.** Nothing has ever been ratified |
| Perspectives | 26 `unreviewed`, 1 whose state cannot be established |
| Handoffs | 10, and every one is transient by its own directory's rule |
| Gates | 10 declared, 9 built, 1 declared-and-not-built |
| Enforced at the merge boundary | nothing. 0 rulesets, no branch protection |
| Mandatory reading before a first edit | `AGENTS.md` 250 + `async-contract.md` 235 + `handoffs/README.md` 141 = **626 lines** |

That last number went **up** this session, by 58 lines, in the course of work
whose stated aim included reducing it.

## Four things a stranger will hit, in the order they will hit them

**1. There are four front doors and no lobby.** `README.md`, `AGENTS.md`,
`PRINCIPLES.md` and `handbook/` all present as the place to start, and each is
correct for a different reader. An alpha tester asks where to begin and the
corpus has four answers, none of them wrong, which is the same as no answer.

**2. Nothing is ratified, so nothing looks decided.** Fourteen `Proposed`
records read, to someone outside, as fourteen things this organisation has not
made up its mind about. The real reason is a gate — one code owner cannot
approve their own pull request — and that reason is written down in `README.md`.
A stranger will not reach it before forming the impression.

**3. The knowledge that is load-bearing lives in the pages built to be deleted.**
`handbook/handoffs/` says so in its own routing note: *delete a page when its
work lands.* Those ten pages currently carry the ordering constraints between
work items, what blocks what, and the milestone itself. When they are deleted as
designed, that knowledge has no home. This is the memory problem, and it is not
hypothetical — it is scheduled.

**4. The second code owner changes a rule I changed today.** Draft-by-default
existed to stop a ready pull request notifying `CODEOWNERS`. I removed it: draft
now means unfinished, and the author merges a green pull request. `.github/CODEOWNERS`
is currently inert — all sixteen rules carry a `#=` prefix. **When the second
owner is added and those rules go live, every ready pull request will notify
them automatically.** Under the two-gate model that is arguably correct, since
the pull request is an audit record and an owner learning that `main` moved is
the point. It will still be a surprise, and it should be a decision rather than
a discovery.

## What I would do before the alpha, and what I would not

**Ratify one record end to end, as a rehearsal.** Ratification has never been
performed. Its five steps include renaming `DRAFT-<slug>.md` to
`QM-NNNN-<slug>.md`, enforced by a regex nobody has ever hit, and
`ci/doc_status.py` now reports a filename-versus-Status disagreement the moment
step 2 happens without step 3. Do the cheapest self-contained record first and
find out what breaks, rather than finding out fourteen times.

**Run the reconciliation this corpus has never had.** Every record against every
entry point, every handbook page against every record. `check_restatements.py`
pairs *declared* restatements and cannot find undeclared ones — that limit is
printed on every run, and there are certainly undeclared ones, because until
today nothing asked. That pass is human, once, and it is what turns thirteen
documents by thirteen sessions into one system.

**Give the ordering a home that is not a handoff.** The gates got one today: a
registry a human edits, a generator, a view. Work ordering could take the same
shape and stop depending on pages scheduled for deletion.

**Do not add clauses.** Two perspectives in this directory already establish
that a clause without a mechanism does not change session behaviour, and that
every clause broken in one measured session had been read in full by the session
that broke it. The temptation before onboarding is to write more rules so
strangers behave. It has been measured here and it does not work. Convert what
exists; add nothing.

**Treat 626 lines as the number to move.** The reviewer's own framing during this
session is the sharpest tool available and is not written down anywhere binding:
*write down what a competent reader cannot derive.* Most of what a stranger must
currently read before their first edit is either derivable or belongs in a check.

## The honest caveat

Everything above is measured on a branch that has not landed, by the session
that wrote the tools doing the measuring. The counts are reproducible —
`uv run qm docs states`, `uv run qm gates` — and the judgements are one
practitioner's. The gap between those two is exactly the gap this corpus keeps
finding in its own work, and naming it here does not close it.
