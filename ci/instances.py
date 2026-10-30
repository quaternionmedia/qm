"""Every server running on this machine, and which one each is.

    uv run qm instances                      # what is up, and what each one is
    uv run qm instances --json               # the same document, on stdout
    uv run qm instances --write              # the document, at ~/.qm/instances.json
    uv run qm instances --check              # exit 1 if any is stale, mismatched or undeclared
    uv run qm instances --port 8000          # also look at a port nothing declares; repeatable
    uv run qm instances run --repo NAME [--port N] [--session S] -- COMMAND ...
    uv run qm instances prune [--yes]        # remove run-files whose process is gone

**The collector** `records/DRAFT-monitoring-seam-and-instance-identity.md` asks
for. A server declares itself with a run-file in a machine-scoped directory
outside every repository; this reads every run-file, asks the operating system
whether its process is alive, dials the port it names, and matches the answer
against the declaration before attributing anything to it (decisions 4 and 5).
It then probes the ports the estate reserves, the dashboard's surfaces and the
family demo's range, for a listener nobody declared (decision 6).

    identified   the port answers as the process the run-file names
    answering    the port answers, and the server does not say which one it is
    silent       the process is alive and its port does not answer
    stale        the process is gone; the run-file outlived it
    mismatch     the port answers as another process
    undeclared   a reserved port is held, and no run-file names it

**Where run-files live.** `~/.qm/run/` for the estate (`QM_RUN_DIR` moves it),
written by `qm instances run` and by `qm dashboard --start`; and qmcp's own,
`~/.qmcp/run/` (`QMCP_RUN_DIR`), which qmcp writes for itself.

**What it reads, and what it never does.** It requests one path per instance,
the health path its run-file declares, and nothing else: a read of qmcp's queue
can write to it (the record's context), so no other route is in reach. It
stops nothing; `prune` removes run-files and only those whose process the
operating system says is gone.

**What it cannot see.** A server that writes no run-file and holds no reserved
port. A server whose health answer states no pid is attributed by its run-file
alone, and is reported as `answering`, never as `identified`. The document is
machine-scoped: it says what was true on this machine at `generated_at`, and
`--write` refuses a path inside a repository (decision 2).
"""

from __future__ import annotations

import argparse
import json
import os
import socket
import subprocess
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

import yaml

ROOT = Path(__file__).resolve().parent.parent
FAMILY_DEMO = ROOT / "ci" / "family-demo.yaml"
SCHEMA = 1
HOST = "127.0.0.1"
PROBLEMS = ("stale", "mismatch", "undeclared")


def run_dirs() -> list[Path]:
    """The estate's run directory, then qmcp's own."""
    return [Path(os.environ.get("QM_RUN_DIR") or Path.home() / ".qm" / "run"),
            Path(os.environ.get("QMCP_RUN_DIR") or Path.home() / ".qmcp" / "run")]


def default_document() -> Path:
    return Path.home() / ".qm" / "instances.json"


def tilde(path: str | Path | None) -> str | None:
    """A path under the home directory, written from `~`, so a document a person
    pastes does not carry their account name."""
    if path is None:
        return None
    text = str(path).replace("\\", "/")
    home = str(Path.home()).replace("\\", "/")
    return "~" + text[len(home):] if text.lower().startswith(home.lower()) else text


# --- the world, each read injected so the tests need no socket and no process


def alive(pid: int) -> bool:
    """Whether the operating system holds a running process with this pid.

    Never `os.kill(pid, 0)` on Windows: there it terminates the process."""
    if pid <= 0:
        return False
    if sys.platform == "win32":
        import ctypes
        handle = ctypes.windll.kernel32.OpenProcess(0x1000, False, pid)
        if not handle:
            return False
        code = ctypes.c_ulong()
        ctypes.windll.kernel32.GetExitCodeProcess(handle, ctypes.byref(code))
        ctypes.windll.kernel32.CloseHandle(handle)
        return code.value == 259                    # STILL_ACTIVE
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def listening(port: int, host: str = HOST) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.settimeout(0.4)
        return probe.connect_ex((host, port)) == 0


