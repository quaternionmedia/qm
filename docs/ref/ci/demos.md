# The trio demo and the surfaces

`uv run qm demo` runs one topology through every window that draws one and
checks that they agree. It follows `protocols/local-demo.md`: the demo is a
file in the repository, a test runs it, it prints what it established, and it
says what it could not.

```sh
uv run qm demo                               # subprocess mode, archive or fixture
uv run qm demo --over-http --side-by-side    # the deployed processes, in columns
uv run qm demo --fixture --window dossier    # one window: refused as agreement
uv run qm demo --subject dossier --json      # one verdict, machine-readable
```

The source is `ci/trio_demo.py` and its tests are `ci/tests/test_trio_demo.py`.

## What it shows

`qmcp` decides what a topology is and emits it as a document. `dossier` draws
that document as text in a terminal and `codecartographer` draws it as a graph.
The demo then checks that the windows agree about what they drew: the same
boxes, the same arrows, and the same edges classified as unmeasured.

Agreement is not likeness: a terminal and a graph must look different.
Agreement is not correctness either: if `qmcp` emitted a wrong picture, both
windows would draw it faithfully. The demo checks the [seam](../../ref/glossary.md#seam){ .glossary-term }, not the truth on
either side of it.

## Two modes, two claims

| Mode | How each window runs | What a pass shows |
|---|---|---|
| Subprocess (default) | Under its own project's interpreter, with JSON on a pipe | The renderers agree about a document |
| `--over-http` | The running [harness](../../ref/glossary.md#harness){ .glossary-term } serves the topology; the running web front end says what it drew | The same, of the deployed processes |

The repositories do not depend on each other, so the subprocess mode never
imports all three into one environment: each window runs under the interpreter
that has its own project's dependencies, never the demo's own, and the demo
resolves and installs nothing (it does not use `uv run`). A contract can be
sound and unreachable; only the HTTP mode tests reachability, and it asks the
server's `/topology/data` route rather than importing the renderer. When a
process is not answering, the demo names it and the command that starts it.

Both modes share one comparison. A single window drawing alone is one window
agreeing with itself, and the demo exits 1 and says so.

## The figures

Each edge is printed as its measurement in percent, the unit both windows use.
An unmeasured edge prints `unmeasured`, never `0%`: a measured zero is a
finding, and an absent measurement is a different one.

`--side-by-side` puts the windows in equal columns aligned by row, so the same
edge sits on the same line in both. A line longer than its column overflows
into the gutter rather than being cut, so the layout never edits what a window
drew.

## The three acts

1. **The topology**, drawn by the windows and held to agreement about the
   picture.
2. **One thread, three readers.** One thread from the harness goes to `qmcp`,
   `looksatwords` and `dossier`, each under its own interpreter. The readers
   draw nothing, so they agree about the seam instead: every reader reports
   the same thread length and the same count of turns that carry prose, the
   two figures a truncation would change separately. `looksatwords` emits no
   decision and no delta, which is the border its adoption [record](../../ref/glossary.md#record){ .glossary-term } draws. The
   stated fixture carries an empty turn so the two counts can differ.
3. **The estate.** Each core member reads `families.json` at its pinned path
   in its own runtime and reports family names, member counts and a sorted
   list of every placement. Agreement is judged on the placements.

Each act runs only after the one before it agrees, so a disagreement about the
topology is never buried under a later act, and all three share the exit status
and the one `agreed` field of `--json`. `--skip-readers` and `--skip-estate`
leave an act out and say so in the output.

## Data and siblings

With a thread archive on the machine, the relations come from it and carry the
weights `qmcp.threads.consolidate` measured. Without one, or with `--fixture`,
the demo runs on a stated fixture and prints which.

The other repositories are looked for beside this clone and one level up.
`QM_SIBLINGS`, a path-separated list of directories, replaces that search when
set, which is how a git worktree names where its siblings are. It replaces
rather than extends, so the repositories a demo may read have one source. A
window or a reader must be a Python project; a derive target need only be a
git repository. A missing sibling is reported, never skipped in silence.

## What it cannot establish

- That the topology, the topics or the placements are right: every act checks
  agreement across a seam.
- Anything about the services in subprocess mode: every window there ran under
  a local interpreter.
- Its own mutation score through `uv run qm mutate`: the mutator runs the suite
  against a copy in a temporary directory, from which no sibling resolves, so
  the baseline is red. The mutations named in the tests are applied by hand.

## The surfaces

`uv run qm dashboard` reports which of the estate's surfaces are up and how to
bring up the rest. The source is `ci/dashboard.py`.

```sh
uv run qm dashboard                  # what is listening, and what to run
uv run qm dashboard --start harness  # detach the harness into its own process
uv run qm dashboard --start web
uv run qm dashboard --stop harness   # stop what --start launched, by its pid
uv run qm dashboard --start-registered  # every surface this machine registered, not yet up
```

`qmcp` holds the work and answers over HTTP. `codecartographer` is its front end
on the web and `dossier` its front end in a terminal. Neither front end owns
anything: both read the same harness, and a figure that differs between them is
a defect rather than a point of view, which is why there are two. `looksatwords`
reads the conversations the harness archived and reports their topics; it is
listed because it is one more server on the same workstation, and a port
collision between any two surfaces is what the table prevents. `apothecary`'s
viewer is listed for the same reason, started as its demo, which touches no
real board.

- **Reporting is the default.** Nothing starts unless `--start` names it.
- **Servers detach; the terminal front end does not.** `--start` backs a server
  off into its own process under its repository's own environment and records
  its pid. `dossier dashboard` draws in the terminal it is run from, so the
  dashboard prints that command rather than launching it into a pipe.
- **Started means the port answered.** `--start` waits, up to `--wait`
  seconds (60 by default), for the server's port. A server that exits first is
  reported as not running, with the end of its log, and its record and
  run-file are dropped. One still silent at the deadline is reported, and kept
  so `--stop` can end it.
- **`--stop` acts on the recorded pid, never the port**, so it never stops a
  process it did not start. It also refuses a pid that has since been handed
  to another process: it records each process's start time and compares it.
  After the stop it withdraws every run-file naming the freed port whose
  process is gone. That includes qmcp's own, which a process ended outright
  cannot withdraw.
- **`--start-registered` starts what this machine is registered to run**
  (`uv run qm instances register`), the harness first, skipping a surface whose
  port already answers.
- **A busy port is "something is listening"**, not "the harness is up": any
  process may hold a port, and the ordinary cause of a surprise is a stale
  process from an earlier session.
- **The ports are defaults, each overridable**, chosen as a memory aid: pi
  (3141) for the harness, e (2718) for the web front end, phi for the terminal
  one, root two for the prose reader, and tau for apothecary's viewer. Each is
  its constant's first four digits, and no two surfaces share one.

## Which server is which

`uv run qm instances` reports every server this machine declares, and whether
each is the server its declaration names. The source is `ci/instances.py`; the
procedure, for a person and for several sessions at once, is
[handbook/running-several-repositories.md](https://github.com/quaternionmedia/qm/blob/main/handbook/running-several-repositories.md).

```sh
uv run qm instances                       # every declared server, and its state
uv run qm instances --port 8000           # also look at a port nothing declares
uv run qm instances run --repo dossier --session mine -- uv run dossier serve --port {port}
uv run qm instances prune                 # run-files whose process is gone; --yes removes them
uv run qm instances register --family core            # this machine runs the core family
uv run qm instances register --repo qmcp --repo apothecary --name bench
uv run qm instances register              # what is registered; --clear registers nothing
```

- **A server is found by its run-file, never by its port.** qmcp writes its
  own; `qm dashboard --start` writes one for every other surface it starts;
  `qm instances run` writes one for any command and withdraws it when the
  server exits.
- **Only the declared health path is requested.** A read of qmcp's queue can
  write to it, so nothing else is in reach.
- **A server that states no pid is `answering`, never `identified`.** Only
  qmcp says which process it is today.
- **A registration says what this machine should be running.** It is a family,
  whose members `families.json` resolves when it is read, or a selection named
  repository by repository, or both. It is kept in `~/.qm/registered.json` and
  never committed. Each registered repository then reads as `up`, `silent`,
  `missing` (nothing declares it, and this corpus starts a server for it) or
  `unjudged` (nothing in this corpus starts one, as for `qm` itself).
  `--check` fails on `missing`.
