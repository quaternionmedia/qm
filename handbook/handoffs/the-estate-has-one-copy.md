# Handoff — A coordinated branch cleanup, and the two views it needs

**Transient.** Delete it when its work lands.

| | |
|---|---|
| **Stamped** | 2026-08-27 UTC. Every figure below is one run of `uv run qm branches` and `uv run qm inbound` at the commits named |
| **Standing instruction** | *"continue locally until further notice"*, reaffirmed. **Nothing here is pushed and nothing has been deleted** |

---

## 1. The cleanup is not the job it looks like

Asked for a branch cleanup, the obvious reading is that there are too many
branches. There are, and most of them are trivially safe. That is not the
finding.

**The finding is that a large body of work across this estate has exactly one
copy, and the oldest of it has had one copy for nineteen days.** `rad`'s seven
stranded commits, already written up in
[`the-menu-contract-nobody-could-fetch.md`](the-menu-contract-nobody-could-fetch.md),
turned out to be the visible corner of it.

**So the order matters and it is the opposite of tidying.** Preserve first,
delete second. A merged branch deleted a week late costs nothing; a branch
deleted while it was the only copy of something costs the thing.

### Why a merged-branch listing cannot be trusted here

`git branch -r --merged` answers a question about *remote* refs. `rad`'s
`evolve/rad-v1` reads `+0/-5` against `main` — fully merged, delete freely —
while the clone holds seven commits nobody else can fetch. Two branches in
`dossier` were each one unpushed commit, seventeen days old, identical in every
count: one had already landed by another route and held nothing, the other was
556 lines that existed nowhere else.

Nothing in this estate could tell those apart, which is why §3 exists.

---

## 2. What is actually there

Run `uv run qm branches --repo <path>` in each. Summarised:

| repo | branches at risk | commits with no second copy | oldest tip | merged, safe to delete |
|---|---|---|---|---|
| qm | 13 | 72 | 2026-08-08 | 29 |
| rad | 2 | 17 | 2026-08-09 | 2 |
| codecartographer | 1 | 11 | 2026-08-25 | 6 |
| dossier | 2 | 2 | 2026-08-09 | 35 |
| qmcp | 0 | 0 | — | 12 |

**qm is the problem, not rad.** Eight `fix/<project>-seed-refresh` branches from
2026-08-08 carry between two and thirteen unique commits each — *the
downward-propagation fixes, which themselves never propagated* — plus
`rescued/rad-integration` at ten and `rescued/enumerated-coverage` at eight.
Three more are today's live sessions and are not stale.

`qmcp` is clean: nothing unique held locally, every non-automation branch
merged. It is the model the others should end at.

---

## 3. The mechanism, in two views

Both are read-only, both are routed through the declared entry point, and
**neither deletes, merges, or closes anything.**

### `uv run qm branches` — the downward view

Every branch, classified by *what deleting it would cost*, sorted so the
dangerous rows come first and the safe rows last. The classes are `stranded`
(local ahead of its own remote), `local` (never pushed), `gone`, `ahead`,
`merged`.

**It counts loss by patch, not by commit.** `git cherry` distinguishes a branch
whose work landed upstream under a different sha from one whose work landed
nowhere. Without that the tool shouts about branches holding nothing, and a
census that cries wolf is one nobody reads before deleting.

It takes no `--delete` flag and a test asserts that it never will. `--fail-on-
stranded` is available for a gate; it fires only on work that would actually be
lost.

### `uv run qm inbound` — the upward view

`handbook/propagation-runbook.md` has always said propagation runs one way and
that org content on a project branch is stranded *"if you find any"*. The guard
closes the wrong route; nothing opened a right one.

It turns out the projects have been writing the return path all along. **Every
`Proposed` record names what it pends on**, the ADR lint enforces the row, and
many of those rows name the organisation. `qm inbound` reads them and groups by
*what is being waited on*.

**The top row is the point.** One org action — ratifying the constitution
records — is pended on by six projects at once. Read one branch at a time that
looks like six problems; read together it is one, and it is the cheapest thing
this organisation can do.

