# Handbook — Research Workspaces and Explorations

**Routing.** Operational standard, not a decision record: it weighs no
alternatives and creates no constraint a project could violate. It completes
the branch rules [`docs/ref/namespaces.md`](../docs/ref/namespaces.md) states,
and names how a workspace takes changes in. If it ever needs adjudicable
teeth — a dispute about whether a workspace's contents bind anything — it is
promoted to a record and this page becomes a pointer.

**Audience.** Anyone, human or agent, contributing to a research workspace, and
anyone reviewing what arrives from one.

---

## What a workspace is

A `workspace/<slug>` branch holds open-ended research: demonstrations designed
against questions a perspective raised, simulations, measurement scaffolding,
notes that are not yet anybody's position. `workspace/math-experiments` holds
the experiment designs for the mathematical-limits perspective.

**A workspace binds nothing.** `records/` is the only binding directory in this
corpus, and a workspace is further from binding than `perspectives/`: a
perspective is at least one named person's stated view on a stated date, while
a workspace is a place to find out. Nothing in a workspace may be cited as
though it settled anything.

That is what makes its explorations safe to run side by side: none of them can
reach `main`.

## A workspace has three directions, and each is named

| Direction | Rule |
|---|---|
| workspace → `main` | **Never.** The branch is terminal. Content that should bind is rewritten and lifted to `main` on an `evolve/<slug>` or `perspective/<date>-<slug>` branch, on its own merits |
| `main` → workspace | A `propagate/<slug>-<date>` pull request, base the workspace branch: the same mechanism, and the same rules, as propagation into `project/<name>`. `<slug>` is the workspace's, and shares the `propagate/` namespace with every project's name, so the two sets may not collide |
| exploration → workspace | A `math/<slug>` pull request, base the workspace branch |

"Never merges back" describes only the first row. A workspace runs only the
workflows it holds, so one that takes nothing in runs none of the checks added
to `main` since it last did. Propagate on the same trigger as for a project
branch: a ratification, a seed change, or a gate the workspace should be
subject to.

Merge, never rebase, for the same reason as a project branch: an exploration
cut from the workspace is invalidated by a rewrite of its base.

## Explorations

An exploration is one line of enquiry against one workspace, on a
`math/<slug>` branch. **Several are open at once by design**: two people, or
two sessions, taking two topics from the same workspace are doing the intended
thing. Each is its own pull request into the workspace and independent of its
siblings, so none is stacked, and each is marked ready once it is done
([`handbook/async-contract.md`](async-contract.md) §1).

| | |
|---|---|
| **Cut from** | the workspace branch it targets, never `main` |
| **Base of its pull request** | that workspace branch, never `main` and never a `project/<name>` |
| **Lifetime** | deleted after merge into its workspace |
| **Naming** | `math/<slug>` for the mathematics workspace. A second research workspace takes its own namespace by the same pattern, added to [`docs/ref/namespaces.md`](../docs/ref/namespaces.md) before it is used |

**The base is checked.** `uv run qm branch` (`project-seed/ci/check_pr_base.py`)
refuses a `math/*` head aimed at anything other than a `workspace/*` branch. It
is allow-listed rather than deny-listed: refusing only `main` would leave an
intermediate base as a clean route to it. A fork without this repository's CLI
runs the same seed script directly; the rule is the same either way.

## What still applies

Everything in `AGENTS.md`. In particular:

- **Human-only contributorship.** No co-author trailer naming a model or an
  unmonitored address, on any commit, including here.
- **Assign, never request a review.** The person who asked for the work is the
  assignee ([`handbook/async-contract.md`](async-contract.md) §2). Draft means
  unfinished.
- **A pull request states decisions, not questions.** An exploration whose
  result is "this does not work" is a decision and is worth merging. An
  exploration that arrives asking what it should have been is not.
- **Say what you ran.** A workspace is where unproven things live, which makes
  the distinction between what was run and what was reasoned the whole value of
  the artifact. Mark it.

## What this page does not authorise

Merging any workspace or exploration branch into `main`, by any route.
Treating a workspace result as a record, a policy, or a settled fact. Deleting
a workspace branch: it is permanent, and an exploration deleted after merge
into its workspace is not the same thing. Rewriting a workspace branch's
history, which invalidates every exploration cut from it.
