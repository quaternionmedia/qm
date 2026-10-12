# ADR-XXXX — Unify parser/cache architecture around `ParserRegistry` + `batch_whole_tree`

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-06-30 |

## Context

The codebase carries three parallel parsing generations as the frontend
migrated forward, each leaving its predecessor's routers and services
behind instead of removing them: a legacy `ParserService`/`PythonCustomAST`
era, a dedicated libclang C era, and the current unified
`ParserRegistry`-era (`codecarto/services/parsers/language_parser.py`).
`local_repo_router.py`, `parser_router.py`, and `polygraph_router.py` had
zero frontend callers — `polygraph_router.py` was a literally-empty
`APIRouter()` whose documented endpoints never existed in code.

Separately, the unified pipeline's C support is broken in two ways that
make it useless for real multi-file C code:

1. `_walk_folder` dispatches every file to its parser one at a time. Fine
   for Python; structurally broken for C, whose pass 2 (cross-file `CALLS`)
   needs the whole file set in a single call — every cross-file call looks
   unresolved.
2. `CLangaugeParser.parse_files()` requires `File.url` to be a real disk
   path. GitHub-fetched content only ever lives in `File.raw` — so every
   GitHub-sourced repo's C/H files silently parses to an empty graph.

## Decision

- Delete the dead router generations outright (`local_repo_router.py`,
  `parser_router.py`, `polygraph_router.py`, `polygraph_service.py`) rather
  than deprecate them — they have no callers, confirmed by a full
  `web/src/` grep, not just `components/`.
- Add `LanguageParser.batch_whole_tree: ClassVar[bool] = False`, an opt-in
  flag defaulting to unchanged per-file behavior for every existing parser.
  `CLangaugeParser` sets it `True`. When set, `_build_graph`/`_walk_folder`
  collect that parser's files across the *whole* tree (keyed by `id(parser)`,
  not extension — `.c`/`.h` are different extensions but the same parser
  instance) before calling `parser.parse_files()` once.
- Give `CParser.parse_files()` an optional `contents: dict[path_str, text]`
  parameter passed to libclang as `unsaved_files`, so GitHub-sourced content
  with no real disk file parses from memory under a shared virtual root
  (`_VIRTUAL_ROOT`) — libclang's quote-include search needs sibling files
  in the same parent directory to resolve `#include "sibling.h"`; bare flat
  filenames do not reliably resolve even with matching `unsaved_files`
  entries.
- Run the batched, CPU-bound libclang parse via `asyncio.to_thread` inside
  the async streaming pipeline — without this, a single C-heavy repo freezes
  the *entire server* for every concurrent request, not just its own.
- Attribute a batch's nodes to their files by the file's key — `File.url`, or
  `File.name` when there is no url — and by its stem only when a parser wrote a
  stem (the C adapter does). Give a file with no url its place in the tree as a
  `tree://` url before batching, so two files with one name never share a key,
  and an adapter that opens real files never opens one by it. Folder and file
  node ids are the path from the root, for the same reason: every crate in a
  Cargo workspace has a `src/lib.rs`.
- Let a batch parser state what it knows *about files* on its graph's
  attributes — `file_relations` (an edge between a node or a file key and a
  file key: a `mod` declaration, a `use` reaching another file, a linker
  script's `INCLUDE`) and `file_meta` (facts merged into a file node's `meta`) —
  and have the pipeline resolve file keys to the file nodes it created, in the
  in-memory and the streaming paths alike.

## Consequences

- Adding a new `batch_whole_tree` language parser gets cross-file resolution
  by opting into the same flag — no per-language batching logic to reinvent.
  Three use it: C, Rust (`DRAFT-rust-is-read-at-the-item-level.md`) and linker
  scripts, batched separately by parser identity.
- Trade-off accepted: a batched extension's symbols arrive as one burst
  after every file in it is fetched + parsed, instead of trickling in
  file-by-file. There is currently no incremental progress signal during
  that gap — documented as a known limitation, not fixed.
- `has_parse_warning` is deliberately emitted as a top-level node attribute
  (not nested in the unified schema's `meta` dict) in both the unified and
  dedicated C pipelines, since `graph_renderer.ts` reads it directly
  regardless of which backend produced the node — a consistency choice,
  not an oversight.

See `docs/llm/ARCHITECTURE.md` § "C support in the unified pipeline" for
the full technical walkthrough.

## Alternatives considered

1. **Deprecate-and-warn instead of delete** the dead routers — rejected:
   zero callers means zero migration cost, and keeping dead code around
   just obscures which pipeline is actually live for the next reader.
2. **Key batches by file extension** instead of parser identity — rejected:
   `.c`/`.h` are the same parser instance with different extensions, and
   keying by extension splits header/impl pairs into separate batches,
   breaking `#include` resolution.

## Revision triggers

- A batch parser needs facts from another parser's batch — a Rust `extern`
  block naming a function a C file in the same tree defines — which batching by
  parser identity cannot join.
- The "symbols arrive as one burst" limitation becomes a real UX complaint,
  forcing `fetch_and_parse_batch` to support partial/incremental progress.

## Amendments

*None.*
