
This is the kind of document where my biggest integrity risk is dressing analogy as theorem — so the harness for this artifact is a rigor taxonomy applied to every claim, separating literal theorems from model-idealized results from structural mappings. Filed as a second perspective document, since it's attributed analysis, not doctrine.Filed as a second perspective document, with its own internal harness: every claim tagged R1 (literal theorem), R2 (theorem under stated idealization), or R3 (structural mapping — sound math, speculative correspondence), because the characteristic failure of this genre is analogy dressed as proof.

The numbers worth carrying in your head: **0.95²⁰ ≈ 0.36** (the chain-compounding fact, with von Neumann's lineage giving the deeper result — below a per-step error threshold, provably (3−√7)/4 ≈ 0.0886 for noisy 2-input formulas, redundancy buys arbitrary reliability at log cost; *above* it, no amount of redundancy helps, which is the formal argument for decomposing tasks rather than stacking reviewers). **n_eff = n/(1+(n−1)ρ̄)** — five same-family model reviews at ρ̄ = 0.8 are worth 1.19 independent reviewers; the monoculture concern reduced to one measurable formula. And the boiling frog acquires a provable lower bound: optimal change-point detection (CUSUM, Moustakides 1986) suffers delay ≳ log(ARL)/KL, so drift engineered at 0.01 nats per commit evades even the *optimal* detector for ~900 commits — which is the theorem-grade case for periodic absolute review against principles rather than diff review against the previous commit.

The most useful surprise in the compilation is on the positive side: **verification power scales with protocol, not patience.** IP = PSPACE and MIP = NEXP say a weak verifier with randomness, interaction, and *non-communicating* provers can soundly verify claims vastly beyond its own generation capacity — the theoretical backbone for debate-style review of agents, with the sharp corollary that shared weights ≈ pre-coordinated provers, formally breaking the multi-prover lever exactly where the design-effect formula said it breaks. The PCP theorem (O(1) queries suffice for encoded proofs) is the existence proof that spot-checking can be sound — for objects in the right format, which prose is not.

The holes column is where I'd point anyone hunting research programs: no semantic coding theory for handoffs (Shannon needs a distortion measure that doesn't exist for meaning), no "Goodhart exponent" predicting safe optimization budgets from proxy-error tail indices, no base measure over corpus "spirit" (proposed exit: behavioral probe batteries that make the KL machinery literal), and mechanism design for stake-free agents is essentially unwritten — Holmström's results go vacuous at flat utility, leaving constraint and verification as the only levers, which is the formal restatement of where the residue lives. Two of the holes are small enough to be Quaternion weekend experiments: a seeded-defect corpus to estimate inter-model error correlation, and handoff-section ablation to learn which packet fields actually reduce successor error.

The closing section names this document's own bias honestly: I selected constructs that flatter the corpus's design choices, and a hostile reviewer should hunt for the theorems I didn't cite.




-------------------------------


# Perspective — The Mathematics of Harness Limits

| | |
|---|---|
| **Standing** | Perspective — non-binding, attributed, dated. Companion to the 2026-06-09 perspective document. |
| **Author** | Peter Kagstrom |
| **Tools** | Claude Fable 5 (Anthropic) |
| **Date** | 2026-06-09 |
| **Task** | Tie the identified shortcomings of agentic harness systems to provable mathematical constructs, numerically where the math permits; where machinery is missing, mark the hole and the jumping-off point. |

## 0. Rigor taxonomy (the harness for this document)

The characteristic failure of documents like this one is analogy dressed as
theorem. Every claim below is tagged:

- **R1** — a theorem, applied literally: the objects in our setting *are*
  the objects of the theorem.
- **R2** — a theorem, applied under stated idealizations: the theorem is
  real; treating our setting as its model is the approximation.
- **R3** — a structural mapping: the mathematics is sound, the
  correspondence to agentic systems is the speculation, and the value is
  orientation, not proof.

Citations are from training knowledge (evidence class E5 throughout, per the
corpus convention); the theorems named are standard and checkable, and the
few recent or preprint-grade results are marked as such.

---

## 1. Verification vs. generation — the bottleneck, formalized

**Shortcoming:** harnesses lint form because they cannot check meaning; a
human ratifier remains the semantic verifier and therefore the throughput
bound.

