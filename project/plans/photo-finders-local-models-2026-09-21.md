# The shape finder, with a model behind it: a plan

*Nothing in this page is built.*

## What this plans

The photo path finds shapes with pixel arithmetic (`apothecary/vision/plain.py`).
It runs with the network off, it is measured (`apothecary photo check`), and
it does not name things, see depth, or know how big anything is. The plan:
an *optional* local model behind the finder, a shape that lets more finders
be added the same way, the open local frameworks rather than an engine of
our own, and a hook for paid services that stays shut.

Two sets of rules decide most of it. *Personal data stays on the device*
(the draft record, enforced by `apothecary/stays_local.py`): the process
cannot reach past loopback, and a paid service only under the record's
named exception, *secured user accounts*, a future record. The house-stack,
build-the-seam and standard-protocol drafts in `governance/qm/records/`: a
component imported into seam code needs an org-level record, one reached
across a protocol seam is an engine selection, and an engine QM writes is
its own project.

So a model is an engine: a subprocess the seam starts, or a server on
loopback, never imported into `apothecary/` (nor is OpenCV). Its weights are
qmcp's, fetched on a person's word (*Reach*). A paid hook is the same seam
with an address the guard refuses.

## The seam as it stands

- `apothecary/vision/finder.py`: `ShapeFinder(Protocol)` with `name()` and
  `look(image) -> Picture`; a lazy registry (`register`, `names`, `get`)
  with two built-ins, `stated` and `plain`. No configuration, capabilities
  or entry-point discovery: a third finder registers by being imported.
- `FoundShape` (`vision/models.py`) carries a box in picture fractions,
  `points`, `confidence`, `origin`, `label`, the turn and the sides.
  `points` is read nowhere; `label` only by `ScaleReference.known_shape`.
  Scale is a person's statement or nothing; a finder never sets millimetres.
- The finder is chosen by name, default `plain`, in the API and the
  `apothecary photo` commands; the browser's camera panel never sends one.
- Gathering trusts confidence (`ENOUGH_CONFIDENCE` in `gathering/resolve.py`).
  A model's score is not a confidence until `photo check` shows it drops
  when the model is wrong; until then it rides in `origin`.
- The fence that keeps engines out (`tests/test_working_together.py`) is an
  exact-name set over the top-level `*.py` of `gathering/`, `vision/` and
  `vocabulary/`: `onnxruntime`, `cv2`, `numpy`, `ollama` and anything in a
  subfolder pass it. It is tightened before it is relied on.

What a model adds: **labels** (to `FoundShape.label`, so `known_shape`
fills itself -- the cheapest real win), **oriented boxes** (the sides and
turn `compose.build` already prefers), **masks** (to `points`, which then
needs a consumer), **depth** (new fields with an origin; metric only with a
focal length the person or EXIF states). Never **a scale**: a model returns
labelled candidate references and a person names one.

## The plugin shape

Keep `ShapeFinder` and the lazy registry, and add three things.

1. **Discovery by entry point** (`importlib.metadata.entry_points(group="apothecary.finders")`),
   loaded lazily by `get()`. Installing a finder package into apothecary's
   environment is the person's act, like `uv sync`, and it runs under the
   guard. Not pluggy, not a plugins folder.
2. **A `Backend` descriptor** beside every finder: *needs* (a weights path,
   its SHA-256, its SPDX licence, a device, a memory figure), *gives*
   (labels, boxes, masks, depth, text), and *reach*: `engine` (a subprocess
   the seam starts), `loopback` (a server on this machine) or `account`
   (the named exception). There is no in-process reach. A test enumerates
   every backend's reach and refuses `account` while no record allows it.
3. **Composition behind one `look()`**: optional `Segmenter`, `Labeller`
   and `Ranger` stages a composite finder chains; everything downstream
   sees one `Picture`. Every shape's `origin` names the backend and model
   digest. Model output is cached, keyed by picture hash, backend, model
   digest and prompt version: in memory until what "this machine" means is
   decided (project/todo.md), then in an account-only folder (0700). The pictures
   plan's Phase 2 builds this cache (`apothecary/vision/cache.py`, in
   memory) for its looks; this plan's phases fill it from model finders.

Testing: a `recorded` finder replays JSON recorded against a local engine on
`vision/bench.py`'s synthetic pictures. Every model finder splits into
`ask(bytes) -> reply` and `parse(reply, w, h) -> Picture`; `parse` is the
unit-tested half. It lives in a new package, `apothecary/finders/`, never
under `apothecary/vision/`, and the fence is tightened in the same commit.

## Reach: what is lawful

