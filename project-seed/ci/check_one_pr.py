#!/usr/bin/env python3
"""One open agent pull request per repository, per contributor.

SEED FILE, run in place.

The rule: at any moment, a repository holds at most one open pull request per
human contributor for agent-produced work. Not one per task, not one per
branch -- one per person, per repository.

It is a review-bandwidth rule, and bandwidth is the thing an asynchronous agent
cannot see. An agent finishes a task in minutes and opens a PR; the human it is
opened for reads at human speed. Six sessions running in parallel across six
repositories will produce six PRs an hour without any of them doing anything
wrong, and the reviewer's queue is where that arrives. Worse than the volume is
the ordering: two open PRs that must merge in a particular order are a puzzle
the agent solved and then discarded, handed to someone who has to solve it
again from the diffs.

Authorship is the contributor's, not the model's -- the human-only
contributorship record means an agent's commits carry the person's name, so the
PR author *is* the contributor. That is what makes this checkable at all.

WHAT COUNTS

  - Open pull requests only. A merged or closed PR occupies no bandwidth.
  - Human authors only. Automation accounts (Dependabot and friends) are
    excluded: they have their own queue and their own dismissal gesture, and a
    contributor cannot close them to make room.
  - Draft and ready alike. A draft PR is still a branch someone must eventually
    read, and this repository's own practice is that drafts are the normal
    state, so exempting them would exempt everything.

THE ONE EXEMPTION, AND WHY IT IS NARROW

`--per-base <glob>` gives each base branch matching the glob its own slot. It
exists for one shape: a repository where several long-lived branches are each
pinned by a different downstream consumer, so a change to one is not a change
to another and they cannot be combined into a single PR without inventing a
dependency between unrelated projects. The corpus repository's `project/*`
branches are that shape.

It is deliberately a glob you must pass, printed in the output whenever it
applies. An exemption nobody can see in the result is an exemption that has
stopped being one.

Exit status is 1 when any contributor in scope holds more than one slot.

Usage:
    python check_one_pr.py --repo quaternionmedia/qm
    python check_one_pr.py --repo owner/name --contributor subcontrabass
    python check_one_pr.py --repo quaternionmedia/qm --per-base 'project/*'
    python check_one_pr.py --repo owner/name --json          # for a dashboard
    python check_one_pr.py --from-json prs.json --repo owner/name   # no network
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import subprocess
import sys
from collections import defaultdict

# Accounts whose pull requests a contributor cannot close to make room. GitHub
# reports these with user.type == "Bot", but the REST list endpoint has been
# seen to return a plain "User" type for app-authored PRs, so the login suffix
# is checked too. Both, because a missed bot inflates a human's count and this
# check would then fail a PR for something nobody can act on.
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
    repository with thirty-one open pull requests would report the thirty-first
    contributor as holding no slot at all -- a check that goes quiet exactly as
    the queue it measures gets long.
    """
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
    if result.returncode != 0:
        sys.exit(
            f"check_one_pr: gh api repos/{repo}/pulls failed:\n"
            f"{result.stderr.strip()}\n"
            "This check reads pull requests; it cannot report a repository it "
            "could not read as compliant."
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
    """The five fields this check reasons about, from the REST shape."""
    out = []
    for pr in prs:
        author = pr.get("user") or {}
        out.append(
            {
                "number": pr.get("number"),
                "title": pr.get("title", ""),
                "author": str(author.get("login", "")),
                "bot": is_bot(author),
                "base": str((pr.get("base") or {}).get("ref", "")),
                # The branch this pull request is made from. Not used by the
                # slot rule, which counts authors rather than branches, but a
                # reader matching a pull request to a local branch has no other
                # way to do it -- and every such reader would otherwise guess
                # from the title.
                "head": str((pr.get("head") or {}).get("ref", "")),
                "draft": bool(pr.get("draft")),
            }
        )
    return out


def slot_key(base: str, per_base: list[str]) -> str:
    """Which slot a PR against `base` occupies.

    Everything shares one slot named "" unless its base matches an exempted
    glob, in which case the base names its own.
    """
    for pattern in per_base:
        if fnmatch.fnmatch(base, pattern):
            return base
    return ""


def find_violations(
    prs: list[dict], per_base: list[str], contributor: str | None
) -> dict[tuple[str, str], list[dict]]:
    """Slots holding more than one open PR, keyed by (author, slot)."""
    slots: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for pr in prs:
        if pr["bot"]:
            continue
        if contributor and pr["author"] != contributor:
            continue
        slots[(pr["author"], slot_key(pr["base"], per_base))].append(pr)
    return {key: held for key, held in slots.items() if len(held) > 1}


def report(
    repo: str, prs: list[dict], per_base: list[str], contributor: str | None
) -> int:
    human = [pr for pr in prs if not pr["bot"]]
    bots = len(prs) - len(human)

    print(f"repository   {repo}")
    print(f"open PRs     {len(prs)}  ({len(human)} human, {bots} automation)")
    if contributor:
        print(f"contributor  {contributor}")
    if per_base:
        print(f"per-base     {', '.join(per_base)}  (each matching base gets a slot)")

    slots: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for pr in human:
        slots[(pr["author"], slot_key(pr["base"], per_base))].append(pr)

    print()
    for (author, slot) in sorted(slots):
        held = slots[(author, slot)]
        where = f"  [{slot}]" if slot else ""
        mark = "OVER" if len(held) > 1 else "ok  "
        print(f"{mark} {author}{where}: {len(held)}")
        for pr in sorted(held, key=lambda p: p["number"]):
            kind = "draft" if pr["draft"] else "READY"
            print(f"       #{pr['number']} [{kind}] -> {pr['base']}  {pr['title']}")

    violations = find_violations(prs, per_base, contributor)
    if not violations:
        print("\nEvery contributor holds at most one slot.")
        return 0

    print()
    for (author, slot) in sorted(violations):
        held = violations[(author, slot)]
        where = f" against {slot}" if slot else ""
        numbers = ", ".join(f"#{pr['number']}" for pr in sorted(
            held, key=lambda p: p["number"]))
        print(
            f"{author} holds {len(held)} open pull requests{where}: {numbers}. "
            "One stays open; the rest are closed or folded into it."
        )
    print(
        "\nFolding is a git operation with an order to it: close the pull "
        "request FIRST, then push its commits onto the branch that survives. "
        "Pushing first merges it, with no review and no way to undo the record."
    )
    return 1


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
        help="Limit the exit status to this login. Others are still listed.",
    )
    parser.add_argument(
        "--per-base",
        action="append",
        default=[],
        metavar="GLOB",
        help="Give each base branch matching GLOB its own slot. Repeatable.",
    )
    parser.add_argument(
        "--from-json",
        metavar="PATH",
        help="Read the pull request list from a file instead of calling gh.",
    )
    parser.add_argument(
        "--json", action="store_true", help="Emit the finding as JSON, for a reader."
    )
    args = parser.parse_args(argv)

    if args.from_json:
        raw = json.loads(open(args.from_json, encoding="utf-8").read())
    else:
        require_slug(args.repo)
        raw = fetch_open_prs(args.repo)
    prs = normalise(raw)

    violations = find_violations(prs, args.per_base, args.contributor)

    if args.json:
        json.dump(
            {
                "repository": args.repo,
                "per_base": args.per_base,
                "contributor": args.contributor,
                "open_prs": prs,
                "violations": [
                    {
                        "author": author,
                        "base": slot,
                        "numbers": sorted(p["number"] for p in held),
                    }
                    for (author, slot), held in sorted(violations.items())
                ],
            },
            sys.stdout,
            indent=2,
        )
        print()
        return 1 if violations else 0

    return report(args.repo, prs, args.per_base, args.contributor)


if __name__ == "__main__":
    raise SystemExit(main())