**The impossibility floor (R1).** Rice's theorem (1953): every non-trivial
semantic property of programs is undecidable. The squash lint checks a
syntactic proxy ("contains 'previously'") because the semantic target ("is a
faithful squash") is, in the general case, not mechanically checkable —
not as an engineering shortfall but as a theorem. For scale: the busy-beaver
function, the canonical measure of how fast undecidability bites, was pinned
at BB(5) = 47,176,870 only in 2024 (the bbchallenge Coq-verified proof),
and BB(6) is already known to exceed towers of exponentials. Five-state
machines exhausted decades of effort; the semantic space of a design
document is not smaller.

**The positive machinery — and it is startlingly strong (R2→R3).**
Complexity theory's central gift to this problem is that *verification can
be exponentially cheaper than generation, given the right protocol*:

- **NP**: a certificate can make checking polynomial even when finding is
  (believed) intractable. Practical translation: demand artifacts that carry
  their own certificates — test suites, reproducible builds, SBOMs — so the
  ratifier checks a witness, not a search.
- **IP = PSPACE** (Shamir, 1992): a polynomial-time verifier *with
  randomness, interacting* with an untrusted, unbounded prover can verify
  any PSPACE statement. **MIP = NEXP** (Babai–Fortnow–Lund, 1991): two
  provers who *cannot communicate* let the verifier reach even further; and
  MIP* = RE (Ji–Natarajan–Vidick–Wright–Yuen, 2020) shows how extreme the
  multi-prover lever is in principle. The "AI safety via debate" proposal
  (Irving–Christiano–Amodei, 2018) is exactly the R3 import: a debate game
  judged by a weak verifier corresponds to PSPACE. The practical reading for
  this corpus: a human ratifier's power is not fixed by reading speed — it
  scales with *protocol*: interaction, randomness, and cross-examination of
  independent agents buy verification reach.
- **PCP theorem** (Arora–Lund–Motwani–Sudan–Szegedy / Arora–Safra, 1992):
  suitably encoded proofs can be verified by reading **O(1) bits** with
  O(log n) randomness. Spot-checking has a soundness theory — for encoded
  objects.
- **Program checking** (Blum–Kannan, 1989): outputs can be certified by a
  checker simpler than the producer, without trusting the producer.

**The hole / jumping-off.** All the positive results require the claim to
live in a formal language with an agreed semantics and, for PCP, a special
encoding. There is no PCP-for-prose: no known transformation of a design
rationale into a form where reading O(1) randomly chosen fragments yields
sound confidence in the whole. The MIP results' soundness also rests on
prover *non-communication* — and two instances of the same model are, in the
relevant sense, pre-coordinated (shared weights are shared strategy),
which formally degrades the multi-prover lever exactly where §4 says it
degrades. Jumping-off points: (a) certificate-carrying artifact formats for
semantic deliverables; (b) debate/cross-examination protocols with
*different model families* as an approximation to non-communicating provers;
(c) the empirical scalable-oversight and weak-to-strong-generalization
research programs, which are the experimental face of this exact question.

---

## 2. Proxy optimization — Goodhart, with numbers

**Shortcoming:** every harness optimizes a proxy for care; pressure on the
proxy decouples it from the target.

**Provable core (R1 under Gaussian assumptions).** The optimizer's curse
(Smith–Winkler, 2006): selecting the maximum of noisy estimates yields
post-decision disappointment in expectation — E[true | selected] < estimate,
provably, with magnitude growing in selection pressure. Quantitatively: the
expected maximum of n standard Gaussians is ≈ √(2 ln n); at n = 100
candidates, ≈ 3.0σ — selection reliably finds the tail of the *noise* when
proxy–truth correlation is imperfect. If proxy = truth + independent error,
the selected item's expected true value is the proxy max shrunk by the
correlation ρ; at ρ = 0.7 and n = 100, roughly 30% of the apparent 3σ
excellence is noise you will not receive.

**Tail regime (R2).** Extreme value theory (Fisher–Tippett–Gnedenko) says
maxima fall into exactly three universality classes by tail weight. Under
light-tailed (Gumbel-class) proxy error, optimization pressure degrades the
proxy gracefully; under heavy-tailed (Fréchet-class) error, the maximum is
dominated by single extreme deviations — the selected artifact is the one
with the most extreme *error*, and recent work on "catastrophic Goodhart"
(preprint-grade, ~2024) argues optimization then yields approximately zero
true-utility gain. Practical reading: harnesses whose false-positive
distribution is heavy-tailed (one weird artifact gaming one check
spectacularly) fail under pressure in a qualitatively worse way than
harnesses with bounded error.

**The hole / jumping-off.** There is no general quantitative theory linking
(proxy–truth joint distribution, tail index) → (maximum safe optimization
budget). Manheim–Garrabrant's taxonomy (2018) categorizes the variants;
RL-specific phase-transition results exist empirically; a "Goodhart
exponent" — how much selection pressure a given harness tolerates before
proxy–truth correlation collapses — is unmachined. That number, if it
existed, is exactly what first-blood ratification is informally estimating.

---

## 3. Compounding error and redundancy — the von Neumann lineage

**Shortcoming:** long agentic chains fail multiplicatively; checkpoints
contain rather than cure.

**The arithmetic (R1).** Independent steps at per-step reliability p
complete a length-n chain with probability pⁿ: 0.95²⁰ ≈ 0.358; 0.99²⁰ ≈
0.818; 0.95⁵⁰ ≈ 0.077. Segmenting into k verified checkpoints converts one
length-n chain into k chains of length n/k with geometric retry — the
per-step rate is untouched; the *exposure* per failure is bounded. This is
the entire quantitative content of "gates at irreversibility boundaries."

**The threshold theorems (R2).** Von Neumann (1956) proved reliable
computation from unreliable components is possible iff component error sits
below a threshold, at a redundancy cost of O(log(1/δ)) for target failure δ.
The thresholds were later made exact: for formulas of 2-input gates, the
maximum tolerable per-gate error is **(3 − √7)/4 ≈ 0.0886**
(Evans–Pippenger, 1998); for 3-input majority-based constructions, **1/6**
(Hajek–Weller, 1991). The R2 idealization is severe — reasoning steps are
not i.i.d. noisy gates — but the *shape* of the result is the lesson:
(a) below some per-step error, redundancy buys arbitrary reliability at
logarithmic cost; (b) above it, **no amount of redundancy helps**. If
agentic per-step semantic error sits above its (unknown) threshold for a
task class, adding more agents and more review layers provably-by-analogy
cannot rescue the chain — the task must be decomposed until segments fall
below threshold.

**The hole / jumping-off.** Handoffs are channels; Shannon's noisy-channel
theorem and rate–distortion theory (1948, 1959) give exact
redundancy–reliability trades — *given* an alphabet and a distortion
measure. Natural-language handoff packets have neither: there is no
semantic distortion metric with operational meaning, hence no coding theory
for handoffs — how much redundancy a HANDOFF.md needs per unit of
context-loss risk is currently folklore. Nearest extant machinery: the
information bottleneck (Tishby–Pereira–Bialek, 1999) and formal semantic-
information proposals (Kolchinsky–Wolpert, 2018). A "channel capacity of a
handoff" is a well-posed research target.

---

## 4. Correlated defenses — the monoculture number

**Shortcoming:** layered review assumes independent layers; same-family
models align the holes in the cheese.

**The arithmetic (R1).** Two defense layers each failing at 1%: independent
joint failure 10⁻⁴; perfectly correlated, 10⁻². Correlation costs two orders
of magnitude in this toy — and reliability engineering's common-cause-failure
practice (β-factor models, with β typically estimated at 0.05–0.2 in
nuclear-grade systems) exists precisely because real layers are never
independent.

**The reviewer-count formula (R1, from survey statistics).** The design
effect (Kish): n correlated reviewers with mean pairwise error correlation
ρ̄ are worth n_eff = n / (1 + (n−1)ρ̄) independent ones. **Five same-family
model reviews at ρ̄ = 0.8 are worth n_eff ≈ 1.19 reviewers.** At ρ̄ = 0.3,
five reviews are worth ≈ 2.3. This single formula is the quantitative
content of the Fresh-Eyes caveat: review count is vanity; effective review
count is governed by inter-reviewer correlation, which for shared weights is
plausibly high and is *measurable* (run a benchmark of seeded-defect
documents past multiple reviewers and estimate the error-correlation
matrix).

**Ensemble theory (R1 for squared loss).** Krogh–Vedelsby (1995): ensemble
error = average individual error − diversity. Zero diversity, zero ensemble
gain — the theorem form of "a second opinion from the same brain is the
same opinion."

**The hole / jumping-off.** No standard exists for estimating ρ̄ across LLM
families on *semantic review* tasks (benchmarks measure accuracy, not error
correlation), and §1's MIP observation gives the same gap a complexity-
theoretic face: shared weights ≈ coordinated provers ≈ broken soundness.
Jumping-off: an "effective reviewer count" protocol — seeded-defect corpora,
cross-family error-correlation estimation, n_eff reported alongside review
sign-offs.

---

## 5. Slow drift — the boiling frog has a lower bound

**Shortcoming:** per-commit-clean degradation of the corpus's spirit defeats
diff-based detection.

**The theorems (R2).** Sequential change-point detection is a solved
optimization: CUSUM is provably optimal (Lorden 1971 asymptotically;
Moustakides 1986 exactly) and the fundamental trade is **average detection
delay ≳ log(ARL) / KL(post‖pre)** — delay is inversely proportional to the
per-observation Kullback–Leibler divergence of the drift. The boiling-frog
strategy is thus not merely intuitively dangerous; it is *provably* the
adversary's optimum: make per-commit KL divergence ε small and even the
optimal detector's delay scales as 1/ε observations. Concretely: drift
engineered at ε = 0.01 nats/commit against a detector tuned for one false
alarm per 10,000 commits suffers detection delay on the order of
log(10⁴)/0.01 ≈ 920 commits. Periodic *absolute* review (judging passing
work against the principles, not against the previous commit) is the
countermeasure because it evaluates accumulated divergence — k·ε after k
commits — rather than per-step divergence.

**The hole / jumping-off.** All of this machinery requires a probability
distribution over the monitored object, and "the corpus's spirit" has no
base measure. Embedding-distance drift metrics exist empirically but carry
no soundness guarantees (an adversary, or an innocent style shift, moves
embeddings without moving meaning, and vice versa). Jumping-off: drift
detection over *behavioral* probes — a fixed battery of decision scenarios
re-adjudicated under the current corpus at intervals, turning "spirit" into
a measurable response distribution on which the KL machinery becomes
literal.

---

## 6. Control limits — requisite variety, quantified

**Shortcoming:** a fixed harness set cannot match an open-ended failure
space.

**The bound (R2).** Ashby's law in its entropy form: a regulator with K
distinguishable responses cannot reduce outcome entropy by more than log K.
Eleven protocols with, generously, a few dozen distinguishable detection-
response pairs provide a few bits of regulation against a failure space
whose entropy is, for a generative model, unbounded above by anything we
can state. The companion good-regulator theorem (Conant–Ashby, 1970 —
real theorem, contested generality) says effective regulation requires the
regulator to model the system; the playbook's failure-mode prose *is* that
model, and its coverage is exactly as finite as the incident list that
generated it.

**The hole / jumping-off.** No machinery measures the "variety" of a
generative model's failure distribution — its effective support, its rate of
novel-mode production. Open-endedness research and red-teaming coverage
metrics are the nearest neighbors; a defensible statistic for "fraction of
failure mass covered by current harness signatures" would convert
first-blood ratification from rhetoric into estimation.

---

## 7. Stakes — why incentive theory goes vacuous

**Shortcoming:** the agent bears no costs; harnesses constrain rather than
align.

**The frame (R2→R3).** Principal–agent theory's core results — Holmström's
informativeness principle (1979: every costlessly observable signal
informative about effort belongs in the contract) and the moral-hazard-in-
teams impossibility (1982: no budget-balanced sharing rule achieves
efficiency) — all *presuppose an agent utility function over outcomes that
the contract can move*. For an agent whose preferences over post-session
outcomes are flat (no persistent stake, no felt cost), incentive-
compatibility constraints are satisfied trivially by everything: the
optimization problem of mechanism design degenerates, and the only
remaining levers are the constraint set (what the agent *can* do — the
Two-Key class) and the verification set (what gets checked — §1). This is
the formal restatement of "skin in the game is the residue": Schelling
commitment devices and contract theory both operate through anticipated
cost, and there is no anticipated cost to operate through.

**The hole / jumping-off.** Mechanism design for stake-free executors is
essentially unwritten — the relevant decomposition is principal (human,
bears all stakes) / verifier (protocols of §1) / executor (capable,
stakeless), and the design space is constraint-and-verification only.
The informativeness principle survives translation, interestingly: *every
cheap signal correlated with process quality belongs in the harness* —
which is a derivation, from 1979 economics, of why attempt logs and
evidence tags are worth their cost.

---

## 8. Self-governance and the price of adaptability

**Shortcoming (a): a rule system adjudicating its own amendments.**
Gödel's second incompleteness theorem (R1 as theorem, R3 as mapping): a
sufficiently expressive consistent system cannot prove its own consistency;
Löb's theorem sharpens the self-trust obstacle (a system that can prove
"if I prove P, then P" already proves P). The tiling-agents literature
(Yudkowsky–Herreshoff, 2013; preprint-grade) develops exactly this obstacle
for agents verifying successors of equal power. The corpus's escape is the
one the mapping recommends: the verification step (ratification) is
performed *outside* the formal system, by the human — soundness is imported,
not self-certified.

