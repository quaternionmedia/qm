"""Tests for the governance loop tooling.

Like the other suites in this directory: real files in temp directories, no
mocks. The errors these tools could produce — wrong counts, wrong check_exists,
wrong shape matches, uncaught vague outcomes — only manifest through real file
I/O against the actual YAML/JSON parsing path.

Each test is written to FAIL on the thing it names. Several of the assertions
below match failures that were discovered while writing the tools.
"""
from __future__ import annotations

import json
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
import yaml

CI_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(CI_DIR))

import session_record as sr
import pattern_index as pi
import shape_index as si
import check_pattern_coverage as cpc
import counterfactual_query as cq


# ---------------------------------------------------------------------------
# Shared fixtures and helpers
# ---------------------------------------------------------------------------

PATTERN_REGISTRY = {
    "patterns": {
        "exit-code-trap": {
            "clause": "async-contract §8",
            "description": "Exit status shadowed by a filter",
            "threshold": 3,
            "check_exists": False,
        },
        "uv-pip-install-bypass": {
            "clause": "AGENTS.md §12",
            "description": "Dependency installed bypassing uv.lock",
            "threshold": 1,
            "check_exists": False,
        },
        "covered-pattern": {
            "clause": "test §1",
            "description": "A pattern that already has a check",
            "threshold": 1,
            "check_exists": True,
            "check_file": "ci/checks/covered.py",
        },
    }
}

SHAPE_REGISTRY = {
    "shapes": {
        "proxy-for-the-thing": {
            "description": "Reading a proxy instead of the subject",
            "contexts": ["verifying-a-result", "asserting-repository-state"],
        },
        "environment-mutation": {
            "description": "Modifying a shared environment without authorisation",
            "contexts": ["adding-dependency", "starting-a-service"],
        },
    }
}

BREAK_PROXY = {
    "pattern_id": "exit-code-trap",
    "clause": "async-contract §8",
    "caught_by": "manual",
    "path_taken": {
        "action": "run_workflows_locally.py | tail; echo $?",
        "outcome": "tail exit status reported; command failure described as success",
    },
    "path_avoided": {
        "action": "run unpiped; read full output",
        "outcome": "exit code preserved; failure visible immediately",
    },
    "shape": {
        "type": "proxy-for-the-thing",
        "context": "verifying-a-result",
        "reversibility": "high",
        "decision_pressure": "implicit",
    },
    "cost": {"commits": 0, "attention": "medium", "time": "low", "agency": "none"},
}

BREAK_ENV = {
    "pattern_id": "uv-pip-install-bypass",
    "clause": "AGENTS.md §12",
    "caught_by": "reviewer",
    "path_taken": {
        "action": "uv pip install pydantic-ai, bypassing uv.lock",
        "outcome": "starlette 1.6.0; 52 tests broke; false finding on 3 surfaces",
    },
    "path_avoided": {
        "action": "uv sync (correct)",
        "outcome": "pydantic-ai 1.44.0; starlette 0.50.0; 278 passed, 11 skipped",
    },
    "shape": {
        "type": "environment-mutation",
        "context": "adding-dependency",
        "reversibility": "low",
        "decision_pressure": "implicit",
    },
    "cost": {
        "commits": 3,
        "attention": "high",
        "time": "medium",
        "agency": "environment-mutated",
    },
}


@pytest.fixture
def tmp(tmp_path):
    return tmp_path


@pytest.fixture
def reg_dir(tmp):
    (tmp / "pattern-registry.yaml").write_text(
        yaml.dump(PATTERN_REGISTRY, allow_unicode=True), encoding="utf-8"
    )
    (tmp / "shape-registry.yaml").write_text(
        yaml.dump(SHAPE_REGISTRY, allow_unicode=True), encoding="utf-8"
    )
    return tmp


@pytest.fixture
def arts(tmp):
    d = tmp / "artifacts"
    d.mkdir()
    return d


def write_artifact(arts_dir, reg_dir_path, breaks, date="2026-08-13", branch="test"):
    """Build and write an artifact file via session_record helpers."""
    pr = sr.load_registry(reg_dir_path / "pattern-registry.yaml")
    sr_ = sr.load_registry(reg_dir_path / "shape-registry.yaml")
    doc = {"date": date, "branch": branch, "repo": "quaternionmedia/qm", "breaks": breaks}
    artifact = sr.build_artifact(doc, pr, sr_)
    out = arts_dir / f"{date}-{branch}.yaml"
    out.write_text(yaml.dump(artifact, allow_unicode=True, sort_keys=False), encoding="utf-8")
    return out


