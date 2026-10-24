# QM-XXXX — A Semantic Index Is a Recorded Document, and the Seam Decodes It

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-10-12 |
| **Namespace** | org |
| **Binds** | This corpus, and any project that reads what a compiler or a language server knows about code |
| **Pends on** | Nothing — ready to be argued |
| **Principle** | `build-the-seam-buy-the-engines` — the compiler and the language server are the engines that resolve names, and reading what they publish is the seam; `seams-on-standard-protocols` — one published schema with an independent producer per language; `one-house-stack` — what the seam imports to read it is house stack |

## Context

A tool that reads source without a compiler can know a program's structure and
not its meaning. codecartographer reads Rust and C at the level a tokenizer and
libclang reach, and draws a call, an implementation or a type reference from a
name only when exactly one item in the parse has that name, labelling the edge
so. Which `Read` a `use` brings in, what a method call's receiver is, what a
macro expands to: those are answered by the compiler, and published by the
language servers built on it.

They publish it in one format. SCIP is a protobuf schema (`scip.proto`) for an
index of a code base -- each document's occurrences of each symbol, each
symbol's kind and relationships -- and it has a producer per language
maintained beside the language's own tooling: `rust-analyzer scip` for Rust,
`scip-clang` for C and C++, and producers for Python, TypeScript, Java and
others. One reader would read all of them.

Two facts constrain how. **Producing an index runs the code being indexed**:
rust-analyzer runs a workspace's build scripts and procedural macros to know
what they generate, as cargo does, and codecartographer's records already refuse
to run a toolchain from a route a port can reach. **Reading an index needs a
protobuf decoder**, and Python's standard library has none; under
`records/DRAFT-house-stack.md` §3, a component imported into seam code is house
stack and needs a record.

## Decision

1. **Semantic facts about code come from the language's own index, in SCIP.**
   What a name refers to, where a symbol is defined and used, what implements
   what: a QM project reads these from a SCIP index its language's tooling
   wrote, and does not reimplement name resolution a compiler performs.
2. **An index is recorded by a command a person runs, and read as a document
   with its age.** It is never produced by a service on request, because
   producing it runs the code being indexed. A reading says when the index was
   written and whether a source changed after it, as every recorded document
   read across a QM seam does.
3. **The seam decodes SCIP's wire format with a reader written against the
   standard library**, limited to the messages and fields it reads. The
   schema's field numbers are named once, in that reader, and a recorded index
   from each producer the reader claims to read is its test fixture. No protobuf
   runtime and no generated code joins the house stack for it.
4. **A field the reader does not know is skipped by its wire type, never an
   error.** SCIP adds fields over time, and an older reader must read a newer
   index; a field it needs and does not find is reported, never defaulted.

**Enforcement.** The dependency-review gate of `records/DRAFT-house-stack.md`
§2 refuses a protobuf runtime in a project's manifest that cites this record
without revising it. The reader's tests replay a recorded index per producer,
and each guard is seen to fail before it is trusted
(`records/DRAFT-a-check-is-evidence-only-after-it-has-failed.md`).

## Consequences

- codecartographer's `unique-name` relations can be replaced by resolved ones
  for every language with a SCIP producer, Rust and C first, through one reader.
- The reader is house-stack code a person maintains: the wire format's few
  types, and the handful of SCIP messages the window reads. The cost is accepted
  and bounded by the revision triggers below.
- Recording an index needs its producer where the recording runs. A window with
  no index draws what it can parse and says which relations it guessed.
- The rule a project already follows for cargo -- read what the toolchain
  wrote, never run it -- becomes the organisation's rule for every indexer.

## Alternatives considered

1. **The protobuf runtime and code generated from `scip.proto`.** The reference
   path, and correct. Rejected for now: it adds a runtime and generated code,
   pinned to a compiler version, to the house stack to read a dozen fields, and
   the schema's evolution still has to be followed by hand either way. The
   second trigger below is the condition under which it wins.
2. **JSON rendered by the `scip` command-line tool.** Rejected as the recorded
   form: it adds a second toolchain to every workstation that records, and a
   translation whose output is not the standard. Acceptable as an additional
   form if that rendering becomes a published, stable schema.
3. **LSIF.** Rejected: its main producer moved to SCIP, and new producers target
   SCIP.
4. **A language server queried live, over LSP.** Rejected: a service on
   request would run a toolchain over code it was pointed at, which §2 refuses,
   and LSP answers one position at a time where a map needs the whole index.
5. **A syntax engine (tree-sitter).** Rejected for this purpose: it parses and
   does not resolve names, which is the gap this record exists to close.

## Revision triggers

- SCIP makes a breaking change to its schema, or its maintainers deprecate it.
- A second QM project needs protobuf for another reason. The runtime then joins
  the house stack once, by record, and §3's reader is retired in its favour.
- The reader grows past decoding -- it needs to write, merge or rewrite indexes
  -- which is the size at which a library should own it.
- The `scip` tool publishes a stable JSON form, which would let §3's reader read
  that instead.

## Amendments

*None.*
