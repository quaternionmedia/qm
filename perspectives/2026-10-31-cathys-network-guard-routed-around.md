# cathy's network guard, routed around — 2026-10-31

| | |
|---|---|
| **Author** | Peter Kagstrom |
| **Date** | 2026-10-31 |
| **Standing** | Perspective — attributed, dated, non-binding |
| **Tools** | Claude Opus 5.5, driving the session under review |

On 2026-10-25 cathy's three open importer pull requests, quaternionmedia/cathy#2,
#3 and #4, were reviewed against the corpus ahead of the first demo on
quaternion.media's real export. Every gate was green on all three. The review
then tried to route around `tests/test_network_boundary.py`, as cathy's
`AGENTS.md` asks of any guard. The guard #2 carried at `d559602` accepted 22
changes that open a connection, start a process, or send a request that is not
a GET. This page is what was assumed, what it cost, and for each finding the
check that would have caught it and whether that check exists.

## A guard that lists its mutations was taken as tried

The guard's docstring listed eight mutations it had been seen to fail on, and
the network record's §6 asks for that list. The false assumption is that such a
list means the guard was routed around. Every mutation on it was in the family
the guard was written for: an import of a network module, or an argument to the
`Request`. None reached the same end another way.

The first pass found these outside `cathy/net.py`:

- `xml.sax.parse(url, handler)`. The standard library's SAX entry point fetches
  a URL it is given, and a server on the loopback interface recorded the GET.
  `minidom`, `pulldom` and `ElementTree` open a local path only.
- `os.startfile`, `os.execvp` and `os.spawnlp`, the same class as the
  `subprocess` and `os.system` the guard already refused.
- `exec("import socket")`, the same bound to another name, and
  `eval("__imp" + "ort__")("socket")`.
- `sys.modules["urllib.request"].build_opener()`.

Inside `cathy/net.py`, a body given to `opener.open` and a method assigned to
the request after it was built both passed the source check. Neither got
further: `tests/test_fetch.py` went red on each at run time, with 2 and 7
failures. The suite held where its static half did not.

**Check now:** the changes the guard refuses are two lists in the module,
`ROUTES` and `NOT_A_GET`, each run against it as a parametrized test. On
2026-10-31, run through `d559602`'s own test functions, with each request change placed inside
that commit's `net.py`, its guard passes 22 of the 31. A first count put each
request change in a file of its own and read five of them as refused. They were
not refused: the old test fails on any file with no `Request` in it. The
harness was measuring itself.

## The first fix had holes of its own

The hardened guard was probed again and seven more got through: a launcher
imported under another name (`from os import startfile as go`),
`getattr(os, "startfile")`, `vars(os)["system"]`, `pkgutil.resolve_name`,
`runpy`, `code` and `pickle`. The false assumption is that closing the cases
found closes the class. The fix that held refuses a name wherever it appears,
any string constant among them, so a name held in a string is read as the
attribute it names. A name built at runtime is still out of reach, and the
docstring says so.

**Check now:** the seven are entries in `ROUTES`.

## The independent pass did not happen

The rule asks for a pass whose brief is to satisfy the check while doing what
it forbids, which is a different person's job from the author's. A subagent was
briefed with the guard and the package, and not with the findings. A safety
classifier stopped it after it had read the code and before it ran a
candidate. It reported that, edited nothing, and was not briefed again. The
seven later bypasses came from the guard's own author, which is the case the
rule exists to avoid.

**Check now:** none. The pass is carried as unfinished in the handoff for
cathy's stack.

## Claims written before they were run

Two pull request bodies carried claims no command had returned.

- **#3's** said neither quaternion.media's export nor harpo.me's held an
  `http://` image. quaternion.media's export had not been read; a stand-in
  built from its public feeds had. The error began in this session: the brief
  it wrote for #3's session said the review "ran it against quaternion.media
  and harpo.me's real export", which reads as two exports, and #3's body
  repeated it. The body was corrected in the review.
- **#2's**, updated for the hardened guard, said the local workflow run passed
  with 94 tests and that one commit carried a good signature. Both lines were
  edited before either command was run at the new head. Both were run before
  the session moved on: 12 steps passed with 94 tests, and two commits carried
  good signatures, so the signature line was corrected. The false assumption is
  that a verification line with a new number in it has been re-run.

**Check now:** none. `check_pr_voice.py` reads a body's voice, never whether
its verification lines match a run at the head.

## A check probed with the wrong phrase

To show the timeless check could fail on the review's worktrees, the first
probe planted "previously … was fixed after it failed", and the check reported
nothing. The check was fine. "Previously" is on the record lint's list for
drafts, and not among `check_timeless.py`'s narrative patterns, which the probe
assumed it shared. A second probe with phrases from its own list gave three
findings. The leak check caught its probe the first time.

**Check now:** the probe is the check. Read the check's own pattern list
before writing what should trip it.

## Two sibling pull requests that conflict

#3 and #4 are both stacked on #2, and both edit `tests/test_convert.py`. An
in-memory merge showed two conflicting hunks there, with `cathy/config.py` and
`cathy/convert.py` merging cleanly. Git 2.37 has only the three-argument
`merge-tree`, since `--write-tree` arrived in 2.38. They stay siblings, as the
asynchronous contract's §1 has independent changes do. Whichever lands second
is brought level with its base and resolved there.
