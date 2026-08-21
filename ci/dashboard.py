#!/usr/bin/env python3
"""Bring the trio up from nothing, and say what is already up.

    uv run qm dashboard
    uv run qm dashboard --start harness
    uv run qm dashboard --start web
    uv run qm dashboard --stop harness

**ONE HARNESS, TWO FRONT ENDS.** `qmcp` holds the work and answers over HTTP.
`codecartographer` is its front end on the web and `dossier` is its front end in
a terminal. Neither front end owns anything: both read the same harness, and a
figure that differs between them is a defect rather than a point of view. That
is the whole reason two exist -- one front end can be wrong for a long time
without anybody finding out.

**REPORTING IS THE DEFAULT AND STARTING IS ASKED FOR.** Running this changes
nothing unless `--start` names something. A command that quietly spawned three
servers because somebody wanted to look at a status table is the kind of thing
this corpus keeps ruling out: an act with consequences happens because a person
asked for it, in those words, every time.

**A SERVER CAN BE DETACHED AND A TERMINAL FRONT END CANNOT.** `--start` backs
the two servers off into their own processes and records where they went.
`dossier dashboard` draws in the terminal it is run from, so this prints the
command instead of pretending it can launch it somewhere you would see it.
Offering `--start terminal` would produce a process drawing to a pipe nobody is
reading, and report success.

**THE PORTS ARE CONSTANTS, WHICH IS A MEMORY AID AND NOT A CLAIM.** pi for the
harness, e for the web front end, phi for the terminal one. Nothing depends on
the number; each is overridable, and the value here is only the default this
corpus's own tooling looks on.
"""

from __future__ import annotations

import argparse
import json
import os
import socket
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
SIBLINGS = HERE.parent

# Where a detached server's details go, so `--stop` acts on what `--start`
# actually launched rather than on whatever happens to hold the port. Killing by
# port would let this command stop a process it never started.
STATE = Path(os.environ.get("QM_DASHBOARD_STATE")
             or Path.home() / ".qm" / "dashboard.json")


@dataclass(frozen=True)
class Surface:
    """One process in the trio, and how to bring it up."""

    name: str
    repo: str
    role: str
    port: int
    constant: str
    command: tuple[str, ...]
    detachable: bool
    """Whether starting it in the background produces something usable. False
    for a terminal front end, which draws where it was run and nowhere else."""

    note: str = ""


SURFACES: tuple[Surface, ...] = (
    Surface(
        name="harness", repo="qmcp", role="the work, and the only source of it",
        port=3141, constant="pi",
        command=("qmcp", "serve", "--port", "3141"), detachable=True,
        note="both front ends read this. Start it first, or they have "
             "nothing to draw"),
    Surface(
        name="web", repo="codecartographer",
        role="front end on the web", port=2718, constant="e",
        command=("codecarto", "serve", "--port", "2718"), detachable=True,
        note="draws the harness's topology as a graph"),
    Surface(
        name="terminal", repo="dossier",
        role="front end in a terminal", port=1618, constant="phi",
        command=("dossier", "dashboard"), detachable=False,
        note="run this in the terminal you want to watch. `dossier serve "
             "--port 1618` is its API, which is a different thing"),
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

    **THIS IS NOT `IS THE RIGHT THING RUNNING`.** Any process may hold a port,
    and this cannot tell the harness from something else that grabbed 3141. It
    is reported as "something is listening" for that reason -- a status table
    claiming the harness is up because a port is busy would be a confident
    wrong answer, and the ordinary cause is a stale process from an earlier
    session.
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
    return True, f"started as pid {child.pid}; output goes to {log}"


def stop(name: str) -> tuple[bool, str]:
    """Stop what this command started, by the pid it recorded.

    **BY RECORDED PID, NEVER BY PORT.** Stopping whatever holds a port would let
    this kill a process it did not start and knows nothing about.
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
    return True, f"stopped pid {pid}"


def report() -> int:
    """The status table, and what to run for anything not up."""
    started = running()
    print("THE TRIO")
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
        description=("Say what of the trio is up, and start what is not. "
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
