# A rename closed a pull request -- 2026-10-19

| | |
|---|---|
| **Author** | Peter Kagstrom |
| **Date** | 2026-10-19 |
| **Standing** | Perspective — attributed, dated, non-binding |
| **Tools** | Claude Opus 5.5, driving the session under review |

apothecary's viewer moved its windows to GoldenLayout, was reviewed once more,
and its stack of pull requests went to its origin. One step of that push closed
a contributor's open pull request. This page is why: what was assumed, what it
cost, and for each finding the check that would have caught it and whether that
check exists. The state the push left is in apothecary's origin-operations
ledger; what to do about the closed pull request is a decision for a person,
and is not made here.

## A branch renamed under an open pull request closes it

**The assumption:** renaming a branch through GitHub's API
(`POST /repos/{owner}/{repo}/branches/{branch}/rename`) carries every open
pull request on that branch across to the new name. It does for a pull request
whose *base* is the branch, which is retargeted. A pull request whose *head* is
the branch is not carried: apothecary#54, from a branch named for the venue its
first version described, was CLOSED the moment the branch became `theatre`,
its head reference gone (`headRef: null`), its last commit unchanged.

The rename was not in the reviewed plan. The ledger the push followed said to
force-push the cleaned commit to the existing branch and retitle the pull
request; the rename was added at the moment of the push, to take the venue's
name off the head reference too, judged as reversible and not checked. Two
things made it worse than a mistake on a branch of one's own: the pull request
was another contributor's, and the repair -- the rename reversed, the pull
request reopened -- was refused by the session's own guard on writes to an
external system, after the original rename had been let through. So the
repair waits on a person, which is where it should have started.

**The check that would have caught it:** none exists. Three would have:

- **An origin operation not in the reviewed ledger is asked before it runs.**
  A rule, not a script: the ledger was reviewed and the improvised step was
  not, and the improvised step is the one that went wrong.
- **A branch that heads an open pull request is never renamed or deleted.** A
  script can hold this: given the branches an operation renames, deletes or
  force-pushes, list the open pull requests whose head or base each is, and
  refuse a rename or a delete of any head. It is a few lines over `gh pr list
  --json headRefName,baseRefName`, and it belongs beside the seed's
  `check_one_pr.py`.
- **A claim about a host's behaviour is checked against the host's own
  documentation before it is acted on** -- the corpus's item 9, establish a
  fact before asserting it, applied to an action rather than a sentence. The
  belief that a head is carried was never stated aloud, which is why nothing
  checked it.

## A configuration switch did more than its name says

**The assumption:** turning a stack's close button off in GoldenLayout's
header configuration (`close: false`) hides the button. It also marks every
stack as not closable, and a window alone in its stack then cannot be closed by
its own tab's button either. The browser tests found it: every test that
closed a lone window failed. The button is hidden by the page's stylesheet
instead.

**The check that would have caught it:** exists -- the browser tests, which
close windows by their tabs as a person does.

## A method overridden for one path was also another path's

**The assumption:** overriding the world's stack's `createHeaderConfig`, so a
window dropped beside the world is made with a tab, changes only drops.
GoldenLayout also asks that method when it saves the layout, so the world was
saved with a header, and every reload from a remembered layout gave the world a
tab and a maximise button. Seven walkthrough pictures taken after a reload were
committed with that tab in them. It was seen in the review's demo tab, not by a
test: no test looked at the world's header after a reload. The override now
applies only while a drop is made, a remembered layout lays the world out
without a tab whatever it says, and two tests check the world's header after a
reload and after a drop on it; both go red with the override as it was.

**The check that would have caught it:** exists now. It did not before, because
the tests checked what the change was for (a dropped window has a tab) and not
what the change touched (everything that calls the method).

## A difference was attributed before it was explained

**The assumption:** pictures that differed from the committed ones, written
after the last commit, were written by a reviewer told not to run the suites.
They were restored to the committed ones on that reading. A clean run of the
whole suite in a worktree of its own then wrote the same seven differences:
the committed pictures were the stale ones, taken while the world's tab was
live, and the restored copies were the fix showing. They were committed from
the clean run.

The corpus's item 10 says to name the ordinary cause before the interesting
one. The ordinary cause here -- the tree's own pictures out of date with a
change made since they were taken -- was available and was not tried first;
the interesting one, someone else's run, was.

**The check that would have caught it:** exists, and was not read first --
`tests/e2e/picture_drift.py` names every picture past its tolerance; looking at
one of them against the committed one took a minute and settled it.

## A rebuilt stack had lost an ancestor

**The assumption:** the stack rebuilt the day before -- every branch re-cut to
drop one commit -- still stood each branch on the one below. It did not:
`build/scene-not-mirrored` no longer held `build/grid-and-fit`'s second commit,
whose pictures its own first commit had taken again. Its pull request, opened
as planned on `build/grid-and-fit`, would have merged with a conflict in every
one of those pictures. An ancestry check over the whole chain before the push
found it; a merge that keeps the branch's tree records the ancestry, and the
five branches above were replayed onto it, their trees unchanged.

**The check that would have caught it:** none standing. The chain was checked
by hand, once, because the push was about to happen. It is a loop of `git
merge-base --is-ancestor` over the ledger's branches, and it belongs in the
push procedure the ledger describes.

## Upstream added up what lies on top of itself

**The assumption:** GoldenLayout's minimum window sizes, once set by the keys
it reads (`defaultMinItemHeight`, `defaultMinItemWidth`), hold for each window.
At a splitter's drag, GoldenLayout 2.6.0 adds up the minimum of every tab in
the stack beside it, though a stack's tabs lie over one another: Site's five
tabs could not be dragged below five tabs' worth. A test's drag that stopped
short found it; the vendored copy carries a one-function fix, recorded in its
README so an update carries it over.

**The check that would have caught it:** exists -- a browser test that drags a
splitter to a stated height and waits for it.

## Reviews that stopped at a limit

Three reviewers ran in parallel over the change, each read-only on its own
slice, and all three stopped part way when the account's rate limit was
reached. One finding survived, from a reviewer's last message: with every
window but the world closed, no window could open again. It was real, fixed and
tested; the rest of their ground was covered by one reader instead of three.
A reviewer that writes each finding to a file as it finds it loses nothing to a
stop; one that reports at the end loses everything but its last line.

## What would prevent the first finding

In order of how much each would have taken off:

1. **The ledger is the plan.** Origin operations run as the reviewed ledger
   lists them; a step added at push time is asked first, with what it does to
   whom stated -- above all a step on a branch or a pull request that is not
   the operator's own.
2. **A guard on destructive host calls.** The session's permission settings ask
   before a branch rename or delete, a pull request's state change, or a force
   push, every time, rather than leaving it to a classifier that let the rename
   through and refused its repair.
3. **A head is never renamed.** A check beside `check_one_pr.py`, run before an
   operation, refuses a rename or a delete of a branch that heads an open pull
   request.
4. **Behaviour is read, not assumed.** A host's behaviour that an action depends
   on is read from its documentation, or tried on a branch of the operator's own,
   before the action.
