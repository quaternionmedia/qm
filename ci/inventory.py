#!/usr/bin/env python3
"""Every repository the org has, against what the corpus knows about.

    uv run qm inventory
    uv run qm inventory --write
    uv run qm inventory --resolve private-03

WHY. `ci/workspace.yaml` holds 14 repositories. The org has 110. Every plan this
corpus has written -- adoption, propagation, the phase ladder, the harness
status -- was scoped to the 14, and nothing said the other 96 existed. A roster
that omits a repository does not merely miss it: it makes the org invisible to
its own planning, and the omission looks exactly like a decision.

THREE FILES, SPLIT BY WHAT MAY LEAVE THE MACHINE

    inventory-public.json    public repositories by name, plus counts and
                             references standing in for the rest. Committable.
    inventory-private.json   reference -> private repository name. Never.
    inventory-local.json     what is cloned on this disk, and where. Never.

**The split is the control, not the redaction.** An earlier version of this file
produced one document and filtered the sensitive fields out of it. That works
until a filter has a bug, and then a single logic error publishes the names of a
private organisation irreversibly. A public file that never receives private
names cannot leak them however broken this code is, so the boundary is a file
boundary and the two gitignored files are the second layer rather than the first.

That earlier version wrote 34 private repository names and 28 absolute paths
carrying the operator's username into the working tree of a public repository,
and was one command from being pushed when the reviewer stopped it. It had
reintroduced a problem `ci/governance_status.py` already solved -- that file
records `private_repository_names_listed: false` -- because assistant-2026-08
was run at the problem without reading that file first.

PRIVATE REPOSITORIES ARE COUNTED AND REFERENCED, NEVER DROPPED. Omitting them
would be the easy fix and the wrong one: a census that silently loses a third of
its subject is a census nobody can act on. So the public file carries

    private-01   ->  "quaternionmedia private repo 1"

with the name only in the private file. References are assigned by creation
order, which is append-only, so `private-03` means the same repository next
month and in every document that cites it. `--resolve` reads the mapping back on
a machine that has it.

WHAT IT CANNOT DO. It cannot see a repository the credential cannot read, a
clone outside the search roots, or anything on a machine that is not this one --
which is most of what `plans/data-collection-pathways.md` cares about. Those are
unknown, never absent.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

SCHEMA = 1
ROOT = Path(__file__).resolve().parent.parent
DEFAULT_ORG = "quaternionmedia"

PUBLIC = "inventory-public.json"
PRIVATE = "inventory-private.json"
LOCAL = "inventory-local.json"

NEVER_COMMIT = (
    "Machine-scoped. Gitignored on purpose. Do not commit this file, paste from "
    "it, or quote it in anything that leaves this machine."
)


def unknown(reason: str) -> dict:
    return {"unknown": reason}


def now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def host_repositories(org: str) -> list[dict] | dict:
    proc = subprocess.run(
        ["gh", "repo", "list", org, "--limit", "500", "--json",
         "name,isPrivate,isArchived,isFork,updatedAt,createdAt,primaryLanguage,diskUsage"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    if proc.returncode != 0:
        detail = (proc.stderr or "").strip().splitlines()[:1]
        return unknown(f"could not list {org}: {detail[0] if detail else 'no detail'}")
    try:
        return json.loads(proc.stdout or "[]")
    except json.JSONDecodeError as exc:
        return unknown(f"repo list was not JSON: {exc}")


def roster_names(path: Path) -> tuple[dict[str, dict], dict | None]:
    if not path.is_file():
        return {}, unknown(f"{path} is not present")
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    entries = data.get("repositories") or []
    return {e["name"]: e for e in entries if e.get("name")}, None


def assign_references(private: list[dict], org: str) -> dict[str, dict]:
    """name -> {ref, label}, ordered by creation date.

    Creation order is append-only: a repository made tomorrow takes the next
    number and never renumbers the ones before it. Ordering by name or by hash
    would shift every reference each time the org gained a repository, which
    would make a reference in a six-month-old document point somewhere else.
    """
    ordered = sorted(private, key=lambda r: (r.get("createdAt") or "", r["name"]))
    return {
        repo["name"]: {"ref": f"private-{i:02d}", "label": f"{org} private repo {i}"}
        for i, repo in enumerate(ordered, start=1)
    }


def local_clone(name: str, entry: dict | None, search_roots: list[Path]) -> str | None:
    """Where this repository is cloned, or None. The path is local-file-only."""
    candidates = list((entry or {}).get("paths") or []) + [name, f"qm/{name}"]
    for candidate in candidates:
        for root in search_roots:
            path = root / candidate
            if (path / ".git").exists():
                return str(path.resolve())
    return None


def build(org: str, roster_path: Path,
          search_roots: list[Path]) -> tuple[dict, dict, dict]:
    """Returns (public, private, local). Only the first may ever be committed."""
    host = host_repositories(org)
    roster, roster_problem = roster_names(roster_path)

    if isinstance(host, dict):
        return ({"schema": SCHEMA, "generated_at": now(), "host": host,
                 "repositories": [], "totals": {}}, {}, {})

    references = assign_references([r for r in host if r.get("isPrivate")], org)
    host_names = {r["name"] for r in host}

    public_rows, private_names, local_rows = [], {}, {}
    for r in sorted(host, key=lambda x: x["name"]):
        name = r["name"]
        entry = roster.get(name)
        private = bool(r.get("isPrivate"))
        clone = local_clone(name, entry, search_roots)

        row = {
            "private": private,
            "fork": bool(r.get("isFork")),
            "archived": bool(r.get("isArchived")),
            "updated_at": r.get("updatedAt"),
            "created_at": r.get("createdAt"),
            "language": (r.get("primaryLanguage") or {}).get("name"),
            "disk_usage_kb": r.get("diskUsage"),
            "in_roster": entry is not None,
            "roster_phase": (entry or {}).get("phase"),
            "cloned_here": clone is not None,
        }
        if private:
            row.update(references[name])
            private_names[references[name]["ref"]] = name
            key = references[name]["ref"]
        else:
            row["name"] = name
            key = name
        public_rows.append(row)
        if clone:
            local_rows[key] = clone

    public_rows.sort(key=lambda r: (r["private"], r.get("name") or r.get("ref")))
    in_roster_only = sorted(set(roster) - host_names)

    public = {
        "schema": SCHEMA,
        "generated_at": now(),
        "generator": {
            "tool": "ci/inventory.py",
            "produced_by": "assistant-2026-08",
            "org": org,
            "private_repository_names_listed": False,
            "absolute_paths_written": False,
            "private_repositories_referenced_as": "private-NN, by creation order",
            "companion_files": {
                PRIVATE: "reference -> name. Gitignored, never committed.",
                LOCAL: "clone paths on one machine. Gitignored, never committed.",
            },
            "roster_is_a_claim": (
                "ci/workspace.yaml is a human's list. Presence in this inventory "
                "is not adoption, not a backlog, and not a phase claim."
            ),
        },
        "reading": {
            "refresh": "uv run qm inventory --write",
            "resolve": "uv run qm inventory --resolve private-03",
            "staleness_budget_hours": 168,
            "do_not": [
                "read this as a list of repositories that should adopt governance",
                "read `cloned_here: false` as a repository that does not exist",
                "commit either companion file, or quote a resolved name anywhere",
                "quote a count without generated_at -- the org gains repositories",
            ],
        },
        "roster_problem": roster_problem,
        "totals": {
            "on_host": len(host_names),
            "in_roster": len(roster),
            "on_host_not_in_roster": sum(1 for r in public_rows if not r["in_roster"]),
            "in_roster_not_on_host": len(in_roster_only),
            "cloned_here": sum(1 for r in public_rows if r["cloned_here"]),
            "private": sum(1 for r in public_rows if r["private"]),
            "forks": sum(1 for r in public_rows if r["fork"]),
            "archived": sum(1 for r in public_rows if r["archived"]),
        },
        "in_roster_not_on_host": in_roster_only,
        "repositories": public_rows,
    }

    private_doc = {"generated_at": now(), "warning": NEVER_COMMIT,
                   "references": private_names}
    local_doc = {"generated_at": now(), "warning": NEVER_COMMIT,
                 "search_roots": [str(r) for r in search_roots],
                 "clones": local_rows}
    return public, private_doc, local_doc


def render(doc: dict) -> str:
    host = doc.get("host")
    if isinstance(host, dict) and "unknown" in host:
        return f"inventory: {host['unknown']}"
    t = doc["totals"]
    out = [
        f"inventory of {doc['generator']['org']} at {doc['generated_at']}",
        "",
        f"  on the host          {t['on_host']}",
        f"  in the roster        {t['in_roster']}",
        f"  host, not roster     {t['on_host_not_in_roster']}   <- the corpus cannot see these",
        f"  cloned here          {t['cloned_here']}",
        f"  private {t['private']}   forks {t['forks']}   archived {t['archived']}",
        "",
        "  Private repositories are referenced, not named. Names and clone paths",
        f"  live in {PRIVATE} and {LOCAL}, both gitignored.",
        "",
    ]
    missing = [r for r in doc["repositories"] if not r["in_roster"]]
    if missing:
        out.append(f"not in the roster ({len(missing)}):")
        for r in missing:
            flags = "".join(["F" if r["fork"] else " ",
                             "A" if r["archived"] else " ",
                             "L" if r["cloned_here"] else " "])
            out.append(f"  [{flags}] {r.get('name') or r['label']}")
        out += ["", "  F fork  A archived  L cloned here", ""]
    out.append("Presence here is not adoption. This lists what exists, nothing more.")
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--org", default=DEFAULT_ORG)
    parser.add_argument("--roster", default=str(ROOT / "ci" / "workspace.yaml"))
    parser.add_argument("--search-root", action="append", default=None)
    parser.add_argument("--out-dir", default=str(ROOT),
                        help="where the three files are written")
    parser.add_argument("--write", action="store_true",
                        help=f"write {PUBLIC}, {PRIVATE} and {LOCAL}")
    parser.add_argument("--resolve", metavar="REF",
                        help="print the name behind a reference, from the local file")
    args = parser.parse_args(argv)

    out_dir = Path(args.out_dir)

    if args.resolve:
        path = out_dir / PRIVATE
        if not path.is_file():
            print(f"no {PRIVATE} here. Run `uv run qm inventory --write` on the "
                  f"machine with the credential.", file=sys.stderr)
            return 1
        name = (json.loads(path.read_text(encoding="utf-8")).get("references") or {}
                ).get(args.resolve)
        if not name:
            print(f"{args.resolve} is not in {PRIVATE}.", file=sys.stderr)
            return 1
        print(name)
        return 0

    roots = [Path(r).resolve() for r in (args.search_root or [ROOT.parent, ROOT.parent.parent])]
    public, private_doc, local_doc = build(args.org, Path(args.roster), roots)

    if args.write:
        for name, doc in ((PUBLIC, public), (PRIVATE, private_doc), (LOCAL, local_doc)):
            if not doc:
                continue
            (out_dir / name).write_text(json.dumps(doc, indent=2) + "\n",
                                        encoding="utf-8", newline="\n")
        print(f"wrote {PUBLIC}  (committable)")
        print(f"wrote {PRIVATE}, {LOCAL}  (gitignored -- do not commit)")
        return 0

    print(render(public))
    return 0


if __name__ == "__main__":
    sys.exit(main())
