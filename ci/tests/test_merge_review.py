"""`qm merge`: the reading half mutates nothing, and the act refuses on anything
short of READY, without the signature, and by any route but a merge commit.

The host is faked at `merge_review.gh`, the module's one boundary, so every
test sees exactly the argument vector the host would have seen and none of
them reaches the network. That is also what lets the listing be checked for
the property that matters most: it issued read verbs only.

The mutations, per `a-check-is-evidence-after-it-fails`, quoted as they printed.
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

    E       At index 0 diff: ('pr', 'merge', '7', '--repo', 'o/r', '--squash')
            != ('pr', 'merge', '7', '--repo', 'o/r', '--merge')
    FAILED test_the_merge_is_a_merge_commit_and_deletes_the_branch

  `retire_branch` ignoring a failed retarget

    FAILED test_a_failed_retarget_leaves_the_branch_in_place
    1 failed, 29 passed

  `retire_branch` deleting the branch before the retargets

    FAILED test_the_merge_is_a_merge_commit_and_deletes_the_branch
    FAILED test_a_stacked_pull_request_is_retargeted_before_the_branch_goes

  `listing` calling `merge` on each row it renders

    E       Extra items in the left set:
    E       ('pr', 'merge')
    FAILED test_the_listing_issues_only_read_verbs

  `blockers` with the never-ran branch disabled

    FAILED test_a_main_only_gate_that_never_ran_blocks_ready
    FAILED test_the_listing_keeps_a_pull_request_with_a_missing_gate_out_of_ready
    2 failed, 34 passed

  `runs_only_into` reading `doc.get("on")` without the True fallback

    FAILED test_a_main_only_gate_that_never_ran_blocks_ready
    FAILED test_the_listing_keeps_a_pull_request_with_a_missing_gate_out_of_ready
    2 failed, 34 passed

  `runs_only_into` without the `paths` exclusion

    FAILED test_a_gate_with_a_path_filter_is_not_required
    1 failed, 35 passed

  `gated_workflows` taking an unreadable listing as no workflows

    FAILED test_unreadable_workflows_are_unknown_rather_than_none
    1 failed, 35 passed

  `open_pull_requests` without `read_gates`

    FAILED test_the_listing_keeps_a_pull_request_with_a_missing_gate_out_of_ready
    1 failed, 35 passed

The rows carry the fake host's keyword arguments whole, because `None` is that
fake's "use the green default": a row passing `checks=None` would ask about
green checks while claiming to test unreadable ones.
"""

from __future__ import annotations

import base64
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
    "baseRefName": "main",
    "author": {"login": "someone"}, "isDraft": False, "state": "OPEN",
    "mergeable": "MERGEABLE", "mergeStateStatus": "CLEAN",
}
GREEN_CHECKS = [{"name": "tests", "bucket": "pass"},
                {"name": "lint", "bucket": "pass"}]

READ_VERBS = {("pr", "list"), ("pr", "view"), ("pr", "checks"), ("api", "user")}

# A workflow that runs only on pull requests into `main`, as the three
# main-only gates are written. `on` is left bare on purpose: YAML 1.1 reads it
# as True, which is the case the reader has to handle.
MAIN_ONLY = """name: Leak check
on:
  pull_request:
    branches: [main]
  push:
    branches: [main]
jobs:
  leaks:
    runs-on: ubuntu-latest
"""
LEAKS_RAN = {"name": "leaks", "bucket": "pass", "workflow": "Leak check"}


def done(stdout="", stderr="", code=0) -> subprocess.CompletedProcess:
    return subprocess.CompletedProcess(("gh",), code, stdout, stderr)


def is_read(call: tuple[str, ...]) -> bool:
    """A read verb, or a GET against the REST API (no `-X`)."""
    if call[:2] in READ_VERBS:
        return True
    return call[0] == "api" and "-X" not in call and call[1].startswith("repos/")


