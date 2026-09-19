#!/usr/bin/env python3
"""Refuse a shell command that goes around a declared route.

**THIS EXISTS BECAUSE THE RULE WAS ALREADY WRITTEN DOWN AND DID NOT HOLD.**
`AGENTS.md` says `uv run qm --help` is the whole surface. A session then, in one
day: ran `pytest` directly a dozen times instead of `qm test`, hand-rolled
mutation testing with `cp` and `sed` instead of `qm mutate`, typed
`python -c "import ast; ast.parse(...)"` after every edit instead of letting the
suite check it, and documented a new demo by its file path rather than adding a
route. Every one of those was against a rule the author had read.

`records/DRAFT-a-check-is-evidence-only-after-it-has-failed.md` is the general
finding: reading a rule tells you what its author meant. Only something that
fires tells you whether it is being followed. This is the thing that fires.

**IT WARNS AND ALLOWS BY DEFAULT.** A hook that blocked would eventually block
something legitimate at the worst moment, and the first person to hit that turns
the hook off -- which is worse than not having it. Set
`QM_ROUTES_STRICT=1` to make it refuse instead.

**IT IS DELIBERATELY SMALL.** It knows about the handful of commands that have a
route and get bypassed anyway. A hook trying to police every command would fire
on things it does not understand, and a guard that cries wolf gets switched off
-- which this corpus has already found once, in a checker that reported a false
positive on its first run.

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
# Each of these was bypassed in the session that prompted the hook. A rule with
# no instance behind it would be a guess about how somebody might go wrong.
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
        # **A HOOK THAT CANNOT READ ITS INPUT LETS THE WORK THROUGH.** Failing
        # closed here would block every command on a parsing bug in the hook.
        return 0

    # **VALID JSON IS NOT THE SAME AS THE RIGHT SHAPE.** `[]` and `null` parse
    # fine and then raise on `.get`, so the guard above caught a decode error
    # and let a type error through -- which fails *closed*, blocking every
    # command, which is the one outcome this hook must never produce. Found by
    # a test written for exactly this and not by reading the code.
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
