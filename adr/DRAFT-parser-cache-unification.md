# ADR-XXXX — Unify parser/cache architecture around `ParserRegistry` + `batch_whole_tree`

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-06-30 |
| **Pends on** | Nothing — ready to be argued |

## Context

Three parsing generations sat side by side as the frontend moved forward,
each leaving its predecessor's routers and services behind: a legacy
`ParserService` generation, a dedicated libclang C generation, and the unified
`ParserRegistry` generation (`codecarto/services/parsers/language_parser.py`).
`local_repo_router.py`, `parser_router.py` and `polygraph_router.py` had no
frontend caller, and `polygraph_router.py` was an empty `APIRouter()` whose
documented endpoints never existed in code.

Separately, the unified pipeline's C support was broken in two ways that made
it useless for real multi-file C code:

1. `_walk_folder` dispatched every file to its parser one at a time. Fine for
   Python; structurally broken for C, whose pass 2 (cross-file `CALLS`) needs
   the whole file set in a single call — every cross-file call looked
   unresolved.
2. `CLangaugeParser.parse_files()` required `File.url` to be a real disk path.
   GitHub-fetched content lives only in `File.raw`, so every GitHub-sourced
   repository's C/H files parsed to an empty graph.

## Decision

- Delete the dead router generations outright (`local_repo_router.py`,
  `parser_router.py`, `polygraph_router.py`, `polygraph_service.py`) rather
  than deprecate them — they had no callers, confirmed by a full `web/src/`
  grep, not just `components/`.
- **A parser opts into batching by declaring
  `batch_whole_tree: ClassVar[bool] = True`.** The pipeline reads it with
  `getattr(parser, "batch_whole_tree", False)`, so every parser that does not
  declare it keeps per-file dispatch; the `LanguageParser` Protocol does not
  name it. When it is set, `build_graph`/`_walk_folder` collect that parser's
  files across the *whole* tree, keyed by `id(parser)` and not by extension
  (`.c` and `.h` are different extensions but one parser instance), and call
  `parser.parse_files()` once.
- Give `CParser.parse_files()` an optional `contents: dict[path_str, text]`
  parameter passed to libclang as `unsaved_files`, so GitHub-sourced content
  with no disk file parses from memory under a shared virtual root
  (`_VIRTUAL_ROOT`) — libclang's quote-include search needs sibling files in
  the same parent directory to resolve `#include "sibling.h"`; bare flat
  filenames do not reliably resolve even with matching `unsaved_files`
  entries.
- Run the batched, CPU-bound parse via `asyncio.to_thread` inside the async
  streaming pipeline — without this, a single C-heavy repository freezes the
  *entire server* for every concurrent request, not just its own.
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
  script's `INCLUDE`) and `file_meta` (facts merged into a file node's `meta`,
  such as Rust's `#![no_std]`) — and have the pipeline resolve file keys to the
  file nodes it created, in the in-memory and the streaming paths alike.

Not yet true at codecartographer 00ce9de: the in-memory path applies both
(`_apply_file_facts`), but the live GitHub stream (`stream_parse_url`'s batch
events, `unified_parser_service.py:390-399`) emits `file_relations` and drops
`file_meta`. A Rust file's `#![no_std]` reaches its file node on a parse of
uploaded or local files, and on a GitHub repository whose tree is cached with
its content, and not on a live stream.

## Consequences

- A new `batch_whole_tree` language parser gets cross-file resolution by
  opting into the same flag — no per-language batching logic to reinvent. C,
  Rust (*Rust is read at the item level until an engine's index replaces it*)
  and linker scripts use it, batched separately by parser identity.
- Because the flag is read by name and the Protocol does not declare it, a
  misspelled attribute opts a parser out silently, and no type check sees it.
- Trade-off accepted: a batched extension's symbols arrive as one burst after
  every file in it is fetched and parsed, instead of trickling in file by
  file. Nothing reports progress during that gap; this is a known limitation,
  not fixed.
- `has_parse_warning` is a top-level node attribute, not nested in the unified
  schema's `meta`: the C adapter and the dedicated C pipeline set it on a node
  libclang warned about, and the cargo diagnostics join sets it on a Rust item
  with a recorded error. No front-end code reads it, so it reaches the browser
  and is drawn nowhere.

## Alternatives considered

1. **Deprecate-and-warn instead of delete** the dead routers — rejected: zero
   callers means zero migration cost, and keeping dead code around obscures
   which pipeline is live for the next reader.
2. **Key batches by file extension** instead of parser identity — rejected:
   `.c`/`.h` are the same parser instance with different extensions, and
   keying by extension splits header/implementation pairs into separate
   batches, breaking `#include` resolution.

## Revision triggers

- A batch parser needs facts from another parser's batch — a Rust `extern`
  block naming a function a C file in the same tree defines — which batching by
  parser identity cannot join.
- The "symbols arrive as one burst" limitation becomes a real complaint,
  forcing `fetch_and_parse_batch` to support partial or incremental progress.
- A renderer draws `has_parse_warning`, or the attribute is removed — the
  consequence above then changes.
- A parser is found opted out by a misspelled flag, or a second opt-in flag of
  this kind is added — the Protocol then names the opt-ins.

## Amendments

*None.*
