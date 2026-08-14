# The Mechanical Governance Loop

| | |
|---|---|
| **Date** | 2026-08-13 |
| **Author** | Peter Kagstrom |
| **Status** | Unreviewed |
| **Binds** | Nothing. `perspectives/` is opinion. |
| **Tools** | GitHub Copilot (Claude Sonnet 4.6), which drafted this |

---

## Scope and assignments

This document is a system-level plan. Three repositories carry the work:

| Repository | Role in this system | What it does *not* own |
|---|---|---|
| `qm` (this repo) | Generators, registries, policy files, adapter commands | Rendering, storage, gating |
| `dossier` | Dashboard, input layer, session artifact storage, counterfactual queries | Re-deriving governance facts, calling generators on its own |
| `qmcp` | Harness: MCP tools + HITL gate; the seam an agent actually touches | Generating indexes, storing artifacts |

The seams between them are all standard protocols: files (JSON/YAML), HTTP, MCP. No component
reads another's internal state. That is P3 applied to the governance layer itself.

---

## What this document is for

`2026-08-12-nineteen-reversals-and-what-a-clause-cannot-fix.md` ended on an
honest finding:

> The honest finding is that writing the clause did not change the rate. Four
> clauses exist, they are accurate, they are cited in two `AGENTS.md` files,
> and the failures continued at roughly one per hour of work. A fifth clause is
> not the remediation.

`2026-08-13-thirteen-breaks-and-the-five-that-became-yours.md` confirmed it
from a second session: every clause broken had been read in full by the session
that broke it. Eight were caught anyway — by running a check, not by remembering
a rule.

The corpus already knows how to turn a prose obligation into a mechanical check.
That pattern — generator, document, renderer, gate — is used for governance
status, harness slots, and disk policy. It is not yet used for the dev loop
itself. This document is the plan to close that gap.

**And it adds one thing the other documents do not have:** a mechanism to
compare hypothetical paths across the time horizon — retrospecting about a
worse or better decision to illuminate prospective questions of the same shape.
The inflation/deflation perspective established that one practitioner solving
different problems and reaching for the same structure three times is evidence
the shape is real. That same principle applies here: a shape captured in a
retrospective becomes navigable in a prospective.

---

## The loop today

```
Session → breaks → perspectives (prose) → [nothing] → next session (same breaks)
```

Every pattern captured in `perspectives/` is a free-form retrospective, not
structured data. Nobody can query "how many times has pattern X occurred" without
reading prose. No gate fails when a pattern crosses a recurrence threshold with
no check. No brief surfaces "this session has historically produced break Y in
situations with this shape."

---

## The system and its layers

Six logical layers, three repositories.

```
┌──────────────────────────────────────────────────────────────────────┐
│  Layer 1: Generators      qm/ci/         pure Python, no net deps    │
│  session_record.py        writes YAML artifacts (never inside repo)  │
│  pattern_index.py         reads artifacts → pattern-index.json       │
│  shape_index.py           reads artifacts → shape-index.json         │
│  check_pattern_coverage   reads index, exits non-zero on gaps        │
│  counterfactual_query     reads index, answers shape queries         │
│  (+ extended cowork_context.py for session brief enrichment)        │
├──────────────────────────────────────────────────────────────────────┤
│  Layer 2: Registries      qm/ci/         committed, reviewed policy  │
│  pattern-registry.yaml    slug → clause, threshold, check_exists     │
│  shape-registry.yaml      type/context → vocabulary, examples       │
├──────────────────────────────────────────────────────────────────────┤
│  Layer 3: Documents       perspectives/artifacts/  not committed     │
│  YYYY-MM-DD-branch.yaml   per-session break observations             │
│  pattern-index.json       frequency + coverage status by pattern     │
│  shape-index.json         instances + outcomes by shape type         │
├──────────────────────────────────────────────────────────────────────┤
│  Layer 4: Storage + API   dossier        SQLModel + FastAPI          │
│  DeltaNote rows           synced from Layer 3 artifacts              │
│  BreakObservation table   normalised rows from each artifact         │
│  GET /governance/patterns  uncovered, by date, by caught-by         │
│  GET /governance/shapes    by type/context; returns instances        │
│  POST /governance/session-artifacts  import artifact + re-index      │
├──────────────────────────────────────────────────────────────────────┤
│  Layer 5: Dashboard       dossier TUI    Textual                     │
│  "Loop" tab               pattern coverage + shape history           │
│  counterfactual panel     worst/best instance for any shape query   │
│  session artifact intake  import a YAML file, trigger re-index       │
├──────────────────────────────────────────────────────────────────────┤
│  Layer 6: Harness         qmcp           MCP tools + HITL gate       │
│  tool: cowork_context     calls Layer 1; returns enriched brief      │
│  tool: record_break       posts break to dossier API (Layer 4)       │
│  tool: query_shapes       queries dossier API for counterfactuals    │
│  tool: check_coverage     queries dossier API; HITL if gaps found    │
│  HITL gate                blocks session until human approves gap    │
└──────────────────────────────────────────────────────────────────────┘
```

