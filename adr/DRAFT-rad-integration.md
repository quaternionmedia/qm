# DRAFT — adopting rad as this project's radial menu

| | |
|---|---|
| **Status** | Draft |
| **Date** | 2026-08-09 |
| **Pends on** | `quaternionmedia/rad` PR #1; the *rad release milestones* draft naming this project a `v0.0.2` proving consumer |
| **Principle** | P3 seams on standard protocols; P6 decisions documented |

## Context

Two findings from a full review of this repository on 2026-08-09, recorded
here because the fix for both is one decision.

**The interaction layer was attached to a renderer nothing mounts.** Every
path that produces a map of real code — Load Demo, plot repo, plot a single
file, replay from cache, replay a bookmark — renders through
`StreamingGraphRenderer`. Roughly 4,100 lines of radial menu, extensions and
interaction profiles hung off `graph_renderer.ts` instead, reachable only by
loading a Lexicon. `layout_context.ts` re-rendered through the renderer
registry only when `selectedRenderer !== 'd3'`, and the default is `'d3'`.
The capability was built, type-checked, and off the road.

**Graph-node expansion was a placeholder.** `POST /parse/expand` worked,
`PlotService.expandNode` existed with zero callers, `parseDirectory` sat on
the live `GraphState` with a docstring saying it was stored for exactly this
purpose, and the menu's Expand item called `logger.debug('placeholder')`.
`docs/llm/LARGE_REPOS.md` calls node expansion "the core UX feature that makes
the single-large-graph experience work"; `docs/llm/UI_REFERENCE.md`
documented it as shipped. Both cannot be true.

Independently, `quaternionmedia/rad` was created as QM's radial-menu
contract. Its own Context names this project's `radial_menu.ts` as the
motivating defect — *"no keyboard navigation, actions expressed as closures
bound to one renderer, mutations that bypass application state, stubbed edge
actions."* Three of those four are the findings above, reached from the other
direction. The contract's standard node vocabulary already contains `expand`
and `collapse`.

## Decision

Adopt rad as this project's radial menu, and let it carry both fixes.

### §1 Port the core; do not import it

rad's platform-free core is a comment banner inside a 3,333-line
`index.html` — its own open conflict C13 — so there is nothing to import. The
contract asks for a native implementation per platform in any case, sharing
only the contract and the vectors. `web/src/features/graph/rad/core/` is a
TypeScript port of about 250 lines, proven by replaying
`conformance/vectors.json`.

**The pinned vector version is `0.4.0`**, carried in the filename
`web/tests/rad/vectors.v0.4.0.json` so that a bump appears in a diff rather
than inside a constant. Per *version tags are claims*, this pins the vector
line, not a product release — rad has no tag and `package.json` reads
`0.0.0`.

### §2 The boundary is the investment

`rad/core`, `rad/session.ts` and `rad/dom` contain no import that escapes
`rad/`. `rad/host/` is the only half that knows about this application. The
directory is therefore shaped as a package and can be lifted into a shared
`@quaternionmedia/rad-web` the day a second web host wants one — which the
*rad core extraction* draft's alternative 5 names as the right eventual
answer, "if a second implementation consumes it".

This is enforced rather than intended. `scripts/rad-core-lint.mjs` fails the
build when `core/` mentions the DOM or when anything outside `host/` imports
application code, and `tsconfig.rad.json` compiles the core with
`lib: ["ES2020"]` so a stray `document` is a compile error before the grep
runs. **This is the import-boundary check the contract's Conformance clause
§2 requires and the reference implementation cannot run on itself.**

### §3 Conformance is a gate, not a claim

`npm run test:rad` runs the lint, compiles the platform-free half, and
replays every governed vector under `node --test` — no browser, no new
dependency. 23 assertions: 40/40 vectors, the declared constants against the
vector set's own geometry and time blocks, the seam properties the
integration standard asks for, and the §5 host obligations.

