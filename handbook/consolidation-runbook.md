# Handbook — Consolidating What Exists Only on One Disk

**Routing.** Operational procedure, not a decision record: it weighs no
alternatives and creates no constraint a project could violate. The decisions
it carries out live in *A stage is recorded, and `main` receives releases*,
*Version tags are claims*, *Human-only contributorship* and the asynchronous
contract; this page is how a person or an agent executes them, in order, across
every repository at once. If it ever needs adjudicable teeth — a dispute about
whether a branch was landed or lost — it is promoted to a record and this page
becomes a pointer.

**Audience.** A human or coding agent with no memory of the sessions that made
the work. Assume nothing here was explained to you in conversation, and assume
the disk you are reading holds commits no other disk has.

---

## The shape of the problem

Work in this organisation accumulates on one workstation faster than it reaches
origin. Sessions run in parallel across the estate, each one correct by every
rule it can see, and each one leaves behind a local branch, an unpushed commit,
or a working tree it did not clean. A branch whose remote is fully merged and a
branch holding commits that exist nowhere else are indistinguishable in a list
of names — `project-seed/ci/branch_census.py` says why — and the second kind
has been deleted with the first.

`handbook/propagation-runbook.md` moves a change *outward*, from `main` into an
adopted project. This page is the step before it: getting what a disk holds onto
`main` in the first place, through pull requests, so that there is something to
propagate. It runs as a cycle because the estate fills up again.

What makes the cycle harder than "push and merge" is written down here so
that the next run expects it rather than discovers it:

- **A pull request that predates rules `main` has since added needs
  reconciliation when it is joined.** Every gate on `main` measures the branch
  as it is when the gate runs, and a branch cut before a gate existed has never
  been measured by it. One join in this organisation met that repeatedly in a
  single pull request: a generator reading documents at names that had moved, a
  generated join ordered before the state page it reads, principles addressed
  by ordinal where a new gate wanted names, and a record missing from the
  index. None was a defect in the branch's own work. Read the gates as the list
  of what changed while the branch was away, and budget for the reconciliation
  as part of landing it rather than as a surprise.
- **"Folded into `main`" and "independent" is the distinction that decides
  whether a leftover branch needs its own pull request.** A branch whose
  every patch is already on `main` — by a different commit, through a
  consolidation that carried it — is retired, with nothing to open. A branch
  holding a patch `main` does not have is work, and gets a pull request of its
  own. A commit count cannot tell the two apart, because the consolidation
  that folded a branch's content did not make its commits ancestors of `main`;
  `git cherry` compares patches rather than hashes and can.

---

## Step 1 — survey the estate, from refs and never from a checkout

The question is *what exists only on this disk*, and the answer is never in a
working tree — the checked-out branch is an accident of who ran what last.

```sh
uv run qm estate                          # every rostered repository, one table
uv run qm branches --repo <path>          # one repository, each branch and its cost
```

`uv run qm estate` reads refs across every repository the roster names and
reports, per repository, what exists on this disk alone: a branch with one
copy, marked *folded* when the current HEAD already contains it and
*independent* when it does not; a branch that is on origin but ahead of its
remote copy; and a dirty working tree. With the host reachable it also says
how many pull requests you hold open in each. It deletes nothing and takes no
flag that could. `uv run qm branches --repo <path>` is the same reading for one
repository, sorted by what it would cost to be wrong: stranded first, merged
last.

Read a working-tree finding separately from a branch finding. A dirty tree
that moves a submodule gitlink is a different class of thing from stray build
output, and the survey cannot tell you which is which — open the diff.

*Verify:* the table names every repository in the roster, and no row says the
repository could not be read. A repository the survey could not open is
*unknown*, not clean; a uniform all-clear across the estate is a tooling fault
until shown otherwise.

## Step 2 — put every scratch branch on a governed name

Nothing reaches origin from a branch outside the namespaces
`docs/ref/namespaces.md` lists. This organisation kept using a local branch
literally named `test` as its working target; the stage record names `test` as
the rewritable entry stage, and nothing may branch from it expecting the branch
to survive. The work that lives there travels under its own name:

```sh
git branch evolve/<slug> test             # org-level work
git branch perspective/<date>-<slug> test # a retrospective
```

One project's records are different: `project/<name>` already exists and a
downstream submodule pins it, so a scratch branch holding records is re-cut
*from* `project/<name>` and opens into it, never into `main`.

Cut the governed branch at the tip you intend to ship, and leave `test` where
it is — Step 9 says what happens to it. Where one scratch branch carries
several independent pieces, cut one governed branch per piece, because a pull
request that carries unrelated work under one title is the failure
`AGENTS.md` item 4 was written for.

Before pushing, decide whether the branch is work at all. The survey's
*folded* and *independent* marks are the first reading; take a second one from
git before retiring anything, because the survey compares against the HEAD
that happened to be checked out:

```sh
git cherry origin/main <branch>           # "+" is not on main; "-" already is, by content
```

A branch whose every line is `-` is folded: retire it, open nothing. A branch
with any `+` is independent and continues.

