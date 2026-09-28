# QM-XXXX — Repositories at the Same Tag Interoperate, and Either Changing Breaks It

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-08-30 |
| **Pends on** | §3 — which repositories share a coordinate. Everything that vendors one contract surface is the narrow reading; every governed repository is the wide one. The narrow reading is written below because it is the one the evidence supports, and the wide one is a decision nobody has made. |
| **Principle** | `seams-on-standard-protocols` — replaceability is the risk strategy; `decisions-are-documented` — decisions are documented or they didn't happen |
| **Restated in** | Nothing. |

## Context

`records/DRAFT-version-tags-are-claims.md` §5 says what a version number tells
a consumer is *compatibility*, and it says it about one repository. Nothing
says what it means when two repositories carry the same number.

They already do, and the gap has already cost something measurable.

One repository publishes an executable contract — a vector set with a version
of its own. Two others implement it and pin the version they replayed. On
2026-08-30 the publisher governed version `0.6.0`, one consumer vendored
`0.4.0`, and both were green. Neither was lying by its own lights: each
replayed the set it had, and each reported all passing. What no artifact said
was that they had stopped agreeing about the contract, because nothing in the
estate compares one repository's claim against another's.

A second measurement made the shape clearer. The governed set holds 58 cases.
The two consumers replay **disjoint** halves — 11 cell-addressing cases in the
one with no pointer, 47 ring, pointer and timing cases in the one with no cell
input, with no overlap. Each was fully green while covering a fraction, and
"conformant" read the same in both.

So the numbers were describing repositories, and the thing a reader wanted to
know was about the *set*.

## Decision

**A tag number shared by two repositories asserts that those two commits
interoperate. A change to either invalidates it for both.**

### §1 — The number is a coordinate, not a description

Within one repository a version still means what semver says it means, and
`records/DRAFT-version-tags-are-claims.md` continues to govern what a tag
asserts about diligence. This adds one thing across repositories: **equal
numbers assert that these artifacts were proven to work together**, and unequal
numbers assert nothing at all about the pair.

### §2 — Either side changing breaks it, and the break is the point

An interoperability claim is about two artifacts as they were when it was
proven. Change either and the claim covers something that no longer exists.
So a repository whose contract surface moves takes the next coordinate, and a
counterpart that has not re-proven **may not carry that coordinate** — it stays
where it is, and the gap between them is visible rather than assumed.

This is what makes the rule worth having. A number that survived either side
changing would tell a reader that two things fit when nobody had checked.

### §3 — Which repositories share a coordinate

Those that vendor one contract surface. A repository that neither publishes nor
implements the contract is not on the coordinate and is not made stale by it.

The wider reading — that every governed repository advances together — is a
different and much more expensive decision, and it is the `Pends on`. Nothing
here assumes it.

### §4 — What is proven, and by whom

A coordinate is claimed on evidence, and the evidence is that the contract's
own vector set at that version was replayed. Where implementations cover
different parts of the set, the coordinate rests on **all of them together**,
each naming what it executed and what it could not.

That last clause is not bookkeeping. Where two implementations partition the
set, no single one proves the contract, and a tag naming one consumer as its
proof would name a host that had demonstrated part.

### §5 — A repository that cannot re-prove holds the set back

It does not get carried. A coordinate advanced past an implementation that has
not replayed the new set is the drift this record was written from, restated
with a number on it.

## Consequences

**Lockstep has a cost and it is the intended one.** A contract edit now obliges
every implementation to re-prove before the coordinate advances. That is slower
than independent numbering and it is the price of the number meaning something
across a boundary.

**The slowest implementation sets the pace.** A host that cannot re-prove holds
the coordinate for the others. That is a real constraint on a small estate and
it is visible rather than silent, which is the trade.

**Two records in the radial-menu project need amending.** Its release
milestones draft states two version lines that "will not converge", and states
that a tag names *the* consuming project that proves it — singular. Under §4
the proof can take more than one, and under §1 the lines converge. Both are
that project's to amend; this record does not edit them.

**Nothing yet checks any of it.** The mechanism is stated in §4 and built
nowhere, so today this is a rule a person applies. A coordinate that nothing
verifies is exactly the kind of claim this corpus keeps finding.

## Alternatives considered

**Leave repositories independently versioned.** The status quo, and it produced
the measured drift: a publisher at one contract version, a consumer at another,
both green, nothing comparing them. It is the cheapest option and it makes the
number mean nothing across a boundary, which is where readers most want it to
mean something.

**A release train by date.** Rejected for the reason the radial-menu project
already gave when it rejected one: it decouples the version from evidence, and
a coordinate that advances on a calendar asserts interoperability nobody
demonstrated.

**Name one proving consumer per tag.** The existing rule in that project, and
insufficient here on measurement rather than on principle: the two consumers
replay disjoint halves, so any single one named as the proof would have
demonstrated part of the contract while the tag implied the whole.

**Version the contract only, and let implementations track it without tags.**
Coherent, and it gives up the thing being asked for — a reader holding two
repositories wants to know whether these two work together, and a contract
version on one side does not answer that.

## Revision triggers

- An implementation that covers the whole set on its own. §4's "all of them
  together" becomes unnecessary for that contract, and the clause should say so
  rather than being quietly unused.
- The first coordinate advance that an implementation cannot follow. §5 is
  untested, and the pressure to carry it anyway will be highest exactly then.
- `Pends on` answered toward the wide reading, which would make this a rule
  about the estate rather than about a contract surface, and would need its own
  cost stated.
- A second contract surface in the estate, which would mean a repository can sit
  on two coordinates at once — a case this record does not address.

## Amendments

*(none)*
