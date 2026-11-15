# Image models through qmcp: a plan

*A prototype of slice 0 and the journeys is built, against a simulated qmcp: the
observation format (`apothecary/evidence/`), the plain colour reader
(`apothecary/vision/colour.py`), the client with every way qmcp can be missing
(`apothecary/finders/`), the Models window and its ring, and `apothecary
vision`; [the models checklist](../models-checklist.md) walks them. The rest of
this page is not built: MCP to a real qmcp, `vision check` and trust, the `qmcp`
finder, asking about a rig's face, a site's own words, and keeping what was
asked.*

## What this plans

Apothecary reads pictures with pixel arithmetic: the plain finder's shapes
(`apothecary/vision/plain.py`) and the rig reader's knobs, faders, switches and
plugs (`apothecary/rig/look.py`). Both are measured, both need nothing but
Pillow, and neither names a thing, counts things of a kind, or says what
something is made of.

This plan adds a layer through which image models answer those questions: how
many of a kind a picture shows, how big, what shape, what material, what colour,
what it is, whether something covers it, and where it is in another camera's
picture. The models are engines that qmcp, the QM family's tool server,
serves as tools on this machine. Apothecary asks qmcp only when a person asks it
to look closer, and only when qmcp is configured and answering; otherwise
apothecary does exactly what it does without the layer. What comes back is a
list of **observations** in the family's observation format, each about one
subject and one property, with a value, a unit, a confidence, an origin and a
time. Apothecary weighs them as evidence beside its own readers' and never above
a person's word. The working-space layer, planned beside this one
(`project/plans/working-space-view-2026-10-30.md`), takes them in the same format.

**This extends [the finders plan](photo-finders-local-models-2026-09-21.md)**
and keeps every rule of it: a model is an engine, a subprocess or a server on
loopback, never imported into `apothecary/`; OpenCV is not imported either;
the paid-service hook stays shut. Its weights rule is narrowed: qmcp fetches a
model's weights on a person's word, from a list it pins, and apothecary never
touches them. This is
that plan's loopback reach, made once, through qmcp, and qmcp is the one door:
every model's answers reach apothecary through it, so that plan's direct client,
`LoopbackModel`, is not built. This replaces that plan's phase 2, a namer over
loopback, and reaches its phase 3's Open Inference Protocol server through
qmcp's adapter rather than from apothecary. Its phases 0 and 1 stand: the seam
hardened, and markers, which are arithmetic in a runner the seam starts, not a
model.

What moves is where the standard protocols sit. Apothecary speaks the Model
Context Protocol (MCP) to qmcp, and qmcp speaks the OpenAI-compatible chat API
or the Open Inference Protocol to the engines. Model output reaches apothecary
through one door, the one charter `shrink-the-black-box` names: what cannot be
moved into a command goes through qmcp, which records what passes.

## The seam: qmcp's vision tools, over MCP

### The transport

