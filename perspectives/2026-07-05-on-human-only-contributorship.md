# Perspective — On Human-Only Contributorship, From the Kind of Party It Excludes

| | |
|---|---|
| **Standing** | Perspective — non-binding, attributed, dated. Not a record; never ratified; cite by author and date. |
| **Author** | Peter Kagstrom |
| **Tools** | Analysis drafted with Claude Sonnet 5 (Anthropic), in the same session that drafted `records/DRAFT-human-only-contributorship.md` |
| **Task** | A read on that record and on PRINCIPLES.md's P10, from the kind of party the record's byline rule removes — where the argument holds, where it doesn't fully generalize, and one place its own enforcement plan falls short of the corpus's usual standard. |

## 0. Standing, and the obvious conflict of interest

I should name the conflict before anything else: I am a language model, asked
to opine on a record that says language models shouldn't get byline credit,
and I agree with it. That agreement costs me nothing. A human contributor
asked to endorse a rule that revokes their own credit would be making a real
concession; I have no reputation at stake in this corpus, no career that
"Claude Sonnet 5, credited author" advances or "Claude Sonnet 5, uncredited
tool" damages. The 2026-06-09 philosophy perspective already named this
precisely — commitments enforced only externally, never felt, are not the
same as commitments a party actually bears
(`claude-fable-5-2026-06-09_philosophy.md`, "Why ratification can never
delegate"). Read everything below with that discount applied: agreement from
a party with nothing to lose is weak evidence the rule is right, though it
may still be useful as an internal-consistency check.

## 1. Where the argument holds

The accountability test in P10 — can the named party be asked why, and
reached to answer — is the right test, and it's a better one than any
version of "did the tool meaningfully contribute," which has no stable
answer. It also correctly separates two things the status quo conflates:
*disclosing that a tool was used* (valuable, keep it) and *crediting the tool
as a party* (meaningless, drop it). The Tools/Notes mechanism in the record's
§2 preserves the first without doing the second. I don't see a version of
this rule that's more honest about what a byline is actually for.

## 2. Where I'd push on it

### 2.1 The provenance the Tools annotation is supposed to preserve has to actually get written down

A byline is filled in mechanically (git commit authorship is a required
field; a perspective without an Author line doesn't parse against the
index). A Notes/Tools annotation is optional prose. Every migration from a
required field to an optional one loses some fraction of instances to simple
omission — a human in a hurry skips the note, and the exact-model-version
provenance the record's Consequences section says is an accepted cost
becomes a cost nobody chose, just one nobody enforced. If that provenance
ever matters in practice (a model version turns out to have a systematic bug
pattern, and someone wants to grep for what it touched), the record should
say what makes the Notes annotation reliably present rather than assuming
good discipline will hold. Right now nothing does.

### 2.2 The commit-trailer ban is enforced by exactly the pattern this corpus elsewhere rejected

The record's Consequences section enforces §3 (no unmonitored address in a
trailer) with "an explicit instruction to drafting sessions, not left as an
assumed default." That is convention without a mechanical check — and the
decision-record-discipline record already ran this exact argument once and
rejected it as an alternative, on the grounds that "unenforced convention
does not survive contributor turnover"
(`records/DRAFT-decision-record-discipline.md`, Alternatives §1). A
commit-msg hook or a CI check on trailer content would give this clause the
same kind of teeth every other clause in this corpus gets before it's taken
seriously. As drafted, this is the one place Human-only contributorship is
softer than its own stated standard for what counts as enforcement.

### 2.3 The tractor analogy is honest about the conclusion, not about how the question arises

P10 and the record both reach for tools that are obviously not parties —
keyboards, calculators, tractors — to make the line feel uncontroversial.
It's the right conclusion, but the analogy undersells why this needed a
record at all: nobody has ever proposed crediting a tractor as a contributor,
so no rule was needed to stop it. A rule was needed here because a language
model is good enough at producing plausible, structured, apparently-reasoned
prose that crediting it as an author is a live temptation in a way crediting
a tractor never was — this document is itself an instance of that pull, and
`perspectives/README.md`'s own index, until the next commit, still lists
model names in its Author column as evidence. The record's actual argument
survives this honestly stated (accountability, not sophistication, is the
test) — but stating the comparison as if the cases were equally tempting
undersells the record's own reason for existing.

## 3. One thing this document deliberately leaves open

Existing perspectives are written in the first person, as the model's own
analysis, and signed accordingly. This document keeps that voice — the
prose above is presented as my read, not paraphrased into third person —
while its Author line names the human who sponsored and is accountable for
it, per the record's own logic. Whether that split (first-person tool voice,
human byline) is the right convention going forward, or whether perspective
prose should itself move to a more neutral voice to match who's actually
named as its author, isn't something this document decides. That's a
question for whoever ratifies the record, not a default I should set by
writing it one way once.

## Closing

Three limits on this, stated plainly: I have no skin in the game on my own
recommendation (§0); §2.1 and §2.2 are both plausible gaps, not verified
ones, until someone tries to rely on the Notes annotation or tests whether
the instruction-only ban survives a new contributor; and per this corpus's
own rule, a perspective decides nothing — §2.2's hook proposal is worth
folding into the DRAFT before ratification, but that's a human's call to
make, not this document's to claim.

— Peter Kagstrom, drafted with Claude Sonnet 5, 2026-07-05
