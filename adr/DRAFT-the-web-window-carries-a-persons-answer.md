# ADR-XXXX — The web window carries a person's answer to a consent request

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-11-24 |
| **Pends on** | How the window knows who is answering. The harness records an answer's `responded_by`, and the window has no account of the person at it: `/auth/github` obtains a token for reading repositories and identifies nobody to the harness. Until that is settled, §4 bounds the window to the one case where the question has an answer without it |

## Context

`qmcp` holds a queue of questions put to a person. An act on an instruction
raises one before it runs anything: the request carries the instruction, the
clone the act would run in, the runtime, and the spend it declares, and the act
waits on the answer. `POST /v1/human/responses` records the answer; the
harness refuses one outside the request's declared options, a second answer to
a request already answered, and an answer to a request that has expired.

Two org records bind what an answer is.
`records/DRAFT-acts-that-are-a-persons-by-constitution.md` names answering a
question in this queue as a person's act: what it asserts is that a person was
asked and said this, and `ci/attested-registry.yaml` carries the entry. Its
clause 3 welcomes everything that prepares the act, carrying the question to
wherever the person is reading among it, and its clause 5 refuses a
confirmation a script can answer, a remembered approval, and a default accepted
by not objecting. `records/DRAFT-no-unattended-spending.md` makes consent to a
paid call consent to a stated amount, for one command.

`codecartographer` is the harness's front end on the web. A person who types an
instruction into the window and starts an act on it is then asked for consent
on the queue. With no way to answer there, the person leaves the window for a
terminal to say yes to what they asked for a moment before, and the window
cannot be the place the harness is run from.

The window stores nothing of the harness's: `tests/test_boundaries.py` holds
the boundary between what it calculates, stores and displays, and its harness
client reaches the harness from the backend rather than from the browser.

## Decision

**The web window shows a pending consent request as the harness holds it, and
relays the answer a person gives there. It answers nothing itself.**

1. **Which requests.** A request an act on an instruction raised: its context
   names the instruction. Every other request on the queue is shown and cannot
   be answered from the window.

2. **What is shown.** The request's prompt, its options, the instruction it is
   for, the clone, the runtime, the declared spend and the expiry, each as the
   harness returned it. The window computes none of them and omits none the
   request carries; a field the request lacks is shown as absent.

3. **What sends an answer.** One act by a person on one request: choosing one
   of the options that request declares. No option is selected in advance.
   Nothing answers on a timer, on page load, or for several requests at once,
   and the window keeps no approval to apply to a later request, whatever the
   project, runtime or amount.

4. **Where it is relayed from.** The backend sends the answer to
   `POST /v1/human/responses`; the browser never calls the harness. The
   relaying route exists only when the backend is bound to a loopback address,
   so the person answering is the person at the machine the harness runs on.
   Bound to any other address, the route is absent and the window says that
   answers are given in a terminal. `responded_by` names the window as the
   surface the answer came through.

5. **The harness decides.** Its acceptance or refusal is shown as given: not
   found, already answered, expired, not one of the options. The window does
   not check an answer before sending it and does not retry one.

6. **Nothing is kept.** The window reads the queue again after an answer and
   draws what the harness returns. An answer lives in the harness's
   `human_responses` row and nowhere in the window.

## Consequences

An instruction can be typed, started and consented to in the window, and its
outcome read there. The terminal front end and the command line stay complete
routes to the same act; the queue has one more place a person can be reading.

The window gains its first route that writes to the harness. The boundary test
grows a case for it: the route forwards and stores nothing. A browser test
answers a request against a stub harness and reads the refusals back, and a
test starts the backend off loopback and finds the route absent.

A request is answerable from two surfaces at once. The harness's refusal of a
second answer is what orders them, and §5 has the window show it.

`responded_by` naming a surface is weaker than naming a person. On a loopback
bind the gap is the one the command line already has, where `--by` is optional.
It is accepted here, and it is what **Pends on** names.

Serving the window to another machine removes answering from it. That cost is
accepted until the window can say who is asking.

`ci/attested-registry.yaml`'s entry for this act names
`qmcp human respond` as its enforcement. The route the window relays to makes
the same refusals in `qmcp`'s server, and the entry's evidence, the
`human_responses` row, is unchanged.

## Alternatives considered

1. **Answers stay in the terminal and the command line.** The smallest
   surface, and the attested act has exactly one shape. It lost because the
   act is defined by who answers, not by where: the org record asks that the
   question be carried to wherever the person is reading, and a window that
   starts an act and cannot receive its consent sends the person elsewhere for
   the half that needs them.

2. **The browser answers the harness directly.** One hop fewer and no route in
   this repository. It lost because the harness serves no cross-origin policy
   and its routes that start processes exist only on a loopback bind; opening
   either for a page is a change to the harness's surface made for one client,
   and the backend already holds the one client every other harness read goes
   through.

3. **An approval the window remembers**, per project or per runtime, so a
   second act of the same kind runs without a question. It lost to
   `records/DRAFT-acts-that-are-a-persons-by-constitution.md` clause 5 and to
   the spending record: consent to a category is not consent to an amount.

4. **Every request on the queue answerable from the window.** The route would
   be the same. It lost because a consent request carries what the person
   needs to answer it, and the person usually raised it; a question an agent
   put on the queue mid-run may need context the window does not draw. Those
   are shown and left to the surfaces that hold that context.

5. **Answerable on any bind, with `responded_by` typed by the person.** It
   lost because a typed name is a claim the window cannot check, and off
   loopback the answerer is anyone who can reach the port.

## Revision triggers

- The question in **Pends on** is settled: §4's loopback bound is read again
  against it.
- The harness gains a route that runs a saved topology. Its consent arrives on
  the same queue, and §1 is read again for whether that request is one of
  these.
- `ci/attested-registry.yaml`'s entry for answering the queue changes what the
  act asserts or what enforces it.
- The harness's response route stops making one of the refusals §5 relies on.
- A request an agent raised mid-run is wanted answerable from the window.

## Amendments

*None.*
