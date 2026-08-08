# Perspective — Onboarding qmetronome: A Mobile Project's Governance Onramp

| | |
|---|---|
| **Standing** | Perspective — non-binding, attributed, dated. Not a record; never ratified; cite by author and date. |
| **Author** | Peter Kagstrom |
| **Tools** | Claude Sonnet 5 (Anthropic), the assistant that performed qmetronome's governance-adoption pass |
| **Task** | An honest retrospective on adopting this corpus into qmetronome — the org's first mobile/device-hardware project — and concrete guideline proposals for keeping the onramp open to the next non-server project and to outside contributors, not just this one. |

## 0. Standing, scope, and evidence base

This is a single-instance retrospective, not a survey. The evidence is one
adoption pass, on one project, performed in one assistant session, reviewed
by one maintainer. Where a claim generalizes beyond that instance it is
marked as inference, not observation.

Evidence classes, per this corpus's convention:

- **E1** — directly authored or read during this adoption pass (the actual
  ADRs, the CI diff, the constitution text cited below).
- **E4** — inference from a single data point; there is only one adoption to
  compare against so far, so anything claiming a pattern is provisional.
- **E5** — prior general knowledge, unverified this cycle.

The same discount the 2026-06-09 perspective applies to itself applies here
more sharply: I am not just reviewing a corpus I drafted, I am reviewing an
adoption *I performed minutes earlier*, in the same session, for the same
maintainer. Treat §1 with appropriate suspicion of self-congratulation and §2
with appropriate suspicion that I am elevating my own friction into the
corpus's problem. The qmetronome-side companion documents are
`docs/governance-perspective.md` (the two headline gaps, written for that
project's own contributors) and `adr/DRAFT-constitution-adoption-scope.md`
(the full record-by-record disposition) — this document is the QM-side half,
written for whoever next forks the seed onto something that isn't a server.

## 1. What worked (concurrences)

### 1.1 Vendoring as a diffable submodule, not a citation, made honesty checkable (E1)

`adr/README.md`'s "Adopted org records" table pins this corpus at a commit
via a git submodule rather than a written reference. This mattered in
practice, not just in principle: every claim in qmetronome's adoption ADR
about what the corpus does or doesn't require was checked by grepping the
actual vendored text, not a remembered paraphrase from an earlier session.
A citation-only pin would have let a stale summary drift silently; a
submodule pin makes staleness a `git diff` away from visible.

### 1.2 "Name the gap, don't paper over it" survived contact with a real mismatch (E1)

The corpus's own preference for an honest, bounded `Proposed`/`Pends on`
disposition over either silent non-compliance or a strained literal reading
(§ Alternatives considered, `adr/DRAFT-constitution-adoption-scope.md`) is
not a hypothetical design choice — it is what kept qmetronome's adoption
pass from inventing a fictional "deployment" or "image" just to have
something to point SBOM language at. The instruction to name gaps as open
questions rather than resolve them unilaterally (`adr/README.md`'s
"deliberate experiment" section) produced a genuinely better document than
the alternative would have: it is legible where the corpus's server-infra
assumptions run out, rather than quietly stretched to cover a shape they
don't fit.

### 1.3 Human review-before-push caught real defects the process didn't (E1)

Two concrete errors survived every check this session ran (compilation,
120-test suite, the ADR vocabulary lint, my own re-reading) and were only
caught when the maintainer asked to see the full diff before anything was
pushed: a wrong section cross-reference in one ADR, and a checklist item
asserting a UI badge was conditional on state when the code shows it is
unconditional. Neither was a syntax problem or a lint-catchable pattern —
both were confidently written, plausible, and wrong claims about what the
code actually does. This is a small, first-hand data point for a claim this
corpus's own math-side perspective makes abstractly (verification bottlenecks
on semantic checking, not syntactic checking): the mandatory
human-diff-before-push step is doing real work that automated gates in this
corpus's current form do not.

## 2. Friction worth naming (dissent / gaps)

### 2.1 The corpus's defaults are server/infra-shaped, and the first non-server project pays the translation tax alone (E1)

Roughly half of `adr/DRAFT-constitution-adoption-scope.md`'s word count is
not decision content — it is establishing *why* SBOM-per-image,
digest-pinned base images, offline mirrors, and a control-plane/engines
architecture don't have a literal referent for a single sideloaded mobile
app. That translation work is real, necessary under P6, and not something I
resent doing — but it had no template to lean on. The next project that
isn't a self-hosted server (a CLI tool, a browser extension, a static site)
will independently re-derive the same category of argument from scratch,
because nothing upstream of the individual adopting project currently
distinguishes "server/infra project" defaults from an org-general core.

### 2.2 The house-stack carve-out only generalizes by analogy, not by rule (E1)

