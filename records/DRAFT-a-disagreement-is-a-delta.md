# QM-XXXX — A Disagreement Is a Delta

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-08-17 |
| **Pends on** | Nothing — ready for ratification |
| **Principle** | P6 — decisions are documented or they didn't happen; P8 — systems over heroics |
| **Restated in** | `handbook/handoffs/two-views-one-dataset.md` |

## Context

Two systems now hold facts about the same things. dossier tracks repositories,
branches, pull requests and units of work; qmcp runs those units and records
what it ran. `docs/ref/addresses.md` gives both one way to name a row, so for
the first time they can be asked the same question and give different answers.

They will. A branch row synced an hour ago against a ref that moved since; a
delta dossier calls `review` that qmcp has no invocation for; a pull request
number one side never learned was closed. None of these is a fault. They are
what two independent observers of a moving system look like.

The usual answer is to name one side authoritative. That answer is available
here and it is wrong for this organisation, for two reasons. It is arbitrary —
the git ref is authoritative about branches and qmcp is authoritative about
invocations, so "which system wins" has no single answer even in principle. And
it is lossy: the losing side's value is discarded at the moment of comparison,
which is exactly when somebody would want to see it.

A dashboard that silently resolves disagreements teaches its readers that the
two views agree. They do not, and the reader has no way to find out.

## Decision

**A disagreement between two views of one address is a delta.**

When two systems hold different values for the same address, neither wins.
The disagreement becomes a unit of work with a name, a lifecycle and an audit
trail — the same `delta` every other unit of work in this organisation is, so
it appears in the same queue, is prioritised against the same list, and is
closed by somebody deciding rather than by a comparison being run again.

Four things follow, and they are the whole of the rule:

1. **Neither value is discarded.** The delta records both, and which system
   said which. A reader who disagrees with the resolution can see what was
   resolved away.

2. **The delta is identified by what disagrees, not by when it was noticed.**
   Its identity is the address plus the field. Re-running detection over an
   unresolved disagreement finds the same delta rather than opening a second
   one, and a queue that grows by one row per sync is a queue nobody reads.

3. **Detection never sets the phase past `brainstorm`.** Noticing that two
   numbers differ is not deciding anything. A tool that opened the delta at
   `planning` would be asserting that somebody had looked at it.

4. **Convergence is reported, not concluded.** When the two values agree again,
   the detector says so and does not close the delta. It cannot know whether
   anyone acted or whether one side simply re-synced, and `complete` is a claim
   about work having been done. Closing is a person's, in the same way
   ratification and the version tag are.

## Consequences

**A disagreement stops being an error and becomes a work item**, which is the
point: it is scheduled, prioritised and closed like anything else, instead of
being handled inside whichever renderer noticed it first.

**Two dashboards can be built before anyone decides who is right**, because the
question is no longer blocking. `handbook/handoffs/two-views-one-dataset.md`
named it as the decision that had to precede the milestone; this record is that
decision, and it removes the precedence rather than answering the question in
the form it was asked.

**The queue can fill with noise if detection is careless.** A field that
legitimately differs between two systems — a timestamp of when each observed
something — would open a delta on every sync. Which fields are compared is a
declaration, not everything both sides happen to hold, and getting that list
wrong is the failure mode of this record.

**A delta with no owner is still an open row.** This creates work items; it does
not create anybody to do them. A growing reconcile queue is a real signal about
the two systems and should be read as one.

## Alternatives considered

**Name one system authoritative.** Rejected as arbitrary and lossy, above. Worth
noting it is not merely unpalatable — there is no consistent assignment, since
authority genuinely differs by kind.

**Resolve by recency.** The later-observed value wins. Cheap, and wrong whenever
the later observation is the stale one — a nightly sync overwriting a value a
person put right an hour earlier.

**Report disagreements in a separate list.** A reconciliation report beside the
dashboards. Rejected because it invents a second queue with its own lifecycle,
its own staleness and its own reader, when the organisation already has one that
does exactly this. A disagreement *is* a unit of work; giving it a different
container hides that.

**Refuse to display anything that disagrees.** Safe and useless: the rows most
worth looking at disappear precisely when they become interesting.

## Revision triggers

- A kind of disagreement that is genuinely not work — where the right response
  is always automatic — would mean this rule is too broad and needs an exemption
  with a stated reason.
- A reconcile queue that grows without being read means the delta lifecycle is
  the wrong container after all, and the third alternative deserves another look.
- A third system holding the same addresses. This record is written for two
  views and says nothing about how three disagree.

## Amendments

*(none)*
