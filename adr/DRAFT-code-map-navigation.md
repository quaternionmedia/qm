# ADR-XXXX — Code-map navigation: source-ordered layout, depth-4 hierarchy, view-source

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-06-30 |
| **Pends on** | Nothing — ready to be argued |

## Context

The compound hierarchical layout (dirs → files → symbols) is correct as a
containment map, but a symbol ringed around its file at an arbitrary angle
says nothing about where it sits in the source. A code map needs that
correspondence, and it needs a way from a node back to the line it came from.

Sub-symbols (depth 3: function arguments, struct fields, class attributes, a
module-level call) form a fourth tier. Placed as peers of the depth-2 symbols
around a file, they lose the symbol that contains them, and a drag that moves
a directory with its files and symbols leaves them behind.

## Decision

**§1 — Source-ordered arc layout (Pass 3):** In `compound_layout.py`, sort
each file's symbols by their `line` attribute before placing them, and arrange
them in a 300° arc, clockwise from 12 o'clock, leaving a 60° gap at the
bottom. A symbol's place in its file's cluster then reflects its place in the
source: earlier lines at the top, later lines towards the bottom, so each file
cluster reads as a minimap of the file.

The order is only as good as the `line` a parser records. The C adapter, the
Rust reader, the linker-script reader and the regex-read languages record
each node's line. Python's parser writes `line=0` on every node
(`python_language_parser.py:181`), so a Python file's arc is in the order the
parser emitted its symbols, not source order.

The arcs are the compound layout's, so a reader sees them after choosing that
layout (the default is spring), on a path that lays the whole graph out at
once through the serializer: a parse of uploaded or local files, or a GitHub
repository whose tree is already cached with its content. The live two-phase
GitHub stream lays out only the directories and files; it places each file's
symbols on an even ring around the file, in the order the parser emitted them,
whatever the layout (`unified_parser_service.py:346-372`).

**§2 — Pass 4 (sub-symbol nesting):** A fourth layout pass places depth-3
sub-symbols in the same source-ordered arc around their nearest depth-2
ancestor, at a tighter radius (`max(0.22, √n × 0.14)`). The parent is found by
tracing containment edges (`contains`, `field_of`) up to the nearest depth-2
ancestor. **A sub-symbol with no depth-2 ancestor orbits its file:** a bare
module-level statement — a top-level call or constant with no enclosing
function or class — has nothing at depth 2 to orbit, so Pass 4 places it
around its depth-1 file, just outside the file's own symbol ring, in the same
arc. A sub-symbol with no containment edge at all is matched by its `file`
attribute to the first depth-2 symbol in that file, or to the file itself when
the file has none.

**§3 — Drag moves the whole subtree:** `CompoundLayoutManager
.computeChildrenMap()` builds a transitive map — dir → [files, their depth-2
symbols, their sub-symbols]; file → [depth-2 symbols and their sub-symbols];
depth-2 symbol → [its sub-symbols] — from the containment edges the backend
sends (`contains` or `field_of`, flat as `edge.kind` or nested as
`edge.metadata.kind`). A node with no such edge to a parent in the tier above
is assigned the nearest parent by position. The streaming renderer keeps the
map as `_childrenMap`, and dragging any node moves its whole subtree by the
same delta.

The frontend has no depth-1 tier for sub-symbols. A sub-symbol whose
containment edge comes from its file (a bare module-level statement) or from
another sub-symbol gets no edge-based parent in the depth-2 tier, so it is
grouped with the depth-2 symbol nearest it by position — where the backend
orbits it around its file, or around the depth-2 ancestor it traced.

**§4 — View Source opens the source.** View ▸ Source on the radial menu and a
double-click on a node share one opener. It opens the forge URL at the node's
line when the file came from a forge — for GitHub, the `raw.githubusercontent.com`
URL the node carries becomes a `github.com/…/blob/…#L{line}` URL in a new tab
— and a local-file badge naming the file and line when it did not. With no
line, it opens at the top of the file. It is enabled whenever the node has a
file.

Not yet true at codecartographer 00ce9de, the commit this record was checked
against: View ▸ Source shows a `file:line` toast (`layout_context.ts:739-743`)
and is enabled on `!!node.file` (`:551`), while a double-click opens the forge
or the badge (`streaming_renderer.ts:709-742`) only on a node at depth 2 or
deeper that has a line (`:439-444`).

## Consequences

- The source-ordered arc makes the compound layout navigable as a code map.
  The arc convention (12 o'clock = top of file) is stable across re-renders
  because the line sort is deterministic.
- Sub-symbols exist only when depth 3 is asked for. The parse options offer
  depth 1, 2 or 3 and start at 2 (`layout_context.ts:88`), and the radial
  menu's Expand asks the parser for depth 3. At depth 2 no parser emits
  sub-symbols, and Pass 4 has nothing to place.
- Parent assignment is edge-based, so building the children map is linear in
  the edges; only nodes with no containment edge cost a scan of the tier above
  them.
- One opener means one rule for when the source can be opened, so the two
  gestures cannot disagree about which nodes have a source.

## Alternatives considered

1. **Linear column layout for symbols** (vertical list, line order) rather
   than arc — rejected: the orbit/arc shape matches the compound layout's
   visual language and keeps clear of neighbouring clusters.
2. **A source viewer inside the app** rather than opening the forge —
   deferred: it means fetching and rendering file content, which is
   significant surface area; opening the forge at the line serves the same
   need.
3. **Extend drag to depth 5 and deeper** — deferred: no parser emits depth >
   3. Both the backend and the frontend put every node at depth 3 or deeper in
   the sub-symbol tier, so a deeper parser would be drawn, flattened into it.
4. **Keep two source gestures with different rules** (a toast from the menu, a
   forge link from a double-click) — rejected: a reader who finds the source
   one way expects the other to do the same, and two enabling rules are two
   answers to one question.

## Revision triggers

- A parser emits depth 4 or deeper, and its nodes need their own tier rather
  than the sub-symbol one.
- A sub-symbol is found dragged with a different symbol than it orbits —
  §3's position fallback and §2's tracing disagree on a real graph, and the
  frontend takes the backend's depth-1 rule.
- Python's parser records real line numbers, at which point §1's exception for
  Python is removed.
- The live GitHub stream is made to place symbols by the compound passes, or
  the compound layout becomes the default — §1's scope statement then
  changes.
- A repository arrives from a forge other than GitHub, and the opener needs
  that forge's line-anchor form.

## Amendments

*None.*
