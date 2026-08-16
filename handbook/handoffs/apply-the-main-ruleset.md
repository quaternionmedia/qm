# Handoff — apply the `main` ruleset

**Stamped 2026-08-16. `qm` `main` at `fde5dfc`.** Every figure below was true at
that commit and nowhere else. Re-derive before quoting one: `uv run qm rulesets`
answers the central question in a second, and it reads the host rather than this
page.

Retrospective for the session this came out of:
[`perspectives/2026-08-16-the-harness-measured-its-own-cache.md`](../../perspectives/2026-08-16-the-harness-measured-its-own-cache.md).
It supersedes nothing; the earlier page for the same day,
[`2026-08-16-what-the-checks-were-not-checking.md`](../../perspectives/2026-08-16-what-the-checks-were-not-checking.md),
is what opened this work.

---

## The one-paragraph version

Everything mechanical is done and merged. **`main` is still not protected**, and
the only remaining step is one command that a human runs. Six rulesets are
drafted, `A - main` is written `active` with zero approvals and seven required
checks, `uv run qm rulesets` reads drafted against applied, and the host reports
**0 applied**. Nothing on this page is blocked on an agent.

## State

| | |
|---|---|
| `qm` `main` | `fde5dfc` — merge of #65 |
| Working tree | clean |
| Branches pushed, no PR | none |
| Open pull requests | re-derive with `uv run qm slot --repo quaternionmedia/qm`; at the stamp, #57 into `project/datum` (its own slot) |
| Rulesets applied on the host | **0 of 6** |
| Checks required to merge | **0 of 10** |

`evolve/protect-main` is merged and **deliberately not deleted**. A branch per
change is kept, which is why `delete_branch_on_merge` stays `false` —
`.github/rulesets/README.md`'s *Not covered* section records that as an
assumption of the design rather than an oversight.

### What landed in #65 and #64's successor commits

- `.github/rulesets/A-main.json` is applicable: `active`, zero approvals, no
  code-owner review, seven required checks, `strict` up-to-date policy, empty
  bypass list including admins. B–F are untouched and still `evaluate`.
- `.github/rulesets/README.md` describes that, and names the seven contexts with
  the **job** each one matches. It also records the four checks that run and are
  deliberately not required, with the reason for each.
- `ci/rulesets.py` has 29 tests. `ci/mutate.py` is a mutation route with 23.
  Counting the second by `grep -c '^def test_'` gives 25: two of those matches
  are inside a fixture string that *is* a test file. Read the pytest count.
- `registries` and `rulesets` are in `ci/gate-registry.yaml`. `registries`
  reported green on a real pull request (#65) for the first time.

## The one thing left, and it is a human's

```sh
gh auth status                  # must be an admin on quaternionmedia/qm
uv run qm rulesets --apply      # wraps .github/rulesets/apply.sh
uv run qm rulesets              # expect 6 applied, A active
```

**An agent must not run this**, at any point, for any reason. It changes what
every contributor and every concurrent session can do, on the host, outside any
pull request. `uv run qm rulesets --check` is the read-only form and is safe.

**Done looks like** `uv run qm rulesets` printing `6 drafted, 6 applied` with
`[=]` against every row and `A - main` at `active`.

### What applying it changes for the next session

- A pull request becomes mandatory on `main`, and so do `tests`, `adr-lint`,
  `check`, `reuse`, `signatures`, `slot` and `symlinks`. A required context that
  never reports is a permanent block with no failure to fix — GitHub matches the
  **job** name, so renaming a workflow's job without editing `A-main.json`
  breaks the repository.
- `strict_required_status_checks_policy: true` means a branch must be up to date
  with `main` before it merges. With more than one branch in flight this forces
  a merge-and-re-run cycle. Deliberate, and friction somebody will mistake for a
  broken gate.
- The commit-message rule blocks any branch carrying a
  `co-authored-by: …noreply` trailer, including pre-existing ones.

## Blocked on a human, and named as such

| | who decides | why nobody else can |
|---|---|---|
| Applying the rulesets | the operator | it needs admin, and it is the act this corpus reserves to a person |
| Changing the required-check list | the operator | with approvals at zero it is the entire governance in the merge path; adding one makes merges wait on something new, removing one silently widens what can land |
| Approvals above zero on A | waits on a **second active code owner** | one person cannot approve their own pull request; `plans/v0.0.1-blockers.md` §4 |
| Ratification of the sixteen records | the same | unchanged and the oldest of these |

## Unfinished, and what done looks like

**Read `rule-suites` a week after applying.** `gh api
repos/quaternionmedia/qm/rule-suites` is the log of what the five evaluating
rulesets *would* have blocked. Ruleset E targets `~ALL` with a `creation` rule,
so the first week's log is the first real test of whether the branch-naming
pattern matches how work is actually named. *Done:* stage 2 promoted, or the
pattern amended because the log said it would have blocked ordinary work.

**Nothing runs `uv run qm mutate`.** The route exists and is tested; no gate
requires a sweep and no document records the last one, so a suite that stops
discriminating goes unremarked until somebody looks. *Done:* either a gate, or a
generated document carrying the last sweep per module with its date. Recorded as
open in `ci/lane-registry.yaml` under `development-loop`.

**Three workflows nobody declared.** `docs.yml`, `docs-audit.yml` and
`docs-draft.yml` are on disk and absent from `ci/gate-registry.yaml`;
`handbook/gates.md` names all three under *Where claim and evidence disagree*.
Pre-existing, and left alone to keep #65 reviewable. *Done:* `uv run qm gates`
reports nowhere in that section, or the entries state why they are not gates.

**No detector for `main-is-entered-through-a-pull-request`.** `qm rulesets`
reports whether the *preventer* is applied, which is a different question from
whether the invariant held. The detector described in `ci/policy-registry.yaml`
— reading `main`'s history for a commit with no merge parent and no associated
pull request — is roughly twenty lines and is not written. *Done:* that check
exists and has a fixture in which it reports bad.

**The next slice, named by the operator on 2026-08-16: how corpora interact.**
The org corpus, `project/<name>` branches, `propagate/<name>-<date>` merges and
the submodule pins downstream. It has to pass its own tests. Nothing has been
drafted for it; this line is the whole of what exists.

## The force-push audit, and what it found in ruleset E

Run on 2026-08-16 against `gh api --paginate repos/quaternionmedia/qm/activity`.
**312 events, back to the creation of `main` on 2026-06-10**, so this is the
whole of the repository's history and not a window.

**Four force pushes, ever. None on `main`, none on any `project/**` branch, none
on a tag.** Nothing a downstream submodule pins has been rewritten.

| when | ref | landed? |
|---|---|---|
| 2026-08-13 | `evolve/git-hygiene-and-handoff` | ruleset D permits this deliberately |
| 2026-08-08 ×2 | `propagate/qmetronome-2026-08-08` | both **before** PR #25 merged into `project/qmetronome` on 08-11; the merged commits were never rewritten |
| 2026-08-08 | `fix/apothecary-seed-refresh` | PR #11 was **closed unmerged**; nothing landed |

Two findings came out of checking those against the rulesets rather than out of
the history itself.

**1. Applying `E-naming.json` as `active` would block propagation.** E targets
`~ALL` with a `creation` rule and excludes exactly five patterns:
`~DEFAULT_BRANCH`, `project/**`, `perspective/**`, `evolve/**`, `workspace/**`.
**`propagate/**` is not among them** — and it is the second most-created
namespace in this repository's history (20 creations, behind `evolve`'s 28),
because it is the only route by which `main` reaches a `project/<name>` branch.
`AGENTS.md` item 3 mandates it and `handbook/propagation-runbook.md` describes
it. With E active, creating one is refused, there are no bypass actors, and
propagation stops.

