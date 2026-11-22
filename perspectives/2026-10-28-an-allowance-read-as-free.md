# An allowance read as free

**2026-10-28.** Surveying the organisation's repositories for a standards plan,
then estimating one repository's CI minutes, until the host refused every call
on the session's credential for the rest of the hour. Attributed, dated, binds
nothing.

Tools: Claude Opus 5.5, which made the mistakes described and wrote this page;
reviewed and committed by a human.

The corpus already had the rule. `records/DRAFT-no-unattended-spending.md` §2
says that where a command's call count depends on what it finds, the count is
shown and confirmed before the first call. It was not followed, and the reasons
are below, roughly in the order they mattered.

## The rule was never in front of the session

**Assumption:** a rule that binds a session's conduct is one the session has
read.

The spending record's `Restated in` row says *Nothing*. `AGENTS.md`, the page
read first, does not mention spending. The session opened that record for the
first time while drafting the record this page belongs to. Every rule it did
follow that day, such as the voice check, the leak check, local-only delivery
and one question at a time, was on a page it read at the start or was enforced
by a tool it ran.

**Would have caught it:** the rule restated where a session reads before it
acts, as `records/DRAFT-the-read-document-governs.md` requires of a decision
that has to govern. `AGENTS.md` item 20 is that restatement, added with the new
record. Nothing mechanical reaches a scratch script.

## The record's own words put the call outside it

**Assumption:** a call that costs no money is outside a rule about spending.

Had the session read the record, its Context would have reassured it: a host
API is listed among the free things, with "a credential that costs nothing per
call". The same record counts a CI runner's time as paid because the allocation
is shared, whatever the plan bills. That reasoning applies to an API allowance
word for word, and the record stops short of saying so.

**Would have caught it:** a definition of spend that follows the sharing, not
the money. `records/DRAFT-a-shared-allowance-is-drawn-on-politely.md` makes it
for allowances. It is Proposed, on a local branch.

## The price was on the screen

**Assumption:** a count printed before a job starts is a size, not a cost.

The run listing reported 2,500 runs before the first job was read. Reading each
run's jobs costs one call per run, which made the job about half the
credential's hourly allowance. The number was read as how much data there was.
Nothing compared it with what remained, which a free query would have shown.

**Would have caught it:** reading the remaining allowance before a fan-out and
stating the count against it. That is the new record's §1, and nothing
mechanical does it yet.

## An estimate was asked for, and a census was run

**Assumption:** a measured figure is better than an estimated one.

The question was for an estimate. The first design read every job of every run
in forty days, following the method the 2026-10-24 retrospective used for a
single day. A day's method was scaled forty-fold without being priced again. A
sample of a few dozen runs per workflow answers an estimate for a fraction of
the calls.

**Would have caught it:** sampling for an estimate and treating a census as a
command of its own, the new record's §2.

## Nothing was kept, so the retry paid twice

**Assumption:** a job that fails on a transient error needs a retry.

The script wrote its results only when it finished. A server error ended the
first attempt about two minutes in, and everything it had read was lost. The
fix was a retry around each call, and the second attempt read everything again
from the beginning. The fix treated the error and ignored the cost: what failed
was a design that could not resume.

**Would have caught it:** writing each response as it arrives and resuming
from it, the new record's §3.

## A habit from local work met a shared service

**Assumption:** parallelism is free speed.

The same session had spent hours making test suites and git reads faster with
thread pools, where the cost of parallelism is one machine's cores. It carried
the habit to a shared service and sent sixteen requests at a time. The two
attempts together ran about five minutes before the allowance was gone. The refusal
was the hourly limit's. Whether the concurrency also met the host's limit on
simultaneous requests is not established, and an earlier report of that in the
session was wrong.

**Would have caught it:** a small declared concurrency for any one service,
the new record's §4.

## The limit was read after the refusal

**Assumption:** a limit is something to check when it bites.

The remaining allowance was first read after the host refused, and it showed
none left and a reset twenty-three minutes away. The session then scheduled a
third attempt to start the moment the allowance returned, as a background job
waiting on the reset. The person cancelled it.

**Would have caught it:** stopping at the first refusal that names a limit and
asking before drawing again, the new record's §5 and §1.

## The session's earlier draws were never added up

**Assumption:** each job's draw stands alone.

Earlier the same day, a survey of all 123 repositories read each one's
settings, rulesets, tags and workflow files. Its call count was not measured.
From its shape it ran to hundreds, perhaps over a thousand, and whether it fell
inside the same hour is not established. That is inference. No job knew what
the jobs before it had drawn.

**Would have caught it:** the remaining-allowance read, which counts every
draw on the credential and not just the job's own.

## The lesson stayed with its resource

The 2026-10-24 retrospective concerned the same repository and the same tool,
and its lesson was to price a draw before making it. It was applied where it
was learnt: pushes became priced, and the spending record gained its CI
paragraph. It did not travel to the next shared resource. Recurrence by one
practitioner is evidence, by `AGENTS.md` item 11, and here it shows that a
lesson stated for one resource is not yet a rule about resources.
