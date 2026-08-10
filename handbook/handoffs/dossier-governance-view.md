# Handoff — Render the governance document in dossier

**Goal.** dossier reads `governance-status.yaml` and shows one view of it:
which projects are current, which have drifted, and what nobody has measured.

**The document now exists** — `governance-status.yaml`, emitted by
`ci/governance_status.py`, with `ci/governance_render.py` as a first reader you
can read for reference and are expected to eventually replace. Its contract is
`handbook/handoffs/governance-status-generator.md`.

**A first cut is delivered as dossier#10**, draft and assigned. *Stamped
2026-08-10; `dossier` `governance/status-view` at `651ea01`, off
`governance/adopt-corpus`. Re-derive before acting.*

| Piece | Where |
|---|---|
| Parser for both documents | `src/dossier/parsers/governance.py` |
| Read model, two tables | `src/dossier/models/governance.py` |
| Load and presentation | `src/dossier/governance.py` |
| Migration `005_governance`, chained to `004_full_name` | `alembic/versions/` |
| `governance load` / `show` / `threads` | `src/dossier/cli.py` |
| Governance tab | `src/dossier/tui/app.py` |
| 53 tests, weighted to the red paths | `tests/test_governance.py` |

It reads both documents, which departs from this page's "take the harness
document second" — the work it was asked for was the threads view, and the
governance view alone does not deliver it. One parser reads both, which is
what this page says the shared `unknown` convention is for. Whether they
should have stayed one entity is a reviewer's call; the cost of the departure
is a second table, `governance_thread`.

Verified: 52 passed and 1 skipped, run twice with identical results. The skip
reads the real vendored documents and correctly skips because the pin predates
them. Nine mutations were run against the suite and all nine were caught — a
slot fallback to `ok`, an unconditional thread delete, dropping the
intermediate unknown check, rendering unknown as blank, importing `subprocess`
into the renderer, reversing the generator order, dropping the app's hand-over
of the governance row, and forcing the coverage column to always say synced.
`run_workflows_locally.py` in dossier: 8 steps, 7 pass, 1 fails on the unpushed
submodule pin.

One command does the whole loop: `dossier governance dashboard` finds the
corpus (current directory, then `governance/qm`, then `../qm`), regenerates both
documents, loads them, and opens on the Governance tab. It prints which corpus
it chose and that a refresh leaves a diff. `--no-refresh` reads what is on disk.

It is joined to dossier's own data, at read time and never by a stored key,
because `github sync` rebuilds the project tables and would destroy anything
hung off them:

* the **Details** tab shows the selected project's governance state
* an **IN DOSSIER** column shows which governed repositories this store holds
* thread pull-request numbers dim when the store has not synced them
* matching is ranked `slug > repo name > name > trailing name` and renders the
  rule that fired, so a weak match reads as a guess rather than a link

No new tab was added for any of it.

**Still open from this page's own list**: the delta branch is unreviewed, so
the tab is written against `main`'s flat `#project-tabs` and will need the
nested `#main-tabs` treatment if that branch lands. One parser precedent was
chosen deliberately — a plain class, like `GitHubParser`, because `BaseParser`
dispatches on file extension and returns `DocumentSection`s.

Read `handbook/handoffs/README.md` first.

---

## Read this before choosing a table

**`dossier github sync` is delete-and-repopulate.** It empties and rebuilds
`ProjectBranch`, `ProjectPullRequest`, `DocumentSection`, `ProjectIssue`,
`ProjectContributor`, `ProjectLanguage`, `ProjectDependency` and
`ProjectRelease` on every run (`cli.py`, the sync command). Any governance state
written into one of those is destroyed the next time somebody syncs, silently
and completely.

So governance state goes in a table sync does not touch — even though
`ProjectBranch` and `ProjectPullRequest` look like the natural homes and an
earlier version of this page recommended them. Establish this yourself before
building; it is the single constraint that decides the schema.

Three more conventions, each of which reads the opposite way at a glance:

- **Zero ORM relationships.** `Relationship` is imported in
  `src/dossier/models/schemas.py` and never called; every join is a manual
  `select(X).where(X.project_id == ...)`. The import makes grep look like a hit.
- **Two competing parser precedents.** `MarkdownParser` subclasses `BaseParser`
  and is registered in `ParserRegistry.default()`; `GitHubParser` subclasses
  nothing, is registered nowhere, and is imported directly by the CLI. Pick one
  deliberately and say which.
- **The test suite purges the developer's real database.** `pytest_configure`
  shells `dossier dev purge` against `./dossier.db` before and after every run.
  Know that before you run it on a machine with data you care about.

## Scope, deliberately small

**One parser, one entity, one view.** Nothing else until it has been used for a
week. The temptation is to model governance richly on day one; the corpus's own
history says the useful shape is discovered by using the plain one.

