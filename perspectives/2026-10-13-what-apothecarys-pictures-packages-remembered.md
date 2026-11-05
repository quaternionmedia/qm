# What apothecary's pictures packages remembered — 2026-10-13

| | |
|---|---|
| **Author** | Peter Kagstrom |
| **Date** | 2026-10-13 |
| **Standing** | Perspective — attributed, dated, non-binding |
| **Tools** | Claude Opus 5.5, in Claude Code, drafted from the sweep's notes |

`apothecary`'s pictures packages sort a folder of photographs into the objects
they show (`gathering`), find the shapes in each photograph (`vision`), and
build each shape as a piece named for its word (`vocabulary`). Their comments
stated almost every rule through the failure that found it, and
quaternionmedia/apothecary#47 swept them under
`records/DRAFT-durable-text-states-what-is-true.md`, so each rule now reads as
a constraint. This page keeps the failures. Each was read at `apothecary`
`bdc0636`, the sweep's base, and checked against that repository's history;
the rest of the package's stories are in
`2026-10-13-what-apothecarys-package-remembered.md`.

The gathering was built on a branch that landed as one commit on 2026-08-28
and joined the main line on 2026-09-19, so most of what follows is dated by
that landing rather than by the day it was seen. The failures were found by
the gathering's meter -- `apothecary photo gather-check`, which draws scenes
whose answers are known, photographs them, and counts what the sorter got
right, declined and got wrong -- by an independent reviewer, or by running it.
The measurements behind its thresholds -- the tables that chose
`TOO_ALIKE_TO_TELL` and `DRIFT_ALLOWED`, the sizes behind
`TRUSTWORTHY_PIXELS`, and the share of groups the sorting finds -- are left
out of this page; they belong in a dated validation record in `apothecary`,
beside the other measurements a reader may want to repeat.

## Shapes matched one at a time

The first sorting matched shapes one at a time, and the meter caught what that
cannot tell apart: two photographs of entirely different things were joined
into one object because both happened to contain a square, a disc and a
triangle of roughly the same proportions. The arrangement check was added for
it. If two photographs show one thing, then where the camera stood and how
close it was are the only differences, so one move and one scale should put
every matched shape on its partner; a real pair fits, and a coincidence does
not.

The matching under it failed in four further ways before it held. It picked
each shape's best partner by how alike the two looked, so a coincidence that
looked slightly more alike took the real match's place and locked it out, and
whole overlapping pictures came back as unrelated; every plausible pairing now
goes in, and one-to-one is enforced at the end, once the arrangement has
decided. It measured each shape's size against the biggest shape in its
picture, which in a close-up is often the one hanging off the edge, so every
size moved at once and the real matches were lost; and it counted cropped
shapes as missing from the other picture, which is how a close-up came to be
judged a separate object. It weighted proportion and size equally, and the
meter showed the cost as overlapping pictures called unrelated.

The fit itself first measured its error in the second picture's frame, which
made it stricter one way round than the other, and a reviewer showed the
consequence: handing the same two photographs in the other order changed a
confident "the same thing" into "cannot tell". The first guess at its
tolerance, which looked generous and harmless, joined unrelated photographs
into single objects, and the value it holds now was measured. The scale
between two pictures was trusted when it rested on two shared shapes, and it
moves with every wobble in the finder; at two it turned one honest refusal
into three confident mistakes, and it now needs three.

## An exception that made the rule unreachable

Two pictures are the same thing only when three shapes line up. There was an
exception for "every single shape in both is accounted for", and a reviewer
walked straight through it: two photographs with one uncropped shape each
score full coverage on a single match, the arrangement check never runs
because one point cannot be checked, and two unrelated photographs were
declared the same thing at full confidence. An exception to a rule that makes
the rule unreachable is not an exception.

The opposite mistake was the most common one when the sorting was first
measured: two or three shapes failing to line up were reported as proof that
two pictures were unrelated. That is a reason not to join them, and the
sorting now says it cannot tell.

## The order things arrive in

