#!/usr/bin/env python3
"""Emit the disk status document: what is full, and what could be given back.

Org-level tooling, copied nowhere. It is the collector half of the split this
repository uses for every dashboard -- a generator that talks to the host and
writes a document, and a renderer that reads only the document. See
ci/harness_status.py and ci/harness_dashboard.py for the worked example, and
handbook/generated-documents.md for the convention itself.

EVERY FACT HERE IS MACHINE-SCOPED, WHICH CHANGES ONE RULE

harness-status.json is mostly an organisation fact with a `local` layer bolted
on, so it has a `--no-local` flag and a committed copy. This document has no
such half. Free space on C:, the size of somebody's Docker disk, the state of a
browser cache -- none of it is true for anyone but the person who ran it, and a
committed copy would be one machine's Tuesday presented as an org fact that
every reader afterwards inherits.

So this tool refuses to write anywhere inside the corpus. Not by default, and
not unless a flag is passed: always. What is committed is the policy the
document is measured against, in ci/disk-policy.yaml, which is the same on
every machine and is the thing worth reviewing.

UNKNOWN IS A VALUE

Any target this tool could not measure is written `{"unknown": "<reason>"}` --
never omitted, never zero. A cache behind a permission error must not render
like a cache that is empty: the first is an absence of evidence and the second
reads as nothing to reclaim. Same spelling as the other two documents here, so
one parser shape reads all three.

NOTHING HERE DELETES ANYTHING

Measuring and reclaiming are separate tools on purpose. A collector that could
also delete would be one flag away from freeing 90GB because a walk returned
the wrong number. ci/disk_reclaim.py acts, defaults to a dry run, and re-reads
the filesystem itself rather than trusting a document that may be hours old.

Usage:
    python ci/disk_status.py --write ~/disk-status.json
    python ci/disk_status.py --write ~/disk-status.json --search-root ~/repos
    python ci/disk_status.py --check
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import stat
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

CI_DIR = Path(__file__).resolve().parent
CORPUS = CI_DIR.parent

# How long this document may be quoted before it has to be re-derived. Shorter
# than the harness budget, and for a blunter reason: a build, a container pull
# or a single test run moves these numbers by gigabytes, so a figure from this
# morning describes a disk that no longer exists. Long enough to survive a
# working session, short enough that nobody plans a cleanup from yesterday's.
STALENESS_BUDGET_HOURS = 6

# The safety tiers, cheapest first. The order is load-bearing: disk_reclaim.py
# permits a tier only when every tier before it is permitted, so there is no
# invocation that empties the recycle bin while leaving a download cache alone.
SAFETY_TIERS = ("refetched", "rebuilt", "destructive")

# The kinds a reclaimer may be. A small closed set rather than an extension
# point: every kind is a way to delete something, and a policy file that could
# name arbitrary code would move the review from this repository to whoever
# wrote the plugin.
KINDS = ("directory_contents", "glob", "command")

# Directory names a glob sweep never descends into. `.git` is the one that
# matters -- a pattern like `**/build` matches inside a pack directory and the
# walk costs minutes for nothing.
NEVER_DESCEND = {".git", "$RECYCLE.BIN", "System Volume Information"}

# How many individual paths to name per target. A `node_modules` sweep finds
# forty and the reader needs the big ones, not the list; the rest are counted.
UNIT_LIMIT = 8


def unknown(reason: str) -> dict:
    return {"unknown": reason}


def unknown_reason(value: object) -> str | None:
    """The reason, if this value is the document's unknown form."""
    if isinstance(value, dict) and "unknown" in value and len(value) == 1:
        return str(value["unknown"])
    return None


def inside_corpus(path: Path) -> bool:
    """Whether this path would land in the repository, and so in a commit."""
    try:
        path.resolve().relative_to(CORPUS.resolve())
    except ValueError:
        return False
    return True


