# Perspective — The Web Window's First Slice, and What Measured the Scaffolding

| | |
|---|---|
| **Standing** | Perspective — non-binding, attributed, dated. Not a record; never ratified; cite by author and date. |
| **Author** | Peter Kagstrom |
| **Tools** | Claude Opus 5 (1M context), driving the session; six subagents of the same model in one orchestrated pass, three writing and three briefed to refute |
| **Task** | One session asked for a recap of codecartographer in its family, a triage of its documents, and a plan for growing it into the estate's front end; the plan was written and its first slice built across five repositories. This is why it went the way it did: the assumptions that were wrong first, the defects the session caused as well as the ones it found, and for each the check that would have caught it and whether that check now exists. |

## 0. Standing and evidence

One workstation, git 2.37, the clones under `repos/qm/`, every branch built in
a worktree under the session's scratchpad because another session was
committing in the `qm` clone the whole time. Commits are stamped in
`handbook/handoffs/the-web-window.md`; every figure here is one run at that
stamp.

- **E1** — directly observed: a command and its output.
- **E2** — read from the repositories.
- **E3** — inference, marked where it appears.

## 1. The shape of the session

The brief was three things in order — recap, triage, plan — and the plan was
answered in nine decisions before anything was built. What followed was one
slice in five repositories: the estate frame in codecartographer, the routes a
designer needs in qmcp, the harness routes documented and a topics document in
looksatwords, a proposal in rad, and the plan itself in this corpus with a
fourth port allocation.

The interesting part of the day was not the work. It was how many times a
check reported on the scaffolding around it rather than on the thing it named,
and how the same failure wore five different faces.

## 2. The false assumptions, in the order they were found

### 2.1 `git checkout -- <file>` restores a file

It restores a *tracked* file. The first mutation ritual of the day ran against
`estate_service.py` before it had ever been committed: the mutation was
applied, the test went red (E1), `git checkout` printed an error to a stream
the script was not reading, and the "restored" run reported the same red as
the mutated one. Three mutations stacked in the file. The ritual was reporting
its own scaffolding — and doing so in a way that *looked like* the mutations
were being seen red, which is the property that makes this class of failure
dangerous. The second mutation of a tracked file then restored a *different*
uncommitted edit to the file's committed state, silently discarding it.

The rule that came out: **commit before you mutate.** The test's docstring
carries the episode. The check that would have caught it — asserting the tree
is clean after each restore — is now in the ritual as a printed dirty-count
(E1), which is a habit rather than a gate.

### 2.2 A green `tsc` means the compiled test tested the new code

`tsconfig.pure.json` still named the old path of a moved file. `tsc` compiled
nothing new, `dist-pure/` kept the previous output, and the node suite passed
19 of 19 against stale JavaScript (E1). Deleting `dist-pure/` before the run
turned the stale green into a real one. No check catches this today; the
`build:pure` script could `rm -rf dist-pure` first, and should.

### 2.3 A source directory can be named anything

`web/src/estate/` was requested by the browser as `/estate/...`, and `/estate`
was the API prefix the dev server had just been told to proxy to the backend
(E1: five 404s in the console, the application never mounted, seventeen
browser tests waiting on a button). The proxy was doing exactly what it was
told. The module moved under `features/`, and
`tests/test_docs_routes.py::test_no_source_directory_is_shadowed_by_the_dev_proxy`
fails on the shape now (E1, seen red on an empty `web/src/estate/`).

### 2.4 The onboarding modal "reappears"

`docs/consolidation.md` recorded that the modal comes back after a panel is
opened and intercepts clicks. It never came back. It arrived *late*:
`maybeShowFirstTime()` ran at the end of the shell's `oncreate`, after four
awaited network probes, so on a first visit it opened seconds after the page
did, over whatever the reader had started (E2, `golden_layout_shell.ts`). It
now opens first and closes on Escape. The test helper then had to change too:
it pressed Escape and re-counted the backdrop in the same tick, found it still
present (Mithril redraws asynchronously), and went hunting for a `×` that had
just been removed. Nine browser tests waited thirty seconds each for it (E1).
The helper now waits for the backdrop to detach. Two false readings of one
modal, and the second was caused by fixing the first.

### 2.5 `item.focus()` shows a panel

Golden Layout's `ComponentItem.focus()` marks the item focused and leaves the
stack's active tab alone; `Stack.setActiveComponentItem` is what shows one tab
and hides the rest (E2, the typings). And before that could matter, the
default layout's Graph entry had no `id`, so `findFirstComponentItemById('graph')`
found nothing and the focus was a no-op — which also meant re-opening the
canvas would have added a second one. Found by a debug spec that dumped the tab
states rather than by reasoning about them (E1: `◈ Graph:inactive`), after two
guesses had failed. Guess twice, then measure.
`test_every_default_layout_entry_carries_its_registry_id` now fails on an
id-less entry (E1, seen red).

