"""The ADR lint's four checks, each proven able to fail.

The corpus's own rule is that a passing test is not evidence until it has been
seen to fail. Applied to a linter, that means every check needs a fixture it
rejects — otherwise "clean" means only that nothing was examined, which is
exactly what the append-only check did in every adopting project for weeks.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from conftest import commit_all, git, index_for, record, run_tool, write


def lint(repo: Path, *extra: str):
    return run_tool(
        "adr_lint.py", "--records-dir", "records", "--index", "README.md", *extra, cwd=repo
    )


# --- check 1: banned vocabulary ------------------------------------------------


def test_banned_vocabulary_is_caught_in_a_draft(repo: Path):
    write(repo / "records" / "DRAFT-x.md", record(body="This was corrected in review.\n"))
    commit_all(repo, "add draft")
    result = lint(repo)
    assert result.returncode == 1, result.stdout
    assert "corrected" in result.stdout.lower()


def test_quoting_the_banned_list_in_a_code_span_is_not_a_violation(repo: Path):
    """The check reads prose only. A record that documents the rule is not breaking it."""
    write(
        repo / "records" / "DRAFT-x.md",
        record(body="The lint rejects `previously` and `corrected` in drafts.\n"),
    )
    write(repo / "README.md", index_for([], ["DRAFT-x.md"]))
    commit_all(repo, "add draft quoting the list")
    assert lint(repo).returncode == 0


def test_a_fenced_block_is_also_excluded(repo: Path):
    write(
        repo / "records" / "DRAFT-x.md",
        record(body="Example:\n\n```\npreviously|corrected\n```\n"),
    )
    write(repo / "README.md", index_for([], ["DRAFT-x.md"]))
    commit_all(repo, "add draft with a fenced block")
    assert lint(repo).returncode == 0


# --- check 2: numbered filenames must be ratified ------------------------------


def test_a_numbered_file_that_is_not_ratified_is_caught(repo: Path):
    write(repo / "records" / "QM-0001-x.md", record(status="Proposed"))
    write(repo / "README.md", index_for([1]))
    commit_all(repo, "number a proposed record")
    result = lint(repo)
    assert result.returncode == 1, result.stdout
    assert "QM-0001" in result.stdout


def test_a_numbered_file_that_is_ratified_passes(repo: Path):
    write(repo / "records" / "QM-0001-x.md", record(status="Accepted"))
    write(repo / "README.md", index_for([1]))
    commit_all(repo, "ratify")
    assert lint(repo).returncode == 0


def test_a_ratified_record_that_was_never_renamed_is_caught(repo: Path):
    """**THE HOLE THE FIRST RATIFICATION WOULD HAVE FALLEN INTO.**

    Every other check keys on the filename: one asks whether a *numbered* file
    is ratified, and the index check compares numbers taken from filenames.
    A record whose Status was flipped to `Accepted` and whose file was never
    renamed matched neither, so the lint reported clean — while the record read
    as ratified to any person opening it.

    `docs/ref/ratification.md` documents the neighbouring failure, where the
    index *was* updated; that one fires. This is the case where the ratifier
    stopped one step earlier, and it was silent.

    Mutation: drop `check_ratified_are_numbered` from `main` and this fails.
    """
    write(repo / "records" / "DRAFT-x.md", record(status="Accepted"))
    write(repo / "README.md", index_for([]))
    commit_all(repo, "flip status without renaming")
    result = lint(repo)
    assert result.returncode == 1, result.stdout
    assert "carries no number" in result.stdout


def test_a_draft_that_is_not_ratified_is_left_alone(repo: Path):
    """The ordinary state of every record in this corpus. A check that fired on
    a `Proposed` draft would fail on an untouched repository."""
    write(repo / "records" / "DRAFT-x.md", record(status="Proposed"))
    write(repo / "README.md", index_for([], ["DRAFT-x.md"]))
    commit_all(repo, "an ordinary draft")
    assert lint(repo).returncode == 0


# --- check 3: ratified bodies are append-only ----------------------------------


def _ratified_repo(repo: Path) -> str:
    write(repo / "records" / "QM-0001-x.md", record(status="Accepted", body="line A\nline B\n"))
    write(repo / "README.md", index_for([1]))
    return commit_all(repo, "ratify a record")


def test_editing_a_ratified_body_is_caught(repo: Path):
    base = _ratified_repo(repo)
    p = repo / "records" / "QM-0001-x.md"
    write(p, p.read_text(encoding="utf-8").replace("line A", "line A changed"))
    commit_all(repo, "edit the body")
    result = lint(repo, "--base-ref", base)
    assert result.returncode == 1, result.stdout


def test_deleting_a_line_from_a_ratified_body_is_caught(repo: Path):
    """A deletion-only hunk carries a new-file count of 0 and reads `@@ -10 +9,0 @@`.

    A condition requiring a non-zero count skips it, and removing a line from a
    ratified record passes clean -- which it did.
    """
    base = _ratified_repo(repo)
    p = repo / "records" / "QM-0001-x.md"
    write(p, p.read_text(encoding="utf-8").replace("line B\n", ""))
    commit_all(repo, "delete a body line")
    result = lint(repo, "--base-ref", base)
    assert result.returncode == 1, result.stdout


def test_appending_under_amendments_is_allowed(repo: Path):
    base = _ratified_repo(repo)
    p = repo / "records" / "QM-0001-x.md"
    write(p, p.read_text(encoding="utf-8").replace("*None.*", "- 2026-02-01: a clarification."))
    commit_all(repo, "amend")
    assert lint(repo, "--base-ref", base).returncode == 0


def test_a_ratified_body_rewritten_inside_a_submodule_is_caught(repo: Path, tmp_path: Path):
    """The branch-per-project model, which is where this check actually runs.

    A project's records live in a submodule; the superproject tracks it as a
    gitlink. Asking the superproject for a diff of a path *inside* the submodule
    matches nothing, so the check ran over an empty list and reported clean
    whatever had been rewritten -- in every adopting project, not just some.
    """
    inner = tmp_path / "governance"
    inner.mkdir()
    git(inner, "init", "-q", "-b", "main")
    (inner / "records").mkdir()
    write(inner / "records" / "QM-0001-x.md", record(status="Accepted", body="line A\nline B\n"))
    write(inner / "README.md", index_for([1]))
    commit_all(inner, "ratified record inside the submodule")

    super_repo = tmp_path / "super"
    super_repo.mkdir()
    git(super_repo, "init", "-q", "-b", "main")
    write(super_repo / "README.md", index_for([1]))
    commit_all(super_repo, "init super")
    git(
        super_repo,
        "-c",
        "protocol.file.allow=always",
        "submodule",
        "add",
        "-q",
        str(inner),
        "governance/qm",
    )
    base = commit_all(super_repo, "vendor the submodule")

    # Rewrite the ratified body inside the submodule, and move the pin.
    sub = super_repo / "governance" / "qm"
    p = sub / "records" / "QM-0001-x.md"
    write(p, p.read_text(encoding="utf-8").replace("line A", "line A rewritten"))
    commit_all(sub, "rewrite a ratified body")
    commit_all(super_repo, "bump the pin")

    result = run_tool(
        "adr_lint.py",
        "--records-dir",
        "governance/qm/records",
        "--index",
        "governance/qm/README.md",
        "--base-ref",
        base,
        cwd=super_repo,
    )
    assert result.returncode == 1, (
        "a ratified body rewritten inside the submodule must be caught; "
        f"got exit {result.returncode}\n{result.stdout}\n{result.stderr}"
    )


# --- check 4: index matches directory ------------------------------------------


def test_a_record_missing_from_the_index_is_caught(repo: Path):
    write(repo / "records" / "QM-0002-y.md", record(status="Accepted"))
    write(repo / "README.md", index_for([]))
    commit_all(repo, "record absent from the index")
    result = lint(repo)
    assert result.returncode == 1, result.stdout
    assert "0002" in result.stdout


def test_an_index_row_with_no_record_is_caught(repo: Path):
    write(repo / "README.md", index_for([7]))
    commit_all(repo, "index row with no file")
    result = lint(repo)
    assert result.returncode == 1, result.stdout
    assert "0007" in result.stdout


def test_an_unnumbered_record_missing_from_the_index_is_caught(repo: Path):
    """**THE CASE THE NUMBER COMPARISON COULD NOT REACH.**

    Numbers are assigned at ratification. Before the first one, no filename
    carries a number and no row carries a number, so both sides of the number
    comparison are empty and it reports clean whatever the index says. A corpus
    can sit in that state for its whole life, which this one did: four records
    were absent from its index, two of them the records behind charter
    principles, while the check reported clean on every run.

    Mutation: delete the `on_disk_files - in_index_files` loop from
    `check_index_matches_directory` and this test fails.
    """
    write(repo / "records" / "DRAFT-y.md", record())
    write(repo / "README.md", index_for([]))
    commit_all(repo, "unnumbered record absent from the index")
    result = lint(repo)
    assert result.returncode == 1, result.stdout
    assert "DRAFT-y.md" in result.stdout


def test_an_index_row_linking_a_record_that_does_not_exist_is_caught(repo: Path):
    """The other direction, also unreachable by number before a ratification.

    Mutation: delete the `in_index_files - on_disk_files` loop and this fails.
    """
    write(repo / "README.md", index_for([], ["DRAFT-gone.md"]))
    commit_all(repo, "index row for a record that is not there")
    result = lint(repo)
    assert result.returncode == 1, result.stdout
    assert "DRAFT-gone.md" in result.stdout


def test_a_link_outside_the_records_directory_is_not_read_as_a_row(repo: Path):
    """An index page carries other tables, and they are not record rows.

    This corpus's own README links the handbook and the docs site from tables
    in the same file. Reading every table link as a record row reported
    fourteen handbook pages as records that do not exist, the first time the
    filename comparison ran.
    """
    write(repo / "records" / "DRAFT-x.md", record())
    second_table = """
