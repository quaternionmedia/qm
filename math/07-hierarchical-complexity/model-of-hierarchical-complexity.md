# Reference — The Model of Hierarchical Complexity

| | |
|---|---|
| **Standing** | Reference exposition for the math workspace. Not a record, not a perspective — the source material topic 07's experiments are designed against. Non-binding. |
| **Author** | Peter Kagstrom |
| **Tools** | Claude Opus 5 (Anthropic) |
| **Date** | 2026-08-15 |
| **Evidence** | **E1** for everything in §1–§3: the primary papers were fetched and read this cycle (listed in §6). This is the first document in this workspace whose source material is E1 rather than E5. §4 is my own analysis of those texts; §5 is explicitly R3. |
| **Task** | State what the Model of Hierarchical Complexity actually defines, what follows from it, and what it does not license — precisely enough that topic 07's experiments test something real. |

## 0. Why this is in the math workspace

The mathematical-limits perspective opens by naming its own characteristic
failure mode: *analogy dressed as theorem*. Its harness against that is the
rigor taxonomy — every claim tagged R1 (literal theorem), R2 (theorem under
stated idealization), or R3 (structural mapping).

That taxonomy classifies a claim's **warrant**. It says nothing about a
claim's **structural depth** — how many layers of organization the assertion
itself is stacking. Two claims can both be tagged R3 and be doing completely
different amounts of work: "handoffs are channels" relates two objects,
while "shared weights ≈ pre-coordinated provers, formally breaking the
multi-prover lever exactly where the design-effect formula says it breaks"
asserts a property of a correspondence *between two systems*. The 2026-06-11
addendum caught the second one and not the first, and it caught it by hand.

The Model of Hierarchical Complexity is a candidate for the missing axis. It
assigns tasks — and, if the mapping in §5 survives testing, claims — a
natural number measuring exactly that depth. Whether it can be applied to
prose reliably is an open empirical question, which is what topic 07 is for.

## 1. The formal core

Commons and Pekker (2008) give the tightest statement. Actions are defined
inductively: there is a unique simple action `Ã`, and every other action is
an ordered pair `A = ({A₁, A₂, …}, R)` — a multiset of at least two
previously defined actions, plus a rule `R` for organizing them.

Rules come in exactly two kinds, distinguished by permutation invariance of
the **outcome**:

- **Chain** — the outcome is the same for all `n!` orderings of the
  subactions.
- **Coordination** — there is at least one ordering that produces a
  different outcome.

Three axioms then fix the complexity function `h`:

- **HC1.** `h(Ã) = 0`.
- **HC2.** Every nonsimple action is either a chain of at least two actions
  of *arbitrary* orders, or a coordination of at least two actions all of
  the *same* order.
- **HC3.** `h(A) = maxᵢ h(Aᵢ)` if `A` is a chain;
  `h(A) = maxᵢ h(Aᵢ) + 1` if `A` is a coordination.

That is the entire generative content. Everything downstream — seventeen
named stages, the developmental sequence, the cross-species claims — follows
from those two lines. The result is a function `h : 𝒜 → ℕ`.

Two derived quantities matter here:

- **Work measure.** `φₙ = 2ⁿ`, the minimum number of simple actions needed
  to complete an order-`n` action.
- **Stage.** `stage(S, 𝒜) = max{ h(A) : A ∈ 𝒜 and A completed successfully
  by S }` — a performer's score is the ceiling of an observed task set, not
  a property of the performer.

The motivating example is distributivity. Evaluating `(a + b) + c` is a
chain: addition is associative, the organization is arbitrary, no
increment. Evaluating `a × (b + c)` is a coordination: the order matters, so
the order increments. Commons' analogy is that a ring is strictly richer
than a group precisely because it non-arbitrarily coordinates two operations
rather than carrying one.

## 2. The ladder

Two numbering conventions are live. The original order 1 was later split
into *automatic* and *sensory or motor*, pushing everything above it up by
one; a seventeenth order was added at the top in 2014. **Cite by name, not
by number** — see D11.