qmcp's server lists its tools at `GET /v1/tools` and runs one at `POST
/v1/tools/{name}`, in a shape of its own (qmcp's `docs/tools.md`). Its MCP
server, `qmcp_mcp.py`, is a stdio server for working on the qmcp repository,
whose `invoke_server_tool` forwards to `/v1/tools`; qmcp's own server does not
speak MCP. Stdio is not the door: a client that starts its own qmcp gets its own
queue and its own invocation rows, the two-clones case of the monitoring record.

The layer's transport is MCP's streamable HTTP, served by qmcp's own server on
loopback (qmcp's slice 2):

- the vision tools are MCP tools, each with an input and an output schema, which
  together are the contract `qm.vision` version 1, and a tool's result is its
  structured content;
- a call through MCP and a call through `/v1/tools` take one path in qmcp, so
  each writes its invocation row, and the row's id comes back in each
  observation's evidence;
- the asker's deadline is MCP's cancellation: past it, apothecary sends
  `notifications/cancelled`, and qmcp passes it on to the engine;
- a picture is read under MCP's roots: apothecary declares the folders it may
  name, the picture root, and qmcp reads nothing outside them;
- qmcp checks each request's `Origin` header and binds to loopback, as the
  transport's specification asks of a server on the machine it serves.

`/v1/tools` keeps serving the same tools to qmcp's other clients.

### `vision.models`: what can be asked

No input. The result lists every model qmcp can reach, each with:

- `name`, `version`, and `weights_sha256`, the digest of its weights file;
- `licence`, the weights' SPDX expression, and `engine`, the server that runs
  it, with its version;
- `answers`: the properties it can be asked, and, for a property answered in
  words, the vocabulary its words come from;
- `warm`: whether it is loaded, so a first call's seconds are not taken for
  every call's.

An empty list is an answer: qmcp is up and has no model.

### `vision.observe`: a picture, its regions, and what is asked

The request:

```json
{
  "contract": "qm.vision",
  "version": 1,
  "picture": {"path": "<the picture root>/captures/2026-10-30T14-02-11.png",
              "sha256": "<digest of the file>", "taken": "2026-10-30T14:02:11+00:00"},
  "regions": [
    {"id": "uno/barrel", "box": [0.41, 0.22, 0.47, 0.31]}
  ],
  "asked": [
    {"property": "quantity", "of": "plug"},
    {"property": "colour"},
    {"property": "material", "among": ["plastic", "metal", "rubber"]}
  ],
  "deadline_ms": 4000
}
```

- **The picture is a path**, with its digest. qmcp resolves its links, reads it
  only under a root apothecary declared, and refuses one whose digest is not the
  one asked about, since the file changed. It applies the picture's EXIF
  orientation, crops each region in memory, gives the engine the crop, and
  writes no copy. qmcp's rows keep the path and the digest, never pixels.
- **Bytes are the expansion.** A later contract version may carry each region's
  own pixels, base64 in the tool's arguments, in place of the path: for a
  picture qmcp cannot read (qmcp run as another user, in a container, or on
  another machine once what "this machine" means is decided), and for a region
  apothecary has already turned (a rig's face rectified through its pinned
  corners, which a model may read better than the raw crop). Bytes wait on qmcp
  recording them as a digest (qmcp's slice 6).
- **A region** is a box in fractions of the picture as it is seen, upright:
  left, top, right, bottom, from 0 at the top left to 1 at the bottom right, the
  convention of `FoundShape`. No box is the whole picture. Its `id` is the
  asker's, and comes back on every observation about it.
- **What is asked** is drawn from a closed set: `label`, `quantity` (with `of`,
  the kind counted), `size`, `shape`, `material`, `colour`, and `covered`,
  whether something stands between the camera and the region. A property
  answered in words may name `among`, the words it is asked among; without it,
  the model's vocabulary from `vision.models` applies. Apothecary always names
  it (*The words*, below).
- **No scale crosses the seam.** A size comes back in fractions of the picture.
  Turning it into millimetres is apothecary's, with a reference a person stated
  (*Which measurements come first*).
- **`deadline_ms`** is how long the asker waits. qmcp passes it to the engine as
  a timeout, and apothecary cancels the call when it passes.

### The answer

The tool's structured content. Each observation is in the family's format,
`qm.observation` version 1 (*An observation*, below), about a sighting, since
qmcp knows a region and not what it is:

```json
{
  "contract": "qm.vision",
  "version": 1,
  "picture": "<the digest asked about>",
  "observations": [
    {"subject": {"sighting": {"picture": "<digest>", "region": "uno/barrel"}},
     "property": "quantity", "of": "plug", "value": 1, "unit": "count",
     "confidence": 0.91,
     "origin": {"kind": "guessed",
                "by": {"tool": "vision.observe", "model": "...", "version": "...",
                       "weights_sha256": "...", "engine": "..."}},
     "at": "2026-10-30T14:02:11+00:00", "recorded_at": "2026-10-30T14:05:40+00:00",
     "evidence": [{"picture": "<digest>", "path": "<as asked>", "box": [0.41, 0.22, 0.47, 0.31]},
                  {"qmcp_invocation": "<id>"}],
     "why": null},
    {"subject": {"sighting": {"picture": "<digest>", "region": "uno/barrel"}},
     "property": "material", "value": null, "unit": null, "confidence": null,
     "origin": {"kind": "guessed", "by": {"tool": "vision.observe", "model": null}},
     "at": "...", "recorded_at": "...", "evidence": ["..."],
     "why": "no model that answers material is loaded"}
  ],
  "elapsed_ms": 812
}
```

- **Every region has an observation for every property asked**, in the order
  asked. One that could not be answered is **unread**: `value: null` and a
  `why`, as the rig reader's `Seen` and `Plug` do. Unread is not a value, and an
  answer missing one is malformed.
- **`value` and `unit` go together.** A count is in `count`. A size is in
  `fraction`, of the picture's width, as `FoundShape`'s sides are. A colour, a
  shape, a material and a label are words whose `unit` names the list they were
  asked among. `covered` is true or false, with no unit. A model gives no
  `rgb`: a measured sRGB is a reader of pixels' alone.
- **`confidence`** is what the model reports of itself, from 0 to 1, as it gave
  it and never rounded up, or null when it reports nothing. It is a report, not
  a measurement; what apothecary makes of it is in the next section.
- **`origin.by.model`** names what answered, and is null only when no model was
  reached.
- **`why`** says why a value is null, as one of a fixed set: no model answers the
  property; the region is too small for the model, with its size in pixels; the
  model declined; the model answered a word outside the words asked among, with
  the word; the deadline passed; the picture could not be read, or is outside
  the declared roots, or changed; a size was asked of a model that gives no
  outline.

Apothecary refuses an answer whole when its `picture` is not the digest asked
about, its version is not one it reads, it names a region not asked about, or it
does not validate against the contract's schema. Nothing from a refused answer
is kept.

### `vision.match`: a region found again in another picture

Two pictures, each a path and its digest under a declared root, and a region in
the first; back come the regions of the second that show the same thing, best
first. The working-space plan asks it for a subject one camera sees with nothing
pinned in another camera's picture, that plan's suggested link, and a person
takes a suggestion before it becomes a link.

The answer is observations in the same format, about the first picture's
region: property `match`, the value the second picture's box in `fraction`s,
the confidence how well the two match, origin `guessed`. No match good enough is
one observation, unread, with its `why`. Which engine matches is qmcp's to
select, a classical feature matcher or a model: OpenCV, when it comes, runs in
otto, the family's video-generation engine, and qmcp reaches it there, so
OpenCV is imported into neither apothecary nor qmcp. How qmcp reaches otto is
otto's and qmcp's to plan.

## How apothecary consumes it

### When it asks

Only when a person asks. A person asks by choosing the `qmcp` finder where a
finder is chosen (`apothecary photo find --finder qmcp`, the viewer's Picture ›
Find), by asking about a rig's face or socket (`apothecary vision ask`, and the
same in the rig's window), or by running `apothecary vision check`. Nothing asks
on its own: not a concert's follower on each frame, not a print's kept frames,
not gathering. Asking about every frame, as a directive a person sets, is later,
once `vision check` has printed a model's seconds per picture on this machine.

### The client

`apothecary/finders/qmcp.py`, in the package the finders plan keeps for model
finders, never under `apothecary/vision/`.

- **Configured, never found.** qmcp's address is `--qmcp URL` or
  `APOTHECARY_QMCP`, as carlos's is `--carlos` or `APOTHECARY_CARLOS`
  (`apothecary/wiring/carlos.py`). With neither set, nothing is asked and
  nothing is probed: apothecary does not look for qmcp at qmcp's default port.
- **Loopback or nothing.** The address is checked when the client is made, with
  `stays_local.is_loopback`, and any other is refused there, naming the
  personal-data record, as `--carlos` refuses one. The guard refuses it again
  at connect.
- **MCP's Python SDK, as an extra.** The client is the SDK's streamable HTTP
  client, from the package qmcp's own MCP server is built on, installed by
  `apothecary[qmcp]` (`uv sync --extra qmcp` from a checkout). The core gains no
  dependency, and an install without the extra is qmcp absent. The SDK's sockets
  are Python's, so the stays-local guard sees each connect, which slice 0's test
  shows by pointing the client past loopback. The SDK and what it brings pass the
  licence gate, and it is a component in seam code, so it waits on the record
  the house stack asks for (*Records it needs*).
- **`ask` and `parse`**, the finders plan's split. `ask(request) -> result` is
  the MCP call, injected, so the tests drive the client against recorded results
  with no socket, as the monitoring record's §10 has a collector tested.
  `parse(result, request) -> List[Observation]` is the tested half, and refuses
  a malformed result whole.
- **A deadline of its own.** The client cancels at the request's `deadline_ms`
  and a margin. qmcp's own bound on a model call is measured and not enforced
  (`qmcp/governed.py`, `Bound.seconds`), so the asker enforces what it waits
  for.
- **Answers are cached** in `apothecary/vision/cache.py`'s cache, whose key is
  already the picture's hash, the backend, the model's digest and the prompt's
  version; here the prompt is the region and what was asked. In memory. Once the
  working-space layer's log exists, its collector for qmcp's answers writes them
  there.

### An observation

**The format is the family's, tightened here.** `qm.observation` version 1 is a
family contract, drafted in qm (*Records it needs*): what any family app says
about one subject and one property, for any other to read. Apothecary's
instance, `apothecary.observation` version 1, adds fields of its own and
tightens what the generic format allows, and never relaxes it. It is one format
for this layer and the working-space layer, in one module, built by whichever of
the two plans' first slices comes first; the field names below are that plan's.

The generic fields, `qm.observation`:

| Field | Holds |
|---|---|
| `subject` | an address, in the scheme of the app that names it, or a **sighting**: a picture or another source's own name, and a region, when nothing has said what it is |
| `property`, `value`, `unit` | a property's name, its value and its unit; `value` null is unread |
| `confidence` | from 0 to 1 as its source gave it, never rounded up; null where the source gives none |
| `origin` | its kind, `stated`, `measured`, `read`, `guessed` or `derived`, and `by`, what produced it |
| `at`, `recorded_at` | when it held (a picture's taken time), and when it was written |
| `evidence` | references to what it rests on, never the bytes: a picture's digest and path and a region, an invocation, other observations |
| `why` | why `value` is null |

An instance adds its fields in a block named for it, so a reader of the generic
format drops them cleanly, and it tightens what the generic format allows (a
closed list of properties, a field required), never the reverse. A reader that
knows only the generic format reads every family app's observations.

What apothecary's instance adds and tightens:

- **Subjects** are apothecary's addresses, as the working-space plan lists them:
  a site's node (`garage:printer_1.mainboard`), a facet of one
  (`garage:printer_1.mainboard#jack:usb`), a rig's module
  (`subharmonicon-complex:dfam#control:cutoff`), a board no node names
  (`usb:<identity>`).
