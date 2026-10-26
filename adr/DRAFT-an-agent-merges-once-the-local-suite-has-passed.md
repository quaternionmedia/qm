# ADR-XXXX — An agent merges into codecartographer's main once every check and the full local suite have passed

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-10-24 |
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

The seed's drafting-session contract (`project-seed/adr/README.md`, carried in
this project's `adr/README.md`) says a session "does not merge its own work",
for every change it makes to the records.

Three facts about codecartographer bear on what "green" is evidence of:

- **The checks run part of a change.** At codecartographer 11b2d44, a pull
  request runs the Python suite and the governance lints, and nothing under
  `web/`. codecartographer #119 adds `web.yml`, which runs the type check,
  `test:pure`, `test:state`, `test:rad`, `test:system` and the browser suite on
  a pull request that touches `web/`, `codecarto/`, the lockfile or the
  workflow. No check builds the frontend or runs `test:families`, and no runner
  reads graphbase, which is private.
- **The local suite finds what the checks miss.** On 2026-10-24, with every
  check green on codecartographer #107, the browser suite run at its head
  failed `demo-graph.spec.ts`; it failed the same way on `main`, which no check
  could show, because no check ran the browser suite there.
- **An agent acts under the contributor's account.** Pull requests, comments
  and merges an agent makes are posted as the human who runs it, so the host
  cannot tell an agent's merge from the human's. That account bypasses the
  repository's rulesets, which is how a forbidden push can succeed without a
  word.

## Decision

**An agent merges its own pull request into codecartographer's `main`, with
a merge commit, once every check the host runs on it is green and the full
local suite has passed at its head.**

- **The full local suite** is every command in the Tests section of
  codecartographer's `AGENTS.md`, `npm run build`, and every other `test:*`
  script `web/package.json` defines, run in an environment synced with
  `--extra dev --extra c-parsing`, after the branch is updated from `main`. A
  suite that does not run on the machine is not a pass, and a test that skips
  is reported as a skip, with its reason.
- **The tests are bolstered first.** Every defect a review of the pull
  request finds, and every claim its body makes that no test holds, is pinned
  by a test that was seen to fail, then fixed on its branch. A finding is not
  deferred as a follow-up, because a suite that passes without it is evidence
  about less than the change.
- **The merge is at the head that was tested**:
  `gh pr merge <n> --merge --match-head-commit <sha>`, so a commit pushed after
  the run cannot land with it. The pull request's body names that head and what
  each command reported there.
- **Never a squash or a rebase**, which rewrite the commits a stacked branch
  was cut from.

**Into `project/codecartographer` in this corpus, a human merges.** The seed's
drafting-session contract has no session merge its own work on the records,
and a project record cannot waive it.

This tightens, for this project only:

- `handbook/async-contract.md` §2's "merge the pull request yourself once every
  gate is green", which this keeps and adds the local suite to;
- its restatements in the corpus's `AGENTS.md` item 3 and
  `project-seed/ide/AGENTS.md` item 3, which this project's `AGENTS.md` is
  drawn from.

It relaxes nothing. The rest of §2 — assign the person who asked, never
request a review — and the rest of item 3 — never push a shared branch
directly — bind as written. Per `docs/ref/precedence.md`, a project record may
add a constraint on top of a handbook page or a record and may not waive one;
this record adds one.

## Consequences

- Green work lands without waiting on a person, and the evidence for what the
  checks do not run sits in the pull request's body, at the head that merged.
- A review's findings are fixed before the merge, each with the test that
  would have caught it, so the suite grows with every pull request it lands.
- A failure the base shares is still a failure. It is fixed in a pull request
  of its own that lands first, and the work above it waits; a red suite is not
  read as green because `main` is red too.
- The merge is posted under the contributor's account, and the contributor who
  runs the agent answers for what lands, as for anything else posted there.
  The rule is carried by instruction — this record, codecartographer's
  `AGENTS.md` item 3, and each session's brief — because no host rule can tell
  the agent's merge from the human's.
- `main` still asserts nothing. This record changes what a merge into it
  requires, not what a merge claims; the version tag remains the gate for what
  the project ships.

## Alternatives considered

1. **A human clicks every merge into `main`.** Lost: the click carried no
   evidence the local suite does not, and every green pull request waited on a
   person — a stack of thirty-nine pull requests was thirty-nine waits. The
   owner keeps the decision by giving the instruction and answering for what
   lands.
2. **Follow §2 as written: an agent merges once the checks are green.** Lost
   because the checks run part of a change, so green alone is weaker evidence
   here than §2 assumes; codecartographer #107 was green with its browser suite
   failing.
3. **A host rule requiring an approving review before merge.** Lost: the org
   requests no reviews (§2), and an agent acting under the contributor's
   account would satisfy or bypass such a rule as that contributor. The host
   cannot tell the two apart, so a rule there would look like enforcement and
   not be any.
4. **Let agents merge some classes of change only** (dependency bumps,
   documentation). Lost: each class is a line someone has to draw and keep
   drawing, and one rule with no exceptions is the one a session cannot
   misread.

## Revision triggers

- Every suite the Decision names runs as a check on every pull request, and
  graphbase is read there — the local suite then adds nothing, and this record
  restates §2 and is deprecated.
- Agents act under accounts of their own, so a host rule can tell an agent's
  merge from a human's — the rule can then be enforced, not only instructed.
- An agent's merge is found in codecartographer's `main` whose head did not
  pass the local suite, or was not the head tested, or is found in
  `project/codecartographer` — the instruction failed, and a check is owed.
- The org amends `handbook/async-contract.md` §2 so that a human merges
  everywhere — this record then restates the org rule, and is deprecated.

## Amendments

*None.*
