#!/usr/bin/env python3
"""The local development environment, measured against what the loop needs.

    uv run qm devloop                     # every section
    uv run qm devloop --section stability # one section; repeatable
    uv run qm devloop --org-folder PATH   # another root to look for clones in
    uv run qm devloop --deep              # per-clone git state; slower
    uv run qm devloop --json              # the same findings, machine-readable
    uv run qm devloop --check             # exit non-zero if the environment is short

ADVISORY, AND LOCAL ONLY. This reads the operator's filesystem, so it says
different things on two machines and belongs nowhere near CI -- a pull request
would go red for a reason its author cannot fix. `--check` exists for a local
pre-flight, not for a gate.

WHAT IT IS FOR. The deliverable is a corpus that accepts concurrent,
overlapping, asynchronous and conflicting feedback and iterates on data
(records/DRAFT-the-base-is-the-deliverable.md §1). Every one of those words is a
claim about a *working environment*, not about this repository alone: work
cannot be concurrent across repositories that are not checked out, and feedback
cannot be collected from clones nobody has.

WHAT IT CANNOT SEE. Anything not on this disk. A repository absent from
`inventory-public.json` is absent from the host as of that document's
`generated_at`, which may be stale; a clone this tool cannot find may exist
under a root it was not given. Both are reported as unknown rather than as zero.

PRIVACY. Private repositories are named nowhere. The public inventory carries
them as `ref`/`label` rather than `name`, and a local directory is named only
when it matches a public repository. This is not a nicety: a tool reading this
inventory wrote 34 private names into a committable artifact on 2026-08-16, and
that tool was this one's author.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
INVENTORY = ROOT / "inventory-public.json"
WORKSPACE = ROOT / "ci" / "workspace.yaml"
LEDGER = ROOT / "ledger.yaml"
POLICIES = ROOT / "ci" / "policy-registry.yaml"
GATES = ROOT / "ci" / "gate-registry.yaml"

SECTIONS = ("stability", "checkout", "surface", "recommendations")

# Where clones are looked for when nothing is passed. These are the parents of
# this repository, not a guess about anyone's layout: `--org-folder` adds more,
# and a root that does not exist is reported rather than skipped.
DEFAULT_ROOTS = (ROOT.parent, ROOT.parent.parent)


def load_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def load_yaml(path: Path) -> dict:
    if not path.is_file():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def display(entry: dict) -> str:
    """What this repository may be called in output.

    Public entries carry `name`; private ones carry `ref` and `label` and no
    name at all. Reading `name` unconditionally is both a crash and a leak
    waiting on a schema change, so every caller comes through here.
    """
    if entry.get("private"):
        return entry.get("label") or entry.get("ref") or "a private repository"
    return entry.get("name") or entry.get("label") or entry.get("ref") or "<unnamed>"


def public_names(inventory: dict) -> set[str]:
    """Repository names this tool is allowed to print for a local directory."""
    return {
        r["name"] for r in inventory.get("repositories", [])
        if r.get("name") and not r.get("private")
    }


def age_hours(stamp: str | None) -> float | None:
    if not stamp:
        return None
    try:
        when = datetime.strptime(stamp, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    except ValueError:
        return None
    return (datetime.now(timezone.utc) - when).total_seconds() / 3600


def git(args: list[str], cwd: Path) -> str:
    try:
        proc = subprocess.run(
            ["git", *args], cwd=str(cwd), capture_output=True, text=True, timeout=20
        )
    except (OSError, subprocess.TimeoutExpired):
        return ""
    return proc.stdout.strip() if proc.returncode == 0 else ""


# --- sections ---------------------------------------------------------------


def stability(ledger: dict) -> dict:
    entries = ledger.get("entries") or []
    recorded = ledger.get("passes") or []
    run = 0
    for entry in reversed(recorded):
        if entry.get("added_since_previous"):
            break
        run += 1
    return {
        "passes_recorded": len(recorded),
        "streak": run,
        "entries": len(entries),
        "open_entries": sum(1 for e in entries if e.get("status") == "open"),
        "missed_projection": sum(
            1 for e in entries if e.get("outcome_matched_projection") is False
        ),
        "last_pass": (recorded[-1].get("at") if recorded else None),
    }


def checkout(inventory: dict, roster: list[dict], roots: list[Path], deep: bool) -> dict:
    """Which of the org's repositories are on this disk, and in what state."""
    repos = inventory.get("repositories") or []
    wanted = [r for r in repos if r.get("in_roster")]
    active = [r for r in repos if not r.get("archived")]

    found: dict[str, Path] = {}
    allowed = public_names(inventory)
    unresolved_roots = [r for r in roots if not r.is_dir()]
    for root in roots:
        if not root.is_dir():
            continue
        for candidate in sorted(root.iterdir()):
            if not (candidate / ".git").exists():
                continue
            if candidate.name in allowed:
                found.setdefault(candidate.name, candidate)

    # A roster entry states where it expects to sit; resolving through the
    # roster's own `paths` finds clones the flat scan above cannot, because not
    # every clone is a direct child of a search root.
    for entry in roster:
        name = entry.get("name")
        if not name or name in found:
            continue
        for rel in entry.get("paths") or []:
            for root in roots:
                candidate = root / rel
                if (candidate / ".git").exists():
                    found[name] = candidate
                    break

    # Presence is decided from the ROSTER, which carries a name and expected
    # paths, and never from the inventory, whose private entries carry no name
    # at all. Joining on the inventory reported every private roster repository
    # as absent whether or not it was on the disk, because `None` is never a
    # key in `found` -- a confident claim the tool structurally could not make.
    missing = []
    for entry in roster:
        name = entry.get("name")
        if not name or name in found:
            continue
        missing.append(name if name in allowed else "a repository not listed publicly")

    states: list[dict] = []
    if deep:
        for name, path in sorted(found.items()):
            dirty = git(["status", "--porcelain"], path)
            branch = git(["rev-parse", "--abbrev-ref", "HEAD"], path)
            counts = git(["rev-list", "--left-right", "--count", "@{upstream}...HEAD"], path)
            behind, ahead = (counts.split() + ["?", "?"])[:2] if counts else ("?", "?")
            states.append({
                "name": name,
                "branch": branch or "unknown",
                "dirty_files": len(dirty.splitlines()) if dirty else 0,
                "ahead": ahead,
                "behind": behind,
            })

    return {
        "generated_at": inventory.get("generated_at"),
        "inventory_age_hours": age_hours(inventory.get("generated_at")),
        "on_host": len(repos),
        "active": len(active),
        "in_roster": len(roster),
        "roster_cloned_here": len(roster) - len(missing),
        "missing_from_disk": missing,
        "clones_found": len(found),
        "roots_searched": [str(r) for r in roots],
        "roots_absent": [str(r) for r in unresolved_roots],
        "deep": states,
    }


