# Walkthrough pictures: how far two runs drift

*The measurement behind `TOLERANCE = 0.001` in `tests/e2e/picture_drift.py`,
the share of a picture's pixels past which CI names a walkthrough picture that
differs from the committed one. It was recorded in the message of commit
`f41cf8f` (2026-10-11), which brought the check, and is kept here as it was
recorded.*

The walkthrough's generated pages (11 to 16), run twice on one machine and one
tree with every picture written fresh each time, differed in six of their
pictures, by 69 pixels at most: 0.007% of a picture.

A changed word of the viewer's hint bar or status line is thousands of
pixels. A tenth of a percent, about a thousand pixels of a page, is past that
machine's noise and short of a changed word.
