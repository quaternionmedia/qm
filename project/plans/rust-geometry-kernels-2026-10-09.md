# A Rust geometry kernel without OpenSCAD: a spike

*A research spike, not a decision; nothing is built on it. It answers the
"researched, not built" half of [the Rust plan](rust-2026-10-08.md): which
kernel could render a scene to STL without OpenSCAD, what each one costs,
and which to try first. Researched on 2026-10-09 against `review/2026-09-26`.
Download counts and stars below are as the registries and repositories showed
them that day; they move. The numbers that compare a kernel with OpenSCAD are
not here: `apothecary kernel-reference` prints the reference's, and
`tests/test_kernel_comparison.py` is where a kernel is measured against them.*

## What a kernel has to cover

The scene language is eleven nodes ([Scene JSON](../../../../docs/scene-json.md);
`apothecary/objects.py`):

| Node | What the kernel must do |
|---|---|
| `cube`, `sphere`, `cylinder` | Primitives. A cylinder takes `r`, or `r1` and `r2` for a cone (a cone is `r2` of zero); `center`; `fn` for the number of facets. |
| `import` | Read an STL or OBJ, then scale, rotate and translate it. The mesh may be one that was never checked to be closed. |
| `union`, `difference`, `intersection` | Booleans on meshes, nested. Top-level scene objects are an implicit union. |
| `hull` | The convex hull of its children. An enclosure shell is four hulled corner cylinders. |
| `translate`, `rotate`, `scale` | Rotation is either Euler angles (OpenSCAD turns about X, then Y, then Z) or an angle about an axis. |

Two things follow before any crate is looked at.

- **OpenSCAD's spheres and cylinders are polygons, not the solids they
  name.** The reference mesh is what `fn` (or OpenSCAD's `$fa`/`$fs` defaults,
  when `fn` is not set) makes of them. A kernel that tessellates differently
  disagrees with the reference by volume and by distance on a sphere alone, and
  that is not a fault in its booleans. The adapter has to build primitives the
  way OpenSCAD does (the ring and facet layout), or the comparison has to say
  which of the two it measured. A B-rep kernel (truck, OCCT) models the true
  sphere and tessellates after the operation, so it can never match the
  reference vertex for vertex.
- **STL goes in and STL comes out.** Everything the viewer draws is an STL,
  so a kernel's output is a triangle mesh whatever it works in. A B-rep kernel
  costs a tessellation step; a mesh kernel costs the question of whether the
  mesh it was given is closed.

## The candidates

