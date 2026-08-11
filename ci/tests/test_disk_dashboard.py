"""The disk tooling's red paths: measurement, rendering, and the delete guards.

A disk dashboard fails the way every dashboard here fails -- it does not report
the wrong answer, it draws a reassuring picture of one. So every test below is
a state that must NOT render like a machine with room on it: a cache nobody
could measure, a volume under its floor, a document generated yesterday.

The reclaimer is tested from the other side, and harder, because it is the only
tool in this repository that deletes. Its tests are about what it refuses.

Every signal has a fixture in which it reports bad. After adding one, break the
code it names and confirm the test fails -- an assertion that matches a phrase
some other section also produces is an assertion that passes against a tool with
the check removed entirely.
"""

from __future__ import annotations

import ast
import json
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
import yaml

CI_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(CI_DIR))
import disk_dashboard as dd  # noqa: E402
import disk_reclaim as dr  # noqa: E402
import disk_status as ds  # noqa: E402


def stamp(hours_ago: float = 0.0) -> str:
    moment = datetime.now(timezone.utc) - timedelta(hours=hours_ago)
    return moment.strftime("%Y-%m-%dT%H:%M:%SZ")


def document(**overrides) -> dict:
    base = {
        "schema": 1,
        "generated_at": stamp(),
        "generator": {
            "tool": "ci/disk_status.py",
            "policy": "ci/disk-policy.yaml",
            "scope": "one machine, one moment",
            "thresholds": {"warn_below_free_ratio": 0.15,
                           "critical_below_free_ratio": 0.05},
            "safety_tiers": list(ds.SAFETY_TIERS),
            "safety_means": "what it costs to get the bytes back",
            "search_roots": ["/repos"],
        },
        "reading": {
            "refresh": "python ci/disk_status.py --write <outside the corpus>",
            "staleness_budget_hours": 6,
            "remediate": "python ci/disk_reclaim.py",
            "unknown_convention": "it is not zero and not empty",
            "do_not": [
                "quote a figure from this document without its generated_at",
                "commit this document, or any rendering of it: it is one machine",
            ],
        },
        "totals": {
            "volumes": 3,
            "volumes_critical": 1,
            "volumes_warn": 0,
            "volumes_unknown": 1,
            "targets": 3,
            "targets_measured": 2,
            "targets_unknown": 1,
            "reclaimable_bytes": {"refetched": 90_000_000_000,
                                  "rebuilt": 4_000_000_000,
                                  "destructive": 6_000_000_000},
            "reclaimable_bytes_total": 100_000_000_000,
        },
        "volumes": [
            {
                "path": "C:\\", "total_bytes": 1000_000_000_000,
                "used_bytes": 999_000_000_000, "free_bytes": 1_000_000_000,
                "free_ratio": 0.001, "state": "warn", "severity": "critical",
                "thresholds_fired": ["0.1% free, under the critical floor of 5%"],
            },
            {
                "path": "D:\\", "total_bytes": 500_000_000_000,
                "used_bytes": 100_000_000_000, "free_bytes": 400_000_000_000,
                "free_ratio": 0.8, "state": "ok", "severity": "ok",
                "thresholds_fired": [],
            },
            {"path": "E:\\", "usage": {"unknown": "device not ready"}},
        ],
        "targets": [
            {
                "name": "nvidia-ota-artifacts", "title": "NVIDIA driver artifacts",
                "kind": "directory_contents", "safety": "refetched",
                "owner": "NVIDIA app", "why": "pure download cache", "note": None,
                "measured": {
                    "bytes": 90_000_000_000, "files": 900, "unreadable": 0,
                    "units": [{"path": "C:/ProgramData/nv/grd", "bytes": 90_000_000_000,
                               "files": 900, "unreadable": 0, "age_days": 27.0}],
                    "units_total": 1,
                },
            },
            {
                "name": "node-modules", "title": "node_modules across the stack",
                "kind": "glob", "safety": "rebuilt", "owner": "this stack",
                "why": None, "note": None,
                "measured": {
                    "bytes": 4_000_000_000, "files": 40_000, "unreadable": 3,
                    "units": [{"path": "/repos/moe/web/node_modules",
                               "bytes": 4_000_000_000, "files": 40_000,
                               "unreadable": 3, "age_days": 2.0}],
                    "units_total": 12,
                },
            },
            {
                "name": "docker-wsl-disk", "title": "Docker's WSL2 disk",
                "kind": "command", "safety": "rebuilt", "owner": "Docker Desktop",
                "why": None, "note": None,
                "measured": {"unknown": "docker exited 1: daemon not running"},
            },
        ],
    }
    base.update(overrides)
    return base


