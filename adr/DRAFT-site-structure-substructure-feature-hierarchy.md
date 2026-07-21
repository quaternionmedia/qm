# ADR-XXXX — Site/Structure/Substructure/Feature Hierarchy for Complex Subassemblies

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-07-20 |
| **Pends on** | Human ratification of the modeling approach itself (naming, class boundaries, and whether `Site` supersedes or supplements `Scene` — see Decision and Alternatives). No implementation lands under this ADR until it is ratified; this record is the design, not the diff. |

## Context

Apothecary's current data model is deliberately flat: a `Scene` holds
`objects: List[OpenSCADObject]`, where `OpenSCADObject` is the common base for
primitives (`Cube`, `Sphere`, `Cylinder`), booleans (`Union`, `Difference`,
`Intersection`), and transforms (`Translate`, `Rotate`, `Scale`). Booleans and
transforms already carry `children: List[OpenSCADObject]`, so arbitrary
geometric nesting is possible today — but nothing above that gives a nested
group a *name*, an *address*, or non-geometric metadata. The one unit of
reusable, registered, named geometry is `BasePart`
(`apothecary/projects/parts/base.py`): a single `.scad` file plus metadata
(bounds, color, print settings), registered flatly in
`apothecary/projects/registry.py`. There is no concept between "one whole
part" and "an anonymous boolean/transform node" — a project wanting to model
one coherent object made of several interacting systems (say, an enclosure
with its own mounting system, cable-routing system, and ventilation system)
has nowhere to put that structure except ad hoc nesting with free-text
`comment` strings, which is not queryable, not addressable, and not reusable
across projects.

This ADR proposes the vocabulary and class shape needed to model **one site
as a complex subassembly composed of multiple structures, each composed of
multiple systems (substructures), each composed of named, parameterized
local features** — sufficient depth for a real multi-system assembly, not
just a single printable part.

## Decision

### Vocabulary (four new levels, outermost to innermost)

1. **Site** — the root of one coherent physical build: a printer enclosure, a
   workbench, a dispensing cabinet. Fixes the global coordinate frame, units,
   and (optionally) an environment/build-volume constraint. Contains one or
   more **Structures**. A `Site` is the semantic superset of today's `Scene`:
   a `Site` compiles down to a `Scene` (or one `Scene` per `Structure`, for
   independent manufacture) rather than replacing it — `Scene` keeps its
   current flat-list contract unchanged.
2. **Structure** — a major, independently-manufacturable or independently
   sourced rigid grouping within a Site (a frame, an enclosure panel, a
   housing). Carries its own local transform (placement within the Site) and
   metadata (material, BOM entry, `PrintSettings`). Contains one or more
   **Substructures**.
3. **Substructure** — a named *system* within a Structure: a mounting system,
   a cable-routing system, a ventilation system, a fastening system. This is
   the level that makes "multiple systems in one subassembly" concrete and
   addressable. A Substructure is composed of **Features** and/or nested
   Substructures, and is independently parameterizable and reusable — the
   same "standard M3 mounting pattern" Substructure can be instanced into
   many Structures across many Sites.
4. **Feature** — a single, named, parameterized local modification: a hole,
   boss, fillet, slot, counterbore, snap-fit tab. Features exist today only
   as anonymous boolean/primitive combinations with an optional free-text
   comment; this proposes making the common ones first-class, so they are
   queryable ("every M3 clearance hole in this Substructure") and can draw
   directly on the existing `apothecary.models.units` (`HardwareSizes`,
   `PrintSettings`) to compute correct clearance/press-fit dimensions instead
   of hand-coding them at each use site.

### Class shape

- All four are Pydantic `BaseModel`s. `Feature` subclasses `OpenSCADObject`
  directly (it already needs `.render()` and `comment`); it wraps its actual
  geometry (typically a `Difference`/`Union` of existing primitives) behind a
  named, parameterized constructor — e.g. a `CounterboredHole(size=M3,
  print_settings=...)` feature expands internally to the right
  `Cylinder`/`Difference` combination, but is addressed and rendered as one
  named node.
- `Substructure`, `Structure`, and `Site` are plain `BaseModel`s (not
  `OpenSCADObject` subclasses — they carry non-geometric metadata a geometry
  node has no field for) with a `name: str`, a local transform, and a
  `to_scad_object() -> OpenSCADObject` method that wraps its children in the
  existing `Translate`/`Union` primitives, tagged with a `comment` naming the
  level and name (e.g. `// Structure: frame`, `// Substructure:
  bearing_mount`, `// Feature: m3_clearance_hole`) so generated `.scad` output
  stays human-legible without any new rendering machinery — `render()` and
  `render_jscad()` on `Site` are thin wrappers that build a `Scene` from the
  composed tree and delegate to it, exactly mirroring `Scene.render_jscad()`'s
  existing delegation to `JSCADRenderer`.
