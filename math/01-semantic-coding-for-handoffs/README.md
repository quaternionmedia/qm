# Topic 01 — Semantic coding for handoffs

| | |
|---|---|
| **Holes addressed** | "Semantic coding theory for handoffs" (§3); "semantic distortion measures; learned handoff codes" (§9) |
| **Source** | [`perspectives/claude-fable-5-2026-06-09-mathematical-limits.md`](../../perspectives/claude-fable-5-2026-06-09-mathematical-limits.md), §3 and §9 |

## The hole

Two sections of the source document name the same gap from opposite
directions:

- **§3 (redundancy side).** Handoffs are channels; Shannon's noisy-channel
  theorem and rate–distortion theory give exact redundancy–reliability
  trades — *given* an alphabet and a distortion measure. Natural-language
  handoff packets have neither, so "how much redundancy a HANDOFF.md needs
  per unit of context-loss risk" is folklore.
- **§9 (compression side).** Kolmogorov complexity is uncomputable: there's
  no procedure that produces, or certifies, the shortest faithful
  description of tacit knowledge. A handoff packet of ~10³–10⁴ tokens has a
  hard capacity ceiling; whatever's above the line is lost or
  reconstructed-from-priors — which is the drift mechanism of §5.

Both point at the same missing object: a **distortion measure for
meaning**, and a way to spend a fixed token budget against it.

## Demonstrations & experiments

### 1. Handoff-section ablation (the §9 "Quaternion weekend experiment")

**Goal.** Find which sections of a handoff packet actually reduce successor
error, empirically — i.e., treat the handoff schema as a code and measure
its per-symbol value.

**Method.**
- Take a real or constructed multi-session task with a HANDOFF.md broken
  into named sections (e.g. *decisions made*, *open questions*, *rejected
  alternatives*, *key file locations*, *current state*, *next steps*,
  *governing principles*).
- Run the successor session N times, each time with exactly one section
  removed (plus one run with all sections present, as control).
- Score each run against a fixed rubric: task completion, deviation from
  the intended approach, number of clarifying questions asked, alignment
  with corpus principles on judgment calls.

**Output.** A per-section "value of information" ranking — which sections,
removed, cause the largest score drop. This is directly actionable: it's an
evidence-based argument for what HANDOFF.md *must* contain vs. what's
padding.

**Feasibility.** Quaternion weekend. ~7 ablation conditions × 2–3 reps each
is a day of agent runs; scoring is the bulk of the remaining effort.

**Caveat.** Scoring by an LLM judge reintroduces the correlated-reviewer
problem of [topic 03](../03-effective-reviewer-count/) — pair a same-family
judge with at least spot-check human scoring.

---

### 2. Compression-ratio vs. fidelity curve

**Goal.** Get an empirical rate–distortion curve for handoffs, even without
a formal distortion measure — by making the rubric *be* the distortion
measure, explicitly and falsifiably.

**Method.**
- Take one rich session transcript. Produce handoff packets at several
  token budgets (e.g. full transcript, ~4000, ~1000, ~250 tokens) via
  progressive summarization.
- Start successor sessions from each, and measure fidelity: e.g., ask the
  successor to restate the key decisions and rationale, and score
  agreement with the original transcript's actual decisions.
- Plot fidelity vs. packet size.

**Output.** A curve shape. Diminishing-returns (smooth, Shannon-like) vs.
cliff-edge (a token count below which fidelity collapses sharply) are
different findings with different implications — the latter would suggest
a real "capacity" threshold for this corpus's handoff format, not just a
gradual tradeoff.

**Feasibility.** Quaternion weekend for a first curve (4–5 budget points);
a second weekend to repeat on 2–3 different source transcripts to see if
the curve shape is stable across task types.

---

### 3. Reconstruction-from-priors detection

**Goal.** Estimate how much of the corpus's tacit knowledge is *silently*
reconstructed (and thus a drift vector, per §5) vs. explicitly flagged as
missing, when information is absent from the handoff.

**Method.** Reuses experiment 1's ablation runs. For each run where a
section was removed, code the successor's behavior into one of three bins:
(a) asks a clarifying question, (b) proceeds on a plausible-but-wrong
assumption (reconstruction from priors), (c) fails visibly / refuses to
proceed.

**Output.** The relative rate of (b) vs. (a)/(c) is an empirical estimate
of "how often missing context becomes silent drift rather than a visible
gap" — directly relevant to whether §5's drift-detection machinery
(topic 04) needs to worry about handoff gaps as a drift *source*, not just
a drift *symptom*.

**Feasibility.** Quaternion weekend — an extra coding pass over experiment
1's transcripts, no new agent runs required.
