# Onramp — a human-in-the-loop testing session

**What this is.** Everything needed to sit down and test the harness/control-panel
pair as a person, in one sitting, without reading the history first.

**What we are testing, and it is not the code.** The suites already say the code
runs. What nothing has established is whether the *loop closes for a human*: a
run finds something, asks you a question, you answer it, and the answer shows up
where you would look. Every part of that has been exercised by whoever built it,
which is the weakest possible evidence.

**Stamped 2026-08-20**, `qm` on `evolve/active-repos`, `qmcp` on
`fix/a-count-nobody-took`, `dossier` on `fix/refuse-a-count-nobody-took`. All
three are local. Re-derive rather than quote.

---

## First: what the onboarding does not tell you

Checked on 2026-08-20 with `grep`, across all three READMEs and the docs site:

| | |
|---|---|
| `dossier/README.md` | never mentions its own `walkthrough/`, which is four executable pages |
| `qmcp/README.md` | mentions human-in-the-loop as a feature bullet and an API path; not the CLI, which is where you would use it |
| the docs site | does not contain the word "walkthrough" anywhere |
| any README | does not mention the pair — that these two applications are two views of one dataset |

So the executable onboarding exists, is current by construction, and **nothing
points at it**. That is a readership problem rather than a documentation one,
and `records/DRAFT-the-read-document-governs.md` is the record about exactly
that distinction: a document that wins on precedence and loses on readership
does not govern.

**This is itself a thing to test.** Come to the session having read nothing but
this page, and notice where you needed something you did not have.

## Setup

Ten minutes, and nothing here can damage anything. Every command names its own
database.

**`~/hil` and not `/tmp/hil`, and that is not fussiness.** This session moves
between two repositories, which invites moving between two shells, and on this
machine the same string means two different directories:

| written | PowerShell opens | Git Bash opens |
|---|---|---|
| `/tmp/hil` | `C:\tmp\hil` | `C:\Users\<you>\AppData\Local\Temp\hil` |
| `~/hil` | `C:\Users\<you>\hil` | `C:\Users\<you>\hil` |

The first draft of this page said `/tmp/hil`. Running it put the harness
database in one directory and the panel database in another, and the failure
surfaced three commands later as a file that did not exist.

```sh
mkdir ~/hil          # or: New-Item -ItemType Directory ~/hil

# in <qmcp>
uv sync

# in <dossier>
uv sync
export DOSSIER_DATABASE_URL=sqlite:///~/hil/panel.db   # PowerShell: $env:DOSSIER_DATABASE_URL = "sqlite:///$HOME/hil/panel.db"
uv run dossier db upgrade
uv run dossier projects add quaternionmedia/qmcp
```

**Name the database.** Both applications otherwise open one relative to the
working directory. `DOSSIER_DATABASE_URL` exists because a demo run from the
repository root wrote into the operator's real data during the session that
built this — the rows had to be identified and deleted by hand.

If you would rather read before running, the two executable pages are
`qmcp/walkthrough/02-a-run-that-found-something.md` and
`dossier/walkthrough/04-the-pair.md`. Both execute under the ordinary test
command, so neither can have drifted from the code.

## The loop

**Eight commands, all numbered.** The first draft numbered six of them and left
the two that write the payload files unnumbered, so a reader following the
numbers went straight from answering the question to ingesting a file nothing
had written. Every line below is a step.

The whole thing takes a few minutes after the first run, which spends most of
its time running the suite.

