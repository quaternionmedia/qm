# QM-XXXX — Nothing Unattended Spends

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-08-20 |
| **Pends on** | A mechanism by which a pull request a bot opens starts no cloud CI job until a person starts it (Enforcement); until there is one, it is a declared gap |
| **Principle** | `interrupted-only-by-a-decision` — a person is interrupted only by a decision; `ownership-is-the-deliverable` — ownership is the deliverable; `systems-over-heroics` — systems over heroics |
| **Restated in** | Nothing. The qmPM standardisations page cites it, which is a citation rather than a restatement: that page decides nothing and says so |

## Context

Most of what this organisation's tooling does is free and local. It reads
git, it reads a SQLite file, it calls a host API with a credential that costs
nothing per call. The worst outcome of a local loop that runs too often is a
warm laptop, and the bound on its time is what stops it
(`DRAFT-shrink-the-black-box.md`).

Wiring a metered API in changes that, and it changes it in a direction that is
easy to miss: **the failure mode of automation stops being a wrong answer and
starts being a bill.** A retry loop that was a nuisance becomes an expense. A
scheduled job somebody forgot becomes a standing charge. A detector that fires
once per row becomes a function of how many rows exist.

Cloud CI is the metered service already in use. A hosted runner's time comes
out of an allocation the organisation pays for and every repository shares,
and every push spends it. On 2026-10-24 one project's pushes started 825
workflow runs and some thirty-five runner-hours of jobs (`gh api
repos/quaternionmedia/apothecary/actions/runs`, each run's jobs summed from
start to completion), a number nobody stated before the pushes were made.

The organisation already has the ingredients for this to go wrong quietly. It
has a harness that runs things on command. It has a self-check that runs a suite
and could as easily run a model. It has a disk tool with a `--check` exit code
*specifically so a scheduled task can drive it*, and no such task, because
scheduling one is a decision of its own. The reasoning is this record's: **a scheduled
program that acts while nobody is watching is a different kind of thing from the
same program run by a person.**

There is also a governance reason, and it is `ownership-is-the-deliverable`'s. A component is owned only if
it can be run, rebuilt and modified without anyone's permission. A metered
dependency is a rental, and a rental that bills on a timer is one whose meter
somebody else controls. Keeping every paid call attached to a human command is
what keeps the dependency a tool rather than a subscription to a behaviour.

## Decision

**No unattended process may call a paid service. Every paid call is a direct,
deterministic, human-issued command.**

**A cloud CI runner's time is a paid service**, whatever the plan bills for it
in money. The push, the tag or the dispatch that starts a run is the command,
and the jobs the run starts are the calls. A run on the contributor's machine
spends nothing this record counts; it is bounded in time instead, as every
guard is.

1. **Direct.** A person issues the command that causes the call. Not a schedule,
   not a watcher, not a hook, not a retry, not a background refresh, and not a
   second call the first one decided to make. In CI: not a scheduled workflow,
   not a run a bot's pull request starts, and not a run that starts itself
   again.

2. **Deterministic.** The command determines what is called and how many times.
   A command whose call count depends on what it finds is not deterministic, and
   the person issuing it cannot consent to a number nobody can state in advance.
   Where a count depends on input, the count is shown and confirmed before the
   first call rather than reported after the last. A push's count is the jobs
   its workflows start, stated from their recorded minutes before it is made. A
   run that splits and runs again on what it finds, as a merge queue bisecting a
   failed batch does, shows each further run and has it confirmed.

3. **Zero is a valid declared count, and it is the default.** A command may be
   issued with a budget of zero paid calls. It then does every free thing it
   can, establishes what the paid work would cost, and stops. That is how a
   count gets stated in advance without spending to find it out: the first pass
   is always free, and the number it produces is what the second pass is issued
   against. In CI the free pass is the contributor's machine: the workflows run
   there first, and what the push would start is the number it is made against.

   **Zero is a fact here, never a sentinel.** Zero calls were authorised and
   zero were made, and both are known precisely. What may be unknown is *how
   many would be needed*, and that stays `unknown` with a reason — the
   convention `status/harness.yaml`'s reading block states and the harness
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
   consented to is an amount rather than a category. A person who authorised a
   push has authorised that push's runs, and the next push is asked again.

