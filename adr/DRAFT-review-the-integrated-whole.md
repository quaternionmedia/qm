# ADR-XXXX — Apothecary is reviewed as one integrated whole, walked as a demo from its README

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-10-15 |
| **Pends on** | The trial: the first review walked this way, of apothecary's `build/integration`, completed by the owner and recorded on its pull request as §4 says. Its outcome decides whether this record is ratified, revised, or proposed to the org. |
| **Checked against** | apothecary `build/integration` at `48bfbaa` (every open pull request merged onto `build/timeless-docs`, #54 included); qm at this project's pin `20e00bd` for the async contract and the version-tags record, and qm `main` at `df1cb51` for the async contract as it stands there |
| **Established by** | the stacks merged with `git merge-tree` and then `git merge`; the commands `apothecary test all` runs, run on the merged tree with each skip's reason; `.github/ci/check_integrates.py` run against the repository's open pull requests, before and after their branches were fixed; `tests/test_readme_map.py` seen to fail on a browser test with no row, and on each failure made in a copy of the README |
| **Tools** | Drafted with Claude Code (Anthropic); the person who ratifies it is its contributor of record |

## Context

Apothecary's work lands as a stack of pull requests, each based on the one
below it; the documentation sweep adds three more stacks on its top. Each
pull request's CI runs at that pull request's own head. A test that passes
there is evidence about a tree that exists nowhere once the pull requests
above it merge, and a review of one pull request in the running app is a
review of a state nobody will run.

Both were seen on this stack. The sweep's branches were cut before a fix to a
browser test that failed in CI (the Machine test waiting on a rescan's
promise), and their CI was green without it. Two stacks each stated a true
paragraph about how a screenshot is taken, and the two contradicted each
other in `tests/e2e/README.md`; that showed only when they were merged into
one tree, where neither paragraph alone held. A walk of the bottom pull
request in the app took a worktree, a server, fixtures and its own test run,
for a tree that the next pull request's merge leaves behind.

Merging every open pull request in order found three that could not be
merged. The page stack's top conflicted with the docs stack in that
paragraph; once its branch took the docs stack's words, the pull request
carrying both stacks conflicted with the fix and took it in turn; and a
pull request from a second contributor, based low in the stack, conflicted
with the network guard's docstring and the viewer's imports. Its browser
tests skip on any machine without a venue's files, which the repository
does not hold.

The org records settle where review sits and say little about its unit. The
async contract makes a pull request an audit record, assigned to the person
who asked and reviewed by nobody; at this project's pin it leaves draft "after
their own testing", and on the org's `main` the human gates are ratification
and the version tag. *Version tags are claims* §2 has a tag assert that a
human reviewed the change set, tested it by hand against its real runtime, and
that deterministic automated validation passed; §3 counts a skipped test as
absent; §6 puts all three in the tag's annotation. *What Apothecary's `v0.0.2`
asserts* §1 asks for one demonstration, written by the run that asserts it.
None says what a person looks at between tags, and on this project that is
where the stack accumulates.

## Decision

Apothecary is reviewed as one integrated whole, walked as a demo from its
README.

1. **The unit of review is the integrated whole.** Every open stack is merged
   into one tree on an integration branch above them (`build/integration`),
   and a person reviews that tree, never a pull request at its own head. Each
   pull request stays the audit record of one change, says what changed and
   why, and merges bottom first, without a review of its own, once the whole is
   approved.
2. **Every test passes on the whole.** The full suite, the unit tests, the
   walkthrough's doctests and every browser test (`apothecary test all`),
   passes on the integrated tree. A test that passes only at the head that
   introduced it holds nothing about the code that ships. Each skip is listed
   with its reason and counts for nothing, as *Version tags are claims* §3
   counts it. A test that skips for want of something the repository does not
   hold -- a venue's files, a board -- is named in the approval with what it
   needs, and its row in the map says so.
3. **The README is the map a reviewer walks.** Its section *What it does, and
   how to see it* has one row per thing the code does: where to see it under
   `apothecary serve --demo`, the tests that hold it, and the walkthrough page
   its run writes. `tests/test_readme_map.py` fails when a row names a test or
   a page that is not there, when a browser test is in no row, or when a page a
   run writes is in no row naming that run. What the code does is stated there
   and nowhere else; a pull request's body says what it changed.
4. **A person walks the map on the running whole and approves it once.** The
   approval names the integration commit, the rows walked, what was tested by
   hand against real hardware (the bench checklist, `docs/bench-checklist.md`),
   and the suite's result with its skips. It is recorded on the integration
   pull request. A tag cut at that commit carries the same three in its
   annotation (*Version tags are claims* §6).
5. **A conflict makes a pull request ineligible to merge, and it is fixed in
   that pull request's branch.** The open pull requests merge depth first from
   their base, oldest first on each. One whose head conflicts with those before
   it is not eligible, and every pull request stacked on it waits on it
   (`.github/ci/check_integrates.py`, which `integrates.yml` runs on every pull
   request). The fix is made in its own branch -- its text brought to agree
   with what it meets, or what it conflicts with merged in -- so that it merges
   as it is; the integration is then built again from the fixed branches, and
   the review goes on. When the branch is another contributor's, the
   integration carries the resolution so the walk is not held up, and the pull
   request stays ineligible until its own branch takes it.

## Consequences

- A review is one walk per integration rather than one per pull request, and
  it looks at the code that ships.
- The integration branch's pull request carries every stack's commits until
  the stacks merge, and then only its own: the resolutions and the README.
  That diff is large while the stacks are open. Accepted: nobody reviews it as
  a diff, and the map is what is reviewed.
- The full suite runs on the integrated tree for every integration; its time
  is what `apothecary test all` reports, and a session runs it in the
  background.
- Every browser test needs a row, and every page a run writes needs its run in
  a row. A new browser test with no row fails the map's check; the failure is
  the reminder, and its cost is one line of the README.
- A row's "See it" runs under the demo's simulated printer and devkit. What
  only hardware shows stays with the bench checklist, and §4 names it as the
  manual test, so the map never claims what the demo cannot show.
- Per-pull-request CI keeps gating each audit record. It stops being the
  evidence a reviewer reads.
- A fix to one branch can make the next one conflict: a branch that carries
  another stack's commits meets the fix as a change to its own text. The
  check finds it on the next run, and the fix moves up one branch at a time.
- The check judges the open pull requests as they stand when it runs. A pull
  request pushed to later can leave an earlier verdict stale until that pull
  request is pushed to or its check is run again; run with every open pull
  request at once, the check judges them all.
- This is apothecary's own rule. It adds a review of the whole where the org
  records require no review of a pull request, so it tightens and relaxes
  nothing.

## Alternatives considered

1. **Review each pull request at its own head, in the running app.** Rejected:
   each walk is of a tree that exists nowhere after the pull requests above it
   merge, and a test passing at that head says nothing about the code that
   ships. It also costs a worktree, a server and a suite run per pull request,
   which on a stack this deep is the review never finishing.
2. **Review only at a version tag, and nothing in between.** Rejected for this
   project, though it is the org's default: the stack grows faster than tags
   are cut, and between tags no person looks at the integrated code at all.
   This record brings the tag's review to each integration and leaves the tag's
   gate as it is.
3. **One integration pull request in place of the stack.** Rejected: each
   change keeps its own audit record and its own reason only if its pull
   request merges as it is. The integration pull request records the review,
   not the changes.
4. **A REVIEW.md written for each integration, beside the README.** Rejected:
   two documents saying what the code does are two accounts of one thing, and
   one of them goes stale, which is the reason *What Apothecary's `v0.0.2`
   asserts* gives for one demonstration.
5. **The walkthrough alone as the map.** Rejected: its pages are the loops, two
   demonstrations and the library's tour, and most browser tests have no page.
   The map links the pages and names the rest.

## Revision triggers

- The trial in `Pends on` completes, or is abandoned before the walk ends.
- An integration needs a conflict resolved with new code rather than a choice
  of text, which is a change of its own rather than a fix to agree.
- A pull request stays ineligible for longer than one integration because its
  branch is another contributor's (§5's last sentence), so the rule has a cost
  to someone outside the session.
- `apothecary test all` on the integrated tree fails where every stack's own CI
  passed: evidence this review catches what per-head CI cannot, which the
  record should then cite.
- A defect reaches `main` that a row of the map shows, meaning the walk or the
  map missed it.
- A row needs hardware the demo cannot simulate, so the map and the bench
  checklist overlap.
- A second project adopts the same review, or *Version tags are claims* is
  ratified with a different unit of review: the rule is then proposed to the
  org, or brought in line.

## Amendments

*None.*
