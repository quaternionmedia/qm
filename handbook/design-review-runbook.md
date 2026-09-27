# Handbook — Reviewing a Repository's Design

**Routing.** Operational procedure, not a decision record: it weighs no
alternatives and creates no constraint a project could violate. It carries out,
for one kind of work, rules other documents own: the evidence clauses of
`records/DRAFT-decision-record-discipline.md` (§7 to §10),
`records/DRAFT-a-check-is-evidence-only-after-it-has-failed.md`,
`records/DRAFT-no-unattended-spending.md`,
`records/DRAFT-few-integers-in-durable-text.md`,
`records/DRAFT-human-only-contributorship.md` and `handbook/async-contract.md`.
Which repository is reviewed next is a handoff's business: the queue in
`handbook/handoffs/README.md` names it.

**Audience.** A person or a session asked to review one repository top down,
with no memory of the run this method came from.

---

## What it is for

A repository gathers weight no single change chose: tests that pass without
discriminating, suites that wait, docs that narrate the sessions that wrote
them, commands nobody runs, code that serves the process of building the thing
rather than its user. Each piece was reasonable when it landed. A design review
finds the sum, fixes what gives wrong answers, removes what does not earn its
place, and says which is which with evidence. It ends in one pull request.

The review hangs on one sentence: **the objective restated as a test the code
can fail.** The first run's was: everything the repository ships either
produces exactly what its model or parameters say, or refuses loudly; code that
serves the process rather than that path stays out of the package. Every cut
and every fix is argued against it. Draft it before the audit; the triage
sharpens it.

It is not the semantic review of the records, which reads meaning; not the
security-review protocol; not an adoption audit
(`handbook/adoption-audit-queue.md`). It consumes their output and does not
redo it.

## Before you start

- **A direct request, carried verbatim.** The owner's charge goes, word for
  word, into every audit and skeptic brief. It sets the bar, and it is what a skeptic tests a cut
  against. Briefs are working files; the charge is never committed.
- **Scripts measure; readers judge.** Phase 0 is scripts. Reading an area for
  what it costs is judgement a script cannot give, and that is the stated
  reason parallel sessions are allowed here at all. They are launched only on
  the owner's direct request, each launch with an audit block: start, predicted
  end, kill time, purpose. One session can run every phase in sequence; only
  the wall clock changes.
- **Every launch states its count first.** How many skeptics and workers run
  depends on what the audit finds, so each phase's count, retries included, is
  shown and confirmed before that phase launches, never reported after it
  (`records/DRAFT-no-unattended-spending.md` §2). Budget the lead's day as
  well as the workers'; the first run's scale is in apothecary #22's body.
- **The four facts** from `AGENTS.md`: the commit and branch, the pull request
  slot, what else is in flight, which gates exist. Start from the tip of work
  already in flight and stack on it, rather than from a `main` it is about to
  leave behind.
- **A never-touch list**: every device, port and service a test or a probe
  could reach, and every server another session holds. It goes into every
  brief. So does what is out of scope: vendored governance, vendored
  third-party code.
- **Scratch lives outside the repository.** Measurements, audits, the triage
  and the briefs are working files. Only the pull request's verification
  section and a retrospective carry anything from them.

An adapter under `adapters/` may carry a reference orchestration for one tool.
None is required, and where one disagrees with this page, this page wins.

## The phases

| Phase | Who | Takes | Produces |
|---|---|---|---|
| 0 Measure | lead | the repository at its base | sizes, profiles, the entry path run, all in files |
| 1 Audit | one reader per area | a common preamble and an area brief | findings with evidence, and a keep list |
| 2 Fix wrong answers | lead, during 1 | the first audits, reproduced | failing-first fixes and a done list |
| 3 Refute deletions | one skeptic per deletion | each deletion finding | upheld with a correction, or refuted |
| 4 Triage | one synthesis | the upheld findings | verdict, objective, target shape, workstreams, not-now, keep |
| 5 Execute | one worker per workstream, in lanes | a brief file | a stacked branch of green commits, and a result |
| 6 Integrate and deliver | lead | the landed branches | one measured tip and one pull request |
| 7 Owner decisions | lead, then workers | the owner's answers | follow-up commits, each reviewed and gated |

### 0 — Measure, once, before anyone audits

- Line counts by area (`git ls-files`, grouped), the largest files, the fan-in
  and fan-out of the biggest modules.
- Wall time per test tier, with a per-test duration profile written to a file.
  Run it in the background and end the file with a sentinel line, so a reader
  can tell a finished profile from one still being written.
- CI's durations and outcomes, read from the host over recent runs.
- Lint, dependency advisories, dead-code candidates and complexity, each tool's
  raw output in a file.
