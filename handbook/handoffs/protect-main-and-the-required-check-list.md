# Handoff — protect `main`, and the required check list

**Written 2026-08-16, mid-task, at the operator's instruction to stop.**
Retrospective for the session this came out of:
[`perspectives/2026-08-16-what-the-checks-were-not-checking.md`](../../perspectives/2026-08-16-what-the-checks-were-not-checking.md).

---

## The one-paragraph version

`main` is not protected: 0 rulesets applied, 0 of 10 checks required, 0 pull
requests ever reviewed, and the account that opens them merges them. Six
rulesets have been drafted in `.github/rulesets/` since 2026-08-10 and never
applied. The operator asked for `main` protected with **0 human approvals and a
human-approved list of deterministic checks that runs every time**, and for a
branch per change to be preserved. `A-main.json` has been edited to be
applicable; a `qm rulesets` route now reads drafted-versus-applied. **The work is
uncommitted and sitting on `main`.**

## First: the tree is dirty on `main`

Nothing here has been committed and none of it belongs on `main`.

```sh
cd <corpus>
git status --short          # 6 modified, 3 untracked, 1 deleted
git switch -c evolve/protect-main
```

| file | state | what it is |
|---|---|---|
| `.github/rulesets/A-main.json` | modified | made applicable — see below |
| `.github/rulesets/README.md` | modified | **partially updated; one edit failed and was not retried** |
| `.github/workflows/private-names.yml` | deleted | retired by decision |
| `.github/workflows/registries.yml` | new | runs the four registry checks that ran nowhere |
| `ci/rulesets.py` | new | the `qm rulesets` route |
| `ci/cli.py` | modified | routes `rulesets` |
| `ci/gate-registry.yaml` | modified | `private-names` now `gates: []`, workflow `null` |
| `plans/v0.0.1-blockers.md` | modified | blocker 1 closed as decided |
| `records/DRAFT-going-private-is-an-act-with-obligations.md` | new | the decision behind retiring the workflow |

**The README edit is the loose end.** A `str.replace` asserted on text that had
already been changed earlier in the session and raised `AssertionError`, so the
"Where this stands" section still carries the 2026-08-10 state and the new
"required checks, and who owns the list" section was never inserted. Everything
that section was going to say is in this document under *The required checks*.

## What was decided, and by whom

Four operator decisions, all in-session:

1. **Private repositories:** redact the roster, register the history. Done,
   merged as #63 and #64.
2. **Going private:** the party who makes a repository private owns removing its
   name from the corpus. The corpus does not watch for the transition — no org
   secret, no digest list, no polling. Recorded in
   `records/DRAFT-going-private-is-an-act-with-obligations.md`; the CI workflow
   is deleted; `qm private-names` stays as a local preflight.
3. **Ruleset:** draft it, the operator applies it. Never applied by an agent.
4. **Protection shape:** 0 human approvals, a human-approved list of
   deterministic checks running every time, and a branch kept per change.

## What `A-main.json` now says

```
enforcement       active          (was evaluate)
rules             deletion, non_fast_forward, required_signatures,
                  pull_request, required_status_checks, commit_message_pattern
approvals         0               (was 2)
code owner review false           (was true)
merge methods     merge, squash, rebase
required checks   tests, adr-lint, check, reuse, signatures, slot, symlinks
strict up-to-date true
bypass actors     none, including admins
```

Three changes were forced, and each would have deadlocked the repository if
applied as originally drafted:

- **2 approvals → 0.** One code owner cannot supply two, and GitHub forbids
  approving your own pull request. As drafted it blocked every merge.
- **`require_code_owner_review` → false.** `.github/CODEOWNERS` has 0 active
  entries across 56 lines.
- **`required_linear_history` removed.** It forbids merge commits, and every
  change here lands as a merge of its own branch.

`bypass_actors` is empty including for admins. That is not a lockout risk: an
admin can always edit or delete a ruleset, so the escape hatch is changing the
rule rather than stepping around it, and changing it leaves a record.

B through F are untouched and still `evaluate`.

## The required checks, and who owns the list

Seven: `tests`, `adr-lint`, `check`, `reuse`, `signatures`, `slot`, `symlinks`.

**Changing this list is a human decision.** With approvals at zero it is the
entire governance in the merge path — adding one makes a merge wait on something
new, removing one silently widens what can land.

Two run and are deliberately not required:

- `private-names` — advisory by decision 2 above.
- GitGuardian — an installed application with no workflow file here and no
  record describing it.

`registries` is a **candidate, not yet required**: it has never reported on a
real pull request. By the same discipline as the README's stage-3 precondition,
it should be green on one before a merge is made to wait on it.

## To finish this

```sh
git switch -c evolve/protect-main          # the work is on main, uncommitted
uv run qm rulesets                         # 6 drafted, 0 applied
uv run qm test                             # was 768 passing before this change
python project-seed/ci/run_workflows_locally.py
uv run qm docs generate && uv run qm docs check
```

Then, in order:

1. **Repair `.github/rulesets/README.md`** — the failed edit. Its content is in
   *The required checks* above and in `plans/v0.0.1-blockers.md`.
2. **Write tests for `ci/rulesets.py`.** It has none. Mutation-test it: the
   `applied()` function must return `None` and never `[]` on a failed call,
   because an empty list means "nothing is applied", which is a real and
   important answer.
3. **Register `registries` and `rulesets` in `ci/gate-registry.yaml`.**
4. **Open the pull request**, let `registries` report green once.
5. **Hand the operator the apply command.** Not an agent action:

   ```sh
   gh auth status                  # must be an admin
   uv run qm rulesets --apply      # wraps .github/rulesets/apply.sh
   uv run qm rulesets              # expect 6 applied, A active
   ```

6. **After a week**, read what the evaluating rules would have blocked:
   `gh api repos/quaternionmedia/qm/rule-suites`.

## Two traps specific to this task

**Applying the ruleset changes this repository's own merge path.** Once
`A-main.json` is active, the pull request that lands it is subject to it, and so
is every concurrent session. The seven required checks must be green names that
actually appear — a required check that never reports is a permanent block, and
GitHub matches on the **job name**, not the workflow name.

**`strict_required_status_checks_policy: true` means a branch must be up to date
with `main` before merging.** With more than one branch in flight this forces a
merge-and-re-run cycle. It is deliberate — a green result should be measured
against the tree the merge will actually produce — but it is friction somebody
will hit and should not mistake for a broken gate.

## What is still open beyond this task

In `plans/v0.0.1-blockers.md`: two private names in public history that no
forward fix removes; nothing restating the stability criterion in `AGENTS.md`;
and ratification waiting on a second code owner.

In `ci/lane-registry.yaml` under `development-loop`: the mutation harnesses are
still ad-hoc scripts written into a scratchpad and thrown away, so every
mutation result this corpus quotes was produced by a script nobody else can run.
