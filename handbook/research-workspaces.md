# Handbook — Research Workspaces and Parallel Exploration

**Routing.** Operational standard, not a decision record: it weighs no
alternatives and creates no constraint a project could violate. It completes
the branch-namespace rules `README.md` states, and names the mechanism for a
direction those rules left unwritten. If it ever needs adjudicable teeth — a
dispute about whether a workspace's contents bind anything — it is promoted to
a record and this page becomes a pointer.

**Audience.** Anyone, human or agent, contributing to a research workspace, and
anyone reviewing what arrives from one.

---

## What a workspace is

A `workspace/<slug>` branch holds open-ended research: demonstrations designed
against questions a perspective raised, simulations, measurement scaffolding,
notes that are not yet anybody's position. `workspace/math-experiments` is the
first, and holds the experiment designs for the mathematical-limits
perspective.

**A workspace binds nothing.** `records/` is the only binding directory in this
corpus, and a workspace is further from binding than `perspectives/` — a
perspective is at least one named person's stated view on a stated date, while
a workspace is a place to find out. Nothing in a workspace may be cited as
though it settled anything.

That is what makes the rest of this page safe. Every relaxation below is
purchased by the fact that a workspace cannot reach `main`.

## A workspace has two directions, and both are named

| Direction | Rule |
|---|---|
| workspace → `main` | **Never.** The branch is terminal. Content that should bind is rewritten and lifted to `main` on an `evolve/<slug>` or `perspective/<date>-<slug>` branch, on its own merits |
| `main` → workspace | A `propagate/<slug>-<date>` pull request, base the workspace branch — the same mechanism, and the same rules, as propagation into `project/<name>` |
| exploration → workspace | A `math/<slug>` pull request, base the workspace branch |

The second row is the one worth stating plainly, because "never merges back"
describes only the first. A workspace that takes nothing in falls behind `main`
silently, and what it falls behind on is the gates: a workspace seeded before a
workflow existed has no `.github/` directory, so the checks the rest of the
corpus relies on do not exist there to run. Propagate on the same trigger you
would use for a project branch — a ratification, a seed change, or a gate the
workspace should be subject to.

Merge, never rebase, for the same reason as a project branch: an exploration
cut from the workspace is invalidated by a rewrite of its base.

## Explorations run in parallel, by design

An exploration is one line of enquiry against one workspace, on a
`math/<slug>` branch. **Several are expected to be open at once** — that is the
purpose of the namespace, not a tolerated side effect. Two people, or two
agent sessions, taking two topics from the same menu are doing the intended
thing.

| | |
|---|---|
| **Cut from** | the workspace branch it targets, never `main` |
| **Base of its pull request** | that workspace branch, never `main` and never a `project/<name>` |
| **Lifetime** | deleted after merge into its workspace |
| **Slot** | its own — see below |
| **Naming** | `math/<slug>` for the mathematics workspace. A second research workspace takes its own namespace by the same pattern, added to `README.md`'s table before it is used |

**The one-open-pull-request rule does not count an exploration.** The slot rule
exists so a reviewer is never handed a sequencing puzzle on binding work.
Explorations are neither sequenced nor binding: each is independent of its
siblings, and none can reach `main` from where it sits. Counting them would
make the namespace useless for the one thing it is for.

Mechanically, `check_one_pr.py --per-head 'math/*'` gives each exploration its
own slot. That is a *head* exemption rather than the `--per-base` one the
`project/*` branches use, because every exploration shares a single base —
a base exemption would collapse all of them into one slot and change nothing.

A head exemption is the wider of the two, and it is bounded by what the glob
can name: point it only at a namespace whose branches cannot reach the default
branch. `math/*` qualifies because a math branch's only legal base is a
workspace branch, and a workspace branch is terminal.

## What still applies

Everything in `AGENTS.md` that is not the slot rule. In particular:

- **Human-only contributorship.** No co-author trailer naming a model or an
  unmonitored address, on any commit, including here.
- **Drafts, and no review request.** `gh pr create --draft`, assignee the
  person who asked, no reviewer.
- **A pull request states decisions, not questions.** An exploration whose
  result is "this does not work" is a decision and is worth merging. An
  exploration that arrives asking what it should have been is not.
- **Say what you ran.** A workspace is where unproven things live, which makes
  the distinction between what was run and what was reasoned the whole value of
  the artifact. Mark it.

## What this page does not authorise

Merging any workspace or exploration branch into `main`, by any route.
Treating a workspace result as a record, a policy, or a settled fact. Deleting
a workspace branch — it is permanent, and an exploration deleted after merge is
not the same thing. Rewriting a workspace branch's history, which invalidates
every exploration cut from it.
