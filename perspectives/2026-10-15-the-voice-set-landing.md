# Landing the voice set — 2026-10-15

| | |
|---|---|
| **Author** | Peter Kagstrom |
| **Date** | 2026-10-15 |
| **Standing** | Perspective — attributed, dated, non-binding |
| **Tools** | Claude Opus 5.5, driving the session under review |

The voice set -- `vox`, `qmcp` and `joe`, approved as one on 2026-10-12 --
was landed in the review page's order, one merge asked for at a time, until
`joe` #33, where testing by hand takes over. The state is in
`handbook/handoffs/voice-set-landing.md`. This page is why the landing took
the shape it did: what was assumed, what that cost, and for each finding the
check that would have caught it and whether that check exists.

## A body true on its branch is not true after `main` is merged in

**The assumption:** a stacked pull request's body, true on the branch it was
written on, stays true once `main` is merged into it, apart from its stated
base. The `qmcp` stack from #61 up was cut without #58, which added an open
question to the approval loop and landed first. Each merge of `main` brought
that open question into a branch whose body made claims about every closed
question or every phrase: #68 that each closed question is hinted, offered and
repeatable; #73 that every closed question can be answered before it ends; #74
that every phrase the loop acts on is declared once, in the vocabulary. After
the merge, each claim was false for the open question's read-back, and every
check was green -- a test asserts what was built, not what a body says about
code that arrived afterwards.

#68's body went further: it promised that the open question would take the
same three lines when it met #58 on `main`, while the review page put that
convergence after the set. Two documents, both read, disagreeing. The
disagreement was taken to a person, who chose to make the claim true in the
pull request, and then made that a standing rule for the rest of the landing,
which saved asking twice more.

**The check that would have caught it:** none exists. Reading each body
against the merged tree is what found all three. The semantic part -- does
the code do what the prose says -- has no mechanical test; a narrower part,
naming every caller a claim covers, might.

## Retargeting moves the base, and leaves the body behind

**The assumption:** moving a stacked pull request onto `main` is the whole of
moving it. Every stacked body carried a Branch block and a line naming the
pull request beneath it, and both went stale the moment it moved. Some forty
bodies were rewritten, each by hand, from `check_pr_base.py`'s report against
`main`. A sentence in one body -- "the command that wraps it is not on this
branch" -- became false only because `main` brought that command in.

**The check that would have caught it:** none exists. `check_pr_base.py` runs
in CI in refuse-only mode and does not read the body. A check that a body's
Branch block names the pull request's actual base is mechanical, and is the
next piece of work here.

## A refusal from the host is not a conflict

**The assumption:** when the host refuses to merge `main` into a branch, the
two conflict. `qmcp` #82 had merged three other pull requests' branches while
they were open, which left it three merge bases with `main`. The host refused;
git merged it locally without a conflict. Elsewhere the refusal was a real
conflict, and the demo branch, which had merged the same pairs before, held
the reference resolution each time -- comparing the resolved file with the
demo's caught one ordering that would otherwise have been a guess.

**The check:** trying the merge locally. It exists as practice, not as a
tool.

## A tool's report is not the state

**The assumption:** `qm merge`'s report describes what happened. In `joe`,
which deletes a branch when its pull request merges, the host retargeted the
pull request stacked above before `qm merge` tried to; `qm merge` then
reported that it could not retarget and had left the branch in place. The
branch was gone and the stacked pull request was open on `main`. Reading the
pull request's base, rather than the message, showed it.

**The check that would have caught it:** none exists. `retire_branch` could
read the stacked pull requests' bases again after a failed retarget, and
report what it finds. That is a small change to `ci/merge_review.py`.

## Defects the session made

Each was found before it reached a merged branch; each is written the way a
found one would be.

- **A script silenced `gh pr ready`** and printed "marked ready" for a pull
  request still a draft (`qmcp` #62). Reading `isDraft` afterwards showed it.
  The script now asserts the draft flag after marking.
- **A wait counted nine checks where a run had eight**, and sat idle until
  stopped (`qmcp` #70); a `slot` run cancelled by a newer run on the same head
  then read as a failure (#72). A cancelled run now counts as superseded only
  when the same check succeeded on that head.
- **A body draft said `_ask_open` matched the demo branch line for line**,
  after the session's own commit on #68 had changed it. Re-reading the draft
  against the file before pushing caught it.
- **A commit was made before its lint result was read**; the new test line
  ran past the length limit. It was folded into the commit before the push.
- **An overview quoted a commit's first line as the pull request's title**
  (`qmcp` #62). The preparation script now prints the title.
- **A Python script written through a shell heredoc** had its escaped
  newlines turned into real ones and would not parse. It was written to a
  file instead.
- **A report captured through a PowerShell redirect** carried a byte-order
  mark. The next script's assertion on the report's first word stopped it.

## Readings checked before they were reported

- The local workflow runner failed every step of `vox`'s CI under PowerShell.
  `bash` there is the WSL launcher, with no distribution; run from Git Bash,
  every step passed. An environment, not the branch.
- `Install REUSE` was red in `qmcp`. The interpreter first on `PATH` belonged
  to a virtual environment that ships no `pip`; with it taken off `PATH`, both
  REUSE steps passed.
- One `vox` mutant -- the synthesizer made non-deterministic -- spun at full
  CPU for ten minutes locally, against two to four minutes for the whole job
  on the host. It was about to be stopped by hand and finished first. Why is
  not established; the likeliest cause, a character-level diff of two large
  byte strings in the assertion message, was not confirmed.

**The check that would have caught the last one:** none exists. An assertion
that compares hashes rather than the bytes themselves would make the mutant
fail at once.

Tools: Claude Opus 5.5.