- **A sighting is attributed only by a link**: a person's pin, a face pinned by
  its corners, a camera's projection. A model's label is a property of the
  sighting and never a link.
- **Properties** are a closed list per facet; the image models add `label`,
  `quantity` (with `of`), `size`, `shape`, `material`, `colour`, `covered` and
  `match`, and apothecary's readers of pixels add `rgb`.
- **Units**: `count`; `fraction`, of the picture's width; `mm` only when
  apothecary turned a fraction into millimetres with a reference a person
  stated; `sRGB`, a hex value, for `rgb`; and, for a word, the list it was asked
  among (*The words*).
- **`trusted`**, on a guess: whether `apothecary vision check` has passed for
  that model, at that weights digest, for that property, with the confidence
  above the threshold the check found (*How each is measured*). An untrusted
  guess is shown and used for nothing.
- **`view`**, on a reading off a picture: the camera, and how well it sees the
  subject, as the working-space plan has it.
- **`origin.by`**, on a guess: qmcp's tool, the model's name, version and weights
  digest, its engine, and qmcp's configured address, until qmcp can say which
  qmcp it is (qmcp's slice 7).

Apothecary's own readers give observations in this format (`read`, by
`plain/colour` and by the rig reader), so a model's and the plain reader's stand
side by side.

### The words

