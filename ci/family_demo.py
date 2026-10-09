#!/usr/bin/env python3
"""The performing family on one machine: each member alone, then together.

    uv run qm family-demo                         # wave 0, then the core together
    uv run qm family-demo --wave 0                # each member alone
    uv run qm family-demo --wave together --hold  # keep it up; open the page
    uv run qm family-demo --ref leo=origin/setlist
    uv run qm family-demo --plan                  # what would run; starts nothing

**WHAT IT SHOWS.** `ci/family-demo.yaml` names the members, the phase each
joins in, the port each is given and the check each is asked to pass. For every
member of a phase that runs, this checks the member out at an exact commit into
a clone of its own, installs it through its lock, starts it on its reserved
port with scratch state, waits on a readiness probe, drives one behaviour in the
real surface, records a picture of that render, stops it, and proves the port
is free. Then it does the same with every member up at once, writes a page that
links each live surface and embeds each picture, and writes a manifest of
commits, commands, ports, timings and results. The page is the demo a person
opens; the manifest is the record.

**WHAT IT DOES NOT SHOW, AND SAYS SO IN EVERY RUN.** Integration. Running the
members together is process simultaneity: they share a machine, not a protocol.
The run looks for a seam two ways -- which members name another in their tracked
source, and which member processes hold a connection to another member's port
while all are up -- and prints both. A name in source is not a wire, and a
connection table sampled at moments cannot see a short request between samples
or anything sent over UDP. No result here is an integration result unless a
check exercised the seam, and none does yet.

**WHERE IT WRITES.** Nowhere it does not own. Each member is cloned with
`git clone --shared` into the work directory -- nothing is written into the
clone the roster resolves, not even worktree metadata -- and every database,
log and data directory is under the run's scratch directory. The work directory
defaults to the system temporary directory and is never inside this repository.

**WHAT A RESULT MEANS.** `pass`, `fail` or `unknown`, per check and per wave,
and unknown is never folded into fail: a port somebody else holds, a probe that
crashed or a member that never got as far as its check is `unknown`, with the
reason. The exit status is 0 when every member that ran passed, 1 when any
failed or an artifact the manifest names is missing, 3 when none failed and some
were unknown, and 2 for a roster or an invocation this cannot run. A skip is not
a pass.

**HAZARDS ARE MEASURED, NOT ASSUMED.** While each member is up, every socket
its process tree holds is listed, and one outside its reserved ports is printed
as a hazard -- a member that opened an OSC port or dialled a console would show
here, whatever its source says. So are a process this run did not start holding
a reserved port, a descendant that had to be forced at shutdown, and a port
still held afterwards.

**WHAT IT CANNOT SEE.** Whether a member is correct beyond the one behaviour it
is asked for, outbound traffic that holds no socket open long enough to be
listed, real audio, MIDI or lighting hardware, and a member the roster does not
place -- that one is printed as unplaced, never dropped.

`protocols/local-demo.md` is the protocol this follows. It is the first runnable
slice of a simultaneous run of the whole performing family: the core phase
starts, and the phases after it are declared with what each member needs.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import platform
import re
import shutil
import signal
import socket
import struct
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from concurrent.futures import ThreadPoolExecutor

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from make_workspace import resolve  # noqa: E402
import roster as corpus_roster  # noqa: E402

CI_DIR = Path(__file__).resolve().parent
CORPUS = CI_DIR.parent
PLAN = CI_DIR / "family-demo.yaml"
PROBES = CI_DIR / "family_demo_probes.py"
FAMILIES = CORPUS / "families.json"

# The families whose members make up the performing estate. A member of one of
# these that the plan does not place is reported as unplaced on every run.
PERFORMING = ("show-control", "performer-display", "instruments")

RESULTS = ("pass", "fail", "unknown")
RUNNERS = ("browser", "terminal")
COUNTS = ("behaviour", "surface")
PLACEHOLDER = re.compile(r"\{([a-z]+)(?::([a-z0-9_-]+))?\}")
WINDOWS = os.name == "nt"

# A silent PCM WAV: a header and no samples, which is a file the member's
# library lists without anything being recorded.
SILENT_WAV = (b"RIFF" + struct.pack("<I", 36) + b"WAVE"
              + b"fmt " + struct.pack("<IHHIIHH", 16, 1, 1, 44100, 88200, 2, 16)
              + b"data" + struct.pack("<I", 0))


class PlanError(ValueError):
    """The demo roster cannot be run as written."""


# ===================================================================
# THE PLAN -- read, checked and expanded without starting anything
# ===================================================================

def load_plan(path: Path = PLAN) -> dict:
    document = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if document.get("schema") != 1:
        raise PlanError(f"{path.name}: schema {document.get('schema')!r} is not 1")
    return document


def check_plan(plan: dict, rostered: set[str], probes: dict[str, set[str]]) -> list[str]:
    """Every reason the plan cannot be run as written. Empty is runnable.

    `rostered` is the corpus roster's names; `probes` maps a runner to the
    check names the probe module knows. Both are passed in rather than read
    here, so the rules can be tested without a roster or a probe on disk.
    """
    problems: list[str] = []
    span = plan.get("ports") or {}
    first, last = span.get("first"), span.get("last")
    if not isinstance(first, int) or not isinstance(last, int) or first > last:
        return [f"ports: first/last must be integers in order, got {first!r}..{last!r}"]

    phases = {p.get("id"): p for p in plan.get("phases") or []}
    if not phases:
        problems.append("phases: none declared")
    owner: dict[int, str] = {}
    names: set[str] = set()
    for member in plan.get("members") or []:
        name = member.get("name") or "<unnamed>"
        if name in names:
            problems.append(f"{name}: declared twice")
        names.add(name)
        if name not in rostered:
            problems.append(f"{name}: not in ci/workspace.yaml, so no clone can be resolved")
        phase = phases.get(member.get("phase"))
        if phase is None:
            problems.append(f"{name}: phase {member.get('phase')!r} is not declared")
            continue
        ports = member.get("ports") or {}
        if not ports:
            problems.append(f"{name}: no reserved port")
        for label, port in ports.items():
            if not isinstance(port, int) or not first <= port <= last:
                problems.append(f"{name}: port {label}={port!r} is outside {first}..{last}")
            elif port in owner:
                problems.append(f"{name}: port {port} is already {owner[port]}'s")
            else:
                owner[port] = name
        if phase.get("runs"):
            problems += _runnable_problems(member, probes)
        elif not member.get("needs"):
            problems.append(f"{name}: a phase that does not run must say what it needs to join")
    return problems


def _runnable_problems(member: dict, probes: dict[str, set[str]]) -> list[str]:
    name = member["name"]
    problems = []
    ports = set((member.get("ports") or {}).keys())
    if not member.get("processes"):
        problems.append(f"{name}: runs, but starts no process")
    for process in member.get("processes") or []:
        if not process.get("command") or not process.get("ready"):
            problems.append(f"{name}: process {process.get('id')!r} needs a command and a ready URL")
        if process.get("cwd") not in ("checkout", "state"):
            problems.append(f"{name}: process {process.get('id')!r} cwd must be checkout or state")
        problems += _placeholder_problems(
            name, ports, [*map(str, process.get("command") or []), str(process.get("ready", "")),
                          *map(str, (process.get("env") or {}).values())])
    behaviours = 0
    problems += _placeholder_problems(
        name, ports, [str(member.get("surface", ""))]
        + [str(v) for entry in member.get("checks") or [] for v in (entry.get("params") or {}).values()])
    for entry in member.get("checks") or []:
        runner, counts = entry.get("runner"), entry.get("counts")
        if runner not in RUNNERS:
            problems.append(f"{name}: check {entry.get('name')!r} runner {runner!r} is not one of {RUNNERS}")
        elif entry.get("name") not in probes.get(runner, set()):
            problems.append(f"{name}: no {runner} probe is named {entry.get('name')!r}")
        if counts not in COUNTS:
            problems.append(f"{name}: check {entry.get('name')!r} counts {counts!r} is not one of {COUNTS}")
        behaviours += counts == "behaviour"
    if not behaviours:
        problems.append(f"{name}: runs, but no check asserts a behaviour")
    if member.get("prepare") and member["prepare"] not in PREPARE:
        problems.append(f"{name}: no preparation is named {member['prepare']!r}")
    return problems


def _placeholder_problems(name: str, ports: set[str], texts: list[str]) -> list[str]:
    problems = []
    for text in texts:
        for kind, label in PLACEHOLDER.findall(text):
            if kind == "port" and label not in ports:
                problems.append(f"{name}: {{port:{label}}} names no declared port")
            elif kind not in ("port", "checkout", "state", "token"):
                problems.append(f"{name}: unknown placeholder {{{kind}}}")
    return problems


def unplaced(plan: dict, families: dict) -> list[str]:
    """Members of a performing family that the plan does not place at all."""
    placed = {m.get("name") for m in plan.get("members") or []}
    claimed = [name for family in families.get("families") or []
               if family.get("name") in PERFORMING for name in family.get("members") or []]
    return sorted(name for name in claimed if name not in placed)


def running(plan: dict, phases: list[str] | None = None) -> list[dict]:
    """The members that start, in plan order, optionally narrowed by phase."""
    runs = {p["id"] for p in plan.get("phases") or [] if p.get("runs")}
    chosen = set(phases) if phases else runs
    return [m for m in plan.get("members") or [] if m.get("phase") in runs & chosen]


def expand(value, context: dict):
    """Substitute placeholders in a string, a list or a mapping.

    An unknown placeholder raises rather than passing through, because a
    command carrying a literal `{port:web}` would bind nothing and fail in a
    way that reads like the member's fault.
    """
    if isinstance(value, list):
        return [expand(v, context) for v in value]
    if isinstance(value, dict):
        return {k: expand(v, context) for k, v in value.items()}
    if not isinstance(value, str):
        return value

    def substitute(match: re.Match) -> str:
        kind, label = match.group(1), match.group(2)
        if kind == "port":
            if label not in context["ports"]:
                raise PlanError(f"{{port:{label}}} names no declared port")
            return str(context["ports"][label])
        if kind in ("checkout", "state", "token") and label is None:
            return str(context[kind])
        raise PlanError(f"unknown placeholder {match.group(0)}")

    return PLACEHOLDER.sub(substitute, value)


def parse_refs(pairs: list[str]) -> dict[str, str]:
    refs = {}
    for pair in pairs:
        name, sep, ref = pair.partition("=")
        if not sep or not name or not ref:
            raise PlanError(f"--ref {pair!r}: expected <member>=<ref>")
        refs[name] = ref
    return refs


# ===================================================================
# RESULTS -- combined without coercion
# ===================================================================

def member_result(checks: list[dict], readiness: str) -> str:
    """One member's result in one wave, from its behaviour checks.

    Readiness that did not pass means the checks never ran, so the member is
    `fail` when it was observed not to start and `unknown` when it could not be
    started at all. A surface check is reported beside it and never changes it.
    """
    if readiness == "fail":
        return "fail"
    if readiness != "pass":
        return "unknown"
    behaviour = [c["result"] for c in checks if c.get("counts", "behaviour") == "behaviour"]
    if not behaviour:
        return "unknown"
    if "fail" in behaviour:
        return "fail"
    if "unknown" in behaviour:
        return "unknown"
    return "pass"


def exit_status(results: list[str]) -> int:
    if not results:
        return 3
    if "fail" in results:
        return 1
    if "unknown" in results:
        return 3
    return 0


# ===================================================================
# THE MACHINE -- processes, ports, listeners
# ===================================================================

def child_env(extra: dict | None = None) -> dict:
    """The environment a member starts in.

    `VIRTUAL_ENV` is removed: under `uv run qm` it names this corpus's own
    environment, and a member's `uv run` would warn about it or, worse, a
    member that honours it would run against the wrong interpreter. UTF-8 is
    forced because the logs are files, and a member printing a non-ASCII
    character to a file under a legacy code page dies of it -- a death the
    harness would have caused.
    """
    env = {k: v for k, v in os.environ.items() if k != "VIRTUAL_ENV"}
    env.update(PYTHONUNBUFFERED="1", PYTHONUTF8="1", PYTHONIOENCODING="utf-8",
               NO_COLOR="1", FORCE_COLOR="0")
    env.update(extra or {})
    return env


def executable(argv: list[str]) -> list[str]:
    """The argument vector with its program resolved on PATH.

    Resolved here because a Windows launcher (`npm.cmd`) is not found by name
    without a shell, and a shell is what this harness avoids.
    """
    found = shutil.which(argv[0])
    return [found or argv[0], *argv[1:]]


def listening(port: int) -> set[int] | None:
    """PIDs holding a listening TCP socket on `port`, or None when unknowable."""
    table = connections()
    if table is None:
        return None
    return {pid for local, _remote, state, pid in table
            if state == "LISTEN" and local[1] == port}


def connections() -> list[tuple[tuple[str, int], tuple[str, int], str, int]] | None:
    """Every TCP socket as (local, remote, state, pid), or None.

    `netstat -ano` on Windows; `ss -tanpH` elsewhere. None when neither
    answers -- an empty table and an absent tool are different findings.
    """
    if WINDOWS:
        try:
            out = subprocess.run(["netstat", "-ano", "-p", "TCP"], capture_output=True,
                                 text=True, timeout=30).stdout
            out += subprocess.run(["netstat", "-ano", "-p", "TCPv6"], capture_output=True,
                                  text=True, timeout=30).stdout
        except (OSError, subprocess.TimeoutExpired):
            return None
        return parse_netstat(out)
    try:
        out = subprocess.run(["ss", "-tanpH"], capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.TimeoutExpired):
        return None
    if out.returncode != 0:
        return None
    return parse_ss(out.stdout)


def _endpoint(text: str) -> tuple[str, int] | None:
    host, sep, port = text.rpartition(":")
    if sep and port == "*":  # ss writes a wildcard port this way
        return host.strip("[]"), 0
    if not sep or not port.isdigit():
        return None
    return host.strip("[]"), int(port)


def parse_netstat(text: str) -> list[tuple]:
    rows = []
    for line in text.splitlines():
        parts = line.split()
        if len(parts) != 5 or parts[0] != "TCP" or not parts[4].isdigit():
            continue
        local, remote = _endpoint(parts[1]), _endpoint(parts[2])
        if local is None or remote is None:
            continue
        state = "LISTEN" if parts[3] == "LISTENING" else parts[3]
        rows.append((local, remote, state, int(parts[4])))
    return rows


def parse_ss(text: str) -> list[tuple]:
    rows = []
    for line in text.splitlines():
        parts = line.split()
        if len(parts) < 5:
            continue
        local, remote = _endpoint(parts[3]), _endpoint(parts[4])
        pid = re.search(r"pid=(\d+)", line)
        if local is None or remote is None or pid is None:
            continue
        state = "LISTEN" if parts[0] == "LISTEN" else parts[0]
        rows.append((local, remote, state, int(pid.group(1))))
    return rows


def binds() -> list[tuple[str, tuple[str, int], int]] | None:
    """Every listening TCP socket and bound UDP socket, as (protocol, local, pid)."""
    try:
        if WINDOWS:
            out = subprocess.run(["netstat", "-ano"], capture_output=True, text=True,
                                 timeout=30).stdout
            return parse_netstat_binds(out)
        done = subprocess.run(["ss", "-tulnpH"], capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.TimeoutExpired):
        return None
    if done.returncode != 0:
        return None
    rows = []
    for line in done.stdout.splitlines():
        parts = line.split()
        pid = re.search(r"pid=(\d+)", line)
        local = _endpoint(parts[4]) if len(parts) > 4 else None
        if pid and local:
            rows.append((parts[0].upper(), local, int(pid.group(1))))
    return rows


def parse_netstat_binds(text: str) -> list[tuple[str, tuple[str, int], int]]:
    rows = []
    for line in text.splitlines():
        parts = line.split()
        if len(parts) == 5 and parts[0] == "TCP" and parts[3] == "LISTENING":
            local, pid = _endpoint(parts[1]), parts[4]
        elif len(parts) == 4 and parts[0] == "UDP":
            local, pid = _endpoint(parts[1]), parts[3]
        else:
            continue
        if local is not None and pid.isdigit():
            rows.append((parts[0], local, int(pid)))
    return rows


def process_table() -> dict[int, tuple[int, int]] | None:
    """pid -> (parent pid, resident bytes), or None when unknowable."""
    try:
        if WINDOWS:
            script = ("Get-CimInstance Win32_Process | ForEach-Object "
                      "{ '{0},{1},{2}' -f $_.ProcessId,$_.ParentProcessId,$_.WorkingSetSize }")
            out = subprocess.run(["powershell", "-NoProfile", "-Command", script],
                                 capture_output=True, text=True, timeout=60).stdout
            sep = ","
        else:
            out = subprocess.run(["ps", "-eo", "pid=,ppid=,rss="], capture_output=True,
                                 text=True, timeout=30).stdout
            sep = None
    except (OSError, subprocess.TimeoutExpired):
        return None
    table = {}
    for line in out.splitlines():
        parts = line.strip().split(sep)
        if len(parts) == 3 and all(p.strip().isdigit() for p in parts):
            pid, parent, size = (int(p) for p in parts)
            table[pid] = (parent, size if WINDOWS else size * 1024)
    return table or None


def descendants(root: int, table: dict[int, tuple[int, int]]) -> set[int]:
    """`root` and every process below it in a (pid -> parent) table."""
    children: dict[int, list[int]] = {}
    for pid, (parent, _size) in table.items():
        if pid != parent:
            children.setdefault(parent, []).append(pid)
    found, frontier = {root}, [root]
    while frontier:
        for child in children.get(frontier.pop(), []):
            if child not in found:
                found.add(child)
                frontier.append(child)
    return found


def bindable(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        try:
            probe.bind(("127.0.0.1", port))
            return True
        except OSError:
            return False


def http_status(url: str, timeout: float = 3.0) -> int | None:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            return response.status
    except urllib.error.HTTPError as exc:
        return exc.code
    except (urllib.error.URLError, OSError, ValueError):
        return None


@dataclass
class Running:
    """One started process and everything observed about it."""

    member: str
    id: str
    argv: list[str]
    cwd: str
    env: dict
    ready_url: str
    log: str
    popen: subprocess.Popen | None = None
    started_at: str = ""
    started: float = 0.0
    ready_seconds: float | None = None
    readiness: str = "unknown"
    readiness_detail: str = ""
    tree: dict[int, int] = field(default_factory=dict)  # pid -> parent
    shutdown: dict = field(default_factory=dict)

    def record(self) -> dict:
        return {"id": self.id, "argv": self.argv, "cwd": self.cwd, "env": self.env,
                "ready_url": self.ready_url, "log": self.log,
                "pid": self.popen.pid if self.popen else None,
                "started_at": self.started_at, "ready_seconds": self.ready_seconds,
                "readiness": self.readiness, "readiness_detail": self.readiness_detail,
                "shutdown": self.shutdown}


def start(process: Running) -> None:
    log = open(process.log, "w", encoding="utf-8", errors="replace")
    flags = subprocess.CREATE_NEW_PROCESS_GROUP if WINDOWS else 0
    process.started_at = now()
    process.started = time.monotonic()
    try:
        process.popen = subprocess.Popen(
            executable(process.argv), cwd=process.cwd, env=child_env(process.env),
            stdout=log, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
            creationflags=flags, start_new_session=not WINDOWS)
    except OSError as exc:
        process.readiness, process.readiness_detail = "fail", f"did not start: {exc}"
    finally:
        log.close()


def wait_ready(process: Running, budget: float) -> None:
    """Poll the readiness URL until it answers 2xx, the process exits, or time runs out.

    Polling a probe rather than sleeping: the time recorded is when the member
    said it was ready, not when a guess elapsed.
    """
    if process.popen is None:
        return
    deadline = process.started + budget
    last = None
    while time.monotonic() < deadline:
        code = process.popen.poll()
        if code is not None:
            process.readiness = "fail"
            process.readiness_detail = f"exited with {code} before answering {process.ready_url}"
            if LOADER_PATH_LIMIT.search(tail(process.log)):
                # The machine, not the member: the log says the loader refused a
                # path. Recorded as unknown, because nothing about the member
                # was observed.
                process.readiness = "unknown"
                process.readiness_detail += (" -- the log shows Windows refusing a native module's "
                                             "path as too long; a shorter --work moves it")
            return
        last = http_status(process.ready_url)
        if last is not None and 200 <= last < 300:
            process.ready_seconds = round(time.monotonic() - process.started, 3)
            process.readiness = "pass"
            return
        time.sleep(0.25)
    process.readiness = "fail"
    process.readiness_detail = (f"no 2xx from {process.ready_url} within {budget:.0f}s "
                                f"(last status {last!r}); slow first start is the other "
                                f"cause, and the log says which")


# What Windows says when a native module's path is past what the loader takes.
LOADER_PATH_LIMIT = re.compile(r"filename or extension is too long|error 0xce", re.IGNORECASE)

# Measured, not documented: a native module at 245 characters loaded and the
# same module at 251 did not, while the file system opened longer paths fine.
# A module past this is a warning, because a member may never import it.
NATIVE_PATH_LIMIT = 250


def tail(path: str, size: int = 8192) -> str:
    try:
        with open(path, "rb") as log:
            log.seek(0, os.SEEK_END)
            log.seek(max(0, log.tell() - size))
            return log.read().decode("utf-8", "replace")
    except OSError:
        return ""


def long_native_paths(root: Path, limit: int = NATIVE_PATH_LIMIT) -> dict:
    """Native modules under `root` whose absolute path is past the loader's limit."""
    over, longest = 0, 0
    for directory, folders, files in os.walk(root):
        if ".git" in folders:
            folders.remove(".git")
        for name in files:
            if name.lower().endswith((".pyd", ".dll", ".node")):
                length = len(os.path.join(directory, name))
                longest = max(longest, length)
                over += length > limit
    return {"limit": limit, "longest": longest, "over_limit": over}


