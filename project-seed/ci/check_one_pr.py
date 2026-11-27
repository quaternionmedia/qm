#!/usr/bin/env python3
"""Every open pull request in a repository, and the stack each one sits in.

A seed file, run in place. A project's copied one-pr-check.yml may run it by
this path, so the path stays whatever the file does.

The rule (handbook/async-contract.md 1): one change per pull request.
Independent changes are parallel pull requests, each against its base, and
there is no limit on how many a contributor holds. A change that needs
another's work is *stacked*: its branch is cut from that branch and its pull
request's base IS that branch. It is marked ready when its work is finished,
wherever it stands in the stack, and it merges after the one beneath it,
retargeted onto that one's base: merged sooner, it would land in its parent's
branch rather than the target. `ci/merge_review.py` (`uv run qm merge`) holds
that order; this file lists.

What it lists

  - Every human's open pull request, draft or ready, and for each one whose
    base is the head branch of another open pull request in the same
    repository, that pull request's number.

What it cannot see:

  - A "stack" that skips the base chain: a branch cut from another pull
    request's branch but opened against the target, carrying its parent's
    commits. Seeing that needs a compare call per pair of open pull requests.
  - Closed pull requests, which are not read.

Automation's pull requests are counted and not listed: Dependabot's queue is
its own.

It fails nothing about a stack. Exit status is 0 once the list is read, and
non-zero only when it could not be: a repository nobody could read is never
reported as one with nothing open.

Usage:
    python check_one_pr.py --repo quaternionmedia/qm
    python check_one_pr.py --repo owner/name --contributor subcontrabass
    python check_one_pr.py --repo owner/name --json          # for a dashboard
    python check_one_pr.py --from-json prs.json --repo owner/name   # no network
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import defaultdict

# Accounts whose pull requests are counted and not listed. GitHub reports
# these with user.type == "Bot", but the REST list endpoint has been seen to
# return a plain "User" type for app-authored PRs, so the login suffix is
# checked too. Both, because a missed bot would be listed among people's work.
BOT_LOGIN_SUFFIXES = ("[bot]",)


def is_bot(author: dict) -> bool:
    login = str(author.get("login", ""))
    return author.get("type") == "Bot" or login.endswith(BOT_LOGIN_SUFFIXES)


def require_slug(repo: str) -> None:
    """Refuse a repository name that is not owner/name.

    In a workflow, `--repo` comes from `${{ github.repository }}` and
    `--contributor` from the pull request event. Outside a pull request event
    both expand to the empty string, and the request becomes `repos//pulls`,
    which answers 404 -- a message about a missing repository, for a
    configuration problem. Naming it here costs one check and saves the reader
    from looking for a repository that was never named.
    """
    if repo.count("/") != 1 or not all(part.strip() for part in repo.split("/")):
        sys.exit(
            f"check_one_pr: --repo must be owner/name, got {repo!r}.\n"
            "In a workflow this comes from ${{ github.repository }}; an empty "
            "value means the step ran outside the event context it needs."
        )


def fetch_open_prs(repo: str) -> list[dict]:
    """Every open pull request in `repo`, via gh.

    `--paginate` is not optional. The unpaginated endpoint returns thirty, and a
    repository with thirty-one open pull requests would never see the
    thirty-first -- a check that goes quiet exactly as the queue it measures
    gets long.
    """
    try:
        result = subprocess.run(
            [
                "gh",
                "api",
                "--paginate",
                f"repos/{repo}/pulls?state=open&per_page=100",
            ],
            capture_output=True,
            text=True,
            # Pull request titles are data this tool did not author, and one emoji
            # in one of them makes a Windows default decoder raise mid-read. The
            # symptom is not a bad title -- it is stdout arriving as None and the
            # whole repository going unchecked.
            encoding="utf-8",
            errors="replace",
        )
    except FileNotFoundError:
        sys.exit(
            "check_one_pr: `gh` is not installed or not on PATH. Install it from "
            "https://cli.github.com, then run `gh auth login`.\n"
            "This lists pull requests; it cannot report a repository it could "
            "not read as one with nothing open."
        )
    if result.returncode != 0:
        # gh exits 4 when it holds no credential, and says `gh auth login`
        # under a line about getting started. Wrapped in the message below
        # that reads as the host refusing the repository, so the missing
        # credential is named first and on its own.
        if result.returncode == 4 or "gh auth login" in result.stderr:
            sys.exit(
                "check_one_pr: no host credential. Run `gh auth login`, or set "
                "GH_TOKEN to a token that can read pull requests.\n"
                "This lists pull requests; it cannot report a repository it "
                "could not read as one with nothing open."
            )
        sys.exit(
            f"check_one_pr: gh api repos/{repo}/pulls failed:\n"
            f"{result.stderr.strip()}\n"
            "This lists pull requests; it cannot report a repository it could "
            "not read as one with nothing open."
        )
    # --paginate concatenates JSON arrays as separate documents on some gh
    # versions and splices them into one on others. Decoding whatever arrives
    # rather than assuming a single array keeps both working.
    decoder = json.JSONDecoder()
    text = result.stdout.strip()
    prs: list[dict] = []
    index = 0
    while index < len(text):
        value, end = decoder.raw_decode(text, index)
        prs.extend(value)
        index = end
        while index < len(text) and text[index] in " \t\r\n":
            index += 1
    return prs


def normalise(prs: list[dict]) -> list[dict]:
    """The fields this check reasons about, from the REST shape."""
    out = []
    for pr in prs:
        author = pr.get("user") or {}
        head = pr.get("head") or {}
        out.append(
            {
                "number": pr.get("number"),
                "title": pr.get("title", ""),
                "author": str(author.get("login", "")),
                "bot": is_bot(author),
                "base": str((pr.get("base") or {}).get("ref", "")),
                "head": str(head.get("ref", "")),
                # A fork's branch cannot be a base here, and one that shares a
                # name with a branch of this repository must not read as a
                # parent. None when the fork has been deleted.
                "head_repo": (head.get("repo") or {}).get("full_name"),
                "draft": bool(pr.get("draft")),
            }
        )
    return out


def parents(prs: list[dict], repo: str) -> dict[str, dict]:
    """Head branch -> the open pull request made from it, in this repository."""
    return {pr["head"]: pr for pr in prs if pr["head_repo"] == repo and pr["head"]}


def listed(prs: list[dict], contributor: str | None) -> list[dict]:
    """The human pull requests in scope: every one, or one login's."""
    return [
        pr for pr in prs
        if not pr["bot"] and (not contributor or pr["author"] == contributor)
    ]


