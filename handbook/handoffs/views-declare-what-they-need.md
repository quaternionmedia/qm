# Handoff — A view declares what it needs, and a topology does too

**Transient.** Written to be deleted when its work lands. Nothing here is a
decision; it is the state of four repositories and the list of things waiting
on somebody.

| | |
|---|---|
| **Stamped** | 2026-08-27 UTC — the evening of the 26th where this was written. Every timestamp quoted below is UTC, which is the clock the host's run records use |
| **qm** | `4126c87` on `main`; this page's branch is cut from it |
| **dossier** | `1c37b96` on `feat/a-view-declares-what-it-needs` |
| **qmcp** | `42a2eae` on `main` — #34 merged after this page was first written |
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
| qmcp | #31–#34 — the governed seam, its documentation, the seams a local round found, and the needs a topology declares |
| codecartographer | #94 — the capability graph |

### Open, and not merged

| what | where | state |
|---|---|---|
| **A topology declares what it needs** | qmcp #34 | **Merged** at `42a2eae` — its four checks were green; see §3.1 for why this page first said they had not run. qmcp's slot is free (the fourteen open pull requests there are dependabot's) |
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

**§3.1 is first because this session called it the headline and it was not.**
It is closed, and it is left standing rather than deleted because the reading
that produced it is the thing worth carrying forward. The rest are open, and
§3.2 is the one that costs most to be wrong about.

### 3.1 A summary that cannot say "has not run yet"

**qmcp #34 is fine and this entry is smaller than it was first written.** For
about six minutes after the pull request opened, `Tests`, `ADR lint` and `One
PR per contributor` had no runs while `gh pr checks` reported:

    GitGuardian Security Checks: pass
    check-submodule-refs: pass

— all-pass, from the two that had reported, with **no row at all** for the four
that had not. Read inside that window the pull request looks merge-ready.

The four then queued and all four succeeded (E1):

    created   2026-08-26T23:54:05Z   (pull request opened)
    pushed    2026-08-26T23:57:42Z   (00ce67f)
    queued    2026-08-26T23:59:39Z   pull_request x4 -> all success

**This session read it as the events having stopped and it was delivery lag** —
the ordinary cause, missed by not waiting. What survives is the smaller and
still real thing: a check that has not run and a check that passed are the same
picture in that summary, and the window is long enough to act inside.

- **Severity**: low and transient. #34 is verified and can be merged.
- **Done looks like**: something that compares the `pull_request` workflows a
  repository *declares* against what has reported, so "four still pending" is
  distinguishable from "four passed". Every input exists — the workflow files
  carry their triggers, `gh run list` says what ran — and nothing joins them.
  It belongs in the seed.
- **And it is not a set difference, which is probably why it does not exist.**
  This page's own pull request, qm #108, reports seven checks while twelve
  workflows declare `pull_request`. All five absences are correct: four are
  filtered out by `paths:` that the diff does not touch, and `namespace-guard`
  is scoped to `branches: ['project/**']`. A naive comparison would report five
  missing checks on a healthy pull request — **which is the same error in the
  opposite direction**, and a guard that cries wolf is the one people learn to
  ignore. The check has to evaluate the filters against the diff.
- **Until it exists**: read the count, not the verdict. Four workflows declared
  and two rows on the summary is not a green.
- **One artifact still carries the wrong reading and cannot be edited.** The
  empty commit pushed to force a re-trigger is on `main` as `00ce67f`, with the
  message *"Re-trigger the pull-request checks, which did not fire on the first
  push"*. They did fire, two minutes later. Leave it; it is history, and this
  page is the correction.

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

- **Whether the local workflow runner agrees with the hosted one, on this
  machine.** It cannot be run from a PowerShell session here: every step fails
  at its first `run:` with `WSL ... execvpe(/bin/bash) failed`, because
  Windows resolves `bash` to the WSL shim, which then looks for Git Bash's
  interpreter inside the WSL namespace. Ten steps of ten in qm, five of five
  in dossier, every one at the first `run:` — the uniform result `AGENTS.md`
  item 10 says to read as a tooling fault. **Launching it from a Git Bash
  shell is the workaround**; the hosted runs are the evidence that stands.
- **Whether MIT-CMU is OSI-approved in fact.** SPDX's data says `osi_approved:
  False` and that data is right about every licence that could be checked
  against independent knowledge. It is one source.
- **Whether the four blind readings found everything.** They are four positions,
  not a proof. A fifth would likely find a fifth thing.
- **Whether GitHub renders an animated SVG in markdown.** Not reached — the GIF
  route was taken instead, so this stayed unanswered rather than being resolved.

---

## 7. The single next action

**§3.2 — record the narrative pictures against a seeded database.** It is the
one open item whose current state makes a false claim in shipped text: the
docstring and the pull request body both say a dashboard change shows up in
`git status`, and the file changes on every run regardless. Fixing it also
removes the CI skip that exists only because the runner has no `dossier.db`.

Everything above it is done: qmcp #34 is merged and that slot is free, and
dossier's branch needs only a pull request.
