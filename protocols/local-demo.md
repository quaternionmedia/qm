# Protocol — Local demo

**Question.** Does this project actually do the thing, on this machine, today?

**Invoked by** a human, or an agent asked to. **Budget** 30 days. **Produces**
`protocols/runs/<date>-local-demo.md`. **Optional** — a project with nothing
demonstrable is a legitimate state, and saying so beats a demo of nothing.

---

## What a local demo is

A committed script that runs the real thing on one machine, with no network, no
credentials and no shared state, and prints what it established.

**It is not a test, and it does not replace one.** A test asserts; a demo shows.
The distinction that matters here is the audience: a test tells a suite whether
to go red, and a demo tells a person what the software does. A project needs
both, and this corpus keeps producing neither — a feature landed, described in a
handoff, and demonstrated once in a session nobody can replay.

## The four rules

**1. It is a file in the repository, not a session transcript.** The failure
this protocol exists against: qmcp's harness demo was typed into a session and
pasted into a handoff page. Nobody else could run it, which is the same defect
as a hand-run check reported as CI.

**2. A test runs it.** Not a test *of* the same behaviour — a test that imports
and executes the demo module. A demo the suite does not touch rots quietly, and
the first person to notice is whoever is being shown it.

**3. It touches nothing the operator owns.** Its own database in a temporary
directory, removed afterwards, and a test asserting the working database is
unchanged. A demo that writes to `./qmcp.db` or `./dossier.db` is one nobody
runs twice, and neither project makes this easy: `dossier.cli` builds its engine
at import time from `sqlite:///dossier.db`, relative to the working directory.

**4. It states what it cannot show, in its own output or docstring.** Every
demo here has a boundary — no network, no Docker, no flow layer on Windows — and
a demo silent about its boundary is read as covering everything it did not fail
at.

## Building one

```sh
uv sync --all-extras          # through the lock; an unpinned install is not the project
uv run pytest -q              # the baseline, asserted before anything is measured
```

**Assert the baseline first.** A demo built against a red suite proves nothing
either way, and this corpus has published one measurement taken that way.

Then write the demo so its central claim is a number the broken version would
get wrong. qmcp's is the audit-log count, because recording an invocation is
precisely what was broken on `main`; a demo that printed a planner's reply would
have passed against the bug.

**Drive the real interface.** Textual's `run_test` gives a `Pilot` over the same
widgets and bindings a person gets. An HTTP demo uses the app's own client. A
demo that calls internal functions is a test with worse output.

**Read the artefact you did not create.** Ask the server for its own count
rather than recounting the list; read a document's Status row rather than
assuming it.

## Two traps, both hit while writing the first two

**A key that does not exist reads as a failure.** `ToolInvokeResponse` carries
`result`, `error` and `invocation_id` — and no `status`. Printing
`status={r.get('status')}` gave `status=None` three times, which reads as three
failed calls against three that succeeded. Status lives on the audit record.

**A widget scrape cannot see a Tree.** dossier's projects are nodes of
`#project-tree`, and nodes are not widgets, so walking the widget tree returned
nothing — indistinguishable from a database that failed to seed. It reported
zero projects against three committed rows.

Both are the same shape: the tool was fine, the reading was wrong, and the wrong
reading looked exactly like a real failure. Before reporting a demo as broken,
name one other thing that would produce the same output.

## Recording the run

`protocols/runs/<date>-local-demo.md`, one section per project, each carrying:
the commit, the baseline, the command, its output, and **what could not be run
locally and why**. That last column is the one worth having — it is the only
place a reader learns that qmcp's flow layer needs Docker because `metaflow`
imports `fcntl`.