| | Licence | Build | Primitives, cone | Hull | Import STL | Booleans on |
|---|---|---|---|---|---|---|
| [`manifold-csg`](https://crates.io/crates/manifold-csg) / [`manifold3d`](https://crates.io/crates/manifold3d) | Apache-2.0 OR MIT | C++ (cmake, a C++ compiler, git) | cube, sphere, cylinder with two radii | yes | mesh in (f64), no STL reader | meshes (Manifold) |
| [`manifold-rs`](https://crates.io/crates/manifold-rs) | MIT OR Apache-2.0 | C++ | the wrapper's own subset | not checked | not checked | meshes (Manifold) |
| [`csgrs`](https://crates.io/crates/csgrs) | MIT | pure Rust | cube, sphere, cylinder, frustum, cone | yes | STL, OBJ, others behind features | meshes (BSP trees on crates.io) |
| [`boolmesh`](https://crates.io/crates/boolmesh) | MPL-2.0 | pure Rust | none (removed in 0.1.10) | no | no | meshes (a port of Manifold's algorithm) |
| [`truck`](https://github.com/ricosjp/truck) | Apache-2.0 | pure Rust | by revolve and extrude | no | meshes only for output | B-rep (NURBS) |
| [Fornjot](https://github.com/hannobraun/fornjot) | 0BSD | pure Rust | few | no | no | B-rep; archived |
| [`opencascade`](https://crates.io/crates/opencascade) (opencascade-rs) | LGPL-2.1 | C++ (cmake; OCCT as a submodule) | yes | no solid hull that I found | STL and STEP | B-rep (OCCT) |

Every licence above can be used from an MIT repository. The question for a
dependency is the one the license check asks, below, and the LGPL row is the
only one that is not on its allowlist.

### Manifold through Rust bindings

[Manifold](https://github.com/elalish/manifold) is the kernel OpenSCAD itself
uses behind `--backend=manifold`, which is what `apothecary/projects/parts/stl_renderer.py`
passes when the OpenSCAD has it. It is Apache-2.0, in C++, and its stated
purpose is "guaranteed manifold output": a manifold in gives a manifold out,
with no cleanup pass. Blender, Godot and OpenSCAD use it.

There are three binding crates, and the first is the one to look at.

- **`manifold-csg`** (repository [zmerlynn/manifold-csg](https://github.com/zmerlynn/manifold-csg),
  version 0.4.1 released 2026-09-09; created April 2026, fifteen versions
  since; `manifold3d` is a facade that re-exports it under another name, same
  version, same repository). Safe wrappers over the Manifold C API with f64
  mesh data. Its README lists cube, sphere, cylinder (the example calls
  `Manifold::cylinder(30.0, 5.0, 5.0, 32, false)`: height, two radii, facets,
  centred), the three booleans, convex hull, transforms, Minkowski, 2D
  cross-sections, and mesh in and out; its I/O is OBJ, so an STL needs a reader
  in front (the `stl_io` crate, or the thirty lines `apothecary/meshes.py`
  spends in Python). Apache-2.0 OR MIT. Two open issues on 2026-10-09, one of
  them the maintainer's own "reduce build time"; the second is a bot's
  tracker for upstream pins. Built by a `-sys` crate whose first build clones
  and compiles Manifold, Clipper2 and a shim with cmake: that is the whole cost.
  `MANIFOLD_CSG_LIB_DIR` points it at a prebuilt Manifold for offline builds.
  Rust 1.85 or newer.
- **`manifold-rs`** ([WilstonOreo/manifold-rs](https://github.com/WilstonOreo/manifold-rs),
  0.7.0, last published 2026-02-24). A smaller wrapper over the same C++.
  Older and less used than `manifold-csg`; not looked at further.
- **`manifold-csg-sys`**: the raw FFI under the first; not a thing to call.

*Robustness.* Manifold requires its inputs to be manifold. An imported STL
that is not closed, or whose vertices are not welded, is refused or must be
merged first; that is the behaviour to measure on the import case, and
OpenSCAD 2021.01's CGAL backend refuses the same meshes, so it is not a
regression. Output is manifold by construction, which is the property a
slicer needs. The STL format itself is lossy for Manifold's purposes (it
recommends 3MF or glTF), which matters here only in that vertices must be
merged when a mesh is read.

*Maturity.* The bindings are new (five months old); the kernel is not. The
risk is the bindings' maintenance, not the algorithm.

### csgrs

[csgrs](https://github.com/timschmidt/csgrs) ("constructive solid geometry on
meshes in Rust") is MIT and pure Rust, with an OpenSCAD-like API: cube,
sphere, cylinder, frustum, cone, torus, extrusions, convex hull, Minkowski
sum, STL/OBJ/PLY and others behind feature flags. It is the closest to the
scene language in what it can say, and it needs no C++ toolchain.

Two things to hold apart when reading its page. The version on crates.io is
0.20.1 (2025-07-24, thirty-five versions since January 2025, tens of
thousands of downloads), whose booleans are **BSP trees** on meshes. The
repository's `main` is 0.23.0 and says its booleans run on a newer set of
sibling crates (`hypermesh`, `hyperreal`: exact predicates), which `Cargo.toml`
there names as local path dependencies, so a build from `main` is not a build
from crates.io. Which of the two a person gets is a choice to make
deliberately, and the second is a bet on a stack that is not published yet.

*Robustness.* BSP-tree booleans are known to be sensitive to coplanar faces
and numeric tolerance, and the open issues of the repository on 2026-10-09
include non-manifold results ("Cube with a tube in the center is not a
manifold"; "Extruded text is not manifold"), a stack overflow in tree building,
and NaNs in tessellation. Its own text says boolean inputs must be finite,
closed and oriented. The nested-boolean and coplanar-face cases in the corpus
are exactly where this would show.

### boolmesh

[boolmesh](https://github.com/komietty/boolmesh) is a from-scratch pure Rust
port of Manifold's boolean algorithm (MPL-2.0; version 0.1.10 on 2026-09-18,
nine versions since November 2025; its dependencies are `glam`, and `rayon`
if asked). It does booleans and nothing else: version 0.1.10 removed the
primitives and transforms "to keep the codebase focused", and it has no hull
and no importer. Used here it would be the boolean engine under our own
primitives, hull and reader. That is a lot to write for a library whose
version number says 0.1. MPL-2.0 is file-level copyleft and is on the license
check's allowlist; unmodified use in a binary needs no more than a notice.

### truck

[truck](https://github.com/ricosjp/truck) is a pure Rust B-rep kernel (NURBS
surfaces, `truck-shapeops` for booleans, `truck-meshalgo` to tessellate),
Apache-2.0, with a long history and a large user base for a Rust CAD crate.
The crates on crates.io (0.6.0 for modelling, `truck-shapeops` 0.4.0) were last
published in September 2024, and the repository has had commits since: its open
issues on 2026-10-09 include boolean operations that mishandle coincident
geometry, boolean operations that "take a long time", and STEP loading that
panics on a tolerance. It has no hull. A sphere is a revolve of an arc, which
is the true sphere, not OpenSCAD's polygon, so volume and distance against
the reference carry a tessellation difference by design. Coincident faces
are the normal case in apothecary scenes (a cutter flush with a face), and
that is the weak spot named in its issues. It is the choice if a real CAD
exchange (STEP) ever matters, and a poor fit for rendering OpenSCAD scenes.

### Fornjot

[Fornjot](https://github.com/hannobraun/fornjot) (0BSD) was an early-stage
B-rep kernel. Its repository was **archived on 2026-06-19** and says the
project is no longer in development and unsuited to real use. Excluded; it is
here so nobody spends a morning finding that out.

### opencascade-rs

[opencascade-rs](https://github.com/bschwind/opencascade-rs) binds OCCT, the
open-source CAD kernel of FreeCAD and many others. The `opencascade` crate is
0.3.0 (last published 2026-08-24, a few thousand downloads), described by its
author as a work in progress and a spare-time project. It is LGPL-2.1, as OCCT
is (with an exception for OCCT's own headers). OCCT is the most capable
kernel here: true booleans on B-reps, fillets, STEP, STL both ways. It is
also the heaviest build (OCCT compiled from a submodule by cmake, or a system
install) and the only licence on this list outside the license check's
allowlist; statically linked into a distributed binary, LGPL-2.1 asks for the
means to relink. It has no solid convex hull that I found, and its booleans are
B-rep booleans, so it carries truck's tessellation difference. Overkill for
cubes, cylinders and spheres.

### Others found

- **IFClite's exact CSG kernel** ([LTplus-AG/ifc-lite](https://github.com/LTplus-AG/ifc-lite);
  [write-up](https://osarch.org/2026/06/12/ifc-lite-exact-csg-kernel/)): pure
  Rust, exact predicates, mesh arrangements, MPL-2.0. Built for IFC wall
  openings, not as a general library; whether it can be used standalone from
  its crates I could not confirm. Worth reading if exactness on coincident faces
  becomes the question, not worth wiring.
- **`baby_shark`** (pure Rust mesh processing with boolean operations):
  turned up in the search and not looked at beyond that.
- **Python `manifold3d`** (the same C++ kernel, from the Python side) is not
  Rust and is mentioned only because it would be the shortest road to a
  comparison today, were the question the kernel and not the language. It adds
  a wheel dependency this repository does not have.

## How it would be called

Two shapes, and the first needs no new idea.

1. **A command that reads the scene's JSON and writes an STL.** A Rust binary,
   `apothecary-render scene.json -o out.stl`, taking the same JSON as
   `apothecary render` and the Scene JSON format already documents. The
   Python side calls it with `subprocess`, as `OpenSCADRenderer` calls OpenSCAD,
   and gets a `RenderResult`. This keeps the Rust out of the wheel, lets the
   binary be fetched at install time as OpenSCAD is, and makes the kernel an
   interchangeable executable: the comparison harness's adapter is exactly this
   (`render(scene_json, out_path)`). It could live in `apothecary-service`
   (see the Rust plan) as a subcommand or as the service's renderer.
2. **A library inside Python** (PyO3, the `apothecary-core` stub). Saves a
   process start; costs a native wheel for every platform, which is the
   packaging the plan chose not to take on yet. Not for a first try.

Either way the Rust side owns the translation the Python side does in
`render()`: the `fn` to facet rule, `Rotate`'s two forms, `Cylinder`'s radii
rule (one of `r1`/`r2` alone sets both), `Import`'s scale-rotate-translate
order, and the implicit union at the top. `apothecary/jscad.py` is the one
place that already does that translation for another backend, and it is the
shape to follow; it has a hull too, so the node list is already proven to map.

## Which to try first

**`manifold-csg`.** It is the same algorithm as the reference, so a
difference in the numbers is the glue (tessellation, rotation order, welding
on import) and not the kernel, and that is the cleanest first measurement
there could be. It covers every node. It is licensed like this repository. Its
cost is the C++ build: a C++ compiler and cmake on the machine that builds
the binary, a first build that clones from the network (to be written into
the personal-data record's install-time list, as the Rust plan says of every
fetch), and the same again on every platform the OpenSCAD installer covers. A
user would fetch a built binary, not build one.

If that cost is the objection, the second try is **csgrs from crates.io
(0.20.1)**, pure Rust, to see how far BSP booleans get on the corpus
before deciding whether the exact-arithmetic main branch is worth waiting for.
Its failures on coincident faces, if any, would show in the nested-boolean
cases and the real parts. truck, Fornjot and OCCT are not worth a first try
for OpenSCAD-shaped scenes: a different tessellation, no hull, and in OCCT's
case a heavy build and an LGPL dependency.

## What a Rust dependency does to the checks

The part of the Rust workspace that belongs to this choice is the license check. `.github/workflows/license-check.yml`
audits Python packages against an allowlist with `pip-licenses`. A Rust
dependency is not in that report. The governance draft on open-license
exclusion (`governance/qm/records/DRAFT-open-license-exclusion-and-upstream-remediation.md`)
names `cargo-license` for Rust, so the check, once a crate has a dependency,
needs: Rust installed in the job, `cargo install cargo-license` (or a prebuilt
binary), and `cargo license --json` run over the workspace, its licence
expressions checked against the same allowlist. Expressions such as
`Apache-2.0 OR MIT` pass if either side is allowed; `MPL-2.0` is on the list;
`LGPL-2.1` (opencascade-rs) is not and would need a decision before it was
admitted. The two stubs have no dependencies yet, so the check has nothing to
report today.
