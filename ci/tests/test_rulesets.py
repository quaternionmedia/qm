"""What the rulesets say against what the host is running.

NOTHING HERE REACHES A HOST. Every test that involves the host feeds a fake
`subprocess.run`, so the suite answers the same way offline, in CI, and on a
machine with an admin credential — and no test can pass because the repository
happens to be in the state it asserts. That matters more here than usual: the
tool's whole job is to report a gap between two places, and a test that read one
of them live would be measuring the gap it exists to detect.

THE LOAD-BEARING DISTINCTION IS `None` VERSUS `[]`. An empty list is a real
answer — nothing is applied, which is the answer this repository has been giving
since it was created and the reason the tool was written. `None` means the host
could not be asked. Collapsing the two reports an unreachable host as an
unprotected repository, in a tool whose output is the argument for applying a
ruleset.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

CI_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(CI_DIR))

import rulesets  # noqa: E402
from rulesets import applied, compare, drafted, main, render  # noqa: E402


def write(directory: Path, filename: str, payload) -> Path:
    path = directory / filename
    path.write_text(
        payload if isinstance(payload, str) else json.dumps(payload),
        encoding="utf-8",
    )
    return path


def ruleset(name: str = "A - main", enforcement: str = "active", *rules: str) -> dict:
    return {
        "name": name,
        "enforcement": enforcement,
        "rules": [{"type": t} for t in (rules or ("pull_request",))],
    }


def host_ruleset(name: str = "A - main", enforcement: str = "active", ruleset_id: int = 1) -> dict:
    return {"id": ruleset_id, "name": name, "enforcement": enforcement}


class FakeProc:
    def __init__(self, returncode: int = 0, stdout: str = "", stderr: str = ""):
        self.returncode, self.stdout, self.stderr = returncode, stdout, stderr


def fake_gh(monkeypatch, *, listing=None, details=None, returncode: int = 0, raises=None):
    """Answer `gh api` from a fixture, and record every command attempted.

    Returns the call log, so a test can assert what the tool did *not* run as
    well as what it did.
    """
    calls: list[dict] = []
    details = details or {}

    def run(cmd, **kwargs):
        calls.append({"cmd": list(cmd), "kwargs": kwargs})
        if raises is not None:
            raise raises
        if returncode != 0:
            return FakeProc(returncode, "", "gh: Not Found (HTTP 404)")
        target = cmd[2] if len(cmd) > 2 else ""
        if target.endswith("/rulesets"):
            body = listing if isinstance(listing, str) else json.dumps(listing or [])
            return FakeProc(0, body)
        return FakeProc(0, json.dumps(details.get(target.rsplit("/", 1)[-1], {})))

    monkeypatch.setattr(rulesets.subprocess, "run", run)
    return calls


# --- drafted: what is on disk -----------------------------------------------


def test_every_json_file_is_read_and_tagged_with_its_filename(tmp_path):
    write(tmp_path, "A-main.json", ruleset())
    write(tmp_path, "B-project.json", ruleset("B - project branches", "evaluate"))
    found = drafted(tmp_path)
    assert [entry["file"] for entry in found] == ["A-main.json", "B-project.json"]
    assert found[0]["enforcement"] == "active"


def test_an_unparseable_ruleset_is_reported_and_not_dropped(tmp_path):
    """A file that does not parse must not vanish into a shorter list.

    Dropping it would report five drafted where six are on disk, and the count
    is the whole of what a reader checks first.
    """
    write(tmp_path, "A-main.json", "{ not json")
    found = drafted(tmp_path)
    assert len(found) == 1
    assert found[0]["broken"]


def test_a_directory_with_no_rulesets_reads_as_empty(tmp_path):
    assert drafted(tmp_path) == []


# --- applied: None is not [] ------------------------------------------------


def test_nothing_applied_is_an_empty_list_and_a_real_answer(monkeypatch):
    fake_gh(monkeypatch, listing=[])
    result = applied("o/r")
    assert result == []
    assert result is not None


def test_the_host_call_captures_its_output(monkeypatch):
    """Without `capture_output`, `proc.stdout` is `None`.

    `json.loads(proc.stdout or "[]")` then yields `[]` from a call that
    succeeded and read nothing — the same "nothing is applied" this tool exists
    to report, produced by a repository with six rulesets applied. A mutation
    pass survived this until the test existed, because a fake `subprocess.run`
    hides it.
    """
    calls = fake_gh(monkeypatch, listing=[])
    applied("o/r")
    assert calls[0]["kwargs"]["capture_output"] is True
    assert calls[0]["kwargs"]["text"] is True


def test_a_failed_call_is_none_and_never_an_empty_list(monkeypatch):
    fake_gh(monkeypatch, returncode=1)
    assert applied("o/r") is None


def test_an_unrunnable_gh_is_none(monkeypatch):
    fake_gh(monkeypatch, raises=OSError("gh not found"))
    assert applied("o/r") is None


def test_a_timeout_is_none(monkeypatch):
    fake_gh(monkeypatch, raises=subprocess.TimeoutExpired(cmd="gh", timeout=60))
    assert applied("o/r") is None


def test_output_that_is_not_json_is_none(monkeypatch):
    fake_gh(monkeypatch, listing="<html>a proxy login page</html>")
    assert applied("o/r") is None


def test_json_that_is_not_a_list_is_none(monkeypatch):
    """A `{"message": "Not Found"}` body parses. It is not an answer."""
    fake_gh(monkeypatch, listing=json.dumps({"message": "Not Found"}))
    assert applied("o/r") is None


# --- compare: drafted against applied ---------------------------------------


def test_a_ruleset_the_host_does_not_have_is_absent():
    rows = compare([{"file": "A-main.json", **ruleset()}], [], "o/r")
    assert rows[0]["state"] == "absent"
    assert rows[0]["applied"] is None


def test_an_unreachable_host_is_unknown_and_not_absent():
    """`None` in, `unknown` out. Absent would assert something nobody read."""
    rows = compare([{"file": "A-main.json", **ruleset()}], None, "o/r")
    assert rows[0]["state"] == "unknown"


def test_a_matching_ruleset_is_a_match(monkeypatch):
    calls = fake_gh(monkeypatch, details={"1": {"rules": [{"type": "pull_request"}]}})
    rows = compare([{"file": "A-main.json", **ruleset()}], [host_ruleset()], "o/r")
    assert rows[0]["state"] == "match"
    assert rows[0]["differences"] == []
    # The per-ruleset detail call captures its output for the same reason the
    # listing call does: an uncaptured `stdout` is `None`, which parses as no
    # rules and reads as every rule having been stripped.
    assert all(call["kwargs"]["capture_output"] is True for call in calls)


def test_an_enforcement_downgrade_on_the_host_is_drift(monkeypatch):
    """The case this tool exists for: drafted active, applied evaluating.

    Both are present, both are named the same, and the repository is not
    protected. Only the enforcement level says so.
    """
    fake_gh(monkeypatch, details={"1": {"rules": [{"type": "pull_request"}]}})
    rows = compare(
        [{"file": "A-main.json", **ruleset(enforcement="active")}],
        [host_ruleset(enforcement="evaluate")],
        "o/r",
    )
    assert rows[0]["state"] == "drift"
    assert rows[0]["applied"] == "evaluate"
    assert "drafted=active applied=evaluate" in rows[0]["differences"][0]


def test_a_drafted_rule_missing_from_the_host_is_named_in_that_direction(monkeypatch):
    fake_gh(monkeypatch, details={"1": {"rules": [{"type": "pull_request"}]}})
    rows = compare(
        [{"file": "A-main.json", **ruleset("A - main", "active",
                                           "pull_request", "required_status_checks")}],
        [host_ruleset()],
        "o/r",
    )
    assert rows[0]["state"] == "drift"
    assert rows[0]["differences"] == ["rule `required_status_checks` drafted, not applied"]


def test_a_rule_on_the_host_that_nobody_drafted_is_named_in_the_other_direction(monkeypatch):
    """Direction is the finding. Drafted-not-applied is a gap in protection;
    applied-not-drafted is a rule nobody reviewed, and they are not the same."""
    fake_gh(monkeypatch, details={
        "1": {"rules": [{"type": "pull_request"}, {"type": "required_linear_history"}]}
    })
    rows = compare([{"file": "A-main.json", **ruleset()}], [host_ruleset()], "o/r")
    assert rows[0]["differences"] == ["rule `required_linear_history` applied, not drafted"]


def test_a_broken_file_is_broken_and_is_never_compared():
    rows = compare([{"file": "A-main.json", "broken": "line 1 column 3"}], [], "o/r")
    assert rows[0]["state"] == "broken"
    assert rows[0]["differences"] == ["line 1 column 3"]


def test_an_unreadable_detail_call_does_not_read_as_a_removed_rule(monkeypatch):
    """`detail` returns `{}` when the second call fails, and `{}` has no rules.

    Reported as drift, this would tell a reader every rule had been stripped
    from a ruleset that is fine. It is a known limit of the tool rather than a
    passing case — the test pins the behaviour so a change to it is deliberate.
    """
    fake_gh(monkeypatch, details={})
    rows = compare(
        [{"file": "A-main.json", **ruleset("A - main", "active", "pull_request")}],
        [host_ruleset()],
        "o/r",
    )
    assert rows[0]["state"] == "drift"
    assert "drafted, not applied" in rows[0]["differences"][0]


# --- render: the sentence a reader acts on ----------------------------------


def test_an_unasked_host_is_not_rendered_as_an_unprotected_repository():
    text = render(compare([{"file": "A-main.json", **ruleset()}], None, "o/r"), None)
    assert "Could not ask the host" in text
    assert "Nothing is applied" not in text


def test_nothing_applied_says_so_in_the_words_that_matter():
    text = render(compare([{"file": "A-main.json", **ruleset()}], [], "o/r"), [])
    assert "1 drafted, 0 applied" in text
    assert "signal rather than a barrier" in text


def test_the_output_states_what_it_did_not_check():
    """A check says what it checked. This one cannot read rule parameters."""
    text = render(compare([{"file": "A-main.json", **ruleset()}], [], "o/r"), [])
    assert "does not read rule parameters" in text


# --- main: exit status ------------------------------------------------------


def run_main(tmp_path, *args) -> int:
    return main(["--repo", "o/r", "--dir", str(tmp_path), *args])


def test_an_empty_directory_is_refused_rather_than_reported_clean(tmp_path):
    """Six lint globs in this corpus have matched nothing and passed."""
    with pytest.raises(SystemExit):
        run_main(tmp_path)


def test_check_fails_when_the_host_could_not_be_asked(tmp_path, monkeypatch, capsys):
    """Unknown is not clean. Exit zero here would report an unreachable host
    as a verified one, which is the failure mode the whole tool is about."""
    write(tmp_path, "A-main.json", ruleset())
    fake_gh(monkeypatch, returncode=1)
    assert run_main(tmp_path, "--check") == 1
    assert "could not be asked, so nothing was verified" in capsys.readouterr().err


def test_check_fails_when_a_drafted_ruleset_is_not_applied(tmp_path, monkeypatch, capsys):
    write(tmp_path, "A-main.json", ruleset())
    fake_gh(monkeypatch, listing=[])
    assert run_main(tmp_path, "--check") == 1
    # The failure names the count and the command that fixes it. A red check
    # that says only "not applied as drafted" leaves the reader to find the
    # route, and the route is the one thing this tool knows and they may not.
    assert "1 ruleset(s) not applied as drafted" in capsys.readouterr().err


def test_check_passes_only_when_every_ruleset_matches(tmp_path, monkeypatch):
    write(tmp_path, "A-main.json", ruleset())
    fake_gh(monkeypatch, listing=[host_ruleset()],
            details={"1": {"rules": [{"type": "pull_request"}]}})
    assert run_main(tmp_path, "--check") == 0


def test_reporting_without_check_exits_zero_even_when_nothing_is_applied(tmp_path, monkeypatch):
    """The reporting route describes; it does not judge. `qm rulesets` in a
    preflight must not red a session because the host is behind."""
    write(tmp_path, "A-main.json", ruleset())
    fake_gh(monkeypatch, listing=[])
    assert run_main(tmp_path) == 0


# --- the write path is never reached by accident ----------------------------


def test_reading_the_host_never_runs_the_apply_script(tmp_path, monkeypatch):
    """`--apply` changes what every contributor and every concurrent session
    can do. Nothing but that flag may reach it."""
    write(tmp_path, "A-main.json", ruleset())
    calls = fake_gh(monkeypatch, listing=[])
    run_main(tmp_path)
    run_main(tmp_path, "--check")
    assert calls, "the host was never asked at all, so this proves nothing"
    assert all(call["cmd"][0] == "gh" for call in calls)
    assert not any("apply.sh" in " ".join(call["cmd"]) for call in calls)


def test_apply_refuses_when_the_script_is_absent(tmp_path, monkeypatch):
    write(tmp_path, "A-main.json", ruleset())
    monkeypatch.setattr(rulesets, "APPLY", tmp_path / "no-such-apply.sh")
    calls = fake_gh(monkeypatch, listing=[])
    with pytest.raises(SystemExit) as exit_info:
        run_main(tmp_path, "--apply")
    assert "not present; nothing to run" in str(exit_info.value)
    assert calls == []


def test_apply_runs_the_script_and_returns_its_status(tmp_path, monkeypatch):
    write(tmp_path, "A-main.json", ruleset())
    script = write(tmp_path, "apply.sh", "#!/bin/sh\nexit 3\n")
    # ROOT as well as APPLY: the banner prints the script's path relative to
    # the repository root, and a fixture script outside it is not a case the
    # tool has to handle.
    monkeypatch.setattr(rulesets, "ROOT", tmp_path)
    monkeypatch.setattr(rulesets, "APPLY", script)
    calls = fake_gh(monkeypatch)

    def run(cmd, **kwargs):
        calls.append({"cmd": list(cmd), "kwargs": kwargs})
        return FakeProc(3)

    monkeypatch.setattr(rulesets.subprocess, "run", run)
    assert run_main(tmp_path, "--apply") == 3
    assert [call["cmd"] for call in calls] == [["bash", str(script)]]