The seams:
- Layer 1 ↔ Layer 3: filesystem (YAML/JSON files)
- Layer 3 ↔ Layer 4: file import (dossier syncs from files, same convention as `governance-status.yaml`)
- Layer 4 ↔ Layer 6: HTTP (`GET /governance/patterns`, `POST /governance/session-artifacts`)
- Layer 6 ↔ agent: MCP protocol

Every seam is a standard protocol. No component reads another's internal state.
That is P3 applied to the governance layer itself.

---

## The loop in motion

```
/cowork (qmcp tool: cowork_context)
  → Layer 1: cowork_context.py --out .harness/session-brief.md
  → Layer 6: query dossier /governance/patterns?uncovered=true
  → Layer 6: query dossier /governance/shapes?context=<this session>
  → returns enriched brief: uncovered patterns + prospective shape matches
                │
                ▼
         Session runs
                │
                ▼
/reflect (qmcp: record_break × N, then check_coverage)
  → Layer 1: session_record.py → perspectives/artifacts/DATE-BRANCH.yaml
  → Layer 4: POST /governance/session-artifacts (imports artifact, re-indexes)
  → Layer 1: pattern_index.py → pattern-index.json  (updated)
  → Layer 1: shape_index.py   → shape-index.json    (updated)
  → Layer 6: check_coverage → if gaps: qmcp creates HumanRequest (blocks)
  → Layer 6: query_shapes → counterfactual output for this session's breaks
                │
                ▼
  HITL gate (qmcp) holds until human responds to coverage gap
  OR session closes cleanly if no uncovered high-frequency patterns
                │
                ▼  (fold-back)
  Next /cowork inherits updated indexes via dossier API
```

The loop closes twice. **Tactically**: a pattern that recurs above threshold
without a check creates a HumanRequest in qmcp that blocks the session. The
human decides: draft a check, approve the gap with a stated reason, or defer.
Either way the decision is recorded. **Strategically**: every break captured as
a shape is immediately queryable by the next session entering the same territory
— not by remembering a rule, by reading a query result.

---

## Layer 1: Generators (`qm/ci/`)

Plain Python scripts. No server, no HTTP. They read files and write files. They
are the only things that produce the indexes. Everything downstream reads from
those indexes; nothing downstream re-derives what the indexes contain.

### `ci/session_record.py`

Accepts a YAML break list on stdin or as a file. Validates slugs against the
registries. Writes the structured artifact. Under 100 lines. The schema is the
contract; Layer 4 and Layer 6 both read it.

