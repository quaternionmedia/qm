# Pictures in the world: what is open

*Split on 2026-10-13 from [Pictures in the world](pictures-in-the-world-2026-09-26.md),
whose Phases 0 and 2 to 4 are built and which `docs/README.md` lists under
History. The design these two phases serve is that plan's, in the words it
was decided in; this page holds what is not built, as it stands on the
branch it was split on. Phase 6 (Selected tethered to the selection) is not
carried here: it was dropped on 2026-10-31, since every section of the viewer
is a window and Selected is one. Plans are dated and exempt from the
durable-text rule.*

## Phase 1 — Gathering leaves core

Decided, not started: photo gathering becomes an optional extra (`project/todo.md`,
*Next round*).

- As it stands: `apothecary/gathering/` is in the package, and
  `pyproject.toml` declares no `photos` extra.
- Proposed (the original plan's Phase 1): gathering is a distribution of its
  own, `apothecary-photos`, a uv workspace member that the `[photos]` extra
  installs; `apothecary/vision/` stays in core whole; `photo gather` and its
  route mount only with the extra, and otherwise `photo gather` names it;
  the build branch of `POST /photos/gather` and `photo gather --open` go.
  The original plan's Phase 1 lists what it delivers, deletes and tests.
- For a person: how gathering leaves core -- the proposal above, or how much
  of `apothecary/vision/` goes with it, which `project/todo.md` leaves to be settled
  when the round starts. The draft record *Personal data stays on the
  device*'s install points (§1) and their test (§7) move with it.

## Phase 7 — The old photo routes closed

- As it stands: `POST /photos`, `GET /photos`, `GET` and
  `DELETE /photos/{name}` and `GET /photos/{name}/picture` answer
  (`apothecary/api.py`), `apothecary/vision/shelf.py` holds what they keep,
  `apothecary photo view` is a command, and walkthrough 11 runs on them.
- To do (the original plan's Phase 7): delete those routes, the shelf and
  `photo view` with its README line; keep `vision/album.py`'s `Album`,
  `Built` and `Provenance`, which gathering's `whole_gathering` uses;
  rewrite walkthrough 11's test to the view routes; a test holds that no
  route registers a site from a picture.
- It follows Phase 1, since walkthrough 11's gathering half is marked
  extra-only there.
