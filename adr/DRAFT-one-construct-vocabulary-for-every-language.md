# ADR-XXXX — One construct vocabulary for every language the window reads

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-10-24 |
| **Pends on** | Nothing — ready to be argued |
| **Principle** | `a-loop-is-not-a-knot` (the layer's mathematics is sought on purpose); `decisions-are-documented` |

## Context

Each parser here names what it finds in its own language's words: C's adapter
emits `struct`, `enum_constant`, `typedef`; Python's emits `class`, `loop`;
Rust's emits `impl` and `trait`, and the item-level Rust reader and the
linker-script reader of codecartographer #109 add `macro_invocation`, `region`
and `section`. Those names are right — they are what the source says — and
they make the languages incomparable. A graph of a C firmware and one of a
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
   (`type.product`, `type.sum`, `callable.method`, `layout.region`); a *facet*
   is something it can also be (`memory.unsafe`, `memory.volatile`,
   `firmware.interrupt`). Constructs carry a look; facets do not. A construct
   can be carried as a facet too: Rust's `#[link_section]` maps to
   `layout.section`, the construct an assembler's section is.
2. **Parsers keep their kinds.** The vocabulary maps each language's kinds — and
   the qualifiers, attributes, macros and body facts that make a facet — onto
   constructs. A kind that is a different construct under a stated condition is
   refined, not renamed: a Rust `enum` is `type.sum` unless its variants carry
   no data, when it is `type.enumeration`.
3. **Every node a listed language's parsers emit carries `construct`, on every
   unified parse, unless the vocabulary says why it is not one.** Each kind is
   mapped to a construct or listed under `not_constructs` with its reason —
   Python's calls, names and literals are what a body does, not what it
   declares — and a node of a kind listed there carries none; nor do the walk's
   own `directory` and `file` nodes, which are the tree's structure rather than
   anything a language declares. The stamp is additive and idempotent; a node
   keeps every attribute its parser gave it. A graph cached before parses
   stamped `construct` is not served: the cache keys a graph by the shape a
   parse gives it (`GRAPH_SCHEMA_VERSION`), so an older one is a miss and the
   tree is parsed again. A node of an unlisted language is left exactly as it
   arrived.
4. **A construct's look is the code map's shared visual grammar, and a parser's
   own look wins.** C's adapter carries the c-visualizer reference design; the
   vocabulary carries the same looks for the same constructs, so a Rust struct is
   drawn as a C struct, and a test holds the two to each other.
5. **The chrestomathy is a reading of the vocabulary and the lexicons, and a
   language with no spelling is a row saying so.** Each construct names the
   tokens each language spells it with — every one of them a token of that
   language's lexicon, and, where the lexicon files a token in more than one
   group, the group of the sense that spells this construct — and a note.
   Every language the vocabulary lists is a row of every construct. Rust has no
   `volatile`; C has no method; the absence is the lesson, and is drawn rather
   than omitted.
6. **Every join is a test.** Tokens to lexicons and to the sense each spells,
   parser kinds to the vocabulary in both directions, C's looks to the
   vocabulary's, looks to the shapes the canvas draws. Each guard was seen to
   fail before it was trusted.

## Consequences

- A new language joins the chrestomathy by a mapping and its spellings, not by
  code: the tests name what is missing.
- With codecartographer #112, the canvas draws the polygon shape C's records
  always asked for and never got; C structs and unions stop drawing as
  circles.
- With codecartographer #112, "Color By: Abstraction Layer" draws again, from
  one ramp the server carries on each node a lexicon places, and the legend
  names the layers. A layer's ordinal is its rank within its own language's
  lexicon, not a scale the languages share: one colour in two languages is one
  rank in each, not one distance from the machine, so a node names its layer
  beside the number (`meta.lexicon_layers`). Colour is never the only carrier
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
