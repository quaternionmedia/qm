"""One topology, three windows, three environments.

    uv run qm demo
    uv run qm demo --fixture --window dossier
    uv run qm demo --subject dossier --json

**REACHED THROUGH `qm`, LIKE EVERY OTHER OPERATION HERE.** `uv run qm --help` is
the whole surface, and a demo documented as `python ci/trio_demo.py` is a second
entry point nobody finds -- it was written that way first, and the correction is
the general one: a thing worth running that has no route needs the route added,
not its path written down somewhere. The script still runs directly under a
plain interpreter, because a fork has no `qm` to run.

**WHAT THIS SHOWS.** `qmcp` decides what a topology is and emits it as a
document. `dossier` draws that document as text in a terminal. `codecartographer`
draws the same document as a graph. The three then agree about what they drew --
same boxes, same arrows, same edges nobody measured -- and the agreement is
checked rather than eyeballed.

**WHY IT RUNS THREE SUBPROCESSES INSTEAD OF THREE IMPORTS.** The repositories do
not depend on each other and must not. A demo that imported all three would need
one environment holding all three, would pass in a way no user's machine
reproduces, and would quietly stop testing the thing it exists to test -- that a
document crosses the seam intact. Each side here runs under its own project, and
the only thing passing between them is JSON on a pipe.

**WHAT AGREEMENT MEANS, AND WHAT IT DOES NOT.** Agreement is: both windows found
the same boxes and arrows, and both classified the same edges as unmeasured. It
is *not* that they look alike -- they must not, they are a terminal and a graph.
And it is not that the topology is correct: `qmcp` could emit a wrong picture and
both windows would faithfully draw it. This checks the seam, not the truth on
either side of it.

**THE DATA IS REAL WHERE IT CAN BE.** With a thread archive on the machine, the
relations come from it and carry the weights `qmcp.threads.consolidate` measured.
Without one, the demo runs on a stated fixture and says so -- a demo that
silently fell back to invented data would be showing its own scaffolding, which
is the failure `records/DRAFT-decision-record-discipline.md` §9 is about.

`protocols/local-demo.md` is the protocol this follows. Its four rules: a file in
the repository, a test runs it, it prints what it established, and it says what
it could not.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent.parent
SIBLINGS = HERE.parent

# The demo is honest about a missing sibling rather than skipping in silence.
# A trio demo that ran with two sides present and printed a cheerful summary
# would be the exact shape this corpus keeps finding: a green result measuring
# less than the reader thinks.
NEEDED = ("qmcp", "dossier")
OPTIONAL = ("codecartographer",)


@dataclass
class Window:
    """What one window reported about the document it was given."""

    name: str
    ok: bool
    boxes: list[str] = field(default_factory=list)
    arrows: list[str] = field(default_factory=list)
    unmeasured: int = 0
    rendering: str = ""
    detail: str = ""


def sibling(name: str) -> Path | None:
    """A repository beside this clone, or None."""
    for base in (SIBLINGS, SIBLINGS.parent):
        found = base / name
        if (found / "pyproject.toml").is_file():
            return found
    return None


def _run(project: Path, script: str, *, subject: str = "",
         fixture: bool = False) -> tuple[bool, str]:
    """A script under one repository's own environment.

    Options reach the child through the environment rather than as arguments,
    because the child is a `-c` script rather than a file with a parser of its
    own. `TRIO_FIXTURE` is set only when `--fixture` was given, so the child
    can tell "the operator asked for the fixture" from "the archive did not
    answer" -- one is a choice and the other is a finding.
    """
    env = _env(project)
    if subject:
        env["TRIO_SUBJECT"] = subject
    if fixture:
        env["TRIO_FIXTURE"] = "1"
    done = subprocess.run(
        [interpreter(project), "-c", script],
        cwd=project, capture_output=True, text=True, timeout=300,
        env=env)
    if done.returncode != 0:
        return False, (done.stderr or done.stdout)[-1200:]
    return True, done.stdout


def interpreter(project: Path) -> str:
    """The python that has `project`'s dependencies installed.

    **NOT `sys.executable`.** The first version of this demo ran every window
    with the interpreter running the demo, which is the corpus's own repeated
    finding: the scaffolding became part of the measurement. `qmcp` failed to
    import `sqlmodel` and the demo reported that the harness could not emit a
    topology -- a true sentence about the wrong process. Each repository has its
    own environment because each has its own dependencies, and using one for all
    three tests nothing about the seam.
    """
    for relative in (Path(".venv") / "Scripts" / "python.exe",
                     Path(".venv") / "bin" / "python"):
        found = project / relative
        if found.is_file():
            return str(found)
    return sys.executable


def _env(project: Path) -> dict[str, str]:
    """`project`'s own environment, with its sources reachable.

    `uv run` would be the ordinary way in. It is not used here because the demo
    must not resolve or install anything -- a demo that changed the machine to
    make itself pass is not showing what the machine does.
    """
    import os

    found = dict(os.environ)
    roots = [str(project / "src"), str(project)]
    found["PYTHONPATH"] = os.pathsep.join(
        roots + ([found["PYTHONPATH"]] if found.get("PYTHONPATH") else []))
    # A parent's virtualenv leaks through this variable and would put the wrong
    # site-packages ahead of the one just chosen.
    found.pop("VIRTUAL_ENV", None)
    return found


# --- the three windows --------------------------------------------------------


EMIT = r'''
import json, os, sys
from pathlib import Path
from qmcp import topology_view as tv

SUBJECT = os.environ.get("TRIO_SUBJECT", "codecartographer")
FIXTURE = bool(os.environ.get("TRIO_FIXTURE"))


class _Chose(Exception):
    """The operator asked for the fixture. Not an error; a short way out."""


relations, source, surveyed = [], "fixture", 0
try:
    # **A CHOICE IS NOT A FAILURE.** `--fixture` skips the archive without
    # entering the handler below, so the stderr note stays reserved for an
    # archive that could not be read. Reporting the operator's own instruction
    # as "archive unavailable" would put a finding where a preference is.
    if FIXTURE:
        raise _Chose
    from qmcp.threads import consolidate
    from qmcp.threads.chatgpt import ChatGPTThreads
    from qmcp.threads.claude import ClaudeThreads

    root = Path(os.environ.get("QMCP_THREADS_ROOT",
                               Path.home() / ".qmcp" / "threads"))
    names = consolidate.roster(Path("governance") / "qm")
    project_of = dict(names)

    from qmcp.spend import FREE, Budget

    threads = []
    problems = []
    for source_class in (ClaudeThreads, ChatGPTThreads):
        try:
            # **A BUDGET OF `FREE`, MEANT LITERALLY.** These sources read files
            # already on the disk, so the authorised spend is zero and the
            # fetch really does cost nothing. `records/DRAFT-no-unattended-
            # spending.md`: a demo may not be the thing that quietly buys
            # something.
            reader = source_class(root=root)
            threads.extend(reader.fetch([], Budget(authorised=FREE)))
        except Exception as error:
            # Named. The first version of this said `continue`, both sources
            # failed on a method that does not exist, and the demo reported
            # "fixture" with nothing on stderr -- a silent fallback wearing the
            # word that was supposed to prevent one.
            problems.append(f"{source_class.__name__}: {type(error).__name__}: "
                            f"{error}")
    for problem in problems:
        print(f"# {problem}", file=sys.stderr)

    # **ONE SUBJECT, EVERY THREAD.** `about` reads one conversation at a time;
    # the relations for a project are what the whole archive says about it.
    for thread in threads:
        reading = consolidate.about(thread, names)
        for relation in consolidate.relations_for(thread, reading,
                                                  project_of=project_of):
            if SUBJECT in str(relation.get("source", "")) or \
               SUBJECT in str(relation.get("target", "")):
                relations.append(relation)
    surveyed = len(threads)
    if relations:
        source = "thread archive"
except _Chose:
    relations = []
except Exception as error:
    # Named rather than swallowed: falling back silently would make a demo of
    # the fixture look like a demo of the archive.
    print(f"# archive unavailable: {type(error).__name__}: {error}",
          file=sys.stderr)
    relations = []

if not relations:
    # STATED, NOT SILENT. The fixture carries one unmeasured relation on
    # purpose: a demo where every edge is measured would never exercise the
    # distinction both windows exist to preserve.
    relations = [
        {"target": "qm/dossier", "relation": "part-of", "weight": 0.91,
         "evidence": [{"basis": "mentions"}]},
        {"target": "qm/qmcp", "relation": "crosses", "weight": 0.34,
         "evidence": [{"basis": "mentions"}]},
        {"target": "qm/rad", "relation": "crosses", "weight": None,
         "evidence": [{}]},
    ]

view = tv.from_relations("codecartographer", relations,
                         caption="what one project is related to")
print(json.dumps({"payload": tv.as_payload(view),
                  "encoding": tv.encoding_payload(),
                  "source": source, "surveyed": surveyed}))
'''


# **THE COUNT IS READ OFF THE RENDERING, NOT OFF THE PAYLOAD.** The first
# version of this counted `weight is None` in the document it had just been
# handed -- so did the other window, and the two "agreed" because both had read
# the same field. Nothing about either renderer was being tested. What each
# window must report is what *it drew*, which for a terminal means counting the
# glyph that actually reached the screen.
DOSSIER = r'''
import json, sys
from dossier import topology

document = json.loads(sys.stdin.read())
payload = document["payload"]
drawn = topology.draw(payload, width=72)
unmeasured = sum(1 for line in drawn.lines if topology.UNMEASURED in line)
print(json.dumps({
    "boxes": [b["id"] for b in payload["boxes"]],
    "arrows": [f'{a["from"]}->{a["to"]}' for a in payload["arrows"]],
    "unmeasured": unmeasured,
    "rendering": drawn.text(),
    "channels_dropped": list(drawn.channels_dropped),
}))
'''


CODECARTO = r'''
import json, sys
from codecarto.services.topology_service import render

document = json.loads(sys.stdin.read())
view = render(document["payload"], document.get("encoding"))
lines = [f'{e.source} -> {e.target}  {e.style:<8} w={e.width:.2f}  {e.label}'
         for e in view.edges]
print(json.dumps({
    "boxes": [n["id"] for n in view.nodes],
    "arrows": [f"{e.source}->{e.target}" for e in view.edges],
    "unmeasured": view.unmeasured,
    "rendering": view.caveat() + "\n" + "\n".join(lines),
}))
'''


# Name -> the script that window runs. A registry rather than a literal pair
# inside `main`, so `--window` can be validated against it and `--list-windows`
# can answer without running anything.
WINDOWS: dict[str, str] = {"dossier": DOSSIER, "codecartographer": CODECARTO}


def _window(name: str, project: Path, script: str, document: str) -> Window:
    """One window, fed the document on stdin."""
    done = subprocess.run([interpreter(project), "-c", script], cwd=project,
                          input=document, capture_output=True, text=True,
                          timeout=300, env=_env(project))
    if done.returncode != 0:
        return Window(name, False, detail=(done.stderr or done.stdout)[-900:])
    try:
        found = json.loads(done.stdout.strip().splitlines()[-1])
    except Exception as error:                     # noqa: BLE001
        return Window(name, False, detail=f"unreadable answer: {error}")
    return Window(name, True, boxes=found["boxes"], arrows=found["arrows"],
                  unmeasured=found["unmeasured"],
                  rendering=found.get("rendering", ""))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="qm demo",
        description=("Run one topology from the harness through every window "
                     "and check that they agree."),
        epilog=("Exits 0 only when every window that drew the topology agrees "
                "about every box, every arrow, and which edges nobody "
                "measured. Exits 1 on disagreement, on a missing sibling, or "
                "when fewer than two windows drew anything -- one window "
                "agreeing with itself establishes nothing."),
    )
    parser.add_argument(
        "--subject", default="codecartographer", metavar="NAME",
        help="the project to survey the archive for (default: %(default)s)")
    parser.add_argument(
        "--fixture", action="store_true",
        help=("use the stated fixture and do not read the thread archive. The "
              "fixture carries one deliberately unmeasured relation, so the "
              "measured/unmeasured distinction is always exercised"))
    parser.add_argument(
        "--window", action="append", metavar="NAME", dest="windows",
        help=("draw in this window only; repeatable. Naming fewer than two "
              "still runs, and still refuses to call the result agreement"))
    parser.add_argument(
        "--list-windows", action="store_true",
        help="list the windows this corpus knows about, and exit")
    parser.add_argument(
        "--json", action="store_true", dest="as_json",
        help=("emit the result as one JSON document instead of prose. The "
              "exit status is the same either way"))
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    say = (lambda *a, **k: None) if args.as_json else print

    if args.list_windows:
        for name in WINDOWS:
            found = sibling(name)
            print(f"{name:<20} {found if found else 'not beside this clone'}")
        return 0

    chosen = list(WINDOWS)
    if args.windows:
        unknown = [n for n in args.windows if n not in WINDOWS]
        if unknown:
            parser.error(f"unknown window(s): {', '.join(unknown)}. "
                         f"Known: {', '.join(WINDOWS)}")
        chosen = [n for n in WINDOWS if n in args.windows]

    say("=" * 72)
    say("TRIO DEMO -- one topology, three windows, three environments")
    say("=" * 72)

    result: dict[str, Any] = {"subject": args.subject, "windows": {},
                              "agreed": False, "problems": []}

    missing = [n for n in NEEDED if sibling(n) is None]
    if missing:
        result["problems"].append(f"not beside this clone: {', '.join(missing)}")
        say(f"\nCannot run: {', '.join(missing)} is not beside this clone.")
        say("This demo needs the harness and at least one window. Nothing was "
            "established.")
        if args.as_json:
            print(json.dumps(result, indent=2))
        return 1

    harness = sibling("qmcp")
    say(f"\n[1] {harness.name} emits the topology")
    ok, out = _run(harness, EMIT, subject=args.subject, fixture=args.fixture)
    if not ok:
        result["problems"].append(f"the harness could not emit a topology: {out}")
        say(f"    the harness could not emit it:\n{out}")
        if args.as_json:
            print(json.dumps(result, indent=2))
        return 1

    document = out.strip().splitlines()[-1]
    emitted = json.loads(document)
    payload = emitted["payload"]
    unmeasured = sum(1 for a in payload["arrows"] if a.get("weight") is None)
    result["topology"] = payload["topology"]
    result["data"] = emitted["source"]
    result["surveyed"] = emitted.get("surveyed", 0)
    say(f"    topology     {payload['topology']} at level {payload['level']}")
    say(f"    data         {emitted['source']}")
    say(f"    boxes        {len(payload['boxes'])}")
    say(f"    arrows       {len(payload['arrows'])}, of which {unmeasured} "
        f"unmeasured")
    say(f"    encoding     {len(emitted['encoding'])} channel(s) declared")

    windows = []
    for name in chosen:
        project = sibling(name)
        if project is None:
            say(f"\n[-] {name} is not beside this clone -- not drawn, and not "
                f"counted as agreeing")
            result["windows"][name] = {"drew": False,
                                       "why": "not beside this clone"}
            continue
        say(f"\n[{len(windows) + 2}] {name} draws it")
        window = _window(name, project, WINDOWS[name], document)
        windows.append(window)
        if not window.ok:
            result["windows"][name] = {"drew": False, "why": window.detail}
            say(f"    could not draw it:\n{window.detail}")
            continue
        result["windows"][name] = {
            "drew": True, "boxes": len(window.boxes),
            "arrows": len(window.arrows), "unmeasured": window.unmeasured}
        say(f"    {window.unmeasured} edge(s) drawn as unmeasured")
        for line in window.rendering.splitlines()[:14]:
            say(f"    | {line}")

    say("\n" + "-" * 72)
    say("AGREEMENT")
    say("-" * 72)
    drew = [w for w in windows if w.ok]
    if len(drew) < 2:
        why = (f"only {len(drew)} window drew it -- agreement is not "
               f"established by one window agreeing with itself")
        result["problems"].append(why)
        say(f"  {why}")
        if args.as_json:
            print(json.dumps(result, indent=2))
        return 1

    problems = []
    first = drew[0]
    for other in drew[1:]:
        if sorted(first.boxes) != sorted(other.boxes):
            problems.append(f"{first.name} and {other.name} disagree about "
                            f"boxes: {set(first.boxes) ^ set(other.boxes)}")
        # **SORTED LISTS, NOT SETS.** Several relations can reach one address --
        # three readings of one delta is the ordinary case in a real archive --
        # and a set turns those three parallel arrows into one. A window that
        # dropped two of them would have compared equal.
        if sorted(first.arrows) != sorted(other.arrows):
            differing = set(first.arrows) ^ set(other.arrows)
            problems.append(
                f"{first.name} drew {len(first.arrows)} arrow(s) and "
                f"{other.name} drew {len(other.arrows)}; differing: "
                + (str(differing) if differing
                   else "same pairs, different counts"))
        if first.unmeasured != other.unmeasured:
            problems.append(
                f"{first.name} drew {first.unmeasured} edge(s) as unmeasured "
                f"and {other.name} drew {other.unmeasured}. **This is the one "
                f"that matters**: the windows disagree about what is known")

    for window in drew:
        say(f"  {window.name:<20} {len(window.boxes)} boxes, "
            f"{len(window.arrows)} arrows, {window.unmeasured} unmeasured")

    result["problems"].extend(problems)
    if problems:
        say("\n  DISAGREEMENT:")
        for problem in problems:
            say(f"    - {problem}")
        if args.as_json:
            print(json.dumps(result, indent=2))
        return 1

    result["agreed"] = True
    say(f"\n  {len(drew)} windows agree about every box, every arrow, and "
        f"which edges nobody measured.")

    say("\n" + "-" * 72)
    say("WHAT THIS DID NOT ESTABLISH")
    say("-" * 72)
    say("  - That the topology is right. Both windows would faithfully draw a "
        "wrong one.")
    say("  - That the two pictures look alike. They must not: one is a "
        "terminal and one is a graph.")
    if emitted["source"] != "thread archive":
        say("  - Anything about real data. The stated fixture was used, "
            + ("because --fixture was given." if args.fixture
               else "because no thread archive answered."))
    for name, found in result["windows"].items():
        if not found["drew"]:
            say(f"  - Anything about {name}: {found['why']}")

    if args.as_json:
        print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
