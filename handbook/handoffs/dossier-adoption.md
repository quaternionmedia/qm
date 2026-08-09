# Handoff — Adopt the constitution in dossier

**Goal.** Bring `quaternionmedia/dossier` under the corpus: a `project/dossier`
branch here for its `adr/`, the submodule and seed in its own repo, and its
first records.

**Why.** dossier is about to become the surface on which this org reviews its
own governance. A tool reporting on adoption while unadopted is an
inconsistency somebody will notice, and it is the kind that erodes the rest.

Read `handbook/handoffs/README.md` first. The procedure itself is
`handbook/forking-a-project.md` — **follow that, do not improvise from this
page.** What follows is only what is specific to dossier.

---

## Where it actually stands

*Stamped 2026-08-09; `dossier` main at `f055376`. Establish all of this yourself
before acting — read `origin/main:<path>`, never the working tree.*

| | |
|---|---|
| Adopted | no — no `.gitmodules`, no `AGENTS.md`, no seed CI |
| Workflows | `test.yml` and dependabot; none from the seed |
| Shape | Python 3.13, SQLModel + Alembic, Textual TUI, FastAPI, `uv` |
| Open PRs | several dependabot; one feature branch with no PR |

## The licensing wrinkle, which is not apothecary's

apothecary had no `LICENSE` at all. dossier **has one** — 21 lines, canonical
MIT, which GitHub classifies as `mit`. The wrinkle is not detection; it is
whose name is on it and whether MIT is the right answer.

**The copyright holder disagrees with the corpus.** `Copyright (c) 2026 Peter
Kagstrom`. The outbound-licensing record §0 places copyright in **Quaternion
Media**, and `quaternionmedia/datum` already carries that form. dossier names an
individual instead. That is a real question for a human, not a typo to fix in
passing — it is the same question the record's own `Pends on` raised, and it was
answered for the corpus, not necessarily for every repo.

There is no `REUSE.toml` and no `LICENSES/`, so the outbound record's §12 gate
has nothing to run against yet. Add them the way apothecary's PR did, in
reporting mode first.

## Two decisions to surface rather than settle

**Which class dossier's own code falls into.** The outbound record has
`AGPL-3.0-or-later` for services and control planes, `MIT` only via the
hardware clause and named embeddable libraries. dossier is a local-first CLI
and TUI, not a hosted service — so the record does not obviously cover it, and
its existing MIT declaration may or may not survive contact with §4. Name the
gap; do not quietly pick.

**What its ADR-0001 says.** Conventionally the adoption + scope record. dossier
is unusual in that it will *report on* the corpus, so its scope record is worth
writing carefully: what it observes, what it asserts, and explicitly that it
renders a document rather than deciding governance itself.

## Verification specific to this repo

Beyond the fork procedure's own checks:

```sh
git check-ignore -v AGENTS.md CLAUDE.md .github/copilot-instructions.md \
  .vscode/settings.json .vscode/extensions.json    # exit 1 = nothing swallowed
git ls-files -s CLAUDE.md .github/copilot-instructions.md   # expect mode 120000
python governance/qm/project-seed/ci/run_workflows_locally.py
```

dossier already has a `test.yml`. The seed's three workflows are additions, not
replacements — but **look for the behaviour before looking for the filename.**
If `test.yml` already does something the seed workflow also does, replace
rather than run both; two checks disagreeing about one rule is worse than one
that is out of date.

## What is not yours here

Ratifying its records. Choosing the licence class. Answering the copyright
question. Deciding whether dossier is a service under the outbound record —
that reading changes what licence it carries, and it belongs to a human.
