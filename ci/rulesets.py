#!/usr/bin/env python3
"""What the rulesets say, what the host is actually running, and the gap.

    uv run qm rulesets            # drafted vs applied, per ruleset
    uv run qm rulesets --check    # exit non-zero when the two disagree
    uv run qm rulesets --apply    # create or update all of them on the host

WHY A ROUTE AND NOT A README FULL OF `gh api`. Six ruleset files have sat in
`.github/rulesets/` since 2026-08-10 with an apply script beside them, and the
host reports zero rulesets. Nothing read the two together, so the drafts looked
like configuration and were documentation. This reads them together, which is
the only way the gap is visible without someone remembering to look.

WHAT `--apply` IS. A wrapper around `.github/rulesets/apply.sh`, which is the
thing that owns the operation. It changes what every contributor and every
concurrent session can do, on the host, outside any pull request -- so it is
never run as part of anything else, and this tool will not reach for it on its
own. `--check` reports; only `--apply` writes.

WHAT THIS CANNOT SEE. Whether a rule is the right rule. It compares the drafted
enforcement level and rule types against the host's, and a ruleset that is
present and active can still be enforcing something nobody wanted. It also
cannot see `rule-suites` -- the log of what an evaluating rule *would* have
blocked -- which is the thing worth reading before promoting one.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIR = ROOT / ".github" / "rulesets"
APPLY = DIR / "apply.sh"
DEFAULT_REPO = "quaternionmedia/qm"


def drafted(directory: Path = DIR) -> list[dict]:
    out = []
    for path in sorted(directory.glob("*.json")):
        try:
            out.append({"file": path.name, **json.loads(path.read_text(encoding="utf-8"))})
        except json.JSONDecodeError as exc:
            out.append({"file": path.name, "broken": str(exc)})
    return out


def applied(repo: str) -> list[dict] | None:
    """What the host is running. None when it could not be asked.

    None rather than an empty list: an empty list is a real and important
    answer -- nothing is applied -- and must not be produced by a failed call.
    """
    try:
        proc = subprocess.run(
            ["gh", "api", f"repos/{repo}/rulesets", "--jq", "."],
            capture_output=True, text=True, timeout=60,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if proc.returncode != 0:
        return None
    try:
        listed = json.loads(proc.stdout or "[]")
    except json.JSONDecodeError:
        return None
    return listed if isinstance(listed, list) else None


def detail(repo: str, ruleset_id: int) -> dict:
    proc = subprocess.run(
        ["gh", "api", f"repos/{repo}/rulesets/{ruleset_id}"],
        capture_output=True, text=True, timeout=60,
    )
    if proc.returncode != 0:
        return {}
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError:
        return {}


def compare(local: list[dict], host: list[dict] | None, repo: str) -> list[dict]:
    rows = []
    by_name = {r.get("name"): r for r in (host or [])}
    for entry in local:
        name = entry.get("name")
        live = by_name.get(name)
        row = {
            "file": entry["file"],
            "name": name,
            "drafted": entry.get("enforcement"),
            "applied": None,
            "state": "unknown",
            "differences": [],
        }
        if entry.get("broken"):
            row["state"] = "broken"
            row["differences"] = [entry["broken"]]
        elif host is None:
            row["state"] = "unknown"
        elif live is None:
            row["state"] = "absent"
        else:
            row["applied"] = live.get("enforcement")
            full = detail(repo, live["id"])
            drafted_rules = sorted(r["type"] for r in entry.get("rules", []))
            live_rules = sorted(r["type"] for r in full.get("rules", []))
            if row["drafted"] != row["applied"]:
                row["differences"].append(
                    f"enforcement drafted={row['drafted']} applied={row['applied']}"
                )
            for missing in sorted(set(drafted_rules) - set(live_rules)):
                row["differences"].append(f"rule `{missing}` drafted, not applied")
            for extra in sorted(set(live_rules) - set(drafted_rules)):
                row["differences"].append(f"rule `{extra}` applied, not drafted")
            row["state"] = "match" if not row["differences"] else "drift"
        rows.append(row)
    return rows


def render(rows: list[dict], host: list[dict] | None) -> str:
    out: list[str] = []
    if host is None:
        out.append("Could not ask the host what is applied. Everything below is "
                   "the drafted side only.")
    else:
        out.append(f"{len(rows)} drafted, {len(host)} applied on the host.")
        if not host:
            out.append("Nothing is applied. Every rule below is a file, and every "
                       "check in this repository is a signal rather than a barrier.")
    out.append("")

    mark = {"match": "[=]", "drift": "[!]", "absent": "[ ]",
            "unknown": "[?]", "broken": "[x]"}
    for row in rows:
        out.append(f"  {mark.get(row['state'], '[?]')} {row['file']:<20} "
                   f"{str(row['name']):<18} drafted={row['drafted']}"
                   + (f" applied={row['applied']}" if row["applied"] else ""))
        for difference in row["differences"]:
            out.append(f"        {difference}")

    out += [
        "",
        "[=] applied and matching   [!] applied and different   [ ] not applied",
        "",
        "This compares enforcement and rule types. It does not read rule "
        "parameters,",
        "and it cannot tell that a rule is the right rule.",
    ]
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo", default=DEFAULT_REPO)
    parser.add_argument("--dir", default=str(DIR))
    parser.add_argument("--check", action="store_true",
                        help="exit non-zero when drafted and applied disagree")
    parser.add_argument("--apply", action="store_true",
                        help="run .github/rulesets/apply.sh against the host")
    args = parser.parse_args(argv)

    local = drafted(Path(args.dir))
    if not local:
        raise SystemExit(f"{args.dir}: no ruleset files. Nothing is drafted.")

    if args.apply:
        if not APPLY.is_file():
            raise SystemExit(f"{APPLY}: not present; nothing to run.")
        print(f"Running {APPLY.relative_to(ROOT).as_posix()} against {args.repo}.")
        print("This changes what every contributor and every concurrent session "
              "can do.\n")
        proc = subprocess.run(["bash", str(APPLY)], cwd=str(ROOT))
        return proc.returncode

    host = applied(args.repo)
    rows = compare(local, host, args.repo)
    print(render(rows, host))

    if args.check:
        wrong = [r for r in rows if r["state"] in ("drift", "absent", "broken")]
        if host is None:
            print("\nThe host could not be asked, so nothing was verified.",
                  file=sys.stderr)
            return 1
        if wrong:
            print(f"\n{len(wrong)} ruleset(s) not applied as drafted. "
                  f"Apply: uv run qm rulesets --apply", file=sys.stderr)
            return 1
        print("\nEvery drafted ruleset is applied as drafted.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
