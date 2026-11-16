# A whiteboard to a model, and round again: a plan

*A plan, dated. Built: every slice, at the command line and in the page --
the `outline` finder ([walkthrough 28](../../../../walkthrough/28-a-whiteboard-to-a-model.md)),
marks sorted with a person's word kept and fitted to, the whiteboard as a part,
a photograph pinned at it squared and laid in front with its corners moved in
the Marks window, cuts, notes and the way out, round again, the whiteboard's
history scrubbed and a moment placed elsewhere, the marks and notes worn over
the picture in the world, and the fifth loop's page,
[walkthrough 30](../../../../walkthrough/30-a-whiteboard-round-twice-through-the-page.md),
with [walkthrough 29](../../../../walkthrough/29-a-whiteboard-round-twice.md) by the
commands ([pictures.md](../../../../docs/pictures.md#a-whiteboards-marks)). What is not built
is under* What it leaves.

## What this plans

A person thinks on a whiteboard: a bracket, a plate with two holes, where three
things stand on the bench. This plan makes the whiteboard a way into
apothecary. The drawing is photographed, the photograph becomes pieces with
names and sizes, the pieces are looked at in the world and adjusted, and the
whiteboard is corrected and photographed again. Each time round, the model
follows the drawing, and a person's word holds where they gave one.

It plans two things:

- **the path**: the steps a person takes from a marker to a model, each a step
  of the page or one command, shown by a walkthrough page a test writes;
- **the featureset**: what the tool gains so each step works on a drawing, in
  slices, each ending where a person refines what the tool guessed.

The loop beside the ones built:

| Station | A picture to a print, as built | A whiteboard to a model, this plan |
|---|---|---|
| The subject | a thing lying on the bench, under a camera | a drawing in marker on a whiteboard |
| The picture | a camera of the site takes it, or a file is pinned | a phone's photograph dropped on the whiteboard in the site, or a camera aimed at it |
| Squared and sized | a camera's picture lands through a pinhole; a file is flat, a width across | the whiteboard's own edge squares it, and its width, said once, sizes every drawing on it |
| Sorted | nothing to sort: a picture holds things | each mark a diagram's, writing, or unsure, and a person's word on any |
| Found | filled shapes, light from dark | a diagram's strokes: a closed stroke is a shape, a stroke inside it a cut |
| Made | a shape stands up as a piece | the same, with its cuts |
| Adjusted | Part › Edit, a person's numbers over the guess | the same |
| Round again | a second picture, a second piece | a second photograph of the same whiteboard, and the pieces already made follow it |
| Kept | sliced and printed | sliced and printed as built; saved as a part once *A made piece saved as a variant* is built |

## Words

*Whiteboard* is always written out. *Board* is a circuit board here (the
devkit, a printer's mainboard) and *sketch* is firmware, so the drawing is a
*drawing* and the finder that reads it is `outline`. A *stroke* is one line of
the marker; a *mark* is the strokes that belong together, a *diagram*'s or
*writing*; a *note* is writing kept with what it is about; an *example* is a
mark with what the tool said of it and what a person said.

## What exists

- The finder seam: a protocol, a registry, two finders (`stated`, `plain`), a
  bench of pictures whose answers are known (`apothecary/vision/finder.py`,
  `apothecary photo check`).
- The plain finder: light split from dark, touching pixels gathered, a blob's
  family guessed from how much of its tightest box it fills
  (`apothecary/vision/plain.py`).
- Words: `disc`, `plate`, `post`, `slot`, `wedge` (`apothecary photo words`).
- A picture pinned at a place as a view, sized by a width a person types or by
  the camera that took it, its shapes made into pieces, a piece adjusted,
  sliced and printed ([pictures.md](../../../../docs/pictures.md),
  [walkthrough 03](../../../../walkthrough/03-a-picture-to-a-print.md)).
- A view's mapping is a homography (`apothecary/vision/projection.py`), so a
  picture taken at an angle has a place to carry its squaring.
- Several photographs sorted into which are of the same thing, by matching
  shapes under one step and zoom (`apothecary/gathering/`,
  [walkthrough 01](../../../../walkthrough/01-photographs-into-pieces.md)).
- A made piece's record keeps the shape and extent it was made from, which
  Make all reads to skip a shape already made (`apothecary/vision/views.py`).
- A picture's ways in: dropped or pasted on the page, added from disk, put in
  the picture folder, taken by a camera of the site.

## What a drawing reads as to the plain finder

Three pictures drawn to order, each a rectangle, a circle and a triangle on a
light ground, read by `apothecary photo find --finder plain`:

| The picture | What `photo find` says |
|---|---|
| The three filled in | `rect`, `disc`, `tri`, read as plate, disc and wedge, each sure past 0.6 |
| The three as marker outlines, the whiteboard filling the picture | three `poly`, each read as plate at 0.30: the stroke is the blob, and a ring fills little of its box |
| The same outlines, the whiteboard framed by a darker wall, a small circle drawn inside the rectangle and a dimension line under it | the outlines' insides as plate, disc and wedge; the whiteboard itself as one more shape, a disc across nearly the whole picture; the small circle as a plate of its own, not a cut; the dimension line not at all |

The third reads the drawing's insides only because the wall is dark: the
picture's edge decides which side is ground, and the whiteboard becomes the
thing found. Not measured here: a real photograph. Glare, a shadow across the
whiteboard, a marker running dry, an eraser's smear and the tray under it are
all absent from a drawn picture, and slice 1's bench is where each is drawn and
counted.

## The path

What a person does, in the page's own words where they exist:

1. **Draw** on a whiteboard: diagrams and writing, in any markers.
2. **Photograph** it, the whole whiteboard in the frame, edge to edge.
3. **Bring it in**: drop the photograph on the whiteboard where it stands in the
   site, or take it with a camera of the site aimed there.
4. **Sort and refine**: every mark is shown as a diagram's, as writing, or as
   unsure, on the picture. A person changes any that is wrong, and nothing is
   made from a mark while it is unsure.
5. **Find shapes**: each closed stroke of a diagram is outlined, squared to the
   whiteboard's edge and sized by the whiteboard's width. A person changes a
   shape's family, closes a gap, or says a stroke is not a shape.
6. **Notes**: writing stays with the shape or the line it is nearest, as a note.
   A person types what it says, or asks for it to be read.
7. **Make**: Picture › Make, or Make all. Each stands as a piece, its cuts
   through it, named for its word, its notes beside it in Selected.
8. **Adjust**: Part › Edit. A thickness, which no drawing shows, and any side a
   person knows better than the marker did.
9. **Round again**: change the drawing, photograph it, bring it in. The page
   lists what moved, grew, appeared and was rubbed out, piece by piece and note
   by note, and changes nothing until each is taken.
10. **Keep it**: Slice and Print as built.

From the command line the same path is `apothecary photo build --finder
outline --width-mm`, and `photo view` for the result.

## Decided

- **Writing and diagrams are different things.** A mark is a diagram's or it is
  writing, and the two are never read by one rule: a diagram's strokes become
  shapes, writing becomes notes.
- **Sorting and refining comes first**, before any slice that makes more from
  a drawing: slice 2.
- **A person's word at every step, kept.** Each step shows its guess where it
  lies and takes a correction, and a correction wins. Each is kept as an
  example: the picture's region, what the tool said, what the person said. The
  examples are what the tool's rules are fitted to and measured against.
- **Fitted rules stay plain.** A rule fitted from examples is a table of
  numbers a command writes and the finder reads: the same picture gives the same
  answer, on this machine, with the network off, with no model to load.
- **Writing is a note on its shape**, not read by apothecary. A person types
  what it says. The way out is short: one action sends a whiteboard's notes to
  qmcp, where an image model reads a note a person asks about, and its words,
  typed or read, to looksatwords as a transcript, over loopback, each refused
  in plain words while it is not serving. A reading is a guess beside a
  person's word and never over it.
- **A marker's colour is a hint, kept.** Each mark's colour is read and kept
  with its example. It decides nothing alone; the sorter may lean on it, and how
  far is fitted.
- **A whiteboard is a part of the site**: it stands at a wall, its width is one
  of its parameters, a camera is aimed at it, and its photographs and notes are
  listed under it.
- **The path is a fifth loop** of page 00, with a page of its own that goes
  round twice.
- **Pictures in the repository are drawn to order.** A real photograph is read
  on the machine of the person who took it, and its examples stay there.
- **A photograph of a whiteboard is laid in front of it**: squared to it, as
  wide as its surface, flat on the floor a step out, where its pieces are made
  at full size.
- **The loop is a heads-up layer and a precursor to designing for making**: a
  picture's marks and notes are worn over it in the world, and every step leads
  towards pieces a machine can make.
- **Navigable by time, on one scrubbed timeline**: a whiteboard's photographs,
  the words given on them and the pieces made and dropped are one history, and
  a moment of it is the whiteboard as it stood then.
- **Navigable by space**: a moment of a whiteboard can be pulled and placed
  elsewhere, its picture at another place with its words by then.
- **A whiteboard's corners are moved on its photograph**, in the Marks window.
- **Kept in the server's memory**, as views are, until the draft record
  *Personal data stays on the device* says where else.

## The featureset

Each slice is one branch, stacked on the one before it, gated by
`apothecary test run`, with `apothecary test all` once on the top. Every slice
after the first ends in a step a person refines, and adds that step's examples
to what is kept.

### 1. A drawing's strokes read as shapes

A third finder, `outline`, registered beside `plain` and `stated`:

- the ground is the whiteboard, found as the light region the strokes lie in,
  whatever runs round the picture's edge; the whiteboard is never a shape;
- light is split from dark near each pixel, not once for the whole picture, so
  a shadow or a glare across the whiteboard moves no stroke to the wrong side;
- a closed stroke is the shape of what it encloses, named by the rule the plain
  finder names a filled shape by, and no surer than the plain finder is;
- a mark filled in is the shape it covers;
- a stroke that neither closes nor fills a shape, a dimension line, an arrow or
  writing, is not reported, and neither is a stroke inside a shape; slice 2
  sorts the first and slice 4 reads the second;
- a gap in a stroke a few pixels of the working picture wide is closed, and a
  wider one leaves the stroke open;
- Pillow alone, with the network off, as every finder is.

`apothecary photo check` draws whiteboards whose answers are known: in
outline, turned, faint, a gap in a stroke, a shadow's gradient, a glare, a
smear, notes beside the shapes, a wall, a frame and a tray. The page's Find
shapes offers `outline` beside `plain` for a picture that holds a drawing, a
closed stroke at least, and stays one press for any other. Held by
`tests/test_outline_finder.py`, whose floors are the bench's; the hermetic half
of the path's page is
[walkthrough 28](../../../../walkthrough/28-a-whiteboard-to-a-model.md).

Not in it: a shadow with a hard edge, which, where it is dark enough to read
as a stroke, loses a shape it crosses; a shape filled in faintly, which it
misses; and a real photograph.

### 2. Marks sorted, and a person's word kept

The first stop after a photograph is read. It makes nothing: it says what each
mark is, lets a person say otherwise, and keeps what they said.

- **Marks.** The outline finder's strokes are gathered into marks: a closed
  stroke with what it holds, a line with its ends, a run of small strokes on
  one baseline. `apothecary/vision/marks.py`, beside the finder and reading the
  same strokes.
- **Sorted.** Each mark is `diagram`, `writing` or `unsure`, with how sure, by
  plain features: its size against the whiteboard, how many strokes it has and
  how they repeat along a line, whether it closes, how straight it runs, its
  colour. A mark under a threshold of sureness is `unsure`, and `unsure` is an
  answer, as *cannot tell* is the gathering's.
- **Shown.** On the picture where it lies, each mark is outlined in its kind's
  own line, and listed beside it. Find shapes reads the marks sorted as a
  diagram's and no others.
- **Refined.** A person changes a mark's kind, joins two marks, parts one, or
  says a mark is nothing, on the picture or in the list. Their word wins and
  says who decided, as an answer to the gathering does.
- **Kept.** Each correction, and each guess a person let stand, is an example:
  the mark's region, its features, the guess, the word. Examples are kept as
  the gathering's answers are, in a file a person names, until *Personal data
  stays on the device* and *Data retention* say where else.
- **Measured.** `apothecary photo check` draws whiteboards with writing beside
  and inside their diagrams, and scores the sorting: marks sorted right, marks
  left unsure, a diagram read as writing and writing read as a diagram counted
  apart, since the second makes a piece nobody drew.
- **Fitted.** `apothecary photo fit` reads examples and writes the sorter's
  thresholds as a table beside the finder, with the score before and after. A
  fit that scores worse on the drawn whiteboards is refused.

Held by `tests/test_marks.py` and the bench's floors; walkthrough 28 gains the
sorting and a correction.

### 3. The whiteboard as a part, squared, its width said once

- **The part.** `parts/whiteboard`, a flat panel on a wall with its width and
  height as parameters, in the garage on the wall behind the bench. A camera
  added at it looks at it, as one added over the bench looks down.
- **Its pictures.** A photograph dropped on it, or taken of it, is its view,
  listed under it with its marks and notes.
- **Squared.** Its four corners are found from the ground's outline; a person
  drags any that is wrong, on the picture, and the dragged corner is an
  example. The corners give the view its mapping, so a photograph taken from
  one side lays its shapes square.
- **Sized.** A squared picture is as wide as the part says. No width is typed
  per photograph.

Held by the part's tests, `tests/test_views_api.py` and a browser test of the
corners.

### 4. A stroke inside a stroke is a cut

A closed stroke of a diagram wholly inside another is a cut through the outer
one, not a piece of its own: `FoundShape` says which shape holds it, a made
piece is its word less its cuts, and Part › Edit lists each cut's place and
size beside the piece's own. A person says a stroke inside is a piece of its
own, or nothing, and that is an example. A cut inside a cut is reported and not
made. Held by the made part's tests (`tests/test_made_part.py`) and the
vocabulary's.

### 5. Notes, and the way out

- **A note** is a mark sorted as writing: its region of the picture, the shape
  or line it is nearest, and the words a person typed for it, if any. It is
  listed under the whiteboard and shown in Selected beside the piece made from
  its shape.
- **Typed.** A person types what a note says. Typed beside a dimension line, a
  number with a unit is offered as that side's size, and taken only on a
  person's yes.
- **Sent.** One action on a whiteboard's notes: to qmcp, a note's region, for
  which of some given words it holds
  ([image-models-through-qmcp-2026-10-30.md](image-models-through-qmcp-2026-10-30.md)),
  the answer kept beside the person's word; to looksatwords, the whiteboard's
  words in reading order as one transcript. qmcp's vision contract asks a label
  among words, so a note read freely waits on a property of that contract, which
  is qmcp's to add. Both are on this machine and reached over loopback
  (`apothecary/stays_local.py`); each that is not serving is said so, with the
  command that starts it.

Held by unit tests against a simulated qmcp and a simulated looksatwords, as
the Models window's are.

### 6. Round again

A photograph of a whiteboard that has an earlier one is read against the pieces
and notes made from the earlier one, shapes matched as the gathering matches
two photographs of one thing:

- a shape that matches a piece and has not changed proposes nothing;
- one that moved or changed size proposes the change to its piece;
- one that matches nothing proposes a new piece;
- a piece whose shape is gone proposes its Drop;
- a note whose writing changed asks for its words again.

Each proposal is a row a person takes or leaves, and nothing changes until
one is taken, as *Photo gathering proposes and waits* ([project/todo.md](../todo.md),
*Next round*) decides for the gathering. A side a person stated in Part › Edit
is not proposed over: the row says the drawing and the person disagree, and by
how much. Each row taken or left is an example. Held by a browser test that
goes round twice.

### 7. The fifth loop

- **Its page**: a runtime-bound page beside
  [walkthrough 28](../../../../walkthrough/28-a-whiteboard-to-a-model.md), the next
  number free when it lands, written by the browser test that walks the path
  twice round; a row of the README's map, held by `tests/test_readme_map.py`.
- **Page 00** names five loops, and the tests and docs that count four follow.
- **In the demo**: `apothecary serve --demo`'s garage has the whiteboard on its
  wall and a drawn photograph of it in its picture folder.
- **In the page**: no sentence is added. The status line names the next step,
  as every step of walkthrough 03 does.

## Pages with pictures

| Slice | Page | Written by |
|---|---|---|
| 1 | 28, *A whiteboard to a model*, hermetic: a drawn whiteboard read, named, placed and sized | its own doctests |
| 2 | 28 gains writing beside the diagram, the marks sorted, a correction and its example | the same |
| 4 | 28 gains a piece with a cut | the same |
| 6 | 29, *A whiteboard, round twice*, hermetic: the loop by its commands | its own doctests |
| 3, 5 to 7 | 30, *A whiteboard, round twice through the page*: the photograph pinned at the whiteboard, found, its writing typed, made, a second photograph, a change taken, Earlier, and a moment placed on the bench | `tests/e2e/test_whiteboard_round_twice.py`, its pictures recorded and never compared |

## Questions the owner decides

Asked one at a time:

1. whether a fitted table of thresholds is committed, when the examples it was
   fitted to are a person's own photographs and are not;
2. whether an example keeps its region of the picture, or its features alone;
3. which is the first thing fitted: the sorter's thresholds, or the finder's
   share of darkness that makes a stroke.

## What it leaves

- **A marker's colour leant on.** Each mark's colour is read, kept with its
  example and shown; the sorter does not yet lean on it, and no fit moves a lean.
- **A camera aimed at the whiteboard.** A camera's picture lands on an upward
  surface; one aimed at a wall lands nowhere, so a whiteboard's photograph comes
  in by a drop, a paste or the picture folder.
- **A note's writing read freely.** qmcp's vision contract answers a label among
  words it is given; reading a note's words needs a property of that contract,
  which is qmcp's to add.
- **Kept across a restart.** A whiteboard's photographs, words, corners and
  history go when the server stops.

- **Handwriting read here.** No plain reader reads handwriting, and none is
  planned in apothecary: a note is read by a person, or by qmcp on a person's
  ask.
- **The model kept as a part.** A made piece has no Save; *A made piece saved
  as a variant* ([project/todo.md](../todo.md), *Next round*) is the path's last
  step once it is built, and waits on the record it names.
- **A drawing to a cut.** A piece made from a drawing declares no cuts for the
  router ([cam.md](../../../../docs/cam.md)); a flat piece with holes is the router's
  natural work, and a plan of its own.
- **A phone that sends its photograph.** A photograph arrives by a drop, a
  paste or the picture folder. Nothing listens for a phone, and what may is the
  draft record *Personal data stays on the device*'s to say.
- **Curves and freehand.** A closed stroke is named as one of the words. A
  freehand outline kept as its own polygon needs `FoundShape.points` to have a
  consumer, which the finders plan also waits on
  ([photo-finders-local-models-2026-09-21.md](photo-finders-local-models-2026-09-21.md)).
- **Height.** A drawing is flat. A thickness is a person's, in Part › Edit.
- **A trained model.** A fitted table is as far as this plan goes. A model with
  weights is the finders plan's, behind its own seam.
