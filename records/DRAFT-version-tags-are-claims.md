# QM-XXXX — Version Tags Are Claims

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-08-08 |
| **Pends on** | Nothing — ready for ratification |
| **Principle** | P6 — decisions are documented or they didn't happen; P8 — systems over heroics |
| **Restated in** | `AGENTS.md` item 3; `project-seed/ide/AGENTS.md` item 3; `handbook/async-contract.md` §2 |

## Context

Every QM project acquires a version number, and nothing says what one means.
Left unstated, a tag degrades into a synonym for "the current commit" — cut
when someone wants an artifact, asserting whatever the reader assumes.

The corpus already has a working answer for this shape of problem. A record's
Status is not a label; it is a claim a named human made in a commit, and
`Accepted` means something because nothing else can produce it. A version tag
needs the same treatment, and for the same reason: it is the one signal that
leaves the organisation and reaches someone who cannot see how it was made.

Semantic versioning fixes what the *numbers* mean and says nothing about when
a person is entitled to increment them. That second question is the one that
gets answered by habit. This record answers it.

The failure mode is specific. An automated gate that is not deterministic
launders uncertainty into a green check: a suite with a retry, a timing
dependency, or a test that quietly skips when its fixture is absent reports
success in a way that is indistinguishable from having verified something. A
release gated on that is worse than a release gated on nothing, because the
reader has been given a reason to believe.

## Decision

1. **A version tag is a human act, never an automated or assistant one.**
   Assistants prepare releases; a human cuts the tag. This is the same gate as
   ratification and is drawn for the same reason.
2. **A `vMAJOR.MINOR.PATCH` tag asserts three things**, all of which must hold
   at the tagged commit:
   - a human **reviewed** the change set;
   - a human **manually tested** it against its real runtime — the hardware,
     the broker, the device, the deployment, whatever the project's
     deliverable actually meets;
   - its **automated validation passed and is deterministic**.
3. **Only deterministic automated tests count as validation.** A test that
   retries, depends on wall-clock timing or ordering, or skips when a fixture
   is absent contributes nothing to §2's third clause, and neither does a
   suite whose result changes between runs on unchanged input. Such tests may
   exist and may be useful; they are not a gate. **A skipped test is an absent
   test that has announced itself** — which is better than silence, and is
   still not evidence.
4. **Everything untagged carries no release claim.** `main`, a pull request,
   a working branch, and a local build are drafts. They may be perfectly good;
   they assert nothing, and nobody outside the project is entitled to read
   them as a release. A project needing to publish something unasserted uses a
   pre-release identifier (`v0.2.0-rc.1`), which is a tag that says so.
5. **Below `1.0.0`, the numbers promise less, the gate does not change.**
   Semver already lets `0.y.z` break anything at any time. §2's three claims
   hold identically at `v0.0.1` and at `v4.2.0`; what differs is what the
   version tells a consumer about compatibility, not what it tells them about
   diligence.
6. **The tag records its own basis.** Tags are annotated, never lightweight,
   and the annotation names who reviewed, what was manually tested, and what
   the automated gate covered — including what it did not. A tag whose
   annotation cannot state the manual test performed is a tag that should not
   exist yet.
7. **Enforcement.** A tag-protection ruleset restricts who may create `v*`,
   so §1 is mechanical rather than customary. Release automation triggers on
   the tag and never creates one. CI fails a release build whose test run
   reports a skip, a rerun, or a retry, so §3 cannot be satisfied by a suite
   that merely looks green. Changes to this record's claims are amendments.

## Consequences

- A tag becomes worth reading. Someone outside the project can tell what was
  verified, by whom, and what was not — which is the entire value of the
  signal and the thing that erodes first.
- Releases become less frequent and more expensive, deliberately. The manual
  testing clause cannot be satisfied by a build server, and that is the point:
  the deliverables this org ships meet physical hardware, real brokers and
  real deployments, none of which a runner exercises.
- Cost accepted: a project with no deterministic automated tests can still
  tag, and its annotation will say the automated gate covered nothing. That is
  an honest weak release rather than a blocked one — and the annotation is
  where the weakness is visible instead of assumed away.
- A skipped test now costs something rather than reading as a pass, which
  will surface fixtures that were never actually run anywhere.
- Cost accepted: pre-release identifiers add ceremony for projects that
  publish intermediate artifacts. The alternative is untagged builds
  circulating with an implied claim nobody made.

## Alternatives considered

1. **Adopt semver and say nothing further** — rejected: semver defines the
   numbers and is silent on entitlement to increment, which is the half that
   decays. The result is a tag meaning "someone wanted an artifact".
2. **Automate releases entirely from `main`** — rejected: it is the
   industry-standard answer and it deletes the manual-testing clause, which is
   the clause that matters for deliverables meeting hardware. Continuous
   delivery is a fine answer for a system whose runtime a runner can fully
   reproduce; that is not what this org ships.
3. **Require deterministic tests to exist before any tag** — rejected: it
   blocks the first release of every new project, which is when a version is
   most useful for coordination. §6 makes the absence visible instead, which
   achieves the honesty without the deadlock.
4. **Let each project define its own release gate** — rejected: a version
   number is read by people outside the project, so its meaning cannot be
   project-local. Projects may add conditions; they may not remove one.

## Revision triggers

- A tagged release ships a defect that the manual-testing clause should have
  caught — the clause is being satisfied by ritual rather than by testing.
- A project's automated gate is found to include a nondeterministic test that
  was counted as validation.
- A second project asks for a pre-release scheme this record does not
  describe.
- Release volume makes human tagging the bottleneck rather than the
  safeguard — the trade this record makes has stopped paying.

## Amendments

*None.*
