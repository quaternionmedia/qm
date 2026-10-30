#!/usr/bin/env python3
"""Bring the estate's surfaces up from nothing, and say what is already up.

    uv run qm dashboard
    uv run qm dashboard --start harness
    uv run qm dashboard --start web
    uv run qm dashboard --stop harness

`qmcp` holds the work and answers over HTTP. `codecartographer` is its front end
on the web and `dossier` its front end in a terminal; neither owns anything,
and a figure that differs between them is a defect. `looksatwords` reads the
conversations the harness archived and reports their topics. `apothecary`
serves its parts and the bench that makes them, in the browser.

Reporting is the default: nothing starts unless `--start` names it. `--start`
detaches a server into its own process and records its pid; the terminal front
end draws where it is run, so for it this prints the command instead.

The ports are defaults, each overridable: pi for the harness, e for the web
front end, phi for the terminal one, root two for the prose reader, and tau
for apothecary's viewer. Each is its constant's first four digits.
`docs/ref/ci/demos.md` describes the surfaces.
"""

from __future__ import annotations

import argparse
import json
import os
import socket
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import instances  # noqa: E402

HERE = Path(__file__).resolve().parent.parent
SIBLINGS = HERE.parent

# Where a detached server's details go, so `--stop` acts on what `--start`
# actually launched rather than on whatever happens to hold the port. Killing by
# port would let this command stop a process it never started.
STATE = Path(os.environ.get("QM_DASHBOARD_STATE")
             or Path.home() / ".qm" / "dashboard.json")


@dataclass(frozen=True)
class Surface:
    """One process among the surfaces, and how to bring it up."""

    name: str
    repo: str
    role: str
    port: int
    constant: str
    command: tuple[str, ...]
    detachable: bool
    """Whether starting it in the background produces something usable. False
    for a terminal front end, which draws where it was run and nowhere else."""

    dataview: str = ""
    """Where this surface shows what it is for, relative to its own root: the
    topology, for the harness and its front ends. **The point of running it.**
    A status table that said a server was up and left a reader to guess the
    path has reported a process rather than a place to look."""

    also: dict[str, str] = field(default_factory=dict)
    """Other places worth knowing, path -> what it is. The application is the
    answer to "show me"; these are the answers to "let me read the data" and
    "what does this server offer", which are different questions and should not
    be guessed at either."""

    note: str = ""

    declares_itself: bool = False
    """Whether the server writes its own run-file (`ci/instances.py`). One that
    does is not declared again here, so `qm instances` reads one declaration of
    it rather than two."""


SURFACES: tuple[Surface, ...] = (
    Surface(
        name="harness", repo="qmcp", role="the work, and the only source of it",
        port=3141, constant="pi",
        command=("qmcp", "serve", "--port", "3141"), detachable=True,
        declares_itself=True,
        dataview="/v1/topology",
        also={"/v1/topology/relations/codecartographer":
              "what the archive says about one project",
              "/docs": "every route this harness serves"},
        note="both front ends read this. Start it first, or they have "
             "nothing to draw"),
    Surface(
        name="web", repo="codecartographer",
        role="front end on the web", port=2718, constant="e",
        command=("codecarto", "serve", "--port", "2718"), detachable=True,
        dataview="/app",
        also={"/topology/gjgf": "the same graph, as data",
              "/topology/available": "whether the harness answered, without "
                                     "drawing anything"},
        note="draws the harness's topology as a graph"),
    Surface(
        name="terminal", repo="dossier",
        role="front end in a terminal", port=1618, constant="phi",
        command=("dossier", "dashboard"), detachable=False,
        note="run this in the terminal you want to watch. `dossier serve "
             "--port 1618` is its API, which is a different thing"),
    Surface(
        name="prose", repo="looksatwords",
        role="reads the archive's conversations", port=1414, constant="root two",
        command=("looksatwords", "serve", "--port", "1414"), detachable=True,
        dataview="/",
        also={"/api/harness/threads": "the harness's archive, as this window "
                                      "lists it",
              "/docs": "every route this reader serves"},
        note="reads the harness's thread archive on loopback, so it has "
             "nothing to list until the harness is up"),
    Surface(
        name="parts", repo="apothecary",
        role="parts and the bench that makes them", port=6283, constant="tau",
        command=("apothecary", "serve", "--demo", "--port", "6283"),
        detachable=True,
        dataview="/viewer",
        also={"/docs": "its guides, and the walkthrough at /walkthrough",
              "/openapi.json": "every route this server serves"},
        note="the demo touches no real board; `apothecary serve` without "
             "--demo drives the boards plugged into this machine"),
)

