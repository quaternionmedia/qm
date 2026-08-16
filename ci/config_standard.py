#!/usr/bin/env python3
"""Check that data files obey the config standard, and migrate them if not.

    uv run qm config              # what conforms and what does not
    uv run qm config --migrate    # move files and rewrite every reference
    uv run qm config --check      # exit non-zero on any violation

The standard is `handbook/config-standard.md`. In short: hand-authored claims
live in `ci/` as YAML, generated evidence lives in `status/` as YAML, views live
in `handbook/`, and machine-scoped files are gitignored and live in neither.

WHY THIS IS A CHECK AND NOT A SCRIPT. The migration runs once; the standard has
to hold afterwards. A one-off script would move nine files and leave nothing to
notice the tenth, which is how the corpus reached two formats and no rule in the
first place. `--migrate` is a mode of the check rather than its own tool, so the
thing that moves files is the thing that knows where they belong.

WHAT IT CANNOT DO. It cannot tell a claim from a measurement by reading a file --
that is what the folder is for, and the folder is the human's assertion. It
checks placement, format and naming. A generated document hand-edited into
`ci/`, or a roster written by a script into `status/`, passes here and is wrong.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent

# Generated evidence: subject name, no redundant suffix, YAML, under status/.
# Keys are the pre-standard paths, values the standard ones. Once migration has
# run this table is the record of what moved, and `--check` uses it to notice a
# regression rather than to move anything.
MIGRATIONS = {
    "governance-status.yaml": "status/governance.yaml",
    "harness-status.json": "status/harness.yaml",
    "gate-status.json": "status/gates.yaml",
    "doc-status.json": "status/documents.yaml",
    "disk-status.json": "status/disk.yaml",
    "inventory-public.json": "status/inventory.yaml",
    "ledger.yaml": "status/ledger.yaml",
}

# Machine-scoped, gitignored, and in neither folder on purpose.
EXEMPT = {"inventory-private.json", "inventory-local.json"}

# Files that are data but are not evidence and not a registry: packaging and
# tool config, which belong at the root by their own tools' convention.
ROOT_ALLOWED = {"pyproject.toml", "uv.lock", "REUSE.toml", "zensical.toml",
                "license-report.json"}

# Files that name a pre-standard path deliberately and must never be rewritten.
# A reference and a historical mention are identical to a text substitution, so
# the distinction is declared. Registered as `migration-keeps-its-own-vocabulary`
# in ci/exception-registry.yaml.
NEVER_REWRITE = {
    "ci/config_standard.py",             # names both sides of every move
    "ci/tests/test_config_standard.py",  # fixtures use the old names on purpose
    "handbook/config-standard.md",       # describes the state the move replaced
}

SEARCHABLE = (".py", ".md", ".yml", ".yaml", ".toml")
SKIP_DIRS = (".git", ".venv", ".harness", "site", "__pycache__", "node_modules")


def searchable_files(root: Path) -> list[Path]:
    out = []
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix not in SEARCHABLE:
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        out.append(path)
    return out


def violations(root: Path) -> list[str]:
    """Where the standard does not hold, one line each."""
    found = []

    for name in sorted(p.name for p in root.glob("*") if p.is_file()):
        if name in ROOT_ALLOWED or name in EXEMPT or name.startswith("."):
            continue
        if name.endswith((".json", ".yaml", ".yml")):
            target = MIGRATIONS.get(name)
            where = f" -- belongs at {target}" if target else ""
            found.append(f"{name}: a data file at the repository root{where}")

    for path in sorted(root.glob("status/*")):
        if path.suffix != ".yaml":
            found.append(f"status/{path.name}: not YAML; the standard is one format")
        if path.stem.endswith("-status"):
            found.append(
                f"status/{path.name}: the folder already says status; "
                f"name it {path.stem.replace('-status', '')}.yaml"
            )

    for path in sorted(root.glob("ci/*")):
        if path.suffix in (".json", ".yml"):
            found.append(f"ci/{path.name}: not YAML; the standard is one format")

    return found


def stale_references(root: Path) -> dict[str, list[str]]:
    """Files still naming a pre-standard path, keyed by that path."""
    stale: dict[str, list[str]] = {}
    for path in searchable_files(root):
        rel = path.relative_to(root).as_posix()
        if rel in NEVER_REWRITE:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for old in MIGRATIONS:
            # Word-boundary so `status/gates.yaml` does not match `gates.yaml`
            # inside an already-migrated path.
            if re.search(rf"(?<![\w/-]){re.escape(old)}", text):
                stale.setdefault(old, []).append(rel)
    return stale


def convert(path: Path, target: Path) -> None:
    """Move a file to its standard path, converting JSON to YAML on the way."""
    target.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
        target.write_text(
            yaml.safe_dump(data, sort_keys=False, allow_unicode=True, width=100),
            encoding="utf-8", newline="\n",
        )
    else:
        target.write_text(path.read_text(encoding="utf-8"),
                          encoding="utf-8", newline="\n")
    path.unlink()


def migrate(root: Path) -> list[str]:
    """Move every pre-standard file and rewrite every reference. Idempotent."""
    done = []
    for old, new in MIGRATIONS.items():
        source, target = root / old, root / new
        if source.is_file():
            convert(source, target)
            done.append(f"moved {old} -> {new}")

    rewritten, skipped = 0, []
    for path in searchable_files(root):
        rel = path.relative_to(root).as_posix()
        if rel in NEVER_REWRITE:
            if any(re.search(rf"(?<![\w/-]){re.escape(o)}", path.read_text(encoding="utf-8"))
                   for o in MIGRATIONS):
                skipped.append(rel)
            continue
        try:
            text = original = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for old, new in MIGRATIONS.items():
            text = re.sub(rf"(?<![\w/-]){re.escape(old)}", new, text)
        if text != original:
            path.write_text(text, encoding="utf-8", newline="\n")
            rewritten += 1
    if rewritten:
        done.append(f"rewrote references in {rewritten} file(s)")
    for rel in skipped:
        done.append(f"left {rel} alone -- it names the old path on purpose")
    return done


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", default=str(ROOT))
    parser.add_argument("--migrate", action="store_true",
                        help="move files to their standard paths and rewrite references")
    parser.add_argument("--check", action="store_true",
                        help="exit non-zero on any violation")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()

    if args.migrate:
        done = migrate(root)
        for line in done:
            print(f"  {line}")
        if not done:
            print("  nothing to move; the standard already holds")
        print("\nRun the suite and the gates before committing: this rewrote "
              "paths inside generators, tests and prose.")
        return 0

    found = violations(root)
    stale = stale_references(root)

    for line in found:
        print(f"  - {line}")
    for old, files in sorted(stale.items()):
        print(f"  - {old}: still named in {len(files)} file(s), e.g. {files[0]}")

    total = len(found) + len(stale)
    if total:
        print(f"\n{total} violation(s) of handbook/config-standard.md. "
              f"`uv run qm config --migrate` fixes the mechanical part.")
    else:
        print("config standard: placement, format and naming all hold.")
        print("This does NOT check that a file in ci/ is a claim or that one in "
              "status/ is a measurement -- the folder is the human's assertion.")
    return 1 if (args.check and total) else 0


if __name__ == "__main__":
    sys.exit(main())
