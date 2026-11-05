# The corpus read whole, then landed — 2026-10-24

| | |
|---|---|
| **Author** | Peter Kagstrom |
| **Date** | 2026-10-24 |
| **Standing** | Perspective — attributed, dated, non-binding |
| **Tools** | Claude Opus 5.5, driving the session under review |

On 2026-10-23 and 2026-10-24 the corpus was read as one body for a critique of
its language, eight contradictions that critique named were fixed one decision
at a time, a governance handoff written in another repository was walked
section by section, and every pull request into `main` but one was landed:
this session's, the older queue's, and three that a consistency pass on `main`
added. `handbook/handoffs/qm-queue.md` is the state that left. This page is why
it went the way it did: what was assumed, what that cost, and for each finding
the check that would have caught it and whether that check exists.

## A critique is a set of claims, and some were weaker than written

The critique listed contradictions at `HEAD` as facts. Three did not survive
the first close reading.

- **The stage record against `AGENTS.md`.** The critique said the record moves
  `main` to a release destination while the entry pages tell everyone to merge
  into it, and that one of the two must be wrong. The record's own Consequences
  already say a pushed stage branch enacts it and that it is Proposed for that
  reason. What was wrong was narrower: its `Pends on` row opened with
  "Nothing". The fix (#213) touched that row and nothing else.
- **Positional principle references in handoffs.** The critique counted them
  against the principle-naming record; that record's §4 excludes
  `handbook/handoffs/` on purpose. The template's `P5` was the real instance,
  and it escaped the guard for a different reason: the guard did not scan the
  repository root (#224).
- **"Six places" say every record is Proposed.** A search for the class found
  ten.

The false assumption is that a contradiction found by reading one side is
established. Each fix began by quoting both texts and the host's state, and
that step changed three of eight answers. No check makes a critique do that;
the habit that did is the one `AGENTS.md` item 10 already states.

## Green on nothing

The first preflight ran on uncommitted edits. Its signature step read "0
commits" in the range and its timeless step found nothing in "lines added since
`origin/main`", because nothing had been added by a commit. Both reported
green. The run was repeated after the commit, and that one is the evidence.

A second run was started with a shell `&` inside one tool call; the job ended
with that call's shell, and its log stopped mid-test. Its last line was a pass,
and it proved nothing. The log's modification time gave it away.

**The check:** preflight saying when its commit range is empty or the tree is
dirty. It does not exist.

## The tool answered a different question

- `git merge-tree --write-tree` does not exist in git 2.37. Its usage message
  went to a pipe whose filter printed nothing, and an empty list read as "no
  conflicts". The three-argument form then flagged a conflict in
  `docs/index.md` that `git merge` resolved cleanly.
- Every project branch read as lacking `signature-check.yml`, uniformly. The
  uniformity was Git Bash converting `ref:path` into a Windows path; with the
  conversion off and a control on `main`, eight had it and eight did not.
- `--help` passed to `ci/glossary_links.py`, which takes no arguments, ran its
  write mode and rewrote four pages.

**The checks:** assert a tool's exit status before reading its output, and
run a control whose answer is known. Both are habits rather than gates.
`glossary_links.py` refusing an unknown argument does not exist.

## A gate built on a belief about the host

#216 added `edited` to the three `main`-only gates on the belief that a
retarget fires it, and `handbook/async-contract.md` was changed in the same
pull request to say so. The pull request's own verification said the trigger
was first observed on the next retarget. That observation came that afternoon:
the host's own retarget, when a merged branch is deleted, started nothing on
#217, #220 or #139, while a body edit on #228 did fire `edited`. The sentence
was corrected in #234.

The consequence was covered anyway. #218 makes `qm merge` read the base's
workflows and refuse a pull request whose `main`-only gates never ran, and it
was live for every merge after it. It refused #188 once on a failed host read,
reporting unknown rather than green, and merged on the retry.

The false assumption is that a sentence about the host can be written before
the host is watched doing it. **The check that would have caught it** is the
one the pull request named and then did not wait for.

## What a stack hides

#139 sat on #138's branch from 2026-10-10 to 2026-10-24. The `main`-only gates never ran on it, so
eleven timeless findings in its own text were invisible until it was brought
level with `main`. A stack's draft is not a holding pen, and it is also not
gated; what it carries is learned at the bottom. #218 now refuses the merge
until a push runs those gates; nothing reports them sooner.

## A gate that reads one kind of signature

#198 and #202 each carried one commit the host verifies, signed with an SSH
key. `check_signatures` runs `git` with no allowed-signers file, reads `N`,
and fails. Both were rebuilt with a signature the gate can read and landed as
#229 and #230. **The check** that would make this unnecessary — the gate
reading the host's verification, or being given the signers — does not exist,
and is §4 of the queue page.

## Defects the session made

- **A conflict marker committed.** Rebuilding #173, a cherry-pick loop called a
  Python resolver with `MSYS_NO_PATHCONV=1` still set from an earlier `git`
  command. Windows Python could not open the script's path, the conflicted
  index was added as it stood, and six commits were made carrying `<<<<<<<`
  lines. A count of markers before pushing caught it; the branch was local
  only and was rebuilt. **No gate refuses a conflict marker**; that is now §4.
- **Private names in a status document.** `qm docs generate`, run in a fresh
  worktree without the uncommitted companion roster, wrote private project
  branch names into `status/harness.yaml` and from there into `loose-ends.json`.
  `uv run qm private-names --source host --strict` caught it before the commit.
  That check runs in no workflow, so a run on the host would not have; §4 has
  both halves.
- **A rule worded into a guard.** A `do_not` line in the new `reading:` block
  said "unadopted:", which contains the substring
  `test_no_adopted_boolean_is_emitted_anywhere` exists to refuse. The guard
  fired as written and the line was reworded.

And one found rather than made: a family-stage test checked the demo plan
against the roster's names only, so it failed on the one machine where the
private roster is present and passed everywhere else, CI included. Running
preflight in the clone rather than in a fresh worktree is what found it (#232).

## Pages read by what they hold

The handoffs index told a reader to read it first and then one other page,
while eight rows each said "read this first". The pages were judged by what
each still held, not by their dates: six retired, three of those with open
items carried into the queue page, two kept untagged (#227). Ten participant
pages added by #138 had no row at all; they share one now. About twenty older
pages are still to be read the same way, and that is the queue page's item
rather than this page's.
