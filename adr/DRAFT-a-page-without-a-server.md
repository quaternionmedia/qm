# DRAFT — One page without a server draws the graphs and addresses other apps hand it

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-10-30 |
| **Pends on** | The origin the page is published from: this repository's GitHub Pages, which its owner enables, or the corpus's site, which the corpus decides (§8) |
| **Principle** | `seams-on-standard-protocols`; `public-by-default`; `minimal-legible-deliverables` |

## Context

codecartographer's window draws only what its backend serves. Every graph it
opens arrives through a route (`web/src/state/api_base.ts`), its boot asks
several of them, and every layout is calculated in Python
(`PositionService`, `show_layout`) and delivered as node positions: the canvas
has no layout of its own (`streaming_renderer.ts`, "Expects backend-computed
(x, y) positions"). A reader with no codecarto running on their own machine
sees a graph only as a picture someone exported.

`docs/scale.md` turns that into a limit. Its rules 2 and 3 send every view
deeper than a page can hold, a family to every symbol or the whole corpus, to
"the live window", linked by its address and drawn by no page. That link leads
only to a server on the reader's own machine.

And an app with a graph to show, or a reader to point at one, has no way to
hand it to the window. The window takes no message, reads no graph document by
URL, and opens no file of graph data; the one parameter it reads is `?show=`,
which it answers from a route.

What already holds, read on 2026-10-30 at `evolve/shared-imports`:

- **The renderer draws a positioned gJGF document with no network.**
  `PlotActions.handlePlotData` takes any document `D3GraphRenderer.canHandle`
  accepts, gJGF's node map or a flat node list.
- **An exported show document's estate views are the route's own answer,
  positioned**, and a project's code view is positioned too. A family's code
  view and the corpus's full view hold a pointer to their projects' code views,
  which the backend composes and lays out again (`family_code_graph`,
  `show_layout.pack`).
- **The corpus's site serves every show document**, at
  `https://quaternionmedia.github.io/qm/show/<subject>/show.json`, with
  `access-control-allow-origin: *`: a page on any origin can read them.
- **The window's address grammar (`show_address.ts`) and rad's `Intent`
  (`rad/core/types.ts`) are already data**: pure, tested, and, in the
  `Intent`'s own words, able to be "sent over a wire".
- **The build names its assets from the root of an origin.** Its `base` sits
  inside `build:`, where Vite does not read it, so the built page works only at
  the root of the host that serves it.

## Decision

### §1 The page

**`view.html` is a second page of the window's build**: the canvas, its
legend, the producer's caveat and the breadcrumb, drawn by the window's one
renderer, and nothing that asks a route. It asks no codecarto route at all,
holds no credential, writes nothing, and stores no graph. The dock stays the
window of a person running codecarto; this page is the window of every other
reader, and of other apps.

### §2 What it draws

**A positioned graph document, drawn as given**: a show document
(`show.json`, schema 1) and one of its views, or a gJGF document as a
`/.../gjgf` route answers it. The layout stays where it was calculated, in
whatever made the document; this page calculates none. A node with no position
is placed on its depth ring, as the canvas places one already, and the page
says how many it placed so.

### §3 Four ways in, one reading

Each way in hands the same reading and the same checks:

1. **An address.** `view.html?show=<address>` reads
   `<docs>/<folder>/show.json` and draws the view the address names. `<docs>`
   is the corpus's published show folder unless `?docs=<url>` names another.
   The grammar is `show_address.ts`'s, and nothing else parses an address.
2. **A document by URL.** `view.html?doc=<url>`, with `&view=` choosing a show
   document's view.
3. **A message**, from the window that embeds the page or opened it (§4).
4. **A file**, dropped on the page, opened, or pasted.

### §4 The messages

**An instruction is a document, an address or an intent, and the page adds
one verb: selecting nodes by id.** Every message is a JSON object carrying
`"codecarto": 1`; anything else posted to the page is ignored, since other
scripts post messages too.

| `op` | carries | does |
|---|---|---|
| `load` | `document`, and a `view` for a show document | draws it, as a file would be drawn |
| `show` | `address` | opens it, as `?show=` does |
| `select` | `ids` | frames those nodes and makes them the selection |
| `intent` | an rad `Intent` | runs it through the ring's own router, `createIntentRouter` |

A message may carry an `id`, and the page answers it with `re: <id>`. The page
posts these to the window that handed it the graph:

| `event` | when | carries |
|---|---|---|
| `ready` | it takes messages | the version, and the ops it takes |
| `drawn` | a drawing settles | the subject, its nodes and edges, and the nodes it placed with no position |
| `selected` | the reader selects | the ids |
| `opened` | the reader opens another showgraph | its address |
| `refused` | a message or document it cannot use | a problem and a remedy |

A new version adds ops and events; it changes none.

### §5 Who may hand it a graph

**Any origin, named.** The page holds nothing a sender could take and writes
nothing a sender could change, so the most a sender can do is make it show a
graph. It therefore always says who handed it what it shows (the URL it read,
the file's name, or the sending window's origin) beside the producer's caveat,
which it shows verbatim. A page that embeds it can narrow it with
`?from=<origin>`. A document is data: a label or a hover is text, never markup,
and nothing in a document runs.

### §6 Its seams

HTML's `postMessage`, and `fetch` over HTTPS, carrying JSON: gJGF, the JSON
Graph Format's shape as `GraphSerializer` writes it, and the show document.
Both pass the replaceability test. Any app that can post a JSON message or
serve a JSON file drives the page without codecarto's code, and a viewer
written from scratch, reading the same documents and taking the same messages,
replaces it.

### §7 Its reference is tested

`docs/api.md` states the messages and the documents the page reads. A test
reads that section against the page's own table of ops and events, and fails
when they differ, as `tests/test_docs_routes.py` holds the routes.

### §8 Where it is published

*Pends on the origin.* The build serves the page from any folder of any static
host: it names its assets relative to itself. Two origins are open: this
repository's GitHub Pages
(`https://quaternionmedia.github.io/codecartographer/view.html`), published by
a workflow from `main` once its owner enables Pages; or the corpus's site,
which already serves the documents. Both are `quaternionmedia.github.io`, so
either reads the documents as its own origin's.

## Consequences

- **A deeper view links to a page any reader can open.** The corpus's pages
  link `view.html?show=<address>`, and the reader's browser fetches the
  document only when they follow the link, so the linking page's own cost is
  unchanged. Rule 2's live window stops meaning a server on the reader's
  machine.
- **Only positioned views open there at first**: each subject's estate view,
  each imports view once it is exported, and a project's code view. A
  family's code view and the corpus's full view are composed and laid out by
  the backend, and the page refuses them by name, with the remedy of opening
  them in codecarto, until a record decides how they are positioned for it:
  written out positioned by the export, or laid out in the browser. That record
  measures both first (`docs/scale.md` rule 11).
- **An app with no layout of its own gets depth rings**, and the `drawn` event
  tells it for how many nodes. Accepted: a layout in the browser is a second
  definition of a layout Python calculates, and the page would draw a graph
  differently from the export it is linked from.
- **It is a second page to keep building**, and its boot must stay free of
  routes as the window grows. A browser test holds that (below).
- Obligations created:
  - the service inventory in this project's adoption record names the static
    host, with its ownability answer: any static host serves the same files;
  - a workflow builds and publishes the page, beside the three governance
    workflows and never one of them;
  - the build's `base` moves to where Vite reads it, relative to the page, and
    a test opens the built page from a subfolder of a plain static server;
  - a browser test opens `view.html` with every codecarto route refused, and
    counts the requests made to them: none;
  - a host page among the browser tests' fixtures embeds the page, drives
    every op, and is answered with every refusal.

## Alternatives considered

1. **The whole window, its server optional**: the dock booting with no
   backend and hiding each panel that needs one. Lost because the boot asks its
   routes and most of the panels need them, so every panel would carry two
   behaviours and two sets of tests, and an app that embeds the window wants a
   canvas, not a dock.
2. **A hosted codecarto server for readers.** Lost because it is a server to
   run, secure and pay for (`no-unattended-spending`), serving documents a
   static host already serves. `/repo/tree?url=` reads a directory on the
   machine it runs on, which is right on a person's machine and wrong on a
   public one. And every reader of a static site would depend on it being up.
3. **Layouts in the browser now**, d3's packing and forces beside the canvas.
   Lost for now, not for good: each is a second definition of a layout Python
   calculates, and the page would draw a graph differently from the export it
   is linked from. The first revision trigger reopens it.
4. **A component other apps import**, a custom element or a library. Lost
   because each app would ship the renderer and d3 at its own version, in its
   own build. A page by URL is one version, opened as a link or in an iframe,
   from any language that can write a URL or post a message.
5. **The graph in the URL's fragment.** Lost as a way in: the places links
   travel (chat, mail, previews) cut them short long before a code map's size,
   and the graph would sit in every history and log the link passes through. A
   small graph could take it later; it is not one of the four.
6. **`BroadcastChannel`, or a socket.** A `BroadcastChannel` reaches only
   pages of the same origin, and a socket needs a server. `postMessage` is the
   channel between origins that every browser has.

## Revision triggers

- An app hands the page graphs without positions, as its `drawn` events
  report: the layout in the browser (alternative 3) reopens.
- A view the corpus's pages link has no positioned document the page can read.
- The page's script, gzipped, grows past a fifth of the window's.
- A browser restricts `window.opener` or `postMessage` between origins in a
  way that closes one of the four ways in.
- The chosen host stops serving the page, or changes its terms.
- A second version of the messages is needed.

## Amendments

*None.*
