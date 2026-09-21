# Handbook — Document States

**Generated `2026-09-21T01:06:42Z`.** Quotable for 168h. **Do not edit by hand.**

## Where this corpus stands

Working toward **alpha** (`v0.1.0`) — Developers and power users outside QM, onboarded as testers. They read the corpus cold, with none of the session history that built it.

| | Claimed | Measured |
|---|---|---|
| Corpus version | `v0.1.0` is the target | **none.** No `v*` tag, so no release claim — records/DRAFT-version-tags-are-claims.md 4 |
| Records ratified | every requirement below | **0 of 39**; 36 proposed |
| Mandatory reading | under budget | 1165 of 1200 lines |
| Documents whose state is unknown | none | 0 |

**What the milestone requires**, and where each is measured:

- **`ratification-rehearsed`** — At least one record ratified end to end, so the five-step path has been walked once  
  *measured by:* `status/documents.yaml readiness.records.ratified`
- **`reading-within-budget`** — Mandatory reading before a first edit stays under its budget  
  *measured by:* `status/documents.yaml reading_load.within_budget`
- **`no-unknown-document-states`** — Every governed document's state can be established  
  *measured by:* `status/documents.yaml totals.unknown`
- **`gates-declared-are-built`** — No gate is declared and unbuilt, or the gap is deliberate and named  
  *measured by:* `status/gates.yaml totals.declared_not_built`
- **`semantic-review-done`** — All records read in one sitting for contradiction, which no check can do  
  *measured by:* `not mechanisable -- a human says so, in a handoff or a record`

*This layer does not say whether the milestone is met. It puts the claim and the measurements side by side; the judgement is a human's, and one of the five requirements cannot be measured at all.* milestone, target_version and requires are what a human stated in ci/workspace.yaml. Nothing here is derived from the repository.

Every governed document in this corpus: **198**, unfiltered.

| | |
|---|---|
| **Refresh** | `uv run qm docs generate` |
| **Toggle one state** | `uv run qm docs states --state draft` |
| **Regenerate every document** | `uv run qm docs generate` |

## What each state tells you

A state says whether a page binds you. It never says the content is right — Status tracks whether a human has acted.

| | State | Means |
|---|---|---|
| [R] | `ratified` | a human ratified it. This binds every QM project. |
| [P] | `proposed` | drafted and awaiting a human's ratification. Binds nobody yet. |
| [D] | `draft` | pre-ratification. Rewritten in place, binds nobody, and may change entirely. |
| [??] | `unknown` | the state could not be established, which is not the same as fine. |
| [+] | `responded` | concrete work exists because of it. |
| [a] | `acknowledged` | a maintainer has read it. Logged, no further commitment. |
| [x] | `declined` | a maintainer read it and decided not to act, for a stated reason. |
| [-] | `unreviewed` | written, and no maintainer has looked at it. Opinion, never binding. |
| [G] | `generated` | written by a tool. Do not edit by hand; check its age before quoting. |
| [S] | `standing` | policy or charter with no lifecycle defined for its class. |
| [T] | `transient` | working instructions, deleted when the work lands. |

## Counts

| State | Documents |
|---|---|
| [P] `proposed` | 36 |
| [D] `draft` | 3 |
| [-] `unreviewed` | 55 |
| [G] `generated` | 7 |
| [S] `standing` | 74 |
| [T] `transient` | 23 |

## Documents

