# Handoff - simultaneous performing-family efficacy plan

**Goal.** Run the requested repositories together in controlled waves and measure efficacy, interference, and unintended simultaneity effects. This is an experiment plan, not a claim that all ten repositories are runnable services.

**Stamp.** 2026-09-21. The workspace includes `midiphonor`, `holophonor`, `wolf`, `ludwig`, `joe`, `leo`, `carlos`, `ShowRunner`, and `ShowStopper`. `loopwall` exists as a private remote but has no local clone yet; it is being added to the `instruments` family and roster as unresolved.

Read [handoffs/README.md](README.md) first, then the ten participant pages named below. The experiment must be repeated against exact commits, not just repository names.

## Scope and interpretation

The requested set contains different kinds of systems:

- **Hubs/services:** ShowRunner, Holophonor, Wolf, possibly Loopwall.
- **Browser or UI clients:** Midiphonor, Joe, Leo, Carlos, ShowStopper.
- **A command-line or hardware-facing endpoint:** Ludwig.

Therefore “run together” has two meanings that must not be collapsed:

1. **Process simultaneity:** processes overlap in time and resource usage.
2. **Protocol simultaneity:** messages, cues, timer events, or rendered state overlap through real integration seams.

A full process list with no shared protocol is a resource experiment, not an end-to-end efficacy result.

## Preconditions

Before Wave 0, record:

- exact commit, branch, dirty/untracked state, and dependency lock for every participant;
- operating system, Python/Node/runtime versions, audio/MIDI devices, and available ports;
- whether each participant has a deterministic health/start probe;
- whether Docker, browser binaries, and hardware access are available;
- a scratch directory and per-repository logs/databases.

`loopwall` remains **unknown** until its private clone is present and independently verified. Do not substitute an empty folder or remote metadata for runtime evidence.

## Waves

### Wave 0: readiness and isolated baselines

Run each repository alone using its documented command. Record startup result, health result, protocol endpoint, shutdown result, and a fixed functional probe. Expected baseline classifications are `pass`, `fail`, or `unknown`; never coerce unknown into fail.

Known baseline risks:

- Midiphonor's package test command is a deliberate failing placeholder.
- Wolf has no tests/CI and its latest local commit is from 2021.
- Ludwig has no tests/CI and is hardware-facing.
- ShowStopper has no tests/CI and its protocol is not yet established.
- Loopwall has no local checkout.

### Wave 1: hub plus one client

Run ShowRunner with one supported client or stub at a time: Leo, Joe, Carlos, Midiphonor, then Holophonor where the seam is real. Use reserved ports and scratch state. This identifies pairwise failures before full concurrency.

### Wave 2: instrument/control cluster

Run Holophonor, Wolf, Ludwig, and any verified Loopwall instance together, with a fixed message/cue script and no live destructive hardware. Add Midiphonor only after its browser target is known. Measure message ordering, delivery, loop/timer drift, reconnects, CPU, memory, and device errors.

### Wave 3: full requested set

Run ShowRunner, ShowStopper, Carlos, Joe, Leo, Holophonor, Midiphonor, Wolf, Ludwig, and Loopwall only if Wave 0 marked it runnable. Use the same fixture and script as the baselines. Do at least three repetitions, including one staggered start and one simultaneous start, so startup races are distinguishable from steady-state contention.

## Measurements

Capture machine-readable timestamps for:

- process start, ready, first useful response, first delivered event, and shutdown;
- request/cue send and receipt, with correlation IDs where possible;
- timer/loop drift against a monotonic reference;
- dropped/reordered messages, reconnects, HTTP/WebSocket errors, browser console errors;
- CPU, memory, open handles/listeners, disk I/O, and audio underruns at fixed intervals;
- output/state hashes for Joe, Leo, Carlos, and any generated cue/loop artifact.

Keep raw logs per process and a normalized event ledger. The ledger must retain missing observations as `unknown`, not zero.

