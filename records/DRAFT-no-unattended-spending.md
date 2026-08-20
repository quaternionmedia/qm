# QM-XXXX — Nothing Unattended Spends Money

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-08-20 |
| **Pends on** | Nothing — ready for ratification |
| **Principle** | P13 — a person is interrupted only by a decision; P1 — ownership is the deliverable; P8 — systems over heroics |
| **Restated in** | Nothing. The qmPM standardisations page cites it, which is a citation rather than a restatement: that page decides nothing and says so |

## Context

Everything this organisation's tooling does today is free and local. It reads
git, it reads a SQLite file, it calls a host API with a credential that costs
nothing per call. The worst outcome of a loop that runs too often is a warm
laptop.

Wiring a metered API in changes that, and it changes it in a direction that is
easy to miss: **the failure mode of automation stops being a wrong answer and
starts being a bill.** A retry loop that was a nuisance becomes an expense. A
scheduled job somebody forgot becomes a standing charge. A detector that fires
once per row becomes a function of how many rows exist.

The organisation already has the ingredients for this to go wrong quietly. It
has a harness that runs things on command. It has a self-check that runs a suite
and could as easily run a model. It has a disk tool with a `--check` exit code
*specifically so a scheduled task can drive it*, and a handoff page recording
that no such task exists and that scheduling one is a decision nobody has taken.
That page's reasoning is the same reasoning as this record: **a scheduled
program that acts while nobody is watching is a different kind of thing from the
same program run by a person.**

There is also a governance reason, and it is P1's. A component is owned only if
it can be run, rebuilt and modified without anyone's permission. A metered
dependency is a rental, and a rental that bills on a timer is one whose meter
somebody else controls. Keeping every paid call attached to a human command is
what keeps the dependency a tool rather than a subscription to a behaviour.

## Decision

**No unattended process may call a paid service. Every paid call is a direct,
deterministic, human-issued command.**

1. **Direct.** A person issues the command that causes the call. Not a schedule,
   not a watcher, not a hook, not a retry, not a background refresh, and not a
   second call the first one decided to make.

2. **Deterministic.** The command determines what is called and how many times.
   A command whose call count depends on what it finds is not deterministic, and
   the person issuing it cannot consent to a number nobody can state in advance.
   Where a count depends on input, the count is shown and confirmed before the
   first call rather than reported after the last.

3. **Zero is a valid declared count, and it is the default.** A command may be
   issued with a budget of zero paid calls. It then does every free thing it
   can, establishes what the paid work would cost, and stops. That is how a
   count gets stated in advance without spending to find it out: the first pass
   is always free, and the number it produces is what the second pass is issued
   against.

   **Zero is a fact here, never a sentinel.** Zero calls were authorised and
   zero were made, and both are known precisely. What may be unknown is *how
   many would be needed*, and that stays `unknown` with a reason — the
   convention `harness-status.json`'s reading block states and the harness
   payload already follows. A run that reported `would_need: 0` when nobody
   could count would be claiming the work is free, which is the same
   substitution refused everywhere else in this corpus.

4. **A declared count of zero is carried downstream.** Anything produced under
   a zero-budget run says so. A consumer reading a row must be able to tell a
   free-path result from a complete one: they are different claims, and a
   partial answer presented as whole is the shape of finding this organisation
   keeps recording. The signal travels with the payload rather than being
   inferred from an empty field.

5. **Human-issued, every time.** Consent does not carry forward. A person
   approving a run has approved that run. There is no remembered permission, no
   `--yes` that persists, and no session-level grant, because the thing being
   consented to is an amount rather than a category.

6. **A paid dependency is declared where it is used.** A module that can cause a
   paid call says so, at the top, in the plainest available words. A reader
   inspecting what a tool does must not have to trace a call graph to find out
   whether it spends.

7. **The unpaid path stays.** Anything built on a paid service keeps a mode that
   works without it — degraded, partial, or refusing with a reason. A capability
   that only exists while the meter runs is one this organisation does not own,
   and P1 is what that costs.

8. **This is not a budget.** No threshold makes an unattended call acceptable.
   The rule is about who caused it, not how much it was, and a cheap call made
   by nobody is exactly the thing being refused.

**Enforcement, and what it can and cannot see.** A registry of paid surfaces —
which modules may spend — with a check that no scheduled entry point, workflow
or hook reaches one. It can see a static call path from a scheduled context into
a declared paid module. **It cannot see a paid call made through a module nobody
declared**, which is why clause 6 is a rule about writing rather than a
derivation, and why a paid surface added without declaring it is the failure
this depends on people not committing.

## Consequences

**Some obvious features become impossible**, and deliberately. Nightly
summarisation. A watcher that classifies incoming work. Anything that keeps a
model warm. Each is a real capability and each is refused.

**A metered call and an interruption become the same event**, which resolves
what looks like a tension with P13. P13 says a person is interrupted only by a
decision, and spending money *is* a decision — the one kind of step that must
not be automated away. Interruptions for sequencing are the thing P13 removes;
this is not one of those.

**Cost stays legible without anybody instrumenting it.** If every call has a
person behind it, the spend is bounded by attention, which is a bound nobody has
to configure or monitor.

**Batch work gets more awkward.** Processing a hundred rows means one command
that states it will make a hundred calls, rather than a loop that discovers it.
That is more work to build and it is the clause that will be argued with first.

**A test suite may not call a paid service.** CI is unattended by definition.
Anything exercising a paid integration does so against a recorded response or a
local substitute, which is a constraint on how those integrations are designed
rather than an afterthought.

## Alternatives considered

**A spending cap.** Rejected as the wrong axis. A cap makes an unattended call
acceptable below a number, and the harm being prevented is not the amount — it
is that nobody decided. A cap also fails silently in the direction that matters:
it is discovered by being hit.

**Approve a session, then run freely within it.** Rejected by clause 5. What a
person is consenting to is an amount, and an amount cannot be consented to
before it is known. It is also the mechanism by which a careful rule becomes a
habit of clicking through.

**Allow scheduled calls with a notification.** Rejected. A notification about
money already spent is a report, not a decision, and P13's own clause is that a
prompt without options is a report delivered as an interruption.

**Rely on provider-side limits.** Rejected under P1. That is somebody else's
mechanism protecting this organisation from itself, and it is a rental of the
control as well as the service.

## Revision triggers

- A paid service that is genuinely free at the margin, which would make clause 1
  cost more than it protects.
- Batch work where even a zero-budget pass cannot establish the count, which
  would mean clause 3's free-first pass does not generalise and clause 2 needs
  a form for bounded uncertainty.
- A paid call reaching production through an undeclared module, which would mean
  clause 6 needs a mechanism rather than a rule.
- Anybody proposing a remembered approval, which is the signal that clause 5 is
  being felt and is the moment to check whether the workflow is wrong instead.

## Amendments

*(none)*
