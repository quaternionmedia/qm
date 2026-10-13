# ADR-XXXX — Adopt rad as this project's radial menu

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-10-13 |
| **Pends on** | Nothing — ready to be argued |
| **Principle** | P3 seams on standard protocols; P6 decisions documented |

## Context

A review of this repository on 2026-08-09 found two defects, and one decision
fixes both.

**The menu was mounted on a canvas the code-map paths did not draw on.** Every
repository plot streamed through `StreamingGraphRenderer`, while the radial
menu, its extensions and its interaction profiles hung off a second D3
renderer, `graph_renderer.ts`, that a reader reached only by loading a Lexicon.
A capability that is built and type-checked but mounted where readers are not
is not available to them.

**Graph-node expansion was a placeholder.** `POST /parse/expand` worked,
`PlotService.expandNode` had no caller, `parseDirectory` sat on the live
`GraphState` with a docstring saying it was kept for exactly this, and the
menu's Expand item logged a placeholder. Expansion is what makes a large
repository readable as one graph.

`quaternionmedia/rad` is QM's radial-menu contract. Its interaction contract's
Context names this project's `radial_menu.ts` as the motivating defect — *"no
keyboard navigation, actions expressed as closures bound to one renderer,
mutations that bypass application state, stubbed edge actions."* Three of those
four are the findings above, reached from the other direction. The contract's
standard node vocabulary contains `expand` and `collapse`. rad's *release
milestones* draft names this project a `v0.0.2` proving consumer: one of the
hosts whose integration is the evidence that the contract survives contact with
code `rad` does not control.

## Decision

Adopt rad as this project's radial menu, and let it carry both fixes.

### §1 Port the core; do not import it

rad's platform-free core is a comment-delimited section of its single-file
`index.html`, and the *rad core extraction* draft that would make it a module
is Proposed, pending a decision on the single-file property. So there is
nothing to import. The contract asks for a native implementation per platform
in any case, sharing only the contract and the vectors.
`web/src/features/graph/rad/core/` is a TypeScript port, proven by replaying
rad's `conformance/vectors.json`.

**The pinned vector version is `0.0.1`**, carried in the filename
`web/tests/rad/vectors.v0.0.1.json` so that a bump appears in a diff rather
than inside a constant; `tests/rad/conformance.test.mjs` asserts that the file
it loads declares the version it pins (`PINNED = '0.0.1'`). Per *version tags
are claims*, this pins the vector line, not a product release — rad has no tag
and its `package.json` reads `0.0.0`.

### §2 The boundary is the investment

`rad/core`, `rad/session.ts` and `rad/dom` contain no import that escapes
`rad/`. `rad/host/` is the only half that knows about this application. The
directory is therefore shaped as a package and can be lifted into a shared
`@quaternionmedia/rad-web` the day a second web host wants one — which the
*rad core extraction* draft's alternative 5 names as the right eventual
answer, "if a second implementation consumes it".

The boundary is checked, not only intended. `scripts/rad-core-lint.mjs` exits
non-zero when `core/` mentions the DOM or when anything outside `host/` imports
application code, and `tsconfig.rad.json` compiles the core with
`lib: ["ES2020"]` so a stray `document` is a compile error before the grep
runs. **This is the import-boundary check the contract's Conformance clause
§2 requires and the reference implementation cannot run on itself.**

The clause asks for that check in CI, and this project does not meet it yet.
Both halves run in `npm run test:rad`, and no workflow on codecartographer's
`main` runs it: `pytest.yml` runs the Python suite and nothing under `web/`.
codecartographer #119 adds `web.yml`, whose `suites` job runs `test:rad`; until
it merges, the boundary holds only when someone runs the suite.

### §3 Conformance is a gate, not a claim

`npm run test:rad` runs the lint, compiles the platform-free half, and replays
every governed vector under `node --test` — no browser, no new dependency. It
asserts every case in the pinned vector file against this port, reporting a
case the port cannot execute as not applicable with its reason rather than as a
pass; the declared constants against the vector set's own geometry and time
blocks; the seam properties the integration standard asks for; and the §5 host
obligations.

Two negative controls, because a check that has never failed is not known to
work. The runner must report red on a corrupted expectation, and a test in the
suite corrupts one and asserts that it does. A changed core constant must turn
the suite red, and the constants check compares every value in the vector
set's geometry and time blocks with the port's own.

### §4 Intents reach the state layer