def stop(process: Running, grace: float = 10.0) -> None:
    """Ask the process group to stop, then force it, then sweep what was left.

    Every pid swept is one recorded as this process's descendant while it ran;
    nothing found by port is ever killed, because a port can be held by a
    process this harness did not start.
    """
    popen = process.popen
    if popen is None:
        process.shutdown = {"method": "never started"}
        return
    began = time.monotonic()
    method = "already exited"
    if popen.poll() is None:
        method = "interrupt"
        try:
            if WINDOWS:
                os.kill(popen.pid, signal.CTRL_BREAK_EVENT)
            else:
                os.killpg(popen.pid, signal.SIGTERM)
        except OSError:
            method = "interrupt refused"
        try:
            popen.wait(timeout=grace)
        except subprocess.TimeoutExpired:
            method = "forced"
            if WINDOWS:
                subprocess.run(["taskkill", "/T", "/F", "/PID", str(popen.pid)],
                               capture_output=True)
            else:
                os.killpg(popen.pid, signal.SIGKILL)
            popen.wait(timeout=grace)
    # A descendant can outlive its root for a moment -- a server finishing its
    # own shutdown after the launcher above it has gone. It gets the same grace
    # before anything is forced, and a pid is forced only while its parent is
    # still the one recorded, because a reused pid would have another parent.
    left = survivors(process.tree, popen.pid)
    outlived = list(left) if left is not None else "unknown"
    deadline = time.monotonic() + grace
    while left and time.monotonic() < deadline:
        time.sleep(0.5)
        left = survivors(process.tree, popen.pid)
    forced = []
    for pid in left or []:
        forced.append(pid)
        if WINDOWS:
            subprocess.run(["taskkill", "/T", "/F", "/PID", str(pid)], capture_output=True)
        else:
            try:
                os.kill(pid, signal.SIGKILL)
            except OSError:
                pass
    process.shutdown = {"method": method, "exit_code": popen.returncode,
                        "seconds": round(time.monotonic() - began, 3),
                        "outlived_root": outlived, "descendants_forced": forced}


