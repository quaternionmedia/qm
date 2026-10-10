# The trio demo

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
