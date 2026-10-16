# ADR-XXXX — A human merges every change into codecartographer's main and its project branch

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-10-13 |
| **Pends on** | Nothing — ready to be argued |
| **Principle** | `credit-tracks-accountability` |
| **Restated in** | codecartographer's `AGENTS.md`, item 3, which states the rule and is to cite this record by path |

## Context

The org's rule for agent-produced work is in `handbook/async-contract.md` §2:
assign the person who asked, request no review, and *"merge the pull request
yourself once every gate is green."* The corpus's `AGENTS.md` item 3 and the
seed's `project-seed/ide/AGENTS.md` item 3 restate it: "merge it yourself once
every gate is green." The reasoning is that `main` asserts nothing
(`records/DRAFT-version-tags-are-claims.md` §4), so the two human gates are
ratification and the version tag, and a pull request is an audit record rather
than a request for anyone's attention.

The corpus also says the opposite in one place. The seed's drafting-session
contract (`project-seed/adr/README.md`, carried in this project's
`adr/README.md`) says a session "does not merge its own work", for every
change it makes to the records.

Three facts about codecartographer bear on which rule it keeps:

- **The gates cover part of a change.** At codecartographer 00ce9de, a pull
  request runs the Python suite and the governance lints. No workflow runs
  anything under `web/` until codecartographer #119 adds `web.yml`, and no
  runner can read graphbase. A green check is evidence about less than the
  change touches.
- **An agent acts under the contributor's account.** Pull requests, comments
  and merges an agent makes are posted as the human who runs it, so the host
  cannot tell an agent's merge from the human's. That account bypasses the
  repository's rulesets, which is how a forbidden push can succeed without a
  word.
- **A merge can happen by accident.** Pushing a pull request's commits onto
  its base merges that pull request, with no review and the pusher as the
  merger; `adr/README.md`'s handoff contract says so under "Closing a pull
  request is a git operation", and that a session that merges by accident has
  still merged.

## Decision

**An agent never merges into codecartographer's `main`, or into
`project/codecartographer` in this corpus.** It works on a branch, opens the
pull request, gets every gate green, assigns the human who asked for the work,
and leaves the merge to that human's click. It says in the session, not in the
pull request, that the pull request is green and waiting.

This tightens, for this project only:

- `handbook/async-contract.md` §2's "merge the pull request yourself once every
  gate is green";
- its restatements in the corpus's `AGENTS.md` item 3 and
  `project-seed/ide/AGENTS.md` item 3, which this project's `AGENTS.md` is
  drawn from.

It relaxes nothing. The rest of §2 — assign the person who asked, never
request a review — and the rest of item 3 — never push a shared branch
directly — bind as written. Per `docs/ref/precedence.md`, a project record may
add a constraint on top of a handbook page or a record and may not waive one;
this record adds one. For this project's records it agrees with the seed's
drafting-session contract, which already forbids a session merging its own
work.

## Consequences

- A green pull request waits for a click. Work that depends on it stacks on
  its branch as a draft rather than waiting for the merge.
- The rule is carried by instruction: this record, codecartographer's
  `AGENTS.md` item 3, and each session's brief. Because an agent acts under the
  contributor's account, no host rule can enforce it, and that is a known soft
  spot rather than a design choice.
- A handoff ends with the open, green pull request and the commands that
  showed it green. The merge, and responsibility for what it lands, belong to
  the human who clicks.
- `main` still asserts nothing. This record changes who performs the merge,
  not what a merge claims; the version tag remains the gate for what the
  project ships.

## Alternatives considered

1. **Follow the org rule: an agent merges once every gate is green.** Lost
   because codecartographer's gates cover part of what a change touches, so
   "green" is weaker evidence here than the rule assumes, and because the owner
   keeps the merge as an act of a person who can answer for it. The cost is
   real: green work waits on a person.
2. **A host rule requiring an approving review before merge.** Lost: the org
   requests no reviews (§2), and an agent acting under the contributor's
   account would satisfy or bypass such a rule as that contributor. The host
   cannot tell the two apart, so a rule there would look like enforcement and
   not be any.
3. **Let agents merge some classes of change** (dependency bumps, record-only
   changes). Lost for now: each class is a line someone has to draw and keep
   drawing, and one rule with no exceptions is the one a session cannot
   misread.

## Revision triggers

- Agents act under accounts of their own, so a host rule can tell an agent's
  merge from a human's — the rule can then be enforced, not only instructed.
- The org amends `handbook/async-contract.md` §2 so that a human merges
  everywhere — this record then restates the org rule, and is deprecated.
- An agent's merge is found in codecartographer's `main` or in
  `project/codecartographer` — the instruction failed, and a check is owed.
- The web suites and every submodule are read on every pull request, and the
  owner judges that green is evidence enough for some class of change.

## Amendments

*None.*
