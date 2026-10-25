"""`qm assigned`: each pull request and issue the host lists lands in its group,
every page of a search is read, and the reading writes nothing.

The host is faked at `merge_review.gh`, the one boundary `assigned` reaches it
through, so no test touches the network.

The mutations, per `a-check-is-evidence-after-it-fails`. Each was applied to
`ci/assigned.py`, this file run, and the file restored and compared with its
original before the next; the file was green before the first and after the
last.

  `groups` sending somebody else's pull requests to your own

    FAILED test_each_item_lands_in_its_group
    FAILED test_a_deleted_author_is_somebody_else
    2 failed, 16 passed

  `read` following no page past the first

    FAILED test_every_page_of_a_search_is_read
    1 failed, 17 passed

  `read` without the empty-page guard

    FAILED test_a_page_with_nothing_on_it_ends_the_search
    1 failed, 17 passed

  `render` without the cap report

    FAILED test_a_search_the_host_cut_short_says_so
    1 failed, 17 passed

  `SCOPE` without `archived:false`

    FAILED test_every_search_asks_for_open_work_in_the_org_and_nothing_writes
    1 failed, 17 passed

  `read` accepting a reply that names nobody

    FAILED test_a_reply_that_does_not_say_who_is_asking_exits_two
    1 failed, 17 passed

  `read` skipping a search the reply does not carry

    FAILED test_a_reply_missing_a_search_exits_two
    1 failed, 17 passed

  `render` without the private mark

    FAILED test_a_private_repository_is_marked_and_a_public_one_is_not
    1 failed, 17 passed

  `line` marking the wrong pull requests as drafts

    FAILED test_a_draft_and_its_base_are_the_host_s_and_no_verdict_is_formed
    1 failed, 17 passed

  the query sent as a mutation

    FAILED test_every_search_asks_for_open_work_in_the_org_and_nothing_writes
    1 failed, 17 passed

`uv run qm mutate ci/assigned.py` kills every textual mutant but these, none
of which changes what the command does: the dataclass's frozen flag and field
defaults, which `Item.from_host` always overrides; the `isPrivate` and
`isDraft` fallbacks, for a field the query always asks for and a flag an issue
never prints; and an `and` or `or` inside a sentence the command prints.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import assigned  # noqa: E402
import merge_review  # noqa: E402

ME = "me"
SEARCH = re.compile(
    r'(\w+): search\(query: "([^"]*)", type: ISSUE, first: \d+'
    r'(?:, after: "([^"]*)")?\)')
# More host calls than any test here needs; a reading past it is a loop.
MOST_CALLS = 5


def pr(repo: str, number: int, author: str | None = ME, draft: bool = False,
       base: str = "main", private: bool = False, title: str = "a change") -> dict:
    return {"number": number, "title": title, "updatedAt": "2026-10-24T12:00:00Z",
            "author": None if author is None else {"login": author},
            "repository": {"nameWithOwner": repo, "isPrivate": private},
            "isDraft": draft, "baseRefName": base}


def issue(repo: str, number: int, author: str = "them",
          title: str = "an issue") -> dict:
    return {"number": number, "title": title, "updatedAt": "2023-09-05T12:00:00Z",
            "author": {"login": author},
            "repository": {"nameWithOwner": repo, "isPrivate": False}}


def paged(*pages: list[dict], total: int | None = None) -> list[dict]:
    """A search's pages, in order. The cursor after page i is "i+1"."""
    count = sum(len(page) for page in pages) if total is None else total
    return [{"issueCount": count,
             "pageInfo": {"hasNextPage": i + 1 < len(pages), "endCursor": str(i + 1)},
             "nodes": page}
            for i, page in enumerate(pages)]


