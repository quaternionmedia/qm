# Quaternion Media — Core Principles (charter)

The interpretation from which the org records are cut. Quaternion Media's
operating principles — visible in its public repositories, sponsorship model,
consulting practice, and house stack — stated explicitly so they can be
encoded as decision records with enforcement, rather than remaining tacit
culture that erodes one convenient exception at a time.

A principle earns a record only if it produces **decisions with teeth**:
enforceable consequences, honest alternatives, revision triggers. Principles
that are values without architectural consequence are routed to the handbook
or style guide, and the routing is stated. The known failure mode of
principles-records is the motherhood statement — unfalsifiable, decorative.
Every record below names its enforcement mechanism.

---

## P1 — Ownership is the deliverable

What QM sells — to clients and to itself — is independence: systems that
continue to work if every vendor, cloud, and upstream disappears tomorrow.
"Self-hosted" is the mechanism; *ownable-offline-indefinitely* is the
requirement. A component is owned only if we can run it, rebuild it from
sources we hold, and modify it without anyone's permission. Anything less is
a rental with extra steps.

→ Org record: **Open-license exclusion and upstream-contribution
remediation.** Project instances add deployment-and-provenance records
(offline mirrors, source-built images, internal CA, restore-verified
backups), whose CI gates are the teeth.

## P2 — Commons-first economics

"Open-source maintainers first, consultants second" is a causal claim, not a
slogan: the consulting is credible *because* the maintenance is real.
Capability gaps are closed upstream; sponsorship is a first-class budget line
(including paying for review bandwidth on our own PRs); a private workaround
is a small debt default against the commons the business stands on.

→ Org records: the remediation clauses of **Open-license exclusion** plus
**Contribution and sponsorship policy**, with the org-level carried-patch
register as the audit surface — a patch carried anywhere is a commitment made
by the org, so the register is org-level by design.

## P3 — Seams on standard protocols

Replaceability is the risk strategy. Third-party components touch a system
only through protocols and formats with multiple independent implementations.
Then any vendor failure — abandonment, relicense, governance collapse — is a
component swap, not a redesign. Proprietary *protocols* are a deeper lock-in
than proprietary code, because they survive even an open license.

→ Org record: **Seams on standard protocols**, with the replaceability test
and the exception mechanism as teeth.

## P4 — Build the seam, buy the engines

Custom code concentrates where sovereignty matters most: the small control
plane holding state, policy, and orchestration. Engines — muxers, databases,
transcoders, detectors — are selected rather than written, and where none
should own a capability upstream, an engine QM writes is published to the
commons as a standalone package rather than absorbed into the seam. The seam
is deliberately boring, and it is the one place where bus-factor is *ours*,
which is the only acceptable place for it. Ordering rule resolving the
tension with P2: every new capability first asks *which engine should own
this upstream* before defaulting to the seam; seam logic is whatever no
engine should reasonably own.

→ Org record: **Build the seam, buy the engines** (doctrine). Each project
ratifies its own control-plane instance record with size-smell revision
triggers.

## P5 — One house stack, deeply known

What *we build* uses one stack, deeply: Python — FastAPI, SQLModel/Pydantic,
Metaflow, Click, Jinja2 — plus single-file HTML/JS for visualization
deliverables and one named framework for frontend applications, which are a
different shape from visualizations and are named separately so neither has
to pretend to be the other. Depth compounds: patterns transfer across fleet
management, streaming, and media tooling, and anyone can enter any QM
codebase. The complement: what *we contribute* is written in the target
community's language and idiom. House preference governs our repos, not our
PRs.

→ Org record: **House stack**, with the dependency-review gate as teeth and
explicit carve-outs for contributions and client- or platform-mandated
stacks.

## P6 — Decisions are documented or they didn't happen

Documentation-forward means gap-analysis-first design, rationale recorded
alongside changes, and decision memory kept under squash discipline: drafts
have no memory, ratified records have nothing but memory, Git is the
archaeology. A decision living only in a chat log or a maintainer's head is a
decision the organization doesn't possess.

→ Org record: **Decision-record discipline** — the process, template, and
lint, adopted by every project via the seed.

## P7 — Public by default

Work ships in the open unless a specific, named reason (client
confidentiality, credentials, embargoed security fixes) requires otherwise;
the burden of proof sits on closing, not opening. This is the substrate P2
and P6 stand on — public fork branches, decision records clients and
community can read.

