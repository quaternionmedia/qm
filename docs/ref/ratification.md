# Ratification

!!! info "Source of truth"
    This page describes how records move from `Proposed` to `Accepted` and what obligations trigger. Cited as: [quaternionmedia/qm](https://github.com/quaternionmedia/qm) `docs/ref/ratification.md`.

## What ratification is

Ratification is a human action at both the org level and the project level: a commit that flips `Status` to `Accepted`, assigns the number from the index, updates the index, and names the record in the commit message. 

**Assistants draft; humans ratify.**

## How ratification works

Ratification is the last human gate, not the only one. **Every change to this corpus arrives as a pull request**, from a typo fix to a new record, and the merge is a human's act. Assistants and contributors work on a branch — `evolve/<slug>`, `perspective/<date>-<slug>`, or the relevant `project/<name>` — and open a PR; nobody merges their own work into `main`, and nothing reaches `main` by direct push. 

The branch protection that makes this mechanical rather than customary is described in the repository's rulesets; the rule stands whether or not the tooling is enforcing it on a given day.

## The deliberate gate

**Every record is `Proposed`, and that is a decision rather than a backlog: ratification waits on a second active code owner.** 

GitHub does not count a PR author's own approval, so a ratification gate one person can satisfy alone is a gate in name only. The mechanisms are not waiting — the discipline is enforced by CI today. See [handbook/governance-rollout.md](https://github.com/quaternionmedia/qm/blob/main/handbook/governance-rollout.md) for what is enforced, what is written but not yet mechanical, and what the wait costs.

## Obligations that fall due at ratification

When a record moves to `Accepted`, certain other actions are triggered:

- **Open-license record → the streaming design branch.** When it is Accepted, the `ADR-0001` on `project/streaming-infrastructure` receives a dated amendment recording adoption-by-reference. Its body is untouched.

Some records describe machinery that costs nothing to run before ratification. Where that is true the machinery is live and the record's Status is still `Proposed`; the two are independent. See [handbook/governance-rollout.md](https://github.com/quaternionmedia/qm/blob/main/handbook/governance-rollout.md), which holds the current inventory so there is one place to update rather than two that drift.

## Related

- [Record precedence](precedence.md) — how the "one place to update" rule flows from the precedence model
- [Handbook: Governance rollout](https://github.com/quaternionmedia/qm/blob/main/handbook/governance-rollout.md) — the machinery and its enforcement status
- [AGENTS.md](https://github.com/quaternionmedia/qm/blob/main/AGENTS.md) — the rule that every change is a PR