def expand(text: str) -> str | None:
    """`${VAR}` against the environment, or None if a variable is unset.

    None rather than an empty string. `${LOCALAPPDATA}/Docker` with the
    variable missing expands to `/Docker`, which is a real path on a POSIX box
    and the root of the drive on Windows -- a measurement of the wrong thing,
    or a deletion of it.
    """
    out: list[str] = []
    rest = text
    while "${" in rest:
        before, _, after = rest.partition("${")
        name, closed, rest = after.partition("}")
        if not closed:
            return None
        value = os.environ.get(name)
        if value is None:
            return None
        out.append(before)
        out.append(value)
    out.append(rest)
    return "".join(out)


def is_reparse_point(path: Path) -> bool:
    """A junction, symlink or mount point, which a walk must not follow.

    Windows junctions are the reason this exists: os.walk descends into them,
    and a cache directory junctioned onto another drive gets counted against
    the wrong volume -- or walked in a loop.
    """
    try:
        info = path.lstat()
    except OSError:
        return True
    if stat.S_ISLNK(info.st_mode):
        return True
    attributes = getattr(info, "st_file_attributes", 0)
    return bool(attributes & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0))


def tree_size(root: Path) -> tuple[int, int, int]:
    """(bytes, files, unreadable) under a path, not following reparse points.

    Unreadable entries are counted rather than raised on. A cache directory
    with one locked file in it is still worth reporting the size of, and the
    count is carried into the document so the figure is known to be a floor.
    """
    if root.is_file():
        try:
            return root.stat().st_size, 1, 0
        except OSError:
            return 0, 0, 1

    total = files = unreadable = 0
    for parent, dirnames, filenames in os.walk(root, onerror=lambda _: None):
        here = Path(parent)
        dirnames[:] = [
            d for d in dirnames
            if d not in NEVER_DESCEND and not is_reparse_point(here / d)
        ]
        for name in filenames:
            try:
                info = (here / name).lstat()
            except OSError:
                unreadable += 1
                continue
            if stat.S_ISLNK(info.st_mode):
                continue
            total += info.st_size
            files += 1
    return total, files, unreadable


def age_days(path: Path) -> float | None:
    try:
        modified = path.lstat().st_mtime
    except OSError:
        return None
    return (datetime.now(timezone.utc).timestamp() - modified) / 86400


def unit(path: Path) -> dict:
    """One deletable thing: the granularity disk_reclaim.py works at.

    A target is a list of these rather than a single number so that the two
    tools agree on what would actually be removed. A reclaimer that deleted a
    directory the collector had only summed would be acting on a fact nobody
    reported.
    """
    size, files, unreadable = tree_size(path)
    return {
        "path": str(path),
        "bytes": size,
        "files": files,
        "unreadable": unreadable,
        "age_days": round(age_days(path) or 0.0, 1),
    }


def units_of_directory(root: Path, retain_days: float | None) -> list[dict]:
    """The children of a directory, which is what emptying it removes.

    The children rather than the directory: the tools keep the directory and
    remove what is in it, because the owning application put it there and may
    not create it again.
    """
    found = []
    try:
        children = sorted(root.iterdir(), key=lambda p: p.name)
    except OSError as error:
        raise PermissionError(str(error)) from error
    for child in children:
        if retain_days is not None:
            age = age_days(child)
            if age is None or age < retain_days:
                continue
        found.append(unit(child))
    return found


def units_of_glob(roots: list[Path], patterns: list[str], blocked: set[str]) -> list[dict]:
    """Every directory under the search roots matching one of this entry's patterns.

    Two separate prunings, and the second is the one that keeps the totals
    honest. `names` is what this entry claims; `blocked` is what *any* entry in
    the policy claims, and the walk descends into neither. Without the second,
    `.venv` is counted whole by one entry and the `__pycache__` directories
    inside it are counted again by another, so the reclaimable total is larger
    than the disk -- a number that is confidently wrong and reads as authority.

    A match is never descended into either, so a `node_modules` nested inside
    another is counted once, in the outer one, which is also the only one a
    deletion would reach.
    """
    names = {p.rsplit("/", 1)[-1] for p in patterns}
    found = []
    seen: set[str] = set()
    for root in roots:
        if not root.exists():
            continue
        for parent, dirnames, filenames in os.walk(root, onerror=lambda _: None):
            here = Path(parent)
            matched = [d for d in dirnames if d in names]
            dirnames[:] = [
                name for name in dirnames
                if name not in NEVER_DESCEND
                and name not in blocked
                and not is_reparse_point(here / name)
            ]
            for name in matched + [f for f in filenames if f in names]:
                path = (here / name).resolve()
                if str(path) in seen:
                    continue
                seen.add(str(path))
                found.append(unit(path))
    return found