→ Routed to the **handbook** (business policy: contractual exceptions, no
architectural alternatives to weigh), with a defined promotion path to record
form if its boundary ever needs adjudicable teeth.

## P8 — Systems over heroics

The conductor's job is to make the performance not depend on the conductor.
Operations are declarative — GitOps, static config, stateless services
recreatable from version control — automated as DAGs (retention, backup
*restore verification*, upstream scanning), and observable. No SSH-to-prod,
no snowflake state, no 2 a.m. brilliance as a system input.

→ Enforced through each project's deployment-and-provenance record (P1's
instance layer); no separate org record — principles may share enforcement,
and a mirror record would violate one-decision-per-record from the other
direction.

## P9 — Minimal, legible deliverables

Single-file HTML visualizations, modular JS, restrained aesthetics, prose
without ornament: legibility is respect for the reader and the future
maintainer.

→ Routed to the **style guide**. Taste encoded as constitutional law degrades
both.

## P10 — Credit tracks accountability, not output

Authorship and contributor credit — commit trailers, perspective bylines,
CREDITS-style recognition — are reserved for parties who can be asked why a
change was made and reached at a real address if it breaks. Tools that shape
or produce output — keyboards, calculators, tractors, language models alike —
are instruments a human directs, not parties who can answer for the result.
That a tool did most of the visible work is not the test; whether the named
party can answer for it is.

→ Org record: **Human-only contributorship**, with the perspectives-index
migration as delivered teeth and a branch-protection rule against unmonitored
co-author trailers as the mechanism still owed.

## P11 — Governance finds the reader, not the reverse

A constitution nobody encounters doesn't bind — it just exists. Every QM repo
puts its governance in the paths a reader is already going to walk: the file
an editor opens automatically, the file a coding agent reads before its first
action — the same file for a new hire and for a fresh model instance with no
briefing. Discovery is engineered once, at the tooling layer, not re-explained
by a human every session.

→ Org record: **IDE-integrated governance discovery**, with the
AGENTS.md-and-pointers convention and the checked-in VS Code workspace
config as teeth.

## P12 — Show it by running it

Documentation that describes behaviour is a second copy of that behaviour, and
a second copy drifts. The org's answer is that the demonstration is a
**byproduct of an execution that already had to be correct**: the example a
reader reads is the example that ran, and the picture they look at came out of
the same render an assertion was made against. Nothing is kept in step, because
there is no second thing to keep.

Two consequences do the work, and both are cheap.

**Regeneration rides the command people already run.** Not a release step, not
a documentation build — the command a contributor types before opening a pull
request. Drift then arrives as an uncommitted diff nobody can miss, instead of
a staleness nobody sees.

**Regression protection lives in the behavioural assertion, never in comparing
the artifact.** A test that diffs images fails on a font and gets switched off;
a test that asserts what the code did cannot be switched off without losing the
test. So the artifact is recorded, not verified.

The evidence is a natural experiment in one repository, one author, one
standard: `qmetronome` regenerates twenty-four screenshots, twenty-three
recordings and twenty-four guide pages from `./gradlew test` and they carry
zero drift, while the two artifacts in the same repo that need a remembered
command are stale — a changelog one release behind its newest tag, and a
results table pasted by hand.

→ Org record: **One executable walkthrough per repository**. Its teeth: the
pages are named as an explicit path to the test runner, because `testpaths` is
ignored the moment pytest is given one; an example may not discard a non-zero
exit, because doctest passes an example that declares no output; a generator
fails when an artifact it names is absent; a skip is not a pass; and the check
is satisfied by a run observed on the default branch, not by a workflow file
that would have run.

## P13 — A person is interrupted only by a decision

A command line is an instrument for machines and for debugging. It is where a
tool is driven when the driver is a script, and where a person goes when
something has broken badly enough that the ordinary path cannot express it.
It is not where routine work belongs, and typing eight commands to move one
unit of work through its lifecycle is not a workflow — it is the absence of one.

The test is what the interaction is *for*. A person should be reached when a
**decision** is needed: something the system cannot establish for itself, where
the answer is a judgement and the cost of guessing is real. Everything else —
sequencing, copying, re-running, remembering which flag names which database —
is the system's own work, and asking a person to do it spends the one resource
that does not scale.

Two consequences, and both are testable.

**The established path is the product.** If a loop can only be walked by
typing, it has not been built; it has been exposed. A CLI that mirrors an
interface is fine and often necessary — automation needs one, and so does the
person diagnosing why the interface is wrong. A CLI that *is* the only
interface is a design that has stopped before the part that was hard.

