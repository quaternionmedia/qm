# Two fixtures that agreed with nothing

**2026-08-19, night.** The `qmcp`/`dossier` seam. Attributed, dated, binds nothing.

Tools: written with an AI coding assistant, reviewed and committed by a human.

## The shape of it

Two applications, one payload crossing between them. `qmcp dashboard --json`
emits; `dossier harness ingest` reads. Neither imports the other, which is
deliberate and right — what crosses is a schema.

Each side had a test suite. Each suite was green. Each verified the seam against
a fixture **it had written itself**:

- `qmcp` built its test databases with hand-written `CREATE TABLE`, then asserted
  its dashboard could read them.
- `dossier` hand-wrote the payload as a dict, then asserted its reader could
  ingest it.

Neither fixture had ever met the other side. The seam was verified twice, in
opposite directions, against two independent inventions — and the two inventions
were never compared, to each other or to the running code.

## What the fixtures had got wrong

`dossier`'s fixture carried `"status": "FAILURE"`. The harness's enum has held
`PENDING`, `SUCCESS` and `FAILED`, and never `FAILURE`. `qmcp`'s fixture carried
`"ERROR"`, which it has also never held. Both suites were green on statuses the
system cannot produce.

That is the harmless one. It was harmless because the *shape* happened to match,
and the shape happened to match because both authors had read the same model. A
coincidence held the seam together, and nothing would have reported when it
stopped.

## The defect underneath

Running the real emitter into the real reader for the first time took a
scratch database, one script, and about a minute. It showed this:

A harness whose database is missing the tables it reads reported
`invocations: 0, failures: 0`. The reader ingested that and stored it. **A
harness nobody could measure was recorded as a harness with nothing wrong.**

The emitter's `_count` returned `0` for an absent table, with a docstring
defending the choice: not raising, so the dashboard stays available exactly when
it is needed to explain why something is down. That reasoning is correct and was
never the question. Returning zero was the error — zero is an answer.

The reader then made it worse in one line:

```python
return {name: int(totals.get(name, 0) or 0) for name in (...)}
```

A missing total, a null, and an unreadable count all became `0`, and `0` went
into the database as a fact about the harness.

**Both sides had noticed the risk and both had mis-stated the remedy.** qmcp's
test file said in capitals that an empty dashboard and a broken one look
identical unless something distinguishes them, and named the table count as what
distinguishes them. It does not: a database holding two unrelated tables reports
a table count like any other. dossier's walkthrough repeated the claim. The
danger was documented, in two places, with the wrong mitigation — which reads
exactly like a solved problem.

## What replaced the fixtures

`project-seed/harness-payload-vectors.json`, shipped through the governance
submodule, the same way the address grammar's vectors already were. Every
payload in it came out of the real emitter reading a database built from the
real models. Nothing in it is hand-written, so a case that stops being
producible stops being in the file.

Each side now runs the same cases against its own real code: the harness asserts
it can produce them, the control panel asserts it handles them as the contract
says. Neither imports the other. Two implementations, one set of cases — which
is the trade this organisation already made for addresses, arriving late at the
seam that needed it more.

The convention for the defect itself was also already here, in
`harness-status.json`'s own reading block: *unknown is a value, it says why, and
it is not zero, not empty and not compliant.* The seam simply had not adopted
it. It has now, at payload schema 2, and the reader refuses such a payload
rather than storing a fiction.

## Three smaller things the same hour turned up

**A refusal exited zero.** The reader correctly declined to write, printed the
refusal, and returned success to whatever ran it. A scheduled ingest of an
unreadable harness would have been recorded as a clean run — the check reporting
success while enforcing nothing, one layer up from where it was just fixed.

**A doctest that was a sentence about itself.** The harness walkthrough sorted a
tuple of key names written on the page and asserted the sorted result. It
imported the emitter and never called it. It would have passed against any
payload shape whatsoever.

**A skip that had stopped being true.** The harness's address-vector test skipped
when the governance pin predated the vector file, and said so honestly. The pin
had since moved and the test was running — but the docstring still told a reader
the implementation was unverified against the contract. A stale skip notice is
cheaper than a stale pass and it still misinforms.

## The transferable part

The rule this suggests is narrow and I would defend it: **a fixture that stands
in for another system is a claim about that system, and it needs the same
provenance as any other claim.** Hand-authored is fine for a grammar, where the
cases *are* the specification. It is not fine for a payload, where the cases are
an assertion about what a running program emits — and where the cheapest way to
be right is to ask the program.

The second thing is about how this stayed hidden. Neither suite was careless.
Both were thoughtful, both named the exact hazard in their own docstrings, and
both wrote down a mitigation that did not work. **Documented danger reads as
handled danger**, and a suite is at its most convincing precisely where its
author was most worried. What broke the tie was not reading either file again.
It was running the two halves against each other once.
