#!/usr/bin/env python3
"""The performing family on one machine: each member alone, then together.

    uv run qm family-demo                         # wave 0, then the core together
    uv run qm family-demo --wave 0                # each member alone
    uv run qm family-demo --wave together --hold  # keep it up; open the page
    uv run qm family-demo --ref leo=origin/setlist
    uv run qm family-demo --plan                  # what would run; starts nothing

**WHAT IT SHOWS.** `ci/family-demo.yaml` names the members, the branch of each
that runs -- the one carrying the active work, not the default branch -- the
phase each joins in and the ports each is given. Every member answers one
contract, declared once in that file: `serve` on a given address with its
state under a given directory, and `check` an instance that is already up. For
every member of a phase that runs, this checks the branch out into a clone of
its own, installs it, starts it with `serve` on its reserved port, waits for it
to answer, runs its `check` against it, stops it, and proves the port is free.
Then it does the same with every member up at once, writes a page that links
each live surface and embeds every picture each check took, and writes a
manifest of commits, commands, ports, timings and results. The page is the
demo a person opens; the manifest is the record.

**WHO OWNS WHICH CHECK.** A check of one member alone lives in that member,
behind `check`: the member owns its selectors and what its screen must show,
and this file never names one. What needs several members, or the machine,
lives here: each member's ports held by the process tree this run started and
by nothing else, a port it reserves and must not bind left unbound, what a
member reports about itself naming this run's port and scratch state, its
checkout left as it was installed, every member up at once, and any seam
between two members.

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
clone the roster resolves, not even worktree metadata -- and every member is
handed a scratch directory under the run. The work directory defaults to the
system temporary directory and is never inside this repository.

**WHAT A RESULT MEANS.** `pass`, `fail` or `unknown`, per check and per wave,
and unknown is never folded into fail: a port somebody else holds, a check that
could not say, a stub that is not implemented, or a member that never got as far
as its check is `unknown`, with the reason. The exit status is 0 when every
member that ran passed, 1 when any failed or an artifact the manifest names is
missing, 3 when none failed and some were unknown, and 2 for a roster or an
invocation this cannot run. A skip is not a pass.

**HAZARDS ARE MEASURED, NOT ASSUMED.** While each member is up, every socket
its process tree holds is listed, and one outside its reserved ports is printed
as a hazard -- a member that opened an OSC port or dialled a console would show
here, whatever its source says. So are a descendant that had to be forced at
shutdown, a port still held afterwards, and a branch that does not contain the
active work it claims to stack on.

**WHAT IT CANNOT SEE.** Whether a member is correct beyond what its own check
asserts, outbound traffic that holds no socket open long enough to be listed,
real audio, MIDI or lighting hardware, and a member the roster does not place --
that one is printed as unplaced, never dropped.

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
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

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
PLACEHOLDER = re.compile(r"\{([a-z]+)(?::([a-z0-9_-]+))?\}")
# What a placeholder may name, and which ones only the contract's own commands
# may use: a member's `url` cannot name itself or a directory made per check.
PLACEHOLDERS = ("port", "checkout", "state", "token", "host", "url", "shots")
CONTRACT_ONLY = ("url", "shots")
WINDOWS = os.name == "nt"

# What the contract's two commands must pass on, so a member is started and
# checked on what this run reserved for it rather than on its own defaults.
CONTRACT_NEEDS = {"serve": ("{host}", "{port}", "{state}"), "check": ("{url}", "{shots}")}

# What a check's pictures are, by suffix.
PICTURES = (".png", ".svg", ".jpg", ".jpeg", ".webp")


class PlanError(ValueError):
    """The demo roster cannot be run as written."""


# ===================================================================
# THE PLAN -- read, checked and expanded without starting anything
# ===================================================================

def load_plan(path: Path = PLAN) -> dict:
    document = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if document.get("schema") != 2:
        raise PlanError(f"{path.name}: schema {document.get('schema')!r} is not 2")
    return document


def check_plan(plan: dict, rostered: set[str]) -> list[str]:
    """Every reason the plan cannot be run as written. Empty is runnable.

    `rostered` is the corpus roster's names, passed in rather than read here so
    the rules can be tested without a roster on disk.
    """
    problems: list[str] = []
    span = plan.get("ports") or {}
    first, last = span.get("first"), span.get("last")
    if not isinstance(first, int) or not isinstance(last, int) or first > last:
        return [f"ports: first/last must be integers in order, got {first!r}..{last!r}"]
    if not isinstance(plan.get("host"), str) or not plan["host"]:
        problems.append("host: the address every member binds is not declared")
    problems += _contract_problems(plan.get("contract") or {})

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
            problems += _runnable_problems(member)
        elif not member.get("needs"):
            problems.append(f"{name}: a phase that does not run must say what it needs to join")
    return problems


def _contract_problems(contract: dict) -> list[str]:
    problems = []
    for command, needs in CONTRACT_NEEDS.items():
        argv = contract.get(command)
        if not isinstance(argv, list) or not argv or not all(isinstance(a, str) for a in argv):
            problems.append(f"contract: {command} must be a list of arguments")
            continue
        if argv[0] != command:
            problems.append(f"contract: {command} must start with the word {command!r}")
        missing = [need for need in needs if need not in argv]
        if missing:
            problems.append(f"contract: {command} does not pass {', '.join(missing)}")
    if not contract.get("not_implemented"):
        problems.append("contract: not_implemented, what a stub check prints, is not declared")
    if not isinstance(contract.get("check_seconds"), (int, float)) or contract["check_seconds"] <= 0:
        problems.append("contract: check_seconds must be a positive number")
    return problems


def _runnable_problems(member: dict) -> list[str]:
    name = member["name"]
    problems = []
    ports = set((member.get("ports") or {}).keys())
    for key in ("branch", "url"):
        if not isinstance(member.get(key), str) or not member[key]:
            problems.append(f"{name}: runs, but names no {key}")
    entry = member.get("entry")
    if not isinstance(entry, list) or not entry:
        problems.append(f"{name}: runs, but has no entry to append the contract to")
    if not member.get("install"):
        problems.append(f"{name}: runs, but installs nothing")
    serves = member.get("serves")
    if serves not in ports:
        problems.append(f"{name}: serves {serves!r}, which is not one of its ports")
    unbound = member.get("unbound") or []
    for label in unbound:
        if label not in ports:
            problems.append(f"{name}: unbound {label!r} is not one of its ports")
        elif label == serves:
            problems.append(f"{name}: the port it serves cannot also be unbound")
    for path in member.get("state_in_checkout") or []:
        pure = PurePosixPath(str(path))
        if pure.is_absolute() or ".." in pure.parts or not pure.parts or ":" in str(path):
            problems.append(f"{name}: state_in_checkout {path!r} must be a path inside the checkout")
    identity = member.get("identity")
    if identity is not None and not all(identity.get(k) for k in ("url", "port", "state")):
        problems.append(f"{name}: identity needs a url, a port field and a state field")
    texts = [*map(str, entry or []), *map(str, member.get("serve_args") or []),
             *map(str, (member.get("env") or {}).values())]
    if identity:
        texts.append(str(identity.get("url", "")))
    problems += _placeholder_problems(name, ports, texts)
    # A url naming {url} or {shots} is refused with the rest: neither has a
    # value until the url itself has one.
    problems += _placeholder_problems(name, ports, [str(member.get("url", ""))])
    return problems


def _placeholder_problems(name: str, ports: set[str], texts: list[str]) -> list[str]:
    problems = []
    for text in texts:
        for kind, label in PLACEHOLDER.findall(text):
            if kind == "port" and label and label not in ports:
                problems.append(f"{name}: {{port:{label}}} names no declared port")
            elif kind not in PLACEHOLDERS:
                problems.append(f"{name}: unknown placeholder {{{kind}}}")
            elif kind in CONTRACT_ONLY:
                problems.append(f"{name}: {{{kind}}} is the contract's to pass, not a member's")
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

    An unknown placeholder, or one this context has no value for, raises
    rather than passing through, because a command carrying a literal
    `{port:web}` would bind nothing and fail in a way that reads like the
    member's fault.
    """
    if isinstance(value, list):
        return [expand(v, context) for v in value]
    if isinstance(value, dict):
        return {k: expand(v, context) for k, v in value.items()}
    if not isinstance(value, str):
        return value

    def substitute(match: re.Match) -> str:
        kind, label = match.group(1), match.group(2)
        if kind == "port" and label is not None:
            if label not in context["ports"]:
                raise PlanError(f"{{port:{label}}} names no declared port")
            return str(context["ports"][label])
        if kind in PLACEHOLDERS and label is None and kind in context:
            return str(context[kind])
        raise PlanError(f"no value for {match.group(0)} here")

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