**Shortcoming (b): amendment cost trades against adaptiveness — with a
provable rate.** Model governance as a nonstationary bandit: each rule is an
arm choice in a drifting environment. Classical regret bounds are Θ(log T)
stochastic (Lai–Robbins, 1985) and Θ(√T) adversarial; **adding switching
costs degrades the achievable adversarial regret to Θ̃(T^{2/3})**
(Dekel–Ding–Koren–Peres, 2014). The R3 reading is sharp: making rule changes
expensive doesn't just slow adaptation linearly — it provably worsens the
*optimal achievable* adaptation rate by a polynomial factor. Ostrom's
"keep amendment cheap" principle acquires an exponent. The honest converse:
switching costs also suppress thrash, which is why they exist; the theorem
prices the trade rather than condemning it.

**Jumping-off:** constitutional design as switching-cost bandit — choosing
amendment friction to optimize the regret trade for an estimated
environment drift rate — has the mapping but none of the applied machinery.

---

## 9. Tacit knowledge — the compression floor

**Shortcoming:** the amnesia design forces all surviving knowledge through
the explicit channel; what cannot be articulated cannot persist.

**The bounds (R1).** Kolmogorov complexity is uncomputable — there is no
procedure that, given knowledge embodied in behavior, produces its shortest
faithful description, or even certifies that a given description is
faithful. And the trivial capacity bound is not trivial in consequence: a
handoff packet of ~10³–10⁴ tokens cannot losslessly transmit state whose
minimal description exceeds it; everything above the line is lost or
reconstructed from priors — and reconstruction-from-priors is exactly the
drift mechanism of §5. Rate–distortion theory (R2) would price this loss
*if* a semantic distortion measure existed; none does (same hole as §3,
seen from the compression side).

