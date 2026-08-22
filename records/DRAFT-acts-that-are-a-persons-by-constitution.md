# QM-XXXX — Acts That Are a Person's by Constitution

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-08-20 |
| **Pends on** | Nothing — ready for ratification |
| **Principle** | P10 — credit tracks accountability, not output; P13 — a person is interrupted only by a decision |
| **Restated in** | `PRINCIPLES.md` P13's closing paragraph |

## Context

This corpus has said "a human does this" in six places and never said what the
six have in common.

Ratification is a human gate. The version tag is a human gate. Closing a delta
is a person's. Applying the `main` ruleset is a command an agent must never run.
Answering a question in the human-in-the-loop queue is a person's. Authorising
a paid call is a person's, every time.

Read as a list, those look like a mixture of caution, permissions and taste —
which is how they will be read by somebody arriving with a good automation idea
and no history. They are not a mixture. They are one kind of thing, and the
distinction is sharper than "risky" and more useful.

**Automating them would not make them risky. It would make them not be the act
at all.**

A version tag asserts that a person read the change set, ran it against the real
thing, and saw the checks pass. A tag cut by a scheduled job asserts that a
scheduled job ran. The string in git is identical and the claim is gone. Nothing
was made dangerous; something was made *empty*, and the emptiness is invisible
because the artifact looks the same.

The same is true of the others. A ratification produced by CI is not the
organisation deciding. A delta a detector closes is not work anybody finished. A
data export requested by a script is not the account holder taking a copy of
their own conversations — and this one arrived from outside, as a constraint the
service imposes, which is the useful accident: **a service that will only
respond to the account holder has encoded the same rule this corpus arrived at
independently.**

The failure this prevents is specific. Not an agent doing something unsafe — an
agent doing something *successfully*, producing the right artifact, and the
organisation later reading that artifact as a claim nobody made.

## Decision

**An act is a person's by constitution when performing it automatically would
change what the act asserts. Such acts are named, and nothing automates one.**

1. **The test is what the act asserts, not what it costs or risks.** Ask: if a
   machine did this and produced the identical artifact, would the artifact
   still mean what it means? Where the answer is no, the act is a person's, and
   no amount of care in the automation recovers it.

2. **They are enumerated, not inferred.** `ci/attested-registry.yaml` names each
   one, what it asserts, and what would be lost. A rule of this kind that lives
   only in prose gets rediscovered by argument, and the argument is always with
   somebody who has a good automation idea and no way to see the class.

3. **Convenience around the act is welcome; the act is not.** Everything that
   *prepares* one may be automated freely and should be — assembling the change
   set, running the gates, drafting the annotation, listing what is outstanding,
   telling a person the export has arrived. **What must not be automated is the
   moment the person's judgement enters.** This is the clause that keeps the
   rule from becoming an excuse for manual work.

4. **An attested act records who, and the record is not a byline.** It names the
   party who can be asked why and reached if it breaks — P10's test, applied to
   acts rather than to authorship. `Reviewed-by` on a tag is the worked example.

5. **A tool that performs one on a person's behalf is refused, however
   convincing the interface.** A confirmation prompt that a script can answer is
   not a person; a remembered approval is not a person; a default that is
   accepted by not objecting is not a person. Where a service enforces this
   itself, that enforcement is kept rather than routed around.

6. **An act nobody has performed is outstanding, and is never inferred from
   surrounding evidence.** Every gate green does not ratify a record. A clean
   `main` does not cut a tag. Work being finished does not close a delta. The
   absence is a real state and the views say so — which is why nothing in this
   corpus is ratified today and the documents report exactly that rather than
   rounding it up.

## Consequences

**The six become one rule with six instances**, which is one thing to teach and
one place to argue with rather than six conversations.

**Some automation is refused that would plainly work.** A nightly job that
tagged a green `main` would produce correct-looking tags forever, and every one
would be a claim nobody made. That is the case this record exists to refuse, and
it is refused at its most attractive.

**The registry will be argued with, and that is its job.** An entry somebody
cannot justify against clause 1 should come out. The list being contestable in
one place is the whole point of clause 2.

**A person becomes a bottleneck, deliberately.** Clause 3 is what keeps that
honest: if an attested act is slow, the fix is automating everything up to it,
not moving the line.

**This says nothing about how many acts there should be.** A corpus that
attested everything would be unusable. Clause 1 is a filter, not an
encouragement, and most work fails it — which is correct.

## Alternatives considered

**Leave the six as separate rules.** Rejected: it is the current state, and it
is why an agent reading the corpus can follow every individual rule and still
propose automating the seventh instance nobody wrote down yet.

**Frame it as risk, and gate on blast radius.** Rejected, and it is the tempting
frame. It gets the tag wrong: tagging a green `main` is *low* risk and still
empties the claim. Risk and constitution are different axes, and conflating them
licenses exactly the automation this refuses.

**Frame it as permissions.** Rejected. Permissions describe who *may*, and this
is about what an act *means*. A person with every permission still cannot
delegate a ratification to a script, because the script cannot hold the thing
being asserted.

**Require a person only where a machine cannot do it.** Rejected as backwards.
Machines can do all six. The reason to keep them is what they would stop meaning
— and a rule keyed on capability erodes exactly as capability grows.

## Revision triggers

- An act in the registry that people route around routinely, which means either
  the entry fails clause 1 or the work around it fails clause 3.
- A new instance nobody could classify with clause 1, which would mean the test
  is underspecified.
- Automation that genuinely preserves what an act asserts — a signature scheme
  that carries a person's judgement rather than their credentials would be that,
  and would narrow this record rather than break it.
- The registry growing past what one person can hold in mind, which is the
  signal that clause 1 has stopped filtering.

## Amendments

*(none)*
