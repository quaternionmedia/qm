# ADR-XXXX — Wire graphbase as a named bookmark store via /db/bookmarks

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-06-30 |
| **Pends on** | graphbase PR #8 reaching graphbase's `main`: the `/db/bookmarks`, `/db/snapshots` and `/db/history` routes exist only on its branch `fix/graceful-mongo-unavailable`, where this project's pin `b422fc0` sits |

## Context

graphbase (mounted at `/db/*`) stores graphs in `nx.node_link_data` form, and
its graph routes take that form: `POST /db/graph/insert` requires
`{"nodes": [...], "links": [...]}`. The front end holds gJGF
(`{"nodes": {id: {metadata: ...}}, "edges": [...]}`), so keeping whole graphs
there means converting in both directions. And replaying a stored graph needs
a path that does not re-parse, beside a `CacheService` that already keeps a
parse's result for 24 hours.

A reader who wants to come back to a repository needs less than that: the
URL and the settings it was parsed with.

## Decision

Add a `bookmarks` collection in graphbase's MongoDB database with three
routes — `POST /db/bookmarks`, `GET /db/bookmarks`,
`DELETE /db/bookmarks/{name}` — that store lightweight parse-input records,
`{name, url, layout, depth, extensions, saved_at}`, rather than the graph.
Saving under an existing name replaces it. Loading a bookmark re-streams its
URL through `_startStreamFromUrl`, the path a repository fetch takes, so the
graph is re-parsed, and is served from `CacheService` while the cache still
holds it.

The Graphbase panel (`graphbase_panel.ts`) is an addable panel, not in the
default dock, because it needs `MONGODB_URI`. It holds Saved (bookmarks),
Snapshots and History, and shows an "unavailable" state when graphbase is
off. Without `MONGODB_URI`, `/db/` answers `{"available": false, "reason": …}`
and the panel reads that answer.

Not yet true at codecartographer 00ce9de: the Graphbase panel also renders a
Recent list of `CacheService` entries, a second one beside the Repository
panel's; the one Recent list belongs in the Open panel (*Generalize dock
panels into a registry; add a window-add menu*).

## Consequences

- A bookmark costs a few dozen bytes, where a gJGF graph can be hundreds of
  KB.
- Loading re-parses from the source; past the cache's TTL the wait returns,
  and the reader gets a fresh graph. Bookmarks are "names for repositories I
  want to revisit", not "the graph exactly as I saw it."
- A bookmark saves its layout, depth and extensions, and loading it uses only
  the URL: the stream takes the reader's current settings
  (`loadGraphbaseBookmark`, `layout_context.ts:364-370`), although that
  function's docstring says it streams "with the saved settings". The saved
  settings are recorded and not applied.
- "The graph exactly as I saw it" is a snapshot, a separate collection:
  `POST /db/snapshots` stores a graph's flat nodes and edges with its URL,
  layout and node count under a name, and loading one feeds them to the
  streaming renderer without a network call. It does not use
  `/db/graph/insert` or the `node_link_data` form.
- The Graphbase panel is not in `DEFAULT_LAYOUT_CONFIG` by design: in the
  default dock it would show an "unavailable" panel to every reader without
  MongoDB. It is reached through the + menu.

## Alternatives considered

1. **Store full gJGF graphs in graphbase as bookmarks** — rejected for this
   record: a bookmark names what to parse, and a stored graph is a different
   thing with a different cost. Stored graphs are snapshots, above.
2. **Add a "Save to graphbase" action in the panels that start a graph rather
   than a dedicated panel** — rejected: the bookmark list (list, load, delete)
   needs its own surface, and putting it where a graph starts would mix
   keeping graphs with making them.

## Revision triggers

- A reader expects a bookmark to restore its settings — then loading applies
  them, or a bookmark stops saving them.
- The re-stream on load becomes a real complaint for bookmarked repositories
  that are slow to parse, and readers reach for snapshots instead of
  bookmarks.
- A reader wants the Graphbase panel in the default dock, which says graphbase
  is used widely enough to change the default.
- graphbase PR #8 closes without merging, or its branch is deleted — the pin
  and every route this record uses then need a new home.

## Amendments

*None.*