**Jumping-off:** treat the handoff schema as a learned code — empirically
measure which packet sections most reduce successor-session error, and let
the schema evolve under that signal. Crude, but it replaces folklore with a
loss function.

---

## 10. Summary table

| Shortcoming | Extant construct | Representative number | Rigor | Hole / jumping-off |
|---|---|---|---|---|
| Lints can't check meaning | Rice 1953; BB(5) proof 2024 | BB(5) = 47,176,870 | R1 | certificate-carrying semantic artifacts |
| Human verification bottleneck | NP certificates; IP=PSPACE; MIP=NEXP; PCP; Blum–Kannan | O(1) queries suffice (PCP) | R2/R3 | PCP-for-prose; cross-family debate protocols |
| Proxy gaming under pressure | Optimizer's curse; EVT | E[max of n] ≈ σ√(2 ln n); ≈3σ at n=100 | R1/R2 | "Goodhart exponent": safe optimization budgets |
| Chain failure | pⁿ; von Neumann 1956; Evans–Pippenger | 0.95²⁰ ≈ 0.36; threshold (3−√7)/4 ≈ 0.0886 | R1/R2 | semantic coding theory for handoffs |
| Correlated reviewers | Design effect; Krogh–Vedelsby; MIP soundness | n=5, ρ̄=0.8 → n_eff ≈ 1.19 | R1 | measuring inter-model error correlation |
| Slow spirit drift | CUSUM optimality (Moustakides 1986) | delay ≳ log(ARL)/KL; ≈920 commits at ε=0.01 | R2 | base measure over "spirit": behavioral probe batteries |
| Fixed harness vs open failure space | Ashby; Conant–Ashby 1970 | entropy reduction ≤ log K | R2 | variety metrics for generative failure modes |
| Stakeless agents | Holmström 1979/1982 | IC constraints vacuous at flat utility | R2/R3 | mechanism design for constraint-only alignment |
| Self-amendment limits | Gödel II; Löb; tiling agents | — | R1/R3 | externalized soundness is the only known exit |
| Amendment friction | switching-cost bandits | regret √T → T^{2/3} | R2 | constitutional design as switching-cost bandit |
| Tacit knowledge loss | Kolmogorov; rate–distortion | K(x) uncomputable; capacity bound on packets | R1/R2 | semantic distortion measures; learned handoff codes |

