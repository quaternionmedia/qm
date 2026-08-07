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
"renumber," supersession language leaks into documents never published. Drift
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
6. **A project in this state is instantiated, not improvised.** The
   distinction the corpus draws is between a project that carries the
   governance machinery and one that does not — never between a compliant
   project and a non-compliant one. A project that has enumerated eight
   conflicts is more governed, not less, than one that has enumerated none
   because nobody looked.

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

## Revision triggers

- The lint produces sustained false positives (vocabulary rules need tuning).
- A second governance artifact class emerges (e.g., runbooks) needing its own
  lifecycle — revisit whether this record generalizes or a sibling is needed.
- A second existing project adopts the corpus — §5 was written from one
  instance and should be confirmed or corrected against the next.
- A §5 conflict table goes stale, or a project uses enumeration to park a
  conflict it has no intention of closing — the no-schedule stance is being
  abused and needs a forcing function it currently lacks.

## Amendments

*None.*
