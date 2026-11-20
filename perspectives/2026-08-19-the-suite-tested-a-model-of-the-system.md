# The suite tested a model of the system

**2026-08-19. `dossier`, `qmcp`, and this corpus.** Attributed, dated, binds
nothing.

Tools: written with an AI coding assistant, reviewed and committed by a human.

## The finding

**Three fresh installations failed on three machines while the test suite was
green, and the suite was green because it built the world it tested.**

Every test constructed its own database with its own fixture, pointed the code
at it, and asserted on the result. None of them ran the thing a person runs.
The database that broke was the one the command-line tool *chooses* — in the
directory the person happened to be standing in, created by a startup path no
test exercised. The fixtures were correct. The assertions were correct. They
were about a system adjacent to the one that shipped.

The false assumption is worth stating plainly, because it did not feel like an
assumption: **that a test which imports the code is testing the program.** It is
testing the code. The program is the code plus how it is invoked, where it
stands, what it finds already on disk, and what it does before it reaches the
part anybody wrote a test for.

## The defect underneath the three failures

`init_db()` called `SQLModel.metadata.create_all` on every command. That builds
tables with no migration stamp, so the first command a fresh installation ran
left a database alembic had no record of. Once such a database holds data no
stamp can be inferred, and it cannot be migrated at all.

Every reported symptom was that one cause wearing different clothes: a missing
column mid-screen; `db upgrade` reporting success and changing nothing; a
repair reporting success against a database that was still broken.

The schema now comes from the migrations or not at all.

**And the state that made it unrecoverable was one this session recommended.**
An earlier version of the health check told the operator to run
`dossier db stamp head` on an unstamped database. That marks every migration
applied — including the ones that never ran — so the columns they add never
arrive. The advice is gone and a test asserts the string is absent from the
module, but the sequence is worth recording: a diagnostic wrote the state that
the next diagnostic could not repair.

## The check that now exists

`tests/e2e/` runs the real console script as a subprocess in a directory with
nothing in it. It patches nothing. The only thing injected is `DOSSIER_HOME`,
so a run cannot rewrite the operator's own state — which is not a convenience,
it is the single isolation the category is permitted.

It reproduced each reported failure before repairing it, and it found five more
the same afternoon:

- **Alembic binds `sys.stdout` as a default argument at import**, so the second
  command in one process wrote to the first one's closed stream. This had been
  tolerated for months as `assert exit_code in [0, 1]` with a comment blaming
  the test environment. *The check that would have caught it existed and had
  been weakened to accommodate it.*
- **Commands appended below the `__main__` guard were invisible** to
  `python -m`, because the guard calls the group at the point it appears. The
  console script imports the module fully first, so the gap could not be seen
  through the route everybody used. *No check existed. One does now, and it
  enumerates every command the group knows rather than naming a few.*
- **The stream-encoding fix reconfigured captured streams**, breaking later
  writes in the same process.
- **Tests located files by counting directories** from their own position, so
  organising the suite into categories broke tests unrelated to the change.
- **A rate limit arrived as a traceback** with eight frames, none of which
  mentioned that unauthenticated GitHub allows sixty requests an hour or that a
  token allows five thousand.

## Naming a few and calling it a class

The `__main__` guard defect happened **twice**, a few hours apart. The test
written after the first occurrence named three commands by hand and asserted
each was reachable. All three happened to sit above the guard. When a new group
was appended below it, the test passed and the command was missing.

A test that enumerates three members of a set does not test the set. It tests
three members, and it reads in the diff exactly like a test that tests the set.

## The documentation had the same shape of error

Four entry documents told a newcomer *"Nobody merges their own work into
`main`"*. The rule is the opposite, and the README said both things on one page.

`ci/check_restatements.py` cannot catch this and says so: it verifies that a
page and a record declare each other, not that their text agrees. The
declaration was correct. The sentences contradicted.

This is `records/DRAFT-the-read-document-governs.md` from the inside: the
decision that wins on precedence and loses on readership does not govern, and
what a reader meets first is what they will believe.

## What I would tell the next session

**Run the thing, in a place that has nothing in it.** Not the code — the
command, as a process, somewhere empty. Every failure this session repaired was
visible in the first thirty seconds of doing that and invisible from inside a
green suite.

**When a test tolerates a failure, the comment explaining why is the defect
report.** `assert exit_code in [0, 1]` carried an accurate description of a real
bug for months, phrased as an excuse.

**Check the collection count, not the pass count.** Wiring an executable
walkthrough into `testpaths` collected zero tests and reported success. The
pages were present and correct; pytest read a directory of markdown as nothing.
Measured in `qmcp`: 409 tests before `--doctest-glob=*.md`, 410 after, against a
page that had not changed.