Integration standard §5.1. Verbs split in two, and the split is written down
rather than inferred: `hide`, `show-hidden`, `pin`, `color:*`, `expand`,
`collapse` and `delete` fold into a serializable `NodeViewState` the renderer
projects, so they survive a re-render, a relayout and a cache replay; `fit`,
`relayout`, `spread`, `cluster`, `toggle-physics`, `select-neighbors`,
`clear-selection` and `focus-group` are camera and selection operations that
own no graph facts and are applied directly. `view-source`, `node-info` and
`compare` leave the canvas.

A relayout re-streams the same graph and remounts the menu. The remount tells
the same graph arriving again from a new plot target: view state is carried
across the first, keyed on node ids, and the second starts clean.

An unrouted verb throws. A stubbed action opens, animates, commits and does
nothing, which from the menu is indistinguishable from working; a test asserts
every verb the resolver can commit reaches a named operation.

That test sits at the `GraphOps` boundary, so it sees which operation fired and
never what the operation does: op bodies are application code and never enter
the conformance build. Three verbs wired to one `fitView()` would pass it. So
the rule is stated where a test can hold it: **a capability this host does not
have is offered disabled, never substituted.** `spread`, `cluster` and
`toggle-physics` keep their wedges and come back `enabled: false` on a canvas
with no client-side layout and no simulation, and a test asserts exactly that.
`focus-group` frames the node and its subtree, not the whole graph.

A disabled wedge is not a dead control. A control that looks enabled and does
nothing is removed; a wedge whose capability this host lacks stays, disabled,
so the other wedges keep their places and the menu says what the canvas cannot
do.

### §5 Vocabulary and rings — extended, not repurposed

Omitted as having no honest meaning for a graph derived from parsing:
`add-node`, and the edge vocabulary (`delete`, `reverse` and `edit-label` on an
edge), because a node or an edge here is a fact about the code. This host
offers no edge ring.

Extended with four declared host verbs: `view-source`, `node-info`,
`focus-group`, and `compare`, which opens the chrestomathy at what a node is —
the construct the vocabulary placed it as, beside every language that writes
it — and is offered disabled on a node the vocabulary did not place. All four
sit under View, so the node ring sits at exactly the contract's 8-item ceiling,
with `expand` at index 0 — the 12 o'clock wedge a straight-up flick reaches —
because drill-down is the verb the large-repo story rests on.
`show-hidden` and `clear-selection` are not in the contract's §1 lists; the
reference implementation's own rings use them, and this host uses them in the
same sense.

The rings:

- **node:** `expand`, `collapse`, `select-neighbors`, `pin`, a colour submenu
  of palette tokens, View (`view-source`, `node-info`, `compare`,
  `focus-group`), `hide`, `delete`.
- **canvas:** `fit`, `relayout`, `spread`, `cluster`, `toggle-physics`,
  `show-hidden`, `clear-selection`. No colour: a canvas intent names no node,
  so a colour committed there has no target. **Deselect is reachable from the
  canvas ring.**
- **selection:** `expand`, `select-neighbors`, `spread`, `cluster`, colour,
  `hide`, `clear-selection`, `delete`.

**View ▸ Source and a double-click on a node share one opener.** It opens the
forge URL at the node's line when the file came from a forge, and a local-file
badge naming the file and line when it did not; with no line, it opens at the
top of the file. It is enabled whenever the node has a file.

Not yet true at codecartographer 00ce9de, the commit this record was checked
against:

- View ▸ Source shows a `file:line` toast (`layout_context.ts:739-743`), and a
  double-click opens the forge only on a node at depth 2 or deeper that has a
  line (`streaming_renderer.ts:439-444`).
- The canvas ring opens only when nothing is selected
  (`rad_extension.ts:106-115`), so its Deselect is never enabled, and it still
  offers colour.
- `resolve.ts` still builds an edge ring that no context opens.

The chord vocabulary (`CHORD_MAP` in `host/vocabulary.ts`) is defined and
tested — prefix-free, and every chord-bound verb reachable in the menu, as
integration standard §5.3 asks — and no input handler reads it, so no chord
commits a verb.

### §6 One divergence, offered upstream as a vector

Integration standard §5.5 requires a divergence to be proposed as a vector
before any code changes. **`cancelScale` was unpinned by the behavioural
suite**: moving it from 1.35 to 1.60 failed no vector. The two `r_cancel`
probes at `r1=108` bounded it loosely, and the two at `r1=92` carry their own
`geom` override, so they constrain the default not at all. The contract's own
revision triggers say 1.35 "has not been validated against a human", which
made it the constant most likely to be tuned and the least guarded.

