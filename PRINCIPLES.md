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