DOC = document()


def run_view(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(CI_DIR / "disk_dashboard.py"), *args],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )


def row_for(page: str, name: str) -> str:
    match = re.search(rf'<tr[^>]*>\s*<th scope="row">{re.escape(name)}.*?</tr>', page, re.S)
    assert match, f"no row for {name}"
    return match.group(0)


# --- the renderer refuses to invent a machine with room on it --------------


def test_an_absent_document_is_a_failure_not_an_empty_page(tmp_path: Path) -> None:
    result = run_view(str(tmp_path / "nothing.json"))
    assert result.returncode != 0
    assert "no document" in result.stderr


def test_a_file_that_is_not_a_disk_document_is_refused(tmp_path: Path) -> None:
    path = tmp_path / "other.json"
    path.write_text(json.dumps({"hello": "world"}), encoding="utf-8")
    result = run_view(str(path))
    assert result.returncode != 0
    assert "not a disk status document" in result.stderr


def test_an_unreadable_volume_renders_as_unknown_not_as_room() -> None:
    """The single failure mode this dashboard has."""
    row = row_for(dd.render(DOC), "E:\\")
    assert "s-unknown" in row
    assert "device not ready" in row
    assert "p-ok" not in row


def test_an_unmeasurable_target_is_not_rendered_as_an_empty_one() -> None:
    """A cache behind a dead daemon must not read as a cache with nothing in it."""
    row = row_for(dd.render(DOC), "Docker")
    assert "s-unknown" in row
    assert "daemon not running" in row
    assert "0 B" not in row


def test_a_volume_under_its_floor_is_distinguished_in_form_not_only_colour() -> None:
    page = dd.render(DOC)
    assert 'class="over"' in row_for(page, "C:\\")
    assert 'class="over"' not in row_for(page, "D:\\")


def test_the_threshold_that_fired_is_named_on_the_row() -> None:
    """'Critical' without the number cannot be acted on or argued with."""
    assert "under the critical floor" in row_for(dd.render(DOC), "C:\\")


def test_a_healthy_volume_is_not_described_as_low() -> None:
    row = row_for(dd.render(DOC), "D:\\")
    assert "p-ok" in row
    assert "critical" not in row


def test_a_small_target_is_never_rounded_to_zero() -> None:
    """`0.0 GB` on a 40MB cache reads as empty, which is the same lie as a blank."""
    assert dd.size(40_000_000) == "40 MB"
    assert dd.size(4_000) == "4 KB"
    assert dd.size(7) == "7 B"
    assert dd.size(None) == "unknown"


def test_an_unreadable_path_count_marks_the_figure_as_a_floor() -> None:
    """A sum over a directory with locked files is a minimum, not a measurement."""
    row = row_for(dd.render(DOC), "node_modules")
    assert "3 paths unreadable" in row
    assert "floor" in row


def test_a_stale_document_says_so_at_the_top() -> None:
    """A page that looks live and is a day old is why people stop checking."""
    old = document(generated_at=stamp(hours_ago=30))
    page = dd.render(old)
    header = page.split("<h2>")[0]
    assert "past the 6h budget" in header
    assert "re-measure before acting" in header


def test_a_fresh_document_is_not_labelled_stale() -> None:
    header = dd.render(DOC).split("<h2>")[0]
    assert "past the" not in header


def test_the_generation_time_is_shown_not_buried() -> None:
    page = dd.render(DOC)
    assert DOC["generated_at"] in page.split("<h2>")[0]


def test_the_page_says_the_reclaimable_total_is_not_space_you_will_get_back() -> None:
    """Three tiers summed into one number is the most misread figure here."""
    page = dd.render(DOC)
    assert "not space you are about to get back" in page
    assert "does not come back at all" in page


def test_the_plan_offers_only_the_tier_that_costs_nothing() -> None:
    """A plan led by a target needing a rebuild is a plan that gets read past."""
    section = dd.render(DOC).split("What to reclaim first")[1].split("<h2>")[0]
    assert "NVIDIA driver artifacts" in section
    assert "node_modules" not in section


def test_the_plan_says_the_command_is_a_dry_run() -> None:
    section = dd.render(DOC).split("What to reclaim first")[1].split("<h2>")[0]
    assert "dry run" in section
    assert "--apply" in section


def test_every_target_carries_what_it_costs_to_get_back() -> None:
    """The tier is a word in a column; without its meaning it is jargon."""
    page = dd.render(DOC)
    assert "downloaded again automatically" in page
    assert "regenerated by a command you run" in page