A reviewer handed the sorter the same folder in nine different orders and got
five different results, some of them merging a photograph that did not belong.
Every judgement of a pair was made symmetric, and the pictures are compared in
the order of their names. A sorter's answer must not depend on the order its
input arrived in.

## A chain no pair could see

The meter first scored the sorting one occasion at a time, and pair by pair
everything looked reasonable. Handed a whole folder, the sorter chained twelve
unrelated photographs into one object through weak seams -- the worst failure
the gathering has had -- and no pairwise score could see it, because the pairs
that did the damage were never in the same occasion and so were never
compared. The meter can now hand every picture in at once, and then counts any
pair joined across occasions as a mistake. A meter that scores pairs cannot
see a chain.

The meter had its own error: its two neighbouring camera windows overlapped by
so little that typically one shape was in both. The sorter said one shared
shape was no evidence, and it was right; the drawing was wrong.

## A person's word

The sorter asks a person about the pairs it cannot decide, and the person's
answers outrank it. The check that breaks a group when a pair inside it
contradicts the rest was destroying groups a person had built, on the strength
of a machine's guess, while the report printed "your word was taken as it
stands" in the same breath. A machine's disagreement now breaks only a group
the machine built. A person's word has to hold everywhere or it holds nowhere.

The answers themselves went astray in several more ways. An answer about a
picture nothing could be read from was dropped without a word, and is now
reported as not applied; and a sentence about a picture the same person had
thrown out simply vanished, and is now refused as a contradiction. The answers
sheet appended its whole block of questions on every run, so a file answered
three times held each question three times, and answering two copies
differently was reported as two people disagreeing; and a sheet written to a
file that was not also passed in as answers replaced it, a person's notes gone
with no warning. A file saved by an ordinary editor on Windows begins with a
byte-order mark, which turned the first name in it into a name nothing
answered to, reported missing and present in the same sentence. And the
sheet's examples were once spelled as ordinary names, so uncommenting the
instructions fed them back as answers, and the run stopped with a complaint
about pictures called "one" and "another".

## Questions worth asking

The questions were once ranked by the size of the composite a picture sat in
rather than the group it was the same thing as, which reported a question
worth four as worth one and sorted it last. Working out those groups once per
pair made ranking take twenty-two seconds on two hundred photographs, longer
than everything else in the run together. And a guard on who had answered a
pair read as protection and was dead code, which a reviewer showed by deleting
it with no effect.

## Pieces that vanished, and confidence from nothing

Combining the pictures of one object into one arrangement lost pieces three
ways: two pieces whose names tidied to the same word meant the second replaced
the first; a piece whose name did not end in a number was dropped; and
measuring only the middles of the pieces reported three arrangements nearly
four thousand units across as one unit across, so they were laid out a unit
apart, every one of them on top of the others, under a heading promising they
would not be. Two sightings of something the finder was not sure about at all
once combined to twenty-five per cent: confidence conjured out of two
admissions of ignorance. And a picture holding one certain shape and one blank
guess was reported as "typically 100% sure", because the upper of the two
middle values was taken for the middle.

The map of a gathering once drew every undecided pair as a line, and on
eighteen photographs there were a hundred and four of them, a ball of string
that hid the four answers the map existed to show; and it gave each picture
standing alone the room of a whole group, which pushed the groups off the top
of the screen.

## The words, the shapes and the cameras

A round word is a cylinder, centred on its axis, so until each word was built
with a corner at the origin every disc, post and wedge was drawn half its size
away from where it was seen (2026-09-26). An ellipse was built as a circle of
its longer side, a mesh wider than the footprint, the bounds and the editor
all said it was (2026-09-28).

In `vision`, resetting an arrangement built from pictures did nothing at all
while appearing to work, because the shelf handed back its live object rather
than a copy. A panel a few pixels off square had its angle thrown away and was
built a quarter turn out. And `vision` and `vocabulary` imported each other at
the top of their modules, so whichever was imported second failed.

Cameras were pinned at places, in a file of their own, until on 2026-10-04 a
camera became a part standing in its site, edited in Selected like any other
part, and one device became one camera, both on the owner's decisions of that
day. The file is neither read nor written now; a person's copy stays where it
was.
