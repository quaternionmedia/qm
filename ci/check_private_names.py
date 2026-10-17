#!/usr/bin/env python3
"""No private repository name appears in a file this repository tracks.

    uv run qm private-names                  # scan the tracked tree
    uv run qm private-names --context        # every occurrence, redacted
    uv run qm private-names --source host    # ask the forge, as CI does
    uv run qm private-names --strict         # fail when it cannot verify

Three states, and only one of them is a pass:

    clean       a source of private names was read, and none of them appear
    found       a name is used as a repository in a tracked file -- exit 1
    unverified  no source was available, so nothing was checked

`unverified` exits 0 by default so a fresh clone is not blocked by the absence
of a file it is never supposed to have, and prints that word first so nobody
reads it as a pass. `--strict` turns it into a failure.

No workflow runs this check. It reads a machine (a gitignored companion or
the forge), and `registries.yml` admits only checks that read committed files,
because a check that reads a machine reds a pull request for a reason its
author cannot fix. So this is a command somebody runs, and a name reaching a
tracked file is caught by a person choosing to look.

Two tiers, because some private repositories are named after ordinary words. A
`found` is a name used *as a repository*. A `possible` is prose containing a
word that a private repository happens to be called, reported and never gated
on.

It reads together files that each look right alone, such as the roster and the
inventory, which name the same repositories in different forms.

What this cannot do: find a name in history, only in the tree as it stands. A
name already in the public history stays there, and is recorded as a declared
exemption rather than quietly carried.

`--source local` reads the gitignored companions, so it works on the
operator's machine only; `--source host` asks the forge. Neither makes it a
gate: that would mean either a gate that reds a pull request for a reason its
author cannot fix, or a runner holding a credential to enumerate an
organisation's private repositories. `docs/ref/ci/gates-and-checks.md`
describes the check.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent

# The organisation, read from the tool that owns the inventory rather than
# repeated here, so one change moves both.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from inventory import DEFAULT_ORG as ORG  # noqa: E402

# The gitignored companions that hold the mapping. Adding a source here is how
# this check learns about a new class of secret name.
SOURCES = (
    ROOT / "inventory-private.json",
    ROOT / "ci" / "workspace-private.yaml",
)

# Files that name a private repository deliberately. Each is itself untracked;
# listed so a future tracked exemption has an obvious place to be declared.
EXEMPT = {
    "ci/workspace-private.yaml",
    "inventory-private.json",
    "inventory-local.json",
}


def private_names(sources=None) -> set[str]:
    """Every private repository name the local companions know about.

    The two companions store the same fact in different shapes:
    `inventory-private.json` as a `references` mapping of ref -> name, and
    `ci/workspace-private.yaml` as a `repositories` list of entries. The
    second holds only the roster's private repositories, so both shapes are
    read.
    """
    sources = SOURCES if sources is None else sources
    names: set[str] = set()
    for path in sources:
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        data = (json.loads(text) if path.suffix == ".json"
                else yaml.safe_load(text)) or {}
        for entry in data.get("repositories") or []:
            if isinstance(entry, dict) and entry.get("name"):
                names.add(entry["name"])
        for name in (data.get("references") or {}).values():
            if isinstance(name, str) and name:
                names.add(name)

    # A private repository named after the organisation cannot be concealed by
    # this check, because every `<org>/<repo>` reference in the tree contains
    # the string and the organisation is public by construction. Registered as
    # `private-name-equal-to-the-org` in ci/exception-registry.yaml.
    return {n for n in names if n.lower() != ORG.lower()}


def host_names(org: str = ORG) -> set[str] | None:
    """Private repository names, asked of the host. None if it could not be asked.

    The local companions are gitignored, so a runner has neither and would
    report `unverified`. The host knows, and a workflow token can ask it.

    `None` rather than an empty set on failure. An empty set would mean "no
    private repositories exist", which reads as clean and is the most
    flattering possible wrong answer.
    """
    try:
        proc = subprocess.run(
            ["gh", "api", f"orgs/{org}/repos?per_page=100&type=all",
             "--paginate", "--jq", ".[] | select(.private) | .name"],
            capture_output=True, text=True, timeout=90,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if proc.returncode != 0:
        return None
    found = {line.strip() for line in proc.stdout.splitlines() if line.strip()}
    # Same exclusion as the local path, for the same reason: a repository named
    # after the organisation cannot be concealed and matches every URL.
    return {n for n in found if n.lower() != org.lower()} or None


def tracked_files(root: Path) -> list[str]:
    proc = subprocess.run(
        ["git", "ls-files"], cwd=str(root), capture_output=True, text=True
    )
    if proc.returncode != 0:
        return []
    return [line for line in proc.stdout.splitlines() if line]


def ambiguous(name: str) -> bool:
    """Could this name plausibly be an ordinary word in prose?

    Tiering on context alone would demote a sentence listing repositories by
    name (no slash, no quotes, no field) to `possible`. What differs is the
    *name*: a hyphenated or long name is a repository wherever it appears; a
    short all-letter name is a word that a repository also happens to be
    called.

    A heuristic, and stated as one: it will call a short distinctive name
    ambiguous, and those are reported as `possible` rather than dropped.
    """
    return name.isalpha() and len(name) < 12


def repository_context(name: str) -> re.Pattern[str]:
    """The name used *as a repository*, rather than as a word.

    One private repository can share the public organisation's name, so it
    would match every `<org>/qm` URL; others are short ordinary words. A
    repository name is disclosed when it is used as one: after a slash, as a
    quoted token, or as the value of a field that names a repository. Prose that
    happens to contain the word is reported separately as `possible`, and never
    as a finding.
    """
    n = re.escape(name)
    return re.compile(
        rf"(?:/{n}(?![A-Za-z0-9_-]))"                    # owner/name, project/name
        rf"|(?<![A-Za-z0-9_-]){n}/"                      # name/something
        rf"|[\"'](?:{n})[\"']"                           # a quoted token
        rf"|(?:^|\s)(?:name|slug|repository|repo|branch)\s*[:=]\s*\"?{n}\b"
    )


def pattern(name: str) -> re.Pattern[str]:
    """A private name, not a longer name that happens to contain it.

    A plain substring search would report a public repository whose name
    contains a private one. Repository names are bounded by characters that
    cannot appear in one.
    """
    return re.compile(rf"(?<![A-Za-z0-9_-]){re.escape(name)}(?![A-Za-z0-9_-])")


def scan(root: Path, names: set[str]) -> list[tuple[str, str]]:
    """(file, name) for every tracked file carrying a private name."""
    patterns = [(name, pattern(name)) for name in names]
    hits: list[tuple[str, str]] = []
    for rel in tracked_files(root):
        if rel in EXEMPT:
            continue
        path = root / rel
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for name, expr in patterns:
            if expr.search(text):
                hits.append((rel, name))
    return hits


def references(sources=None) -> dict[str, str]:
    """name -> ref, so an occurrence can be shown without being published.

    `inventory-private.json` stores `references` as ref -> name and
    `ci/workspace-private.yaml` stores entries carrying both, so this inverts
    the first and reads the second. A name with no reference is shown as
    `<private>`: a redaction with no handle is still a redaction, and inventing
    a handle would make two different repositories look like one.
    """
    sources = SOURCES if sources is None else sources
    out: dict[str, str] = {}
    for path in sources:
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        data = (json.loads(text) if path.suffix == ".json"
                else yaml.safe_load(text)) or {}
        for ref, name in (data.get("references") or {}).items():
            if isinstance(name, str):
                out[name] = ref
        for entry in data.get("repositories") or []:
            if isinstance(entry, dict) and entry.get("name") and entry.get("ref"):
                out[entry["name"]] = entry["ref"]
    return out


def occurrences(root: Path, names: set[str]) -> list[dict]:
    """Every hit, with its line number and the line already redacted.

    The redaction happens here rather than at the print, so no caller can
    accidentally hold the raw line. Surfacing a leak by quoting it is the
    mistake this whole check exists to stop.
    """
    handles = references()
    patterns = [(name, pattern(name)) for name in names]
    found: list[dict] = []
    for rel in tracked_files(root):
        if rel in EXEMPT:
            continue
        try:
            text = (root / rel).read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for lineno, line in enumerate(text.splitlines(), start=1):
            redacted, hit, certain = line, None, False
            for name, expr in patterns:
                if expr.search(redacted):
                    hit = handles.get(name, "<private>")
                    # A distinctive name is a disclosure wherever it appears.
                    # An ambiguous one counts only where it is used as a
                    # repository, because elsewhere it is probably the word.
                    certain = certain or not ambiguous(name) or bool(
                        repository_context(name).search(line)
                    )
                    redacted = expr.sub(f"<{hit}>", redacted)
            if hit:
                found.append({"file": rel, "line": lineno, "certain": certain,
                              "text": printable(redacted.strip()[:120])})
    return found


def printable(text: str) -> str:
    """Text this console can actually emit.

    A line carrying a character the console cannot encode must not crash the
    report. The console's encoding is a property of the machine, not of the
    finding.
    """
    encoding = sys.stdout.encoding or "utf-8"
    return text.encode(encoding, errors="replace").decode(encoding, errors="replace")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", default=str(ROOT))
    parser.add_argument("--context", action="store_true",
                        help="show each occurrence, with the name redacted to its reference")
    parser.add_argument("--source", choices=("local", "host"), default="local",
                        help="where the private names come from. `host` asks the "
                             "forge, which is the only source a runner has.")
    parser.add_argument("--org", default=ORG)
    parser.add_argument("--strict", action="store_true",
                        help="fail when no source of private names is available")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    if args.source == "host":
        names = host_names(args.org)
        where = f"the host ({args.org})"
    else:
        # Read through the module global rather than the default argument, so a
        # test can point this at a fixture. A default is bound at definition.
        names = private_names(SOURCES)
        where = ", ".join(p.name for p in SOURCES)

    if not names:
        print("unverified  no source of private names, so nothing was checked.")
        print(f"            asked: {where}")
        print("            This is not a pass. It is the absence of evidence, "
              "and it is what a fresh clone sees.")
        return 1 if args.strict else 0

    found = occurrences(root, names)
    certain = [h for h in found if h["certain"]]
    possible = [h for h in found if not h["certain"]]

    if args.context:
        if not found:
            print("clean       no occurrence in any tracked file.")
            return 0
        print(f"found       {len(certain)} used as a repository, {len(possible)} "
              f"as a bare word. Names shown as their reference:")
        for label, rows in (("found", certain), ("possible", possible)):
            if not rows:
                continue
            print()
            print(f"  --- {label} ---")
            current = None
            for hit in rows:
                if hit["file"] != current:
                    current = hit["file"]
                    print(f"  {current}")
                print(f"      {hit['line']:>5}  {hit['text']}")
        print()
        print("            `possible` is prose containing a word that is also a "
              "private repository's name.")
        print("            Redact a finding, or declare the exemption in "
              "ci/exception-registry.yaml.")
        return 1 if certain else 0

    if certain:
        # The name itself is never printed -- doing so here would put it in a
        # log, which is the thing being prevented one layer along.
        print(f"found       {len(certain)} occurrence(s) of a private repository "
              f"name used as a repository:", file=sys.stderr)
        for rel in sorted({h["file"] for h in certain}):
            print(f"              {rel}", file=sys.stderr)
        if possible:
            print(f"\n            {len(possible)} further line(s) contain a word "
                  f"that is also a private name. See --context.", file=sys.stderr)
        print("\n            Redact the file, or declare the exemption in "
              "ci/exception-registry.yaml.", file=sys.stderr)
        return 1

    print(f"clean       {len(names)} private name(s) checked against "
          f"{len(tracked_files(root))} tracked file(s); none appear.")
    print("            History is not read. A name already published stays "
          "published.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