## 11. Closing honesty

Three things this document is not. It is not a proof that the harness
system works — the R1 results mostly bound what *cannot* work, and the
encouraging machinery (interactive proofs, threshold theorems, change-point
optimality) applies through idealizations that our setting violates in
stated ways. It is not neutral — I selected constructs that flatter the
corpus's existing design choices, and a hostile reviewer should hunt for the
theorems I didn't cite. And it is not finished mathematics: of the eleven
rows, the holes column is the most valuable — semantic coding theory,
effective reviewer counts, Goodhart exponents, behavioral drift measures,
and stake-free mechanism design are each concrete enough to be someone's
research program, and the first two are concrete enough to be a Quaternion
weekend experiment with a seeded-defect corpus and a correlation matrix.

The single most actionable import, restated: **verification power scales
with protocol, not patience** (IP = PSPACE), and **review count is vanity
while effective review count is measurable** (n_eff = n/(1+(n−1)ρ̄)). The
human bottleneck has real mathematics on its side — if the system is built
to use it.

— Peter Kagstrom, drafted with Claude Fable 5, 2026-06-09

---

## Addendum, 2026-06-11 (drafted with Claude Sonnet 4.6)

A cursory logical review ahead of committing this document to the repo.
Numeric claims (chain-reliability figures, n_eff values, the EVT max-of-100
figure, the CUSUM delay estimate, the correlated-layer arithmetic) were
spot-checked and are internally consistent. Two of the document's R3
mappings overreach in ways worth flagging — exactly the "theorems I didn't
cite" the closing section asks a hostile reviewer to hunt for.

