# Perspective — The Consolidation Cycle, and the Readings It Got Wrong First

| | |
|---|---|
| **Standing** | Perspective — non-binding, attributed, dated. Not a record; never ratified; cite by author and date. |
| **Author** | Peter Kagstrom |
| **Tools** | Claude Opus 5 (1M context), driving the session; subagents of the same tool for the parallel audit and the parallel build, each of which returned findings that contradicted the brief it was given |
| **Task** | One session took the estate from "a large body of work has exactly one copy, on one disk" to seven repositories merged to `main` and the cycle written down as a runbook with two routes. This is why it went the way it did, and in particular the readings that were wrong before they were right. The reusable part is the assumption behind each. |

## 0. Standing and evidence

One workstation, the clones under `repos/qm/` and three outside it, one git
(2.37), the host reached through `gh`. Commits are stamped in
`handbook/handoffs/six-branches-reached-origin.md`; every figure here is one
run at that stamp.

- **E1** — directly observed: command output, gate output, host state.
- **E2** — read from the repositories.
- **E3** — inference, marked where it appears.

## 1. The shape of the session

A survey of every clone found the same thing the previous handoffs had named:
work with one copy, on scratch branches, several of them literally called
`test`. The cycle that followed — govern the names, verify the commits, push,
open one pull request per repository, audit what a green pull request hides,
merge stage by stage on a person's approval, retire what landed, regenerate,
reload — is now `handbook/consolidation-runbook.md`, and its two missing
instruments are `uv run qm estate` and `uv run qm merge`. Nothing below is
about that outcome. It is about the moments where a signal said one thing
and the estate was another.

## 2. The reassuring form of a trap already written down

**The assumption:** `git merge-tree --write-tree` answers "does this branch
rebase clean?" — so a dry run over seven leftover branches that printed
`CONFLICTS=0` for every one meant seven clean rebases.

**What it was (E1):** this machine's git is 2.37, which does not have that
flag. Every call errored; a `grep -c '^CONFLICT'` over the *error text* found
zero; the script printed the reassuring number seven times. Real trial merges
— a detached worktree, `git merge --no-commit --no-ff`, read `--diff-filter=U`,
abort — showed **every one of the seven conflicts**, mostly in regenerated
artifacts and index files, a few in source.

**Why it is worth a section:** the memory that steers these sessions already
held this exact trap, from 2026-08-11, in its *dramatic* form — the same usage
error read as "eight branches conflicting." Knowing the trap in one direction
did not protect against it in the other. Uniformly dramatic and uniformly
reassuring are the same tell, and a uniform result is a tooling fault until
shown otherwise (`AGENTS.md` item 10). The assertion that would have caught it
is the one item 12 names: assert the intermediate — that the command exited
zero and produced the document you are about to grep — before reading it.

**The check now:** none mechanical. The memory carries both forms; the
handoff's queue records the trial-merge method and results. The next piece of
work is a `--trial-merge` reading in `qm estate` that does the worktree method
for each one-copy branch, so the survey answers the question instead of
inviting a dry run that cannot.

## 3. A worker that reaches the network is not invisible to the tests around it

**The assumption:** a `@work(thread=True)` method on dossier's Harness tab that
polls the harness over HTTP affects only that tab.

**What it was (E1):** under the parallel suite, with a development harness
running on this machine, that thread's real I/O slowed screenshot captures in
*unrelated* tests until one of them failed intermittently. In CI, with no
harness, it fast-failed and was invisible. The defect was mine — the worker
was added that session — and it presented as a flake in a test it never
touched.

**The check now:** an autouse fixture in `tests/ui/conftest.py` stubs every
seam-crossing worker for every UI test, and each new worker added later that
session (the topology pane, the goal send, the archive read) was added to it
with its reason. That is a convention, not a guard: nothing fails when the next
worker is added without a stub. The guard that does not yet exist is a test
that enumerates every threaded worker that can reach the network and asserts
each is in the stub list.

## 4. A runner that cannot read the keyring reports every commit unsigned

**The assumption:** the local preflight's signature step saying most commits
"carry no signature this git could read" meant the consolidation line was
unsigned.

**What it was (E1):** the step's own wording was exact — *could not be checked*
— and `git log --format=%G?` read directly showed nearly every commit `G`; the
two `E` were the other session's, signed with a key this keyring lacks and
verified by the host. The runner's subprocess simply could not reach the agent.
I conflated "could not check" with "unsigned" in the summary before reading
the per-commit column.

**The check now:** the step distinguishes the two states in its output, and
the runbook's verify line says to read `%G?` directly. What would remove the
conflation is the preflight summary counting `E` apart from `N`; it counts
them together today.

## 5. "Merge it yourself" and a tool that gates merging

**The assumption:** `AGENTS.md` item 3 — the author merges once every gate is
green — meant the session could merge nine green pull requests in one pass.

