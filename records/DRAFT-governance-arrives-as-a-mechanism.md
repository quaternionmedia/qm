# QM-XXXX — Governance Arrives as a Mechanism

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-08-14 |
| **Pends on** | Nothing — ready for ratification |
| **Principle** | P8 — systems over heroics; P6 — decisions are documented or they didn't happen; P11 — governance finds the reader, not the reverse |
| **Restated in** | Nothing, deliberately. See §4 |

## Context

This corpus has measured its own governance twice and got the same answer both
times. `perspectives/2026-08-12-nineteen-reversals-and-what-a-clause-cannot-fix.md`
counted nineteen findings stated and withdrawn while four discipline clauses
were being written, and the rate did not change.
`perspectives/2026-08-13-thirteen-breaks-and-the-five-that-became-yours.md`
counted thirteen protocol breaks and found that **every clause broken had been
read in full by the session that broke it** — the eight caught were caught by a
check that ran, not a rule that was remembered.

Two failures follow from writing governance as prose, and both are in this
corpus today.

**A rule can claim to be mechanical and not be.**
`records/DRAFT-version-tags-are-claims.md` §7 said its §1 was "mechanical rather
than customary." Nothing read a tag until 2026-08-14 — six days during which the
sentence was true of an intention and false of the repository. Two lightweight
tags were cut in that window asserting what §6 says a lightweight tag cannot.

**A record can assert a state of the world that is not the case.**
`records/DRAFT-outbound-licensing.md` §12 states that "Every QM repository is
REUSE-compliant." Checked on 2026-08-14: `qmcp` and `alfred` carry no
`REUSE.toml`, and `qmcp` declares no licence at all — there is no grant to
reproduce it. The record is not wrong about what should be true. It is wrong
because it says *is* about something it never measured, and nothing in the
corpus could notice.

There is a third cost, paid by a reader rather than by the org. Mandatory
reading before a first edit — `AGENTS.md`, `handbook/async-contract.md`,
`handbook/handoffs/README.md` — stands at 626 lines, and **rose by 58 during a
session whose stated aim included reducing it.** The corpus is about to be read
by people who did not build it, and prose is the part of it that does not scale
to a stranger.

## Decision

1. **A rule that binds arrives with a mechanism, or it arrives as a declared
   gap.** Prose alone is an intention, not a rule. `ci/pattern-registry.yaml`
   already holds the declared-gap form: an entry with `check_exists: false` is
   a rule this org has named and not yet made enforceable, counted rather than
   assumed. Writing a clause and stopping is the one path this record closes.

2. **A record states a requirement. It does not assert an empirical
   universal.** "Every QM repository is X" is a sentence a generator writes
   from evidence, with a timestamp, never a sentence a record writes from
   intent. A record says what must hold; `governance-status.yaml`,
   `gate-status.json` and their kin say what does. Where a record needs to
   refer to compliance, it names the document that measures it.

3. **A record's enforcement clause names its mechanism by path, and the
   mechanism exists at ratification.** A record whose §Enforcement names
   nothing is honest and permitted — most of `records/` is advisory by nature
   and will stay so. A record whose enforcement clause names a check that does
   not exist is refused.

4. **Governance prose does not state what a competent reader derives**, and
   mandatory reading is a budgeted figure rather than a habit. What a session
   must read before its first edit is measured and reported, and the budget is
   **700 lines**. That is above today's 626 on purpose: a ceiling that is
   already breached is a ceiling nobody can act on, and one set at today's
   figure forbids the next necessary sentence. It is a ratchet to lower, not a
   target to fill.
   **This record is not restated in any entry point**, which is the clause
   applying to itself: a reader who needs it can reach it, and adding fifteen
   lines to `AGENTS.md` to announce a rule about not adding lines to `AGENTS.md`
   would be the failure it names.

5. **Converting beats adding.** Where an existing clause could become a check,
   that is the work. A new clause added alongside the existing ones needs to
   say why the measured result — twice, in this corpus — does not apply to it.

6. **Enforcement.** `ci/doc_status.py` carries a `reading_load` layer: the
   documents a session must read before a first edit, their line counts, the
   total, and the budget above. `ci/record_review.py` reports, for every record,
   whether its enforcement clause names a mechanism that exists and whether any
   gate declares that it enforces that record. `ci/gate-registry.yaml`'s
   `declared_not_built` count is the register of gaps §1 permits.
   **What none of them can do:** none reads a record for meaning. A record that
   states a requirement in a way no check could ever express passes all three,
   and a universal assertion phrased as a requirement passes §2's check while
   violating its intent. These report structure. A human reads for sense, and
   §2 exists precisely because that reading has to happen somewhere.

## Consequences

- Fewer rules, and the ones that exist are countable. The register of declared
  gaps becomes the honest measure of how much governance is aspirational, which
  is a number this org has never had.
- Records get shorter and duller. A record that cannot assert a universal has
  less to say, and what it says survives longer.
- Cost accepted: a genuine rule with no available mechanism now costs a registry
  entry as well as a clause. That is small and it is the point — the entry is
  what makes the gap visible when somebody later asks what is actually enforced.
- Cost accepted: the 700-line budget will be hit, and the response has to be
  deleting prose rather than raising the number. A budget raised on contact is a
  budget that was never one. Raising it is an amendment to this record, argued in
  the open.
- Existing records are not rewritten on ratification day. §2 applies to what is
  drafted from here; `records/DRAFT-outbound-licensing.md` §12 is a known instance and
  is repaired on its own, not as a sweep.

## Alternatives considered

1. **Require every record to be mechanical before ratification** — rejected. The
   contribution policy, the seams doctrine and the house stack govern judgement,
   and a rule that only counts when a script can check it would delete the half
   of this corpus that is actually load-bearing.
2. **Let records assert facts and correct them when they go stale** — rejected;
   that is the status quo and it produced §12. Nothing notices, because a false
   universal in prose reads exactly like a true one.
3. **Track reading length informally** — rejected. It rose 58 lines in a single
   session that had reducing it as an explicit goal, held by a practitioner who
   had written the goal down that morning.
4. **Cap the number of records instead** — rejected. Record count is not the
   burden; a stranger reads entry points, and thirteen short records they never
   open cost them nothing.

## Revision triggers

- The declared-gap register stops being drained — entries accumulate with
  `check_exists: false` and none becomes `true` over two milestones. The
  registry would then be a place rules go to be forgotten politely.
- The reading budget is hit and the response is to raise it.
- A record is refused under §3 for naming a mechanism that does not exist, and
  the right answer turns out to be that the mechanism was unnecessary.
- Someone outside this org reads the corpus cold and the thing that stops them
  is not prose volume, which would mean this record optimised the wrong number.

## Amendments

*None.*
