# What apothecary's package remembered — 2026-10-13

| | |
|---|---|
| **Author** | Peter Kagstrom |
| **Date** | 2026-10-13 |
| **Standing** | Perspective — attributed, dated, non-binding |
| **Tools** | Claude Opus 5.5, in Claude Code, drafted from the sweep's notes |

`apothecary`'s package -- its docstrings, comments and `--help` texts -- was
swept under `records/DRAFT-durable-text-states-what-is-true.md` in
quaternionmedia/apothecary#44 and #46. Its docstrings carried more history
than any other part of the repository: decisions cited by date or plan, the
old names of things, and past failures given as the reason for a line. Each is
now a constraint stated as a fact, and what a reader needs explained is in
`apothecary`'s `docs/`. This page keeps the stories. Each was read at
`apothecary` `bdc0636`, the sweep's base, and dated from that repository's
history; figures are as the passages and their commits gave them. The pictures
packages, swept in quaternionmedia/apothecary#47, are in
`2026-10-13-what-apothecarys-pictures-packages-remembered.md`, and a part's
values moving into its text, which the package told as well as the pages, is
in `2026-10-13-what-apothecarys-pages-remembered.md`.

## A page written by the run that asserts it

Until 2026-08-28 the photo path's walkthrough was two demonstrations: a
hand-written page of doctests walked the model half, and `apothecary docs
generate` drove the viewer half in a browser and wrote it as a second page,
regenerated only when somebody remembered the command. The remembered page
went stale. That day the two halves became one demonstration that the ordinary
test command runs and writes; `docs generate` keeps only the workflows marked
`docs`. A page regenerated on request goes stale, and one written by the run
that asserts it does not.

## The datum parts and their numbers

`datum-core`, the tray drawn for the `datum` board, carried a `show` parameter
choosing between the tray and its cover, so one part's bounds depended on
which mode was asked for -- two parts wearing one name. On 2026-08-20 the
cover was split out as `datum-cap`. Beside them stood `parts/datum`, an
earlier single-piece tray, which set its walls to 2.4 and its fit clearance to
0.2 while citing the enclosure record's clause 3 for values that record does
not contain. It also carried the black-box seam between a measured board and
the enclosure's parameters, which the bench assembly drove, so deleting it
that day broke the suite and it stayed. On 2026-08-21, when the library moved
to underscore case, the seam moved to `datum_core` and `parts/datum` retired,
and what it had called `usb_w` and `usb_h` the core names for what they are,
an edge connector.

With the old tray gone, the house constants of 3.0 and 0.4 stood unopposed,
and of the three numbers the project's sources had stated differently only
`board_y` stayed contested, because two live sources still disagree about the
board's size. The comment above `datum_core`'s contested values still opened
on "Three numbers", and `datum_cap`'s comment began "The same disagreement
datum_core carries" above an empty table. A citation is provenance only while
a reader can open it and find the value; a count written beside the data it
counts goes stale when the data changes.

## Checks that said what they had not looked at

The readiness check, written on 2026-08-21, asks among other things whether a
part is fitted to measured artifacts. Its first version read `build()`'s
`(Scene, Assembly)` as one object and reported "no stubs remain" for an
assembly it had never looked at -- the false pass its own docstring warned
about -- and comparing it with the assembly's own report caught that before it
was committed. The same day it reported the bench's stubs for every part in
the library, so `calibration_cube` was told it was fitted to a board it has
never heard of; it now reports them only for a part the assembly places.

`apothecary problems` reported a part that had never been rendered as having
drifted from its declared bounds (fixed on 2026-08-21). On a fresh checkout no
part is rendered, so every part was said to disagree with geometry nobody had
measured; an unmeasured part is now left out of drift, and its missing render
is its own problem with the command that closes it.

The bench assembly once placed bare `Cube`s, which carry no position of their
own, so every object rendered at the origin on top of every other while the
Python model looked correct throughout (2026-08-08); each block is now wrapped
in a `Translate`. A model that looks right is not a render that is right.

The `datum_core` site assembly typed out twelve of the parts' defaults again,
and a test kept the copies in step with the parts until, on 2026-08-20, the
assembly read the parts' parameter models instead. A gate that keeps two
copies in step is worse than one copy. In the problem index, an adversarial
review found the contested problem's owner typed into the code beside the
table that already declared it (2026-08-21): the duplication the index exists
to avoid, lying dormant.

## One page in front of the world

On 2026-07-21 the hierarchy's four fixed classes became one recursive
`Assembly`, and a zoom viewer absorbed both earlier viewers, the parts browser
and the bare Site browser. The part view's address was kept as a redirect into
the one viewer, because links to it had been handed out, and a part's old
hyphenated name still resolves, because links to `datum-core` were handed out
before the library moved to underscore case. Two pages onto one object give
two answers about it.

On 2026-10-04, in the consolidation's fifth phase, the firmware page and the
printer monitor became the Bench and a board's Machine in front of the world.
Their links had been handed out too, so `/firmware` and `/firmware/monitor`
answer with the viewer and the right panel open.

Two defects left the viewer looking loaded while it did nothing. A site's
generated SCAD rode only on the layout route's answer, so a site loaded and
never dragged kept its "Load a site..." placeholder in the code panel; on
2026-08-19 every read of a site began carrying it. And three.js came from a
public CDN: with no route to it the module script never ran, and the canvas,
the contents and the code panel came up empty while the status line and the
"Layout valid" chip, both static markup, said otherwise. It was found twice on
two branches that had not yet met -- on 2026-08-19 from a reported symptom,
reproduced by aborting every request to the CDN, and on 2026-08-28 by the
photo walkthrough's browser test, whose first run had no network -- and both
vendored the library. A dependency fetched at the moment of use is a
dependency on the network.

