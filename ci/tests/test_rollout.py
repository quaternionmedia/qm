"""ci/rollout.py -- the phased push-through, claims apart from evidence.

Every state the tool can print has a test that produces it, and the local
detectors run against real git repositories built in tmp_path: git is the
oracle for "is this file on HEAD", so a fake would test the fake.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import rollout  # noqa: E402


# --- fixtures ------------------------------------------------------------------

def _git(path: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(path), *args], capture_output=True, text=True,
                          check=True).stdout.strip()


def make_repo(root: Path, name: str, files: dict[str, str]) -> Path:
    repo = root / name
    repo.mkdir(parents=True)
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "config", "user.email", "t@example.invalid")
    _git(repo, "config", "user.name", "T")
    _git(repo, "config", "commit.gpgsign", "false")
    for rel, body in files.items():
        p = repo / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(body, encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "seed")
    return repo


STEPS = [
    {"id": "rekeyed",
     "applies_when": {"kind": "path-exists", "path": ".github/workflows/adr-lint.yml"},
     "evidence": {"kind": "file-matches", "path": ".github/workflows/adr-lint.yml",
                  "pattern": r"branches:\s*\[\s*test\s*\]"}},
    {"id": "handoff-noted"},
]


def families_doc(**members) -> dict:
    return {"families": [{"name": k, "drives": "", "members": v} for k, v in members.items()],
            "unstated": []}


class FakeSource:
    """Evidence by table, for the state matrix; the local tests use the real thing."""

    def __init__(self, verdicts: dict[tuple[str, str], rollout.Verdict | None]):
        self.verdicts = verdicts

    def measure(self, evidence, entry):
        # keyed by kind as well as path: a step's gate and its evidence may share a path
        key = (entry["name"], evidence["kind"], evidence["path"])
        if key in self.verdicts:
            return self.verdicts[key]
        if evidence["kind"] == "path-exists":
            return rollout.Verdict("pass", "gate open by default in this fake")
        return rollout.Verdict("unverifiable", "no table entry")


# --- the state matrix ------------------------------------------------------------

@pytest.mark.parametrize("claimed,verdict,expected", [
    (True, rollout.Verdict("pass", ""), "ok"),
    (True, None, "unverified"),
    (True, rollout.Verdict("unverifiable", ""), "unverifiable"),
    (True, rollout.Verdict("fail", ""), "CONTRADICTED"),
    (False, rollout.Verdict("pass", ""), "unclaimed"),
    (False, None, "-"),
    (False, rollout.Verdict("fail", ""), "-"),
    (False, rollout.Verdict("unverifiable", ""), "-"),
])
def test_every_state_comes_from_one_cell_of_the_claim_by_evidence_table(claimed, verdict, expected):
    assert rollout.state_of(claimed, verdict) == expected


def test_a_claim_the_evidence_contradicts_is_a_delta_and_fails_check():
    plan = {"name": "r", "steps": STEPS, "phases": [{"name": "p", "repos": ["a"]}],
            "claims": [{"repo": "a", "step": "rekeyed", "date": "2026-09-19", "by": "T"}]}
    src = FakeSource({("a", "file-matches", ".github/workflows/adr-lint.yml"): rollout.Verdict("fail", "still main")})
    doc = rollout.report(plan, families_doc(), [{"name": "a"}], src)
    row = doc["phases"][0]["members"][0]["steps"]["rekeyed"]
    assert row["state"] == "CONTRADICTED"
    assert "claimed 2026-09-19 by T" in row["detail"]
    assert doc["summary"]["contradicted"] == 1


def test_evidence_without_a_claim_is_reported_as_unclaimed_not_as_done():
    plan = {"name": "r", "steps": STEPS, "phases": [{"name": "p", "repos": ["a"]}], "claims": []}
    src = FakeSource({("a", "file-matches", ".github/workflows/adr-lint.yml"): rollout.Verdict("pass", "on test")})
    doc = rollout.report(plan, families_doc(), [{"name": "a"}], src)
    assert doc["phases"][0]["members"][0]["steps"]["rekeyed"]["state"] == "unclaimed"
    assert doc["phases"][0]["status"] == "current"   # unclaimed is not ok, so not done


def test_a_phase_is_done_only_when_every_step_of_every_member_is_ok():
    plan = {"name": "r", "steps": [STEPS[0]], "phases": [{"name": "p", "repos": ["a", "b"]}],
            "claims": [{"repo": "a", "step": "rekeyed"}, {"repo": "b", "step": "rekeyed"}]}
    passing = rollout.Verdict("pass", "")
    src = FakeSource({("a", "file-matches", ".github/workflows/adr-lint.yml"): passing,
                      ("b", "file-matches", ".github/workflows/adr-lint.yml"): passing})
    doc = rollout.report(plan, families_doc(), [{"name": "a"}, {"name": "b"}], src)
    assert doc["phases"][0]["status"] == "done"
    # one member falls: the phase is current again
    src.verdicts[("b", "file-matches", ".github/workflows/adr-lint.yml")] = rollout.Verdict("fail", "")
    doc = rollout.report(plan, families_doc(), [{"name": "a"}, {"name": "b"}], src)
    assert doc["phases"][0]["status"] == "current"
    assert doc["summary"]["contradicted"] == 1


def test_a_claim_only_step_closes_on_a_persons_word_and_the_phase_counts_it():
    plan = {"name": "r", "steps": [STEPS[1]], "phases": [{"name": "p", "repos": ["a", "b"]}],
            "claims": [{"repo": "a", "step": "handoff-noted"}, {"repo": "b", "step": "handoff-noted"}]}
    doc = rollout.report(plan, families_doc(), [{"name": "a"}, {"name": "b"}], FakeSource({}))
    assert doc["phases"][0]["status"] == "done"
    assert doc["phases"][0]["on_a_persons_word"] == 2
    assert "2 row(s) on a person's word" in rollout.render(doc)
    # take one claim away and the phase is open again, with the next step named
    plan["claims"].pop()
    doc = rollout.report(plan, families_doc(), [{"name": "a"}, {"name": "b"}], FakeSource({}))
    assert doc["phases"][0]["status"] == "current"
    assert doc["phases"][0]["members"][1]["next"] == "handoff-noted"


def test_applies_when_failing_marks_the_step_not_applicable_and_does_not_block_the_phase():
    plan = {"name": "r", "steps": [STEPS[0]], "phases": [{"name": "p", "repos": ["a"]}], "claims": []}
    src = FakeSource({("a", "path-exists", ".github/workflows/adr-lint.yml"): rollout.Verdict("fail", "not there")})
    doc = rollout.report(plan, families_doc(), [{"name": "a"}], src)
    assert doc["phases"][0]["members"][0]["steps"]["rekeyed"]["state"] == "n/a"
    assert doc["phases"][0]["status"] == "done"


# --- the plan resolves, or says why not --------------------------------------------

def test_phases_resolve_families_from_the_document_and_each_repo_belongs_to_its_first_phase():
    plan = {"name": "r", "steps": [], "phases": [
        {"name": "first", "repos": ["qm"]},
        {"name": "core", "families": ["core"], "except": ["qm"]},
    ], "claims": []}
    fam = families_doc(core=["qm", "dossier"])
    phases, problems = rollout.members_of(plan, fam, [{"name": "qm"}, {"name": "dossier"}])
    assert problems == []
    assert [m["name"] for m in phases[0]["members"]] == ["qm"]
    assert [m["name"] for m in phases[1]["members"]] == ["dossier"]


def test_a_repo_named_twice_is_a_problem_not_a_dedupe():
    plan = {"name": "r", "steps": [], "phases": [
        {"name": "first", "repos": ["qm"]}, {"name": "core", "families": ["core"]}], "claims": []}
    _, problems = rollout.members_of(plan, families_doc(core=["qm"]), [{"name": "qm"}])
    assert any("named by phase 'core' and by an earlier phase" in p for p in problems)


def test_an_undeclared_family_and_an_unrostered_repo_are_problems_and_an_empty_phase_too():
    plan = {"name": "r", "steps": [], "phases": [{"name": "p", "families": ["ghosts"], "repos": ["nobody"]}],
            "claims": []}
    _, problems = rollout.members_of(plan, families_doc(), [])
    assert any("family 'ghosts'" in p for p in problems)
    assert any("'nobody', which the roster does not list" in p for p in problems)
    assert any("resolves to no members" in p for p in problems)


def test_private_repositories_are_published_by_ref_never_by_name():
    plan = {"name": "r", "steps": [], "phases": [{"name": "p", "repos": ["private-03"]}], "claims": []}
    doc = rollout.report(plan, families_doc(), [{"ref": "private-03", "name": "secret-real-name"}],
                         FakeSource({}))
    assert doc["phases"][0]["members"][0]["repo"] == "private-03"
    assert "secret-real-name" not in json.dumps(rollout.document(doc, "local"))


def test_a_claim_naming_an_unknown_step_or_an_unplaced_repo_is_a_problem():
    plan = {"name": "r", "steps": [STEPS[1]], "phases": [{"name": "p", "repos": ["a"]}],
            "claims": [{"repo": "a", "step": "nope"}, {"repo": "zzz", "step": "handoff-noted"}]}
    doc = rollout.report(plan, families_doc(), [{"name": "a"}, {"name": "zzz"}], FakeSource({}))
    assert any("names step 'nope'" in p for p in doc["problems"])
    assert any("'zzz'" in p and "no phase names" in p for p in doc["problems"])


def test_a_claim_ahead_of_its_phase_is_reported_not_refused():
    plan = {"name": "r", "steps": [STEPS[1]], "phases": [
        {"name": "now", "repos": ["a"]}, {"name": "later", "repos": ["b"]}],
        "claims": [{"repo": "b", "step": "handoff-noted"}]}
    doc = rollout.report(plan, families_doc(), [{"name": "a"}, {"name": "b"}], FakeSource({}))
    assert doc["ahead_of_phase"] == ["b (later)"]
    assert doc["phases"][1]["members"][0]["steps"]["handoff-noted"]["state"] == "unverified"


# --- local evidence, with git as the oracle -----------------------------------------

def test_local_file_matches_reads_head_not_the_working_tree(tmp_path):
    repo = make_repo(tmp_path, "adopter", {
        ".github/workflows/adr-lint.yml": "on:\n  push:\n    branches: [main]\n"})
    src = rollout.LocalSource(roots=(tmp_path,), corpus=repo)
    entry = {"name": "adopter"}
    ev = {"kind": "file-matches", "path": ".github/workflows/adr-lint.yml", "pattern": r"branches:\s*\[\s*test\s*\]"}
    assert src.measure(ev, entry).state == "fail"
    # edit the working tree only: HEAD is what counts
    (repo / ".github/workflows/adr-lint.yml").write_text("on:\n  push:\n    branches: [test]\n", encoding="utf-8")
    assert src.measure(ev, entry).state == "fail"
    _git(repo, "commit", "-q", "-am", "rekey")
    assert src.measure(ev, entry).state == "pass"


def test_local_path_exists_and_ref_exists(tmp_path):
    repo = make_repo(tmp_path, "adopter", {"AGENTS.md": "x"})
    src = rollout.LocalSource(roots=(tmp_path,), corpus=repo)
    entry = {"name": "adopter"}
    assert src.measure({"kind": "path-exists", "path": "AGENTS.md"}, entry).state == "pass"
    assert src.measure({"kind": "path-exists", "path": "governance/qm"}, entry).state == "fail"
    assert src.measure({"kind": "ref-exists", "branch": "test"}, entry).state == "fail"
    _git(repo, "branch", "test")
    assert src.measure({"kind": "ref-exists", "branch": "test"}, entry).state == "pass"


def test_local_submodule_at_or_past_uses_the_corpus_ancestry(tmp_path):
    corpus = make_repo(tmp_path, "corpus", {"a": "1"})
    old = _git(corpus, "rev-parse", "HEAD")
    (corpus / "a").write_text("2", encoding="utf-8")
    _git(corpus, "commit", "-q", "-am", "two")
    new = _git(corpus, "rev-parse", "HEAD")
    adopter = make_repo(tmp_path, "adopter", {"x": "x"})
    subprocess.run(["git", "-C", str(adopter), "-c", "protocol.file.allow=always", "submodule", "add", "-q",
                    str(corpus), "governance/qm"], check=True, capture_output=True)
    _git(adopter, "commit", "-q", "-m", "pin")
    src = rollout.LocalSource(roots=(tmp_path,), corpus=corpus)
    entry = {"name": "adopter"}
    ev = {"kind": "submodule-at-or-past", "path": "governance/qm", "commit": old}
    assert src.measure(ev, entry).state == "pass"          # pinned at new, which is past old
    ev["commit"] = new
    assert src.measure(ev, entry).state == "pass"          # pinned at new, which is new
    (corpus / "a").write_text("3", encoding="utf-8")
    _git(corpus, "commit", "-q", "-am", "three")
    ev["commit"] = _git(corpus, "rev-parse", "HEAD")
    assert src.measure(ev, entry).state == "fail"          # pinned at new, which is not past three
    ev["commit"] = "0" * 40
    assert src.measure(ev, entry).state != "pass"          # a commit that does not exist never passes
    ev["commit"] = 0                                        # what YAML makes of forty zeros
    assert src.measure(ev, entry).state == "unverifiable"
    ev["commit"] = "set-at-enactment"
    assert src.measure(ev, entry).state == "unverifiable"


def test_a_missing_clone_is_unverifiable_never_a_fail(tmp_path):
    src = rollout.LocalSource(roots=(tmp_path,), corpus=tmp_path)
    v = src.measure({"kind": "path-exists", "path": "AGENTS.md"}, {"name": "absent"})
    assert v.state == "unverifiable"


# --- host evidence, with the runner replaced -------------------------------------------

def test_host_file_matches_decodes_the_contents_api_and_a_404_is_a_fail():
    import base64
    body = base64.b64encode(b"on:\n  push:\n    branches: [test]\n").decode()

    def fake(args):
        endpoint = args[1]
        if endpoint.endswith("/contents/.github/workflows/adr-lint.yml"):
            return 0, json.dumps({"encoding": "base64", "content": body, "type": "file"})
        if endpoint.endswith("/git/ref/heads/test"):
            return 0, "{}"
        return 1, "gh: Not Found (HTTP 404)"

    src = rollout.HostSource(org="o", runner=fake)
    entry = {"name": "adopter"}
    assert src.measure({"kind": "file-matches", "path": ".github/workflows/adr-lint.yml",
                        "pattern": r"branches:\s*\[\s*test\s*\]"}, entry).state == "pass"
    assert src.measure({"kind": "file-matches", "path": ".github/workflows/adr-lint.yml",
                        "pattern": "never"}, entry).state == "fail"
    assert src.measure({"kind": "path-exists", "path": "nope"}, entry).state == "fail"
    assert src.measure({"kind": "ref-exists", "branch": "test"}, entry).state == "pass"
    assert src.measure({"kind": "ref-exists", "branch": "dev"}, entry).state == "fail"


def test_host_cannot_name_a_private_repo_without_the_companion():
    src = rollout.HostSource(org="o", runner=lambda args: (0, "{}"))
    v = src.measure({"kind": "path-exists", "path": "AGENTS.md"}, {"ref": "private-03"})
    assert v.state == "unverifiable"


# --- claims are appended by text, and the file still parses -------------------------------

PLAN_TEXT = """# a comment that must survive
rollouts:
  - name: one
    steps:
      - id: s
    phases:
      - name: p
        repos: [a]
    claims: []
  - name: two
    steps: []
    phases: []
    claims:
      - {repo: z, step: s, date: 2026-01-01, by: Q}