# ---------------------------------------------------------------------------
# session_record
# ---------------------------------------------------------------------------

class TestSessionRecord:
    def test_valid_break_roundtrips_without_unknowns(self, reg_dir):
        pr = sr.load_registry(reg_dir / "pattern-registry.yaml")
        shr = sr.load_registry(reg_dir / "shape-registry.yaml")
        result = sr.validate_break(BREAK_PROXY, pr, shr)

        assert result["pattern_id"] == "exit-code-trap"
        assert result["caught_by"] == "manual"
        assert result["path_taken"]["action"] == BREAK_PROXY["path_taken"]["action"]
        assert result["shape"]["type"] == "proxy-for-the-thing"
        assert sr.count_unknowns(result) == 0

    def test_unknown_pattern_id_is_flagged_not_silenced(self, reg_dir):
        pr = sr.load_registry(reg_dir / "pattern-registry.yaml")
        shr = sr.load_registry(reg_dir / "shape-registry.yaml")
        b = {**BREAK_PROXY, "pattern_id": "does-not-exist"}
        result = sr.validate_break(b, pr, shr)

        assert sr.is_unknown(result["pattern_id"])
        assert "not in pattern-registry.yaml" in result["pattern_id"]["unknown"]

    def test_vague_avoided_outcome_is_flagged(self, reg_dir):
        # The deflation principle: "no problems" is a claim without evidence.
        pr = sr.load_registry(reg_dir / "pattern-registry.yaml")
        shr = sr.load_registry(reg_dir / "shape-registry.yaml")
        b = {**BREAK_PROXY, "path_avoided": {"action": "uv sync", "outcome": "no problems"}}
        result = sr.validate_break(b, pr, shr)

        assert sr.is_unknown(result["path_avoided"]["outcome"])

    def test_empty_avoided_outcome_is_flagged(self, reg_dir):
        pr = sr.load_registry(reg_dir / "pattern-registry.yaml")
        shr = sr.load_registry(reg_dir / "shape-registry.yaml")
        b = {**BREAK_PROXY, "path_avoided": {"action": "uv sync", "outcome": ""}}
        result = sr.validate_break(b, pr, shr)

        assert sr.is_unknown(result["path_avoided"]["outcome"])

    def test_unknown_shape_type_is_flagged(self, reg_dir):
        pr = sr.load_registry(reg_dir / "pattern-registry.yaml")
        shr = sr.load_registry(reg_dir / "shape-registry.yaml")
        b = {**BREAK_PROXY, "shape": {**BREAK_PROXY["shape"], "type": "not-in-registry"}}
        result = sr.validate_break(b, pr, shr)

        assert sr.is_unknown(result["shape"]["type"])

    def test_invalid_context_for_valid_type_is_flagged(self, reg_dir):
        pr = sr.load_registry(reg_dir / "pattern-registry.yaml")
        shr = sr.load_registry(reg_dir / "shape-registry.yaml")
        b = {**BREAK_PROXY, "shape": {**BREAK_PROXY["shape"], "context": "not-a-valid-context"}}
        result = sr.validate_break(b, pr, shr)

        assert sr.is_unknown(result["shape"]["context"])

    def test_missing_registries_produce_unknowns_not_errors(self, tmp):
        """Absent registries yield unknowns; the tool does not crash."""
        pr = sr.load_registry(tmp / "absent.yaml")
        shr = sr.load_registry(tmp / "also-absent.yaml")
        result = sr.validate_break(BREAK_PROXY, pr, shr)

        assert sr.is_unknown(result["pattern_id"])

    def test_build_artifact_writes_both_breaks(self, reg_dir):
        pr = sr.load_registry(reg_dir / "pattern-registry.yaml")
        shr = sr.load_registry(reg_dir / "shape-registry.yaml")
        doc = {
            "date": "2026-08-13",
            "branch": "test",
            "repo": "qm",
            "breaks": [BREAK_PROXY, BREAK_ENV],
        }
        artifact = sr.build_artifact(doc, pr, shr)

        assert len(artifact["breaks"]) == 2
        assert artifact["date"] == "2026-08-13"

    def test_cli_writes_file(self, reg_dir, tmp):
        input_doc = {
            "date": "2026-08-13",
            "branch": "test",
            "repo": "qm",
            "breaks": [BREAK_PROXY],
        }
        inp = tmp / "input.yaml"
        inp.write_text(yaml.dump(input_doc, allow_unicode=True), encoding="utf-8")
        out = tmp / "output.yaml"

        rc = sr.main([
            "--input", str(inp),
            "--out", str(out),
            "--registry-dir", str(reg_dir),
        ])
        assert rc == 0
        artifact = yaml.safe_load(out.read_text(encoding="utf-8"))
        assert len(artifact["breaks"]) == 1


