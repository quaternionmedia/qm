# Handoff — the web window: what landed, and the phases that remain

**Stamped 2026-09-21, after the landing.** `qm` `main` at `2fb2828`;
`project/codecartographer` at `51a832a`, carrying `main` at `de8f383`;
`codecartographer` `main` at `c5ed009`, pinned to that tip; `qmcp` `main` at
`d834916`; `looksatwords` `main` at `01da481`; `rad` `main` at `3e8794f`;
`dossier` `main` at `d42967a`. Every figure here was
true at those commits and nowhere else; the next session re-derives before
acting. The plan is [`plans/the-web-window.md`](../../plans/the-web-window.md)
and this page is where its remaining phases are picked up. Read the plan's
*Constraints inherited* first: every phase below is bounded by them.

---

## 0. What landed

Phases 0 and 1 of the plan, across five repositories in one day, each as its
own pull request, merged with explicit approval:

- **codecartographer** — the estate frame: `estate_service` identifies every
  seam by a document whose shape the window knows; `/estate/seams` is the
  liveness table; Capabilities, Overview and Estate panels beside Topology on
  the one canvas; one seam client for the four outcomes; the boundary between
  calculated, stored and displayed stated in `docs/architecture.md` and checked
  by `tests/test_boundaries.py`; layouts resolved once whatever the spelling;
  every document read against the application by `tests/test_docs_routes.py`.
- **qmcp** — `GET /v1/orchestration/plane`, `GET /v1/orchestration/runnable`,
  `GET /v1/topology/schema/{kind}`, and `/v1/topologies` (POST, GET, GET one,
  PUT) over the table that existed with no route; `walkthrough/07`.
- **looksatwords** — every `/api/harness/*` route documented and guarded both
  ways; `GET /api/harness/threads/{source}/{thread_id}/topics`, a document a
  graph can draw; its port from the corpus's allocation.
- **dossier** — the overview seam carries `generated_at`.
- **rad** — a Proposed record: an authored-graph mode for the ring.
- **this corpus** — the plan; the prose reader's surface on the dashboard;
  `check_pr_voice.py` in `one-pr-check.yml`; clause 5 of the contributorship
  record; the remote-branch audit completed.

`perspectives/2026-09-20-the-web-window-first-slice.md` is why it went the way
it did — fourteen findings, the defects the session caused written the same
way as the ones it found.

**Landed the next day**, each as its own merged pull request: the propagation
of `main` to `project/codecartographer` (its first CI run red on the newer
`adr_lint.py`, the twelve drafts then listed as linked rows); codecartographer's
pin moved to that tip with its seed workflows re-copied, so its `one-pr-check.yml`
carries the voice step and `leak-check.yml` joins its gates; and three
docs-only pointers so a session opening a project finds this page —
codecartographer's `docs/llm/roadmap/README.md` (*Picking up the web window*),
qmcp's `docs/ROADMAP.md` (Phase 9), looksatwords' `docs/open-questions.md`.
`perspectives/2026-09-21-landing-the-slice.md` is what the landing found.

## 1. Residue of the landed slice — small, and each is a session's first hour

| what | where | done when |
|---|---|---|
| **A stranded branch inside codecartographer's governance submodule clone** | `adr/one-graph-path`: two commits of 2026-08-25 amending `adr/DRAFT-rad-integration.md`, on no remote — `check_submodule_pins.py` reports it as *at risk* on every local run. The record it amends is the one Phase 3 begins with | read on the workstation that holds it; what still applies is carried into the Phase 3 record on a pull request based on `project/codecartographer`, and the branch is then pushed or deleted, never left as the only copy |
| **The `topology` address kind** in the corpus's address grammar | `docs/ref/addresses.md`, `project-seed/address-vectors.json`; qmcp #36 says so beside its constant and its shared-vectors test will read the new vector | qmcp's `tests/test_addresses.py` passes against the pinned vectors with the kind present |
| **A codecarto row in `dossier.sources`** | `the-third-side.md` step one; nothing in codecartographer changes | `dossier sources` lists the web window, reachable or not, with a reason when not |
| **The seed's `adr-lint.yml`, `one-pr-check.yml` and `leak-check.yml` on a project with a private submodule** | codecartographer's copies depart from the seed at the checkout step — `submodules: false` and a governance-only init — for the reason stated there; the seed's `submodule-check.yml` already takes that shape | the three seed copies take the same shape, or `project-seed/ci/README.md` names the departure as the known exception |
| **dossier's public test suite names two private repositories** | `tests/core/test_overview_redacts_private.py`, the fixture rows; pre-existing | the fixtures name invented repositories, as that file's newest test already does |

## 2. Phase 2 — the live flow on the shape