def check_result(exit_code: int | None, output: str, not_implemented: str) -> tuple[str, bool]:
    """(result, stub) for a member's `check`, from its exit status and output.

    0 held and 1 did not, per the contract. Anything else -- a crash, a usage
    error, a timeout (no exit code at all), a check with nothing to check
    against -- could not say. A stub is one of those, named so it reads as not
    implemented rather than as a broken check.
    """
    if exit_code == 0:
        return "pass", False
    if exit_code == 1:
        return "fail", False
    return "unknown", exit_code is not None and not_implemented in output


def member_result(checks: list[dict], readiness: str) -> str:
    """One member's result in one wave: its own check and the demo's checks of it.

    Readiness that did not pass means the checks never ran, so the member is
    `fail` when it was observed not to start and `unknown` when it could not be
    started at all. A member whose own check did not run is never a pass,
    however its isolation reads.
    """
    if readiness == "fail":
        return "fail"
    if readiness != "pass":
        return "unknown"
    results = [c["result"] for c in checks]
    if not any(c.get("owner") == "member" for c in checks):
        return "unknown"
    if "fail" in results:
        return "fail"
    if "unknown" in results or not results:
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


def process_table() -> dict[int, tuple[int, int, str]] | None:
    """pid -> (parent pid, resident bytes, program name), or None when unknowable.

    On Windows this reads the kernel's process snapshot directly. It asked WMI
    first, and on a machine busy with other work one query took over half a
    minute and another timed out -- which turned every shutdown's descendant
    check into a wait, and an identity check into an unknown.
    """
    if WINDOWS:
        try:
            return _windows_process_table() or None
        except (OSError, AttributeError, ValueError):
            return None
    try:
        out = subprocess.run(["ps", "-eo", "pid=,ppid=,rss=,comm="], capture_output=True,
                             text=True, timeout=30).stdout
    except (OSError, subprocess.TimeoutExpired):
        return None
    out = "\n".join("|".join(line.split(None, 3)) for line in out.splitlines())
    return parse_process_table(out, bytes_per_unit=1024) or None