| Now | Pre-split | Order | What the action does |
|---|---|---|---|
| 0 | 0 | Calculatory | Exact computation, no generalization |
| 1 | — | Automatic | One hard-wired, unlearned reaction |
| 2 | 1 | Sensory or motor | Rote discrimination; conditioned response |
| 3 | 2 | Circular sensory-motor | Open-ended classes; phonemes |
| 4 | 3 | Sensory-motor | Concepts; respond to any stimulus in a class |
| 5 | 4 | Nominal | Relations among concepts; names |
| 6 | 5 | Sentential | Acquire sequences; chain words |
| 7 | 6 | Preoperational | Simple deductions; follow ordered lists |
| 8 | 7 | Primary | Logical deduction; arithmetic |
| 9 | 8 | Concrete | Full arithmetic; coordinate two perspectives |
| 10 | 9 | Abstract | Variables from classes; quantification |
| 11 | 10 | Formal | One unknown; linear one-dimensional logic |
| 12 | 11 | Systematic | Multivariate systems and matrices |
| 13 | 12 | Metasystematic | Compare systems; name their properties — isomorphic, complete, consistent, commensurable |
| 14 | 13 | Paradigmatic | Fit metasystems together into paradigms |
| 15 | 14 | Cross-paradigmatic | Fit paradigms together into new fields |
| 16 | — | Meta-cross-paradigmatic | Reflect on cross-paradigmatic operations |

Order 13 is the row that matters for this corpus. See §5.

## 3. What the empirical program shows

The method has been consistent for four decades: construct items at target
orders, collect responses, fit a Rasch model, then regress empirically
estimated item difficulty on the a priori order. Reported correlations
between MHC order and Rasch item difficulty (Commons & Chen 2014, Table 5):

| Instrument | r (df) | Instrument | r (df) |
|---|---|---|---|
| Balance beam | .980 (51) | Infinity | .912 (52) |
| Helper person | .977 (40) | Empathy | .910 (22) |
| Algebra | .966 (40) | Breakup dilemma | .835 (21) |
| Laundry | .964 (111) | Caregiver | .711 (42) |
| Counselor–patient | .934 (30) | Forensic expert bias | .698 (16) |

Commons et al. (2014, *Journal of Applied Measurement*) additionally report
that Rasch-scaled item scores at one order do not overlap those of adjoining
orders, and that testing for equal spacing found the orders equally spaced.

What this establishes: trained analysts can construct item sets whose
structural depth predicts empirical difficulty *before* data collection, in
domains with almost no surface content in common. That is the strongest
argument the model has, and it is a real one.

What it does not establish is in D10.

## 4. Dissection

Each finding carries a rigor tag in this corpus's taxonomy. These are my
analysis of the primary texts, not positions taken in the MHC literature.

**D1 — `h` is a gated rank function (R1).** Strip the developmental
vocabulary and HC1–HC3 describe the rank function of a well-founded tree.
The same recursion appears as: rank of a well-founded set
(`rank(x) = sup{rank(y)+1 : y ∈ x}`), order of a simple type
(`ord(σ→τ) = max(ord σ + 1, ord τ)`), circuit depth, and quantifier rank.
Four of those five increment on *every* composition. The MHC increments
**conditionally** — only across a non-commuting join. Hierarchical
complexity is not depth; it is *depth counted only across non-commutative
joins*. That gate is the model's entire novel content.

**D2 — `h` scores decompositions, not tasks (R1).** `h` is defined by
structural recursion on the term `({A₁,…}, R)`. Its domain is the set of
parse trees, not tasks. Nothing in HC1–HC3 constrains which term denotes a
given task, and no theorem establishes that `h` descends to the quotient by
outcome-equality. Any finite task can be re-expressed as a memorized lookup
table — a simple action, `h = 0` — with identical outcomes. The 2014 paper
concedes the principle: a computer running a program has no order of its
own, because the action belongs to the programmer. **Consequence: an OHC
score is a property of a task analysis, not of a task. The analyst is inside
the measurement.** This is the single most important finding for topic 07,
and it is why experiment 1 is inter-rater agreement.