def find_stacked(
    prs: list[dict], repo: str, contributor: str | None
) -> list[tuple[dict, dict]]:
    """(pull request, the one it is stacked on) for every stacked one in scope.

    The parent may be anybody's: the base chain is what orders the merges,
    whoever cut each branch.
    """
    by_head = parents(prs, repo)
    found = []
    for pr in listed(prs, contributor):
        parent = by_head.get(pr["base"])
        if parent is not None and parent["number"] != pr["number"]:
            found.append((pr, parent))
    return sorted(found, key=lambda pair: pair[0]["number"])


def report(repo: str, prs: list[dict], contributor: str | None) -> int:
    human = [pr for pr in prs if not pr["bot"]]
    bots = len(prs) - len(human)
    on_parent = {pr["number"]: parent for pr, parent in find_stacked(prs, repo, contributor)}

    print(f"repository   {repo}")
    print(f"open PRs     {len(prs)}  ({len(human)} human, {bots} automation)")
    if contributor:
        print(f"contributor  {contributor}")

    print()
    for pr in sorted(listed(prs, contributor), key=lambda p: (p["author"], p["number"])):
        parent = on_parent.get(pr["number"])
        on = f" (on #{parent['number']})" if parent else ""
        kind = "draft" if pr["draft"] else "ready"
        print(f"#{pr['number']} [{kind}] {pr['author']}: "
              f"{pr['head']} -> {pr['base']}{on}  {pr['title']}")

    if on_parent:
        print(
            f"\n{len(on_parent)} stacked on another open pull request. Each merges "
            "after the one beneath it, retargeted onto that one's base."
        )
    else:
        print("\nNone is stacked on another open pull request.")
    return 0


def force_utf8_output() -> None:
    """Titles this tool prints were authored elsewhere and may hold anything.

    The same reason the fetch decodes explicitly: a cp1252 console kills the
    report partway through, after a confident header has already been printed.
    """
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")


def main(argv: list[str] | None = None) -> int:
    force_utf8_output()
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo", required=True, help="owner/name")
    parser.add_argument(
        "--contributor",
        help="List this login's pull requests only. A parent is found whoever opened it.",
    )
    parser.add_argument(
        "--from-json",
        metavar="PATH",
        help="Read the pull request list from a file instead of calling gh.",
    )
    parser.add_argument(
        "--json", action="store_true", help="Emit the list as JSON, for a reader."
    )
    args = parser.parse_args(argv)

    if args.from_json:
        raw = json.loads(open(args.from_json, encoding="utf-8").read())
    else:
        require_slug(args.repo)
        raw = fetch_open_prs(args.repo)
    prs = normalise(raw)

    if args.json:
        json.dump(
            {
                "repository": args.repo,
                "contributor": args.contributor,
                # Every open pull request, whatever --contributor names: a
                # reader counting a repository's queue counts all of it.
                "open_prs": prs,
                # One entry per stacked pull request in scope, `base` being
                # its parent's branch.
                "stacked": [
                    {
                        "number": pr["number"],
                        "author": pr["author"],
                        "base": pr["base"],
                        "parent": parent["number"],
                    }
                    for pr, parent in find_stacked(prs, args.repo, args.contributor)
                ],
            },
            sys.stdout,
            indent=2,
        )
        print()
        return 0

    return report(args.repo, prs, args.contributor)


if __name__ == "__main__":
    raise SystemExit(main())
