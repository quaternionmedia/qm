# Workspace review — 2026-09-21

This is a dated review of the repositories visible in the QM workspace. It is
an inventory of holes and open work, not a backlog or a release assessment.
Repository state was checked on 2026-09-21. A repository with no test or CI
evidence is reported as unverified, not as passing.

## Highest-priority holes

### 1. Several repositories have no executable safety net

The following repositories have neither a GitHub Actions workflow nor a
discoverable test suite in the checkout:

- `Cuelist-python`
- `QLab-python`
- `TheatreMix-python`
- `cesar`
- `ShowStopper`
- `aes`
- `wolf`

`Cuelist-python` is the most immediate integration risk: it declares runtime
dependencies on `showrunner`, FastAPI, Pydantic and multipart parsing, but has
no tests or CI. Its README also makes CRUD behaviour and a ShowRunner plugin
part of the public surface. The smallest useful next step is a smoke suite for
model validation, plugin discovery, and one request path, followed by CI.

`QLab-python`, `TheatreMix-python`, `ShowStopper`, `aes`, `wolf`, and `cesar`
may be intentionally experimental or dormant. Their current state is still
unknown because the workspace contains no automated signal establishing that
they build, start, or preserve their documented hardware/network behaviour.

### 2. Release and maintenance posture is inconsistent

`qmetronome` has CI and release workflows but no discoverable test files under
the workspace scan. Its documented Gradle command could not be executed here:
the checkout has no Java runtime (`JAVA_HOME` and `java` are absent). The open
work is therefore twofold: establish the intended unit-test location and make
the build reproducible on a documented Android/Java environment.

`holophonor`, `ludwig`, and `waveofhormuz` have release or deployment workflows
but no discoverable tests. `midiphonor` has CI/deployment workflows and four
test-like files, but its README does not describe how to run or validate them.
These projects need an explicit supported test command and a release smoke
check, even if the projects are not currently active.

`joe` has tests but no `.github/workflows` directory in this checkout. `leo`
has CI and deployment workflows and its local suite passed: 34 tests passed.
`leo` nevertheless has an untracked `irealforms.ipynb`; decide whether it is a
deliberate working artifact, a missing commit, or a file that belongs in
`.gitignore`.

### 3. The governance corpus still has a large declared open surface

The committed `loose-ends.json` is generated at 2026-09-20T17:17:01Z and
reports 127 open items: 18 blind spots, 36 document-proposed items, 55
document-unreviewed items, 2 over-slot items, and 16 stalled threads. The
document says these are declared gaps, not a queue to burn down.

The durable open work includes:

- ratifying records, applying the main ruleset, and cutting the first version
  tag, all blocked on a human decision or second code owner;
- applying governance artifacts to projects that have not adopted the seed;
- making the tag-determinism gate run as an actual pushed-tag workflow;
- deciding retention and recoverability for the archive;
- replacing file-based delta reconciliation with the HTTP path;
- making a second project emit deltas;
- finishing the unimplemented `rad` menu actions and its numpad conformance
  vectors;
- resolving the unpushed `alfred` work and the remote availability of
  `qmetronome`'s historical `v0.0.25` claim.

The source of truth for these items is [plans/open-work.md](open-work.md),
not this review. Refresh generated status documents before acting on counts.

## Active work and repository state

All checked-out branches except the corpus branch and `leo` tracked their
configured upstream at the same commit. The active branches are:

- `qm`: `evolve/performing-estate-refresh`, with no upstream configured. This
  is local-only until pushed or intentionally abandoned.
- `ShowRunner`: `integrate/2026-09-20`.
- `Cuelist-python`: `fix/install-and-packaging`.
- `ShowStopper`: `fix/textual-containers`.
- `carlos`: `fix/dials-cable-ends-and-scroll`.
- `qmetronome`: `governance/pin-project-tip`.
- `joe`: `docs/onboarding-hardening`.
- `leo`: `setlist`, plus untracked `irealforms.ipynb`.

These are active strands, not defects by themselves. Before starting more work,
the owner should decide which branches are ready for integration and which are
intentionally parked. The corpus branch without an upstream is the clearest
coordination risk because another session cannot fetch it.

## Validation performed

- `leo`: `uv run pytest` — 34 passed.
- `qm`: `uv run qm test` was attempted from the inherited shell context, but
  the `qm` executable was not available; an explicit project invocation then
  correctly refused because the command was not run from the corpus root. This
  is an environment/routing result, not a test failure.
- `carlos`: the analogous explicit invocation resolved the current working
  directory incorrectly and refused; no suite result is claimed.
- `qmetronome`: the Gradle command was run from the repository root and stopped
  before compilation because Java is not installed.
- `ShowRunner` and the remaining repositories were not claimed green by this
  review; they need their native commands run in their own environments.

## Recommended order

1. Resolve the corpus branch handoff and the untracked `leo` notebook.
2. Give `Cuelist-python` a minimal test/CI contract because it is an active
   integration dependency.
3. Run or document native checks for `ShowRunner`, `carlos`, `joe`, and
   `qmetronome` on machines with their required runtimes.
4. Classify the untested repositories as maintained, experimental, or archived;
   add a smoke check to maintained projects and state the status of the rest.
5. Refresh the corpus generated status and work registers, then work the human-
   blocked governance items separately from application maintenance.