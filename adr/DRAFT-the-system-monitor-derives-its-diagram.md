# DRAFT — the system monitor derives its diagram from a repository's contents

| | |
|---|---|
| **Status** | Proposed |
| **Date** | 2026-08-27 |
| **Pends on** | Nothing — ready to be argued |
| **Principle** | `seams-on-standard-protocols` seams on standard protocols; `decisions-are-documented` decisions documented; `a-check-is-evidence-after-it-fails` a check is evidence only after it has failed |

## Context

The system monitor shipped as one hard-wired instance. `SystemRenderer` was an
abstract class whose only subclass drew the Linux PAM authentication stack, and
`GraphRendererRegistry.register('system', () => new PamRenderer())` fixed that
choice at module load. A `SystemDefinition` interface and a
`SystemDefinitionRegistry` existed beside it — designed for exactly the plural
case — and nothing ever registered a definition, so the control panel's
definition selector was dead code guarded by a length check that could not
become true.

The second monitor wanted was moat: the homelab whose cluster, charts and
provisioning that repository describes. The decisive constraint, set by the
operator when asked: **the monitoring is about the contents of the repository,
never about the repository itself.** A monitor of moat-the-repo (pull request
counts, branch names as subjects) was explicitly not the ask; a monitor of the
homelab moat *declares* was.

That constraint forced the question this record answers: where does the second
diagram come from? PAM's is hand-placed, and hand-placing moat's would create a
drawing that goes stale the day a chart is added — a second copy of the
repository's structure that nothing keeps true, in an estate that has spent the
month finding exactly that class of drift (two stored views going stale
together, `dossier`'s delta board being the worked case).

## Decision

**The renderer is concrete and definition-driven, and a definition may derive
its diagram from a repository's own declarations.**

1. `SystemRenderer` takes no subclasses. It resolves a `SystemDefinition` from
   `styling.systemId` via the registry and owns machinery only: DOM, edges,
   packets, the demo loop, the websocket. A definition drives it through the
   callback surface (`setNodeState`, `firePacket`, `log`, `resetAllNodes`).

2. **PAM is one registration among others**, converted to a definition object
   with identical nodes, edges, demo sequence and event mapping. Current
   functionality is retained, selectable, and no longer privileged.

3. **`DerivedSystemDefinition` builds a diagram from what a repository
   declares**, over two backend endpoints (`/system/compose`, `/system/events`)
   whose derivation rules each read a file whose meaning is fixed by the tool
   that consumes it, never a naming convention:
   - a directory holding `Chart.yaml` is a **chart** (Helm reads that file);
   - a `kind: Application` manifest names what it deploys via
     `spec.source.path` (ArgoCD acts on that field) — moat's `groot` yields
     its six deploy edges this way;
   - `Chart.yaml dependencies` naming another local component is a
     **dependency edge**; an external dependency is an upstream annotation,
     never an invented node;
   - `*.tf` is **infrastructure**; a `Dockerfile` without a chart is an
     **application** the repo builds.

4. **Events are the history of the same contents.** Commits map onto the
   components whose files they touched; branches ahead of the default branch
   are **in-flight changes** — the offline proxy for open pull requests,
   labelled as a proxy in the payload and in the log, because pull request
   state lives on the host and this reads none of it. Every replayed frame
   carries `replay: true` and the badge says DEMO or the log says REPLAY:
   history dressed as a live tail would teach a reader the homelab is busier
   than it is.

5. **moat is the default `systemId`**; PAM remains in the selector. The
   repository a derived definition reads is resolved by name beside the
   checkout (one path segment, separators refused), with
   `CODECARTO_REPO_ROOTS` replacing — never extending — the roots.

## Consequences

- A chart added to moat appears on the monitor at the next compose, with no
  layout edit. The same class instantiates for any sibling repository
  (`/system/repos` lists what is reachable), though the derivation rules are
  chart/terraform/container-shaped and a repository declaring none of those
  derives an honest, near-empty diagram.
- The platform-free half (`system_core.ts`: types, registry, layout, replay
  sequencing) builds without the DOM lib and is tested under `node --test`,
  the same split rad's core made and for the same reasons. The layout tests
  found their first real defect before the demo did: at forty charts the
  fixed column step walked off the canvas (`px=1.03`).
- The seam grew a test discipline finding worth keeping (`a-check-is-evidence-after-it-fails`): the router's
  traversal refusals passed green through two versions that proved nothing —
  first against escape targets that did not exist, then against a guard whose
  doubled defence covered the mutation. A refusal test is evidence only when
  the thing refused would otherwise have succeeded.

## Alternatives considered

**Curated moat layout, like PAM's.** Best-looking result and rejected as a
second copy of the repository's structure that nothing keeps true. The
operator chose full derivation when asked directly.

**Monitor the repository (pull requests, checks, branches) rather than the
system it describes.** Rejected by the operator in exactly those words; also
already half-built elsewhere in the estate (`dossier deltas drift`), where the
subject really is the repository.

**Read the cluster instead of the repo.** The truest possible monitor and a
different feed with different credentials; nothing local can know whether a
pod is up. Deliberately out of scope; the diagram claims declarations and
changes, and says nothing about runtime state.

**Keep subclassing as the extension seam.** One subclass had already sat as
"the" system for months while the definition interface rusted unused beside
it. An interface nothing instantiates twice is a diagram of intent.

## What this cannot do

Say whether the homelab is up. Say whether an in-flight branch has an open
pull request. See a pull request that was closed without merging, which
leaves no trace in the default branch. Derive components from conventions
other than chart/terraform/container without a new rule, argued here first.

## Revision triggers

- A second derived repository needs derivation rules this record does not
  name — the rule belongs here before it belongs in code.
- A runtime feed (cluster events, webhooks) is wired in — §4's "declarations
  and changes only" boundary is then wrong and this record must say what the
  monitor now claims.
- The offline in-flight proxy misleads in practice — a branch read as
  in-flight whose pull request closed long ago — in which case the proxy
  needs host data or needs removing, not softening.