BY_NAME = {s.name: s for s in SURFACES}


def repo_of(surface: Surface) -> Path | None:
    """The repository beside this clone, or None."""
    for base in (SIBLINGS, SIBLINGS.parent):
        found = base / surface.repo
        if (found / "pyproject.toml").is_file():
            return found
    return None


def listening(port: int, host: str = "127.0.0.1") -> bool:
    """Whether anything holds the port.

    This is not "is the right thing running": any process may hold a port, and
    this cannot tell the harness from something else on 3141, so it reports
    "something is listening". The ordinary cause of a surprise is a stale
    process from an earlier session.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.settimeout(0.4)
        return probe.connect_ex((host, port)) == 0


def running() -> dict[str, dict]:
    """What this command started earlier, as it recorded it."""
    if not STATE.is_file():
        return {}
    try:
        return json.loads(STATE.read_text(encoding="utf-8"))
    except Exception:                              # noqa: BLE001
        return {}


def _remember(found: dict[str, dict]) -> None:
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(found, indent=2), encoding="utf-8")


def start(surface: Surface, repo: Path) -> tuple[bool, str]:
    """Back one server off into its own process.

    The command runs under the repository's own environment via `uv run`,
    because each has its own dependencies and this corpus's interpreter has
    none of them.
    """
    if not surface.detachable:
        return False, (f"{surface.name} draws in the terminal it is run from. "
                       f"Run `{' '.join(surface.command)}` there yourself")
    if listening(surface.port):
        return False, (f"something is already listening on {surface.port}. "
                       f"Stop it, or it is already what you wanted")

    log = STATE.parent / f"{surface.name}.log"
    log.parent.mkdir(parents=True, exist_ok=True)
    handle = log.open("a", encoding="utf-8")
    child = subprocess.Popen(
        ["uv", "run", "--no-sync", *surface.command],
        cwd=repo, stdout=handle, stderr=subprocess.STDOUT,
        stdin=subprocess.DEVNULL,
        # Detached, so closing this terminal does not take the server with it.
        creationflags=getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0),
    )
    found = running()
    found[surface.name] = {"pid": child.pid, "port": surface.port,
                           "repo": str(repo), "log": str(log)}
    _remember(found)
    if not surface.declares_itself:
        # So `qm instances` finds it by its declaration, not by its port.
        instances.declare(surface.repo, child.pid, surface.port,
                          ["uv", "run", "--no-sync", *surface.command],
                          session="dashboard", checkout=repo)
    return True, f"started as pid {child.pid}; output goes to {log}"


def stop(name: str) -> tuple[bool, str]:
    """Stop what this command started, by the pid it recorded.

    By recorded pid, never by port, so this never stops a process it did not
    start.
    """
    found = running()
    if name not in found:
        return False, f"this command did not start {name}, so it will not stop it"
    pid = found[name]["pid"]
    try:
        if sys.platform == "win32":
            subprocess.run(["taskkill", "/F", "/T", "/PID", str(pid)],
                           capture_output=True, check=False)
        else:
            os.kill(pid, 15)
    except Exception as error:                     # noqa: BLE001
        return False, f"could not stop pid {pid}: {error}"
    found.pop(name)
    _remember(found)
    instances.withdraw(BY_NAME[name].repo if name in BY_NAME else name, pid)
    return True, f"stopped pid {pid}"


def report() -> int:
    """The status table, and what to run for anything not up."""
    started = running()
    print("THE SURFACES")
    print("=" * 74)
    print(f"{'':<10} {'repository':<20} {'port':<7} {'state'}")
    print("-" * 74)

    missing = []
    for surface in SURFACES:
        repo = repo_of(surface)
        if repo is None:
            state = "not beside this clone"
            missing.append(surface)
        elif listening(surface.port):
            state = "something is listening"
            if surface.name in started:
                state += f" (started here, pid {started[surface.name]['pid']})"
        else:
            state = "nothing listening"
            missing.append(surface)
        print(f"{surface.name:<10} {surface.repo:<20} "
              f"{surface.port:<7} {state}")

    print()
    print("Each front end reads the harness. A figure that differs between them")
    print("is a defect, not a point of view -- which is why there are two.")

    live = [s for s in SURFACES
            if s.dataview and repo_of(s) is not None and listening(s.port)]
    if live:
        print()
        print("WHERE TO LOOK, IN EACH ONE THAT IS UP")
        print("-" * 74)
        for surface in live:
            print(f"  {surface.name:<10} http://127.0.0.1:{surface.port}"
                  f"{surface.dataview}")
            for extra, what in surface.also.items():
                print(f"  {'':<10} http://127.0.0.1:{surface.port}{extra}"
                      f"  ({what})")
        print()
        print("  both at once, in this terminal:")
        print("    uv run qm demo --over-http --side-by-side")

    if missing:
        print()
        print("TO BRING UP WHAT IS NOT RUNNING")
        print("-" * 74)
        for surface in missing:
            repo = repo_of(surface)
            if repo is None:
                print(f"  {surface.name:<10} {surface.repo} is not beside this "
                      f"clone. Nothing here can start it")
                continue
            if surface.detachable:
                print(f"  {surface.name:<10} uv run qm dashboard --start "
                      f"{surface.name}")
                print(f"  {'':<10} or, in its own terminal: "
                      f"cd {surface.repo} && uv run {' '.join(surface.command)}")
            else:
                print(f"  {surface.name:<10} cd {surface.repo} && uv run "
                      f"{' '.join(surface.command)}")
                print(f"  {'':<10} ({surface.note})")

    print()
    print("Both front ends drawing one topology, in one terminal:")
    print("  uv run qm demo --side-by-side")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="qm dashboard",
        description=("Say what of the surfaces is up, and start what is not. "
                     "qmcp holds the work; codecartographer is its front end "
                     "on the web and dossier its front end in a terminal."),
        epilog=("With no options this changes nothing -- it reports, and "
                "prints the command for anything that is not running."),
    )
    parser.add_argument(
        "--start", metavar="NAME", action="append", dest="to_start",
        choices=[s.name for s in SURFACES],
        help=("bring this surface up in its own process; repeatable. A "
              "terminal front end is refused, because a detached terminal "
              "draws where nobody is looking"))
    parser.add_argument(
        "--stop", metavar="NAME", action="append", dest="to_stop",
        choices=[s.name for s in SURFACES],
        help="stop a surface this command started, by the pid it recorded")
    parser.add_argument(
        "--json", action="store_true", dest="as_json",
        help="the status table as one JSON document")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.as_json:
        started = running()
        print(json.dumps({
            s.name: {"repository": s.repo, "role": s.role, "port": s.port,
                     "constant": s.constant, "detachable": s.detachable,
                     "present": repo_of(s) is not None,
                     "listening": listening(s.port),
                     "started_here": s.name in started}
            for s in SURFACES}, indent=2))
        return 0

    status = 0
    for name in args.to_stop or []:
        ok, detail = stop(name)
        print(f"{name}: {detail}")
        status = status or (0 if ok else 1)

    for name in args.to_start or []:
        surface = BY_NAME[name]
        repo = repo_of(surface)
        if repo is None:
            print(f"{name}: {surface.repo} is not beside this clone")
            status = 1
            continue
        ok, detail = start(surface, repo)
        print(f"{name}: {detail}")
        status = status or (0 if ok else 1)

    if args.to_start or args.to_stop:
        print()

    report()
    return status


if __name__ == "__main__":
    sys.exit(main())
