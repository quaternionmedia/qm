# QM-XXXX — A Capability Has Four Phases, and Deployment Is the One That Fails Silently

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-08-25 |
| **Pends on** | Nothing — ready for ratification. The evidence rules in §3 are stated per phase and each is a precondition rather than a proof, so a project may adopt the ladder before it can compute every rung. |
| **Principle** | P6 — decisions are documented or they didn't happen; P12 — show it by running it; P16 — a check is evidence only after it has failed |
| **Restated in** | none yet |

## Context

`DRAFT-project-phase-ladder.md` settles what a *project* is working toward. It
leaves untouched a smaller subject that turns out to fail in its own way: a
**capability** — one named thing a system can do, which persists after the
change that introduced it is closed.

A delta is a unit of work and it ends. `qmcp.governed` is not a unit of work; it
is a door that either exists, is reachable, has been used, and is watched — or
is not. `DeltaPhase` cannot hold that, and should not be stretched to: its
ladder runs `brainstorm → complete`, and a capability is at its most dangerous
*after* the delta that built it closed.

**The failure this record exists for was measured rather than imagined.** On
2026-08-25 a local round ran three repositories against each other for the first
time — `perspectives/2026-08-25-defects-between-two-green-suites.md`. Four
defects were found. The shape they shared is not "untested"; every one of them
was tested. It is that **something was designed, and its being reachable was
assumed**:

- `qmcp.topology_view` and `qmcp.orchestration` opened with `uv run qmcp
  topology gallery` and `uv run qmcp orchestration plane`. Six of the ten
  command groups those modules named did not exist. The modules imported, their
  functions worked, their tests passed.
- `MCPClient()` defaulted to a port the server had stopped serving. Both sides
  were tested, each against itself.
- `qmcp.topology_service`'s own opening paragraph records the same shape from
  earlier: *"The contract was tested and the seam was not deployed, and those
  look identical from inside the demo."*

A vocabulary that cannot distinguish *designed* from *reachable* cannot report
any of that, and every view in this organisation lacked one.

## Decision

1. **A capability is in exactly one of four phases, and they are ordered.**

   | phase | the claim | what it does not assert |
   |---|---|---|
   | **design** | it is decided and written down | that anything can reach it |
   | **deployment** | somebody other than its author can reach it by name | that anyone has |
   | **execution** | it has been run against real input, at least once | that anyone is watching |
   | **monitoring** | something reads what it produces, over time | that anyone acts on it |

   The right-hand column is the load-bearing one. Each phase is defined as
   much by what it declines to claim as by what it claims, because every
   silent failure above came from a phase being read as the phase above it.

2. **Deployment is a separate phase because it is the one that fails without a
   symptom.** A capability that is designed and not deployed has passing tests,
   a green suite, and a docstring telling somebody to run a command that does
   not exist. Nothing goes red. This is the whole reason the ladder has four
   rungs rather than three.

3. **The claim and the evidence are separate, and neither may be derived from
   the other** — `DRAFT-project-phase-ladder.md` clause 4, applied unchanged. A
   human states which phase a capability is in. A mechanical check produces
   evidence. A view shows both and shows the gap; nothing rewrites a claim to
   match its evidence, and nothing infers a claim from artifacts.

4. **Evidence disqualifies; it never qualifies** — the same record's clause 6.
   Per phase, the cheapest honest precondition:

   - **design** — a record, or a module docstring, names it. Absent: not yet.
   - **deployment** — its declared entry point resolves. A command named in a
     docstring dispatches; a route named in a docstring answers. This is
     `AGENTS.md`'s *use the declared entry point* rule made checkable, and
     `qmcp`'s `tests/test_declared_commands.py` is one implementation.
   - **execution** — a record exists that it ran: a delta, an invocation row, a
     queue entry. **A test run is not execution.** A test exercises the
     capability against input the author chose, which is the condition every
     defect above survived.
   - **monitoring** — a reading of its output exists at more than one time.
     One reading is execution; a series is monitoring.

   A complete set at any rung means *a human may now assert this*. It never
   means the assertion has been made.

5. **`unknown` is preserved at every rung.** A capability whose evidence could
   not be read is `unknown` — never `design`, and never "not deployed". A thing
   nobody could measure must not render like a thing measured and found
   wanting.

6. **The vocabulary is the organisation's, not an application's.** `dossier`
   and `codecarto` are two windows onto one estate, and a phase named in one
   must mean the same thing in the other. The words and the evidence rules live
   here; a window renders them and adds none of its own. This is the seams
   doctrine applied to a vocabulary rather than to a protocol —
   `DRAFT-seams-on-standard-protocols.md`.

7. **A capability may sit at a rung indefinitely, and that is a report rather
   than a fault.** Most capabilities should never reach `monitoring`; watching
   everything costs attention, which is the scarcest thing here. The ladder
   exists to make the gap visible, not to be climbed.

## Alternatives

**Extend `DeltaPhase` with the four rungs.** Rejected: a delta ends and a
capability does not, so the two ladders measure different subjects. A delta that
closed at `complete` while its capability was never reachable is exactly the
state this record exists to name, and merging the vocabularies would make that
state unsayable.

**Three phases — design, execution, monitoring.** Rejected on the evidence in
the Context: `deployment` is where four of four measured defects sat, and
folding it into either neighbour returns the vocabulary to the one that could
not report them.

**Infer the phase from the evidence and drop the claim.** Rejected, and it is
the tempting one because it needs no human. `DRAFT-project-phase-ladder.md`
clause 6 already settles it: the mechanical set is a precondition. A capability
is not deployed because a command resolves; it is deployed because somebody
established that the people who need it can reach it. The check can only say
*not yet*.

**Let each application define its own ladder.** Rejected per clause 6. Two
windows that disagreed about what `deployed` means would produce two readings of
one estate, and nothing could say which is right — the failure
`DRAFT-a-disagreement-is-a-delta.md` handles for measurements and which is
cheaper to prevent than to reconcile for vocabulary.

## Verification

The four defects in the Context are recorded with their commands and outputs in
`perspectives/2026-08-25-defects-between-two-green-suites.md`, and the fixes in
`quaternionmedia/qmcp#33` and `quaternionmedia/dossier#50`.

**What this record has not earned.** No view computes these rungs yet, so
clause 4's evidence rules are stated and unimplemented. The `deployment` rule is
the exception: `qmcp`'s `tests/test_declared_commands.py` implements it for
commands named in that package, and it was seen to fail — on its first run it
found a seventh broken claim nobody was looking for, and three deliberate
mutations turned it red. The other three rules have been run against nothing.

**And a caution about this record's own evidence.** Its Context rests on one
session's findings in one estate, and three of those four defects were last
touched by the same practitioner who then found them. Recurrence by one
practitioner is evidence, not its absence — but a ladder generalised from four
instances is a ladder that has not yet met a case it fits badly.
