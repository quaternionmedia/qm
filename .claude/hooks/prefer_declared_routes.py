#!/usr/bin/env python3
"""Refuse a shell command that goes around a declared route.

`AGENTS.md` says `uv run qm --help` is the whole surface. This hook fires when a
shell command goes around a route that exists: running `pytest` directly
instead of `qm test`, mutation testing by hand with `cp` and `sed` instead of
`qm mutate`, parsing a file by hand instead of letting the suite check it.
Reading a rule says what its author meant; only something that fires says
whether it is followed
(`records/DRAFT-a-check-is-evidence-only-after-it-has-failed.md`).

It warns and allows by default: a hook that blocked would eventually block
something legitimate at the worst moment and be turned off. Set
`QM_ROUTES_STRICT=1` to make it refuse instead.

It is deliberately small: it knows the commands that have a route and get
bypassed, because a hook policing every command would fire on things it does
not understand.

Wire it in `.claude/settings.json`:

    {"hooks": {"PreToolUse": [{"matcher": "Bash",
      "hooks": [{"type": "command",
                 "command": "python .claude/hooks/prefer_declared_routes.py"}]}]}}
"""

from __future__ import annotations

import json
import os
import re
import sys

# pattern -> (what to run instead, why it matters)
#
# Each pattern is a bypass that has happened, not a guess about how somebody
# might go wrong.
ROUTES: tuple[tuple[str, str, str], ...] = (
    (
        r"(?<!qm )(?<!run )\bpytest\b(?!.*--collect-only)",
        "uv run qm test   (or: uv run dossier test)",
        "the suites CI runs, with CI's arguments. Running pytest directly "
        "picks up different paths and different plugins, and a green run that "
        "collected less than CI does is the reason this route exists",
    ),
    (
        r"\bpython\s+-c\s+[\"'].*\bast\.parse\b",
        "nothing -- the suite already checks it",
        "every script's syntax is checked by "
        "`tests/.../test_every_script_compiles.py`. Typing this after each edit "
        "is a check living in somebody's fingers, which is a check performed "
        "when somebody remembers",
    ),
    (
        r"\bcp\b.*\.py.*(/tmp|\\Temp).*&&|sed -i.*\.py.*&&.*pytest",
        "uv run qm mutate <module> --tests <tests>",
        "hand-rolled mutation has three failure modes the command does not: an "
        "edit that silently matches nothing, a restore that does not happen "
        "when something raises, and a mutation nobody else can reproduce",
    ),
    (
        r"\bgit\s+(commit|push)\b(?!.*--dry-run)",
        "uv run --extra preflight qm preflight   (before committing)",
        "the workflows' real steps. Reading a workflow and running the commands "
        "you think it contains is not the same thing, and the difference is "
        "where false 'CI is green' claims come from",
    ),
)

# Commands that look like a bypass and are not. A hook without this list fires
# on its own remedy, which is the fastest way to get itself disabled.
ALLOWED = (
    r"uv run qm\b",
    r"uv run --\S+ qm\b",
    r"uv run (--no-sync )?dossier\b",
    r"uv run (--no-sync )?qmcp\b",
    r"\.claude[/\\]hooks",
    r"--help\b",
)


def looks_allowed(command: str) -> bool:
    return any(re.search(pattern, command) for pattern in ALLOWED)


def findings(command: str) -> list[tuple[str, str]]:
    """Every route this command goes around."""
    if looks_allowed(command):
        return []
    found = []
    for pattern, instead, why in ROUTES:
        if re.search(pattern, command):
            found.append((instead, why))
    return found


def main() -> int:
    try:
        event = json.load(sys.stdin)
    except Exception:                              # noqa: BLE001
        # A hook that cannot read its input lets the work through. Failing
        # closed here would block every command on a parsing bug in the hook.
        return 0

    # Valid JSON is not the same as the right shape: `[]` and `null` parse and
    # then raise on `.get`, which would fail closed and block every command.
    # A non-object input lets the work through too.
    if not isinstance(event, dict):
        return 0

    if event.get("tool_name") != "Bash":
        return 0
    command = str((event.get("tool_input") or {}).get("command", ""))
    hits = findings(command)
    if not hits:
        return 0

    lines = ["A declared route exists for this:"]
    for instead, why in hits:
        lines.append(f"  run instead:  {instead}")
        lines.append(f"  because:      {why}")
    lines.append("")
    lines.append("AGENTS.md: `uv run qm --help` is the whole surface. If there "
                 "is genuinely no route for what you are doing, add one -- that "
                 "is the correction, not writing the path down.")
    message = "\n".join(lines)

    if os.environ.get("QM_ROUTES_STRICT"):
        print(message, file=sys.stderr)
        return 2                                   # refuse, and say why

    print(message, file=sys.stderr)
    return 0                                       # warn, and allow


if __name__ == "__main__":
    sys.exit(main())
