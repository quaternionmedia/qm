# Handbook — Where This Corpus Is In Its Own Adoption

**Routing.** Operational status, not a decision record: it weighs no
alternatives and constrains nobody. It exists because a corpus that governs
projects should be able to answer, in one place, how far along it is in
governing itself. The decisions it reports live in `records/`.

**Read this if** you are picking the work up cold and need to know what is
wired, what is written but not yet binding, and what is deliberately waiting.

---

## The short version

Every org record is **`Proposed`**. None is ratified, and that is a decision
rather than a backlog: **ratification waits on a second active code owner.**

The mechanisms are not waiting. Where a record describes machinery that costs
nothing to run before ratification and protects something in the meantime,
the machinery is live and the record's Status is still `Proposed`. The two
are independent, and holding the machinery back would leave a known gap open
for bookkeeping's sake.

---

## What is enforced today

| Mechanism | Enforces | Where |
|---|---|---|
| ADR lint, four checks | banned vocabulary in drafts; numbered filenames not ratified; edits to a ratified body outside Amendments; index/directory mismatch | `.github/workflows/adr-lint.yml`, logic in `project-seed/ci/adr_lint.py` |
| REUSE lint | every file carries copyright and licence; every licence text present and used | `.github/workflows/reuse-lint.yml` |
| Symlink integrity | the pointer files stay mode `120000` rather than degrading to stale copies | `.github/workflows/symlink-integrity.yml` |
| Namespace guard | a `project/*` branch's own commits touch `adr/` only | `.github/workflows/namespace-guard.yml` |
| IDE discovery | `AGENTS.md` at root, with `CLAUDE.md` and `.github/copilot-instructions.md` as symlinks to it | repo root, mirrored in `project-seed/ide/` |
| Attribution | `Author` names an accountable human; tools disclosed as a `Tools:` note | `perspectives/README.md` and each file's own header |

The vocabulary check reads prose only — fenced blocks, inline code spans and
HTML comments are excluded — which is what lets a document quote the banned
list without tripping on it.

## What is written but not yet mechanical

- **Branch protection.** The rulesets are checked in at
  `.github/rulesets/` as configuration with an apply script a human runs.
  Nothing is applied. That directory's README carries the staged path.
- **The commit-trailer ban.** Human-only contributorship is the one rule an
  assistant's *default tooling* violates automatically, and it is currently
  an instruction rather than a check. Ruleset A carries the negated
  `co-authored-by:.*noreply` pattern that closes it.
- **The carried-patch register.** No gate can detect a patch applied during a
  build, so registration is an obligation on whoever adds it and a reviewer
  following fork step 7, not a check. The records now say that rather than
  claiming a lint.
- **`reuse lint` beyond this repository.** It blocks here. No other QM
  repository has been inventoried, so each runs it in reporting mode until
  its own licensing pass is done.

## What a project owes, and who checks

Eight obligations follow from the org records and are produced by nothing
automatic — the baseline component audit, cumulative licence gates, the
service inventory no scanner can build, the quarterly upstream scan, naming a
seam protocol, the control-plane instance record, a risk register, and
registering carried patches.

They are listed with what satisfies each in `project-seed/adr/README.md`,
under "What the org records oblige this project to produce", which every
project copies. Fork step 6 routes a new project there. **A project is not
compliant because it copied the seed**; a project that cannot satisfy one yet
names the gap in its adoption record.

**Audited so far: qmetronome only** (2026-08-08, the first exercise of the
propagation runbook). It was correctly pinned to its branch and had none of
the IDE governance-discovery artifacts, plus a pre-seed inline lint running one
of the four checks. Being pinned is not being adopted, and nothing reports the
difference — which is why the audit has to be walked per project rather than
inferred.

**apothecary** was audited next (2026-08-08) and is the healthiest instance:
level with `main`, touching `adr/` only, every seed artifact present with the
pointer files at mode `120000`, and a **working dependency-manifest license
gate** — the first real instance of the open-license record's §4 enforcement
anywhere. Its only gaps are the `<name>` placeholder and an ADR lint still on
the single-check version.

The audit paid for itself immediately. apothecary's CI had failed on
`upload-pack: not our ref` — a submodule pinned to a commit that was not
pushed. qmetronome had hit the same failure, written a check for it, and
nothing carried that check across. It is now `project-seed/ci/submodule-check.yml`,
which is what the seed is for.

The other six adopting projects have not been audited. That is the largest
open item on this page.

## What is deliberately waiting

**Ratification, on a second code owner.** GitHub does not count a PR author's
own approval, and one account authored this corpus. A ratification gate that
one person can satisfy alone is a gate in name only, so the Status field
waits for the thing that makes it mean something.

The cost is real and worth naming: while every record is `Proposed`, the
corpus contains **no worked example** of a ratified record, of an
`## Amendments` region, or of the append-only discipline `TEMPLATE.md`
describes. New projects therefore learn the drafting half of the discipline
by example and the ratified half only by reading about it.

Nothing else is blocked by it. Records bind by adoption and by the checks
above; the drafting discipline is enforced today.

---

## The branch model, in one place

`main` carries the constitution and nothing else. Four namespaces hang off
it, and a branch outside them is a mistake rather than a variation.

| Namespace | Holds | Lifetime |
|---|---|---|
| `project/<name>` | one adopting project's `adr/` | permanent — a downstream submodule pins its tip |
| `perspective/<date>-<slug>` | one perspective, staged for `main` | deleted after merge |
| `evolve/<slug>` | org-level work in progress | deleted after merge |
| `workspace/<slug>` | a research workspace that never merges back | permanent, terminal |

Two properties of this model cause most of the confusion, and both are
mechanical rather than a matter of care:

- **A merge cannot fix a copy.** `adr/TEMPLATE.md` and
  `project-seed/adr/TEMPLATE.md` are different paths, so a branch can be zero
  commits behind `main` and still carry a stale template.
- **Propagation runs one way.** `main` flows outward. Org content committed
  on a `project/*` branch is stranded permanently.

`handbook/propagation-runbook.md` is the procedure for both.

## Revisiting this page

It is status, so it goes stale by default. Update it when a record ratifies,
when a stage in `.github/rulesets/README.md` is reached, or when something in
"written but not yet mechanical" becomes mechanical. If it ever needs
adjudicable teeth — a dispute about whether a project or the corpus is
compliant — it is promoted to a record through the normal drafting process
and this page becomes a pointer.
