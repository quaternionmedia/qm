"""The ADR lint's four checks, each proven able to fail.

The corpus's own rule is that a passing test is not evidence until it has been
seen to fail. Applied to a linter, that means every check needs a fixture it
rejects — otherwise "clean" means only that nothing was examined, which is
exactly what the append-only check did in every adopting project for weeks.
"""

from __future__ import annotations

from pathlib import Path

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
    commit_all(repo, "add draft quoting the list")
    assert lint(repo).returncode == 0


def test_a_fenced_block_is_also_excluded(repo: Path):
    write(
        repo / "records" / "DRAFT-x.md",
        record(body="Example:\n\n```\npreviously|corrected\n```\n"),
    )
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
    commit_all(repo, "add draft")
    assert lint(repo).returncode == 0, "a proxy must not cost a true sentence"


def test_previously_unknown_is_not_narration(repo: Path):
    write(repo / "records" / "DRAFT-x.md",
          record(body="A previously unknown failure mode turned up.\n"))
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
    commit_all(repo, "add draft")
    assert lint(repo).returncode == 0
