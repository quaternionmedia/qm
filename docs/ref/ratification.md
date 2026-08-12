# Ratification

!!! info "Canonical"
    This page states the ratification mechanics. Cited as `docs/ref/ratification.md`.

## What ratification is

Ratification turns a draft record into a binding one. It is a human action, at both the org level and the project level. One commit:

1. flips the record's Status to `Accepted`,
2. assigns the number from the index (`QM-NNNN` or `ADR-NNNN`),
3. updates the index,
4. names the record in the commit message.

**Assistants draft; humans ratify.** An assistant never performs any of the four steps.

## Ratification is the last gate, not the only one

Every change to the corpus arrives as a pull request — a typo fix and a new record alike. Contributors work on a branch (`evolve/<slug>`, `perspective/<date>-<slug>`, or a `project/<name>` base) and a human merges. Nobody merges their own work into `main`, and nothing reaches `main` by direct push.

Branch protection makes this mechanical where it is enabled. The rule stands either way.

## Why nothing is ratified yet

Every org record is `Proposed`. This is a decision, not a backlog: ratification waits on a second active code owner. GitHub does not count a pull request author's own approval, so a gate one person can satisfy alone would not be a real gate.

The discipline is still enforced meanwhile — the lints and checks run in CI today. [handbook/governance-rollout.md](https://github.com/quaternionmedia/qm/blob/main/handbook/governance-rollout.md) tracks what is enforced, what is written but not yet mechanical, and what the wait costs.

## Obligations that fall due at ratification

Some records name follow-on work that triggers when they are Accepted:

- **Open-license record:** on acceptance, the `ADR-0001` on the `project/streaming-infrastructure` branch receives a dated amendment recording adoption by reference. Its body is not touched.

Some records describe machinery that costs nothing to run early. That machinery can be live while the record is still `Proposed`; the two states are independent. The current inventory is in [handbook/governance-rollout.md](https://github.com/quaternionmedia/qm/blob/main/handbook/governance-rollout.md).

## Related

- [Record precedence](precedence.md) — what a ratified record binds
- [Draft a record](../cookbook/draft-a-record.md) — how a record reaches `Proposed`
