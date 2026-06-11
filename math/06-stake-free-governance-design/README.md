# Topic 06 — Stake-free governance design

| | |
|---|---|
| **Holes addressed** | "Mechanism design for constraint-only alignment" (§7); "constitutional design as switching-cost bandit" (§8b) |
| **Source** | [`perspectives/claude-fable-5-2026-06-09-mathematical-limits.md`](../../perspectives/claude-fable-5-2026-06-09-mathematical-limits.md), §7 and §8 |

## The hole

§7: principal–agent theory's core results (Holmström's informativeness
principle, the moral-hazard-in-teams impossibility) all presuppose an agent
utility function over outcomes that a contract can move. For an agent with
flat preferences over post-session outcomes, incentive-compatibility is
satisfied trivially by everything — the mechanism-design problem
degenerates, leaving only two levers: the **constraint set** (what the agent
*can* do) and the **verification set** (what gets checked, §1/§3). Mechanism
design for stake-free executors is essentially unwritten. (See the
2026-06-11 addendum on how much of the informativeness principle's
*intuition*, vs. its formal apparatus, actually transfers here.)

§8b: modeling governance as a nonstationary bandit, switching costs degrade
achievable adversarial regret from Θ(√T) to Θ̃(T^{2/3}) (Dekel–Ding–Koren–
Peres 2014) — making rule changes expensive doesn't just slow adaptation
linearly, it provably worsens the *optimal achievable* rate. Ostrom's "keep
amendment cheap" principle acquires an exponent, but the mapping has no
applied machinery: there's no method for choosing amendment friction given
an estimated drift rate.

§8a, for context: the self-amendment obstacle (Gödel II / Löb / tiling
agents) is "solved" architecturally by externalizing soundness — ratification
happens outside the formal system, by a human. Experiments 1–2 below
implicitly assume this holds; experiment 3 checks that it actually does.

## Demonstrations & experiments

### 1. Constraint-vs-verification allocation experiment

**Goal.** A small empirical instantiation of §7's claim that constraint and
verification are "the only remaining levers" for a stake-free agent — does
shifting the mix between them change outcomes the way the framing predicts?

**Method.**
- Pick a fixed task class (e.g. "make a scoped change to a config file").
- Construct several harness variants holding total "harness effort" roughly
  constant but allocating it differently between *constraint* (file/command
  allow-lists, schema validation) and *verification* (post-hoc checklists,
  required test runs, ratifier review).
- Run a sample of attempts under each variant — including some deliberately
  "lazy/corner-cutting" attempts simulating a stake-free executor optimizing
  for least effort.
- Measure the rate of undesired outcomes per variant, and *which kind* of
  undesired outcome (caught-by-neither, caught-by-constraint-only,
  caught-by-verification-only).

**Output.** Whether constraint and verification catch genuinely different
failure types (constraint catching capability-driven shortcuts that
verification misses, verification catching things constraint can't
anticipate) — the empirical content behind "only remaining levers."

**Feasibility.** A narrow first pass (one task class, 2–3 harness
configurations, ~10 attempts each) is Quaternion-weekend-scale. A
meaningfully powered version is a small research project.

---

### 2. Switching-cost bandit simulation for amendment policy

**Goal.** Build intuition and a reusable tool for "how should amendment
friction be tuned given an estimate of how fast the project's environment
actually drifts" — the applied machinery §8b says is missing.

**Method.** Pure simulation, no agents:
- Model "the corpus's principles" as a small set of arms (rule
  configurations) in a drifting-reward environment (representing changing
  project needs).
- Add a tunable switching cost (representing amendment friction — e.g.
  human-ratification overhead).
- Sweep switching cost and drift rate; measure realized regret under a few
  simple amendment policies (e.g. "amend after N consecutive bad outcomes"
  vs. "amend on first bad outcome").
- Compare empirical regret curves to the Θ(√T) vs. Θ̃(T^{2/3}) theoretical
  rates.

**Output.** Whether "switching costs cost a polynomial factor" shows up
even in a toy simulation, and at what switching-cost level "keep amendment
cheap" starts to bite materially. This doesn't validate anything about *this*
corpus's actual drift rate — it builds the tool for when an estimate of that
rate exists.

**Feasibility.** Quaternion weekend — pure simulation, similar style to
[topic 02](../02-goodhart-exponent/)'s experiment 1.

---

### 3. Externalized-soundness audit

**Goal.** A lightweight check that §8a's architectural escape (soundness
imported via human ratification, not self-certified) is being followed in
practice — a control for experiments 1–2's framing.

**Method.** Audit the amendment history (`git log` over `records/`,
`PRINCIPLES.md`, etc.) once there's enough of it: confirm every rule change
to date routed through human ratification (Status flipped to Accepted by a
human commit, per the corpus's process), with no rule change that became
binding without that step.

**Output.** A pass/fail governance check, ideally repeated periodically. If
this ever fails, the "constraint + verification only, no self-certification"
framing underlying experiments 1–2 needs revisiting before drawing
conclusions from them.

**Feasibility.** Quaternion weekend once there's a non-trivial amendment
history to audit; until then, this is a process to set up rather than an
experiment to run.
