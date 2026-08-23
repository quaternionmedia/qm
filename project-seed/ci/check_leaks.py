#!/usr/bin/env python3
"""What is committed that names a person, a machine, or a private conversation.

    python project-seed/ci/check_leaks.py
    python project-seed/ci/check_leaks.py --json

**THE SECRET SCANNER IS NOT THIS.** An installed scanner looks for credentials
— a token, a key, something with a shape a service can revoke. Everything below
is the other kind of leak: an account name, a home directory, a link to a
private conversation. None of it is a credential, none of it would be flagged,
and all of it was found committed in this organisation's repositories on
2026-08-23:

  qmcp        `C:/Users/<name>/repos/qm/qmcp` in a documented MCP client config
  dossier     `C:\\Users\\<name>\\.dossier\\dossier.db` in two of 54 screenshots
  qm          a `claude.ai/share/` link, two conversation identifiers and the
              absolute path of an archive, in a committed transcript's header

**THIS IS THE ONE RULE WITH NO CHECK BEHIND IT.** The organisation states
nowhere more firmly than about the thread archive — conversation titles, session
identifiers and archive paths must never be published — and until this file
nothing enforced it. `check_private_names.py` covers private *repository* names
and nothing else.

**FINDINGS ARE REPORTED REDACTED.** A sweep that echoes what it found has
published it a second time, into a terminal and whatever reads that terminal.

WHAT THIS CANNOT DO. Read history: a name already committed stays committed, and
this reads the working tree. Tell a placeholder from a real name beyond the ones
listed in `PLACEHOLDERS` — `C:\\Users\\you` is fine and `C:\\Users\\<account>` is a
finding, and the difference is a convention rather than anything decidable. Or
find the leak nobody thought of, which is why `--json` exists: a person reading
the whole list is still the check.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

# Account names that are deliberately not anybody's. Extend this rather than
# widening a pattern: a placeholder is a decision, and it should read like one.
PLACEHOLDERS = {"you", "user", "username", "your-user", "someone", "me",
                "<name>", "name", "runner", "root", "home",
                # Ellipsis stands in for a name the writer chose not to give.
                "...", "…",
                # Fixture people. A parser test for a sudo log needs a user in
                # it, and inventing one is the correct thing to have done.
                "alice", "bob", "carol", "dave", "testuser", "example"}

KINDS: list[tuple[str, str, re.Pattern]] = [
    # **NOT CASE-INSENSITIVE, AND THAT IS THE WHOLE POINT.** `/Users/` is a
    # macOS home; `/users/` is a REST route, and `api.github.com/users/x/repos`
    # matched until this was pinned down. A check that fires on every GitHub
    # URL is one people turn off. The Windows form keeps a little insensitivity
    # because the drive letter genuinely varies there.
    ("home-path", "a home directory names the account it belongs to",
     re.compile(r"(?:[A-Za-z]:[\\/]{1,2}[Uu]sers[\\/]{1,2}|/home/|/Users/)"
                r"(?P<who>[A-Za-z0-9._-]+)")),
    ("shared-conversation", "a link anybody holding it can read",
     re.compile(r"(?i)\b(?:claude\.ai|chatgpt\.com|chat\.openai\.com)/share/"
                r"(?P<who>[A-Za-z0-9-]+)")),
    # A *path* to an archive, not the archive's filename. `conversations.json`
    # names an export format, and `qmcp threads import <conversations.json>` is
    # a command somebody has to be able to write down — it appeared nine times
    # in the repository whose job is importing that file. Requiring a directory
    # in front of it is what separates a format from somebody's disk.
    ("conversation-archive", "the path of somebody's exported conversations",
     re.compile(r"(?i)(?P<who>(?:[A-Za-z]:[\\/]|~[\\/]|\.{1,2}[\\/])"
                r"[\w.\\/-]*(?:claude_history|chatgpt_history|"
                r"conversations\.json))")),
]

# Extensions worth reading. Binaries are skipped; an SVG is text and is exactly
# where one of the three findings above lived.
SKIP_SUFFIX = {".png", ".jpg", ".jpeg", ".gif", ".ico", ".pdf", ".zip", ".gz",
               ".whl", ".exe", ".dll", ".so", ".dylib", ".woff", ".woff2",
               ".ttf", ".mp4", ".mov", ".webm", ".wasm", ".bin", ".db",
               ".sqlite", ".sqlite3"}


# An escape hatch with a price: the reason is required, and the count of
# exemptions used is printed on every run, so silencing this stays visible
# rather than becoming the way it is used. Copied in shape from `adr_lint.py`,
# which already solved the same problem in this corpus.
#
# It exists because the first run flagged eight lines in the tests that prove
# this check works — a scan firing on the fixture that demonstrates it, which is
# the false reading `records/DRAFT-decision-record-discipline.md` names. Those
# lines are the check working, and they still need a way to say so.
ALLOW = re.compile(r"leaks:\s*allow\s+(?P<why>\S.*?)\s*(?:-->|\*/|$)")


def allowed_here(lines: list[str], index: int) -> str | None:
    """The stated reason for allowing a hit, from this line or the one above."""
    for candidate in (lines[index], lines[index - 1] if index else ""):
        found = ALLOW.search(candidate)
        if found:
            return found.group("why")
    return None


def tracked(root: Path) -> list[str]:
    done = subprocess.run(["git", "-C", str(root), "ls-files"],
                          capture_output=True, text=True, encoding="utf-8",
                          errors="replace")
    return [line for line in done.stdout.splitlines() if line.strip()]


def redact(text: str) -> str:
    """Enough to recognise, never enough to use."""
    text = text.strip()
    return text[:3] + "…" if len(text) <= 8 else f"{text[:3]}…{text[-2:]}"


def findings(root: Path) -> tuple[list[dict], list[dict]]:
    """(findings, exemptions used). Both are returned; neither is silent."""
    found: list[dict] = []
    excused: list[dict] = []
    for rel in tracked(root):
        if Path(rel).suffix.lower() in SKIP_SUFFIX:
            continue
        path = root / rel
        try:
            body = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if len(body) > 4_000_000:
            continue
        lines = body.splitlines()
        for number, line in enumerate(lines, start=1):
            if len(line) > 6000:
                continue
            for kind, why, pattern in KINDS:
                for match in pattern.finditer(line):
                    who = match.group("who")
                    if who.lower().strip("<>") in PLACEHOLDERS:
                        continue
                    reason = allowed_here(lines, number - 1)
                    if reason:
                        excused.append({"kind": kind, "path": rel,
                                        "line": number, "why": reason})
                        continue
                    found.append({"kind": kind, "why": why, "path": rel,
                                  "line": number, "shown": redact(who)})
    return found, excused


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", default=".")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    files = tracked(root)
    found, excused = findings(root)

    if args.as_json:
        print(json.dumps({"checked": len(files), "findings": found,
                          "exempted": excused}, indent=2))
    elif not found:
        # The denominator, always. `clean` against four files and `clean`
        # against four hundred are the same word and not the same claim.
        print(f"clean   {len(files)} tracked file(s) carry no account name, "
              f"shared-conversation link or archive path.")
        print("        History is not read. What is committed stays committed.")
    else:
        by_kind: dict[str, list[dict]] = {}
        for row in found:
            by_kind.setdefault(row["kind"], []).append(row)
        print(f"found   {len(found)} in {len(files)} tracked file(s). "
              f"Names are shown redacted on purpose.")
        for kind, rows in by_kind.items():
            print(f"\n  {kind} -- {rows[0]['why']}")
            for row in rows[:12]:
                print(f"      {row['path']}:{row['line']}  {row['shown']}")
            if len(rows) > 12:
                print(f"      ... and {len(rows) - 12} more")
        print("\nRedact, or add the account to PLACEHOLDERS if it is nobody's.")

    if excused and not args.as_json:
        print("")
        print(f"{len(excused)} hit(s) allowed by a stated reason. Each is a "
              f"place the pattern matched something deliberate.")

    return 1 if found else 0


if __name__ == "__main__":
    raise SystemExit(main())