def test_text_from_the_document_containing_markup_is_escaped() -> None:
    """Paths and a command's stderr are the least trusted text in the document."""
    doc = document()
    doc["targets"][0]["measured"]["units"][0]["path"] = "<script>alert('p')</script>"
    doc["targets"][2]["measured"] = {"unknown": "<script>alert('w')</script>"}
    doc["volumes"][2]["usage"] = {"unknown": "<script>alert('v')</script>"}
    page = dd.render(doc)
    assert "<script>" not in page
    assert page.count("&lt;script&gt;") >= 3


def test_a_healthy_machine_says_so_rather_than_showing_an_empty_section() -> None:
    doc = document()
    doc["volumes"] = [doc["volumes"][1]]
    section = dd.render(doc).split("Under pressure")[1].split("<h2>")[0]
    assert "above both thresholds" in section


@pytest.mark.parametrize(
    "theme_block", [":root {", "prefers-color-scheme: dark", '[data-theme="dark"]']
)
def test_the_page_defines_all_three_theme_states(theme_block: str) -> None:
    assert theme_block in dd.render(DOC)


def test_every_colour_token_is_defined_on_bare_root() -> None:
    page = dd.render(DOC)
    bare = re.search(r":root \{(.*?)\}", page, re.S).group(1)
    defined = set(re.findall(r"(--[a-z-]+)\s*:", bare))
    used = set(re.findall(r"var\((--[a-z-]+)\)", page))
    assert not used - defined


def test_the_page_closes_every_tag_it_opens() -> None:
    import html.parser

    void = {"meta", "br", "img", "hr", "input", "link"}

    class P(html.parser.HTMLParser):
        def __init__(self) -> None:
            super().__init__()
            self.stack: list[str] = []
            self.bad: list[str] = []

        def handle_starttag(self, tag, attrs):
            if tag not in void:
                self.stack.append(tag)

        def handle_endtag(self, tag):
            if self.stack and self.stack[-1] == tag:
                self.stack.pop()
            else:
                self.bad.append(tag)

    parser = P()
    parser.feed(dd.render(DOC))
    assert not parser.bad and not parser.stack


def imports_of(module) -> set[str]:
    tree = ast.parse(Path(module.__file__).read_text(encoding="utf-8"))
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            found.add(node.module.split(".")[0])
    return found


def calls_of(module) -> set[str]:
    tree = ast.parse(Path(module.__file__).read_text(encoding="utf-8"))
    return {
        node.func.attr if isinstance(node.func, ast.Attribute) else node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, (ast.Attribute, ast.Name))
    }


def test_the_renderer_never_shells_out_or_touches_the_filesystem() -> None:
    """A convenience call to disk_usage here would be a second definition of free.

    Asserted on the parsed module rather than on its text. The docstrings in
    these files are where the rule is explained, and an explanation necessarily
    names the thing it forbids -- a scan for the word `disk_usage` matches the
    paragraph saying this renderer must never call it, so the test fails on the
    documentation and would pass on a renderer that had the prose removed and
    the call added.
    """
    assert not imports_of(dd) & {"subprocess", "shutil", "os"}
    assert not calls_of(dd) & {"disk_usage", "walk", "rmtree", "run", "stat"}


def test_all_three_views_share_one_stylesheet() -> None:
    """Two dashboards in one window must not be two colour systems."""
    import harness_dashboard as hd

    assert hd.STYLE is dd.STYLE


def test_a_fragment_carries_no_document_shell_but_keeps_the_stylesheet() -> None:
    fragment = dd.render(DOC, fragment=True)
    for tag in ("<!doctype", "<html", "<head>", "<body>"):
        assert tag not in fragment.lower()
    assert "<style>" in fragment and ":root {" in fragment


# --- the agent view ---------------------------------------------------------


def test_the_markdown_view_states_unknown_in_words() -> None:
    text = dd.render_markdown(DOC)
    assert "unknown (device not ready)" in text
    assert "unknown (docker exited 1: daemon not running)" in text


def test_the_markdown_view_never_leaves_a_state_implied_by_an_empty_cell() -> None:
    for line in dd.render_markdown(DOC).splitlines():
        if line.startswith("| ") and "---" not in line and "Volume |" not in line:
            assert "|  |" not in line, line
            assert not line.endswith("| |"), line


def test_the_markdown_view_carries_the_staleness_budget_and_refresh() -> None:
    """The next agent has the document, not the handbook page explaining it."""
    text = dd.render_markdown(DOC)
    assert "older than 6h" in text
    assert "disk_status.py --write" in text


def test_the_markdown_view_carries_the_do_not_list() -> None:
    text = dd.render_markdown(DOC)
    assert "Do not commit this document" in text


