# ADR-XXXX — Control Plane and Engine Boundary

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-08-07 |
| **Pends on** | Nothing — ready for ratification |
| **Principle** | P4 — custom code concentrates where sovereignty matters |

## Context

The build-the-seam org record requires each project to ratify a control-plane
instance record naming what its seam owns, what it refuses to own, and
size-smell thresholds as revision triggers. This is that record for Alfred.

Alfred's structure has one feature the org record does not contemplate. That
record describes engines as selected from the commons, and treats a
QM-maintained engine as a remediation outcome — what happens after an upstream
rejects a patch or goes dead. Alfred's render engine, `otto`, is neither. It
was written by QM as a standalone public package with its own repository,
documentation, test suite, and PyPI release, and Alfred consumes it as a
versioned dependency across a public API. It is not a fork, not a vendored
copy, and not a private module that happens to live elsewhere.

Measured against the tree at adoption: the seam is roughly 1,200 lines of
logic across 30 modules, plus 749 lines of demo seed data. `otto` is
roughly 1,350 lines. The seam imports exactly three symbols from it —
`otto.models.Edl`, `otto.render.renderMultitrack`, and `otto.getdata.timestr`
— and imports no media library at all: no moviepy, no direct ffmpeg or
ImageMagick invocation anywhere in the control plane.

## Decision

1. **The seam is `alfred/`.** It owns authentication and identity, project
   and render lifecycle state, render orchestration and job dispatch, access
   policy, storage and notification integration glue, and the HTTP API.

2. **The seam refuses to own media.** No decoding, encoding, muxing,
   compositing, frame handling, or codec configuration lives in `alfred/`.
   Media work belongs to `otto` and, below it, to the engines `otto` selects.
   A direct import of a media library into `alfred/` is a boundary violation,
   not a shortcut.

3. **`otto` is an engine, and QM authoring it does not change that.** The
   classification follows from function, not authorship: it does media work,
   which §2 forbids the seam from doing. It is consumed the way any engine is
   — as a released package, across its public API, at a version — and its
   development is governed by its own repository, not by this one. That QM
   maintains it is a commons contribution, not an extension of this project's
   seam.

4. **The boundary is the published API.** The seam depends on `otto`'s
   released interface and does not reach into its internals. The submodule at
   `alfred/otto` is a development convenience for editing both together; it
   is not a license to couple to unreleased or private surfaces. If the seam
   needs something `otto` does not expose, the answer is a release of `otto`
   that exposes it.

5. **`ffmpeg_params` is a recognized leak, and is capped rather than
   blessed.** The render model accepts a list of raw encoder arguments and
   passes them through to the engine. This is engine-specific configuration
   crossing the seam as opaque data, and it lets an API client influence
   encoder invocation directly. It is not extended, and no second parameter of
   its kind is added. Replacing it with named, validated render options is the
   preferred direction.

## Consequences

- The bus-factor concentration sits in roughly 1,200 lines, which one person
  can hold, and the media complexity sits in a package with its own tests and
  its own release cadence.
- `otto` is reusable outside Alfred and is in fact released independently,
  which is what makes the boundary real rather than notional. A boundary only
  one consumer ever crosses is an untested claim.
- Cost accepted: two repositories and a release step for changes that span
  both, against the alternative of one repository where the boundary erodes
  quietly because nothing forces it to hold.
- Cost accepted: `ffmpeg_params` stays until named options replace it, so the
  leak in §5 is live and recorded rather than closed by this record.
- The seam's own dependencies still include a datastore, a broker, and an
  object store whose selections are non-compliant at adoption. This record
  governs the *shape* of the boundary; the constitution-adoption record
  governs the *compliance* of what sits behind it. They are separate
  decisions and separate records.

## Alternatives considered

1. **Fold `otto` into `alfred/` as a package directory.** Rejected: it would
   put media handling inside the seam, which §2 forbids, and would end
   `otto`'s independent existence as a commons artifact for no gain beyond
   one less release step.
2. **Treat `otto` as part of the seam because QM wrote it.** Rejected:
   authorship is the wrong test. It would make the seam's size smell
   meaningless — any engine could be absorbed by writing it in-house — and it
   contradicts the org record's own reasoning, which classifies by what a
   component does.
3. **Select an existing render engine instead of maintaining one.** Rejected
   as a decision already made and still sound: the engines `otto` sits on
   (moviepy, and ffmpeg below it) are selected from the commons, and `otto` is
   the orchestration layer over them that no upstream should reasonably own.
   It is published so that if that judgment is wrong, the cost is one
   package's maintenance and not a private dependency.
4. **Expose the engine's full option surface through the API** rather than
   capping `ffmpeg_params`. Rejected: it converts an acknowledged leak into
   doctrine, couples the API to one engine's flags permanently, and widens an
   input path that reaches an encoder invocation.

## Revision triggers

- Seam logic exceeds 2,500 lines excluding seed data — roughly double its
  size at adoption — which forces a split-or-upstream review rather than an
  assumption that growth was warranted.
- Any media library is imported directly into `alfred/`.
- The seam imports an `otto` symbol that is not part of its published API, or
  the count of imported symbols grows past a handful without a release
  boundary being crossed.
- A second parameter of the `ffmpeg_params` kind is proposed, or that
  parameter is replaced by named options.
- `otto` gains a consumer outside QM, or loses its independent release — the
  first strengthens the boundary claim, the second invalidates it.

## Amendments

*None.*