| | State | Document | Class | Declared |
|---|---|---|---|---|
| [P] | `proposed` | `records/DRAFT-a-capability-has-four-phases.md` | record | Proposed |
| [P] | `proposed` | `records/DRAFT-a-check-is-evidence-only-after-it-has-failed.md` | record | Proposed |
| [P] | `proposed` | `records/DRAFT-a-disagreement-is-a-delta.md` | record | Proposed |
| [P] | `proposed` | `records/DRAFT-a-family-is-bordered-by-what-it-drives.md` | record | Proposed |
| [P] | `proposed` | `records/DRAFT-a-knot-is-a-cycle-of-obligation.md` | record | Proposed |
| [P] | `proposed` | `records/DRAFT-a-principle-is-addressed-by-its-name.md` | record | Proposed |
| [P] | `proposed` | `records/DRAFT-a-route-is-an-address.md` | record | Proposed |
| [P] | `proposed` | `records/DRAFT-a-session-between-people-is-encrypted-end-to-end.md` | record | Proposed |
| [P] | `proposed` | `records/DRAFT-a-shared-tag-asserts-interoperability.md` | record | Proposed |
| [P] | `proposed` | `records/DRAFT-a-stage-is-recorded-and-main-receives-releases.md` | record | Proposed |
| [P] | `proposed` | `records/DRAFT-acts-that-are-a-persons-by-constitution.md` | record | Proposed |
| [P] | `proposed` | `records/DRAFT-attention-is-a-claim-activity-is-measured.md` | record | Proposed |
| [P] | `proposed` | `records/DRAFT-build-the-seam-buy-the-engines.md` | record | Proposed |
| [P] | `proposed` | `records/DRAFT-clis-are-for-machines-and-debugging.md` | record | Proposed |
| [P] | `proposed` | `records/DRAFT-contribution-and-sponsorship-policy.md` | record | Proposed |
| [P] | `proposed` | `records/DRAFT-decision-record-discipline.md` | record | Proposed |
| [P] | `proposed` | `records/DRAFT-deltas-compose.md` | record | Proposed |
| [P] | `proposed` | `records/DRAFT-few-integers-in-durable-text.md` | record | Proposed |
| [P] | `proposed` | `records/DRAFT-governance-arrives-as-a-mechanism.md` | record | Proposed |
| [P] | `proposed` | `records/DRAFT-granularity-is-a-perspective.md` | record | Proposed |
| [P] | `proposed` | `records/DRAFT-house-stack.md` | record | Proposed |
| [P] | `proposed` | `records/DRAFT-human-only-contributorship.md` | record | Proposed |
| [P] | `proposed` | `records/DRAFT-ide-integrated-governance-discovery.md` | record | Proposed |
| [P] | `proposed` | `records/DRAFT-monitoring-seam-and-instance-identity.md` | record | Proposed |
| [P] | `proposed` | `records/DRAFT-no-unattended-spending.md` | record | Proposed |
| [P] | `proposed` | `records/DRAFT-nothing-is-both-a-claim-and-its-own-evidence.md` | record | Proposed |
| [P] | `proposed` | `records/DRAFT-one-executable-walkthrough.md` | record | Proposed |
| [P] | `proposed` | `records/DRAFT-open-license-exclusion-and-upstream-remediation.md` | record | Proposed |
| [P] | `proposed` | `records/DRAFT-outbound-licensing.md` | record | Proposed |
| [P] | `proposed` | `records/DRAFT-project-phase-ladder.md` | record | Proposed |
| [P] | `proposed` | `records/DRAFT-seams-on-standard-protocols.md` | record | Proposed |
| [P] | `proposed` | `records/DRAFT-shrink-the-black-box.md` | record | Proposed |
| [P] | `proposed` | `records/DRAFT-the-ledger.md` | record | Proposed |
| [P] | `proposed` | `records/DRAFT-the-read-document-governs.md` | record | Proposed |
| [P] | `proposed` | `records/DRAFT-version-tags-are-claims.md` | record | Proposed |
| [P] | `proposed` | `records/DRAFT-what-is-not-the-organisation.md` | record | Proposed |
| [D] | `draft` | `records/DRAFT-a-loose-end-is-carried-or-dismissed.md` | record | Draft |
| [D] | `draft` | `records/DRAFT-going-private-is-an-act-with-obligations.md` | record | Draft |
| [D] | `draft` | `records/DRAFT-the-base-is-the-deliverable.md` | record | Draft |
| [-] | `unreviewed` | `perspectives/2026-07-05-on-human-only-contributorship.md` | perspective | — |
| [-] | `unreviewed` | `perspectives/2026-07-21-verify-before-fixing.md` | perspective | — |
| [-] | `unreviewed` | `perspectives/2026-08-07-alfred-brownfield-adoption.md` | perspective | — |
| [-] | `unreviewed` | `perspectives/2026-08-07-verification-discipline-in-assisted-sessions.md` | perspective | — |
| [-] | `unreviewed` | `perspectives/2026-08-08-a-board-is-an-engine-you-sell.md` | perspective | — |
| [-] | `unreviewed` | `perspectives/2026-08-08-hardware-onramp-invisible-artifacts.md` | perspective | — |
| [-] | `unreviewed` | `perspectives/2026-08-08-reading-the-proxy-instead-of-the-thing.md` | perspective | — |
| [-] | `unreviewed` | `perspectives/2026-08-09-adopting-a-corpus-whose-harness-is-unmerged.md` | perspective | — |
| [-] | `unreviewed` | `perspectives/2026-08-09-explanation-in-the-wrong-place.md` | perspective | — |
| [-] | `unreviewed` | `perspectives/2026-08-09-tests-that-enumerate-around-the-defect.md` | perspective | — |
| [-] | `unreviewed` | `perspectives/2026-08-09-the-reviewer-is-the-shared-resource.md` | perspective | — |
| [-] | `unreviewed` | `perspectives/2026-08-11-inflation-deflation-and-what-discovery-looks-like.md` | perspective | — |
| [-] | `unreviewed` | `perspectives/2026-08-11-measuring-your-own-scaffolding.md` | perspective | Unreviewed |
| [-] | `unreviewed` | `perspectives/2026-08-12-nineteen-reversals-and-what-a-clause-cannot-fix.md` | perspective | Unreviewed |
| [-] | `unreviewed` | `perspectives/2026-08-13-the-mechanical-governance-loop.md` | perspective | Unreviewed |
| [-] | `unreviewed` | `perspectives/2026-08-13-thirteen-breaks-and-the-five-that-became-yours.md` | perspective | Unreviewed |
| [-] | `unreviewed` | `perspectives/2026-08-14-before-it-meets-a-stranger.md` | perspective | Unreviewed |
| [-] | `unreviewed` | `perspectives/2026-08-14-one-schema-for-intended-work.md` | perspective | Unreviewed |
| [-] | `unreviewed` | `perspectives/2026-08-14-precedence-lost-to-readership.md` | perspective | Unreviewed |
| [-] | `unreviewed` | `perspectives/2026-08-14-teeth-and-what-the-mutations-said.md` | perspective | Unreviewed |
| [-] | `unreviewed` | `perspectives/2026-08-15-the-exit-code-was-green.md` | perspective | Unreviewed |
| [-] | `unreviewed` | `perspectives/2026-08-15-two-corrections-that-did-not-take.md` | perspective | Unreviewed |
| [-] | `unreviewed` | `perspectives/2026-08-15-what-is-shaping-this-tool.md` | perspective | Unreviewed |
| [-] | `unreviewed` | `perspectives/2026-08-16-the-base-was-the-deliverable.md` | perspective | Unreviewed |
| [-] | `unreviewed` | `perspectives/2026-08-16-the-harness-measured-its-own-cache.md` | perspective | Unreviewed |
| [-] | `unreviewed` | `perspectives/2026-08-16-what-the-checks-were-not-checking.md` | perspective | Unreviewed |
| [-] | `unreviewed` | `perspectives/2026-08-18-a-ring-in-a-terminal.md` | perspective | Unreviewed |
| [-] | `unreviewed` | `perspectives/2026-08-18-the-numbers-were-the-distraction.md` | perspective | — |
| [-] | `unreviewed` | `perspectives/2026-08-19-a-gate-that-never-passed.md` | perspective | — |
| [-] | `unreviewed` | `perspectives/2026-08-19-the-suite-tested-a-model-of-the-system.md` | perspective | — |
| [-] | `unreviewed` | `perspectives/2026-08-19-three-fields-and-none-of-them-is-activity.md` | perspective | — |
| [-] | `unreviewed` | `perspectives/2026-08-19-two-fixtures-that-agreed-with-nothing.md` | perspective | — |
| [-] | `unreviewed` | `perspectives/2026-08-20-eight-commands-and-a-count.md` | perspective | — |
| [-] | `unreviewed` | `perspectives/2026-08-20-the-demo-found-what-the-fix-did-not.md` | perspective | — |
| [-] | `unreviewed` | `perspectives/2026-08-21-a-green-suite-and-eight-holes.md` | perspective | — |
| [-] | `unreviewed` | `perspectives/2026-08-21-what-a-system-says-about-itself.md` | perspective | — |
| [-] | `unreviewed` | `perspectives/2026-08-22-what-it-cost-to-get-one-panel-right.md` | perspective | — |
| [-] | `unreviewed` | `perspectives/2026-08-23-the-rules-with-nothing-behind-them.md` | perspective | — |
| [-] | `unreviewed` | `perspectives/2026-08-25-defects-between-two-green-suites.md` | perspective | — |
| [-] | `unreviewed` | `perspectives/2026-08-25-the-suite-that-outgrew-its-loop.md` | perspective | — |
| [-] | `unreviewed` | `perspectives/2026-08-26-the-plan-was-still-running.md` | perspective | — |
| [-] | `unreviewed` | `perspectives/2026-08-27-the-precondition-nobody-declared.md` | perspective | — |
| [-] | `unreviewed` | `perspectives/2026-08-27-two-views-that-go-stale-together.md` | perspective | — |
| [-] | `unreviewed` | `perspectives/2026-09-20-the-consolidation-cycle.md` | perspective | — |
| [-] | `unreviewed` | `perspectives/2026-09-20-the-families-delineated.md` | perspective | — |
| [-] | `unreviewed` | `perspectives/2026-09-20-the-web-window-first-slice.md` | perspective | — |
| [-] | `unreviewed` | `perspectives/claude-fable-5-2026-06-09-mathematical-limits.md` | perspective | — |
| [-] | `unreviewed` | `perspectives/claude-fable-5-2026-06-09.md` | perspective | — |
| [-] | `unreviewed` | `perspectives/claude-fable-5-2026-06-09_philosophy.md` | perspective | — |
| [-] | `unreviewed` | `perspectives/claude-sonnet-4-6-2026-06-27-mobile-cross-platform-governance.md` | perspective | — |
| [-] | `unreviewed` | `perspectives/claude-sonnet-5-2026-07-04-qmetronome-onramp-retrospective.md` | perspective | — |
| [-] | `unreviewed` | `perspectives/claude-sonnet-5-2026-07-08-mobile-timing-precision-perspective.md` | perspective | — |
| [-] | `unreviewed` | `perspectives/claude-sonnet-5-2026-07-09-first-beat-timing-retrospective.md` | perspective | — |
| [-] | `unreviewed` | `perspectives/claude-sonnet-5-2026-07-18-test-timeout-halting-problem-retrospective.md` | perspective | — |
| [-] | `unreviewed` | `perspectives/session-transcript-2026-06-09.md` | perspective | — |
| [G] | `generated` | `handbook/document-states.md` | generated | — |
| [G] | `generated` | `handbook/gates.md` | generated | — |
| [G] | `generated` | `inventory.json` | generated | — |
| [G] | `generated` | `status/documents.yaml` | generated | — |
| [G] | `generated` | `status/gates.yaml` | generated | — |
| [G] | `generated` | `status/governance.yaml` | generated | — |
| [G] | `generated` | `status/harness.yaml` | generated | — |
| [S] | `standing` | `AGENTS.md` | entry | — |
| [S] | `standing` | `PRINCIPLES.md` | entry | — |
| [S] | `standing` | `README.md` | entry | — |
| [S] | `standing` | `docs/about/architecture.md` | reference | — |
| [S] | `standing` | `docs/about/history.md` | reference | — |
| [S] | `standing` | `docs/about/index.md` | reference | — |
| [S] | `standing` | `docs/about/overview.md` | reference | — |
| [S] | `standing` | `docs/cookbook/add-a-perspective.md` | reference | — |
| [S] | `standing` | `docs/cookbook/build-these-docs.md` | reference | — |
| [S] | `standing` | `docs/cookbook/draft-a-record.md` | reference | Starts at `Draft` or `Proposed` |
| [S] | `standing` | `docs/cookbook/index.md` | reference | — |
| [S] | `standing` | `docs/cookbook/propagate-a-change.md` | reference | — |
| [S] | `standing` | `docs/cookbook/read-status-documents.md` | reference | — |
| [S] | `standing` | `docs/cookbook/run-ci-locally.md` | reference | — |
| [S] | `standing` | `docs/index.md` | reference | — |
| [S] | `standing` | `docs/ref/addresses.md` | reference | — |
| [S] | `standing` | `docs/ref/glossary.md` | reference | — |
| [S] | `standing` | `docs/ref/handbook.md` | reference | — |
| [S] | `standing` | `docs/ref/index.md` | reference | — |
| [S] | `standing` | `docs/ref/namespaces.md` | reference | — |
| [S] | `standing` | `docs/ref/precedence.md` | reference | — |
| [S] | `standing` | `docs/ref/protocols.md` | reference | — |
| [S] | `standing` | `docs/ref/ratification.md` | reference | — |
| [S] | `standing` | `docs/ref/repo-layout.md` | reference | — |
| [S] | `standing` | `docs/usage/first-project.md` | reference | — |
| [S] | `standing` | `docs/usage/getting-started.md` | reference | — |
| [S] | `standing` | `docs/usage/index.md` | reference | — |
| [S] | `standing` | `docs/usage/next-steps.md` | reference | — |
| [S] | `standing` | `docs/usage/questions-a-new-developer-asks.md` | reference | — |
| [S] | `standing` | `handbook/adoption-audit-queue.md` | handbook | — |
| [S] | `standing` | `handbook/async-contract.md` | handbook | — |
| [S] | `standing` | `handbook/config-standard.md` | handbook | — |
| [S] | `standing` | `handbook/consolidation-runbook.md` | handbook | — |
| [S] | `standing` | `handbook/forking-a-project.md` | handbook | — |
| [S] | `standing` | `handbook/generated-documents.md` | handbook | — |
| [S] | `standing` | `handbook/glossary.md` | handbook | — |
| [S] | `standing` | `handbook/governance-rollout.md` | handbook | — |
| [S] | `standing` | `handbook/handoffs/README.md` | index | — |
| [S] | `standing` | `handbook/merge-review.md` | handbook | — |
| [S] | `standing` | `handbook/propagation-runbook.md` | handbook | — |
| [S] | `standing` | `handbook/public-by-default.md` | handbook | — |
| [S] | `standing` | `handbook/style-guide.md` | handbook | — |
| [S] | `standing` | `handbook/test-posture.md` | handbook | — |
| [S] | `standing` | `handbook/what-is-not-the-organisation.md` | handbook | — |
| [S] | `standing` | `perspectives/README.md` | index | — |
| [S] | `standing` | `plans/authorship-first-governance.md` | other | — |
| [S] | `standing` | `plans/data-collection-pathways.md` | other | — |
| [S] | `standing` | `plans/first-ratification.md` | other | — |
| [S] | `standing` | `plans/governance-prose-signals.md` | other | — |
| [S] | `standing` | `plans/hil-testing-session.md` | other | — |
| [S] | `standing` | `plans/moat-remediation.md` | other | — |
| [S] | `standing` | `plans/open-work.md` | other | — |
| [S] | `standing` | `plans/qmpm-standardisations.md` | other | — |
| [S] | `standing` | `plans/readme-onramp.md` | other | — |
| [S] | `standing` | `plans/semantic-review-instrument.md` | other | — |
| [S] | `standing` | `plans/the-active-set-and-the-pair.md` | other | — |
| [S] | `standing` | `plans/the-third-side.md` | other | — |
| [S] | `standing` | `plans/the-web-window.md` | other | — |
| [S] | `standing` | `plans/thread-archive-access.md` | other | — |
| [S] | `standing` | `plans/v0.0.1-blockers.md` | other | — |
| [S] | `standing` | `plans/v0.0.1-review-packet.md` | other | — |
| [S] | `standing` | `protocols/README.md` | index | — |
| [S] | `standing` | `protocols/curriculum.md` | protocol | — |
| [S] | `standing` | `protocols/history-archive.md` | protocol | — |
| [S] | `standing` | `protocols/local-demo.md` | protocol | — |
| [S] | `standing` | `protocols/plain-language.md` | protocol | — |
| [S] | `standing` | `protocols/runs/2026-08-17-local-demo.md` | protocol | — |
| [S] | `standing` | `protocols/runs/2026-08-19-plain-language.md` | protocol | — |
| [S] | `standing` | `protocols/runs/2026-08-21-trio-demo.md` | protocol | — |
| [S] | `standing` | `protocols/runs/2026-08-23-security-review.md` | protocol | — |
| [S] | `standing` | `protocols/runs/2026-08-27-local-demo.md` | protocol | — |
| [S] | `standing` | `protocols/security-review.md` | protocol | — |
| [S] | `standing` | `walkthrough/01-two-views-one-dataset.md` | walkthrough | — |
| [S] | `standing` | `walkthrough/02-rollout-by-family.md` | walkthrough | — |
| [T] | `transient` | `handbook/handoffs/apply-the-main-ruleset.md` | handoff | — |
| [T] | `transient` | `handbook/handoffs/disk-tooling.md` | handoff | — |
| [T] | `transient` | `handbook/handoffs/dossier-delta-review.md` | handoff | — |
| [T] | `transient` | `handbook/handoffs/enact-the-stages.md` | handoff | — |
| [T] | `transient` | `handbook/handoffs/families-delineated.md` | handoff | — |
| [T] | `transient` | `handbook/handoffs/for-a-stronger-model.md` | handoff | — |
| [T] | `transient` | `handbook/handoffs/governance-loop-poc.md` | handoff | — |
| [T] | `transient` | `handbook/handoffs/governance-status-generator.md` | handoff | — |
| [T] | `transient` | `handbook/handoffs/harness-next-test.md` | handoff | — |
| [T] | `transient` | `handbook/handoffs/hil-review-2026-08-25.md` | handoff | — |
| [T] | `transient` | `handbook/handoffs/qmcp-flows-as-deltas.md` | handoff | — |
| [T] | `transient` | `handbook/handoffs/semantic-review-of-the-records.md` | handoff | — |
| [T] | `transient` | `handbook/handoffs/semantic-review-session.md` | handoff | — |
| [T] | `transient` | `handbook/handoffs/session-2026-08-12.md` | handoff | — |
| [T] | `transient` | `handbook/handoffs/session-2026-08-15.md` | handoff | — |
| [T] | `transient` | `handbook/handoffs/session-2026-08-23.md` | handoff | — |
| [T] | `transient` | `handbook/handoffs/six-branches-reached-origin.md` | handoff | — |
| [T] | `transient` | `handbook/handoffs/the-active-four.md` | handoff | — |
| [T] | `transient` | `handbook/handoffs/the-pair-and-the-fresh-setup.md` | handoff | — |
| [T] | `transient` | `handbook/handoffs/the-web-window.md` | handoff | — |
| [T] | `transient` | `handbook/handoffs/two-gate-and-tag-teeth.md` | handoff | — |
| [T] | `transient` | `handbook/handoffs/two-views-one-dataset.md` | handoff | — |
| [T] | `transient` | `handbook/handoffs/views-declare-what-they-need.md` | handoff | — |

## Reading this document

- **Do not** read `ratified` off a filename alone -- the Status row is the claim.
- **Do not** read `proposed` as reviewed: nothing in this corpus has been ratified.
- **Do not** treat `standing` as a state; it is the absence of one for that class.
- **Do not** quote a count without this document's generated_at.

