# Two sessions, one checkout — 2026-10-25

| | |
|---|---|
| **Author** | Peter Kagstrom |
| **Date** | 2026-10-25 |
| **Standing** | Perspective — attributed, dated, non-binding |
| **Tools** | Claude Opus 5.5, driving the session under review |

This follows `2026-10-25-the-label-was-not-the-content.md`. It covers the
same session's last hours: three corpus pull requests merged, and a second
close of the session, made while another session was working in the same
`qmcp` checkout.

## A description edit restarted the gates

**Assumption:** editing a pull request's description changes its text and
nothing else.

#253's description was corrected after its branch was brought level with
`main`, and only then were its checks read. Four of them (`leaks`,
`registries`, `slot` and `timeless`) had started again on the `edited` event
and were still running at that one read, so the merge waited for the person
to ask a second time. `qm-queue.md` §6 already says this: a body edit fires
`edited`, and `qm merge` refuses a pull request whose `slot` run is pending.

**The check exists and held:** the merge was not made on a partial set. The
habit it asks for is to settle the description before reading the checks.

## Every page added conflicts with every other

**Assumption:** two pull requests that add different pages merge
independently.

A pull request that adds a governed page also rewrites three generated
files, `status/documents.yaml`, `handbook/document-states.md` and
`loose-ends.json`, whose counts and timestamps every such pull request
changes. When #244 and #245 landed, #251 and #253 both conflicted.

A conflicting pull request also runs none of its `pull_request` workflows,
because there is no merge ref to run them on. Only the GitGuardian app
reported, so the checks list read as one green item rather than as a
conflict. Each branch was brought level by a merge of `main`, taking `main`'s
generated files and rebuilding them, never by merging them by hand.

**The check:** the host's mergeability field (`DIRTY`) says it. Nothing
turns a missing set of workflow runs into a failure that a reader of the
checks list would see.

## Another session was working in the same checkout

**Assumption:** the checkout a session starts in belongs to that session.

Another session working in the same `qmcp` clone:
- switched it to its own branch;
- moved the `governance/qm` submodule to a merge of `main` into
  `project/qmcp` that exists only on that machine, at a detached HEAD;
- rebuilt that merge once this session's pull requests had landed.

This session saw it only when `git status` showed a branch it had never
made. Two consequences followed.

- **The command changed under the session.** This session ran `/handoff`
  twice. The second run asked for a sweep of every handoff page that the
  first had not. `.claude/commands/handoff.md` is one of the seed files the
  other session's pin bump copies again, and the checkout was on that
  session's branch. So a session's procedure depended on which branch another
  session had checked out.
- **The object store is shared.** This session added and removed worktrees
  in the submodule's repository while the other session's merge existed there
  only at a detached HEAD. Nothing here moved that HEAD. The checkout then
  moved anyway: at 21:24 the `qmcp` clone went back to `main`, and the
  submodule followed to `235708c`. From then on the merge (`c1fd0a4`,
  `7ae8035`) was on no ref **in the submodule's repository**. The other
  session's `qmcp` commit still pinned it, but a gitlink keeps nothing alive.
  This session created no ref for it, because the work was not this
  session's to name, and told the other session directly.
- **A defect this session caused, in reporting that.** The message, the
  queue entry and the first version of this page all said the merge was
  reachable "only from that machine's reflog". The other session answered
  that a separate `qm` clone on the same machine held both commits on
  branches all along. This session had searched one repository and stated
  the result for the whole machine. The other session then named the second
  commit in the submodule too, so its pin checks out.

  **The check:** none. `for-each-ref --contains` answers for one
  repository, and nothing lists every clone that shares a remote.

**The check:** none detects a second session in a working tree. `qmcp`'s
run-file identifies a serving process, not a checkout. A session in a
worktree of its own would not have shared the branch or the commands. The
object store is shared by every worktree of a repository, so a worktree
removes the first risk and leaves the second. An unpushed commit at a
detached HEAD is safe from another session only once it is on a branch.

## What this close did instead of a page

The `/handoff` asked for a handoff page for the other session's work. That
work was changing minute by minute. In one hour its unpushed pin bump was
committed, reset and recommitted, and its submodule merge was rebuilt. A
page stating it would have been out of date before its pull request
merged.

So the handoff is two things: a state entry in `qm-queue.md` §4, stamped to
the minute, and a message sent to that session directly. The page that
outlives the work is the queue's.
