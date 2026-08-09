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

# Where the committed copy lives. An agent that cannot guess this path reads
# nothing, so it is fixed rather than passed, and named in AGENTS.md.
COMMITTED = CORPUS / "harness-status.json"

# How long this document may be quoted before it has to be re-derived. Pull
# request slots turn over in hours -- six sessions produced eight in a day --
# so a figure from yesterday describes an organisation that no longer exists.
# This is a budget for *quoting*, not for reading: a stale document still says
# true things about the commit it names, and it says them with a date attached.
STALENESS_BUDGET_HOURS = 24


def unknown(reason: str) -> dict:
    return {"unknown": reason}


def inside_corpus(path: Path) -> bool:
    """Whether this path would land in the repository, and so in a commit."""
    try:
        path.resolve().relative_to(CORPUS.resolve())
    except ValueError:
        return False
    return True


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


# The seed artifacts a project carries once it has adopted the constitution.
# Per the phase-ladder record these are a PRECONDITION for v0.0.1 and never a
# proof of it: a complete set means a human may now assert governance, never
# that they have. So this layer reports `met` and `incomplete` and no verdict
# above them, and the word `adopted` appears nowhere in what it emits.
GOVERNANCE_ARTIFACTS = ("submodule", "ide", "workflows", "licensing")


def governance_evidence(project: dict | None) -> dict:
    """What has actually landed on a project's default branch.

    Read out of governance-status.yaml, which is generated from git and the
    host. Nothing here consults the roster: the roster holds what somebody
    claimed, and a check that reads a claim to decide whether the claim is true
    is not a check.

    Work sitting in an open pull request is work and is not evidence. That gap
    is the whole reason this corpus opens draft pull requests, and crediting
    the intent here would erase it.
    """
    if project is None:
        return unknown(
            "no project/<name> branch in the corpus, so there is nothing to read"
        )

    adoption = project.get("adoption") or {}
    if "unknown" in adoption:
        return unknown(str(adoption["unknown"]))

    submodule = adoption.get("submodule") or {}
    missing = []
    if not submodule.get("corpus_mounted_at"):
        missing.append("submodule")
    elif not submodule.get("branch"):
        missing.append("submodule branch")
    if adoption.get("ide_missing"):
        missing.append("ide")
    if adoption.get("seed_workflow_filenames_absent"):
        missing.append("workflows")
    if len(adoption.get("licensing") or []) < 2:
        missing.append("licensing")

    branch = project.get("branch") or {}
    return {
        "precondition": "met" if not missing else "incomplete",
        "missing": missing,
        "detail": {
            "submodule": submodule.get("corpus_mounted_at"),
            "submodule_branch": submodule.get("branch"),
            "ide_present": len(adoption.get("ide") or []),
            "ide_absent": len(adoption.get("ide_missing") or []),
            "workflows_present": len(adoption.get("seed_workflow_filenames_present") or []),
            "workflows_absent": len(adoption.get("seed_workflow_filenames_absent") or []),
            "licensing_present": len(adoption.get("licensing") or []),
        },
        "behind_corpus": branch.get("behind_corpus"),
        "observed_at": project.get("observed_at"),
        "asserted_by": None,
        "asserts": (
            "a complete artifact set means a human may assert v0.0.1, never "
            "that they have"
        ),
    }


def load_governance(path: Path) -> tuple[dict[str, dict], str | None]:
    """The status document's projects, keyed by name, or the reason there are none."""
    if not path.exists():
        return {}, f"no governance status document at {path}"
    try:
        document = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as error:
        return {}, f"{path} did not parse: {error}"
    projects = document.get("projects")
    if not projects:
        return {}, f"{path} lists no projects"
    return {p["name"]: p for p in projects}, None


def resolve(entry: dict, search_roots: list[Path]) -> Path | None:
    for candidate in entry.get("paths", []):
        for root in search_roots:
            probe = (root / candidate).resolve()
            if (probe / ".git").exists():
                return probe
    return None


