# Documentation tooling

The tools that build, link and audit this documentation site.

## Glossary links

`uv run qm glossary-links` links the first use of each glossary term on every
page under `docs/` to its definition in `docs/ref/glossary.md`. The source is
`ci/glossary_links.py`.

- **First use per page, and nothing else.** The first use is where a reader
  decides whether they know the word; linking every occurrence makes a page of
  underlines.
- **A fixed point.** A term already linked anywhere on the page is done, so a
  second run changes nothing. That is what lets the pass ride the ordinary
  command (`show-it-by-running-it`): drift arrives as an uncommitted diff, and
  `ci/tests/test_glossary_links.py` fails while a committed page is not
  current.
- **Longest term first**, so `phase ladder` wins over `phase`.
- **Left alone:** fenced and indented code (the executable cookbook pages write
  their doctests as indented blocks), inline code, headings (a linked heading
  breaks its own anchor), existing link text and URLs, attribute lists,
  admonition titles, and the glossary page itself.
- **Compounds are not the word.** A term joined to something by `-`, `/`, `_`
  or `.` is part of a compound or a path, so `seed` is not linked inside
  `project-seed/ci/`.
- **The prose keeps its own capitalisation.** The link text is the word as
  written, not the glossary's spelling.
- Every generated link carries the `glossary-term` class, which the stylesheet
  colours.

It cannot know whether a word is used in the glossary's sense: `gate` in a
[record](../../ref/glossary.md#record){ .glossary-term } means a CI check, and `gate` in a sentence about an airport does not.
The command prints that limit on every run.