### 2.6 `--offline` regeneration leaves the other documents alone

`generate_docs.py --offline` rewrote `status/gates.yaml` to say the host was
not asked (E1: `unknown: --no-host was passed`), replacing a real answer with
an honest absence. The generator warned that a rewrite you did not expect is a
finding, and it was. Those files were restored and only the document index
that names the new plan was kept. Nothing catches this except reading the
diff, which the generator asks you to do.

### 2.7 A heredoc carries an escape sequence

A Python edit script with a literal `\n` inside a string, passed through a
shell heredoc, broke the shell before Python ran (E1). This is already a
recorded lesson in this workstation's notes and it recurred; the fix — write
the script to a file and run it — is what the note says. The recurrence is the
finding.

### 2.8 `isdigit()` is `int()`'s test

An adversarial reviewer of qmcp #36 saved a design named `²`. `'²'.isdigit()`
is True; `int('²')` raises; every read of that design was a 500 (E1, the
reviewer's transcript). The gate is now what `int` accepts, and the test was
seen red against the original gate. Nobody who wrote the code would have tried
that input; the reviewer's brief was to refute, and it did.

### 2.9 A guard at the root guards the tree

rad's proposal placed the authored-only refusal at `openAt`. The reviewer
nested `Reverse` under an `Edit` submenu over a derived graph and committed it
from one level in (E1). The core already asserts its ceiling at `enterSub` as
well; the proposal now says *wherever a ring is asserted*, and carries the
nested case as a candidate vector. A guard is not finished until someone has
tried to route around it — this corpus's rule, and it held.

### 2.10 A `Mount` is a route; a table row is a table row

looksatwords' new doc-vs-code guard compared `APIRoute`s against table rows
whose path sat in backticks. The reviewer mounted a sub-application under
`/api/harness/hidden` (invisible to both directions) and wrote a row without
backticks (rendered for a reader, skipped by the pattern); the guard stayed
green through both (E1). Two tests now refuse each shape, each seen red.

### 2.11 The layout was chosen, and the canvas did not change

Asked why a layout chosen in Graph Settings was not respected on an estate
graph. Three causes, none of them the one a reader would guess:

- A layout change re-runs *the last plot action*, and only the code-map paths
  ever set one. An estate draw was never remembered, so the setting changed
  and nothing re-drew (E2, `layout_context.ts`). Every panel that draws now
  goes through `plotWith`.
- Two hand-written tables translated the menu's names to the backend's, and
  both fell back to `Spring` for any name they did not list — `compound_layout`
  among them (E2). One rule, no fallback.
- The serializer normalised the name for the lookup and compared the raw
  string for its spread constant, so `Kamada_Kawai` came out five times larger
  than `Kamada Kawai` (E1: x-range −400..363 against −80..73 on the same graph),
  and an already-suffixed name raised through the route as a 500 (E1).

The same probe found `sorted_square_layout` presuming a `type` on every node —
a position calculation that assumed a styling attribute — and three hex colours
riding in the topology metadata that the front end overwrote on arrival.

### 2.12 A stamp set in one place and dropped in the next

dossier's seam gained `generated_at`; the test pinned it and passed; the real
seam came out with `generated_at: ""` (E1). `build` stamps the picture and
`_redact_private` rebuilds it field by field, without the new field — and the
test's fixture had no private project, so it never crossed that branch. The
check that would have caught it is the one that now exists: the test adds a
private project. The lesson is §2.1's in another coat: a green test proves the
path its fixture walks, and the fixture is scaffolding.

### 2.13 Where a figure is calculated, stored and displayed

The review that produced §2.11 also wrote the boundary down —
`docs/architecture.md`, *Calculated, stored, displayed* — because every one of
these was a figure or a constant in the wrong layer: a display constant in a
data document, a calculation keyed on a caller's spelling, a panel guessing at
a producer's shape. `tests/test_boundaries.py` is the check; its docstring says
what it cannot see.

### 2.14 Seven pull requests in which the contributor talked to himself

Every pull request body this session opened began "**Not to be merged without
your click** — assigned, no review requested", and one said a change was
"worth your eye". Posted under the contributor's account, that is the
contributor telling himself not to merge his own work (E1: the host shows the
body as his comment). The words were his instruction to the tool — *"PRs are
fine, nothing pulled to main without my manual click"* — carried out of the
session and into an artefact he signs. He had said this before, more than once.

The false assumption: that a pull request body is the session's report to the
reviewer. It is not. It is the reviewer's statement of the change to everyone
else; the session's report to the reviewer is the session. `async-contract.md`
§3 already said a body states decisions and not questions, and this is the
same rule from the other side — it states them in the contributor's voice.

The check that would have caught it did not exist and now does:
`project-seed/ci/check_pr_voice.py`, a step in `one-pr-check.yml`, refuses the
second person and the handling phrases that leaked, and says what it cannot
see (the third person). Clause 5 of `DRAFT-human-only-contributorship.md` is
the decision; `AGENTS.md` item 3 and the seed's restate it. The seven bodies
were rewritten in place.

## 3. Defects this session caused

- **The stacked mutations** (§2.1) — a false "seen red" report that was true
  by accident: each mutation *had* gone red, but the restoration was fiction.
- **The lost edit** (§2.1) — `git checkout` on a tracked file discarded the
  `remedy_404` change that had not been committed; the test caught it on the
  next run as a `TypeError`, and the change was re-applied.
- **The helper's assumption** (§2.4) — fixing the modal broke every browser
  test that dismissed it, for one run.
- **Two wrong guesses at focusing a tab** (§2.5) before measuring.
- **A commit that swallowed staged deletions.** `git commit` after `git add
  <paths>` commits the whole index, and the deletions had been staged by `git
  rm` earlier; the frame commit carried them. Recut with `reset --soft`. The
  audit record is the reason to care.
- **Seven pull-request bodies addressed to the contributor**, under his name (§2.14).
- **A pull-request footer that was a byline.** The tool's default attribution
  line went into #100's body; the house form is a `Tools:` note, as #115
  shows. Replaced.
- **`-c core.editor=true` passed to git once**, to finish a cherry-pick without
  an editor. The workstation's note says never pass `-c` to git in either
  direction. It changed nothing about signing (E1: the commit is `G`), and
  `GIT_EDITOR=true` is the form that does not touch git's own configuration.

## 4. What the adversarial pass was worth

Three implementers, three refuters, in one orchestrated pass — roughly an hour
of wall clock and a million tokens (E1, the run's usage). The refuters found
§2.8, §2.9 and §2.10, plus a citation overreach in the rad record and the fact
that looksatwords' port test passed only because a sibling worktree's
*uncommitted* file happened to be beside it. Every one of those was real and
none was found by the implementer. The pass was worth its cost because the
brief was *refute*, not *review*: a reviewer asked to find problems finds the
problems the author would have found; one asked to walk past a guard finds the
ones the author could not.

## 5. The check that would have caught each, and whether it exists

| Finding | Check | Exists |
|---|---|---|
| stacked mutations on an untracked file | tree clean after restore | as a printed count in the ritual, not a gate |
| stale `dist-pure` | build from nothing | no; `build:pure` should remove the directory first |
| source directory shadowed by the proxy | `test_no_source_directory_is_shadowed_by_the_dev_proxy` | yes, seen red |
| modal arriving late | `_identity.spec.ts` + the helper's detach wait | the helper waits; nothing asserts the modal is present *at load* |
| id-less default entry | `test_every_default_layout_entry_carries_its_registry_id` | yes, seen red |
| offline regeneration degrading a document | reading the diff | the generator's own sentence; no gate |
| `isdigit` vs `int` | `test_a_name_of_unicode_digits_is_a_name_and_not_a_crash` | yes, seen red |
| root-only guard | a candidate vector for the nested case | proposed, not applied |
| Mount / backtick-less row | two tests in `test_api_reference.py` | yes, seen red |
| documents naming a retired port, a stale count, a missing route | `tests/test_docs_routes.py` | yes, seen red on the unrepaired tree |
| the seed's slot workflow on a project with a private submodule | none; the workflow itself is the check and it could not check out | the project's copy departs from the seed; the seed is unchanged |
| a layout's spread keyed on spelling; an already-suffixed name raising | `test_a_layout_is_one_calculation_however_it_is_spelled`, `test_the_menus_own_registry_names_lay_out` | yes, seen red |
| a layout change not re-drawing an estate graph | a browser test watching the re-draw request | yes, seen red with `plotWith` removed |
| display constants in a data document; a service that persists; a panel that stores | `test_boundaries.py` | yes, each seen red |
| a stamp dropped by a rebuild the test never crossed | the test walks the redacting path | yes, seen red |
| a pull-request body addressed to the contributor under his own name | `check_pr_voice.py` in `one-pr-check.yml` | yes, seen red four ways |

The last row is the one that matters most going forward: the seed's
`one-pr-check.yml` cannot run in any project that vendors a private submodule,
and codecartographer is the first to carry it. It reads as a configured gate
and had never executed a line.

## 6. What this changes about the next slice

Phase 2 of the plan draws a live flow on a topology's shape. Everything in §2
says: start with the fixture that reports bad (a harness whose invocations
carry an address no box has), commit the fixture before mutating anything,
and put the browser on a tab you have measured is active. The rest is drawing.