def surface(policies: dict, gates: dict) -> dict:
    entries = policies.get("policies") or []
    gate_rows = gates.get("gates") or []
    return {
        "policies": len(entries),
        "detected": sum(1 for p in entries if p.get("detector")),
        "undetectable": sum(1 for p in entries if p.get("detectable") is False),
        "planned": sum(
            1 for p in entries if not p.get("detector") and p.get("detector_planned")
        ),
        "unenforced": [
            p["id"] for p in entries
            if not p.get("detector") and p.get("detectable") is not False
        ],
        "gates": len(gate_rows),
        "gates_unbuilt": sum(1 for g in gate_rows if g.get("declared_built") is False),
    }


# --- recommendations --------------------------------------------------------


def recommendations(state: dict) -> list[dict]:
    """Ranked, each naming the command that would settle it.

    Ordered by what blocks the loop rather than by what is quick. A report whose
    author also wrote what it measures has every reason to grade generously, so
    the rules here are thresholds rather than judgements: each fires on a number
    the reader can check against the sections above.
    """
    out: list[dict] = []
    stab, check, surf = state["stability"], state["checkout"], state["surface"]

    if stab["passes_recorded"] == 0:
        out.append({
            "priority": 1, "topic": "stability",
            "finding": "no pass has been recorded, so stability is unknown rather than zero",
            "do": 'uv run qm ledger --pass --ran "<what you ran>"',
        })
    elif stab["streak"] == 0:
        out.append({
            "priority": 1, "topic": "stability",
            "finding": "the last pass added an entry, so the base moved under it",
            "do": "run the loop again and record the pass; the criterion is a pass that adds nothing",
        })

    if stab["open_entries"]:
        out.append({
            "priority": 2, "topic": "ledger",
            "finding": f"{stab['open_entries']} entr(ies) carry a projection nobody scored",
            "do": "uv run qm ledger --close <id> --outcome ... --cost ... --matched true|false|unknown",
        })

    for policy in surf["unenforced"]:
        out.append({
            "priority": 2, "topic": "policy",
            "finding": f"{policy} has no detector and is not declared undetectable",
            "do": "write the detector, or record why it cannot exist in ci/policy-registry.yaml",
        })

    if check["missing_from_disk"]:
        out.append({
            "priority": 3, "topic": "checkout",
            "finding": (
                f"{len(check['missing_from_disk'])} of {check['in_roster']} roster "
                f"repositories are not on this disk: {', '.join(check['missing_from_disk'])}"
            ),
            "do": "clone them under a search root, or pass --org-folder if they are elsewhere",
        })

    age = check["inventory_age_hours"]
    if age is None:
        out.append({
            "priority": 3, "topic": "inventory",
            "finding": "the inventory carries no readable timestamp, so its age is unknown",
            "do": "uv run qm inventory --write",
        })
    elif age > 168:
        out.append({
            "priority": 3, "topic": "inventory",
            "finding": f"the inventory is {age / 24:.0f} days old, past its 168-hour budget",
            "do": "uv run qm inventory --write",
        })

    for repo in check["deep"]:
        if repo["dirty_files"]:
            out.append({
                "priority": 4, "topic": "concurrency",
                "finding": (
                    f"{repo['name']} has {repo['dirty_files']} uncommitted file(s) on "
                    f"{repo['branch']} -- possibly another session's work"
                ),
                "do": "read the diff before writing there; handbook/async-contract.md",
            })
        if repo["ahead"] not in ("0", "?"):
            out.append({
                "priority": 4, "topic": "concurrency",
                "finding": f"{repo['name']} has {repo['ahead']} unpushed commit(s)",
                "do": "push, or find out whose they are",
            })

    return sorted(out, key=lambda r: r["priority"])


