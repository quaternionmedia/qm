"""Tests for the vendor/model-name check, and for its one exemption.

The exemption is the reason this file exists. A check with a hole is worse than
no check -- a green tick standing where a reader believes something is enforced
-- so the hole is tested from both sides: it must let exactly one commit through,
and it must announce it every time.

Real repositories, because the subject check is about `git log` output.
"""

from __future__ import annotations

import sys
from importlib import import_module
from pathlib import Path

from conftest import commit_all, git, run_tool, write

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
_mod = import_module("check_attribution")
EXEMPT_SUBJECTS = _mod.EXEMPT_SUBJECTS
families_in = _mod.families_in

NAMED = "Re-refactor docs with Fable 5"


def check(repo: Path, *args: str):
    return run_tool("check_attribution.py", *args, cwd=repo)


# --- the rule ---------------------------------------------------------------


def test_a_subject_naming_a_model_fails(repo: Path):
    base = git(repo, "rev-parse", "HEAD")
    write(repo / "a.md", "x\n")
    commit_all(repo, NAMED)
    result = check(repo, "--base-ref", base)
    assert result.returncode == 1
    assert "names a tool" in result.stdout + result.stderr


def test_an_ordinary_subject_passes(repo: Path):
    base = git(repo, "rev-parse", "HEAD")
    write(repo / "a.md", "x\n")
    commit_all(repo, "Re-refactor the docs")
    assert check(repo, "--base-ref", base).returncode == 0


def test_the_detector_finds_the_name_at_all():
    """If this stops matching, every test below passes for the wrong reason."""
    assert families_in(NAMED)


# --- trailers and the author field ------------------------------------------
#
# The rule these hold is `DRAFT-human-only-contributorship.md` section 3: no
# trailer or author field naming an address that is not a monitored inbox
# reachable to a human accountable for the content. Every one of the cases below
# was run against the check before it was written down here, and the two marked
# as findings were routed around by an adversarial pass and closed afterwards.

VENDOR = "noreply@anthropic.com"


def commit_with(repo: Path, subject: str, *trailers: str, author: str = "") -> str:
    """A commit whose trailers git itself will parse.

    Two `-m` blocks rather than one string: git joins them with a blank line, so
    the second is a paragraph of its own, which is the only place git recognises
    a trailer. Building the message by hand would be a second definition of
    "trailer" sitting next to git's.
    """
    args = ["commit", "-q", "--allow-empty", "-m", subject]
    if trailers:
        args += ["-m", "\n".join(trailers)]
    if author:
        args += [f"--author={author}"]
    git(repo, *args)
    return git(repo, "rev-parse", "HEAD")


def test_a_vendor_noreply_co_author_fails(repo: Path):
    base = git(repo, "rev-parse", "HEAD")
    commit_with(repo, "An ordinary subject", f"Co-authored-by: Fable 5 <{VENDOR}>")
    result = check(repo, "--base-ref", base)
    assert result.returncode == 1
    assert "nobody reads" in result.stdout


def test_the_two_reasons_are_reported_separately(repo: Path):
    # A tool's name and an unreadable address are different defects with
    # different fixes: deleting a byline, and naming somebody who can be asked
    # why. A single message would send half the readers to the wrong one.
    base = git(repo, "rev-parse", "HEAD")
    commit_with(repo, "S", f"Co-authored-by: Fable 5 <{VENDOR}>")
    out = check(repo, "--base-ref", base).stdout
    assert "names a tool where a person should be" in out
    assert "nobody reads" in out


def test_an_ordinary_human_co_author_passes(repo: Path):
    base = git(repo, "rev-parse", "HEAD")
    commit_with(repo, "S", "Co-authored-by: A Person <a@person.example>")
    assert check(repo, "--base-ref", base).returncode == 0


def test_a_forge_per_user_alias_passes(repo: Path):
    # It is not an unreachable address standing in for accountability -- it is
    # an account, naming one person. Refusing it would refuse every contributor
    # who keeps their email private.
    base = git(repo, "rev-parse", "HEAD")
    commit_with(repo, "S", "Co-authored-by: A Person <p@users.noreply.github.com>")
    assert check(repo, "--base-ref", base).returncode == 0


