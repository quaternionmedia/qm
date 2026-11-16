# Roadmap — apothecary

What apothecary claims is built, in the order to take it. A ticked line is a claim;
what shows it is the journey or the walkthrough pages the line names. `qmcp tour`
reads this page beside the running application's journeys and the feedback kept on
each stage, and says of each line what was found. What a person said is never written
into this page.

A line names a journey as `journey:<id>` and a page of the repository's walkthrough by
its link. A journey's stages name the walkthrough steps and pages that go through each
of them (`apothecary/journeys.py`, served at `GET /tour`), so a page named at a stage
is not named here again. A line that names neither is shown by nothing, and the review
says so.

The journeys are a chain, each handing the next what it made: a part designed is made
on a printer or cut on a router; a machine runs on a board, which is built, flashed
and heard; a deck's knobs are hands on the machines; a procedure brings the site up
through the family's hub; the working space watches it; and a drawing photographed
becomes pieces, which are parts to design. Photographs come last.

## Starting

- [x] A fresh clone is installed, checked and served, and a person finds their way in. [00](../../../walkthrough/00-getting-started.md), [10](../../../walkthrough/10-serving-it.md)

## Designing a part

- [x] A part is chosen, its numbers staged and applied, its SCAD edited, its variants kept, and it says whether it is ready. `journey:design`
- [x] An assembly is navigated by its pieces. [09](../../../walkthrough/09-an-assembly.md)

## Making a thing

- [x] A part is chosen, shaped, sliced, seen and printed on a machine. `journey:make`
- [x] A part that says how it is cut goes through the router: its toolpath written and drawn, what the router needs said, and cut. `journey:cut`
- [x] A board is built for, flashed and heard. `journey:board`
- [x] The Stream Deck shows the machines, and its knobs jog them. `journey:hands`
- [x] A procedure brings the site up, each step a member's of the family, fired through the hub. `journey:bring-up`

## The site and the page

- [x] The working space says what each machine's hour held, and what is heard and quiet. `journey:watch`
- [x] Windows are kept over a reload. [33](../../../walkthrough/33-windows-kept-over-a-reload.md)
- [x] apothecary is depended on. [16](../../../walkthrough/16-being-depended-on.md)
- [x] The checks run here before a push. [15](../../../walkthrough/15-preflight.md)
- [x] The tour takes the page to each stage of each journey, and keeps a person's word on it. [34](../../../walkthrough/34-the-tour.md), [39](../../../walkthrough/39-the-chain-a-stage-at-a-time.md)

## Photographs

- [x] A drawing on the whiteboard is photographed, squared, read as shapes and marks, and stood up as pieces. `journey:drawing`
- [x] A camera's picture becomes pieces, and a piece a print. [01](../../../walkthrough/01-photographs-into-pieces.md), [03](../../../walkthrough/03-a-picture-to-a-print.md)
- [x] The bench is seen by a camera looking at it. [02](../../../walkthrough/02-the-bench-as-it-is.md)
