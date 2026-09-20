#!/usr/bin/env python3
"""Every repository the org rosters, and what of it exists on this disk alone.

**A CONSOLIDATION STARTS WITH A QUESTION NOBODY COULD ANSWER FROM ONE PLACE.**
`project-seed/ci/branch_census.py` says, for one repository, which branches
hold commits that exist on one disk. Before the estate's branches were brought
to the host, somebody ran that census by hand in every clone the roster names,
kept the answers in a scratch file, and then did it again when a session
elsewhere had moved a branch. It was the single most expensive step of the
whole cycle, and every one of its answers was a fact git already held.

This module asks the same question of every repository at once. It reads the
roster `ci/make_workspace.py` reads, resolves each entry to a clone the same
way, and asks each clone -- with read commands only -- what it holds that the
host does not:

  one-copy    a local branch ahead of the default branch and not on `origin`
              at all; deleting the clone deletes the work. Each is marked as
              *folded* when the current HEAD already contains it, so it can
              go once HEAD reaches the host, or *independent* when it cannot.
  ahead       a local branch that is on `origin` but carries commits its
              remote copy does not. Pushing it is the whole remedy.
  dirty       uncommitted changes in the working tree. Not a branch, and the
              cheapest thing here to lose.

With the host reachable it also asks, per repository, how many pull requests
the current user has open, because one open pull request per repository per
contributor is the sequencing rule (`handbook/async-contract.md` 1) and a
draft holds the slot like any other.

WHAT IT REFUSES TO DO.

  * **It never writes.** No push, fetch, prune, merge or delete, and no flag
    to ask for one. A survey that can also act is one somebody runs in a
    hurry, and the `git` helper here refuses any verb outside a short list of
    readers. `ci/tests/test_estate.py` breaks that list and watches it fire.
  * **It is a reading, not a gate.** A completed survey exits zero whatever
    it found; the only non-zero exit is a roster that could not be read. A
    tool that failed on the estate's state would be run less, which is the
    opposite of what a survey is for.
  * **It drops nothing.** A roster entry no candidate path resolves is
    reported as MISSING with its candidates, as the workspace generator does,
    because a survey silently short of two repositories reads exactly like a
    survey of everything.

WHAT IT CANNOT TELL YOU. Whether a one-copy branch is worth keeping. It says
what would be lost and how much, and stops; the deletion is a person's act,
as it is for the single-repository census. Nor can it see a clone the roster
does not name: a repository is surveyed because somebody wrote it down.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

import yaml

# This module is imported two ways: as `ci.<name>` by the qm CLI, and as a
# bare script by anyone running it directly. A plain sibling import works
# only in the second. Putting this file's own directory first makes the
# roster loader and the workspace resolver resolvable under both, which is
# what `ci/make_workspace.py` does for the same reason.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from make_workspace import resolve  # noqa: E402
from roster import ROSTER, label, load  # noqa: E402

CORPUS = Path(__file__).resolve().parent.parent

# Every git verb this module may run. The helper refuses any other, so the
# promise in the header is enforced by the code and not by a reader's trust.
READ_VERBS = frozenset({
    "rev-parse", "status", "for-each-ref", "rev-list", "ls-remote",
    "merge-base", "symbolic-ref",
})

# The current branch relative to a one-copy branch: the checked-out branch
# itself, an ancestor of it, or neither.
HEAD = "head"
FOLDED = "folded"
INDEPENDENT = "independent"


class Refused(RuntimeError):
    """A git verb outside `READ_VERBS`, which this module must never run."""


def run_git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    """`git -C repo <args>`, refused unless the verb is a reader.

    The one place git is spawned, so the refusal cannot be walked around by
    a later edit that forgot the list existed.
    """
    if not args or args[0] not in READ_VERBS:
        raise Refused(f"git {' '.join(args) or '<nothing>'} is not a read")
    return subprocess.run(("git", "-C", str(repo), *args), capture_output=True,
                          text=True, encoding="utf-8", errors="replace")


def git(repo: Path, *args: str) -> str | None:
    """Standard output, or None when git says no.

    None rather than an empty string, because several of the questions asked
    here have an empty answer that means something -- no branches, no changes
    -- and a reader must be able to tell that from a command that failed.
    """
    done = run_git(repo, *args)
    return done.stdout if done.returncode == 0 else None


def lines(repo: Path, *args: str) -> list[str] | None:
    out = git(repo, *args)
    return None if out is None else [l for l in out.splitlines() if l.strip()]


def run_gh(args: list[str], cwd: Path) -> subprocess.CompletedProcess:
    """One seam for the host CLI, so a test can stand in for it."""
    return subprocess.run(("gh", *args), capture_output=True, text=True,
                          encoding="utf-8", errors="replace", cwd=str(cwd))


@dataclass
class OneCopy:
    """A local branch no copy of which is on `origin`."""

    name: str
    ahead: int          # commits not on origin/<default>
    relation: str       # HEAD, FOLDED or INDEPENDENT, against the current HEAD


@dataclass
class Ahead:
    """A local branch that is on `origin` and ahead of its copy there."""

    name: str
    unpushed: int       # commits the remote copy does not have


@dataclass
class Repository:
    """One roster entry, and what its clone holds that the host does not."""

    name: str
    path: str | None = None            # None is MISSING
    candidates: list[str] = field(default_factory=list)
    branch: str = ""                   # "(detached)" when HEAD is not a branch
    dirty: int = 0
    default: str = ""
    one_copy: list[OneCopy] = field(default_factory=list)
    ahead: list[Ahead] = field(default_factory=list)
    open_prs: list[dict] | None = None  # None: not asked, or the host said no
    notes: list[str] = field(default_factory=list)

    @property
    def missing(self) -> bool:
        return self.path is None

    @property
    def holds_one_copy(self) -> bool:
        """Work that is committed and exists on this disk alone.

        Both classes count: a branch the host has never seen and a branch
        whose remote copy is behind. One definition, used by the table, the
        detail blocks and the closing line, so they cannot disagree.
        """
        return bool(self.one_copy or self.ahead)

    @property
    def over_slot(self) -> bool:
        return self.open_prs is not None and len(self.open_prs) > 1


def default_branch(repo: Path, remote: str, online: bool) -> tuple[str, str]:
    """The default branch on the remote, and where the answer came from.

    The tracking symref is what a clone recorded; the remote's own HEAD is the
    truth and costs a round trip. Neither is assumed to be `main` until both
    have been asked, and the fallback says that it is a fallback.
    """
    head = git(repo, "symbolic-ref", f"refs/remotes/{remote}/HEAD")
    if head:
        return head.strip().rsplit("/", 1)[-1], "tracking ref"
    if online:
        out = git(repo, "ls-remote", "--symref", remote, "HEAD") or ""
        for line in out.splitlines():
            if line.startswith("ref: refs/heads/"):
                return line.split()[1].rsplit("/", 1)[-1], "ls-remote"
    return "main", "assumed"


def remote_heads(repo: Path, remote: str, online: bool) -> dict[str, str] | None:
    """Branch name -> tip sha, as the remote holds it.

    Online this is one `ls-remote --heads` for the whole remote rather than
    one per branch: the same question, answered once, and the estate has
    enough branches for the difference to be minutes. Offline it is the
    tracking refs, which are the remote as of the last fetch -- a fact this
    clone recorded rather than one the host confirmed, and the output says so.
    """
    if online:
        out = lines(repo, "ls-remote", "--heads", remote)
        if out is None:
            return None
        found = {}
        for line in out:
            sha, _, ref = line.partition("\t")
            found[ref.strip().removeprefix("refs/heads/")] = sha
        return found
    out = lines(repo, "for-each-ref", "--format=%(objectname) %(refname:short)",
                f"refs/remotes/{remote}")
    if out is None:
        return None
    prefix = f"{remote}/"
    found = {}
    for line in out:
        sha, _, ref = line.partition(" ")
        # `origin/HEAD` is a symbolic ref, not a branch.
        if ref.endswith("/HEAD") or not ref.startswith(prefix):
            continue
        found[ref[len(prefix):]] = sha
    return found


def count(repo: Path, spec: str) -> int | None:
    out = git(repo, "rev-list", "--count", spec)
    return None if out is None else int(out.strip() or 0)


def relation_to_head(repo: Path, branch: str, current: str) -> str:
    if branch == current:
        return HEAD
    done = run_git(repo, "merge-base", "--is-ancestor", branch, "HEAD")
    # Exit 0 is "yes", 1 is "no", anything else is git failing; a failure is
    # reported as independent because that is the reading that loses nothing.
    return FOLDED if done.returncode == 0 else INDEPENDENT


def survey_repository(entry: dict, path: Path, remote: str, online: bool) -> Repository:
    repo_path = path
    repo = Repository(name=label(entry), path=str(path),
                      candidates=list(entry.get("paths", [])))

    current = (git(repo_path, "rev-parse", "--abbrev-ref", "HEAD") or "").strip()
    repo.branch = "(detached)" if current in ("", "HEAD") else current

    changes = lines(repo_path, "status", "--porcelain")
    if changes is None:
        repo.notes.append("working tree could not be read")
    else:
        repo.dirty = len(changes)

    repo.default, source = default_branch(repo_path, remote, online)
    if source == "assumed":
        repo.notes.append(f"default branch assumed to be {repo.default}; "
                          f"no {remote}/HEAD and the remote was not asked")

    heads = remote_heads(repo_path, remote, online)
    if heads is None:
        repo.notes.append(f"{remote} could not be read; every local branch "
                          f"is reported as one copy")
        heads = {}
    elif not online:
        repo.notes.append(f"{remote} read from tracking refs, as of the last fetch")

    base = f"{remote}/{repo.default}"
    if git(repo_path, "rev-parse", "--verify", "--quiet", f"refs/remotes/{base}") is None:
        repo.notes.append(f"no {base} in this clone; nothing to measure ahead of")
        return repo

    for name in lines(repo_path, "for-each-ref", "--format=%(refname:short)",
                      "refs/heads") or []:
        if name in heads:
            # The remote's own tip, not the tracking ref: online, the sha came
            # from the host this run. It may be an object this clone has never
            # fetched, in which case rev-list cannot count and says so.
            unpushed = count(repo_path, f"{heads[name]}..{name}")
            if unpushed is None:
                repo.notes.append(f"{name}: {remote} tip not in this clone; "
                                  f"cannot count what is unpushed")
            elif unpushed:
                repo.ahead.append(Ahead(name, unpushed))
            continue
        ahead = count(repo_path, f"{base}..{name}")
        if ahead:
            repo.one_copy.append(
                OneCopy(name, ahead, relation_to_head(repo_path, name, current)))
    return repo


def host_pull_requests(repo: Repository) -> None:
    """The current user's open pull requests, drafts included, via gh.

    A failure -- no host remote, not signed in, the host down -- leaves
    `open_prs` as None and says why, because a list that read as empty would
    report a free slot on a repository nobody asked.
    """
    done = run_gh(["pr", "list", "--author", "@me", "--state", "open",
                   "--json", "number,headRefName,isDraft"], Path(repo.path))
    if done.returncode != 0:
        detail = (done.stderr or "").strip().splitlines()
        repo.notes.append("pull requests unknown: "
                          + (detail[0] if detail else "gh gave no reason"))
        return
    try:
        repo.open_prs = json.loads(done.stdout or "[]")
    except json.JSONDecodeError as exc:
        repo.notes.append(f"pull requests unknown: gh output was not JSON ({exc})")


def survey(roster: list[dict], search_roots: list[Path], remote: str = "origin",
           online: bool = True) -> list[Repository]:
    """Every roster entry, surveyed or reported MISSING. Never fewer rows."""
    found: list[Repository] = []
    for entry in roster:
        path = resolve(entry, search_roots)
        if path is None:
            found.append(Repository(name=label(entry),
                                    candidates=list(entry.get("paths", []))))
            continue
        repo = survey_repository(entry, path, remote, online)
        if online:
            host_pull_requests(repo)
        found.append(repo)
    return found


def totals(found: list[Repository]) -> dict[str, int]:
    """The reading's subject, and the one place a bare count belongs."""
    present = [r for r in found if not r.missing]
    return {
        "named": len(found),
        "found": len(present),
        "missing": len(found) - len(present),
        "with_one_copy": sum(1 for r in present if r.holds_one_copy),
        "dirty": sum(1 for r in present if r.dirty),
    }


