#!/usr/bin/env python3
"""One address for one data point, so two dashboards can show the same thing.

    uv run qm addresses                      # the grammar, and every kind
    uv run qm addresses --parse <address>    # what an address denotes
    uv run qm addresses --check              # every conformance vector round-trips

WHY THIS EXISTS. dossier and qmcp hold overlapping facts about the same
repositories -- branches, pull requests, deltas, tool invocations -- and each
names them its own way. dossier builds names by string interpolation in
`parsers/autolinker.py` and reads them back by substring in `cli.py`
(`elif "/branch/" in name`). qmcp names nothing at all: a step is a bare `name`
and an invocation is a bare UUID. Two views of one dataset need one way of
pointing at a row, and this is it.

THE DEFECT THAT FORCED IT. dossier slugs a branch with
`branch.name.replace("/", "-")`, so `evolve/protect-main` is addressed as
`.../branch/evolve-protect-main`. That is not reversible -- a branch legitimately
named `evolve-protect-main` produces the identical address -- and **30 of the 32
branches in this corpus contain a slash**, because every org namespace is
`evolve/`, `project/`, `perspective/` or `propagate/`. Listing active branches
as deltas means linking a row back to a ref, and today that link is broken for
almost every branch in the organisation.

THE GRAMMAR, and the one rule that makes it reversible:

    <owner>/<repo>/<kind>/<id>

**The first three segments are owner, repo and kind. Everything after is the id,
verbatim, slashes included.** So `quaternionmedia/qm/branch/evolve/protect-main`
parses to id `evolve/protect-main` and formats back to itself. No slug, no
collision, nothing lost. A bare `<owner>/<repo>` denotes the repository.

`KINDS` is closed on purpose. If the third segment is not a known kind then the
string is not a repo-scoped address, which is what stops `owner/repo/some/path`
being read as one.

WHAT THIS CANNOT DO. Tell you whether the thing addressed exists.
`quaternionmedia/qm/pr/99999` is a well-formed address for a pull request nobody
opened. Resolution is each system's own job, and folding it in here would make
rendering a dashboard depend on a network call.

It also does not own dossier's global buckets beyond reserving their prefixes.
`github/user/<u>`, `lang/<l>` and `pkg/<p>` are dossier's and are not
repo-scoped. They are named here so that an owner called `lang` is a collision
somebody chose rather than one they discovered.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VECTORS = ROOT / "project-seed" / "address-vectors.json"

SCHEMA = 1

# Closed set. A third segment outside it is not a kind, and the string is then
# not a repo-scoped address -- the check that keeps `owner/repo/a/b` from being
# read as one.
KINDS: dict[str, str] = {
    "branch": "a git ref, named exactly as git names it",
    "pr": "a pull request, by number",
    "issue": "an issue, by number",
    "ver": "a version tag, by tag name",
    "doc": "a document section, by type-slug",
    "delta": "a unit of work, by its short name",
    "invocation": "a recorded tool call, by id",
}

# Not repo-scoped, and reserved so that an owner with one of these names is a
# collision somebody chose rather than one they discovered.
GLOBAL_PREFIXES = ("github/user/", "lang/", "pkg/")

REPO = "repo"


@dataclass(frozen=True)
class Address:
    """A parsed address. `kind` is `repo` for a bare `owner/repo`."""

    owner: str
    repo: str
    kind: str
    id: str = ""

    @property
    def project(self) -> str:
        return f"{self.owner}/{self.repo}"

    def format(self) -> str:
        if self.kind == REPO:
            return self.project
        return f"{self.project}/{self.kind}/{self.id}"


def is_global(text: str) -> bool:
    return text.startswith(GLOBAL_PREFIXES)


def parse(text: str) -> Address | None:
    """The address this string denotes, or None when it denotes none.

    None rather than an exception: callers sweep mixed lists of names, most of
    which are not addresses, and a parser that raised would make the ordinary
    case the exceptional one.
    """
    if not text or is_global(text):
        return None
    parts = text.split("/")
    if len(parts) < 2 or not all(parts[:2]):
        return None
    owner, repo = parts[0], parts[1]
    if len(parts) == 2:
        return Address(owner, repo, REPO)
    kind = parts[2]
    if kind not in KINDS:
        return None
    # Everything after the kind, rejoined. This is the whole reversibility
    # property: a branch id keeps its slashes instead of being slugged into
    # something no git command accepts.
    identifier = "/".join(parts[3:])
    if not identifier:
        return None
    return Address(owner, repo, kind, identifier)


def format_address(owner: str, repo: str, kind: str, identifier: str = "") -> str:
    if kind != REPO and kind not in KINDS:
        raise ValueError(f"{kind!r} is not a kind. Known: {', '.join(sorted(KINDS))}")
    if kind != REPO and not identifier:
        raise ValueError(f"a {kind} address needs an id")
    return Address(owner, repo, kind, identifier).format()


def load_vectors(path: Path = VECTORS) -> list[dict]:
    """The shared conformance cases.

    Committed under `project-seed/` so every fork receives them through the
    governance submodule. Two implementations of this grammar stay honest by
    running the same cases, which is the alternative to one importing the other.
    """
    if not path.is_file():
        raise SystemExit(f"{path}: no vectors. Nothing would be verified.")
    data = json.loads(path.read_text(encoding="utf-8"))
    cases = data.get("cases") or []
    if not cases:
        raise SystemExit(f"{path}: no cases. An empty vector file verifies nothing.")
    return cases


def check(cases: list[dict]) -> list[str]:
    """Every vector parses as declared, and every valid one formats back.

    The round trip is the assertion. A parser tested only on its output is one
    that can quietly drop a segment.
    """
    problems: list[str] = []
    for case in cases:
        text = case["address"]
        got = parse(text)
        if not case.get("valid", True):
            if got is not None:
                problems.append(f"{text!r}: parsed, and the vector says it must not")
            continue
        if got is None:
            problems.append(f"{text!r}: did not parse, and the vector says it must")
            continue
        for field in ("owner", "repo", "kind", "id"):
            if field in case and getattr(got, field) != case[field]:
                problems.append(
                    f"{text!r}: {field} is {getattr(got, field)!r}, "
                    f"vector says {case[field]!r}"
                )
        if got.format() != text:
            problems.append(
                f"{text!r}: formats back as {got.format()!r}. An address that "
                f"does not round-trip cannot link a row to the thing it names"
            )
    return problems


def render(cases: list[dict]) -> str:
    out = [
        "<owner>/<repo>/<kind>/<id>",
        "",
        "The first three segments are owner, repo and kind. Everything after is",
        "the id, verbatim -- slashes included, so a branch keeps the name git",
        "gave it. A bare <owner>/<repo> denotes the repository.",
        "",
        "kinds:",
    ]
    for kind, meaning in sorted(KINDS.items()):
        out.append(f"  {kind:<11} {meaning}")
    out += [
        "",
        "reserved, and not repo-scoped:",
        f"  {', '.join(GLOBAL_PREFIXES)}",
        "",
        f"{len(cases)} conformance vector(s) in "
        f"{VECTORS.relative_to(ROOT).as_posix()}, shared with every fork.",
        "",
        "This is a grammar. It does not tell you the thing addressed exists.",
    ]
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--vectors", default=str(VECTORS))
    parser.add_argument("--parse", help="show what one address denotes")
    parser.add_argument("--check", action="store_true",
                        help="exit non-zero if any vector fails to round-trip")
    args = parser.parse_args(argv)

    if args.parse:
        found = parse(args.parse)
        if found is None:
            print(f"{args.parse!r} is not an address.")
            print("Not an error: most names are not addresses, and a sweep over "
                  "mixed names relies on that.")
            return 0
        print(f"owner  {found.owner}")
        print(f"repo   {found.repo}")
        print(f"kind   {found.kind}  ({KINDS.get(found.kind, 'the repository itself')})")
        print(f"id     {found.id or '-'}")
        print(f"back   {found.format()}")
        return 0

    cases = load_vectors(Path(args.vectors))

    if args.check:
        problems = check(cases)
        for problem in problems:
            print(f"  - {problem}", file=sys.stderr)
        if problems:
            print(f"\n{len(problems)} problem(s) against {args.vectors}.", file=sys.stderr)
            return 1
        print(f"addresses: {len(cases)} vector(s), every one parsing as declared "
              f"and round-tripping.")
        print("This does NOT mean anything addressed exists -- this is a grammar, "
              "and resolution is each system's own.")
        return 0

    print(render(cases))
    return 0


if __name__ == "__main__":
    sys.exit(main())