def survivors(tree: dict[int, int], root: int) -> list[int] | None:
    """Recorded descendants still alive under the parent they were recorded with."""
    table = process_table()
    if table is None:
        return None
    return sorted(pid for pid, parent in tree.items()
                  if pid != root and pid in table and table[pid][0] == parent)


def port_report(ports: list[int]) -> dict[str, dict]:
    """Whether each port is free: nothing listening, and bindable."""
    report = {}
    for port in ports:
        holders = listening(port)
        report[str(port)] = {
            "listeners": sorted(holders) if holders is not None else "unknown",
            "bindable": bindable(port),
            "free": (not holders) if holders is not None else "unknown",
        }
    return report


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# ===================================================================
# MEMBERS -- checkout, install, prepare
# ===================================================================

def git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True,
                          encoding="utf-8", errors="replace")


def resolve_commit(clone: Path, ref: str | None) -> tuple[str, str]:
    """(ref used, full commit) in the roster's clone. Reads only."""
    if ref is None:
        head = git(clone, "symbolic-ref", "--short", "refs/remotes/origin/HEAD")
        if head.returncode != 0:
            raise PlanError(f"{clone.name}: origin/HEAD is unset, so there is no default "
                            f"branch to demo; pass --ref {clone.name}=<ref>")
        ref = head.stdout.strip()
    done = git(clone, "rev-parse", "--verify", f"{ref}^{{commit}}")
    if done.returncode != 0:
        raise PlanError(f"{clone.name}: {ref} is not a commit here: {done.stderr.strip()}")
    return ref, done.stdout.strip()


