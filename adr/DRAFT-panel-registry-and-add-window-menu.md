# ADR-XXXX — Generalize dock panels into a registry; add a window-add menu

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-06-30 |
| **Pends on** | Nothing — ready to be argued |

## Context

Every dockable panel is a Golden Layout component, and each needs the same
facts: its GL config, its menu label, its overflow and its Mithril mount.
Without one list of panels, those facts live in a config map in
`layout_context.ts` and in one `registerComponentFactoryFunction` call per
panel in `golden_layout_shell.ts`, so a new panel is an edit in three files.
And a panel that is not in the layout can be reached only by whatever control
happens to re-open it.

Golden Layout 2.6.0 does not skip a component it cannot bind. A
`ComponentContainer` binds its component as it is built, and a component type
with no registered factory, on a layout with no `bindComponentEvent`, throws
`BindError` (`VirtualLayout.bindComponent`). So `loadLayout` on a saved layout
that names a panel id missing from the registry throws, and the shell does
not boot. This is established by reading golden-layout 2.6.0's source; it was
not reproduced for this record.

A type-only import used as a runtime value compiles under `vite build` and
fails in the browser, because `vite` transpiles each file with esbuild and
checks no types. The header's restore button threw `ReferenceError:
LayoutManager is not defined` on every click for that reason:
`import type { LayoutManager }` read as `LayoutManager.defaultLocationSelectors`.
`tsc --noEmit` reports that misuse as a compile error.

Starting a graph needs a source, the parse options and a Plot button. Spread
across an Upload, a Repository and an Actions panel, the same Quick Start and
parse options render in two panels, a Recent list renders in two, and Plot
sits in a third.

## Decision

- **One registry.** `panel_registry.ts` is one array of
  `{ id, menuLabel, config, overflow, mount }`, and the shell registers every
  panel with one loop over it. Same registration-table pattern as
  `ParserRegistry` (backend) and the renderer registry (`renderers.ts`,
  frontend).
- **The header + menu is the only way to add a window.** It opens
  `AddPanelMenu` (`web/src/layout/components/add_panel_menu.ts`), which lists
  every registered panel not in the layout (`LayoutContext.addablePanels()`),
  closed ones included, and adds the chosen one through `restoreDockPanel()`,
  which adds a panel that is missing and brings forward one that is present.
  There is no second add-window entry point: no dock context menu and no header
  restore strip.
- **A panel opened from context uses the same function.** An Estate row opens
  Topology, Capabilities or Overview, and View ▸ Compare on a node opens
  Chrestomathy, each through `restoreDockPanel()`. **A source that loads data
  for a panel brings that panel forward.**
- **One Open panel (id `open`) is where a graph starts.** It holds every
  source — a GitHub URL, the examples, local files, the demo and the lexicons,
  and one Recent list — the parse options once, and one Plot / Cancel bar.
  Graphbase keeps Saved, Snapshots and History. Files keeps click-a-file. The
  default dock is Graph · Open · Files · Graph Settings · Estate.
- **Import `LayoutManager` as a value.** `restoreDockPanel()` reads
  `LayoutManager.defaultLocationSelectors` at runtime, so it is imported with
  `import { LayoutManager }`; `LayoutConfig` stays `import type`, since it is
  type-only. `npm run build` runs `tsc --noEmit` before `vite build`, and
  `npm run typecheck` runs it alone.
- **Layout persistence.** `saveLayoutAsDefault()` serializes
  `LayoutManager.toConfig()` to `localStorage['cc:gl-layout:default']`;
  `loadInitialLayoutConfig()` is consulted on boot instead of always loading
  `DEFAULT_LAYOUT_CONFIG`; `resetLayoutToBuiltinDefault()` clears the saved
  entry. The two actions live in `AddPanelMenu` under a "Layout" section, so
  they add no header chrome.
- **A saved layout never stops the shell booting.** A saved layout that names
  a removed panel id is migrated to `open` when the id is one the Open panel
  replaced, and otherwise falls back to the built-in default. This is what
  Golden Layout's `BindError` makes necessary.

Not yet true at codecartographer 00ce9de, the commit this record was checked
against:

- Ctrl+right-click on the dock opens the add-window menu
  (`golden_layout_shell.ts:164-174`), and the header shows a "Restore" button
  per closed panel (`:137-145`).
- Upload (`upload-panel`), Repository (`repo-panel`) and Actions (`plotbar`)
  are separate panels, and the default dock is Graph, Files, Upload,
  Repository, Graph Settings, Actions and Estate.
- `glInstance.loadLayout(ctx.loadInitialLayoutConfig())` runs outside any
  `try` (`golden_layout_shell.ts:70`), and `loadInitialLayoutConfig()` guards
  only `JSON.parse` (`layout_context.ts:245-253`), so a saved layout naming an
  unknown panel id throws at boot — by the reading of golden-layout in
  Context, not reproduced.
- A bundled example that carries recorded cargo documents loads them for the
  Cargo panel without bringing the panel forward (`layout_context.ts:1068-1073`).
- No workflow runs `tsc --noEmit`. codecartographer #119 adds `web.yml`, whose
  `suites` job runs `npm run typecheck`.

## Consequences

- A new dock panel is one entry in `panel_registry.ts`, not edits across
  three files.
- The + menu, the context openers and layout persistence all go through
  `restoreDockPanel()` and the one `LayoutManager`, so there is one place to
  reason about where a panel lands.
- One way to add a window means one thing to document and one thing to test.
  A reader who closes a panel finds it again in the + menu, which lists it.
- `saveLayoutAsDefault()` / `resetLayoutToBuiltinDefault()` persist panel
  arrangement and sizing only (`LayoutManager.toConfig()`). A saved layout is
  versioned by nothing but the ids it names; the migration in the Decision is
  the whole of its upgrade path, and it is extended whenever a panel id is
  removed.
- Until `tsc --noEmit` runs in CI, an `import type` misused as a value is
  caught only by whoever runs `npm run build` or `npm run typecheck`.

## Alternatives considered

1. **Rewrite the restore mechanism from scratch** instead of fixing the import
   and building alongside it — rejected: the defect was a one-line import; a
   rewrite would not have been guaranteed to touch it and would have discarded
   a working design (registry + menu + persistence) for no benefit.
2. **Keep the dock context menu and the restore strip beside the + menu** —
   rejected: three ways to reach one list, and the restore strip's tooltips
   named panels by raw id where the menu used their labels. Each path is a place for
   the others to drift from.
3. **Let Golden Layout skip an unknown panel** — not available: 2.6.0 throws
   rather than skipping, and binding a placeholder through `getComponentEvent`
   would put a blank panel in the layout. Migrating the saved layout before loading it keeps
   the failure out of Golden Layout entirely.
4. **Keep Upload, Repository and Actions as three panels and deduplicate their
   contents** — rejected: the duplication follows from splitting one task, start
   a graph, across three panels; a reader still has to learn which of the three
   holds the control they want.

## Revision triggers

- A second way to add a window is proposed — the one-entry-point rule is then
  being relaxed, and this record says why or refuses it.
- A panel needs a fact the registry entry cannot carry (a precondition, a
  per-panel default size, a dependency on a backend feature), testing whether
  `panel_registry.ts`'s shape still fits.
- A saved layout fails to boot in the field — the migration in the Decision
  missed an id.
- A `tsc --noEmit` gate runs in CI, closing the `import type` gap this record
  names.

## Amendments

*None.*