`docs` is in the same position and is load-bearing differently: `docs.yml`
triggers on pushes to `[main, docs]`. Creation is not push, so an existing
`docs` branch keeps working — but it could not be recreated if deleted.
Thirteen historical creations sit outside every exclusion: `fix` (8), and one
each of `qmetronome`, `polish`, `math`, `docs`, `broaden`. Most of those are
what E is *for*. Two are not.

The README already flags E as the thing to watch in the first week's logs, which
is why it ships evaluating and why stage 2 exists. It does not name
`propagate/**`, and that one is not "a rule that would have blocked ordinary
work" — it is a rule that would have blocked a mandated one.

*Done:* `refs/heads/propagate/**` and `refs/heads/docs` added to E's exclude
list, or a stated reason they should be refused. **A human decides which**, and
the README's `## The six` row for E says "the four namespaces" while the file
excludes five plus the default branch — that sentence needs the same repair.

**2. Nothing protects `propagate/**` from a force push, even after all six are
applied.** A covers the default branch, B `project/**`, C `perspective/**`, D
`evolve/**` (and permits force-push on purpose), F `refs/tags/v*`. E carries
only `creation`. So the class of branch that carries governance into pinned
project branches has no `non_fast_forward` rule, and two of the four historical
force pushes were on one.

Adding `non_fast_forward` to E is the wrong fix: E targets `~ALL`, rulesets are
additive, and it would override D's deliberate permission for `evolve/**`.
*Done:* a `G-propagate.json` targeting `refs/heads/propagate/**` with
`non_fast_forward` and `required_signatures`, or a recorded decision that a
pre-merge working branch does not need it.

**What this audit cannot see.** Whether a force push was *justified* — the log
records that history was rewritten, not why. It also has no route: it was run by
hand with one `gh api` call, which by this corpus's own standard is a hand-run
check reported as a result. *Done:* `uv run qm force-pushes`, or the same read
folded into `qm rulesets`, so the next person reproduces it with a command
rather than by being told one.

## What could not be verified — inference, not fact

- **Whether the host accepts `A-main.json` as written.** It has never been
  applied. The JSON is well-formed and the field names match GitHub's ruleset
  schema as documented, but no request has been made with it, so a rejected
  field would show up for the first time during the apply. Read `apply.sh`'s
  output rather than assuming a silent success.
- **Whether the seven contexts match at apply time.** They are the names that
  reported on #64 and #65, read from `gh pr checks`. A workflow's job renamed
  between now and the apply would break the match, and nothing watches for that.
- **Whether `strict` is tolerable in practice.** It is reasoned about above and
  has never been lived with here.

## Standing constraints still in force

- **Never push `main`.** Everything enters through a pull request, and the
  pull request is an audit record rather than a request for anyone's attention.
- **One open pull request per repository, per contributor.** Each
  `project/<name>` branch in this repository holds its own slot; that is the
  only exemption.
- **Never add a co-author trailer** naming an unmonitored address. Once A is
  applied this is mechanical, and it blocks the merge rather than warning.
- **Nothing here is unpushed on purpose.** If a later session finds local
  commits on `evolve/protect-main`, they are not deliberate — that branch was
  merged at `fde5dfc` and is finished.
