# The web window: codecartographer as the estate's front end

**What this is.** The plan for growing `codecartographer` from a code-map tool
with three estate routes into the front end most people touch: one canvas that
draws code, the estate, the harness and the archive, and the frame a topology
designer sits on. It follows [`the-third-side.md`](the-third-side.md), which
placed codecarto beside the pair and asked eight questions; the ones a person has
since answered are recorded under *Decisions taken*, the rest under *Open*.

**Stamped 2026-09-20** against `codecartographer` `main` at `4e30271`, `qmcp`
`main` at `3e25711`, `dossier` `main` at `bd322d3`, `looksatwords` `main` at
`32d3371`, and this corpus at `f23a875`. Every figure below was true at those
commits. Re-derive before acting; the commands that answer are named beside each.

---

## The reading of the brief

Two words, one canvas.

**Cartography** is maps of things: source code by parsing; the estate by reading
`ci/capability-registry.yaml`, `families.json` and dossier's overview seam; the
harness by reading its topologies and its runs; conversations by reading what the
archive says a project is related to.

**Chrestomathy** is the comparative reading of those maps — the same construct
exhibited across languages so a reader learns by comparison, as a printed
chrestomathy did for natural languages. codecarto already holds the raw material:
a parser registry across many languages (`GET /parse/languages` is the count),
hand-authored lexicons that place a language's tokens on abstraction layers, and a
bridge that stamps parsed nodes with those layers. `looksatwords` holds the other
half — the turns of a conversation, and which topics each carried. The plan's last
phase joins them by the address grammar the pair already shares.

## What exists, and what the plan reuses

