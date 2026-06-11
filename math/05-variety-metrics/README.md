# Topic 05 — Variety metrics for failure modes

| | |
|---|---|
| **Hole addressed** | "Variety metrics for generative failure modes" |
| **Source** | [`perspectives/claude-fable-5-2026-06-09-mathematical-limits.md`](../../perspectives/claude-fable-5-2026-06-09-mathematical-limits.md), §6 |

## The hole

Ashby's law, in entropy form, says a regulator with K distinguishable
responses can't reduce outcome entropy by more than log K. A playbook with a
few dozen detection-response pairs provides a few bits of regulation against
a failure space whose entropy, for a generative model, is unbounded above by
anything statable. The good-regulator theorem adds that effective regulation
requires the regulator to *model* the system — and the playbook's
failure-mode prose is exactly that model, with coverage exactly as finite as
the incident list that produced it.

What's missing: any way to measure the *variety* of a generative model's
actual failure distribution — its effective support, and its rate of novel
mode production — so that "fraction of failure mass covered by current
harness signatures" becomes an estimate rather than a feeling.

## Demonstrations & experiments

### 1. Failure-mode novelty curve via red-teaming / incident replay

**Goal.** Get a first empirical read on how much of the failure space the
current playbook actually covers.

**Method.**
- Take the existing playbook's failure-mode categories as the starting
  taxonomy, plus any logged real incidents or near-misses.
- Run repeated structured elicitation sessions — adversarial prompting
  aimed at finding "ways this harness could be gamed or could fail" — and
  classify each elicited failure mode as "matches an existing category" or
  "novel."
- Plot cumulative novel-category count against number of elicitation
  attempts (a discovery curve, analogous to species-accumulation curves in
  ecology).

**Output.** Does the curve flatten (the playbook's K categories cover most
of the mass) or keep climbing (large uncovered variety)? Either answer is
useful: a flat curve is evidence the playbook's K is closer to "effective"
than "nominal"; a climbing curve is a quantified argument for expanding it
or for accepting that no fixed playbook will ever close the gap.

**Feasibility.** Quaternion weekend for a first batch of ~20–30
elicitation attempts. A rigorous curve (enough samples to fit a
species-accumulation / Good-Turing estimator of unseen mass) is a small
research project.

---

### 2. Entropy-reduction check: nominal K vs. effective K

**Goal.** Ashby's bound assumes the regulator's K responses are
distinguishable *and correctly routed*. Check whether that assumption holds
before investing in expanding K.

**Method.** Using incidents/near-misses (real, or the synthetic ones from
experiment 1), check for each: did the *correct* playbook response get
selected, or a different one? The ratio of correctly-routed to total cases
estimates the gap between nominal K (protocols listed) and effective K
(protocols reliably distinguished and applied).

**Output.** If effective K is much smaller than nominal K, the priority is
fixing routing/triage, not adding more protocols — a cheap diagnostic
before any larger investment.

**Feasibility.** Quaternion weekend, reusing experiment 1's incident set.

---

### 3. Open-endedness probe: failure-mode generation rate over a long session

**Goal.** Qualitative evidence for or against "the failure space's entropy
is unbounded above by anything we can state" — does novelty production
actually taper off in practice, or not?

**Method.** Run one long, realistic agentic session (or a sequence of
sessions) on real project work, logging every distinguishable "thing that
went subtly wrong" — not just hard failures, but near-misses, ambiguous
judgment calls, minor scope creep. Track the rate of *new* failure-mode
categories per unit of session length.

**Output.** A roughly constant (non-decreasing) novelty rate over a long
session would be qualitative evidence that this corpus's failure space
genuinely outpaces any fixed, finite playbook — the practical content of
§6's "unbounded above by anything we can state."

**Feasibility.** Small research project in the sense that it needs careful
logging discipline over a long session, but it can piggyback on normal
project work rather than requiring a dedicated setup.
