# ADR-XXXX — Alfred's Docs Are Timeless, and Its History Lives in the Corpus

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-10-31 |
| **Pends on** | Ratification of the org record it adopts, `records/DRAFT-a-projects-history-lives-in-the-corpus.md` |
| **Principle** | `decisions-are-documented` — Git is the archaeology; the account of how alfred got here is kept where a reader of alfred can find it, and nowhere a reader of alfred's code must read through it |
| **Written against** | alfred `docs/history-in-qm`, the tip of quaternionmedia/alfred#138, stacked on quaternionmedia/alfred#137 |

## Context

The org record on a project's history makes a project's docs timeless, sends
its dated account to its subtree on the corpus's site, `docs/projects/<name>/`,
and binds a project only once a record of its own adopts it. This is that
record for alfred.

alfred's pages carried three kinds of dated text: two retrospectives in
`docs/`, under a History section of its docs site; a table of development
rounds and a table of what each measured, in the changelog's unreleased
section; and comments and docstrings across the specs, the tests and the
site's source that narrated how the code came about. The rounds come as a stack
of pull requests, each a round, and each added a row to both tables.

The corpus generates alfred's subtree: a round log, `rounds.yaml`, with each
round's branch, pull request, dates, what it carried and what it measured;
`git.yaml`, the merged pull requests and tags read from alfred's clone; a
`timeline.md` drawn from both by `uv run qm timeline alfred --write`; and the
two retrospectives. alfred's project page on the site links them.

## Decision

1. **alfred adopts the org record.** Its README, `docs/`, `AGENTS.md`,
   `CONTRIBUTING.md` and the READMEs beside its tests state what is true at the
   commit they are read at, with no retrospective, History section, table of
   rounds, measured count or date of an event.

2. **The changelog is release notes**, under each version's heading. The
   unreleased section says what has changed, and links alfred's timeline on
   the corpus's site for when each round landed and what it measured.

3. **The docs site's History tab links out**, to
   `https://quaternionmedia.github.io/qm/projects/alfred/timeline/`, and to
   nothing in alfred's repository.

4. **A round's account goes to the corpus.** The session that closes a round
   adds its row, and what it measured, to `docs/projects/alfred/rounds.yaml`
   in a pull request to the corpus, and runs the timeline's `--write` there.
   A retrospective of alfred is written in the subtree, dated.

5. **The line is held mechanically where a program can see it.** In alfred:
   - `.github/workflows/timeless-check.yml`, the seed's, verbatim, reads the
     lines a pull request into `main` adds;
   - `tests/unit/test_docs_timeless.py`, in the quick suite, refuses a history
     page in `docs/`, a History tab that is not the corpus's timeline, a
     changelog with a Measured section, a round table, a date or a measured
     count, and a date in a durable page;
   - the same test runs the seed's `check_timeless.py --all` over every
     tracked line, so a narrated comment that arrives by a merge between
     stacked branches is read too.

## Consequences

- alfred's docs site is shorter by its History section, and its changelog by
  two tables that grew with every round.
- Every comment and docstring in alfred passes the seed's timeless gate, and
  stays passing: the quick suite fails on a new one that narrates or shouts.
- A round costs a pull request to the corpus as well as the round's own. That
  cost is the org record's, accepted there.
- A count in neutral words, in a page or a comment, passes every gate. The
  reviewer reads for it.

## Alternatives considered

- **Keep the history in alfred, under `docs/history/`.** The account stays one
  repository away from nothing, and it is published as alfred's documentation:
  read at commits it does not describe, and lengthened by every round. The org
  record rejects it for every project.
- **Keep the changelog's round table, and move only the retrospectives.** The
  table is the part that grows fastest, and its counts are true of one commit
  each. It is the history the boundary exists for.
- **Run the timeless gate on added lines alone.** alfred's pull requests stack
  on each other, and only the bottom one targets `main`, where the workflow
  runs; a line arrives on `main` by merge with no workflow reading it. The
  whole-repository run in the quick suite reads it where the developer works.
