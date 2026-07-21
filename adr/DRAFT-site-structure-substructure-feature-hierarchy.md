# ADR-XXXX — Site/Structure/Substructure/Feature Hierarchy for Complex Subassemblies

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-07-20 |
| **Pends on** | Human ratification of the modeling approach itself — a single generic, self-similar recursive node (`Assembly`), with `role` as free-form metadata rather than a type distinction, and whether `Site` supersedes or supplements `Scene` (see Decision and Alternatives). No production/ratified-path implementation exists yet: `apothecary/hierarchy.py`'s `Assembly` is an explicitly-labeled prototype, evaluated against real geometry (a garage workbench with a fleet of instrumented printers, nested five levels deep) before this decision is ratified, not a preempting of it. |

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

This ADR proposes one generic, self-similar recursive node — an `Assembly` —
sufficient to model a site as a complex subassembly composed of multiple
structures, each composed of multiple systems, each composed of named,
parameterized local features, to whatever depth a real project actually
needs. A depth fixed in advance would just be an arbitrary limit waiting to
be hit by the first project whose real assembly needs one more level than
was anticipated.

## Decision

### The shape: one generic recursive node, not four fixed classes

`Assembly` is a single Pydantic `BaseModel`, self-referential (`children:
List["Assembly"]`, plus `additions`/`subtractions` for positive/negative
geometric composition — see Class shape), carrying at every node regardless
of role:

- `name: str` — unique within its parent, giving the dotted addressing path
  this hierarchy has always needed (`enclosure.mounting_system.m3_boss_fl`).
- `role: str` — free-form metadata ("site", "structure", "substructure",
  "feature", or anything a project invents), used for the render comment and
  for future revision/diff messages — **not a type distinction**. Nothing in
  the shape stops a "feature"-role node from having `children`, or a
  "site"-role node from having `additions`; the same shape applies uniformly
  at every depth, which is the point.
- A local transform (`position`), an optional `footprint`/bounding box,
  optional manufacturing metadata (`material`, `build_volume`, `status`), and
  `comment`.
- `base: Optional[OpenSCADObject]` — a node's own geometry, if it has any
  (the common case for a leaf).
- One `to_scad_object()` compiles a node — its `base`, `additions`,
  `subtractions`, and `children` — to a single OpenSCAD object, recursively.
  One `validate()` checks siblings for overlap at every level of the tree a
  footprint was given, not only at the root.

### Vocabulary: Site/Structure/Substructure/Feature as configuration, not classes

The four names this ADR is titled after remain the vocabulary for describing
a build — they are ergonomic constructors (`Site(...)`, `Structure(...)`,
`Substructure(...)`, and a `Feature` namespace of leaf-geometry constructors)
that build a role-tagged `Assembly`, not four distinct Pydantic classes. A
project reads and writes `Structure(name=..., substructures=[...])` exactly
as it would against a dedicated class; underneath, one class walks the tree.

1. **Site** — the root of one coherent physical build: a printer enclosure, a
   workbench, a dispensing cabinet. Fixes the global coordinate frame, units,
   and (optionally) an environment/build-volume constraint. Contains one or
   more **Structures**. Compiles down to a `Scene` (or one `Scene` per
   Structure, for independent manufacture) rather than replacing it —
   `Scene` keeps its current flat-list contract unchanged.
2. **Structure** — a major, independently-manufacturable or independently
   sourced rigid grouping within a Site (a frame, an enclosure panel, a
   housing). Carries its own local transform and metadata (material, BOM
   entry, `PrintSettings`). Contains one or more **Substructures**.
3. **Substructure** — a named *system* within a Structure: a mounting system,
   a cable-routing system, a ventilation system, a fastening system. Composed
   of **Features** and/or nested Substructures, independently parameterizable
   and reusable — the same "standard M3 mounting pattern" Substructure can be
   instanced into many Structures across many Sites.