Every property answered in a word is asked among a list, and the lists come from
three places.

- **Colour and material are qm's**, beside `qm.observation`, so carlos and every
  family app read the same words. A colour is one of the basic colour words:
  black, white, grey, red, orange, yellow, green, blue, purple, pink, brown. A
  material is one a camera can tell apart: plastic, metal, wood, rubber, fabric,
  glass, paper, ceramic. The finer word, PLA or PETG, is a person's or the
  site's `material` on a node (`apothecary/hierarchy.py`), and either wins over
  a guess.
- **A site adds its own words**, each mapped onto one of qm's: a rig's cream
  leads, a lab's safety yellow, a node's `PETG` onto plastic. A model is asked
  among the site's words, and a reader of the generic format reads the qm word
  each maps to, so a guess of plastic agrees with a site that stated PETG. A
  site may narrow a list, to the colours its leads come in, and adds no word
  that maps to none.
- **Kinds counted and labels are built for each question** from what apothecary
  already knows about the subject: for a rig's face, carlos's entry, its
  controls' kinds (`KINDS` in `apothecary/rig/panels.py`), its sockets and
  plugs; for a device, the parts library's names and the site's nodes. A person
  may add words when asking. Apothecary's instance keeps the rule that builds
  them, not a list.
- **A colour's value is the word.** Its measured sRGB is a property of its own,
  `rgb`, which only a reader of pixels gives: the plain reader gives both, a
  model the word alone.
- **A word outside the list is unread**, its `why` naming the word, so nothing
  uses it, and a person sees it and can add it to a site's list.

### As a finder

`qmcp` is registered in `vision/finder.py`'s lazy registry beside `stated` and
`plain`. It runs the plain finder, then asks qmcp, for each shape found, its
`label` and `shape`, and, for the whole picture, the `quantity` of each kind
found. Its `Picture` is the plain finder's, with:

- `FoundShape.label` filled from a trusted label, so
  `ScaleReference.known_shape` finds it: the finders plan's cheapest real win;
- `FoundShape.origin` naming both, `plain+qmcp/<model>@<version>`;
- each shape's `confidence` the plain finder's, since `ENOUGH_CONFIDENCE` is
  measured against it;
- no shape that the model found and the plain finder did not, until `photo
  check` has measured the model finding shapes. Until then a model's own
  detection is an observation, not a shape.

Chosen with qmcp absent, it says so in `Picture.finder` (`plain; qmcp not
configured`) and answers as `plain` does. The default finder stays `plain`.

### Beside the rig reader

When a person asks about a face, apothecary sends each socket's box and the
face's own, through the face's mapping onto the picture; asks for the
`quantity` of plugs, a socket's `colour` and the face's `label`; and sets each
guess beside what the reader read.

- **A guess moves no level.** A rig's states in carlos are computed from the
  observations that are not guesses, as the working-space plan holds for every
  subject: a guess alone stays at `none`, and no guess lowers a level either.
- **A trusted guess that something covers the face** may withhold a reading and
  never makes one, as the working-space plan has a cover: the reading is unread,
  *covered*, with the guess as its evidence, and the socket's state carries as
  last known. It moves no level, since a state carried is not a state changed;
  it only lowers what is claimed. An untrusted cover guess is shown beside the
  reading, which stands.
- **They agree:** the state is the reader's, and its lines say the model agrees.
- **They disagree:** both are shown, each with its origin and evidence (`the
  reader saw a plug; <model> saw none`), and the state and its level stay the
  reader's. In the working-space layer it is a disagreement like any other,
  open until a person closes it.
- **The reader could not read it** (too small, no pointer to see): the guess is
  shown beside the unread (`unread: too small in the picture; <model> guesses a
  plug`), and the socket stays unread.

