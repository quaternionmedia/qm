# Gates and checks

The checks that refuse something. `uv run qm gates` lists every [gate](../../ref/glossary.md#gate){ .glossary-term } with what
it cannot see; this page describes the rules several checks share, and the
checks whose behaviour needs more than a docstring.

## Principle edges

`uv run qm edges` (`ci/check_principle_edges.py`) holds the charter,
`PRINCIPLES.md`, to its own declared shape. Every principle carries one line:

```
↔ Edges: rests-on credit-tracks-accountability, completes show-it-by-running-it
↔ Edges: none -- <a reason>
```

- **A declaration is required, an edge is not.** A charter made connected by
  effort looks checked and is worse than an honest sparse one. `none` is a
  first-class answer, and it costs a reason long enough not to be a label, so
  the honest answer is also the cheapest one.
- **Both ends.** An edge stated from one end only is refused: a reader arriving
  at the other principle would never learn of it.
- **A closed vocabulary with declared inverses.** `orders` and `ordered-by`,
  `completes` and `completed-by`, `rests-on` and `bears`, and the symmetric
  `shares-teeth`. A free string would let a typo become a category.
- **Names, not ordinals.** A principle is addressed by its name. A reference to
  a position that has shifted still resolves, to the wrong principle; a name
  moves with what it names. The check scans every binding directory for the
  ordinal form. `perspectives/` and `handbook/handoffs/` are not scanned, so an
  ordinal can survive there. A document that names the form in order to forbid
  it, or whose own numbering collides with it, declares
  `principle-name: allow` with a reason, on the line or once at the top of the
  file.

It cannot tell whether two principles actually conflict, or whether a stated
edge is true: that is a reading.

## Shared shapes

- **An exception costs a stated reason.** `timeless: allow`,
  `principle-name: allow` and the [ADR](../../ref/glossary.md#adr){ .glossary-term } lint's allowance all take a reason on
  the line, and a bare marker counts for nothing.
- **A limit is printed.** Each check states what it cannot see, in its own
  output where a reader meets it.
