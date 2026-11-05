#!/usr/bin/env python3
"""What is committed that names a person, a machine, or a private conversation.

    python project-seed/ci/check_leaks.py
    python project-seed/ci/check_leaks.py --json

A secret scanner looks for credentials: a token, a key, something with a shape
a service can revoke. This looks for the other kind of leak, which no secret
scanner flags: an account name in a home directory, a link to a private
conversation or a path to a thread archive, a link to a page an assistant's
host keeps outside every repository, a personal directory (the
Documents or Desktop folder, an IDE's projects folder) used as a path, and a
session's scratch space used as a path. `check_private_names.py` covers private
repository names.

`handbook/what-is-not-the-organisation.md` draws the line: the workstation, the
agent driving a session and the conversation are not the organisation, and a
committed file describes none of them. A path is the mechanical part of that
line; the rest (an editor by name, a process seen running, what somebody said)
is prose, and the reader is the check.

Findings are reported redacted, because a sweep that echoes what it found
publishes it a second time.

What this cannot do: read history (a name already committed stays committed,
and this reads the working tree); tell a placeholder from a real name beyond
the ones listed in `PLACEHOLDERS` (`C:\\Users\\you` is fine and
`C:\\Users\\<account>` is a finding, by convention rather than anything
decidable); or find the leak nobody thought of, which is why `--json` exists: a
person reading the whole list is still the check.
`docs/ref/ci/gates-and-checks.md` describes the patterns.
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
    # Case-sensitive: `/Users/` is a macOS home and `/users/` is a REST route,
    # such as `api.github.com/users/x/repos`. The Windows form keeps a little
    # insensitivity because the drive letter varies there.
    ("home-path", "a home directory names the account it belongs to",
     re.compile(r"(?:[A-Za-z]:[\\/]{1,2}[Uu]sers[\\/]{1,2}|/home/|/Users/)"
                r"(?P<who>[A-Za-z0-9._-]+)")),
    ("shared-conversation", "a link anybody holding it can read",
     re.compile(r"(?i)\b(?:claude\.ai|chatgpt\.com|chat\.openai\.com)/share/"
                r"(?P<who>[A-Za-z0-9-]+)")),
    # A page an assistant's host keeps outside every repository: work
    # delivered there is not versioned with the code and is reviewed as no diff
    # (records/DRAFT-work-is-delivered-into-a-repository.md). The hosts listed
    # are the ones known; a host not listed passes.
    ("hosted-page", "work kept on an assistant's host rather than in a repository",
     re.compile(r"(?i)\b(?:claude\.ai/(?:code/|public/)?artifacts?/|claude\.site/artifacts/|"
                r"chatgpt\.com/canvas/shared/)(?P<who>[A-Za-z0-9-]+)")),
    # A *path* to an archive, not the archive's filename. `conversations.json`
    # names an export format, and `qmcp threads import <conversations.json>` is
    # a command somebody has to be able to write down. Requiring a directory in
    # front of it is what separates a format from somebody's disk.
    ("conversation-archive", "the path of somebody's exported conversations",
     re.compile(r"(?i)(?P<who>(?:[A-Za-z]:[\\/]|~[\\/]|\.{1,2}[\\/])"
                r"[\w.\\/-]*(?:claude_history|chatgpt_history|"
                r"conversations\.json))")),
    # A directory an operating system or an IDE makes for a *person*, used as a
    # path. Case-sensitive, followed by a separator and a component of at least
    # two characters, so `the Documents folder` in prose, `api/documents/` in
    # a route, and a heading followed by an escape in source (`"## Documents\n"`,
    # where the backslash is not a separator) are not matched; the thing
    # matched is a location on somebody's disk.
    ("workstation-layout", "a path through one person's home layout",
     re.compile(r"(?<![A-Za-z0-9_-])(?P<who>(?:\.\.[\\/])?(?:Documents|Desktop|"
                r"Downloads|OneDrive|Dropbox|AndroidStudioProjects|IdeaProjects|"
                r"PycharmProjects|WebstormProjects)[\\/][^\s\"'`)\]]{2,})")),
    # A session's scratch space, used as a path. What a tool wrote there was
    # never the organisation's, and a committed reference to it points at a
    # file that no other machine has.
    ("session-scratch", "a path inside a session's scratch space",
     re.compile(r"(?<![A-Za-z0-9_-])(?P<who>(?:\.?scratchpad|\.claude[\\/]projects|"
                r"\.codex[\\/]sessions)[\\/][^\s\"'`)\]]+)")),
]

# Extensions worth reading. Binaries are skipped; an SVG is text, and a
# screenshot exported as one can carry a path.
SKIP_SUFFIX = {".png", ".jpg", ".jpeg", ".gif", ".ico", ".pdf", ".zip", ".gz",
               ".whl", ".exe", ".dll", ".so", ".dylib", ".woff", ".woff2",
               ".ttf", ".mp4", ".mov", ".webm", ".wasm", ".bin", ".db",
               ".sqlite", ".sqlite3"}


# An escape hatch with a price: the reason is required, and the count of
# exemptions used is printed on every run, so silencing this stays visible
# rather than becoming the way it is used. The same shape as `adr_lint.py`'s.
# The tests that prove this check works carry fixtures it would flag, and those
# lines declare themselves this way.
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
              f"home-layout or scratch path, shared-conversation or hosted-page "
              f"link, or archive path.")
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
