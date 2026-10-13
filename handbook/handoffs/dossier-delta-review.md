# Handoff — Review dossier's delta entity branch

**Goal.** Review `feature/delta-entity-type` in `quaternionmedia/dossier`,
report findings, and open a pull request for it. It currently has **no PR**, so
nothing has been reviewed and nothing is tracking it.

**Why it comes first.** The governance dashboard will model *intended work*
alongside observed state, and this branch is where that concept already lives.
Reviewing it before building on it avoids designing a second one; landing it
avoids building against a schema still in flight.

Read `handbook/handoffs/README.md` first for the rules that apply to all of
these.

---

## What it is

*Restamped 2026-08-12; `dossier` main at `604efb8`,
`origin/feature/delta-entity-type` at `393450f`,
`wip/delta-entity-type-local` at `3dc8192`. Two rows below changed since the
2026-08-09 stamp — re-derive before acting on any of them.*

| | |
|---|---|
| Branch to review | `wip/delta-entity-type-local` — **not** the feature branch; see below |
| Size against `main` | 26 files, +4,342 / −408 |
| Position | **16 ahead, 16 behind.** `main` is no longer an ancestor |
| PR | none, and there has never been one (`gh pr list --state all --head feature/delta-entity-type` is empty) |

**The branch to review is the wip one, and that is a fact rather than a
judgement.** `git merge-base feature/delta-entity-type
wip/delta-entity-type-local` returns `393450f` — the feature branch's own tip —
so wip contains every feature commit and `git log
wip..feature` is empty. wip is feature plus one commit, `3dc8192`, which adds
11 files at +1,972 / −112 including `src/dossier/database.py`,
`docs/DELTA_ENTITY_PLAN.md`, and 822 lines of tests across `test_api.py`,
`test_cli.py` and `test_models.py`. Reviewing the feature branch reviews the
design without the tests written for it.

**wip exists on no remote** — `git branch -r --list 'origin/wip/*'` returns 0.
It is one disk's copy of the more complete work.

## Before it can land: two alembic heads

`005_delta_tables` and `main`'s `005_governance` both declare
`down_revision = '004_full_name'`. The revision *identifiers* are distinct, so
nothing errors on import and no filename check catches it; `alembic upgrade
head` is what fails, with multiple heads present.

```
004_full_name ─┬─ 005_governance ─ 006_disk ─ 007_reclaim ─ 008_release   (main)
               └─ 005_delta_tables                                        (this branch)
```

Re-parent `005_delta_tables` onto `008_release` and rename the file, or add a
merge revision. One line either way, and it must happen before the branch is
judged on whether it applies.

## Before it can open: dossier's slot is spent

**#12** (`governance/refresh-seed-copies` → `main`) is draft, `MERGEABLE`, six
of six checks green. It holds dossier's single slot. The delta pull request
cannot open until #12 lands or closes, and folding them is not the answer —
a seed refresh and a new entity type are unrelated changes arriving together.

It adds a change-management entity: `Delta` with a lifecycle
(`brainstorm → planning → implementation → review → documentation → complete`,
plus `abandoned`), `DeltaNote` for phase-stamped markdown, and `DeltaLink`
joining a delta to issues, PRs, branches, docs and other deltas. Most of the
diff is `src/dossier/tui/app.py` (+1,386) and `src/dossier/models/schemas.py`
(+134).

## What to review for

Ordinary review applies. These are the parts that matter for what comes next,
in rough order:

1. **Is the phase model right, or merely plausible?** A lifecycle enum is easy
   to write and hard to change once rows exist. Ask what happens to a delta
   that skips a phase, reopens after `complete`, or is abandoned and revived.
   `advance()` and `can_advance()` encode the answer today.
2. **`DeltaLink.target_id` / `target_name` is a loose join.** `link_type` is a
   free string (`"issue"`, `"pr"`, `"branch"`, `"delta"`, `"doc"`) with no
   foreign key. That may be right for a cache-merge architecture that syncs
   partial data; it also means nothing stops a dangling link. Establish which
   it is, and whether anything cleans up.