- **The entry path, run.** Follow the README's own first example. Build the
  package from a clean copy and install it into an empty environment. Feed the
  CI gate a suite that errors and read its exit status directly.

Auditors read these files and re-run nothing. One shared profile keeps every
area's numbers comparable and keeps the machine for the work.

A measurement that changes the tree, such as a screenshot rewritten or a
generated file regenerated, is a finding: the suite dirties the tree. Throw the
churn away before cutting the review branch.

*Verify:* every file is non-empty, the profile ends with its sentinel, and each
figure names the commit it was measured at.

### 1 — Audit, one area at a time

Each area gets one reader and a brief: a common preamble, then the files the
area covers and the questions to answer. The preamble gives the repository and
commit; says it is read-only, with scratch outside; says what the repository is
for, from its README and the subsystems grown since; carries the charge; lists
the tools allowed (reading, search, history and blame, one-line interpreters,
dead-code and complexity tools, named test files only); points at the shared
profile; and carries the never-touch list and what is out of scope.

What makes it a review and not a ceremony:

- **No praise, no hedging, no style nits.** Narrative a maintainer does not
  need is weight.
- **Evidence by execution.** A finding carries `file:line` and what is there,
  and where it can, the command that shows it with its output. Where the price
  of a fix is the argument, price it by experiment before anyone changes code.
- **A keep list is compulsory.** Everything genuinely fine goes in it, one line
  each, so the triage leaves it alone. An audit with an empty keep list has not
  looked at what works.
- **Savings rank; they never total.** Readers of different areas count the same
  lines twice.

The finding shape, which every later phase keys on:

| Field | Carries | Used by |
|---|---|---|
| `id` | a short slug, unique in its area | everything after: `area:id` is the join key |
| `title` | one line | the triage |
| `kind` | `delete`, `merge`, `simplify`, `fix-bug`, `speed-up`, `rewrite`, `harden`, `document` | routing: only `delete` goes to a skeptic |
| `severity` | `critical`, `high`, `medium`, `low` | the triage's priority |
| `evidence` | `file:line`, what is there, a command and its output | the skeptic; the worker re-finding code after lines move |
| `impact` | the cost today: wrong answers, seconds, lines, confusion | the commit body's *why* |
| `recommendation` | concrete | the workstream's steps |
| `files` | paths | the triage's file partition |
| `lines_saved`, `seconds_saved` | estimates | ordering only |
| `risk` | what could break | the skeptic's first question; the workstream's risk |

Each reader returns `{area, objective_fit, metrics, verdict, findings, keep}`:
how the area serves the objective in a sentence or two, measured numbers, one
blunt paragraph, the findings and the keep list. *Fitting the areas*, below,
says which areas to run.

### 2 — Fix wrong answers while the audit runs

The lead reads each audit as it lands and reproduces its headline claims by
hand. A wrong answer or a hazard (output that contradicts its input, a gate
that passes on failure, a device left unsafe, a security hole) is fixed at
once, on its own branch, not scheduled: a test seen failing on the base, the
fix, the full suite. The ids fixed go on a **done list** with one paragraph
saying what is done. Skeptics skip those ids and the triage builds on them, so
nothing is scheduled twice.

*Verify:* each fix's test failed on the base. After any dependency change the
slowest suite runs as well; a narrowing that looks safe to the fast tier can
break a path only the slow one exercises.

### 3 — A skeptic for every deletion

Every finding of kind `delete` not on the done list goes to a skeptic whose
brief is to refute it:

- check the evidence at the cited lines;
- search for callers the auditor missed: templates, scripts, tests, docs, the
  command line, string references, entry points, and **other repositories**
  that consume this one;
- ask whether the cut breaks a user path, a CI gate or a governance rule, and
  whether the saving is real.

It returns `{refuted, reason, correction, evidence}`. A finding that is right
but overstated is upheld, with the correction the triage must apply. Skeptics
are cheap because the evidence field tells them where to look.

Send them deletions and nothing else: a broader trigger multiplies the count
without catching more.

### 4 — Triage into workstreams

One synthesis, over the upheld findings with the skeptics' corrections applied,
the refuted list and the done paragraph. It returns:

1. **The verdict**, one blunt paragraph.
2. **The objective**, in two sentences, as a test the code can fail.
3. **The target shape**, in fifteen lines at most: layout, test tiers each with
   a time budget, the doc set with a target size, what CI runs and how long it
   may take.
4. **Workstreams** that can run in parallel without touching the same file.
   Each has an id, a name, a priority (*now*: wrong answers, slow or flaky
   tests, dead weight; *next*; *plan only*), a goal stated as a fact, the files
   it owns, ordered steps that name files, the finding ids it closes, estimated
   lines and seconds, the commands that prove it, and the risk. One sitting
   each; split anything larger.