**What.** A topology is drawn as a shape; the harness knows what is running
through it. `GET /v1/invocations` and `GET /v1/human/requests` already exist and
every row carries an address (`owner/repo/invocation/<id>`,
`owner/repo/ask/<id>`). The window joins those addresses to the boxes it drew
and shows run state on them — the `idle / active / success / failed` channel
`SystemRenderer` already has for the PAM view, moved onto the one canvas as an
extension rather than a second renderer. A Harness panel shows recent runs and
the human queue **read-only**, including how many rows the harness held back
(`dossier.human`'s `Reading.more` is the model).

**Where.** codecartographer: a `web/src/features/graph/extensions/` extension
that overlays state by address; a `harness_panel.ts` beside the estate panels,
through `plotWith` like the rest; `qmcp_client` gains `invocations()` and
`queue()`; `estate_service`'s harness seam grows the two routes in its
`routes` list. qmcp: nothing for polling. **Polling first**, because it needs
nothing from the harness; an event stream (`/v1/events`, SSE) second, because
it is cleaner and is one more surface to govern — decided on 2026-09-20.

**Read first.** `feat/the-monitor-derives-the-system` in the codecartographer
clone (unpushed, 2026-08-27): `codecarto/services/system_composer.py` and
`web/src/features/graph/services/derived_system.ts` are the idea — a system
derived from what a repository holds, PAM as one definition among others. It
edits a renderer `main` deleted, so it is read, not merged.

**Done when.** A stub harness fixture whose invocations name box addresses
turns those boxes' state on the canvas (browser test, on the non-default
ports); a fixture whose invocation names an address no box has is **reported
in the panel, never dropped**; the queue panel shows the held-back count from
a fixture that pages; the overlay is a `BaseExtension` and no new renderer
exists (`test_boundaries.py`'s canvas-import guard stays green). Nothing in the
window posts to the queue.

**Traps, from the retrospective.** Commit before mutating; delete `dist-pure/`
before trusting a green pure test; the Graph tab must be *active* for a node to
be visible (`focusDockPanel`); a source directory named like an API prefix is
proxied to the backend.

## 3. Phase 3 — the topology designer

**Read first (3a).** A Designer panel that lists what `/v1/orchestration/plane`
declares: each shape with `status`, what it spends, writes or decides, its
`needs` and what supplies each; a REFUSED shape drawn refused, a BRAINSTORM
drawn as a proposal; `/v1/orchestration/runnable?workers=&budget=&model=` as a
"what could run with this hand" control. Nothing here is computed in the window
— the plane is the harness's, and `drift` (`stubs`, `undeclared`,
`unregistered_types`) greys a shape whose declaration lies.

**Author (3b).** Compose boxes and arrows in the harness's vocabulary
(`input/worker/gate/store/output`; `flow/feedback/refusal`) on the canvas. The
form for a shape's `config` is built from `GET /v1/topology/schema/{kind}`;
the design saves through `POST /v1/topologies` and reloads through `GET`; the
response's `capability` block is the plane's verdict and is shown as given.
**Saving a refused shape is allowed and running it is not** — the harness says
so in the response; the window renders that, adds nothing.

**The authored verbs.** rad #6 proposes an authored-graph mode in which
`add-node`, `reverse` and `edit-label` are honest. Its first `Pends on` item is
codecartographer's own record carrying the divergence in its `Pends on` row,
naming `rad` — the host-side half of the standard's §5.5 channel. Do that first
(a pull request on `project/codecartographer`), then build the verbs in
`rad/host/` with `MenuContext.graph: 'authored' | 'derived'` set per canvas.
Derived graphs offer them **disabled, never substituted**.

**Done when.** A design saved in the browser reads back from the harness with
the same config; a `council` design shows the refusal sentence verbatim; the
conformance suite stays green with the new verbs present and disabled on a
parsed map; `test_boundaries.py` stays green (the window still stores nothing
— the design lives in the harness).

## 4. Phase 4 — manipulation

Run a shape whose plane status is `runs` (`delegation`, `crosscheck`) against
declared workers and a declared budget, through the governed seam, and watch it
in Phase 2's overlay; its draft lands in the human queue. **Every decision is
the harness's:** an execution route in qmcp (not yet written), the spend
declared and consented there (`records/DRAFT-no-unattended-spending.md`), the
refusal of a shape against an attested act asked of `orchestration.refuses` at
run. Nothing in the window turns a draft into a decision, and **answering the
queue from the web is deferred by decision** — build nothing for it until it
has been reviewed.

## 5. Phase 5 — cartography and chrestomathy

**In codecartographer.** The `annotate_lexicon` toggle into the main parse
flow (it lives only in the legacy control panel today); lexicon-layer colouring
as legend rows; a Chrestomathy panel: choose a construct — a layer, a lexicon
group — and see it across every language with a lexicon; a third language's
lexicon in `codecarto/data/lexicons/` (`docs/llm/roadmap/lexicon.md`, *Adding a
language*).

**The looksatwords bridge, both ways.** A thread → the repositories it was
about (`GET /v1/topology/relations/{subject}` on the harness, weighted) → the
code map of one; a file or symbol → the threads that spoke of it, with the
topics each carried (`GET /api/harness/threads/{source}/{thread_id}/topics` on
the prose reader, landed in #23). The join is the address. The prose seam
already has a row in the Estate table with no panel; this is the panel.

**Done when.** The Estate table's prose row has a panel; a thread's topics
draw on the canvas with the same caveat discipline as every other seam; a
construct chosen in one language shows its neighbours in the others.

## 6. Phase 6 — the triangle, executed

One walkthrough page showing a change cross the panel, the harness and the
map, run by the ordinary test command. **Where it lives is still open**
(`the-third-side.md`'s question 8): `dossier/walkthrough`, `qmcp/walkthrough`,
codecartographer, or this corpus's `walkthrough/`.

## 7. Standing constraints

- **Nothing reaches `main` without the human's explicit approval.** Pull
  requests are opened green and assigned; the merge is a human act, said in
  the session and in pages like this one, **never in a pull request body**
  (`check_pr_voice.py` refuses it; `handbook/async-contract.md` §3).
- One open pull request per repository, per contributor. At the stamp above
  the only open slot in the repositories named here is the one carrying this
  page.
- Identity, not reachability, for every server; never a default port.
- Human-only contributorship on every commit; a `Tools:` note where the
  artifact calls for one.

## 8. What could not be verified here

- Whether the voice check catches the *third* person addressing the
  contributor by name. It does not try to; that is its stated blind spot.
- Whether the two retrospectives landed by the carrying pull request still
  describe a live state — they are dated 2026-08-15 and were read as records
  of that day, not re-derived.
