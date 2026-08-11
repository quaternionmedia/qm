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

## The work is delivered

*Stamped 2026-08-10. `qm` `project/dossier` at `a9a6e33`, `dossier`
`governance/status-view` at `651ea01`. Every number here is true at those
commits and nowhere else — re-derive before acting, and do not quote a figure
from this page as current.*

**Keep everything local was in force while this was built, and was relaxed on
2026-08-10 for pull request maintenance only.** The relaxation is not general:
it covers pushing to and adding commits to a pull request that already exists,
plus the one project-governance draft below. It does not authorise opening
further pull requests anywhere.

| Branch | Repo | Head | Carries | State |
|---|---|---|---|---|
| `project/dossier` | qm | `a9a6e33` | 3 commits, 3 files, all under `adr/` | pushed, no PR — a long-lived project branch, per the fork procedure's step 2 |
| `governance/status-view` | dossier | `651ea01` | 9 commits, 30 files | pushed, **dossier#10**, draft, assigned |
| `governance/adopt-corpus` | dossier | `5278a4d` | the adoption half, an ancestor of the above | local only; #10 carries its commits |
| `wip/delta-entity-type-local` | dossier | `3dc8192` | see the delta-review page | local only, deliberately |

Both branches are cut from their base tip with no unrelated commits, by
`check_pr_base.py`. While a branch is unpushed that check needs
`--remote refs/heads`, because it prefixes the remote unconditionally and
`origin/<head>` does not resolve for a branch that does not exist yet.

**`project/dossier` is pushed without a pull request, and that is worth a
reviewer's attention.** The fork procedure says to create the branch and push
it, and other `project/*` branches exist that way; the constitution says
everything arrives as a pull request. A pull request from `project/dossier`
into `main` would merge one project's records into the corpus, which the
branch-per-project model exists to prevent — so the two rules cannot both be
followed literally here. The three commits it carries touch `adr/` and nothing
else, and the ADR lint runs against them from dossier's own workflow. If the
intended shape is different, say so before the branch is pinned any further:
rewriting a branch a submodule pins is forbidden.

**What remains**: leaving dossier#10 draft is the assignee's decision, after
their own testing. Nothing else is outstanding on this page.

## What the gates said

`run_workflows_locally.py` in dossier: **8 steps, all pass**, once
`project/dossier` was pushed — `submodule-check.yml` was the one red gate and
it was red correctly, because the pinned corpus commit did not exist on the
corpus remote. In the corpus on `project/dossier`: 7 steps, all pass. The
runner reproduces neither `uses:` steps, the runner image, nor secrets.

The ADR lint runs from the submodule and reports `clean (governance/qm/adr/)`,
which is the arrangement working: the project's workflow lints the records on
the corpus branch, so the corpus's own `adr-lint.yml` does not need to.

## Where it actually stands, re-derived

*`dossier` main at `f055376`.*

| | |
|---|---|
| Adopted before this work | no — no `.gitmodules`, no `AGENTS.md`, no `governance/` |
| Workflows | **none.** `gh api repos/quaternionmedia/dossier/actions/workflows` returns one entry, GitHub's dynamic `Dependabot Updates`. `git ls-tree -r origin/main .github` returns only `copilot-instructions.md` |
| Shape | Python 3.13, SQLModel + Alembic, Textual TUI, FastAPI, `uv` |
| Open PRs | five, all Dependabot, all bot-authored and therefore outside the slot rule |

**dossier had no CI at all**, which changes two things a reader would
otherwise assume. There is no `test.yml` and no `🧪 Test` workflow anywhere in
the repository, so the seed's workflows are pure additions with nothing to
deduplicate against — the "look for the behaviour before the filename" caution
has nothing to bite on here. And nothing has ever run against
`feature/delta-entity-type`.

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

Both questions are carried as the adoption record's `Pends on` and as conflict
C1 in its table. Neither was settled by the drafting.

`REUSE.toml` and `LICENSES/` now exist, and `reuse lint` passes at 60 of 60
files. The seed's workflow went in **blocking** rather than in reporting mode,
because the licensing pass finished in the same round — `continue-on-error` on
a lint that already exits 0 installs a check that cannot fail. REUSE checks
that copyright information is present, not whose name it carries, so C1 does
not hold it red.

## Two decisions surfaced rather than settled

**Which class dossier's own code falls into.** The outbound record has
`AGPL-3.0-or-later` for services and control planes, `MIT` only via the
hardware clause and named embeddable libraries. dossier is a local-first CLI
and TUI, not a hosted service — so the record does not obviously cover it, and
its existing MIT declaration may or may not survive contact with §4. It also
ships a FastAPI application, which a reader could fairly call a service. Named
as a gap; not picked.