A route also once turned a name from its URL into an import path, so `GET
/parts/stl_renderer` imported the renderer module and answered 500 (fixed on
2026-09-26); only a registered part's name is looked up now.

## Addresses a hand has learned

The page's options sit on rings, each cell with a number, and people learn the
numbers. As the page consolidated, each new option took the seat an old one
had left, so learned digits kept working. On the canvas ring, Pictures took
the seat its Camera had (2026-09-27). On the owner's choice of 2026-10-04,
View took Fit's seat on the canvas ring with Fit inside it, so Fit's address
gained a digit. On 2026-10-04 Watch and Monitor, two ways into two views of
one board, became Open, in Watch's cell, and Flash took the cell Monitor
freed, so every cell after it stayed where hands had learned it. On 2026-10-12
the part's ring was full at eight, and the part-iteration plan's View and
History took the seats Float and Fullscreen had, with those two one press
deeper; a saved variant's Draw took the seat choosing its name had held.

Each comment recorded its own seat's history. The rule that survives is stated
once, in `docs/viewer.md` and the menu module's docstring: the cells a ring
always has come first and keep one address wherever it is opened, and the
cells that come and go are seated after them. An address a hand has learned is
an interface.

## What the census could see

`apothecary census` counts the page's controls from its markup. It counted
three pages until the firmware page and the printer monitor folded into the
viewer on 2026-10-04, and their widgets kept the names the old pages gave
them. Until the part-iteration work of 2026-10-12, a part's parameter controls
were built by the page's script at run time, so the census never counted them;
they are written as markup in their own widget now. A meter counts what is
written where it reads.

## The printer link

On 2026-09-20, the first run against the Ender's real mainboard found three
defects the simulator could not show. One of them: the printer came back as
`ttyUSB0` after a night as `ttyUSB1`, so a pin by port name pointed at
nothing; a pin has since been kept by the board's own identity, its MAC or
else its bridge's serial number. Earlier, a CP2102 bridge on a realtime kernel
was seen handing back bytes it had already delivered, which is why the serial
reader has had a replay guard since the firmware seam landed (2026-09-17).

An audit of the firmware code then found three ways to lose a print, each
reproduced against a fake transport before the fix (2026-09-26). The worst:
one lost temperature reply mid-print made the status poll force-close the link
under the print's thread, the print failed on its next write, and the safe-off
stopped at its first unanswered line, so the lines that turn the heaters off
were never sent -- on the printer, a hotend and bed left at print temperature
with no host attached. The same audit found that the server and a CLI command,
writing the state file at once, kept 12 of 200 pins and crashed on a shared
temporary name.

The unit suite waited out a real board's silences against scripted boards that
answer at once, which cost it more than a minute, until every wait went
through one time scale (2026-09-26). Hardware facts become constraints in the
code; the incidents belong to the bench's history, not to the docstrings.

## Running CI here first

`apothecary preflight` runs the CI workflows locally, through the corpus's
runner, and its help said a green local suite had hidden a CI failure here
more than once. On 2026-08-20 CI failed ten viewer tests, because the vendored
three.js needed `node_modules` and CI never installed it, and seven unit tests
read STLs that only existed in a developer's working tree; then `npm ci` died
on a postinstall that a local `npm install` had long since cached. In a
sibling project, one workflow's `uv sync --locked` stripped the tools a later
workflow needed, and its licensing gate failed for it while saying nothing
about licensing -- which is why preflight runs one workflow per invocation.

When preflight was written (2026-08-22), the runner the governance pin carried
invoked steps as bare `bash`, which Windows resolves through the WSL alias
before it reads `PATH`, so every workflow failed alike for a reason that was
not about any of them; preflight refuses to run rather than report five gates
red for one cause. On 2026-08-18 `apothecary serve` and `apothecary check`
died on their first status line, because a Windows console defaults to cp1252
and a check mark is not in it; three days later the CLI's marks, until then
chosen per command, became one vocabulary.

## An obligation written on one side

The enclosure record asks its consumer to depend on a released `apothecary`,
pinned, rather than a commit. Read from this side that is an obligation on
`apothecary`: a geometry change reaches the consumer by being published. It
was written down only in the consuming project's boundary document, so a
contributor here had no way to learn that anything pinned this repository.
`apothecary release` (2026-08-22) states it where the code is and answers it
with a command: whether this commit is something a downstream may pin.

## Without a lesson

These left the package as history with no lesson beyond their own dated
account, and are listed so they can be cited:

- **The firmware toolchains.** The Rust plan, decided on 2026-10-08, made the
  arduino-cli seam the first toolchain module (2026-10-09), kept
  `/firmware/status`'s top-level fields as Arduino's, named sketches
  `<name>@<toolchain>`, and the scripted bench moved out of the tests on
  2026-10-11 so that `serve --demo` could run on it.
- **OpenSCAD installs.** Before an install wrote `install.json` (2026-10-03),
  a snapshot was the AppImage itself at `<date>/openscad`, and the installer
  still reads one.
- **The kernel comparison.** Its tolerances were set on 2026-10-09, before any
  geometry kernel was run: a starting point for the first comparison, not a
  finding.
- **The garage.** Widened from 3000 to 6000 mm on 2026-07-21 by moving its
  east wall, with the storage and the CNC router moved with it; one printer
  has stood in it since the owner's decision of 2026-10-04.
- **Personal data stays local.** That OrcaSlicer reaches no host was checked
  with an strace of a real slice when the slicer landed (2026-10-10); the
  evidence belongs to that change, not the module.
- **The slicer.** Its decisions were made with the owner one question at a
  time on 2026-10-10, and the code states them as its rules.
