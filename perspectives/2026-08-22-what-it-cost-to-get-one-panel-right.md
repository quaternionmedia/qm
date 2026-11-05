# What it cost to get one panel right

**2026-08-22.** A retrospective on delivering one feature — a harness topology,
visible in two front ends — across four repositories, written because the
operator asked how hard it was and how much they had to re-request.

**Tools:** assistant-2026-08. See `ci/tool-registry.yaml`.

**The short answer.** The feature was asked for once and delivered five times.
Four of those deliveries were wrong in the same way, and the operator caught
each one. The code that finally shipped is good; the path to it was not, and the
pattern in the failures is specific enough to be worth naming.

---

## 1. What was asked, and what was delivered

The request was stable throughout: *show the harness's flows in the front ends,
side by side, and make sure they agree.* It never changed. What changed was my
reading of it.

| # | Delivered | What the operator had to say |
|---|---|---|
| 1 | A demo script, documented as `python protocols/trio_demo.py` | "per governance this should be a cli route with options" |
| 2 | A server-rendered page with hand-written SVG | "this should be served through codecarto integrating into the project language, canvases and renderers" |
| 3 | The same page, now using the project's serializer | "continue iteration and reconcilliation of front end instead of the half stiched presented demo" |
| 4 | A real panel in the real application | "I see it stuck on `Flows / asking the harness…`" |
| 5 | The panel, unstuck | "when switching between topologies, the graphs arent unloading" |

Five rounds. **Three were corrections of approach** and two were defects I
shipped and the operator found by using the thing. Alongside those, three
requests added scope that was genuinely new — links to each dataview, validating
the same view on all three surfaces, and the consolidation notes — and those are
not failures; they are the request growing, which is normal.

The corrections were not: each one was me building something adjacent to the
system instead of inside it.

## 2. The errors, counted and classed

Roughly **thirty distinct errors** in this stretch of work. Counted as "a thing
that was wrong and had to be changed", not as "a commit". They fall into six
classes, and the classes are more useful than the total.

### Class 1 — Building beside a system instead of inside it (5, and the expensive ones)

Every re-request in the table above is in this class.

- A demo documented by file path, when `uv run qm --help` is the whole surface.
- Hand-written SVG in a router, when the project has layouts, a palette, a
  serializer and a canvas.
- A standalone page with its own CSS and its own blue palette, when the
  application is terminal-green with a panel registry that says in its own
  header: *a new panel is a registration here rather than an edit in three
  files*.
- `TopologyService` reading `{status, message, results}`, when
  `RequestHandler.handleResponse` had already unwrapped it thirty lines away.
  **This one caused the stuck panel.** The service read `.results` off the
  results, got `undefined`, threw on the next access, and the throw was
  swallowed — with a successful `200` in the network log.

The common failure is not laziness about reading. I read a great deal. It is
that I read **for the thing I intended to write** rather than for what already
existed. I read `topology_view.py` closely and `request_handler.ts` not at all,
because I had already decided what my service would look like.

### Class 2 — Tests and tools that proved nothing (6)

The corpus has a name for this (`records/DRAFT-decision-record-discipline.md`
§9) and I did it anyway, repeatedly.

- A "does not create the database" test whose path had a missing parent, so
  `connect` failed before it could create anything. Passed with the guard
  removed.
- Two browser tests that **skipped** because a selector matched nothing — green,
  asserting nothing.
- A test asserting `sys.executable` did not appear, which failed on the
  docstring forbidding `sys.executable`.
- Both demo windows counting `weight is None` in the document they had *both
  been handed* — perfect agreement, testing nothing.
- A harness-down test that only ran when the harness happened to be down.

Each was caught by mutating, or by the operator. **None was caught by writing
it.**

### Class 3 — Wrong context (5)

Commands run in the wrong directory; windows run under the demo's interpreter
instead of each project's, so the harness "could not emit a topology" — a true
sentence about the wrong process; `main()` reading pytest's `argv`.

### Class 4 — Edits that did not land, and were not checked (3)

A patch whose `replace` matched nothing, after which I confirmed the file
*parsed* — which proves nothing about whether the edit applied. `--over-http`
was dead for a full round because of it.

### Class 5 — Regressions from my own changes (3)