def render(found: list[Repository], online: bool) -> str:
    """One row per repository, then detail for any row that needs a person."""
    out: list[str] = []
    width = max(len("repository"), *(len(r.name) for r in found))
    prs = "prs" if online else "prs (offline)"
    out.append(f"  {'repository':<{width}}  {'branch':<28}  dirty  one-copy  ahead  {prs}")
    for r in found:
        if r.missing:
            out.append(f"  {r.name:<{width}}  MISSING")
            continue
        if r.open_prs is None:
            slot = "-" if not online else "?"
        else:
            slot = str(len(r.open_prs)) + (" OVER" if r.over_slot else "")
        out.append(f"  {r.name:<{width}}  {r.branch[:28]:<28}  {r.dirty:>5}  "
                   f"{len(r.one_copy):>8}  {len(r.ahead):>5}  {slot}")
    out.append("")

    for r in found:
        if r.missing or not (r.holds_one_copy or r.dirty or r.over_slot):
            continue
        out.append(f"  {r.name}  ({r.path})")
        if r.dirty:
            out.append(f"      {r.dirty} uncommitted change(s) on {r.branch}")
        for b in r.one_copy:
            out.append(f"      one-copy  +{b.ahead:<3} {b.name}  [{b.relation}]")
        for b in r.ahead:
            out.append(f"      ahead     +{b.unpushed:<3} {b.name}  "
                       f"(not on its remote copy)")
        if r.over_slot:
            heads = ", ".join(f"#{p.get('number')} {p.get('headRefName')}"
                              + (" draft" if p.get("isDraft") else "")
                              for p in r.open_prs)
            out.append(f"      over the one-PR slot: {heads}")
        out.append("")

    for r in found:
        if r.missing:
            # A private entry carries no paths in the committed roster; they
            # come from the companion file `ci/roster.py` merges in. Without
            # it there was nothing to try, which is a different fact from
            # trying and failing.
            tried = (", ".join(r.candidates) if r.candidates
                     else "no candidate paths; a private entry needs "
                          "ci/workspace-private.yaml")
            out.append(f"  {r.name}: MISSING -- {tried}")
    notes = [(r.name, n) for r in found for n in r.notes
             if not n.endswith("as of the last fetch")]
    if any(r.missing for r in found) and notes:
        out.append("")
    for name, note in notes:
        out.append(f"  {name}: {note}")
    if any(r.missing for r in found) or notes:
        out.append("")

    t = totals(found)
    out.append(f"  {t['named']} repositories named, {t['found']} found on this "
               f"disk, {t['with_one_copy']} holding committed work with one copy"
               + (f", {t['dirty']} with uncommitted changes" if t["dirty"] else "")
               + ".")
    out.append("  [folded] is contained in that clone's HEAD; [independent] "
               "is not. Either exists on this disk alone.")
    if not online:
        out.append("  --offline: the remote is as of the last fetch, and no "
                   "pull request was asked about.")
    out.append("  This survey writes nothing. Pushing, merging and deleting "
               "are a person's acts.")
    return "\n".join(out) + "\n"