# ---------------------------------------------------------------------------
# pattern_index
# ---------------------------------------------------------------------------

class TestPatternIndex:
    def test_counts_breaks_by_pattern(self, arts, reg_dir):
        write_artifact(arts, reg_dir, [BREAK_PROXY], "2026-08-12")
        write_artifact(arts, reg_dir, [BREAK_PROXY], "2026-08-13")

        registry = pi.load_registry(reg_dir)
        data = pi.aggregate(pi.load_artifacts(arts), registry)

        assert data["exit-code-trap"]["count"] == 2

    def test_caught_by_distribution_is_accurate(self, arts, reg_dir):
        write_artifact(arts, reg_dir, [BREAK_PROXY], "2026-08-12")
        write_artifact(arts, reg_dir, [{**BREAK_PROXY, "caught_by": "reviewer"}], "2026-08-14")

        data = pi.aggregate(pi.load_artifacts(arts), pi.load_registry(reg_dir))

        assert data["exit-code-trap"]["caught_by"]["manual"] == 1
        assert data["exit-code-trap"]["caught_by"]["reviewer"] == 1

    def test_check_exists_true_when_registry_says_so(self, arts, reg_dir):
        covered = {**BREAK_PROXY, "pattern_id": "covered-pattern"}
        write_artifact(arts, reg_dir, [covered])

        data = pi.aggregate(pi.load_artifacts(arts), pi.load_registry(reg_dir))

        # check_exists: true with a file pointer
        assert data["covered-pattern"]["check_exists"] is True or (
            isinstance(data["covered-pattern"]["check_exists"], dict)
            and "file" in data["covered-pattern"]["check_exists"]
        )

    def test_check_exists_false_when_registry_says_so(self, arts, reg_dir):
        write_artifact(arts, reg_dir, [BREAK_PROXY])

        data = pi.aggregate(pi.load_artifacts(arts), pi.load_registry(reg_dir))

        assert data["exit-code-trap"]["check_exists"] is False

    def test_threshold_read_from_registry(self, arts, reg_dir):
        write_artifact(arts, reg_dir, [BREAK_ENV])

        data = pi.aggregate(pi.load_artifacts(arts), pi.load_registry(reg_dir))

        # uv-pip-install-bypass has threshold: 1 in the registry
        assert data["uv-pip-install-bypass"]["threshold"] == 1

    def test_empty_artifacts_returns_empty_dict(self, arts, reg_dir):
        data = pi.aggregate(pi.load_artifacts(arts), pi.load_registry(reg_dir))
        assert data == {}

    def test_first_and_last_seen_are_correct(self, arts, reg_dir):
        write_artifact(arts, reg_dir, [BREAK_PROXY], "2026-08-10")
        write_artifact(arts, reg_dir, [BREAK_PROXY], "2026-08-13")

        data = pi.aggregate(pi.load_artifacts(arts), pi.load_registry(reg_dir))

        assert data["exit-code-trap"]["first_seen"] == "2026-08-10"
        assert data["exit-code-trap"]["last_seen"] == "2026-08-13"

    def test_write_produces_valid_json(self, arts, reg_dir, tmp):
        write_artifact(arts, reg_dir, [BREAK_PROXY])
        out = tmp / "pattern-index.json"

        rc = pi.main([
            "--artifacts", str(arts),
            "--write", str(out),
            "--registry-dir", str(reg_dir),
        ])
        assert rc == 0
        doc = json.loads(out.read_text(encoding="utf-8"))
        assert "patterns" in doc
        assert "generated_at" in doc


# ---------------------------------------------------------------------------
# shape_index
# ---------------------------------------------------------------------------

