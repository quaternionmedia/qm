# ADR-XXXX — `CacheService` and `graphbase` stay separate stores, not one merged cache

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-06-30 |
| **Pends on** | Nothing — ready to be argued |

## Context

Two graph stores exist in this codebase and, on a first read, look redundant:

- **`CacheService`** (`codecarto/services/cache_service.py`) — a
  filesystem-first, content-addressed cache. A graph's key is
  `{repo_key}::{hash}`, where `hash` is
  `sha256(url :: mode :: layout :: sorted(extensions))[:16]`, and an index of
  graph entries, newest first and capped at 50, backs the UI's Recent list.
  Its job is "don't reparse or refetch what has already been seen."
- **`graphbase`** (the `graphbase` submodule, mounted at `/db/*` when
  `MONGODB_URI` is set) — a store of things a reader chose to keep: named
  graphs with full CRUD (`POST /graph/insert`, `GET /graph/{name}`,
  `GET /graphs`, `DELETE /graph/{name}`, plus node- and edge-level
  operations), named bookmarks, named snapshots, and per-URL render history.
  Its job is "keep this graph, under a name I chose, until I delete it."

When `MONGODB_URI` is set, `CacheService` keeps its Mongo copy in a
`graph_cache` collection of graphbase's database, reached through graphbase's
`get_db()` (one `MongoClient`), and falls back to its own `pymongo` client
when the submodule cannot be imported. The two systems share infrastructure,
and that shared plumbing is what makes "just merge them" look tempting.

## Decision

Keep them as two separate abstractions sharing one Mongo database, rather
than merging into a single keyed store:

- `CacheService` entries are derived and disposable — the key is a hash of
  parse *inputs*, not a name a person chose, and the 50-entry index cap plus
  TTL (`CC_CACHE_TTL`, default 24 h) assume anything in it can be regenerated
  by re-running the same parse.
- `graphbase` entries are intentional — a name the reader picked or a history
  the reader turned on — and leave only by explicit `DELETE` or by the rule
  of the collection the reader chose.

These are different lifecycle contracts. Forcing them through one keyed store
would mean either giving cache entries TTL-defeating permanence, or giving
saved entries surprise eviction.

## Consequences

- The front end reaches graphbase through `web/src/services/graphbase_service.ts`
  — bookmarks, snapshots and history over `/db/*` — and reaches the cache over
  `/parse/cache`. The two meet in the UI, not in a store: a Recent entry is a
  `CacheService` entry, and promoting one to a bookmark writes a new graphbase
  record from its URL.
- Anyone adding a "keep my graph" feature reaches for `/db/*`, not a no-TTL
  mode of `CacheService` — the moment a cache entry needs to survive eviction
  by a reader's intent, it has become a graphbase entry.
- graphbase's `history` collection is the one with cache-like eviction. When a
  reader turns on history tracking (off by default), each finished stream
  appends its nodes and edges under the URL's hash, and graphbase prunes each
  URL to its newest 20 entries on append. It is derived, as a cache entry is,
  and kept by the reader's choice to track, as a saved entry is.
- Without `MONGODB_URI`, `/db/` answers `{"available": false, "reason": …}`
  and every other `/db/*` route is unmounted; `CacheService` stays on the
  filesystem, and Recent works without MongoDB.

## Alternatives considered

1. **Merge into one Mongo collection with a `kind` discriminator field**
   (cache vs. saved) — rejected: the eviction/TTL logic and the
   naming/addressing logic are different enough that a discriminator field
   would mostly stand in for two services already separated by their HTTP
   surface (`/parse/cache*` vs `/db/*`).

## Revision triggers

- A feature has to list or look up entries across both stores by one key — a
  Recent entry beside the snapshots and history of the same URL, say — which
  is the shared-key question this record leaves open. (The two use different
  keys: `CacheService` keys a GitHub repo by `{owner}-{repo}`, and graphbase's
  history by `sha256(url)[:16]`.)
- History tracking becomes the usual way a reader revisits a graph — the line
  between a derived store and a kept one then needs drawing again.
- A third graph store is proposed, forcing a decision about whether this
  pattern (separate stores, one database) generalizes or breaks down.

## Amendments

*None.*
