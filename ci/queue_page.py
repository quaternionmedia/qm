#!/usr/bin/env python3
"""Is the queue page still true? Every pull request it names, asked again.

    uv run qm queue                                    # handbook/handoffs/qm-queue.md
    uv run qm queue --page handbook/handoffs/<page>.md

A queue page is stamped with the commit each repository's `main` was at when
the page was last re-derived. This reads every pull request and issue the page
names, asks the host what each is now, and reports the ones that merged or
closed after the stamp: for each, the page states something the host no longer
does. It also says how far each stamped `main` has moved since.

Exit 0: nothing the page names changed after its stamp. Exit 1: something did,
or a number resolves to no pull request or issue; each is listed. Exit 2: the
page, its stamp or the host could not be read, or there is no credential to
read the host with: the login is checked first, by name, because without one
every read fails the same way and the first to fail would be the stamp's.

How a number is read. `owner/name#N` is that repository's. `name #N`, with
`name` a roster repository (in backticks or not), is that repository's, and so
is every number joined to it by a comma, "and", "or" or a slash. Any other `#N`
is the corpus's own. A heading's `#` and a link's anchor are not numbers.

The stamp's moment is the committer date of the commit the page gives for
`qm`. That commit predates the page's writing, so a pull request merged
between the two is reported though the page may already say so: a false
alarm, never a miss.

What it cannot see: a pull request the page never names; whether a sentence
claims a pull request is open, so one merged before the stamp passes whatever
the page says of it; and a re-stamp made without re-reading the page, which
silences everything before it. The page's own "How this page is kept" section
is the procedure that covers those.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

# The host is reached through `merge_review`'s one boundary, `gh`, so a test
# that fakes it there fakes every read this makes.
import merge_review as host  # noqa: E402
import roster  # noqa: E402
from merge_review import DEFAULT_ORG, HostUnavailable  # noqa: E402

DEFAULT_PAGE = Path("handbook/handoffs/qm-queue.md")
CORPUS = "qm"

# "`qm` `main` at `8a6002b`", read from the page with its line breaks folded.
STAMP = re.compile(r"`([\w.-]+)` `main` at `([0-9a-f]{7,40})`")
# `owner/name#N`, or a `#N` that is not part of a word, a path, a heading or a
# link's anchor (`](#3-section)`, `page.md#3-section`).
NUMBER = re.compile(
    r"(?P<full>[\w.-]+/[\w.-]+)#(?P<fn>\d+)(?![\w-])"
    r"|(?<![\w/.#-])(?<!\]\()#(?P<n>\d+)(?![\w-])")
# The word right before a number, which names its repository if it is one.
NAMED = re.compile(r"`?([\w.-]+)`?\s+$")
# What joins a number to the one before it, so that it shares that one's
# repository: "`joe` #33 and #34".
JOINED = re.compile(r"\s*(?:,|,?\s*and|,?\s*or|/)\s*")


class Unreadable(RuntimeError):
    """The host answered, and the answer was not one this can read."""


@dataclass(frozen=True)
class Ref:
    """One number the page names, and the repository it belongs to."""

    repo: str     # owner/name, as the host is asked
    number: int
    shown: str    # the repository as the page writes it

    def __str__(self) -> str:
        return f"{self.shown}#{self.number}"


def repositories() -> dict[str, str]:
    """Every word that names a roster repository, to the name the host knows.

    A private entry answers to its `ref` as well, which is how a committed
    page writes it.
    """
    names: dict[str, str] = {}
    for entry in roster.load():
        names[entry["name"]] = entry["name"]
        if entry.get("ref"):
            names[entry["ref"]] = entry["name"]
    return names


def flatten(text: str) -> str:
    return re.sub(r"\s+", " ", text)


def stamps(text: str) -> dict[str, str]:
    """Repository -> the commit the page stamps its `main` at, first one wins."""
    found: dict[str, str] = {}
    for repo, sha in STAMP.findall(flatten(text)):
        found.setdefault(repo, sha)
    return found


def numbers(text: str, names: dict[str, str], org: str = DEFAULT_ORG) -> list[Ref]:
    """Every pull request or issue the page names, once each, in page order."""
    flat = flatten(text)
    refs: list[Ref] = []
    previous: Ref | None = None
    previous_end = 0
    for match in NUMBER.finditer(flat):
        if match["full"]:
            ref = Ref(match["full"], int(match["fn"]), match["full"])
        else:
            gap = flat[previous_end:match.start()]
            word = NAMED.search(gap[-64:])
            if word and word[1] in names:
                ref = Ref(f"{org}/{names[word[1]]}", int(match["n"]), word[1])
            elif previous and JOINED.fullmatch(gap):
                ref = Ref(previous.repo, int(match["n"]), previous.shown)
            else:
                ref = Ref(f"{org}/{CORPUS}", int(match["n"]), CORPUS)
        if ref not in refs:
            refs.append(ref)
        previous, previous_end = ref, match.end()
    return refs


def when(stamp: str) -> datetime:
    return datetime.fromisoformat(stamp.replace("Z", "+00:00"))


def signed_in() -> bool:
    """Whether the host CLI holds a credential: `gh auth status` exits zero.

    Asked before any other read. Without a credential the compare read fails
    too, and its empty answer would be reported as the host not knowing the
    page's stamp: a fault in the page, where the fault is the session's.
    """
    return host.gh("auth", "status").returncode == 0


def read_stamp(repo: str, sha: str, org: str = DEFAULT_ORG) -> dict | None:
    """`{"ahead_by": n, "date": committer date of the stamp}`, or None."""
    reply = host.gh_json(
        "api", f"repos/{org}/{repo}/compare/{sha}...main",
        "--jq", "{ahead_by, date: .base_commit.commit.committer.date}")
    return reply if isinstance(reply, dict) and reply.get("date") else None


def read_states(refs: list[Ref]) -> dict[Ref, dict | None]:
    """What the host says each number is now, in one query; None for nothing."""
    by_repo: dict[str, list[Ref]] = {}
    for ref in refs:
        by_repo.setdefault(ref.repo, []).append(ref)
    parts = []
    for i, (repo, group) in enumerate(by_repo.items()):
        owner, name = repo.split("/", 1)
        fields = " ".join(
            f"n{ref.number}: issueOrPullRequest(number: {ref.number}) {{ "
            "... on PullRequest { state mergedAt closedAt baseRefName title } "
            "... on Issue { state closedAt title } }"
            for ref in group)
        parts.append(f"r{i}: repository(owner: {json.dumps(owner)}, "
                     f"name: {json.dumps(name)}) {{ {fields} }}")
    # A number that is neither makes the host add an error beside the data and
    # exit non-zero; the data is still the answer for every other number.
    done = host.gh("api", "graphql", "-f", "query={ " + " ".join(parts) + " }")
    try:
        reply = json.loads(done.stdout)
    except (json.JSONDecodeError, TypeError):
        reply = None
    if not isinstance(reply, dict) or not isinstance(reply.get("data"), dict):
        raise Unreadable(done.stderr.strip() or "no data in the reply")
    states: dict[Ref, dict | None] = {}
    for i, (repo, group) in enumerate(by_repo.items()):
        node = reply["data"].get(f"r{i}") or {}
        for ref in group:
            states[ref] = node.get(f"n{ref.number}") or None
    return states


def changed_since(state: dict, since: datetime) -> str | None:
    """"merged" or "closed" if that happened after `since`; else None."""
    if state.get("state") == "OPEN":
        return None
    moment = state.get("mergedAt") or state.get("closedAt")
    if not moment or when(moment) <= since:
        return None
    return "merged" if state.get("mergedAt") else "closed"


def report(page: Path, out, org: str = DEFAULT_ORG) -> int:
    text = page.read_text(encoding="utf-8")
    stamped = stamps(text)
    if CORPUS not in stamped:
        out.write(f"queue: {page.as_posix()} carries no stamp for `{CORPUS}` "
                  f"(\"`{CORPUS}` `main` at `<commit>`\").\n")
        return 2
    if not signed_in():
        out.write("queue: no host credential, so nothing the page names can be "
                  "asked about. Run `gh auth login`, or set GH_TOKEN.\n")
        return 2
    lags = {repo: read_stamp(repo, sha, org) for repo, sha in stamped.items()}
    if lags[CORPUS] is None:
        out.write(f"queue: the host does not know {CORPUS} {stamped[CORPUS]}, "
                  "the page's stamp.\n")
        return 2
    since = when(lags[CORPUS]["date"])

    out.write(f"{page.as_posix()}: stamped at {CORPUS} {stamped[CORPUS]}, "
              f"{since:%Y-%m-%d %H:%M} UTC\n")
    for repo, sha in stamped.items():
        lag = lags[repo]
        moved = "unreadable" if lag is None else f"{lag['ahead_by']} commit(s) past it"
        out.write(f"  {repo} main at {sha}: {moved}\n")

    refs = numbers(text, repositories(), org)
    states = read_states(refs) if refs else {}
    moved = [(ref, changed_since(state, since), state)
             for ref, state in states.items()
             if state and changed_since(state, since)]
    missing = [ref for ref, state in states.items() if state is None]
    still_open = sum(1 for state in states.values()
                     if state and state.get("state") == "OPEN")
    out.write(f"{len(refs)} number(s) named: {still_open} open, {len(moved)} "
              f"merged or closed since the stamp, {len(missing)} unresolved.\n")

    if moved:
        out.write("\nMerged or closed since the stamp; the page says otherwise "
                  "until it is re-derived:\n")
        for ref, verb, state in moved:
            base = f" into {state['baseRefName']}" if state.get("baseRefName") else ""
            moment = when(state.get("mergedAt") or state["closedAt"])
            out.write(f"  {str(ref):<14} {verb} {moment:%Y-%m-%d}{base}  "
                      f"{state.get('title', '')}\n")
    if missing:
        out.write("\nNo pull request or issue by these numbers; a mistyped number, "
                  "or a repository the page did not name before it:\n")
        for ref in missing:
            out.write(f"  {ref}\n")
    out.write("\nCannot see: a pull request the page never names, or whether a "
              "sentence claims one is open.\n")
    return 1 if moved or missing else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Every pull request the queue page names, asked again; "
                    "what changed since its stamp.")
    parser.add_argument("--page", type=Path, default=DEFAULT_PAGE,
                        help=f"the page to read (default {DEFAULT_PAGE.as_posix()})")
    parser.add_argument("--org", default=DEFAULT_ORG,
                        help=f"owner of the repositories it names (default {DEFAULT_ORG})")
    args = parser.parse_args(argv)

    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    if not args.page.is_file():
        sys.stderr.write(f"queue: no page at {args.page}\n")
        return 2
    try:
        return report(args.page, sys.stdout, args.org)
    except (HostUnavailable, Unreadable) as exc:
        sys.stderr.write(f"queue: the host could not be read: {exc}\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
