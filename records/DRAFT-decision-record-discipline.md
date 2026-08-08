# QM-XXXX — Decision-Record Discipline

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-06-09 |
| **Pends on** | Nothing — ready for ratification |
| **Principle** | P6 — decisions are documented or they didn't happen |

## Context

Decision documents drift in predictable ways: drafts accumulate references to
their own revision history, numbers get assigned before ratification and then
`renumber`, supersession language leaks into documents never published. Drift
of this kind was observed and fixed in the org's first drafting round; the
discipline below makes prevention mechanical rather than memorial.

Adoption itself needs a discipline too, and for a while this corpus only had
one that fit new projects. A project created under the constitution can be
compliant from its first commit. A project that predates its adoption of the
constitution generally cannot: its datastore, its dependencies, and its
integration shapes were chosen before the records existed. With only
"instantiated" and "improvised" available as states, such a project faced a
choice between claiming a compliance it does not have and not adopting at
all. Both outcomes are worse for the org than an honest third answer, and the
second is worse than it looks — the projects most in need of governance are
exactly the ones with the longest history of decisions made without it. §5
supplies that answer.

## Decision

1. Every QM project carries an `adr/` directory instantiated from the
   constitution's `project-seed/` — process contract, template, and CI lint —
   at project creation, or at the point of adoption for a project that
   predates this corpus. A project without it is improvised, not
   instantiated.
2. The discipline at both levels is: **before ratification, documents have no
   memory; after ratification, they have nothing but memory.** Drafts are
   numberless, referenced by title, rewritten whole when positions change.
   Accepted records are append-only (dated Amendments); reversals are new
   records that supersede; numbers are assigned at ratification by the index,
   are permanent, and are never reused.
3. Ratification is a human commit. Assistants and contributors draft; a human
   flips status, assigns the number, updates the index, and names the record
   in the commit message.
4. Drafting sessions (human or AI-assisted) receive the process contract, the
   constitution, and the current index as inputs, and present a plan with a
   contradiction check before writing.
5. **Adoption by an existing project is declared with its conflicts
   enumerated.** A project adopting this corpus after the fact ratifies an
   adoption-and-scope record whose substance is a table of every known
   conflict with an org record, each row naming the conflict, the record it
   violates, and what compliance would look like. The rules governing that
   table:
   - **Enumeration is not a waiver.** A row records that a conflict is known
     and unresolved. It does not authorize it, does not create an exception,
     and does not soften the record it conflicts with. Records that admit no
     waivers continue to admit none.
   - **A schedule is not required, and an invented one is worse than none.**
     Enumerating a conflict and sequencing its remediation are different
     decisions with different owners and different information behind them.
     A date not derived from a real estimate either slips, teaching
     contributors that recorded dates are decorative, or forces a conflict
     closed badly to meet it. Revision triggers are observable events, as
     everywhere else in this corpus.
   - **Scope is frozen per conflict.** While a conflict is open, the project
     adds no new coupling that deepens it. This is not remediation; it stops
     the eventual work from growing while it is unscheduled, and it is the
     one commitment available that does not depend on a schedule.
   - **The table is the project's compliance surface**, amended when a
     conflict is resolved or a new one is found, and it is what the project
     points at instead of claiming compliance it does not have.
   - **Each row says how the conflict is pinned.** Where a conflict can be
     captured by a test, the row names it. A defect described only in prose
     drifts away from the code as the code changes, and a conflict that is
     quietly fixed leaves a row asserting something untrue. A test pinning it
     cannot drift, and a strict-xfail pinning it turns the suite red the
     moment the defect is fixed, which is the prompt to update the row. Where
     no test is possible, the row says that too, rather than leaving the
     absence to be inferred.
6. **A project in this state is instantiated, not improvised.** The
   distinction the corpus draws is between a project that carries the
   governance machinery and one that does not — never between a compliant
   project and a non-compliant one. A project that has enumerated eight
   conflicts is more governed, not less, than one that has enumerated none
   because nobody looked.
7. **A claim of fact about a system names how it was established.** This
   corpus governs how decisions are written and, until this clause, said
   nothing about how the facts underneath them are checked. A record can be
   flawlessly disciplined — squashed, numberless, honest about its
   alternatives, carrying real revision triggers — and rest on a root cause
   nobody reproduced.
   - **Assertions that something is broken, unsupported, non-compliant, or
     behaves a particular way carry their reproduction**: the command run and
     what it returned, in enough detail that a reader can run it again.
     "The image does not build" is an opinion; "`docker build .` fails at the
     `bezier` install with `No module named 'pkg_resources'`" is a finding.
   - **A claim that has not been reproduced is marked as inference**, not
     omitted and not stated flatly. Undecided inputs already have to be
     visible under the drafting rules; unverified ones are the same problem
     one layer down.
   - **Records name the commit they were written against.** A review is a
     claim about a specific tree. Naming it is one line, and it is what makes
     staleness a checkable fact rather than an assumption nobody restates.
   - Cost accepted: this adds friction to every record, and most of it will
     be spent on claims that were never in doubt. The judgement is that the
     expensive errors are not the claims that felt uncertain — those get
     checked — but the ones that felt settled.

