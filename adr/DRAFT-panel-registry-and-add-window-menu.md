# ADR-XXXX — Generalize dock panels into a registry; add a window-add menu

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-06-30 |
| **Pends on** | codecartographer's `fix/shell-backports` reaching `main`; each *Pending* note says what `main` does until then |

## Context

The fixed 5-panel `DOCK_PANEL_CONFIGS` map was duplicated across
`layout_context.ts` (config) and `golden_layout_shell.ts` (five
near-identical `registerComponentFactoryFunction` calls plus a manual
label switch). There was no way to add a panel except via the header
restore buttons, which only ever appear for a panel the user had already
closed — no "+" control, no right-click, no saved/default layouts.

Separately, the header's closed-panel restore button threw
`ReferenceError: LayoutManager is not defined` on every click.
`layout_context.ts` imported `LayoutManager` via `import type { ...,
LayoutManager } from 'golden-layout'`. `import type` is erased entirely
at compile time, but `restoreDockPanel()` reads
`LayoutManager.defaultLocationSelectors` as a runtime value — a static
property access with no binding left in the emitted JS. The bug predates
this work and is the actual reason restore had never functioned.
`vite build` transpiles per file without cross-module type checking, so
the misuse compiled cleanly and shipped silently every time; it surfaced
via a live browser console, not a source read.

## Decision

- Extract the panel list into `panel_registry.ts` — one array of
  `{ id, menuLabel, config, overflow, mount }`, replacing the
  `DOCK_PANEL_CONFIGS` map and the five duplicated
  `registerComponentFactoryFunction` calls with a loop over the registry.
  Same registration-table pattern as `ParserRegistry` (backend) and the
  renderer registry (`renderers.ts`, frontend).
- Fix the restore bug at its source: import `LayoutManager` as a value
  (`import { LayoutManager } from 'golden-layout'`), and keep
  `import type` for names used only as types. `hiddenDockPanels` /
  `hideDockPanel` / `showDockPanel` / `restoreDockPanel` keep their
  existing shape — the defect was the import, not the surrounding logic.
- Add a header "+" button and a Ctrl+right-click handler on the dock area,
  both opening `AddPanelMenu` (`web/src/layout/components/add_panel_menu.ts`)
  — a dropdown listing registered panels not currently in the layout
  (`LayoutContext.addablePanels()`), reusing `restoreDockPanel()` (it
  already handles "add if missing, show if hidden" in one method).
- Add layout persistence: `saveLayoutAsDefault()` serializes
  `LayoutConfig.fromResolved(LayoutManager.saveLayout())`, the form
  `loadLayout` reads, to `localStorage['cc:gl-layout:default']`;
  `loadInitialLayoutConfig()` is consulted on boot instead of always
  loading `DEFAULT_LAYOUT_CONFIG`; `resetLayoutToBuiltinDefault()` clears
  the saved entry. Save and reset live in `AddPanelMenu` under a
  "Layout" section, to avoid adding more header chrome than one button.
  *Pending:* on `main` the save serializes `LayoutManager.toConfig()`,
  Golden Layout's resolved form, which `loadLayout` cannot read, so the
  next visit opens with no panels.

## Consequences

- Adding a dock panel is one entry in `panel_registry.ts`, not edits
  across three files.
- Restore, add-window, and layout persistence all route through the same
  `restoreDockPanel()` / `LayoutManager` calls, so there is one place to
  reason about dock-panel placement rather than three.
- `saveLayoutAsDefault()` / `resetLayoutToBuiltinDefault()` persist panel
  arrangement and sizing only; they do not version or migrate the saved
  config if `panel_registry.ts`'s panel ids change later. GL throws on a
  component type nobody registered, so `loadInitialLayoutConfig()` checks
  a saved layout against the registry first (`saved_layout.ts`): a stale
  one referencing a removed panel id is forgotten, the built-in default
  opens, and a toast says why. *Pending:* on `main` such a layout throws
  on load and the page opens with no panels.
- `npm run build` runs `tsc --noEmit` before `vite build`, and `tsc`
  refuses a name imported with `import type` and used as a value; no CI
  workflow runs it, so a pull request can carry a bug of this exact shape
  with every check green. Adding a `tsc --noEmit` CI step is a worthwhile
  follow-up; the header of `.github/workflows/pytest.yml` records the gap.

## Alternatives considered

1. **Rewrite the restore mechanism from scratch** instead of fixing the
   import and building alongside it — rejected: the actual defect is a
   one-line import correction; a rewrite would not have been guaranteed
   to touch it and would have discarded a working design (registry +
   menu + persistence) for no benefit.
2. **Add a `tsc --noEmit` CI gate as part of this change** — deferred:
   real value, but a build-pipeline change is a separate decision from
   the panel-registry work and deserves its own review.

## Revision triggers

- A `tsc --noEmit` CI gate is added, closing the `import type` blind spot
  this ADR documents as open.
- A sixth dock panel or a second add-window entry point is built, testing
  whether `panel_registry.ts`'s shape still fits.

## Amendments

*None.*