"""


def test_append_claim_keeps_comments_and_order_and_the_file_parses(tmp_path):
    plan = tmp_path / "rollout.yaml"
    plan.write_text(PLAN_TEXT, encoding="utf-8")
    line = rollout.append_claim(plan, "one", "a", "s", "T", "PR #7", on="2026-09-19")
    text = plan.read_text(encoding="utf-8")
    assert text.startswith("# a comment that must survive")
    loaded = yaml.safe_load(text)
    assert loaded["rollouts"][0]["claims"] == [{"repo": "a", "step": "s", "date": "2026-09-19", "by": "T", "note": "PR #7"}]
    assert line.lstrip().startswith("- {repo: a, step: s, date:")
    assert loaded["rollouts"][1]["claims"][0]["repo"] == "z"   # the other rollout is untouched
    # a second claim lands after the first, still parseable
    rollout.append_claim(plan, "one", "b", "s", "T", None, on="2026-09-20")
    loaded = yaml.safe_load(plan.read_text(encoding="utf-8"))
    assert [c["repo"] for c in loaded["rollouts"][0]["claims"]] == ["a", "b"]
    assert "\r" not in plan.read_text(encoding="utf-8")


def test_append_claim_refuses_an_unknown_rollout(tmp_path):
    plan = tmp_path / "rollout.yaml"
    plan.write_text(PLAN_TEXT, encoding="utf-8")
    with pytest.raises(SystemExit):
        rollout.append_claim(plan, "three", "a", "s", "T", None)


# --- the committed plan ----------------------------------------------------------------

def test_the_committed_plan_resolves_against_the_committed_families_and_roster():
    import roster
    plan = rollout.load_plan()
    r = rollout.select_rollout(plan, None)
    phases, problems = rollout.members_of(r, rollout.families_document(), roster.load())
    assert problems == []
    assert sum(len(p["members"]) for p in phases) > 0
    ids = [s["id"] for s in r["steps"]]
    assert len(ids) == len(set(ids)), "step ids must be unique"


def test_the_render_names_every_state_it_prints():
    plan = {"name": "r", "subject": "s", "steps": STEPS, "phases": [{"name": "p", "repos": ["a"]}],
            "claims": [{"repo": "a", "step": "rekeyed"}]}
    src = FakeSource({("a", "file-matches", ".github/workflows/adr-lint.yml"): rollout.Verdict("fail", "")})
    doc = rollout.report(plan, families_doc(), [{"name": "a"}], src)
    text = rollout.render(doc)
    assert "CONTRADICTED" in text and "1 contradicted claim(s)" in text
    assert "decides nothing" in text