- A parser reading the document. It parses YAML; it does not talk to git or to
  GitHub.
- The smallest schema addition that holds it, in a table `github sync` does not
  rebuild, plus one alembic revision chained to whatever is head at the time
  (`005_delta_tables` if the delta branch has landed).
- One TUI tab. **The tab topology differs between refs** — `main` has a flat
  `#project-tabs`, and `feature/delta-entity-type` restructures it into nested
  `#main-tabs`. Code written against one silently fails to activate on the
  other, which is the other reason the delta branch is reviewed first.

### Every field may be `{unknown: <reason>}`

Not just the ones that look optional. `behind_corpus` is an integer or the
mapping `{unknown: "..."}`; `open_prs` is a list or that same mapping. An `int`
column cannot hold it, and a reader that coerces gets a blank — and blank reads
as fine. Type-check every field, and keep the reason: a nullable value column
beside an `unknown_reason` column preserves the distinction across the
relational mapping.

`null` is not unknown. `last_propagation: null` means *never propagated*, which
is an established fact.

## The distinction to preserve

**Status is observed; a delta is intended.**

*"apothecary is 62 behind"* is a fact the generator derives and this view
displays. *"Bring apothecary current"* is work, with a lifecycle and links to a
PR — which is what `Delta` already models.

Conflating them produces a tracker that argues with reality: a row a human has
marked done while the world still reports it undone, and no way to tell which
is wrong. Keep the generated status read-only in dossier. If a view wants to
show both, it joins them; it does not merge them.

## What the view must not do

**Never write back to the document.** It is generated. A renderer that edits
its own input creates a second source of truth for the same fact, which is the
thing the seam exists to prevent.

**Never re-derive a governance fact.** If the view wants something the document
lacks — say, how long a branch has been behind — that is a change to the
generator in qm, one place, reviewed once, and every reader gets it. A
convenience computation in the renderer is a second definition of a governance
rule.

**Never present a stale document as current.** The document carries
`generated_at` and per-project `observed_at` precisely so a view can say how
old it is. Show that. A dashboard that looks live and is three days old is
worse than one that admits its age, because the first stops people checking.

## Red paths, which apply here too

The renderer needs its own fixtures, for the same reason the generator does:

| Case | What the view must do |
|---|---|
| document absent | say so; not render an empty happy table |
| document older than a threshold | show its age prominently, not silently |
| a project reporting `unknown` | render as unknown, distinct from healthy |
| a project with drift | visibly distinct from one without, in form as well as text |

The third and fourth are where a dashboard usually fails: `null` renders as
blank, blank reads as fine, and a project nobody could measure looks identical
to one that is healthy.

## Verification

Run dossier's own suite, and the corpus runner if dossier has adopted by then:

```sh
uv sync && .venv/Scripts/python.exe -m pytest -q
python governance/qm/project-seed/ci/run_workflows_locally.py
```

dossier had no CI of its own before adoption; the workflows it has now are
the seed's three plus a dependency-licence gate, all added by the adoption
round. There is no `🧪 Test` workflow, so a green suite here is one you ran
yourself.

Before running it: `pytest_configure` in `tests/conftest.py` shells
`dossier dev purge` against the operator's `./dossier.db` both before and
after the run. On a machine with real data, that data is gone.

## There is a second document now, and it is the same shape

`harness-status.json`, emitted by `ci/harness_status.py`, reports where every
repository stands against the one-open-pull-request-per-contributor rule.
`ci/harness_dashboard.py` is its first reader, exactly as `governance_render.py`
is `governance-status.yaml`'s, and it is built to be replaced the same way —
`--fragment` emits the page without a document shell, for a host that supplies
its own.

**Take it second, not first.** One parser, one entity, one view still holds;
land the governance view, use it for a week, and only then decide whether the
harness document is a second parser or a second entity behind the same one.

Two things about it that change how you would model it:

- **It has two layers with different scopes.** `slots` is read over the network
  and is true for everyone. `local` is one machine's clones and is true for
  whoever ran the collector. They are in one document because they are read
  together, but a row that merges them is a row that claims org-wide standing
  for a fact about somebody's laptop. `generator.local_layer_scope` carries the
  caveat; a view that drops it has lost the only thing separating the two.
- **`{"unknown": "<reason>"}` is the same convention** as
  `governance-status.yaml`, deliberately, so one parser shape reads both. The
  table above applies unchanged: unknown renders as unknown, never as blank and
  never as healthy.

## What is not yours here

Changing either document's schema — that is the generator's handoff, and a
renderer that needs a schema change files it there. Deciding what a governance
signal means. And, as always: no merging, no ratifying, one draft PR per repo.