def build(
    roster: list[dict],
    org: str,
    search_roots: list[Path],
    want_local: bool,
    governance: dict[str, dict] | None = None,
    governance_gap: str | None = None,
) -> dict:
    repositories = []
    for entry in roster:
        name = entry["name"]
        slug = f"{org}/{name}"
        record = {
            "name": name,
            "slug": slug,
            "role": entry.get("role", "unknown"),
            # The claim, carried verbatim with its provenance. A view that
            # loses `phase_source` has turned a default into a finding.
            "phase": entry.get("phase", "unknown"),
            "phase_source": entry.get("phase_source", "unknown"),
            "note": entry.get("note"),
            "slots": slot_layer(
                slug, CORPUS_PER_BASE if entry.get("role") == "corpus" else []
            ),
        }
        if governance is not None:
            record["governance"] = (
                unknown(governance_gap)
                if governance_gap
                else governance_evidence(governance.get(name))
                if entry.get("role") != "corpus"
                else {"precondition": "n/a", "missing": [],
                      "asserts": "this repository is the corpus"}
            )
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
    governed = [
        r
        for r in repositories
        if isinstance(r.get("governance"), dict)
        and r["governance"].get("precondition") in ("met", "incomplete")
    ]
    return {
        "schema": 1,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "generator": {
            "tool": "ci/harness_status.py",
            "org": org,
            "rule": "one open pull request per repository, per contributor",
            "rule_source": "handbook/async-contract.md",
            "corpus_exemption": CORPUS_PER_BASE,
            "phase_ladder_source": "records/DRAFT-project-phase-ladder.md",
            "phase_layer_is_a_claim": (
                "phase and phase_source come from ci/workspace.yaml and record "
                "what a human stated. They are never derived from artifacts."
            ),
            "governance_layer_is_evidence": (
                "read from governance-status.yaml, on each project's default "
                "branch. Work in an open pull request is work, not evidence."
            ),
            "layers": ["phase", "slots"]
            + (["governance"] if governance is not None else [])
            + (["local"] if want_local else []),
            "local_layer_scope": (
                "one machine, one set of clones — true for whoever ran this and "
                "nobody else"
                if want_local
                else None
            ),
            "search_roots": [str(r) for r in search_roots] if want_local else [],
        },
        # Everything a reader needs in order to read this correctly, inside the
        # document. A convention that lives only in a handbook page is a
        # convention the next reader does not have: it opens the file, not the
        # page, and it opens it in a session that knows nothing.
        "reading": {
            "refresh": "python ci/harness_status.py --no-local --write harness-status.json",
            "staleness_budget_hours": STALENESS_BUDGET_HOURS,
            "human_view": "python ci/harness_dashboard.py harness-status.json --out status.html",
            "agent_view": "python ci/harness_dashboard.py harness-status.json --format md",
            "unknown_convention": (
                '{"unknown": "<reason>"} is a value. It means the fact could '
                "not be established and says why. It is not zero, not empty, "
                "and not compliant -- a repository nobody could measure must "
                "never be read as a repository with nothing wrong."
            ),
            "do_not": [
                "quote a figure from this document without its generated_at",
                "treat a phase as evidence: phase is what a human claimed",
                "treat the governance layer as a claim: it is what has landed",
                "regenerate this in CI -- it reads other repositories, so every "
                "unrelated pull request would go red for a reason its author "
                "cannot fix",
            ],
            "committed_copy_omits": ["local"],
        },
        "totals": {
            "repositories": len(repositories),
            "slots_measured": len(measured),
            "slots_unknown": len(repositories) - len(measured),
            "compliant": sum(1 for r in measured if r["slots"]["compliant"]),
            "over_limit": sum(1 for r in measured if not r["slots"]["compliant"]),
            # Counted over what could be read, never over the roster: a project
            # with no evidence is absent from both numerator and denominator,
            # so neither reads as a project measured and found wanting.
            "governance_readable": len(governed),
            "governance_precondition_met": sum(
                1 for r in governed if r["governance"]["precondition"] == "met"
            ),
            "phase_scaffolded": sum(
                1 for r in repositories if r.get("phase_source") == "scaffolded"
            ),
            "phase_stated_above_governance": sum(
                1
                for r in repositories
                if r.get("phase_source") == "stated" and r.get("phase") > "v0.0.1"
            ),
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
    parser.add_argument(
        "--governance",
        type=Path,
        default=CORPUS / "governance-status.yaml",
        help="the generated status document the evidence layer is read from",
    )
    parser.add_argument(
        "--no-governance",
        action="store_true",
        help="omit the evidence layer entirely",
    )
    args = parser.parse_args(argv)

    document = yaml.safe_load(args.roster.read_text(encoding="utf-8"))
    roster = document.get("repositories") or []
    if not roster:
        sys.exit(f"harness_status: {args.roster} lists no repositories")

    search_roots = [p.resolve() for p in args.search_root] or [CORPUS.parent.parent]

    governance, governance_gap = (None, None)
    if not args.no_governance:
        governance, governance_gap = load_governance(args.governance)
        # An absent or unparseable document makes every project's evidence
        # unknown -- with the reason -- rather than making the layer vanish. A
        # missing column reads as a column with nothing in it.
        if governance_gap:
            governance = {}

    status = build(
        roster,
        args.org,
        search_roots,
        not args.no_local,
        governance,
        governance_gap,
    )

    text = json.dumps(status, indent=2, ensure_ascii=False) + "\n"
    if args.write and not args.no_local and inside_corpus(args.write):
        sys.exit(
            f"harness_status: refusing to write the machine layer to "
            f"{args.write}, which is inside the corpus.\n"
            "That layer is one person's clones -- branch names, uncommitted "
            "counts, unpushed work -- and committing it would publish one "
            "machine's state as an organisation fact that every reader after "
            "you inherits.\n"
            "Pass --no-local for the committed copy, or --write somewhere "
            "outside the repository for a machine-scoped one."
        )
    if args.write:
        args.write.write_text(text, encoding="utf-8", newline="\n")
        totals = status["totals"]
        print(
            f"wrote {args.write}: {totals['repositories']} repositories, "
            f"{totals['compliant']} compliant, {totals['over_limit']} over limit, "
            f"{totals['slots_unknown']} unknown"
        )
        if governance is not None:
            print(
                f"  governance evidence: "
                f"{totals['governance_precondition_met']} of "
                f"{totals['governance_readable']} readable meet the v0.0.1 "
                f"precondition; {totals['phase_scaffolded']} phases scaffolded, "
                f"{totals['phase_stated_above_governance']} stated above governance"
            )
        if governance_gap:
            print(f"  governance evidence unreadable: {governance_gap}")
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
