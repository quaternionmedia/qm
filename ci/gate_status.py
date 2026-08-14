#!/usr/bin/env python3
"""Write the gate status document: what governs, and what each gate cannot see.

Org-level tooling, copied nowhere. This is the *document* half of the shape
`handbook/generated-documents.md` describes -- the only piece here that talks
to the filesystem and the host. `ci/gate_dashboard.py` renders it and does
nothing else.

THREE LAYERS, AND THEY ARE NOT INTERCHANGEABLE

  claim        ci/gate-registry.yaml. What a human asserts each gate does and,
               more importantly, what it cannot see. Never inferred from a
               workflow file: inferring the claim from the artifact would
               redefine governance as a filename check, which is the exact
               substitution ci/workspace.yaml refuses in its own header.
  evidence     .github/workflows/. Which workflow files exist, what triggers
               them, which jobs they declare.
  enforcement  the host. Whether anything actually blocks a merge. It changes
               with no commit here, so it carries this document's staleness
               budget and `--no-host` writes it as `unknown` rather than as
               absent.

A gate declared and never built is kept, not dropped. That count is the honest
measure of how much of this governance is still customary, and deleting an
entry to make a page green is the one edit the registry forbids.

Usage:
    python ci/gate_status.py --write gate-status.json
    python ci/gate_status.py --no-host --write gate-status.json
    python ci/gate_status.py --check gate-status.json
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
DEFAULT_REGISTRY = ROOT / "ci" / "gate-registry.yaml"
DEFAULT_WORKFLOWS = ROOT / ".github" / "workflows"
DEFAULT_ORG_REPO = "quaternionmedia/qm"

OK, WARN, UNKNOWN = "ok", "warn", "unknown"


def unknown(reason: str) -> dict:
    """The one spelling of a fact nobody could establish.

    Never omitted and never defaulted. A gate nobody could measure must not
    render like a gate with nothing wrong.
    """
    return {"unknown": reason}


def now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_registry(path: Path) -> list[dict]:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    gates = data.get("gates") or []
    if not gates:
        # An empty registry would make every count below vacuously clean, which
        # is how this corpus's lint globs have failed before.
        raise SystemExit(f"{path}: no gates declared -- nothing would be measured")
    return gates


def discover(workflows: Path) -> dict[str, dict]:
    """What is actually in .github/workflows/, keyed by filename.

    Triggers come from the parsed document, not a text scan: PyYAML parses the
    `on:` key as the boolean True, and a grep for "on:" also matches
    `python-version:` and every comment mentioning it.
    """
    if not workflows.is_dir():
        return {}
    found: dict[str, dict] = {}
    for path in sorted(workflows.glob("*.yml")):
        try:
            doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError as exc:
            found[path.name] = {"unreadable": str(exc).splitlines()[0]}
            continue
        triggers = doc.get(True, doc.get("on"))
        if isinstance(triggers, dict):
            triggers = sorted(triggers)
        elif isinstance(triggers, str):
            triggers = [triggers]
        found[path.name] = {
            "name": doc.get("name"),
            "triggers": sorted(triggers or []),
            "jobs": sorted(doc.get("jobs") or {}),
        }
    return found


def read_enforcement(repo: str) -> dict:
    """What the host blocks a merge on. Never guessed, never defaulted."""
    proc = subprocess.run(
        ["gh", "api", f"repos/{repo}/rulesets"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout or "").strip().splitlines()[:1]
        return unknown(f"could not read rulesets: {detail[0] if detail else 'no detail'}")
    try:
        rulesets = json.loads(proc.stdout or "[]")
    except json.JSONDecodeError as exc:
        return unknown(f"rulesets response was not JSON: {exc}")

    proc = subprocess.run(
        ["gh", "api", f"repos/{repo}/branches/main/protection"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    # A 404 here is a real answer -- no protection -- and any other failure is
    # not. Collapsing the two would report an unreadable repository as an
    # unprotected one.
    combined = proc.stdout + proc.stderr
    if proc.returncode != 0 and "Not Found" not in combined and "Branch not protected" not in combined:
        return unknown(f"rulesets read, branch protection did not: {combined.strip().splitlines()[:1]}")

    return {
        "repository": repo,
        "rulesets_applied": len(rulesets),
        "ruleset_names": sorted(r.get("name", "?") for r in rulesets),
        "branch_protection_on_main": proc.returncode == 0,
        "blocks_a_merge": bool(rulesets) or proc.returncode == 0,
    }


def gate_row(gate: dict, found: dict[str, dict]) -> dict:
    """One gate, with its evidence attached and a state that cannot flatter it."""
    workflow = gate.get("workflow")
    declared_built = bool(gate.get("exists"))
    row = {
        "id": gate.get("id"),
        "gates": gate.get("gates") or [],
        "seed": bool(gate.get("seed")),
        "external": bool(gate.get("external")),
        "declared_built": declared_built,
        "workflow": workflow,
        "job": gate.get("job"),
        "runs": gate.get("runs") or [],
        "enforces": gate.get("enforces") or [],
        "refuses": " ".join((gate.get("refuses") or "").split()) or unknown(
            "the registry does not say what this refuses"
        ),
        "cannot_see": " ".join((gate.get("cannot_see") or "").split()) or unknown(
            "the registry does not say what this cannot see, which is a gap "
            "rather than a clean bill"
        ),
    }
    if gate.get("note"):
        row["note"] = " ".join(gate["note"].split())

    if not declared_built:
        row["evidence"] = unknown("declared and not built, so there is nothing to inspect")
        row["state"] = WARN
        return row

    if gate.get("external"):
        # An installed application has no workflow file to read. Reporting it
        # `ok` would assert something nobody here can check.
        row["evidence"] = unknown(
            "an installed application with no workflow file in this repository; "
            "nothing here can read its configuration"
        )
        row["state"] = UNKNOWN
        return row

    evidence = found.get(workflow)
    if evidence is None:
        row["evidence"] = unknown(f"{workflow} is not in the workflows directory")
        row["state"] = WARN
        return row
    if "unreadable" in evidence:
        row["evidence"] = unknown(f"{workflow} did not parse: {evidence['unreadable']}")
        row["state"] = UNKNOWN
        return row

    job_declared = gate.get("job") in evidence.get("jobs", [])
    row["evidence"] = {
        "present": True,
        "workflow_name": evidence.get("name"),
        "triggers": evidence.get("triggers", []),
        "jobs": evidence.get("jobs", []),
        "job_declared": job_declared,
    }
    row["state"] = OK if job_declared else WARN
    return row


def build(registry: Path, workflows: Path, repo: str, host: bool) -> dict:
    gates = load_registry(registry)
    found = discover(workflows)
    rows = [gate_row(g, found) for g in gates]

    claimed = {g.get("workflow") for g in gates if g.get("workflow")}
    undeclared = sorted(set(found) - claimed)

    return {
        "schema": SCHEMA,
        "generated_at": now(),
        "generator": {
            "tool": "ci/gate_status.py",
            "registry": registry.relative_to(ROOT).as_posix() if registry.is_relative_to(ROOT) else str(registry),
            "workflows": workflows.relative_to(ROOT).as_posix() if workflows.is_relative_to(ROOT) else str(workflows),
            "layers": ["claim", "evidence", "enforcement"],
            "claim_layer_is_not_evidence": (
                "refuses, cannot_see, enforces and gates come from "
                "ci/gate-registry.yaml and record what a human stated. They are "
                "never derived from a workflow file."
            ),
            "gate_states": [OK, WARN, UNKNOWN],
            "states_are_not_a_score": (
                "ok means the declared workflow and job are on disk. It does not "
                "mean the gate is effective, required to merge, or tested."
            ),
        },
        "reading": {
            "refresh": "uv run qm docs generate",
            "refresh_without_the_cli": "python ci/gate_status.py --write gate-status.json",
            "staleness_budget_hours": 168,
            "human_view": "python ci/gate_dashboard.py gate-status.json --out gates.html",
            "agent_view": "uv run qm gates",
            "faithfulness_check": "python ci/gate_status.py --check gate-status.json",
            "unknown_convention": (
                '{"unknown": "<reason>"} is a value. It means the fact could not '
                "be established and says why. It is not zero, not empty, and not "
                "compliant -- a gate nobody could measure must never be read as a "
                "gate with nothing wrong."
            ),
            "do_not": [
                "quote a figure from this document without its generated_at",
                "read `ok` as `required to merge` -- that is the enforcement layer",
                "read `ok` as `tested` -- no gate here has a mutation pass",
                "drop a gate whose declared_built is false to make a view green",
                "regenerate this in CI with the host layer: it reads the host, so "
                "an unrelated pull request would go red for a reason its author "
                "cannot fix. --check reads the local layers only, and is safe there",
            ],
        },
        "enforcement": read_enforcement(repo) if host else unknown(
            "--no-host was passed, so the host was not asked what it requires"
        ),
        "totals": {
            "gates": len(rows),
            "built": sum(1 for r in rows if r["declared_built"]),
            "declared_not_built": sum(1 for r in rows if not r["declared_built"]),
            "by_state": {s: sum(1 for r in rows if r["state"] == s) for s in (OK, WARN, UNKNOWN)},
            "gate_main": sum(1 for r in rows if "main" in r["gates"]),
            "seed": sum(1 for r in rows if r["seed"]),
            "undeclared_workflows": len(undeclared),
        },
        "gates": rows,
        "undeclared_workflows": undeclared,
    }


def local_layers(document: dict) -> dict:
    """Everything a check can verify offline -- the claim and evidence layers.

    `enforcement` and `generated_at` are excluded on purpose: both change
    without any commit here, so including them would make the faithfulness
    check fail for reasons a pull request cannot fix.
    """
    return {
        "schema": document.get("schema"),
        "generator": document.get("generator"),
        "reading": document.get("reading"),
        "totals": {k: v for k, v in (document.get("totals") or {}).items()},
        "gates": document.get("gates"),
        "undeclared_workflows": document.get("undeclared_workflows"),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--registry", default=str(DEFAULT_REGISTRY))
    parser.add_argument("--workflows", default=str(DEFAULT_WORKFLOWS))
    parser.add_argument("--repo", default=DEFAULT_ORG_REPO)
    parser.add_argument("--no-host", action="store_true", help="write enforcement as unknown")
    parser.add_argument("--write", help="write the document here")
    parser.add_argument("--check", help="fail if this document's local layers have drifted")
    args = parser.parse_args(argv)

    if args.check:
        target = Path(args.check)
        if not target.is_file():
            print(f"{args.check}: not present. Run the refresh command.", file=sys.stderr)
            return 1
        committed = json.loads(target.read_text(encoding="utf-8"))
        fresh = build(Path(args.registry), Path(args.workflows), args.repo, host=False)
        if local_layers(committed) != local_layers(fresh):
            print(
                f"{args.check} no longer describes ci/gate-registry.yaml and the "
                f"workflows on disk.\nRun: python ci/gate_status.py --write {args.check}",
                file=sys.stderr,
            )
            return 1
        print(f"{args.check}: claim and evidence layers match the repository.")
        print("The enforcement layer is not checked here -- it changes on the host.")
        return 0

    document = build(Path(args.registry), Path(args.workflows), args.repo, host=not args.no_host)

    if args.write:
        Path(args.write).write_text(
            json.dumps(document, indent=2) + "\n", encoding="utf-8", newline="\n"
        )
        print(f"wrote {args.write}")
        return 0

    json.dump(document, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
