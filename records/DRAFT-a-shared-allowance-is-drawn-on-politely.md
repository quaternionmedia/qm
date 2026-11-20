# QM-XXXX — A Shared Allowance Is Drawn On Politely

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-10-28 |
| **Pends on** | The share in §1, written below as a tenth of what remains. |
| **Principle** | `interrupted-only-by-a-decision` — a person is interrupted only by a decision; `systems-over-heroics` — systems over heroics; `governance-finds-the-reader` — governance finds the reader, not the reverse |
| **Restated in** | `AGENTS.md` item 20; `project-seed/ide/AGENTS.md` item 16 |

## Context

`DRAFT-no-unattended-spending.md` decides who may cause a paid call. It counts a
CI runner's time as paid, whatever the plan bills for it in money, because the
allocation is the organisation's and every repository shares it. Its Context
places a host API among the free things: a credential that costs nothing per
call.

A call that costs nothing still draws on an allowance. A code host grants each
credential a number of calls per window and a limit on how many it serves at
once, and past either it refuses every caller on that credential until the
window resets: every session, every tool and every person using it. A model
provider's free tier, a package index and a CI runner pool are allowances of the
same shape. Drawing one down is not a bill. It is an outage for everyone else
on it, and they cannot see why.

On 2026-10-28 a session asked for an estimate of one repository's CI minutes
read the job list of every run in a forty-day window, sixteen requests at a
time. It restarted from the beginning after a server error, and the host
refused it at its hourly limit, so every caller on that credential was refused
for the rest of the hour.
`perspectives/2026-10-28-an-allowance-read-as-free.md` is why it went that way.

No-unattended-spending §2 already names the missing step: where a count depends
on what a command finds, the count is shown and confirmed before the first
call. What it does not say, because its subject is consent, is how a call a
person did authorise is made. That is manners, and manners are what this
record decides.

## Decision

**A call to a shared allowance is priced, sampled, kept, paced and stopped.** An
allowance is any limit a service sets per credential, per organisation or per
window that more than one session or person draws on.

1. **Priced.** A command that will make more than a handful of calls to one
   service reads the remaining allowance first, since the query costs nothing,
   and states its count before its first call: exactly where the count is known,
   as an upper bound where it depends on what the command finds. A count above
   a tenth of what remains is confirmed by a person before it starts, in the
   form no-unattended-spending §2 gives a paid call.
2. **Sampled.** An estimate reads a sample sized to its question and states the
   sample beside the number. A census is a command of its own, priced as §1
   prices it.
3. **Kept.** Every response is written to disk as it arrives. A job that stops
   resumes from what it holds and never starts again from the beginning: a
   restart draws the same allowance twice.
4. **Paced.** Requests to one service run a small, declared number at a time,
   and wait as long as the service asks them to. Concurrency is for local work.
5. **Stopped.** A refusal that names a limit ends the job at once. The job
   reports what it read, what it did not and when the allowance resets, and it
   does not retry. A server error is retried a bounded number of times, each
   after a longer pause than the last.
6. **Said.** A session that exhausts a shared allowance tells the person at
   once, with the time it resets. Every other caller on that credential is
   failing for a reason it cannot see.
7. **One seam per service.** The corpus's tools reach a service through one
   module that applies §§1, 3, 4 and 5. A session's own scripts import that
   module rather than spawning the service's CLI themselves.

**Enforcement, and what it can and cannot see.** A check that no module under
`ci/` or `project-seed/ci/` spawns the host's CLI outside the seam, and the
seam's tests, which break §1, §3, §4 and §5 one at a time and watch each fail.
**It cannot see a script written outside the repository**, and a session's
scratch script is where the draw in the Context was made. So §6 and the second
half of §7 are conduct, and they reach a session only where it reads them:
`AGENTS.md` item 20 restates them on the page read first, and
`project-seed/ide/AGENTS.md` item 16 on a project's.

## Consequences

**A large read gets slower.** A census of thousands of items at a few requests
at a time takes several times as long as sixteen at a time. That cost is
accepted: the faster version spent an hour of everybody's access.

**An estimate says what it extrapolates.** The sample, its size and how it was
drawn travel with the number, so a reader can tell an estimate from a count.

**The corpus's own tools move behind the seam.** Several modules under `ci/`
spawn the host's CLI directly. The ones that already route it through a single
function of their own become the seam's callers rather than seams of their own.

**A session asks before a large draw.** §1's confirmation is an interruption,
and it is the kind `interrupted-only-by-a-decision` keeps: spending a share of
an allowance other people depend on is a decision, and the person it belongs
to is asked before it is made.

## Alternatives considered

**Fold this into no-unattended-spending.** Rejected. That record is about who
causes a paid call, and it rejects thresholds as the axis of consent: a cheap
call made by nobody is exactly what it refuses. This record is about the manner
of a call a person did issue, and it needs a threshold, §1's share, to decide
when a count must be confirmed. One record would then carry two decisions, one
refusing thresholds and one setting one.

**A cap per session, enforced by the seam.** Rejected. A cap cannot see what
other sessions on the same credential have drawn, so a session under its cap
can still exhaust the allowance. Reading what remains can see it.

**Rely on the host's own limits.** Rejected. The limit is the thing exhausted.
It protects the host from its callers, not the callers from one another, and it
reports only after the harm.

**A credential per session.** Rejected for now. It isolates one session's draw
from another's, but a credential is a person's to issue and revoke, a standing
token per session is the remembered permission no-unattended-spending §5
refuses, and the organisation's own limits stay shared across every credential.

## Revision triggers

- A service that offers no way to read what remains of its allowance, which
  makes §1's read impossible and needs a form for an unknown allowance.
- A draw that §1's share lets through and that still exhausts the allowance,
  which means the share is wrong.
- A scratch script that exhausts an allowance after this record is restated
  where sessions read, which means §7 needs a mechanism rather than a rule.

## Amendments

*(none)*