def fetch(url: str) -> tuple[int, object]:
    """(status, body): the body parsed as JSON where it is JSON. Status 0 when
    nothing answered."""
    try:
        with urllib.request.urlopen(url, timeout=2) as response:
            raw = response.read().decode("utf-8", errors="replace")
            status = response.status
    except urllib.error.HTTPError as error:
        return error.code, None
    except Exception:                                # noqa: BLE001
        return 0, None
    try:
        return status, json.loads(raw)
    except ValueError:
        return status, raw


@dataclass
class World:
    alive: Callable[[int], bool] = alive
    listening: Callable[[int], bool] = listening
    fetch: Callable[[str], tuple[int, object]] = fetch


# --- what is declared, and what is reserved


def read_run_files(directories: list[Path]) -> list[dict]:
    """Every declaration, normalised to one shape. qmcp's own run-files carry no
    `repo`; their directory says it."""
    found = []
    for directory in directories:
        if not directory.is_dir():
            continue
        for path in sorted(directory.glob("*.json")):
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                found.append({"run_file": str(path), "repo": None, "pid": 0, "port": 0,
                              "unreadable": True})
                continue
            data.setdefault("repo", "qmcp" if path.name.startswith("qmcp-") else None)
            data.setdefault("health", "/health")
            data.setdefault("host", HOST)
            data["run_file"] = str(path)
            found.append(data)
    return found


def reserved_ports() -> dict[int, str]:
    """port -> what reserves it: the dashboard's surfaces, by their constant,
    and the family demo's range."""
    ports: dict[int, str] = {}
    sys.path.insert(0, str(ROOT / "ci"))
    try:
        import dashboard
        for surface in dashboard.SURFACES:
            ports[surface.port] = f"the dashboard's {surface.name} ({surface.repo})"
    except Exception:                                # noqa: BLE001
        pass
    try:
        block = yaml.safe_load(FAMILY_DEMO.read_text(encoding="utf-8"))["ports"]
        for port in range(int(block["first"]), int(block["last"]) + 1):
            ports.setdefault(port, "the family demo's range")
    except Exception:                                # noqa: BLE001
        pass
    return ports


# --- the judgement, one declaration at a time


def judge(declared: dict, world: World) -> dict:
    row = {key: declared.get(key) for key in
           ("repo", "session", "pid", "port", "started_at", "checkout", "commit")}
    row["run_file"] = tilde(declared["run_file"])
    row["checkout"] = tilde(row["checkout"])
    if declared.get("unreadable"):
        return {**row, "state": "stale", "why": "the run-file cannot be read"}
    pid, port = int(declared.get("pid") or 0), int(declared.get("port") or 0)
    if not world.alive(pid):
        answered = " Another process answers its port." if port and world.listening(port) else ""
        return {**row, "state": "stale",
                "why": f"pid {pid} is gone; the run-file outlived it.{answered}"}
    if not port or not world.listening(port):
        return {**row, "state": "silent",
                "why": f"pid {pid} is alive and port {port} does not answer"}
    status, body = world.fetch(f"http://{declared['host']}:{port}{declared['health']}")
    if status == 0:
        return {**row, "state": "silent",
                "why": f"port {port} accepts a connection and {declared['health']} answers nothing"}
    if status != 200:
        return {**row, "state": "answering",
                "why": f"the port answers; {declared['health']} answered {status}"}
    said = body if isinstance(body, dict) else {}
    if "pid" in said and int(said["pid"]) != pid:
        return {**row, "state": "mismatch",
                "why": f"port {port} answers as pid {said['pid']}, not {pid}"}
    if "port" in said and int(said["port"]) != port:
        return {**row, "state": "mismatch",
                "why": f"the server on {port} says it serves {said['port']}"}
    started = declared.get("started_at")
    if "started_at" in said and started and said["started_at"] != started:
        return {**row, "state": "mismatch",
                "why": "the server's start time is not the run-file's"}
    if "pid" in said:
        return {**row, "state": "identified", "why": "its health answer names this pid and port"}
    return {**row, "state": "answering",
            "why": "the port answers; the server does not say which one it is"}


