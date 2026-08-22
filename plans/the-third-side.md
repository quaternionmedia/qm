# The third side: codecartographer beside the pair

**What this is.** An analysis of `codecartographer` as read on 2026-08-21, and a
proposed shape for making it the third side of a triangle with `qmcp` and
`dossier`. It decides nothing. The open questions are at the end and several of
them change the plan.

**Stamped against `codecartographer` at `706e49f` on `feat/rad-integration`.**
Every figure below was true at that commit. Re-derive before acting.

---

## What it is today

A development tool that parses source code and draws it as graphs. Three parts:

| part | what it is |
|---|---|
| `codecarto/` | FastAPI backend — 20 language parsers, SSE streaming |
| `web/` | TypeScript front end, Vite, rad ported and mounted |
| *(a private submodule)* | networkx graphs into MongoDB, optional — named by description because this page is public |

**Suite: 328 passed, 27 skipped, 198 seconds.** That last figure is the one
worth holding onto: dossier runs 828 tests in about 220 seconds, so this is
roughly four times the cost per test today, before the growth in the brief.

---

## The stated role, and what follows from it

The brief is that `qmcp` and `dossier` are required to run at all; `codecarto`
is optional but foundationally integrated. `dossier` stays the surface for
debugging and building the core. `codecarto` becomes the layer most people
touch. Its testing gets slower and harder as it grows, so it needs a base that
does not.

Three consequences follow, and they are the design:

**One: optional cannot mean unwitnessed.** A part that may be absent still has
to be *reportable* as absent. The pair already does this — an unreachable
archive is a row with a reason rather than a missing row. codecarto joins as a
source that says whether it is there, not as one whose absence looks like
health.

**Two: the base absorbs the governance so the surface does not.** If codecarto
grows fastest and tests slowest, then every check that can live in the pair
should live in the pair. Work-shape dispatch, spend declaration, attested acts,
the address grammar — these are settled in `qmcp` and `dossier` and should not
be re-decided in a third place at a third speed.

**Three: the slow tests are the ones that must not be the only ones.** A
three-minute suite is run less often than a twenty-second one, and a suite run
less often catches less. The pair's answer this week was to make the cheap
checks structural — reading source and configuration rather than running the
application. That transfers directly.

---

## What I found reading it

### It is on a stacked, unpushed branch

`feat/rad-integration` sits on `cleanup/2026-07-21-full-review`, which is **53
commits ahead of `origin/main` and unmerged**. Its own `HANDOFF.md` says so, and
says the work joins that queue rather than jumping it.

Nothing here is a defect. It is a fact that shapes sequencing: anything proposed
below lands on top of an existing unmerged stack, or waits for it.

### There are two governance checkouts

| path | state |
|---|---|
| `docs/qm` | the registered submodule, pinned to `adr/rad-integration` at `fd9d756` |
| `governance/qm` | **untracked** — a second corpus checkout at `5e1eb04`, dated 2026-08-11 |

Every other repository in the workspace uses `governance/qm`: `dossier`, `qmcp`,
`rad`, `alfred`, `apothecary`, `datum`. codecartographer is the only one using
`docs/qm`, and somebody has since dropped an untracked checkout at the standard
path without wiring it.

`git status` shows `?? governance/`. The submodule pointer is deliberately not
bumped, which the handoff explains and which is correct.

### The rad integration is vector-green and has never been driven

Its handoff is unusually honest about this and the table is worth quoting in
shape: seven rows established by tests and sabotage runs, then three rows
reading **not established** — that rad works in a browser, that expand hits a
live backend, and that the gesture grammar is usable. The third is marked *"and
it is the actual deliverable"*.

This is the same gap the pair spent this week closing from the other side: a
green suite that cannot see whether the thing is reachable. codecarto has the
gap written down and not yet closed.

### It has no seed CI

`docs/qm/project-seed/ci/` has no scripts in this checkout, and `.github/workflows/`
holds `adr-lint.yml` and `copilot-setup-steps.yml` — not the gate set the other
projects run. Whether that is drift or a deliberate lighter footprint is a
question, not a finding.

### Ports collide with the pair's history