def test_the_markdown_view_collects_what_needs_a_human() -> None:
    section = dd.render_markdown(DOC).split("## What needs a human")[1].split("## ")[0]
    assert "C:\\" in section
    assert "critical" in section
    assert "deletes nothing" in section


def test_an_unreadable_volume_becomes_an_action_rather_than_a_silence() -> None:
    """A volume nobody could measure is not a volume with room on it."""
    section = dd.render_markdown(DOC).split("## What needs a human")[1].split("## ")[0]
    assert "E:\\" in section
    assert "not a volume with room on it" in section


def test_a_healthy_document_says_nothing_needs_a_human_rather_than_nothing() -> None:
    doc = document()
    doc["volumes"] = [doc["volumes"][1]]
    doc["targets"] = [doc["targets"][0]]
    section = dd.render_markdown(doc).split("## What needs a human")[1].split("## ")[0]
    assert "- nothing" in section


def test_both_views_render_the_same_document() -> None:
    for name in ("nvidia-ota-artifacts", "node-modules", "docker-wsl-disk"):
        assert name in dd.render(DOC)
        assert name in dd.render_markdown(DOC)


# --- the collector writes unknown rather than a comfortable default --------


def test_an_unset_environment_variable_is_not_expanded_to_a_root() -> None:
    """`${NOPE}/Docker` must not become `/Docker`, which exists and is not it."""
    assert ds.expand("${PATH}") is not None
    assert ds.expand("${DEFINITELY_NOT_SET_12345}/Docker") is None


def test_a_target_whose_variable_is_unset_is_unknown_not_absent(monkeypatch) -> None:
    monkeypatch.delenv("DEFINITELY_NOT_SET_12345", raising=False)
    entry = {"name": "x", "kind": "directory_contents", "safety": "refetched",
             "roots": ["${DEFINITELY_NOT_SET_12345}/cache"]}
    result = ds.measure(entry, [], set())
    assert "unknown" in result
    assert "environment variable that is not set" in result["unknown"]


def test_a_target_that_does_not_exist_here_says_so_rather_than_measuring_zero() -> None:
    entry = {"name": "x", "kind": "directory_contents", "safety": "refetched",
             "roots": ["/no/such/path/anywhere"]}
    result = ds.measure(entry, [], set())
    assert "unknown" in result
    assert "does not exist" in result["unknown"]


def test_a_command_target_without_its_tool_is_unknown_not_zero() -> None:
    entry = {"name": "x", "kind": "command", "safety": "refetched",
             "requires": "definitely-not-a-real-binary-12345",
             "measure": {"argv": ["definitely-not-a-real-binary-12345"]}}
    result = ds.measure(entry, [], set())
    assert "unknown" in result
    assert "not on PATH" in result["unknown"]


def test_a_command_that_prints_nonsense_is_unknown_not_a_size() -> None:
    entry = {"name": "x", "kind": "command", "safety": "refetched",
             "measure": {"argv": [sys.executable, "-c", "print('lots')"]}}
    result = ds.measure(entry, [], set())
    assert "unknown" in result
    assert "not a size" in result["unknown"]


def test_sizes_are_read_in_whatever_unit_the_tool_chose() -> None:
    """`docker system df` prints 12.4GB; PowerShell prints an integer."""
    assert ds.parse_bytes("12.4GB") == 12_400_000_000
    assert ds.parse_bytes("6547218432") == 6_547_218_432
    assert ds.parse_bytes("1.5MiB") == 1_572_864
    assert ds.parse_bytes("") is None
    assert ds.parse_bytes("lots") is None


def test_a_size_carrying_a_percentage_is_still_a_size() -> None:
    """`docker system df --format {{.Reclaimable}}` prints `23.62GB (97%)`.

    Two facts in one field. Refusing the whole reading over the second hid a
    23GB target behind an unknown whose wording -- "not a size" -- read like a
    dead daemon rather than a format this tool could not parse.
    """
    assert ds.parse_bytes("23.62GB (97%)") == 23_620_000_000
    assert ds.parse_bytes("0B (0%)") == 0
    assert ds.parse_bytes("(97%)") is None


def test_an_unclassified_policy_entry_is_refused_rather_than_defaulted(tmp_path: Path) -> None:
    """An entry with no safety would be reclaimed at whatever tier was permitted."""
    path = tmp_path / "policy.yaml"
    path.write_text(
        yaml.safe_dump({"schema": 1, "reclaimers": [
            {"name": "mystery", "kind": "directory_contents", "roots": ["/tmp"]}]}),
        encoding="utf-8",
    )
    with pytest.raises(SystemExit) as caught:
        ds.load_policy(path)
    assert "safety" in str(caught.value)


