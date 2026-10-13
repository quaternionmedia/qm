# ADR-XXXX — One construct vocabulary for every language the window reads

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-10-12 |
| **Pends on** | Nothing — ready to be argued |
| **Principle** | `a-loop-is-not-a-knot` (the layer's mathematics is sought on purpose); `decisions-are-documented` |

## Context

Each parser here names what it finds in its own language's words: C's adapter
emits `struct`, `enum_constant`, `typedef`; Python's emits `class`, `loop`;
Rust's emits `impl`, `trait`, `macro_invocation`; the linker-script reader emits
`region` and `section`. Those names are right — they are what the source says —
and they make the languages incomparable. A graph of a C firmware and one of a
Rust firmware drew a struct two ways, and nothing could say that a Rust `enum`
whose variants carry data is a different thing from C's `enum`, or that a Rust
`#[link_section]` and a linker script's output section are the same idea seen
from two sides.

The plan this window is built to (`plans/the-web-window.md`, phase 5) asks for a
chrestomathy of code: one construct set beside itself across languages, so a
reader learns by the difference. The lexicons already place each language's
tokens on abstraction layers; what was missing is the join between a token, a
parser's kind, and the thing both of them are.

## Decision

1. **`codecarto/data/constructs.yaml` is the one place a parsed thing's
   language-neutral identity lives.** A *construct* is what a node is
   (`type.product`, `type.sum`, `callable.method`, `layout.region`,
   `layout.section`, `firmware.entry`); a *facet* is something it can also be
   (`memory.unsafe`, `memory.volatile`, `firmware.interrupt`). Constructs carry
   a look; facets do not. A construct can also stand in a node's
   `meta.facets`: Rust's `#[link_section]` puts `layout.section` on the item it
   marks, which is what a linker script's output section is, and `#[entry]`
   puts `firmware.entry` there, which is what a linker script's `ENTRY` is.
2. **Parsers keep their kinds.** The vocabulary maps each language's kinds — and
   the qualifiers, attributes, macros and body facts that make a facet — onto
   constructs. A kind that is a different construct under a stated condition is
   refined, not renamed: a Rust `enum` is `type.sum` unless it has variants
   and none of them carries data, when it is `type.enumeration`. An enum with
   no variants at all is `type.sum`: it is the empty sum, with no variants to
   make it C-like.
3. **Every node of a listed language carries `construct`, on every graph a
   route serves.** The stamp is applied where every graph passes — the
   serializer — and again to a cached graph as it is replayed, so a graph no
   parser stamped (the crate graph, read as the `cargo` language, where a crate
   is a package) and one cached before a construct existed both arrive saying
   what their nodes are. The stamp is additive and idempotent; a node keeps
   every attribute its parser gave it. A node of an unlisted language is left
   exactly as it arrived. One function decides a node's construct, and the
   client never decides one.

   Not yet true at codecartographer 00ce9de, the commit this record was
   checked against:

   - A kind the mapping does not list gets no `construct`. The crate graph
     draws `workspace`, `target`, `feature`, `native_lib`, `device_target` and
     `memory_map` beside the `crate` and `external_crate` the `cargo` mapping
     places. Python's parser emits `call`, `argument`, `name`, `constant`,
     `string` and its fallback `symbol` beside the kinds its mapping places.
   - C's dedicated routes under `/c-parser/` answer from the libclang pipeline
     and never pass the serializer. `/c-parser/stream-github` emits nodes
     labelled `language: c` with no `construct`, and `/c-parser/file`,
     `/c-parser/github` and `/c-parser/directory` return nodes with no
     `language` at all, which the vocabulary cannot place. The front end calls
     none of them; the C graphs it draws come through `/parse`, which stamps
     them.
4. **A construct's look is the code map's shared visual grammar, and a parser's
   own look wins.** C's adapter carries the c-visualizer reference design; the
   vocabulary carries the same looks for the same constructs, so a Rust struct is
   drawn as a C struct, and a test holds the two to each other.
5. **The chrestomathy is a reading of the vocabulary and the lexicons, and a
   language with no spelling is a row saying so.** Each construct names the
   tokens each language spells it with — every one of them a token of that
   language's lexicon — and a note. Rust has no `volatile`; C has no method; the
   absence is the lesson, and is drawn rather than omitted.
6. **Any graph on the canvas can be read as a chrestomathy.** A census route
   takes the nodes a canvas holds and answers the constructs they are, in which
   languages, with the nodes that are each — and what the vocabulary could not
   place: a kind it does not map, a language it does not list, a node with no
   language. What is not placed is said, never dropped, because a reading of
   only the placed nodes would claim a coverage the vocabulary does not have.
   From the canvas the same reading is reached three ways: the Chrestomathy
   panel reads whatever is drawn, the canvas can be coloured by construct, and
   a node's own menu opens the chrestomathy at what that node is.
7. **Every join is a test.** Tokens to lexicons, parser kinds to the vocabulary
   in both directions, C's looks to the vocabulary's, looks to the shapes the
   canvas draws, the crate graph's kinds to the `cargo` mapping. Each guard was
   seen to fail before it was trusted.

   Not yet true at 00ce9de: the both-direction test of parser kinds exists for
   C, the linker-script reader and Rust (`tests/test_construct_service.py`).
   The `cargo` test runs one way — every kind the mapping lists is one the
   crate graph draws (`tests/test_every_graph_a_chrestomathy.py`) — and
   Python's and assembly's kinds have no test against their mappings, which is
   how the unmapped kinds in §3 pass.

## Consequences

- A new language joins the chrestomathy by a mapping and its spellings, not by
  code: the tests name what is missing. A new panel's graph joins it by passing
  through the serializer, which every route already does.
- The radial menu's View submenu carries a fourth host verb, `compare`; the
  record adopting rad names it.
- The canvas gained the polygon shape C's records always asked for and never
  got; C structs and unions stop drawing as circles.
- "Color By: Abstraction Layer" draws again, from one ramp the server carries on
  each node, and the legend names the layers. Colour is never the only carrier
  of a layer.
- The vocabulary is a second hand-authored file beside the lexicons, and it can
  be wrong in ways no test catches: a construct can be mis-glossed, a mapping
  can be defensible and still not the best reading. That is the cost of naming a
  structure on purpose, and it is accepted.
- The estate palette (`palette_service.vocabulary`) is untouched. It styles the
  estate's kinds of graph; this styles code. They stay two vocabularies for two
  kinds of picture.

## Alternatives considered

1. **One unified kind vocabulary, imposed on every parser.** Rejected: it would
   erase what each language calls a thing, which is half of what a reader
   comparing languages needs, and would make every parser change a cross-language
   negotiation.
2. **Map in each parser, without a shared file.** Rejected: the mapping would be
   copied per language and drift, and the chrestomathy would have nothing to
   read but code.
3. **Derive constructs from the lexicons alone.** Rejected: a lexicon places
   tokens, and most constructs are not one token — a sum type is `enum` plus
   variants that carry data; a volatile access in Rust has no token at all.
4. **Adopt an external ontology of program constructs.** Rejected for now: none
   found covers firmware facets (sections, interrupts, memory regions) and the
   spellings at once. A revision trigger watches for one.

## Revision triggers

- An external, maintained ontology of program constructs covers the firmware
  facets this one names.
- A language's semantic index (SCIP, LSIF) is read here: its symbol kinds become
  a second source of kinds, and the mapping should take them rather than parse
  around them.
- Two constructs are found indistinguishable in every listed language, or one
  construct is found to be two.

## Amendments

*None.*