In a concert, a person asks about a frame after it is held; nothing the follower
does waits on qmcp.

### A person's word, and switching a model off

- **A person's word wins over a guess.** A stated shape (`origin: stated`), an
  answer in `--answers` (`BY_A_PERSON`), a stated scale, a setup's pinned faces,
  a rig's leads and a site as drawn are a person's. A guess about the same
  subject and property that differs is kept, used for no state, and scores the
  model: `vision check`'s real-photograph rows take it, as an answer in
  gathering scores the sorting.
- **A guess ranks below every other origin.** Between a person's word, an
  instrument and a reading, the working-space plan decides.
- **Every observation carries its origin**, so it is weighed per origin and
  property (*How each is measured*) and switched off per origin. The switches
  are a list in the state folder, shown as a window in the viewer, with
  `apothecary vision off <origin>` as its command; apothecary reads it before it
  asks. Unsetting `APOTHECARY_QMCP` switches them all off. Kept observations
  from an origin switched off leave every view and stay in the record, marked.

## What "always optional" means

Each row is what apothecary does when a person asks, and each answer is the one
it gives without the layer:

| When | Apothecary |
|---|---|
| **qmcp absent:** no address configured, or the `qmcp` extra not installed | asks nothing, says which (`qmcp is not configured`; `the qmcp extra is not installed`), and answers as it does without the layer |
| **qmcp not answering:** the connection refused, or MCP's initialisation failing | says so (`qmcp at URL is not answering; reading without it`) and answers as it does without the layer |
| **model absent:** no `vision.observe` among qmcp's tools, or no model answers a property | answers as it does without the layer; that property's observation is unread, with the `why` |
| **model slow:** the deadline passes | cancels the call and answers as it does without the layer, without waiting; the observation is unread, too late |
| **call refused:** an error result, a protocol error, or a result that does not validate or names another picture | answers as it does without the layer; nothing from the result is kept, and the record says why |

The test that holds it: each command that can ask (`photo find --finder qmcp`,
`vision ask`), run with qmcp unset, with the extra missing, pointed at a closed
port, answering with no vision tools, answering past the deadline from a stub
that sleeps, and answering malformed, gives the readings the same command gives
with the layer not built, and says why it added nothing. `photo check`'s and
`rig check`'s tables, `rig read`'s output and a followed concert's record are
unchanged, since none of them asks. A stub MCP server on loopback, bound to port
0, speaks the contract in the tests, so no qmcp is needed. Its mutation: let a
refused connection raise, and watch the test go red.

## Which measurements come first

