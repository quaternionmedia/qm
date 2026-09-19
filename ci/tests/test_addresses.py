"""The address grammar, whose one property is that an address survives a round trip.

WHY THE ROUND TRIP IS THE TEST. A parser checked only on its output can drop a
segment and still look right: `.../branch/evolve/protect-main` parsed to
`evolve` reports a plausible branch, and nothing about the parse says otherwise.
Formatting it back and comparing is what catches that, and it is the assertion
every conformance vector carries.

THE VECTORS ARE RUN HERE AND SHIPPED TO FORKS. `project-seed/address-vectors.json`
reaches every project through the governance submodule, so dossier's and qmcp's
implementations can be held to the same cases without either importing this one.
A vector that only this repository ran would not be a shared contract.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

CI_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(CI_DIR))

from addresses import (  # noqa: E402
    GLOBAL_PREFIXES,
    KINDS,
    REPO,
    Address,
    check,
    format_address,
    is_global,
    load_vectors,
    main,
    parse,
    render,
)

ROOT = CI_DIR.parent


# --- the conformance vectors -------------------------------------------------


def test_every_committed_vector_holds():
    """The shared contract. If this fails, forks running the same file fail too."""
    assert check(load_vectors()) == []


def test_the_vectors_cover_both_verdicts():
    """A file of only-valid cases proves a parser that accepts everything."""
    cases = load_vectors()
    assert any(case.get("valid", True) for case in cases)
    assert any(not case.get("valid", True) for case in cases)


def test_every_vector_says_what_it_is_for():
    """A case with no reason is one nobody can decide to remove."""
    for case in load_vectors():
        assert case.get("why") or case.get("valid", True), case["address"]


def test_an_empty_vector_file_is_refused(tmp_path):
    path = tmp_path / "v.json"
    path.write_text(json.dumps({"schema": 1, "cases": []}), encoding="utf-8")
    with pytest.raises(SystemExit):
        load_vectors(path)


def test_a_missing_vector_file_is_refused(tmp_path):
    with pytest.raises(SystemExit):
        load_vectors(tmp_path / "absent.json")


# --- the rule that makes an address reversible -------------------------------


def test_a_branch_keeps_the_slashes_git_gave_it():
    """The defect this grammar exists for. dossier slugged these to hyphens,
    which is not reversible, on 30 of the 32 branches in this repository."""
    found = parse("quaternionmedia/qm/branch/evolve/protect-main")
    assert found.id == "evolve/protect-main"


def test_a_slashed_branch_and_a_hyphenated_one_stay_distinct():
    """`replace("/", "-")` collapsed these two onto one address."""
    slashed = parse("quaternionmedia/qm/branch/evolve/protect-main")
    hyphened = parse("quaternionmedia/qm/branch/evolve-protect-main")
    assert slashed.id != hyphened.id
    assert slashed.format() != hyphened.format()


def test_a_kind_name_inside_an_id_does_not_retrigger_a_match():
    """Substring parsing -- `elif "/pr/" in name` -- reads this as a pull
    request. Segment position is what makes it a branch."""
    found = parse("quaternionmedia/qm/branch/feature/pr/nested")
    assert found.kind == "branch"
    assert found.id == "feature/pr/nested"


def test_every_kind_round_trips_with_a_slashed_id():
    """Not just branches: any id may contain a slash, and none may be mangled."""
    for kind in KINDS:
        text = f"o/r/{kind}/a/b/c"
        found = parse(text)
        assert found is not None and found.kind == kind
        assert found.id == "a/b/c"
        assert found.format() == text


# --- what is and is not an address -------------------------------------------


def test_a_bare_owner_repo_is_the_repository():
    found = parse("quaternionmedia/qm")
    assert found.kind == REPO
    assert found.id == ""
    assert found.format() == "quaternionmedia/qm"


def test_an_unknown_third_segment_is_not_an_address():
    """The closed kind set is what separates an address from an ordinary path."""
    assert parse("quaternionmedia/qm/tools/build.sh") is None


def test_a_kind_with_no_id_is_not_an_address():
    assert parse("quaternionmedia/qm/branch/") is None


def test_an_owner_alone_is_not_an_address():
    assert parse("quaternionmedia") is None


def test_an_empty_owner_segment_is_not_an_address():
    assert parse("/qm/branch/main") is None


def test_the_empty_string_is_not_an_address():
    assert parse("") is None


def test_a_non_address_returns_none_rather_than_raising():
    """Callers sweep mixed lists where most names are not addresses. Raising
    would make the ordinary case the exceptional one."""
    for text in ("not an address", "lang/python", "", "x"):
        assert parse(text) is None


def test_the_global_buckets_are_reserved_and_not_repo_scoped():
    for prefix in GLOBAL_PREFIXES:
        assert is_global(prefix + "something")
        assert parse(prefix + "something") is None


# --- formatting --------------------------------------------------------------


def test_formatting_and_parsing_are_inverses():
    text = format_address("quaternionmedia", "qmcp", "delta", "summarizer")
    assert text == "quaternionmedia/qmcp/delta/summarizer"
    assert parse(text) == Address("quaternionmedia", "qmcp", "delta", "summarizer")


def test_formatting_an_unknown_kind_is_refused():
    with pytest.raises(ValueError, match="not a kind"):
        format_address("o", "r", "sprocket", "x")


def test_formatting_a_kind_with_no_id_is_refused():
    """An address that denotes nothing must not be constructible."""
    with pytest.raises(ValueError, match="needs an id"):
        format_address("o", "r", "branch", "")


def test_a_repo_address_needs_no_id():
    assert format_address("o", "r", REPO) == "o/r"


# --- the check reports rather than flatters ----------------------------------


def test_a_vector_that_should_not_parse_but_does_is_reported():
    assert check([{"address": "o/r/branch/x", "valid": False}])


def test_a_vector_that_should_parse_but_does_not_is_reported():
    assert check([{"address": "o/r/nope/x", "valid": True}])


def test_a_wrong_field_is_named_in_the_problem():
    problems = check([{"address": "o/r/branch/x", "valid": True, "id": "y"}])
    assert any("vector says 'y'" in p for p in problems)


def test_a_vector_that_holds_reports_nothing():
    assert check([{"address": "o/r/branch/x", "valid": True, "owner": "o",
                   "repo": "r", "kind": "branch", "id": "x"}]) == []


# --- the route ---------------------------------------------------------------


def test_check_passes_against_the_committed_vectors():
    assert main(["--check"]) == 0


def test_check_fails_when_a_vector_does_not_hold(tmp_path, capsys):
    path = tmp_path / "v.json"
    path.write_text(json.dumps({"schema": 1, "cases": [
        {"address": "o/r/branch/x", "valid": True, "id": "wrong"}]}), encoding="utf-8")
    assert main(["--vectors", str(path), "--check"]) == 1
    assert "vector says" in capsys.readouterr().err


def test_parsing_a_non_address_is_not_an_error(capsys):
    assert main(["--parse", "not an address"]) == 0
    assert "is not an address" in capsys.readouterr().out


def test_the_listing_names_every_kind():
    text = render(load_vectors())
    for kind in KINDS:
        assert kind in text


def test_the_output_states_that_it_does_not_resolve():
    """A grammar that read as an existence check would have every dashboard
    render depending on a network call."""
    assert "does not tell you the thing addressed exists" in render(load_vectors())


def test_a_vector_omitting_valid_is_treated_as_valid():
    """`case.get("valid", True)` -- the default is what most cases rely on, and
    an untested default is one a change can flip without any test noticing."""
    assert check([{"address": "o/r/branch/x", "owner": "o", "repo": "r",
                   "kind": "branch", "id": "x"}]) == []
    assert check([{"address": "o/r/nope/x"}])


def test_an_address_cannot_be_edited_after_it_is_parsed():
    """Addresses are passed between systems as identity. One that can be
    rewritten in flight is not an identity."""
    found = parse("o/r/branch/x")
    with pytest.raises(Exception):
        found.id = "y"


def test_parsing_a_repo_address_shows_a_placeholder_for_the_empty_id(capsys):
    """A blank where the id goes reads as a field that failed to print."""
    assert main(["--parse", "quaternionmedia/qm"]) == 0
    assert "id     -" in capsys.readouterr().out
