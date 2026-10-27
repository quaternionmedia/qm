# ADR-XXXX — The window reads what cargo wrote, and never runs cargo

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-10-12 |
| **Pends on** | Nothing — ready to be argued |
| **Principle** | `build-the-seam-buy-the-engines`; `seams-on-standard-protocols`; `shrink-the-black-box` |

## Context

codecartographer reads Rust workspaces: their crates, targets, dependencies,
features, build scripts, native libraries and device targets, and what the
compiler last said about them. Much of that is not in the source. Which
features are enabled, which platform-specific dependencies apply, which version
of a crate was chosen and what `rustc` reported are answers only cargo and
`rustc` compute, and they publish them in two documented JSON forms:
`cargo metadata --format-version 1` and the message stream of
`cargo check --message-format=json`. How much memory a firmware's sections use
is an answer only the linker computes, in the map it writes when asked.

Producing any of these means running cargo in the workspace, and running cargo
there runs that workspace's code. `cargo check` compiles and executes build
scripts and procedural macros. Even `cargo metadata`, which builds nothing,
asks the configured `rustc` for target information, and a repository's own
`.cargo/config.toml` can name that `rustc` or wrap it (`build.rustc`,
`build.rustc-wrapper`). This window is an HTTP service: a route that ran cargo
on a path would run whatever a cloned repository put there, for anyone who can
reach the port.

The estate views already meet the same shape from the other side. dossier
writes its overview as a document and this window reads it, with the time it
was written beside every figure; the window never runs dossier.

## Decision

1. **No route runs cargo, `rustc`, or any toolchain command, on any path.** A
   route reads manifests (`Cargo.toml`, `Cargo.lock`, `.cargo/config.toml`,
   linker scripts) as data and reads documents a toolchain wrote. Nothing in a
   manifest is executed, including a configured `runner`, which is shown as the
   text it is.
2. **One command runs cargo, and a person runs it.** `codecarto cargo record
   <path>` runs, in the path, offline unless asked otherwise (`--online`), each
   bounded by a timeout that is reported when it fires:
   - `cargo metadata --format-version 1`, written to
     `<path>/target/codecarto/metadata.json`;
   - `cargo check --workspace --message-format=json`, written to
     `check.jsonl` there;
   - for each `--map BIN`, `cargo rustc --profile <profile> --package <PKG>
     --bin BIN -- <map flag>`, where `PKG` is the workspace member that owns
     `BIN` by the metadata just recorded, so that the linker writes its map to
     `BIN.map` there. The profile defaults to `release`, the one that is
     flashed.

   A check that fails still writes its document, because the diagnostics are
   what it is for.
3. **A recorded resolution is used only while it is current, and only when it
   is cargo's.** `metadata.json` is used when it is newer than every manifest
   and carries `version: 1` and a `packages` list. Otherwise the manifests are
   read directly and the reading says why: a stale resolution delivered as
   current is worse than a declared one labelled as declared. Diagnostics and
   link maps are different: they are drawn while stale, labelled stale, because
   the last thing `rustc` or the linker said is still the best evidence there
   is, and the label keeps it from reading as current.
4. **Every reading names its engine and every document's state.** The graph's
   metadata and the `/cargo/data` document say whether cargo's resolution or the
   manifests answered, and, for each document, whether it was present, used,
   stale, and why not. An absent document is a sentence — no diagnostics drawn
   is not the same as a clean build — never an empty overlay.
5. **The same holds for any other toolchain document.** A link map is read this
   way: recorded by `cargo record --map`, read by `link_map_service` with its
   age, measured against the regions it links into. An index from a language
   server, a build-timing or unit-graph document, a probe trace: each is
   recorded by a command a person runs and read by the window with its age.

Not yet true at codecartographer 00ce9de, the commit this record was checked
against:

- `metadata.json` is compared only against `Cargo.toml`. `_walk` collects
  `Cargo.toml` files as the manifests (`cargo_service.py:314-340`), and
  `_read_metadata` takes the newest of those (`:536-538`), so a changed
  `Cargo.lock` or `.cargo/config.toml` does not make the resolution stale.
  `check.jsonl` and link maps are compared against the newest `Cargo.toml`,
  `Cargo.lock` or `.rs` file, which leaves out `.cargo/config.toml` and the
  linker scripts.
- Diagnostics on the code map are never marked stale. The parse pipeline joins
  `check.jsonl` onto Rust items through `recorded_diagnostics`
  (`:1044-1054`), which reads the document without walking the workspace, so
  the newest source time it compares against is `0.0`, and no document is
  older than that. Each item carries `diagnostics_recorded_at`, and no stale
  flag.

## Consequences

- The dev loop has a step: after an edit, `codecarto cargo record` (or a build
  that writes the same documents) before the window shows new diagnostics. The
  staleness rule makes a skipped step visible instead of silent.
- A repository read from GitHub, with no recorded documents, is drawn from its
  manifests alone. That is the correct answer for a remote the window must not
  build, and the caveat says what it cannot see.
- Staleness is decided by modification times. A checkout writes files in an
  order of its choosing, so a document committed beside its sources can read as
  stale after a clone; tests that depend on staleness set the times themselves.
- `cargo record` is the project's command that executes a workspace's code. Its
  help text says so, and it writes only under the workspace's own `target/`,
  which Cargo projects already treat as disposable.
- The cargo route and its services join the estate modules under
  `tests/test_boundaries.py`: `cargo_router.py`, `cargo_service.py` and
  `construct_service.py` store nothing, start no process, and the router never
  raises to the browser. `link_map_service.py`, which `cargo_service` reads link
  maps through, is not in those lists, and imports nothing that starts a
  process.
- This record decides only what reads a toolchain's output. Two other routes
  start processes, and it does not cover them: `/system/compose`,
  `/system/events` and `/system/ws/replay` run `git` in a clone beside the
  checkout (*The system monitor derives its diagram from a repository's
  contents*), and `/pam` runs `journalctl` on the host when `PAM_USE_JOURNALD`
  is set.

## Alternatives considered

1. **Run `cargo metadata --offline` from the route.** It builds nothing, and is
   the obvious way to get the resolution. Rejected because it still invokes the
   configured `rustc`, which the repository being read can choose; "offline" is
   about the network, not about what runs.
2. **Run cargo from the route inside a sandbox.** The right shape if this window
   ever reads repositories it has not been handed. Rejected for now: it needs a
   toolchain image and an isolation boundary nobody has built or governs, and
   the dev loop is served without it. Named below as a revision trigger.
3. **Read manifests only, never cargo's documents.** Rejected: resolved features,
   platform conditions and diagnostics are cargo's and `rustc`'s answers, and a
   window that guessed them would be a second, wrong implementation of a
   resolver.
4. **A cargo subcommand, written in Rust, that serves the graph.** Rejected: a
   component imported into this project's code is house stack, and the reading
   needs nothing cargo's documented JSON does not already carry.

## Revision triggers

- The estate gains a governed way to run a command in isolation (the harness
  running toolchain jobs under its spend and attestation rules), at which point
  recording could be offered from the window and run there.
- cargo publishes a new `metadata` format version, or changes the shape of its
  JSON messages.
- A reader asks for cargo's resolution of a repository nobody has recorded — a
  remote — often enough to justify Alternative 2.
- Beyond the gaps named in the Decision, a stale `metadata.json` is found used
  as the resolution, or a module in `tests/test_boundaries.py`'s lists is found
  starting a process: either is this record failing, not a detail.

## Amendments

*None.*