3. **Migrations.** The revision exists and the two-heads problem above is
   established. What is *not* established is whether it downgrades, and
   whether `005_delta_tables` still applies once re-parented onto
   `008_release` — three migrations landed under it in the meantime.
4. **Test coverage of the new surface.** `tests/test_tui.py` changes by 55
   lines against 1,386 lines of new TUI code. Judge whether the untested part
   is untestable or merely untested, and say which.
5. **Does anything already report success while enforcing nothing?** The
   corpus's recurring defect. A phase guard that cannot fail, a link validator
   that accepts everything.

## How to establish anything you claim

The repo has a venv and a test suite:

```sh
cd <dossier>
uv sync                       # or: .venv/Scripts/python.exe -m pytest
.venv/Scripts/python.exe -m pytest -q
```

**Nothing has run against this branch** — no test, no lint, no review — because
it still has no pull request. Note the reason, because this page used to give a
different one: dossier *does* have CI now, four committed workflows on `main`
(`adr-lint`, `license-check`, `reuse-lint`, `submodule-check`), and both commands
quoted here as evidence return the opposite of what they returned when it was
written. The gap is the missing pull request, not a missing pipeline.
That raises the value of this handoff rather than lowering it, and it means
any suite result is one you produced yourself and should describe as such.

**One hazard, and it destroys data.** `pytest_configure` in
`tests/conftest.py` shells `dossier dev purge` against the operator's
`./dossier.db` before the run, and `pytest_unconfigure` repeats it after — on a
machine with real data, that data is gone. This is why no suite result appears
on this page: the session that restamped it read the branches and declined to
run the tests. Point the run at a scratch database, or accept the loss
knowingly.

For anything you assert about the branch's content, read
`wip/delta-entity-type-local:<path>`, not the working tree. The working tree is
whatever branch happens to be checked out, and reporting it as the repo's state
has already produced one false finding that reached `main` — and produced
another in qmcp the same week, where an uncommitted `docs/ROADMAP.md` claims a
phase the repository does not carry. See
[`qmcp-flows-as-deltas.md`](qmcp-flows-as-deltas.md).

## The same question, arriving from the other side

`project_delta`, `delta_link` and `delta_note` exist in a developer's
`dossier.db` today with **no models and no migration** on `main` — they are the
tables this branch adds models for. The disk tooling has since introduced its
own *delta* vocabulary for the difference between two measurements, so the two
now collide by name, and the orphan tables would appear as spurious drops in any
autogenerated migration diff.

That is [`disk-tooling.md`](disk-tooling.md) **item 3** — the page this one
used to cite as item 4, which is the per-project policy question and unrelated.
It asks whether those tables are live, dead, or in progress.

**They are in progress.** The branch that models them exists, carries a
migration for exactly those three tables, and is unmerged with no pull request
ever opened. So the migration adopts them rather than dropping them, and the
*delta* name collision with the disk tooling's own vocabulary is a naming
collision only. That answer holds until somebody abandons this branch, which
would make it a different answer and a `drop` migration.

## What to produce

A **draft PR** on `quaternionmedia/dossier`, base `main`, head
`wip/delta-entity-type-local` — pushed first, since it exists on no remote —
whose description is the review: what the branch does, what you verified and
how, what you found, and what you could not establish. Assign the person who
asked. Opening it requires dossier's slot, which #12 holds.

If the findings are small, say so plainly and recommend it lands. If they are
structural — particularly on the phase model, which is expensive to change
later — say that instead. **Do not** push fixes onto someone else's branch
without asking; report first.

## What is not yours here

Merging it. Rewriting its history. Deciding whether the delta concept is
right — that is a design decision for the person who wrote it; your job is to
make the trade-offs visible.
