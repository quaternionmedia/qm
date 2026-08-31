#!/usr/bin/env python3
"""Every repository on one contract surface claims the same version, or none do.

    uv run qm interop            # what each repository claims
    uv run qm interop --check    # exit non-zero when a surface disagrees

The decision is `records/DRAFT-a-shared-tag-asserts-interoperability.md`: equal
numbers assert that these artifacts were proven to work together, and a change
on either side invalidates the claim for both.

ADVISORY, AND LOCAL ONLY. This reads sibling clones, so it says different things
on two machines and belongs nowhere near CI -- a runner has no siblings, and a
pull request that went red for a missing clone would be red for a reason its
author cannot fix. `--check` is a local pre-flight, not a gate. `ci/devloop.py`
carries the same constraint for the same reason.

WHAT IT CANNOT DO. Tell whether an implementation that claims a version
actually replayed it: this reads a declared string, not a test run. And it
cannot see coverage. Two implementations may claim one version while replaying
disjoint halves of the set -- which is the state of the one surface registered
today -- so agreement here is necessary for interoperability and not sufficient
for the contract being proven. That second half is the record's 4, and no check
reaches it.
"""

from __future__ import annotations

import argparse
import json
import re
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
        if read["cannot_see"]:
            print(f"\n  cannot see: {' '.join(read['cannot_see'].split())}")

    print("\nA declared version is a claim that a set was replayed, not evidence "
          "that it was. Nothing here ran a test.")
    return 1 if (failed and args.check) else 0


if __name__ == "__main__":
    raise SystemExit(main())