class FakeHost:
    """Answers `gh` from a script of replies and remembers every call."""

    def __init__(self, *, view=None, checks=None, listing=None, login="someone",
                 merge=None, after=None, checks_reply=None, listing_reply=None,
                 stacked=(), retarget=None, workflows=None, workflows_reply=None):
        self.view = READY_VIEW if view is None else view
        self.checks = GREEN_CHECKS if checks is None else checks
        self.listing = [self.view] if listing is None else listing
        # The base's `.github/workflows/`, file name to text. None is a
        # repository without the directory, which the host answers with 404.
        self.workflows = workflows
        # Whole replies, for the cases where what the host says is not JSON.
        self.workflows_reply = workflows_reply
        self.checks_reply = checks_reply
        self.listing_reply = listing_reply
        self.login = login
        self.merge = done() if merge is None else merge
        self.after = ({"mergedAt": "2026-09-19T10:00:00Z",
                       "mergeCommit": {"oid": "abc123"}}
                      if after is None else after)
        self.stacked = list(stacked)
        self.retarget = done() if retarget is None else retarget
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
        if args[0] == "api" and "pulls?state=open&base=" in args[1]:
            return done(json.dumps(self.stacked))
        if args[0] == "api" and "/contents/.github/workflows?ref=" in args[1]:
            if self.workflows_reply is not None:
                return self.workflows_reply
            if self.workflows is None:
                return done(json.dumps({"message": "Not Found", "status": "404"}),
                            "gh: Not Found (HTTP 404)", 1)
            return done(json.dumps([
                {"type": "file", "path": f".github/workflows/{name}",
                 "sha": f"sha-{name}"} for name in self.workflows]))
        if args[0] == "api" and "/git/blobs/sha-" in args[1]:
            name = args[1].split("/git/blobs/sha-", 1)[1]
            text = self.workflows[name]
            return done(json.dumps({
                "encoding": "base64",
                "content": base64.b64encode(text.encode()).decode()}))
        if args[:3] == ("api", "-X", "PATCH"):
            return self.retarget
        if args[:3] == ("api", "-X", "DELETE"):
            return done()
        raise AssertionError(f"unscripted gh call: {args}")

    @property
    def merges(self) -> list[tuple[str, ...]]:
        return [c for c in self.calls if c[:2] == ("pr", "merge")]

    @property
    def writes(self) -> list[tuple[str, ...]]:
        """PATCH and DELETE, in the order issued."""
        return [c[2:4] for c in self.calls if c[:2] == ("api", "-X")]


@pytest.fixture
def host(monkeypatch):
    def install(**kw) -> FakeHost:
        fake = FakeHost(**kw)
        monkeypatch.setattr(merge_review, "gh", fake)
        # The reads are cached per base and per blob; each test is its own host.
        monkeypatch.setattr(merge_review, "_GATED", {})
        monkeypatch.setattr(merge_review, "_BLOBS", {})
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

    Rows carry the host's keyword arguments whole, so what a row says is what
    the fake does.

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


# --- a gate the host never started is a blocker, not a pass ---------------------


def test_a_main_only_gate_that_never_ran_blocks_ready(host):
    """The retarget case: every check that ran is green, and the workflow that
    runs only on pull requests into `main` is absent from the list because
    nothing started it. Absent is not green.

    Mutation: delete the `if missing and pr.checks_read` branch of `blockers`
    and this is red; read `doc.get("on")` without the True fallback and it is
    red too, because the bare key `on` parses as True.
    """
    host(workflows={"leak-check.yml": MAIN_ONLY})
    why = merge_review.blockers(merge_review.view(REPO, 7))
    assert any("never ran: Leak check" in reason for reason in why), why


def test_the_same_gate_having_reported_is_ready(host):
    host(workflows={"leak-check.yml": MAIN_ONLY}, checks=GREEN_CHECKS + [LEAKS_RAN])
    assert merge_review.blockers(merge_review.view(REPO, 7)) == []


def test_a_gate_with_a_path_filter_is_not_required(host):
    """Not running is a legitimate outcome for it.

    Mutation: drop the `paths` exclusion from `runs_only_into` and this is red.
    """
    filtered = MAIN_ONLY.replace("    branches: [main]\n  push:",
                                 "    branches: [main]\n    paths: ['ci/**']\n  push:")
    host(workflows={"leak-check.yml": filtered})
    assert merge_review.blockers(merge_review.view(REPO, 7)) == []