def as_document(found: list[Repository], roster: Path, search_roots: list[Path],
                online: bool) -> dict:
    return {
        "roster": str(roster),
        "search_roots": [str(p) for p in search_roots],
        "offline": not online,
        "repositories": [
            {**asdict(r), "missing": r.missing, "holds_one_copy": r.holds_one_copy,
             "over_slot": r.over_slot}
            for r in found
        ],
        "totals": totals(found),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Every rostered repository, and what of it exists on this "
                    "disk alone.")
    parser.add_argument("--roster", type=Path, default=ROSTER)
    parser.add_argument(
        "--search-root", action="append", type=Path, default=[],
        help="a directory the roster's paths are relative to. Repeatable. "
             "Default: two directories above the corpus clone, as the "
             "workspace generator assumes.")
    parser.add_argument("--remote", default="origin")
    parser.add_argument("--offline", action="store_true",
                        help="ask nothing of the host: no ls-remote, no gh")
    parser.add_argument("--json", action="store_true",
                        help="emit the survey as one JSON document")
    args = parser.parse_args(argv)

    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    try:
        roster = load(args.roster)
    except (OSError, ValueError, yaml.YAMLError) as exc:
        print(f"estate: cannot read the roster at {args.roster}: {exc}",
              file=sys.stderr)
        return 2
    if not roster:
        print(f"estate: {args.roster} lists no repositories", file=sys.stderr)
        return 2

    search_roots = [p.resolve() for p in args.search_root] or [CORPUS.parent.parent]
    online = not args.offline
    found = survey(roster, search_roots, args.remote, online)

    if args.json:
        json.dump(as_document(found, args.roster, search_roots, online),
                  sys.stdout, indent=2)
        sys.stdout.write("\n")
    else:
        sys.stdout.write(render(found, online))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
