#!/usr/bin/env python3
"""Merge it yourself once every gate is green -- with the runbook's discipline held.

    uv run qm merge                                  # every roster repository
    uv run qm merge --repo owner/name                # one repository
    uv run qm merge --repo owner/name --pr 12        # re-verify one, and stop
    uv run qm merge --repo owner/name --pr 12 --yes  # the act

**THE RULE IS ONE SENTENCE AND THE PRACTICE WAS SEVEN HAND-RUN CHECKS.**
`AGENTS.md` item 3: the author merges once every gate is green.
`handbook/propagation-runbook.md`: with a merge commit, never squash, never
rebase, because a rewritten branch breaks every submodule pin pointing at it.
The session that closed the estate's backlog merged one pull request at a time
and, before each one, read the live state again by hand -- state, mergeability,
the host's own verdict, every check -- because a pull request that was green an
hour ago is a pull request that was green an hour ago. Seven times, the same
four reads and the same one write, and nothing held the four to the one.

This holds them. The reading half is the default and mutates nothing; the act
is one flag away and refuses unless the reading, taken at that moment, says
READY.

READY IS ONE DEFINITION, IN `blockers`, and both halves use it. A listing that
said READY where the act would refuse -- or the reverse -- is two definitions
of the same rule, and two definitions drift the first time one is fixed.

WHAT IT REFUSES TO DO.

  * **It never squashes and never rebases.** Both flags exist so that passing
    one is answered with the reason rather than with argparse's usage line,
    and neither reaches the host. The merge is `--merge --delete-branch` and
    nothing else.
  * **It never merges without `--yes`.** Merging is the author's act; the flag
    is the signature. Without it the act mode re-verifies, says what it found,
    and stops with a non-zero status, so a script that forgot the flag cannot
    read the pause as success.
  * **It never pushes, never closes a pull request, and never touches `main`
    by any route but the host's own merge.** A closed pull request is a git
    operation with an ordering trap of its own (`AGENTS.md` item 3), and a
    tool that could also close would be one somebody runs in a hurry.
  * **It does not decide what a failing check means.** A check that is red is
    a reason to stop, by name; whether it is a defect or an environment
    difference is what `uv run --extra preflight qm preflight` and a person
    establish.

WHAT IT CANNOT SEE. Whether the pull request should merge -- only whether the
host says it can. A green pull request carrying eighteen commits of unrelated
work is READY here and wrong; `uv run qm branch` is the reader of that. And it
reads the contributor's own pull requests only: another contributor's queue is
not this contributor's to merge, and a bot's is not anybody's.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import roster  # noqa: E402

DEFAULT_ORG = "quaternionmedia"

# The host's own vocabulary for the three fields the predicate reads. Spelled
# out once so a typo becomes a NameError rather than a pull request that can
# never be READY.
OPEN = "OPEN"
MERGEABLE = "MERGEABLE"
CLEAN = "CLEAN"

# `gh pr checks --json bucket` normalises every check's state into one of five
# words. The two that stop a merge, and the one that says wait.
FAILING_BUCKETS = ("fail", "cancel")
PENDING_BUCKET = "pending"

# What `gh pr checks` says on stderr, exit non-zero, when the branch has no
# checks at all. That is a state and not a read failure, and the two must not
# collapse: one is "nothing to wait for" and the other is "could not look".
NO_CHECKS = "no checks reported"


class HostUnavailable(RuntimeError):
    """`gh` could not be run at all -- not installed, not on the path."""


def gh(*args: str) -> subprocess.CompletedProcess:
    """The one boundary with the host. Every read and the one write go here.

    Tests replace this and nothing else, so what a test sees is exactly the
    argument vector the host would have seen.
    """
    try:
        return subprocess.run(
            ("gh", *args),
            capture_output=True, text=True,
            # Pull request titles are data this tool did not write, and one
            # emoji in one of them makes a Windows default decoder raise
            # mid-read. Same defence as `project-seed/ci/check_one_pr.py`.
            encoding="utf-8", errors="replace",
        )
    except OSError as exc:
        raise HostUnavailable(str(exc)) from exc


def gh_json(*args: str):
    """One host call, parsed. None when the reply was not JSON.

    None and not an empty list, for the reason `ci/rulesets.py` gives: an
    empty list is a real answer and a failed call must never produce one.
    """
    done = gh(*args)
    try:
        return json.loads(done.stdout)
    except (json.JSONDecodeError, TypeError):
        return None


@dataclass
class PullRequest:
    """One pull request, as the host described it at one moment."""

    repo: str
    number: int
    title: str = ""
    head: str = ""
    author: str = ""
    draft: bool = False
    state: str = ""
    mergeable: str = ""
    merge_state: str = ""
    failing: list[str] = field(default_factory=list)
    pending: list[str] = field(default_factory=list)
    # False when `gh pr checks` could not be read. Distinct from "no checks",
    # which is an empty pair of lists with this True.
    checks_read: bool = True

    @classmethod
    def from_host(cls, repo: str, raw: dict) -> "PullRequest":
        return cls(
            repo=repo,
            number=int(raw.get("number", 0)),
            title=str(raw.get("title", "")),
            head=str(raw.get("headRefName", "")),
            author=str((raw.get("author") or {}).get("login", "")),
            draft=bool(raw.get("isDraft", False)),
            state=str(raw.get("state", "")),
            mergeable=str(raw.get("mergeable", "")),
            merge_state=str(raw.get("mergeStateStatus", "")),
        )


def blockers(pr: PullRequest) -> list[str]:
    """Why this pull request is not READY. Empty means it is.

    **THE ONE DEFINITION.** The listing prints it and the act refuses on it,
    and deliberately the same expression, so the two cannot disagree.

    Each condition is its own line rather than one boolean, because a refusal
    that says "not ready" teaches nothing and gets argued with; a refusal that
    names the draft flag, the conflicting file, or the check by name is one a
    person can act on.
    """
    why: list[str] = []
    if pr.state != OPEN:
        why.append(f"state is {pr.state or 'unknown'}, not {OPEN}")
    if pr.draft:
        why.append("it is a draft, and draft means incomplete")
    if pr.mergeable != MERGEABLE:
        why.append(f"mergeable is {pr.mergeable or 'unknown'}, not {MERGEABLE}")
    if pr.merge_state != CLEAN:
        why.append(f"merge state is {pr.merge_state or 'unknown'}, not {CLEAN}")
    if not pr.checks_read:
        why.append("the checks could not be read, so their state is unknown")
    if pr.failing:
        why.append("failing: " + ", ".join(pr.failing))
    if pr.pending:
        why.append("pending: " + ", ".join(pr.pending))
    return why


def read_checks(pr: PullRequest) -> None:
    """Fill in the failing and pending check names, or mark them unreadable."""
    done = gh("pr", "checks", str(pr.number), "--repo", pr.repo,
              "--json", "name,bucket")
    if NO_CHECKS in (done.stderr or ""):
        return
    try:
        rows = json.loads(done.stdout)
    except (json.JSONDecodeError, TypeError):
        rows = None
    if not isinstance(rows, list):
        pr.checks_read = False
        return
    for row in rows:
        name = str(row.get("name", "?"))
        bucket = str(row.get("bucket", ""))
        if bucket in FAILING_BUCKETS:
            pr.failing.append(name)
        elif bucket == PENDING_BUCKET:
            pr.pending.append(name)


VIEW_FIELDS = "number,title,headRefName,author,isDraft,state,mergeable,mergeStateStatus"


def open_pull_requests(repo: str) -> list[PullRequest] | None:
    """The contributor's open pull requests in one repository, with checks.

    `--author @me` is the host resolving the contributor, so no login is
    guessed here. None when the repository could not be read -- a private
    repository this token cannot see, a name that does not exist -- which the
    listing reports by name rather than as a repository with nothing open.
    """
    rows = gh_json("pr", "list", "--repo", repo, "--author", "@me",
                   "--state", "open", "--json", VIEW_FIELDS)
    if not isinstance(rows, list):
        return None
    found = [PullRequest.from_host(repo, row) for row in rows]
    for pr in found:
        read_checks(pr)
    return found


def view(repo: str, number: int) -> PullRequest | None:
    """One pull request, read live, at the moment of the call."""
    raw = gh_json("pr", "view", str(number), "--repo", repo, "--json", VIEW_FIELDS)
    if not isinstance(raw, dict):
        return None
    pr = PullRequest.from_host(repo, raw)
    read_checks(pr)
    return pr


def current_login() -> str:
    """Who the host thinks is asking. Empty when it cannot say."""
    done = gh("api", "user", "--jq", ".login")
    return done.stdout.strip() if done.returncode == 0 else ""


def roster_repositories() -> list[tuple[str, str | None]]:
    """(name, owner/name) for every roster entry; the slug is None where it
    cannot be formed.

    A private entry without its companion file carries only its reference, and
    a slug built from a reference names a repository that does not exist. It
    is listed as unreadable rather than dropped, because a roster silently a
    few short reads exactly like a roster of everything that exists.
    """
    out: list[tuple[str, str | None]] = []
    for entry in roster.load():
        name = roster.label(entry)
        if entry.get("ref") and name == entry["ref"]:
            out.append((name, None))
            continue
        out.append((name, entry.get("slug") or f"{DEFAULT_ORG}/{name}"))
    return out


def render(pr: PullRequest) -> list[str]:
    why = blockers(pr)
    verdict = "READY" if not why else "not ready"
    lines = [f"    #{pr.number}  {verdict:<9} {pr.head}  {pr.title}"]
    for reason in why:
        lines.append(f"           - {reason}")
    return lines


def listing(repos: list[tuple[str, str | None]]) -> str:
    """What a person reads before choosing which pull request to merge.

    Beside each repository: whether the contributor holds more than one open
    pull request there. That is the slot rule (`handbook/async-contract.md`
    section 1), and it is why the view is per repository rather than one flat
    queue -- the second open pull request in a repository is the one that
    should not have been opened yet, whatever its checks say.
    """
    out: list[str] = []
    unreadable: list[str] = []
    unnamed: list[str] = []
    ready: list[str] = []
    for name, slug in repos:
        if slug is None:
            unnamed.append(name)
            continue
        found = open_pull_requests(slug)
        if found is None:
            unreadable.append(slug)
            continue
        if not found:
            continue
        slots = ("one open pull request" if len(found) == 1
                 else f"{len(found)} open pull requests -- more than the one slot")
        out.append(f"  {slug}: {slots}")
        for pr in sorted(found, key=lambda p: p.number):
            out.extend(render(pr))
            if not blockers(pr):
                ready.append(f"{slug}#{pr.number}")
        out.append("")

    if not out:
        out.append("  No open pull request of yours in any repository read.")
        out.append("")
    if unreadable:
        out.append("  Could not be read, so UNKNOWN rather than empty:")
        out.append(f"      {', '.join(unreadable)}")
        out.append("")
    if unnamed:
        out.append("  Private, and not named in this clone, so not asked:")
        out.append(f"      {', '.join(unnamed)}")
        out.append("")
    if ready:
        out.append("  READY: " + ", ".join(ready))
        out.append("  Each is merged with: uv run qm merge --repo <owner/name> "
                   "--pr <n> --yes")
    out.append("  This mode reads. Nothing here merged, closed or pushed anything.")
    return "\n".join(out) + "\n"


def merge(pr: PullRequest) -> tuple[bool, str]:
    """The act: a merge commit, and the branch deleted. Nothing else.

    (ok, text). The text is the merge commit and time when ok, and the host's
    own words when not -- the host can refuse a merge the reading said was
    READY, because the reading and the act are two moments.
    """
    done = gh("pr", "merge", str(pr.number), "--repo", pr.repo,
              "--merge", "--delete-branch")
    if done.returncode != 0:
        return False, (done.stderr or done.stdout).strip()
    after = gh_json("pr", "view", str(pr.number), "--repo", pr.repo,
                    "--json", "mergedAt,mergeCommit")
    if not isinstance(after, dict):
        return True, "merged; the host did not say when or as what commit"
    commit = (after.get("mergeCommit") or {}).get("oid", "?")
    return True, f"merged as {commit} at {after.get('mergedAt', '?')}"


def act(repo: str, number: int, signed: bool, out) -> int:
    """Re-verify one pull request at this moment, and merge it only on READY
    with the signature."""
    pr = view(repo, number)
    if pr is None:
        out.write(f"  {repo}#{number}: could not be read from the host.\n")
        return 1
    out.write("\n".join(render(pr)) + "\n")
    why = blockers(pr)
    if why:
        out.write(f"  Refused: {repo}#{number} is not READY.\n")
        return 1
    me = current_login()
    if me and pr.author and pr.author != me:
        # The rule is that the author merges. A pull request somebody else
        # opened is theirs to merge, whatever its checks say.
        out.write(f"  Refused: {repo}#{number} was opened by {pr.author}, "
                  f"and you are {me}. The author merges their own.\n")
        return 1
    if not signed:
        out.write(f"  READY, and not merged: --yes is the author's signature "
                  f"and it was not given.\n")
        return 1
    ok, text = merge(pr)
    if not ok:
        out.write(f"  Refused by the host: {text}\n")
        return 1
    out.write(f"  {repo}#{number} {text}\n")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Your open pull requests, live; merge one when every gate is green.")
    parser.add_argument("--repo", help="owner/name; default is every roster repository")
    parser.add_argument("--pr", type=int, help="one pull request number; needs --repo")
    parser.add_argument("--yes", action="store_true",
                        help="the author's signature: merge if READY at this moment")
    parser.add_argument("--list", action="store_true",
                        help="read only (the default when --pr is absent)")
    # Declared so that they are refused with the reason. Undeclared, argparse
    # would answer with its usage line and exit 2, which reads as a typo.
    parser.add_argument("--squash", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--rebase", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args(argv)

    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    if args.squash or args.rebase:
        flag = "--squash" if args.squash else "--rebase"
        sys.stderr.write(
            f"merge: refused {flag}. The merge is a merge commit and nothing "
            "else: a rewritten branch breaks every submodule pin pointing at "
            "it (handbook/propagation-runbook.md).\n")
        return 1

    if args.pr is not None and not args.repo:
        parser.error("--pr needs --repo owner/name")
    if args.yes and args.pr is None:
        # A signature with nothing to sign is most likely a flag left on by a
        # script; swallowing it would teach that script it is harmless.
        parser.error("--yes signs one merge; name it with --repo and --pr")
    if args.repo and args.repo.count("/") != 1:
        parser.error(f"--repo must be owner/name, got {args.repo!r}")

    try:
        if args.pr is not None:
            return act(args.repo, args.pr, args.yes, sys.stdout)
        if args.repo:
            repos: list[tuple[str, str | None]] = [(args.repo, args.repo)]
        else:
            try:
                repos = roster_repositories()
            except Exception as exc:  # any unreadable roster is exit 2, whatever raised
                sys.stderr.write(f"merge: the roster could not be read: {exc}\n")
                return 2
        sys.stdout.write(listing(repos))
        return 0
    except HostUnavailable as exc:
        sys.stderr.write(f"merge: gh could not be run: {exc}\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