class TestShapeIndex:
    def test_groups_by_shape_type_and_context(self, arts, reg_dir):
        write_artifact(arts, reg_dir, [BREAK_PROXY, BREAK_ENV])

        shapes = si.aggregate(si.load_artifacts(arts))

        assert "proxy-for-the-thing/verifying-a-result" in shapes
        assert "environment-mutation/adding-dependency" in shapes

    def test_instances_carry_full_paths(self, arts, reg_dir):
        write_artifact(arts, reg_dir, [BREAK_PROXY])

        shapes = si.aggregate(si.load_artifacts(arts))
        instance = shapes["proxy-for-the-thing/verifying-a-result"]["instances"][0]

        assert "action" in instance["path_taken"]
        assert "action" in instance["path_avoided"]

    def test_worst_cost_points_to_highest_score(self, arts, reg_dir):
        # low cost
        write_artifact(arts, reg_dir, [BREAK_PROXY], "2026-08-12")
        # high cost: 5 commits + high attention + agency taken
        costly = {
            **BREAK_PROXY,
            "cost": {"commits": 5, "attention": "high", "time": "high",
                     "agency": "reviewer-time-spent"},
        }
        write_artifact(arts, reg_dir, [costly], "2026-08-14")

        shapes = si.aggregate(si.load_artifacts(arts))
        entry = shapes["proxy-for-the-thing/verifying-a-result"]

        assert entry["worst_cost_instance"] == "2026-08-14"

    def test_best_catch_points_to_mechanical_check(self, arts, reg_dir):
        write_artifact(arts, reg_dir, [BREAK_PROXY], "2026-08-12")  # caught: manual
        mech = {**BREAK_PROXY, "caught_by": "mechanical-check"}
        write_artifact(arts, reg_dir, [mech], "2026-08-13")

        shapes = si.aggregate(si.load_artifacts(arts))
        entry = shapes["proxy-for-the-thing/verifying-a-result"]

        assert entry["best_catch_instance"] == "2026-08-13"

    def test_count_across_multiple_artifacts(self, arts, reg_dir):
        write_artifact(arts, reg_dir, [BREAK_PROXY, BREAK_PROXY], "2026-08-12")
        write_artifact(arts, reg_dir, [BREAK_PROXY], "2026-08-13")

        shapes = si.aggregate(si.load_artifacts(arts))

        assert shapes["proxy-for-the-thing/verifying-a-result"]["count"] == 3

    def test_write_produces_valid_json(self, arts, reg_dir, tmp):
        write_artifact(arts, reg_dir, [BREAK_PROXY])
        out = tmp / "shape-index.json"

        rc = si.main(["--artifacts", str(arts), "--write", str(out)])
        assert rc == 0
        doc = json.loads(out.read_text(encoding="utf-8"))
        assert "shapes" in doc


# ---------------------------------------------------------------------------
# check_pattern_coverage
# ---------------------------------------------------------------------------

def _stamp(hours_ago: float) -> str:
    return (datetime.now(timezone.utc)
            - timedelta(hours=hours_ago)).strftime("%Y-%m-%dT%H:%M:%SZ")


def fresh() -> str:
    """A stamp well inside the budget, whenever it is read."""
    return _stamp(1)


def stale() -> str:
    """A stamp well outside it. Asked for, never inherited."""
    return _stamp(200)


def _make_pattern_index(path, patterns, generated_at=None):
    """A pattern index that is fresh unless a test says otherwise.

    THE DEFAULT WAS A LITERAL, and the literal was correct on the day it was
    typed: `2026-08-13T12:00:00Z`, against a 168h budget, committed the next
    morning. The fixture needed to mean "recent enough to trust" and the only
    thing on offer was a date, so it said the thirteenth of August. Those two
    sentences agreed for seven days.

    What happened when they stopped disagreeing quietly is the part worth
    keeping. `check_pattern_coverage` short-circuits a stale document to 0 --
    correctly, because a stale document is an absent signal rather than a green
    one -- so on 2026-08-20 the three tests expecting 1 went red and announced
    themselves, and `test_exits_0_when_count_below_threshold` stayed green while
    asserting nothing at all. It expected 0, it got 0, and it never reached the
    coverage logic. The loud failures were the lucky half.

    So the stamp is relative now, and staleness is something a test asks for by
    name. `fresh()` and `stale()` say which property is under test where a date
    said only when it was written.
    """
    doc = {
        "generated_at": generated_at or fresh(),
        "staleness_budget_hours": 168,
        "patterns": patterns,
    }
    path.write_text(json.dumps(doc), encoding="utf-8")


