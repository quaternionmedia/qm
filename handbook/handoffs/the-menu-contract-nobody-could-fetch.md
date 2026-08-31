# Handoff — The menu contract nobody could fetch

**Transient.** Delete it when its work lands. Nothing here is a decision.

| | |
|---|---|
| **Stamped** | 2026-08-27 UTC |
| **Standing instruction** | *"continue locally until further notice."* **Everything below is unpushed**, deliberately, and §1 is the reason that sentence needs a date on it |

**Every number was true at the commits named and nowhere else.** Re-derive:
`npm run gate` in rad, `uv run pytest tests/rad` in dossier,
`uv run --with pytest --with pyyaml pytest ci/tests/` in qm.

---

## 1. Read this first: a local-only instruction has already cost this project once

`rad`'s `evolve/rad-v1` carries **seven commits that exist only on this disk**,
every one dated 2026-08-09. `origin/evolve/rad-v1` still points at the commit
that branch's own handoff flagged as stale — seventeen days ago, under the
heading *"six commits exist only on this disk"*, calling the push *"the
highest-value action on the page"*. It says why it was not taken:

> the instruction was to iterate locally, and it was given before a second
> session existed

That is the same instruction this session is working under. It is not being
questioned — it is being **recorded with a date**, because the cost is now
measurable and it is not confined to rad:

- `codecartographer` ships `web/tests/rad/vectors.v0.4.0.json`, byte-identical
  to rad `176ea60` — **the first stranded commit**. Its pin is to a contract
  version reachable from no remote.
- Four files in codecartographer cite *"the rad host integration standard"* §2,
  §4 and §5. That document is `adr/DRAFT-rad-host-integration-standard.md`,
  added by `a6cb517` — also stranded. **A reader who goes looking finds
  nothing**, in any of the four repositories.
- Three versions of the governed vectors are live and no two agree:

| where | version | cases | reachable? |
|---|---|---|---|
| rad `origin/main` | 0.3.0 | 34 | yes — and it is the oldest |
| codecartographer, vendored | 0.4.0 | 40 | no |
| rad `evolve/rad-v1` | 0.5.0 | 47 | no |
| this session's work | 0.6.0 | 58 | no |

**What this session did not do:** push anything. **What it did do:** avoid
adding a third unreachable consumer silently — dossier's new vendored copy
carries its provenance and the caveat in its own module docstring, in the file a
reader opens first.

---

## 2. What was built

All of it is local. Branch names are given because nothing else identifies it.

### rad — `evolve/consolidate-rad`, 11 commits ahead of `origin/main`

Cut from `evolve/rad-v1`, then `main` merged in — **clean, no conflicts**, which
is worth knowing before anyone treats the stranding as risky. Then:

- **`ab124d1` — the cell layer gets an executable half.** The record
  *the menu addresses nine cells* said conformance would gain cell cases. It had
  not, at any version. Now `conformance/vectors.json` is **v0.6.0, 58 cases**,
  eleven of them new: placement order, the centre holding nothing at every size,
  reachability of every occupied cell by direction alone, grid movement clamping
  at the edge, the chord in both orders, and the agreement bound below. The
  reference implementation gained the pure functions to run them against.
- **`be6e486` — the seam takes a cell.** §2b of the host integration standard,
  written because that document predates the cells record and §3 says input is
  polar, which is unusable for a host with no pointer.
- **`7c75bbf` — `AGENTS.md` stops describing a cleared blocker.** See §4.

`npm run gate`: **371 passed, 0 failed, 0 skipped, 0 flaky** — the runner's own
words, *"deterministic … eligible to support a tag."*

### dossier — `feat/the-terminal-replays-the-governed-vectors`, 1 commit

`tests/rad/test_conformance.py` replays the governed cell suite against
`dossier.rad.numpad`. **This port implemented the cells and replayed nothing**,
while `docs/plan-rad-tui.md` said it *"is held to the same cases"* — a
commitment nothing carried out, in the document that made it. Suites a terminal
cannot answer are named with a reason and fail if one belongs to neither list.

Local gates: **1387 passed**, one step failed — `reuse-lint :: Install REUSE`,
which passes when that workflow is run alone and fails when several install
into the same user site-packages at once. That is the local runner's property,
not the branch's; the hosted `REUSE lint` is green on this repository's last
several pull requests, and `python -m reuse lint` here reports 226 of 226 files
covered.

### qm — `evolve/the-status-sees-local-records`, 1 commit

`governance-status.yaml` reports rad with **zero records** while rad holds
eleven. The census counts a project's `adr/` on its corpus branch, and
`project/rad` carries only the seeded `README.md` and `TEMPLATE.md`. The
generator now also reads the `RECORDS_DIR` a project's own `adr-lint.yml`
declares, so a zero can be told apart from records kept somewhere it does not
look. `ci/tests/`: **1074 passed, 8 skipped.**

---

## 3. The finding that came out of writing the vectors

**The nine-cells record promised a cell↔angle mapping that cannot exist above
four items**, and writing the conformance cases is what surfaced it.