def _windows_process_table() -> dict[int, tuple[int, int, str]]:
    import ctypes
    from ctypes import wintypes

    class Entry(ctypes.Structure):  # PROCESSENTRY32W
        _fields_ = [("dwSize", wintypes.DWORD), ("cntUsage", wintypes.DWORD),
                    ("th32ProcessID", wintypes.DWORD), ("th32DefaultHeapID", ctypes.c_size_t),
                    ("th32ModuleID", wintypes.DWORD), ("cntThreads", wintypes.DWORD),
                    ("th32ParentProcessID", wintypes.DWORD), ("pcPriClassBase", ctypes.c_long),
                    ("dwFlags", wintypes.DWORD), ("szExeFile", ctypes.c_wchar * 260)]

    class Memory(ctypes.Structure):  # PROCESS_MEMORY_COUNTERS
        _fields_ = [("cb", wintypes.DWORD), ("PageFaultCount", wintypes.DWORD)] + [
            (name, ctypes.c_size_t) for name in (
                "PeakWorkingSetSize", "WorkingSetSize", "QuotaPeakPagedPoolUsage",
                "QuotaPagedPoolUsage", "QuotaPeakNonPagedPoolUsage", "QuotaNonPagedPoolUsage",
                "PagefileUsage", "PeakPagefileUsage")]

    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.CreateToolhelp32Snapshot.restype = wintypes.HANDLE
    kernel.CreateToolhelp32Snapshot.argtypes = (wintypes.DWORD, wintypes.DWORD)
    kernel.Process32FirstW.argtypes = kernel.Process32NextW.argtypes = (
        wintypes.HANDLE, ctypes.POINTER(Entry))
    kernel.OpenProcess.restype = wintypes.HANDLE
    kernel.OpenProcess.argtypes = (wintypes.DWORD, wintypes.BOOL, wintypes.DWORD)
    kernel.K32GetProcessMemoryInfo.argtypes = (wintypes.HANDLE, ctypes.POINTER(Memory),
                                               wintypes.DWORD)
    kernel.CloseHandle.argtypes = (wintypes.HANDLE,)

    snapshot = kernel.CreateToolhelp32Snapshot(0x2, 0)  # TH32CS_SNAPPROCESS
    if not snapshot or snapshot == wintypes.HANDLE(-1).value:
        raise OSError(ctypes.get_last_error(), "no process snapshot")
    table: dict[int, tuple[int, int, str]] = {}
    try:
        entry = Entry()
        entry.dwSize = ctypes.sizeof(Entry)
        more = kernel.Process32FirstW(snapshot, ctypes.byref(entry))
        while more:
            size = 0
            handle = kernel.OpenProcess(0x1000, False, entry.th32ProcessID)  # query, limited
            if handle:
                counters = Memory()
                counters.cb = ctypes.sizeof(Memory)
                if kernel.K32GetProcessMemoryInfo(handle, ctypes.byref(counters),
                                                  counters.cb):
                    size = counters.WorkingSetSize
                kernel.CloseHandle(handle)
            table[entry.th32ProcessID] = (entry.th32ParentProcessID, size, entry.szExeFile)
            more = kernel.Process32NextW(snapshot, ctypes.byref(entry))
    finally:
        kernel.CloseHandle(snapshot)
    return table


def parse_process_table(text: str, bytes_per_unit: int = 1) -> dict[int, tuple[int, int, str]]:
    table = {}
    for line in text.splitlines():
        parts = line.strip().split("|", 3)
        if len(parts) >= 3 and all(p.strip().isdigit() for p in parts[:3]):
            pid, parent, size = (int(p) for p in parts[:3])
            table[pid] = (parent, size * bytes_per_unit, parts[3].strip() if len(parts) > 3 else "")
    return table


def descendants(root: int, table: dict[int, tuple[int, int]]) -> set[int]:
    """`root` and every process below it in a (pid -> parent) table."""
    children: dict[int, list[int]] = {}
    for pid, row in table.items():
        parent = row[0]
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
# In another environment scikit-learn's modules loaded at 253 and one at 261
# did not, so the limit is not one number. A module past this is a warning,
# because a member may never import it.
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
# MEMBERS -- branch, checkout, install
# ===================================================================

def git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True,
                          encoding="utf-8", errors="replace")


def find_branch(clone: Path, branch: str) -> tuple[str, str] | None:
    """(ref, commit) for a branch in the roster's clone: local first, then origin's.

    Local first, because the branch carrying the contract may exist only in
    the clone it was made in; the manifest records which one answered. Reads
    only.
    """
    for ref in (f"refs/heads/{branch}", f"refs/remotes/origin/{branch}"):
        done = git(clone, "rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}")
        if done.returncode == 0 and done.stdout.strip():
            return ref.removeprefix("refs/heads/").removeprefix("refs/remotes/"), done.stdout.strip()
    return None


def resolve_commit(clone: Path, branch: str, override: str | None) -> tuple[str, str]:
    """(ref used, full commit) in the roster's clone. Reads only."""
    if override is not None:
        done = git(clone, "rev-parse", "--verify", f"{override}^{{commit}}")
        if done.returncode != 0:
            raise PlanError(f"{clone.name}: {override} is not a commit here: {done.stderr.strip()}")
        return override, done.stdout.strip()
    found = find_branch(clone, branch)
    if found is None:
        raise PlanError(f"{clone.name}: no branch {branch!r}, locally or on origin")
    return found


def stacked(clone: Path, base: str | None, commit: str) -> dict:
    """Whether `commit` contains the active work it claims to stack on.

    A claim in the plan, checked against the clone: `contains` is True, False,
    or "unknown" when the base cannot be found -- which is not the same as a
    branch cut from somewhere else.
    """
    if not base:
        return {"claimed": None, "contains": "unknown", "why": "no stacks_on declared"}
    found = find_branch(clone, base)
    if found is None:
        return {"claimed": base, "contains": "unknown", "why": f"no branch {base!r} here"}
    ref, tip = found
    done = git(clone, "merge-base", "--is-ancestor", tip, commit)
    contains = {0: True, 1: False}.get(done.returncode, "unknown")
    return {"claimed": base, "ref": ref, "commit": tip, "contains": contains}


