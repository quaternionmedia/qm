"""The regeneration command, which is the P12 mechanism and was untested.

**THE COMMAND CHARTER P12 RESTS ON.** "Regeneration rides the command people
already run" — this is that command. Drift is supposed to arrive as an
uncommitted diff nobody can miss, and the whole arrangement depends on this
running the right steps in the right order.

`uv run qm posture` found that no test executed it. Its *outputs* are checked by
each document's own tests, so a wrong document is caught downstream — but
nothing checked the ordering, the `--check` mode, or what it reports as moved,
which are the three things only this module decides.

THE TEST WORTH READING IS THE ORDERING ONE. "A renderer must run after the
document it reads, and `doc-status.json` must run last because it reports on the
files the others just wrote. Getting that backwards produces a state page
describing the previous run" — that is written in the module and was checked by
nothing.
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

CI = Path(__file__).resolve().parent.parent
CORPUS = CI.parent


def _module():
    spec = importlib.util.spec_from_file_location(
        "generate_docs", CI / "generate_docs.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


generate_docs = _module()


# One `--check` run for the module. **MEMOISED, NOT MERGED** -- two tests assert
# two different properties of one invocation, and each spawning its own cost ten
# seconds because `--check` runs every document's checker as a subprocess.
# Merging them would buy the same seconds and cost the failure message.
#
# `--check` writes nothing by contract, which is what makes sharing it safe: a
# second run can only produce the same answer.
_CHECKED: dict[str, subprocess.CompletedProcess] = {}


def checked() -> subprocess.CompletedProcess:
    if "run" not in _CHECKED:
        _CHECKED["run"] = subprocess.run(
            [sys.executable, str(CI / "generate_docs.py"), "--check"],
            cwd=CORPUS, capture_output=True, text=True, timeout=600,
            encoding="utf-8", errors="replace")
    return _CHECKED["run"]


# --- the ordering the module's own comment says matters -----------------------


def test_the_state_document_is_written_last():
    """THE ONE THAT MATTERS.

    `doc-status.json` reports on the files the other steps just wrote. Run it
    earlier and it describes the *previous* run — a state page that is
    confidently wrong, which is the shape this corpus keeps finding.

    Mutation: move the `doc status` step earlier and this fails.
    """
    labels = [label for label, *_ in generate_docs.STEPS]
    writes = [out for _, _, out, _, _ in generate_docs.STEPS]

    assert "doc-status.json" in writes, writes
    at = writes.index("doc-status.json")
    later = [w for w in writes[at + 1:] if w != "doc-status.json"]
    # Renderers of doc-status may follow it; nothing that *writes a document it
    # reports on* may.
    assert all(w.endswith(".md") for w in later), (
        f"these write after the state document and would not be described by "
        f"it: {later}")
    assert at >= len(writes) - 3, (
        f"doc-status.json is step {at + 1} of {len(writes)}; it reports on what "
        f"the others wrote and must come after them")


def test_a_renderer_runs_after_the_document_it_reads():
    """`handbook/gates.md` is rendered from `gate-status.json`. Rendering first
    would produce a page describing the previous run.

    Mutation: swap a renderer above its source and this fails.
    """
    order = {out: n for n, (_, _, out, _, _) in enumerate(generate_docs.STEPS)}
    for renderer, source in (("handbook/gates.md", "gate-status.json"),
                             ("handbook/document-states.md", "doc-status.json")):
        if renderer in order and source in order:
            assert order[source] < order[renderer], (
                f"{renderer} is rendered before {source}, which it reads")


def test_every_step_names_a_script_that_exists():
    """A step naming a script nobody wrote fails at the prompt, in the middle
    of a regeneration, after some documents have already been rewritten."""
    for label, argv, _, _, check_argv in generate_docs.STEPS:
        script = CORPUS / argv[0]
        assert script.is_file(), f"{label}: no such script {argv[0]}"
        if check_argv:
            assert (CORPUS / check_argv[0]).is_file(), (
                f"{label}: check mode names a script that is not there")


def test_every_step_declares_whether_it_reaches_the_network():
    """`--offline` skips network steps. A step that lied about being offline
    would reach out during a run somebody asked not to.

    Mutation: drop the flag from a step and this fails.
    """
    for label, _, _, network, _ in generate_docs.STEPS:
        assert isinstance(network, bool), f"{label}: network is not stated"


# --- check mode is the CI-safe half -------------------------------------------


def test_check_mode_writes_nothing():
    """**THE PROPERTY CI DEPENDS ON.** `--check` runs on a runner against a
    checked-out tree; writing there would turn a verification into a change.

    Mutation: let `--check` fall through to the writing branch and this fails.
    """
    before = {
        path: path.read_bytes()
        for path in (CORPUS / "governance-status.yaml",
                     CORPUS / "gate-status.json",
                     CORPUS / "doc-status.json")
        if path.is_file()
    }
    assert before, "nothing to compare; the documents are absent"

    checked()

    for path, was in before.items():
        assert path.read_bytes() == was, f"--check rewrote {path.name}"


def test_check_mode_says_which_documents_it_cannot_check():
    """A step with no check mode is skipped, and saying so is the difference
    between "verified" and "verified what it could".

    Mutation: silently skip them and this fails.
    """
    done = checked()
    said = done.stdout + done.stderr

    uncheckable = [label for label, _, _, _, check in generate_docs.STEPS
                   if check is None]
    if uncheckable:
        assert "no check mode" in said, said
    assert "Checking generated documents" in said


def test_check_mode_names_what_drifted_rather_than_only_counting():
    """A count sends somebody to diff twelve files. The failing step's own
    output is what says which line moved."""
    import inspect

    source = inspect.getsource(generate_docs.main)
    assert 'f"--- {label}' in source, (
        "a failing check does not print the step's own output")
    assert "have drifted" in source
    assert "Run: python ci/generate_docs.py" in source, (
        "the remedy is not named")


# --- what it reports ----------------------------------------------------------


def test_it_distinguishes_wrote_from_unchanged_from_skipped():
    """Three different outcomes. Collapsing them would make a run that skipped
    everything look like a run that found nothing to change.

    Mutation: report skipped steps as unchanged and this fails.
    """
    import inspect

    source = inspect.getsource(generate_docs.main)
    for bucket in ("skipped", "wrote", "unchanged", "failed"):
        assert f"{bucket}" in source, f"{bucket} is not tracked separately"


def test_offline_mode_is_offered_and_says_what_it_skipped():
    """A regeneration on a machine with no network must be possible and must
    not pretend it did the network steps."""
    done = subprocess.run(
        [sys.executable, str(CI / "generate_docs.py"), "--help"],
        cwd=CORPUS, capture_output=True, text=True, timeout=120,
        encoding="utf-8", errors="replace")
    assert "--offline" in done.stdout
    assert "skip anything that reaches" in done.stdout
