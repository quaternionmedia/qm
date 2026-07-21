# ADR-XXXX — Compound hierarchical layout (dirs → files → symbols)

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-06-30 |

## Context

The unified graph schema treats directories, files, and symbols as nodes
at depths 0/1/2(/3) in one flat graph. Generic force-directed layouts
(spring, kamada-kawai) treat all nodes as peers, so a directory node and
the dozens of symbols inside its files compete for the same visual space —
there is no layout-level signal that a directory is a *container* for its
files, or that a file is a container for its symbols.

## Decision

Add a custom 4-pass layout (`codecarto/models/custom_layouts/compound_layout.py`,
registered in `position_service.py` as `'compound_layout'`):

1. **Pass 1** — spring layout on the directory-only subgraph. Each
   directory's raw spring position is scaled by `sqrt(N_dirs) * cluster_r *
   1.6`, then further multiplied by `sqrt(dir_weight / avg_dir_weight)`,
   where `dir_weight` is the directory's cumulative descendant count
   (files + symbols + sub-symbols, counted recursively through nested
   subdirectories via dir→dir `contains` edges) — a directory whose
   room-need comes from a deep or wide nested subtree is pushed
   proportionally further from the pack centroid than one with the same
   direct file count but no depth beneath it.
2. **Pass 2** — files orbit their parent directory at
   `max(1.8, sqrt(n_files) * 0.9) + max_child_sym_r` units, where
   `max_child_sym_r` is the largest symbol-orbit radius among the dir's
   files.
3. **Pass 3** — symbols orbit their parent file at
   `max(0.45, sqrt(n_syms) * 0.28)` units, placed in a source-line-ordered
   arc (earliest line at 12 o'clock, clockwise) so the arc reads as a
   minimap of the file.
4. **Pass 4** — sub-symbols orbit their nearest depth-2 symbol ancestor at
   `max(0.22, sqrt(n_subsyms) * 0.14)` units, with the same source-order
   arc convention. A sub-symbol with no depth-2 ancestor at all — a bare
   module-level statement, e.g. a top-level call or constant with no
   enclosing function/class — instead orbits its file directly, at the
   same radius formula pushed just outside the file's real symbol-orbit
   ring so the two rings don't collide.

Parent detection prefers `kind='contains'` edges — the unified schema's
edge-kind field, set by `make_edge()` on every containment edge the
parser emits (including dir→dir edges for nested directories, consumed
by Pass 1's weighting) — falls back to the node's `file` attribute for
symbols, and places true orphans on a fallback ring rather than failing.
The frontend (`compound_layout.ts`'s `CompoundLayoutManager`) resolves
the same dir→file→symbol→sub-symbol grouping from the identical
`contains` edges the backend already sends — nearest-neighbor-by-position
is used only as a fallback for orphan nodes
with no matching edge, the same concept as the backend's own fallback
ring.

## Consequences

- Directory-level spacing accounts for each directory's cumulative
  descendant weight (files + symbols + sub-symbols through nested
  `contains` edges), not just its direct file count — a directory with a
  deep or wide subtree gets proportionally more orbital room from Pass 1
  than a same-position directory with few descendants.
- The frontend and backend both key their dir/file/symbol grouping off
  the same `contains` edges rather than each computing it independently —
  bounding-circle and drag-propagation grouping (`compound_layout.ts`)
  stays structurally tied to the backend's own parent structure; only
  orphan nodes with no matching edge fall back to nearest-neighbor,
  mirroring the backend's own fallback-ring behavior.
- Parent detection is only as good as the `contains` edges a given
  language parser actually emits — a parser that produces a duplicate,
  disconnected depth-1 node for a file (rather than attaching that file's
  top-level symbols to the one depth-1 node the directory walker already
  created and connected) defeats every pass downstream of it for that
  file's entire contents, not just the file itself.

## Alternatives considered

1. **A single global force simulation with custom per-edge weights** (e.g.
   heavier attraction on `contains` edges) — rejected: weight tuning alone
   doesn't produce the "container with orbiting children" visual, it
   produces tighter clusters, not nested ones, and offers no clean way to
   draw a bounding circle around a fuzzy cluster boundary.
2. **Pre-computed treemap-style layout** — rejected for the first pass as
   a bigger algorithmic lift than the orbit approach for comparable visual
   clarity; remains a candidate if orbit spacing proves insufficient at
   scale.

## Revision triggers

- The weighted Pass 1 scaling (`sqrt(dir_weight / avg_dir_weight)`) or the
  axis-stretch constants (1.6, 0.7) produce visibly wrong spacing for a
  repo with an atypical dir/file/symbol ratio (e.g. very few directories
  each with enormous subtrees, or many flat directories with no nesting)
  — revisit the weighting formula or derive the axis constants
  dynamically.
- A future layout needs parent detection that isn't expressible as a
  `contains` edge — revisit whether frontend and backend should keep
  sharing grouping via edges, or need a dedicated serialized field.

## Amendments

*None.*