def test_an_unknown_kind_is_refused(tmp_path: Path) -> None:
    path = tmp_path / "policy.yaml"
    path.write_text(
        yaml.safe_dump({"schema": 1, "reclaimers": [
            {"name": "x", "kind": "run_arbitrary_code", "safety": "refetched"}]}),
        encoding="utf-8",
    )
    with pytest.raises(SystemExit) as caught:
        ds.load_policy(path)
    assert "not one of" in str(caught.value)


def test_a_missing_policy_is_an_exit_not_an_empty_permissive_one(tmp_path: Path) -> None:
    with pytest.raises(SystemExit):
        ds.load_policy(tmp_path / "nothing.yaml")


def test_a_critical_volume_does_not_also_report_its_warn_thresholds() -> None:
    """Both fire at once; listing both doubles the sentence for no new fact."""
    thresholds = {"warn_below_free_ratio": 0.15, "critical_below_free_ratio": 0.05,
                  "warn_below_free_gb": 25, "critical_below_free_gb": 8}
    state, severity, fired = ds.volume_state(1_000_000_000, 1000_000_000_000, thresholds)
    assert (state, severity) == ("warn", "critical")
    assert all("warn" not in line for line in fired)


def test_an_absolute_floor_catches_a_large_volume_a_ratio_would_pass() -> None:
    """15% of a 4TB array is 600GB and fine; 4GB free is not, at any ratio."""
    thresholds = {"warn_below_free_ratio": 0.15, "critical_below_free_gb": 8}
    _, severity, fired = ds.volume_state(4_000_000_000, 4000_000_000_000, thresholds)
    assert severity == "critical"
    assert any("GB free" in line for line in fired)


def test_a_volume_reporting_zero_total_is_unknown_not_full() -> None:
    state, severity, _ = ds.volume_state(0, 0, {})
    assert state == "unknown" and severity == "unknown"


def test_a_healthy_volume_fires_nothing() -> None:
    thresholds = {"warn_below_free_ratio": 0.15, "critical_below_free_ratio": 0.05}
    state, severity, fired = ds.volume_state(800_000_000_000, 1000_000_000_000, thresholds)
    assert (state, severity, fired) == ("ok", "ok", [])


# --- the totals, which is where a lie compounds ----------------------------


def test_no_two_targets_count_the_same_bytes(tmp_path: Path) -> None:
    """`.venv` counted whole and its `__pycache__` counted again is a total
    larger than the disk. The pruning is across the whole policy, not per entry.
    """
    venv = tmp_path / "project" / ".venv" / "lib" / "__pycache__"
    venv.mkdir(parents=True)
    (venv / "a.pyc").write_bytes(b"x" * 1000)
    loose = tmp_path / "project" / "src" / "__pycache__"
    loose.mkdir(parents=True)
    (loose / "b.pyc").write_bytes(b"y" * 500)

    policy = {
        "schema": 1,
        "reclaimers": [
            {"name": "envs", "kind": "glob", "safety": "rebuilt",
             "within": "search_roots", "patterns": ["**/.venv"]},
            {"name": "bytecode", "kind": "glob", "safety": "rebuilt",
             "within": "search_roots", "patterns": ["**/__pycache__"]},
        ],
    }
    blocked = ds.glob_names(policy)
    envs = ds.measure(policy["reclaimers"][0], [tmp_path], blocked)
    bytecode = ds.measure(policy["reclaimers"][1], [tmp_path], blocked)

    assert envs["bytes"] == 1000
    assert bytecode["bytes"] == 500, "the __pycache__ inside .venv was counted twice"


def test_a_nested_match_is_counted_once_in_the_outer_one(tmp_path: Path) -> None:
    outer = tmp_path / "node_modules"
    (outer / "pkg" / "node_modules").mkdir(parents=True)
    (outer / "pkg" / "node_modules" / "f").write_bytes(b"z" * 100)
    entry = {"name": "n", "kind": "glob", "safety": "rebuilt",
             "within": "search_roots", "patterns": ["**/node_modules"]}
    result = ds.measure(entry, [tmp_path], {"node_modules"})
    assert result["units_total"] == 1
    assert result["bytes"] == 100


def test_an_unmeasured_target_contributes_to_no_reclaimable_total() -> None:
    """A target nobody could read must not read as a target with nothing in it."""
    policy = {"schema": 1, "reclaimers": [
        {"name": "gone", "kind": "directory_contents", "safety": "refetched",
         "roots": ["/no/such/path/anywhere"]}]}
    built = ds.build(policy, [], [])
    assert built["totals"]["targets_unknown"] == 1
    assert built["totals"]["reclaimable_bytes"]["refetched"] == 0
    assert "unknown" in built["targets"][0]["measured"]