```yaml
date: "2026-08-13"
branch: "evolve/git-hygiene-and-handoff"
repo: "quaternionmedia/qm"
breaks:
  - pattern_id: uv-pip-install-bypass   # slug from pattern-registry.yaml
    clause: "AGENTS.md §12"
    caught_by: reviewer                  # mechanical-check | manual | reviewer

    path_taken:
      action: "uv pip install pydantic-ai, bypassing uv.lock"
      outcome: "starlette 1.6.0; 52 tests broke; false finding on 3 surfaces"
    path_avoided:
      action: "uv sync (correct)"
      outcome: "pydantic-ai 1.44.0; starlette 0.50.0; 278 passed, 11 skipped"

    # Shape is the cross-temporal key: what a prospective query matches on.
    # Two different pattern_ids can share a shape. Vocabulary from shape-registry.yaml.
    shape:
      type: environment-mutation
      context: adding-dependency
      reversibility: low          # low | medium | high
      decision_pressure: implicit # implicit | explicit | asked

    cost:
      commits: 3
      attention: high             # low | medium | high
      time: medium
      agency: environment-mutated

  - pattern_id: exit-code-trap
    clause: "async-contract §8"
    caught_by: manual
    path_taken:
      action: "run_workflows_locally.py | tail; echo $?"
      outcome: "tail's exit status reported; failure described as success"
    path_avoided:
      action: "run unpiped; read full output"
      outcome: "exit code preserved; failure immediately visible"
    shape:
      type: proxy-for-the-thing
      context: verifying-a-result
      reversibility: high
      decision_pressure: implicit
    cost:
      commits: 0
      attention: medium
      time: low
      agency: none

artifacts_produced:
  - "quaternionmedia/qm#56"
  - "quaternionmedia/qmcp#21"
```

**What it refuses.** Never writes inside the corpus. A committed artifact presents
one session's breaks as an org fact — same failure as a committed `disk_status.py`
output. The `.gitignore` entry for `perspectives/artifacts/` is load-bearing.

### `ci/pattern_index.py`

Aggregates artifact files by `pattern_id`. Same generator/document split as
`governance_status.py`. Output: `pattern-index.json`. Two layers: `count` and
`caught_by` are a pure function of the artifact files — verifiable offline.
`check_exists` cross-references the registry — also offline and deterministic.

### `ci/shape_index.py`

Aggregates by `shape.type` + `shape.context`. Output: `shape-index.json`. Each
entry carries the full `path_taken` and `path_avoided` of every instance, plus
`worst_cost_instance` and `best_catch_instance`.

### `ci/check_pattern_coverage.py`

Gate. Reads `pattern-index.json`. For every pattern whose `count >= threshold`
(per-pattern in the registry, default 3), if `check_exists` is unknown or false,
exits non-zero and names them. Under 50 lines. Runs in
`run_workflows_locally.py` alongside adr-lint and one-pr-check.

### `ci/counterfactual_query.py`

Reads `shape-index.json`. Given `--type` and `--context`, returns matching
historical instances with costs and avoided paths. The prospective query.

```
$ python ci/counterfactual_query.py \
    --type proxy-for-the-thing --context verifying-a-result

Shape: proxy-for-the-thing / verifying-a-result (7 instances)

Worst case (2026-08-08, committed damage):
  Taken:   audited apothecary from governance branch, not origin/main
  Outcome: false claim merged to main; caught 9 hours later
  Avoided: git -C <repo> diff origin/main; one command

Best-caught (mechanical-check, exit-code-trap):
  Avoided: run commands unpiped; read full output
  Check:   none yet (pattern-registry.yaml check_exists: false)
```

---

## Layer 2: Registries (`qm/ci/`)

Committed files. The vocabulary. Everything reads them; nothing else defines
the valid slugs or thresholds.

### `ci/pattern-registry.yaml`