Three routers already obey the two rules every new view inherits, and their
docstrings state them: **serve a codecarto graph, not a picture of one** (build a
`networkx` graph, hand it to `GraphSerializer`; layouts, palettes and the canvas
follow), and **an absence is a sentence, never an empty graph** (a 200 whose
`results` carry `unreachable` or `unreadable`, a `problem`, a `remedy` and a
`where`). They are `/topology` (the harness's shapes and readings, over HTTP),
`/capabilities` (the registry the corpus holds) and `/overview` (dossier's seam).
Only the first has a panel in the web application; the other two have routes and
no window. The front end's canvas is one streaming renderer since
codecartographer #98, with the legend and the radial menu mounted as extensions
against it rather than inside a renderer.

Two words "topology" live in that repository. `docs/llm/roadmap/` uses it for
code structure derived by parsing. `/topology` uses it for the harness's
collaboration shapes — boxes and arrows with kinds, an arrow weight that may be
absent and is then drawn dashed rather than thin. The designer below is built on
the second.

On the harness side, `qmcp.orchestration.PLANE` declares for every shape whether
it runs, is a brainstorm or is refused; whether it spends, writes or decides; and
what it *needs* before it could run, each need naming what supplies it. A
`Topology` table exists. **No route creates, lists or runs a topology**, and
every registered class's `run` raises — the shapes that do run (`delegation`,
`crosscheck`) run as functions. `dossier` draws the same shapes in a terminal,
monitors and answers the harness live, and states its own gap in
`dossier/topology.py`: it cannot show a topology *running*, and drawing a live
flow on a shape is the next thing.

## Constraints inherited

None of these is new. Each is a record, a docstring or a handoff, and the plan is
bounded by them rather than by taste.

1. Serve a graph, not a picture. No second renderer. (`topology_router.py`)
2. Absence is a sentence. (`qmcp_client.py`, `capability_router.py`)
3. Vocabulary lives upstream: rungs in the corpus, box and arrow kinds and needs
   in the harness, the address grammar in the pair. A copy in codecarto says
   which file is right when they differ. (`capability_service.py`;
   `the-third-side.md`, "the base absorbs the governance")
4. A capability the host lacks is offered disabled, never substituted.
   (`adr/DRAFT-rad-integration.md` §4 on `project/codecartographer`)
5. Attested acts are a person's. Answering the queue, ratifying, tagging,
   authorising spend. (`ci/attested-registry.yaml`, `qmcp.governed`,
   `dossier.human`)
6. Optional but witnessed. codecarto absent is reportable as absent by the pair;
   the pair absent is a sentence in codecarto. (`the-third-side.md`)
7. Identity, not reachability. Ask a server what it is; a port answering proves
   only that something listens. (`handbook/async-contract.md` §4)
8. Every signal has a fixture in which it reports bad, and a worked example is
   executed by the test command. (`handbook/handoffs/README.md`;
   `records/DRAFT-one-executable-walkthrough.md`)
9. Durable text carries few integers; provenance — source, commit, age — travels
   with every figure a window shows. (`records/DRAFT-few-integers-in-durable-text.md`)

## The frame

The generalisation is latent in the three services, which share one shape:
read → a `Reading` or a reason → `as_graph` → `as_gjgf` → `metadata` carrying a
`caveat`. The frame names that shape and makes it the thing a new view implements.

**Backend.** A `Seam` is a source this window reads: it can say what it is
(identity, with the schema it speaks), read a document or say why it could not,
and turn the document into a graph with metadata. The three existing services
become seams in place, with no behaviour change and their routes untouched — the
pair's `qm demo --over-http` compares against those routes and must keep
working. One new route lists every seam with its identity and liveness, which is
the row `the-third-side.md`'s first step asked dossier to hold about codecarto,
answered from this side.

**Frontend.** One client unwraps the envelope and tells four outcomes apart — the
window's own API down, the seam unreachable, the seam unreadable, a document —
where today that logic lives in the topology service alone. One component renders
a problem (what, remedy, where, retry). One strip renders provenance above every
estate graph: the source, the commit or generation time, the caveat. Panels are
controls that choose what to draw; the drawing goes to the one canvas. The graph
metadata gains a typed estate shape so the canvas, the legend and the strip read
one thing.

**The radial menu, in authored mode.** The rad adoption record omitted
`add-node`, `reverse` and `edit-label` as having no honest meaning for a graph
derived from parsing. A designed topology is not derived from parsing; those
verbs become honest exactly there, and codecarto becomes the contract's first web
host for its full node vocabulary. The divergence is proposed to `rad` first, as
the integration standard asks.

## Phases

Each phase is useful alone, each is one slice, and each ends in something a
person can open. Slices are not split into several pull requests unless a gate or
a slot requires it; the aim is a cogent demo per slice.

**0 — Truth pass.** The documentation says what the tree says. Ports name the
constant `uv run qm dashboard` allocates or point at `serve --help`; the
project's `AGENTS.md` carries the corpus's pull-request text and the merge
instruction; test figures give way to the command; the record index and the
submodule path are current; the three estate routes appear in `docs/api.md`; the
dev-server proxy list and the API base carry every route; the UI reference is
written from `panel_registry.ts`; the scaffolding nothing imports is deleted. A
structural check rebuilds the route table from the application and fails when the
document disagrees — the pattern `looksatwords/tests/test_cli_reference.py`
already uses for its CLI.

**1 — The estate frame.** The seam base, the client, the problem view, the
provenance strip; a Capabilities panel and an Overview panel beside Topology; the
liveness route. A stub harness fixture so every panel has a red case: harness
down, harness too old, harness answering something unreadable. dossier gains a
codecarto row in `dossier.sources`.

**2 — Monitoring: the live flow on the shape.** The harness already serves its
invocations and its human queue, addressed as `owner/repo/invocation/<id>` and
`owner/repo/ask/<id>`; those addresses join to topology boxes. The window overlays
run state on the boxes using the state channel its system renderer already has for
the PAM view, moved onto the one canvas as an extension. Polling first, because it
needs nothing from the harness; an event stream from the harness second, because
it is cleaner and is one more surface to govern. The human queue is shown
read-only, including how many rows the harness held back.

**3 — The topology designer.** Read first: the gallery from the plane — status,
what each shape spends, writes or decides, what it needs and what supplies each
need; a refused shape drawn refused, a brainstorm drawn as a proposal; a "what
could run with this hand" control from `runnable_now`. Then author: compose boxes
and arrows in the harness's vocabulary on the canvas through the authored verbs; a
configuration form generated from the shape's own schema; save as a row in the
harness's existing `Topology` table. The refusal of a shape against an attested
act is asked of the harness at save and at run; the window renders the answer.
Client-plane persistence, no server orchestration, as the harness's own agent
framework overview describes itself.

**4 — Manipulation.** Run a shape whose status is `runs` against declared workers
and a declared budget, through the governed seam; watch it in the overlay; its
draft lands in the queue. The execution route and the spend declaration live in
the harness. Nothing in the window turns a draft into a decision.

**5 — Cartography and chrestomathy.** The lexicon toggle into the main parse
flow, and layer colouring as legend rows. A chrestomathy panel: choose a construct
— a layer, a lexicon group — and see it across every language with a lexicon;
extend the lexicons past the two that exist. The looksatwords bridge, both ways: a
thread to the repositories it was about (weighted, from the harness's relations
route) to the code map of one; a file or symbol to the threads that spoke of it,
with the topics each turn carried. Words and code, joined by the address.

**6 — The triangle, executed.** One walkthrough page showing a change cross the
panel, the harness and the map, run by the ordinary test command. Where it lives
is still open below.

## What must change in the neighbours

| Repository | Change | Why the window cannot do it instead |
|---|---|---|
| `qmcp` | a route serving the plane and its needs; a route serving a shape's configuration schema; create, list and read over the existing `Topology` table; later an execution route for `runs` shapes and an event stream | refusal, spend and attested acts are decided there; the window adds nothing |
| `qmcp` | expose what `undeclared()` and `stubs()` already compute | so the designer greys a shape whose declaration lies |
| `looksatwords` | its `docs/api.md` lists the harness routes it serves; a per-thread topics document the window can draw; a port of its own from the dashboard's allocation | the border record: it reads prose, the window reads its reading |
| `dossier` | a codecarto row in `dossier.sources` | `the-third-side.md`, step one |
| this corpus | capability-registry rows for the window's own capabilities, of which there are none today; a home for the triangle walkthrough | the registry is where a phase claim lives |

## Testing posture

Structural checks first, because they run in under a second and do not need a
browser: routes against documents, ports against the dashboard's allocation, the
panel registry against the UI reference, the envelope's shape. Pure tests for
every state transition and every branch of the seam client — the pattern that
pinned the graph-merge defect in `web/tests/state/`. Browser tests against a stub
harness on a non-default port, with the harness's identity asserted before any
measurement, and screenshots recorded by the test rather than captured by hand.
Each new guard is broken once, seen red, restored, and the mutation is written
beside it.

## Decisions taken

Answered by Peter Kagstrom on 2026-09-20, in session.

- Nothing is held local. Branches are pushed and pull requests opened; **nothing
  reaches `main` without his explicit approval.**
- The two unpushed codecarto branches — `test`, carrying the rad vectors re-pinned
  to the publisher's current version and the seed's one-pull-request workflow, and
  `feat/the-monitor-derives-the-system` — are the implementing session's to triage
  and integrate.
- A designed topology persists in the harness's existing `Topology` table.
- Pull requests may be opened in `qmcp`.
- Chrestomathy is the intended reading, and the window is to be the digital,
  modern form of it for code.
- Polling and an event stream are both wanted, phased in that order.
- This plan lives in this corpus, with a pointer from codecarto's roadmap.
- Slices are not split unless a gate or slot requires it.
- The authored radial verbs are proposed to `rad`.

## Deferred, and named so it is not forgotten

**Answering the human queue from the web.** Attested by `ci/attested-registry.yaml`;
dossier's terminal does it with a required name, one question at a time, no
batch. Whether the web window should ever post an answer — and if so under what
identity, since a browser session names nobody by default — wants its own
consideration and review before it is built. Until then the queue is read-only
here, and a panel that shows a question says where it can be answered.

## Open

- Where the triangle walkthrough lives: `dossier/walkthrough`, `qmcp/walkthrough`,
  `codecartographer`, or this corpus's `walkthrough/`. The third side's question,
  still open.
- Whether the graph submodule and its database are in scope for the window at
  all. The third side's question, still open.
- Whether `dossier.views.Need` and `qmcp.orchestration.Need` stay two
  vocabularies. `handbook/handoffs/views-declare-what-they-need.md` §2.1 holds the
  argument; the designer renders the harness's and does not need the answer.