codecarto's backend defaults to **8000**. That is the port `dossier` looked for
the harness on for weeks while `qmcp` served 3333 — the mismatch that made the
panel report an absent archive. Three services on one machine is a naming
problem before it is a networking one.

---

## Proposed shape

Four steps, smallest first, each independently useful.

### Step 1 — codecarto becomes a source the panel can see

`dossier.sources` already lists every store this installation reads and marks
which is live: two databases, a config file, the thread archive over HTTP. A
codecarto row joins that list, reachable or not, with a reason when not.

This is the cheapest possible integration and it establishes the shape: optional
and witnessed. It needs no change in codecarto at all.

### Step 2 — the same inward diagnostics, pointed at the third repo

`dossier.diagnostics` is eight checks that read source and configuration. Three
transfer unchanged in spirit:

- **seam agreement** — codecarto's port against whatever the panel looks for,
  the same check that caught 8000-versus-3333
- **documented routes** — its `UI_REFERENCE.md` documents two radial menus; a
  check can ask whether both still exist
- **wiring** — its front end has the same handler-on-the-wrong-class hazard the
  panel had, in a different language

Each is structural, fast, and does not require running a browser or a server.
That is the property that matters given a 198-second suite.

### Step 3 — a work-shape dispatch for map generation

`qmcp.sweep` and `qmcp.orchestration` dispatch by *shape of work*, not by tool.
Parsing 20 languages across many repositories is the same shape: some parses are
mechanical, some need judgement, some are a person's. The dispatcher exists and
is tested; codecarto would supply shares rather than a second dispatcher.

### Step 4 — a demo that shows the triangle

One page, executable, that shows a change moving across all three: the panel
finds it, the harness dispatches it, codecarto shows what it touched in the
graph. Nothing about that requires codecarto to be present for the first two to
work, which is the point of the arrangement.

---

## Questions

These change the plan, so I would rather ask than choose.

**1. Which governance path is canonical for codecarto — `docs/qm` or
`governance/qm`?** Every other repository uses `governance/qm`. codecarto uses
`docs/qm` and has an untracked checkout at the standard path. Moving it is a
submodule change on an already-stacked branch; leaving it makes codecarto the
exception a reader has to remember.

**2. Does the 53-commit `cleanup/2026-07-21-full-review` branch land first?**
Anything proposed here stacks on top of it or waits. Its own handoff says the
rad work "joins that queue rather than jumping it" — I would like to know
whether that is still the intent.

**3. Should the browser gap be closed before integration, or alongside it?**
Three rows of codecarto's own verification table read *not established*,
including the actual deliverable. Integrating on top of unproven ground would
build the triangle on the one side nobody has seen work. But the browser run
needs a person at a browser, which is not something I can do.

**4. What is the port arrangement for three services?** *Answered.*
`ci/dashboard.py` owns the allocation and `uv run qm dashboard` prints it: one
fixed port per surface, each a mathematical constant so nobody has to remember
which is which. The arrangement is not restated here, because a second copy is
what produced the mismatch above.

**5. Is the private graph submodule in scope?** It is a submodule on its own
branch, it wants MongoDB, and MongoDB is a service nobody else in the triangle
needs. Optional-but-integrated may or may not extend to it.

Named by description rather than by name: it is a private repository, and this
page is in a public corpus. `uv run qm private-names` is what noticed, and the
forge confirmed it — the check reads a gitignored companion, so a reader
without that file cannot reproduce the finding and should not have to.

**6. How much of codecarto's suite should the pair be able to run?** The brief
says testing gets slower as it grows. The pair could run codecarto's *structural*
checks cheaply and leave the 198-second suite to CI and to a person — but that
is a policy about who runs what, and it is yours.

**7. Two radial menus: is retiring the legacy one in scope?** codecarto's
handoff says migrating the Lexicon path to rad is "the real task, and it is not
scoped here", and that the standing preference is additive change over
purge-and-replace. Worth knowing whether that holds for this arc.

**8. Where should the demo live?** `dossier/walkthrough` and `qmcp/walkthrough`
each hold executable pages for their own side. A triangle demo spans three
repositories and none of them owns it. The corpus has `walkthrough/` too.
