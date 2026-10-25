# ADR-XXXX — Rust is read at the item level until an engine's index replaces it

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-10-24 |
| **Pends on** | Nothing — ready to be argued |
| **Principle** | `build-the-seam-buy-the-engines`; `one-house-stack` |

## Context

Rust source was read by a line-anchored regex: top-level names only, no nesting,
no `impl` blocks' methods tied to their type, no module tree, no relations, and
`mod foo;` not recognised at all. The firmware and FFI facts a reader of a Rust
workspace looks for first — `#[repr(C)]`, `#[link_section]`, `#[no_mangle]`,
`extern "C"` blocks, `unsafe`, `static mut`, `#![no_std]` — were invisible.

Three ways to read Rust better exist. The engine that owns Rust is the compiler,
reached through `rust-analyzer`, whose `scip` command writes a semantic index in
a format other language servers also write (`scip-clang` for C/C++). A second,
general engine is tree-sitter, whose Python bindings and Rust grammar are
already declared in this project's `multilang` extra and imported nowhere.
The third is to extend the in-house tier the regex readers belong to.

`records/DRAFT-house-stack.md` §3 draws the line between them mechanically: a
component imported into seam code is house stack and needs an org record to sit
outside the blessed set; a component reached only across a protocol seam is an
engine selection. tree-sitter would be imported. A SCIP index would be read as a
document, across a seam — but reading it needs a protobuf decoder, which is
imported.

## Decision

1. **Rust source is read by a stdlib tokenizer and brace matcher, at the item
   level, and no further.** Items, their nesting, visibility, qualifiers,
   attributes, ABIs, receivers, field types, the `mod` tree across files, `use`
   paths walked through it, and the calls in a body. It replaces the regex
   patterns for `.rs` and adds nothing to the dependency set.
2. **Every relation it draws says how it was resolved.** `module-tree`,
   `crate-by-directory`, `unique-name`, or `external`, on the edge, and the
   linker reader of §4 writes `same-file`, `include`, `same-directory` or
   `unique-name`. A `contains` edge carries none: it records nesting the source
   shows, not a name resolved. A call, impl or field type is resolved only when
   exactly one local item has the name, and an ambiguous name draws nothing;
   so do a crate name two crates' directories share, an `INCLUDE` two files
   could answer when none sits beside the script, and a region name two
   regions answer where it is first found — its own file, then the files it
   includes, then the whole batch. A method call on anything but `self` is
   counted as unresolved rather than guessed.
3. **It stops where name resolution begins.** Macro expansion, type inference,
   trait resolution and re-exports are the compiler's. The reader does not
   approximate them.
4. **Linker scripts are read by the same tier** — regions, sections, symbols,
   entry, includes — because a firmware's memory map is the layer below both
   C and Rust and has no engine worth buying for reading it as structure.
5. **The engine's index replaces the reader's guesses when it is read.** A SCIP
   index from `rust-analyzer` (and `scip-clang`) is the intended successor for
   every `unique-name` edge, for Rust and C alike, recorded by a person-run
   command as *The window reads what cargo wrote, and never runs cargo* §5
   requires. Its
   decoder is a house-stack addition and starts as an org record.

## Consequences

- Rust nodes carry the attributes and facets the construct vocabulary reads, so
  firmware facts are visible on the code map today, without a toolchain.
- The reader is a second batch-whole-tree parser, which is the revision trigger
  of *Unify parser/cache architecture around `ParserRegistry` +
  `batch_whole_tree`*; that record states the attribution by
  file key this needed.
- A wrong `unique-name` edge is possible (a free function shadowed by a local
  closure of the same name) and is labelled as what it is. A missing edge is
  the common failure, and is the safe one.
- `tree-sitter` stays declared and unused. Whether it joins the house stack is
  the org's decision, not this project's.

## Alternatives considered

1. **tree-sitter with the Rust grammar.** A full syntax tree and a general
   engine for many languages. Rejected for this project alone: it is an import
   into seam code, which the house-stack record sends to an org record, and a
   syntax tree resolves no more names than this reader does — the gap that
   matters is semantic, which tree-sitter does not close.
2. **`rust-analyzer` directly, as a language-server client.** The real answer to
   name resolution. Rejected as the first step: it means running a toolchain
   process from the window, which the cargo record forbids; its batch output
   (SCIP) is the form this window can read, and is §5.
3. **Keep the regex.** Rejected: it cannot see nesting, attributes or modules,
   which are most of what a reader of a Rust workspace asks.
4. **`syn` through a small Rust helper.** Exact parsing, by the community's own
   parser. Rejected: a Rust component built and shipped by this project is
   outside the house stack, and it still resolves no names.

## Revision triggers

- An org record admits a protobuf decoder (or SCIP reader) to the house stack —
  then §5 is built and §2's `unique-name` edges are replaced.
- An org record admits tree-sitter — then whether it replaces this reader, the
  regex readers, or neither is decided against what it would add.
- A reader of a real workspace finds a construct this tier misreads often enough
  that the fix is a parser rather than a pattern.

## Amendments

*None.*