def collect(directories: list[Path] | None = None, world: World | None = None,
            reserved: dict[int, str] | None = None) -> dict:
    world = world or World()
    directories = run_dirs() if directories is None else directories
    reserved = reserved_ports() if reserved is None else reserved
    rows = [judge(declared, world) for declared in read_run_files(directories)]
    declared_live = {row["port"] for row in rows if row["state"] != "stale"}
    candidates = sorted(port for port in reserved if port not in declared_live)
    with ThreadPoolExecutor(max_workers=32) as pool:
        held = list(pool.map(world.listening, candidates))
    undeclared = [{"port": port, "reserved_for": reserved[port]}
                  for port, up in zip(candidates, held) if up]
    counts = {state: sum(1 for row in rows if row["state"] == state)
              for state in ("identified", "answering", "silent", "stale", "mismatch")}
    counts["undeclared"] = len(undeclared)
    return {
        "schema": SCHEMA,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "scope": "this machine, at generated_at; never committed",
        "run_dirs": [tilde(d) for d in directories],
        "reserved_ports_probed": len(candidates),
        "instances": rows,
        "undeclared": undeclared,
        "counts": counts,
    }


def render(document: dict) -> str:
    rows = document["instances"]
    out = [f"INSTANCES ON THIS MACHINE  (at {document['generated_at']}; "
           "machine-scoped, never committed)", "=" * 78]
    if rows:
        out.append(f"{'repo':<18} {'session':<14} {'pid':>7} {'port':>6}  {'state':<11} why")
        out.append("-" * 78)
        for row in rows:
            out.append(f"{str(row['repo'] or '?'):<18} {str(row['session'] or '-'):<14} "
                       f"{row['pid'] or 0:>7} {row['port'] or 0:>6}  {row['state']:<11} "
                       f"{row['why']}")
    else:
        out.append("No run-file declares a server here.")
    if document["undeclared"]:
        out += ["", "HELD WITHOUT A RUN-FILE  (reserved ports something listens on)", "-" * 78]
        out += [f"{item['port']:>6}  {item['reserved_for']}" for item in document["undeclared"]]
    counts = document["counts"]
    problems = sum(counts[k] for k in PROBLEMS)
    out.append("")
    # Decision 7: the quiet sentence only where every instance has earned it.
    if rows and not problems and counts["silent"] == 0 and counts["answering"] == 0:
        out.append(f"Every declared server is identified, and no reserved port is held "
                   f"without one. Run-files read from {', '.join(document['run_dirs'])}.")
    else:
        out.append("  ".join(f"{k} {v}" for k, v in counts.items()) +
                   f"  -- run-files read from {', '.join(document['run_dirs'])}; "
                   f"{document['reserved_ports_probed']} reserved port(s) probed.")
    return "\n".join(out)


# --- declaring a server that does not declare itself


def free_port(host: str = HOST) -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.bind((host, 0))
        return probe.getsockname()[1]


def _git(*args: str) -> str | None:
    try:
        done = subprocess.run(["git", *args], capture_output=True, text=True, timeout=10)
    except Exception:                                # noqa: BLE001
        return None
    if done.returncode != 0:
        return None
    return done.stdout.strip() or None


def declare(repo: str, pid: int, port: int, command: list[str], *, session: str | None = None,
            health: str = "/health", host: str = HOST, state: str | None = None,
            checkout: Path | None = None, directory: Path | None = None) -> Path:
    """Write the run-file that declares a server this machine is running."""
    directory = directory or run_dirs()[0]
    directory.mkdir(parents=True, exist_ok=True)
    where = ["-C", str(checkout)] if checkout else []
    path = directory / f"{repo}-{pid}.json"
    path.write_text(json.dumps({
        "schema": SCHEMA, "repo": repo, "pid": pid, "host": host, "port": port,
        "health": health, "session": session or os.environ.get("QM_SESSION"),
        "started_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "checkout": _git(*where, "rev-parse", "--show-toplevel"),
        "commit": _git(*where, "rev-parse", "--short", "HEAD"), "state": state,
        "command": command,
    }, indent=2), encoding="utf-8")
    return path


