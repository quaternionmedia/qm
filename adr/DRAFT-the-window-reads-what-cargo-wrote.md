# ADR-XXXX — The window reads what cargo wrote, and never runs cargo

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-10-24 |
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
`cargo check --message-format=json`.

Producing either means running cargo in the workspace, and running cargo there
runs that workspace's code. `cargo check` compiles and executes build scripts
and procedural macros. Even `cargo metadata`, which builds nothing, asks the
configured `rustc` for target information, and a repository's own
`.cargo/config.toml` can name that `rustc` or wrap it (`build.rustc`,
`build.rustc-wrapper`). This window is an HTTP service: a route that ran cargo
on a path would run whatever a cloned repository put there, for anyone who can
reach the port.

The estate views already meet the same shape from the other side. dossier
writes its overview as a document and this window reads it, with the time it
was written beside every figure; the window never runs dossier.

## Decision

1. **No route runs cargo, `rustc`, or any toolchain command, on any path.** A
   route reads manifests (`Cargo.toml`, `Cargo.lock`, `.cargo/config.toml`)
   and linker scripts as data, and reads documents a toolchain wrote. Nothing
   in a manifest is executed, including a configured `runner`, which is shown
   as the text it is.
2. **One command runs cargo, and a person runs it.** `codecarto cargo record
   <path>` runs `cargo metadata --format-version 1 --locked` and
   `cargo check --workspace --message-format=json --locked` in the path,
   offline unless asked otherwise, bounded by a timeout that is reported when
   it fires. It writes their output to `metadata.json` and `check.jsonl` in the
   `target/codecarto/` of the workspace root cargo names — the path's own, or
   the workspace above it when the path is a member crate — which is where
   reading the workspace looks. `--locked` keeps cargo from rewriting
   `Cargo.lock`: a lockfile that is missing or out of date is reported, not
   regenerated. A check that fails still writes its document, because the
   diagnostics are what it is for.
3. **A recorded resolution is used only while it is current, and only when it
   is cargo's.** `metadata.json` is used when it is newer than every manifest
   — each `Cargo.toml`, `Cargo.lock` and `.cargo/config.toml` under the path,
   the files cargo resolves from; a linker script, `memory.x` among them, is
   not one, because nothing in it can change cargo's resolution — and carries
   `version: 1` and a `packages` list. Otherwise the manifests are read
   directly and the reading says why: a stale resolution delivered as current
   is worse than a declared one labelled as declared.
4. **Every reading names its engine and every document's state.** The graph's
   metadata and the `/cargo/data` document say whether cargo's resolution or the
   manifests answered, and, for each document, whether it was present, used,
   stale, and why not. An absent document is a sentence — no diagnostics drawn
   is not the same as a clean build — never an empty overlay. So is a check
   that never finished: a `check.jsonl` with no `build-finished` message says
   cargo stopped first, and the reading says a crate with no diagnostic in it
   is not a clean one.
5. **The same holds for any toolchain document read later.** An index from a
   language server, a linker map, a build-timing or unit-graph document, a probe
   trace: recorded by a command a person runs, read by the window with its age.

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
- `cargo record` is the project's first command that executes a workspace's
  code. Its help text says so. What it writes itself is the two documents,
  under the workspace's own `target/`, which Cargo projects already treat as
  disposable, and `--locked` keeps cargo from rewriting `Cargo.lock`.
- The route modules join the estate modules under `tests/test_boundaries.py`:
  they store nothing, start no process, and never raise to the browser.

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
- A recorded document is found used while stale, or a route is found invoking a
  process: either is this record failing, not a detail.

## Amendments

*None.*
