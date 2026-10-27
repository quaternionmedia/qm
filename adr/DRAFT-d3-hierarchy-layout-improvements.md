# ADR-XXXX — Hierarchical drag propagation, per-depth labels, and compound layout spread improvements

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-06-30 |
| **Pends on** | Nothing — ready to be argued |

## Context

The compound hierarchical layout (dirs → files → symbols → sub-symbols)
produces a correct four-tier grouping but has three interaction and
visual gaps:

1. **Drag**: directory and file nodes are drawn as cluster containers
   (translucent bounding circles), so dragging one has to take its children
   with it, or the spatial grouping the layout communicates breaks.

2. **Label granularity**: a single global `showNodeLabels` boolean makes a
   reader choose all labels or none. At depth 2 (thousands of symbols in a
   large repo) labels are noise; at depth 0 (a handful of dir nodes) they are
   navigation.

3. **Spread scaling and axis**: a file orbit sized only by
   `sqrt(n_files)` — the number of *direct* file children — ignores how large
   those files' symbol clusters are, so a dir whose files carry many symbols
   gets the same orbit as one whose files are empty, and the symbol clusters
   overlap. An isotropic dir spring layout (no directional bias) makes the
   dir-layer axis and the file/symbol cluster axes indistinguishable.

## Decision

**§1 — Hierarchical drag:** extend `CompoundLayoutManager` in
`compound_layout.ts` with `computeChildrenMap(nodes, edges)` — returns a
Map from parent nodeId to all transitive descendant nodeIds (dir → [files
+ their symbols + their sub-symbols]; file → [its symbols + their
sub-symbols]; symbol → [its sub-symbols]), resolved from the real
containment edges the backend already sends — `kind` of `contains` or
`field_of` (the unified schema's edge-kind field, arriving flat as `edge.kind` or, for gJGF
payloads, nested at `edge.metadata.kind`), with nearest-neighbor-by-position
as a fallback only for orphan nodes with no
matching edge — the same parent-chain helper `computeGroupBounds` uses.
`StreamingGraphRenderer` stores this map as `_childrenMap`, computed when
the compound backgrounds are drawn. Its drag handler computes the
frame-by-frame delta `(dx, dy)` before updating the dragged node's
position, then applies the same delta to every descendant's `x`/`y`, its
SVG element, its edges and its label. There is no simulation on this
canvas, so there are no `fx`/`fy` to pin. Compound background circles are
redrawn on drag end so they follow the moved cluster.

**§2 — Per-depth labels:** add `showLabelsByDepth?: Partial<Record<number,
boolean>>` to `GraphStylingOptions` in `state/types.ts`, which
`control_panel.ts` re-exports rather than copying. When a depth has an
entry, it overrides `showNodeLabels` for that depth; absent entries fall back
to the global flag. The streaming renderer applies this to each label's
`display` style, and `StreamingGraphRenderer.updateStyling()` re-evaluates
every label when either `showNodeLabels` or `showLabelsByDepth` changes.
Graph Settings carries one chip-checkbox per depth: Dir, File, Sym, Sub.

**§3 — Compound layout spread:** in `compound_layout.py`:
- `file_orbit_r(n_files, max_child_sym_r)` adds `max_child_sym_r` (the
  largest symbol-cluster radius among the dir's files) to the base orbit
  radius, so file-cluster bounding circles don't overlap.
- A per-dir `max_child_sym_r` is computed before pass 1, giving each
  directory's pass-2 orbit its own appropriate size.
- The directory spring layout is stretched by `(x_stretch=1.6,
  y_stretch=0.7)` after the spring positions are computed, so the directory
  layer spreads more along the X axis than the Y axis.

## Consequences

- `computeChildrenMap` and `computeGroupBounds` share one
  `_buildParentChain`/`_assignParents` helper, so they cannot assign a
  node to a different parent from each other. Both key off the same
  containment edges `compound_layout.py` reads, so drag groups and
  bounding circles stay tied to the backend's parent structure rather than
  to a second, independently re-derived one. The one place they part is
  a sub-symbol whose edge comes from its file or from another sub-symbol:
  the backend orbits it around its file or its traced depth-2 ancestor, and
  the frontend groups it with the nearest depth-2 symbol by position (see
  *Code-map navigation*, §3).
- `showLabelsByDepth` is not persisted in the saved GL layout (it is part
  of `graphStyling` in Meiosis state, not `LayoutManager.toConfig()`).
  Saved layouts remember panel arrangement but not graph styling, as for
  every other styling option.
- The x/y axis-stretch values (1.6, 0.7) were tuned empirically on a 2-dir
  25-node test graph; they are not derived from first principles. A repo
  with a very different dir/file/symbol count ratio may look noticeably
  asymmetric.

## Alternatives considered

1. **Propagate drag via edges** (walk the `contains` edges at drag time
   rather than pre-computing a children map) — rejected: O(E) edge-walk on
   every mouse-move event is measurably expensive on large graphs; the
   pre-computed map is O(N) computed once, O(K) per drag event where K is
   the number of descendants.
2. **Replace `showNodeLabels` entirely with `showLabelsByDepth`** — rejected:
   the global toggle is still the right default UX for most users; per-depth
   overrides are an additive refinement, not a replacement.
3. **Derive axis-stretch from the dir/file ratio** (e.g. larger stretch when
   dirs outnumber files proportionally) — deferred: the fixed-coefficient
   approach is sufficient for the observed cases; a data-driven stretch could
   be added as a follow-up if the fixed values prove unsuitable at scale.

## Revision triggers

- A future layout emits parent relationships the `contains`-edge
  convention can't express (e.g. a many-to-one or non-tree grouping) —
  `_buildParentChain`'s single-parent-per-node assumption would need to
  change.
- Per-depth label preferences become a frequently-used feature that warrants
  persistence across sessions (add to the saved styling state).
- The axis-stretch values produce obviously wrong layouts for a real
  repo (e.g., all dirs collapsed onto a line or clustered at origin) —
  revisit the stretch coefficients or derive them dynamically.

## Amendments

*None.*