**In-process is a C extension outside the guard.** Measured 2026-09-21: ONNX
Runtime's official Linux build resolved and connected to a telemetry host
from a native thread that the Python guard never saw, and did not with
`ORT_DISABLE_TELEMETRY=1`. So a model is a **managed engine**: a subprocess
with an argv the seam builds, the scrubbed environment plus every
telemetry and offline switch its libraries have, a contract over a standard
protocol, and an `strace -e trace=network` run recorded in the personal-data
record, which is rewritten in place to name each engine and what it is given
(a picture, a weights path, nothing else).

**The protocol is a standard one.** Labels and text: the OpenAI-compatible
chat API that `llama-server`, Ollama and vLLM all speak. Masks and depth:
the Open Inference Protocol (KServe V2), served by OpenVINO Model Server,
Triton and MLServer. A runner of QM's own is written only if none of those
passes the gates, as its own project, speaking one of those protocols.

**Loopback is a server the seam starts, or the person runs.** One client,
`LoopbackModel(base_url, model)`, checks `is_loopback()` at construction
and raises `LeftTheMachine` otherwise, sends pictures only as base64 data,
validates a JSON-schema'd reply, and refuses Ollama's cloud models
(loopback that forwards). A proxy on loopback that forwards is the person's
program and cannot be detected. Preferred: the seam starts `llama-server`
over a weights file, bound to 127.0.0.1 with a random key. Every model's
answers come through qmcp instead, over MCP, so `LoopbackModel` is not built
and these rules are qmcp's engine adapters'
([image models through qmcp](image-models-through-qmcp-2026-10-30.md)).

**Weights are fetched by qmcp, on a person's word**: a download of a
model's weights is a class of fetch of its own, not an install-time tool
fetch. `qmcp localmodel fetch` fetches only from qmcp's pinned list, and
apothecary never touches the weights ([image models through
qmcp](image-models-through-qmcp-2026-10-30.md)). It is a second fetch door,
reviewed as one, and qmcp's.

**Paid services** are the same OpenAI-compatible seam with an address the
guard refuses. Adding one is a proposal of the secured-user-accounts record
and goes to the governance branch. The UI does not list them meanwhile.

A model-backed finder becomes a default only when, on `photo check`'s table
plus a row of real bench photographs with a marker in frame, *found* and
*named right* fall on no row, *made up* stays at zero, the *honest* gap is
positive, and seconds per picture on this machine are printed beside it.

## Phases

**0. The seam, hardened** (no model). Entry-point discovery; the `Backend`
descriptor with reach; the `recorded` finder; `label` on `Provenance`; the
`ask`/`parse` split; the fence tightened; the marker row and timing column
in `photo check`; tests in `tests/test_stays_local.py`'s style (reach is
`engine` or `loopback`, a non-loopback URL raises at construction, a cloud
model is refused). The licence gate rewritten to read SPDX expressions and
scan every shape the project ships (numpy's compound expression fails
`pip-licenses --allow-only` today). The finder seam record drafted.

**1. Markers.** An `aruco` finder in a runner the seam starts: a marker's
corners as a labelled shape of known size, so a bench photograph is in
millimetres. The first managed engine.

**2. A namer over loopback.** `LoopbackModel` and a `vlm:<model>` finder:
labels for what the plain or marker finder found. A seam-started
`llama-server`, or the person's Ollama with the cloud refusal. A selection
record for the model; measured on this machine before it is offered. Replaced
by [image models through qmcp](image-models-through-qmcp-2026-10-30.md): qmcp
is the one door for every model's answers, and `LoopbackModel` is not built.

**3. Masks and depth.** An Open Inference Protocol server over ONNX
exports, evaluated for licence, a CPU build and telemetry, reached through
qmcp's adapter; failing that, one runner as its own project. `points` consumed by `vision/geometry.py`,
relative depth on shapes, a stated focal length for metric depth, and
`Provenance.thickness_guessed = False` when a depth said so.

**4. The records**, one decision each: the finder seam (an engine slot,
reached behind a managed runner or a standard protocol on loopback); a
selection record per engine; the personal-data draft rewritten for each
engine; the component audit for llama.cpp, Ollama and any runner.

**5. The paid hook.** Not built. It needs the secured-user-accounts record
first, then the edits it names to `stays_local.py` and its tests.

## Pends on

| Question | Whose |
|---|---|
| The licence gate reading SPDX expressions and every shape | this project, phase 0 |
| `CC0-1.0` (numpy) on the licence allowlist | the org: an allowlist addition is an amendment |
| Whether a one-time model download is an install-time fetch | answered in [image models through qmcp](image-models-through-qmcp-2026-10-30.md): a class of its own, by qmcp's command from a pinned list |
| The runner's protocol, or a seams-record exception | phase 3 |
| Whether the browser offers a finder choice | answered in [the pictures plan](pictures-in-the-world-2026-09-26.md): Picture › Find, where more than one finder can read the picture |