6. **A paid dependency is declared where it is used.** A module that can cause a
   paid call says so, at the top, in the plainest available words. A reader
   inspecting what a tool does must not have to trace a call graph to find out
   whether it spends.

7. **The unpaid path stays.** Anything built on a paid service keeps a mode that
   works without it — degraded, partial, or refusing with a reason. A capability
   that only exists while the meter runs is one this organisation does not own,
   and `ownership-is-the-deliverable` is what that costs.

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

For CI the registry is each workflow's triggers. A check that no workflow runs
on a schedule or starts itself again, and that a bot's pull request starts no
job until a person starts it, is not built: it arrives as a declared gap. The
host names the person who re-runs a run (`github.triggering_actor`, which on a
re-run differs from the `github.actor` who started the first), so a job
conditioned on it waits for a person; that is the documented behaviour, not one
any workflow here uses.

## Consequences

**Some obvious features become impossible**, and deliberately. Nightly
summarisation. A watcher that classifies incoming work. Anything that keeps a
model warm. Each is a real capability and each is refused.

**A metered call and an interruption become the same event**, which resolves
what looks like a tension with `interrupted-only-by-a-decision`. `interrupted-only-by-a-decision` says a person is interrupted only by a
decision, and spending money *is* a decision — the one kind of step that must
not be automated away. Interruptions for sequencing are the thing `interrupted-only-by-a-decision` removes;
this is not one of those.

**Cost stays legible without anybody instrumenting it.** If every call has a
person behind it, the spend is bounded by attention, which is a bound nobody has
to configure or monitor.

**Batch work gets more awkward.** Processing a hundred rows means one command
that states it will make a hundred calls, rather than a loop that discovers it.
That is more work to build and it is the clause that will be argued with first.

**A test suite may not call a paid service.** A CI run, once a push has
started it, runs unattended. Anything exercising a paid integration does so
against a recorded response or a local substitute, which is a constraint on how
those integrations are designed rather than an afterthought.

**Every push is priced before it is made.** Its jobs and their recorded minutes
are stated, and the person pushing authorises that number. A project keeps its
long suites on the contributor's machine and in CI at a version tag, and its
pull requests' CI to what is cheap and must be seen on the host.

**A bot's pull requests are unattended spend.** Dependency updates a bot opens
start CI that nobody issued. Grouping them (one pull request per ecosystem per
interval) bounds how often, which this record does not count as consent; until
a job waits for a person, the runs they start are the declared gap above.

## Alternatives considered

**Count only money.** A free plan bills runner time on a public repository at
nothing. Rejected: the allocation is the organisation's, shared by every
repository and every person in it, and spent at a rate nobody sees until a
day's runs are summed. The harm is the one this record refuses, a spend nobody
decided, and it does not change with the currency.

**A spending cap.** Rejected as the wrong axis. A cap makes an unattended call
acceptable below a number, and the harm being prevented is not the amount — it
is that nobody decided. A cap also fails silently in the direction that matters:
it is discovered by being hit.

**Approve a session, then run freely within it.** Rejected by clause 5. What a
person is consenting to is an amount, and an amount cannot be consented to
before it is known. It is also the mechanism by which a careful rule becomes a
habit of clicking through.

**Allow scheduled calls with a notification.** Rejected. A notification about
money already spent is a report, not a decision, and `interrupted-only-by-a-decision`'s own clause is that a
prompt without options is a report delivered as an interruption.

**Rely on provider-side limits.** Rejected under `ownership-is-the-deliverable`. That is somebody else's
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
- A CI host that bills nothing and shares nothing, which would make a push a
  free call again.

## Amendments

*(none)*
