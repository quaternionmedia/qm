#!/usr/bin/env python3
"""Every v* tag in the org, judged by the rule the seed check defines.

Org-level tooling, copied nowhere. `project-seed/ci/check_tag_claims.py` is the
rule and runs inside one repository; this sweeps the roster and reports which
repositories are ready to show.

ONE DEFINITION OF THE RULE. The verdict comes from `check_annotation()`,
imported from the seed script. A second implementation here would be a second
definition of a governance rule, and the two would drift the first time one was
fixed -- which is the failure `harness_dashboard.py`'s own docstring refuses for
the same reason.

WHY THE HOST AND NOT A CLONE. A tag is a published artifact; what is on
somebody's disk is not what a consumer sees. Reading the host also means the
audit needs no clone, so it answers the same way on any machine and inside CI.
`gh api repos/O/R/git/refs/tags` gives each tag's object type -- `tag` for
annotated, `commit` for lightweight -- and the annotation body comes from
`gh api repos/O/R/git/tags/<sha>`.

WHAT THIS CANNOT DO. Everything the seed check cannot do, unchanged: it reads
annotations, so it cannot tell whether a review or a manual test happened. See
that module's docstring. It adds one limit of its own -- a repository it could
not read is reported as `unknown`, never as clean. A repository nobody could
measure must not look like a repository with nothing wrong.

Usage:
    python ci/tag_audit.py                          # the roster in ci/workspace.yaml
    python ci/tag_audit.py --repo quaternionmedia/alfred
    python ci/tag_audit.py --from-json captured.json   # no network; see tests
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "project-seed" / "ci"))

from check_tag_claims import check_annotation  # noqa: E402

DEFAULT_ORG = "quaternionmedia"
WORKSPACE = Path(__file__).resolve().parent / "workspace.yaml"

READY, NO_TAGS, FAILING, UNKNOWN = "READY", "NO TAGS", "FAILING", "UNKNOWN"


@dataclass
class RepoResult:
    repo: str
    state: str = NO_TAGS
    reason: str | None = None
    tags: list = field(default_factory=list)  # (name, ok, [problems])

    @property
    def failing(self) -> list:
        return [t for t in self.tags if not t[1]]


def gh_json(path: str) -> tuple[bool, object]:
    """GET one API path. Returns (ok, parsed). A 404 is `ok` with None."""
    proc = subprocess.run(
        ["gh", "api", path],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if proc.returncode != 0:
        # An empty tag namespace 404s. That is "no tags", not "unreadable" --
        # and the two must not collapse, since one is a state and one is a gap.
        if "Not Found" in (proc.stdout + proc.stderr):
            return True, None
        return False, (proc.stderr or proc.stdout).strip().splitlines()[:1]
    try:
        return True, json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        return False, [f"unparseable response: {exc}"]


def roster(workspace: Path, org: str) -> list[str]:
    """Repository names from ci/workspace.yaml, as owner/name.

    Parsed without a YAML dependency: the file is a flat list of `- name:`
    entries and this reads exactly that, so the audit runs on a bare Python.
    """
    if not workspace.is_file():
        return []
    names: list[str] = []
    for line in workspace.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("- name:"):
            names.append(f"{org}/{stripped.split(':', 1)[1].strip()}")
    return names


def judge_payload(repo: str, refs: object, bodies: dict[str, str]) -> RepoResult:
    """Judge one repository from data already fetched.

    Split from every network call so the whole rule is testable against a
    captured payload -- the tests feed this, and nothing in them reaches a host.

    >>> refs = [{"ref": "refs/tags/v1.0.0", "object": {"type": "commit", "sha": "a"}}]
    >>> judge_payload("o/r", refs, {}).state
    'FAILING'
    >>> judge_payload("o/r", None, {}).state
    'NO TAGS'
    """
    result = RepoResult(repo=repo)
    if refs is None:
        return result
    if not isinstance(refs, list):
        # A single ref comes back as an object rather than a list of one.
        refs = [refs]

    v_tags = [r for r in refs if str(r.get("ref", "")).startswith("refs/tags/v")]
    if not v_tags:
        return result

    for ref in v_tags:
        name = str(ref["ref"]).removeprefix("refs/tags/")
        obj = ref.get("object") or {}
        verdict = check_annotation(name, str(obj.get("type", "")), bodies.get(obj.get("sha", ""), ""))
        result.tags.append((name, verdict.ok, verdict.problems))

    result.state = FAILING if result.failing else READY
    return result


def audit_repo(repo: str) -> RepoResult:
    """Fetch and judge one repository."""
    ok, refs = gh_json(f"repos/{repo}/git/refs/tags")
    if not ok:
        return RepoResult(repo=repo, state=UNKNOWN, reason=str(refs))

    bodies: dict[str, str] = {}
    if isinstance(refs, list):
        for ref in refs:
            obj = ref.get("object") or {}
            if obj.get("type") == "tag" and obj.get("sha"):
                body_ok, body = gh_json(f"repos/{repo}/git/tags/{obj['sha']}")
                if not body_ok:
                    return RepoResult(repo=repo, state=UNKNOWN, reason=str(body))
                bodies[obj["sha"]] = (body or {}).get("message", "")

    return judge_payload(repo, refs, bodies)


def report(results: list[RepoResult], verbose: bool) -> None:
    width = max((len(r.repo) for r in results), default=10)
    for r in results:
        count = f"{len(r.tags)} tag(s)" if r.tags else ""
        print(f"{r.state:<8} {r.repo:<{width}}  {count}")
        if r.reason:
            print(f"           unreadable: {r.reason}")
        for name, ok, problems in r.tags:
            if ok and not verbose:
                continue
            print(f"           {'ok  ' if ok else 'FAIL'} {name}")
            for problem in problems:
                print(f"                  - {problem}")

    ready = [r.repo for r in results if r.state == READY]
    print("\nReady to demo -- every v* tag carries its claims:")
    print("  " + (", ".join(ready) if ready else "(none)"))

    for state, label in ((FAILING, "Tags that do not carry their claims"),
                         (UNKNOWN, "Could not be measured (not the same as clean)"),
                         (NO_TAGS, "No v* tag, so no release claim made")):
        named = [r.repo for r in results if r.state == state]
        if named:
            print(f"\n{label}:\n  " + ", ".join(named))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo", action="append", help="owner/name; repeatable")
    parser.add_argument("--org", default=DEFAULT_ORG)
    parser.add_argument("--workspace", default=str(WORKSPACE))
    parser.add_argument("--from-json", help="captured {repo: {refs, bodies}} payload")
    parser.add_argument("--verbose", action="store_true", help="list passing tags too")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="exit non-zero if any tag fails or any repository is unreadable",
    )
    args = parser.parse_args(argv)

    if args.from_json:
        payload = json.loads(Path(args.from_json).read_text(encoding="utf-8"))
        results = [
            judge_payload(repo, data.get("refs"), data.get("bodies", {}))
            for repo, data in payload.items()
        ]
    else:
        repos = args.repo or roster(Path(args.workspace), args.org)
        if not repos:
            print("no repositories to audit -- nothing was checked", file=sys.stderr)
            return 1
        results = [audit_repo(r) for r in repos]

    report(results, args.verbose)

    if args.strict and any(r.state in (FAILING, UNKNOWN) for r in results):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
