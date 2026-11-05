# Perspective — Two Views That Go Stale Together

| | |
|---|---|
| **Standing** | Perspective — non-binding, attributed, dated. Not a record; never ratified; cite by author and date. |
| **Author** | Peter Kagstrom |
| **Tools** | Claude Opus 5, which found the third instance only after being told to look for the same shape twice more |
| **Task** | One defect, found three times in one day in three unrelated subsystems, each time by the same method. The reusable part is the method, and it is one sentence long: *compare against something this system did not write.* |

## 0. Standing and evidence

One machine, five clones, one database, at the commits stamped in
`handbook/handoffs/the-estate-has-one-copy.md`.

- **E1** — directly observed: command output, query results, git history.
- **E2** — read from the repositories.
- **E3** — inference, marked where it appears.

## 1. The same defect, three times

Each of these was a *stored claim* with an *observable truth* beside it and
nothing between them.

**Branches.** `git branch -r --merged` says which remote branches are contained
in the default branch. It has nothing to say about a *local* branch holding
commits its own remote does not have. `rad`'s `evolve/rad-v1` reads `+0/-5` —
fully merged, delete freely — while the clone held seven commits nobody could
fetch. Across five clones, a hundred and two commits had exactly one copy, the
oldest for nineteen days (E1).

**Deltas.** `dossier` builds one delta per *open* pull request. When one merges
it stops being open, so the pass that would update its delta never sees it
again: a delta enters at `review` and can only leave if a person moves it. Not
one delta in the database was `complete` or `abandoned`. The repository the
application is named for had forty-four merged pull requests and **no deltas at
all** (E1). Noisy and incomplete at once.

**Threads.** Nine threads listed as work in flight. Three named pull requests
that had already closed or merged (E1).

## 2. Why none of them was visible

In every case the two things that disagreed were **both written by the same
system**, and a system's own records go stale together.

`project_delta.phase` and `project_pull_request.state` are filled by one sync.
When the sync stops running, the delta says `review`, the pull request row says
`open`, and they agree perfectly. A checker comparing them returns nothing and
prints a clean result — which is the estate's most-repeated mistake, an empty
query read as a good answer, and the reason it keeps being repeated is that
this version of it is *indistinguishable from success*.

The same for branches: `git branch --merged` compares refs against refs, all of
them local. And for threads: the thread list and the pull-request rows come
from the same generated document.

## 3. The method, which is one sentence

**Anchor the comparison to an artefact this system did not write.**

In all three cases the anchor turned out to be the same thing — the git
history — and in all three it needed no network and no credentials:

- **Branches**: `git cherry` compares *patch ids*, so a branch whose work
  landed upstream under a different sha is distinguishable from one whose work
  landed nowhere. Two `dossier` branches were each one unpushed commit,
  seventeen days old, identical in every count `rev-list` can produce: one had
  already landed and held nothing, the other was 556 lines that existed
  nowhere else (E1).
- **Deltas and threads**: `Merge pull request #N` in the default branch is
  GitHub's own record of what landed, written by the host. Comparing it against
  the database's highest known pull request gives a lag per project, entirely
  offline. `dossier`'s board was twenty-nine pull requests behind its own
  clone; `qm`'s was thirty-six (E1).

The lag is the important half, and it changes what every other line means. A
board behind its own clone cannot report a clean result however few
disagreements it shows, because the disagreements it can see are a floor rather
than a count. Both tools print that verdict first and refuse the word "clean"
while it stands.

## 4. What the anchor cannot do, which is half of one case

**A pull request closed without merging leaves no trace in the default
branch.** So the offline check finds a thread whose pull request merged and
cannot find one whose pull request was closed — and both of the threads found
genuinely stale by hand were the second kind.

That is not a caveat to bury in a docstring. A short list of findings reads as
a small problem, so the tool prints the boundary whether or not it found
anything. Naming what a check cannot see is the difference between a limit and
a hole, and this corpus has enough experience of the second to prefer stating
the first.

## 5. The rule I nearly wrote, and the data that refused it

The threads had dates on them. The oldest named a pull request last touched on
2023-12-30, and an age-based rule would have been the obvious thing to write.

That pull request is **genuinely still open** (E1). The two threads that were
actually wrong had closed within the last three weeks. A rule keyed on age
would have flagged the one correct row and missed both defects — precisely
inverted.

So nothing in the tool judges a thread by its date. It reports what the clone's
history settles and stops. **Age is not staleness**, the counterexample was in
the data before the rule was written, and the only reason it was found is that
four rows were checked against the host instead of reasoned about.

## 6. What a machine may fix

Of five kinds of disagreement the delta tool reports, exactly one may be acted
on automatically: a delta whose pull request has merged becomes `complete`,
because that is arithmetic rather than judgement.

The other four are refused, and the reasons differ:

- **absent** would have the board invent rows for work nobody chose to track,
  and a board that writes its own entries is one nobody trusts.
- **automated** asks whether a bot's dependency bump is a unit of work. That is
  a policy, and an application does not get to set the policy about what counts
  as its users' work.
- **unbacked** and **behind** both mean *go and sync*, not *go and edit*.

The branch tool goes further and takes **no delete flag at all**, with a test
asserting it never will. A census that can also destroy is one somebody runs in
a hurry.

## 7. What this cost, and what it did not

Nothing was broken. Every suite was green through all three defects — not green
afterwards, green while they were live — because every check that existed was
checking the wrong pair of things. The cost was three signals that had quietly
stopped meaning anything: a branch list that could not warn you, a board
reporting work that finished weeks ago, and a thread list mixing three-year-old
truth with three-week-old fiction.

## 8. What to distrust here

§3's claim that the anchor is *always* the git history is a generalisation from
three cases that happened to share a substrate. The real rule is the weaker and
duller one — compare against something you did not write — and git was simply
the thing at hand. The next instance may have no such artefact, and then the
honest answer is `unknown` rather than a cleverer comparison between two things
that already agree.

And the ordinary caution: all three defects were found by one practitioner in
one day, looking for the same shape after being shown it once. That says
something about how well the shape generalises. It says nothing about how many
other shapes went unlooked-for.
