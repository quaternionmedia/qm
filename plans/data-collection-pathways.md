# Plan — Collection pathways, and the end of propagation as the goal

**Status: stub. Five pathways sketched, none built, and the shift below is the
part that needs arguing before any of it.**

## The shift

**Governance propagation stops being the objective. Data collection becomes it.**

Propagation was the plan while the corpus was the thing being spread. The
inventory says what that assumed:

| | |
|---|---|
| Repositories on the host | 110 |
| In `ci/workspace.yaml` | 14 |
| **Neither seen nor planned for** | **96** |
| Cloned on this disk | 28 |
| Private / forks / archived | 34 / 10 / 2 |

Every plan this corpus has written — adoption, the phase ladder, the harness
status, propagation itself — was scoped to the 14. The other 96 were not
excluded; they were never visible. Propagating governance to 14 while 96 go
unrecorded optimises the wrong number.

So: collect first. What the org *has* is prior to what the org *governs*, and
the corpus currently cannot answer the first question.

**Open, and load-bearing: does this retire propagation, or defer it?** #57 is an
open propagation pull request. Eleven project branches have never seen this
session's work. If propagation is retired, those are abandoned rather than
pending, and somebody should say so out loud.

## What the five pathways share

Each is a source CI cannot reach. Each needs the same five things, and naming
them once is most of the design:

| | |
|---|---|
| **Capture** | what produces the data, and whether it is still producing |
| **Transport** | how it crosses to the archive — the hard part for anything offline |
| **Integrity** | how a reader knows a dump is complete and unmodified |
| **Space** | what it costs, and what gets dropped when that runs out |
| **Boundary** | what must not be collected, or must not leave a machine |

`unknown` is a value here as everywhere: a source nobody could capture is
recorded as uncaptured with the reason, never as empty.

## The five

### 1. Local dev machines that are never online

**Hardest transport, most at risk.** No network, so no pull — the machine must
emit, and something must physically carry it.

- Capture: a script that runs locally and writes a dated bundle
- Transport: removable media. There is no other answer for an air-gapped host
- Integrity: a manifest with hashes, signed on the machine that made it
- **Open:** is anything on these machines the only copy? If yes, this is the
  highest-priority pathway and not the fourth. Nobody has asked.

### 2. Private repositories and forks, arriving later

34 private, 10 forks. Some will open, some never will.

- Capture: `gh repo list` already sees them with the right credential; the
  inventory does
- Transport: ordinary clone, once permitted
- **Boundary:** a private repository may be private for a reason that outlives
  the collection. Collecting metadata (existence, size, last touched) is a
  different act from collecting contents, and the two need separate permission
- **Open:** does the archive hold contents, or an index plus a promise?

### 3. Full dumps from LLM vendors

Session and conversation exports, per vendor.

- Capture: vendor export, on request, in whatever shape the vendor gives
- Integrity: the export is the vendor's account of the sessions. It is evidence
  of what was said, not of what happened, and the two diverge — this corpus has
  measured its own narration wrong nineteen times in one thread
- **Boundary:** exports carry everything typed, including material that was
  never meant for a repository
- **Open:** does a vendor export belong in the corpus at all, or in an archive
  the corpus merely points at? Committing one would put a third party's format
  and a private conversation into a public governance repository

### 4. Local model runs, deterministic logs, tool output

The runs that leave no vendor trace.

- Capture: this is the one already half-built. `perspectives/artifacts/` is
  machine-scoped and gitignored; `ledger.yaml` is committed and human-written
- **Open:** the corpus already decided session artifacts are machine-scoped and
  must not be committed, because one machine's history would read as an org
  fact. Collection wants the opposite. That is a genuine conflict with a
  standing decision and it cannot be resolved by preferring the newer one

### 5. Human input, past and future

Media, publications, notes, things made offline. The largest and least
structured.

- Capture: mostly manual, mostly retrospective
- **Integrity:** provenance and date, or it is unattributable. The corpus's own
  rule — every figure was true at some commit — has no equivalent for a
  photograph
- **Boundary:** other people appear in human media
- **Open:** what is the smallest useful unit? A publication, a project, a year?
  Nobody has proposed one

## Space

No pathway has a budget and the total is unknown. `ci/disk-policy.yaml` already
exists for reclaim, with a `safety` tier per target — that vocabulary probably
extends here, and reusing it beats inventing one.

**Open:** is there a size at which collection stops being worth it? Answering
"no" is a decision with a bill attached.

## The low-hanging fruit, in order

1. **`uv run qm inventory`** — built. 110 against 14, refreshed on demand.
2. **Commit `inventory.json`** so the gap is a tracked number rather than a
   command somebody remembers to run.
3. **Metadata-only capture for the 96** — existence, visibility, size, last
   touched. No contents, no permission needed beyond what the credential has.
4. Then the pathways above, hardest transport first if pathway 1 holds unique
   data.

## What would make this plan wrong

The 96 are dormant, forked, or superseded, and collecting them buys an index of
things nobody will read.

**Tested 2026-08-16, and the answer is split.** Last touched, of the 96 the
corpus cannot see:

| | |
|---|---|
| Within 90 days | 6 |
| Within a year | 14 |
| One to three years | 21 |
| **Three years or more** | **55** |

So 57% are plausibly dormant and **20 have been touched inside a year, six
inside 90 days.** The strong form of the objection fails: this is not an index
of dead things. The weak form survives — most of the volume is old, and a
pathway that treats all 96 alike will spend most of its budget on the 3y+ tail.

**That suggests recency as the first cut, and nobody has agreed to it.** It is
also the kind of criterion that quietly discards exactly the material a
collection exists to preserve, since the oldest things are the ones least likely
to exist anywhere else.