`records/DRAFT-house-stack.md` (P5) has a client-mandated-stack carve-out.
qmetronome's platform-mandated toolchain (Kotlin/Android Gradle Plugin — no
Python-native equivalent exists) had to be argued as "structurally identical
in kind" to that carve-out (`adr/README.md`'s "deliberate experiment"
section) rather than cited as an instance of an already-general rule. The
argument holds, but it shouldn't have had to be constructed — a
platform-mandated toolchain is exactly as far outside a contributor's
control as a client-mandated one, and the record's own logic already covers
it if the carve-out clause said "client- or platform-mandated" instead of
just "client-mandated."

### 2.3 A perspective fed back has no forcing function on the other end (E4)

`docs/governance-perspective.md` and
`adr/DRAFT-constitution-adoption-scope.md` are explicitly written to feed an
open question back to the org (mobile/device projects as a distinct project
class). Nothing in the process as currently specified guarantees that
question gets looked at — there is no queue, no acknowledgment step, no
"reviewed and deferred" state short of full ratification. For a single
well-resourced project this is a tolerable gap. As an onramp for outside or
occasional contributors, it is a worse one: writing an honest gap analysis
is real work, and a process where that work can sit unacknowledged
indefinitely gives a plausible reason for the next contributor not to
bother writing one, and to quietly special-case around the mismatch instead
— precisely the failure mode P6 exists to prevent.

### 2.4 The license gate degrades to a hand-typed table without container-image tooling (E1)

`records/DRAFT-open-license-exclusion-and-upstream-remediation.md`'s
enforcement mechanism (SBOM-per-image, quarterly scan) has no Gradle/npm/
cargo-dependency-tree equivalent blessed anywhere in this corpus. qmetronome's
adoption ADR discloses this honestly (a manually compiled dependency-license
table, explicitly flagged as "not by a generated SBOM") rather than
overclaiming automated coverage — but the honest disclosure is still a
disclosure of a real gap: the policy is adopted, the teeth are not, and nothing
currently prompts revisiting the table when a new dependency is added. The
CI ADR-lint job that now runs in qmetronome exists only because *that*
project's assistant reactively added it after hitting the violation it
catches once; there was no equivalent off-the-shelf non-container license
tool to reach for.

### 2.5 Adoption cost is currently shaped for "assistant plus engaged maintainer doing a deep dive," not for a drive-by contributor (E4)

Fully onboarding qmetronome onto this corpus took three research passes, a
new project ADR, edits to five docs, and a CI change, in one extended
session. That cost is one-time for the *project*, which is the right unit of
accounting for a binding constitution — but it is also a real signal about
who can currently complete an onramp: a human contributor without an
AI assistant doing the cross-referencing would face a materially harder
version of this same task. That may be an acceptable tradeoff (the
constitution binds project structure, not individual PRs — see
`CONTRIBUTING.md`'s scoped, two-sentence pointer to this material, which
deliberately does not ask a drive-by contributor to read any of it), but it
is worth the org stating on purpose rather than discovering by omission.

## 3. Concrete proposals

None of these are self-executing; each is a candidate `DRAFT-*` change for a
human to pick up, not something this document ratifies.

1. **Generalize the house-stack carve-out** from "client-mandated" to
   "client- or platform-mandated" (§2.2) — a small text change that removes
   the need for the next non-Python project to reconstruct the analogy.
2. **Ship the ADR vocabulary lint in `project-seed` by default**, rather than
   leaving each project to add it reactively after hitting the violation it
   catches (as qmetronome did). It has no server-infra assumption and costs
   nothing to run.
3. **Give perspective documents a defined response state** short of full
   ratification — even "acknowledged, tracked, not yet actioned" as a status
   a maintainer can set, so honest gap analyses have a visible outcome other
   than silence (§2.3).
4. **Publish an org-blessed non-container license-gate pattern** (a
   dependency-manifest-plus-allowlist approach, per package ecosystem) as an
   alternative to the SBOM-per-image mechanism, so open-license enforcement
   doesn't stay a hand-typed table for every project whose runtime isn't a
   container image (§2.4).
5. **Name the "first project of a new class" cost explicitly** in the
   forking procedure (`README.md`'s "Forking a new project" section) — a
   short note that a genuinely novel project shape should expect to spend
   real effort on translation-not-decision work, and that this is expected
   overhead, not a sign the corpus doesn't fit.

## 4. Closing honesty

Three limits on this document. It is not independent review — I performed
the adoption pass it evaluates, in the same session, and a reviewer who
wants to find where I am flattering my own work should start with §1. It is
not a survey — every generalization above rests on a sample size of one
project and should be weighted accordingly; the proposals in §3 are
plausible fixes to a single instance's friction, not validated fixes to a
recurring pattern, until a second non-server project either confirms or
contradicts them. And it is not a request for anything — per this corpus's
own rule, a perspective is the most draft-like thing there is, opinion that
never graduates on its own; if any of §3 is worth acting on, that is a human
decision to pick up as a record, not a status this document can claim for
itself.

— Peter Kagstrom, drafted with Claude Sonnet 5, 2026-07-04
