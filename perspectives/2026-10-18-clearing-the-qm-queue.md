# Clearing the qm queue — 2026-10-18

| | |
|---|---|
| **Author** | Peter Kagstrom |
| **Date** | 2026-10-18 |
| **Standing** | Perspective — attributed, dated, non-binding |
| **Tools** | Claude Opus 5.5, driving the session under review |

From 2026-10-16 to 2026-10-18 the voice set's `qm` part landed, then the
pull requests stacked on it, then the ready ones of the rest of `qm`'s queue,
each reviewed by a deterministic pass and then by reading, and its merge asked
for. `handbook/handoffs/qm-queue-and-qmcp-cleanup.md` is the state that left.
This page is why it took the shape it did: what was assumed, what that cost,
and for each finding the check that would have caught it and whether it
exists.

## A check that runs nowhere cannot go red

**The assumption:** a pull request green on the host and green in the local
preflight leaves `main` consistent. `qm` #135 added a handoff page and merged
with both green, and `status/documents.yaml` no longer described the tree.
Nothing said so: `uv run qm docs check`, which compares every generated
document with a fresh generation, runs in no workflow and in no preflight
step. It was run by hand during the next pull request's review, which is the
only reason the drift was found. The same gap let #136 add a gate to
`ci/gate-registry.yaml` without regenerating `status/gates.yaml`, so `qm gates`
would not have listed the gate it added; `ci/gate_status.py --check` reads that
drift, and runs nowhere either. Every merge of a page or record since has
drifted the document again until a pull request regenerated it.

**The check:** `ci/generate_docs.py`'s own docstring calls its `--check` mode
the CI-safe half, and no workflow calls it. Wiring it in is the next piece of
work.

## A new gate, routed around the day it was reviewed

**The assumption:** a gate's own tests, each with a mutation seen red, cover
what the gate claims. #136's timeless check diffed with `--diff-filter=AM`,
and `git diff` detects renames by default, so the lines a branch added to a
file it also renamed were never read. A line in capitals added to a renamed
file passed with exit 0; the same line added without the rename failed. It was
found by trying to satisfy the check while doing what it forbids, which is
what `AGENTS.md` item 13 asks for, and not by any of its sixteen tests.

**The check:** now exists. The filter is `AMR`, and a test renames a file and
adds a line, seen red against the old filter and again with `R` removed.

## The instrument at hand was not the authority

**The assumption:** `git log --format=%G?` says whether a commit is signed.
Here it read `N` for commits the host verified: signed with a key this clone
cannot check. Counted locally, ten pull requests carried unsigned commits;
asked of the host (`.commit.verification`), five did -- #173, #178 and #171,
#172 through #171, and #121, whose commits run from 2026-09-18 -- and the
rest verified. The same day a comparison of `qmcp`'s seed workflows read *none* for
every file, a uniform result that turned out to be Git Bash rewriting the
`ref:path` arguments; read through Python, all six differed from the seed and
all six equalled it at `qmcp`'s pin.

**The check:** for signatures, the hosted `signatures` gate asks the host and
is right; no local tool does, and the triage loop's survey should ask the
host too. For the uniform result, the rule in `AGENTS.md` item 10 caught it.

## Red for a reason nobody had connected

**The assumption:** a `slot` failure on a project-branch pull request is about
that pull request. Every pull request into a project branch but
`project/qmcp`'s read `slot` red for weeks. The failing run's message
was the old rule's, one open pull request per contributor, because each
branch still carried the corpus as it was before the stack rule, and a pull
request runs the check its merge with the branch holds. Propagating `main`
into `project/codecartographer` cleared it there; eight branches still wait.
Alongside it, no signature check runs on a pull request into a project branch
at all, which is why apothecary's #121 carries 33 unsigned commits and never
showed red.

**The check:** none reports that a project branch's copy of a gate predates a
change to its rule, and none checks signatures on project branches. Both are
open.

## The local runner answered a different question

**The assumption:** the local workflow runner reproduces a pull-request run.
It sets `GITHUB_REF_NAME` from `--ref`, `main` by default, for a pull-request
event, where the host sets `<number>/merge`. On a pull request into a project
branch, the ADR lint's step refusing project records on the default branch
therefore read red locally and green hosted. Passing `--ref 174/merge` made
the two agree on every one of the 31 steps.

**The check:** none yet. A seed change setting the ref as the host does, with
a test, is open work.

## A restamped page that passed every gate

**The assumption:** a handoff page whose figures were taken from the host on
the day is accurate. The restamp of the voice set's landing handoff, `handbook/handoffs/voice-set-landing.md` until it was deleted,
passed every check and was then read with the person, section by section,
each figure re-derived. Eight were wrong. Some were written that day: the
reading load said to be over its budget only after #136, when it was over
before; the pin bump said to re-copy three seed workflows where `qmcp` carries
six; a `slot` run said to follow a ready mark in `vox`, which has no such
check. Some were carried from the page before it: a range of pull requests
that included one closed unmerged; two pull requests listed as merged by
hand, when the host's committer field showed the host had merged them and a
hand commit followed. Classing merges by committer is what settled the last.

**The check:** none can read a handoff's prose against the host. The read with
a person found them, and is now how a handoff page is brought to its merge.

## Text that gave the tool an author's place

Pull request bodies and retrospectives written from 2026-10-10 to 2026-10-14
carried a section headed *For the owner*, a tools line saying the tool drafted the change, and
sentences such as "because the session had not read that file first". Each was
restated: the open items as facts under *Not changed here*, the tools line as
the model's name, the omission as the tool having been run without the file
being read. `check_pr_voice.py` refuses the second person and none of these;
no check reads for them.

## Defects the session made

Each was found before it reached a merged branch.

- **A wait that could not end on failure.** Its exit condition required `gh pr
  checks` to exit zero, which it does not when a check fails, so a red would
  have been waited on until the timeout. It was stopped and rewritten to wait
  only on pending checks.
- **A wait on a head the host would not move.** After `update-branch` was
  refused for a conflict, a loop waited for the head to change. It was stopped,
  and the conflict merged by hand.
- **A comparison that read prose as code.** The script comparing syntax trees
  with docstrings removed counted an attribute docstring as code and reported a
  file as changed. It now removes every bare string statement, and a control
  holds it to reporting a real code change.
- **A Python edit written through a shell heredoc** failed its own assertion
  on the escaped line continuation; the file was untouched, and the edit was
  made with the editor.
- **A pull request body claiming an overlap** with two branches the branch
  report did not list; read against the report before posting, and corrected.
- **A reading-load figure quoted from a branch** before it took `main`: #136's
  body says #141 brings the load to 1189, and `main` read 1190 after #141.

## The local model, read once

Tier 2 of the voice demonstration passed on `qmcp`'s `main`: the second
instruction was handed the first and what it found. The answers were weak:
the file named but not quoted, then seven searches for phrases the model had
made up and a heading quoted where a sentence was asked for. A green tier 2 is
a statement about continuity; the loop the session left for next leans on the
model reading pull requests, and nothing checks what it says.
