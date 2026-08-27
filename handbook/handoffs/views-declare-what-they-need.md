# Handoff — A view declares what it needs, and a topology does too

**Transient.** Written to be deleted when its work lands. Nothing here is a
decision; it is the state of four repositories and the list of things waiting
on somebody.

| | |
|---|---|
| **Stamped** | 2026-08-27 |
| **qm** | `4126c87` on `main`; this page's branch is cut from it |
| **dossier** | `1c37b96` on `feat/a-view-declares-what-it-needs` |
| **qmcp** | `00ce67f` on `evolve/a-topology-declares-what-it-needs` |
| **codecartographer** | `3480feb` on `feat/unify-ui-paths` — **another session's branch**, not touched here |

**Every number on this page was true at those commits and nowhere else.**
Re-derive rather than quote: `uv run qm capabilities`, `uv run dossier show
readiness`, `python scripts/license_gate.py` all answer for themselves.

---

## 1. State

### Landed on `main` today

| repo | pull requests |
|---|---|
| qm | #97–#107 — P17's mechanism, the charter's three states, the capability vocabulary, two propagations, the licence amendment |
| dossier | #42–#54 — ring and pointer work, clone, delta compounds, the recursion fix, harness queue truncation, the trim sweep, the capability window, the blind-review fixes, one GIF per narrative |
| qmcp | #31–#33 — the governed seam, its documentation, the seams a local round found |
| codecartographer | #94 — the capability graph |

### Open, and not merged

| what | where | state |
|---|---|---|
| **A topology declares what it needs** | qmcp #34 | Open, not draft. **Its checks did not run** — see §3.1 |
| **A view declares what it needs** | dossier `feat/a-view-declares-what-it-needs` | Committed, **not pushed**, no pull request. Local gates were running when this page was written |
| **This handoff and its retrospective** | qm `handoff/views-declare-what-they-need` | Committed, not pushed |

### Working trees

qm and qmcp are clean. dossier is clean on its branch. `codecartographer` has a
modified `governance/qm` on a branch this session did not create and did not
touch — **another session is working in that clone**; reconcile before writing
there.

---

## 2. For asynchronous review

Take one. They are independent and none blocks another.

### 2.1 The readiness model, in two repositories

`dossier.views.Need` and `qmcp.orchestration.Need` are the same idea applied to
different subjects: a view declares what it needs before it can *show* anything,
a topology declares what it needs before it can be *run*. Both name the thing
that satisfies the need.

**What to look at, in order of how much your judgement is worth:**

- **Whether the vocabularies should be one thing or two.** They are separate
  today, deliberately: `dossier` needs `project / harness / clone / corpus /
  attention`; `qmcp` needs `build / budget / workers / model / person`. The
  overlap is zero and the subjects differ, so a shared module would be a
  shared word with two meanings. That is a judgement and it may be wrong.
- **Whether `unknown` should block.** It does not, and one need uses it
  honestly: whether the overview's reading has been taken is recorded nowhere,
  so `attention` answers `unknown` and Outstanding stays reachable. The
  alternative — refuse the view on a measurement that never happened — was
  rejected as the worse error. Weigh that.
- **Whether the remedies are the right ones.** `Topology` and `Harness` send a
  reader to `uv run qmcp serve`, which is another program's command. That is
  the only exemption in the guard and it is named rather than pattern-matched.

### 2.2 The human queue, answered from dossier

`dossier harness queue` reads the harness live; `dossier harness answer <id>
<answer> --as <who>` answers one. This closes a loop `qmcp.governed` leaves open
on purpose — a model's draft arrives at the queue and stops.

**Answering is an attested act**, and three refusals follow from that: the name
is required and defaulted nowhere, there is no `--all`, and nothing answers on a
timeout or a retry. Check those are the right three.

Demonstrated end to end at the stamped commits: a governed run reached the
queue, was answered from dossier, left the pending list, and a second answer was
refused with the harness's own words.

### 2.3 The licence encoding

qm #107 is merged. The allowlist is generated from SPDX — the union of
`osi_approved` and `fsf_libre`, deprecated excluded — rather than typed. The
hand-kept list it replaced was wrong in both directions, and the gate's own
selftest had asserted that `GPL-3.0-or-later` *must fail*, which is copyleft
avoided technically and §1 forbids.

**Nothing here needs review to proceed.** It is listed because the `Pends on`
row it added is a live question — see §4.

---

## 3. Triage

Ordered by what it costs to be wrong about.

### 3.1 A pull request that reads green and was never checked

**qmcp #34's `pull_request` workflows did not fire.** `Tests`, `ADR lint` and
`One PR per contributor` produced no runs, on the pull request opening *and* on
a forced `synchronize` from an empty commit. Only `Submodule refs` ran, because
it triggers on `push`.

    GitGuardian Security Checks: pass
    check-submodule-refs: pass

**`gh pr checks` reports all-pass**, so the pull request reads merge-ready. The
seventeen merged before it were merged on exactly that signal.