**D3 — the coordination test detects non-commutativity, not dependency
(R1 for the reading; R2 for the repair).** The informal theory says a
higher-order action "non-arbitrarily organizes" its subactions — a claim
about structure. The formal test says some permutation of the execution
sequence changes the outcome — a claim about commutativity. These come
apart in both directions. *Over-generation:* any two actions sharing a
mutable resource are permutation-sensitive, so socks-before-shoes is a
coordination and "get dressed" sits an order above "put on a sock."
*Under-generation:* in `A = ({A₁,…}, R)` the organizing rule `R` sits
outside the permuted multiset, so any coordination symmetric in its
arguments — conjunction of two independently verified propositions,
comparison of two obtained quantities, class inclusion — passes the
invariance test and scores as a chain. The repair is to define the gate on
the dependency DAG rather than on sequence permutations; that is a design
proposal, not a theorem.

**D4 — HC2's equal-order clause has no lifting rule (R1).** Coordination
requires subactions of equal order, but real tasks coordinate across orders
constantly. Commons resolves this in his own worked example by fiat — `+`
at order 7 becomes `⊕` at order 9 "due to the distributive law." No rule in
the formalism licenses that promotion. Dropping the clause and defining
`h(A) = maxᵢ h(Aᵢ) + 1` for every coordination makes the function total and
costs nothing the model uses.

**D5 — `φₙ = 2ⁿ` prices an unfolded tree (R1).** The derivation quantifies
over tree unfoldings and tacitly forbids sharing. Under reuse the structure
is a DAG: the same depth needs 2ⁿ *executions* but only `n+1` *distinct
competencies*. The unmade argument is the stronger one — if what develops is
the set of distinct capabilities, the count is linear in `n`, which supports
treating `n` as the measure more directly than the exponential story does.

**D6 — horizontal and vertical complexity are not independent (R1).** The
2008 paper concludes from one example that the two are "independent and
incommensurate." The example establishes only non-equivalence. From the
model's own `φₙ = 2ⁿ`: `L(A) ≥ 2^h(A)`, hence **`h(A) ≤ log₂ L(A)`**.
Vertical complexity is bounded above by the logarithm of horizontal
complexity. They are the depth and the size of one tree.

**D7 — "Hbits" is a change of units (R1).** `φₙ = 2ⁿ` was derived from the
definition of order; taking `log₂` recovers `n` by construction. The
identity carries no information the definition did not already contain. The
Shannon analogy is a pun: entropy is a functional of a probability
distribution, and there is no distribution anywhere in the model.

**D8 — three of the five 2014 axioms carry no content (R1).** Axiom 1
("if a > b then φ(a) > φ(b)") presupposes an ordering on actions prior to
`φ`, which is what `φ` exists to define — circular as stated, and misnamed
(order-preservation is monotonicity, not well-ordering). Axiom 2
(transitivity) is inherited from ℕ. The genuine content lives entirely in
Axioms 3 and 4, which restate HC2 and HC3.

**D9 — Axiom 5 decodes to a falsifiable power law (R2).** As a statement
about labels, "equal spacing" is a tautology; the orders were labelled with
consecutive integers. As a statement about *difficulty*, combined with
`φₙ = 2ⁿ`, it asserts that difficulty is logarithmic in required primitive
work. Push that through the Rasch model the empirical program already uses:
with `δᵢ = δ₀ + c·nᵢ` and `n = log₂ φ`,

```
log odds = θ − δ₀ − c·log₂ φ
    odds = e^(θ−δ₀) · φ^(−c/ln 2)
```

**The odds of completing a task follow a power law in the number of
primitive operations it requires**, exponent `−c/ln 2` (≈ −1.44 at one logit
per order). R2 rather than R1 because it holds under the idealizations that
the Rasch model applies and that `φ` is the right work measure. This is the
one place in the model that can lose, and it is the throughline topic 07's
experiment 2 tests.

**D10 — what the Rasch evidence does not establish (R2).** Items are
constructed to the theory, so the result is about constructible item sets,
not tasks in the wild. No competitor structural metric is tested head to
head — since OHC is essentially tree depth, the studies cannot distinguish
"OHC predicts difficulty" from "some depth-like quantity does, and OHC is
one proxy." Some estimates are very unstable: four moral-reasoning
instruments of identical design report r(3) = .992, .919, .916 and .624.
And gaps in the *scale* (definitional) are repeatedly listed alongside gaps
in *performance* (empirical) as though they were the same kind of claim.

