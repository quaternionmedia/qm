# Branch protection rulesets

Checked in as configuration so the protection this repository relies on is
reviewable, diffable, and reproducible on a fresh clone — rather than living
only in a settings page nobody can read from the corpus.

**Nothing here is applied automatically.** A human runs `apply.sh`. That is
the same rule the corpus states for its own content: assistants draft, humans
decide.

**The JSON describes the end state, and ships evaluating.** Every file is
written as the protection this repository is building toward — including two
required code-owner approvals on `main` and an empty bypass list — while
`"enforcement": "evaluate"` means all five log what they *would* have blocked
and block nothing. Applying them today is therefore safe and reversible, and
it is how the deadlocks below get found in logs rather than on the day
someone tries to ratify.

## The staged path, and what unlocks ratification

This repository has never had a single check run, and has one active
reviewer. Turning on the end state today would deadlock immediately. The
stages below each add one thing and can be verified before the next.

| Stage | Change | Precondition |
|---|---|---|
| 0 — today | No rulesets. The rules hold as doctrine (`AGENTS.md`, `README.md`) | — |
| 1 | Apply all five **evaluating**. Read `rule-suites` for a week | none — safe now |
| 2 | Flip C, D, E to **active**: force-push, deletion, signing, branch naming | Stage 1 quiet |
| 3 | A and B **active**, but A with `required_approving_review_count: 1` and a `pull_request`-scoped admin bypass | `adr-lint`, `symlinks` and `reuse` have each reported green on a real PR |
| 4 | A as written here: **2 approvals, no bypass** | **a second code owner is genuinely active** |

**Records stay `Proposed` until stage 4.** Ratification is the act of a
human taking responsibility for what the corpus says, and with one active
reviewer that is a single point of failure holding a pen. The corpus is
already operating under its own doctrine — the discipline is enforced by CI,
the drafts are honoured in practice — so nothing is blocked by waiting except
the Status field and a QM number.

This is a deliberate trade, and it has a cost worth naming: a corpus of
`Proposed` records has no worked example of a ratified record, of an
`## Amendments` region, or of the append-only discipline the template
describes. Reaching stage 4 is what closes that, and adding a second code
owner is the only thing standing in the way.

## Why rulesets rather than classic branch protection

All four collaborators hold `admin`. Classic branch protection lets admins
bypass it unless explicitly disabled; a ruleset binds admins whenever its
bypass list is empty. Patterns are fnmatch, where `*` does not cross `/` —
hence `refs/heads/project/**`.

## The five

| | Target | Shape |
|---|---|---|
| **A** | default branch | The ratification gate: PR + code-owner review + status checks, linear history, signed commits |
| **B** | `project/**` | Submodule pins. Deletion and force-push blocked, **linear history deliberately off** |
| **C** | `perspective/**` | Force-push blocked, signed. No PR required — non-binding by construction, and the merge *into* main is gated by A |
| **D** | `evolve/**` | Signed only. Force-push allowed: rebasing a working branch onto a moved `main` is the one legitimate case |
| **E** | everything else | `creation` restricted, so a branch outside the four namespaces cannot be created |

## Three decisions worth understanding before applying

**B must not require linear history.** Org ratifications reach a project by
*merging* `main` into its branch — that merge commit is the pin bump. Linear
history would force a rebase, which rewrites the branch and breaks every
downstream submodule pin. `adr/README.md` states it directly: *"The branch's
ancestry is the pin."*

**B requires zero approvals, on purpose.** A propagation merge is mechanical
and conflict-free on most branches. Requiring a second human per project per
ratification is the friction that produced the current drift, where four
branches sit behind and the propagation merge has never once run. The PR
still runs CI and is still a reviewed commit; code-owner review still fires
when a project branch touches an org path.

**A's commit-message rule is the cheapest win here.** Human-only
contributorship is the one corpus rule an AI agent's *default tooling*
violates automatically, and the record itself admits it has no mechanical
check. A negated `(?i)co-authored-by:.*noreply` pattern is that check. Note
it also blocks merging any pre-existing branch carrying such a trailer.

## Two ordering traps

**Propagate `main` into every `project/**` branch before making B's status
checks required.** For `pull_request` events GitHub resolves workflow files
from the merge of head into base. A PR into a branch with no workflows
produces a merge ref with no workflow, so the check never reports and the PR
blocks forever at *"Expected — waiting for status to be reported"*, with no
failure to fix. The same applies to `CODEOWNERS`, which GitHub also reads
from the base branch.

**A's code-owner review will stop you merging your own PR, by design.**
GitHub does not count a PR author's own approval, and one account authored
every file in this repository. As written — two approvals, no bypass — A is
unsatisfiable by one person. That is the point rather than a defect: it is
what "two code owners" means mechanically, and it is why A is the *last*
stage rather than the first.

Until then, stage 3 runs A with one required approval and a
`pull_request`-scoped repo-admin bypass, which keeps the PR, its CI and its
audit trail while letting a solo maintainer complete the merge. To run stage
3, set `required_approving_review_count` to `1` and add:

```json
"bypass_actors": [
  { "actor_id": 5, "actor_type": "RepositoryRole", "bypass_mode": "pull_request" }
]
```

## Applying

```sh
gh auth status                       # must be an admin on the repo
./.github/rulesets/apply.sh          # creates or updates all five
```

To advance a stage, edit `"enforcement"` to `"active"` in the files that
stage covers and re-run. Check what evaluating rules have been catching
first:

```sh
gh api repos/quaternionmedia/qm/rulesets/rule-suites
```

## Not covered here

Two repository settings this design assumes, neither of which is a ruleset:

- `delete_branch_on_merge: true` — currently `false`, which is why a fully
  merged branch with zero unique commits is still sitting on the remote.
- The propagation-drift workflow that reports which `project/**` branches are
  behind `main`.