5. **Not now**: each deferred finding with the reason and what it waits on — a
   person's decision, a ratified record, a bench session with hardware, another
   workstream landing first.
6. **Keep**: the keep lists, consolidated.

Deduplicate across areas. No file is in two workstreams. A refuted finding
never returns. A question for the owner is never a step: where the triage
writes one anyway, the lead decides the interim in the brief and puts the
question on the owner's list.

The lead then writes **one brief file per workstream**, handed to the worker by
path and never pasted into a prompt:

| Field | Carries |
|---|---|
| `id`, `name`, `priority`, `goal`, `files`, `steps`, `checks`, `risk`, `closes` | the triage's |
| `findings` | the full text of every finding it closes, evidence included, so the worker never needs the audit |
| `adjust` | the lead's overrides, which win over the steps: decisions taken, steps already done, lane limits, steps only a person may do, salvage from a dead attempt |

A brief on disk is what lets the lead keep routing: a follow-up found in one
landed branch is appended to the `adjust` of a workstream not yet started.

### 5 — Execute in lanes

- **Lanes are drawn by shared resource, not by topic.** Workstreams that need
  the slow, exclusive suite (a browser, a simulator, a server on a port) share
  one lane, and only that lane runs it or starts servers. The others name any
  such check they need, for the lead. Docs and CI run last, on top of
  everything, because they describe the result.
- **One fresh worktree per workstream**, its branch cut from the previous tip in
  its lane, so a lane never conflicts with itself. A prerequisite from another
  lane is merged in explicitly.
- **The brief first.** `adjust` wins. Line numbers are stale: re-locate by
  content. A step an earlier lane already did, or made moot, is skipped and
  said so. A branch that already exists is checked out and built on, because a
  killed attempt leaves its work there.
- **Commits** are small and each is green. The subject is one sentence saying
  what is now true; the body says why, with evidence. The repository's
  contributorship rule holds: in this estate the owner is the author, no
  co-author trailer, no tool as author, and a `Tools:` line naming the tool
  and the workstream.
- **Owned files only.** A test elsewhere that must follow a behaviour change is
  changed and named in the notes. Format and auto-fix only the files you
  changed, never a directory. Never stage a submodule pin.
- **No narrative.** A comment or docstring you touch that tells history is cut
  to what a maintainer needs. No number a command computes goes into prose;
  name the command.
- **New tests fail on the base first.** Finish green. Skip a step that proves
  wrong, with the reason. If green is out of reach, reset to the base and
  report failed; *partial* means green with steps skipped. Leave the tree
  clean. Do not push.
- **Long commands run in the background**, written to a file and polled. A
  worker that goes silent looks dead to whatever supervises it.

A worker returns `{status: done|partial|failed, branch, head_sha, commits,
done_steps, skipped_steps: [{step, why}], checks: [{command, outcome}],
lines_removed, notes}`. The notes carry cross-file follow-ups, edits outside
the owned files and decisions to confirm.

The supervisor survives a worker dying: one dead worker fails its own
workstream and nothing else. Salvage a failed worktree as a patch and point the
next attempt's `adjust` at it; redo by hand a small workstream that keeps
failing.

### 6 — Integrate, measure after, deliver one pull request

The lead reads each branch as it lands, merges the lanes, and on **every merged
tip** runs the whole ladder before anything stacks on it. The lead's own
commits get the same ladder.

| When | What runs |
|---|---|
| Before (phase 0) | sizes; a per-test profile per tier; CI's duration from the host; the entry path; the package built and installed clean; the gate fed a failure; lint, advisories, dead code |
| Each commit (worker) | the brief's checks; the fast tier; the slow-suite files touched, then the slow suite once, in its lane; each new test seen failing on the base |
| Each merged tip (lead) | every tier; lint; licence compliance and the dependency audit, where they exist; the package installed into an empty environment and exercised; the repository's own run-everything command, its exit status read directly and never through a pipe; no co-author trailer in the branch's history; every commit signed where the repository gates it (`git log --format='%G? %h %s' <base>..<tip>`, no `N`); submodule pins unchanged; generated artifacts regenerated only after rebuilding what they are made from |
| After (final tip) | the before measurements, repeated the same way, and CI's own run on the pull request |

One pull request carries the whole review, from a branch in the repository's
namespace for such work, stacked on the in-flight work the review started
from. Its body, in order:

1. **What this is**: the objective, the areas, the findings and skeptic
   verdicts, the workstreams, and that each landed as its own commits.
2. **The verdict, before this branch**: the worst truths, one line each.
3. **Wrong answers and hazards, fixed**, each with a test that failed first,
   and **needs a bench run** in bold wherever hardware was not exercised.
4. **Cut**: net lines, docs before and after, what went. A retired command stays
   one release as a stub naming its replacement.
