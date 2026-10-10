#!/usr/bin/env python3
"""Refuses durable text that shouts or narrates its own history.

    python check_timeless.py --base origin/main   # the lines this branch adds
    python check_timeless.py --all                 # every tracked file
    python check_timeless.py --all --summary       # counts per file

The rule is `records/DRAFT-durable-text-states-what-is-true.md`: durable text
states what is true now and what to do with it. This check recognises two
shapes of the opposite:

- **shout**: three or more capitalised words in a row, such as a sentence set
  in capitals to carry emphasis;
- **narrative**: a phrase that only tells how the text or the code came to be,
  such as `used to be`, `the day it was written` or `the check that caught`.

It reads prose only: comments and docstrings in code, markdown outside fenced
blocks and code spans, and comments in configuration files. A deliberate
exception is declared with `timeless: allow` and a reason on the line or the
line above; allowances are counted on every run.

With `--base`, only lines added since the merge base with that ref are
checked, so a repository can adopt the gate before its existing text is swept.
`--all` checks every tracked line and is the measure of a sweep.

Exit status: 0 when nothing is found, 1 when something is, 2 when the
repository or the base cannot be read.

Limits: a story told in neutral words passes, and so does history phrased as
a present fact that is false. Capitals in title case or spaced out, a phrase
broken so that no line holds three of its words, and file types other than
those listed below are not read as shouting. Whether a sentence is true,
current and useful is for the author and the reviewer; this sees the shapes a
pattern can match.
"""

from __future__ import annotations

import argparse
import ast
import io
import re
import subprocess
import sys
import tokenize
from dataclasses import dataclass
from pathlib import Path

# An allowance names its reason: at least one word after `allow`, so a bare
# marker, or one closed straight away by a comment terminator, counts for nothing.
ALLOW = re.compile(r"timeless:\s*allow\s+[^\s>*/-]")

# Three or more words of two or more capitals each, separated by single
# spaces. A hyphenated name such as a licence identifier is one word, and a
# one-letter word does not break the run.
SHOUT = re.compile(r"(?<![\w`-])[A-Z][A-Z'’]+(?: (?:[A-Z] )?[A-Z][A-Z'’]+){2,}(?![\w`-])")

# Phrases whose only job is to narrate. Each is chosen to have no ordinary
# present-tense reading in this kind of text.
NARRATIVE = tuple(re.compile(p, re.IGNORECASE) for p in (
    r"\bused to (?:be|say|read|call|live|sit|hold|open)\b",
    r"\buntil (?:recently|now)\b",
    r"\b(?:at|as of) the time of writing\b",
    r"\bas of this writing\b",
    r"\bthe day it was written\b",
    r"\b(?:in one|in a single|the same) (?:session|afternoon|morning|week|day)\b",
    r"\b(?:that|this) (?:afternoon|morning|week)\b",
    r"\bthe (?:check|test|guard|tool|lint|gate) that caught\b",
    r"\bwas (?:found|caught|discovered) (?:to|missing|wanting|lying|in|at)\b",
    r"\b(?:it )?turned out\b",
    r"\bnobody (?:had|noticed|knew)\b",
    r"\bnothing served\b",
))

# Paths that are about a moment by nature (§4), or are not this repository's.
EXEMPT = (
    "perspectives/", "handbook/handoffs/", "protocols/runs/", "governance/", "vendor/",
    "node_modules/", "CHANGELOG",
)
CODE = {".py"}
HASH_COMMENTED = {".yml", ".yaml", ".toml", ".cfg", ".ini", ".sh", ".gd"}
SLASH_COMMENTED = {".js", ".mjs", ".cjs", ".ts", ".css"}
MARKDOWN = {".md"}


@dataclass(frozen=True)
class Finding:
    path: str
    line: int
    kind: str
    text: str


def git(root: Path, *args: str) -> str:
    done = subprocess.run(["git", *args], cwd=str(root), capture_output=True,
                          text=True, encoding="utf-8", errors="replace")
    if done.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)}: {done.stderr.strip()}")
    return done.stdout


def checked(path: str) -> bool:
    if any(path.startswith(p) or f"/{p}" in path for p in EXEMPT):
        return False
    suffix = Path(path).suffix
    return suffix in CODE | HASH_COMMENTED | SLASH_COMMENTED | MARKDOWN


def _python_prose(text: str) -> dict[int, str]:
    """Comment and docstring lines of a Python file, by line number."""
    prose: dict[int, str] = {}
    lines = text.splitlines()
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return prose
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            body = getattr(node, "body", [])
            if body and isinstance(body[0], ast.Expr) and isinstance(
                    getattr(body[0], "value", None), ast.Constant) and isinstance(
                    body[0].value.value, str):
                first, last = body[0].lineno, body[0].end_lineno or body[0].lineno
                for number in range(first, last + 1):
                    prose[number] = lines[number - 1]
    try:
        for token in tokenize.generate_tokens(io.StringIO(text).readline):
            if token.type == tokenize.COMMENT:
                prose[token.start[0]] = token.string
    except (tokenize.TokenError, IndentationError):
        pass
    return prose