def checkout(clone: Path, commit: str, into: Path) -> dict:
    """This run's own clone of a member at `commit`.

    `--shared` borrows the source's objects through alternates and writes
    nothing into it, so a commit only a local branch or a remote-tracking ref
    reaches is still here. Reused across runs when it already sits at the
    commit.
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


def dirty(repo: Path) -> list[str] | None:
    """`git status --porcelain`, line by line; None when git could not be asked.

    None rather than an empty list, because an empty list is the answer "the
    tree is clean", and a status that could not be read is not that.
    """
    done = git(repo, "status", "--porcelain")
    if done.returncode != 0:
        return None
    return [line for line in done.stdout.splitlines() if line]


def lock_digest(repo: Path) -> dict[str, str]:
    digests = {}
    for name in ("uv.lock", "package-lock.json", "pdm.lock"):
        path = repo / name
        if path.is_file():
            digests[name] = hashlib.sha256(path.read_bytes()).hexdigest()[:16]
    return digests


# What an install leaves in a clone, by the installers the plan uses.
INSTALLED = (".venv", "node_modules")


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
        # The stamp describes an environment on disk, so it is reused only while
        # that environment is still there: a removed .venv under a matching key
        # was reported as installed, and the member then failed to start.
        present = all((repo / made).is_dir() for made in previous.get("made") or ["?"])
        if previous.get("key") == key and previous.get("result") == "pass" and present:
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
    made = [name for name in INSTALLED if (repo / name).is_dir()]
    record = {"key": key, "result": result, "steps": steps, "at": now(), "reused": False,
              "made": made}
    stamp.parent.mkdir(parents=True, exist_ok=True)
    stamp.write_text(json.dumps(record, indent=2), encoding="utf-8")
    return record


def empty_state_in_checkout(checkout_path: Path, work: Path, paths: list[str]) -> list[str]:
    """Empty the directories a member keeps state in despite `--state`.

    Only ever inside this run's own clone: the clone must sit under the work
    directory and each path must resolve inside the clone, or nothing is
    removed. The roster's clone is never this path.
    """
    root = checkout_path.resolve()
    if work.resolve() not in root.parents:
        raise PlanError(f"{root} is not under the work directory; nothing emptied")
    emptied = []
    for relative in paths:
        target = (root / relative).resolve()
        if root not in target.parents:
            raise PlanError(f"{relative} resolves outside {root}; nothing emptied")
        if target.exists():
            shutil.rmtree(target)
            emptied.append(relative)
    return emptied


# ===================================================================
# PROBES -- the demo's own browser check, under its own interpreter
# ===================================================================

def run_probe(checks: list[dict], where: Path, plan: dict) -> list[dict]:
    if not checks:
        return []
    where.mkdir(parents=True, exist_ok=True)
    job_path, out_path = where / "browser-job.json", where / "browser-results.json"
    job_path.write_text(json.dumps({"checks": checks, "out": str(out_path)}, indent=2),
                        encoding="utf-8")
    pin = plan.get("browser") or {}
    argv = ["uv", "run", "--no-project", "--python", str(pin.get("python", "3.12")),
            "--with", f"playwright=={pin.get('playwright')}", "python",
            str(PROBES), "browser", str(job_path)]
    log = where / "browser.log"
    with open(log, "w", encoding="utf-8", errors="replace") as out:
        done = subprocess.run(executable(argv), cwd=where, env=child_env(), stdout=out,
                              stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, timeout=900)
    if done.returncode != 0 or not out_path.is_file():
        why = f"the browser probe exited {done.returncode}; see {log}"
        return [{"member": c["member"], "check": c["name"], "result": "unknown", "detail": why,
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
    """One member in one wave: its server, its checks and their results."""

    member: dict
    context: dict
    state: Path
    shots: Path
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

    def served(self) -> list[int]:
        """The ports the member is expected to be listening on."""
        unbound = set(self.member.get("unbound") or [])
        return [port for label, port in self.context["ports"].items() if label not in unbound]

    def record(self) -> dict:
        return {
            "ports": self.context["ports"],
            "url": self.context["url"],
            "state": str(self.state),
            "shots": str(self.shots),
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
    """From the member's first process starting to its last one answering."""
    if not processes or any(p.ready_seconds is None for p in processes):
        return "unknown"
    began = min(p.started for p in processes)
    return round(max(p.started + p.ready_seconds for p in processes) - began, 3)


def contract_context(member: dict, plan: dict, checkout_path: str, state: Path, shots: Path,
                     token: str) -> dict:
    """Every value a placeholder can take for one member in one wave."""
    ports = dict(member.get("ports") or {})
    context = {"ports": ports, "port": ports.get(member.get("serves")), "host": plan["host"],
               "token": token, "checkout": checkout_path, "state": state.as_posix(),
               "shots": shots.as_posix(),
               "not_implemented": (plan.get("contract") or {}).get("not_implemented")}
    context["url"] = expand(member["url"], context)
    return context


def serve_argv(member: dict, plan: dict, context: dict) -> list[str]:
    """The member's entry, then the contract's `serve`, then the member's own flags."""
    return (expand(member["entry"], context) + expand(plan["contract"]["serve"], context)
            + expand(member.get("serve_args") or [], context))


def check_argv(member: dict, plan: dict, context: dict) -> list[str]:
    """The member's entry, then the contract's `check`, and nothing of the member's."""
    return expand(member["entry"], context) + expand(plan["contract"]["check"], context)


def stage(member: dict, members: dict, wave: str, run: Path, token: str, plan: dict) -> Stage:
    state = run / "state" / wave / member["name"]
    shots = run / "shots" / wave / member["name"]
    state.mkdir(parents=True, exist_ok=True)
    checkout_path = (members[member["name"]].get("checkout") or {}).get("path", "")
    context = contract_context(member, plan, checkout_path, state, shots, token)
    built = Stage(member=member, context=context, state=state, shots=shots)
    built.processes.append(Running(
        member=member["name"], id="serve", argv=serve_argv(member, plan, context),
        cwd=checkout_path, env=expand(member.get("env") or {}, context),
        ready_url=context["url"],
        log=str(run / "logs" / f"{wave}-{member['name']}-serve.log")))
    return built


def prepare(built: Stage, members: dict, work: Path) -> bool:
    """What has to be true before a member starts; records why when it is not."""
    if members[built.name].get("install", {}).get("result") != "pass":
        built.blocked = "install did not pass"
        return False
    busy = {port: sorted(holders) for port in built.context["ports"].values()
            if (holders := listening(port))}
    if busy:
        built.blocked = (f"reserved port held by a process this run did not start: {busy}; "
                         f"nothing was killed")
        return False
    paths = built.member.get("state_in_checkout") or []
    if paths:
        try:
            built.prepared["emptied_in_checkout"] = empty_state_in_checkout(
                Path(built.context["checkout"]), work, paths)
        except (OSError, PlanError) as exc:
            built.blocked = f"could not empty {paths} in this run's clone: {exc}"
            return False
    return True


def bring_up(built: Stage, budget: float, members: dict, work: Path) -> None:
    """Prepare, start and wait for one member."""
    if not prepare(built, members, work):
        return
    for process in built.processes:
        start(process)
        wait_ready(process, budget)
        read_stub(built, process)
        if process.readiness != "pass":
            break
    states = [p.readiness for p in built.processes]
    built.readiness = "pass" if states and all(s == "pass" for s in states) else (
        "fail" if "fail" in states else "unknown")


