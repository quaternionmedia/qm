# Math — experiments workspace

| | |
|---|---|
| **Standing** | Non-binding research workspace. Not a record, not a perspective — a place to design and (eventually) run demonstrations against the open questions named in [`perspectives/claude-fable-5-2026-06-09-mathematical-limits.md`](../perspectives/claude-fable-5-2026-06-09-mathematical-limits.md). |
| **Source** | Topics 01–06 each correspond to one or more "hole / jumping-off" entries from that document's §10 summary table. Topic 07 addresses a gap in the document's own harness rather than a row of its table, and says so. |
| **Branch** | This workspace lives on `workspace/math-experiments`, not on `main`. The source perspective carries an editorial note pointing here. |

## Why this exists

The mathematical-limits perspective separates what's provable (R1/R2 —
theorems, applied literally or under stated idealizations) from what's
merely suggestive (R3 — structural mappings). The R1/R2 content doesn't need
experiments; it's already proven. The value left on the table is in the
**holes**: places where the relevant machinery (a distortion measure, a
correlation estimate, a base measure, an exponent) doesn't exist yet, and
the document names a "jumping-off point" instead of a result.

This directory groups those holes into topics — by the open question they
share, not by which section of the source document they appear in, since
several holes recur across sections under different names. Each topic
directory has a `README.md` with:

- the hole(s), restated, with pointers back to the source document;
- a set of candidate demonstrations/experiments, ordered roughly by
  feasibility;
- for each, what it would actually teach us and what it wouldn't.

None of these have been run. This is a menu, not a results page.

## Topics

| Topic | Holes addressed | Source sections |
|---|---|---|
| [01 — Semantic coding for handoffs](01-semantic-coding-for-handoffs/) | Channel capacity / distortion measure for HANDOFF.md packets; learned handoff codes | §3, §9 |
| [02 — Goodhart exponent](02-goodhart-exponent/) | Safe optimization budget as a function of proxy–truth correlation and tail index | §2 |
| [03 — Effective reviewer count & verification protocols](03-effective-reviewer-count/) | Measuring inter-model error correlation ρ̄; certificate-carrying artifacts; cross-family debate as approximation to non-communicating provers | §1, §4 |
| [04 — Behavioral drift measures](04-behavioral-drift-measures/) | Base measure over "corpus spirit" for CUSUM/KL drift detection | §5 |
| [05 — Variety metrics](05-variety-metrics/) | Estimating the variety/entropy of a generative model's failure distribution | §6 |
| [06 — Stake-free governance design](06-stake-free-governance-design/) | Mechanism design for constraint-only alignment; amendment friction as a switching-cost bandit | §7, §8 |
| [07 — Hierarchical complexity as a claim-classification engine](07-hierarchical-complexity/) | No axis for a claim's structural *depth* — the rigor taxonomy classifies warrant only | §0, and the 2026-06-11 addendum |

[**Glossary**](GLOSSARY.md) — terms and notation used across these topics and
the source document.

## Topic 07's different standing

Topics 01–06 work holes the source document marked in its own summary table.
Topic 07 works one the document could not mark from the inside, because it
is a property of its harness rather than of its content: the R1/R2/R3
taxonomy classifies how well-warranted a claim is and has no axis for how
deep it is. The 2026-06-11 addendum found two overreaching claims by hand,
two days after the fact; both were R3 claims written in the grammar of
narrower ones.

The topic proposes the Model of Hierarchical Complexity as the missing axis
and carries a [reference document](07-hierarchical-complexity/model-of-hierarchical-complexity.md)
stating what that model actually defines. Two things about it are worth
flagging at this level:

- It is the first topic here whose source material is **E1** — the primary
  papers were fetched and read, not recalled.
- Its central mapping — that a claim in prose has a well-defined order — is
  **R3**, and the model's own formalism makes it fragile, since order is a
  property of a chosen decomposition rather than of the thing decomposed.
  Its first experiment tests whether two annotators agree at all, and a null
  result closes the topic rather than refining it.

## The cheap experiments

Three experiments across the set are small enough to be a weekend's work and
gate a disproportionate amount of what follows:

- a **seeded-defect corpus** to estimate inter-model error correlation
  (topic 03, experiment 1);
- a **handoff-section ablation** to learn which packet fields reduce
  successor error (topic 01, experiment 1);
- an **order-annotation reliability check** on the corpus's own claims
  (topic 07, experiment 1), which decides whether topic 07 has anything in
  it at all.

The first two are the most directly load-bearing for this corpus's review
and handoff practices. The third is the cheapest and the most decisive: it
either opens a topic or closes one.