```sh
# --- in <qmcp> ---
# 1. the run
uv run qmcp selfcheck --database ~/hil/run.db

# 2. what it asked you
uv run qmcp human list --database ~/hil/run.db

# 3. you answer
uv run qmcp human respond selfcheck-tag-claims defer \
      --database ~/hil/run.db --by "<your name>"

# 4. write the units of work         <- produces a file. Do not skip.
uv run qmcp selfcheck --database ~/hil/run.db --deltas > ~/hil/deltas.json

# 5. write what has run              <- produces a file. Do not skip.
uv run qmcp dashboard --database ~/hil/run.db --json > ~/hil/harness.json

# 6. check both files exist before crossing to the other side
ls -l ~/hil/deltas.json ~/hil/harness.json

# --- in <dossier> ---
# 7. what ran, and the work
uv run dossier harness ingest ~/hil/harness.json --write
uv run dossier deltas  ingest ~/hil/deltas.json  --write

# 8. the panel
uv run dossier dashboard
```

**Step 6 is there because it was needed.** `Invalid value for 'PAYLOAD': Path
... does not exist` arrives at step 7 and reads as a broken tool. It means a
step that writes a file was not run, or was run in a shell where `~/hil` meant
somewhere else.

**What should happen.** The run finds that `tag-claims` does not pass — a real
gate refusing this repository's real captured test run, because the suite skips
tests needing optional dependencies. That becomes one unit of work at
`brainstorm`. Answering the question moves it to `planning` and no further.

## What to judge

The code either works or the suites are lying. **You are testing the parts no
assertion can reach.**

**Is the question answerable?** `qmcp human list` prints a prompt and three
options. Read it cold. Could you decide from what is on the screen, or would you
have to go and find out what `tag-claims` is and why skipped tests matter?

**Is `defer` the right vocabulary?** The options are `fix`, `accept`, `defer`.
Those were chosen by the thing that raises the question. If none of them is what
you actually want to say, that is the finding.

**Does the panel tell you what to do next?** After ingesting, `dossier dashboard`
shows the delta. Does it show it somewhere you would have looked? Does anything
connect it to the run that produced it?

**Does the phase mean anything to you?** `brainstorm` and `planning` are
positions in a lifecycle this organisation defined. A delta sitting at `planning`
forever is either an honest state or a queue nobody empties — say which it reads
as.

**Where did you have to switch windows?** Every one of those is a seam that has
not closed yet, and the count is the measure.

## Known-broken, so we do not spend the session re-finding it

Established, and none of it is a surprise to look for:

**The human queue does not cross.** Verified on 2026-08-20: the payload carries
`human_requests` and `human_responses` as *counts*, and dossier has no table for
the rows. So the panel can tell you that one thing is waiting on a person and
never which thing. To answer anything you must go back to the harness. **This is
the biggest gap in the loop and the most likely thing for the session to
sharpen** — what the panel would need to show for you to answer from there.

**The payloads are files you copy.** No live channel. Both walkthroughs say so.

**Only one project emits.** "Deltas across projects" needs a second emitter;
`dossier deltas from-prs` covers the org from the host side and the two have not
been made to meet on the address.

**`qmcp` cannot be tagged.** That is the finding the demo produces, and it is
real. The skips are missing optional dependencies, and `metaflow` cannot run on
Windows at all — `import fcntl` is POSIX-only.

**The payload carries the operator's absolute database path**, and the panel
stores it. Undecided: keep it, hash it, or reduce it to a basename. It is a
decision with a consumer on the other side.

## What would count as a finding

Anything in these three shapes, and they are worth more than a bug:

**A question you could not answer from what was on screen.** The loop's whole
claim is that a person can act on what it shows them.

**A number you did not believe.** Every figure the panel shows carries how old it
is, and the two sides are allowed to disagree — a disagreement is a unit of work,
not an error. If a figure looked wrong, say so before checking; whether it was
wrong is the less interesting half.

**A moment you did what the tool did not expect.** Answering with a word that is
not an option, running the ingest twice, ingesting a payload from an hour ago.
Those paths have assertions behind them and no person has walked them.

## What the session must not do

Ratify anything. Push any of the three branches. Bump a submodule pin — the
corpus commit lands first, and until it does the new tests in both projects fail
with a message naming the absent file, deliberately rather than skipping.

And **do not run any of this without naming a database.** That is the one
mistake the session that built it already made.