def read_stub(built: Stage, process: Running) -> None:
    """A `serve` that exits saying it is not implemented is a stub, not a failure.

    Nothing about the member was observed but its declaration that it does not
    answer the contract yet, so it is unknown and named as a stub.
    """
    marker = built.context.get("not_implemented")
    if process.readiness == "fail" and marker and marker in tail(process.log):
        process.readiness = "unknown"
        process.readiness_detail += f" -- its serve says {marker!r}"
        built.prepared["serve_stub"] = True


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
    holders = {str(port): sorted(listening(port) or []) for port in built.served()}
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
        def named(pid: int) -> str:
            return f"pid {pid} {table[pid][2]}" if pid in table and len(table[pid]) > 2 else f"pid {pid}"
        built.identity["binds"] = sorted({f"{proto} {host}:{port} ({named(pid)})"
                                          for proto, (host, port), pid in held if pid in ours})
        built.identity["unreserved_binds"] = sorted(
            {f"{proto} {host}:{port} ({named(pid)})" for proto, (host, port), pid in held
             if pid in ours and port not in reserved})
    built.memory = sum(table[pid][1] for pid in ours if pid in table) if ours else "unknown"


# --- the demo's checks of a member: isolation, never behaviour --------------

def demo_check(built: Stage, name: str, result: str, detail: str = "", **evidence) -> dict:
    return {"member": built.name, "check": name, "owner": "demo", "result": result,
            "detail": detail, "evidence": evidence}


def listener_check(built: Stage) -> dict:
    """Every port the member serves is held by the process tree this run started."""
    verdict = built.identity.get("verdict")
    listeners = built.identity.get("listeners", {})
    if verdict == "ours":
        return demo_check(built, "ports-held-by-this-run", "pass", listeners=listeners)
    if verdict == "foreign":
        return demo_check(built, "ports-held-by-this-run", "fail",
                          f"held by processes this run did not start: {built.identity['foreign']}",
                          listeners=listeners)
    why = built.identity.get("why") or f"a served port had no listener: {listeners}"
    return demo_check(built, "ports-held-by-this-run", "unknown", why, listeners=listeners)


def unbound_check(built: Stage) -> dict | None:
    """A port the member reserves so nothing answers there is still not listening."""
    labels = built.member.get("unbound") or []
    if not labels:
        return None
    held, unknown = {}, []
    for label in labels:
        port = built.context["ports"][label]
        holders = listening(port)
        if holders is None:
            unknown.append(port)
        elif holders:
            held[str(port)] = sorted(holders)
    if held:
        return demo_check(built, "reserved-ports-left-unbound", "fail",
                          f"listening where nothing may: {held}", held=held)
    if unknown:
        return demo_check(built, "reserved-ports-left-unbound", "unknown",
                          f"no listener table for {unknown}")
    return demo_check(built, "reserved-ports-left-unbound", "pass",
                      ports=[built.context["ports"][label] for label in labels])


def identity_check(built: Stage) -> dict | None:
    """What the member reports about itself names this run's port and scratch state.

    The member's own words, asked over HTTP: the port is the socket that
    answered and the state path is the one it resolved, so a stale server or a
    shared database is caught before anything is attributed to this run.
    """
    identity = built.member.get("identity")
    if not identity:
        return None
    url = expand(identity["url"], built.context)
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            said = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, OSError, ValueError) as exc:
        return demo_check(built, "identity-names-this-run", "fail",
                          f"{url} did not answer as JSON: {exc}")
    port, state = said.get(identity["port"]), said.get(identity["state"])
    problems = []
    if str(port) != str(built.context["port"]):
        problems.append(f"{identity['port']}={port!r}, not {built.context['port']}")
    try:
        inside = state is not None and built.state.resolve() in Path(state).resolve().parents
    except (OSError, ValueError, TypeError):
        inside = False
    if not inside:
        problems.append(f"{identity['state']}={state!r} is not under {built.state}")
    return demo_check(built, "identity-names-this-run", "fail" if problems else "pass",
                      "; ".join(problems), said={identity["port"]: port, identity["state"]: state})


def untouched_check(built: Stage, members: dict) -> dict:
    """The member's checkout is as its install left it, after it served and was checked.

    Compared with the clone's status right after install, so what an install
    writes -- a lock file the installer makes -- is not counted as the run's.
    Files git ignores are not seen, and a member's declared `state_in_checkout`
    is ignored by its own repository.
    """
    before = (members[built.name].get("checkout") or {}).get("after_install")
    now_ = dirty(Path(built.context["checkout"]))
    if before is None or now_ is None:
        return demo_check(built, "checkout-untouched", "unknown", "git status could not be read")
    written = sorted(set(now_) - set(before))
    if written:
        return demo_check(built, "checkout-untouched", "fail",
                          f"written into the checkout: {written[:8]}", written=written)
    return demo_check(built, "checkout-untouched", "pass")


# --- the member's own check, through the contract ----------------------------

ANSI = re.compile(r"\x1b\[[0-9;?]*[A-Za-z]")


def last_line(text: str) -> str:
    for line in reversed(ANSI.sub("", text).splitlines()):
        # pytest frames its summary in rules of = signs; the words are the line.
        if line.strip().strip("=").strip():
            return line.strip().strip("=").strip()[:300]
    return ""


def pictures(directory: Path) -> list[str]:
    if not directory.is_dir():
        return []
    return sorted(str(p) for p in directory.rglob("*")
                  if p.is_file() and p.suffix.lower() in PICTURES and p.stat().st_size > 0)