*Verify:* `git branch --list 'test' 'wip/*' 'tmp/*'` shows nothing you intend
to push, and every branch you do intend to push matches a namespace in
`docs/ref/namespaces.md`.

## Step 3 — establish what the branch carries and who signed it

Each of these checks has failed silently here.

```sh
git log --format='%G? %h %s' origin/main..<branch>
```

Every line begins with `G`. Read the other letters before acting on them: `N`
is unsigned and stops the branch; `E` means the signing key is not on *this*
machine, which says nothing about the commit; `B` is a bad signature and is a
question for a person. A branch of `E` on a machine that has never held the
key is the ordinary reading, not an alarm.

```sh
git log --format='%h %(trailers:key=Co-Authored-By,valueonly)' origin/main..<branch>
```

Every line is a bare hash. A trailer naming an unmonitored address violates
`records/DRAFT-human-only-contributorship.md`, and the fix is a rewrite of
that commit on the branch — which is allowed here, because the branch has not
yet reached origin and nothing pins it. Once pushed, it is a history rewrite
and `protocols/history-archive.md` runs first.

```sh
uv run qm branch --base main --head <branch>
```

This reports the merge-base, the commit and file counts, the authors, and any
commit that also lives on another branch. Paste its output into the pull
request body. A branch cut from the wrong parent passes every other check,
because those measure the branch and not where it came from.

```sh
uv run qm private-names --strict
uv run qm leaks
```

These two read a machine — the host's list of private repositories, and the
shapes of a person's name or a shared-conversation link — so they are kept off
the runner on purpose (`.github/workflows/registries.yml` says why) and no
gate will run them for you. They run here, before anything is pushed, because
a page pushed without them can carry a private repository's name into a public
artifact, and the first run of this runbook did exactly that and had to be
repaired after the push. `--strict` turns "no source of private names was
available" from a pass into a failure; a machine without the host's list has
not checked anything.

*Verify:* the signature column is uniform `G`, the trailer column is empty,
`private-names` reports clean (not unverified), `leaks` exits zero, and the
`qm branch` output names the merge-base you expected. Commits listed as shared
with another branch are explained in the pull request, or the branch is re-cut.

## Step 4 — push, and open one pull request per repository

`handbook/async-contract.md` §1: one open pull request per repository, per
contributor. It is a sequencing constraint — the puzzle of two pull requests
that must merge in an order is what it prevents — so the leftover branches in a
repository are landed one at a time, each cut from the `main` the previous one
produced.

```sh
uv run qm slot --repo <owner/name>        # the slot is free, or names what holds it
git push -u origin <branch>
gh pr create --base main --head <branch> --assignee <who-asked> \
  --title '<what it decides>' --body-file <body>
```

Assign the person who asked for the work. Request no reviewer — reviewers are
named at the tag. The body states decisions and carries the `qm branch` output;
a question in it hands the drafting back. A record's `Pends on` row is the one
place an open question belongs, and it names something the organisation has
not settled rather than something you have not.

In this repository, a branch based on `project/<name>` opens *into*
`project/<name>` and never into `main`; `project-seed/ci/check_pr_base.py`
refuses the wrong direction, and each such branch holds its own slot.

*Verify:* `gh pr view <number> --json isDraft,reviewRequests,assignees` shows
not a draft, no reviewers, and the assignee you set. Draft means unfinished;
a green pull request left in draft is a change that never reached `main`.

## Step 5 — audit what a green pull request state cannot see

A pull request's checks measure what runs *on a pull request*. Several classes
of failure are outside that, and every one of them has produced a red `main`
from a green merge here. Audit each before Step 6, per repository:

- **Merge-only workflows.** A job triggered on push to `main`, on a tag, or on
  a release has never run against this branch. Find them and run their steps:

  ```sh
  grep -ln 'branches:.*main\|^\s*tags:\|^\s*release:' .github/workflows/*.yml
  uv run --extra preflight qm preflight        # here; a project runs the seed runner in place
  ```

  A deploy step that needs a hosting setting nobody has enabled is a repository
  setting rather than code, and the audit names it for a person rather than
  fixing it.
- **Determinism gates.** A tag-time gate that asks whether committed artifacts
  match a fresh run fails on a branch whose artifacts were generated once and
  edited since. Regenerate and diff before the merge, not after the tag.
- **Cross-repository pins.** A submodule gitlink is a commit a consumer must be
  able to fetch. `uv run qm pins` in each consuming repository reports any pin
  that resolves on this disk and nowhere else — the shape a local-only
  perspective commit produces when a working tree moves the gitlink under it.
  Do not push such a pin; it breaks every consumer's submodule update at once.
- **Environment-bound tests.** A suite that reads a variable this machine sets
  and the runner does not measures this machine. Run it once with the
  inherited environment and once with that variable unset, and report which
  you quoted.
- **Checks that pass by luck.** A skip is not a pass and an empty assertion is
  not a pass; both report green. `pytest -rs` lists what was skipped, and a
  glob that matched no files is found by counting what it matched.

