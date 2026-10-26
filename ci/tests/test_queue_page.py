"""`qm queue`: every number the queue page names is read to the right
repository, and one that merged or closed after the stamp is reported.

The host is faked at `merge_review.gh`, the one boundary `queue_page` reaches
it through, so no test touches the network.

The mutations, per `a-check-is-evidence-after-it-fails`. Each was applied to
`ci/queue_page.py`, this file run, and the file restored before the next; the
file was green before the first and after the last.

  `numbers` without the `JOINED` branch

    FAILED test_each_number_is_read_to_its_repository
    FAILED test_nothing_changed_since_the_stamp_exits_zero
    FAILED test_a_merge_after_the_stamp_is_reported_and_exits_one
    FAILED test_a_merge_before_the_stamp_is_history_and_passes
    4 failed, 11 passed

  `NUMBER` without the `](` lookbehind

    FAILED test_each_number_is_read_to_its_repository
    FAILED test_an_anchor_or_a_heading_is_not_a_number
    FAILED test_nothing_changed_since_the_stamp_exits_zero
    FAILED test_a_merge_before_the_stamp_is_history_and_passes
    4 failed, 11 passed

  `changed_since` returning None for every closed state

    FAILED test_a_merge_after_the_stamp_is_reported_and_exits_one
    FAILED test_a_close_after_the_stamp_is_reported
    2 failed, 13 passed

  `changed_since` without `<= since`

    FAILED test_a_merge_before_the_stamp_is_history_and_passes
    1 failed, 14 passed

  the exit status without `or missing`

    FAILED test_a_number_the_host_does_not_know_exits_one
    1 failed, 14 passed
"""

from __future__ import annotations

import io
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import merge_review  # noqa: E402
import queue_page  # noqa: E402

CORPUS = Path(__file__).resolve().parent.parent.parent
NAMES = {"qm": "qm", "joe": "joe", "datum": "datum", "private-34": "secret"}
STAMP_DATE = "2026-10-24T17:00:00Z"

PAGE = """# Handoff

**Stamped 2026-10-24.** `qm` `main` at `abc1234`; `joe` `main` at
`def5678`.

## 1. Open

- #10 and #11, into project branches; `joe` #33 and #34 wait on a test.
- Held: datum #2, private-34 #5 and quaternionmedia/.github#9.
- [section](#3), [page](other.md#4-rules), and C# 7 are not numbers.
"""


def names_of(refs):
    return [str(ref) for ref in refs]


def test_each_number_is_read_to_its_repository():
    """Mutation: drop the `JOINED` branch and `joe#34` reads as `qm#34`."""
    refs = queue_page.numbers(PAGE, NAMES)
    assert names_of(refs) == [
        "qm#10", "qm#11", "joe#33", "joe#34", "datum#2", "private-34#5",
        "quaternionmedia/.github#9"]
    assert {ref.repo for ref in refs} == {
        "quaternionmedia/qm", "quaternionmedia/joe", "quaternionmedia/datum",
        "quaternionmedia/secret", "quaternionmedia/.github"}


def test_an_anchor_or_a_heading_is_not_a_number():
    """Mutation: drop the `](` lookbehind and `#3` from the anchor is read."""
    assert queue_page.numbers("## 1. Open\n[s](#3) [p](a.md#4-y) C# 7",
                              NAMES) == []


def test_a_word_that_is_no_repository_leaves_the_number_the_corpus_s():
    assert names_of(queue_page.numbers("the propagation #174", NAMES)) == ["qm#174"]


def test_a_number_wrapped_onto_the_next_line_keeps_its_repository():
    assert names_of(queue_page.numbers("held: datum\n  #2", NAMES)) == ["datum#2"]


def test_the_stamp_is_read_across_a_line_break():
    assert queue_page.stamps(PAGE) == {"qm": "abc1234", "joe": "def5678"}


def test_the_committed_page_carries_a_stamp_this_reads():
    """The page and this reader agree on the stamp's form, or this is red
    before anybody runs the command and is told the page has no stamp."""
    text = (CORPUS / queue_page.DEFAULT_PAGE).read_text(encoding="utf-8")
    assert queue_page.CORPUS in queue_page.stamps(text)
    assert queue_page.numbers(text, queue_page.repositories())


# --- against a fake host ----------------------------------------------------


def fake_host(states: dict[str, dict | None], stamp_date: str | None = STAMP_DATE):
    """`states` maps "repo#N" to the host's node for it, None for nothing."""
    calls = []

    def gh(*args):
        calls.append(args)
        if args[:2] == ("api", "graphql"):
            query = args[3]
            data = {}
            for alias, repo in _repositories(query):
                node = {}
                for number in _numbers_in(query, alias):
                    node[f"n{number}"] = states.get(f"{repo}#{number}")
                data[alias] = node
            return subprocess.CompletedProcess(args, 0, json.dumps({"data": data}), "")
        if "/compare/" in args[1]:
            reply = {"ahead_by": 3, "date": stamp_date} if stamp_date else {}
            return subprocess.CompletedProcess(args, 0, json.dumps(reply), "")
        raise AssertionError(f"unexpected host call {args}")

    return gh, calls


