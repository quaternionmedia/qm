#!/usr/bin/env python3
"""Every repository on one contract surface claims the same version, or none do.

    uv run qm interop            # what each repository claims
    uv run qm interop --verify   # run each host's replay and read what it covered
    uv run qm interop --check    # exit non-zero when a surface disagrees

The decision is `records/DRAFT-a-shared-tag-asserts-interoperability.md`: equal
numbers assert that these artifacts were proven to work together, and a change
on either side invalidates the claim for both.

ADVISORY, AND LOCAL ONLY. This reads sibling clones, so it says different things
on two machines and belongs nowhere near CI -- a runner has no siblings, and a
pull request that went red for a missing clone would be red for a reason its
author cannot fix. `--check` is a local pre-flight, not a gate. `ci/devloop.py`
carries the same constraint for the same reason.

TWO MODES, AND THEY PROVE DIFFERENT THINGS. Without `--verify` this reads
declared strings: it establishes that the repositories agree on a number, and
nothing about whether any of them replayed it. With `--verify` it runs each
implementation's own suite -- `npm` in one, `uv run pytest` in another -- and
reads one printed sentence from each, so the counts come from runs.

WHAT NEITHER MODE REACHES. A clean union is a sum compared against a total.
Two implementations could replay one case twice and miss another and still add
up, so `covers all` is necessary for the contract being proven and not
sufficient. `records/DRAFT-a-shared-tag-asserts-interoperability.md` 4 is the
clause, and this is the part of it no check here discharges.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from roster import load as roster_load  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "ci" / "interop-registry.yaml"
DEFAULT_ROOTS = (ROOT.parent, ROOT.parent.parent)

UNKNOWN = "unknown"


def clone_of(name: str, roots) -> Path | None:
    """Where a roster repository sits, or None. Resolved through the roster's
    own `paths`, so a clone that is not a direct child of a search root is
    found the way `ci/make_workspace.py` finds it."""
    candidates = []
    for entry in roster_load():
        if entry.get("name") == name:
            candidates = list(entry.get("paths") or [])
            break
    candidates.append(name)
    for rel in candidates:
        for root in roots:
            path = root / rel
            if (path / ".git").exists():
                return path
    return None


def declared_version(path: Path, spec: dict) -> str:
    """The version a file declares, or `unknown` with the reason folded in.

    Never raises and never returns a default that reads as agreement: a file
    that could not be read is `unknown`, and `unknown` never equals anything.
    """
    if not path.is_file():
        return UNKNOWN
    text = path.read_text(encoding="utf-8", errors="replace")
    if "json_key" in spec:
        try:
            return str(json.loads(text)[spec["json_key"]])
        except (json.JSONDecodeError, KeyError):
            return UNKNOWN
    found = re.search(spec["pattern"], text)
    return found.group("version") if found else UNKNOWN



def total_cases(surface: dict, roots) -> int | None:
    """How many cases the publisher governs, or None when it cannot be read."""
    spec = surface["publisher"]
    clone = clone_of(spec["repo"], roots)
    if clone is None:
        return None
    try:
        return len(json.loads((clone / spec["file"]).read_text(encoding="utf-8"))["cases"])
    except (OSError, json.JSONDecodeError, KeyError):
        return None


def prove(surface: dict, spec: dict, roots) -> dict:
    """Run one implementation's replay and read what it covered.

    The command is the host's own -- `npm` here, `uv run pytest` there -- and
    the only thing agreed across the seam is one printed sentence. Requiring a
    shared runner would be the coupling the seam exists to avoid.
    """
    out = {"repo": spec["repo"], "ran": False, "passed": False,
           "applicable": None, "not_applicable": None, "why": ""}
    clone = clone_of(spec["repo"], roots)
    if clone is None:
        out["why"] = "no clone on this disk"
        return out
    proves = spec.get("proves")
    if not proves:
        out["why"] = "declares no proving command"
        return out
    cwd = (clone / proves.get("cwd", ".")).resolve()
    # Resolve the launcher rather than trusting the bare name. On Windows `npm`
    # is `npm.cmd`, and `subprocess` without a shell finds neither -- it reports
    # "the system cannot find the file specified", which reads like a missing
    # repository rather than a missing shim. `shell=True` would fix it and hand
    # a registry string to a shell, which this file will not do.
    command = list(proves["command"])
    launcher = shutil.which(command[0])
    if launcher is None:
        out["why"] = f"{command[0]!r} is not on PATH"
        return out
    command[0] = launcher
    try:
        done = subprocess.run(command, cwd=str(cwd), capture_output=True,
                              encoding="utf-8", errors="replace", timeout=900, shell=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        out["why"] = f"could not run: {exc}"
        return out
    out["ran"] = True
    out["passed"] = done.returncode == 0
    text = (done.stdout or "") + (done.stderr or "")
    found = re.search(surface.get("coverage", ""), text) if surface.get("coverage") else None
    if found:
        out["applicable"] = int(found.group("applicable"))
        out["not_applicable"] = int(found.group("not_applicable"))
    else:
        out["why"] = "ran, and printed no coverage line this surface can read"
    return out

def read_surface(surface: dict, roots) -> dict:
    out = {"id": surface["id"], "what": surface.get("what", ""),
           "cannot_see": surface.get("cannot_see", ""), "claims": []}
    for role, spec in [("publisher", surface["publisher"])] + [
        ("implementation", s) for s in surface.get("implementations", [])
    ]:
        clone = clone_of(spec["repo"], roots)
        out["claims"].append({
            "repo": spec["repo"],
            "role": role,
            "version": declared_version(clone / spec["file"], spec) if clone else UNKNOWN,
            "where": spec["file"],
            "covers": spec.get("covers", ""),
            "absent": clone is None,
        })
    return out


def problems(surface: dict) -> list[str]:
    versions = {c["version"] for c in surface["claims"]}
    if len(versions) == 1 and UNKNOWN not in versions:
        return []
    found = []
    unknown = [c for c in surface["claims"] if c["version"] == UNKNOWN]
    for claim in unknown:
        why = "no clone on this disk" if claim["absent"] else f"{claim['where']} declares none"
        found.append(f"{surface['id']}: {claim['repo']} claims no version -- {why}")
    known = {c["version"] for c in surface["claims"]} - {UNKNOWN}
    if len(known) > 1:
        detail = ", ".join(
            f"{c['repo']} {c['version']}" for c in surface["claims"]
            if c["version"] != UNKNOWN
        )
        found.append(
            f"{surface['id']}: the surface disagrees -- {detail}. Equal numbers "
            f"assert these were proven to work together; unequal ones assert "
            f"nothing about the pair."
        )
    return found


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true",
                        help="exit non-zero when a surface disagrees")
    parser.add_argument("--verify", action="store_true",
                        help="run each implementation's replay and read what it covered")
    parser.add_argument("--org-folder", action="append", default=[],
                        help="another root to look for clones in")
    args = parser.parse_args(argv)

    roots = [Path(p) for p in args.org_folder] + list(DEFAULT_ROOTS)
    document = yaml.safe_load(REGISTRY.read_text(encoding="utf-8")) or {}
    surfaces = document.get("surfaces") or []
    if not surfaces:
        print(f"{REGISTRY}: registers no surface -- nothing was compared.",
              file=sys.stderr)
        return 1

    failed = []
    for surface in surfaces:
        read = read_surface(surface, roots)
        found = problems(read)
        failed.extend(found)
        print(f"\n## {read['id']}")
        for claim in read["claims"]:
            mark = "  " if claim["version"] != UNKNOWN else "??"
            print(f"  {mark} {claim['repo']:20} {claim['role']:14} {claim['version']}")
            if claim["covers"]:
                print(f"       covers {' '.join(claim['covers'].split())}")
        if found:
            for problem in found:
                print(f"  !! {problem}")
        else:
            print("  -- every repository on this surface claims the same version")
        if args.verify:
            governed = total_cases(surface, roots)
            proofs = [prove(surface, spec, roots)
                      for spec in surface.get("implementations", [])]
            print("\n  replayed, by running each host's own suite:")
            covered = 0
            for proof in proofs:
                if not proof["ran"]:
                    print(f"  ?? {proof['repo']:20} did not run -- {proof['why']}")
                    failed.append(
                        f"{read['id']}: {proof['repo']} did not run -- {proof['why']}")
                    continue
                verdict = "passing" if proof["passed"] else "FAILING"
                counts = (f"{proof['applicable']} applicable, "
                          f"{proof['not_applicable']} not applicable"
                          if proof["applicable"] is not None else proof["why"])
                ok = proof["passed"] and proof["applicable"] is not None
                print(f"  {'  ' if ok else '!!'} {proof['repo']:20} "
                      f"{verdict:8} {counts}")
                if not proof["passed"]:
                    failed.append(f"{read['id']}: {proof['repo']} replay failed")
                if proof["applicable"] is None:
                    failed.append(f"{read['id']}: {proof['repo']} -- {proof['why']}")
                else:
                    covered += proof["applicable"]
            if governed is None:
                failed.append(f"{read['id']}: the governed case count is unreadable")
            else:
                # NECESSARY, NOT SUFFICIENT. This compares a total against a
                # sum. Two hosts could replay one case twice and miss another
                # and still add up, so a clean union is not proof of coverage.
                # The registry's `cannot_see` says so, and it stays true.
                verdict = ("covers all" if covered == governed else
                           "LEAVES A GAP" if covered < governed else
                           "overlaps -- the halves are not disjoint")
                print(f"     union: {covered} of {governed} governed cases "
                      f"-- {verdict}")
                if covered != governed:
                    failed.append(
                        f"{read['id']}: the implementations cover {covered} of "
                        f"{governed} governed cases")
        if read["cannot_see"]:
            print(f"\n  cannot see: {' '.join(read['cannot_see'].split())}")

    if args.verify:
        print("\nEach count above came from that host's own suite, run just now. "
              "The union is a sum against a total, so it can be clean while a "
              "case is replayed twice and another missed.")
    else:
        print("\nA declared version is a claim that a set was replayed, not "
              "evidence that it was. Nothing here ran a test -- pass --verify "
              "to run them.")
    return 1 if (failed and args.check) else 0


if __name__ == "__main__":
    raise SystemExit(main())