class TestCheckPatternCoverage:
    def test_exits_0_when_all_above_threshold_are_covered(self, tmp):
        idx = tmp / "pi.json"
        _make_pattern_index(idx, {
            "covered-pattern": {
                "count": 5, "threshold": 3,
                "check_exists": True,
                "caught_by": {"reviewer": 0},
            }
        })
        assert cpc.main(["--index", str(idx)]) == 0

    def test_exits_1_when_gap_above_threshold(self, tmp):
        idx = tmp / "pi.json"
        _make_pattern_index(idx, {
            "exit-code-trap": {
                "count": 4, "threshold": 3,
                "check_exists": False,
                "caught_by": {"manual": 4, "reviewer": 0, "mechanical-check": 0},
            }
        })
        assert cpc.main(["--index", str(idx)]) == 1

    def test_exits_0_when_count_below_threshold(self, tmp, capsys):
        idx = tmp / "pi.json"
        _make_pattern_index(idx, {
            "exit-code-trap": {
                "count": 2, "threshold": 3,
                "check_exists": False,
                "caught_by": {},
            }
        })
        assert cpc.main(["--index", str(idx)]) == 0
        # And for the right reason. This exact assertion passed for a week
        # against a stale fixture that never reached the coverage logic: 0 out
        # of the staleness short-circuit is indistinguishable from 0 out of
        # "below threshold" unless something looks at why.
        assert "stale" not in capsys.readouterr().err

    def test_exits_1_when_check_exists_unknown(self, tmp):
        # An unknown is the same as a gap operationally.
        idx = tmp / "pi.json"
        _make_pattern_index(idx, {
            "exit-code-trap": {
                "count": 4, "threshold": 3,
                "check_exists": {"unknown": "not in registry"},
                "caught_by": {},
            }
        })
        assert cpc.main(["--index", str(idx)]) == 1

    def test_exits_2_when_index_absent(self, tmp):
        assert cpc.main(["--index", str(tmp / "absent.json")]) == 2

    def test_a_stale_index_reports_0_and_says_why(self, tmp, capsys):
        """0 here means "could not check", and only stderr says so.

        The gate is right not to fail on staleness -- blocking every pull
        request until somebody regenerates a document would make the document's
        age everybody's problem. But the exit code carries both meanings, so a
        caller reading it alone cannot tell a checked-and-clean run from a run
        that checked nothing. This is the assertion that keeps the difference
        visible in the one place it currently exists.
        """
        idx = tmp / "pi.json"
        _make_pattern_index(idx, {
            "exit-code-trap": {
                "count": 4, "threshold": 3,   # a real gap, deliberately
                "check_exists": False,
                "caught_by": {},
            }
        }, generated_at=stale())

        assert cpc.main(["--index", str(idx)]) == 0
        complaint = capsys.readouterr().err
        assert "stale" in complaint
        assert "not a passing gate" in complaint

    def test_the_same_index_fails_when_it_is_fresh(self, tmp):
        """The control for the test above: the gap is real, the age hid it."""
        idx = tmp / "pi.json"
        _make_pattern_index(idx, {
            "exit-code-trap": {
                "count": 4, "threshold": 3,
                "check_exists": False,
                "caught_by": {},
            }
        }, generated_at=fresh())
        assert cpc.main(["--index", str(idx)]) == 1

    def test_at_threshold_counts_as_above(self, tmp):
        # count == threshold should trigger the gate, not count > threshold
        idx = tmp / "pi.json"
        _make_pattern_index(idx, {
            "exit-code-trap": {
                "count": 3, "threshold": 3,
                "check_exists": False,
                "caught_by": {},
            }
        })
        assert cpc.main(["--index", str(idx)]) == 1

    def test_end_to_end_from_artifacts(self, arts, reg_dir, tmp):
        """Full pipeline: write artifacts → index → gate."""
        # uv-pip-install-bypass has threshold 1 in the real registry, so 1
        # occurrence should trigger the gate.
        write_artifact(arts, reg_dir, [BREAK_ENV])

        idx = tmp / "pi.json"
        pi.main([
            "--artifacts", str(arts),
            "--write", str(idx),
            "--registry-dir", str(reg_dir),
        ])
        assert cpc.main(["--index", str(idx)]) == 1


# ---------------------------------------------------------------------------
# counterfactual_query
# ---------------------------------------------------------------------------

