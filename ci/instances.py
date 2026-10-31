"""Every server running on this machine, and which one each is.

    uv run qm instances                      # what is up, and what each one is
    uv run qm instances --json               # the same document, on stdout
    uv run qm instances --write              # the document, at ~/.qm/instances.json
    uv run qm instances --check              # exit 1 on stale, mismatch, undeclared or missing
    uv run qm instances --port 8000          # also look at a port nothing declares; repeatable
    uv run qm instances run --repo NAME [--port N] [--session S] -- COMMAND ...
    uv run qm instances prune [--yes]        # remove run-files whose process is gone
    uv run qm instances register --family core            # this machine runs a family
    uv run qm instances register --repo qmcp --repo apothecary [--name bench]
    uv run qm instances register [--clear]   # what is registered; or nothing

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

**Which repositories this machine should be running.** `register` writes that
claim to `~/.qm/registered.json` (`QM_REGISTERED` moves it): a family, whose
members `families.json` resolves from the family record, a selection named
repository by repository, or both. Every reading then judges each registered
repository as well as each server:

    up           a live run-file declares it, and its port answers
    silent       a live run-file declares it, and its port does not answer
    missing      nothing declares it running, and this corpus says how it starts
    unjudged     nothing declares it running, and nothing in this corpus says how

A repository this corpus names no way to start, `qm` itself among them, is
`unjudged` rather than `missing`, so registering a family does not fail
`--check` on the members that serve nothing. A server running outside the
registration is reported, and is not a problem.

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
FAMILIES = ROOT / "families.json"
SCHEMA = 1
HOST = "127.0.0.1"
PROBLEMS = ("stale", "mismatch", "undeclared", "missing")


def run_dirs() -> list[Path]:
    """The estate's run directory, then qmcp's own."""
    return [Path(os.environ.get("QM_RUN_DIR") or Path.home() / ".qm" / "run"),
            Path(os.environ.get("QMCP_RUN_DIR") or Path.home() / ".qmcp" / "run")]


def default_document() -> Path:
    return Path.home() / ".qm" / "instances.json"


def registration_path() -> Path:
    return Path(os.environ.get("QM_REGISTERED") or Path.home() / ".qm" / "registered.json")


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

    A zombie, a process that has exited and whose parent has not yet collected
    it, holds its pid without running, so it is not alive. Never
    `os.kill(pid, 0)` on Windows: there it terminates the process."""
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
        pass
    try:                                            # field 3 of /proc/<pid>/stat
        state = Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].split()[0]
    except (OSError, IndexError):                   # no /proc, as on macOS
        return True
    return state not in ("Z", "X")


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


def created(pid: int) -> int | None:
    """When the process holding this pid started, in the operating system's own
    count, or None where it cannot say. A pid is handed out again once its
    process has gone, so a pid recorded before a restart can name a stranger;
    the start time tells them apart."""
    if pid <= 0:
        return None
    if sys.platform == "win32":
        import ctypes
        from ctypes import wintypes
        kernel = ctypes.windll.kernel32
        handle = kernel.OpenProcess(0x1000, False, pid)
        if not handle:
            return None
        times = [wintypes.FILETIME() for _ in range(4)]
        ok = kernel.GetProcessTimes(handle, *(ctypes.byref(t) for t in times))
        kernel.CloseHandle(handle)
        return (times[0].dwHighDateTime << 32 | times[0].dwLowDateTime) if ok else None
    try:                                            # field 22 of /proc/<pid>/stat
        return int(Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].split()[19])
    except (OSError, ValueError, IndexError):
        return None


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


# --- which repositories this machine should be running


def families(path: Path = FAMILIES) -> dict[str, list[str]]:
    """family -> every member, the families within it included, as
    `families.json` resolves them from the record."""
    document = json.loads(path.read_text(encoding="utf-8"))
    return {f["name"]: list(f["all_members"]) for f in document["families"]}


def roster_names() -> set[str]:
    """Every name the roster answers to: a repository's name and its reference."""
    sys.path.insert(0, str(ROOT / "ci"))
    import roster
    return {name for entry in roster.load()
            for name in (entry.get("name"), entry.get("ref")) if name}


def servers() -> dict[str, str]:
    """repo -> the command that brings it up, for every repository this corpus
    says how to start: the dashboard's surfaces that detach, the stacks its
    owner session starts, and the family demo's members that serve. A
    repository absent here may well serve; nothing in this corpus says how."""
    known: dict[str, str] = {}
    try:
        block = yaml.safe_load(FAMILY_DEMO.read_text(encoding="utf-8"))
        for member in block.get("members") or []:
            if member.get("serves"):
                known[member["name"]] = "uv run qm family-demo"
    except Exception:                                # noqa: BLE001
        pass
    sys.path.insert(0, str(ROOT / "ci"))
    try:
        import dashboard
        for surface in dashboard.SURFACES:
            if surface.detachable:
                known[surface.repo] = f"uv run qm dashboard --start {surface.name}"
            elif surface.owner_starts:
                known[surface.repo] = (f"ask the session that owns {surface.repo}; "
                                       f"if none has, cd {surface.repo} && "
                                       f"{' '.join(surface.command)}")
    except Exception:                                # noqa: BLE001
        pass
    return known


