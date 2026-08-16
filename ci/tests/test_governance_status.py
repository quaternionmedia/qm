"""Every signal, in a fixture where it reports bad.

A signal only ever observed green has not been tested; it has been watched. The
defects this suite exists for are not crashes -- they are confident, clean
answers. Each test below is written so that it FAILS against the mistake it
names, and several of them did fail against an earlier draft of the tool:
`ls-tree` without `-r`, "any merge commit is a propagation", a whole-file
regex over .gitmodules, a truncated API page, seed drift measured against a
moving tip.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

from governance_fixtures import (  # noqa: F401  (`corpus` is a fixture, used by name)
    SEED_README,
    TEMPLATE,
    add_project,
    advance_corpus,
    commit,
    corpus,
    git,
    record,
    run_tool,
    with_origin,
    write,
)

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import governance_status as gs  # noqa: E402


def generate(repo: Path, *extra: str) -> dict:
    proc = run_tool(
        "governance_status.py", "--offline", "--corpus-ref", "main", *extra, cwd=repo
    )
    assert proc.returncode == 0, proc.stderr
    return yaml.safe_load(proc.stdout)


def project(doc: dict, name: str) -> dict:
    return next(p for p in doc["projects"] if p["name"] == name)


# --------------------------------------------------------------------------
# behind_corpus
# --------------------------------------------------------------------------


def test_a_branch_behind_the_corpus_reports_how_far(corpus):
    add_project(corpus, "alpha")
    advance_corpus(corpus, 3)
    assert project(generate(corpus), "alpha")["branch"]["behind_corpus"] == 3


def test_a_branch_level_with_the_corpus_reports_zero(corpus):
    add_project(corpus, "alpha")
    assert project(generate(corpus), "alpha")["branch"]["behind_corpus"] == 0


# --------------------------------------------------------------------------
# last_propagation -- three ways to get this wrong, all of them tried
# --------------------------------------------------------------------------


def test_a_branch_that_never_took_the_corpus_reports_no_propagation(corpus):
    add_project(corpus, "alpha")
    advance_corpus(corpus, 2)
    assert project(generate(corpus), "alpha")["branch"]["last_propagation"] is None


def test_a_branch_merging_its_own_feature_branch_is_not_a_propagation(corpus):
    """The trap that reports an untouched branch as current.

    project/qmetronome's only merge commit is its own pull request #1. A check
    asking "does this branch have a merge commit" calls that a propagation and
    reports a branch sixty-nine commits behind as up to date.
    """
    add_project(corpus, "alpha")
    advance_corpus(corpus, 2)
    git(corpus, "checkout", "-q", "-b", "feature/x", "project/alpha")
    write(corpus / "adr" / "DRAFT-more.md", record())
    commit(corpus, "alpha: a feature")
    git(corpus, "checkout", "-q", "project/alpha")
    git(corpus, "merge", "-q", "--no-ff", "-m", "Merge pull request #1", "feature/x")
    git(corpus, "checkout", "-q", "main")

    assert project(generate(corpus), "alpha")["branch"]["last_propagation"] is None


def test_the_corpus_own_merges_are_not_counted_as_propagations(corpus):
    """The trap that multiplies one propagation into thirteen.

    Once a branch has taken any corpus history, every merge commit on the
    corpus is reachable from it, and each has a parent contained in the corpus.
    Walking all reachable merges reported main's own thirteen merges as
    thirteen propagations of a branch that had had exactly one.
    """
    git(corpus, "checkout", "-q", "-b", "evolve/x", "main")
    write(corpus / "records" / "DRAFT-three.md", record())
    commit(corpus, "corpus: a change")
    git(corpus, "checkout", "-q", "main")
    git(corpus, "merge", "-q", "--no-ff", "-m", "Merge pull request #9", "evolve/x")
    add_project(corpus, "alpha")

    branch = project(generate(corpus), "alpha")["branch"]
    assert branch["last_propagation"] is None, (
        "a branch cut from main after main merged something has taken no "
        "propagation of its own"
    )


def test_a_real_propagation_is_found_and_dated(corpus):
    add_project(corpus, "alpha")
    advance_corpus(corpus, 2)
    git(corpus, "checkout", "-q", "project/alpha")
    git(corpus, "merge", "-q", "--no-ff", "-m", "Propagate main", "main")
    git(corpus, "checkout", "-q", "main")

    prop = project(generate(corpus), "alpha")["branch"]["last_propagation"]
    assert prop is not None and prop["subject"] == "Propagate main"
    assert project(generate(corpus), "alpha")["branch"]["behind_corpus"] == 0


def test_a_propagation_through_an_intermediate_branch_is_still_found(corpus):
    """Propagation as the runbook actually instructs it: via propagate/<name>."""
    add_project(corpus, "alpha")
    advance_corpus(corpus, 2)
    git(corpus, "checkout", "-q", "-b", "propagate/alpha", "project/alpha")
    git(corpus, "merge", "-q", "--no-ff", "-m", "Merge main into propagate/alpha", "main")
    git(corpus, "checkout", "-q", "project/alpha")
    git(corpus, "merge", "-q", "--no-ff", "-m", "Merge pull request #2", "propagate/alpha")
    git(corpus, "checkout", "-q", "main")

    assert project(generate(corpus), "alpha")["branch"]["last_propagation"] is not None


# --------------------------------------------------------------------------
# seed drift -- and the distinction that makes it a signal at all
# --------------------------------------------------------------------------


def test_an_edited_copy_drifts_from_the_seed_it_was_taken_from(corpus):
    add_project(corpus, "alpha", template=TEMPLATE + "A project edited this.\n")
    seed = project(generate(corpus), "alpha")["seed"]
    assert seed["adr_template_vs_merge_base"] == "drift"


def test_a_moved_seed_does_not_make_an_untouched_copy_look_edited(corpus):
    """The discrimination the two comparisons exist for.

    Measured against the corpus tip, every branch here drifts and the signal is
    behind_corpus said twice. Measured against the branch's own merge-base, an
    untouched copy still matches -- which is the fact a reader wants.
    """
    add_project(corpus, "alpha")
    advance_corpus(corpus, 2, touch_seed=True)
    seed = project(generate(corpus), "alpha")["seed"]
    assert seed["adr_template_vs_corpus"] == "drift"
    assert seed["adr_template_vs_merge_base"] == "match"


def test_a_missing_copy_is_absent_rather_than_matching(corpus):
    add_project(corpus, "alpha")
    git(corpus, "checkout", "-q", "project/alpha")
    (corpus / "adr" / "TEMPLATE.md").unlink()
    commit(corpus, "alpha: drop the template")
    git(corpus, "checkout", "-q", "main")
    seed = project(generate(corpus), "alpha")["seed"]
    assert seed["adr_template_vs_merge_base"] == "absent"


def test_an_unfinished_copy_still_carrying_the_seed_comment_reports_it(corpus):
    add_project(corpus, "alpha", readme=SEED_README)
    assert project(generate(corpus), "alpha")["seed"]["readme_seed_comment_left_in"] is True


def test_a_finished_copy_reports_the_seed_comment_gone(corpus):
    add_project(corpus, "alpha")
    assert project(generate(corpus), "alpha")["seed"]["readme_seed_comment_left_in"] is False


# --------------------------------------------------------------------------
# records
# --------------------------------------------------------------------------


def test_records_are_counted_from_the_ref_not_the_working_tree(corpus):
    """Reading the checkout is what put a false adoption finding into main."""
    add_project(corpus, "alpha", records={"DRAFT-a.md": record(), "DRAFT-b.md": record()})
    # The worktree is on main and has no adr/ at all.
    assert not (corpus / "adr").exists()
    assert project(generate(corpus), "alpha")["records"]["total"] == 2


def test_a_ratified_record_is_counted_as_ratified(corpus):
    add_project(corpus, "alpha", records={"ADR-0001-a.md": record(status="Accepted")})
    census = project(generate(corpus), "alpha")["records"]
    assert census["ratified"] == 1 and census["numbered_files"] == 1


def test_a_directory_of_records_is_not_reported_as_empty(corpus):
    """`ls-tree` without -r lists the directory entry and nothing in it.

    The first run of this generator reported "no records" for a directory
    holding ten of them, and it reported it as an unknown rather than as zero
    -- which is the only reason it was caught at a glance.
    """
    doc = generate(corpus)
    assert doc["corpus"]["records"]["total"] == 2


# --------------------------------------------------------------------------
# the empty-query passes
# --------------------------------------------------------------------------


def test_a_clone_with_no_project_refs_reports_unknown_not_an_empty_list(corpus):
    """A shallow or unfetched checkout must not render as a clean org."""
    doc = generate(corpus)
    assert isinstance(doc["projects"], dict) and "unknown" in doc["projects"]
    assert "fetch them" in doc["projects"]["unknown"]


def test_remote_project_refs_are_preferred_over_local_ones(corpus):
    add_project(corpus, "alpha")
    with_origin(corpus)
    doc = generate(corpus)
    assert project(doc, "alpha")["branch"]["ref"] == "origin/project/alpha"


def test_one_unreadable_project_does_not_destroy_the_document(corpus):
    add_project(corpus, "alpha")
    add_project(corpus, "beta")
    doc = generate(corpus, "--offline")
    names = {p["name"] for p in doc["projects"]}
    assert names == {"alpha", "beta"}


def test_offline_reports_github_fields_as_unknown_rather_than_absent(corpus):
    add_project(corpus, "alpha")
    entry = project(generate(corpus), "alpha")
    for field in ("repository", "adoption", "open_prs"):
        assert "unknown" in entry[field], f"{field} must say why, not vanish"
    assert entry["repository"]["unknown"].endswith("--offline")


def test_the_credential_a_run_used_is_recorded(corpus):
    add_project(corpus, "alpha")
    assert generate(corpus)["generator"]["credential"] == "none: --offline"


def test_unknowns_are_counted_in_the_header(corpus):
    add_project(corpus, "alpha")
    doc = generate(corpus)
    assert doc["generator"]["unknowns"] >= 3


# --------------------------------------------------------------------------
# .gitmodules parsing, which decides whether a project vendors the corpus
# --------------------------------------------------------------------------


def test_a_submodule_that_is_not_the_corpus_is_not_read_as_the_pin():
    """alfred vendors otto with `branch = master`, and nothing else.

    A whole-file regex for `branch =` reports `master` as alfred's corpus pin.
    """
    parsed = gs.parse_gitmodules(
        '[submodule "alfred/otto"]\n'
        "\tpath = alfred/otto\n"
        "\turl = git@github.com:quaternionmedia/otto.git\n"
        "\tbranch = master\n"
    )
    assert parsed == {"corpus_mounted_at": None, "branch": None}


def test_the_corpus_is_found_wherever_it_is_mounted():
    """codecartographer mounts it at docs/qm, not governance/qm.

    The sibling submodule is named nonsense on purpose. This fixture carried a
    real private repository's name, pasted from a live run, and a public
    repository then published it in test data -- which is where names arrive,
    because a fixture is copied from output rather than invented. A name no
    repository has cannot be mistaken for a claim about the org.
    """
    parsed = gs.parse_gitmodules(
        '[submodule "wobbly-teapot"]\n\tpath = wobbly-teapot\n'
        "\turl = https://github.com/example-org/wobbly-teapot.git\n"
        '[submodule "docs/qm"]\n\tpath = docs/qm\n'
        "\turl = https://github.com/quaternionmedia/qm.git\n"
    )
    assert parsed == {"corpus_mounted_at": "docs/qm", "branch": None}


def test_a_repository_whose_name_merely_starts_with_qm_is_not_the_corpus():
    """`"/qm" in ".../qmetronome"` is true, and wrong."""
    parsed = gs.parse_gitmodules(
        '[submodule "vendor/qmetronome"]\n\tpath = vendor/qmetronome\n'
        "\turl = https://github.com/quaternionmedia/qmetronome.git\n"
        "\tbranch = main\n"
    )
    assert parsed["corpus_mounted_at"] is None


def test_the_branch_pin_is_read_from_the_corpus_section(corpus):
    parsed = gs.parse_gitmodules(
        '[submodule "other"]\n\tpath = other\n'
        "\turl = https://github.com/x/other.git\n\tbranch = master\n"
        '[submodule "governance/qm"]\n\tpath = governance/qm\n'
        "\turl = https://github.com/quaternionmedia/qm.git\n"
        "\tbranch = project/datum\n"
    )
    assert parsed == {"corpus_mounted_at": "governance/qm", "branch": "project/datum"}


# --------------------------------------------------------------------------
# the emitter, which produces a file people read in diffs
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "value",
    ["yes", "no", "null", "on", "12:30", "0755", "", "a: b", "a #c", 'say "hi"', "-x"],
)
def test_every_awkward_scalar_survives_a_round_trip(value):
    text = gs.dumps({"k": value})
    assert yaml.safe_load(text)["k"] == value


def test_object_ids_are_quoted_consistently():
    """Two shas rendering differently is noise in a file read as a diff."""
    text = gs.dumps({"a": "b94d91085ba728788ede43e7ab4865ecb21c9261",
                     "b": "4541f92df9fc9a3b3b8c04358ec173687c5e35cb"})
    assert text.count('"') == 4


def test_an_unknown_renders_as_a_reason_and_never_as_null():
    text = gs.dumps({"k": gs.Unknown("could not reach it")})
    assert yaml.safe_load(text) == {"k": {"unknown": "could not reach it"}}


def test_the_same_world_twice_produces_the_same_bytes(corpus, tmp_path):
    add_project(corpus, "alpha")
    with_origin(corpus)
    first, second = tmp_path / "a.yaml", tmp_path / "b.yaml"
    for out in (first, second):
        proc = run_tool(
            "governance_status.py", "--offline", "--corpus-ref", "origin/main",
            "--write", str(out), cwd=corpus,
        )
        assert proc.returncode == 0, proc.stderr
    assert first.read_bytes() == second.read_bytes()


def test_the_document_is_written_with_unix_line_endings(corpus, tmp_path):
    add_project(corpus, "alpha")
    out = tmp_path / "doc.yaml"
    run_tool("governance_status.py", "--offline", "--corpus-ref", "main",
             "--write", str(out), cwd=corpus)
    assert b"\r\n" not in out.read_bytes()


# --------------------------------------------------------------------------
# --check: the gate, and the ways a gate passes without checking anything
# --------------------------------------------------------------------------


def written(corpus: Path, out: Path, *extra: str):
    return run_tool(
        "governance_status.py", "--offline", "--corpus-ref", "main",
        "--write", str(out), *extra, cwd=corpus,
    )


def test_check_passes_against_the_commits_the_document_names(corpus, tmp_path):
    add_project(corpus, "alpha")
    out = tmp_path / "doc.yaml"
    written(corpus, out)
    proc = run_tool("governance_status.py", "--corpus-ref", "main", "--check", str(out), cwd=corpus)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "faithfully renders" in proc.stdout


def test_check_fails_on_a_doctored_git_layer_field(corpus, tmp_path):
    add_project(corpus, "alpha")
    advance_corpus(corpus, 4)
    out = tmp_path / "doc.yaml"
    written(corpus, out)
    out.write_text(
        out.read_text(encoding="utf-8").replace("behind_corpus: 4", "behind_corpus: 0"),
        encoding="utf-8", newline="\n",
    )
    proc = run_tool("governance_status.py", "--corpus-ref", "main", "--check", str(out), cwd=corpus)
    assert proc.returncode == 1
    assert "behind_corpus" in proc.stdout


def test_check_still_passes_when_the_corpus_has_moved_on(corpus, tmp_path):
    """The document is a rendering of the commits it names, not of the world.

    Byte-comparing against a fresh generation would go red on every merge to
    main and could never be made green, because the remedy is another merge.
    """
    add_project(corpus, "alpha")
    out = tmp_path / "doc.yaml"
    written(corpus, out)
    advance_corpus(corpus, 5)
    proc = run_tool("governance_status.py", "--corpus-ref", "main", "--check", str(out), cwd=corpus)
    assert proc.returncode == 0, proc.stdout
    assert "5 commit(s) behind" in proc.stdout


def test_check_refuses_a_document_that_names_no_corpus_commit(corpus, tmp_path):
    doc = tmp_path / "empty.yaml"
    doc.write_text("schema: 1\nprojects: []\n", encoding="utf-8", newline="\n")
    proc = run_tool("governance_status.py", "--corpus-ref", "main", "--check", str(doc), cwd=corpus)
    assert proc.returncode == 1
    assert "names no corpus commit" in proc.stdout


def test_check_refuses_to_pass_when_it_could_compare_nothing(corpus, tmp_path):
    """A shallow clone must not produce a clean bill of health.

    The document names a corpus commit this clone does not have, so not one
    field can be re-derived. Reporting "0 of 0 verified" as success is the
    empty-query pass in the gate itself.
    """
    add_project(corpus, "alpha")
    out = tmp_path / "doc.yaml"
    written(corpus, out)
    out.write_text(
        out.read_text(encoding="utf-8").replace(git(corpus, "rev-parse", "main"), "0" * 40),
        encoding="utf-8", newline="\n",
    )
    proc = run_tool("governance_status.py", "--corpus-ref", "main", "--check", str(out), cwd=corpus)
    assert proc.returncode == 1
    assert "Nothing was comparable" in proc.stdout


def test_check_does_not_compare_the_github_layer(corpus, tmp_path):
    """Comparing an observation would assert the world has not moved."""
    add_project(corpus, "alpha")
    out = tmp_path / "doc.yaml"
    written(corpus, out)
    out.write_text(
        out.read_text(encoding="utf-8").replace(
            "not queried: --offline", "something else entirely"
        ),
        encoding="utf-8", newline="\n",
    )
    proc = run_tool("governance_status.py", "--corpus-ref", "main", "--check", str(out), cwd=corpus)
    assert proc.returncode == 0, proc.stdout


def test_no_git_layer_key_is_treated_as_an_observation(corpus):
    """The layer split must not be re-expressible as a name pattern.

    An earlier draft filtered observations out with a regex over key paths, so
    renaming or re-nesting a field silently removed it from the only gate.
    """
    add_project(corpus, "alpha")
    with_origin(corpus)
    g = gs.Git(corpus)
    layer = gs.git_layer(g, "origin/main", "origin")
    hub = gs.Hub("example", enabled=False)
    full = gs.build(g, "origin/main", "origin", hub, False)

    checkable = set(gs.keyed_by_project(layer))
    observed = set(gs.flatten(gs.plain(full))) - set(gs.flatten(gs.plain(
        {"corpus": layer["corpus"], "projects": layer["projects"]}
    )))
    assert checkable and observed
    assert not (checkable & observed)


def test_check_reports_a_commit_this_clone_does_not_have(corpus, tmp_path):
    add_project(corpus, "alpha")
    out = tmp_path / "doc.yaml"
    written(corpus, out)
    out.write_text(
        out.read_text(encoding="utf-8").replace(
            git(corpus, "rev-parse", "project/alpha"), "0" * 40
        ),
        encoding="utf-8", newline="\n",
    )
    proc = run_tool("governance_status.py", "--corpus-ref", "main", "--check", str(out), cwd=corpus)
    assert "not in this clone" in proc.stdout or "missing commits" in proc.stdout


# --------------------------------------------------------------------------
# the document says what it did not compute
# --------------------------------------------------------------------------


def test_the_document_names_the_terms_the_corpus_does_not_define(corpus):
    terms = {g["term"] for g in generate(corpus)["undefined"]}
    assert "adopted" in terms and "current" in terms


def test_no_adopted_boolean_is_emitted_anywhere(corpus):
    """The corpus refuses the compliant/non-compliant axis; so does this."""
    add_project(corpus, "alpha")
    proc = run_tool("governance_status.py", "--offline", "--corpus-ref", "main", cwd=corpus)
    assert "adopted:" not in proc.stdout


def test_every_input_that_changes_the_bytes_is_recorded_in_them(corpus):
    add_project(corpus, "alpha")
    generator = generate(corpus)["generator"]
    for field in ("remote", "org", "credential", "private_repository_names_listed", "probed"):
        assert field in generator


# --- a redacted document, checked ------------------------------------------
#
# Redacting a private repository is what keeps its name out of a public
# document. It also cuts the document loose from the refs it describes: the git
# layer is re-derived from `project/<name>` refs and nothing offline can bind
# `private-32` to one. Both the pin lookup and the field comparison key on that
# name, so a redacted document verified nothing and reported every field as
# changed -- a check failing for a reason unrelated to what it checks.


REDACTED_DOC = {
    "projects": [
        {"name": "datum", "branch": {"ref": "origin/project/datum"}},
        {"name": "private-32", "branch": {"ref": "origin/project/private-32"}},
    ]
}


def test_a_reference_resolves_through_the_companion(monkeypatch):
    monkeypatch.setattr(gs, "reference_map", lambda: {"private-32": "hidden-repo"})
    resolved, unresolved = gs.resolve_references(REDACTED_DOC)
    assert unresolved == []
    assert resolved["projects"][1]["name"] == "hidden-repo"


def test_resolving_reaches_the_ref_inside_the_branch_too(monkeypatch):
    """Renaming only the `name` field left three fields reported as differences."""
    monkeypatch.setattr(gs, "reference_map", lambda: {"private-32": "hidden-repo"})
    resolved, _ = gs.resolve_references(REDACTED_DOC)
    assert resolved["projects"][1]["branch"]["ref"] == "origin/project/hidden-repo"


def test_without_a_companion_the_reference_is_unresolved(monkeypatch):
    """What every runner and every fresh clone sees."""
    monkeypatch.setattr(gs, "reference_map", dict)
    resolved, unresolved = gs.resolve_references(REDACTED_DOC)
    assert unresolved == ["private-32"]
    assert resolved["projects"][1]["name"] == "private-32"


def test_a_public_project_is_untouched_either_way(monkeypatch):
    for mapping in ({"private-32": "hidden-repo"}, {}):
        monkeypatch.setattr(gs, "reference_map", lambda m=mapping: m)
        resolved, _ = gs.resolve_references(REDACTED_DOC)
        assert resolved["projects"][0] == REDACTED_DOC["projects"][0]


def test_a_document_with_no_projects_is_returned_unchanged(monkeypatch):
    monkeypatch.setattr(gs, "reference_map", dict)
    doc = {"projects": gs.Unknown("no refs in this clone")}
    assert gs.resolve_references(doc) == (doc, [])


def test_the_real_document_carries_no_unredacted_private_project():
    """The regression this whole change exists for: the governed-project list
    was unfiltered while the document claimed private names were withheld."""
    document = yaml.safe_load(
        (Path(__file__).resolve().parent.parent.parent / "governance-status.yaml").read_text(encoding="utf-8")
    )
    assert document["generator"]["private_repository_names_listed"] is False
    names = [p["name"] for p in document["projects"] if isinstance(p, dict)]
    assert names, "no projects in the document"