- **Addressing:** `name` at each level is unique within its parent, giving a
  dotted path (`enclosure.mounting_system.m3_boss_fl`) usable both for
  human reference in this ADR's examples and as the natural extension of the
  existing `/parts/{name}` API pattern to `/sites/{name}/structures/{name}/...`
  — the API surface itself is out of scope for this ADR and would need its
  own record.
- **Reuse:** Substructures (and Features) are registered the same way
  `BasePart` is registered today (`projects/registry.py`'s pattern extended
  downward), so a "standard V-Slot bracket" Substructure or a
  "counterbored-M3-hole" Feature becomes a library entry usable across many
  Structures and Sites — this is the concrete mechanism that makes "systems"
  shared across a complex assembly rather than copy-pasted.

### What this ADR does not decide

- The exact registry/API wiring for Substructure and Feature libraries
  (separate record).
- Whether `Structure`/`Substructure` need their own bounding-box or
  `BasePart`-style geometry-metadata integration (`get_bounds`,
  `preview_color`) — likely yes, by extension of the existing pattern, but
  not specified here to keep this ADR to one decision (the hierarchy shape),
  not two.
- Migration of any existing `parts/*` entries into this hierarchy — none are
  migrated by this ADR; it is additive.

## Consequences

- **Additive, not breaking.** `Scene`, `OpenSCADObject`, and every existing
  primitive/boolean/transform are unchanged. Existing parts and JSON scenes
  continue to work exactly as today; `Site` is an opt-in layer for assemblies
  that need it.
- **No implementation lands under this ADR.** Per decision-record discipline,
  this document is Proposed, not Accepted — it fixes the shape for human
  review. Implementing `apothecary/hierarchy.py` (or wherever these land) is
  explicit follow-up work, tracked outside this ADR's own text once
  ratified, not silently started alongside the draft.
- **New surface to maintain:** four new model classes, a registry extension
  pattern for Substructures/Features, and (eventually, separately) API
  routes. The existing single-part model stays exactly as simple as it is
  today for projects that don't need the extra levels — the cost is paid
  only by assemblies that opt in.
- **Feature library growth is unbounded in principle** — a parameterized
  feature library (counterbores, snap-fits, standard bosses) can grow
  indefinitely. Accepted: the alternative (no shared feature library) means
  every project hand-codes the same clearance-hole math already centralized
  in `PrintSettings.clearance_hole`/`press_fit_hole`.

## Alternatives considered

1. **Keep flat nesting with disciplined comment-naming conventions, no new
   classes** — rejected: comments are not queryable or reusable; "which
   Substructure does this hole belong to" would remain answerable only by
   reading generated `.scad` text, not by code.
2. **Model this as a general-purpose scene-graph/BOM library (adopt an
   external PLM or CAD-kernel scene-graph package)** — rejected under the
   seams/house-stack doctrine: Apothecary's whole value proposition is a
   small, deeply-understood Pydantic model compiled to OpenSCAD/JSCAD; a
   general external scene-graph engine is exactly the kind of "engine" P4
   would ask "should this be bought," and the answer here is no — the
   hierarchy is thin metadata over existing primitives, not a CSG/rendering
   capability that needs an engine.
3. **Collapse Structure and Substructure into one level** — rejected: it
   erases the distinction the user's stated requirement actually needs
   (independently-manufactured groupings vs. named systems within one
   grouping) — a Structure can and typically will contain more than one
   Substructure (that is the "multiple systems" requirement), so a single
   level cannot represent both a manufacturing boundary and a system
   boundary at once without conflating them.
4. **Make `Feature` a plain function/helper instead of a Pydantic model** —
   rejected: a bare function returning an `OpenSCADObject` cannot carry
   `name` for addressing or be registered in a reusable library the same way
   `BasePart` is; the marginal cost of a `BaseModel` wrapper is small next to
   losing addressability.
5. **Replace `Scene` outright with `Site`** — rejected: `Scene` is simple,
   already used by every existing part and the JSON scene format
   (`docs/scene-json.md`); breaking it for assemblies that don't need the
   extra hierarchy would violate the additive, opt-in shape this ADR argues
   for. `Site` compiling down to `Scene` keeps both true at once.

## Revision triggers

- This ADR is ratified (Accepted, numbered) — implementation work begins as
  its own tracked follow-up, not folded silently into this document.
- A real multi-system assembly is modeled against this shape and the
  Structure/Substructure boundary proves wrong in practice (e.g., a project
  needs a grouping level this ADR didn't anticipate) — revisit before
  extending the vocabulary further.
- The registry pattern this ADR extends (`projects/registry.py`) changes
  shape for unrelated reasons — re-verify the Substructure/Feature reuse
  mechanism still fits.
- An API surface for this hierarchy is proposed — that record should cite
  this one rather than re-deriving the vocabulary.

## Amendments

*None.*