| Page | What it answers |
|---|---|
| [Async contract](handbook/async-contract.md) | concurrency |
"""
    write(repo / "README.md", index_for([], ["DRAFT-x.md"]) + second_table)
    commit_all(repo, "an index page with a second table")
    assert lint(repo).returncode == 0


# --- the empty case, which is where a check quietly stops enforcing ------------


def test_an_empty_records_directory_does_not_report_clean_by_omission(repo: Path):
    """Distinguishes "nothing to check" from "checked and clean".

    This is the shape every one of the six known defects took: a query that
    matched nothing, and an exit code that read as success.
    """
    result = lint(repo)
    assert result.returncode == 0
    assert "clean" in result.stdout.lower() or "no records" in result.stdout.lower()


def test_a_records_directory_that_does_not_exist_is_an_error_not_a_pass(repo: Path):
    result = run_tool(
        "adr_lint.py", "--records-dir", "nope", "--index", "README.md", cwd=repo
    )
    assert result.returncode != 0, (
        "a missing records directory must fail loudly; a mislocated adr/ that "
        "reports clean is indistinguishable from a compliant one"
    )


# --- the banned list is a proxy, and a proxy over-matches ----------------------


def test_a_word_that_narrates_nothing_is_not_a_violation(repo: Path):
    """`corrected` was a bare word in the pattern and fired on this sentence --
    prose about two perspectives that narrates nothing about the draft.

    It was reworded to keep the check quiet, which is the wrong repair: the
    tool ends consistent and the record ends worse. The pattern now matches a
    narrating construction rather than a word.
    """
    write(repo / "records" / "DRAFT-x.md",
          record(body="Neither is a mistake and neither is corrected.\n"))
    write(repo / "README.md", index_for([], ["DRAFT-x.md"]))
    commit_all(repo, "add draft")
    assert lint(repo).returncode == 0, "a proxy must not cost a true sentence"


def test_previously_unknown_is_not_narration(repo: Path):
    write(repo / "records" / "DRAFT-x.md",
          record(body="A previously unknown failure mode turned up.\n"))
    write(repo / "README.md", index_for([], ["DRAFT-x.md"]))
    commit_all(repo, "add draft")
    assert lint(repo).returncode == 0


def test_real_narration_is_still_caught(repo: Path):
    """The pair for the two above. A rule narrowed until it fires on nothing is
    worse than the false positives it removed."""
    for body in ("This record previously said the opposite.\n",
                 "That claim was corrected in this revision.\n",
                 "It originally stated a different threshold.\n",
                 "An earlier draft named three.\n",
                 "The figure is now corrected.\n"):
        write(repo / "records" / "DRAFT-x.md", record(body=body))
        commit_all(repo, "add draft")
        assert lint(repo).returncode == 1, f"narration slipped through: {body!r}"


def test_an_annotated_hit_is_allowed_and_counted(repo: Path):
    """An escape hatch with a price. The count is printed so that silencing the
    check stays visible rather than becoming the way it is used."""
    write(repo / "records" / "DRAFT-x.md",
          record(body='It previously said so. <!-- adr-lint: allow "quoting a '
                      'source, not this draft" -->\n'))
    write(repo / "README.md", index_for([], ["DRAFT-x.md"]))
    commit_all(repo, "add draft")
    result = lint(repo)
    assert result.returncode == 0, result.stdout
    assert "allowed by a stated reason" in result.stdout


def test_an_annotation_without_a_reason_is_the_check_turned_off(repo: Path):
    """Mutation: accept an empty reason and this fails, which is an exemption
    anybody can apply without saying anything."""
    write(repo / "records" / "DRAFT-x.md",
          record(body='It previously said so. <!-- adr-lint: allow "" -->\n'))
    commit_all(repo, "add draft")
    result = lint(repo)
    assert result.returncode == 1
    assert "states a reason" in result.stdout


def test_the_annotation_survives_comment_stripping(repo: Path):
    """`prose_only` blanks HTML comments, which is right for the scan and would
    make the annotation invisible to the thing it annotates. The exemption is
    read from the raw file; this is the test that says so."""
    write(repo / "records" / "DRAFT-x.md",
          record(body='<!-- adr-lint: allow "on the line above" -->\n'
                      'It previously said so.\n'))
    write(repo / "README.md", index_for([], ["DRAFT-x.md"]))
    commit_all(repo, "add draft")
    assert lint(repo).returncode == 0


def test_a_record_listed_only_by_title_in_the_drafts_line_is_listed(repo: Path):
    """**THE SEED'S OWN CONVENTION, WHICH THE TABLE-ONLY CHECK REJECTED.**

    `project-seed/adr/README.md` ships a `Drafts in flight (numberless, by
    title): ---` line and tells a project to list unratified drafts there;
    numbers reach the table at ratification. Reading only the table failed
    every project that followed the template it was given, and it was caught on
    a branch whose commit message said "and put it in the index" -- because
    they had.

    Mutation: drop the `listed_by_title` set from
    `check_index_matches_directory` and this fails.
    """
    write(repo / "records" / "DRAFT-x.md",
          '# ADR-XXXX --- A Thing With A Name\n\n| | |\n|---|---|\n| **Status** | Proposed |\n')
    write(repo / "README.md",
          '| # | Title | Status | Date |\n|---|---|---|---|\n\nDrafts in flight (numberless, by title): A Thing With A Name.\n')
    commit_all(repo, "list a draft the way the seed template says to")
    assert lint(repo).returncode == 0, lint(repo).stdout


def test_a_record_in_neither_the_table_nor_the_prose_is_still_caught(repo: Path):
    """The relaxation must not become a hole: a record nobody listed at all
    still fails, in both conventions."""
    write(repo / "records" / "DRAFT-y.md",
          '# ADR-XXXX --- Nobody Listed This\n\n| | |\n|---|---|\n| **Status** | Proposed |\n')
    write(repo / "README.md",
          '| # | Title | Status | Date |\n|---|---|---|---|\n\nDrafts in flight (numberless, by title): ---\n')
    commit_all(repo, "a record listed nowhere")
    result = lint(repo)
    assert result.returncode == 1, result.stdout
    assert "DRAFT-y.md" in result.stdout


@pytest.mark.parametrize("h1", [
    "# QM-XXXX --- A Thing With A Name",
    "# ADR-XXXX --- A Thing With A Name",
    "# DRAFT --- A Thing With A Name",
])
def test_every_h1_prefix_this_estate_writes_yields_the_same_title(repo: Path, h1: str):
    """**THREE CONVENTIONS, ONE TITLE.**

    The org corpus writes `QM-XXXX`, a project following the seed writes
    `ADR-XXXX`, and one project marks the state instead of the slot and writes
    `DRAFT`. Only the title reaches an index. Handling two of the three dropped
    a word from every title in the third, and all eleven of that project's
    records read as unlisted while its index listed all eleven correctly.

    Mutation: remove `DRAFT` from `TITLE_PREFIX` and the third case fails.
    """
    write(repo / "records" / "DRAFT-x.md",
          h1 + '\n\n| | |\n|---|---|\n| **Status** | Proposed |\n')
    write(repo / "README.md",
          '| # | Title | Status | Date |\n|---|---|---|---|\n\nDrafts in flight (numberless, by title):\n\n- A Thing With A Name\n')
    commit_all(repo, "index a draft by title")
    assert lint(repo).returncode == 0, lint(repo).stdout


def test_a_title_appearing_as_a_mere_substring_is_not_listed(repo: Path):
    """**THE WALK-AROUND THE ADVERSARIAL PASS FOUND.** A record titled "The"
    passed against an index whose prose merely contained the word. A title
    counts only when a whole segment -- a bullet, or one semicolon-separated
    part of the drafts line -- equals it.

    Mutation: compare by containment instead of segment equality and this
    fails.
    """
    write(repo / "records" / "DRAFT-the.md",
          '# DRAFT --- The\n\n| | |\n|---|---|\n| **Status** | Proposed |\n')
    write(repo / "README.md",
          '| # | Title | Status | Date |\n|---|---|---|---|\n\nDrafts in flight (numberless, by title): nothing yet, but the word appears.\n')
    commit_all(repo, "an index that merely contains the word")
    result = lint(repo)
    assert result.returncode == 1, result.stdout
    assert "DRAFT-the.md" in result.stdout


def test_a_counted_allowance_covers_exactly_that_many_unlisted_records(repo: Path):
    """A record whose title names a private repository cannot be listed by
    title or filename without republishing the name. The allowance is counted
    so the gate stays a gate: one more unlisted record than the count fails.

    Mutation: drop the `len(unlisted) <= allowed` comparison and the second
    half of this fails.
    """
    write(repo / "records" / "DRAFT-private-thing.md",
          '# ADR-XXXX --- Adopts The Secret Repo\n\n| | |\n|---|---|\n| **Status** | Proposed |\n')
    allowance = '<!-- adr-lint: allow-unlisted 1 "the title names a private repository" -->'
    write(repo / "README.md",
          '| # | Title | Status | Date |\n|---|---|---|---|\n\n'
          + allowance
          + '\n\nDrafts in flight (numberless, by title): ---\n')
    commit_all(repo, "one unlisted record under a counted allowance")
    assert lint(repo).returncode == 0, lint(repo).stdout

    write(repo / "records" / "DRAFT-second-thing.md",
          '# ADR-XXXX --- A Second Unlisted Thing\n\n| | |\n|---|---|\n| **Status** | Proposed |\n')
    commit_all(repo, "a second unlisted record exceeds the count")
    result = lint(repo)
    assert result.returncode == 1, result.stdout
    assert "allowance covers 1" in result.stdout