def member_check(built: Stage, plan: dict, run: Path, wave: str) -> dict:
    """Run the member's `check` against the instance this run started.

    Its argument vector is the member's entry and the contract's words, and
    nothing else, so the member is asked exactly what every other member is.
    """
    contract = plan["contract"]
    argv = check_argv(built.member, plan, built.context)
    log = run / "logs" / f"{wave}-{built.name}-check.log"
    built.shots.mkdir(parents=True, exist_ok=True)
    began = time.monotonic()
    exit_code, timed_out = None, False
    flags = subprocess.CREATE_NEW_PROCESS_GROUP if WINDOWS else 0
    with open(log, "w", encoding="utf-8", errors="replace") as out:
        try:
            child = subprocess.Popen(executable(argv), cwd=built.context["checkout"],
                                     env=child_env(), stdout=out, stderr=subprocess.STDOUT,
                                     stdin=subprocess.DEVNULL, creationflags=flags,
                                     start_new_session=not WINDOWS)
        except OSError as exc:
            out.write(f"did not start: {exc}\n")
            child = None
        if child is not None:
            try:
                exit_code = child.wait(timeout=float(contract["check_seconds"]))
            except subprocess.TimeoutExpired:
                timed_out = True
                stop_tree(child)
    output = tail(str(log), 65536)
    result, stub = check_result(exit_code, output, contract["not_implemented"])
    if timed_out:
        detail = f"ran past {contract['check_seconds']}s and was stopped"
    elif stub:
        detail = "not implemented"
    else:
        detail = last_line(output)
    return {"member": built.name, "check": "contract check", "owner": "member",
            "result": result, "stub": stub, "detail": detail, "exit_code": exit_code,
            "argv": argv, "log": str(log), "seconds": round(time.monotonic() - began, 3),
            "shots": pictures(built.shots)}


def stop_tree(child: subprocess.Popen) -> None:
    """Stop a check this run started, and everything under it."""
    if WINDOWS:
        subprocess.run(["taskkill", "/T", "/F", "/PID", str(child.pid)], capture_output=True)
    else:
        try:
            os.killpg(child.pid, signal.SIGKILL)
        except OSError:
            pass
    try:
        child.wait(timeout=10)
    except subprocess.TimeoutExpired:
        pass


def not_run(built: Stage, why: str) -> dict:
    return {"member": built.name, "check": "contract check", "owner": "member",
            "result": "unknown", "stub": False, "detail": why, "shots": []}


def assert_all(stages: list[Stage], run: Path, plan: dict, wave: str) -> None:
    """The demo's isolation checks, then each ready member's own check, in turn."""
    table = process_table()
    for built in stages:
        observe(built, table)
    for built in stages:
        if built.readiness != "pass":
            built.checks = [not_run(built, built.blocked or "not ready, so no check ran")]
            continue
        demo = [listener_check(built)]
        demo += [c for c in (unbound_check(built), identity_check(built)) if c]
        if built.identity.get("verdict") == "foreign":
            own = not_run(built, "a process this run did not start holds one of the "
                                 "member's ports, so a check would measure that one")
        else:
            print(f"  {wave:<8} {built.name:<12} checking", flush=True)
            own = member_check(built, plan, run, wave)
        built.checks = [own] + demo


def take_down(stages: list[Stage], members: dict) -> dict:
    for built in reversed(stages):
        for process in reversed(built.processes):
            stop(process)
    for built in stages:
        if built.readiness == "pass":
            built.checks.append(untouched_check(built, members))
    ports = [p for s in stages for p in s.context["ports"].values()]
    return port_report(ports)


def wave_zero(order: list[dict], members: dict, run: Path, token: str, plan: dict,
              budget: float, work: Path) -> dict:
    records = {}
    for member in order:
        built = stage(member, members, "wave0", run, token, plan)
        print(f"  wave 0  {member['name']:<12} starting", flush=True)
        try:
            bring_up(built, budget, members, work)
            assert_all([built], run, plan, "wave0")
        finally:
            ports = take_down([built], members)
        record = built.record()
        record["ports_after"] = ports
        records[member["name"]] = record
        print(f"  wave 0  {member['name']:<12} {record['result']:<8} "
              f"ready {seconds(record['ready_seconds'])}  {summary(record)}", flush=True)
    return records


def together(order: list[dict], members: dict, run: Path, token: str, plan: dict,
             budget: float, simultaneous: bool, hold: float | None, work: Path,
             finish) -> dict:
    stages = [stage(m, members, "together", run, token, plan) for m in order]
    seams_live: dict = {}
    landing: dict = {}
    try:
        if simultaneous:
            _simultaneous(stages, budget, members, work)
        else:
            for built in stages:
                print(f"  together {built.name:<11} starting", flush=True)
                bring_up(built, budget, members, work)
        before = live_connections(stages)
        assert_all(stages, run, plan, "together")
        seams_live = merge_samples([before, live_connections(stages)])
        landing = finish(stages, seams_live)
        if hold is not None:
            hold_open(run, hold)
    finally:
        ports = take_down(stages, members)
    records = {}
    for built in stages:
        records[built.name] = built.record()
        print(f"  together {built.name:<11} {records[built.name]['result']:<8} "
              f"ready {seconds(records[built.name]['ready_seconds'])}  "
              f"{summary(records[built.name])}", flush=True)
    return {"start": "simultaneous" if simultaneous else "staggered", "members": records,
            "ports_after": ports, "live_connections": seams_live, "landing": landing}