**D11 — the numbering is not stable (R1).** Pre-split, formal operations is
order 10; post-split it is 11. The 2008 formal-theory paper uses the old
numbering; most current writing uses the new. The 2014 paper uses both — it
announces "17 stages" and then calls the seventh order *primary*. The base
case also moved: 2008 sets `h(Ã) = 0`, 2014 sets `φ(x) = 1` for the simplest
action with 0 reserved for the null action.

## 5. What this licenses for the corpus — and what it does not

**The proposed mapping is R3, and nothing better.** MHC is validated on
constructed psychometric items, not on prose claims in a governance corpus.
Asserting that a claim in `perspectives/` has a well-defined order of
hierarchical complexity is exactly the move the mathematical-limits
perspective warns against in its own §0. It is offered here as orientation,
and topic 07 exists to find out whether it survives contact with two
annotators.

With that stated, the mapping is this. The rigor taxonomy classifies
warrant; MHC order classifies depth; the two are orthogonal, and a claim's
honest description is the pair.

The sharp case is **order 13, metasystematic** — the order whose defining
operation is *comparing systems and naming properties of the comparison:
isomorphic, complete, consistent, commensurable*. That is a precise
description of what an R3 structural mapping does. Which yields the
candidate throughline:

> An R3 claim is a metasystematic operation. The danger is not that it is
> R3; it is that metasystematic operations are routinely *written* in the
> grammar of order-11 formal claims — "X ≈ Y, formally breaking Z" — where
> the reader's warrant expectation is set by the grammar, not the tag.

That reframes the corpus's own worst near-miss. The 2026-06-11 addendum's
first correction (the MIP/shared-weights step) is exactly an order-13 claim
written as though it were order 11, and the addendum's repair is to demote
the *assertion grammar*, not the warrant tag. If order is reliably
assignable, the mismatch is mechanically detectable — which is experiment 3.

**What it does not license.** Not a quality ranking: high order is not
better, and D2 means order is analyst-relative, so an order label is a
claim about a reading of a text, not about the text. Not a substitute for
the R-tag: warrant and depth are independent, and a deep claim with good
warrant and a shallow claim with bad warrant are both ordinary. And not
anything at all until experiment 1 returns — if two annotators cannot agree
on the order of the same paragraph, the engine is inert and topic 07 should
be closed rather than elaborated.

## 6. Sources

All fetched and read 2026-08-15 (E1) unless marked otherwise.

- Commons, M. L. & Pekker, A. (2008). Presenting the formal theory of
  hierarchical complexity. *World Futures* 64: 375–382. — the axiomatization;
  HC1–HC3, C1–C4, `φₙ = 2ⁿ`, the distributivity example.
- Commons, M. L., Gane-McCalla, R., Barker, C. D. & Li, E. Y. (2014). The
  model of hierarchical complexity as a measurement system. *Behavioral
  Development Bulletin* 19(3): 9–14. — the five-axiom rewrite, Axiom 5,
  Hbits.
- Commons, M. L. & Ross, S. N. (2007). Introduction to the Model of
  Hierarchical Complexity. *Behavioral Development Bulletin* 13. — the stage
  table, the Piaget mapping, r = .92.
- Commons, M. L. & Chen, S. (2014). Advances in the model of hierarchical
  complexity. *Behavioral Development Bulletin* 19(4). — Table 5, the study
  catalogue.
- Commons, M. L. et al. (2014). Does the model of hierarchical complexity
  produce significant gaps between orders and are the orders equally spaced?
  *Journal of Applied Measurement* 15(4). — **E3**: summarized from the
  *Advances* catalogue; the full paper was not obtained.
- Commons, M. L., Trudeau, E. J., Stein, S. A., Richards, F. A. & Krause,
  S. R. (1998). The existence of developmental stages as shown by the
  hierarchical complexity of tasks. *Developmental Review* 8(3): 237–278. —
  **not obtained.** Source of "Theorem 4," the uniqueness claim D2 turns on.
  Anyone relying seriously on MHC scores should read that proof first.
