# Handoff — two dashboards, one dataset

**Stamped 2026-08-17. `qm` `main` at `fde5dfc`, this page on
`evolve/address-grammar` at `8388a69`.** Every figure was true at those commits.
Re-derive before quoting one.

**The milestone.** dossier's dashboard and qmcp's dashboard showing two views
into the same data, with active efforts and branches listed as deltas.

**What this page is not.** The milestone. It is the foundation the milestone
needs, which is now built, plus the four things that are not.

---

## What was blocking it, and is not any more

Two views of one dataset need one way to name a row. Neither system had one.

dossier built names by interpolation in `parsers/autolinker.py` and read them
back by substring in `cli.py` — `elif "/branch/" in name`. qmcp named nothing:
a step was a bare `name`, an invocation a bare UUID.

Worse, dossier's branch address was **not reversible**. It slugged with
`branch.name.replace("/", "-")`, so `evolve/protect-main` became
`.../branch/evolve-protect-main`, indistinguishable from a branch legitimately
named that. **30 of the 32 branches in this corpus contain a slash.** Listing
branches as deltas means linking a row back to a ref, and that link was broken
for nearly every branch in the organisation.

`docs/ref/addresses.md` is the grammar:

```
<owner>/<repo>/<kind>/<id>
```

First three segments are owner, repo, kind. **Everything after is the id,
verbatim, slashes included.** `uv run qm addresses --parse <address>` reads one;
`--check` runs the shared vectors.

Kinds: `branch`, `pr`, `issue`, `ver`, `doc`, `delta`, `invocation`. The last two
are the ones this milestone needs.

## The four pieces that exist

| piece | where | state |
|---|---|---|
| the grammar | `docs/ref/addresses.md` | on `evolve/address-grammar`, no PR |
| reference implementation | `ci/addresses.py`, 33 tests, 35/44 mutants killed | same |
| shared conformance vectors | `project-seed/address-vectors.json`, 20 cases | same |
| step ↔ delta mapping | `qmcp/cookbook/delta.py`, 24 tests | on qmcp #21, pushed |

The vectors ship through the governance submodule, so a fork receives them at
`governance/qm/project-seed/address-vectors.json`. **Nothing imports the
reference implementation.** Each system implements the grammar and runs the same
cases — the same trade `qmcp/cookbook/delta.py` makes for the delta schema, and
for the same reason: an import would mean neither project ships without the
other.

## What the milestone still needs

**1. dossier reads and writes addresses.** Replace the interpolation in
`parsers/autolinker.py` and the substring chain in `cli.py` with one
implementation, and run the shared vectors against it in dossier's own suite.
*Done:* dossier's tests include the vector file and pass.

**2. Existing rows are migrated, or declared unmigrated.** Every branch address
already in a dossier database was written by the slugging code. They are not
addresses under this grammar and cannot be recovered into ones — `evolve-protect-main`
does not say which branch it meant. *Done:* either a migration that re-derives
them from the git refs, or a recorded decision that pre-grammar rows are
re-synced rather than converted. **Do not write a converter that guesses.**

**3. qmcp emits addresses.** `to_delta` carries `project` as `owner/repo` and a
delta `name`; the address is `<project>/delta/<name>` and the invocation link is
`<project>/invocation/<id>`. Both are one `format_address` call away and neither
is made yet. *Done:* the delta payload carries addresses, and its schema version
moves to 2.

**4. Each dashboard renders the other's rows.** Only after 1–3. An active effort
is a branch with an open pull request; a delta is the unit of work behind it; the
address is what lets one row appear in both views.

## What this cannot do, and should not be asked to

**Resolve.** `quaternionmedia/qm/pr/99999` is well-formed and denotes nothing.
The grammar deliberately says nothing about existence — folding a lookup in
would make every dashboard render depend on a network call.

**Say which view is right.** dossier's row for a branch and the git ref can
drift. The address makes the disagreement expressible and is silent on who wins.
That is a real decision and nobody has taken it: **when the two dashboards
disagree about the same address, which one is the source?** It should be settled
before either dashboard is built, not after they disagree in front of somebody.

## Blocked on a human

- **`main`'s slot** holds #66, so `evolve/governance-protocols` and
  `evolve/address-grammar` are pushed with no pull request. The second is
  stacked on the first: `check_pr_base` reports 8 of its 9 commits also live
  there, and they must land in that order.
- **A record for the grammar.** It binds two projects and lives in `docs/ref/`
  with no decision behind it. The same is true of `SCHEMA = 1` in
  `qmcp/cookbook/delta.py`. Both want records; `project/qmcp` holds its own slot
  and is available now.
- **Neither project gates its tests.** No `pytest` step exists in either
  repository's workflows, so every test named on this page runs on one machine
  and nowhere else.
