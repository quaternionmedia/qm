# Branch protection rulesets

Checked in as configuration so the protection this repository relies on is
reviewable, diffable, and reproducible on a fresh clone — rather than living
only in a settings page nobody can read from the corpus.

**Nothing here is applied automatically.** A human runs `apply.sh`. That is
the same rule the corpus states for its own content: assistants draft, humans
decide.

All five ship at `"enforcement": "evaluate"` — they log what they *would*
have blocked and block nothing. This repository has never had a check run, so
evaluating first is how the deadlocks below get found before they can strand
a ratification.

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

**A's code-owner review will stop you merging your own ratification PR.**
GitHub does not count a PR author's own approval, and `subcontrabass`
authored every file in this repository. `A-main.json` therefore ships with a
repo-admin bypass scoped to `pull_request` — the PR, its CI and its audit
trail all still happen; a solo maintainer can complete the merge. Remove that
bypass entry when a second maintainer is genuinely active.

## Applying

```sh
gh auth status                       # must be an admin on the repo
./.github/rulesets/apply.sh          # creates or updates all five
```

To promote to enforcing, edit `"enforcement": "evaluate"` to `"active"` in
each file and re-run. Do that after one clean ratification cycle, not before.

## Not covered here

Two repository settings this design assumes, neither of which is a ruleset:

- `delete_branch_on_merge: true` — currently `false`, which is why a fully
  merged branch with zero unique commits is still sitting on the remote.
- The propagation-drift workflow that reports which `project/**` branches are
  behind `main`.