def _simultaneous(stages: list[Stage], budget: float, members: dict, work: Path) -> None:
    """Start every member at once, then wait on all of them together."""
    started = []
    for built in stages:
        if prepare(built, members, work):
            start(built.processes[0])
            started.append(built)

    def finish(built: Stage) -> None:
        wait_ready(built.processes[0], budget)
        built.readiness = built.processes[0].readiness

    # Waited on together, so a member's ready time is its own and not the time
    # the harness got round to asking it after the members before it answered.
    with ThreadPoolExecutor(max_workers=max(1, len(started))) as pool:
        list(pool.map(finish, started))


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
        detail = f" -- {entry['detail']}" if entry.get("detail") and entry["result"] != "pass" else ""
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
code{font-size:.85em;overflow-wrap:anywhere}
.pass{color:var(--pass);font-weight:600}.fail{color:var(--fail);font-weight:600}
.unknown{color:var(--unknown);font-weight:600}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:16px}
.card{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:12px}
.card img{width:100%;border:1px solid var(--line);border-radius:4px;background:#000;margin-top:6px}
.card h3{margin:0 0 4px;font-size:1rem}.live{font-size:.8rem;color:var(--muted)}
.card ul{margin:4px 0;padding-left:18px;font-size:.85rem}
.wrap{overflow-x:auto}
"""

LIVE = """
document.querySelectorAll('[data-live]').forEach(el => {
  fetch(el.dataset.live, {mode: 'no-cors'})
    .then(() => { el.textContent = 'answering now'; })
    .catch(() => { el.textContent = 'not answering now'; });
});
"""


def result_span(result: str, stub: bool = False) -> str:
    label = "not implemented" if stub else result
    return f'<span class="{html.escape(result)}">{html.escape(label)}</span>'


def contract_status(record: dict) -> str:
    """What the member's own check said about the contract, in this wave."""
    if (record.get("prepared") or {}).get("serve_stub"):
        return "stub"
    own = next((c for c in record.get("checks") or [] if c.get("owner") == "member"), None)
    if own is None or own.get("exit_code", "absent") == "absent":
        return "not asked"
    return "stub" if own.get("stub") else "implemented"


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
        w0, tg = wave0.get(name, {}), together_members.get(name, {})
        surface = member.get("url", "")
        stack = member.get("stacks_on") or {}
        contains = {True: "contains it", False: "does not contain it"}.get(
            stack.get("contains"), "not established")
        status = contract_status(tg or w0)
        rows.append(
            f'<tr data-member="{e(name)}"><td><strong>{e(name)}</strong><br>'
            f'<span class="live">{e(member.get("family") or "unstated")}</span></td>'
            f'<td><code>{e(member.get("ref", ""))}</code> <code>{e(commit)}</code><br>'
            f'<span class="live">on <code>{e(str(stack.get("claimed") or ""))}</code>, '
            f'{e(contains)}</span></td>'
            f'<td>{e(ports)}</td><td>{e(status)}</td>'
            f'<td>{result_span(w0.get("result", "unknown")) if w0 else "not run"}'
            f'<br><span class="live">ready {e(str(w0.get("ready_seconds", "")))}s</span></td>'
            f'<td>{result_span(tg.get("result", "unknown")) if tg else "not run"}'
            f'<br><span class="live">ready {e(str(tg.get("ready_seconds", "")))}s</span></td>'
            f'<td><a href="{e(surface)}">{e(surface)}</a><br>'
            f'<span class="live" data-live="{e(surface)}">not checked</span></td></tr>')
        for wave, record in (("alone", w0), ("together", tg)):
            if record:
                cards.append(member_card(name, wave, record, run))

    later = "".join(
        f'<tr><td>{e(name)}</td><td>{e(m["phase"])}</td>'
        f'<td>{e(", ".join(str(p) for p in m["ports"].values()))}</td>'
        f'<td>{"<br>".join(e(n) for n in m.get("needs") or [])}</td></tr>'
        for name, m in manifest["members"].items() if not m.get("runs"))
    choices = "".join(
        f'<li><strong>{e(name)}</strong>: {e(m["choice"])}</li>'
        for name, m in manifest["members"].items() if m.get("runs") and m.get("choice"))
    contract = manifest.get("contract") or {}
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
member's own check took while it ran. Overall: {result_span(manifest["overall"]) if manifest.get("overall")
else "not decided while the members are still up"}.</p>

<h2>Members that ran</h2>
<p>Each runs the branch carrying its active work, with the contract on top.</p>
<div class="wrap"><table>
<tr><th>Member</th><th>Branch and commit</th><th>Ports</th><th>Contract</th><th>Alone</th><th>Together</th><th>Surface</th></tr>
{"".join(rows)}
</table></div>
{f"<h3>Where the branch was a judgement</h3><ul>{choices}</ul>" if choices else ""}

<h2>The contract</h2>
<p>Every member is started with <code>{e(" ".join(contract.get("serve") or []))}</code>
and checked with <code>{e(" ".join(contract.get("check") or []))}</code>, appended to its
own entry. The member's check is the member's: its selectors and what its screen
must show live in it. The demo's checks are of isolation: ports held by this run's
processes and by nothing else, reserved ports left unbound, what a member says
about itself naming this run, and its checkout left as installed.</p>

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


def member_card(name: str, wave: str, record: dict, run: Path) -> str:
    e = html.escape
    own = next((c for c in record.get("checks") or [] if c.get("owner") == "member"), {})
    demo = [c for c in record.get("checks") or [] if c.get("owner") == "demo"]
    detail = f"<p>{e(own['detail'])}</p>" if own.get("detail") else ""
    shots = own.get("shots") or []
    pictures_html = "".join(
        f'<img alt="{e(name)} {e(wave)}: {e(Path(shot).name)}" '
        f'src="{e(Path(os.path.relpath(shot, run)).as_posix())}">'
        for shot in shots if Path(shot).is_file()) or "<p>no picture was recorded</p>"
    isolation = "".join(
        f'<li><code>{e(c["check"])}</code> {result_span(c["result"])}'
        f'{" -- " + e(c["detail"]) if c.get("detail") and c["result"] != "pass" else ""}</li>'
        for c in demo)
    return (f'<div class="card" data-card="{e(name)}-{e(wave)}"><h3>{e(name)}, {e(wave)}</h3>'
            f'<p>its own check {result_span(own.get("result", "unknown"), bool(own.get("stub")))}'
            f' <span class="live">{e(str(own.get("seconds", "")))}s</span></p>{detail}'
            f'<ul>{isolation}</ul>{pictures_html}</div>')


def missing_artifacts(manifest: dict, run: Path) -> list[str]:
    """Every artifact the manifest names that is not on disk, or is empty."""
    named = [run / "index.html", run / "manifest.json"]
    records = list((manifest.get("wave0") or {}).values())
    records += list(((manifest.get("together") or {}).get("members") or {}).values())
    for record in records:
        for entry in record.get("checks") or []:
            named += [Path(shot) for shot in entry.get("shots") or []]
            if entry.get("log"):
                named.append(Path(entry["log"]))
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
        if (member.get("stacks_on") or {}).get("contains") is False:
            found.append(f"{name}: {member.get('ref')} does not contain "
                         f"{member['stacks_on']['claimed']}, the active work it claims to stack on")
    return found


