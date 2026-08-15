# Math workspace — glossary

| | |
|---|---|
| **Standing** | Reading aid for this workspace. Non-binding, not a record. Defines terms as they are used in these topics and in the source perspective; it does not restate their full mathematical content. |
| **Evidence** | Inherits the source document's classes. Entries drawn from [`perspectives/claude-fable-5-2026-06-09-mathematical-limits.md`](../perspectives/claude-fable-5-2026-06-09-mathematical-limits.md) carry that document's blanket **E5** (training knowledge, unverified this cycle). Entries drawn from [topic 07's reference](07-hierarchical-complexity/model-of-hierarchical-complexity.md) are **E1**. |
| **Scope note** | Corpus process terms used in the source document but defined elsewhere in this repository — *first-blood ratification*, *Two-Key*, *squash discipline*, *perspective*, *record*, *ratification* — are deliberately not defined here. See `records/`, `handbook/`, and `README.md`. |

## Notation

| Symbol | Reads as | Where |
|---|---|---|
| `ρ` | proxy–truth correlation | 02 |
| `ρ̄` | mean pairwise error correlation across reviewers | 03, 04 |
| `n_eff` | effective independent reviewer count | 03 |
| `n*` | maximum safe selection pressure — the unmachined "Goodhart exponent" | 02 |
| `ε` | per-observation drift size, in nats | 04 |
| `K` | number of distinguishable regulator responses | 05 |
| `T` | time horizon in a bandit problem | 06 |
| `Θ(·)`, `Θ̃(·)` | exact growth rate; `Θ̃` suppresses logarithmic factors | 06 |
| `h(A)`, `φ(a)` | order of hierarchical complexity of an action | 07 |
| `φₙ` | minimum simple actions to complete an order-`n` action; `= 2ⁿ` | 07 |
| `κ` | Cohen's kappa — chance-corrected inter-rater agreement | 07 |

---

## A–Z

**ARL (average run length).** In change-point detection, the expected time
between false alarms when no change has occurred. Tuning a detector for a
long ARL (rare false alarms) costs detection delay — the trade CUSUM
optimizes. *(04)*

**Ashby's law of requisite variety.** Only variety can absorb variety. In
entropy form: a regulator with `K` distinguishable responses cannot reduce
outcome entropy by more than `log K`. The bound that makes a fixed playbook
inadequate to an open-ended failure space. *(05)*

**Bandit, multi-armed.** A decision problem where a learner repeatedly picks
one of several options with unknown payoffs. Governance is modelled as a
bandit whose arms are rule configurations and whose environment drifts. *(06)*

**Base measure.** A probability distribution over the object being
monitored, without which KL divergence and every change-point result are
undefined. "The corpus's spirit" has none; supplying one is topic 04's whole
problem. *(04)*

**Busy beaver, BB(n).** The maximum number of steps an n-state halting
Turing machine can run. `BB(5) = 47,176,870`, proved 2024; `BB(6)` exceeds
towers of exponentials. Cited as the scale at which undecidability bites.
*(source §1)*

**Chain rule (MHC).** A composition of actions whose outcome is the same
under all `n!` orderings of its parts. Chains do not raise the order:
`h(A) = max h(Aᵢ)`. Contrast **coordination rule**. *(07)*

**Change-point detection.** Sequential testing for the moment a data stream's
distribution changes. See **CUSUM**. *(04)*

**Common-cause failure / β-factor.** Reliability engineering's model for
non-independent defence layers; β is the fraction of failures that hit
multiple layers at once, typically estimated at 0.05–0.2 in nuclear-grade
systems. The physical-world ancestor of the correlated-reviewer problem.
*(03)*

**Coordination rule (MHC).** A composition where at least one ordering of
the parts changes the outcome, and all parts sit at the same order.
Coordinations raise the order by exactly one: `h(A) = max h(Aᵢ) + 1`. This
gate is the model's entire novel content. *(07)*

**CUSUM (cumulative sum).** The provably optimal sequential change-point
detector — asymptotically (Lorden 1971), exactly (Moustakides 1986). Its
detection delay is bounded below by roughly `log(ARL) / KL(post‖pre)`, which
is why slow drift defeats even an optimal detector. *(04)*

**Design effect (Kish).** `n_eff = n / (1 + (n−1)ρ̄)` — the survey-statistics
formula converting `n` correlated observations into an equivalent number of
independent ones. Five same-family model reviews at `ρ̄ = 0.8` are worth
about 1.19 independent reviewers. *(03)*

**Distortion measure.** In rate–distortion theory, the function saying how
bad a given reconstruction error is. Coding theory gives exact
redundancy–reliability trades *given* one; no such measure exists for
meaning, which is why handoff sizing is folklore. *(01)*

**Ensemble ambiguity decomposition (Krogh–Vedelsby 1995).** For squared
loss, ensemble error = average individual error − diversity. Zero diversity,
zero ensemble gain. The theorem form of "a second opinion from the same
brain is the same opinion." *(03)*

**Evidence classes E1–E5.** This corpus's convention for how a claim was
established: **E1** primary source read this cycle; **E2** multiple
independent secondary sources agreeing; **E3** a single secondary source;
**E4** inference from convention or documentation pattern; **E5** prior
training knowledge, unverified this cycle. Stated separately from
confidence. *(all)*

**Extreme value theory (Fisher–Tippett–Gnedenko).** Maxima of large samples
converge to one of exactly three families by tail weight: Gumbel
(light-tailed — optimization degrades gracefully), Fréchet (heavy-tailed —
the maximum is dominated by single extreme deviations), Weibull (bounded).
Which class a harness's error distribution falls in decides whether gaming
it fails gradually or catastrophically. *(02)*

**Gödel's second incompleteness theorem.** A sufficiently expressive
consistent formal system cannot prove its own consistency. Mapped onto a
rule system adjudicating its own amendments; the corpus's escape is to
perform ratification outside the system, by a human. See also **Löb's
theorem**. *(06, source §8)*

**Good regulator theorem (Conant–Ashby 1970).** Effective regulation
requires the regulator to model the system it regulates. Real theorem,
contested generality. *(05)*

**Goodhart's law.** When a measure becomes a target it ceases to be a good
measure. Manheim–Garrabrant (2018) give a taxonomy of the mechanisms; the
missing piece is the quantitative one — see **Goodhart exponent**. *(02)*

**Goodhart exponent (`n*`).** The hypothesised function from (proxy–truth
joint distribution, tail index) to the maximum selection pressure a proxy
tolerates before decoupling. Does not exist; topic 02 is about building a
first instance of it by simulation. *(02)*

**Hbits.** Commons' proposed unit: since `φₙ = 2ⁿ`, `log₂ φₙ = n`, so order
is claimed to measure "hierarchical information" in parallel to bits. The
reference document's D7 rates this a change of units rather than a result —
`2ⁿ` was derived from the definition of order, so taking `log₂` recovers `n`
by construction. *(07)*

**Hole / jumping-off point.** This workspace's organising unit: a place
where the source document found the relevant machinery missing and named a
research direction instead of a result. The six original topics group the
holes from the source's §10 summary table. *(all)*

**Information bottleneck (Tishby–Pereira–Bialek 1999).** A method for
finding representations that keep information about a target while
compressing the input. Named as the nearest extant machinery to a semantic
distortion measure. *(01)*

**Informativeness principle (Holmström 1979).** Every costlessly observable
signal informative about effort belongs in the optimal contract. Goes
vacuous for an agent with flat utility over outcomes — there is no contract
for a signal to belong to. The 2026-06-11 addendum notes that only the
*intuition* survives translation to stake-free agents, not the principle.
*(06)*

**IP = PSPACE (Shamir 1992).** A polynomial-time verifier with randomness,
interacting with an untrusted unbounded prover, can verify any PSPACE
statement. The formal backbone of "verification power scales with protocol,
not patience." *(03)*

**KL divergence (Kullback–Leibler).** An asymmetric measure of how far one
probability distribution is from another, measured in **nats** when using
natural logarithms. Drives CUSUM's detection delay. *(04)*

**Kolmogorov complexity.** The length of the shortest program producing a
given object. Uncomputable: no procedure produces, or certifies, the
shortest faithful description of tacit knowledge. The formal ceiling on what
a handoff packet can carry. *(01)*

**Logit.** Log-odds, `log(p/(1−p))`; the unit of the Rasch scale. Equal
spacing between MHC orders is a claim about logit gaps. *(07)*

**Löb's theorem.** A system that can prove "if I prove P, then P" already
proves P — sharpening the self-trust obstacle beyond Gödel II. *(06)*

**Metasystematic.** MHC order 13 (order 12 pre-split): the operation of
comparing systems and naming properties of the comparison — isomorphic,
complete, consistent, commensurable. Topic 07's candidate identification is
that an R3 structural mapping *is* a metasystematic operation. *(07)*

**MIP = NEXP (Babai–Fortnow–Lund 1991); MIP\* = RE (2020).** Multiple provers
who cannot communicate *during* the protocol let a weak verifier reach much
further than one prover allows. The 2026-06-11 addendum corrects a common
misreading: MIP soundness permits unlimited pre-game coordination on a
shared strategy; what it forbids is an in-protocol channel. *(03)*

**Nat.** Unit of information using natural logarithms rather than base 2.
Drift of "0.01 nats per commit" is the source document's worked adversarial
example. *(04)*

**NP certificate.** A witness that makes checking cheap even when finding is
expensive. The practical translation is to demand artifacts carrying their
own certificates — tests, reproducible builds, SBOMs — so a ratifier checks
a witness rather than repeating a search. *(03)*

**Optimizer's curse (Smith–Winkler 2006).** Selecting the maximum of noisy
estimates yields post-decision disappointment in expectation. The expected
maximum of `n` standard Gaussians is about `√(2 ln n)` — roughly 3σ at
`n = 100`, most of which is noise when proxy–truth correlation is imperfect.
*(02)*

**Order of hierarchical complexity (OHC).** The MHC's assignment of a
natural number to a task-action: 0 for a simple action, `max` of the parts
for a chain, `max + 1` for a coordination. Formally the rank function of a
well-founded tree, gated on non-commutativity. *(07)*

**PCP theorem (1992).** Suitably encoded proofs can be verified by reading
`O(1)` bits with `O(log n)` randomness. Spot-checking has a soundness theory
— for encoded objects, which prose is not. "PCP-for-prose" is the named
gap. *(03)*

**Program checking (Blum–Kannan 1989).** An output can be certified by a
checker simpler than the producer, without trusting the producer. *(03)*

**Rank function.** The standard construction assigning ordinals to a
well-founded structure by `rank(x) = sup{rank(y) + 1 : y ∈ x}`. The
reference document's D1 identifies MHC's `h` as an instance, distinguished
only by incrementing conditionally rather than on every composition. *(07)*

**Rasch model.** An item-response model placing persons and items on one
dimension: log-odds of success = person ability − item difficulty. The MHC's
empirical program regresses Rasch-estimated item difficulty on a priori
order. *(07)*

**Rate–distortion theory (Shannon 1959).** Gives the minimum rate needed to
represent a source within a given distortion. Would price handoff loss
exactly — if a semantic **distortion measure** existed. *(01)*

**Requisite variety.** See **Ashby's law**.

**Rice's theorem (1953).** Every non-trivial semantic property of programs
is undecidable. The reason lints check syntactic proxies: the semantic
target is not mechanically checkable, as a theorem rather than an
engineering shortfall. *(03)*

**Rigor taxonomy R1/R2/R3.** The source document's harness. **R1** — a
theorem applied literally; the objects in our setting *are* the objects of
the theorem. **R2** — a theorem applied under stated idealizations; the
theorem is real, treating our setting as its model is the approximation.
**R3** — a structural mapping; the mathematics is sound, the correspondence
is the speculation, and the value is orientation, not proof. Classifies
warrant only — the gap topic 07 addresses. *(all)*

**Species-accumulation curve.** Ecology's tool for estimating unseen
richness from a sampling effort; borrowed in topic 05 to ask whether the
playbook's failure-mode categories are converging or still climbing.
Good–Turing estimators of unseen mass are the associated machinery. *(05)*

**Stage of performance (MHC).** `stage(S, 𝒜) = max{h(A) : A ∈ 𝒜, completed
by S}` — the highest order of task a performer completes. A maximum over a
task set the experimenter chose, therefore a censored statistic, not a
trait. *(07)*

**Switching cost.** A penalty for changing arms in a bandit problem;
governance's analogue is amendment friction. Dekel–Ding–Koren–Peres (2014)
show switching costs degrade achievable adversarial regret from `Θ(√T)` to
`Θ̃(T^{2/3})` — a polynomial worsening of the *optimal achievable* adaptation
rate, not merely a linear slowdown. *(06)*

**Threshold theorem (von Neumann 1956).** Reliable computation from
unreliable components is possible if and only if per-component error sits
below a threshold, at redundancy cost `O(log(1/δ))`. Exact thresholds
followed: `(3 − √7)/4 ≈ 0.0886` for 2-input formulas (Evans–Pippenger 1998),
`1/6` for 3-input majority (Hajek–Weller 1991). Above threshold, *no amount
of redundancy helps* — the formal argument for decomposing tasks rather than
stacking reviewers. *(source §3)*

**Tiling agents.** The research line (Yudkowsky–Herreshoff 2013,
preprint-grade) on agents verifying successors of equal power, developing
the Gödel/Löb obstacle in an agentic setting. *(06)*