```yaml
patterns:
  exit-code-trap:
    clause: "async-contract §8"
    description: "Exit status shadowed by a filter (tail, head, grep)"
    threshold: 3
    check_exists: false
  uv-pip-install-bypass:
    clause: "AGENTS.md §12"
    description: "Dependency installed with uv pip install, bypassing uv.lock"
    threshold: 1
    check_exists: false
  bind-past-localhost:
    clause: "async-contract §4"
    description: "Server bound to 0.0.0.0 rather than 127.0.0.1"
    threshold: 3
    check_exists: false
  act-without-asking:
    clause: "AGENTS.md standing list"
    description: "Destructive or environment-mutating act taken without asking"
    threshold: 3
    check_exists: false
```

### `ci/shape-registry.yaml`

```yaml
shapes:
  proxy-for-the-thing:
    description: "Reading a proxy instead of the subject (working tree, branch, exit code, empty result)"
    sources:
      - "2026-08-08-reading-the-proxy-instead-of-the-thing.md (12 of 13 errors)"
    contexts: [verifying-a-result, asserting-repository-state, reading-pr-state]
  scaffolding-measures-itself:
    description: "Measurement produced by the act of measuring"
    sources:
      - "2026-08-11-measuring-your-own-scaffolding.md (7 instances)"
    contexts: [diffing-files, running-a-test, reading-a-count]
  environment-mutation:
    description: "Modifying a shared environment without explicit authorisation"
    sources:
      - "2026-08-13-thirteen-breaks-and-the-five-that-became-yours.md (breaks 9, 11, 12)"
    contexts: [adding-dependency, starting-a-service, cleaning-up]
```

The shape vocabulary is not invented here. `proxy-for-the-thing` and
`scaffolding-measures-itself` are named and counted in the perspectives above;
the registry formalises names that already exist in the prose. A shape the
registry has never evaluated writes `{"unknown": "slug not in
shape-registry.yaml"}`. Expanding the vocabulary is a reviewed commit.

---

## Layer 4: Storage and API (`dossier`)

Dossier already parses `governance-status.yaml` and `harness-status.json` via
`parsers/governance.py`, which enforces the rule: read the document; never
re-derive a fact it carries; `subprocess` does not appear in the parser.
`tests/test_governance.py` asserts it. The same rule governs this extension.

### One schema, extending the delta entity

The loop stores into the delta tables on dossier's `wip/delta-entity-type-local`
rather than into tables of its own. That branch already carries `ProjectDelta`,
`DeltaNote` and `DeltaLink`; this layer adds three columns to one of them and
one new table.

The reason is that `DeltaNote` and a session artifact are the same row. Both are
a phase-stamped record attached to a unit of work: one written by a person during
planning, one emitted by a session during implementation. Modelled separately
they need two migrations, two sync paths, two panels, and a decision in every
session about which table a thing belongs in.

**`ProjectDelta` is unchanged.** The loop's aggregations are queries over
`BreakObservation` joined through `DeltaNote`, not columns on the delta.

**`DeltaNote` gains four columns**, all nullable, so existing rows and
human-written notes are unaffected:

```python
class DeltaNote(SQLModel, table=True):
    __tablename__ = "delta_note"

    id: Optional[int] = Field(default=None, primary_key=True)
    delta_id: int = Field(foreign_key="project_delta.id", index=True)
    phase: DeltaPhase                       # the delta's phase when written
    content: str                            # markdown; "" for an imported artifact
    created_at: datetime = Field(default_factory=utcnow)

    # the session-artifact half
    source: str = Field(default="human", index=True)   # human | session
    repo: Optional[str] = None
    branch: Optional[str] = None
    artifact_path: Optional[str] = None     # source file path; content not stored
    imported_at: Optional[datetime] = None

    breaks: list["BreakObservation"] = Relationship(back_populates="note")
```

**`BreakObservation` is the one new table**, hanging off the note rather than off
a session:

```python
class BreakObservation(SQLModel, table=True):
    __tablename__ = "break_observation"

    id: Optional[int] = Field(default=None, primary_key=True)
    note_id: int = Field(foreign_key="delta_note.id", index=True)
    pattern_id: str
    clause: str
    caught_by: str            # mechanical-check | manual | reviewer
    shape_type: str
    shape_context: str
    reversibility: str
    decision_pressure: str
    path_taken_action: str
    path_taken_outcome: str
    path_avoided_action: str
    path_avoided_outcome: str
    cost_commits: int
    cost_attention: str
    cost_agency: str
    note: DeltaNote = Relationship(back_populates="breaks")
```

**Every session artifact attaches to a delta.** `DeltaNote.delta_id` is not
nullable and `DeltaNote.phase` has no meaning without a parent, so `governance
loop sync` creates a delta for a session that is not already working one, with
`delta_type="session"` and `phase=implementation`. The alternative — a nullable
`delta_id` — was rejected because it produces rows whose `phase` column is
unreadable, and because a break that is not attached to the work it happened
during cannot answer the question the loop exists to answer.

**One migration, not two.** `005_delta_tables` must be re-parented onto
`008_release` before it can land at all; it carries the four `delta_note` columns
and `break_observation` in the same revision, renamed `009_delta_and_loop`.

**`ProjectDelta.phase` is a plain column and `advance_phase()` is a helper.**
The helper refuses to move an `abandoned` delta and returns `False` at
`complete`; nothing stops an assignment to `self.phase` that skips a phase,
reopens a completed delta, or revives an abandoned one. That is true today with
one writer. Under this layer the writers include `governance loop sync`, so the
guard's placement decides whether it holds — a fact for the delta branch's review
rather than a change this plan makes.

`sync` is dossier's `corpus.py` pattern: it calls the Layer 1 generators, then
imports the resulting JSON into SQLite. It never re-derives a governance fact —
it imports what the generators produced. `tests/test_governance_loop.py` asserts
`subprocess` does not appear in the API module or the parser.

### New API endpoints

```
GET /governance/patterns
  ?uncovered=true              → only patterns with check_exists false/unknown
  ?pattern_id=exit-code-trap   → single pattern detail
  → { pattern_id, count, caught_by, check_exists, instances: [...] }

GET /governance/shapes
  ?type=proxy-for-the-thing
  ?context=verifying-a-result
  → { shape, count, worst_cost_instance, best_catch_instance, instances: [...] }

POST /governance/session-artifacts
  body: { artifact_path: "perspectives/artifacts/..." }
  → triggers import + re-index
  → { imported: N, patterns_updated: [...], shapes_updated: [...] }
```

### New CLI

```sh
uv run dossier governance loop sync          # import artifacts, update indexes
uv run dossier governance loop dashboard     # open TUI on Loop tab
uv run dossier governance loop query \
  --type proxy-for-the-thing                 # counterfactual query
```

---

## Layer 5: Dashboard (`dossier` TUI)

A new "Loop" tab in the existing Textual TUI, using the same structure, key
bindings, and colour palette as the "Governance" and "Disk" tabs.

**Pattern panel** — DataTable of patterns, sortable by count and by `caught_by`
distribution. Rows with `check_exists: false` and count above threshold are
highlighted in WARN. The three semantic states (`ok`, `warn`, `unknown`) come
from `dashboard_style.py` — one colour system, shared across all three status
pages.

**Shape panel** — DataTable of shapes sorted by worst-cost instance. Selecting
a row opens a detail panel: all instances, each showing `path_taken` and
`path_avoided` side by side. This is the time-horizon comparison view. Reading
down the table from worst-cost to best-caught is the retrospective half;
pressing `q` on any row calls `query_shapes` and prints what a session about to
enter this territory should know.

