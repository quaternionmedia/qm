# ADR-XXXX — Formalize the graphbase submodule interface; keep it a submodule

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-06-30 |
| **Pends on** | graphbase PR #8 reaching graphbase's `main`: the root `__init__.py` this record makes the contract exists only on its branch `fix/graceful-mongo-unavailable`, where this project's pin `b422fc0` sits |

## Context

`graphbase` is a git submodule with its own FastAPI application. Two callers
in the parent package import from it:

- `codecarto/main.py` — mounts the `graphdb` APIRouter at `/db`
- `codecarto/services/cache_service.py` — borrows the shared MongoClient via
  `get_db()` to avoid opening a second connection

An import such as `from graphbase.src.main import ...` reaches into the
submodule's internal module layout. Python resolves it at runtime, with no
static import boundary, so restructuring `graphbase/src/` (splitting
`main.py`, say) would break such a caller silently.

graphbase is mounted only when `MONGODB_URI` is set, and a shell that does not
inherit the variable is a common way for it to be unset without anyone
noticing: git-bash does not pick up Windows user-scope variables set through
PowerShell or the registry. A `try/except` that swallows a failed mount leaves
nothing at startup to say which of the two happened.

## Decision

- **The public surface is the package root.** `graphbase/__init__.py` exports
  `graphdb` and `get_db`, and callers write `from graphbase import graphdb,
  get_db` — a single-module path that stays stable if `graphbase/src/main.py`
  is split. `graphbase/src/__init__.py` re-exports the same two names; nothing
  in `codecarto` imports it. In development graphbase is not installed: it
  is imported from the repository root. The Docker image copies it to
  `/app/graphbase` and installs it with `pip install -e`.
- **graphbase stays a submodule.** Its standalone deployability — it ships its
  own FastAPI app and `docker-compose.yml` — is a feature, not incidental.
  Absorbing it into `codecarto` would tie releases together and remove the
  ability to run graphbase as an independent service.
- **The mount says what happened.** `main.py` logs at info on a successful
  mount, at error when the import fails, and at info when `MONGODB_URI` is
  absent, naming the git-bash inheritance gap — the failure mode met in
  practice, and the fastest path to diagnosing the next one. With graphbase
  off, `GET /db/` answers `{"available": false, "reason": "graphbase is off:
  set MONGODB_URI to enable /db/*"}` rather than a 404, and every other
  `/db/*` route stays unmounted.

## Consequences

- Restructuring `graphbase/src/` requires updating only the root
  `__init__.py`, not every caller in the parent package.
- Every server start logs either the mount or the instruction to set
  `MONGODB_URI`, and the front end can ask `/db/` whether the store is on
  without logging an error in the browser. `tests/test_graphbase_off.py`
  asserts the off answer and that `/db/bookmarks` stays a 404.
- The root `__init__.py` is a versioned contract surface. Removing `graphdb`
  or `get_db` from it is a breaking change to `codecarto` and is coordinated
  as a submodule update, not a silent internal refactor.
- The pin is not on graphbase's `main`. `b422fc0` sits on
  `fix/graceful-mongo-unavailable`, seven commits ahead of `main`, and those
  commits carry everything `codecarto` uses beyond graph CRUD: the root
  `__init__.py`, the exports in `src/__init__.py`, the bookmarks, snapshots and
  history routes, and the 503 when MongoDB is unreachable. graphbase's `main`
  has an empty `src/__init__.py` and the graph routes only. Where graphbase's
  remote can be read, `check_submodule_pins.py` finds the pinned commit on
  that branch; a CI runner cannot read it, and the check reports the pin as
  unchecked rather than as passing.

## Alternatives considered

1. **Absorb `graphbase` into `codecarto` as an inline module** — rejected: the
   submodule's standalone deployability is intentional and is kept.
2. **Leave imports as `from graphbase.src.main import ...`** — rejected: the
   internal-path import is fragile; the public-surface pattern costs nothing
   and removes a class of silent breakage.

## Revision triggers

- `codecarto` needs a graphbase symbol beyond `graphdb` and `get_db` — extend
  the root `__init__.py` rather than reaching into `graphbase.src.*`.
- A second project depends on graphbase — document the contract in the
  submodule's own README at that point.
- graphbase PR #8 merges, closes, or its branch is deleted — the pin moves to
  graphbase's `main`, or the surface and routes need a new home.

## Amendments

*None.*
