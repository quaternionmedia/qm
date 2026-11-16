# Gathering thresholds: what was measured

*The measurements behind four numbers in the picture gathering and its finder:
`TOO_ALIKE_TO_TELL` in `apothecary/gathering/resolve.py`, `DRIFT_ALLOWED` in
`apothecary/gathering/arrangement.py`, `TRUSTWORTHY_PIXELS` in
`apothecary/vision/plain.py`, and the share of groups the sorting finds
(`apothecary/gathering/judgement.py`), with the share of pairs it answers one
pair at a time (`tests/test_gathering_accuracy.py`). Each was recorded in a comment beside
its number when the number was set, in commit `70b6c26` (2026-08-28), and is
kept here as it was recorded. The code states each rule; `apothecary photo
gather-check` and `apothecary photo check` measure the sorting and the finder
again, on drawn pictures whose answers are known.*

## How alike the shapes may be: `TOO_ALIKE_TO_TELL = 1.8`

How many pairings that looked alike there may be for each one that actually
fitted, before a match is too flimsy to join anything on. Across fifteen
folders of twenty-seven drawn photographs:

| Ratio | Groups found | Groups mixing unrelated pictures |
|---|---|---|
| no limit | 67 | 9 |
| 3.5 | 62 | 5 |
| 2.5 | 58 | 3 |
| 2.0 | 50 | 1 |
| 1.8 | 41 | 0 |

On seventeen further folders never used while choosing the ratio, 1.8 found
41 more groups and again mixed none. As recorded: "roughly a fifth of the
groups that were there to find, in exchange for never having built one out of
photographs that did not belong together."

## How far a matched shape may drift: `DRIFT_ALLOWED = 0.04`

How far a matched shape may sit from where the single move-and-scale says it
should, as a share of the picture, averaged over all of them. In one folder of
twenty-seven drawn photographs:

| Drift allowed | Pairs of unrelated photographs joined into one object |
|---|---|
| 10% | 10 |
| 6% | 3 |
| 4% | 0 |

Genuine pairs came in at nought to two percent, the false ones at four to
eight. Four percent cost nothing measurable in what the sorting found.

## How small a shape may be named with confidence: `TRUSTWORTHY_PIXELS = 40`

| Shape drawn at, as a share of the picture's short side | Named right |
|---|---|
| 3–6% | 33% of the time |
| 14–26% | 100% of the time |

A shape narrower than 40 pixels is still named, with its confidence pulled
down to `LEAST_TRUSTED`.

## How many groups the sorting finds

On drawn pictures, about a fifth of the groups that are there. A person
naming what belongs together (`apothecary/gathering/judgement.py`) is the
rest.

## How many pairs it answers, one pair at a time

18% to 41% of pairs, depending on what was drawn. Most pairs in a folder are
two photographs of different things, which the sorting declines to call
unrelated rather than claim to be sure. `tests/test_gathering_accuracy.py`
sets its floor below the lowest rate seen.
