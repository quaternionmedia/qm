# Plan — the triplet: every family and project shown three ways

**What this is.** A proposal to give every family page, every public project
page and the families index on the corpus's docs site three views of the same
subject: the pictures a person picked (**showcase**), the graphs codecarto draws
(**showgraph**), and the terminal view dossier renders (**showtui**, a working
name). The pages become, in effect, codecarto's and dossier's README: each tool
is explained by showing it applied to the whole estate.

**What it is not.** A decision, a schema, or a change to any repository. It
sits in `plans/` the way `plans/the-web-window.md` does, with a pointer from
codecartographer's and dossier's roadmaps once a person accepts it. Its first
phase's local proof of concept is quaternionmedia/codecartographer#147, a draft
stacked on that repository's open stack.

**Stamped 2026-10-23** against `qm` `origin/main` at `bc38ab6`,
`codecartographer` `main` at `c5ed009` (open stack tip `dcf1ca3`), and `dossier`
`main` at `414be1c`. Re-derive before acting: the command that answers each
figure is named next to it.

---

## Decisions taken

Peter Kagstrom answered these in session on 2026-10-23.

- **The pair is a triplet, for now:** showcase for pictures, showgraph for
  graphs, showtui for the terminal. All three readings offered hold at once.
  The committed picture is paired with the interactive window. A page carries
  more than one graph. codecarto's view of a subject sits beside dossier's.
  *Stack and consolidate where possible, but keep every feature described.*
- **A project's showgraph draws all of it:** its place in the estate, a coarse
  code map, and its system diagram where it declares one.
- **A family's edges come from all three sources:** roster claims, declared
  seams, and measured dependencies, each drawn so that it reads as what it is.
- **The interactive half is a static viewer on GitHub Pages, after a local
  proof of concept.**
- **The pages are the READMEs' tour** of codecarto and dossier.
- **The default showgraph is every family at once:** the whole estate, from
  which a family or a project is a step in.
- **Local until there is a demo, then drafts:** the work stayed on local
  branches until the proof of concept drew in a browser. On 2026-10-24 both
  halves were opened as draft pull requests, assigned to their author, with no
  review requested.

---

## What exists, and what this reuses

### In the corpus (`qm` `main`)

| piece | what it does today |
|---|---|
| `uv run qm cookbook docs/families --site --write` | Generates the docs site's family pages, project pages and the index, from `families.json`, `status/inventory.yaml` and `ci/showcase.yaml` |
| `ci/showcase.yaml` | A person picks each project's pictures: files on that project's default branch, shown from `raw/HEAD`. A listed file the branch does not hold yet is left out. Most projects have no entry, and their page says so (`git show origin/main:ci/showcase.yaml`) |
| `families.json` schema 2 | Families nest (`performing` contains `instruments`, `performer-display` and `show-control`), and a repository may claim several families. Neither shape is a tree |
| `ci/palette.py`, `ci/dashboard_style.py` | One palette for the site, the family pictures and the dashboards. Every family has a hue in both themes, plus the `ok` / `warn` / `unknown` states |
| `ci/interop-registry.yaml` | Contract surfaces and the repositories on each. One surface today: rad's interaction contract, published by `rad` and implemented by codecartographer and dossier |
| `ci/capability-registry.yaml` | The capability rungs, per repository. codecarto already draws it |
| The site | Static, published at `https://quaternionmedia.github.io/qm/` (`gh api repos/quaternionmedia/qm/pages`) |

Open in `qm` right now, and relevant: #215 renames `civic` to `commons`. So
family names are read from the document every time, never written into a
producer.

### In codecartographer

Every estate-style route already follows the two rules each showgraph inherits.
**Serve a graph, not a picture:** a networkx graph goes through
`GraphSerializer` and comes out as gJGF with positions. **An absence is a
sentence:** a 200 whose results carry `problem`, `remedy` and `where`. Reused
directly:

- **Seams:** `/capabilities`, `/overview`, `/topology` and `/estate`, with
  liveness rows in `estate_service.SEAMS`.
- **Compound outlines:** `CompoundLayoutManager`, driven by `depth` plus
  `contains` edges. The Cargo graph (workspace 0, crates 1, targets 2) is the
  existing non-code template for family, then member.