def test_a_noreply_wearing_the_per_user_exemption_fails(repo: Path):
    """A finding. The adversarial pass walked through the first version here.

    The exemption was unconditional on the host label, so any no-reply local
    part at a host called `users.noreply.<anything>` inherited it. The exemption
    now holds only where the local part names an account.
    """
    base = git(repo, "rev-parse", "HEAD")
    commit_with(repo, "S", "Co-authored-by: A B <noreply@users.noreply.evil.test>")
    assert check(repo, "--base-ref", base).returncode == 1


def test_a_human_at_a_vendor_domain_passes(repo: Path):
    # Section 3 is explicit: naming a human is always fine, including a human
    # who works at or through a tool vendor. The ban is on unreachable addresses
    # standing in for accountability, not on the domain.
    base = git(repo, "rev-parse", "HEAD")
    commit_with(repo, "S", "Co-authored-by: A Person <aperson@anthropic.com>")
    assert check(repo, "--base-ref", base).returncode == 0


def test_a_bare_address_is_read_as_an_address(repo: Path):
    """The other finding, and it is about the *reason*, not the verdict.

    With no angle brackets there was no address to test, so the whole value fell
    to the name check and matched on the domain. A vendor `noreply@` was still
    refused -- with the words "names a tool", which is the wrong reason -- and a
    real contributor's bare `person@vendor` address was refused with it too.
    """
    base = git(repo, "rev-parse", "HEAD")
    commit_with(repo, "S", f"Co-authored-by: {VENDOR}")
    result = check(repo, "--base-ref", base)
    assert result.returncode == 1
    assert "nobody reads" in result.stdout
    assert "names a tool" not in result.stdout


def test_a_bare_human_address_at_a_vendor_domain_passes(repo: Path):
    base = git(repo, "rev-parse", "HEAD")
    commit_with(repo, "S", "Co-authored-by: aperson@anthropic.com")
    assert check(repo, "--base-ref", base).returncode == 0


def test_a_model_name_at_a_reachable_address_fails(repo: Path):
    # The seed AGENTS.md adds "do not add yourself, your model name" to the
    # record's address test. A byline routing somewhere real still credits
    # software for the work.
    base = git(repo, "rev-parse", "HEAD")
    commit_with(repo, "S", "Co-authored-by: Fable 5 <real@person.example>")
    assert check(repo, "--base-ref", base).returncode == 1


def test_every_trailer_is_read_not_only_co_author(repo: Path):
    # Section 3 says "No commit trailer", and keying on one name would leave the
    # rule enforced for the spelling somebody happened to think of.
    base = git(repo, "rev-parse", "HEAD")
    commit_with(repo, "S", f"Signed-off-by: A Bot <{VENDOR}>")
    assert check(repo, "--base-ref", base).returncode == 1


def test_the_trailer_key_is_case_insensitive(repo: Path):
    # Both spellings appear in the wild, from the same tool.
    base = git(repo, "rev-parse", "HEAD")
    commit_with(repo, "S", f"co-authored-by: Fable 5 <{VENDOR}>")
    assert check(repo, "--base-ref", base).returncode == 1


def test_the_author_field_is_read(repo: Path):
    base = git(repo, "rev-parse", "HEAD")
    commit_with(repo, "S", author=f"Fable 5 <{VENDOR}>")
    result = check(repo, "--base-ref", base)
    assert result.returncode == 1
    assert "author" in result.stdout


def test_the_committer_is_not_read(repo: Path):
    """Every squash merge on GitHub is committed by `GitHub <noreply@github.com>`.

    Measured on a real repository before this was written. Reading the committer
    would fail every merge the org makes, on the forge's own identity -- a guard
    that fires on the thing it is protecting is a guard somebody switches off.
    Section 3 says "author field", and the author is the accountable human.
    """
    base = git(repo, "rev-parse", "HEAD")
    git(repo, "-c", "user.name=GitHub", "-c", "user.email=noreply@github.com",
        "commit", "-q", "--allow-empty", "-m", "S", "--author=A Person <a@b.example>")
    assert check(repo, "--base-ref", base).returncode == 0


