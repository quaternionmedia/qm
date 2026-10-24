#!/usr/bin/env python3
"""Run each family's own suites, and say what the batch establishes.

    uv run qm family-suite                  # every family that can report
    uv run qm family-suite --family core    # one, repeatable
    uv run qm family-suite --check          # exit non-zero on a failed member

The point is the denominator. Each member's suite proves something about
that member. This adds the assertions that only exist across members, and it
states which of them the batch was large enough to reach. A run covering one
family cannot conclude what a run covering four can, and the difference is
reported rather than left for a reader to infer -- `qm demo` refuses to call
one window agreeing with itself agreement, and this is that rule applied to a
test batch.

Tiers, in order: each needs strictly more of
the estate to have reported than the one above it:

  shape        1 family    every member that ran, ran something
  cover        all         every family the record declares had a member run
  contract     all + seam  every contract surface agrees across the families

A repository in two families runs once and its result counts for both, and a
family counts as reporting when anyone in it reported, the families within it
included.

A tier the batch cannot reach is printed as `not reached`, with what it would
have taken. It is never printed as passing, because an assertion nobody could
evaluate reporting green is the failure this corpus keeps finding.

Advisory, and local only. It runs sibling clones' suites, so it says different
things on two machines and belongs nowhere near CI.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FAMILIES = ROOT / "families.json"
SEARCH_ROOTS = (ROOT.parent, ROOT.parent.parent)

# What a member runs to report. A member absent from here has no suite this
# tool knows how to start, which is a fact about the estate rather than about
# the member -- most of the performing families have never been adopted, and
# inventing a command for them would manufacture a result.
SUITES: dict[str, dict] = {
    "qm": {"cwd": ".", "command": ["uv", "run", "pytest", "ci/tests", "-q"]},
    "dossier": {"cwd": ".", "command": ["uv", "run", "pytest", "tests/ui", "-q",
                                        "-p", "no:randomly"]},
    "codecartographer": {"cwd": "web", "command": ["npm", "run", "test:rad"]},
}


def clone_of(name: str) -> Path | None:
    for root in SEARCH_ROOTS:
        candidate = root / name
        if (candidate / ".git").exists():
            return candidate
    return None


def run_member(name: str) -> dict:
    """One member's suite, or the reason it did not report."""
    out = {"member": name, "ran": False, "passed": False, "why": ""}
    spec = SUITES.get(name)
    if spec is None:
        out["why"] = "no suite this tool knows how to start"
        return out
    clone = clone_of(name)
    if clone is None:
        out["why"] = "not on this disk"
        return out
    launcher = shutil.which(spec["command"][0])
    if launcher is None:
        out["why"] = f"{spec['command'][0]!r} is not on PATH"
        return out
    command = [launcher, *spec["command"][1:]]
    try:
        done = subprocess.run(command, cwd=str(clone / spec["cwd"]),
                              capture_output=True, encoding="utf-8",
                              errors="replace", timeout=1800)
    except (OSError, subprocess.TimeoutExpired) as exc:
        out["why"] = f"could not run: {exc}"
        return out
    out["ran"] = True
    out["passed"] = done.returncode == 0
    if not out["passed"]:
        # Name what failed, not just that something did: a summary line
        # alone is a result nobody can act on, and a failure's likely cause (a
        # module edited while the batch ran it) can then be established rather
        # than argued for.
        text = (done.stdout or "") + (done.stderr or "")
        named = [line.strip() for line in text.splitlines()
                 if line.startswith(("FAILED ", "not ok ")) or " FAILED" in line[:40]]
        tail = [line for line in text.splitlines() if line.strip()][-1:]
        out["why"] = "; ".join(named[:4])[:300] or (tail[0][:160] if tail else "failed")
        out["failures"] = named
    return out


