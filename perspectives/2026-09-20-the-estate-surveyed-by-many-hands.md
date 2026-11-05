# Perspective — The Estate Surveyed by Many Hands, and What Each Hand Got Wrong

| | |
|---|---|
| **Standing** | Perspective — non-binding, attributed, dated. Not a record; never ratified; cite by author and date. |
| **Author** | Peter Kagstrom |
| **Tools** | Claude Opus 5 |
| **Task** | One session opened to bring a workspace level with origin, closed with the performing estate cloned, tested, mapped and eight pull requests open. This is why it went the way it did: the assumptions that were wrong first, the defects the session caused as well as the ones it found, and for each the check that would have caught it and whether that check now exists. |

## 0. Standing and evidence

One workstation, twenty-one clones, git 2.37, the host reached through `gh`.
Commits are stamped in `handbook/handoffs/the-performing-estate-refreshed.md`;
every figure here is one run at that stamp.

- **E1** — directly observed: command output, gate output, host state.
- **E2** — read from the repositories.
- **E3** — inference, marked where it appears.

## 1. The shape of the session

The brief was small: update the clones, then build a workspace for "the live
show family". There is no family by that name. The record that borders the
families declares seven and calls three of them performing; the workspace
generator knew nothing of families at all. So the first work was to make the
generator take a family (`--family`, checked against the seam file, refusing
a name the record does not declare), and to count the performing families the
same way everywhere the record counts them — it had been drafted against an
estate of three and still said "the three" of a table of seven.

The second half fanned out. Sixteen repositories, one surveying pass each,
one refuting pass each, one synthesis, one critic, one revision; then three
implementing passes with three refuting passes. The refuting passes earned
their keep: one downgraded a "shared vocabulary" seam to none (two copies of
an external model are a consolidation item, not a seam), one found a
"branch keeps it" claim to be the reverse of the code, and one found two
holes in a guard the implementing pass had just written and tested.

## 2. What was assumed, and what was true

**A handoff said the clones moved; they had not — on this machine.** The
page on the branch under review stated that three clones sat at their
`qm/<name>` candidates. On this workstation two were absent and one was
elsewhere under a different name. The first reading was "the page is wrong";
the true reading was "the page is another workstation's truth". The tell was
in the commits: the branch carried two signing keys, one this machine could
verify and one it could not. *Check that would have caught it:* none can — a
committed page cannot know which machine reads it. The corpus's answer
arrived the same day from the other session: `handbook/what-is-not-the-organisation.md`
and the machine-local roster companion. The handoff this session leaves
carries no clone layout.

**A monitor expiring was read as a monitor stopping.** The origin poll was
re-armed each time its watch expired, and each expiry left the previous loop
running. Three loops of an older script and two of a newer wrote the same
state files, and one cycle reported every branch of a repository deleted.
The uniform result was the tell (`AGENTS.md` item 10): `git ls-remote` showed
every branch present. *Check that now exists:* the poll takes a lock and
never diffs against an empty snapshot; the operator kills the previous loop
before re-arming. *Check that would have caught it earlier:* a poll that
reports its own instance count. Not built.

**A commit message asserted a rename that never happened.** An uncommitted
change in ShowStopper swapped `HorizontalGroup` for `HorizontalScroll`; the
session committed it under a message saying Textual had renamed the class.
The refuting pass installed the locked Textual and found both names exported.
The change was a choice, the message a story about it, and the story was
false. This defect the session caused. *Check that would have caught it:* a
commit message that names an upstream change should cite the upstream
version or changelog line; none does, and no gate reads a message for a
claim. The branch is left un-opened with the finding on the handoff.

**`git stash` in a merge drops the merge.** Trying a type-checker baseline
while a merge was in progress, the session stashed and popped; the working
tree came back and `MERGE_HEAD` did not, so the resolved files sat as plain
modifications with no second parent. Re-entering the merge and laying the
resolved files over it restored the shape. *Check that now exists:* the
merge commit has two parents (E1, `%p`). *Check that would have caught it
sooner:* none needed — the status line said "diverged" where it had said
"merging".

**The pull-request voice leaked before the gate existed.** The first draft of
the running merge list said "your click" in a column meant to be read by the
person; the same phrase, in a pull request body, is the thing the other
session's `check_pr_voice.py` refuses, and it arrived on origin while this
session was writing bodies. Every body this session opened afterwards was
grepped for the second person before `gh pr create`. *Check that now
exists:* the gate, once #117 merges; until then the grep.

**A local `uv run` rewrites a stale lock, and did.** Two repositories carried
locks their `pyproject` had left behind. A surveying pass ran `uv run pytest`
in one and the lock changed by seven hundred lines; the pass noticed, restored
it, and every later invocation used `--frozen`. The implementing pass then
regenerated it on purpose, once, and committed it. *Check that now exists:*
`uv lock --check` passes on that branch. *Check the org lacks:* a gate that
runs `uv lock --check` on every pull request in every uv project.

**A shell heredoc that fails silently.** Several multi-line commands were
rejected by the shell with an unmatched-quote error at a line that had no
quote. The scripts were written to files and run from there. This is the
tool's mishap, recorded here only because the workaround — a script file
beside the repository, never inside it — is the one to reuse.

## 3. What the many hands found that one would not have

- Seams graded by one reading and re-graded by another converged on a
  smaller, harder set: sixteen surveys claimed more "implemented" seams than
  the sixteen refutations allowed, and the synthesis took the refutations.
- A guard written and tested by one pass (bare-name and containment on two
  routes) had two aliases the tests did not name — trailing dot and space,
  which Windows strips, and a NUL byte, which the filesystem call turned into
  a 500. The refuting pass, whose brief was to get past the guard, found both
  and closed them.
- Two of the three plugin repositories of show-control could not have been
  installed by anyone from their own locks; nobody had tried since the
  ShowRunner they point at last changed a dependency.

## 4. What this leaves for the organisation

- A committed page states what is true of the organisation; where a clone
  sits, which key signed what, and which loop is still running are a
  machine's facts and belong in the tool's own memory. The rule now exists in
  the handbook; this session's pages obey it, and its predecessor's page did
  not because the rule did not yet exist.
- A refuting pass is worth its cost precisely on the change its author is
  surest of. The traversal guard was tested and green when the second pass
  found two holes.
- A number a commit message asserts about the world outside the repository
  is a claim with no gate. Cite the source or say "chosen", never "renamed".