def registration(named_families: list[str], repos: list[str], name: str | None,
                 known_families: dict[str, list[str]], known_repos: set[str]) -> dict:
    """The document `register` writes, refusing a name nothing resolves."""
    unknown = [f for f in named_families if f not in known_families]
    if unknown:
        raise ValueError(f"no family named {', '.join(unknown)}; families.json names "
                         f"{', '.join(sorted(known_families))}")
    strangers = [r for r in repos if r not in known_repos]
    if strangers:
        raise ValueError(f"{', '.join(strangers)}: not in the roster, ci/workspace.yaml")
    if not name:
        name = named_families[0] if len(named_families) == 1 and not repos else "local"
    return {
        "schema": SCHEMA, "name": name,
        "families": list(dict.fromkeys(named_families)), "repos": list(dict.fromkeys(repos)),
        "registered_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "scope": "this machine; never committed",
    }


def read_registration(path: Path | None = None) -> dict | None:
    try:
        return json.loads((path or registration_path()).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def expected(registered: dict, known_families: dict[str, list[str]]
             ) -> tuple[dict[str, str], list[str]]:
    """(repo -> why it is registered, the families that no longer resolve). A
    family is resolved when it is read, so a member the roster gains later is
    expected without registering again."""
    found: dict[str, str] = {}
    gone = []
    for family in registered.get("families") or []:
        if family not in known_families:
            gone.append(family)
            continue
        for member in known_families[family]:
            found.setdefault(member, f"family {family}")
    for repo in registered.get("repos") or []:
        found.setdefault(repo, "named")
    return found, gone


def judge_registered(members: dict[str, str], rows: list[dict],
                     starts: dict[str, str]) -> list[dict]:
    """One row per registered repository: up, silent, missing or unjudged."""
    judged = []
    for repo, via in members.items():
        mine = [row for row in rows if row["repo"] == repo]
        answering = [r for r in mine if r["state"] in ("identified", "answering")]
        silent = [r for r in mine if r["state"] == "silent"]
        row = {"repo": repo, "via": via, "start": starts.get(repo)}
        if answering:
            row |= {"state": "up", "why": "; ".join(
                f"pid {r['pid']} on {r['port']}, {r['state']}" for r in answering)}
        elif silent:
            row |= {"state": "silent", "why": "; ".join(
                f"pid {r['pid']} is alive and {r['port']} does not answer" for r in silent)}
        elif repo in starts:
            row |= {"state": "missing", "why": f"nothing declares it running; {starts[repo]}"}
        else:
            row |= {"state": "unjudged",
                    "why": "nothing declares it running, and nothing here starts it"}
        judged.append(row)
    return judged


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
            reserved: dict[int, str] | None = None, registered: dict | None = None,
            known_families: dict[str, list[str]] | None = None,
            starts: dict[str, str] | None = None) -> dict:
    world = world or World()
    directories = run_dirs() if directories is None else directories
    reserved = reserved_ports() if reserved is None else reserved
    rows = [judge(declared, world) for declared in read_run_files(directories)]
    machine = None
    if registered:
        members, gone = expected(registered, families() if known_families is None
                                 else known_families)
        for row in rows:
            row["registered"] = row["repo"] in members
        machine = {key: registered.get(key) for key in
                   ("name", "families", "repos", "registered_at")}
        machine["unresolved"] = gone
        machine["repositories"] = judge_registered(
            members, rows, servers() if starts is None else starts)
    declared_live = {row["port"] for row in rows if row["state"] != "stale"}
    candidates = sorted(port for port in reserved if port not in declared_live)
    with ThreadPoolExecutor(max_workers=32) as pool:
        held = list(pool.map(world.listening, candidates))
    undeclared = [{"port": port, "reserved_for": reserved[port]}
                  for port, up in zip(candidates, held) if up]
    counts = {state: sum(1 for row in rows if row["state"] == state)
              for state in ("identified", "answering", "silent", "stale", "mismatch")}
    counts["undeclared"] = len(undeclared)
    judged = machine["repositories"] if machine else []
    for state in ("missing", "unjudged"):
        counts[state] = sum(1 for row in judged if row["state"] == state)
    return {
        "schema": SCHEMA,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "scope": "this machine, at generated_at; never committed",
        "run_dirs": [tilde(d) for d in directories],
        "reserved_ports_probed": len(candidates),
        "instances": rows,
        "undeclared": undeclared,
        "registered": machine,
        "counts": counts,
    }


