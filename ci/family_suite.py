#!/usr/bin/env python3
"""Run each family's own suites, and say what the batch establishes.

    uv run qm family-suite                  # every family that can report
    uv run qm family-suite --family core    # one, repeatable
    uv run qm family-suite --check          # exit non-zero on a failed member

**THE POINT IS THE DENOMINATOR.** Each member's suite proves something about
that member. This adds the assertions that only exist across members, and it
states which of them the batch was large enough to reach. A run covering one
family cannot conclude what a run covering four can, and the difference is
reported rather than left for a reader to infer -- `qm demo` refuses to call
one window agreeing with itself agreement, and this is that rule applied to a
test batch.

**TIERS, AND WHY THEY ARE ORDERED THIS WAY.** Each tier needs strictly more of
the estate to have reported than the one above it:

  shape        1 family    every member that ran, ran something
  disjoint     2 families  no repository is in two families
  cover        all         every family the record declares had a member run
  contract     all + seam  every contract surface agrees across the families

A tier the batch cannot reach is printed as `not reached`, with what it would
have taken. It is never printed as passing, because an assertion nobody could
evaluate reporting green is the failure this corpus keeps finding.

ADVISORY, AND LOCAL ONLY. It runs sibling clones' suites, so it says different
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
        # NAME WHAT FAILED, NOT JUST THAT SOMETHING DID. The first run of this
        # tool reported "1 failed, 1143 passed" and kept no name, so the failure
        # could not be diagnosed from the log -- and the most likely cause,
        # a module being edited while the batch ran it, could be argued for and
        # not established. A summary line is a result nobody can act on.
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
    found: list[dict] = []

    found.append({
        "tier": "shape",
        "needs": "one family reporting",
        "reached": bool(ran),
        "verdict": (f"{sum(len(r) for r in ran.values())} member suite(s) ran across "
                    f"{len(ran)} family(ies)") if ran else "no member reported",
    })

    if len(ran) >= 2:
        seen: dict[str, str] = {}
        clash = []
        for family in document["families"]:
            for member in family["members"]:
                if member in seen and seen[member] != family["name"]:
                    clash.append(f"{member} in {seen[member]} and {family['name']}")
                seen[member] = family["name"]
        found.append({"tier": "disjoint", "needs": "two families reporting",
                      "reached": True,
                      "verdict": "no repository is in two families" if not clash
                                 else "; ".join(clash), "failed": bool(clash)})
    else:
        found.append({"tier": "disjoint", "needs": "two families reporting",
                      "reached": False,
                      "verdict": f"{len(ran)} family(ies) reported"})

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

    for family in document["families"]:
        if family["name"] not in wanted:
            continue
        print(f"\n## {family['name']}")
        results = []
        for member in family["members"]:
            result = run_member(member)
            if not result["ran"]:
                print(f"   -- {member:20} did not report -- {result['why']}")
                continue
            mark = "  " if result["passed"] else "!!"
            print(f"   {mark} {member:20} {'passed' if result['passed'] else 'FAILED'}"
                  f"{'' if result['passed'] else '  ' + result['why']}")
            results.append(result)
            if not result["passed"]:
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
