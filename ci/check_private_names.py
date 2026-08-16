#!/usr/bin/env python3
"""No private repository name appears in a file this repository tracks.

    uv run qm private-names            # scan the tracked tree
    uv run qm private-names --strict   # also fail when it cannot verify

THREE STATES, AND ONLY ONE OF THEM IS A PASS.

    clean       a source of private names was read, and none of them appear
    found       a private name is in a tracked file -- exit 1
    unverified  no source was available, so nothing was checked

`unverified` exits 0 by default so a fresh clone is not blocked by the absence
of a file it is never supposed to have, and prints that word first so nobody
reads it as a pass. `--strict` turns it into a failure, which is what a machine
holding the companions should run.

WHY IT EXISTS. Two private repository names sat in the committed
`ci/workspace.yaml` from 2b50bd6 while `inventory-public.json` redacted the same
two repositories as `private-32` and `private-33`. Both files were committed,
each looked right alone, and nothing read them together. This reads them
together.

WHAT IT CANNOT DO. It cannot find a name in history -- only in the tree as it
stands. The two names above remain in the public history of a public repository
and no forward fix removes them; that is recorded as a declared exemption rather
than quietly carried.

LOCAL ONLY. The sources it reads are gitignored, so on a runner this reports
`unverified` every time. It belongs in preflight, not in a workflow.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent

# The gitignored companions that hold the mapping. Adding a source here is how
# this check learns about a new class of secret name.
SOURCES = (
    ROOT / "inventory-private.json",
    ROOT / "ci" / "workspace-private.yaml",
)

# Files that name a private repository deliberately. Each is itself untracked;
# listed so a future tracked exemption has an obvious place to be declared.
EXEMPT = {
    "ci/workspace-private.yaml",
    "inventory-private.json",
    "inventory-local.json",
}


def private_names(sources=SOURCES) -> set[str]:
    """Every private repository name the local companions know about."""
    names: set[str] = set()
    for path in sources:
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        data = (json.loads(text) if path.suffix == ".json"
                else yaml.safe_load(text)) or {}
        for entry in data.get("repositories") or []:
            if isinstance(entry, dict) and entry.get("name"):
                names.add(entry["name"])
    return names


def tracked_files(root: Path) -> list[str]:
    proc = subprocess.run(
        ["git", "ls-files"], cwd=str(root), capture_output=True, text=True
    )
    if proc.returncode != 0:
        return []
    return [line for line in proc.stdout.splitlines() if line]


def pattern(name: str) -> re.Pattern[str]:
    """A private name, not a longer name that happens to contain it.

    A plain substring search reported `inventory-public.json` as carrying a
    private name. It carries a *public* repository whose name is three
    characters longer and contains the private one -- so the file's whole
    guarantee appeared broken, by the check rather than by the file. Repository
    names are bounded by characters that cannot appear in one.
    """
    return re.compile(rf"(?<![A-Za-z0-9_-]){re.escape(name)}(?![A-Za-z0-9_-])")


def scan(root: Path, names: set[str]) -> list[tuple[str, str]]:
    """(file, name) for every tracked file carrying a private name."""
    patterns = [(name, pattern(name)) for name in names]
    hits: list[tuple[str, str]] = []
    for rel in tracked_files(root):
        if rel in EXEMPT:
            continue
        path = root / rel
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for name, expr in patterns:
            if expr.search(text):
                hits.append((rel, name))
    return hits


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", default=str(ROOT))
    parser.add_argument("--strict", action="store_true",
                        help="fail when no source of private names is available")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    # Read through the module global rather than the default argument, so a
    # test can point this at a fixture. A default is bound at definition.
    names = private_names(SOURCES)

    if not names:
        print("unverified  no source of private names on this machine, so "
              "nothing was checked.")
        print(f"            expected one of: "
              f"{', '.join(p.name for p in SOURCES)}")
        print("            This is the normal result on a runner and on a fresh "
              "clone. It is not a pass.")
        return 1 if args.strict else 0

    hits = scan(root, names)
    if hits:
        # The name itself is never printed -- doing so here would put it in a
        # log, which is the thing being prevented one layer along.
        print(f"found       {len(hits)} occurrence(s) of a private repository "
              f"name in tracked files:", file=sys.stderr)
        for rel, _ in sorted(set(hits)):
            print(f"              {rel}", file=sys.stderr)
        print("\n            Redact the file, or declare the exemption in "
              "ci/exception-registry.yaml.", file=sys.stderr)
        return 1

    print(f"clean       {len(names)} private name(s) checked against "
          f"{len(tracked_files(root))} tracked file(s); none appear.")
    print("            History is not read. A name already published stays "
          "published.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
