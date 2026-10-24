#!/usr/bin/env python3
"""What the projects are waiting on this organisation for.

Propagation runs one way: `main` flows outward (`handbook/propagation-runbook.md`),
and `.github/workflows/namespace-guard.yml` refuses org content pushed onto a
project branch. This reads the return path. Every `Proposed` record names what
it pends on (`project-seed/adr/TEMPLATE.md` asks for the row; no lint checks
for it, and a record without one is skipped here, so its question never
reaches this list), and many of those rows name the organisation rather than the
project: an amendment nobody has ratified, a carve-out nobody has recognised, a
licensing input nobody has settled. This invents no channel; it reads that one.

Rows are grouped by what is being waited on, so one org action that unblocks
many projects shows as one group rather than as many problems, and the group
with the most projects is the cheapest thing the organisation can do.

What it does not do:

  * **It does not decide what is an org question.** A `Pends on` row is prose
    written by a person. This groups identical text and reports the rest
    verbatim; it does not parse intent, because a classifier that guessed
    wrong would move a project's question into a bucket nobody reads.
  * **It does not read a project's own repository.** Records on a
    `project/<name>` branch are read from refs here, with no network. A project
    that keeps `adr/` locally -- rad does, and the seed workflow supports it --
    is reported as unreadable *from here*, by name, rather than as having
    nothing to say. That is the same distinction `status/governance.yaml` draws
    with `records_dir`, and this is the second reader of it.
  * **It does not close anything.** A row stops appearing when the record's
    author changes it, which is the only party that can know.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from collections import defaultdict
from dataclasses import dataclass

PROJECT_NS = "project/"

# The template's row, matched on the whole line so a `Pends on` mentioned in
# prose is not mistaken for the declaration. `adr_lint` requires this shape.
PENDS_ON = re.compile(r"^\|\s*\*\*Pends on\*\*\s*\|\s*(.+?)\s*\|\s*$", re.MULTILINE)

# A row that opens with one of these is the record saying it waits on no input.
# Matched at the start only: "Nothing in this project has settled X" is a real
# dependency and must not be swallowed by a prefix that happens to appear.
SETTLED = re.compile(r"^(nothing|none|n/?a)\b", re.I)

# Where the shared part of an ask ends and one project's own detail begins: a
# sentence break, an aside, or a dash in any of the four spellings this corpus
# uses. Space-delimited for the hyphens so a hyphenated word is not a break.
SEPARATOR = re.compile(r"[.;]|\s[—–-]{1,2}\s|\s\(")


def git(*args: str, repo: str = ".") -> str:
    done = subprocess.run(("git", "-C", repo, *args), capture_output=True,
                          text=True, encoding="utf-8", errors="replace")
    return done.stdout if done.returncode == 0 else ""


def lines(*args: str, repo: str = ".") -> list[str]:
    return [line for line in git(*args, repo=repo).splitlines() if line.strip()]


@dataclass(frozen=True)
class Waiting:
    """One record, and the thing it says it is waiting for."""

    project: str
    record: str
    pends_on: str

    @property
    def key(self) -> str:
        """What two rows must share to be the same ask.

        Normalised on case and whitespace and cut at the first sentence break,
        because the same request is written with different trailing detail in
        different projects -- and cutting is the whole reason the estate-wide
        repeat becomes visible at all. Nothing fuzzier: two rows that differ in
        their first clause are two asks until a person says otherwise.

        The dash has four spellings in this corpus (em, en, ASCII hyphen and a
        doubled hyphen), and the cut honours all four, so one ask written with
        different dashes stays one group. A parenthesis opens an aside for the
        same reason.
        """
        head = SEPARATOR.split(self.pends_on, maxsplit=1)[0]
        return " ".join(head.lower().split())


def project_branches(repo: str, remote: str) -> list[str]:
    refs = lines("for-each-ref", "--format=%(refname:short)",
                 f"refs/remotes/{remote}/{PROJECT_NS}*", repo=repo)
    return refs or lines("for-each-ref", "--format=%(refname:short)",
                         f"refs/heads/{PROJECT_NS}*", repo=repo)


def records_on(branch: str, repo: str) -> list[str]:
    names = lines("ls-tree", "-r", "--name-only", branch, "--", "adr",
                  repo=repo)
    return [n for n in names
            if n.endswith(".md")
            and n.rsplit("/", 1)[-1] not in ("README.md", "TEMPLATE.md")]


def survey(repo: str = ".", remote: str = "origin") -> tuple[list[Waiting], list[str]]:
    """Every unsettled `Pends on`, and the projects that could not be read.

    The second half of the tuple is not an error list. A project whose records
    are not on its branch has not thereby said nothing, and reporting it as
    zero would be this estate's most-repeated mistake -- an empty query read as
    a clean answer.
    """
    found: list[Waiting] = []
    silent: list[str] = []
    for branch in project_branches(repo, remote):
        name = branch.split(PROJECT_NS, 1)[1]
        records = records_on(branch, repo)
        if not records:
            silent.append(name)
            continue
        for path in records:
            row = PENDS_ON.search(git("show", f"{branch}:{path}", repo=repo))
            if not row:
                continue
            text = row.group(1).strip()
            if SETTLED.match(text):
                continue
            found.append(Waiting(name, path.rsplit("/", 1)[-1], text))
    return found, sorted(silent)


def render(found: list[Waiting], silent: list[str]) -> str:
    """What a person reads to pick the one thing worth doing.

    Ordered by how many projects an answer would unblock, because that is the
    question this view exists to answer and no per-project reading can.
    """
    grouped: dict[str, list[Waiting]] = defaultdict(list)
    for row in found:
        grouped[row.key].append(row)

    out: list[str] = []
    ranked = sorted(grouped.values(),
                    key=lambda rows: (-len({r.project for r in rows}),
                                      rows[0].key))
    for rows in ranked:
        projects = sorted({r.project for r in rows})
        out.append(f"  {len(projects)} project(s): {', '.join(projects)}")
        # The longest wording of the shared ask, so the group's line carries
        # the most detail any of its records bothered to write.
        out.append(f"      {max((r.pends_on for r in rows), key=len)}")
        for row in sorted(rows, key=lambda r: (r.project, r.record)):
            out.append(f"        {row.project}/{row.record}")
        out.append("")

    if not found:
        out.append("  No project record names an unsettled input.")
        out.append("")

    if silent:
        out.append("  No records on the branch, so these projects are UNKNOWN "
                   "rather than quiet:")
        out.append(f"      {', '.join(silent)}")
        # Two things produce an empty `adr/` on a project branch -- records
        # kept in the project's own repository, and a branch nobody has
        # written a record on yet -- and this cannot tell them apart from
        # here. Naming the field that can is the honest end of the sentence;
        # asserting which case each project is in would be a guess printed as
        # a finding.
        out.append("      Either the records are in the project's own "
                   "repository or none has been written. "
                   "`status/governance.yaml`'s `records_dir` says which.")
        out.append("")

    out.append("  A row leaves this list when its own record's author changes "
               "it. Nothing here closes anything.")
    return "\n".join(out) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="What the projects are waiting on this organisation for.")
    parser.add_argument("--repo", default=".")
    parser.add_argument("--remote", default="origin")
    args = parser.parse_args(argv)

    # The rows are this corpus's own prose and are full of em dashes; on a
    # console whose codepage cannot encode them they would come back as
    # replacement characters, which reads as badly encoded records. Same
    # reconfiguration as `ci/disk_dashboard.py`.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    found, silent = survey(args.repo, args.remote)
    sys.stdout.write(render(found, silent))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