def checkout(clone: Path, commit: str, into: Path) -> dict:
    """This run's own clone of a member at `commit`.

    `--shared` borrows the source's objects through alternates and writes
    nothing into it, so a commit only a remote-tracking ref reaches is still
    here. Reused across runs when it already sits at the commit.
    """
    if not (into / ".git").exists():
        into.parent.mkdir(parents=True, exist_ok=True)
        cloned = subprocess.run(["git", "clone", "--quiet", "--shared", "--no-checkout",
                                 str(clone), str(into)], capture_output=True, text=True)
        if cloned.returncode != 0:
            raise PlanError(f"clone of {clone.name} failed: {cloned.stderr.strip()}")
    switched = git(into, "-c", "advice.detachedHead=false", "checkout", "--quiet",
                   "--detach", commit)
    if switched.returncode != 0:
        raise PlanError(f"{into.name}: checkout of {commit} failed: {switched.stderr.strip()}")
    head = git(into, "rev-parse", "HEAD").stdout.strip()
    if head != commit:
        raise PlanError(f"{into.name}: HEAD is {head}, wanted {commit}")
    return {"path": str(into), "head": head, "dirty": dirty(into)}


def dirty(repo: Path) -> list[str]:
    return [line for line in git(repo, "status", "--porcelain").stdout.splitlines() if line]


def lock_digest(repo: Path) -> dict[str, str]:
    digests = {}
    for name in ("uv.lock", "package-lock.json", "pdm.lock"):
        path = repo / name
        if path.is_file():
            digests[name] = hashlib.sha256(path.read_bytes()).hexdigest()[:16]
    return digests


def install(member: dict, repo: Path, logs: Path, stamp: Path, fresh: bool) -> dict:
    """Run the member's install commands, once per commit unless `fresh`.

    The stamp is the member's, not the commit's, because the clone is: an
    environment synced for one commit is reused only while the clone is still
    at that commit with the same commands and the same lock files.
    """
    commands = member.get("install") or []
    key = hashlib.sha256(json.dumps([commands, git(repo, "rev-parse", "HEAD").stdout.strip(),
                                     lock_digest(repo)]).encode()).hexdigest()[:16]
    if stamp.is_file() and not fresh:
        previous = json.loads(stamp.read_text(encoding="utf-8"))
        if previous.get("key") == key and previous.get("result") == "pass":
            return {**previous, "reused": True}
    steps, result = [], "pass"
    for argv in commands:
        began = time.monotonic()
        log = logs / f"install-{member['name']}-{len(steps)}.log"
        with open(log, "w", encoding="utf-8", errors="replace") as out:
            done = subprocess.run(executable(argv), cwd=repo, env=child_env(), stdout=out,
                                  stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL)
        steps.append({"argv": argv, "exit_code": done.returncode, "log": str(log),
                      "seconds": round(time.monotonic() - began, 3)})
        if done.returncode != 0:
            result = "fail"
            break
    record = {"key": key, "result": result, "steps": steps, "at": now(), "reused": False}
    stamp.parent.mkdir(parents=True, exist_ok=True)
    stamp.write_text(json.dumps(record, indent=2), encoding="utf-8")
    return record


def prepare_showrunner(state: Path, context: dict) -> dict:
    """A show.toml naming a scratch database, log file and loopback bind."""
    port = context["ports"]["http"]
    (state / "show.toml").write_text(
        "[database]\n"
        f'path = "{(state / "show.db").as_posix()}"\n\n'
        "[server]\n"
        'host = "127.0.0.1"\n'
        f"port = {port}\n\n"
        "[plugins.showlogger]\n"
        'level = "INFO"\n'
        f'file = "{(state / "show.log").as_posix()}"\n',
        encoding="utf-8")
    return {"config": str(state / "show.toml"), "database": str(state / "show.db")}


def prepare_joe(state: Path, context: dict) -> dict:
    """A scratch recording named for the run, and a Vite config aimed at this run's API.

    The config imports the member's own and changes only where its proxies
    point, so `root` and `base` stay the member's. `/v1` is qmcp's queue in the
    member's config; it is pointed at joe's own API here, which answers 404,
    rather than at a qmcp somebody may have running.
    """
    audio = state / "Data" / "Audio"
    audio.mkdir(parents=True, exist_ok=True)
    recording = f"family-demo-{context['token']}.wav"
    (audio / recording).write_bytes(SILENT_WAV)
    api = f"http://127.0.0.1:{context['ports']['api']}"
    # Relative, so Vite's config bundler inlines the member's file. A file URL
    # is left external, and Node then loads the member's ESM config as CommonJS
    # because the member's package.json declares no module type.
    target = Path(context["checkout"]) / "vite.config.js"
    try:
        member_config = Path(os.path.relpath(target, state)).as_posix()
    except ValueError:  # another drive: no relative path exists, so the absolute one
        member_config = target.as_posix()
    (state / "vite.config.mjs").write_text(
        f"import member from {json.dumps(member_config)}\n"
        "export default {\n"
        "  ...member,\n"
        "  server: {\n"
        "    ...member.server,\n"
        f"    proxy: {{ '/api': {json.dumps(api)}, '/v1': {json.dumps(api)} }},\n"
        "  },\n"
        "}\n", encoding="utf-8")
    return {"recording": recording, "vite_config": str(state / "vite.config.mjs"), "api": api}


PREPARE = {
    "showrunner-config": prepare_showrunner,
    "joe-scratch": prepare_joe,
}


def check_params(entry: dict, context: dict, prepared: dict) -> dict:
    """What a check needs beyond its URL: what preparation made, and what it declares."""
    return {**prepared, **expand(entry.get("params") or {}, context)}


# ===================================================================
# PROBES -- run under their own interpreters
# ===================================================================

def probe_names() -> dict[str, set[str]]:
    """The check names the probe module declares, read from its source.

    Read, not imported: the probe module is written to run under other
    interpreters, and importing it here would be a third.
    """
    text = PROBES.read_text(encoding="utf-8")
    names = {}
    for runner, table in (("browser", "BROWSER"), ("terminal", "TERMINAL")):
        block = re.search(rf"^{table} = \{{(.*?)^\}}", text, re.MULTILINE | re.DOTALL)
        names[runner] = set(re.findall(r'"([a-z0-9-]+)":', block.group(1))) if block else set()
    return names


def run_probe(runner: str, checks: list[dict], where: Path, plan: dict,
              checkout: Path | None = None) -> list[dict]:
    if not checks:
        return []
    where.mkdir(parents=True, exist_ok=True)
    stem = f"{runner}-{checks[0]['member'] if runner == 'terminal' else 'all'}"
    job_path, out_path = where / f"{stem}-job.json", where / f"{stem}-results.json"
    job_path.write_text(json.dumps({"checks": checks, "out": str(out_path)}, indent=2),
                        encoding="utf-8")
    if runner == "browser":
        pin = plan.get("browser") or {}
        argv = ["uv", "run", "--no-project", "--python", str(pin.get("python", "3.12")),
                "--with", f"playwright=={pin.get('playwright')}", "python"]
        cwd = where
    else:
        argv = ["uv", "run", "--no-sync", "--project", str(checkout), "python"]
        cwd = checkout
    argv += [str(PROBES), runner, str(job_path)]
    log = where / f"{stem}.log"
    with open(log, "w", encoding="utf-8", errors="replace") as out:
        done = subprocess.run(executable(argv), cwd=cwd, env=child_env(), stdout=out,
                              stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, timeout=900)
    if done.returncode != 0 or not out_path.is_file():
        why = f"the {runner} probe exited {done.returncode}; see {log}"
        return [{"member": c["member"], "check": c["name"], "runner": runner,
                 "counts": c.get("counts"), "result": "unknown", "detail": why,
                 "evidence": {}, "shot": None, "console_errors": [], "seconds": 0.0}
                for c in checks]
    results = json.loads(out_path.read_text(encoding="utf-8"))
    for result in results:
        result["probe_argv"] = argv
    return results


# ===================================================================
# A WAVE
# ===================================================================

@dataclass
class Stage:
    """One member in one wave: its processes, checks and results."""

    member: dict
    context: dict
    state: Path
    processes: list[Running] = field(default_factory=list)
    prepared: dict = field(default_factory=dict)
    identity: dict = field(default_factory=dict)
    memory: int | str = "unknown"
    checks: list[dict] = field(default_factory=list)
    readiness: str = "unknown"
    blocked: str = ""

    @property
    def name(self) -> str:
        return self.member["name"]

    def record(self) -> dict:
        return {
            "ports": self.context["ports"],
            "state": str(self.state),
            "prepared": self.prepared,
            "blocked": self.blocked,
            "readiness": self.readiness,
            "ready_seconds": member_ready_seconds(self.processes),
            "processes": [p.record() for p in self.processes],
            "listener_identity": self.identity,
            "memory_bytes_at_check": self.memory,
            "checks": self.checks,
            "result": member_result(self.checks, self.readiness),
        }