def fake_host(searches: dict[str, list[dict]], login: str | None = ME):
    """`searches` maps each alias to its pages; an alias left out is empty."""
    calls = []

    def gh(*args):
        calls.append(args)
        if len(calls) > MOST_CALLS:
            raise AssertionError("the reading did not stop asking for pages")
        assert args[:3] == ("api", "graphql", "-f"), args
        query = args[3].removeprefix("query=")
        data: dict = {"viewer": None if login is None else {"login": login}}
        for alias, _terms, cursor in SEARCH.findall(query):
            pages = searches.get(alias) or paged([])
            data[alias] = pages[int(cursor) if cursor else 0]
        return subprocess.CompletedProcess(args, 0, json.dumps({"data": data}), "")

    return gh, calls


def run(monkeypatch, capsys, searches, argv=(), login=ME):
    gh, calls = fake_host(searches, login)
    monkeypatch.setattr(merge_review, "gh", gh)
    status = assigned.main(list(argv))
    captured = capsys.readouterr()
    return status, captured.out, captured.err, calls


def group(out: str, title: str) -> str:
    """The lines under one group's heading, up to the blank line after it."""
    start = out.index(f"\n{title}: ") + 1
    end = out.find("\n\n", start)
    return out[start:end if end != -1 else None]


def queries(calls) -> list[str]:
    return [call[3].removeprefix("query=") for call in calls]


EVERY_GROUP = {
    "reviews": paged([pr("o/a", 4, author="them")]),
    "pulls": paged([pr("o/b", 2, author="them"), pr("o/qm", 9)]),
    "issues": paged([issue("o/c", 1)]),
}


def test_each_item_lands_in_its_group(monkeypatch, capsys):
    status, out, _, _ = run(monkeypatch, capsys, EVERY_GROUP)
    assert status == 0, out
    reviews = group(out, "Review requested of you")
    assert "o/a" in reviews and "#4" in reviews and "by them" in reviews
    others = group(out, "Pull requests assigned to you, opened by somebody else")
    assert "o/b" in others and "#2" in others and "o/qm" not in others
    issues = group(out, "Issues assigned to you")
    assert "o/c" in issues and "#1" in issues
    own = group(out, "Your own pull requests, assigned to you")
    assert "o/qm" in own and "#9" in own
    assert "o/b" not in own and "by " not in own


def test_an_empty_group_says_none_rather_than_vanishing(monkeypatch, capsys):
    _, out, _, _ = run(monkeypatch, capsys, {})
    for title, _items in assigned.groups(assigned.Reading(ME, {
            alias: [] for alias in assigned.SEARCHES}, {})):
        assert f"{title}: 0\n  none" in out


def test_every_page_of_a_search_is_read(monkeypatch, capsys):
    searches = {"pulls": paged([pr("o/qm", 1)], [pr("o/qm", 2)])}
    _, out, _, calls = run(monkeypatch, capsys, searches)
    own = group(out, "Your own pull requests, assigned to you")
    assert "#1 " in own and "#2 " in own
    asked = queries(calls)
    assert len(asked) == 2
    # The second request asks again only for the search that had more.
    assert [(alias, cursor) for alias, _, cursor in SEARCH.findall(asked[1])] == [
        ("pulls", "1")]


def test_a_page_with_nothing_on_it_ends_the_search(monkeypatch, capsys):
    stuck = [{"issueCount": 3, "pageInfo": {"hasNextPage": True, "endCursor": "0"},
              "nodes": []}]
    status, _, _, calls = run(monkeypatch, capsys, {"issues": stuck})
    assert status == 0
    assert len(calls) == 1


def test_a_search_the_host_cut_short_says_so(monkeypatch, capsys):
    searches = {"issues": paged([issue("o/c", 1)], total=1500)}
    _, out, _, _ = run(monkeypatch, capsys, searches)
    assert "counted 1500" in out and "listed 1" in out


def test_a_search_listed_whole_says_nothing_of_a_cap(monkeypatch, capsys):
    _, out, _, _ = run(monkeypatch, capsys, EVERY_GROUP)
    assert "counted" not in out