`uv run qm gates` lists every gate in this repository with what each one
cannot see; that column is the checklist for this step.

*Verify:* for every item above, either the command ran and its output is in the
pull request, or the item is named as unreproducible with the reason. "CI is
green" is a claim about the pull request event and nothing else.

## Step 6 — merge, stage by stage, with a person approving each

Every merge is a merge commit — never squash, never rebase — because the signed
history is the audit record and a rewritten branch breaks any pin pointing at
it. A person approves each stage in the session; the approval is not a review
request on the host and is not recorded there.

```sh
uv run qm merge                                   # every open pull request you hold, live, and whether each is READY
uv run qm merge --repo <owner/name> --pr <number> # re-verify one, and stop
uv run qm merge --repo <owner/name> --pr <number> --yes   # the act, refused unless that reading says READY
```

The reading is the default and mutates nothing; the act is one flag away and
uses the same definition of ready, so a listing cannot say READY where the act
would refuse. The route answers a squash or a rebase flag with the reason
rather than with the operation.

Order the stages by dependency: a repository whose pull request pins another's
branch merges after the branch it pins. The constitution's own pull request
merges last, because every other repository's gates read it. Re-verify the live
state immediately before each merge rather than trusting the survey from Step
5 — a pull request can lose its checks, or gain a conflict, in the minutes
between.

`main` asserts nothing. The merge ratifies no record and releases no project;
the two human gates are ratification and the version tag, and this step passes
neither. Every record stays `DRAFT` for a person.

*Verify:* `git log -1 --format=%P origin/main` shows two parents, and
`gh pr view <number> --json state,mergeCommit` reports `MERGED` with that
commit. The slot in that repository is free again: `uv run qm slot` says so.

## Step 7 — retire the handoff pages whose work landed

`handbook/handoffs/README.md` carries the routing rule: **delete a page when
its work lands**; the method that outlives it belongs in a runbook, not there.
A page describing delivered work as pending is worse than no page, because a
session picks it up and re-derives a state that no longer exists.

For each page in `handbook/handoffs/`:

- its work is on `main` → delete the page;
- part of its work is on `main` → move what remains into the one page that
  stays, and delete the rest;
- its work is blocked on a person → it stays, and says on whom.

Then refill the queue table in `handbook/handoffs/README.md`, ordered by
expected delta, with the leftover branches Step 2 found independent, the pull
requests a person chose to hold, and the decisions that need one. Stamp it
with the commit each repository is at.

*Verify:* every page the table links exists, every page in the directory is in
the table, and no row describes as pending a pull request that
`gh pr view` reports `MERGED`.

## Step 8 — regenerate the generated documents

The status documents and the dashboards rendered from them are stale the moment
`main` moves, and a stale number delivered with a date looks checked.

```sh
uv run qm docs generate
uv run qm docs check
```

`handbook/generated-documents.md` indexes what each command touches, with the
refresh command and the staleness budget per document. The regeneration rides
the commit that closes the cycle, so the next session reads a document that
agrees with the `main` it opens.

*Verify:* `uv run qm docs check` exits zero, and `git status --short` shows
only the generated paths that page names.

## Step 9 — reload for the next cycle

The merge leaves the local stage behind. `test` was not advanced by anything
in Steps 1–8, and `main` now holds what `test` held plus the reconciliation.
Whether to advance it — reset it onto `main`, or leave it where it is — is the
decision `records/DRAFT-a-stage-is-recorded-and-main-receives-releases.md`
§1a makes: `test` is rewritable, and rewriting it is an ordinary operation
there and nowhere else. It is not an automatic reset, and this page does not
make it one.

```sh
git rev-list --left-right --count test...origin/main    # how far apart, both ways
```

A worktree another session cut from the old `test` must be rebased onto the
new `main` before it opens anything; say so in the handoff rather than doing
it, because that session is live.

*Verify:* the handoff that closes the cycle states where `test` was left and
why, so the next `uv run qm estate` does not report it as stranded work.

---

## What the first run of this found

Exercised end to end across the estate on 2026-09-20. The findings that none
of the pages then in force predicted:

| Finding | Where |
|---|---|
| A local branch named `test` held the organisation's real work in more than one repository, indistinguishable from scratch | Step 2 |
| The consolidation folded most leftover branches by content without making their commits ancestors of `main`, so an ancestry check called them independent | Step 2 |
| The constitution's own pull request needed reconciling against gates added after it was cut, several times in one join | The shape of the problem |
| A working tree moved a submodule gitlink to a commit on no origin ref, and only the pins check could tell | Step 5 |
| A deploy job on `main` was red for a hosting setting, invisible to every pull request check | Step 5 |
| Handoff pages described the landed work as pending until they were retired | Step 7 |

## What this page does not authorise

Ratification, deleting a branch, force-pushing anything a submodule pins,
advancing the stage branch, or merging a stage a person has not approved. The
survey and the census take no `--delete` flag by design; deletion is a person's
act, repository by repository, after `uv run qm branches` in that repository
has said what it costs.