# --- rendering --------------------------------------------------------------


def render(state: dict, wanted: tuple[str, ...]) -> str:
    out: list[str] = ["Local development environment, measured against what the loop needs.", ""]

    if "stability" in wanted:
        s = state["stability"]
        out += ["## Base stability", ""]
        if s["passes_recorded"] == 0:
            out.append("  passes    none recorded -- unknown, which is not the same as stable")
        else:
            out.append(f"  passes    {s['passes_recorded']} recorded, "
                       f"{s['streak']} in a row adding nothing")
            out.append(f"  last      {s['last_pass']}")
        out += [
            f"  entries   {s['entries']} ({s['open_entries']} open, "
            f"{s['missed_projection']} missed their projection)",
            "",
            "  Stable means a full pass adds no entry. It does not mean correct:",
            "  a pass finds only what its checks look for.",
            "",
        ]

    if "checkout" in wanted:
        c = state["checkout"]
        out += ["## Org checkout", ""]
        out.append(f"  roster    {c['roster_cloned_here']} of {c['in_roster']} on this disk")
        out.append(f"  host      {c['on_host']} repositories, {c['active']} not archived")
        out.append(f"  found     {c['clones_found']} clone(s) under "
                   f"{len(c['roots_searched'])} root(s)")
        age = c["inventory_age_hours"]
        out.append("  measured  " + (f"{age:.0f}h ago" if age is not None
                                     else "unknown -- the inventory has no readable timestamp"))
        for missing in c["missing_from_disk"]:
            out.append(f"    absent  {missing}")
        for absent in c["roots_absent"]:
            out.append(f"    no root {absent}")
        if c["deep"]:
            out.append("")
            for repo in c["deep"]:
                flag = "  " if not repo["dirty_files"] else " *"
                out.append(f"   {flag} {repo['name']:<22} {repo['branch']:<28} "
                           f"{repo['dirty_files']} dirty, {repo['ahead']} ahead, "
                           f"{repo['behind']} behind")
        else:
            out.append("    (--deep reads each clone's branch, dirty files and drift)")
        out += ["", "  A repository absent here is absent from this disk, not from the org.", ""]

    if "surface" in wanted:
        s = state["surface"]
        out += [
            "## Governance surface", "",
            f"  policies  {s['policies']} -- {s['detected']} detected, "
            f"{s['undetectable']} cannot be, {s['planned']} planned",
            f"  gates     {s['gates']} built, {s['gates_unbuilt']} declared and unbuilt",
        ]
        for policy in s["unenforced"]:
            out.append(f"    open    {policy} has nothing durable behind it")
        out.append("")

    if "recommendations" in wanted:
        recs = state["recommendations"]
        out += ["## What to do next", ""]
        if not recs:
            out.append("  Nothing this tool can see. That is a statement about its "
                       "checks, not about the corpus.")
        for rec in recs:
            out.append(f"  [{rec['priority']}] {rec['topic']}: {rec['finding']}")
            out.append(f"      {rec['do']}")
        out.append("")

    out += [
        "This reads this disk. It says different things on another machine, and "
        "nothing here belongs in CI.",
    ]
    return "\n".join(out)


def gather(roots: list[Path], deep: bool) -> dict:
    inventory = load_json(INVENTORY)
    roster = (load_yaml(WORKSPACE).get("repositories") or [])
    state = {
        "stability": stability(load_yaml(LEDGER)),
        "checkout": checkout(inventory, roster, roots, deep),
        "surface": surface(load_yaml(POLICIES), load_yaml(GATES)),
    }
    state["recommendations"] = recommendations(state)
    return state


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--section", action="append", choices=SECTIONS,
                        help="report only this section; repeatable")
    parser.add_argument("--org-folder", action="append", default=[],
                        help="another root to look for clones in; repeatable")
    parser.add_argument("--deep", action="store_true",
                        help="read each clone's branch, dirty files and drift")
    parser.add_argument("--json", action="store_true", help="machine-readable")
    parser.add_argument("--check", action="store_true",
                        help="local pre-flight: exit non-zero if the environment is short")
    args = parser.parse_args(argv)

    roots = [Path(p).expanduser() for p in args.org_folder] or list(DEFAULT_ROOTS)
    state = gather(roots, args.deep)

    if args.json:
        print(json.dumps(state, indent=2, default=str))
        return 0

    wanted = tuple(args.section) if args.section else SECTIONS
    print(render(state, wanted))

    if args.check:
        blocking = [r for r in state["recommendations"] if r["priority"] <= 2]
        if blocking:
            print(f"\n{len(blocking)} finding(s) at priority 2 or above.", file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
