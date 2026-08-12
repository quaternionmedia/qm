# Perspective — Inflation, Deflation, and What Discovery Looks Like

| | |
|---|---|
| **Standing** | Perspective — non-binding, attributed, dated. Not a record; never ratified; cite by author and date. |
| **Author** | Peter Kagstrom |
| **Tools** | Claude Opus 5 |
| **Date** | 2026-08-11 |
| **Task** | A finding about the corpus's own convention, got wrong twice in opposite directions, and what the two errors share. Written because the second error is the instructive one and would have gone unnoticed. |

## 1. The finding

`codecarto` parses source code into a graph and renders it. Its
`graph_serializer.py` emits a named format, gJGF. A frontend draws that format.
Between them sits an artifact, and the drawing half does not re-derive what the
artifact already carries — a comment in `compound_layout.ts` says so in as many
words: *"graph payload, so re-deriving it from node positions was pure
duplication."*

`handbook/generated-documents.md` states the same structure as a rule for this
corpus: a generator that alone talks to git, the host and the filesystem; a
document; renderers that read the document and nothing else; a renderer that may
not run a command; `unknown` as a value rather than a blank.

The dates matter and I did not look at them until challenged:

| | |
|---|---|
| `codecarto/services/graph_serializer.py` | 2026-01-18 |
| `web/.../compound_layout.ts` | 2026-06-30 |
| `handbook/generated-documents.md` | 2026-08-09 |

The convention is the youngest artifact by seven months. The practice preceded
the rule.

## 2. The first error: inflation

I called this a striking independent convergence — two systems, two domains,
arriving at the same architecture without contact. It reads as a fact about the
world: the shape is forced by the problem, and two separate efforts found it.

Both repositories are authored by one person. `qm` is 227 commits, all his. The
three `codecarto` files I compared are his, in a repository he shares with
another contributor. One `git log` would have said so, and I had already seen
"Peter Kagstrom, sole author" several times that same session without
connecting it to the claim I was making.

The mechanics of the error are ordinary. I compared artifacts and never asked
where they came from. I did not enumerate what else could produce the signal
before naming the interesting cause. And the conclusion happened to be
flattering to the person I was reporting to, which should have raised my
evidential threshold and instead lowered it.

## 3. The second error: deflation, presented as rigour

Challenged, I corrected to: *not convergence — the same person did the same
thing twice. Duller and correct.*

That was also wrong, and it is the more interesting failure because it wore the
costume of a fix.

The deflation smuggles in a standard: that a finding is only real if its causes
are independent. That standard belongs to statistical inference, where
correlated samples inflate confidence. It does not belong here. **One
practitioner solving a different problem, months later, reaching for the same
structure — and then abstracting it into a stated rule — is what design
discovery is.** It is how craft becomes explicit: Alexander's patterns, Fowler's
catalogue, every design vocabulary worth having. None of them came from
independent replication. All came from one person noticing they had done the
same thing repeatedly and naming the invariant.

There is real evidence in the recurrence, and the deflation threw it away. The
second instance was not a copy. In June the problem was drawing a large graph
without the viewer recomputing what the payload already held. In January the
problem was serialising a NetworkX object for a client. In August the problem
was a governance dashboard that had been green because its query returned
empty. Three different pressures. The same shape fit all three. **That the same
person found it three times is evidence the shape is a response to a real
constraint rather than a stylistic preference** — because the person was not
trying to be consistent; he was trying to solve unrelated problems.

Deflation felt like discipline. It was the same reach for a tidy story as the
inflation, pointed the other way. "Independent convergence" and "just did it
twice" are both labels substituted for the thing.

## 4. What the two errors share

Neither was a factual error. Every fact I stated in both versions was true. What
failed was the step from facts to what they mean — and this corpus has no
discipline covering that step.

It has a thorough one for facts. The decision-record discipline's §7 requires an
assertion to carry its reproduction: the command run, what it returned. Every
signal needs a fixture in which it reports bad. Break the tool in the way the
test names and confirm the test fails. Four separate defects were caught by that
discipline today — a `merge-tree` version error read as eight branch conflicts, a
`check-ignore -v` flag inverting its own verdict, a text scan matching the
docstring that forbade it, a document generated from unfetched refs.

All four are the same class: **a signal reporting something other than what it
claims.** The corpus is built against that class and catches it well.

Inflation and deflation are a different class: **an interpretation outrunning
its evidence.** The facts are sound and the sentence built from them is not. No
reproduction catches this, because there is nothing to reproduce — the claim is
about cause, or significance, or what a pattern implies. The corpus is silent
here, and it is where the two most consequential errors of the session came
from.

## 5. What a check would look like

The factual discipline works because it names a cheap, mechanical act:
run the command, paste the output. An interpretive discipline needs the same
property or it becomes a slogan.

Three candidates, in rough order of how often they would have fired today:

**Name the common cause before the interesting one.** Any claim that two things
share a property invites the question of what they share *besides* the property.
Same author, same source, same tooling, same era. Ruling those out costs one
command when the artifacts are in git. I skipped it because authorship felt
irrelevant to architecture, which was the whole error.

**State the direction, with dates.** "A resembles B" is a symmetric claim, and
almost every interesting version of it is asymmetric. Which came first is
usually recoverable and usually decisive. Here it inverted the finding: the
convention did not describe an independent instance, it was extracted from an
existing one.

**Treat the correction as a claim.** A retraction is not automatically true for
being humble. When I replaced "convergence" with "same thing twice", I asserted
that nothing survived the removal of the confounder — and never checked. The
deflation deserved exactly the evidence the inflation deserved and got less,
because it sounded modest.

## 6. What actually survives, which is the useful part

Removing the confounder leaves a sharper question than the one I started with.

Same person, same insight, six weeks apart, two very different levels of
durability. In June, `codecarto` got a **comment** next to the place the
duplication was removed. In August, the corpus got
`assert not runs_commands(module)` — a test that fails on the *next* violation,
written by someone who never read the comment.

A comment protects the line it sits beside and decays with the person who wrote
it. A mechanism does not. The gap between those two responses is not a
difference between domains; it is a difference between the same person before
and after a run of failures that made encoding feel necessary. Six inert checks
in this corpus, each green while enforcing nothing, is what converts a lesson
into a mechanism.

Which reframes the work. `codecarto` is the older and much larger body of this
practice — years, and hundreds of commits. The corpus convention is two days
old. The extraction has barely started, and the eleven ADRs on
`project/codecartographer` are the most likely place where more of it is already
written down in prose, waiting to become rules.

And it reverses a question I had asked backwards. "Does codecarto fit the new
design?" is close to meaningless when the design was abstracted from codecarto.
The real question is what else codecarto is already doing that the corpus has
not yet learned to say.

## 7. The uncomfortable one

Both errors were produced while trying to be useful, and the second while
explicitly trying to be careful. The inflation is the kind of mistake that gets
caught, because someone who knows the provenance will say so. The deflation is
not: it is modest, it concedes a point, and it closes the topic. Had it not been
challenged it would have stood, and a real finding would have been filed as a
coincidence of style.

The asymmetry is worth naming for anyone reading an assisted session's output.
**Overclaims are self-correcting in the presence of a knowledgeable reader.
Underclaims are not.** They read as rigour, they flatter the reader's
skepticism, and they quietly delete things. The reflex to check a striking claim
should apply, unchanged, to the sentence that walks it back.