Two boundaries it states in its own output: a project whose records are not on
its branch is **unknown, not quiet** (rad keeps `adr/` in its own repository,
which the seed workflow supports); and it does not judge which rows are the
org's to answer, because a `Pends on` row is prose and reading intent would be
a guess printed as a finding.

---

## 4. The cleanup, in order

Nothing below has been done. Each step is a person's act.

**Step 1 — preserve.** Push every branch in the at-risk column, or decide
explicitly that a given one is abandoned. Thirteen of them are in `qm` and eight
are the seed-refresh set. Until this is done, no deletion anywhere is safe,
because the census is the only thing distinguishing the two cases and it is a
snapshot.

**Step 2 — reconcile the seed-refresh set.** Eight branches, one per project,
all from the same day, all carrying propagation work. They are either still
wanted (land them) or superseded (confirm with `git cherry`, then drop). They
are the largest single block and the most likely to be already-superseded.

**Step 3 — land or drop `rescued/rad-integration`.** Ten unique commits from
2026-08-09, the same day `rad`'s branch stranded, and the name says it is about
the integration whose citations currently resolve to nothing. Read it against
`evolve/consolidate-rad` before deciding.

**Step 4 — then delete the merged branches.** Eighty-four across the estate,
none of which cost anything. `dossier` and `qmcp` are almost entirely this.

**Step 5 — the three GONE branches in codecartographer** are 2023 issue
branches this clone has no copy of. Deleting them is safe and they are the only
rows where "old" is a sufficient argument.

---

## 5. What is blocked on you

| what | why it needs you |
|---|---|
| **The local-only window** | Step 1 cannot happen inside it. This is the second handoff to say so and the instruction has been reaffirmed once; it is recorded, not questioned |
| **Ratifying the constitution records** | Six projects pend on it. `uv run qm inbound` names them |
| **Whether the seed-refresh branches are still wanted** | Nobody but their author can say; `git cherry` can only say whether the patches are upstream |
| **`main` protection** | Still queued, still unapplied |

---

## 6. What could not be verified

- **Whether any at-risk branch is abandoned rather than paused.** The census
  reports the age of the tip and stops. A threshold would be a guess.
- **Whether `rescued/rad-integration` overlaps `evolve/consolidate-rad`.** Not
  compared — they are ten and eleven commits from different days and reading
  them against each other is the work of step 3, not of this page.
- **Whether the three 2023 codecartographer branches were deliberately kept.**
  They are reachable only from the remote and nothing in this clone explains
  them.

---

## 7. Verification

One run, at the commits stamped above.

    uv run qm branches --repo <each of the five>
    uv run qm inbound

102 commits across the five clones have no second copy; the oldest at-risk tip
is 2026-08-08. 19 records across 13 projects name an unsettled input, and the
largest group is 6 projects on one ask. `ci/tests/` and
`project-seed/ci/tests/`: 1291 passed, 8 skipped. `uv run --extra preflight qm
preflight`: 37 of 39 steps pass, and the two that fail are `signatures` and the
base check asking the host about a branch that has never been pushed — both
pass locally against `--source git`.

---

## 7b. Where this session's own work is

Two `git worktree` checkouts, because the shared clones were on other sessions'
branches and switching one under somebody is the thing `handbook/async-contract.md`
exists to stop:

| branch | repo | carries |
|---|---|---|
| `evolve/the-status-sees-local-records` | qm | the two views, the `records_dir` probe, the runbook's return path, and this page |
| `evolve/consolidate-rad` | rad | `main` merged into the stranded branch, the cell layer, and the standard's §2b and §5.5 |
| `feat/the-terminal-replays-the-governed-vectors` | dossier | the terminal port replaying the governed vectors |

**They are in the at-risk column of their own census**, which is the correct
answer and not an irony to be smoothed over.

Running rad's gate from a worktree needs `node_modules`, which a worktree does
not get. It was linked in with a directory junction and **the junction has been
removed**, because a later `git worktree remove` walking into it would have
taken the real `node_modules` with it. Re-create it with
`New-Item -ItemType Junction` if the gate needs running again.

## 8. The single next action

**Push the at-risk branches, or say which are abandoned.** Everything else in
§4 is safe, cheap, and reversible. That step is neither, and it is the only one
that gets harder the longer it waits.