4. **Feature** — a single, named, parameterized local modification: a hole,
   boss, fillet, slot, counterbore, snap-fit tab. Queryable ("every M3
   clearance hole in this Substructure") and can draw directly on
   `apothecary.models.units` (`HardwareSizes`, `PrintSettings`) to compute
   correct clearance/press-fit dimensions instead of hand-coding them at each
   use site. A Feature can carry its own child Feature (a relief cut on a
   boss, say) the same way a Substructure always could, since both are the
   same underlying node.

A project is not limited to these four names or four levels: since `role` is
free-form and depth is unbounded, a fifth level — or a different vocabulary
entirely, for a project shaped differently than a garage full of printers —
costs nothing beyond choosing a name for it.

### Class shape

- `Assembly` is the one Pydantic `BaseModel` described above. It is not an
  `OpenSCADObject` subclass — it carries non-geometric metadata a geometry
  node has no field for — but `to_scad_object()` wraps its composed children
  in the existing `Translate`/`Union`/`Difference` primitives, tagged with a
  comment naming the role and name (e.g. `// Structure: frame`, `//
  Substructure: bearing_mount`, `// Feature: m3_clearance_hole`), so
  generated `.scad` output stays human-legible without new rendering
  machinery — `render()`/`render_jscad()` on `Assembly` are thin wrappers
  that build a `Scene` from a node's `children` and delegate to it, mirroring
  `Scene.render_jscad()`'s existing delegation to `JSCADRenderer`.
- **Addressing:** `name` at each level is unique within its parent, giving a
  dotted path usable both for human reference and as the natural extension of
  the existing `/parts/{name}` API pattern to `/sites/{name}/structures/{name}/...`
  — the API surface itself is out of scope for this ADR and would need its
  own record.
- **Reuse:** any role is registered the same way `BasePart` is registered
  today (`projects/registry.py`'s pattern extended downward), so a "standard
  V-Slot bracket" Substructure or a "counterbored-M3-hole" Feature becomes a
  library entry usable across many Structures and Sites.

### What this ADR does not decide

- The exact registry/API wiring for reusable Assembly nodes (separate
  record).
- Whether a node needs richer bounding-box or `BasePart`-style
  geometry-metadata integration (`get_bounds`, `preview_color`) beyond what's
  here — likely yes, by extension of the existing pattern, but not specified
  here to keep this ADR to one decision (the shape), not two.
- Migration of the existing `parts/*` registry into this hierarchy. A
  prototype migration (`apothecary/example_parts_library.py`, wrapping each
  registered part as a leaf node) exists to evaluate the shape against the
  real registry, the same way the garage worked example evaluates it against
  a physical layout — nothing here treats that migration as ratified or
  permanent.

## Consequences

- **Additive, not breaking.** `Scene`, `OpenSCADObject`, and every existing
  primitive/boolean/transform are unchanged. Existing parts and JSON scenes
  continue to work exactly as today; `Assembly` is an opt-in layer for
  assemblies that need it.
- **No production/ratified-path implementation exists yet.** Per
  decision-record discipline, this document is Proposed, not Accepted — it
  fixes the shape for human review. The prototype under
  `apothecary/hierarchy.py` exists to let this shape be evaluated against
  real geometry (and, per the migration note above, the real parts registry)
  before ratification, not to stand in for that decision.
- **One class to maintain, not four** — a registry extension pattern for
  reusable nodes, and (eventually, separately) API routes. The cost is paid
  only by assemblies that opt in; a project with no need for the extra depth
  is unaffected.
- **Depth and shape flexibility are traded for per-level type safety.**
  Nothing in the type system stops a "feature"-role node from carrying
  `build_volume`, the way a dedicated `Feature` class once would have
  prevented. Accepted: scenario code (e.g. `example_hierarchy.py`'s
  `job_fits_printer`, which only ever looks at printer-role Structures) is
  what enforces which fields matter for a given role, not the class system —
  the alternative (a class per role) is rejected below for the fixed-depth
  problem it reintroduces.
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
3. **Four fixed levels (Site, Structure, Substructure, Feature as four
   distinct classes, no deeper nesting)** — rejected: matching an assembly's
   real depth to a number fixed in advance isn't possible in general; a
   project needing a fifth level, or a different vocabulary than "garage full
   of printers," has nowhere to put it except forcing an ill-fitting level.
   Evaluated directly against a worked example: extending the garage with a
   genuinely deeper nesting — a Substructure inside a Substructure, a Feature
   carrying its own child Feature — has no home in a four-class scheme, since
   a leaf `Feature` in that shape has no `children` slot at all.
4. **Shared behavior across four distinct classes via a common
   protocol/mixin** (each of Site/Structure/Substructure/Feature keeps its
   own class, but a shared interface — `name`, a children-like list,
   `to_scad_object()`, `world_bounds()` — lets generic operations like
   overlap-checking or revision/diff logic work across all four without
   knowing which one they're touching) — rejected in favor of full collapse:
   a shared protocol still requires deciding, per class, which fields exist
   (does `Feature` get a `children` list? does `Site` get `additions`?), a
   decision a single class with free-form `role` metadata avoids needing to
   make at all, and one that would need revisiting every time a project's
   shape didn't match the four anticipated roles.
5. **Make Feature (or any leaf) a plain function/helper instead of part of
   the Assembly shape** — rejected: a bare function returning an
   `OpenSCADObject` cannot carry `name` for addressing, cannot have
   `children` of its own, and cannot be registered in a reusable library the
   same way a `BasePart` is; the marginal cost of the shared `Assembly` shape
   is small next to losing addressability and uniform recursion.
6. **Replace `Scene` outright with `Assembly`** — rejected: `Scene` is
   simple, already used by every existing part and the JSON scene format
   (`docs/scene-json.md`); breaking it for assemblies that don't need the
   extra hierarchy would violate the additive, opt-in shape this ADR argues
   for. `Assembly` compiling down to `Scene` keeps both true at once.

## Revision triggers

- This ADR is ratified (Accepted, numbered) — the prototype is confirmed as
  the production path, tracked as its own follow-up, not folded silently
  into this document.
- A real multi-system assembly is modeled against this shape and free-form
  `role` metadata proves insufficient in practice (e.g. a project needs a
  genuine type distinction the `role` string can't express) — revisit before
  reintroducing per-role structure.
- The registry pattern this ADR extends (`projects/registry.py`) changes
  shape for unrelated reasons — re-verify the reuse mechanism still fits.
- An API surface, or a compositing/merge mechanism for planning design
  iterations, is proposed for this hierarchy — those records should cite
  this one rather than re-deriving the shape.

## Amendments

*None.*