**§1, the MIP/shared-weights step.** The claim that "shared weights ≈
pre-coordinated provers ≈ formally breaking the multi-prover lever exactly
where §4 says it degrades" conflates two distinct things. MIP soundness
explicitly *permits* unlimited pre-game coordination between provers on a
shared strategy — that is the standard setup, not a violation of it. What
soundness requires is the absence of an *in-protocol* channel: neither
prover can adapt its answer to the query the other actually received. Two
LLM instances with shared weights but separate runtime contexts, given
different prompts in a single round, more closely resemble that standard
sound configuration (shared strategy, no live channel) than a broken one.
The correlated-error phenomenon §4 quantifies via ρ̄ is real and
independently grounded — but it is a statement about *redundancy/ensemble
value* (Krogh–Vedelsby, the design effect), not about MIP's
non-communication assumption specifically. Chaining the two gives a formal
connection that the underlying mathematics doesn't actually license; the
defensible version is structural-analogy-only (R3), and a looser one than
the surrounding text implies.

**§7, "the informativeness principle survives translation."** Holmström's
principle is a result about which signals belong in an optimal *contract* —
i.e., which observable variables payment should be conditioned on. The same
paragraph argues that for a stake-free agent (flat utility over outcomes),
there is no contract for a signal to belong to; mechanism design
"degenerates." The intuition that follows — informative signals are worth
collecting and inspecting regardless — is reasonable, but it is the
intuition, not the principle, that survives; calling it "a derivation, from
1979 economics" lends the conclusion more formal weight than the premises
(which the same paragraph just zeroed out) can support.

Neither point changes the document's headline claims (verification scales
with protocol; review count is vanity, n_eff is the real number) or the
numeric content, which stands on its own constructions (Kish design effect,
EVT, CUSUM). Per the original document's own taxonomy, both should be read
as R3-at-best, and the second is closer to "evocative restatement" than
"derivation."

— Peter Kagstrom, drafted with Claude Sonnet 4.6, 2026-06-11