**Key bindings** (same convention as Disk's `x`/`X`):
- `s` — sync from corpus (calls `governance loop sync`)
- `q` — counterfactual query for the selected shape
- `Enter` — expand selected row

**Document age is always visible.** The staleness of `pattern-index.json` and
`shape-index.json` is printed in the panel header. A dashboard that looks live
and is three days old is worse than one that admits its age.

---

## Layer 6: Harness (`qmcp`)

qmcp is the seam an agent touches. It exposes the governance loop as MCP tools
and owns the HITL gate when coverage gaps are found. Four new tools.

### Tool: `cowork_context`

Calls `ci/cowork_context.py`. Then queries the dossier API to add two sections
to the brief: uncovered patterns above threshold, and historical shapes matching
this session's announced context. If dossier is unreachable, the brief notes it
and continues — missing does not silently pass.

### Tool: `record_break`

Validates the break against the registries. Posts to dossier
`POST /governance/session-artifacts`. The agent calls this once per break during
`/reflect`.

### Tool: `query_shapes`

Calls `GET /governance/shapes?type=...&context=...`. Returns the counterfactual
history for a given shape. Used by `/reflect` and by the session brief.

### Tool: `check_coverage`

Calls `GET /governance/patterns?uncovered=true`. If any pattern is above its
threshold, creates a HumanRequest and returns `{"blocked": true, "request_id":
...}`. The calling workflow suspends until the human responds.

**The HITL interaction:**

```
Pattern coverage gap requires a decision.

Patterns above threshold with no mechanical check:
  exit-code-trap (count: 4, threshold: 3)
    Last caught by: manual (4/4 times)
    Worst reviewer cost: 0 corrective commits
    Path that avoids it: run commands without piping through filters

Options:
  [draft-check]    I will write the check before merging
  [approve-gap]    Known gap; proceeding for a stated reason
  [defer]          Not this session
```

`draft-check` unblocks and creates a stub at `ci/checks/exit-code-trap.py`.
`approve-gap` requires a stated reason, stored in the registry as
`check_exists: deferred-YYYY-MM-DD-reason`. `defer` unblocks with no action.

The `defer` path requires watching. A pattern deferred enough times is the same
as a clause read and violated: it exists, it is accurate, and it is not changing
behaviour. The dossier dashboard counts deferrals alongside the pattern count.
A pattern with three deferrals above threshold is surfaced in WARN regardless of
how the human responded each time. `defer` is not the same as `ok`.

---

## The counterfactual mechanism in full

The user's framing: *"retrospecting about a worse/better decision should give
insight into prospective questions of the same shape."*

**Retrospective half.** Every break recorded via `record_break` requires
`path_taken` (what was done, what it cost) and `path_avoided` (what could have
been done, what that would have produced). Both are required. Both require
specifics. An avoided path that says "no problems" without stating how is
rejected at the schema level — same constraint as the inflation/deflation
perspective: a deflation without evidence is a second claim under the same
burden.

**Shape as the cross-temporal key.** `shape.type` and `shape.context` connect a
2026-08-08 break to a 2026-08-13 break with nothing else in common. Both were
`proxy-for-the-thing / verifying-a-result`. The shape index aggregates them. The
counterfactual query surfaces both when someone asks "I am about to verify a
result — what happened last time someone was in this situation?"

**Prospective half.** When `/cowork` runs, the session brief includes Section B:
historical shapes matching the session's announced context. Before the session
has made a single decision, it has read the worst-case outcome for the shape it
is most likely to enter. This is not a checklist; the brief is read once, at
session open. It is structured historical evidence, not a reminder.

**The time-horizon comparison** lives in the dossier TUI Shape panel. Each row
in the DataTable is a shape; each detail panel shows instances sorted by date.
Left column: path taken. Right column: path avoided. Reading from worst-cost to
best-caught across dates is the comparison. Retrospecting that fork is how it
becomes a prospective warning.

---

## Constraints that are not optional

**The generator/document split is non-negotiable.** dossier reads; it never
re-derives. If the pattern index is wrong, the fix is in `ci/pattern_index.py`,
not in a query added to the dossier parser. `tests/test_governance_loop.py`
asserts `subprocess` does not appear in the API module or the new parser —
same assertion that governs the existing governance parser in dossier today.

**The registry is the vocabulary.** A slug not in the registry writes
`{"unknown": ...}`. Neither dossier nor qmcp accept an unknown slug as a valid
value. Expanding the vocabulary is a reviewed commit to `ci/pattern-registry.yaml`
or `ci/shape-registry.yaml`.

**Artifacts are machine-scoped, never committed.** The committed artifacts are
the registries. A committed session artifact would present one session's breaks
as an org fact — the exact shape of `disk_status.py`'s machine-scope error.

**The HITL gate must not expire automatically.** qmcp's AGENTS.md already names
the hazard: `GET /v1/human/requests/{id}` sets `EXPIRED` on a pending request
whose `expires_at` has passed, persisted by the read. Coverage gap requests must
have no `expires_at`, or a budget long enough to outlast active work. A request
that expires before the human sees it is a gate that closed without a decision.

**Unknown is a value throughout.** `check_exists: {unknown: ...}` is not
`check_exists: false`. A pattern the registry has never evaluated is different
from one the registry has evaluated and found lacking. The gate and the dashboard
treat both as gaps operationally, but the distinction is recorded so a triage
pass can tell them apart.

---

## Phased delivery

**Phase 1 — Generators and registries (`qm`)**
`pattern-registry.yaml`, `shape-registry.yaml`, `session_record.py`,
`pattern_index.py`, `shape_index.py`, `check_pattern_coverage.py`,
`counterfactual_query.py`. Extended `cowork_context.py`. `/reflect` adapter
command. `.gitignore` entry. Single PR. Gate test: `check_pattern_coverage`
against a known-gap fixture exits non-zero. No network dependencies.

**Phase 2 — Storage and API (`dossier`)**
`governance_loop.py` models. `governance loop sync` CLI. `/governance/patterns`
and `/governance/shapes` endpoints. `test_governance_loop.py` asserting
subprocess-free parsing. Single PR extending the migration sequence.

**Phase 3 — Dashboard (`dossier` TUI)**
"Loop" tab with Pattern panel and Shape panel. Counterfactual detail. Key
bindings. Single PR.

**Phase 4 — Harness (`qmcp`)**
`cowork_context`, `record_break`, `query_shapes`, `check_coverage` tools. HITL
pattern for coverage gaps. Metaflow example flow for session lifecycle. Single PR.

**Phase 5 — Seed propagation (`qm` → all projects)**
Move `session_record.py`, `pattern_index.py`, `shape_index.py`,
`check_pattern_coverage.py`, `counterfactual_query.py` to `project-seed/ci/`.
Move `/reflect` to `project-seed/ide/`. The registries stay in `ci/` —
org-level. Single propagation pass.

---

## What this does not solve

**It does not write the checks.** The HITL gate surfaces the gap; a human commits
the check. The loop makes the gap visible and records the decision; it does not
make it.

**It does not validate the avoided path.** A plausible `path_avoided` passes the
schema. The deflation principle applies: an avoided path that overstates the
benefit is a second claim under the same burden, and it is harder to catch
because it reads as rigour. Human review of artifacts is the only control here.

**It does not catch novel shapes.** A shape not in the registry writes
`{"unknown": ...}`. A dossier tab listing unknowns would make registry triage
prompt rather than scheduled — worth adding in Phase 3.

**It does not replace the handoff.** `/reflect` produces a structured
observation. The handoff states what is built and what is next. They are
complementary; neither supersedes the other.

---

## Why this is a perspective and not a record

The decisions this touches across three repositories — a new migration in
dossier, new tools in qmcp, new files in `project-seed/ci/` — each warrant a
record in their own project. What this document establishes is the architecture:
the seams, the vocabulary, the constraints that bind all three. The records that
follow reference it rather than re-arguing the shape from scratch.

The architecture is the thing most likely to be wrong before the first
prototype. The records are the things most likely to be right after it. The
distinction matters for which document gets corrected when the prototype finds
a gap.