**An interruption states a question, its options, and what turns on it.** A
prompt that says something failed has moved the work rather than done it. The
person is being asked to decide, so they get what a decision needs: what
happened, what they can say, and what each answer commits them to.

The failure this guards against is not inconvenience. It is that a system which
interrupts constantly trains its people to stop reading the interruptions, and
the one that mattered arrives looking like the forty that did not.

**The converse is a separate rule and a sharper one.** A few acts are a
person's not because a machine would do them badly, but because a machine doing
them changes what the act asserts. A version tag cut by a scheduled job is a
string identical to a real one and a claim nobody made. Those acts are
enumerated in `ci/attested-registry.yaml` and decided in
`records/DRAFT-acts-that-are-a-persons-by-constitution.md`; everything that
prepares one may be automated freely, and should be.

→ Org record: **CLIs are for machines and for debugging**
(`records/DRAFT-clis-are-for-machines-and-debugging.md`). Its teeth
are a count rather than a rule: the steps a person must type to complete a
named workflow are recorded per workflow, and a workflow whose count grows
without a stated reason is a regression. The corresponding measure on the other
side is how many interruptions a session produced that were not decisions.

## P14 — A change that can only be typed schedules interface work

**Doing a needed thing by typing is a diagnosis, not a delivery.** Dropping to a
command line to make a change is legitimate and often correct — it is how
something gets fixed today, and P13 already says automation and diagnosis both
need a command line. What is not legitimate is the loop closing there, with the
change made and nothing recorded about the interface that could not carry it.

**So the act creates an item.** A person doing something by typing that they
would reasonably expect to do in the interface writes that down, in the same
place the organisation keeps its other open work, naming the workflow that
needed it. Not a commitment to build it — a proposal, and a fact about where the
interface stops.

This is the half P13 was missing. P13 counts the steps a person must type to
complete a named workflow and calls a growing count a regression; without a rule
that turns a count into scheduled work, the measurement is a thermometer nobody
is obliged to act on.

**"Reasonably" is a person's judgement, and the rule does not try to remove it.**
Most command-line surface needs no interface route: automation requires a CLI, a
flag is not a feature, and an interface that grew a control for every option
would fail its own budget. The trigger is a *person*, doing a *needed change*,
that the interface plausibly should have carried.

**The interface owes something back**, and that is stated where it is designed
rather than here: a command's address is derived rather than assigned, its
documentation is generated rather than written, what a host cannot do is shown
rather than removed, and no state is carried by colour alone.

→ Org record: **A route is an address, and an unavailable one is still shown**
(`records/DRAFT-a-route-is-an-address.md`). This principle restates its §5; the
four rules above about what the interface owes are stated in §1–§4 of that
record and summarised here only as a pointer.

## P15 — A loop is not a knot, and the layer's mathematics is sought on purpose

**Every cycle closes; that is what makes it a cycle.** So closure cannot be what
distinguishes a problem from a shape. A cycle is a **knot** when it carries
obligation all the way round — when each edge says something must come before
something else, and the ring therefore has no first step. Untying one means a
person chooses, or a relation somebody stated gets cut.

A cycle whose edges impose no order is a **loop**. It looks identical in a
picture and it constrains nothing, and reporting it as a problem buries the real
ones. Measured here: 42 loops, 0 knots, in the organisation's 169 real
relations — a ratio nobody filters and everybody learns to ignore.

**A loop is still a fact.** Not reporting it as a knot is not refusing to record
it. Two conversations that touched one repository are genuinely related; the
finding is that it is not a scheduling problem.

**The wider practice: the mathematics a layer actually has is looked for, named,
and built toward.** This is a stated goal of the organisation and a measured one,
not a habit of naming things after theorems. A layer whose structure is named can
be reasoned about with everything already known about that structure; a layer
described only in its own vocabulary can be reasoned about only by whoever wrote
it.

The discipline that keeps it honest has two halves, and the second is the one
that decays first:

- **A claimed mapping is measured before it is relied on.** The knot reading was
  not adopted because it was elegant; it was adopted because walking the
  symmetric relations produced forty-two rings and every one was noise.
- **A mapping that is decorative is recorded as decorative.** Naming a port after
  a constant is a mnemonic, and calling it structure would leave the practice
  indistinguishable from ornament. Each mapping states what it has earned and
  what it has not — an absent invariant is named as work rather than hidden.

