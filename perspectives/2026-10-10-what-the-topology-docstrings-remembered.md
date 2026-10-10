# What the topology docstrings remembered — 2026-10-10

| | |
|---|---|
| **Author** | Peter Kagstrom |
| **Date** | 2026-10-10 |
| **Standing** | Perspective — attributed, dated, non-binding |
| **Tools** | Claude Opus 5.5 |

`qmcp`'s topology modules -- the capability plane, the views, the services
that serve them, and the saved-design routes -- carried their own history in
their docstrings: what each replaced, what was found missing, which check
caught what. Under `records/DRAFT-durable-text-states-what-is-true.md` those
docstrings now state facts, and the explanations moved to `qmcp`'s
`docs/agentframework/topologies.md`. This page keeps the stories, dated, because
several hold lessons that no other retrospective records. Each section names
the module it came from.

## The table nobody served (`qmcp/topology_designs.py`)

`Topology` was a table from the day the agent framework was written, and
`qmcp council create` built a row and printed it, but no route read or wrote
one. A front end growing a topology designer had nowhere to keep a design except
its own storage, and a design held only by the window was one the harness had
never seen, so nothing could tell the designer what the plane thought of it.
Serving the table fixed the storage; returning the plane's verdict on every row
fixed the second half.

The same module once tested whether a reference was an id with `isdigit()`.
`'²'.isdigit()` is true and `int('²')` raises, so a design named with such a
character saved and then returned a 500 on every read. The conversion itself is
now the test.

## A plane only a terminal could read (`qmcp/orchestration_service.py`)

The capability plane began as `uv run qmcp orchestration plane`, and a window
cannot shell out. A designer that wanted to know which shapes spend, decide or
are refused would have had to keep its own copy of the rule, and a copy is kept
current by nobody. The routes were added so the window asks.

## A tested contract, an undeployed seam (`qmcp/topology_service.py`)

`qmcp.topology_view` could build a view for anything that imported it, and both
front ends are repositories that must not import it. A demo proved the two
renderings agreed by running the harness's code in a subprocess, while nothing
at either front end's port could obtain a topology at all. The contract was
tested and the seam was not deployed, and from inside the demo those look the
same. The lesson generalises: a passing demonstration of a contract says nothing
about whether the thing that serves it exists.

The loopback test for the readings route had its own false start. Its first
version split the server's source on the first occurrence of the registering
function and asserted `is_loopback` came before it; the import line always
does, so the test failed on correct code. Text order is not nesting, and the
test now walks the syntax tree.

## The plane that said a stub ran (`qmcp/orchestration.py`)

The plane declared that the pipeline ran. The registry held the stub: two
classes registered the pipeline type, `TopologyRegistry` keeps one class per
type, and import order chose. `stubs()` exists because of that afternoon -- a
`runs` declaration is a claim about a reachable class, so it can be checked.

The seven unbuilt shapes with schemas were named `brainstorm` rather than left
as raising stubs, because read as code they looked like debt and read as design
they were a considered catalogue written before anybody needed them. The status
says which reading is meant.

Two lessons arrived from neighbouring work in the same week. `dossier.views`
learned that telling somebody a shape cannot run, without saying what would make
it run, leaves them where silence did, so every need in the plane names its
remedy. And the delegation shape was already the shape `qmcp.sweep` had taken
before it had a name -- parsers and questions chosen by the work rather than by
a setting -- and was generalised so a second caller would not write a third
dispatcher.

The cross-check's docstring once remarked that every mutation run that day had
been a cross-check of this form: break the thing, see whether the guard says
so. It is a fair description of mutation testing, and not a fact about the
class.

## Three boxes that were one (`qmcp/topology_view.py`)

`from_relations` first keyed its boxes by position. On a real thread archive,
three threads' readings of one delta drew as three nodes with the same label
and note, which read as three deltas sharing a name. `protocols/trio_demo.py`
found it; the fixture could not, because no two of its relations pointed
anywhere near each other. Boxes are now keyed by address.

In the same function, the subject of a reading had no address while every
relation target did, so the one box naming the project a reader asked about was
the only one they could not follow. It carries its own address now.

## What the sorting found

Of the prose removed from these modules, most was neither fact nor
explanation: it was the author's account of getting there, set in capitals so
it would be read first. The facts underneath were short, usually a sentence.
The explanations -- statuses, the pairing rule, view levels, channels, what is
served where -- were the part a user needed and the part least served by being
inline, because they apply across modules and were repeated in several. They
now live once in `docs/`.
