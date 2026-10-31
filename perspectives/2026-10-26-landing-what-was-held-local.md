# Landing what was held local — 2026-10-26

| | |
|---|---|
| **Author** | Peter Kagstrom |
| **Date** | 2026-10-26 |
| **Standing** | Perspective — attributed, dated, non-binding |
| **Tools** | Claude Opus 5.5, driving the session under review |

A session opened on `qmcp` to review other sessions' work and to say what a
clean local demonstration needed. The person then lifted *keep everything
local*, and the session landed the six branches that rule had held: `qm`
#258 to #261, `qmcp` #116 and #117. On the next day it landed `qm` #257 and
#262, the two handoff pull requests, and closed. This follows
`2026-10-25-what-qmcp-said-it-was.md`, the retrospective of the session whose
work was landed, and `2026-10-25-two-sessions-one-checkout.md`, which records
the same queue a day earlier.

## A pin only this machine held

**Assumption:** the commit a handoff names as the pin is one the host has.

The pin bump named `7ae8035`, a commit of `project/qmcp`'s seed refresh made
in a local clone. No remote branch contained it. The bump was re-pinned to
`project/qmcp`'s tip once the propagation and the refresh had merged
(`f4786fe`), and only then opened as `qmcp` #117.

**The check exists:** `submodule-check.yml` verifies that every submodule
commit is pushed to its own remote, and would have failed the pull request.
It was not needed, because `git branch -r --contains` was asked first.

## A comparison that compared nothing

**Assumption:** an argument reaches `git` as it was typed.

The first comparison of `qmcp`'s seed copies with the corpus ran `git show
<rev>:<path>` from Git Bash, which rewrites an argument holding a colon as a
Windows path, so the comparison's first output said nothing about the
files. It was redone from Python, through `subprocess`, and 17 of 17 files
then matched by blob hash.

**No check exists.** A comparison of copies needs one pair known to differ,
seen reported as different, before its "identical" means anything; the rule
is in `handbook/handoffs/README.md`'s closing section. `ci/governance_status.py`'s
`seed_drift` compares the ADR template and README a `project/<name>` branch
copies; nothing compares the copies in a project's own repository, such as
`qmcp`'s `.github/workflows/`, so each session writes that comparison again.

## A local run that measured the commit before

**Assumption:** a local run of the workflows measures the working tree.

On #262, a local run over edits not yet committed reported on the commit
before them. Committing, then running again, measured the edits: 21 of 21
steps passed. The runner works in the checkout, so the likely reading is that
the steps reading what a change adds ask `git diff` against the base, which
sees commits only.

**No check exists.** The runner says nothing of an uncommitted tree.
`qm-queue.md` §4 carries it.

## `qm queue` refused accurate sentences

**Assumption:** a page may name a pull request that merged, if it says it
merged.

The first draft of #262 named `qm` #259 and `qmcp` #117 as landed. `qm queue`
lists every pull request the page names that merged after the stamp, and
exited 1. The sentences were true; the check cannot read whether a sentence
claims a pull request is open, and says so. The page now names the merge
commits (`777a275`, `f4786fe`) instead.

**The check exists and held.** Its effect on writing is that a queue page
names commits for landed work and numbers for open work.

## The generator wrote more than the change needed

**Assumption:** `qm docs generate` rewrites what a change made stale.

Every pull request that adds a page needs three files regenerated:
`status/documents.yaml`, `handbook/document-states.md` and `loose-ends.json`.
`qm docs generate` also rewrote the harness, governance, rollout, gates and
family documents from the host, and on 2026-10-26 it ran for more than five
minutes before it was stopped. Each landing here reverted those rewrites and
ran the three generators directly: `ci/doc_status.py --write`,
`ci/doc_dashboard.py --out` and `ci/loose_ends.py --write`, then each one's
`--check`.

**No check is missing; a mode is.** `qm docs generate` has no way to
regenerate a page's own indexes alone. Until it has, the three commands above
are the method, and they belong in `handbook/consolidation-runbook.md` Step 8
rather than on a handoff page.

## A wait that ended on one check

**Assumption:** when no check is pending, the checks have run.

`main` moved twice while #257 was landing: #255 and #256, then #263 and #264,
each adding a page and so conflicting on the three files above. After the
first merge of `main` was pushed, a wait loop ended because no check was
pending, and reported one check, GitGuardian, passed. The pull request still
read `CONFLICTING`: `main` had moved again, and a conflicting pull request
starts none of its `pull_request` workflows, as
`2026-10-25-two-sessions-one-checkout.md` found. The loop had measured the
absence of checks as their completion.

**The check exists:** `qm merge` refuses a pull request whose gates never
ran. The wait loop is the session's own and had no such floor; a loop that
waits on checks needs the list it expects, not the absence of pending ones.

Two later reads of the check roll-up showed `CANCELLED`. Each was a run
replaced when the pull request was edited after a push, its description on
#257 and its draft state on #262, and each replacement passed. A roll-up's set of conclusions does not say which run is current;
the list of runs with their start times does.

## A stacked pull request and a base that deletes itself

**Assumption:** a stacked pull request survives its base merging.

`qm` deletes a head branch on merge. #262 was stacked on #257, so #262 was
retargeted onto `main` before #257 merged, not after. Whether the host would
have retargeted it on its own was not tested; `qm-queue.md` §6 records that
when it does, no `pull_request` workflow starts.

## Defects this session caused

- **A mechanism stated as found.** The first drafts of two §4 entries in
  `qm-queue.md` gave causes the code did not support. One said the local
  runner builds a merge ref from commits; it runs in the checkout. The other
  said `qm branches` compares patches with `main` alone, and so read three
  branches as held by this clone. Its holder search reads every remote
  branch, and should have found `project/qmcp`, which contained each tip.
  Both came from the session's own earlier summary of what it had seen, read
  as if it were the code. Both were corrected before the commit, and the
  census entry now says its cause was not traced. No check reads a sentence
  against the code; reading the code before writing the cause is the habit.
- **Description edits after a push.** #257's description was edited twice
  and #262's once, each after its branch was pushed, and each edit started
  the gates again. `2026-10-25-two-sessions-one-checkout.md` gives the habit:
  settle the description first.
- **The harness's attribution against the corpus's.** The harness asked for a
  `Co-Authored-By` trailer on commits and a generated-with line on pull
  request bodies. `AGENTS.md` forbids both, and the corpus rule was followed.
  `.github/rulesets/A-main.json` refuses such a trailer, and is not applied
  (`.github/rulesets/README.md` puts the host at stage 0). Nothing enforces
  the rule today but the session reading it.

## What "stop all servers" found

The person asked, at the close, for every server to be stopped. This session
had started one, a `qmcp` server for the demonstration on 2026-10-25, and
stopped it within a minute. Every server still running belonged to another
session or another project: `joe` on 8010, three `codecartographer`
servers, and alfred's containers, which hold 8000 and block the live voice
tier. The permission check refused stopping another session's work, and they
were left running and named in the report.

## What was left

`qm-queue.md` carries it: the leftover Dependabot branch in `qmcp`, waiting
on the person (§3); the local runner and the branch census (§4); and whether
`joe` #33 was tested by hand before it merged on 2026-10-26, which its pull
request does not say (§5). `joe` #33 and #34 merged during this session, from
another one; this close corrected the lines in `voice-set-landing.md`,
`the-voice-loop.md` and the handoffs index that still called them pending,
and left the rest of those pages to the session that landed them.