## Controls

Use these controls to isolate unintended simultaneity:

- same fixture, same input, same machine, same exact commits;
- isolated run versus pairwise run versus full run;
- staggered starts versus simultaneous starts;
- reserved ports and per-repo databases/output directories;
- fake or dry-run hardware targets before real devices;
- a no-op client/control run to measure background resource cost;
- process cleanup and port-free verification after every repetition.

Do not run destructive cleanup, hardware writes, or database purges against a user's real data. Carlos and any other stateful service must use scratch databases.

## Efficacy measures

Report separately:

- **Readiness:** did the participant start and expose its claimed interface?
- **Functional success:** did the fixed probe produce the expected state/output?
- **Integration success:** did the expected cross-repository event arrive and converge?
- **Concurrency degradation:** change from isolated baseline in latency, loss, drift, errors, or output mismatch.
- **Resource interference:** change in CPU, memory, I/O, handles, or port collisions.
- **Unmeasured:** prerequisites absent, access denied, or no deterministic probe.

A useful first comparison is a vector, not a single score:

`(readiness, functional_success, integration_success, p95_latency, loss_rate, drift, resource_delta, unknowns)`

Only aggregate participants with the same observable contract. Do not average a browser page load with a hardware mixer acknowledgement.

## Simultaneity hazards to watch

- Two services bind the same default port.
- A stale prior process answers health checks for the new process.
- Shared SQLite/database/output paths cause cross-run contamination.
- Browser clients point at different backend instances.
- Audio/MIDI devices allow only one owner.
- A service silently drops or reorders messages under load.
- A full run fails because one dormant repository never had an isolated baseline.
- Startup order creates a race that steady-state operation does not reproduce.
- A passing process check hides a missing protocol seam.

## Stop and interpretation rules

Stop a wave if it writes outside scratch locations, targets real hardware unexpectedly, binds an unreserved port, or produces an unbounded process/resource condition. Stop the experiment, not the repository, when a participant lacks a safe deterministic probe.

Classify each finding as:

- **isolated failure:** baseline fails alone;
- **pairwise interaction:** baseline passes, one pair fails;
- **full-run interaction:** lower waves pass, full wave fails;
- **startup race:** simultaneous start fails but staggered start passes;
- **resource contention:** functional behavior degrades with measured resource saturation;
- **unknown:** access, hardware, or observability prevented attribution.

A full-run failure without a passing baseline is not evidence of unintended simultaneity.

## Outputs

Produce:

1. one run manifest with commits, commands, ports, devices, and environment;
2. raw per-process logs and normalized event ledger;
3. baseline/pairwise/full-wave result table;
4. resource and timing plots or CSV summaries;
5. an interaction matrix showing which combinations were actually observed;
6. a short findings page naming failures, unknowns, and missing seams;
7. follow-up handoffs only for defects established by a reproducible run.

The participant handoffs are:

- [midiphonor-simultaneous-run.md](midiphonor-simultaneous-run.md)
- [holophonor-simultaneous-run.md](holophonor-simultaneous-run.md)
- [wolf-simultaneous-run.md](wolf-simultaneous-run.md)
- [ludwig-simultaneous-run.md](ludwig-simultaneous-run.md)
- [joe-simultaneous-run.md](joe-simultaneous-run.md)
- [leo-simultaneous-run.md](leo-simultaneous-run.md)
- [carlos-simultaneous-run.md](carlos-simultaneous-run.md)
- [loopwall-simultaneous-run.md](loopwall-simultaneous-run.md)
- [showrunner-simultaneous-run.md](showrunner-simultaneous-run.md)
- [showstopper-simultaneous-run.md](showstopper-simultaneous-run.md)

## What this does not authorise

Cloning private Loopwall without access, cutting or merging repository branches, changing dependency locks, running destructive cleanup, or connecting untested software to live show hardware. Those are separate decisions.
