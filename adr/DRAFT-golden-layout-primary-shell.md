# ADR-XXXX — Golden Layout as the primary application shell

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-06-30 |
| **Pends on** | Nothing — ready to be argued |

## Context

The frontend shell this replaces, `web/src/components/codecarto/codecarto.ts`
with its `codecarto.css`, hand-rolled panel layout, tab switching and panel
sizing as one Mithril component tree. Adding a dockable panel meant threading
new state and DOM through that one file. Two independent local branches
converged on the same fix, which is evidence that the old shell was a known
pain point rather than a stylistic preference.

## Decision

Adopt Golden Layout 2.x (the `golden-layout` npm package, 2.6.0 in
`package-lock.json`) as the primary application shell.
`web/src/layout/golden_layout_shell.ts` is the top-level component, and
`codecarto.ts` is deleted. Every dockable panel is registered as a GL component
factory function (`glInstance.registerComponentFactoryFunction(panelId, ...)`),
one per entry in the panel registry, and mounts a small dedicated Mithril
component into the container GL gives it. Panel lifecycle hooks use GL2's
`beforeComponentRelease` event, not `close`, which GL2 does not emit on
`ComponentContainer`. This was confirmed by trial and is called out in an
inline comment, so that a later reader trusting the more intuitive name does
not switch it back to `close`.

## Consequences

- New panels are a registration, not a rewrite of the shell — see
  *Generalize dock panels into a registry; add a window-add menu*, which
  extracts the per-panel config into `panel_registry.ts` and decides how a
  panel is added.
- GL2 pop-out windows are a known limitation: `registerComponentFactoryFunction`
  callbacks are bound to the *original* window's Mithril instance and are not
  replayed in a popped-out window, so a popped-out panel renders only the GL
  frame chrome with an empty content area. `popInOnClose: true`
  (`default_layout.ts`) works around this by returning a panel when its
  pop-out closes, rather than fixing the binding gap.
- GL2 throws `BindError` on a layout naming a component type nothing
  registered, so a stored layout is a contract with the registry. The
  registry record decides what a saved layout naming a removed panel does.

## Alternatives considered

1. **Incrementally refactor `codecarto.ts`** instead of replacing the shell —
   rejected: the state-threading problem is structural (manual DOM/Mithril
   coordination for dock/undock/resize), not a matter of file organization.
2. **Roll a custom minimal docking layout** — rejected: GL2 already solves
   drag-to-dock, resizable splits, and stack/tab grouping; reimplementing that
   well is a large surface area for a project this size to own.

## Revision triggers

- GL2 ships a fix for the pop-out Mithril-binding gap, making the
  `popInOnClose` workaround unnecessary.
- Panel count or layout complexity grows enough that GL2's API surface becomes
  a bottleneck rather than a convenience.
- A Golden Layout major version changes the component-binding or lifecycle
  events this shell relies on (`registerComponentFactoryFunction`,
  `beforeComponentRelease`).

## Amendments

*None.*
