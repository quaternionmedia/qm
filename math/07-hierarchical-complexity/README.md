# Topic 07 — Hierarchical complexity as a claim-classification engine

| | |
|---|---|
| **Hole addressed** | **Not from the §10 holes table.** This one is structural: the source document's rigor taxonomy classifies a claim's *warrant* (R1/R2/R3) and has no axis for its *depth*. Named here rather than there, because the source document cannot see it from the inside — it is a property of its own harness. |
| **Source** | [`perspectives/claude-fable-5-2026-06-09-mathematical-limits.md`](../../perspectives/claude-fable-5-2026-06-09-mathematical-limits.md), §0 (the taxonomy itself) and the 2026-06-11 addendum (the failure the taxonomy did not catch) |
| **Reference** | [`model-of-hierarchical-complexity.md`](model-of-hierarchical-complexity.md) — what the model defines, what follows, what it does not license. Read §5 before designing anything here. |

## The hole

The source document names its own characteristic failure — *analogy dressed
as theorem* — and builds a harness against it: every claim tagged R1, R2, or
R3. The harness works on warrant. It does not work on depth.

Two claims can carry the same tag and be doing very different amounts of
work. "Handoffs are channels" relates two objects. "Shared weights ≈
pre-coordinated provers, formally breaking the multi-prover lever exactly
where the design-effect formula says it breaks" asserts a property of a
correspondence *between two systems*, and chains it to a second system's
result. Both are R3. Only the second was wrong, and it took a separate
review pass two days later to catch it — by hand, by reading.

The Model of Hierarchical Complexity supplies a candidate second axis. Its
order 13, *metasystematic*, is defined as the operation of comparing systems
and naming properties of the comparison — isomorphic, complete, consistent,
commensurable. That is a precise description of what an R3 structural
mapping is. The candidate throughline:

> An R3 claim is a metasystematic operation. The danger is not the R3 tag;
> it is that metasystematic claims are routinely *written* in the grammar of
> order-11 formal claims, where the reader's warrant expectation is set by
> the grammar rather than the tag.

If that holds, the corpus's worst near-miss to date has a mechanical
signature, and the missing instrument is a two-axis classification —
`(warrant, order)` — rather than a one-axis one.

**The load-bearing uncertainty.** The mapping from MHC to prose claims is
R3 itself, and the model's own formalism makes it fragile: `h` is defined by
structural recursion over a *decomposition*, not over a task, so an order
label is a property of a reading (reference, D2). Whether two annotators
reading the same paragraph assign the same order is not a detail — it is the
precondition for everything else here. Experiment 1 tests exactly that, and
a null result closes this topic rather than refining it.

## Demonstrations & experiments

### 1. Order-annotation reliability on the corpus's own claims

**Goal.** Find out whether MHC order is assignable to prose claims at all,
before building anything on top of it. This is the make-or-break test.

**Method.**
- Take the 11 rows of the source document's §10 summary table plus ~20
  individual tagged claims drawn from its §1–§9, as the annotation set.
- Write a one-page annotation protocol from HC2/HC3: identify the
  subactions the claim composes, decide chain vs. coordination, count.
  Deliberately keep it thin — a thick protocol would smuggle the answer in.
- Have 2–3 annotators independently assign an order to each claim, blind to
  each other and to the R-tag. Use both human and model annotators; the
  same-family correlation question from
  [topic 03](../03-effective-reviewer-count/) applies here directly.
- Compute inter-rater agreement (weighted κ or ICC, since orders are
  ordinal and near-misses matter less than far-misses).

**Output.** An agreement number. High agreement (κ ≳ 0.7) means order is a
usable label for this corpus and experiments 2–3 are worth running. Low
agreement means the reference document's D2 dominates in practice — order is
analyst-relative to the point of uselessness on prose — and this topic
should be closed with that written down, which is itself a result worth
having.

**Feasibility.** Quaternion weekend. ~30 claims × 3 annotators, plus
protocol drafting. The scoring is trivial; the protocol design is the work.

---

### 2. Order as a covariate on the seeded-defect corpus

**Goal.** Test the reference document's D9 in this setting: does reviewer
detection rate fall with the structural depth of the claim containing the
defect, at the rate the power law predicts?

**Method.**
- Reuse [topic 03](../03-effective-reviewer-count/)'s seeded-defect corpus
  rather than building a new one — this experiment is a covariate added to
  that design, not a separate study.
- When seeding defects, stratify by the MHC order of the claim the defect
  sits in (using experiment 1's protocol), spanning at least orders 11–14.
- Record per-defect detection as usual for ρ̄ estimation, then regress
  detection log-odds on claim order.
- Compare the fitted slope to D9's prediction: log-odds linear in order,
  equivalently odds following a power law in primitive-operation count with
  exponent `−c/ln 2`.

**Output.** A slope, with an interval. A significantly negative slope means
deep claims really are harder to review here, and the corpus has an
empirical basis for spending review attention by order rather than by
length. A flat slope falsifies D9 in this domain — a clean negative result
against the one part of the MHC that can lose.

**Feasibility.** Quaternion weekend *if* topic 03's corpus exists; the
marginal cost is stratified seeding plus one regression. Standalone, it
inherits topic 03's cost.

**Caveat.** Claim order and claim length are plausibly collinear (D6:
`h ≤ log₂ L`). The regression needs length as a control or the result is
uninterpretable.

---

### 3. Order/grammar mismatch as a mechanical check

**Goal.** Test whether the throughline above yields a detector: can the
mismatch between a claim's assertion grammar and its warrant tag be flagged
without a human reading for meaning?

**Method.**
- From experiment 1's annotated set, label each claim on two axes: the order
  its *content* operates at, and the order its *grammar* projects — the
  latter cued by surface markers ("formally", "therefore", "breaking",
  "implies", bare equation-chaining across two named results).
- Look for the mismatch class specifically: high content order, low grammar
  order, R3 tag. Check whether the 2026-06-11 addendum's two corrections
  fall in it, and how many other claims do.
- If the class is populated and separable, write the cheapest possible lint
  — a surface-marker grep gated on the R3 tag — and measure its precision
  and recall against the hand annotation.

**Output.** Either a check that earns its place in the harness, or a
measured false-positive rate that says this must stay a human read. Both are
publishable into the corpus. Note that a surface-pattern proxy for a
semantic target is precisely the configuration
[topic 02](../02-goodhart-exponent/) studies — if this lint ships, it is
also a test case for that topic's experiment 2.

**Feasibility.** Quaternion weekend, downstream of experiment 1. Do not
start it before experiment 1 returns.
