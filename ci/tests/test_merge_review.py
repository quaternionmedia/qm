"""`qm merge`: the reading half mutates nothing, and the act refuses on anything
short of READY, without the signature, and by any route but a merge commit.

The host is faked at `merge_review.gh`, the module's one boundary, so every
test sees exactly the argument vector the host would have seen and none of
them reaches the network. That is also what lets the listing be checked for
the property that matters most: it issued read verbs only.

THE MUTATIONS, per `a-check-is-evidence-after-it-fails`, quoted as they printed.
Each was applied to `ci/merge_review.py`, the suite run, and the file restored
and diffed against its original before the next; the suite was green before the
first and after the last.

  `blockers` with the draft condition removed

    FAILED test_each_failing_condition_alone_blocks_ready[draft-setup0]
    1 failed, 27 passed

  `blockers` with the pending-checks condition removed

    FAILED test_each_failing_condition_alone_blocks_ready[pending-setup7]
    FAILED test_the_act_re_verifies_live_and_refuses_on_a_blocker
    2 failed, 26 passed

  `blockers` with the unreadable-checks condition removed

    FAILED test_each_failing_condition_alone_blocks_ready[unreadable-checks-setup8]
    1 failed, 27 passed

  `act` with the `if not signed` block removed

    E       assert 0 == 1
    FAILED test_without_yes_it_verifies_and_stops

  the merge issued as `--squash` in place of `--merge`

    E       At index 0 diff: ('pr', 'merge', '7', '--repo', 'o/r', '--squash',
            '--delete-branch') != ('pr', 'merge', '7', '--repo', 'o/r',
            '--merge', '--delete-branch')
    FAILED test_the_merge_is_a_merge_commit_and_deletes_the_branch

  `listing` calling `merge` on each row it renders

    E       Extra items in the left set:
    E       ('pr', 'merge')
    FAILED test_the_listing_issues_only_read_verbs

**THE FIRST RED WAS THE SUITE'S OWN.** Before any mutation, the
`unreadable-checks` row failed against the unmodified module: it passed
`checks=None` to the fake host, and `None` is that fake's "use the green
default". The row was asking about green checks and reporting a defect in
`blockers` that was not there -- the setup describing itself. The rows now
carry the fake's keyword arguments whole, and the unreadable-checks mutation
above is the evidence that the repaired row reads the condition it names.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

CI_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(CI_DIR))

import merge_review  # noqa: E402

REPO = "o/r"

READY_VIEW = {
    "number": 7, "title": "One slice", "headRefName": "evolve/slice",
    "author": {"login": "someone"}, "isDraft": False, "state": "OPEN",
    "mergeable": "MERGEABLE", "mergeStateStatus": "CLEAN",
}
GREEN_CHECKS = [{"name": "tests", "bucket": "pass"},
                {"name": "lint", "bucket": "pass"}]

READ_VERBS = {("pr", "list"), ("pr", "view"), ("pr", "checks"), ("api", "user")}


def done(stdout="", stderr="", code=0) -> subprocess.CompletedProcess:
    return subprocess.CompletedProcess(("gh",), code, stdout, stderr)


class FakeHost:
    """Answers `gh` from a script of replies and remembers every call."""

    def __init__(self, *, view=None, checks=None, listing=None, login="someone",
                 merge=None, after=None, checks_reply=None, listing_reply=None):
        self.view = READY_VIEW if view is None else view
        self.checks = GREEN_CHECKS if checks is None else checks
        self.listing = [self.view] if listing is None else listing
        # Whole replies, for the cases where what the host says is not JSON.
        self.checks_reply = checks_reply
        self.listing_reply = listing_reply
        self.login = login
        self.merge = done() if merge is None else merge
        self.after = ({"mergedAt": "2026-09-19T10:00:00Z",
                       "mergeCommit": {"oid": "abc123"}}
                      if after is None else after)
        self.calls: list[tuple[str, ...]] = []

    def __call__(self, *args: str) -> subprocess.CompletedProcess:
        self.calls.append(args)
        verb = args[:2]
        if verb == ("pr", "list"):
            return self.listing_reply or done(json.dumps(self.listing))
        if verb == ("pr", "view"):
            if "mergedAt,mergeCommit" in args:
                return done(json.dumps(self.after))
            return done(json.dumps(self.view))
        if verb == ("pr", "checks"):
            if self.checks_reply is not None:
                return self.checks_reply
            if self.checks is None:
                return done("", "boom", 1)
            return done(json.dumps(self.checks))
        if verb == ("api", "user"):
            return done(self.login + "\n")
        if verb == ("pr", "merge"):
            return self.merge
        raise AssertionError(f"unscripted gh call: {args}")

    @property
    def merges(self) -> list[tuple[str, ...]]:
        return [c for c in self.calls if c[:2] == ("pr", "merge")]


@pytest.fixture
def host(monkeypatch):
    def install(**kw) -> FakeHost:
        fake = FakeHost(**kw)
        monkeypatch.setattr(merge_review, "gh", fake)
        return fake
    return install


# --- READY is one predicate, and every condition alone defeats it ------------


def test_a_green_open_mergeable_clean_pull_request_is_ready(host):
    host()
    pr = merge_review.view(REPO, 7)
    assert merge_review.blockers(pr) == []


RED = [{"name": "reuse", "bucket": "fail"}]
CANCELLED = [{"name": "build", "bucket": "cancel"}]
WAITING = [{"name": "docs", "bucket": "pending"}]


@pytest.mark.parametrize("label,setup", [
    ("draft", dict(view={**READY_VIEW, "isDraft": True})),
    ("not-open", dict(view={**READY_VIEW, "state": "MERGED"})),
    ("not-mergeable", dict(view={**READY_VIEW, "mergeable": "CONFLICTING"})),
    ("dirty", dict(view={**READY_VIEW, "mergeStateStatus": "DIRTY"})),
    ("blocked", dict(view={**READY_VIEW, "mergeStateStatus": "BLOCKED"})),
    ("failing-check", dict(checks=GREEN_CHECKS + RED)),
    ("cancelled-check", dict(checks=GREEN_CHECKS + CANCELLED)),
    ("pending", dict(checks=GREEN_CHECKS + WAITING)),
    ("unreadable-checks", dict(checks_reply=done("", "boom", 1))),
])
def test_each_failing_condition_alone_blocks_ready(host, label, setup):
    """One condition at a time, each against an otherwise READY pull request,
    so a predicate that dropped exactly one of them is caught by exactly one
    row here rather than hidden behind the others.

    **THE LAST ROW WAS GREEN FOR THE WRONG REASON THE FIRST TIME.** It passed
    `checks=None`, and `None` is the fake host's "use the default" -- so the
    row asked about green checks and reported a module defect that was not
    there. The setup described itself. Rows now carry the host's keyword
    arguments whole, so what a row says is what the fake does.

    Mutation: delete the `if pr.draft` branch of `blockers` and the `draft`
    row goes red alone; delete the pending branch and `pending` goes red.
    """
    host(**setup)
    pr = merge_review.view(REPO, 7)
    why = merge_review.blockers(pr)
    assert why, f"a pull request with {label} was READY"


def test_a_blocker_names_the_check(host):
    """A refusal that says only "not ready" gets argued with."""
    host(checks=GREEN_CHECKS + [{"name": "reuse", "bucket": "fail"}])
    why = merge_review.blockers(merge_review.view(REPO, 7))
    assert any("reuse" in reason for reason in why)


def test_no_checks_at_all_is_a_state_and_not_a_read_failure(host):
    """`gh pr checks` exits non-zero and says so when a branch has no checks.
    That is "nothing to wait for", and it must not read as "could not look"."""
    host(checks_reply=done("", "no checks reported on the 'x' branch", 1))
    pr = merge_review.view(REPO, 7)
    assert pr.checks_read is True
    assert merge_review.blockers(pr) == []


# --- the listing reads and nothing else ---------------------------------------


def test_the_listing_issues_only_read_verbs(host):
    """**THE PROPERTY THE DEFAULT MODE EXISTS FOR.** Whatever the state of the
    queue -- here one READY pull request, which is the tempting case -- a
    listing never merges, closes or pushes."""
    fake = host()
    text = merge_review.listing([("r", REPO)])
    assert "READY" in text
    verbs = {c[:2] for c in fake.calls}
    assert verbs <= READ_VERBS, verbs - READ_VERBS
    assert fake.merges == []


def test_the_listing_says_when_the_slot_holds_more_than_one(host):
    host(listing=[READY_VIEW, {**READY_VIEW, "number": 8, "isDraft": True}])
    text = merge_review.listing([("r", REPO)])
    assert "more than the one slot" in text


def test_an_unreadable_repository_is_unknown_rather_than_empty(host):
    host(listing_reply=done("<html>a proxy login page</html>"))
    text = merge_review.listing([("r", REPO)])
    assert "UNKNOWN" in text and REPO in text


def test_a_private_entry_without_a_name_is_not_asked_and_not_dropped(host):
    fake = host()
    text = merge_review.listing([("private-32", None)])
    assert "private-32" in text
    assert fake.calls == []


# --- the act ----------------------------------------------------------------


def run_main(*argv: str) -> tuple[int, str]:
    import io
    out = io.StringIO()
    err = io.StringIO()
    saved = sys.stdout, sys.stderr
    sys.stdout, sys.stderr = out, err
    try:
        code = merge_review.main(list(argv))
    finally:
        sys.stdout, sys.stderr = saved
    return code, out.getvalue() + err.getvalue()


def test_without_yes_it_verifies_and_stops(host):
    """Mutation: remove the `if not signed` block from `act` and this is red.
    The listing above cannot catch that -- it never reaches `act`."""
    fake = host()
    code, text = run_main("--repo", REPO, "--pr", "7")
    assert code == 1
    assert "READY" in text and "--yes" in text
    assert fake.merges == [], "a merge was issued without the signature"


@pytest.mark.parametrize("flag", ["--squash", "--rebase"])
def test_squash_and_rebase_are_refused_before_the_host_is_asked(host, flag):
    fake = host()
    code, text = run_main("--repo", REPO, "--pr", "7", "--yes", flag)
    assert code == 1
    assert "refused" in text and "merge commit" in text
    assert fake.calls == [], "the host was reached on a refused flag"


def test_the_merge_is_a_merge_commit_and_deletes_the_branch(host):
    """Exactly this vector and no other: `--merge` because a rewritten branch
    breaks every submodule pin pointing at it, `--delete-branch` because a
    merged branch left on the host is a slot that looks occupied.

    Mutation: change `--merge` to `--squash` in `merge` and this is red.
    """
    fake = host()
    code, text = run_main("--repo", REPO, "--pr", "7", "--yes")
    assert code == 0
    assert fake.merges == [
        ("pr", "merge", "7", "--repo", REPO, "--merge", "--delete-branch")]
    assert "abc123" in text and "2026-09-19T10:00:00Z" in text


def test_the_act_re_verifies_live_and_refuses_on_a_blocker(host):
    """The reading and the act are two moments; the act reads again."""
    fake = host(checks=GREEN_CHECKS + [{"name": "docs", "bucket": "pending"}])
    code, text = run_main("--repo", REPO, "--pr", "7", "--yes")
    assert code == 1
    assert "pending: docs" in text
    assert fake.merges == []


def test_somebody_else_s_pull_request_is_theirs_to_merge(host):
    fake = host(login="not-the-author")
    code, text = run_main("--repo", REPO, "--pr", "7", "--yes")
    assert code == 1
    assert "author" in text
    assert fake.merges == []


def test_the_host_refusing_the_merge_is_a_refusal_with_its_words(host):
    fake = host(merge=done("", "base branch was modified", 1))
    code, text = run_main("--repo", REPO, "--pr", "7", "--yes")
    assert code == 1
    assert "base branch was modified" in text


def test_the_act_never_closes_and_never_pushes(host):
    """Asserted on the whole call log, not on the merge alone."""
    fake = host()
    run_main("--repo", REPO, "--pr", "7", "--yes")
    for call in fake.calls:
        assert "close" not in call
        assert "push" not in call


# --- exit codes -------------------------------------------------------------


def test_an_unrunnable_gh_is_exit_two(monkeypatch):
    def missing(*args):
        raise merge_review.HostUnavailable("gh not found")
    monkeypatch.setattr(merge_review, "gh", missing)
    code, text = run_main("--repo", REPO)
    assert code == 2
    assert "gh could not be run" in text


def test_an_unreadable_roster_is_exit_two(monkeypatch, host):
    host()

    def broken():
        raise OSError("no roster")
    monkeypatch.setattr(merge_review, "roster_repositories", broken)
    code, text = run_main()
    assert code == 2
    assert "roster could not be read" in text


def test_a_signature_with_nothing_to_sign_is_refused():
    with pytest.raises(SystemExit) as stop:
        merge_review.main(["--yes"])
    assert stop.value.code == 2


# --- the route ---------------------------------------------------------------


def test_the_route_is_registered_as_qm_merge():
    import cli
    assert cli.ROUTES["merge"] == ("merge_review", False, [])
