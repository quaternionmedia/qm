# Topic 02 — Goodhart exponent

| | |
|---|---|
| **Hole addressed** | "'Goodhart exponent': safe optimization budgets" |
| **Source** | [`perspectives/claude-fable-5-2026-06-09-mathematical-limits.md`](../../perspectives/claude-fable-5-2026-06-09-mathematical-limits.md), §2 |

## The hole

The optimizer's curse and extreme value theory together say: selecting the
max of n noisy proxies yields an expected true value shrunk by the
proxy–truth correlation ρ, and the *shape* of that degradation depends on
the tail class of the proxy error (Gumbel-class: graceful; Fréchet-class:
catastrophic — the selected artifact is the one with the single most
extreme error).

What's missing is the function from **(proxy–truth joint distribution,
tail index) → maximum safe selection pressure n***. That number, if it
existed, is what "first-blood ratification" and similar gates are
informally estimating every time a harness decides how hard a proxy can be
leaned on before it needs a human look.

## Demonstrations & experiments

### 1. Simulated optimizer's-curse sweep

**Goal.** Build the reusable simulator that the "Goodhart exponent" concept
needs, and see its qualitative shape under controlled conditions.

**Method.** Pure simulation, no agents:
- Generate synthetic (truth, proxy) pairs under a chosen joint distribution:
  vary the correlation ρ, and vary the proxy-error tail (Gaussian/Gumbel-
  class vs. heavy-tailed, e.g. a t-distribution with varying degrees of
  freedom, for Fréchet-class).
- For each (ρ, tail-class, n), repeatedly simulate "select the max-proxy
  item out of n" and measure E[true value of selected] − E[true value of
  random item] — the realized "Goodhart gain."
- Plot Goodhart gain vs. n for each (ρ, tail-class).

**Output.** For each regime, the n at which the gain curve peaks and turns
negative is exactly "n*" — a numeric instance of the unmachined exponent,
for a *synthetic* distribution. The qualitative question worth answering:
does the heavy-tailed case show a sharp phase transition (gain collapses
suddenly past some n) vs. the light-tailed case's gradual decline?

**Feasibility.** Quaternion weekend — an afternoon of numpy. No real data
needed; this is the cheapest experiment in the whole set and produces a
tool the other experiments below can reuse.

---

### 2. Real proxy/truth pairs from this corpus's own lints

**Goal.** Get a first *real* (ρ, tail behavior) data point to feed into
experiment 1's simulator, instead of an assumed one.

**Method.**
- Pick a harness check that's a known proxy for something semantic — e.g.
  the squash lint's surface pattern check, or an ADR-format lint.
- Assemble a sample of N≈30–50 artifacts: some genuinely good, some
  synthetically perturbed to pass the proxy while being semantically weaker
  (deliberately constructed "near-Goodhart" cases).
- Score each on (a) the proxy (pass/fail or a score) and (b) a human
  judgment of actual quality/faithfulness.
- Estimate the empirical correlation ρ between proxy and truth, and look at
  the cases where proxy passes but truth is poor — is that tail heavy
  (a few catastrophic gamings) or light (mild, evenly-distributed slippage)?

**Output.** A real ρ and a qualitative read on tail weight for at least one
of this corpus's actual proxies — the first concrete input to "what does
the Goodhart exponent look like *here*."

**Feasibility.** Small research project (more than a weekend): assembling
and scoring 30–50 artifacts with human judgment is the bottleneck.

---

### 3. Adversarial-perturbation stress test

**Goal.** A cheap, qualitative probe at "catastrophic Goodhart" — does
gaming a specific check fail gradually or suddenly?

**Method.** Construct 5–10 artifacts designed to satisfy a specific harness
check's surface pattern while being progressively more semantically
unfaithful (increasing "cleverness" of the gaming). Track at what point
proxy-truth correlation visibly breaks — a smooth decline, or a discrete
"this trick defeats the lint entirely" cliff.

**Output.** A small, illustrative answer to "is this check's failure mode
Gumbel-shaped or Fréchet-shaped" — useful as a prioritization signal for
which lints most need a human-in-the-loop backstop.

**Feasibility.** Quaternion weekend, small N — closer to a structured
thought experiment with receipts than a statistical study.