Nothing was changed here; a boundary-pair vector was proposed to rad, and rad
applied it. The pinned vector file carries the pair — at `r1=108`, a release at
`r=145.7` commits and one at `r=145.9` cancels — so `cancelScale` is pinned in
this port's replay.

### §7 One D3 canvas, and the ring is mounted on it

`StreamingGraphRenderer` is the only D3 canvas. The registry's `d3` renderer
(`d3_renderer.ts`) hands a finished graph to a `StreamingGraphRenderer` through
`mergeGraph`, and every canvas, streamed or handed over, announces itself
through `GraphSurface`. The radial menu and the legend subscribe there, so
every D3 graph gets the same menu and the same key, whichever path drew it. The
renderer registry keeps three renderers that draw with something other than a
D3 canvas — gravis on vis-network, the notebook iframe, and the system diagram
— and choosing one of them means no radial menu.

**The legend is an extension**, `LegendExtension`, mounted on the same
`ExtensionContext` as the menu, so it reaches anything that supplies one.

**Layout: the depth ring is accepted, and instrumented rather than argued
about.** `StreamingGraphRenderer` has no force simulation. A node that arrives
without coordinates is placed on a ring by its depth, and each new node gets a
one-shot collision nudge. That trade holds only while nothing reaches the
fallback, and two checks say whether anything does:
`tests/test_positions_are_guaranteed.py` walks the gJGF routes and asserts that
every node they serve carries `x` and `y`, failing as well if every route
skipped; and a streamed plot's status line names how many nodes the renderer
placed itself. `position_service.ensure_positions` is the call for a route that
builds a gJGF by hand. Nothing calls it, and the test says so.

**What the one canvas leaves standing.** `ExtensionRegistry`,
`graphExtensions` and the six D3 extensions (drag, selection, zoom, highlight,
tooltip, colour) have no importer outside `extensions/`: the streaming renderer
carries its own drag and zoom, titles its own nodes, and takes colour through
rad's view state. `BaseExtension` and `ExtensionContext` stay, because rad and
the legend mount on them. Deleting the six is a separate change and is not
decided here.

## Consequences

- There is one radial menu. The legacy `radial_menu.ts`, `graph_renderer.ts`
  and the `interaction_manager.ts` only it imported are deleted
  (codecartographer 0eb0417).
- This project is a proving consumer of a QM contract, which is a standing
  obligation rather than a one-off: a rad vector bump is a change this
  repository has to replay.
- Cost accepted: the node ring has no spare wedge.
- Cost accepted: a graph drawn by gravis, the notebook or the system renderer
  has no radial menu.

## Alternatives considered

1. **Re-render every completed stream through `graph_renderer.ts`**, by
   deleting the `selectedRenderer !== 'd3'` guard, so its bespoke menu reached
   repository plots. Two lines, and it would have worked. Rejected as the
   destination rather than as a probe: it keeps the callbacks-as-closures
   shape the contract rejects, discards streaming, and buys nothing for any
   other project.
2. **Wait for rad's core extraction and import a package.** Rejected: the
   extraction pends on a human decision about rad's single-file property,
   `v0.0.3` forces it at the latest, and this port is prior art for it rather
   than work thrown away.
3. **Build a bespoke menu against the existing extension system.** Cheaper by
   a day. Rejected: it produces no evidence for anyone else, and the contract
   exists because this project already wrote one bespoke menu whose defects it
   then had to pay off.
4. **Adopt only the geometry and state machine, not the seam.** Rejected: the
   seam is what puts the menu on the canvas every path draws. Geometry was
   never the problem.

## Revision triggers

- rad publishes a vector version this port does not replay.
- The core extraction lands and a shared `@quaternionmedia/rad-web` exists —
  §1 and §2 are then wrong and this becomes a dependency record.
- A second web host integrates and needs a shape `host/` assumes is private.
- The node ring needs a ninth verb after honest grouping.
- A human drives the menu on a touch device and the gesture grammar is wrong
  in a way no vector caught — that is a vector, and it is the evidence this
  record is missing.
- A streamed plot's status line reports nodes placed without backend positions
  on a path anyone uses — §7's trade stops being free and a force pass is owed.
- A second renderer draws on a D3 canvas — §7's one-canvas rule then needs
  restating.

## Amendments

*None.*