def _repositories(query: str):
    return re.findall(r'(r\d+): repository\(owner: "[^"]+", name: "([^"]+)"\)', query)


def _numbers_in(query: str, alias: str):
    block = re.split(r" r\d+: repository", query.split(f"{alias}: repository", 1)[1])[0]
    return [int(n) for n in re.findall(r"n(\d+): issueOrPullRequest", block)]


def merged(at: str, base: str = "main") -> dict:
    return {"state": "MERGED", "mergedAt": at, "closedAt": at,
            "baseRefName": base, "title": "a change"}


OPEN = {"state": "OPEN", "mergedAt": None, "closedAt": None,
        "baseRefName": "main", "title": "still open"}


def run(tmp_path, monkeypatch, states, text=PAGE, stamp_date=STAMP_DATE):
    page = tmp_path / "queue.md"
    page.write_text(text, encoding="utf-8")
    gh, calls = fake_host(states, stamp_date)
    monkeypatch.setattr(merge_review, "gh", gh)
    monkeypatch.setattr(queue_page, "repositories", lambda: NAMES)
    out = io.StringIO()
    return queue_page.report(page, out), out.getvalue(), calls


def every_number(state: dict) -> dict:
    return {key: state for key in (
        "qm#10", "qm#11", "joe#33", "joe#34", "datum#2", "secret#5", ".github#9")}


def test_nothing_changed_since_the_stamp_exits_zero(tmp_path, monkeypatch):
    status, out, calls = run(tmp_path, monkeypatch, every_number(OPEN))
    assert status == 0, out
    assert "7 open, 0 merged or closed since the stamp, 0 unresolved" in out
    # One query for every number, and one read per stamped repository.
    assert sum(1 for c in calls if c[:2] == ("api", "graphql")) == 1


def test_a_merge_after_the_stamp_is_reported_and_exits_one(tmp_path, monkeypatch):
    """Mutation: `changed_since` returning None after the OPEN test, and this
    exits 0."""
    states = every_number(OPEN) | {"joe#34": merged("2026-10-25T09:00:00Z")}
    status, out, _ = run(tmp_path, monkeypatch, states)
    assert status == 1
    assert "joe#34" in out and "merged 2026-10-25 into main" in out


def test_a_merge_before_the_stamp_is_history_and_passes(tmp_path, monkeypatch):
    """Mutation: drop `<= since` from `changed_since`, and this exits 1."""
    states = every_number(OPEN) | {"qm#10": merged("2026-10-23T09:00:00Z")}
    status, out, _ = run(tmp_path, monkeypatch, states)
    assert status == 0, out


def test_a_close_after_the_stamp_is_reported(tmp_path, monkeypatch):
    closed = {"state": "CLOSED", "mergedAt": None, "closedAt": "2026-10-25T09:00:00Z",
              "baseRefName": "project/x", "title": "closed"}
    status, out, _ = run(tmp_path, monkeypatch, every_number(OPEN) | {"datum#2": closed})
    assert status == 1
    assert "datum#2" in out and "closed 2026-10-25 into project/x" in out


def test_a_number_the_host_does_not_know_exits_one(tmp_path, monkeypatch):
    """Mutation: drop `or missing` from the exit status, and this exits 0."""
    status, out, _ = run(tmp_path, monkeypatch, every_number(OPEN) | {"qm#11": None})
    assert status == 1
    assert "qm#11" in out.split("No pull request or issue")[1]


def test_a_page_without_a_corpus_stamp_exits_two(tmp_path, monkeypatch):
    status, out, calls = run(tmp_path, monkeypatch, {}, text="#10 is open.\n")
    assert status == 2 and "carries no stamp" in out
    assert calls == []


def test_a_stamp_the_host_does_not_know_exits_two(tmp_path, monkeypatch):
    status, out, _ = run(tmp_path, monkeypatch, every_number(OPEN), stamp_date=None)
    assert status == 2 and "does not know" in out


def test_a_reply_without_data_is_unreadable_not_empty(monkeypatch):
    def gh(*args):
        return subprocess.CompletedProcess(args, 1, "", "HTTP 502")
    monkeypatch.setattr(merge_review, "gh", gh)
    with pytest.raises(queue_page.Unreadable, match="502"):
        queue_page.read_states(queue_page.numbers("#1", NAMES))


def test_the_route_is_registered_as_qm_queue():
    import cli
    assert cli.ROUTES["queue"] == ("queue_page", False, [])
