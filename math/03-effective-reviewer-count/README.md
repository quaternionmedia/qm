# Topic 03 — Effective reviewer count & verification protocols

| | |
|---|---|
| **Holes addressed** | "Measuring inter-model error correlation" (§4); "certificate-carrying semantic artifacts" and "PCP-for-prose; cross-family debate protocols" (§1) |
| **Source** | [`perspectives/claude-fable-5-2026-06-09-mathematical-limits.md`](../../perspectives/claude-fable-5-2026-06-09-mathematical-limits.md), §1 and §4; see also the 2026-06-11 addendum on the §1 MIP/shared-weights step |

## The hole

§4 gives the formula but not the input: n_eff = n / (1 + (n−1)ρ̄) converts a
review *count* into an effective independent count, but ρ̄ — the mean
pairwise error correlation across reviewers on *semantic review tasks* — has
never been measured for this corpus, or for LLMs in general (benchmarks
measure accuracy, not inter-model error correlation).

§1 names two related but distinct gaps: no certificate format exists for
semantic deliverables (so a ratifier checks a search, not a witness), and no
protocol exists for approximating the "non-communicating provers" of MIP
with real models. The 2026-06-11 addendum to the source document narrows
this second point: shared weights plus separate runtime contexts is closer
to the *standard, sound* MIP configuration (shared strategy, no live
channel) than to a violation of it. What's actually untested is whether that
configuration buys anything in practice for prose claims — MIP's soundness
guarantee is for encoded statements, not natural language.

## Demonstrations & experiments

### 1. Seeded-defect corpus / error-correlation matrix (the §4 "Quaternion weekend experiment")

**Goal.** Get a first real ρ̄ for this corpus's review tasks, and compare
it to the illustrative 0.8 used in the source document.

**Method.**
- Build a corpus of N≈10–20 documents (ADR drafts, code-review diffs,
  design docs) with a small number of deliberately seeded defects of known
  types and locations (logical inconsistency, factual error, scope
  violation, missing edge case), plus some clean controls.
- Run the corpus past several reviewer configurations: multiple instances
  of one model (same family, different runs/temperatures), and 2–3
  different model families. Human reviewers as a baseline if available.
- Score each reviewer's defect-detection (hit/miss per seeded defect,
  false positives on clean docs).
- Compute the pairwise error-correlation matrix ρ_ij, separately for
  within-family and cross-family pairs.
- Plug the resulting ρ̄ values into n_eff = n/(1+(n−1)ρ̄) for a few
  candidate review-panel compositions (e.g. "5 runs of one model" vs. "1
  run each of 5 different models") and compare to the source document's
  illustrative numbers (n_eff ≈ 1.19 at ρ̄=0.8 for n=5 same-family).

**Output.** This corpus's actual ρ̄, within- and cross-family — directly
answering "is same-family review really only worth ~1.2 reviewers here, or
is real ρ̄ lower (and review correspondingly more valuable) than the
illustrative figure?"

**Feasibility.** Quaternion weekend for a first pass at N≈10–20 documents
and 3–4 reviewer configurations. A robust ρ̄ estimate (tighter confidence
intervals, more defect types) is a small research project.

---

### 2. Cross-family debate as an approximation to non-communicating provers

**Goal.** Test, empirically, whether "verification power scales with
protocol" holds even qualitatively for *prose* claims — an empirical read on
the "PCP-for-prose" gap, and a direct test of the addendum's narrower claim
about what the MIP analogy can and can't deliver.

**Method.**
- Take a claim that's hard to verify directly but has a knowable ground
  truth — e.g. reuse the seeded-defect corpus from experiment 1 ("is this
  ADR's handoff section sufficient for a successor with no other context?"
  where the true answer is known because the defect was seeded).
- Compare judge accuracy (against the known ground truth) across three
  configurations: (a) a judge model alone; (b) judge + a single same-family
  "advocate" arguing for one side; (c) judge + two different-family
  advocates arguing opposing sides, each seeing only the claim and the
  rebuttals — not each other's full context.
- Hold the judge model's compute/context budget roughly constant across
  configurations.

**Output.** Whether (c) > (b) > (a) in judge accuracy — and by how much —
is the empirical content the source document's R3 mapping gestures at,
without claiming the formal MIP guarantee actually transfers. A null result
(no improvement from debate) would be a meaningful finding too: it would
suggest the "PCP-for-prose" gap isn't just about encoding, but about
whether debate dynamics do anything useful for claims without a checkable
certificate at all.

**Feasibility.** Small research project — needs a held-out claim set with
known ground truth (can reuse experiment 1's corpus) and three model
configurations × N claims, ideally N≥20 for the comparison to mean
anything.

---

### 3. Certificate-carrying artifact pilot

**Goal.** Test §1's "demand artifacts that carry their own certificates"
recommendation directly: does attaching a verifiable witness to a semantic
deliverable actually reduce ratifier error/time, or just relocate the
trust problem to the certificate itself?

**Method.**
- Pick a recurring semantic deliverable in this corpus — e.g. a session
  "squash" / summary.
- Design a certificate format: a structured appendix listing each claim in
  the squash with a pointer to the specific transcript line or diff hunk
  that supports it.
- Build a small sample of squashes (some faithful, some with deliberately
  introduced unfaithful claims) in plain form and in certificate-annotated
  form.
- Compare ratifier accuracy and time on plain vs. annotated versions.

**Output.** Whether certificate annotation measurably helps a human
ratifier catch unfaithful claims faster/more reliably — and, if it doesn't,
whether that's because the certificates themselves need verifying (pushing
the bottleneck rather than removing it).

**Feasibility.** Quaternion weekend for format design + a handful of test
cases (qualitative read). A meaningfully powered comparison (enough
ratifier-trials to detect a time/accuracy difference) is a small research
project.
