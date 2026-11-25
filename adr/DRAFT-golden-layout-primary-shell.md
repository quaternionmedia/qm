# ADR-XXXX — Golden Layout as the primary application shell

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-06-30 |
| **Pends on** | codecartographer's `fix/shell-backports` reaching `main`; each *Pending* note says what `main` does until then |

## Context

The original frontend shell (`web/src/components/codecarto/codecarto.ts`,
741 lines, plus `codecarto.css`, 268 lines) hand-rolls panel layout, tab
switching, and panel sizing as one monolithic Mithril component tree. Any
new dockable panel means threading new state and DOM through that file.
Two independent local branches converged on the same fix at about the same
time: the old shell is a known pain point, not a stylistic preference.

## Decision

Adopt Golden Layout 2.x (`golden-layout` npm package) as the primary
application shell. `web/src/layout/golden_layout_shell.ts` is the
top-level component; `codecarto.ts` is deleted entirely. Each dockable
area (graph, file tree, graph settings, actions/plotbar and the rest of
`panel_registry.ts`) is registered as a GL component factory function
(`glInstance.registerComponentFactoryFunction(panelId, ...)`), mounting a
small dedicated Mithril component into the container GL gives it. Panel
lifecycle hooks use GL2's `beforeComponentRelease` event (not `close`,
which GL2 does not emit on `ComponentContainer` — confirmed by trial, and
called out in an inline comment so it isn't "fixed" back to `close` later
by someone trusting the more intuitive name); on release the shell
unmounts the panel's Mithril root (`m.mount(container.element, null)`), so
a closed panel stops drawing. GL follows its container's size by itself
only when that container is `<body>`, so the shell sets
`resizeWithContainerAutomatically` with a zero debounce interval, and the
dock follows the window at once. *Pending:* on `main` a closed panel's root goes on
redrawing into a detached element, and the dock keeps the size it was
built at.

## Consequences

- New panels are a registration, not a rewrite of the shell — see
  *Generalize dock panels into a registry; add a window-add menu*, which
  extracts the per-panel config into `panel_registry.ts`.
- GL2 pop-out windows are a known limitation: `registerComponentFactoryFunction`
  callbacks are bound to the *original* window's Mithril instance and are
  not replayed in a pop-out, which renders only the GL frame chrome with
  an empty content area. Rather than fix that binding gap, no panel offers
  to pop out (`header.popout: false`, `default_layout.ts`). *Pending:* on
  `main` every stack's header offers the pop-out control, and
  `popInOnClose: true` returns a panel to the dock only when its empty
  pop-out window closes.
- The header's restore-closed-panel mechanism (`hiddenDockPanels` /
  `restoreDockPanel` in `layout_context.ts`) used the structurally correct
  `beforeComponentRelease` event but imported `LayoutManager` type-only
  while using it as a runtime value (`LayoutManager.defaultLocationSelectors`),
  so every restore click since the shell's adoption threw a
  `ReferenceError`, silently. *Generalize dock panels into a registry; add
  a window-add menu* has the fix and the detection method (a live console
  error, not static review).

## Alternatives considered

1. **Incrementally refactor `codecarto.ts`** instead of replacing the
   shell — rejected: the state-threading problem is structural (manual
   DOM/Mithril coordination for dock/undock/resize), not a matter of file
   organization.
2. **Roll a custom minimal docking layout** — rejected: GL2 already solves
   drag-to-dock, resizable splits, and stack/tab grouping; doing that well
   is a large surface for a project this size to own.

## Revision triggers

- GL2 ships a fix for the pop-out Mithril-binding gap, making the
  workaround unnecessary.
- Panel count or layout complexity grows enough that GL2's API surface
  becomes a bottleneck rather than a convenience.

## Amendments

*None.*