def member_ready_seconds(processes: list[Running]):
    """From the member's first process starting to its last one answering.

    Each process is timed from its own start, and a member whose second
    process starts only once its first answers would otherwise report the
    slower half of its own start-up.
    """
    if not processes or any(p.ready_seconds is None for p in processes):
        return "unknown"
    began = min(p.started for p in processes)
    return round(max(p.started + p.ready_seconds for p in processes) - began, 3)


def stage(member: dict, members: dict, wave: str, run: Path, token: str) -> Stage:
    state = run / "state" / wave / member["name"]
    state.mkdir(parents=True, exist_ok=True)
    context = {"ports": dict(member.get("ports") or {}), "token": token,
               "checkout": (members[member["name"]].get("checkout") or {}).get("path", ""),
               "state": state.as_posix()}
    built = Stage(member=member, context=context, state=state)
    for process in member.get("processes") or []:
        built.processes.append(Running(
            member=member["name"], id=process["id"],
            argv=expand(process["command"], context),
            cwd=context["checkout"] if process["cwd"] == "checkout" else str(state),
            env=expand(process.get("env") or {}, context),
            ready_url=expand(process["ready"], context),
            log=str(run / "logs" / f"{wave}-{member['name']}-{process['id']}.log")))
    return built


def bring_up(built: Stage, budget: float, members: dict) -> None:
    """Prepare, start and wait for one member; records why when it cannot."""
    if members[built.name].get("install", {}).get("result") != "pass":
        built.blocked = "install did not pass"
        return
    busy = {port: sorted(holders) for port in built.context["ports"].values()
            if (holders := listening(port))}
    if busy:
        built.blocked = (f"reserved port held by a process this run did not start: {busy}; "
                         f"nothing was killed")
        return
    preparation = built.member.get("prepare")
    if preparation:
        built.prepared = PREPARE[preparation](built.state, built.context)
    for process in built.processes:
        start(process)
        wait_ready(process, budget)
        if process.readiness != "pass":
            break
    states = [p.readiness for p in built.processes]
    built.readiness = "pass" if states and all(s == "pass" for s in states) else (
        "fail" if "fail" in states else "unknown")


def observe(built: Stage, table: dict | None) -> None:
    """Who is listening on the member's ports, and is it this run's process tree."""
    if table is None:
        built.identity = {"verdict": "unknown", "why": "no process table"}
        return
    ours: set[int] = set()
    for process in built.processes:
        if process.popen is not None:
            process.tree = {pid: table[pid][0] if pid in table else -1
                            for pid in descendants(process.popen.pid, table)}
            ours |= set(process.tree)
    holders = {str(port): sorted(listening(port) or []) for port in built.context["ports"].values()}
    foreign = {port: [pid for pid in pids if pid not in ours] for port, pids in holders.items()}
    foreign = {port: pids for port, pids in foreign.items() if pids}
    built.identity = {"listeners": holders, "foreign": foreign,
                      "verdict": "ours" if not foreign and all(holders.values()) else
                      ("foreign" if foreign else "unknown")}
    # Everything the member's processes hold open, not only what it was asked
    # to serve: a bind outside the reserved ports is a hazard the plan stops on.
    held = binds()
    reserved = set(built.context["ports"].values())
    if held is None or not ours:
        built.identity["binds"] = built.identity["unreserved_binds"] = "unknown"
    else:
        built.identity["binds"] = sorted({f"{proto} {host}:{port}"
                                          for proto, (host, port), pid in held if pid in ours})
        built.identity["unreserved_binds"] = sorted(
            {f"{proto} {host}:{port}" for proto, (host, port), pid in held
             if pid in ours and port not in reserved})
    built.memory = sum(table[pid][1] for pid in ours if pid in table) if ours else "unknown"


def checks_for(built: Stage, runner: str, shots: Path, wave: str) -> list[dict]:
    entries = []
    for entry in built.member.get("checks") or []:
        if entry["runner"] != runner:
            continue
        params = check_params(entry, built.context, built.prepared)
        suffix = ".svg" if runner == "terminal" else ".png"
        entries.append({
            "member": built.name, "name": entry["name"], "counts": entry["counts"],
            "base": expand(built.member.get("surface", ""), built.context),
            "token": built.context["token"], "params": params,
            "checkout": built.context["checkout"],
            "shot": str(shots / f"{wave}-{built.name}-{entry['name']}{suffix}")})
    return entries


def assert_all(stages: list[Stage], run: Path, plan: dict, wave: str) -> None:
    """Run every ready member's checks: one browser for all, a terminal per member."""
    ready = [s for s in stages if s.readiness == "pass"]
    table = process_table()
    for built in stages:
        observe(built, table)
    shots, probes = run / "shots", run / "probes" / wave
    browser = [c for s in ready if s.identity.get("verdict") != "foreign"
               for c in checks_for(s, "browser", shots, wave)]
    results = run_probe("browser", browser, probes, plan)
    for built in ready:
        if built.identity.get("verdict") == "foreign":
            built.checks = [{"member": built.name, "check": e["name"], "counts": e["counts"],
                             "result": "unknown", "detail": "a process this run did not "
                             "start holds one of the member's ports", "shot": None}
                            for e in built.member.get("checks") or []]
            continue
        terminal = run_probe("terminal", checks_for(built, "terminal", shots, wave), probes,
                             plan, Path(built.context["checkout"]))
        built.checks = [r for r in results if r["member"] == built.name] + terminal
    for built in stages:
        if built.readiness != "pass" and not built.checks:
            why = built.blocked or "not ready, so no check ran"
            built.checks = [{"member": built.name, "check": e["name"], "counts": e["counts"],
                             "result": "unknown", "detail": why, "shot": None}
                            for e in built.member.get("checks") or []]


def take_down(stages: list[Stage]) -> dict:
    for built in reversed(stages):
        for process in reversed(built.processes):
            stop(process)
    ports = [p for s in stages for p in s.context["ports"].values()]
    return port_report(ports)


def wave_zero(order: list[dict], members: dict, run: Path, token: str, plan: dict,
              budget: float) -> dict:
    records = {}
    for member in order:
        built = stage(member, members, "wave0", run, token)
        print(f"  wave 0  {member['name']:<12} starting", flush=True)
        try:
            bring_up(built, budget, members)
            assert_all([built], run, plan, "wave0")
        finally:
            ports = take_down([built])
        record = built.record()
        record["ports_after"] = ports
        records[member["name"]] = record
        print(f"  wave 0  {member['name']:<12} {record['result']:<8} "
              f"ready {seconds(record['ready_seconds'])}  {summary(record)}", flush=True)
    return records


def together(order: list[dict], members: dict, run: Path, token: str, plan: dict,
             budget: float, simultaneous: bool, hold: float | None,
             finish) -> dict:
    stages = [stage(m, members, "together", run, token) for m in order]
    seams_live: dict = {}
    landing: dict = {}
    try:
        if simultaneous:
            _simultaneous(stages, budget, members)
        else:
            for built in stages:
                print(f"  together {built.name:<11} starting", flush=True)
                bring_up(built, budget, members)
        before = live_connections(stages)
        assert_all(stages, run, plan, "together")
        seams_live = merge_samples([before, live_connections(stages)])
        landing = finish(stages, seams_live)
        if hold is not None:
            hold_open(run, hold)
    finally:
        ports = take_down(stages)
    records = {}
    for built in stages:
        records[built.name] = built.record()
        print(f"  together {built.name:<11} {records[built.name]['result']:<8} "
              f"ready {seconds(records[built.name]['ready_seconds'])}  "
              f"{summary(records[built.name])}", flush=True)
    return {"start": "simultaneous" if simultaneous else "staggered", "members": records,
            "ports_after": ports, "live_connections": seams_live, "landing": landing}


def _simultaneous(stages: list[Stage], budget: float, members: dict) -> None:
    """Start every member's first process at once, then each remaining process in turn."""
    firsts = []
    for built in stages:
        if members[built.name].get("install", {}).get("result") != "pass":
            built.blocked = "install did not pass"
            continue
        busy = {p for p in built.context["ports"].values() if listening(p)}
        if busy:
            built.blocked = f"reserved port held by a process this run did not start: {sorted(busy)}"
            continue
        if built.member.get("prepare"):
            built.prepared = PREPARE[built.member["prepare"]](built.state, built.context)
        start(built.processes[0])
        firsts.append(built)
    def finish(built: Stage) -> None:
        wait_ready(built.processes[0], budget)
        for process in built.processes[1:]:
            if built.processes[0].readiness == "pass":
                start(process)
                wait_ready(process, budget)
        states = [p.readiness for p in built.processes]
        built.readiness = "pass" if all(s == "pass" for s in states) else (
            "fail" if "fail" in states else "unknown")

    # Waited on together, so a member's ready time is its own and not the time
    # the harness got round to asking it after the members before it answered.
    with ThreadPoolExecutor(max_workers=max(1, len(firsts))) as pool:
        list(pool.map(finish, firsts))