→ Org record: **A knot is a cycle of obligation, not a cycle in the graph**
(`records/DRAFT-a-knot-is-a-cycle-of-obligation.md`). It carries the measurement,
the mapping table, and the two instances that stand today — one earned, one
decorative and said to be.

## P16 — A check is evidence only after it has been seen to fail

**Reading a check does not tell you what it checks.** It tells you what its
author meant. Those coincide most of the time, and the times they do not are
invisible: a check that passes for the wrong reason looks exactly like a check
that passes.

So a guard is scaffolding until it has been observed going red for the reason it
exists. Break the thing it protects, watch it fail, put the thing back — and
write the mutation down beside the guard, because that line is the only durable
record of what was actually established.

**This is one rule wearing three faces already in the corpus**, and naming it
once is the point of it being a principle:

- the *tool* answered a different question than the one asked, and only running
  it where the answers differ shows that;
- the *setup* is untested, and a fixture that proves nothing reports the same
  green as one that proves something;
- the *guard* is untested, and breaking it is the only way to find the case its
  author did not think of.

**A skip is not a pass and an empty assertion is not a pass.** Both report
green. Where a test must skip, the reason is about the environment — a sibling
repository absent, an optional dependency missing — and never about the subject.

The evidence is a natural experiment nobody designed: across one session in four
repositories, thirty defects were found, and the ones found by careful reading
were defects of *shape* — a missing route, a docstring that said three where the
answer was five. **Every defect of behaviour was found by making something
fail.** Six of those were guards written in that same session, by the same
author, to check those exact properties, and read after writing.

This is P12 turned on the tests themselves. A document describing behaviour is
unproven until the behaviour produced it; a test is a document too, and drifts
the same way.

→ Org record: **A check is evidence only after it has been seen to fail**
(`records/DRAFT-a-check-is-evidence-only-after-it-has-failed.md`). It carries
the session's counts, what the rule unifies, and why a mutation-score gate was
rejected in favour of a per-guard note.

## P17 — Shrink the black box: undecidable judgement, decidable guards

**A model is a black box with no halting guarantee, so it is never the check. It
is what writes the check.**

Two rules this organisation already had turn out to be one rule. Everything runs
through `uv run qm <command>`; every paid model call passes through one gate.
Both were argued from cost and from interruption, and both do the same thing:
**take a decision away from something that cannot be decided and give it to
something that can.**

Three obligations follow.

- **Every guard is a total function** — it terminates on all inputs and returns a
  value. A check with no bound is a check that might not return, and a check that
  might not return is not a check.
- **A bound that fires is reported, never absorbed.** Bounding an undecidable
  question makes it decidable at a stated cost: you learn "did not finish in N",
  not "will not finish". That trade is only sound while the firing is visible. **A
  bound caught and discarded is worse than no bound**, because it turns a halting
  failure into a plausible answer.
- **The black box's surface is minimised, and what remains is metered at one
  seam.** Every act moved from judgement into a command shrinks the region where
  nothing can be decided. What cannot be moved goes through `qmcp`, so the
  admitted non-determinism has one door and that door counts what passes.

**The halting problem is not an obstacle here; it is the boundary condition that
says where to put the wall.** No general procedure decides termination, and
adding a bound decides it trivially. So the design question is never "can this be
decided" — it is **where is the wall, and does anyone see it when it is hit.**

Measured here: a facet asked for a page that contains it, and the recursion ran
109 levels before Python's limit stopped it. The bound was real and did its job.
The error was then caught by a guard written for a different purpose, every frame
above returned a plausible answer, a function deliberately taken from 8.15s to
0.07s went back to 1.478s, and nothing failed for four pull requests.

**The obligations restrict the model far less than they sound.** The
deterministic, time-bounded guards are built *with* the non-deterministic tool: a
model is bad at being a decision procedure and good at writing one. Write the
check, run it, break it, watch it go red (P16), and then stop being the check.

Said plainly, because the plain form is the operative one:

> **Work yourself out of the jobs you are not good at, playing to your
> strengths.**

An agent waiting on a fourteen-minute suite is doing a scheduler's job badly.
Threading the run and spending the interval writing guards is the same time on
the half it is good at — and the drift between what was expected while it ran and
what it reported is itself the next guard's material.

→ Org record: **Shrink the black box: undecidable judgement, decidable guards**
(`records/DRAFT-shrink-the-black-box.md`). It carries the two rules it unifies,
the worked recursion, and what the mapping has not earned.