Moving a width calculation broke `--side-by-side` in the other mode. Moving the
routes onto the project's envelope broke the demo and five of my own tests.
The demo caught the first of those, which is the system working.

### Class 6 — Mechanical (4+)

Heredoc escaping, a literal tab in a docstring, a stale asset filename, `_log`
used above its definition. Cheap individually; they consumed a real share of the
turns.

## 3. What went right, and why

Three things worked, and they were the same thing: **something mechanical
disagreed with me.**

- **The agreement check caught its own hole.** Comparing arrows as sets let
  parallel edges collapse; a mutation exposed it. It later caught the envelope
  change I had just made, reporting `could not draw it: None`.
- **A test I wrote counted two implementations of one comparison** and went red
  on its first run, because the subprocess path had kept its own copy.
- **Mutation testing found the marker `x`** with no gravis shape — the one
  marker a palette author chose *precisely* to stand apart from `o`, silently
  becoming a circle.

Every one of these is a machine contradicting a person. None of my careful
reading found any of them.

## 4. Twenty-one defects, and what they say about each system

The consolidation notes in `codecartographer/docs/consolidation.md` list every
one with its cost. The pattern by system:

**codecartographer** — a project that changed canvas (matplotlib to gravis) and
kept its old vocabulary. The `Palette` declared six styling tables and *nothing
read them*: a palette could be edited, saved and selected without changing a
pixel. Layouts could not be named the way a menu names them. The API's address
was written in four places and three were wrong. **The single improvement with
the best return: make the lexicon and the palette one ontology.** They describe
the same language for the same renderer and neither knows the other exists.

**qmcp** — the harness was correct and *unreachable*: it served no topology
route at all, so no front end could fetch one. The library was complete and the
seam was not deployed. **The improvement: treat "a module exists" and "a route
reaches it" as different states**, and check the second — which is now a test in
`qm`.

**dossier** — had exactly the same defect on the same day: a renderer, tested,
that no command or tab reached. Two independent instances of one shape is not
coincidence; it is what happens when "done" means "the function works".

**qm** — governance caught the class, not the instance. `AGENTS.md` item 10
("name one other thing that would produce the same output") and §9 (the
scaffolding is part of the measurement) describe my failures precisely, in
advance, in writing. **They did not prevent one of them.** That is the finding
about qm: a corpus that names a failure mode accurately and still watches it
happen has a readership problem, not a drafting problem.

## 5. The tide that raises all the ships

One change would have prevented most of this, and it is not a rule.

**Every one of the five re-requests would have been avoided by asking, before
writing a line: what in this system already does this, and what would it look
like if I added mine to it rather than beside it?** Not "read the code" — I did.
Specifically: find the registry, the vocabulary, the envelope, the entry point,
and put the new thing *in* them.

The three systems each have a version of that seam, and each was crossed wrongly
at least once:

| System | The thing to join | What I did instead |
|---|---|---|
| `qm` | `ci/cli.py`'s `ROUTES` | wrote a path in a document |
| `codecarto` | `panel_registry`, `Palette`, `generate_return`, `RequestHandler` | a page, a palette, an envelope, a parser — all my own |
| `qmcp` | `create_app`'s loopback decision | (joined correctly, and it is the one that went cleanly) |

The qmcp case is the control: where I found the existing decision and put the
new routes inside it, nothing went wrong. That is the whole lesson, and it has
one mechanical form worth adopting — **a checklist item that names the joining
point before the work starts, and is answered with a file and a line number,
not a yes.**

The second, smaller tide: **a green test I wrote is not evidence.** Six of my
tests asserted nothing until something else proved they did not. Mutating is
cheap and it found all six. It should not be a discipline I remember; it should
be what "the test is finished" means.

## 6. What this retrospective does not establish

- **That thirty is the real number.** It is what I can enumerate from this
  session's record. Errors I fixed inside a single turn without noting are not
  in it, and the true figure is higher.
- **That the shipped code is right.** Four suites are green — codecarto 381,
  dossier 896, qmcp 723, qm 908 — and green suites are what let all of the above
  happen unnoticed for a round at a time.
- **That the operator's five interventions were the only ones needed.** They are
  the ones that were made. A reader with less patience would have stopped at the
  second.
