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
`"enforcement": "evaluate"` means all six log what they *would* have blocked
and block nothing. Applying them today is therefore safe and reversible, and
it is how the deadlocks below get found in logs rather than on the day
someone tries to ratify.

## The staged path, and what unlocks ratification

Turning on the end state today would deadlock: it wants two code-owner
approvals and this corpus has had one active reviewer. The stages below each
add one thing and can be verified before the next.

*Where this stands, 2026-08-10.* Checks now run: pull request #36 reported
`adr-lint`, `symlinks`, `reuse`, `tests`, `check` and `slot` green, which is
**stage 3's stated precondition, met**. Stage 1 is therefore the only thing
between here and a staged rollout, and it has no precondition at all.

| Stage | Change | Precondition | State |
|---|---|---|---|
| 0 | No rulesets. The rules hold as doctrine (`AGENTS.md`, `README.md`) | — | left behind at stage 1 |
| 1 | Apply all six **evaluating**. Read `rule-suites` for a week | none — safe now | **the next step** |
| 2 | Flip C, D, E to **active**: force-push, deletion, signing, branch naming | Stage 1 quiet | waiting on a week of logs |
| 3 | A and B **active**, but A with `required_approving_review_count: 1` and a `pull_request`-scoped admin bypass | `adr-lint`, `symlinks` and `reuse` have each reported green on a real PR | **precondition met** (#36) |
| 4 | A as written here: **2 approvals, no bypass** | **a second code owner is genuinely active** | the standing blocker |

Stage 3's precondition being met does not let it jump the queue: stage 2 exists
so that force-push, deletion and signing are known-quiet before a rule starts
gating merges. What it does mean is that once stage 1 has had its week, nothing
else has to be waited for.

**One thing to watch in the first week's logs.** Ruleset E targets `~ALL` with a
`creation` rule, so every branch made in this repository is evaluated against
the naming pattern. Branches created on 2026-08-10 — `project/dossier` here,
and `governance/*` names in adopting projects — are the first real test of
whether that pattern matches how work is actually named. A rule that would have
blocked ordinary work is better found in a log than on the day it is switched
on.

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

## The six

| | Target | Shape |
|---|---|---|
| **A** | default branch | The ratification gate: PR + code-owner review + status checks, linear history, signed commits |
| **B** | `project/**` | Submodule pins. Deletion and force-push blocked, **linear history deliberately off** |
| **C** | `perspective/**` | Force-push blocked, signed. No PR required — non-binding by construction, and the merge *into* main is gated by A |
| **D** | `evolve/**` | Signed only. Force-push allowed: rebasing a working branch onto a moved `main` is the one legitimate case |
| **E** | everything else | `creation` restricted, so a branch outside the four namespaces cannot be created |
| **F** | `refs/tags/v*` | Version tags: signed, immutable, semver-shaped, and creatable only by named actors |

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

**F is the teeth of the version-tags record.** That record makes a tag a
human claim about review, manual testing and deterministic validation; the
ruleset is what stops it being customary. `bypass_actors` is empty, so no
automation can cut a release tag — release workflows trigger *on* a tag and
must never create one. Deletion and force-push are blocked because a moved tag
silently changes what a published version means.

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
./.github/rulesets/apply.sh          # creates or updates all six
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
