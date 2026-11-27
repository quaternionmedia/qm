# A reader written without its language

| | |
|---|---|
| **Author** | Peter Kagstrom |
| **Date** | 2026-11-24 |
| **Standing** | Perspective — attributed, dated, non-binding |
| **Tools** | Claude Fable 5.2, driving the session under review, wrote this page. No second reading was made of it |

One session added a reader for Lean 4 to codecartographer, bundled an example
for it, and then fixed a canvas fault a person found while using the demo. It
left two pull requests there: quaternionmedia/codecartographer#170, ready
against `main`, and quaternionmedia/codecartographer#171, a draft stacked on
it. Figures on this page are of #170 at `726634f` and #171 at `0ff746e`.

The page is about what the session believed without having it shown, in the
order the beliefs gave way. Each is marked **established**, with how, or
**inference**.

## The reader has only ever read its author's Lean

**Established**: `lean --version` on the machine answered *command not found*
before any code was written, and nothing was installed afterwards.

The reader is a tokenizer and a bracket matcher. Its tests hold it to Lean
sources written in the same session, for those tests, by the same tool that
wrote the reader. Thirty-odd tests pass and thirteen mutations each turn one
red. All of that shows the reader does what its author meant. None of it
shows the author's picture of Lean is right: where a declaration ends, what a
binder is, how a name is scoped.

The assumption was that a mutation pass closes the question of whether a
check is evidence. It closes one half. A mutation shows the test notices when
the code changes; it cannot show the expectation was correct, because the
expectation and the code share a source. The corpus's rule that a check is
evidence only after it has failed is necessary here and not sufficient.

The same holds one level up for the example. `examples/lean-proofs` is
offered as a Lean library, and no Lean has compiled it. Its proofs were kept
to forms believed safe. That is **inference** about a language the session
could not run.

*The check that would catch it*: the reader's declarations and `uses` edges
for one real library, compared with what Lean itself lists for it; and `lake
build` in the example. Neither exists. Both are in the queue's *Not verified*.
The pull request says so in its own section rather than in its verification
list, which was a correction made at the clean-up pass: the first body put it
as the last bullet of a list of things that passed.

## A fault found by using the thing

**Established**: the fault was reported by a person dragging a node in the
running demo; the session had not found it.

The session had opened the demo, clicked the example, counted nodes and edges
and taken a picture. It called that verification. It never moved anything.
The canvas found a dragged node's edges by a selector built from the node's
id, and on Windows a local repository's symbol ids hold a path with
backslashes, so the selector matched nothing. Every local repository on
Windows had the fault before the session began; the Lean example, bundled
and local, put it one click from the front door.

Two ordinary causes kept it out of sight. The browser suite draws stubbed
maps whose ids hold forward slashes, and runs on a host where a path has
none. And the session's first attempt to reproduce it dragged a node on the
graph that happened to be on screen, a lexicon, whose ids are plain: the
edges followed, and for one probe the report could have read *cannot
reproduce*. What settled it was asking the page which ids its own selector
failed to match, which named the backslash at once.

The assumption was that a drawing that appears is a drawing that works. A
canvas has verbs, and a demonstration is checked by using them.

*The check*: `web/tests/e2e/drag.spec.ts` in #171 drags nodes whose ids hold
a backslash and a quote, and reads the result by comparing attributes rather
than building a selector of its own. It was red on all three cases before the
change. It exists.

One finding is left open on purpose. A symbol's id carries the absolute path
of the checkout that read it. The fix escapes the id; it does not ask whether
the id should hold that path. That is a question for a person and is in the
queue's *Blocked on a person*.

## Tests that passed and checked nothing

**Established**, both by reading the run.

- A guard that stops a structure's fields at its `deriving` clause had a test
  whose docstring named the mutation that would break it. Applied, the
  mutation left the test green: the sample put `deriving` where another rule
  already stopped the fields. The mutation pass caught it, which is the pass
  doing its work. The test was replaced by one the mutation turns red.
- A test named for the reader never raising on malformed text ended in an
  assertion about a fixed string that did not involve its input. It would
  have passed with the reader deleted from it. No mutation of the listed
  thirteen touched it, because its docstring claimed none. It was found by
  reading the diff before calling the pull request ready, and rewritten.

The second is the more useful. The mutations were chosen from the docstrings
that named one, so a test with no stated mutation was a test nobody tried to
break. *The check*: mutate against every test, not against every claim. It
does not exist; codecartographer has no mutation runner, and the pass was a
script that is not committed.

## Defects the session made

Each is **established** from the command output that showed it.

- **A key that meant more than it said.** The reader put a count under
  `sorry` on a file node as well as on a declaration. The construct
  vocabulary maps that key to the *unfinished proof* facet for every node of
  the language, so a file became an unfinished proof. The example's test
  listed which nodes carry the facet and expected one name; it got two. The
  file's key is now `sorry_count`, and a test says a file carries no facet.
  The assumption was that a `meta` key is private to the kind that sets it.
- **Line endings.** One Python file in codecartographer is stored with CRLF.
  A script rewrote it through a text API and every line changed. `git diff
  --stat` showed twenty-five lines for a one-line edit, and the endings were
  restored before anything was committed. `git ls-files --eol` was run on
  every file edited afterwards.
- **An escape written through a here-document.** A `\n` meant for a Python
  string in a test arrived as a real newline and the file no longer parsed.
  Collection failed at once. A note against exactly this was in the
  session's context when it happened; the note did not stop it, and the same
  is said of governance in `2026-11-21-the-evidence-was-in-the-context.md`.
- **A sentence asserted before it was checked.** The suite skipped one test
  fewer than at the base commit. The pull request body said why, naming the
  front end's installed dependencies, and was posted. Reading the skip
  conditions afterwards showed the test waits on a front-end build on disk.
  The body was corrected. The corpus's rule on establishing a fact before
  asserting it covers this case exactly and was not applied until after.

## The scaffolding answered twice

- **Established.** With the demo's servers running from the worktree, the
  local workflow runner went red at three front-end install steps. The error
  named a file the running dev server held open, `npm ci` had by then removed
  most of the installed modules, and the same run with the servers stopped
  passed every step. The reds were the session's own demo.
- **Established.** After a restart, the page's DOM showed no bundled examples
  and no lexicon buttons, for several probes over many seconds, though the
  data had arrived. A picture of the same page taken a moment later showed
  them all. The page had not painted a frame, so its redraw had not run, and
  `document.hidden` read false throughout. Two probes went into the
  application's redraw code before the picture was taken.

In both the result was uniform — every install step, every chip — and the
corpus already says an unexpected uniform result is a tooling fault until
shown otherwise. The second took longer because the session had just found a
real fault in the same canvas and was ready to find another.

## What a session opened in the corpus cannot do in a project

**Inference**, from one session. The work was in codecartographer and the
session was opened in the corpus. The project's own rule on merging differs
from the corpus's — a person merges there — and was followed because the
project's entry document was read before the first commit. The cost of the
mismatch was smaller things: the session's own tooling tied the pull request
to a folder it was not opened in. A session whose work is one project's is
better opened in that project.

## Next

1. Compare the reader with Lean on one real library, and build the example.
2. Decide whether symbol ids hold an absolute path.
3. A mutation pass that takes every test, not every stated mutation.
