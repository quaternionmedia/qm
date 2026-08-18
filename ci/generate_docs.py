#!/usr/bin/env python3
"""Regenerate every generated document, in order, and say what moved.

Org-level tooling, copied nowhere. One command a human runs before a pull
request, so drift shows up as an uncommitted diff rather than as staleness
nobody sees -- charter P12, and `records/DRAFT-one-executable-walkthrough.md`.

WHY THIS EXISTS. Six generated artifacts live at this repository's root and in
`handbook/`, each with its own refresh command written down in its own
`reading:` block. That is correct and it is not usable: nobody runs six
commands from memory, so the ones needing a remembered command go stale and the
ones riding an existing command do not. That gap has already been measured in
this corpus -- the artifacts riding the test command carry zero drift and the
two needing a remembered command are stale.

THE NETWORK SPLIT IS THE IMPORTANT PART. Three of these read other repositories
or the host:

    governance-status.yaml   reads every project's refs
    harness-status.json      reads pull requests across the org
    gate-status.json         reads this repository's rulesets

`--offline` skips exactly those and says so in the report. It never writes a
network-derived fact it did not fetch, and it never leaves a stale one looking
fresh: a document skipped is reported skipped, with its age.

**Do not wire the online half into CI.** It reads other repositories, so an
unrelated pull request would go red for a reason its author cannot fix. The
`--check` mode is the CI-safe half: it verifies the offline documents still
describe the repository and never fetches anything.

Usage:
    python ci/generate_docs.py               # the manual dev regeneration
    python ci/generate_docs.py --offline     # skip anything that reaches a network
    python ci/generate_docs.py --check       # CI-safe: has anything drifted?
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

def _corpus_root() -> Path:
    """The corpus this run belongs to.

    Resolved from the working directory first, because `uv run qm` installs this
    package into a venv -- where `__file__`'s parent is site-packages and every
    relative path below would write into it. Falls back to the source layout so
    `python ci/generate_docs.py` still works from anywhere.
    """
    current = Path.cwd().resolve()
    for candidate in (current, *current.parents):
        if (candidate / "PRINCIPLES.md").exists() and (candidate / "records").is_dir():
            return candidate
    return Path(__file__).resolve().parent.parent


ROOT = _corpus_root()

# (label, argv, output path, reaches_network, check_argv or None)
#
# Order matters twice: a renderer must run after the document it reads, and
# doc-status.json must run last because it reports on the files the others just
# wrote. Getting that backwards produces a state page describing the previous
# run, which is the kind of confidently-wrong artifact this corpus keeps finding.
STEPS: list[tuple[str, list[str], str, bool, list[str] | None]] = [
    (
        "governance status",
        ["ci/governance_status.py", "--write", "governance-status.yaml"],
        "governance-status.yaml",
        True,
        ["ci/governance_status.py", "--check", "governance-status.yaml"],
    ),
    (
        "harness status",
        ["ci/harness_status.py", "--no-local", "--write", "harness-status.json"],
        "harness-status.json",
        True,
        None,
    ),
    (
        "gate status",
        ["ci/gate_status.py", "--write", "gate-status.json"],
        "gate-status.json",
        True,
        ["ci/gate_status.py", "--check", "gate-status.json"],
    ),
    (
        "gate view",
        ["ci/gate_dashboard.py", "gate-status.json", "--format", "md",
         "--out", "handbook/gates.md"],
        "handbook/gates.md",
        False,
        ["ci/gate_dashboard.py", "gate-status.json", "--format", "md",
         "--check", "handbook/gates.md"],
    ),
    (
        "document states",
        ["ci/doc_status.py", "--write", "doc-status.json"],
        "doc-status.json",
        False,
        ["ci/doc_status.py", "--check", "doc-status.json"],
    ),
    (
        "document states view",
        ["ci/doc_dashboard.py", "doc-status.json", "--out", "handbook/document-states.md"],
        "handbook/document-states.md",
        False,
        ["ci/doc_dashboard.py", "doc-status.json", "--check", "handbook/document-states.md"],
    ),
]

# gate-status.json reaches the host only for its enforcement layer, and writes
# `unknown` instead when told not to. The others have no offline mode.
OFFLINE_FLAG = {"gate status": "--no-host"}


def run(argv: list[str]) -> tuple[int, str]:
    proc = subprocess.run(
        [sys.executable, *argv],
        cwd=str(ROOT), capture_output=True, text=True,
        encoding="utf-8", errors="replace",
    )
    return proc.returncode, (proc.stdout + proc.stderr).strip()


def digest(path: Path) -> bytes | None:
    """Bytes, so a line-ending translation cannot read as a content change."""
    return path.read_bytes() if path.is_file() else None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--offline", action="store_true",
                        help="skip anything that reaches another repository or the host")
    parser.add_argument("--check", action="store_true",
                        help="CI-safe: verify the offline documents, write nothing")
    args = parser.parse_args(argv)

    if args.check:
        print("Checking generated documents. Nothing is fetched and nothing is written.\n")
        failed = []
        for label, _, out, network, check_argv in STEPS:
            if check_argv is None:
                print(f"  skip   {label:<22} no check mode; its freshness is a "
                      f"staleness budget, not a gate")
                continue
            code, output = run(check_argv)
            print(f"  {'ok  ' if code == 0 else 'FAIL'}   {label:<22} {out}")
            if code != 0:
                failed.append((label, output))
        if failed:
            print()
            for label, output in failed:
                print(f"--- {label}\n{output}\n")
            print(f"{len(failed)} document(s) have drifted. "
                  f"Run: python ci/generate_docs.py")
            return 1
        print("\nEvery checkable document still describes the repository.")
        return 0

    print("Regenerating documents." + (" Offline: network steps are skipped.\n"
                                       if args.offline else "\n"))
    skipped, wrote, unchanged, failed = [], [], [], []

    for label, step_argv, out, network, _ in STEPS:
        path = ROOT / out
        if args.offline and network and label not in OFFLINE_FLAG:
            age = "absent" if not path.is_file() else "left as it was"
            skipped.append((label, out, age))
            print(f"  skip   {label:<22} {out}  ({age})")
            continue

        run_argv = list(step_argv)
        if args.offline and label in OFFLINE_FLAG:
            run_argv.insert(1, OFFLINE_FLAG[label])

        before = digest(path)
        code, output = run(run_argv)
        after = digest(path)

        if code != 0:
            failed.append((label, output))
            print(f"  FAIL   {label:<22} {out}")
        elif before != after:
            wrote.append(out)
            print(f"  wrote  {label:<22} {out}")
        else:
            unchanged.append(out)
            print(f"  same   {label:<22} {out}")

    print()
    if failed:
        for label, output in failed:
            print(f"--- {label}\n{output}\n")
        print(f"{len(failed)} generator(s) failed. Nothing above is trustworthy "
              f"until they do.")
        return 1

    print(f"{len(wrote)} changed, {len(unchanged)} unchanged"
          + (f", {len(skipped)} skipped" if skipped else "") + ".")
    if wrote:
        print("\nChanged files are an uncommitted diff. Read it before committing: "
              "a generator that rewrote a document you did not expect it to touch "
              "is a finding, not noise.")
    if skipped:
        print("\nSkipped documents were NOT refreshed and may be stale. Each one "
              "carries its own generated_at -- check it before quoting a figure.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