Two negative controls, because a check that has never failed is not known to
work: the runner must report red on a corrupted expectation, and it does; and
a deliberately changed core constant must turn the suite red, and it does.

### §4 Intents reach the state layer

Integration standard §5.1. Verbs split in two, and the split is written down
rather than inferred: `hide`, `pin`, `color:*`, `expand`, `collapse` and
`delete` fold into a serializable `NodeViewState` the renderer projects, so
they survive a re-render, a relayout and a cache replay; `fit`, `relayout`,
`spread`, `cluster`, `toggle-physics`, `select-neighbors` and
`clear-selection` are camera and selection operations that own no graph facts
and are applied directly.

An unrouted verb throws. The legacy menu's stubbed actions opened, animated,
committed and did nothing, which from the menu is indistinguishable from
working; a test asserts every verb the resolver can commit reaches a named
operation.

### §5 Vocabulary — extended, not repurposed

Omitted as having no honest meaning for a graph derived from parsing:
`add-node`, `reverse`, `edit-label`. Extended with three declared host verbs:
`view-source`, `node-info`, `focus-group`. The node ring sits at exactly the
contract's 8-item ceiling, with `expand` at index 0 — the 12 o'clock wedge a
straight-up flick reaches — because drill-down is the verb the large-repo
story rests on.

### §6 One divergence, offered upstream as a vector

Integration standard §5.5 requires a divergence to be proposed as a vector
before any code changes. **`cancelScale` is unpinned by the behavioural
suite**: moving it from 1.35 to 1.60 fails no vector, and the undetected
window is `[1.3043, 1.413)`. The cases probe `r_cancel` at r=130/200 against
r1=108 and r=120/130 against r1=92, so none straddles the boundary closely
enough. The contract's own revision triggers say 1.35 "has not been validated
against a human", which makes it the constant most likely to be tuned and
currently the least guarded. Nothing was changed here; a boundary-pair vector
is proposed to rad.

## Consequences

- The rich interaction layer is on the path users take. Deleting the legacy
  `radial_menu.ts` is a follow-up, not this record — it still serves the
  Lexicon path until that is migrated.
- This project becomes a proving consumer of a QM contract, which is a
  standing obligation rather than a one-off: a rad vector bump is now a
  change this repository has to replay.
- Cost accepted: two radial menus exist until the legacy one is retired, and
  the node ring has no spare wedge.
- `docs/llm/RAD_INTEGRATION_HANDOFF.md` is written for the other `v0.0.2`
  consumers and marks its own findings as candidates for the standard.

## Alternatives considered

1. **Fix M1 by deleting the `selectedRenderer !== 'd3'` guard**, so the
   completed stream re-renders through the static renderer. Two lines, and it
   would work. Rejected as the destination rather than as a probe: it keeps
   the callbacks-as-closures shape the contract rejects, discards streaming,
   and buys nothing for any other project. It remains the right *first*
   experiment for anyone sizing this work.
2. **Wait for rad's core extraction (C13) and import a package.** Rejected:
   C13 pends on a human decision about rad's single-file property, `v0.0.3`
   forces it at the latest, and this port is prior art for it rather than
   work thrown away.
3. **Build a bespoke menu against the existing extension system.** Cheaper by
   a day. Rejected: it produces no evidence for anyone else, and the contract
   exists precisely because this project already wrote one bespoke menu whose
   defects it is now paying off.
4. **Adopt only the geometry and state machine, not the seam.** Rejected: the
   seam is the part that fixes M1. Geometry was never the problem.

## Revision triggers

- rad publishes a vector version this port does not replay.
- The core extraction lands and a shared `@quaternionmedia/rad-web` exists —
  §1 and §2 are then wrong and this becomes a dependency record.
- A second web host integrates and needs a shape `host/` assumes is private.
- The node ring needs a ninth verb after honest grouping.
- A human drives the menu on a touch device and the gesture grammar is wrong
  in a way no vector caught — that is a vector, and it is the evidence this
  record is currently missing.

## Amendments

*None.*
