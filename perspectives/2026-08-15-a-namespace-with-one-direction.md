# Perspective — A Namespace With One Direction

| | |
|---|---|
| **Standing** | Perspective — non-binding, attributed, dated. Not a record; never ratified; cite by author and date. |
| **Author** | Peter Kagstrom |
| **Tools** | Claude Opus 5 (Anthropic) |
| **Date** | 2026-08-15 |
| **Task** | Record why `workspace/<slug>` drifted out of reach of every gate, and what the shape of that omission was, so the same shape is recognisable next time. |

## Evidence classes

**E1** — established by a command run this session, output read. **E4** —
inference from a documentation pattern. Nothing here is E5; every claim about
this repository was checked against a fetched ref rather than recalled.

---

## 1. What was found (E1)

Working on the mathematics workspace, four facts came out of the fetch, in this
order:

- `workspace/math-experiments` was **74 commits behind `main`**.
- It has **no `.github/` directory at all**, and `project-seed/ci/` on it
  contains one file. `run_workflows_locally.py`, `check_pr_base.py` and
  `check_one_pr.py` do not exist there.
- Every mention of the namespace across `README.md`, `AGENTS.md` and
  `handbook/` was the same table row — *"a research workspace that never
  merges back | permanent, terminal"* — plus one sentence siting the branch.
- `AGENTS.md` named three branch namespaces for an agent to work on; the
  README's table has five.

So the branch was outside the reach of every gate the corpus had built, and
had been since it was seated. Nothing was broken. Nothing reported anything.

## 2. The shape of the omission

"Never merges back" is a statement about **one direction**. It says a workspace
does not reach `main`, which is true, load-bearing, and the reason a workspace
is safe. It says nothing about whether `main` reaches a workspace.

The absence was read as a rule. Not by anyone in particular — there was
nothing to read it *from*. A `project/<name>` branch has a runbook, a
`propagate/<name>-<date>` convention, a merge-not-rebase rule, and a page
saying when to run it. A `workspace/<slug>` branch had a lifetime column.

That is the general shape, and it is worth naming because it is not a
misstatement: **a rule that constrains one direction of flow, published in a
table whose columns are "Holds" and "Lifetime", reads as complete.** Neither
column has a place to say *how things get in*, so nothing looked missing. The
table was not wrong; it was answering a different question than the one a
contributor arrives with.

## 3. It had already happened once, in the same table (E1)

The README says so itself, one paragraph below the table:

> `propagate/*` was mandated by the propagation runbook and by the table below
> while this list said there were four namespaces and that anything outside
> them was a mistake — with eight such branches pushed. It is listed because
> the rule that a branch outside these namespaces is wrong is only usable if
> the list is complete.

That is the same failure, one namespace over, already diagnosed with the right
general lesson attached. The lesson did not generalise on its own — it was
recorded as a fact about `propagate/*` rather than as a property of the table,
and the next incomplete entry went in underneath it.

## 4. And it was still live in the file most agents read first (E1)

`AGENTS.md` item 3 lists the branches an agent may work on: `evolve/<slug>`,
`perspective/<date>-<slug>`, `project/<name>`. Three of five. An agent asked to
contribute to a research workspace had no sanctioned branch and no sanctioned
base, and the honest options were to invent one or to stop.

This persists in the in-flight governance-loop pull request. Fetching
`evolve/governance-loop-poc` and reading its `AGENTS.md`: the same three-item
list, and the string `workspace` appears zero times in the file. The rewrite
that touches this document most heavily since it was written carries the gap
forward, because the gap is an absence and a rewrite reproduces what is there.

**That is the part worth carrying.** A drift between a canonical list and a
summary of it is invisible to review of either one. The README is complete and
correct. `AGENTS.md` is correct about everything it mentions. Only the
*relation* between them is wrong, and nothing reads the relation.

## 5. What I would take from it

**A namespace table needs a direction column, or a page per namespace.** The
fix taken was the second: `handbook/research-workspaces.md` states both
directions explicitly, including the one that is "never". A rule that says
never is still a rule that has been written down, and the writing is what
stops the absence being reinterpreted.

**A summary of a canonical list should say it is one.** `AGENTS.md`'s branch
list is a convenience restatement of the README's table. Nothing marks it as
derived, so nothing suggests checking it when the table changes. A generated
list, or a line naming the source, would both work; a hand-maintained copy with
no pointer is the one that rots.

**Terminal is not the same as unreachable.** The instinct that a workspace
"doesn't participate" is what made 74 commits of drift feel unremarkable. A
branch that never merges back still needs the gates, and needs them *more* than
a branch under review, because nothing else is looking at it.

**A gate that does not exist on a branch is not a gate that passed there.** The
first CI run in this session was green, against the wrong tree — the `main`
worktree rather than the branch under test. The branch could not have run it;
the runner is not on the branch. Item 12 of `AGENTS.md` names exactly this and
it still happened, which is the ordinary outcome of a rule that has to be
recalled at the moment it applies rather than enforced by the setup.

## 6. What this perspective is not

It is not a claim that the drift cost anything. The workspace holds experiment
designs, none of them run; nothing downstream consumed it; no decision rested
on it. The cost was potential, and the reason to write it down is the shape
rather than the damage.

It is also not a criticism of the propagation model, which is unusually well
specified for the branches it covers. The model's quality is what made the
omission legible at all: `project/<name>` has a runbook detailed enough that
the absence of an equivalent for `workspace/<slug>` was conspicuous once
someone stood in the right place to look.

— Peter Kagstrom, drafted with Claude Opus 5, 2026-08-15