def render(document: dict) -> str:
    rows = document["instances"]
    out = [f"INSTANCES ON THIS MACHINE  (at {document['generated_at']}; "
           "machine-scoped, never committed)", "=" * 78]
    if rows:
        out.append(f"{'repo':<17} {'session':<19} {'pid':>6} {'port':>6}  {'state':<11} why")
        out.append("-" * 78)
        for row in rows:
            out.append(f"{str(row['repo'] or '?'):<17} {str(row['session'] or '-'):<19} "
                       f"{row['pid'] or 0:>6} {row['port'] or 0:>6}  {row['state']:<11} "
                       f"{row['why']}")
    else:
        out.append("No run-file declares a server here.")
    if document["undeclared"]:
        out += ["", "HELD WITHOUT A RUN-FILE  (reserved ports something listens on)", "-" * 78]
        out += [f"{item['port']:>6}  {item['reserved_for']}" for item in document["undeclared"]]
    machine = document.get("registered")
    if machine:
        claim = ", ".join([*(f"family {f}" for f in machine["families"]), *machine["repos"]])
        out += ["", f"REGISTERED ON THIS MACHINE  ({machine['name']}: {claim}; "
                    f"since {machine['registered_at']})", "-" * 78]
        out += [f"{row['repo']:<17} {row['state']:<9} {row['via']:<16} {row['why']}"
                for row in machine["repositories"]]
        out += [f"family {name} is no longer in families.json, so nothing of it is expected"
                for name in machine["unresolved"]]
        outside = sorted({str(row["repo"] or "?") for row in rows
                          if not row.get("registered") and row["state"] != "stale"})
        if outside:
            out.append(f"Running and not registered: {', '.join(outside)}.")
    counts = document["counts"]
    problems = sum(counts.get(k, 0) for k in PROBLEMS)
    out.append("")
    # Decision 7: the quiet sentence only where every instance has earned it.
    if rows and not problems and counts["silent"] == 0 and counts["answering"] == 0:
        earned = (f" Every registered repository this corpus starts is up, and "
                  f"{counts['unjudged']} it starts nothing for are not judged."
                  if machine else "")
        out.append(f"Every declared server is identified, and no reserved port is held "
                   f"without one.{earned} Run-files read from "
                   f"{', '.join(document['run_dirs'])}.")
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


def describe(registered: dict, known_families: dict[str, list[str]]) -> str:
    members, gone = expected(registered, known_families)
    claim = ", ".join([*(f"family {f}" for f in registered["families"]), *registered["repos"]])
    lines = [f"{registered['name']}: {claim}, registered {registered['registered_at']}",
             f"  {len(members)} repositories: {', '.join(members)}"]
    lines += [f"  family {name} is no longer in families.json" for name in gone]
    return "\n".join(lines)


def register(argv: list[str]) -> int:
    """Say which repositories this machine should be running, or show it."""
    parser = argparse.ArgumentParser(
        prog="qm instances register",
        description="Which repositories this machine should be running: a family, a "
                    "selection of its own, or both. Replaces what was registered before; "
                    "with no option, shows it.")
    parser.add_argument("--family", action="append", default=[],
                        help="every member of this family, as families.json resolves it "
                             "when read; repeatable")
    parser.add_argument("--repo", action="append", default=[],
                        help="this repository, by its roster name; repeatable")
    parser.add_argument("--name", help="what to call the selection (default: the family's "
                                       "name, or `local`)")
    parser.add_argument("--clear", action="store_true", help="register nothing")
    args = parser.parse_args(argv)
    path = registration_path()
    if args.clear:
        path.unlink(missing_ok=True)
        print(f"instances: nothing is registered on this machine; {tilde(path)} is gone.")
        return 0
    if not args.family and not args.repo:
        current = read_registration(path)
        print(describe(current, families()) if current else
              "Nothing is registered on this machine. `qm instances register --family NAME` "
              "or `--repo NAME` says what it should be running.")
        return 0
    if inside_a_repository(path):
        print(f"instances: {path} is inside a repository, and a registration belongs to "
              "one machine. Keep it outside every repository.", file=sys.stderr)
        return 2
    try:
        document = registration(args.family, args.repo, args.name, families(), roster_names())
    except ValueError as error:
        print(f"instances: {error}", file=sys.stderr)
        return 2
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(document, indent=2), encoding="utf-8")
    print(describe(document, families()))
    print(f"Written to {tilde(path)}; `uv run qm instances` judges it, and "
          "`uv run qm dashboard --start-registered` starts the surfaces in it.")
    return 0


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
    if argv[:1] == ["register"]:
        return register(argv[1:])
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
    document = collect(reserved=reserved, registered=read_registration())
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