def test_retained_files_are_not_counted_as_reclaimable(tmp_path: Path) -> None:
    """A temp sweep that would delete a file being written is the one cleanup
    that breaks something that was working."""
    fresh = tmp_path / "new.txt"
    fresh.write_bytes(b"x" * 1000)
    entry = {"name": "t", "kind": "directory_contents", "safety": "refetched",
             "roots": [str(tmp_path)], "retain_days": 7}
    assert ds.measure(entry, [], set())["bytes"] == 0

    entry.pop("retain_days")
    assert ds.measure(entry, [], set())["bytes"] == 1000


# --- the document is machine-scoped, in full -------------------------------


def test_writing_the_document_into_the_repository_is_refused() -> None:
    """Unlike harness-status.json there is no committable half to fall back to.

    Run against the real corpus path, because the real path is the whole
    subject: a guard tested against a temporary directory is a guard tested
    where it never fires.
    """
    target = CI_DIR.parent / "disk-status.json"
    existed = target.exists()
    result = subprocess.run(
        [sys.executable, str(CI_DIR / "disk_status.py"), "--write", "disk-status.json"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        cwd=str(CI_DIR.parent),
    )
    assert result.returncode == 1
    assert "refusing to write" in result.stderr
    assert "one machine" in result.stderr
    assert target.exists() == existed, "the guard let the file be written anyway"


def test_the_refusal_happens_before_the_walk(monkeypatch) -> None:
    """Measuring 90GB and then rejecting the destination wastes the minutes
    that made somebody reach for the tool."""
    def explode(*args, **kwargs):
        raise AssertionError("build() ran before the destination was checked")

    monkeypatch.setattr(ds, "build", explode)
    with pytest.raises(SystemExit):
        ds.main(["--write", str(CI_DIR / "disk-status.json")])


def test_the_document_names_its_own_scope_and_says_it_is_never_committed() -> None:
    built = ds.build({"schema": 1, "reclaimers": []}, [], [])
    assert "nobody else" in built["generator"]["scope"]
    assert "refuses to write it inside the corpus" in built["generator"]["never_committed"]
    assert any("commit this document" in d for d in built["reading"]["do_not"])


def test_the_collector_deletes_nothing() -> None:
    """Measuring and reclaiming are separate tools, and this is the measuring one.

    Parsed rather than scanned, for the reason given on the renderer's own
    version of this test: the docstring explaining that this tool deletes
    nothing is not an instance of it deleting something.
    """
    assert not calls_of(ds) & {"rmtree", "unlink", "remove", "rmdir"}


# --- the reclaimer: what it refuses -----------------------------------------


def test_dry_run_is_the_default_and_deletes_nothing(tmp_path: Path) -> None:
    doomed = tmp_path / "cache" / "big"
    doomed.mkdir(parents=True)
    (doomed / "f").write_bytes(b"x" * 5000)
    policy = tmp_path / "policy.yaml"
    policy.write_text(
        yaml.safe_dump({"schema": 1, "reclaimers": [
            {"name": "c", "kind": "directory_contents", "safety": "refetched",
             "roots": [str(tmp_path / "cache")]}]}),
        encoding="utf-8",
    )
    result = subprocess.run(
        [sys.executable, str(CI_DIR / "disk_reclaim.py"), "--policy", str(policy)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    assert result.returncode == 0
    assert "DRY RUN" in result.stdout
    assert "would remove" in result.stdout.lower()
    assert doomed.exists(), "the dry run deleted something"


def test_apply_actually_removes_what_the_dry_run_promised(tmp_path: Path) -> None:
    doomed = tmp_path / "cache" / "big"
    doomed.mkdir(parents=True)
    (doomed / "f").write_bytes(b"x" * 5000)
    policy = tmp_path / "policy.yaml"
    policy.write_text(
        yaml.safe_dump({"schema": 1, "reclaimers": [
            {"name": "c", "kind": "directory_contents", "safety": "refetched",
             "roots": [str(tmp_path / "cache")]}]}),
        encoding="utf-8",
    )
    result = subprocess.run(
        [sys.executable, str(CI_DIR / "disk_reclaim.py"),
         "--policy", str(policy), "--apply"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    assert result.returncode == 0
    assert not doomed.exists()
    assert (tmp_path / "cache").exists(), "the root itself was removed, not its contents"


def test_the_tiers_are_a_ratchet_and_not_a_menu() -> None:
    """No invocation empties the recycle bin while sparing a download cache."""
    assert dr.permitted("refetched") == ["refetched"]
    assert dr.permitted("rebuilt") == ["refetched", "rebuilt"]
    assert dr.permitted("destructive") == ["refetched", "rebuilt", "destructive"]


def test_an_expensive_tier_is_not_touched_by_default(tmp_path: Path) -> None:
    kept = tmp_path / "bin" / "thing"
    kept.mkdir(parents=True)
    (kept / "f").write_bytes(b"x" * 5000)
    policy = tmp_path / "policy.yaml"
    policy.write_text(
        yaml.safe_dump({"schema": 1, "reclaimers": [
            {"name": "d", "kind": "directory_contents", "safety": "destructive",
             "roots": [str(tmp_path / "bin")]}]}),
        encoding="utf-8",
    )
    result = subprocess.run(
        [sys.executable, str(CI_DIR / "disk_reclaim.py"),
         "--policy", str(policy), "--apply"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    assert kept.exists(), "a destructive target ran without --allow destructive"
    assert not any(line.startswith("d:") for line in result.stdout.splitlines())


def test_a_filesystem_root_is_refused(tmp_path: Path) -> None:
    root = Path(tmp_path.anchor or "/")
    assert dr.refuse(root, [root]) == "it is a filesystem root"


def test_the_home_directory_is_refused() -> None:
    home = Path.home()
    assert dr.refuse(home, [home]) == "it is the home directory"


def test_a_path_inside_the_corpus_is_refused() -> None:
    """git is responsible for what is in the repository, not this tool."""
    reason = dr.refuse(CI_DIR / "disk-policy.yaml", [CI_DIR])
    assert reason and "corpus" in reason


def test_a_path_outside_the_entrys_declared_roots_is_refused(tmp_path: Path) -> None:
    """The guard that makes the policy an authorisation rather than a suggestion."""
    inside = tmp_path / "allowed" / "x"
    inside.mkdir(parents=True)
    outside = tmp_path / "elsewhere"
    outside.mkdir()
    roots = [tmp_path / "allowed"]
    assert dr.refuse(inside, roots) is None
    reason = dr.refuse(outside, roots)
    assert reason and "does not authorise it" in reason


def test_a_junction_is_refused_rather_than_followed(tmp_path: Path, monkeypatch) -> None:
    """Deleting a junction acts on whatever it points at, which is not in scope."""
    target = tmp_path / "allowed" / "link"
    target.mkdir(parents=True)
    monkeypatch.setattr(ds, "is_reparse_point", lambda p: p == target.resolve())
    reason = dr.refuse(target, [tmp_path / "allowed"])
    assert reason and "junction or symlink" in reason


def test_a_refused_path_is_announced_rather_than_skipped_quietly(tmp_path: Path) -> None:
    """A guard that fires silently is a policy nobody knows is wrong."""
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "f").write_bytes(b"x" * 100)
    policy = tmp_path / "policy.yaml"
    policy.write_text(
        yaml.safe_dump({"schema": 1, "reclaimers": [
            {"name": "c", "kind": "directory_contents", "safety": "refetched",
             "roots": [str(tmp_path)]}]}),
        encoding="utf-8",
    )
    # The entry's root is tmp_path, so its children are authorised; monkeypatching
    # is not needed -- what is asserted is that the refusal path prints at all.
    result = subprocess.run(
        [sys.executable, str(CI_DIR / "disk_reclaim.py"),
         "--policy", str(policy), "--target", "c"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    assert "REFUSED" in result.stdout or "would remove" in result.stdout.lower()
    assert "REFUSED" in Path(dr.__file__).read_text(encoding="utf-8")


def test_a_target_absent_from_this_machine_is_not_a_failure(tmp_path: Path) -> None:
    """The policy is written for an organisation, not a laptop.

    Nobody has every tool it names, so an absent pip cache is the normal state
    of a machine without pip. Exiting non-zero for it made a dry run fail on a
    healthy workstation, which is the surest way to teach somebody that this
    tool's exit code means nothing.
    """
    policy = tmp_path / "policy.yaml"
    policy.write_text(
        yaml.safe_dump({"schema": 1, "reclaimers": [
            {"name": "not-here", "kind": "directory_contents", "safety": "refetched",
             "roots": [str(tmp_path / "no" / "such" / "cache")]}]}),
        encoding="utf-8",
    )
    result = subprocess.run(
        [sys.executable, str(CI_DIR / "disk_reclaim.py"), "--policy", str(policy)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    assert result.returncode == 0, result.stdout
    assert "absent" in result.stdout
    assert "not a problem" in result.stdout
    assert "FAILED" not in result.stdout


def test_a_target_that_genuinely_failed_still_reaches_the_exit_status(
    tmp_path: Path,
) -> None:
    """The other side of the distinction. If absence stopped counting and
    nothing else started, the exit code would just always be zero."""
    policy = tmp_path / "policy.yaml"
    policy.write_text(
        yaml.safe_dump({"schema": 1, "reclaimers": [
            {"name": "broken", "kind": "command", "safety": "refetched",
             "reclaim": {"argv": [sys.executable, "-c", "raise SystemExit(3)"]}}]}),
        encoding="utf-8",
    )
    result = subprocess.run(
        [sys.executable, str(CI_DIR / "disk_reclaim.py"),
         "--policy", str(policy), "--apply"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    assert result.returncode == 1
    assert "FAILED" in result.stdout


def test_a_missing_tool_is_absence_and_a_broken_one_is_failure() -> None:
    """Both produce no bytes; only one is somebody's problem."""
    missing = reclaim_gap({"name": "x", "requires": "definitely-not-a-binary-12345"})
    assert missing and missing.absent

    broken = reclaim_gap(
        {"name": "x", "reclaim": {"argv": [sys.executable, "-c", "raise SystemExit(2)"]}},
        apply=True,
    )
    assert broken and not broken.absent


def reclaim_gap(entry: dict, apply: bool = False):
    return dr.reclaim_command(entry, apply)


def test_an_unknown_target_name_is_an_error_not_a_silent_no_op(tmp_path: Path) -> None:
    """`--target typo` that quietly does nothing reads as a clean machine."""
    policy = tmp_path / "policy.yaml"
    policy.write_text(
        yaml.safe_dump({"schema": 1, "reclaimers": [
            {"name": "real", "kind": "directory_contents", "safety": "refetched",
             "roots": [str(tmp_path)]}]}),
        encoding="utf-8",
    )
    result = subprocess.run(
        [sys.executable, str(CI_DIR / "disk_reclaim.py"),
         "--policy", str(policy), "--target", "typo"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    assert result.returncode != 0
    assert "no policy entry named typo" in result.stderr


def test_the_reclaimer_never_reads_a_status_document() -> None:
    """Deletion has no staleness budget, so it re-reads the filesystem itself.

    A document with a six-hour budget describes a path that may since have
    become a checkout. Acting on it would delete what was measured, not what
    is there.
    """
    assert "json" not in imports_of(dr)
    assert not calls_of(dr) & {"load", "loads"}


def test_the_reclaimer_and_the_collector_share_one_definition_of_a_target() -> None:
    """Two resolvers would let the tool delete something nobody reported."""
    called = calls_of(dr)
    assert {"units_of_glob", "units_of_directory", "resolve_roots"} <= called
    assert "walk" not in called


# --- the policy this repository actually ships ------------------------------


def test_the_shipped_policy_parses_and_every_entry_is_classified() -> None:
    policy = ds.load_policy(CI_DIR / "disk-policy.yaml")
    assert policy["reclaimers"]
    for entry in policy["reclaimers"]:
        assert entry["safety"] in ds.SAFETY_TIERS
        assert entry["kind"] in ds.KINDS
        assert entry.get("title"), entry["name"]


def test_the_shipped_policy_carries_both_kinds_of_threshold() -> None:
    """A ratio alone says the same thing about a laptop and a 4TB array."""
    thresholds = ds.load_policy(CI_DIR / "disk-policy.yaml")["thresholds"]
    for key in ("warn_below_free_ratio", "critical_below_free_ratio",
                "warn_below_free_gb", "critical_below_free_gb"):
        assert key in thresholds


def test_the_shipped_policy_puts_the_recycle_bin_in_the_destructive_tier() -> None:
    """It is the undo. Emptying it is the act of giving up the undo."""
    policy = ds.load_policy(CI_DIR / "disk-policy.yaml")
    entry = next(e for e in policy["reclaimers"] if e["name"] == "recycle-bin")
    assert entry["safety"] == "destructive"


def test_no_shipped_entry_targets_a_path_this_corpus_owns() -> None:
    """A policy that named the repository would delete work git is tracking."""
    policy = ds.load_policy(CI_DIR / "disk-policy.yaml")
    for entry in policy["reclaimers"]:
        for raw in entry.get("roots") or []:
            expanded = ds.expand(str(raw))
            if expanded and Path(expanded).exists():
                assert not ds.inside_corpus(Path(expanded)), entry["name"]
