# Math — experiments workspace

| | |
|---|---|
| **Standing** | Non-binding research workspace. Not a record, not a perspective — a place to design and (eventually) run demonstrations against the open questions named in [`perspectives/claude-fable-5-2026-06-09-mathematical-limits.md`](../perspectives/claude-fable-5-2026-06-09-mathematical-limits.md). |
| **Source** | Each topic below corresponds to one or more "hole / jumping-off" entries from that document's §10 summary table. |

## Why this exists

The mathematical-limits perspective separates what's provable (R1/R2 —
theorems, applied literally or under stated idealizations) from what's
merely suggestive (R3 — structural mappings). The R1/R2 content doesn't need
experiments; it's already proven. The value left on the table is in the
**holes**: places where the relevant machinery (a distortion measure, a
correlation estimate, a base measure, an exponent) doesn't exist yet, and
the document names a "jumping-off point" instead of a result.

This directory groups those holes into six topics — by the open question
they share, not by which section of the source document they appear in,
since several holes recur across sections under different names. Each topic
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

## The two "Quaternion weekend" experiments

The source document calls out two holes as small enough to be a weekend's
work:

- a **seeded-defect corpus** to estimate inter-model error correlation
  (topic 03, experiment 1);
- a **handoff-section ablation** to learn which packet fields reduce
  successor error (topic 01, experiment 1).

If you're picking just one thing to actually run, start with one of those
two — they're the most self-contained and the most directly load-bearing
for this corpus's own review and handoff practices.