def _markdown_prose(text: str) -> dict[int, str]:
    prose: dict[int, str] = {}
    fenced = False
    for number, line in enumerate(text.splitlines(), start=1):
        if line.lstrip().startswith(("```", "~~~")):
            fenced = not fenced
            continue
        if not fenced and not line.startswith("    "):
            prose[number] = re.sub(r"`[^`]*`", "", line)
    return prose


def _commented_prose(text: str, marker: str) -> dict[int, str]:
    prose: dict[int, str] = {}
    block = False
    for number, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if marker == "//":
            if block or stripped.startswith("/*"):
                prose[number] = stripped
                block = "*/" not in stripped
                continue
        index = line.find(marker)
        if index >= 0:
            prose[number] = line[index + len(marker):]
    return prose


def prose_lines(path: str, text: str) -> dict[int, str]:
    suffix = Path(path).suffix
    if suffix in CODE:
        return _python_prose(text)
    if suffix in MARKDOWN:
        return _markdown_prose(text)
    if suffix in HASH_COMMENTED:
        return _commented_prose(text, "#")
    if suffix in SLASH_COMMENTED:
        return _commented_prose(text, "//")
    return {}


def scan(path: str, text: str, only: set[int] | None = None) -> tuple[list[Finding], int]:
    """Findings in one file, and how many lines were allowed."""
    lines = text.splitlines()
    found: list[Finding] = []
    allowed = 0
    for number, line in sorted(prose_lines(path, text).items()):
        if only is not None and number not in only:
            continue
        line = re.sub(r"`[^`]*`", "", line)
        hits = []
        for match in SHOUT.finditer(line):
            hits.append(("shout", match.group(0)))
        for pattern in NARRATIVE:
            for match in pattern.finditer(line):
                hits.append(("narrative", match.group(0)))
        if not hits:
            continue
        above = lines[number - 2] if number >= 2 else ""
        if ALLOW.search(lines[number - 1]) or ALLOW.search(above):
            allowed += 1
            continue
        for kind, excerpt in hits:
            found.append(Finding(path, number, kind, excerpt))
    return found, allowed


def added_lines(root: Path, base: str) -> dict[str, set[int] | None]:
    """Lines added since the merge base with `base`, by path.

    Compared with the working tree, so uncommitted edits are read, and an
    untracked file counts as added in full. On a runner the working tree is
    the commit under test.
    """
    merge_base = git(root, "merge-base", base, "HEAD").strip()
    diff = git(root, "diff", "-U0", "--no-color", "--diff-filter=AM", merge_base)
    added: dict[str, set[int]] = {
        path: None for path in git(root, "ls-files", "--others", "--exclude-standard").splitlines()
    }
    path = None
    for line in diff.splitlines():
        if line.startswith("+++ "):
            path = line[6:] if line.startswith("+++ b/") else None
        elif line.startswith("@@") and path:
            span = re.search(r"\+(\d+)(?:,(\d+))?", line)
            start, count = int(span.group(1)), int(span.group(2) or 1)
            added.setdefault(path, set()).update(range(start, start + count))
    return added


def findings(root: Path, base: str | None = None) -> tuple[list[Finding], int]:
    if base is None:
        scope = {path: None for path in git(root, "ls-files").splitlines()}
    else:
        scope = added_lines(root, base)
    found: list[Finding] = []
    allowed = 0
    for path, only in sorted(scope.items()):
        if not checked(path) or not (root / path).is_file():
            continue
        text = (root / path).read_text(encoding="utf-8", errors="replace")
        more, allows = scan(path, text, only)
        found += more
        allowed += allows
    return found, allowed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    which = parser.add_mutually_exclusive_group(required=True)
    which.add_argument("--base", help="check only lines added since the merge base with this ref")
    which.add_argument("--all", action="store_true", help="check every tracked line")
    parser.add_argument("--summary", action="store_true", help="print counts per file")
    parser.add_argument("--root", default=".", help="the repository to read")
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()
    try:
        found, allowed = findings(root, None if args.all else args.base)
    except RuntimeError as exc:
        print(f"timeless: cannot read the repository: {exc}", file=sys.stderr)
        return 2
    if args.summary:
        per_file: dict[str, int] = {}
        for item in found:
            per_file[item.path] = per_file.get(item.path, 0) + 1
        for path, count in sorted(per_file.items(), key=lambda kv: (-kv[1], kv[0])):
            print(f"{count:>5}  {path}")
    else:
        for item in found:
            print(f"{item.path}:{item.line}: {item.kind}: {item.text}")
    scope = "every tracked line" if args.all else f"lines added since {args.base}"
    print(f"timeless: {len(found)} finding(s) in {scope}; {allowed} allowed by a stated reason.")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
