#!/usr/bin/env python3
"""Emit the harness status document: where every repository's PR slot stands.

Org-level tooling, copied nowhere. It is the collector half of a two-part
split this repository already uses once: a generator that talks to git, gh and
the filesystem and writes a document, and a renderer that reads only the
document. See ci/governance_status.py and ci/governance_render.py.

The split is not tidiness. A renderer that can run a command is a second place
a governance rule gets defined, and the two definitions drift. Everything the
dashboard shows must be a fact in this document or it is not shown.

TWO LAYERS, AND THEY ARE NOT THE SAME KIND OF FACT

  - `slots` is about the org, read over the network. It is true for everyone.
  - `local` is about one machine, read from one set of clones. It is true for
    whoever ran this and nobody else, and it is labelled that way in the
    document and in anything that renders it. It is included because the thing
    worth watching -- work sitting unpushed in a clone after a parallel session
    -- exists nowhere else. A dashboard that showed it as an org fact would be
    lying about its scope.

UNKNOWN IS A VALUE

Any fact this tool could not establish is written as `{"unknown": "<reason>"}`,
never omitted and never defaulted. A repository whose pull requests could not
be read must not render like a repository with none, because the second reads
as compliance and the first is an absence of evidence. This is the same
convention as governance-status.yaml, deliberately.

Usage:
    python ci/harness_status.py --write harness-status.json
    python ci/harness_status.py --write harness-status.json --no-local
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

CI_DIR = Path(__file__).resolve().parent
CORPUS = CI_DIR.parent
CHECK_ONE_PR = CORPUS / "project-seed" / "ci" / "check_one_pr.py"

# The corpus's own exemption, and the only one. See handbook/async-contract.md.
CORPUS_PER_BASE = ["project/*"]


def unknown(reason: str) -> dict:
    return {"unknown": reason}


def run(*args: str, cwd: Path | None = None) -> tuple[int, str, str]:
    result = subprocess.run(
        args,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=str(cwd) if cwd else None,
    )
    return result.returncode, (result.stdout or "").strip(), (result.stderr or "").strip()


def git(repo: Path, *args: str) -> tuple[int, str]:
    status, out, err = run("git", "-C", str(repo), *args)
    return status, out or err


def slot_layer(slug: str, per_base: list[str]) -> dict:
    """What check_one_pr.py says about this repository, as data.

    Invoked as a subprocess rather than imported so that this document records
    what the check actually does, including its exit status. An import would
    let this file's own reading of the rule diverge from the file CI runs.
    """
    args = [sys.executable, str(CHECK_ONE_PR), "--repo", slug, "--json"]
    for pattern in per_base:
        args += ["--per-base", pattern]
    status, out, err = run(*args)
    if not out:
        return unknown(f"check_one_pr produced no output: {err.splitlines()[0] if err else 'silent'}")
    try:
        payload = json.loads(out)
    except json.JSONDecodeError:
        return unknown(f"check_one_pr output was not JSON: {out.splitlines()[0][:120]}")
    payload["exit_status"] = status
    payload["compliant"] = not payload["violations"]
    return payload


def local_layer(path: Path) -> dict:
    """One clone, on one machine. Scope is in the key name for a reason."""
    if not (path / ".git").exists():
        return unknown(f"no clone at {path}")
    facts: dict = {"path": str(path)}
    _, facts["branch"] = git(path, "rev-parse", "--abbrev-ref", "HEAD")
    _, facts["head"] = git(path, "rev-parse", "HEAD")
    _, facts["head_at"] = git(path, "log", "-1", "--format=%cI")
    _, facts["head_subject"] = git(path, "log", "-1", "--format=%s")

    status, out = git(path, "status", "--porcelain")
    facts["dirty"] = len(out.splitlines()) if status == 0 and out else 0

    status, upstream = git(path, "rev-parse", "--abbrev-ref", "@{upstream}")
    if status == 0 and upstream:
        facts["upstream"] = upstream
        _, counts = git(path, "rev-list", "--left-right", "--count", f"{upstream}...HEAD")
        parts = counts.split()
        if len(parts) == 2:
            facts["behind"], facts["ahead"] = int(parts[0]), int(parts[1])
        else:
            facts["behind"] = facts["ahead"] = None
    else:
        facts["upstream"] = None
        facts["ahead"] = facts["behind"] = None
        facts["note"] = "no upstream: nothing on this branch is on a remote"
    return facts


def resolve(entry: dict, search_roots: list[Path]) -> Path | None:
    for candidate in entry.get("paths", []):
        for root in search_roots:
            probe = (root / candidate).resolve()
            if (probe / ".git").exists():
                return probe
    return None


def build(roster: list[dict], org: str, search_roots: list[Path], want_local: bool) -> dict:
    repositories = []
    for entry in roster:
        name = entry["name"]
        slug = f"{org}/{name}"
        record = {
            "name": name,
            "slug": slug,
            "role": entry.get("role", "unknown"),
            "phase": entry.get("phase", "unknown"),
            "note": entry.get("note"),
            "slots": slot_layer(
                slug, CORPUS_PER_BASE if entry.get("role") == "corpus" else []
            ),
        }
        if want_local:
            path = resolve(entry, search_roots)
            record["local"] = (
                local_layer(path)
                if path
                else unknown(
                    "not found on this machine; candidates: "
                    + ", ".join(entry.get("paths", []))
                )
            )
        repositories.append(record)

    measured = [r for r in repositories if "unknown" not in r["slots"]]
    return {
        "schema": 1,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "generator": {
            "tool": "ci/harness_status.py",
            "org": org,
            "rule": "one open pull request per repository, per contributor",
            "rule_source": "handbook/async-contract.md",
            "corpus_exemption": CORPUS_PER_BASE,
            "layers": ["slots"] + (["local"] if want_local else []),
            "local_layer_scope": (
                "one machine, one set of clones — true for whoever ran this and "
                "nobody else"
                if want_local
                else None
            ),
            "search_roots": [str(r) for r in search_roots] if want_local else [],
        },
        "totals": {
            "repositories": len(repositories),
            "slots_measured": len(measured),
            "slots_unknown": len(repositories) - len(measured),
            "compliant": sum(1 for r in measured if r["slots"]["compliant"]),
            "over_limit": sum(1 for r in measured if not r["slots"]["compliant"]),
        },
        "repositories": repositories,
    }


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--roster", type=Path, default=CI_DIR / "workspace.yaml")
    parser.add_argument("--org", default="quaternionmedia")
    parser.add_argument("--write", type=Path, help="write the document here")
    parser.add_argument("--search-root", action="append", type=Path, default=[])
    parser.add_argument(
        "--no-local",
        action="store_true",
        help="omit the machine-scoped layer entirely",
    )
    args = parser.parse_args(argv)

    document = yaml.safe_load(args.roster.read_text(encoding="utf-8"))
    roster = document.get("repositories") or []
    if not roster:
        sys.exit(f"harness_status: {args.roster} lists no repositories")

    search_roots = [p.resolve() for p in args.search_root] or [CORPUS.parent.parent]
    status = build(roster, args.org, search_roots, not args.no_local)

    text = json.dumps(status, indent=2, ensure_ascii=False) + "\n"
    if args.write:
        args.write.write_text(text, encoding="utf-8", newline="\n")
        totals = status["totals"]
        print(
            f"wrote {args.write}: {totals['repositories']} repositories, "
            f"{totals['compliant']} compliant, {totals['over_limit']} over limit, "
            f"{totals['slots_unknown']} unknown"
        )
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