**What its ADR-0001 says.** dossier predates its adoption, so the discipline
record's §5 applies and the record's substance is a conflict table: eight rows,
three closed by the adoption round and five open. Three of the five (Textual
and Trogon outside the blessed set, `uv`/`hatchling` against the record's PDM,
and the GitHub API as a single-vendor seam) cannot be closed inside dossier at
all — two need an org-level record and one needs an architecture change.

## Verification specific to this repo

Beyond the fork procedure's own checks:

```sh
git check-ignore AGENTS.md CLAUDE.md .github/copilot-instructions.md \
  .vscode/settings.json .vscode/extensions.json    # exit 1 = nothing swallowed
git ls-files -s CLAUDE.md .github/copilot-instructions.md   # expect mode 120000
python governance/qm/project-seed/ci/run_workflows_locally.py
```

Use `git check-ignore` **without** `-v` here. With `-v` git prints negation
matches too and exits 0, so a repository that has applied the negation fix
reads as still broken.

dossier's `.gitignore` excluded `.vscode/` wholesale — the alfred-class trap,
by a third distinct rule. The fix is not the one the fork procedure states:
git will not re-include a file whose parent directory is excluded, so a
negation under `.vscode/` is inert. The rule has to exclude the directory
*contents*, `.vscode/*`, for the negations below it to do anything.

The submodule was cloned from a path on disk, because `project/dossier` is not
pushed. Its `origin` is the canonical remote and the phantom
`origin/project/dossier` the local clone left behind has been deleted, along
with its branch upstream and the copied `origin/HEAD`. So `git status` inside
`governance/qm` now reports no remote counterpart, which is true. If you
re-clone or re-add the submodule from disk, this comes back — the procedure's
step 3 carries the four commands.

`governance/qm` is a fresh clone and does not inherit `core.symlinks`, so the
seed's own pointer files inside the submodule materialise as one-line text
stubs on Windows even when the superproject is set up correctly. Copying from
them without checking produces a regular file where a symlink belongs. Both
pointer files here were written as symlink objects directly, and their blob
SHAs match the seed's.

## Blocked on a human, and named rather than guessed

1. **Lifting *keep everything local*.** Nothing moves until this happens.
2. **How `project/dossier` is delivered.** The fork procedure's step 2 says to
   push the branch, and the other `project/*` branches exist that way. The
   constitution says everything arrives as a pull request. Those pull the same
   branch two ways, because a PR from `project/dossier` into `main` would merge
   one project's records into the corpus, which is the one thing the
   branch-per-project model exists to prevent. The two shapes that work are:
   push `project/dossier` as a new long-lived branch and review the records on
   it afterwards; or push it at `b94d910` carrying nothing, and open a draft PR
   with base `project/dossier` and an `evolve/*` head carrying the three
   commits, which earns its own slot under the per-base exemption. This is a
   reviewer's call about how the corpus is governed, not a drafting detail, and
   it was left rather than picked.
3. **The two licensing questions**, carried as the record's `Pends on` and as
   conflict C1.
4. **C2 and C3 need an org-level record**, not a change in dossier: the
   house-stack record places additions at org level, and dossier uses Textual,
   Trogon and `uv`/`hatchling`. apothecary also uses `uv`, so the packaging
   question already has two instances and is a candidate for one org record
   covering both.

## What the harness does not yet reach

`project/dossier` is cut from `main`, and **`main` has no harness**: no `ci/`
directory, no `governance-status.yaml`, no `harness-status.json`, and nothing
in `project-seed/ide/.claude/commands/`. All of it is on
`evolve/ci-tooling-fixes` (#36). So a session opening dossier today gets
governance discovery and four working gates, and does not get `/cowork`, the
slot check, or anything to render.

That is the propagation path behaving correctly rather than a gap in this
work, and it makes the ordering explicit: **#36 landing on `main` is the single
thing between here and a governance view with data**. After it lands, bump this
project's pin and the rest arrives.

## Marked as inference, not established

- That the delta branch's 1,833 uncommitted lines are abandoned rather than
  in-progress. Their file mtimes are 2026-01-25 to 2026-02-01 and the branch's
  last commit is 2026-01-25; nothing establishes intent, and they were
  committed to a `wip/` branch rather than judged.
- That `reuse lint` passing means dossier's licensing is *correct*. It
  establishes that every file carries copyright and licence information and
  that every identifier used has its text present. It says nothing about
  whether MIT is the right class or whose name belongs on it, which is exactly
  what C1 and the `Pends on` hold open.

## What is not yours here

Ratifying its records. Choosing the licence class. Answering the copyright
question. Deciding whether dossier is a service under the outbound record —
that reading changes what licence it carries, and it belongs to a human.
Pushing either branch, while local-only stands.