def tiers(document: dict, reported: dict[str, list[dict]]) -> list[dict]:
    """What this batch establishes, and what it could not reach.

    `reported` is family -> member results that actually ran. A tier reads only
    families that reported, so its own denominator is the batch rather than the
    estate.
    """
    declared = [f["name"] for f in document["families"]]
    ran = {name: results for name, results in reported.items() if results}
    # A family within another reports through it: whoever ran in
    # `instruments` ran in `performing`.
    within = {f["name"]: f.get("within") for f in document["families"]}
    for name in list(ran):
        outer = within.get(name)
        while outer and outer not in ran:
            ran[outer] = ran[name]
            outer = within.get(outer)
    found: list[dict] = []

    found.append({
        "tier": "shape",
        "needs": "one family reporting",
        "reached": bool(ran),
        "verdict": (f"{sum(len(r) for r in ran.values())} member suite(s) ran across "
                    f"{len(ran)} family(ies)") if ran else "no member reported",
    })

    if set(ran) == set(declared):
        found.append({"tier": "cover", "needs": "every declared family reporting",
                      "reached": True,
                      "verdict": f"all {len(declared)} declared families had a member run"})
    else:
        missing = sorted(set(declared) - set(ran))
        found.append({"tier": "cover", "needs": "every declared family reporting",
                      "reached": False,
                      "verdict": f"no member ran for: {', '.join(missing)}"})

    interop = ROOT / "ci" / "interop.py"
    if set(ran) == set(declared) and interop.is_file():
        done = subprocess.run([sys.executable, str(interop), "--check"],
                              cwd=str(ROOT), capture_output=True,
                              encoding="utf-8", errors="replace")
        # `--check` reads declared strings, and the verdict says so. The first
        # wording was "every contract surface agrees", which is the claim
        # `--verify` earns by running the hosts -- a tier must not spend
        # evidence it did not collect, least of all the tier that requires the
        # most. `--verify` is not run here because the members' suites just
        # ran above; re-running them to re-earn one sentence would double the
        # batch's cost to say what the pins already say.
        found.append({"tier": "contract", "needs": "every family reporting, and a seam",
                      "reached": True, "failed": done.returncode != 0,
                      "verdict": ("every contract surface claims one version "
                                  "(declared strings -- `qm interop --verify` "
                                  "is the run-backed form)")
                                 if done.returncode == 0
                                 else "a contract surface disagrees"})
    else:
        found.append({"tier": "contract", "needs": "every family reporting, and a seam",
                      "reached": False,
                      "verdict": "the cover tier was not reached, so this cannot be"})
    return found


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--family", action="append", default=[],
                        help="only this family; repeatable")
    parser.add_argument("--check", action="store_true",
                        help="exit non-zero on a failed member or a failed tier")
    args = parser.parse_args(argv)

    document = json.loads(FAMILIES.read_text(encoding="utf-8"))
    wanted = set(args.family) or {f["name"] for f in document["families"]}
    reported: dict[str, list[dict]] = {}
    failures: list[str] = []
    # One run per repository, however many families claim it.
    results_of: dict[str, dict] = {}

    for family in document["families"]:
        if family["name"] not in wanted:
            continue
        print(f"\n## {family['name']}")
        results = []
        for member in family.get("all_members", family["members"]):
            if member not in results_of:
                results_of[member] = run_member(member)
            result = results_of[member]
            if not result["ran"]:
                print(f"   -- {member:20} did not report -- {result['why']}")
                continue
            mark = "  " if result["passed"] else "!!"
            print(f"   {mark} {member:20} {'passed' if result['passed'] else 'FAILED'}"
                  f"{'' if result['passed'] else '  ' + result['why']}")
            results.append(result)
            if not result["passed"] and member not in {f.split("/")[-1] for f in failures}:
                failures.append(f"{family['name']}/{member}")
        reported[family["name"]] = results

    print("\n" + "=" * 64)
    print("WHAT THIS BATCH ESTABLISHES")
    print("=" * 64)
    for tier in tiers(document, reported):
        if not tier["reached"]:
            print(f"  not reached  {tier['tier']:10} needs {tier['needs']} "
                  f"-- {tier['verdict']}")
        elif tier.get("failed"):
            print(f"  FAILED       {tier['tier']:10} {tier['verdict']}")
            failures.append(tier["tier"])
        else:
            print(f"  established  {tier['tier']:10} {tier['verdict']}")

    print("\nA tier nobody could evaluate is printed as `not reached`, never as "
          "passing. Running more of the estate is what moves one.")
    return 1 if (failures and args.check) else 0


if __name__ == "__main__":
    raise SystemExit(main())
