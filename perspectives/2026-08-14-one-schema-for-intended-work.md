# One Schema for Intended Work

| | |
|---|---|
| **Date** | 2026-08-14 |
| **Author** | Peter Kagstrom |
| **Status** | Unreviewed |
| **Binds** | Nothing. `perspectives/` is opinion. |
| **Tools** | An assistant, which found the collision and performed the merge |

---

## Two designs for the same thing, written a week apart

`dossier`'s `wip/delta-entity-type-local` carries `ProjectDelta`, `DeltaNote`
and `DeltaLink`: a change-management entity with a lifecycle
(`brainstorm → planning → implementation → review → documentation → complete`,
plus `abandoned`), phase-stamped markdown notes, and a loose join to issues,
pull requests, branches, docs and other deltas.

`perspectives/2026-08-13-the-mechanical-governance-loop.md` specified
`SessionArtifact` and `BreakObservation`: one row per session, and one row per
protocol break within it, carrying a pattern, a shape, a counterfactual and a
cost.

The plan document mentioned `delta` nowhere — `grep -i delta` over it returned
nothing. The two were written independently, both propose a table for *intended
or recorded work* in the same database, and both need `dossier`'s single pull
request slot. Nobody had decided whether they were one schema or two.

The reviewer decided: one.

## Why they merge cleanly

`DeltaNote` and a session artifact are the same row. Both are a phase-stamped
record attached to a unit of work — one written by a person during planning, one
emitted by a session during implementation. The difference is provenance, which
is a column.

So:

- `ProjectDelta` is unchanged. The loop's aggregations are queries over
  `BreakObservation` joined through `DeltaNote`, not columns on the delta.
- `DeltaNote` gains five nullable columns: `source` (`human` | `session`),
  `repo`, `branch`, `artifact_path`, `imported_at`.
- `BreakObservation` is the one new table, keyed on `delta_note.id`.
- `SessionArtifact` does not exist.

Two schemas would have meant two migrations, two sync paths, two dashboard
panels, and a decision in every session about which table a thing belongs in.
That last cost is the one that compounds.

## The decision inside the decision

`DeltaNote.delta_id` stays non-nullable, so every session artifact attaches to a
delta. `governance loop sync` creates one — `delta_type="session"`,
`phase=implementation` — for a session not already working a delta.

The alternative was a nullable `delta_id`, which is less constraining and was
rejected for two reasons. `DeltaNote.phase` has no meaning without a parent, so
nullable rows carry an unreadable column. And a break that is not attached to
the work it happened during cannot answer the question the loop exists to
answer, which is what a given kind of work keeps costing.

## What this costs, stated plainly

The governance loop's Phase 2 now depends on `wip/delta-entity-type-local`
landing, which it did not before. That branch exists on no remote, is 17 ahead
and 16 behind `origin/main`, and has never had a pull request opened against it.
The ordering is: `dossier` #12 lands, the delta branch is pushed and reviewed
and lands, then Phase 2.

That is a longer chain than the two-schema version. It is the price of the
merge, and it is worth naming rather than discovering.

## One thing found on the way, not fixed

`ProjectDelta.phase` is a plain column and `advance_phase()` is a helper. The
helper refuses to move an `abandoned` delta and returns `False` at `complete`;
nothing stops an assignment to `self.phase` that skips a phase, reopens a
completed delta, or revives an abandoned one.

That is true today with one writer. Under this layer `governance loop sync` is a
second writer, and the guard's placement decides whether it holds at all. It
belongs to the delta branch's review, which has not happened — that branch has
never had a pull request, so no test, no lint and no reader has been near it.
Pushing a fix onto someone else's unreviewed branch is not this session's call.