def _make_shape_index(path, shapes):
    doc = {
        "generated_at": "2026-08-13T12:00:00Z",
        "staleness_budget_hours": 168,
        "shapes": shapes,
    }
    path.write_text(json.dumps(doc, indent=2), encoding="utf-8")


ONE_INSTANCE = {
    "date": "2026-08-13",
    "branch": "test",
    "pattern_id": "exit-code-trap",
    "caught_by": "manual",
    "path_taken": {
        "action": "piped command",
        "outcome": "wrong exit code used",
    },
    "path_avoided": {
        "action": "unpiped command",
        "outcome": "correct exit code preserved",
    },
    "cost": {"commits": 0, "attention": "medium", "agency": "none"},
    "source": "2026-08-13-test.yaml",
}


class TestCounterfactualQuery:
    def test_exits_0_for_matching_shape(self, tmp, capsys):
        idx = tmp / "si.json"
        _make_shape_index(idx, {
            "proxy-for-the-thing/verifying-a-result": {
                "type": "proxy-for-the-thing",
                "context": "verifying-a-result",
                "count": 1,
                "worst_cost_instance": "2026-08-13",
                "best_catch_instance": None,
                "instances": [ONE_INSTANCE],
            }
        })
        rc = cq.main(["--type", "proxy-for-the-thing", "--index", str(idx)])
        assert rc == 0
        out = capsys.readouterr().out
        assert "proxy-for-the-thing" in out
        assert "piped command" in out

    def test_context_filter_excludes_non_matching(self, tmp, capsys):
        idx = tmp / "si.json"
        _make_shape_index(idx, {
            "proxy-for-the-thing/verifying-a-result": {
                "type": "proxy-for-the-thing", "context": "verifying-a-result",
                "count": 1, "worst_cost_instance": None, "best_catch_instance": None,
                "instances": [ONE_INSTANCE],
            },
            "proxy-for-the-thing/asserting-repository-state": {
                "type": "proxy-for-the-thing", "context": "asserting-repository-state",
                "count": 1, "worst_cost_instance": None, "best_catch_instance": None,
                "instances": [{**ONE_INSTANCE, "date": "2026-08-14"}],
            },
        })
        cq.main([
            "--type", "proxy-for-the-thing",
            "--context", "verifying-a-result",
            "--index", str(idx),
        ])
        out = capsys.readouterr().out
        assert "verifying-a-result" in out
        assert "asserting-repository-state" not in out

    def test_list_shows_all_shapes(self, tmp, capsys):
        idx = tmp / "si.json"
        _make_shape_index(idx, {
            "proxy-for-the-thing/verifying-a-result": {
                "type": "proxy-for-the-thing", "context": "verifying-a-result",
                "count": 7, "worst_cost_instance": "2026-08-08",
                "best_catch_instance": None, "instances": [],
            }
        })
        rc = cq.main(["--list", "--index", str(idx)])
        assert rc == 0
        out = capsys.readouterr().out
        assert "proxy-for-the-thing" in out
        assert "7" in out

    def test_worst_cost_instance_is_labelled(self, tmp, capsys):
        idx = tmp / "si.json"
        instances = [
            {**ONE_INSTANCE, "date": "2026-08-10",
             "cost": {"commits": 0, "attention": "low", "agency": "none"}},
            {**ONE_INSTANCE, "date": "2026-08-13",
             "cost": {"commits": 5, "attention": "high", "agency": "reviewer-time"}},
        ]
        _make_shape_index(idx, {
            "proxy-for-the-thing/verifying-a-result": {
                "type": "proxy-for-the-thing", "context": "verifying-a-result",
                "count": 2, "worst_cost_instance": "2026-08-13",
                "best_catch_instance": None,
                "instances": instances,
            }
        })
        cq.main(["--type", "proxy-for-the-thing", "--index", str(idx)])
        out = capsys.readouterr().out
        assert "worst cost" in out

    def test_end_to_end_from_real_artifacts(self, arts, reg_dir, tmp):
        """Full pipeline: artifacts → shape_index → query."""
        write_artifact(arts, reg_dir, [BREAK_PROXY])

        idx = tmp / "si.json"
        si.main(["--artifacts", str(arts), "--write", str(idx)])

        rc = cq.main([
            "--type", "proxy-for-the-thing",
            "--context", "verifying-a-result",
            "--index", str(idx),
        ])
        assert rc == 0