def run(argv: list[str]) -> tuple[int, str, str]:
    try:
        result = subprocess.run(
            argv,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except (OSError, ValueError) as error:
        return 127, "", str(error)
    return result.returncode, (result.stdout or "").strip(), (result.stderr or "").strip()


def parse_bytes(text: str) -> int | None:
    """A byte count from a tool's output, in whatever unit it chose.

    `docker system df` prints `12.4GB`; PowerShell prints `6547218432`. Both
    are the same fact and neither is worth a second document field.
    """
    cleaned = text.strip().split(chr(10))[0].strip().replace(",", "")
    # Docker reports reclaimable space as `23.62GB (97%)` -- the size, and what
    # share of the total it is. The parenthetical is a second fact in the same
    # field, and without dropping it the whole reading was refused as "not a
    # size", which hid a 23GB target behind an unknown that looked like a dead
    # daemon.
    if "(" in cleaned:
        cleaned = cleaned.split("(", 1)[0].strip()
    if not cleaned:
        return None
    units = {"B": 1, "KB": 10**3, "MB": 10**6, "GB": 10**9, "TB": 10**12,
             "KIB": 2**10, "MIB": 2**20, "GIB": 2**30, "TIB": 2**40}
    for suffix in sorted(units, key=len, reverse=True):
        if cleaned.upper().endswith(suffix):
            head = cleaned[: -len(suffix)].strip()
            try:
                return int(float(head) * units[suffix])
            except ValueError:
                return None
    try:
        return int(float(cleaned))
    except ValueError:
        return None


def measure_command(entry: dict) -> dict:
    """A target whose size only the owning tool can report.

    Docker's reclaimable bytes live inside a virtual disk, and uv's cache is
    hardlinked into live environments. Asking the tool is the only measurement
    that is not a guess, and it is also the only one whose answer matches what
    the tool's own prune would free.
    """
    requires = entry.get("requires")
    if requires and not shutil.which(requires):
        return unknown(f"{requires} is not on PATH, so this target cannot be measured")

    spec = entry.get("measure") or {}
    argv = spec.get("argv")
    if not argv:
        return unknown("policy entry has no measure.argv")

    status, out, err = run([str(a) for a in argv])
    if status != 0:
        first = (err or out or "no output").splitlines()[0]
        return unknown(f"{argv[0]} exited {status}: {first[:160]}")

    if spec.get("measures_path_from_output"):
        target = Path(out.strip())
        if not target.exists():
            return unknown(f"{argv[0]} named {target}, which does not exist")
        size, files, unreadable = tree_size(target)
        return {
            "bytes": size,
            "units": [{"path": str(target), "bytes": size, "files": files,
                       "unreadable": unreadable, "age_days": round(age_days(target) or 0.0, 1)}],
            "units_total": 1,
            "measured_by": " ".join(str(a) for a in argv),
        }

    size = parse_bytes(out)
    if size is None:
        return unknown(f"{argv[0]} printed {out.splitlines()[0][:80]!r}, which is not a size")
    return {
        "bytes": size,
        "units": [],
        "units_total": 0,
        "measured_by": " ".join(str(a) for a in argv),
        "note": "reported by the owning tool; there are no separate paths to list",
    }


def resolve_roots(entry: dict) -> tuple[list[Path], list[str]]:
    """(paths that exist, reasons the others do not) for a path-shaped entry."""
    resolved: list[Path] = []
    gaps: list[str] = []
    for raw in entry.get("roots") or []:
        expanded = expand(str(raw))
        if expanded is None:
            gaps.append(f"{raw} names an environment variable that is not set")
            continue
        path = Path(expanded)
        if not path.exists():
            gaps.append(f"{path} does not exist on this machine")
            continue
        resolved.append(path)
    return resolved, gaps


def glob_names(policy: dict) -> set[str]:
    """Every directory name any glob entry claims, across the whole policy.

    Collected once and handed to each sweep so that no entry counts bytes that
    another entry already owns. See units_of_glob for what goes wrong without it.
    """
    names: set[str] = set()
    for entry in policy.get("reclaimers") or []:
        if entry.get("kind") != "glob":
            continue
        for pattern in entry.get("patterns") or []:
            names.add(pattern.rsplit("/", 1)[-1])
    return names


def measure(entry: dict, search_roots: list[Path], blocked: set[str]) -> dict:
    """One policy entry, measured. Never raises: a failure is an unknown."""
    kind = entry.get("kind")
    try:
        if kind == "command":
            return measure_command(entry)

        if kind == "glob":
            roots = (
                search_roots
                if entry.get("within") == "search_roots"
                else resolve_roots(entry)[0]
            )
            if not roots:
                return unknown("no search roots to sweep")
            units = units_of_glob(roots, entry.get("patterns") or [], blocked)
        elif kind == "directory_contents":
            roots, gaps = resolve_roots(entry)
            if not roots:
                return unknown("; ".join(gaps) or "no roots resolved")
            units = []
            for root in roots:
                units.extend(units_of_directory(root, entry.get("retain_days")))
        else:
            return unknown(f"unknown kind {kind!r}")
    except PermissionError as error:
        return unknown(f"permission denied: {error}")
    except OSError as error:
        return unknown(f"could not be walked: {error}")

    units.sort(key=lambda u: -u["bytes"])
    return {
        "bytes": sum(u["bytes"] for u in units),
        "files": sum(u["files"] for u in units),
        "unreadable": sum(u["unreadable"] for u in units),
        "units": units[:UNIT_LIMIT],
        "units_total": len(units),
    }


def anchor_of(path: Path) -> Path:
    """The volume a path sits on."""
    resolved = path.resolve()
    return Path(resolved.anchor or resolved.root or "/")


def volume_state(free: int, total: int, thresholds: dict) -> tuple[str, str, list[str]]:
    """(state, severity, the tests that fired) for one volume.

    Ratio and absolute are both checked and the worse result wins. Ten percent
    of a four-terabyte array is four hundred gigabytes and is fine; ten percent
    of a laptop is not, and a policy with only a ratio says the same thing about
    both.
    """
    if total <= 0:
        return "unknown", "unknown", ["total size reported as zero"]
    ratio = free / total
    free_gb = free / 10**9

    # Critical first, and the moment it fires the warn checks are not reported.
    # A volume that is both is only critical, and listing the warn thresholds
    # underneath doubles the length of the sentence a reader is skimming for
    # the one number in it.
    for level in ("critical", "warn"):
        fired = []
        limit = thresholds.get(f"{level}_below_free_ratio")
        if limit is not None and ratio < limit:
            fired.append(f"{ratio:.1%} free, under the {level} floor of {limit:.0%}")
        limit = thresholds.get(f"{level}_below_free_gb")
        if limit is not None and free_gb < limit:
            fired.append(f"{free_gb:.2f}GB free, under the {level} floor of {limit:g}GB")
        if fired:
            # Three semantic states, as every view here carries. `critical` is a
            # severity inside `warn`, not a fourth colour: both mean a person is
            # needed and the difference is how soon, which the words carry and a
            # new colour would not.
            return "warn", level, fired
    return "ok", "ok", []


def build(policy: dict, search_roots: list[Path], volumes: list[Path]) -> dict:
    thresholds = policy.get("thresholds") or {}
    blocked = glob_names(policy)

    targets = []
    for entry in policy.get("reclaimers") or []:
        measured = measure(entry, search_roots, blocked)
        targets.append(
            {
                "name": entry["name"],
                "title": entry.get("title", entry["name"]),
                "kind": entry.get("kind"),
                "safety": entry.get("safety"),
                "owner": entry.get("owner"),
                "why": (entry.get("why") or "").strip() or None,
                "note": (entry.get("note") or "").strip() or None,
                "measured": measured,
            }
        )

    # Every volume a target actually sits on, plus the ones the policy names.
    # Derived rather than listed: a cache junctioned onto another drive is
    # reported against the drive it is on, which is the whole point of asking.
    wanted = {str(anchor_of(v)): anchor_of(v) for v in volumes}
    for entry in policy.get("reclaimers") or []:
        for raw in (entry.get("roots") or []):
            expanded = expand(str(raw))
            if expanded:
                anchor = anchor_of(Path(expanded))
                wanted.setdefault(str(anchor), anchor)
    for root in search_roots:
        anchor = anchor_of(root)
        wanted.setdefault(str(anchor), anchor)

    volume_records = []
    for key in sorted(wanted):
        path = wanted[key]
        try:
            usage = shutil.disk_usage(str(path))
        except OSError as error:
            volume_records.append({"path": key, "usage": unknown(f"{error}")})
            continue
        state, severity, fired = volume_state(usage.free, usage.total, thresholds)
        volume_records.append(
            {
                "path": key,
                "total_bytes": usage.total,
                "used_bytes": usage.used,
                "free_bytes": usage.free,
                "free_ratio": round(usage.free / usage.total, 4) if usage.total else None,
                "state": state,
                "severity": severity,
                "thresholds_fired": fired,
            }
        )

    measured_targets = [t for t in targets if unknown_reason(t["measured"]) is None]
    reclaimable = {
        tier: sum(
            t["measured"]["bytes"] for t in measured_targets if t["safety"] == tier
        )
        for tier in SAFETY_TIERS
    }

    return {
        "schema": 1,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "generator": {
            "tool": "ci/disk_status.py",
            "policy": str(policy.get("_source", "ci/disk-policy.yaml")),
            "scope": (
                "one machine, one moment. Every figure below is true for "
                "whoever ran this and nobody else."
            ),
            "never_committed": (
                "this document is machine-scoped in full, so unlike "
                "harness-status.json it has no committable half and the tool "
                "refuses to write it inside the corpus"
            ),
            "thresholds": thresholds,
            "safety_tiers": list(SAFETY_TIERS),
            "safety_means": (
                "what it costs to get the bytes back: refetched, a download the "
                "owning tool repeats unprompted; rebuilt, a command a human "
                "runs; destructive, nothing comes back"
            ),
            "search_roots": [str(r) for r in search_roots],
            "measures_only": (
                "nothing in this tool deletes anything. ci/disk_reclaim.py acts, "
                "defaults to a dry run, and re-reads the filesystem rather than "
                "trusting this document"
            ),
        },
        "reading": {
            "refresh": "python ci/disk_status.py --write <path outside the corpus>",
            "staleness_budget_hours": STALENESS_BUDGET_HOURS,
            "human_view": "python ci/disk_dashboard.py disk-status.json --out disk.html",
            "agent_view": "python ci/disk_dashboard.py disk-status.json --format md",
            "remediate": "python ci/disk_reclaim.py",
            "unknown_convention": (
                '{"unknown": "<reason>"} is a value. It means the target could '
                "not be measured and says why. It is not zero and not empty -- a "
                "cache behind a permission error must never read as a cache with "
                "nothing in it."
            ),
            "do_not": [
                "quote a figure from this document without its generated_at",
                "commit this document, or any rendering of it: it is one machine",
                "read a reclaimable total as space you will get back -- it is the "
                "measured size of what the policy permits removing, and the "
                "tiers above refetched cost a rebuild",
                "delete anything by hand that ci/disk-policy.yaml does not name; "
                "add the entry instead, so the next person inherits the reasoning",
            ],
        },
        "totals": {
            "volumes": len(volume_records),
            "volumes_critical": sum(
                1 for v in volume_records if v.get("severity") == "critical"
            ),
            "volumes_warn": sum(1 for v in volume_records if v.get("severity") == "warn"),
            "volumes_unknown": sum(
                1 for v in volume_records if unknown_reason(v.get("usage")) is not None
            ),
            "targets": len(targets),
            "targets_measured": len(measured_targets),
            "targets_unknown": len(targets) - len(measured_targets),
            "reclaimable_bytes": reclaimable,
            "reclaimable_bytes_total": sum(reclaimable.values()),
        },
        "volumes": volume_records,
        "targets": targets,
    }


def load_policy(path: Path) -> dict:
    """The policy, or an exit. An unreadable policy is never a permissive one."""
    if not path.exists():
        sys.exit(f"disk_status: no policy at {path}")
    try:
        policy = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as error:
        sys.exit(f"disk_status: {path} did not parse: {error}")
    if not isinstance(policy, dict) or policy.get("schema") != 1:
        sys.exit(f"disk_status: {path} is not a schema 1 disk policy")

    for entry in policy.get("reclaimers") or []:
        name = entry.get("name", "<unnamed>")
        if entry.get("kind") not in KINDS:
            sys.exit(
                f"disk_status: {name} has kind {entry.get('kind')!r}, which is not "
                f"one of {', '.join(KINDS)}"
            )
        if entry.get("safety") not in SAFETY_TIERS:
            sys.exit(
                f"disk_status: {name} has safety {entry.get('safety')!r}. Every "
                f"entry states what it costs to get the bytes back, as one of "
                f"{', '.join(SAFETY_TIERS)} -- an unclassified target would be "
                "reclaimed at whatever tier happened to be permitted."
            )
    policy["_source"] = str(path)
    return policy


def gb(count: object) -> str:
    if not isinstance(count, (int, float)):
        return "unknown"
    return f"{count / 10**9:.1f}GB"


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--policy", type=Path, default=CI_DIR / "disk-policy.yaml")
    parser.add_argument("--write", type=Path, help="write the document here")
    parser.add_argument(
        "--search-root",
        action="append",
        type=Path,
        default=[],
        help="where this stack's clones live; repeatable",
    )
    parser.add_argument(
        "--volume",
        action="append",
        type=Path,
        default=[],
        help="an extra volume to measure, beyond the policy's",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="exit 2 if a volume is critical, 1 if any is low or unreadable",
    )
    args = parser.parse_args(argv)

    policy = load_policy(args.policy)

    search_roots = [p.resolve() for p in args.search_root] or [CORPUS.parent]
    volumes = list(args.volume)
    for raw in policy.get("volumes") or []:
        expanded = expand(str(raw))
        if expanded:
            volumes.append(Path(expanded))

    # Refused before the walk, not after. Measuring a 90GB cache and then
    # discovering the destination was rejected wastes the minutes that made
    # somebody reach for the tool.
    if args.write and inside_corpus(args.write):
        sys.exit(
            f"disk_status: refusing to write to {args.write}, which is inside "
            "the corpus.\n"
            "Every fact in this document is one machine at one moment -- free "
            "space, cache sizes, paths in a home directory -- and committing it "
            "would publish that as an organisation fact every later reader "
            "inherits. Unlike harness-status.json there is no committable half "
            "to fall back to; the reviewable artifact is ci/disk-policy.yaml.\n"
            "Write it somewhere outside the repository."
        )

    document = build(policy, search_roots, volumes)

    text = json.dumps(document, indent=2, ensure_ascii=False) + "\n"
    if args.write:
        args.write.write_text(text, encoding="utf-8", newline="\n")
        totals = document["totals"]
        print(
            f"wrote {args.write}: {totals['volumes']} volumes "
            f"({totals['volumes_critical']} critical, {totals['volumes_warn']} low), "
            f"{totals['targets_measured']} of {totals['targets']} targets measured"
        )
        for tier in SAFETY_TIERS:
            print(f"  {tier:<12} {gb(totals['reclaimable_bytes'][tier])}")
        if totals["targets_unknown"]:
            print(f"  {totals['targets_unknown']} targets could not be measured")
    elif not args.check:
        sys.stdout.write(text)

    if args.check:
        for volume in document["volumes"]:
            reason = unknown_reason(volume.get("usage"))
            if reason:
                print(f"{volume['path']}: unknown — {reason}")
                continue
            print(
                f"{volume['path']}: {gb(volume['free_bytes'])} free of "
                f"{gb(volume['total_bytes'])} "
                f"({volume['free_ratio']:.1%}) — {volume['severity']}"
            )
        totals = document["totals"]
        if totals["volumes_critical"]:
            return 2
        if totals["volumes_warn"] or totals["volumes_unknown"]:
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