def withdraw(repo: str, pid: int, directory: Path | None = None) -> None:
    (directory or run_dirs()[0]).joinpath(f"{repo}-{pid}.json").unlink(missing_ok=True)


def run(repo: str, command: list[str], port: int = 0, session: str | None = None,
        health: str = "/health", host: str = HOST, state: str | None = None,
        directory: Path | None = None) -> int:
    """Serve `command` with a run-file for as long as it lives.

    `{port}`, `{host}` and `{state}` in the command are replaced. Port 0 takes a
    free one: the port is chosen here and handed to the server, which a server
    that binds port 0 itself would make unknowable to everyone but it."""
    port = port or free_port(host)
    values = {"port": str(port), "host": host, "state": state or ""}
    argv = [part.format(**values) if "{" in part else part for part in command]
    child = subprocess.Popen(argv, creationflags=getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0))
    path = declare(repo, child.pid, port, argv, session=session, health=health, host=host,
                   state=state, directory=directory)
    print(f"instances: {repo} serving on {host}:{port} as pid {child.pid}; "
          f"declared in {tilde(path)}", flush=True)
    try:
        return child.wait()
    except KeyboardInterrupt:
        stop_tree(child.pid)
        return 130
    finally:
        path.unlink(missing_ok=True)


def stop_tree(pid: int) -> None:
    if sys.platform == "win32":
        subprocess.run(["taskkill", "/F", "/T", "/PID", str(pid)], capture_output=True, check=False)
    else:
        os.kill(pid, 15)


def prune(directories: list[Path], world: World, yes: bool) -> list[Path]:
    """The run-files whose process is gone; removed only with `yes`."""
    gone = [Path(d["run_file"]) for d in read_run_files(directories)
            if d.get("unreadable") or not world.alive(int(d.get("pid") or 0))]
    if yes:
        for path in gone:
            path.unlink(missing_ok=True)
    return gone


def inside_a_repository(path: Path) -> bool:
    parent = path.resolve().parent
    while not parent.exists():
        parent = parent.parent
    done = subprocess.run(["git", "-C", str(parent), "rev-parse", "--show-toplevel"],
                          capture_output=True, text=True)
    return done.returncode == 0


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv[:1] == ["run"]:
        parser = argparse.ArgumentParser(prog="qm instances run")
        parser.add_argument("--repo", required=True)
        parser.add_argument("--port", type=int, default=0)
        parser.add_argument("--session")
        parser.add_argument("--health", default="/health")
        parser.add_argument("--host", default=HOST)
        parser.add_argument("--state")
        parser.add_argument("command", nargs=argparse.REMAINDER)
        args = parser.parse_args(argv[1:])
        command = args.command[1:] if args.command[:1] == ["--"] else args.command
        if not command:
            parser.error("give the command after --")
        return run(args.repo, command, args.port, args.session, args.health, args.host, args.state)
    if argv[:1] == ["prune"]:
        yes = "--yes" in argv
        gone = prune(run_dirs(), World(), yes)
        for path in gone:
            print(f"{'removed' if yes else 'would remove'} {tilde(path)}")
        if not gone:
            print("instances: no run-file outlived its process.")
        elif not yes:
            print("instances: nothing removed; --yes removes these, and only these.")
        return 0

    parser = argparse.ArgumentParser(prog="qm instances", description=__doc__.split("\n")[0])
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--write", nargs="?", const=str(default_document()))
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--port", type=int, action="append", default=[],
                        help="another port to look at, such as a stack that writes no "
                             "run-file; repeatable, and never committed anywhere")
    args = parser.parse_args(argv)
    reserved = reserved_ports()
    for port in args.port:
        reserved.setdefault(port, "named on the command line")
    document = collect(reserved=reserved)
    if args.write:
        target = Path(args.write).expanduser()
        if inside_a_repository(target):
            print(f"instances: {target} is inside a repository, and this document is "
                  "machine-scoped. Write it outside every repository.", file=sys.stderr)
            return 2
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(document, indent=2), encoding="utf-8")
    print(json.dumps(document, indent=2) if args.json else render(document))
    if args.check and any(document["counts"][k] for k in PROBLEMS):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
