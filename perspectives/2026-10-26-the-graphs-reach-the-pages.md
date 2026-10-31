# The graphs reach the pages — 2026-10-26

| | |
|---|---|
| **Author** | Peter Kagstrom |
| **Date** | 2026-10-26 |
| **Standing** | Perspective — attributed, dated, non-binding |
| **Tools** | Claude Opus 5.5, driving the session under review |

One session, one day. It began on codecartographer's guided steps, a numbered
flow from opening source to reading its graph. It went on to the dock
following the browser window, then this project's copies of the seed's
workflows, and ended with the triplet's graph leg exported and laid on the
corpus's pages. In codecartographer, quaternionmedia/codecartographer#151 to
quaternionmedia/codecartographer#154 landed. In the corpus, #267 propagated
`main` into `project/codecartographer`, and #268 put every family's and
project's showgraph on its page. Most findings share one shape: a check that
passed on this machine was answering a narrower question than the one asked.

## A test that passed by racing the drawing

**Assumption:** a browser test that passes here is evidence about the window.

The every-family test in `show.spec.ts` counts how many names the map hides
once it is fitted. It polled for a frame with no overlapping name, then
counted. Partway through the fit's transition no name overlaps yet and none is
hidden, and on this machine the poll was usually met there. So it read 0 of
48 hidden where the settled fit hides 11. The Linux runner is slower and
always read the settled fit. When the governance pin moved to a corpus with 48
names it failed there, and passed here. Slowing the page's CPU fourfold
reproduced the runner. The test's own mutation, hiding every name but the
first, passed two runs in three against the racing version.

**The check now exists:** the test waits for the fit's transform to settle
(quaternionmedia/codecartographer#153). The general lesson has no check: a
poll that stops at the first frame meeting a condition can stop before the
state it is meant to measure.

## A layout that fitted only in one font

**Assumption:** a header that holds its height here holds it everywhere.

The header's rail was tested at 700 pixels and fitted with 18 pixels to
spare. The runner has no Consolas, and its monospace is wider, so Next ran
past the rail's end there. The fix lets Next give its name to its number. The
same session then measured its own fixture the same way: a code-map fixture
captured with the API's default layout fitted at a scale of 1.14, while the
window asks for the compound layout and fits the same repository at 0.13.
That test passed for a reason the window never meets.

**The checks now exist:** the header test runs again in a wider font. The
code-map fixture is the parse the window asks for. A fixture captured through
a request the window does not make is still not caught by anything.

## A window's sentence is not a document's

**Assumption:** what the window says about a drawing can be published with
the drawing.

The first export copied the show routes' metadata, which names the corpus by
where it sits on the exporting disk. The scrub caught that. It did not catch
three sentences the window says about the machine it runs on:

- "no clone of benchmark beside this checkout";
- "had no clone beside this one";
- the session's own "the clone of alfred on this disk is at …".

Twelve project pages and twenty documents would have published them. Worse,
two system views were composed from clones on local branches: codecartographer's
at a commit only that clone held. Published, the picture showed a state no
reader can see.

**The checks now exist:**

- a system view is drawn only when its clone is at the default branch head the
  document names;
- the exporter says what the export read, not where;
- `scrub` refuses those phrases as it refuses a path.

The phrase list is a word list. A new way of saying "this machine" passes it,
which is a guard with a hole: the next piece of work is a structured reason
from the routes, not prose to match.

## A count made before deriving it

**Assumption:** a figure written into a message or a description is the
figure.

Twice the session wrote a number and then derived it:

- a corpus commit message said 35 code maps and 136 files, where the export
  held 37 and 132;
- a pull request description said every page loaded with no broken image, when
  five of 47 had been opened.

Both were corrected before they left the machine. The second by opening all
47.

**No check exists** beyond reading. The habit is to write a figure only after
the command that answers it has run.

## The environment the gates run in

Three local failures were the setup and not the change:

- An edit script wrote a TypeScript file with CRLF line endings. The commit
  normalises them, so the remote was green, but the state tests read the
  working copy, and nine failed here with "the pattern is stale". The shell's
  `grep` counted no carriage returns in the file, hiding the cause;
  `git ls-files --eol` showed it.
- Stopping a background suite left its servers running, and the next run's
  `npm ci` failed on files they held.
- The corpus's preflight could not reach the signing key ring, and called a
  signed commit unsigned. `check_signatures.py`, run from the contributor's
  shell, read it as good.

**No check exists** for any of the three. Each is recorded in the session's
working notes, not in a gate.

## What held

The rule that a check is not evidence until it has been seen to fail caught
most of the above. A header test passed two of its mutations, because it
measured before the redraw that brings Next back; it now waits. A docs test
read a fixture of another project's data as pages this one names. The
landing session merged every pull request with a merge commit at its
reviewed head, so the commit that drew the corpus's pictures is on
codecartographer's `main`, and the documents can name it.