def hold_open(run: Path, seconds: float) -> None:
    page = run / "index.html"
    if seconds <= 0:
        print(f"\nholding every member up; open {page.as_uri()}\nCtrl+C stops them.", flush=True)
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("stopping", flush=True)
    else:
        print(f"\nholding every member up for {seconds:.0f}s; open {page.as_uri()}", flush=True)
        time.sleep(seconds)


def seconds(value) -> str:
    return f"{value}s" if isinstance(value, (int, float)) else str(value)


def summary(record: dict) -> str:
    if record.get("blocked"):
        return record["blocked"]
    parts = []
    for entry in record.get("checks") or []:
        detail = f" -- {entry['detail']}" if entry.get("detail") else ""
        parts.append(f"{entry['check']}={entry['result']}{detail}")
    for process in record.get("processes") or []:
        if process["readiness"] != "pass" and process["readiness_detail"]:
            parts.append(f"{process['id']}: {process['readiness_detail']}")
    return "; ".join(parts)


# ===================================================================
# SEAMS -- named in source, and held open at runtime
# ===================================================================

def named_in_source(members: dict, names: list[str]) -> list[dict]:
    """Which member's tracked files name another member, by word, ignoring case.

    A name is not a wire. This is reported so a reader can see where a seam is
    *claimed*; nothing here says one works.
    """
    found = []
    for source in names:
        repo = Path(members[source]["checkout"]["path"])
        for target in names:
            if target == source:
                continue
            done = git(repo, "grep", "-I", "-l", "-i", "-w", "-e", target, "--",
                       ".", ":(exclude)*.lock", ":(exclude)package-lock.json")
            files = [f for f in done.stdout.splitlines() if f]
            if files:
                found.append({"from": source, "names": target, "files": files[:12],
                              "file_count": len(files)})
    return found


def live_connections(stages: list[Stage]) -> dict:
    """Connections a member's process holds to another member's port, right now."""
    table, procs = connections(), process_table()
    if table is None or procs is None:
        return {"observed": "unknown", "why": "no connection or process table", "pairs": []}
    owner_of_port = {port: s.name for s in stages for port in s.context["ports"].values()}
    tree = {}
    for built in stages:
        for process in built.processes:
            if process.popen is not None:
                for pid in descendants(process.popen.pid, procs):
                    tree[pid] = built.name
    pairs = {}
    for _local, remote, state, pid in table:
        if state != "ESTABLISHED" or pid not in tree:
            continue
        target = owner_of_port.get(remote[1])
        if target and target != tree[pid]:
            key = f"{tree[pid]} -> {target}"
            pairs[key] = pairs.get(key, 0) + 1
    return {"observed": "sampled", "at": now(), "pairs": pairs,
            "blind_to": "requests that open and close between samples, and UDP"}


def merge_samples(samples: list[dict]) -> dict:
    """Several connection samples as one reading; unknown if any could not be taken."""
    if any(sample.get("observed") != "sampled" for sample in samples):
        return {"observed": "unknown", "why": "a sample could not be taken",
                "samples": samples, "pairs": {}}
    pairs: dict[str, int] = {}
    for sample in samples:
        for key, count in sample["pairs"].items():
            pairs[key] = pairs.get(key, 0) + count
    return {"observed": "sampled", "samples": len(samples),
            "at": [sample["at"] for sample in samples], "pairs": pairs,
            "blind_to": samples[0]["blind_to"]}


# ===================================================================
# THE PAGE AND THE MANIFEST
# ===================================================================

STYLE = """
:root{--bg:#fbfbf9;--fg:#1d1d1b;--muted:#6b6b66;--line:#deded8;--pass:#1f7a3a;
--fail:#b3261e;--unknown:#8a6d00;--card:#fff}
@media (prefers-color-scheme:dark){:root{--bg:#161615;--fg:#ececea;--muted:#a3a39d;
--line:#33332f;--pass:#5fc77f;--fail:#ff8a80;--unknown:#e2c25b;--card:#1f1f1d}}
body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.5 system-ui,sans-serif}
main{max-width:1100px;margin:0 auto;padding:24px 16px}
h1{font-size:1.6rem;margin:0 0 4px}h2{font-size:1.15rem;margin:32px 0 8px}
.lede{color:var(--muted);margin:0 0 16px}
table{border-collapse:collapse;width:100%;font-size:.9rem}
th,td{border-bottom:1px solid var(--line);padding:6px 8px;text-align:left;vertical-align:top}
code{font-size:.85em}
.pass{color:var(--pass);font-weight:600}.fail{color:var(--fail);font-weight:600}
.unknown{color:var(--unknown);font-weight:600}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:16px}
.card{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:12px}
.card img{width:100%;border:1px solid var(--line);border-radius:4px;background:#000}
.card h3{margin:0 0 4px;font-size:1rem}.live{font-size:.8rem;color:var(--muted)}
.wrap{overflow-x:auto}
"""

LIVE = """
document.querySelectorAll('[data-live]').forEach(el => {
  fetch(el.dataset.live, {mode: 'no-cors'})
    .then(() => { el.textContent = 'answering now'; })
    .catch(() => { el.textContent = 'not answering now'; });
});
"""


def result_span(result: str) -> str:
    return f'<span class="{html.escape(result)}">{html.escape(result)}</span>'


def landing_page(manifest: dict, run: Path) -> str:
    """The demo as a page: every surface, every picture, every unknown."""
    e = html.escape
    rows, cards = [], []
    together_members = (manifest.get("together") or {}).get("members") or {}
    wave0 = manifest.get("wave0") or {}
    for name, member in manifest["members"].items():
        if not member.get("runs"):
            continue
        commit = member.get("commit", "")[:12]
        ports = ", ".join(f"{k} {v}" for k, v in member["ports"].items())
        w0 = wave0.get(name, {})
        tg = together_members.get(name, {})
        surface = member.get("surface", "")
        rows.append(
            f'<tr data-member="{e(name)}"><td><strong>{e(name)}</strong><br>'
            f'<span class="live">{e(member.get("family") or "unstated")}</span></td>'
            f'<td><code>{e(member.get("ref", ""))}</code><br><code>{e(commit)}</code></td>'
            f'<td>{e(ports)}</td>'
            f'<td>{result_span(w0.get("result", "unknown")) if w0 else "not run"}'
            f'<br><span class="live">ready {e(str(w0.get("ready_seconds", "")))}s</span></td>'
            f'<td>{result_span(tg.get("result", "unknown")) if tg else "not run"}'
            f'<br><span class="live">ready {e(str(tg.get("ready_seconds", "")))}s</span></td>'
            f'<td><a href="{e(surface)}">{e(surface)}</a><br>'
            f'<span class="live" data-live="{e(member.get("live_probe", ""))}">'
            f'not checked</span></td></tr>')
        source = tg or w0
        for entry in source.get("checks") or []:
            shot = entry.get("shot")
            picture = (f'<img alt="{e(name)}: {e(entry["check"])}" '
                       f'src="{e(Path(os.path.relpath(shot, run)).as_posix())}">'
                       if shot and Path(shot).is_file() else "<p>no picture was recorded</p>")
            detail = f"<p>{e(entry['detail'])}</p>" if entry.get("detail") else ""
            cards.append(
                f'<div class="card"><h3>{e(name)}</h3>'
                f'<p><code>{e(entry["check"])}</code> {result_span(entry["result"])} '
                f'<span class="live">({e(entry.get("counts", ""))})</span></p>{detail}{picture}</div>')

    later = "".join(
        f'<tr><td>{e(name)}</td><td>{e(m["phase"])}</td>'
        f'<td>{e(", ".join(str(p) for p in m["ports"].values()))}</td>'
        f'<td>{"<br>".join(e(n) for n in m.get("needs") or [])}</td></tr>'
        for name, m in manifest["members"].items() if not m.get("runs"))
    seams = manifest.get("seams") or {}
    named = "".join(
        f'<tr><td>{e(s["from"])}</td><td>{e(s["names"])}</td><td>{s["file_count"]}</td>'
        f'<td><code>{e(", ".join(s["files"][:4]))}</code></td></tr>'
        for s in seams.get("named_in_source") or []) or '<tr><td colspan="4">none</td></tr>'
    live = (manifest.get("together") or {}).get("live_connections") or {}
    live_pairs = "".join(f"<li>{e(k)}: {v}</li>" for k, v in (live.get("pairs") or {}).items())
    live_text = (f"<ul>{live_pairs}</ul>" if live_pairs else
                 f"<p>None observed ({e(str(live.get('observed', 'not sampled')))} "
                 f"{e(str(live.get('samples', '')))} times, before and after the checks; "
                 f"blind to {e(str(live.get('blind_to', '')))}).</p>")
    unknowns = "".join(f"<li>{e(u)}</li>" for u in manifest.get("unknowns") or []) or "<li>none</li>"
    hazards = "".join(f"<li>{e(h)}</li>" for h in manifest.get("hazards") or []) or "<li>none</li>"
    unplaced_text = ", ".join(manifest.get("unplaced") or []) or "none"
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Performing family demo</title><style>{STYLE}</style></head>
<body><main>
<h1>Performing family demo</h1>
<p class="lede">Run <code>{e(manifest["run"])}</code>, corpus commit
<code>{e(manifest["corpus"]["commit"][:12])}</code>, {e(manifest["started_at"])}.
Live links answer only while the run is held open; the pictures are what each
check ran against. Overall: {result_span(manifest["overall"]) if manifest.get("overall")
else "not decided while the members are still up"}.</p>