- **Severity**: highest on this page. Not because the change is risky — it is
  small and locally green — but because the *signal* is wrong, and a wrong
  signal is worse than a red one.
- **What is established**: the workflows are `active`, carry no path filters,
  and ran normally on the previous pull request in the same repository hours
  earlier. Nothing is queued or awaiting approval. Push-triggered runs work.
- **What is not established**: the cause. Repository-level, account-level or
  platform — this session could not tell which from here. **Inference, not
  fact.**
- **Done looks like**: either the events resume and #34 shows four checks, or
  somebody establishes why they stopped. **Do not merge #34 on the current
  green.**
- **Worth checking across the estate**: whether any other repository is in the
  same state, because the same reading would mislead there too.

### 3.2 The narrative pictures are not reproducible

Two consecutive recordings of `first-run.gif` produce different bytes. The
picture is drawn from the live database — relative timestamps, ordering, a
synced-project count — so the committed file is dirty after every test run.

The claim made in that PR body and in the test docstring — *"a change to the
dashboard shows up in `git status`"* — **is false as built**. The file changes
regardless, so the signal is noise, and noise in `git status` teaches people to
`checkout --` past it.

- **Done looks like**: recording against a fixed, seeded database rather than
  the live one, so the picture is of a known dataset. A vendored font was added
  for exactly this reason and the data was left machine-dependent.
- **It also closes a second thing**: the CI skip added when the runner turned
  out to have no `dossier.db`. With a seeded database there is data everywhere,
  no skip, and the staleness check works on a bare runner.

### 3.3 A blank frame in a shipped narrative

`a-sweep.gif`'s middle frame is an empty Dependencies table. The tour never
selects a project, so per-project views inherit whatever the application
auto-selected.

- **Done looks like**: the narrative names its project and `tour_frames`
  asserts it was found. `show_project_details()` is the hook.
- **This is now cheap**: `dossier.readiness` can tell the tour which views can
  answer, replacing the hand-written exclusion list that carried a wrong
  diagnosis for a day.

### 3.4 Live reading and the payload file both claim the queue

`dossier harness queue` reads the harness; `dossier harness ingest` reads an
exported payload. They can disagree and nothing notices.

- **Done looks like**: a decision on whether the file survives, and if it does,
  a check that a disagreement between the two is reported. This corpus already
  has a record for that shape — a disagreement is a delta.
- **Argument for keeping the file**: it works when the harness is down, which is
  when you most want to know what it last did, and it is an artifact you can
  commit and diff.

### 3.5 `waiting()`'s truncation guard is inert

It reads `total` from the harness document; the harness does not send one, so
`total` falls back to the page length and `more` is always zero. Honest — it
claims only what the page holds — but it does not yet do the job it was written
for. Needs a count from qmcp or a second request.

---

## 4. Blocked on a person

| what | who decides | where it surfaces |
|---|---|---|
| **§5's scope boundary** — whether a project's *test* environment is inside the licence scan. `MIT-CMU` is the live instance: on neither the OSI nor the FSF list, while the package declaring it is a documentation tool | you | Pinned in `DRAFT-open-license-exclusion-and-upstream-remediation.md`'s `Pends on` row. **Nothing waits on it**; the encoding is correct either way |
| **`main` protection** — six drafted rulesets unapplied, so every "never push to main" rule here is customary | you | queued, per your instruction |
| **A live share link** — `claude.ai/share/7bbc74b5-7d95-4ca1-9610-0f628b2d64a8`, still recoverable from commit `0c1ac0b` on pushed `main`. Removing it from the working tree did not remove it from history, so revoking is the only fix | you | named in the 2026-08-23 security review |

---

## 5. Standing constraints still in force

- **Nothing unattended may spend.** Every paid call is a direct, deterministic,
  human-issued command. `dossier harness answer` posts an answer and spends
  nothing; `re-issue` is a decision, and the run still happens when somebody
  issues it.
- **Answering the human queue is attested.** A person's name, one question at a
  time, no defaults.
- **Assistants draft; humans ratify and cut tags.** No record here has been
  ratified and `Status` stays `Proposed` throughout.
- **Never push `main` directly.** This session worked briefly on dossier's
  `main` before noticing and moving the work to a branch — nothing was pushed.
- **The thread archive is never published.**

---

## 6. What could not be verified

Marked as inference, not fact.

- **Why qmcp's pull-request events stopped.** §3.1. Everything checkable was
  checked; the cause was not reached.
- **Whether MIT-CMU is OSI-approved in fact.** SPDX's data says `osi_approved:
  False` and that data is right about every licence that could be checked
  against independent knowledge. It is one source.
- **Whether the four blind readings found everything.** They are four positions,
  not a proof. A fifth would likely find a fifth thing.
- **Whether GitHub renders an animated SVG in markdown.** Not reached — the GIF
  route was taken instead, so this stayed unanswered rather than being resolved.

---

## 7. The single next action

**Establish why qmcp #34's checks did not run**, and do not merge it until they
do or somebody decides to merge without them. Everything else on this page can
wait; that one is a wrong signal, and a wrong signal spreads.