def test_a_private_repository_is_marked_and_a_public_one_is_not(monkeypatch, capsys):
    searches = {"pulls": paged([pr("o/hidden", 3, private=True), pr("o/open", 4)])}
    _, out, _, _ = run(monkeypatch, capsys, searches)
    assert "  o/hidden  (private)\n" in out
    assert "  o/open\n" in out


def test_a_draft_and_its_base_are_the_host_s_and_no_verdict_is_formed(
        monkeypatch, capsys):
    searches = {"pulls": paged([pr("o/qm", 5, draft=True, base="adr/x"),
                                pr("o/qm", 6, base="main")])}
    _, out, _, _ = run(monkeypatch, capsys, searches)
    lines = {int(m[1]): m[0] for m in re.finditer(r"#(\d+) .*", out)}
    assert "draft" in lines[5] and "-> adr/x" in lines[5]
    assert "draft" not in lines[6] and "-> main" in lines[6]
    assert "Drafts among your own: 1." in out
    assert "READY" not in out


def test_a_deleted_author_is_somebody_else(monkeypatch, capsys):
    searches = {"pulls": paged([pr("o/b", 7, author=None)])}
    _, out, _, _ = run(monkeypatch, capsys, searches)
    others = group(out, "Pull requests assigned to you, opened by somebody else")
    assert "#7" in others and "by a deleted account" in others


def test_every_search_asks_for_open_work_in_the_org_and_nothing_writes(
        monkeypatch, capsys):
    _, _, _, calls = run(monkeypatch, capsys, EVERY_GROUP, argv=["--org", "other"])
    assert all(call[:3] == ("api", "graphql", "-f") for call in calls)
    asked = queries(calls)
    assert all("mutation" not in query for query in asked)
    searched = {alias: terms for alias, terms, _ in SEARCH.findall(asked[0])}
    assert set(searched) == set(assigned.SEARCHES)
    for terms in searched.values():
        assert {"is:open", "archived:false", "org:other"} <= set(terms.split())
    assert "review-requested:@me" in searched["reviews"]
    assert "assignee:@me" in searched["pulls"] and "is:pr" in searched["pulls"]
    assert "assignee:@me" in searched["issues"] and "is:issue" in searched["issues"]


def test_an_unreadable_reply_exits_two(monkeypatch, capsys):
    def gh(*args):
        return subprocess.CompletedProcess(args, 1, "not json", "HTTP 502")
    monkeypatch.setattr(merge_review, "gh", gh)
    assert assigned.main([]) == 2
    err = capsys.readouterr().err
    assert "the host could not be read" in err and "502" in err


def test_a_reply_that_does_not_say_who_is_asking_exits_two(monkeypatch, capsys):
    status, _, err, _ = run(monkeypatch, capsys, EVERY_GROUP, login=None)
    assert status == 2
    assert "did not say who is asking" in err


def test_a_reply_missing_a_search_exits_two(monkeypatch, capsys):
    def gh(*args):
        data = {"viewer": {"login": ME}, "reviews": paged([])[0]}
        return subprocess.CompletedProcess(args, 0, json.dumps({"data": data}), "")
    monkeypatch.setattr(merge_review, "gh", gh)
    assert assigned.main([]) == 2
    assert "no pulls search" in capsys.readouterr().err


def test_gh_missing_exits_two(monkeypatch, capsys):
    def gh(*args):
        raise merge_review.HostUnavailable("gh not found")
    monkeypatch.setattr(merge_review, "gh", gh)
    assert assigned.main([]) == 2
    assert "gh not found" in capsys.readouterr().err


def test_the_route():
    import cli
    assert cli.ROUTES["assigned"] == ("assigned", False, [])


@pytest.mark.parametrize("flag", ["--merge", "--comment", "--yes"])
def test_there_is_no_flag_that_acts(flag, capsys):
    with pytest.raises(SystemExit) as exit_:
        assigned.main([flag])
    assert exit_.value.code == 2