<h2>Members that ran</h2>
<div class="wrap"><table>
<tr><th>Member</th><th>Ref and commit</th><th>Ports</th><th>Alone</th><th>Together</th><th>Surface</th></tr>
{"".join(rows)}
</table></div>

<h2>What each check saw</h2>
<div class="cards">{"".join(cards)}</div>

<h2>Seams</h2>
<p>Running together here is process simultaneity: the members share a machine,
not a protocol. No check exercises a seam between two members.</p>
<h3>Named in another member's tracked source</h3>
<p>A whole-word match on the member's name, ignoring case. It finds a claimed
seam and a person called Joe alike, so read the files; a name is not a wire.</p>
<div class="wrap"><table><tr><th>In</th><th>Names</th><th>Files</th><th>Some of them</th></tr>
{named}</table></div>
<h3>Connections between members while all were up</h3>
{live_text}

<h2>Declared, not run yet</h2>
<div class="wrap"><table><tr><th>Member</th><th>Phase</th><th>Reserved</th><th>Needs before joining</th></tr>
{later}</table></div>
<p>Performing-family members the demo roster does not place: {e(unplaced_text)}.</p>

<h2>Hazards observed</h2><ul>{hazards}</ul>
<h2>Unknowns</h2><ul>{unknowns}</ul>
<p class="live">Full record: <a href="manifest.json">manifest.json</a>.</p>
</main><script>{LIVE}</script></body></html>
"""


def missing_artifacts(manifest: dict, run: Path) -> list[str]:
    """Every artifact the manifest names that is not on disk, or is empty."""
    named = [run / "index.html", run / "manifest.json"]
    for wave in ("wave0",):
        for record in (manifest.get(wave) or {}).values():
            named += [Path(c["shot"]) for c in record.get("checks") or [] if c.get("shot")]
    for record in ((manifest.get("together") or {}).get("members") or {}).values():
        named += [Path(c["shot"]) for c in record.get("checks") or [] if c.get("shot")]
    landing = (manifest.get("together") or {}).get("landing") or {}
    if landing.get("shot"):
        named.append(Path(landing["shot"]))
    return [str(p) for p in named if not p.is_file() or p.stat().st_size == 0]


def collect_hazards(manifest: dict) -> list[str]:
    """What the plan says to stop on or watch for, as observed in this run."""
    found = []
    waves = (("alone", manifest.get("wave0") or {}),
             ("together", (manifest.get("together") or {}).get("members") or {}))
    for wave, records in waves:
        for name, record in records.items():
            identity = record.get("listener_identity") or {}
            loose = identity.get("unreserved_binds")
            if isinstance(loose, list) and loose:
                found.append(f"{name} {wave}: holds sockets outside its reserved ports: "
                             f"{', '.join(loose)}")
            if identity.get("foreign"):
                found.append(f"{name} {wave}: a process this run did not start holds "
                             f"{identity['foreign']}")
            for process in record.get("processes") or []:
                forced = (process.get("shutdown") or {}).get("descendants_forced")
                if forced:
                    found.append(f"{name} {wave}: {process['id']} left processes that had "
                                 f"to be forced: {forced}")
            for port, state in (record.get("ports_after") or {}).items():
                if state.get("free") is not True:
                    found.append(f"{name} {wave}: port {port} not free after shutdown")
    for port, state in ((manifest.get("together") or {}).get("ports_after") or {}).items():
        if state.get("free") is not True:
            found.append(f"together: port {port} not free after shutdown")
    for name, member in (manifest.get("members") or {}).items():
        native = (member.get("checkout") or {}).get("native_paths") or {}
        if native.get("over_limit"):
            found.append(f"{name}: {native['over_limit']} native module(s) past the loader's "
                         f"path limit in this work directory (longest {native['longest']})")
    return found


def collect_unknowns(manifest: dict) -> list[str]:
    found = []
    for wave, records in (("alone", manifest.get("wave0") or {}),
                          ("together", (manifest.get("together") or {}).get("members") or {})):
        for name, record in records.items():
            for entry in record.get("checks") or []:
                if entry["result"] == "unknown":
                    found.append(f"{name} {wave}: {entry['check']} -- {entry.get('detail', '')}")
            if record.get("listener_identity", {}).get("verdict") == "unknown":
                found.append(f"{name} {wave}: listener identity not established")
            if record.get("memory_bytes_at_check") == "unknown":
                found.append(f"{name} {wave}: memory not sampled")
    for name, member in manifest["members"].items():
        if not member.get("runs"):
            found.append(f"{name}: not run in this phase ({member['phase']})")
        elif member.get("ref_overridden"):
            # The checks are written against the default branch's surface. On
            # another ref a missing element is as likely the check's as the
            # member's, so a failure there is not evidence about that ref.
            found.append(f"{name}: run at {member.get('ref')} rather than its default "
                         f"branch; its checks were written for the default branch's surface")
    if (manifest.get("together") or {}).get("live_connections", {}).get("observed") == "unknown":
        found.append("cross-member connections: not observable on this machine")
    return found


def environment() -> dict:
    def version(argv: list[str]) -> str:
        try:
            done = subprocess.run(executable(argv), capture_output=True, text=True, timeout=30)
            return (done.stdout or done.stderr).strip().splitlines()[0]
        except (OSError, IndexError, subprocess.TimeoutExpired):
            return "unknown"
    return {"os": platform.platform(), "python": platform.python_version(),
            "uv": version(["uv", "--version"]), "node": version(["node", "--version"]),
            "npm": version(["npm", "--version"]), "git": version(["git", "--version"])}


def default_search_roots() -> list[Path]:
    """Where the roster's clone paths are relative to.

    Two directories above the corpus clone, as `qm estate` assumes -- but found
    through git's common directory, because a worktree of this corpus sits
    wherever the worktree was made and its parents hold none of the clones.
    """
    done = git(CORPUS, "rev-parse", "--path-format=absolute", "--git-common-dir")
    if done.returncode == 0 and done.stdout.strip():
        main_clone = Path(done.stdout.strip()).parent
        return [main_clone.parent.parent]
    return [CORPUS.parent.parent]


# ===================================================================
# MAIN
# ===================================================================

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="qm family-demo",
        description="Bring the performing family up on reserved ports, alone and "
                    "together, and record what each member did.")
    parser.add_argument("--plan-file", type=Path, default=PLAN)
    parser.add_argument("--wave", choices=("0", "together", "all"), default="all")
    parser.add_argument("--phase", action="append", default=[],
                        help="run only this phase (repeatable); default every phase that runs")
    parser.add_argument("--member", action="append", default=[],
                        help="run only this member (repeatable); the rest are reported as not run")
    parser.add_argument("--ref", action="append", default=[], metavar="MEMBER=REF",
                        help="check a member out at this ref instead of origin/HEAD")
    parser.add_argument("--work", type=Path,
                        default=Path(tempfile.gettempdir()) / "qm-family-demo",
                        help="where clones, installs and runs go; never this repository")
    parser.add_argument("--search-root", action="append", type=Path, default=[])
    parser.add_argument("--start", choices=("staggered", "simultaneous"), default="staggered")
    parser.add_argument("--ready-budget", type=float, default=120.0,
                        help="seconds a member may take to answer its readiness probe")
    parser.add_argument("--hold", nargs="?", type=float, const=0.0, default=None,
                        metavar="SECONDS",
                        help="keep the together wave up (until Ctrl+C, or for SECONDS)")
    parser.add_argument("--fresh-install", action="store_true",
                        help="reinstall even when this commit was installed before")
    parser.add_argument("--plan", action="store_true", dest="dry",
                        help="print what would run and check the roster; start nothing")
    args = parser.parse_args(argv)

    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    try:
        plan = load_plan(args.plan_file)
        rostered_entries = corpus_roster.load()
        rostered = {e["name"]: e for e in rostered_entries}
        problems = check_plan(plan, set(rostered), probe_names())
        refs = parse_refs(args.ref)
    except (OSError, yaml.YAMLError, PlanError) as exc:
        print(f"family-demo: {exc}", file=sys.stderr)
        return 2
    if problems:
        print("family-demo: the demo roster cannot run as written:", file=sys.stderr)
        for problem in problems:
            print(f"  - {problem}", file=sys.stderr)
        return 2

    families = json.loads(FAMILIES.read_text(encoding="utf-8")) if FAMILIES.is_file() else {}
    family_of = {n: f["name"] for f in families.get("families") or [] for n in f.get("members") or []}
    order = [m for m in running(plan, args.phase or None)
             if not args.member or m["name"] in args.member]
    unknown_members = set(args.member) - {m["name"] for m in plan["members"]}
    if unknown_members:
        print(f"family-demo: no member is named {sorted(unknown_members)}", file=sys.stderr)
        return 2
    unknown_phases = set(args.phase) - {p["id"] for p in plan["phases"]}
    if unknown_phases:
        print(f"family-demo: no phase is named {sorted(unknown_phases)}", file=sys.stderr)
        return 2
    search_roots = [p.resolve() for p in args.search_root] or default_search_roots()
    lonely = unplaced(plan, families)

    print(f"family-demo: {len(order)} member(s) run; search root "
          f"{', '.join(str(r) for r in search_roots)}")
    for member in plan["members"]:
        runs = member in order
        ports = ", ".join(f"{k}={v}" for k, v in member["ports"].items())
        print(f"  {'run ' if runs else 'later'} {member['name']:<18} {member['phase']:<22} {ports}")
    if lonely:
        print(f"  unplaced performing-family members: {', '.join(lonely)}")
    if args.dry:
        return 0

    work = args.work.resolve()
    if CORPUS in (work, *work.parents):
        print("family-demo: --work is inside this repository; runs belong elsewhere",
              file=sys.stderr)
        return 2
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    token = f"{stamp.lower()}-{os.getpid()}"
    run = work / "runs" / stamp
    for sub in ("logs", "shots", "state", "probes"):
        (run / sub).mkdir(parents=True, exist_ok=True)

    corpus_commit = git(CORPUS, "rev-parse", "HEAD").stdout.strip()
    manifest: dict = {
        "schema": 1, "run": stamp, "token": token, "started_at": now(),
        "corpus": {"commit": corpus_commit, "dirty": dirty(CORPUS),
                   "plan": str(args.plan_file.relative_to(CORPUS)) if
                   CORPUS in args.plan_file.resolve().parents else str(args.plan_file),
                   "plan_sha256": hashlib.sha256(args.plan_file.read_bytes()).hexdigest()[:16]},
        "environment": environment(), "work": str(work), "port_range": plan["ports"],
        "search_roots": [str(r) for r in search_roots], "unplaced": lonely, "members": {},
        "reading": {
            "results": "pass, fail or unknown; unknown is never folded into fail",
            "together": "process simultaneity only -- no check exercises a seam between members",
            "ready_seconds": "process start to the first 2xx from its readiness URL",
        },
    }

    members: dict = {}
    for member in plan["members"]:
        name = member["name"]
        record = {"phase": member["phase"], "family": family_of.get(name),
                  "ports": member["ports"], "runs": member in order}
        if member in order:
            bare = {"ports": member["ports"], "token": token, "checkout": "", "state": ""}
            record.update(documented=member.get("documented"),
                          deviations=member.get("deviations") or [],
                          surface=expand(member.get("surface", ""), bare),
                          # The page's live badge asks this, not the surface:
                          # fetching a surface opens a page session the badge
                          # then abandons, which is load the demo did not mean
                          # to add. The readiness URL is the cheapest answer.
                          live_probe=expand(member["processes"][-1]["ready"], bare))
            clone = resolve(rostered[name], search_roots)
            if clone is None:
                record["install"] = {"result": "unknown",
                                     "why": f"no clone at {rostered[name].get('paths')}"}
            else:
                try:
                    ref, commit = resolve_commit(clone, refs.get(name))
                    # One clone per member, moved to each run's commit: a
                    # directory named for the commit cost characters Windows'
                    # native-module path limit does not have to spare.
                    into = work / "checkouts" / name
                    print(f"  checkout {name:<12} {ref} {commit[:12]}", flush=True)
                    record.update(source_clone=str(clone), ref=ref, commit=commit,
                                  ref_overridden=name in refs,
                                  checkout=checkout(clone, commit, into))
                    record["locks"] = lock_digest(into)
                    print(f"  install  {name:<12}", end=" ", flush=True)
                    record["install"] = install(member, into, run / "logs",
                                                work / "installed" / f"{name}.json",
                                                args.fresh_install)
                    record["checkout"]["dirty_after_install"] = dirty(into)
                    if WINDOWS:
                        record["checkout"]["native_paths"] = long_native_paths(into)
                    print(record["install"]["result"]
                          + (" (reused)" if record["install"].get("reused") else ""), flush=True)
                    native = record["checkout"].get("native_paths") or {}
                    if native.get("over_limit"):
                        print(f"           {native['over_limit']} native module(s) past the "
                              f"loader's path limit (longest {native['longest']}); a member "
                              f"importing one fails to start -- a shorter --work avoids it",
                              flush=True)
                except PlanError as exc:
                    record["install"] = {"result": "unknown", "why": str(exc)}
                    print(f"  {name}: {exc}", flush=True)
        else:
            record["needs"] = member.get("needs") or []
        members[name] = record
    manifest["members"] = members

    started = [m for m in order if members[m["name"]].get("install", {}).get("result") == "pass"]
    if args.wave in ("0", "all"):
        print("wave 0: each member alone", flush=True)
        manifest["wave0"] = wave_zero(order, members, run, token, plan, args.ready_budget)

    def finish(stages: list[Stage], live: dict) -> dict:
        """Write the page while everything is up, and check it in a browser."""
        manifest["together"] = {"members": {s.name: s.record() for s in stages},
                                "live_connections": live}
        manifest["seams"] = {"named_in_source": named_in_source(
            members, [m["name"] for m in started])}
        manifest["unknowns"] = collect_unknowns(manifest)
        manifest["hazards"] = collect_hazards(manifest)
        (run / "index.html").write_text(landing_page(manifest, run), encoding="utf-8")
        result = run_probe("browser", [{
            "member": "landing", "name": "landing-page-shows-every-member",
            "counts": "behaviour", "base": (run / "index.html").as_uri(), "token": token,
            "params": {"members": [m["name"] for m in order]},
            "shot": str(run / "shots" / "landing.png")}], run / "probes" / "landing", plan)
        return result[0] if result else {}

    if args.wave in ("together", "all"):
        print(f"together: every member up, {args.start} start", flush=True)
        manifest["together"] = together(order, members, run, token, plan, args.ready_budget,
                                        args.start == "simultaneous", args.hold, finish)
    manifest.setdefault("seams", {"named_in_source": named_in_source(
        members, [m["name"] for m in started])})

    wave_results = [r["result"] for r in (manifest.get("wave0") or {}).values()]
    wave_results += [r["result"] for r in
                     ((manifest.get("together") or {}).get("members") or {}).values()]
    wave_results += [members[m["name"]].get("install", {}).get("result", "unknown")
                     for m in order if members[m["name"]].get("install", {}).get("result") != "pass"]
    landing = (manifest.get("together") or {}).get("landing") or {}
    if landing:
        wave_results.append(landing.get("result", "unknown"))
    status = exit_status(wave_results)
    manifest["overall"] = {0: "pass", 1: "fail", 3: "unknown"}[status]
    manifest["finished_at"] = now()
    manifest["unknowns"] = collect_unknowns(manifest)
    manifest["hazards"] = collect_hazards(manifest)
    (run / "manifest.json").write_text(json.dumps(manifest, indent=2, default=str),
                                       encoding="utf-8")
    (run / "index.html").write_text(landing_page(manifest, run), encoding="utf-8")

    missing = missing_artifacts(manifest, run)
    if missing:
        print("family-demo: artifacts the manifest names are missing:", file=sys.stderr)
        for path in missing:
            print(f"  - {path}", file=sys.stderr)
        status = 1
    print(f"\noverall {manifest['overall']}; unknowns {len(manifest['unknowns'])}; "
          f"hazards {len(manifest['hazards'])}")
    for hazard in manifest["hazards"]:
        print(f"  hazard  {hazard}")
    print(f"page     {(run / 'index.html').as_uri()}")
    print(f"manifest {run / 'manifest.json'}")
    print("seams    no check exercises a seam between members; see the page")
    return status


if __name__ == "__main__":
    sys.exit(main())
