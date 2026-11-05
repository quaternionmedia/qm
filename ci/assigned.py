#!/usr/bin/env python3
"""What the host says is waiting on you: review requests, assignments, issues.

    uv run qm assigned                  # every repository in the organisation
    uv run qm assigned --org owner      # another owner's repositories

`handbook/async-contract.md` §2 routes work to a person by assignment: a pull
request names the person who asked for it as its assignee, and nobody is asked
to review. This reads that channel back. It asks the host, as whoever `gh` is
signed in as, for every open pull request and issue in the organisation that
names them as assignee and every open pull request that requests their review,
and lists them in four groups, each grouped by repository:

  review requested    a pull request requests your review, directly or through
                      a team you are on. A `CODEOWNERS` file makes that request
                      the moment a pull request opens.
  assigned to you     somebody else's pull request names you as assignee.
  issues              an issue names you as assignee.
  your own            a pull request you opened names you as assignee, which
                      every pull request a session opens does; each is waiting
                      on its merge.

A pull request that both requests your review and is assigned to you is in
both groups, because it asks two things. A private repository is printed as
the host names it and marked private: the listing is for the person reading
it, and a name copied out of it into tracked text is what
`uv run qm private-names` looks for.

What it refuses to do:

  * **It never writes.** No comment, review, merge, close or reassignment, and
    no flag to ask for one. Every call it makes is one read-only query.
  * **It forms no verdict on readiness.** Whether one of your own pull requests
    can merge is `uv run qm merge`'s reading, which holds the one definition of
    READY. This prints the host's draft flag and base and reads no checks.
  * **It is a reading, not a gate.** A completed reading exits 0 whatever it
    found. Exit 2 means the host could not be read.

What it cannot see: an ask made in a comment, a mention or a chat rather than
by assignment or review request; a review you have already given, which the
host stops listing as requested; a repository outside `--org`; an archived
repository, which the query leaves out because nothing in one can be acted on;
and anything past the host's own cap on search results, which it reports as a
count the host made and did not list.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

# The host is reached through `merge_review`'s one boundary, `gh`, so a test
# that fakes it there fakes every read this makes.
import merge_review as host  # noqa: E402
from merge_review import DEFAULT_ORG, HostUnavailable  # noqa: E402

# Each search, by the alias the query gives it. `@me` is the host resolving
# the person, so no login is guessed here.
SEARCHES = {
    "reviews": "is:pr review-requested:@me",
    "pulls": "is:pr assignee:@me",
    "issues": "is:issue assignee:@me",
}
SCOPE = "is:open archived:false org:{org}"

# The most results the host returns on one page of a search.
PAGE = 100

FIELDS = "number title updatedAt author { login } repository { nameWithOwner isPrivate }"
NODE = (f"... on PullRequest {{ {FIELDS} isDraft baseRefName }} "
        f"... on Issue {{ {FIELDS} }}")


class Unreadable(RuntimeError):
    """The host answered, and the answer was not one this can read."""


@dataclass(frozen=True)
class Item:
    """One pull request or issue, as the host listed it at one moment."""

    repo: str
    number: int
    title: str = ""
    updated: str = ""
    author: str = ""
    private: bool = False
    pull: bool = False
    draft: bool = False
    base: str = ""

    @classmethod
    def from_host(cls, node: dict) -> "Item":
        repository = node.get("repository") or {}
        return cls(
            repo=str(repository.get("nameWithOwner", "?")),
            number=int(node.get("number", 0)),
            title=str(node.get("title", "")),
            updated=str(node.get("updatedAt", ""))[:10],
            # A deleted account is reported as a null author.
            author=str((node.get("author") or {}).get("login", "")),
            private=bool(repository.get("isPrivate", False)),
            pull="isDraft" in node,
            draft=bool(node.get("isDraft", False)),
            base=str(node.get("baseRefName", "")),
        )


@dataclass
class Reading:
    """Everything the host listed, and how many it counted for each search."""

    login: str
    found: dict[str, list[Item]]
    totals: dict[str, int]


def query(org: str, cursors: dict[str, str | None]) -> str:
    """One request for the next page of every search that has one."""
    parts = ["viewer { login }"]
    for alias, cursor in cursors.items():
        terms = f"{SEARCHES[alias]} {SCOPE.format(org=org)}"
        after = f", after: {json.dumps(cursor)}" if cursor else ""
        parts.append(
            f"{alias}: search(query: {json.dumps(terms)}, type: ISSUE, "
            f"first: {PAGE}{after}) {{ issueCount "
            f"pageInfo {{ hasNextPage endCursor }} nodes {{ {NODE} }} }}")
    return "{ " + " ".join(parts) + " }"


def read(org: str) -> Reading:
    """Every search, followed page by page until the host has no more."""
    pending: dict[str, str | None] = {alias: None for alias in SEARCHES}
    found: dict[str, list[Item]] = {alias: [] for alias in SEARCHES}
    totals: dict[str, int] = {}
    login = ""
    while pending:
        done = host.gh("api", "graphql", "-f", "query=" + query(org, pending))
        try:
            reply = json.loads(done.stdout)
        except (json.JSONDecodeError, TypeError):
            reply = None
        data = reply.get("data") if isinstance(reply, dict) else None
        if not isinstance(data, dict):
            raise Unreadable((done.stderr or "").strip() or "no data in the reply")
        login = login or str((data.get("viewer") or {}).get("login", ""))
        if not login:
            raise Unreadable("the host did not say who is asking")
        following: dict[str, str | None] = {}
        for alias in pending:
            result = data.get(alias)
            if not isinstance(result, dict):
                raise Unreadable(f"the reply carries no {alias} search")
            totals[alias] = int(result.get("issueCount") or 0)
            nodes = [node for node in result.get("nodes") or [] if node]
            found[alias].extend(Item.from_host(node) for node in nodes)
            page = result.get("pageInfo") or {}
            # A page with nothing on it ends the search whatever it says next,
            # so a reply that always claims another page cannot loop this.
            if nodes and page.get("hasNextPage") and page.get("endCursor"):
                following[alias] = str(page["endCursor"])
        pending = following
    return Reading(login, found, totals)


def groups(reading: Reading) -> list[tuple[str, list[Item]]]:
    me = reading.login
    pulls = reading.found["pulls"]
    return [
        ("Review requested of you", reading.found["reviews"]),
        ("Pull requests assigned to you, opened by somebody else",
         [item for item in pulls if item.author != me]),
        ("Issues assigned to you", reading.found["issues"]),
        ("Your own pull requests, assigned to you",
         [item for item in pulls if item.author == me]),
    ]


def line(item: Item, me: str) -> str:
    cells = [f"#{item.number:<5}", item.updated]
    if item.pull:
        cells.append("draft" if item.draft else "     ")
        cells.append(f"-> {item.base}")
    if item.author != me:
        cells.append(f"by {item.author or 'a deleted account'}")
    cells.append(item.title)
    return "  ".join(cells)


def render(reading: Reading, org: str, out) -> None:
    out.write(f"Open in {org}, for {reading.login}: assigned, or asking for a "
              "review.\n")
    for title, items in groups(reading):
        out.write(f"\n{title}: {len(items)}\n")
        if not items:
            out.write("  none\n")
            continue
        repo = None
        for item in sorted(items, key=lambda i: (i.repo, i.number)):
            if item.repo != repo:
                repo = item.repo
                out.write(f"  {repo}{'  (private)' if item.private else ''}\n")
            out.write(f"    {line(item, reading.login)}\n")

    out.write("\n")
    for alias, total in reading.totals.items():
        listed = len(reading.found[alias])
        if total > listed:
            out.write(f"The host counted {total} for `{SEARCHES[alias]}` and "
                      f"listed {listed}; the rest are past its cap on search "
                      "results.\n")
    own = [item for item in reading.found["pulls"] if item.author == reading.login]
    if own:
        drafts = sum(1 for item in own if item.draft)
        out.write(f"Drafts among your own: {drafts}. Which of the rest can merge "
                  "is `uv run qm merge`'s reading; this one reads no checks.\n")
    out.write("This reads. Nothing here commented, reviewed, merged or "
              "reassigned anything.\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="What the host says is waiting on you: review requests, "
                    "assigned pull requests and assigned issues.")
    parser.add_argument("--org", default=DEFAULT_ORG,
                        help=f"owner of the repositories to read (default {DEFAULT_ORG})")
    args = parser.parse_args(argv)

    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    try:
        reading = read(args.org)
    except (HostUnavailable, Unreadable) as exc:
        sys.stderr.write(f"assigned: the host could not be read: {exc}\n")
        return 2
    render(reading, args.org, sys.stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