Clause 2 says a cell number *is* a screen direction and may not be reassigned.
Clause 3 places cardinals first — `8, 6, 2, 4, 9, 3, 1, 7`. Clause 4 concluded
that *"the cell number is the name of a wedge."* The first two are compatible;
the third does not follow. Cardinals-first and clockwise-from-the-top are the
same order only for `N ≤ 4`:

    n=4  agrees
    n=5  i=1 cell 6 (0°)   ring -18°    off 18°
    n=8  i=3 cell 4 (180°) ring 45°     off 135°

At the eight-item ceiling the record calls structural, an item is drawn at 45°
and addressed as the cell that points at 180°.

**The trade is real and the record had not noticed it.** Placing clockwise makes
clause 4 true at every size and puts a four-item menu in one quadrant instead of
at the cardinals. Cardinals-first keeps the common case and pays above four. The
draft now states which side it picked, why, and what would reverse it; clause 4
says what is true instead; and `cellAgreesWithRing(N)` is pinned true at 1 and 4
and false at 5 and 8 so no port can adopt one order and claim the other.

---

## 4. Cleanup, and one claim this session got wrong on the way

- **rad keeps `adr/` in its own repository, and that is supported.** The seed's
  `adr-lint.yml` offers two models behind `RECORDS_DIR`; rad sets it to `adr`
  and the lint runs clean against those records. This session first read rad as
  the estate's only outlier doing it wrong — that reading was **wrong**, and it
  came from comparing record counts across projects before reading the workflow
  that explains them.
- **What *is* stale is rad's `AGENTS.md`**, which said the submodule *"cannot
  exist yet"* and the workflow *"will fail until the submodule exists."*
  `.gitmodules` pins `project/rad`, the branch exists, and the lint is clean.
  Corrected in `7c75bbf`.
- **`tests/governance.spec.mjs` has outlived its own stated condition.** Its
  first line says to delete it when the submodule lands. It landed. Two copies
  of one check is what its own header calls the drift the seed exists to avoid.
  **Not deleted here** — the lint and the spec do not assert identical
  properties, so removing it is a coverage decision, not a tidy-up.
- **A vendored contract silently changed licence.** dossier's blanket REUSE rule
  would have declared a copy of rad's Apache-2.0 vectors as MIT under a
  different copyright line. Fixed with an override that keeps rad's licence and
  says why. **REUSE lint passed either way** — it checks that a declaration
  exists, never that it is right.

---

## 5. Triage

### 5.1 codecartographer declares rad's Apache-2.0 file as MIT

`web/tests/rad/vectors.v0.4.0.json` is a verbatim copy of rad's vectors. cc's
`REUSE.toml` has a blanket `path = "**"` MIT rule and an Apache-2.0 override
list that does not include it. Same defect dossier nearly shipped, already in
that repository.

- **Not fixed here.** codecartographer is on `feat/unify-ui-paths` with a dirty
  `governance/qm` — **another session's tree**. Reconcile before writing.
- **Done looks like** an override on `web/tests/rad/vectors.v*.json`. One block.
- Both projects are Quaternion Media, so nothing is misappropriated. Apache-2.0
  to MIT still drops a patent grant and a notice obligation, and it makes the
  file read as something cc wrote.

### 5.2 The reference implementation still walks the ring

rad's page has the cell core and its key handler does not use it —
`index.html`'s menu keys are still `(highlight + 1) % n`, the walk the record
was written against. So the record's own reference implements the cells in
`cellStep`/`cellStepToItem` and reaches them from nothing.

- **Deliberately not wired here.** It changes the page's behaviour, its IPA
  figures, its screenshots and every generated guide page — a slice of its own,
  not a rider on the vectors.
- `docs/guide/keyboard-path.md` describes the walk and is **accurate today**
  because of that. It stops being accurate the moment the handler changes.

### 5.3 codecartographer is three vector versions behind

Pinned at `v0.4.0`; governed is now `v0.6.0`. Bumping is not a version-string
edit: cc's runner has no `cells` branch, so replaying v0.6.0 would send eleven
cases into its trace fallback and fail them. Implementing the cells there is the
work, and cc is a pointer host, so §2b's open question — what a host that
renders a ring *and* accepts cells should do — is asked of it first.

### 5.4 The census still counts one place

qm's change reports where a project says its records live; it does not count
them there. Reading the second location means fetching a tree from the project
repository, which the generator does elsewhere and not here.

---

## 6. What could not be verified

- **Whether pushing `evolve/rad-v1` is safe against anything downstream.**
  Nothing in this estate submodules rad, and no `project/rad` propagation
  exists — but that is an absence measured from here, not a survey.
- **Whether `tests/governance.spec.mjs` and the seed lint assert the same
  properties.** Asserted as *not* identical on a reading of both, not on a
  property-by-property comparison.
- **Whether the eight skips in qm's `ci/tests/` predate this session.** They
  were not introduced by it — the change touches one module — but no
  before-and-after run was taken.

---

## 7. The single next action

**Decide whether rad's local-only window is still open.** Everything else on
this page is downstream of that one answer, and the page exists because the
question was last asked seventeen days ago and never closed. If it is still
open, this handoff is the record of what is on the disk. If it is not,
`evolve/consolidate-rad` is clean against `main`, its gate is deterministic, and
pushing it makes two other repositories' citations resolve.
