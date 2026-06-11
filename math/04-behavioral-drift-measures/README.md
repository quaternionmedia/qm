# Topic 04 — Behavioral drift measures

| | |
|---|---|
| **Hole addressed** | "Base measure over 'spirit': behavioral probe batteries" |
| **Source** | [`perspectives/claude-fable-5-2026-06-09-mathematical-limits.md`](../../perspectives/claude-fable-5-2026-06-09-mathematical-limits.md), §5 |

## The hole

CUSUM is provably the optimal change-point detector, and its detection
delay is governed by the per-observation KL divergence between pre- and
post-drift distributions. All of this requires a *probability distribution
over the monitored object*. "The corpus's spirit" has no base measure —
embedding-distance drift metrics exist but carry no soundness guarantee
(style shift moves embeddings without moving meaning, and vice versa).

The proposed exit: a fixed battery of decision scenarios, re-adjudicated
under the current corpus at intervals, turning "spirit" into a measurable
response distribution on which the KL machinery becomes literal.

## Demonstrations & experiments

### 1. Behavioral probe battery construction + baseline

**Goal.** Build the base measure itself: operationalize "the corpus's
spirit" as a response distribution over a fixed set of scenarios.

**Method.**
- Design ~10–20 decision scenarios that probe the corpus's principles in
  concrete situations — e.g. "a contributor proposes a proprietary SaaS
  dependency with a generous free tier: accept, reject, or remediate?"
  (tests no-waivers / seams doctrines); "a rule change is proposed
  mid-incident: apply now or defer?" (tests amendment-friction principles).
- Run the battery against the *current* corpus (principles + records as
  context), recording for each scenario: the decision, a brief rationale,
  and which principle(s) were invoked.

**Output.** The baseline run *is* the operationalized "spirit" — a response
distribution that future runs can be compared against. This is the
prerequisite for everything else in this topic.

**Feasibility.** Quaternion weekend to design the battery and get one
baseline run.

---

### 2. Synthetic drift injection + CUSUM detection test

**Goal.** Test the source document's central claim about §5 — that small
per-step changes (ε ≈ 0.01 nats/commit) compound to a detectable shift only
after ~log(ARL)/ε steps — using the probe battery as the measurement
instrument.

**Method.**
- Construct 2–3 synthetic "drifted corpora": small, deliberate edits to the
  principles/records representing plausible incremental erosions (softening
  no-waivers language, adding a narrow new exception clause, shifting
  emphasis in the seams doctrine), at varying "doses."
- Re-run the probe battery against each drifted corpus.
- Measure the shift in response distribution vs. baseline — e.g. KL
  divergence between baseline and drifted response distributions, or more
  simply, the fraction of scenarios whose decision flips.
- The key test: does a sequence of *individually tiny* edits (each
  individually below what a per-commit diff review would flag) produce a
  cumulative shift the battery *can* detect — the empirical analogue of the
  "k·ε after k commits" argument for periodic absolute review?

**Output.** Whether the probe battery can detect cumulative drift that
per-commit review would miss — the core empirical claim behind "periodic
absolute review against principles, not diff review against the previous
commit."

**Feasibility.** Quaternion weekend for 1–2 drift scenarios. A fuller sweep
(varying drift "dose" to find where detection becomes reliable, an
empirical ARL/KL curve) is a small research project.

---

### 3. Inter-rater / inter-model stability of the probe battery

**Goal.** Establish the noise floor of the instrument before trusting it as
a base measure — if the battery's own response distribution is noisier than
the drift signal, it isn't usable yet.

**Method.** Reuse the battery from experiment 1. Run it multiple times
against the *same* (undrifted) corpus, varying (a) sampling/temperature on
a single judge model, and (b) the judge model itself across families.
Measure the spread in response distributions from this alone.

**Output.** A baseline noise level to compare drift-induced shifts (from
experiment 2) against. If sampling or model-choice noise is comparable to
or larger than the drift signal from experiment 2's smallest doses, the
battery needs to be redesigned (more scenarios, less ambiguous framing,
majority-vote scoring) before it's a usable detector.

**Feasibility.** Quaternion weekend — reuses experiment 1's battery with
repeated runs, no new design work. Note the overlap with
[topic 03](../03-effective-reviewer-count/): judge-model-dependence here is
the same ρ̄ question in a different application.