5. **Faster**: before and after, per tier and for CI.
6. **Behaviour a user will notice.**
7. **Decisions taken**, dated.
8. **After this merges**: a checklist.
9. **Deferred on purpose**: the not-now headlines, and where they are recorded.
10. **Verification on this tip**: the commands and their results, which every
    figure above comes from.
11. The `Tools:` line.

Where this corpus governs the repository, the body speaks as the contributor,
in the third person, and states decisions rather than questions
(`handbook/async-contract.md` §3). The owner's questions (phase 7) are asked
in the session before it opens, and the body records the answers. Paste the branch report (`uv run qm
branch` here; `check_pr_base.py` run in place in a project). Then confirm that
CI actually ran on the pull request: a stacked base can fall outside a
workflow's branch filter.

### 7 — Owner decisions, then follow-ups

Put what the review cannot settle to the owner as one numbered list in the
session, each item with a recommendation and answerable in a line. Then, per
answer, on the review branch while it is open or on a new one after:

- **A change to code.** Build it in a worktree. Review it through separate
  lenses in parallel: correctness, by running every path; test value, with the
  implementation reverted to the base so each new test must fail, and the fast
  tier timed on both; scope, docs and commits. Deduplicate what the lenses
  report, since they find the same defect separately. Fix, then run a gate that
  fixes nothing: every tier, the behaviour promised, the trailer check, the
  diffstat. Loop fix and gate for a bounded number of rounds. **A fix round that
  fails or returns nothing stops the loop and hands its findings to the lead**;
  gating the unfixed tip reports green over open findings.
- **A governance decision.** Research by execution in a scratch worktree, then a
  draft record in its namespace (a project's records on a branch based on its
  `project/<name>`), rewritten in place under the drafting contract in
  `project-seed/adr/README.md`. The code waits for a person to ratify.
- **Anything else.** A line in the repository's own next-round list, with what
  it waits on.

## Fitting the areas to the repository

Six areas apply everywhere:

- **Architecture, top down**: the objective against the README; the command
  tree; the import graph; god modules; cycles hidden by late imports; global
  state; a target shape.
- **Tests, runtime**: the slowest tests from the shared profile and why, each
  fix priced in seconds; CI's shape and duration.
- **Tests, value**: tests of prose or process rather than behaviour, count pins,
  duplicate coverage, timing assertions, machine-coupled tests; what each kept
  test guards. Where the repository has a mutation or yield instrument, run it
  rather than invent one.
- **Docs**: overlap, finished or stale plans, session diaries, claims the code
  contradicts, the minimal set and its size.
- **Hygiene**: root clutter, runtime against development dependencies, lint
  enforcement, CI workflows, dependency advisories.
- **Dead weight**: dead-code candidates, each confirmed by search across code,
  templates, scripts, tests and docs; modules only their own tests import;
  routes and commands with no caller.

Then add by kind:

| Kind | Areas to add |
|---|---|
| Service, library or CLI | one per subsystem: the server core (route sprawl, error shapes, blocking work in async handlers, caches without invalidation, string-built paths); the CLI and its registry, each command judged against `--help`; any hardware seam (locks, threads, safe states, sleeps that slow tests); research code (on a user path, or exercised only by its own tests) |
| Governance corpus | record coherence, read mechanically; ceremony against enforcement (what stops each rule today: the host, CI, preflight or nothing); tooling correctness (each registry claim against its workflow trigger and its code); tooling scope and weight; routing sprawl (handoffs, plans, perspectives, duplicate pages); generated documents and staleness; seed drift into adopters; branch and pull request hygiene; self-application; the reader's path and its cost |
| Contract publisher | the vectors as the contract; versioning; conformance across implementations; whether the gates are deterministic in practice |
| Web or mobile app | frontend architecture; escaping and injection; state and sync correctness; lifecycle and background work; the release pipeline and signing; asset weight and licensing |
| Game | loop and physics determinism; scene and script coupling; global singletons; test value against runtime; the export pipeline per platform; asset licensing and weight |
| Infrastructure | secrets and state; least privilege and exposure; drift between declared and running; failing pipelines |
| Docs vault | reachability from the navigation; duplicates and second sources of truth; staleness against what is described; the reading cost of the entry path; routing by tier |

A repository that is quiet, has no consumer and has no stated attention gets
**triage only**: one sitting that ends in a keep, archive or adopt proposal for
the owner, not an audit.

## What this page does not authorise

Launching parallel sessions without a direct request, or past a stated count.
Taking a decision that is on the owner's list. Ratifying anything; the code for
a governance decision waits for ratification. Deleting a branch,
force-pushing, or rewriting a branch a submodule pins. Opening anything on the
never-touch list.