def test_a_gate_filtered_on_another_base_is_not_required(host):
    """A pull request stacked on `evolve/x` owes nothing to `main`'s gates."""
    host(view={**READY_VIEW, "baseRefName": "evolve/x"},
         workflows={"leak-check.yml": MAIN_ONLY})
    assert merge_review.blockers(merge_review.view(REPO, 7)) == []


def test_the_listing_keeps_a_pull_request_with_a_missing_gate_out_of_ready(host):
    """One definition for both halves: the listing reads the base's gates too.

    Mutation: drop `read_gates(pr)` from `open_pull_requests` and this is red.
    """
    host(workflows={"leak-check.yml": MAIN_ONLY})
    text = merge_review.listing([("r", REPO)])
    assert "never ran: Leak check" in text
    assert not [line for line in text.splitlines() if "READY:" in line]


def test_unreadable_workflows_are_unknown_rather_than_none(host):
    """A failed read is not a base with no gates.

    Mutation: return `[]` where `gated_workflows` returns None and this is red.
    """
    host(workflows_reply=done("", "boom", 1))
    why = merge_review.blockers(merge_review.view(REPO, 7))
    assert any("could not be read" in reason for reason in why), why


# --- the listing reads and nothing else ---------------------------------------


def test_the_listing_issues_only_read_verbs(host):
    """The property the default mode exists for. Whatever the state of the
    queue -- here one READY pull request, which is the tempting case -- a
    listing never merges, closes or pushes."""
    fake = host(workflows={"leak-check.yml": MAIN_ONLY},
                checks=GREEN_CHECKS + [LEAKS_RAN])
    text = merge_review.listing([("r", REPO)])
    assert "READY" in text
    writes = [c for c in fake.calls if not is_read(c)]
    assert writes == [], writes
    assert fake.merges == []


def test_the_listing_counts_open_pull_requests_and_keeps_a_draft_out_of_ready(host):
    """Two open is not a finding; the stacked draft is simply not READY."""
    host(listing=[READY_VIEW, {**READY_VIEW, "number": 8, "isDraft": True}])
    text = merge_review.listing([("r", REPO)])
    assert "2 open pull requests" in text
    assert "stacked on another pull request" in text
    ready = [line for line in text.splitlines() if "READY:" in line]
    assert ready and f"{REPO}#7" in ready[0] and "#8" not in ready[0]


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
    breaks every submodule pin pointing at it, and the branch deleted after.

    Mutation: change `--merge` to `--squash` in `merge` and this is red.
    """
    fake = host()
    code, text = run_main("--repo", REPO, "--pr", "7", "--yes")
    assert code == 0
    assert fake.merges == [("pr", "merge", "7", "--repo", REPO, "--merge")]
    assert fake.writes == [("DELETE", f"repos/{REPO}/git/refs/heads/evolve/slice")]
    assert "abc123" in text and "2026-09-19T10:00:00Z" in text


def test_a_stacked_pull_request_is_retargeted_before_the_branch_goes(host):
    """Deleting the branch first closes every pull request based on it."""
    fake = host(view={**READY_VIEW, "baseRefName": "main"}, stacked=[8, 9])
    code, text = run_main("--repo", REPO, "--pr", "7", "--yes")
    assert code == 0
    assert fake.writes == [("PATCH", f"repos/{REPO}/pulls/8"),
                           ("PATCH", f"repos/{REPO}/pulls/9"),
                           ("DELETE", f"repos/{REPO}/git/refs/heads/evolve/slice")]
    assert ("-f", "base=main") == fake.calls[-3][-2:]
    assert "#8 moved down onto main" in text


def test_a_failed_retarget_leaves_the_branch_in_place(host):
    fake = host(view={**READY_VIEW, "baseRefName": "main"}, stacked=[8],
                retarget=done("", "HTTP 422", 1))
    code, text = run_main("--repo", REPO, "--pr", "7", "--yes")
    assert code == 0
    assert ("DELETE", f"repos/{REPO}/git/refs/heads/evolve/slice") not in fake.writes
    assert "left in place" in text and "HTTP 422" in text


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
