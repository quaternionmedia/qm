#!/usr/bin/env python3
"""The procedures this org runs deliberately, and when each was last run.

    uv run qm protocols                     # every protocol, and its last run
    uv run qm protocols --id security-review
    uv run qm protocols --check             # refuse an unrunnable declaration

A PROTOCOL IS NOT A GATE. A gate is automatic, refuses, and nobody invokes it.
A protocol is invoked, takes judgement, and produces a dated artifact. Listing
the two in one place would make a protocol read as always-on and a gate read as
optional, so `ci/gate-registry.yaml` holds one and `ci/protocol-registry.yaml`
holds the other.

WHAT `--check` REFUSES, and each of these has an instance in this repository's
history:

  * a registered protocol with no page, and a page nobody registered -- the
    claim layer and the artifact layer disagreeing, which is the split
    `ci/gate-registry.yaml` keeps for the same reason;
  * a step invoking `uv run qm <route>` where no such route exists. A procedure
    naming a command nobody can run is a procedure nobody has run, and a
    renamed route breaks every page that cited it silently;
  * a protocol with no `cannot_see`, which is undescribed rather than thorough.

WHAT IT DOES NOT REFUSE. A protocol that has never been run. That is printed,
loudly, and it is a fact about the organisation rather than a defect in the
file -- most of this list has never been run, and a check that failed on it
would be a check somebody deletes.

WHAT THIS CANNOT SEE. Whether a run did what the protocol says. It reads the
filename of the artifact and its date; it does not read a word of the contents,
and it cannot tell a thorough review from a file with the right name.
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import date, datetime
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "ci" / "protocol-registry.yaml"
PAGES = ROOT / "protocols"
RUNS = PAGES / "runs"

REQUIRED = ("id", "name", "question", "page", "invoked_by", "produces",
            "steps", "cannot_see", "cadence_days")

RUN_NAME = re.compile(r"^(\d{4}-\d{2}-\d{2})-(?P<id>[a-z0-9][a-z0-9-]*)\.md$")
QM_STEP = re.compile(r"^uv run qm ([a-z][a-z-]*)")


def load(path: Path = REGISTRY) -> list[dict]:
    if not path.is_file():
        raise SystemExit(f"{path}: no protocol registry. Nothing is declared.")
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    protocols = data.get("protocols") or []
    if not protocols:
        # An empty registry makes every count below vacuously clean, which is
        # how this corpus's lint globs have failed before.
        raise SystemExit(f"{path}: no protocols listed. That is a claim, not an absence.")
    return protocols


def known_routes() -> set[str]:
    """The `qm` commands that exist, read from the CLI rather than a list here.

    A second copy of the route table would be a second thing to keep in step,
    and the whole point of the step check is that it notices a rename.
    """
    sys.path.insert(0, str(ROOT / "ci"))
    import cli  # noqa: PLC0415 -- deliberately late: ROOT must be on the path first

    return set(cli.ROUTES) | {"docs"}


def runs(directory: Path = RUNS) -> dict[str, list[tuple[date, Path]]]:
    """Every dated artifact under `protocols/runs/`, keyed by protocol id.

    Derived, never declared. A `last_run` field in the registry would be a date
    a person types, and a date a person types is a date that stops being true
    without anything changing.
    """
    found: dict[str, list[tuple[date, Path]]] = {}
    if not directory.is_dir():
        return found
    for path in sorted(directory.glob("*.md")):
        match = RUN_NAME.match(path.name)
        if not match:
            continue
        try:
            when = datetime.strptime(match.group(1), "%Y-%m-%d").date()
        except ValueError:
            continue
        found.setdefault(match.group("id"), []).append((when, path))
    for entries in found.values():
        entries.sort()
    return found


def last_run(protocol: dict, found: dict[str, list[tuple[date, Path]]]):
    entries = found.get(protocol.get("id", ""))
    return entries[-1] if entries else None


def age_days(when: date, today: date) -> int:
    return (today - when).days


def problems(protocols: list[dict], routes: set[str], root: Path = ROOT) -> list[str]:
    found: list[str] = []
    seen: set[str] = set()
    registered_pages: set[str] = set()

    for protocol in protocols:
        pid = protocol.get("id", "<no id>")
        if pid in seen:
            found.append(f"{pid}: duplicate id")
        seen.add(pid)

        for field in REQUIRED:
            if not protocol.get(field):
                found.append(f"{pid}: missing `{field}`")

        page = protocol.get("page")
        if page:
            registered_pages.add(str(page))
            if not (root / str(page)).is_file():
                found.append(f"{pid}: page {page} is not there")

        for step in protocol.get("steps") or []:
            match = QM_STEP.match(str(step).strip())
            if match and match.group(1) not in routes:
                found.append(
                    f"{pid}: step names `qm {match.group(1)}`, which is not a "
                    f"route. A procedure nobody can run is a procedure nobody has run"
                )

    pages_dir = root / "protocols"
    if pages_dir.is_dir():
        for path in sorted(pages_dir.glob("*.md")):
            if path.name == "README.md":
                continue
            relative = path.relative_to(root).as_posix()
            if relative not in registered_pages:
                found.append(
                    f"{relative}: a page nobody registered. A protocol this "
                    f"registry cannot describe is one nobody can rely on"
                )
    return found


def render(protocols: list[dict], found: dict, today: date, only: str | None) -> str:
    rows = [p for p in protocols if not only or p.get("id") == only]
    if only and not rows:
        raise SystemExit(f"{only}: no such protocol. Known: "
                         f"{', '.join(str(p.get('id')) for p in protocols)}")

    never = sum(1 for p in protocols if not last_run(p, found))
    out = [
        f"{len(protocols)} protocol(s). {never} have never been run.",
        "",
        "A protocol is invoked, not automatic. Nothing here runs anything, and",
        "nothing here gates a merge.",
        "",
    ]

    for protocol in rows:
        latest = last_run(protocol, found)
        if latest is None:
            state = "NEVER RUN"
        else:
            age = age_days(latest[0], today)
            budget = int(protocol.get("cadence_days") or 0)
            over = " (past its budget)" if budget and age > budget else ""
            state = f"last run {latest[0].isoformat()}, {age}d ago{over}"

        out += [
            f"## {protocol.get('name')}  ({protocol.get('id')})"
            + ("  [optional]" if protocol.get("optional") else ""),
            f"   {' '.join(str(protocol.get('question', '')).split())}",
            "",
            f"   state     {state}",
            f"   page      {protocol.get('page')}",
            f"   invoked   {protocol.get('invoked_by')}",
            f"   produces  {protocol.get('produces')}",
            f"   budget    {protocol.get('cadence_days')} days",
        ]
        for step in protocol.get("steps") or []:
            out.append(f"   step      {step}")
        out.append(f"   cannot see  {' '.join(str(protocol.get('cannot_see', '')).split())}")
        out.append("")

    out += [
        "NEVER RUN is a fact about this organisation, not a defect in the "
        "registry.",
        "This reads a run's filename and its date. It does not read one word of "
        "what the run said.",
    ]
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--registry", default=str(REGISTRY))
    parser.add_argument("--root", default=str(ROOT),
                        help="the checkout whose protocols/ directory is scanned")
    parser.add_argument("--runs", default=str(RUNS))
    parser.add_argument("--id", help="one protocol")
    parser.add_argument("--check", action="store_true",
                        help="refuse a declaration nobody could run")
    args = parser.parse_args(argv)

    protocols = load(Path(args.registry))
    found = runs(Path(args.runs))

    if args.check:
        issues = problems(protocols, known_routes(), Path(args.root))
        for issue in issues:
            print(f"  - {issue}", file=sys.stderr)
        if issues:
            print(f"\n{len(issues)} problem(s) in {args.registry}.", file=sys.stderr)
            return 1
        never = [str(p.get("id")) for p in protocols if not last_run(p, found)]
        print(f"protocols: {len(protocols)} declared, every one with a page and "
              f"runnable steps.")
        if never:
            print(f"{len(never)} have never been run: {', '.join(never)}. "
                  f"That is reported, not refused.")
        print("This does NOT mean a run did what its protocol says -- nothing "
              "here reads a run's contents.")
        return 0

    print(render(protocols, found, date.today(), args.id))
    return 0


if __name__ == "__main__":
    sys.exit(main())
