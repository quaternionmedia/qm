# Perspective — Explanation in the Wrong Place

| | |
|---|---|
| **Standing** | Perspective — non-binding, attributed, dated. Not a record; never ratified; cite by author and date. |
| **Author** | Peter Kagstrom |
| **Tools** | Claude Opus 5, the assistant whose own output supplies most of the examples |
| **Date** | 2026-08-09 |
| **Task** | Why `.github/CODEOWNERS` is inert, why a file's header comment was the wrong place to say so, and the pattern both belong to: explanation accumulating wherever an author happened to be typing. |

## 1. What happened

An assistant opened a pull request against `main` touching `/project-seed/`,
`/.github/workflows/` and `/.github/rulesets/`. It named no reviewer. GitHub
requested review from `@mrharpo` on open, and the notification cannot be
recalled.

`.github/CODEOWNERS` said, in its own header:

> This file has no effect unless "Require review from Code Owners" is enabled
> on a ruleset

That is false. GitHub requests code-owner review when a non-draft PR opens
against a base branch carrying the file. No ruleset participates, and
enforcement mode is irrelevant — every ruleset in this repo is still
`evaluate`, blocking nothing, and the request fired anyway.

So the corpus documented a live mechanism as dormant, and the documentation
sat in the mechanism's own header, where it read as authoritative.

## 2. A claim made while investigating it, and why it was wrong

The first explanation offered for why only one of four named owners was
requested: GitHub silently skips users without write access, so the blast
radius looked smaller than it was.

Checking rather than asserting:

```
subcontrabass  admin
mrharpo        admin
CameronRWest   admin
MJWKagstrom    admin
```

All four hold admin. The real mechanism is that **CODEOWNERS does not
accumulate — last match wins**. Every file in that PR matched
`/project-seed/` or `/.github/rulesets/`, both of which name two owners, so
the four-owner catch-all never applied. The author is excluded from his own
PR, leaving exactly one person.

The two explanations predict differently. Under the wrong one, exposure grows
as access is granted. Under the real one, exposure depends on which paths a PR
touches, and the catch-all reaches only paths no other rule names. A plausible
mechanism, stated without checking, would have been carried into the fix.

## 3. The pattern both are instances of

Explanation lands wherever the author is typing when they understand
something. The understanding is real; the location is an accident of when it
arrived. This produces:

- a configuration file whose header is an essay about an incident;
- a docstring that argues for a design before saying what a function returns;
- a README a reader finishes rather than passes through;
- a comment block that outlives the code it describes, silently, because
  nothing tests prose and no later edit has cause to revisit it.

The failure is not that the writing is bad. Each is legible where it sits. The
cost is that rationale beside code cannot age honestly: the code changes and
the argument stays, asserting something about a design that has moved. A
retrospective is dated and attributed, so age is a feature — it says what was
true on a day and remains accurate forever.

There is a second cost, visible here. The CODEOWNERS header was authoritative
by position — a reader treats a file's own header as knowing what the file
does. Being wrong in that position is more expensive than being wrong in a
dated opinion, which is read as one.

## 4. What follows

`handbook/style-guide.md` states it as a requirement: inline carries
clarifying facts about the code, README is a shallow onramp, `docs/` is the
reference, and every why goes to a retrospective. The boundary that keeps this
from swallowing the record template: a record answers *why this decision*,
prospectively, bounded by Context and Alternatives; a retrospective answers
*why it went that way*, after the fact.

The corpus does not satisfy that page today. Neither does the work that
produced this file — the assistant's own commit messages and PR descriptions
in the same session run to essay length, and a good deal of what is now in
`project-seed/ci/adr_lint.py`'s docstring is argument rather than fact.
Migration is per-file as files are touched, not a sweep; a sweep spends review
attention on files nobody is otherwise editing.

CODEOWNERS itself is off until there is a second active reviewer and rulesets
A and B move off `evaluate`. The rules are kept commented behind a `#= `
sentinel so re-enabling is one command. Draft pull requests are the defence
that does not depend on any of this: a draft PR requests nobody, whatever the
file says.

---

*Peter Kagstrom, 2026-08-09. Tools: Claude Opus 5.*