## Consequences

- CI lint in every repo rejects: banned vocabulary in drafts
  (`previously|originally|earlier draft|re-review|renumber|retroactive|
  supersedes the ... (stance|finding)|corrected`), numbered filenames not
  Accepted+, edits to an Accepted record outside its Amendments region,
  index/directory mismatches.
- Onboarding cost for contributors and assistants is the process contract —
  one page, supplied with every drafting session.
- Cost accepted: ceremony on small decisions. Mitigation: one-decision
  records can be short; brevity is compliant, absence is not.
- §5 makes an existing project's gap set legible in one table, which is the
  point: an adopting project that enumerates is auditable, and one that
  adopts silently is not.
- Cost accepted: a project may sit with open conflicts indefinitely, because
  §5 deliberately declines to require a schedule. The org trades the
  appearance of urgency for accuracy, and relies on the frozen scope and the
  visibility of the table rather than on a date nobody costed.
- §7 shifts some of this corpus's enforcement weight from prose discipline to
  execution. The lint, the handoff contract, and human review before push all
  govern how a record reads; none of them ask whether its claims are true. A
  reproduction in the record is the cheapest available check, because it lets
  any later reader re-run it rather than re-reason about it.
- §7's reproductions decay: a command that ran clean a year ago may not run
  at all now. That is a feature — a reproduction that no longer reproduces is
  a revision trigger firing, and it is more informative than prose that
  cannot go stale because it never committed to anything.

## Alternatives considered

1. **Convention without enforcement** — rejected: the observed drift occurred
   *during* an attentive, two-party drafting round; unenforced convention
   does not survive contributor turnover.
2. **Full RFC process** — rejected as ceremony disproportionate to org size;
   records + lint capture the value at a fraction of the weight.
3. **Require an existing project to remediate before adopting** — rejected:
   it inverts the dependency. The constitution is what makes conflicts
   legible as conflicts, so withholding adoption until they are fixed means
   fixing them without the framework that names them, and leaves a project
   ungoverned for precisely as long as it is most in need of governance.
4. **Require dated remediation milestones per conflict** — rejected: the
   dates would be invented. The one instance available offers no scoping for
   its largest conflict, and a schedule with nothing behind it converts a
   recorded commitment into a recorded fiction.
5. **Grant time-boxed waivers instead of enumerating conflicts** — rejected:
   several org records admit no waivers at all, so a waiver mechanism here
   would relax them from the outside, which is the one thing project-level
   adoption may never do.
6. **Leave verification to reviewer diligence** (§7) — rejected on this
   corpus's own precedent. "Convention without enforcement" was rejected in
   alternative 1 for vocabulary drift, on the grounds that it did not survive
   an attentive two-party drafting round. The same argument applies with more
   force here: a reviewer can see that a record is well-formed, and cannot
   see that its root cause was never reproduced.
7. **Require every claim to carry a reproduction, including obvious ones** —
   rejected as the failure mode of the clause rather than a stricter version
   of it. Mandating a citation for "PostgreSQL is open source" produces
   ceremony that trains readers to skip the field, which is exactly how the
   evidence marking loses its signal. §7 asks for reproductions where a claim
   is doing work — a defect, an incompatibility, a behavior — and inference
   to be marked as inference everywhere else.

## Revision triggers

- The lint produces sustained false positives (vocabulary rules need tuning).
- A second governance artifact class emerges (e.g., runbooks) needing its own
  lifecycle — revisit whether this record generalizes or a sibling is needed.
- A second existing project adopts the corpus — §5 was written from one
  instance and should be confirmed or revised against the next.
- A §5 conflict table goes stale, or a project uses enumeration to park a
  conflict it has no intention of closing — the no-schedule stance is being
  abused and needs a forcing function it currently lacks.
- A ratified record is found resting on a claim nobody reproduced — §7 is
  being written around rather than applied, and needs a mechanical check
  rather than a stated obligation.
- §7's reproduction fields become boilerplate that nobody runs — the clause
  has become the ceremony alternative 7 rejects, and should be narrowed to
  the claim classes where it earns its cost.
- A second assisted session audits its own false assumptions and finds a
  materially different distribution than the one in
  `perspectives/2026-08-07-verification-discipline-in-assisted-sessions.md` —
  §7 was shaped by a single session's error profile and should be re-cut
  against the second.

## Amendments

*None.*
