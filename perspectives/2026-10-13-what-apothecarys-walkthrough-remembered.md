# What apothecary's walkthrough remembered — 2026-10-13

| | |
|---|---|
| **Author** | Peter Kagstrom |
| **Date** | 2026-10-13 |
| **Standing** | Perspective — attributed, dated, non-binding |
| **Tools** | Claude Opus 5.5, in Claude Code, drafted from the sweep's notes |

`apothecary`'s walkthrough is the path a person takes from a fresh clone.
Pages 00 to 10 are written by hand, most of them held by doctests; pages 11 to
16 are written by the browser tests that walk them. The hand-written pages
stated their constraints through the stories that produced them, and the
generated pages carried a few sentences their runs did not assert. Both halves
were swept under `records/DRAFT-durable-text-states-what-is-true.md`: pages 00
to 10 in quaternionmedia/apothecary#51, where a doctest now holds what a story
used to explain, and pages 11 to 16 in quaternionmedia/apothecary#52. This
page keeps the stories. Each was read at `apothecary` `bdc0636`, the sweep's
base, and dated from that repository's history.

Most of what the pages told, the code and the tests told too, and it is told
once elsewhere: the viewer that needed a network (page 04), the readiness
check and the problem index's owner (pages 06 and 08), the CLI that died on a
check mark and the CI failures a green local suite hid (pages 07 and 09), and
the release obligation written on one side (page 10) are in
`2026-10-13-what-apothecarys-package-remembered.md`, and the walkthrough's two
halves becoming one page written by its run is there too. What follows is what
only the pages held.

## A number with no control, a control with no number

Page 02 says that every number in a part's SCAD is a control. On 2026-08-21 it
was not: `datum-core` exposed nine of its twenty-four numbers as controls, so
its corner radius, mount inset, connector opening and antenna relief could be
changed only by editing the file, which is the loop the tooling exists to
replace. Every top-level number became a parameter, and a test began holding
the two together in both directions -- a number with no parameter cannot be
tuned, and a parameter with no number renders nothing when moved. The second
direction found six dead parameters at once: `datum-core` still declared the
indicator and contact dimensions after the cover had moved to `datum-cap`.

## A page that kept the retired number

When `parts/datum` retired on 2026-08-21, its walls of 2.4 and clearance of
0.2 stopped being a second opinion, and page 05 told that retirement as an
event: "This page listed three until recently." It went on using the retired
2.4 to show what a contested number costs, in its doctest and in the recipes
it gave for rendering a candidate, for a number nobody contested any more. The
page now shows the consequence of a contested number with `board_y`, the one
that still is.

## A pin older than the fix

Page 09 runs the CI workflows locally through the corpus's runner, out of the
governance submodule. That runner invoked each step as bare `bash`, which
Windows resolves to the WSL alias before it reads `PATH`, and the corpus's
`main` gave it an absolute shell on 2026-08-14. `apothecary`'s pin is its
project branch of the corpus, which had last been propagated from `main` on
2026-08-11, three days before, so `apothecary preflight` refused to run on
Windows while the fix sat on `main`. Moving the pin is a governance act, a
merge of `main` into the project's branch, and the page explained the refusal
by that history until the sweep.

## Words the run did not assert

Each generated page opened on a shared header: "This page is written by the
run it describes. Every sentence below was emitted by a test that had just
asserted it." A numbered step is written after the assertions before it, but a
page's opening, its notes and its list of what it does not show are fixed
strings in the test, and nothing asserted them. That is how page 14's last
"does not show" bullet came to disagree with its own steps, until a run's
words stopped printing "(read from the STL)" on 2026-10-12.

Page 11 had three such sentences from 2026-08-28, when its two halves were
joined. Step 3 said a shape's confidence "is measurably lower when the finder
is wrong", which the run did not assert; it now asserts the plain finder's
ceiling and says that. Step 12 said "No drawing code was written for any of
this", though the commit that brought the photo path into the viewer had
corrected that same claim in its own message earlier the same day: groups from
a picture's words needed filter chips and colours of their own, and both were
drawn for them. And step 17 closed the page with the census of the viewer's
controls -- "a tool that is pleasant to demonstrate and expensive to use is
neither" -- which is about the viewer rather than photographs, and went. A
page's fixed words need the care its steps get, because no assertion stands
behind them. The header now names the test that writes the page, and the
browser tests' README says which of a page's words are steps and which are
fixed.