def collect_unknowns(manifest: dict) -> list[str]:
    found = []
    for wave, records in (("alone", manifest.get("wave0") or {}),
                          ("together", (manifest.get("together") or {}).get("members") or {})):
        for name, record in records.items():
            for entry in record.get("checks") or []:
                if entry["result"] == "unknown":
                    label = "not implemented" if entry.get("stub") else entry.get("detail", "")
                    found.append(f"{name} {wave}: {entry['check']} -- {label}")
            if record.get("memory_bytes_at_check") == "unknown":
                found.append(f"{name} {wave}: memory not sampled")
    for name, member in manifest["members"].items():
        if not member.get("runs"):
            found.append(f"{name}: not run in this phase ({member['phase']})")
        elif member.get("ref_overridden"):
            found.append(f"{name}: run at {member.get('ref')} rather than its branch "
                         f"{member.get('branch')}, which carries the contract")
        elif (member.get("stacks_on") or {}).get("contains") == "unknown":
            found.append(f"{name}: whether {member.get('ref')} contains "
                         f"{(member.get('stacks_on') or {}).get('claimed')} was not established")
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
                        help="check a member out at this ref instead of its branch")
    parser.add_argument("--work", type=Path,
                        default=Path(tempfile.gettempdir()) / "qm-family-demo",
                        help="where clones, installs and runs go; never this repository")
    parser.add_argument("--search-root", action="append", type=Path, default=[])
    parser.add_argument("--start", choices=("staggered", "simultaneous"), default="staggered")
    parser.add_argument("--ready-budget", type=float, default=120.0,
                        help="seconds a member may take to answer at its url")
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
        problems = check_plan(plan, set(rostered))
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
        branch = f"  {member['branch']}" if runs else ""
        print(f"  {'run ' if runs else 'later'} {member['name']:<18} {member['phase']:<22} "
              f"{ports}{branch}")
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
        "schema": 2, "run": stamp, "token": token, "started_at": now(),
        "corpus": {"commit": corpus_commit, "dirty": dirty(CORPUS),
                   "plan": str(args.plan_file.relative_to(CORPUS)) if
                   CORPUS in args.plan_file.resolve().parents else str(args.plan_file),
                   "plan_sha256": hashlib.sha256(args.plan_file.read_bytes()).hexdigest()[:16]},
        "environment": environment(), "work": str(work), "port_range": plan["ports"],
        "contract": plan["contract"], "host": plan["host"],
        "search_roots": [str(r) for r in search_roots], "unplaced": lonely, "members": {},
        "reading": {
            "results": "pass, fail or unknown; unknown is never folded into fail",
            "owners": "a check owned by the member is its own `check`; one owned by the "
                      "demo is isolation, and never behaviour",
            "together": "process simultaneity only -- no check exercises a seam between members",
            "ready_seconds": "process start to the first 2xx from the member's url",
        },
    }

    members: dict = {}
    for member in plan["members"]:
        name = member["name"]
        record = {"phase": member["phase"], "family": family_of.get(name),
                  "ports": member["ports"], "runs": member in order}
        if member in order:
            record.update(branch=member["branch"], choice=member.get("choice"),
                          deviations=member.get("deviations") or [],
                          url=expand(member["url"], {"ports": member["ports"],
                                                     "host": plan["host"]}))
            clone = resolve(rostered[name], search_roots)
            if clone is None:
                record["install"] = {"result": "unknown",
                                     "why": f"no clone at {rostered[name].get('paths')}"}
            else:
                try:
                    ref, commit = resolve_commit(clone, member["branch"], refs.get(name))
                    # One clone per member, moved to each run's commit, under a
                    # one-letter directory: every character here is one less
                    # for the deepest native module in the member's
                    # environment, and a joe clone a few characters deeper
                    # failed to import scikit-learn mid-check.
                    into = work / "c" / name
                    print(f"  checkout {name:<12} {ref} {commit[:12]}", flush=True)
                    record.update(source_clone=str(clone), ref=ref, commit=commit,
                                  ref_overridden=name in refs,
                                  stacks_on=stacked(clone, member.get("stacks_on"), commit),
                                  checkout=checkout(clone, commit, into))
                    record["locks"] = lock_digest(into)
                    print(f"  install  {name:<12}", end=" ", flush=True)
                    record["install"] = install(member, into, run / "logs",
                                                work / "installed" / f"{name}.json",
                                                args.fresh_install)
                    record["checkout"]["after_install"] = dirty(into)
                    if WINDOWS:
                        record["checkout"]["native_paths"] = long_native_paths(into)
                    print(record["install"]["result"]
                          + (" (reused)" if record["install"].get("reused") else ""), flush=True)
                    native = record["checkout"].get("native_paths") or {}
                    if native.get("over_limit"):
                        print(f"           {native['over_limit']} native module(s) past the "
                              f"loader's path limit (longest {native['longest']}); a member "
                              f"importing one fails -- a shorter --work avoids it", flush=True)
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
        manifest["wave0"] = wave_zero(order, members, run, token, plan, args.ready_budget, work)

    def finish(stages: list[Stage], live: dict) -> dict:
        """Write the page while everything is up, and check it in a browser."""
        manifest["together"] = {"members": {s.name: s.record() for s in stages},
                                "live_connections": live}
        manifest["seams"] = {"named_in_source": named_in_source(
            members, [m["name"] for m in started])}
        manifest["unknowns"] = collect_unknowns(manifest)
        manifest["hazards"] = collect_hazards(manifest)
        (run / "index.html").write_text(landing_page(manifest, run), encoding="utf-8")
        result = run_probe([{
            "member": "landing", "name": "landing-page-shows-every-member",
            "base": (run / "index.html").as_uri(),
            "params": {"members": [m["name"] for m in order]},
            "shot": str(run / "shots" / "landing.png")}], run / "probes" / "landing", plan)
        return result[0] if result else {}

    if args.wave in ("together", "all"):
        print(f"together: every member up, {args.start} start", flush=True)
        manifest["together"] = together(order, members, run, token, plan, args.ready_budget,
                                        args.start == "simultaneous", args.hold, work, finish)
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
