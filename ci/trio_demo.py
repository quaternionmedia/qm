"""One topology, three windows, three environments.

    uv run qm demo
    uv run qm demo --over-http --side-by-side
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

**TWO MODES, AND THE DIFFERENCE IS WHAT IS BEING CLAIMED.**

*Subprocess* (the default) runs each window's code under its own project's
interpreter and passes JSON on a pipe. The repositories do not depend on each
other and must not; a demo that imported all three would need one environment
holding all three and would pass in a way no machine reproduces. This proves the
two renderers agree about a document.

*`--over-http`* asks the running harness for the topology and the running web
front end what it drew. This proves the same thing **as deployed** -- and the
distinction is not academic: for a while the harness served no topology route at
all and the web front end had a renderer nothing routed to, so the subprocess
demo passed green while nothing at either port could produce a picture. A
contract can be sound and unreachable, and only one of these modes can tell.

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
import shutil
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


def _sibling_roots() -> list[Path]:
    """Where the other repositories are looked for.

    Beside this clone and one level up, by convention. `QM_SIBLINGS`
    (os.pathsep-separated directories) **replaces** that when set, because a
    git worktree is beside nothing -- its parents are wherever the worktree was
    made -- and a session working from one found every sibling "not beside this
    clone" while all four sat in the usual place. Replaces rather than extends:
    two sources of truth for which repositories a demo may read is how an
    allowlist stops being one, and the same call was made in codecartographer's
    `/system` router the same week.
    """
    import os

    override = os.environ.get("QM_SIBLINGS", "")
    if override.strip():
        return [Path(part) for part in override.split(os.pathsep) if part.strip()]
    return [SIBLINGS, SIBLINGS.parent]


def sibling(name: str) -> Path | None:
    """A Python project beside this clone, or None.

    `pyproject.toml` is the test because a sibling here is something whose
    interpreter the demo will run a script under. A repository with no Python
    in it is not a window and not a reader -- see `clone` for what it can be.
    """
    for base in _sibling_roots():
        found = base / name
        if (found / "pyproject.toml").is_file():
            return found
    return None


def clone(name: str) -> Path | None:
    """Any git repository beside this clone, or None.

    The derived system monitor reads a repository's *contents*, and the
    repository it is best aimed at -- moat, a homelab of charts and terraform
    -- has no `pyproject.toml`. Resolving the derive target with `sibling`
    reported it "not beside this clone" while it sat in the usual place, which
    was this demo describing its own resolver rather than the machine.
    """
    for base in _sibling_roots():
        found = base / name
        if (found / ".git").exists():
            return found
    return None


def _run(project: Path, script: str, *, subject: str = "",
         fixture: bool = False, width: int = 0) -> tuple[bool, str]:
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
    if width:
        env["TRIO_WIDTH"] = str(width)
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


# --- the same windows, as deployed ---------------------------------------------
#
# **THE DIFFERENCE BETWEEN THIS AND THE SUBPROCESS MODE IS THE WHOLE POINT.**
# Running each window's code in a subprocess proves the two renderers agree
# about a document. It says nothing about whether either is *reachable* -- and
# for a while neither was: the harness served no topology at all and the web
# front end had a renderer with no route, so a demo could pass while nothing at
# either port could produce a picture. Over HTTP, every answer comes from a
# process somebody could have opened in a browser.

HARNESS_URL = "http://127.0.0.1:3141"
WEB_URL = "http://127.0.0.1:2718"


def _get(url: str, timeout: float = 15.0):
    """One JSON document, or a reason."""
    import urllib.error
    import urllib.request

    try:
        with urllib.request.urlopen(url, timeout=timeout) as answer:
            return json.loads(answer.read()), ""
    except urllib.error.HTTPError as error:
        detail = ""
        try:
            detail = str(json.loads(error.read()).get("detail", ""))
        except Exception:                          # noqa: BLE001
            pass
        return None, f"{error.code} from {url}" + (f": {detail}" if detail else "")
    except Exception as error:                     # noqa: BLE001
        return None, f"{type(error).__name__} reaching {url}: {error}"


def _harness_document(subject: str) -> tuple[dict | None, str]:
    """The topology, from the running harness."""
    found, why = _get(f"{HARNESS_URL}/v1/topology/relations/{subject}")
    if found is not None:
        return found, ""
    # A subject with no reading is not a dead harness. Fall back to a shape,
    # which every harness serves, rather than reporting the harness down.
    shape, shape_why = _get(f"{HARNESS_URL}/v1/topology/shape/delegation")
    if shape is not None:
        return shape, f"no reading for {subject} ({why}); drew a shape instead"
    return None, why


def _figure(weight: float | None) -> str:
    """One edge's measurement, in the units every window prints it in.

    **THE TWO COLUMNS WERE SHOWING DIFFERENT KINDS OF NUMBER FOR ONE EDGE.**
    The terminal window prints the measurement (`17%`); this side printed only
    `w=1.42`, which is a line thickness derived from that measurement by
    `MIN_WIDTH + (MAX_WIDTH - MIN_WIDTH) * weight`. Both were correct and
    neither was comparable, so a reader set the demo's whole premise -- a figure
    that differs between the windows is a defect -- against two figures that
    could not be compared at all.

    An unmeasured edge has no figure and must not borrow one: it says so,
    rather than rounding `None` into a percentage that looks measured.
    """
    if weight is None:
        return "unmeasured"
    return f"{round(weight * 100)}%"


def _web_window(document: dict, subject: str, kind: str) -> Window:
    """What the deployed web front end says it drew.

    **ASKS THE SERVER, NOT THE LIBRARY.** `/topology/data` returns the widths
    and styles that front end resolved. Importing its renderer here would test
    the same code the subprocess mode already tests and would leave the route
    -- the part that was missing -- unexercised.
    """
    query = f"subject={subject}" if subject else f"kind={kind}"
    envelope, why = _get(f"{WEB_URL}/topology/data?{query}")
    if envelope is None:
        return Window("codecartographer", False, detail=why)

    # **THE PROJECT'S ENVELOPE, NOT A SHAPE INVENTED FOR THIS DEMO.** That
    # front end answers `{status, message, results}` like every other route it
    # serves. This demo read the inner document directly until the route was
    # moved onto the house style, and then reported "could not draw it: None"
    # -- which was this side failing to read, not that side failing to draw.
    status = int(envelope.get("status") or 200)
    found = envelope.get("results") or envelope
    if status >= 400:
        return Window("codecartographer", False,
                      detail=f"{found.get('problem') or envelope.get('message')}"
                             f" -- {found.get('remedy') or ''}")
    if "edges" not in found:
        return Window("codecartographer", False,
                      detail=f"the front end answered without a rendering: "
                             f"{sorted(found)[:6]}")
    lines = [f"{e['source']} -> {e['target']}  {e['style']:<8} "
             f"{_figure(e.get('weight')):<11} w={e['width']:.2f}  {e['label']}"
             for e in found["edges"]]
    return Window(
        "codecartographer", True,
        boxes=[n["id"] for n in found["nodes"]],
        arrows=[f"{e['source']}->{e['target']}" for e in found["edges"]],
        unmeasured=found["unmeasured"],
        rendering=found["caveat"] + "\n" + "\n".join(lines))


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
import json, os, sys
from dossier import topology

document = json.loads(sys.stdin.read())
payload = document["payload"]
drawn = topology.draw(payload, width=int(os.environ.get("TRIO_WIDTH") or 72))
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
def figure(edge):
    """The measurement, in the units the other window prints it in."""
    if edge.weight is None:
        return "unmeasured"
    return str(round(edge.weight * 100)) + "%"

lines = [f'{e.source} -> {e.target}  {e.style:<8} {figure(e):<11} '
         f'w={e.width:.2f}  {e.label}'
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


# --- the second act: one thread, three readers ---------------------------------
#
# **A FOURTH WINDOW WOULD HAVE BEEN A LIE.** looksatwords does not draw a
# topology, and its own adoption record (`project/looksatwords`, §3) says what it
# does instead: qmcp names the handful of decisions a thread settled; dossier
# carries those through a lifecycle; looksatwords reads the *turns* underneath
# -- the ninety-seven that were not decisions -- and says what they were about.
# Asking it to agree about boxes and arrows would test nothing it does.
#
# So the second act takes ONE THREAD from the harness and hands it to three
# readers, each under its own interpreter with JSON on a pipe, exactly as the
# first act does with a topology:
#
#   qmcp           what the thread settled, and which shapes it could run now
#                  given what this demo supplies (`orchestration.runnable_now`)
#   looksatwords   which topics the turns carried, which tangents never resolved
#   dossier        which of its views could answer with this subject selected
#                  (`readiness.survey`) -- the same "what do I need" model, from
#                  the panel's side
#
# **WHAT AGREEMENT MEANS HERE.** The readers do not draw one thing, so they
# cannot agree about a picture. What they can agree about is the seam: every
# reader must report the same thread length and the same count of turns that
# carry prose, because those are the two figures looksatwords' seam code says
# are different facts and are the ones a truncation would silently change. And
# looksatwords must emit no decision and no delta -- it reads turns and owns
# nothing in the other two, which is the border its record draws.

# One thread from the archive when there is one, else this. Stated, not
# silent, and carrying one empty turn and one tool-shaped turn on purpose so
# the prose-versus-turns distinction is exercised every time.
THREAD_FIXTURE = {
    "source": "fixture", "id": "fixture-one-thread", "partial": False,
    "title": "How the panel reads the thread archive",
    "turns": [
        {"id": "t0", "role": "user", "at": None,
         "text": "We need to decide how the panel reads the thread archive."},
        {"id": "t1", "role": "assistant", "at": None,
         "text": "The obvious move is to import the harness package directly."},
        {"id": "t2", "role": "assistant", "at": None, "text": ""},
        {"id": "t3", "role": "user", "at": None,
         "text": "That couples them. If the storage layout changes, the panel "
                 "breaks, and the archive never asked to be involved."},
        {"id": "t4", "role": "assistant", "at": None,
         "text": "Then it crosses as HTTP on loopback and a schema. The port is "
                 "a setting; the host is not."},
        {"id": "t5", "role": "user", "at": None,
         "text": "Quick tangent: should the panel cache what it reads?"},
        {"id": "t6", "role": "assistant", "at": None,
         "text": "Anyway, back to the seam. A precondition names what "
                 "satisfies it, so a view that cannot answer says why."},
        {"id": "t7", "role": "user", "at": None,
         "text": "Agreed. The harness stays the one author of a thread row."},
    ],
}


THREAD = r'''
import json, os, sys
from pathlib import Path

SUBJECT = os.environ.get("TRIO_SUBJECT", "codecartographer")
FIXTURE = bool(os.environ.get("TRIO_FIXTURE"))
STATED = json.loads(os.environ["TRIO_THREAD_FIXTURE"])

from qmcp.orchestration import PLANE, runnable_now, unmet, by_type
from qmcp.agentframework.models.enums import TopologyType


class _Chose(Exception):
    """The operator asked for the fixture."""


thread, source, settled = None, "fixture", []
try:
    if FIXTURE:
        raise _Chose
    from qmcp.spend import FREE, Budget
    from qmcp.threads import consolidate
    from qmcp.threads.chatgpt import ChatGPTThreads
    from qmcp.threads.claude import ClaudeThreads

    root = Path(os.environ.get("QMCP_THREADS_ROOT",
                               Path.home() / ".qmcp" / "threads"))
    names = consolidate.roster(Path("governance") / "qm")
    for source_class in (ClaudeThreads, ChatGPTThreads):
        try:
            reader = source_class(root=root)
            for candidate in reader.fetch([], Budget(authorised=FREE)):
                prose = [t for t in candidate.turns if (t.text or "").strip()]
                if len(prose) < 8:
                    continue
                reading = consolidate.about(candidate, names)
                if SUBJECT not in " ".join(reading.projects
                                           if hasattr(reading, "projects")
                                           else []):
                    continue
                # **THE OTHER SIDE'S ANSWER, NOT RECOMPUTED.** What the thread
                # settled is qmcp's to say; the reader's own extractor says it
                # with a budget of FREE, because these files are on the disk.
                found = reader.deltas(candidate, Budget(authorised=FREE))
                # The first payload is the thread itself -- `deltas` always
                # emits it, so an inconclusive conversation stays visible.
                # What it *settled* is the rest.
                settled = [d.get("delta", {}).get("title") or d.get("name")
                           for d in (found or [])[1:] if isinstance(d, dict)]
                thread = {
                    "source": getattr(reader, "perspective", source_class.__name__),
                    "id": candidate.id, "title": candidate.title,
                    "partial": candidate.partial,
                    "turns": [{"id": t.id, "role": t.role, "at": t.at,
                               "text": t.text} for t in candidate.turns],
                }
                source = "thread archive"
                break
        except Exception as error:
            print(f"# {source_class.__name__}: {type(error).__name__}: {error}",
                  file=sys.stderr)
        if thread is not None:
            break
except _Chose:
    pass
except Exception as error:
    print(f"# archive unavailable: {type(error).__name__}: {error}",
          file=sys.stderr)

if thread is None:
    thread = STATED
    settled = ["How the panel reads the thread archive"]
    source = "fixture"

prose = sum(1 for t in thread["turns"] if (t.get("text") or "").strip())

# **WHAT THIS DEMO SUPPLIES, STATED.** It has the harness built and nothing
# else: no budget somebody authorised, no worker pool, no model, and no person
# at the keyboard. `runnable_now` says which shapes that is enough for, and
# `unmet` says what the rest are short of -- the topology declares its needs,
# per the walkthrough that landed with qmcp #34.
have = {"built": True}
runnable = [t.value for t in runnable_now(**have)]
short = {}
for capability in PLANE:
    missing = [n.key for n in unmet(capability, **have)]
    if missing:
        short[capability.topology.value] = missing

print(json.dumps({
    "thread": thread, "source": source, "settled": settled,
    "turns_total": len(thread["turns"]), "turns_with_text": prose,
    "runnable_now": runnable, "short": short,
}))
'''


LOOKSATWORDS = r'''
import json, sys
from looksatwords import harness
from looksatwords.frontend.visualizer_backend import ThreadVisualizerBackend

document = json.loads(sys.stdin.read())
raw = document["thread"]
thread = harness.Thread(source=raw["source"], id=raw["id"],
                        title=raw.get("title") or "", turns=tuple(raw["turns"]),
                        partial=bool(raw.get("partial")))
# THE SEAM'S OWN CONVERSION, so the counts reported below are the ones the
# project reports to its own users, not a second reading done for the demo.
text, report = harness.as_conversation(thread)

backend = ThreadVisualizerBackend()
backend.parseConversation(text)
backend.identifyThreads()
backend.detectTangents()
summary = backend.getAnalysisSummary()

print(json.dumps({
    "turns_total": report["turns_total"],
    "turns_with_text": report["turns_with_text"],
    "turns_used": report["turns_used"],
    "truncated": report["truncated"],
    "speakers": sorted(backend.speakers),
    "topics": [{"name": t["name"], "points": len(t["points"])}
               for t in backend.threads],
    "tangents": {"total": summary["tangent_count"],
                 "unresolved": summary["unresolved_tangents"]},
    "dynamic_topics": summary["dynamic_topics_enabled"],
}))
'''


DOSSIER_READINESS = r'''
import json, os, sys
from dossier import readiness, views

document = json.loads(sys.stdin.read())
subject = os.environ.get("TRIO_SUBJECT", "codecartographer")

# The reading a person gets with this subject selected. The harness address is
# a dead port on purpose: the demo makes no claim about a running harness in
# this act, and a view that needs one must say so rather than read as ready.
found = readiness.survey(selection=object(), clone_of=subject,
                         harness_base="http://127.0.0.1:9",
                         corpus=os.path.join("governance", "qm"))
ready = [r.view.tab for r in found if r.ready]
waiting = {}
for r in found:
    if r.ready:
        continue
    first = r.blocking[0].need
    waiting.setdefault(first.key, []).append(r.view.title)

print(json.dumps({
    "views": len(found), "ready": len(ready), "waiting": waiting,
    "declared": sum(1 for v in views.VIEWS if v.needs),
    "thread_turns_seen": len(document["thread"]["turns"]),
}))
'''


# The derived system monitor, if this checkout of codecartographer carries it.
# **PRESENCE IS CHECKED ON DISK, NEVER ASSUMED**: it landed on a local branch,
# and the sibling's checked-out tree may be older. When the module is absent
# the demo says so and moves on; a reader that imported it anyway would be the
# demo importing its own scaffolding.
CODECARTO_DERIVED = r'''
import json, os, sys
from pathlib import Path
from codecarto.services import system_composer

document = json.loads(sys.stdin.read())
target = Path(os.environ["TRIO_DERIVE_FROM"])
composed = system_composer.compose(target)
roles = {}
for c in composed["components"]:
    roles[c["role"]] = roles.get(c["role"], 0) + 1
print(json.dumps({
    "system": composed["system"], "commit": composed["commit"],
    "components": len(composed["components"]), "roles": roles,
    "edges": len(composed["edges"]),
    "thread_turns_seen": len(document["thread"]["turns"]),
}))
'''


# Name -> the script that reader runs. Kept apart from WINDOWS on purpose:
# a window draws a topology and is held to agreement about a picture; a reader
# reads a thread and is held to the seam's counts.
READERS: dict[str, str] = {
    "looksatwords": LOOKSATWORDS,
    "dossier": DOSSIER_READINESS,
    "codecartographer": CODECARTO_DERIVED,
}


# The gap between columns. Wide enough that two renderings do not read as one
# wrapped paragraph, narrow enough not to cost a column its content.
GUTTER = 4

# Below this, splitting produces two columns too narrow for either window's own
# layout, and the comparison is worse than the sequence it replaced.
MIN_COLUMN = 34


def columns(windows: list["Window"], total: int) -> list[str]:
    """Every window's drawing, side by side, as lines.

    **PADDED, NEVER TRUNCATED.** A line longer than its column overflows into
    the gutter and is left alone. Cutting it would make this side the author of
    what the other side drew, and a comparison whose own layout edits the
    evidence cannot be used to find a disagreement.

    Columns are equal width and rows are aligned by index, so the same edge sits
    on the same line in both -- which is what makes a difference visible rather
    than merely present.
    """
    if not windows:
        return []
    each = (total - GUTTER * (len(windows) - 1)) // len(windows)
    blocks = [w.rendering.splitlines() for w in windows]
    heads = [w.name for w in windows]
    rules = ["-" * min(each, len(w.name) + 8) for w in windows]

    rows: list[str] = []
    for line in (heads, rules):
        rows.append((" " * GUTTER).join(c.ljust(each) for c in line).rstrip())
    for index in range(max(len(b) for b in blocks)):
        cells = [(b[index] if index < len(b) else "") for b in blocks]
        rows.append((" " * GUTTER).join(c.ljust(each) for c in cells).rstrip())
    return rows


def _window(name: str, project: Path, script: str, document: str,
            width: int = 0) -> Window:
    """One window, fed the document on stdin.

    `width` is a request, not an instruction. A window draws at whatever width
    it can and this side does not check -- a column that silently truncated a
    window's own layout would be this side editing the other's rendering, which
    is the one thing a comparison must not do.
    """
    env = _env(project)
    if width:
        env["TRIO_WIDTH"] = str(width)
    done = subprocess.run([interpreter(project), "-c", script], cwd=project,
                          input=document, capture_output=True, text=True,
                          timeout=300, env=env)
    if done.returncode != 0:
        return Window(name, False, detail=(done.stderr or done.stdout)[-900:])
    try:
        found = json.loads(done.stdout.strip().splitlines()[-1])
    except Exception as error:                     # noqa: BLE001
        return Window(name, False, detail=f"unreadable answer: {error}")
    return Window(name, True, boxes=found["boxes"], arrows=found["arrows"],
                  unmeasured=found["unmeasured"],
                  rendering=found.get("rendering", ""))


def _over_http(args, say, result: dict, chosen: list[str], terminal: int,
               column_width: int) -> int:
    """The demo against the deployed trio.

    Every failure here names the process that is not answering and the command
    that starts it, because "the demo failed" is useless when the cause is a
    server nobody started.
    """
    say("\n[1] the running harness serves the topology")
    document, note = _harness_document(args.subject)
    if document is None:
        say(f"    {note}")
        say(f"    start it with `uv run qm dashboard --start harness`")
        result["problems"].append(note)
        if args.as_json:
            print(json.dumps(result, indent=2))
        return 1
    if note:
        say(f"    note: {note}")

    payload = document["payload"]
    unmeasured = sum(1 for a in payload["arrows"] if a.get("weight") is None)
    result["topology"] = payload["topology"]
    result["data"] = document.get("source", "")
    result["surveyed"] = document.get("surveyed", 0)
    say(f"    topology     {payload['topology']} at level {payload['level']}")
    say(f"    data         {document.get('source', '')}")
    say(f"    boxes        {len(payload['boxes'])}")
    say(f"    arrows       {len(payload['arrows'])}, of which {unmeasured} "
        f"unmeasured")
    say(f"    served by    {HARNESS_URL}")

    windows = []
    if "dossier" in chosen:
        say("\n[2] dossier draws it")
        project = sibling("dossier")
        if project is None:
            say("    dossier is not beside this clone")
        else:
            window = _window("dossier", project, DOSSIER,
                             json.dumps({"payload": payload}),
                             width=column_width if args.columns else 0)
            windows.append(window)
            _say_window(say, args, window)

    if "codecartographer" in chosen:
        say(f"\n[3] codecartographer draws it, at {WEB_URL}")
        window = _web_window(document, args.subject, "delegation")
        windows.append(window)
        _say_window(say, args, window)
        if not window.ok:
            say(f"    start it with `uv run qm dashboard --start web`")

    for window in windows:
        result["windows"][window.name] = (
            {"drew": True, "boxes": len(window.boxes),
             "arrows": len(window.arrows), "unmeasured": window.unmeasured}
            if window.ok else {"drew": False, "why": window.detail})

    return _agree(args, say, result, [w for w in windows if w.ok], terminal)


def _say_window(say, args, window: "Window") -> None:
    if not window.ok:
        say(f"    could not draw it: {window.detail}")
        return
    say(f"    {window.unmeasured} edge(s) drawn as unmeasured")
    if not args.columns:
        for line in window.rendering.splitlines()[:14]:
            say(f"    | {line}")


def _agree(args, say, result: dict, drew: list["Window"], terminal: int) -> int:
    """The comparison, shared by both modes so neither can drift lenient."""
    say("\n" + "-" * 72)
    say("AGREEMENT")
    say("-" * 72)

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

    if args.columns:
        say("")
        for line in columns(drew, terminal):
            say(line)
        say("")

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
    return 0


def _readers(args, say, result: dict) -> int:
    """The second act: one thread from the harness, read three ways.

    Returns 0 when every reader that ran agrees with the harness about the
    seam's two counts and looksatwords authored nothing; 1 otherwise. A reader
    whose repository is not beside this clone, or whose checkout lacks the
    module, is reported and not counted -- the same rule the windows follow.
    """
    import os

    say("\n" + "=" * 72)
    say("SECOND ACT -- one thread, three readers")
    say("=" * 72)

    harness = sibling("qmcp")
    say(f"\n[1] {harness.name} serves one thread, and says what it settled")
    env_extra = {"TRIO_THREAD_FIXTURE": json.dumps(THREAD_FIXTURE)}
    saved = {k: os.environ.get(k) for k in env_extra}
    os.environ.update(env_extra)
    try:
        ok, out = _run(harness, THREAD, subject=args.subject,
                       fixture=args.fixture)
    finally:
        for key, value in saved.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
    if not ok:
        result["problems"].append(f"the harness could not serve a thread: {out}")
        say(f"    the harness could not serve one:\n{out}")
        return 1

    document = out.strip().splitlines()[-1]
    served = json.loads(document)
    thread = served["thread"]
    readers: dict[str, Any] = {
        "source": served["source"],
        "turns_total": served["turns_total"],
        "turns_with_text": served["turns_with_text"],
        "settled": served["settled"],
        "runnable_now": served["runnable_now"],
        "read": {},
    }
    result["readers"] = readers
    say(f"    thread       {thread['source']}/{thread['id']}")
    say(f"    title        {thread.get('title') or '(untitled)'}")
    say(f"    data         {served['source']}")
    say(f"    turns        {served['turns_total']}, of which "
        f"{served['turns_with_text']} carry prose")
    say(f"    settled      {len(served['settled'])} delta(s): "
        + (", ".join(served["settled"][:3]) or "none"))
    say(f"    runnable now {', '.join(served['runnable_now']) or 'nothing'} "
        f"-- given only a built harness")
    for shape, missing in list(served["short"].items())[:8]:
        say(f"                 {shape:<12} short of {', '.join(missing)}")

    problems: list[str] = []
    step = 2

    # looksatwords: the turns.
    project = sibling("looksatwords")
    say(f"\n[{step}] looksatwords reads the turns")
    if project is None:
        say("    looksatwords is not beside this clone -- not read")
        readers["read"]["looksatwords"] = {"read": False,
                                           "why": "not beside this clone"}
    else:
        window = _reader("looksatwords", project, LOOKSATWORDS, document)
        if not window.ok:
            readers["read"]["looksatwords"] = {"read": False, "why": window.detail}
            say(f"    could not read it:\n{window.detail}")
        else:
            found = window.found
            readers["read"]["looksatwords"] = {"read": True, **found}
            say(f"    speakers     {', '.join(found['speakers'])}")
            say(f"    topics       "
                + (", ".join(f"{t['name']} ({t['points']})"
                             for t in found["topics"][:8]) or "none found"))
            say(f"    tangents     {found['tangents']['total']}, "
                f"{found['tangents']['unresolved']} unresolved")
            say(f"    turns        {found['turns_total']} total, "
                f"{found['turns_with_text']} with prose, "
                f"{found['turns_used']} used"
                + (" -- TRUNCATED" if found["truncated"] else ""))
            problems.extend(_seam_problems(served, found))
    step += 1

    # dossier: what could answer with this subject selected.
    project = sibling("dossier")
    say(f"\n[{step}] dossier says which views could answer, with "
        f"{args.subject} selected")
    if project is None:
        say("    dossier is not beside this clone -- not read")
        readers["read"]["dossier"] = {"read": False, "why": "not beside this clone"}
    else:
        window = _reader("dossier", project, DOSSIER_READINESS, document,
                         subject=args.subject)
        if not window.ok:
            readers["read"]["dossier"] = {"read": False, "why": window.detail}
            say(f"    could not read it:\n{window.detail}")
        else:
            found = window.found
            readers["read"]["dossier"] = {"read": True, **found}
            say(f"    ready        {found['ready']} of {found['views']} views "
                f"({found['declared']} declare a need)")
            for key, titles in found["waiting"].items():
                say(f"    waiting on   {key}: {', '.join(titles)}")
            if found["thread_turns_seen"] != served["turns_total"]:
                problems.append("dossier was handed a different thread than "
                                "the harness served")
    step += 1

    # codecartographer: the derived system monitor, if this checkout has it.
    project = sibling("codecartographer")
    say(f"\n[{step}] codecartographer derives {args.subject}'s system from its "
        f"clone")
    target = clone(args.subject)
    if project is None:
        say("    codecartographer is not beside this clone -- not read")
        readers["read"]["codecartographer"] = {"read": False,
                                               "why": "not beside this clone"}
    elif not (project / "codecarto" / "services" / "system_composer.py").is_file():
        why = ("this checkout of codecartographer does not carry the derived "
               "system monitor (feat/the-monitor-derives-the-system)")
        say(f"    {why} -- not read")
        readers["read"]["codecartographer"] = {"read": False, "why": why}
    elif target is None:
        say(f"    {args.subject} is not beside this clone, so there is nothing "
            f"to derive from -- not read")
        readers["read"]["codecartographer"] = {
            "read": False, "why": f"{args.subject} not beside this clone"}
    else:
        os.environ["TRIO_DERIVE_FROM"] = str(target)
        try:
            window = _reader("codecartographer", project, CODECARTO_DERIVED,
                             document)
        finally:
            os.environ.pop("TRIO_DERIVE_FROM", None)
        if not window.ok:
            readers["read"]["codecartographer"] = {"read": False,
                                                   "why": window.detail}
            say(f"    could not derive it:\n{window.detail}")
        else:
            found = window.found
            readers["read"]["codecartographer"] = {"read": True, **found}
            say(f"    derived      {found['components']} component(s), "
                f"{found['edges']} edge(s), from {found['system']} at "
                f"{found['commit']}")
            say(f"    roles        " + ", ".join(
                f"{n} {role}" for role, n in sorted(found["roles"].items())))

    say("\n" + "-" * 72)
    say("THE SEAM")
    say("-" * 72)
    read = [n for n, r in readers["read"].items() if r.get("read")]
    say(f"  {len(read)} reader(s) read the thread the harness served: "
        + (", ".join(read) or "none"))
    result["problems"].extend(problems)
    if problems:
        say("\n  DISAGREEMENT:")
        for problem in problems:
            say(f"    - {problem}")
        return 1
    if "looksatwords" in read:
        say("  looksatwords reported the harness's own turn counts and emitted "
            "no decision:")
        say("  qmcp says what the thread settled; looksatwords says what the "
            "other turns were about.")
    return 0


def _seam_problems(served: dict, found: dict) -> list[str]:
    """What looksatwords is held to: the seam's two counts, and the border.

    **A FUNCTION, SO IT CAN BE FED A WRONG ANSWER.** The first version of this
    check lived inline and its test asserted that the border's *message*
    appeared in the source -- a mutation that emptied the check and kept the
    string passed it. This takes the harness's document and the reader's and
    returns the disagreements, so a test hands it an over-count and an
    authored decision and watches both come back named.
    """
    problems: list[str] = []
    # THE SEAM'S TWO COUNTS, BOTH SIDES. They are different facts -- how long
    # the thread is, and how much of it is prose -- and a truncation would
    # move exactly one of them.
    if found["turns_total"] != served["turns_total"]:
        problems.append(
            f"looksatwords read {found['turns_total']} turns and the "
            f"harness served {served['turns_total']}")
    if found["turns_with_text"] != served["turns_with_text"]:
        problems.append(
            f"looksatwords found prose in {found['turns_with_text']} turns "
            f"and the harness counted {served['turns_with_text']} -- the "
            f"seam's second count disagrees")
    # THE BORDER: it reads turns and owns nothing in the other two.
    authored = [k for k in found if k in ("deltas", "decisions", "settled",
                                          "delta")]
    if authored:
        problems.append(
            f"looksatwords emitted {authored}; its record says it never "
            f"authors a decision or a delta")
    return problems


@dataclass
class Reading:
    """What one reader reported, as the JSON it printed."""

    name: str
    ok: bool
    found: dict = field(default_factory=dict)
    detail: str = ""


def _reader(name: str, project: Path, script: str, document: str,
            subject: str = "") -> Reading:
    """One reader, fed the thread on stdin. Same pipe, same rule as `_window`:
    this side never edits what the other side reported."""
    import os

    env = _env(project)
    if subject:
        env["TRIO_SUBJECT"] = subject
    done = subprocess.run([interpreter(project), "-c", script], cwd=project,
                          input=document, capture_output=True, text=True,
                          timeout=300, env=env)
    if done.returncode != 0:
        return Reading(name, False, detail=(done.stderr or done.stdout)[-900:])
    try:
        return Reading(name, True,
                       found=json.loads(done.stdout.strip().splitlines()[-1]))
    except Exception as error:                     # noqa: BLE001
        return Reading(name, False, detail=f"unreadable answer: {error}")


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
        "--over-http", action="store_true", dest="over_http",
        help=("compare the front ends as deployed: fetch the topology from the "
              "running harness and ask the running web front end what it drew. "
              "Without this the windows are run as subprocesses, which tests "
              "the contract and not the seam anybody actually uses"))
    parser.add_argument(
        "--side-by-side", action="store_true", dest="columns",
        help=("put every window's drawing in its own column, so one topology "
              "is read as one view. Falls back to one below the other when the "
              "terminal is too narrow to split, rather than wrapping into "
              "gibberish"))
    parser.add_argument(
        "--json", action="store_true", dest="as_json",
        help=("emit the result as one JSON document instead of prose. The "
              "exit status is the same either way"))
    parser.add_argument(
        "--skip-readers", action="store_true", dest="skip_readers",
        help=("stop after the topology act. The second act hands one thread "
              "to looksatwords, dossier and codecartographer as readers; it "
              "is part of the demo and skipping it is stated in the output"))
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    say = (lambda *a, **k: None) if args.as_json else print

    if args.list_windows:
        for name in WINDOWS:
            found = sibling(name)
            print(f"{name:<20} {found if found else 'not beside this clone'}")
        print("readers:")
        for name in READERS:
            found = sibling(name)
            print(f"  {name:<18} {found if found else 'not beside this clone'}")
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

    # **THE WIDTH IS DECIDED ONCE, BEFORE EITHER MODE.** One view means one
    # measure: columns of different widths would lose the row alignment that
    # carries the whole comparison. It sits here rather than beside the drawing
    # because both modes need it, and the first version computed it after the
    # call that uses it -- which only broke with `--side-by-side`, so every
    # other run looked fine.
    terminal = shutil.get_terminal_size((100, 24)).columns
    column_width = max(MIN_COLUMN,
                       (terminal - GUTTER * (len(chosen) - 1)) // max(1, len(chosen)))
    if args.columns and terminal < MIN_COLUMN * len(chosen) + GUTTER * (len(chosen) - 1):
        say(f"\n[!] this terminal is {terminal} columns; "
            f"{MIN_COLUMN * len(chosen) + GUTTER * (len(chosen) - 1)} are needed "
            f"to put {len(chosen)} windows side by side. Drawing them one below "
            f"the other instead.")
        args.columns = False

    # Over HTTP the windows are the deployed processes rather than subprocesses
    # of this one, which is a different claim and the one anybody cares about.
    if args.over_http:
        return _over_http(args, say, result, chosen, terminal, column_width)

    harness = sibling("qmcp")
    say(f"\n[1] {harness.name} emits the topology")
    ok, out = _run(harness, EMIT, subject=args.subject, fixture=args.fixture,
                   width=column_width if args.columns else 0)
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
        window = _window(name, project, WINDOWS[name], document,
                             width=column_width if args.columns else 0)
        windows.append(window)
        if not window.ok:
            result["windows"][name] = {"drew": False, "why": window.detail}
            say(f"    could not draw it:\n{window.detail}")
            continue
        result["windows"][name] = {
            "drew": True, "boxes": len(window.boxes),
            "arrows": len(window.arrows), "unmeasured": window.unmeasured}
        say(f"    {window.unmeasured} edge(s) drawn as unmeasured")
        if not args.columns:
            for line in window.rendering.splitlines()[:14]:
                say(f"    | {line}")

    # **ONE COMPARISON, SHARED WITH THE HTTP MODE.** Two copies drift, and the
    # one that drifts lenient is the one nobody notices. This had two until a
    # test counted them.
    verdict = _agree(args, say, result, [w for w in windows if w.ok], terminal)
    if verdict != 0:
        return verdict

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

    # **THE SECOND ACT RUNS AFTER THE FIRST HAS AGREED**, so a disagreement
    # about the topology is never buried under a page of thread analysis. It
    # shares the exit status: a reader that disagrees with the harness about
    # the seam's counts is as much a defect as a window that drew a different
    # picture.
    if args.skip_readers:
        say("\n  - The second act was skipped (--skip-readers): nothing about "
            "looksatwords, readiness or the derived monitor.")
    else:
        verdict = _readers(args, say, result)
        if verdict != 0:
            # **THE VERDICT IS ONE FIELD.** The first act had already set
            # `agreed` true, and a failing second act left it standing -- a
            # mutation that made looksatwords over-count by one produced a
            # JSON document with the disagreement in `problems` and `agreed:
            # true` above it. Two answers to one question in one document.
            result["agreed"] = False
            if args.as_json:
                print(json.dumps(result, indent=2))
            return verdict
        say("\n" + "-" * 72)
        say("WHAT THE SECOND ACT DID NOT ESTABLISH")
        say("-" * 72)
        say("  - That the topics are right. looksatwords reports what its "
            "extractor found; nothing here judges it.")
        say("  - Anything about the running services. Every reader ran under "
            "its own interpreter on a pipe; dossier's readiness was measured "
            "against a harness address nobody answers on, so the views that "
            "need one read as waiting, on purpose.")
        for name, found in result.get("readers", {}).get("read", {}).items():
            if not found.get("read"):
                say(f"  - Anything about {name}: {found['why']}")

    if args.as_json:
        print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