def test_prose_that_looks_like_a_trailer_is_not_one(repo: Path):
    # git owns the definition, and the forge uses the same one. A regex written
    # beside it would disagree with both.
    base = git(repo, "rev-parse", "HEAD")
    commit_with(repo, "S", f"Co-authored-by: Fable 5 <{VENDOR}> is banned.",
                "", "An ordinary closing paragraph.")
    assert check(repo, "--base-ref", base).returncode == 0


def test_a_url_is_not_an_address(repo: Path):
    base = git(repo, "rev-parse", "HEAD")
    commit_with(repo, "S", "See-also: https://example.com/a@b")
    assert check(repo, "--base-ref", base).returncode == 0


def test_a_clean_range_says_what_it_read(repo: Path):
    # A check whose clean message does not name what it covered is a check a
    # reader credits for more than it did.
    base = git(repo, "rev-parse", "HEAD")
    commit_with(repo, "S", "Co-authored-by: A Person <a@person.example>")
    out = check(repo, "--base-ref", base).stdout
    assert "trailers" in out and "authors" in out


def test_a_ref_that_is_not_there_is_one_finding(repo: Path):
    """Two checks read the same range, and both probe it.

    Reported once because a count of two for one missing ref is a reader
    counting problems that are not there -- and the first thing anyone does
    with a finding count is decide how bad it is.
    """
    result = check(repo, "--base-ref", "no/such/ref")
    assert result.returncode == 1
    assert result.stdout.count("does not exist") == 1
    assert "1 finding(s)" in result.stdout


def test_there_is_no_attribution_exemption_hatch():
    """Adding one has to be a visible act, not a quiet edit.

    The subject check needs its list because a subject is immutable. This one
    runs over a pull request's own commits, which their author can still amend,
    so an empty hatch would only ever be an invitation to add the first red.
    """
    assert not hasattr(_mod, "EXEMPT_ATTRIBUTION")


# --- the exemption ----------------------------------------------------------


def test_exactly_one_subject_is_exempt():
    """Growth in this list is the failure mode the code comment names."""
    assert len(EXEMPT_SUBJECTS) == 1


def test_every_exemption_carries_a_reason():
    """An exemption without a stated reason is indistinguishable from an oversight."""
    for sha, reason in EXEMPT_SUBJECTS.items():
        assert len(sha) == 40, f"{sha} is not a full SHA; a short one can collide"
        assert reason and len(reason) > 80, f"{sha[:8]} has no substantive reason"


def test_the_exemption_is_keyed_on_a_full_sha():
    """A prefix would exempt any future commit that happened to share it."""
    for sha in EXEMPT_SUBJECTS:
        assert all(c in "0123456789abcdef" for c in sha)


def test_an_exempt_subject_on_a_different_commit_still_fails(repo: Path):
    """The exemption is the commit, not the wording.

    Keying on the subject text would exempt every future commit that copied it,
    which is how one allowance becomes a general licence.
    """
    base = git(repo, "rev-parse", "HEAD")
    write(repo / "a.md", "x\n")
    commit_all(repo, NAMED)          # same words, different SHA
    assert check(repo, "--base-ref", base).returncode == 1


def test_the_exemption_is_announced_not_silent(repo: Path):
    """A hole a run does not print is a hole in a check that reports green.

    Driven through the module rather than a fixture repo, because the exempt
    SHA only exists in the real corpus.
    """
    source = (Path(__file__).resolve().parent.parent / "check_attribution.py").read_text(
        encoding="utf-8"
    )
    assert "is exempt" in source
    assert "EXEMPT_SUBJECTS[sha]" in source, "the reason must be printed, not just the SHA"