| Order | Property | Needs | Why there |
|---|---|---|---|
| 1 | colour | nothing for a colour in the picture; a colour reference for one in the world | Apothecary reads a region's colour itself, its median through Pillow, so the first model is measured against a plain baseline from its first run, and drawn pictures have exact answers. On the rig: a plug's colour, a lead's |
| 2 | quantity | nothing | Counts are exact on drawn pictures and on a known device, since carlos's entry says how many knobs and sockets a face has. On the rig: plugs in a row of sockets, beside the reader's own |
| 3 | label | nothing | Fills `FoundShape.label`, so `known_shape` fills itself, and names a device in a picture ([the bench plan](qm-family-carlos-2026-10-29.md)'s slice 2) |
| 4 | shape | nothing | Measured by `photo check` itself, against the plain finder's kinds |
| 5 | material | nothing | No plain baseline and no drawn truth: measured on real photographs alone |
| 6 | size | **a scale** | A model gives a better outline, in fractions of the picture. Millimetres need a reference a person stated (`ScaleReference`) or a marker of known size (the finders plan's phase 1); without one, a size is a fraction of the picture and says so |
| 7 | covered | nothing | The working-space plan's last test of a cover, after the picture's limits, the reference surround, time and parallax, so it is measured against theirs. On the rig: a hand over a row of sockets, a lead draped across a face |
| 8 | match | **a second camera** | Measured once two cameras see one subject, on frames whose pairs are written down |

**Size needs a scale, and colour a reference.** A region's colour is the
camera's: under a stage's warm light a white plug reads amber. A named colour is
the picture's, its subject the sighting, unless a patch of known colour is in
frame and a person has said so, as a scale is stated.

## How each is measured before anything trusts it

`apothecary vision check`, in the style of `apothecary photo check` and
`apothecary rig check`: pictures whose every answer is known, a row for each
condition, a column for each score, and the model named, with its seconds per
picture on this machine beside it.

- **Drawn pictures**, which need nothing but this machine: `vision/bench.py`'s
  shapes drawn in known colours and known numbers, under the conditions `photo
  check` draws (turned, speckled, blurred, faint, small, crowded), with a tinted
  light and JPEG compression added; and `rig/simulated.py`'s faces, whose every
  plug is known. They prove the plumbing, not the eyes, as `rig check` says of
  its own.
- **Real photographs with written answers**, recorded in `project/validation/` as
  the [rig plan](carlos-concert-rig-2026-10-29.md)'s slice 4 records its first:
  the Uno's power and USB edge, each lead in and out; bench boards, with their
  names; things of known material. Material and label are measured here alone.
  A guess a person's word overruled joins this row, with the person's word as
  its answer.

The scores:

| Property | Scored as |
|---|---|
| colour | named right; how far off its sRGB value is; declined; the plain reader's row beside it |
| quantity | exactly right; off by one; off by more; declined |
| label | named right; named wrong; declined, which is allowed and counted apart |
| shape | `photo check`'s own columns: found, named, made up, honest |
| material | named right; named wrong; declined |
| size | how far off, as a share of the true size, with the scale stated |
| covered | said covered when clear, which withholds a reading for nothing; said clear when covered, which lets a wrong reading through; declined |
| match | the right region first; the right region among those offered; a wrong one first |

and, for every property, **made up**, an answer about a region holding nothing
of the kind, and **honest**, how much lower the reported confidence is when the
answer is wrong.

**When a guess is trusted.** For one model, at one weights digest, for one
property: made up is zero on every row, the honest gap is positive on every
row, and on the real-photograph row it beats the plain reader where there is
one. The check writes its result to the state folder, keyed by the digest and
the property, with the confidence below which its answers were wrong, the
threshold that `ENOUGH_CONFIDENCE` is for the plain finder. Only then is a guess
`trusted`, and only above that threshold. New weights are a new digest, measured
again.

## What lives where

| | qmcp | apothecary |
|---|---|---|
| the model | the engines it reaches, the weights a person fetched with its command from its pinned list, their digests and licences, `vision.models` | nothing: no engine, no weights, no image library but Pillow, no OpenCV, no numpy |
| the call | `vision.observe` over MCP: a region's crop to an engine over a standard protocol, the engine's reply into the contract, the deadline and the cancellation passed on, the invocation row | the client: the address, loopback, the MCP call, its own deadline, the schema, `ask` and `parse` |
| the picture | reads the file under a declared root, checks its digest, crops in memory, keeps the path and the digest | the picture root declared, the regions, what to ask |
| the format | observations in `qm.observation`, about sightings | its instance: subjects, links, `trusted`, `view` |
| the words | answers among the words it is asked; none of its own | each question's `among`: qm's colours and materials, a site's words mapped onto them, the catalogues' kinds and labels |
| meaning | none: a count is a count and a word a word | scale, colour reference, subjects, the order of evidence, a person's word |
| trust | reports the model's confidence | measures it (`vision check`), switches origins off, keeps the record |

qmcp's tool rules hold: the vision tools are stateless, call no other tool and
decide nothing (qmcp's `docs/tools.md`). Its human queue is not part of this: an
observation is evidence, and nothing here asks a person about each picture.

### qmcp's own slice

None of this is in qmcp at `ed01fc0`. It is qmcp's work, a pull request each, in
its own repository, started when the owner says so.

1. **A slow tool does not stall the server.** `invoke_tool` calls a tool's
   handler inline in an `async` route (`qmcp/server.py:230`), so a model call
   holds every other route for as long as it runs. Handlers run off the event
   loop.
2. **MCP on qmcp's own server.** Streamable HTTP, mounted in qmcp's app at the
   address qmcp binds, with the `mcp` package its `mcp` extra already declares
   for `qmcp_mcp.py`. Each request's `Origin` checked; every registered tool
   listed with its input and output schema and answered with structured
   content; one invocation path for MCP and `/v1/tools`, so each call writes its
   row and returns its id; cancellation passed to the handler; the client's
   roots read for a tool that takes a path. `qmcp_mcp.py` stays the repository's
   own server.
3. **The vision tools, on loopback only**, as the thread archive and voice are
   registered only when qmcp is bound to loopback (`qmcp/server.py:141`):
   `vision.models` and `vision.observe`, with a `recorded` engine that replays
   JSON, so the contract is tested with no model; and the path form: the roots,
   links resolved, the digest checked, EXIF orientation applied, crops in memory
   and none written. Cropping needs an image decoder in qmcp, qmcp's to choose
   and record; apothecary's is Pillow, a conflict row in its own adoption scope
   (`project/todo.md`).
4. **Engine adapters**, as qmcp's voice integration has `vox` state the contract
   and name no engine while an adapter names one: an OpenAI-compatible adapter
   (`llama-server`; Ollama, with its cloud models refused; vLLM), then the Open
   Inference Protocol, for detectors and segmenters. An engine qmcp starts runs
   with every telemetry and offline switch its libraries have, as the finders
   plan has a managed engine run.
5. **Vision models in `qmcp localmodel`**: `check`; `fetch <model>`, which
   downloads a model's weights when a person runs it, only from qmcp's pinned
   list, each entry a source, size, SHA-256 and SPDX licence, with no account,
   token or cookie sent, and keeps them only once the digest matches; and
   `plan`, as it has for its judgement worker. Nothing checks a host for newer
   weights: a new version is a new entry in a commit to the list, measured again
   before it is trusted.
6. **A picture's bytes recorded as their digest**, before the bytes form. An
   invocation row keeps a tool's input verbatim (`input_params`,
   `qmcp/server.py:217`, a JSON column in `qmcp/db/models.py`). A tool declares
   the fields kept as a digest and a length instead, and the vision tools
   declare their bytes. The path form needs none of this: its rows keep a path
   and a digest.
7. **qmcp says which qmcp it is**: the identity endpoint the monitoring record's
   revision triggers name, so an origin names the instance as well as the model.
   Until then apothecary's record names a qmcp by its configured address, which
   two clones on one port would share (that record's *Context*).
8. **`vision.match`**, with the recorded engine first, then an engine qmcp
   selects; OpenCV's, when it comes, run in otto and reached there.

## Governance

### What it rests on

- **Build the seam, buy the engines**
  (`governance/qm/records/DRAFT-build-the-seam-buy-the-engines.md`): a model is
  an engine, selected, and the seam is apothecary's client and qmcp's tools.
  Selecting an engine is where the weight goes. The MCP client is the
  protocol's own SDK, not one of apothecary's.
- **Seams on standard protocols**: apothecary reaches qmcp over MCP, which has
  independent implementations in several languages and many clients and servers
  that speak it, and qmcp reaches the engines over the OpenAI-compatible API or
  the Open Inference Protocol, each served by several independent servers. Each
  seam is on a standard protocol, and `qm.vision` is the tools' schemas over
  MCP.
- **Open-licence exclusion**: model weights and their toolchains are in its
  scope, restricted "open weights" are excluded, and there are no waivers. A
  model's weights licence is read from what its publisher ships at the digest
  chosen, since a family of models can license its code and its weights, or its
  sizes, differently. A model whose weights do not clear is not offered.
- **House stack**, and the adoption scope
  (`governance/qm/adr/DRAFT-constitution-adoption-scope.md`): apothecary gains
  one optional dependency, the MCP SDK, in an extra. qmcp, each engine and each
  model's weights are rows in its audit when the layer is configured, conflict
  rows where they do not clear.
- **Shrink the black box**: the model is never the check. A check apothecary runs
  decides whether a guess is trusted, a person decides whether it is used, and
  its output arrives through one seam that records each call.
- **A check is evidence only after it has failed**: the degrade test's mutation,
  and each check's *made up* column.
- **Nothing unattended spends money**: a local model spends nothing. A paid
  vision service is the finders plan's shut hook; through qmcp it would pass
  `qmcp/spend.py`'s gate, and the secured-user-accounts record first.
- **The monitoring seam, and instance identity**: what qmcp can and cannot say
  about which qmcp it is (qmcp's slice 7).
- **Personal data stays on the device** (apothecary's draft, in qm#121): qmcp on
  loopback, and what it keeps, count as on the device. The draft is rewritten in
  place, as the finders plan asks for each engine, to name qmcp and what it is
  given (a picture's path and digest, and its regions), that it reads a picture
  only under the roots it is given, each engine it starts and what that is given
  (a crop), and qmcp's invocation rows as a place observations are kept on this
  machine. It names a model's download as a fetch of a class of its own: by
  qmcp's command, on a person's word, from qmcp's pinned list, telling the host
  which model was fetched, from which address and when, and nothing a program
  sends unattended.

### Records it needs

Each drafted with the slice that needs it; a person ratifies.

- **The observation format** (an org record, in qm): `qm.observation` version
  1, its generic fields, the origin kinds, unread as no value, evidence by
  reference, and how an instance adds to and tightens it, with the colour and
  material words beside it and how a site maps its own words onto them. It
  belongs to the family, since every family app that says something about the
  world reads and writes it.
- **Apothecary's instance** (on `project/apothecary`): the working-space plan's
  project record for the evidence model, with this layer's decisions in it.
  Models answer through qmcp alone, over MCP, and only when a person asks; the
  layer is optional in each way the table above lists; a person's word comes
  first; a guess moves no level, and a trusted cover guess only withholds a
  reading; a model never sets a scale; a word outside the list is unread; and a
  guess is trusted only after a check. One record for both plans, one decision
  each with the finders plan's finder-seam record.
- **Data retention** (for governance/qm): how long each program keeps what it is
  given and what it makes, who forgets it, and how a person deletes it: qmcp's
  invocation rows (a picture's path and digest, every observation), apothecary's
  observations, frames and vision cache, and carlos's states. The family's to
  decide, since qmcp and carlos keep what apothecary sends them; apothecary's
  personal-data record names its own part. The working-space plan's question of
  how long frames are kept is the same question for one kind of thing.
- **The MCP SDK as a component**: the record the house stack asks for before a
  component is imported into seam code, for apothecary's extra and for qmcp,
  which already imports it.
- **Model weights, a class of their own** (in qmcp's records, and named in
  apothecary's personal-data record): weights are not a tool fetched at install.
  qmcp fetches them by a command a person runs, only from its pinned list, each
  entry a source, size, SHA-256 and SPDX licence read from what the publisher
  ships at that digest, with no account, token or cookie sent; nothing checks a
  host for newer weights, and new weights are a new entry, measured again.
  Apothecary's personal-data record names the download and what it tells the
  host, and that apothecary never touches the weights.
- **A selection record for each model**: its name, version, weights digest,
  licence and engine, the check's table, and its seconds on this machine.
- **qmcp's vision tools** (in qmcp's records): `vision.models`,
  `vision.observe` and `vision.match`, served on loopback only, over MCP and
  `/v1/tools`, reading a picture only under declared roots, the contract
  `qm.vision` version 1, and OpenCV run in otto rather than imported.

## Decided

- **2026-10-31:** qmcp is the one door for every model's answers. The finders
  plan's `LoopbackModel` is not built.
- **2026-10-31:** apothecary reaches qmcp over MCP, served by qmcp's own server
  over streamable HTTP on loopback; MCP on qmcp's server is part of this plan,
  in qmcp's slice.
- **2026-10-31:** a picture crosses the seam as a path and its digest. A region's
  bytes are an expansion, for a later contract version.
- **2026-10-31:** qmcp on this machine, and what it keeps, count as on the
  device. How long each program keeps what it is given is a governance decision,
  drafted as *Data retention*.
- **2026-10-31:** apothecary asks a model only when a person asks.
- **2026-10-31:** the observation format is a generic family contract in qm,
  `qm.observation`, which apothecary's instance adds to and tightens for this
  project, one format with the working-space layer's.
- **2026-10-31:** a colour's value is one of the basic colour words, and its
  measured sRGB is a property of its own that only a reader of pixels gives. A
  material is a coarse word a camera can tell apart. Both lists are qm's, beside
  `qm.observation`, and a site adds words of its own, each mapped onto one of
  qm's.
- **2026-10-31:** the kinds counted and the labels are built for each question
  from apothecary's catalogues. A word a model answers outside the list is
  unread, with the word.
- **2026-10-31:** a model's weights are a class of fetch of their own: qmcp's
  command fetches them on a person's word, from a pinned list, and the host
  learns only what was fetched; nothing checks for newer weights. qmcp's records
  govern them, and apothecary's personal-data record names the download.
- **2026-10-31:** a trusted guess that something covers a face may withhold a
  reading, and never makes one.
- **2026-10-31:** a region found again in another camera's picture is qmcp's
  `vision.match`. OpenCV, when it comes, runs in otto, reached by qmcp.

## Slices

Smallest first; each lands alone.

0. **The format and the switch, with no model.** `qm.observation` drafted in qm,
   with the colour and material words; apothecary's instance, one module with
   the working-space layer's, with a site's own words mapped onto qm's;
   `--qmcp` and `APOTHECARY_QMCP`, loopback when the client is made; the `qmcp`
   extra with the MCP client, its transport injected, and `parse` tested on
   recorded results; the degrade test against a stub MCP server, a case for
   every row of the table; and a walkthrough page that reads an observation
   from a recorded result and shows each row's degrading.
1. **The plain reader's answers as observations** (apothecary). A region's
   colour from its pixels (`plain/colour`), and the rig reader's plugs, so the
   baseline is in the format before any model is.
2. **qmcp's slices 1 to 3**, in qmcp: the server unstalled, MCP on its own
   server, and the vision tools with the recorded engine and the path form.
   Apothecary's client reaches a real qmcp over MCP, in a cross-app test that
   runs qmcp from a checkout a variable names, as
   `tests/e2e/test_carlos_concert.py` runs carlos. The personal-data rewrite
   lands with it, the first time a picture's path leaves apothecary's process.
3. **Colour from a model, measured.** qmcp's slices 4 and 5 for one
   vision-language model over the OpenAI-compatible API, its weights fetched by
   `qmcp localmodel fetch` from the pinned list; `apothecary vision
   check --property colour`, with the plain reader's row beside it; the first
   selection record.
4. **Quantity**: drawn pictures, drawn rig faces, then the Uno's photographs
   from the rig plan's slice 4.
5. **Label**: the `qmcp` finder fills `FoundShape.label`; a device named in a
   picture, measured on bench photographs with their names written down.
6. **Shape**: `photo check --finder qmcp`.
7. **Material**, on real photographs alone.
8. **Size**, with a stated scale, then with the finders plan's marker finder.
9. **Bytes**: qmcp's slice 6, then a contract version that carries a region's
   pixels, first a rig's face rectified through its pinned corners, measured by
   `vision check` against the path form's crop.
10. **Covered**: `covered` from a model, measured on drawn faces with the covers
    the working-space plan's spike drew, then on real frames at the bench, before
    a cover guess is trusted to withhold anything.
11. **A match**: qmcp's slice 8, measured on frames from two cameras with their
    pairs written down, for the working-space layer's suggested links.
12. **The working-space layer takes them**, in its own plan.
