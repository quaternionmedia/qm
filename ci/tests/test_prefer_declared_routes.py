"""The hook that fires when a command goes around a declared route.

The hook is a guard, so it is held to charter
`a-check-is-evidence-after-it-fails`: it is seen to fire. A guard that cries
wolf on legitimate work gets switched off, so the cases here are the ones that
decide whether it survives contact:

1. it fires on bypasses that have happened, not on invented ones;
2. it does **not** fire on its own remedy;
3. it fails open: a hook that cannot read its input, or that raises, lets the
   work through, because blocking every command on a bug in the hook is worse
   than any bypass it prevents.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

HOOK = (Path(__file__).resolve().parents[2] / ".claude" / "hooks"
        / "prefer_declared_routes.py")


def run(command: str, tool: str = "Bash", strict: bool = False,
        raw: str | None = None) -> subprocess.CompletedProcess:
    """The hook, as Claude Code invokes it: JSON on stdin, exit code out."""
    import os

    payload = raw if raw is not None else json.dumps(
        {"tool_name": tool, "tool_input": {"command": command}})
    env = dict(os.environ)
    env.pop("QM_ROUTES_STRICT", None)
    if strict:
        env["QM_ROUTES_STRICT"] = "1"
    return subprocess.run([sys.executable, str(HOOK)], input=payload,
                          capture_output=True, text=True, env=env)


# --- the commands that actually happened --------------------------------------


@pytest.mark.parametrize("command,expected", [
    ("uv run --no-sync python -m pytest -q", "qm test"),
    ("python -m pytest tests/ -q --durations=25", "qm test"),
    ('python -c "import ast;ast.parse(open(p).read());print(\'parses\')"',
     "the suite already checks it"),
    ("git commit -q -m 'a message'", "preflight"),
    ("git push origin main", "preflight"),
])
def test_it_fires_on_what_was_actually_typed(command, expected):
    """Each of these is a bypass that has happened, against a rule its
    author had read.

    Mutation: remove a pattern from `ROUTES` and the matching case fails.
    """
    done = run(command)
    assert expected in done.stderr, done.stderr
    assert "AGENTS.md" in done.stderr, "the reason is missing"


def test_it_says_what_to_run_and_why():
    """A guard that says only "no" teaches nothing, and gets argued with."""
    done = run("python -m pytest -q")
    assert "run instead:" in done.stderr
    assert "because:" in done.stderr


# --- and does not fire on its own remedy --------------------------------------


@pytest.mark.parametrize("command", [
    "uv run qm test",
    "uv run --extra preflight qm preflight",
    "uv run qm mutate ci/check_mathematics.py --tests ci/tests/x.py",
    "uv run --no-sync dossier topology --list",
    "uv run --no-sync qmcp dashboard",
    "python .claude/hooks/prefer_declared_routes.py",
    "python -m pytest --help",
    "ls -la",
    "git status --short",
    "git commit --dry-run",
])
def test_it_leaves_the_right_thing_alone(command):
    """The hook does not fire on the command it recommends: `uv run qm test`
    runs pytest underneath, and a pattern matching the word would fire on the
    remedy.

    Mutation: remove the allow-list and this fails.
    """
    done = run(command)
    assert done.returncode == 0
    assert not done.stderr.strip(), f"fired on {command!r}: {done.stderr}"


def test_it_ignores_tools_that_are_not_bash():
    """A Write or an Edit is not a shell command, and a hook reading their
    input as one would fire on file contents that mention pytest."""
    done = run("python -m pytest", tool="Write")
    assert done.returncode == 0 and not done.stderr.strip()


# --- it fails open ------------------------------------------------------------


@pytest.mark.parametrize("payload", ["", "not json at all", "[]", "null"])
def test_unreadable_input_lets_the_work_through(payload):
    """Failing closed here would block every command on a bug in the hook.
    A bypass produces a wrong result somebody finds; a jammed hook leaves
    nobody able to work.

    Mutation: raise on bad input and this fails.
    """
    done = run("", raw=payload)
    assert done.returncode == 0


def test_a_missing_command_field_is_not_a_match():
    done = run("", raw=json.dumps({"tool_name": "Bash", "tool_input": {}}))
    assert done.returncode == 0 and not done.stderr.strip()


# --- warn by default, refuse when asked ---------------------------------------


def test_it_warns_and_allows_by_default():
    """Start with warn. A hook that blocks something legitimate at a bad moment
    gets switched off, and a switched-off hook is worse than none.

    Mutation: return 2 unconditionally and this fails.
    """
    done = run("python -m pytest -q")
    assert done.returncode == 0, "the default must not block"
    assert done.stderr.strip(), "and it must still say something"


def test_strict_mode_refuses():
    """For a machine that has decided the routes are not optional.

    Mutation: ignore the environment variable and this fails.
    """
    done = run("python -m pytest -q", strict=True)
    assert done.returncode == 2
    assert "run instead:" in done.stderr


def test_strict_mode_still_allows_the_right_thing():
    """Strict must be strict about bypasses, not about everything."""
    done = run("uv run qm test", strict=True)
    assert done.returncode == 0


# --- the hook is wired, and the wiring is opt-in ------------------------------


def test_the_example_settings_name_this_hook():
    """A hook nothing invokes is a file. The example is what a person copies.

    Mutation: rename the hook without updating the example and this fails.
    """
    example = HOOK.parents[1] / "settings.example.json"
    assert example.is_file(), "there is nothing to copy"
    text = example.read_text(encoding="utf-8")
    assert HOOK.name in text
    assert '"PreToolUse"' in text
    assert '"matcher": "Bash"' in text


def test_the_hook_is_not_enabled_without_somebody_choosing_it():
    """Enabling it changes how every session in this repository behaves, which
    is a decision for whoever works here rather than whoever wrote it."""
    live = HOOK.parents[1] / "settings.json"
    if not live.is_file():
        return
    import json as _json

    hooks = _json.loads(live.read_text(encoding="utf-8")).get("hooks")
    # If somebody has enabled it, that is their decision and this says nothing.
    assert hooks is None or isinstance(hooks, dict)