- **The derived system monitor:** `/system/*` and `system_composer.compose`.
  The worked case is `moat`, read from `Chart.yaml`, ArgoCD, Terraform and
  Dockerfiles. It is only on the open stack (#105, #107).
- **Path-based node ids:** without them, every folder named `src` collapses into
  one node. Only on the open stack (#107).
- **One renderer, already SVG:** `streaming_renderer.ts` and `system_renderer.ts`
  draw with d3 into SVG elements, so the real renderer's output can be
  serialized as an SVG file with no second drawing path.
- **A replay path that needs no backend:** graphbase snapshots rebuild
  `appState.graphData` from gJGF and redraw without parsing
  (`layout_context.ts`, the snapshot load). A static viewer is that path with
  the source swapped.
- **A browser harness:** the e2e suite and its screenshot tour (#138) already
  drive the real window headlessly on non-default ports.

What is missing:

- **No stable address.** The web app has no URL routing, so nothing can link
  into a particular graph.
- **One reader of the corpus**, `capability_service`, at a hard-coded relative
  `governance/qm`, with no env var.
- **The only reader of `families.json` is red.** `npm run test:families` fails
  1 of 4 against today's `qm`: `2 !== 1`, because `qm` moved to schema 2. CI
  does not run it: `web.yml` says a runner has no sibling `qm` clone, so every
  case would skip. C0 below gives it the clone, or a fixture generated from one.
- **The governance pin is behind:** `git -C governance/qm rev-list --count
  origin/project/codecartographer..origin/main`. So the submodule still carries
  schema 1.

### In dossier

- `App.export_screenshot()` returns SVG, rendered by Textual itself.
- `tests/core/test_published_screenshots.py` refuses a shipped picture of a
  view the app no longer has.
- `dossier.views` is the registry of views. The README already embeds two TUI
  SVGs.
- Nothing in dossier reads families: `git grep -n families.json -- src` finds
  nothing.
- `DOSSIER_DATABASE_URL` points the app at a database of the caller's choosing.

---

## Constraints inherited

None of these is new. The design is bounded by them.

1. **One renderer per leg.** Showgraphs are drawn by codecarto's web renderer,
   and showtuis by Textual. Nothing redraws either in Python.
   (`topology_router.py`; `plans/the-web-window.md` constraint 1)
2. **An absence is a sentence.** A leg that could not be produced shows what,
   why and where, never an empty frame, and never a borrowed picture standing
   in. (`adr/DRAFT-rad-integration.md` §4: offered disabled, never substituted)
3. **The vocabulary lives upstream.** Families, nesting, phase, attention,
   capability rungs, contract surfaces and hues are the corpus's. Producers read
   them as data and copy none of them.
4. **A family is a claim.** A measured edge never places a repository, and
   never moves one. (`records/DRAFT-a-family-is-bordered-by-what-it-drives.md`
   §1)
5. **What crosses between families crosses as a protocol.** A declared seam
   names its protocol. (same record, §5)
6. **The picture is drawn, not pasted,** and carries where it came from.
   (`ci/cookbook.py`'s docstring; `records/DRAFT-few-integers-in-durable-text.md`)
7. **Nothing machine-scoped reaches a committed page.** That covers dirty
   counts, unpushed branches, absolute paths and an operator's archive.
   (`ci/inventory.py`'s file boundary; the harness payload's `database` field
   is the counter-example)
8. **No private name reaches a public artifact.** A private member is counted
   and never drawn by name, the way the site's pages already treat one.
9. **Identity, not reachability.** A producer asks a server what it is before
   reading it. (`handbook/async-contract.md` §4)

---

## The design

### 1. Subjects

| subject | showcase | showgraph | showtui |
|---|---|---|---|
| the families index | none | the estate: every family, its nesting, shared members and seams | dossier's org overview |
| a family page | its members' picked pictures, as the cards show today | the family: members, subfamilies, shared members, seams, measured links | dossier's overview filtered to the family's members |
| a public project page | its picked pictures | three views: **estate**, **code**, **system** | dossier's view of that repository |
| a private member | none | an anonymous counted node in its family's graph, and nothing else | none |

Subjects are read from `families.json` and the inventory: every family it
declares and every public repository the site has a page for (`git ls-tree
--name-only origin/main docs/projects/`). A repository with no family is
`unstated`. The index counts it and names nobody.

### 2. One registry: `ci/showcase.yaml` holds all three legs

Showcase is where a person shapes a page, so the triplet's per-subject choices
go there rather than into a second file. The `pictures` leg keeps today's
shape. The other two default on and take optional overrides:

```yaml
defaults:
  graph:
    views: [estate, code, system]
    code: {depth: directory, node_budget: <set here, not in prose>}
  tui: {size: [120, 36]}

projects:
  carlos:
    pictures:                # today's list, unchanged in meaning
      - path: walkthrough/media/05-in-the-browser-menu.png
        caption: A whole rig from the back panels, with the radial menu open.
    graph:
      code: {exclude: [walkthrough/media]}
    tui: {view: <a name from dossier.views>}
```

Pictures stay picked. Graphs and TUIs are drawn, so their defaults apply to
every subject, and a person's entry only narrows or opts out (`graph: off`). An
opt-out is stated on the page. Today's top-level `projects: {name: [pictures]}`
form is read as `pictures:` until it is rewritten, so the change lands without
touching every entry at once.

### 3. One document per subject

Each subject has one **show document**. The page, the static viewer and the
checks all read that one document.

```json
{
  "schema": 1,
  "subject": {"kind": "project", "name": "carlos"},
  "provenance": {
    "claims":   {"repo": "quaternionmedia/qm", "commit": "<sha>", "digest": "<of this subject's own claim rows>"},
    "source":   {"repo": "quaternionmedia/carlos", "commit": "<sha>"},
    "drawn_by": {"graph": "codecartographer@<sha>", "tui": "dossier@<sha>"},
    "drawn_at": "<UTC>"
  },
  "views": {
    "estate": {"graph": {"...gJGF, with positions": "..."}, "metadata": {"caveat": "..."}},
    "code":   {"graph": {"...": "..."}, "metadata": {"depth": "directory", "truncated": 0}},
    "system": {"absent": true, "problem": "carlos declares no system codecarto reads",
               "remedy": "...", "where": "..."}
  },
  "files": {"estate": "estate.svg", "code": "code.svg", "tui": "tui.svg"}
}
```

- **The claims digest covers only this subject's own rows:** its families, its
  nesting, and its roster entry. An edit elsewhere in the roster does not stale
  every graph in the estate.
- **The schema lives in the corpus.** Its cases are generated by the real
  producer, never written by hand. That is the lesson of
  `project-seed/harness-payload-vectors.json`: two fixtures that each agreed
  with their own side and with nothing else.

### 4. The family showgraph

A family graph draws three bases on one canvas. Every edge carries its basis in
its metadata, and the legend names all three.

| basis | read from | drawn as | can it move a member? |
|---|---|---|---|
| **claim** | `families.json`: `contains` (family to subfamily, family to member), `member_of` for a repository in two families | compound outlines in the family's hue; `member_of` solid and thin | it *is* the placement |
| **declared** | `ci/interop-registry.yaml`, extended as below: a surface names its protocol and the repositories on it | a solid edge labelled with the protocol (MIDI, OSC, HTTP + schema, the rad contract) | no |
| **measured** | each member's manifests on its default branch: `.gitmodules`, `pyproject.toml`, `package.json`, `Cargo.toml`. Only a dependency that resolves unambiguously to an estate repository's URL is drawn | dashed, labelled with `measured from <file>@<commit>` | no |

Drawing rules the layout has to keep:

- **Nesting is depth.** `performing` is 0, `instruments` is 1, and a member is
  2. The compound layout already draws depth-0 and depth-1 outlines.
- **A shared member is drawn once.** On a family's own page it sits inside that
  family, marked "also in `irl`", which links to that page. On the index it sits
  outside both outlines, with one `member_of` edge to each. Placing it inside
  one would make the picture assert the function that schema 2 removed.
- **`governance/qm` is not an edge.** Every governed project vendors it, so
  drawing it would add one spoke per member and say nothing the governed badge
  does not. It is drawn as the badge.
- **Disagreement is drawn as a delta, in one direction only.** A measured link
  with no declared seam is a seam somebody has not stated: a delta, opened at
  `brainstorm` (`records/DRAFT-a-disagreement-is-a-delta.md`). The other way is
  normal and is not a delta, because MIDI and OSC never appear in a manifest.
  Neither side is rewritten to match the other.
- **A name that matches but does not resolve** (for example, a package named
  like a repository) is listed under the graph as unresolved, never drawn.
  Drawing a guess would be the measurement asserting a claim.

**Extend `ci/interop-registry.yaml` rather than add a seam registry.** Its
header already says it is *"contract surfaces, and every repository that sits on
one"*, which is what a family seam is.

- A surface gains `protocol`. Its `pattern` and `file` become optional.
- `uv run qm interop` reports a surface without a version pattern as
  *declared, unversioned*. That is never passing, because no version agreement
  was measured.
- A second registry answering "what crosses between these two repositories"
  would be two definitions of one thing, which `AGENTS.md`'s governance-gates
  section warns against by name.

### 5. The project showgraph: three views of one document

- **estate**: where the repository sits. It shows:
  - each family it claims, in its hue;
  - `phase` and `attention` (the claims) beside `recency` (the measurement),
    never merged;
  - its `project/<name>` branch, and its records grouped by status. A `Pends
    on` row draws an edge where it names an address, such as graphbase PR #8;
  - its capabilities and their rungs (`/capabilities` already draws these);
  - the surfaces it publishes or implements, and the substrate it is built
    with (rad, graphbase).

  For an ungoverned repository this view is thin, and it says so.
- **code**: the parse of the default branch at a stated commit, through the
  existing GitHub source, so no clone is needed. Directories are drawn, files
  are counted, and symbols stay in the interactive view. The node budget lives
  in `showcase.yaml`'s defaults. A repository past it is truncated at a depth,
  and the truncation is reported in `metadata.truncated`, not hidden. It needs
  path-based ids (#107).
- **system**: `system_composer.compose` where the repository declares a system
  codecarto reads. Today that is mostly `moat`, so for most repositories this
  view is an absence sentence. That is the honest reading, not a defect.

A Rust workspace reads better as its Cargo graph than as directories. Whether
`code` switches to `/cargo` when a workspace is present is a later refinement,
listed under Open.

### 6. The showtui

dossier renders the same subject through `App.run_test()` and
`export_screenshot()` at the fixed size `showcase.yaml` states, so the picture
is the TUI's own output.

- **Index:** the org overview.
- **Family:** the overview filtered to the family's members. dossier has to read
  `families.json` as data, the way codecarto's families test does, and import
  nothing.
- **Project:** the view `showcase.yaml` names from `dossier.views`.

**It runs against a throwaway database populated only from the subject's
public data** (`DOSSIER_DATABASE_URL`). Never the operator's archive. An
operator's dossier holds private repositories and local paths, and a screenshot
of it is constraint 7 broken in a single file.

### 7. Producing, landing, checking

- **Producers.** codecarto and dossier each gain one export command over the
  same subject list:
  - `codecarto show export --corpus <qm checkout> --subject <name|all> --out <dir>`
  - `dossier show export …`, the same arguments.

  The SVG comes from the real renderer, run headlessly by the harness the e2e
  suite already has. The show document comes from the same graph the renderer
  drew.
- **Orchestration.** One command in the corpus,
  `uv run qm cookbook docs/families --site --write --show`, runs each producer
  from its sibling clone, the way `qm interop --verify` runs `proves.command`.
  It records a producer that is absent or fails as that leg's absence sentence.
  So codecarto absent is reportable as absent, and the page still builds.
- **Where it lands.** Recommended: `qm` `docs/show/<subject>/`, served by the
  corpus's own site. That gives one origin for the pages, the documents and,
  later, the viewer, and the pages survive a producer being unreachable. The
  alternative is under Open.
- **What `qm cookbook --check` can do without the producers:**
  - Every subject has a show document, or a stated absence.
  - Every document's claims digest matches the subject's current rows. A
    picture showing the wrong members is a page that stopped being true, and
    fails.
  - No private name and no machine-scoped field appears in any document (the
    `private-names` gate, pointed at `docs/show/`).
  - The source commit's age is shown, and budgeted the way
    `handbook/generated-documents.md` budgets a generated document. An old code
    map is a dated picture, not a false one.
- **What it cannot do:** re-draw a graph. That needs codecarto and the
  estate's clones or the host, so it is local and advisory, as `family-suite`
  and `interop --verify` already are.
- **Refreshing is a protocol, not a gate.** It is invoked by a person, takes
  judgement about what changed, and produces dated artifacts. It gets a
  `ci/protocol-registry.yaml` entry with a `cadence_days`, so "the triplet was
  last refreshed" is derived from a dated run rather than remembered.

### 8. The interactive half

- **Local proof of concept first.** codecarto gains:
  - a `show` seam: `/show/{kind}/{name}`, plus a row in `estate_service.SEAMS`;
  - a Show panel that lists the subjects from `families.json` and draws each
    view on the one canvas;
  - **URL routing**, which does not exist today:
    `?show=project:carlos&view=code` opens that view.

  **The default is every family at once.** A bare `?show`, and a Show panel
  opened onto an empty canvas, draw the index. A family or a project is a step
  into it.

  It reads the corpus through one resolver. The governance pin is the default,
  because it is the state the project adopted. `CODECARTO_CORPUS` replaces it
  with another checkout, such as the sibling `qm` clone when the pin is behind
  on schema. Every drawing says which commit it read, and whether it was the
  pin. The reader accepts schemas 1 and 2, so a pin behind on schema still
  draws, flat. The proof of concept may overlay machine-scoped state (dirty,
  unpushed) because nothing in it is committed, and it labels that state as
  this machine's.
- **Then the static viewer on Pages.** A build of the web app with no backend:
  - It loads a show document through the snapshot-replay path, with positions
    already in the document.
  - It is deployed to codecartographer's Pages, which is issue #30 closing.
  - It fetches `https://quaternionmedia.github.io/qm/show/<subject>/…`, the
    same origin, so it needs no CORS arrangement.
  - Each SVG on a page links to it.

  The viewer is read-only. It has no parse, no Open panel, and no rad verbs
  that edit.

### 9. The READMEs

- **codecartographer's README** opens on the index showgraph and links the
  family pages as its tour. Its own showcase entry lists its own showgraphs, so
  its project page stops saying it has no pictures.
- **dossier's README** opens on the index showtui.

Both keep setup on one page (#123 makes the README an on-ramp) and stop
carrying screenshots that only the README uses. dossier's
published-screenshots test extends to the showtuis, so a shipped picture of a
deleted view still fails.

---

## Consolidation, named

| becomes one | from |
|---|---|
| the triplet's registry | `ci/showcase.yaml`, grown, rather than a `showgraph.yaml` and a `showtui.yaml` |
| the seam declaration | `ci/interop-registry.yaml`, extended, rather than a new seam registry |
| the corpus reader in codecarto | `capability_service`'s hard-coded path, the families test's sibling path, and the new show seam, resolved in one place with one schema check |
| the drawing path | the web renderer, run headlessly for SVG and statically for Pages. No Python SVG drawer for showgraphs |
| the static load path | graphbase's snapshot replay, with its source made pluggable |
| the browser harness | the e2e suite and screenshot tour (#138), for export and for the checks |
| the hues | `ci/palette.py`. codecarto reads the family hues rather than keeping a copy |
| the README pictures | the showgraph and showtui of the index |

The cookbook's own column chart (`families.svg`, the share governed per family)
stays. It is a chart, not a graph, and nothing here replaces it.

---

## Phases and the stacks

Each phase ends in something a person can open. Within a repository the pull
requests stack: each is a draft on top of the one beneath it, and only the
bottom one is ready. Across repositories the order below holds.

**Before any of it: codecartographer's open stack.** Forty of its pull
requests are one linear stack, each targeting `main`, and every one is red on
the one-pull-request gate (`gh pr list`; the `slot` job's log). The triplet's
codecarto work stacks on whichever single pull request survives that fold,
which is a person's call. It needs #105 and #107 from inside that stack.

| # | repository | slice | ends in |
|---|---|---|---|
| C0 | codecartographer | the families test reads schema 2 and runs in CI; one corpus resolver (`CODECARTO_CORPUS`), with `capability_service` moved onto it | a red test made green, seen red first |
| Q1 | qm | this plan, in `plans/` | a page |
| C1 | codecartographer | the show seam, the claims layer for the index, families and project estate views, the Show panel, URL routing | **POC 1**: every family opens locally from a link |
| Q2 | qm | `interop-registry` surfaces gain `protocol`; `qm interop` reports *declared, unversioned* | a registry a person can state seams in |
| C2 | codecartographer | the declared and measured layers, and the one-direction delta | **POC 2**: a family graph with all three bases |
| C3 | codecartographer | the code view (coarse) and the system view | **POC 3**: a project page's three views, locally |
| D1 | dossier | the family filter, from `families.json` as data | the overview filtered to a family |
| D2 | dossier | `dossier show export`, from a throwaway database | a showtui per subject |
| C4 | codecartographer | `codecarto show export`: show documents and SVGs, through the real renderer | a `docs/show/` tree on disk |
| Q3 | qm | the show-document schema, and cases generated by C4's real producer | a contract both sides run |
| Q4 | qm | `showcase.yaml` grows `graph` and `tui`; the cookbook lays out the triplet with absences; `--check` as in §7; the refresh protocol | the triplet on every page, locally built |
| Q5 | qm | the first generated `docs/show/` | the triplet on the published site |
| R1 | codecartographer, dossier | the READMEs | each README opens on the estate |
| C5 | codecartographer | the static build, and the Pages workflow | **the viewer**: every picture opens interactively |

The governance pin bump in codecartographer (merging `qm` `main` into
`project/codecartographer`) is a human-reviewed step. It has to precede any
slice that reads the submodule rather than the sibling clone. The proof of
concept reads the sibling clone, so it does not wait on the bump.

## What must change in the neighbours

| repository | change | why codecarto cannot do it instead |
|---|---|---|
| `qm` | the plan; `interop-registry` gains `protocol`; the show schema and its cases; `showcase.yaml` grows; cookbook layout and checks; a protocol entry; `docs/show/` | the claims, the registry and the pages are the corpus's |
| `dossier` | a family filter; an export command; its README | the TUI is dossier's renderer |
| each project | nothing | showgraphs read the default branch from the host. Writing into thirty repositories, most of them unadopted, would be adoption by side effect (`ci/workspace.yaml`: *presence here is not adoption*) |

## Testing posture

Every new signal gets a fixture in which it reports bad. Each guard is broken
once, seen red, then restored, and the mutation is written beside it.

- `families.json` at a schema the reader does not know. **This one is red
  today.**
- A subject whose producer is absent, unreachable, or answers as something else
  (identity, not a port).
- A claims digest that no longer matches: a member moved.
- A private member: no private name in any document or SVG.
- A machine-scoped field: no absolute path and no dirty count in any committed
  document.
- A shared member: drawn once, with a `member_of` edge to each family.
- A measured dependency that resolves only by name: listed, not drawn.
- A measured link with no declared seam: one delta at `brainstorm`, and the same
  delta on a second run, not a second one.
- A showtui of a view dossier no longer has: refused by the published-pictures
  test.
- The static viewer opened with no backend: it draws, and asks nothing of a
  server.

Structural checks come first, because they need no browser: schema, digests,
names and fields. Browser tests come after, on non-default ports, with the
server's identity asserted before anything is measured.

## What must not be built

- **A family inferred from a graph.** Measured edges never place a repository.
- **A winner between declared and measured.** Both are drawn, and the gap is a
  delta.
- **A second renderer.** No Python SVG drawer for showgraphs, and no screenshot
  of the TUI taken by hand.
- **A borrowed picture where a leg is absent.** The sentence is the content.
- **The operator's archive in a showtui,** or any machine-scoped fact on a
  committed page.
- **Write access in the viewer.** No parse, no authored verbs, and no answers to
  the human queue. `plans/the-web-window.md` defers that, and this plan does not
  reopen it.

## Open

1. **The third leg's name.** *showtui* is a working name. Also open: whether
   *showcase* becomes the word for all three legs, with pictures, graphs and TUI
   as its parts.
2. **Where the drawn legs land.** Recommended: the corpus's `docs/show/`.
   - What it buys: one origin, and pages that survive an absent producer.
   - The alternative: each producer commits into its own repository, and the
     corpus links `raw/HEAD` the way showcase pictures are linked. That keeps
     each tool's output in its own history, at the price of three places to
     refresh and a viewer reading across origins.
3. **Which dossier view is a project's showtui.** It is named per project in
   `showcase.yaml`, but its default wants dossier's maintainer.
4. **Private repositories locally.** Whether the proof of concept may draw a
   private member's triplet on the operator's own machine, never committed.
5. **Rust workspaces.** Whether a repository with a Cargo workspace gets its
   Cargo graph as its code view.
6. **The refresh cadence,** set as `cadence_days` in the protocol entry.
