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

*Stamped 2026-08-09; `dossier` main at `f055376`. Re-derive before acting — this
branch moved from 8 commits to 16 in under a day.*

| | |
|---|---|
| Branch | `origin/feature/delta-entity-type` |
| Size | 16 commits, 18 files, +2,392 / −318 |
| Position | 0 behind `main`, merges clean |
| PR | none |

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
3. **Migrations.** There is an `alembic/` directory. Does this branch add a
   revision, and does it downgrade? A table added without a migration is a
   schema that only exists on machines that ran the branch.
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

Its `🧪 Test` workflow needs Playwright browsers. If they are absent locally,
that is an environment difference and not a defect — say which you established.

For anything you assert about the branch's content, read
`origin/feature/delta-entity-type:<path>`, not the working tree. The working
tree is whatever branch happens to be checked out, and reporting it as the
repo's state has already produced one false finding that reached `main`.

## What to produce

A **draft PR** on `quaternionmedia/dossier`, base `main`, head
`feature/delta-entity-type`, whose description is the review: what the branch
does, what you verified and how, what you found, and what you could not
establish. Assign the person who asked.

If the findings are small, say so plainly and recommend it lands. If they are
structural — particularly on the phase model, which is expensive to change
later — say that instead. **Do not** push fixes onto someone else's branch
without asking; report first.

## What is not yours here

Merging it. Rewriting its history. Deciding whether the delta concept is
right — that is a design decision for the person who wrote it; your job is to
make the trade-offs visible.
