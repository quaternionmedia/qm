# Branch protection rulesets

Checked in as configuration so the protection this repository relies on is
reviewable, diffable, and reproducible on a fresh clone — rather than living
only in a settings page nobody can read from the corpus.

**Nothing here is applied automatically.** A human runs `uv run qm rulesets
--apply`, which wraps `apply.sh`. That is the same rule the corpus states for
its own content: assistants draft, humans decide.

**Five of the six ship evaluating. A does not.** B through F are written as the
protection this repository is building toward, with `"enforcement": "evaluate"`
meaning they log what they *would* have blocked and block nothing — so applying
them is safe and reversible, and it is how the deadlocks below get found in
logs rather than on the day someone tries to ratify. **A is `active`, and is
meant to be.** It is the one that makes a pull request and a check list
mandatory on `main`; while it is evaluating, nothing is required to merge, which
is the state this repository has been in since it was created.

## The staged path, and what unlocks ratification

The end state as first drafted would have deadlocked. It wanted two code-owner
approvals, and this corpus has one active reviewer, who GitHub will not let
approve their own pull request. What replaced it is not a weaker form of that
rule but a different one: **zero approvals, and a human-approved list of
deterministic checks that runs every time.** The stages below still add one
thing each and can be verified before the next.

*Where this stands, 2026-08-16.* `uv run qm rulesets` reports **6 drafted, 0
applied**. **None of these six has ever been applied**, so every rule below
is a file and nothing else, and every gate in this repository is a signal to
whoever merges rather than a barrier. Nothing is required to merge into `main`.

That matters beyond this page. `main-is-entered-through-a-pull-request` is
registered in `ci/policy-registry.yaml` with a preventer that was never applied
and no detector — this is that preventer. A reader who sees a green check and
believes it was required is reading something that is not true.

Pull request #64 reported `tests`, `adr-lint`, `check`, `reuse`, `signatures`,
`slot` and `symlinks` green. Those seven are what ruleset A now names as
required, and each has reported green on a real pull request more than once.

| Stage | Change | Precondition | State |
|---|---|---|---|
| 0 | No rulesets. The rules hold as doctrine (`AGENTS.md`, `README.md`) | — | **where the host still is** |
| 1 | Apply all six: **A active**, B–F evaluating. Read `rule-suites` for a week | every name in A's required list has reported green on a real pull request | **the next step** |
| 2 | Flip C, D, E to **active**: force-push, deletion, signing, branch naming | Stage 1 quiet | waiting on a week of logs |
| 3 | B **active** | every `project/**` branch has been propagated, so B's checks can report at all | waiting on the propagation merge |
| 4 | Approvals above zero on A | **a second code owner is genuinely active** | not a merge rule today — see below |

A goes active at stage 1 rather than last because with zero approvals it
deadlocks nobody: it requires a pull request, a signature, and seven checks that
already pass. The stages after it are about the *other* five, and about what
becomes possible once a second human exists.

Stage 4 is not what stands between this repository and a protected `main`. It is
what *ratification* waits on, which is a different gate —
`plans/v0.0.1-blockers.md` §4.

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

## The required checks, and who owns the list

Seven, named in `A-main.json` and nowhere else:

| context | workflow | job | why it is required |
|---|---|---|---|
| `tests` | `ci-tooling-tests.yml` | `tests` | the tooling's own suite |
| `adr-lint` | `adr-lint.yml` | `adr-lint` | record discipline, attribution, restatements |
| `check` | `governance-status.yml` | `check` | the status document still renders the commits it names |
| `reuse` | `reuse-lint.yml` | `reuse` | outbound licensing |
| `signatures` | `signature-check.yml` | `signatures` | every commit is attributable |
| `slot` | `one-pr-check.yml` | `slot` | one open pull request per contributor |
| `symlinks` | `symlink-integrity.yml` | `symlinks` | a pointer file has not silently forked in two |

**GitHub matches the `context` against the *job* name, not the workflow name.**
The middle column is here so that renaming a workflow does not quietly detach a
required check, and the third is the one that has to match.

**Changing this list is a human decision, and it is the only governance in the
merge path.** With approvals at zero there is no reviewer to catch what the list
misses: adding a context makes every merge wait on something new, and removing
one silently widens what can land, with nothing going red either way.

### What runs and is deliberately not required

| check | why not |
|---|---|
| `private-names` | advisory by decision — `records/DRAFT-going-private-is-an-act-with-obligations.md`. It reads gitignored companions and cannot run on a runner at all |
| GitGuardian Security Checks | an installed application with no workflow file here and no record describing it. Requiring a check this corpus cannot configure or read hands a third party a veto over merging |
| `namespace` | `namespace-guard.yml` triggers only on `project/**`. As a required context on `main` it would never report, and never reporting is a permanent block |
| `audit`, `draft` | `docs-audit.yml` and `docs-draft.yml` are path-filtered. A required path-filtered check does not report on a pull request that misses its paths — the same permanent block, arriving only for some changes, which is worse |

**`registries` is a candidate and is not on the list.** It has never reported on
a real pull request. By the same discipline as stage 1's precondition, it stays
off until it has been green on one — a context added to `A-main.json` before its
first report is a merge block with no failure to fix.

## Why rulesets rather than classic branch protection

All four collaborators hold `admin`. Classic branch protection lets admins
bypass it unless explicitly disabled; a ruleset binds admins whenever its
bypass list is empty. Patterns are fnmatch, where `*` does not cross `/` —
hence `refs/heads/project/**`.

## The six

| | Target | Shape |
|---|---|---|
| **A** | default branch | The merge gate: PR required, seven status checks, signed commits, no unmonitored co-author trailer. **Zero approvals**, and merge commits allowed |
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

**Any approval requirement above zero locks this repository, and no bypass
fixes it honestly.** GitHub does not count a pull request author's own approval,
and one account authored every file here — so `required_approving_review_count:
1` is unsatisfiable by the only person who can satisfy it, and the usual escape,
a `pull_request`-scoped admin bypass, is a rule that permits exactly the thing
it forbids. A is written at zero for that reason rather than as a concession:
the governance moved to the check list, which an author *can* satisfy once and
then cannot skip.

`bypass_actors` is empty, admins included. That is not a lockout risk, because
an admin can always edit or delete a ruleset — the escape hatch is changing the
rule, which leaves a record, rather than stepping around it, which does not.

**Applying A changes the merge path of the pull request that lands it**, and of
every branch already in flight. Each of the seven contexts must be a name that
actually reports, or the repository is blocked with nothing to fix, and
`strict_required_status_checks_policy: true` additionally makes every branch
merge `main` and re-run before it can land. That is deliberate — a green result
should be measured against the tree the merge will produce — but with more than
one branch open it is friction, not a broken gate.

## Applying

```sh
uv run qm rulesets                   # what is drafted, against what is applied
gh auth status                       # must be an admin on the repo
uv run qm rulesets --apply           # wraps apply.sh; creates or updates all six
uv run qm rulesets                   # expect 6 applied, A active
```

`uv run qm rulesets --apply` is the only route here that writes to the host, and
nothing calls it on anyone's behalf. `uv run qm rulesets --check` exits non-zero
when what is drafted and what is applied disagree; it is not wired into any
workflow, by the rule stated in `.github/workflows/registries.yml` — it reads a
host, and a check that reads a host reds a pull request for a reason its author
cannot fix.

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
