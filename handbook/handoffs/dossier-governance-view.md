# Handoff — Render the governance document in dossier

**Goal.** dossier reads `governance-status.yaml` and shows one view of it:
which projects are current, which have drifted, and what nobody has measured.

**Blocked on all three of the other handoffs.** There must be a document to
render, a reviewed schema to render it into, and — per the decision already
taken — a repo that has adopted the corpus it reports on. Do not start this one
by generating the data yourself; that is the seam this design exists to avoid.

Read `handbook/handoffs/README.md` first.

---

## Scope, deliberately small

**One parser, one entity, one view.** Nothing else until it has been used for a
week. The temptation is to model governance richly on day one; the corpus's own
history says the useful shape is discovered by using the plain one.

- A parser beside `src/dossier/parsers/github.py`, reading the document.
- The smallest schema addition that holds it. Most of the content maps onto
  rows dossier already syncs — `Project`, `ProjectPullRequest`,
  `ProjectBranch` — so the genuinely new state is a per-project governance
  record plus one corpus-level row. Resist adding a table per nested key.
- One TUI tab: the project table, ordered by what needs attention rather than
  alphabetically.

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

Its `🧪 Test` workflow needs Playwright browsers; absent locally, that is an
environment difference rather than a defect — report which you established.

## What is not yours here

Changing the document's schema — that is the generator's handoff, and a
renderer that needs a schema change files it there. Deciding what a governance
signal means. And, as always: no merging, no ratifying, one draft PR per repo.