**What it was (E1):** the tool's permission classifier refused the act as a
merge without review. The corpus's rule and the tool's gate are not in
conflict; the corpus assigns the pull request to the person who asked, and a
person approving each stage *is* the review the gate wants. Nine stages, each a
question with the live state re-read immediately before the act, satisfied it.

**The check now:** `uv run qm merge` is that shape made permanent — a reading
by default, and the act only with `--yes`, re-read live at that moment, merge
commit only. The flag is the signature of the person's act, which is what both
the corpus and the gate were asking for.

## 6. The estate moves while you are reading it

**The assumption:** state established at the start of a pass stays true for
the pass.

**What it was (E1):** between the survey and the merge review, another session
closed the apothecary pull request this session had opened and replaced it
with a broader one; between building and integrating, another session merged
qm #111, which *took this session's own handoff page into the queue* and
rewrote a generated document with LF; qm's `main` moved twice under a branch
cut from it. None of this was wrong — it is `handbook/async-contract.md`'s
normal case — and each was caught only because every act re-read the host
first: the merge sweep found #21 where the brief said #20; the merge of `main`
into the cycle branch surfaced the two-sided edit of one handoff page and let
the newer version win.

**The check now:** `qm merge` and `qm estate` both read live. What has no
guard is two sessions editing one handoff page; the one-pull-request rule and
the routing rule (delete a page when its work lands) are the constraint, and
they held.

## 7. A pull request that predates the rules `main` has since added

Joining #110 — a two-commit loose-ends tracker — with the consolidation line
that added several rules needed four reconciliations, and two were real
defects the gates caught rather than textual conflicts:

- the tracker read its three sources at names the consolidation had moved,
  as JSON where the documents were now YAML;
- the tracker ran *before* the state page it reads. `uv run qm docs check`
  reported drift the moment the document was written — it described the
  previous run. Moving the join after the page tripped the ordering guard,
  which approximated "a document the state page reports on" as "anything not
  `.md`." The guard was right to fire and wrong in its approximation; it now
  states its invariant — a step may follow the page if it renders it, or reads
  it as a source and is not described by it — tied to `loose_ends.SOURCES` and
  seen to go red when that fact is mutated (`AGENTS.md` item 13);
- the record addressed principles by ordinal, which the new `edges` gate
  refuses;
- the record was absent from the index the strengthened adr-lint requires.

**The reusable part:** read the base's gates as the list of what changed since
the branch was cut. Expect the reconciliation; the trial-merge results in the
handoff show the same shape waiting on every leftover branch.

## 8. Briefs that stated a hypothesis as a diagnosis

Two of the parallel agents returned findings that contradicted their briefs,
and both were right. The codecartographer brief said the failing test was
"likely a handler bug from stacking two lines"; the agent showed it was a test
mis-classifying a submodule-fed route as self-contained, and that the fix the
brief suggested would have broken sanctioned tests. The estate builder's own
mutation loop had a scaffolding fault — a backup written by a fallback that
never ran, so restores silently failed and mutations accumulated — which it
caught by asserting the backup existed before trusting a red, and recorded in
the test's header.

**The assumption:** an error message locates the defect. It locates the
symptom. The briefs were written from the message, not the code, and the
saving grace was that they said *likely*.

## 9. What was found before it fired

alfred's working tree moves its `governance/qm` submodule pin to a commit that
exists on no origin ref. Pushed, that gitlink would break `git submodule
update` for every consumer. It was found by reading, not by a gate — but the
gate exists: `uv run qm pins` asks exactly "is every pin a commit somebody else
could get," and the seed's `check-submodule-refs` refuses it at push. The
handoff says do not push it, and names the two legitimate targets.

## 10. The check that exists, run last

**The assumption:** a pull request green on every listed gate has passed the
corpus's checks. The `registries` gate was green on #112, so private names
had been checked.

**What it was (E1):** `uv run qm private-names --strict`, run at the closing
pass, found the names of two private repositories in the handoff page this
session had already pushed — and the same names in the committed roster and
in files another session merged that day. The `registries` workflow's own
header says it **leaves `qm private-names` out on purpose**: the check reads
the host's list of private repositories, and a check that reads a machine
"reds a pull request for a reason its author cannot fix." It is an
author-run gate. Nothing was hiding it; I had read the green gate as covering
a check it names as excluded, which is the ordinary cause (`AGENTS.md` item
11) and not the interesting one. The leak was mine; the roster's is older.

**The check now:** it existed the whole time. What did not exist was a place
in the procedure that runs it: `handbook/consolidation-runbook.md` Step 3 now
runs `private-names --strict` and `leaks` before Step 4 pushes, and says why
the runner will not. The roster's own exposure is a person's redaction
(handoff, blocked on a person). One nit for whoever touches the check next:
its docstring says CI runs it with `--strict`, and the workflow that would
says it does not.

## 11. What this session did not verify (E3)

Whether the other qm session is live at this moment; whether the leftover
branches' source conflicts are shallow; whether the deploy job on rad's `main`
is red only for the Pages setting. Each is marked as inference where the
handoff repeats it.
