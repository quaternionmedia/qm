#!/usr/bin/env python3
"""No private repository name appears in a file this repository tracks.

    uv run qm private-names                  # scan the tracked tree
    uv run qm private-names --context        # every occurrence, redacted
    uv run qm private-names --source host    # ask the forge, as CI does
    uv run qm private-names --strict         # fail when it cannot verify

THREE STATES, AND ONLY ONE OF THEM IS A PASS.

    clean       a source of private names was read, and none of them appear
    found       a name is used as a repository in a tracked file -- exit 1
    unverified  no source was available, so nothing was checked

`unverified` exits 0 by default so a fresh clone is not blocked by the absence
of a file it is never supposed to have, and prints that word first so nobody
reads it as a pass. `--strict` turns it into a failure, and CI runs it that way.

TWO TIERS, BECAUSE SOME PRIVATE REPOSITORIES ARE NAMED AFTER ORDINARY WORDS.
A `found` is a name used *as a repository*. A `possible` is prose containing a
word that a private repository happens to be called, reported and never gated
on. Without that split this check produced 187 findings and no disclosures.

WHY IT EXISTS. Two private repository names sat in the committed
`ci/workspace.yaml` from 2b50bd6 while `inventory-public.json` redacted the same
two repositories as `private-32` and `private-33`. Both files were committed,
each looked right alone, and nothing read them together. This reads them
together.

WHAT IT CANNOT DO. It cannot find a name in history -- only in the tree as it
stands. The two names above remain in the public history of a public repository
and no forward fix removes them; that is recorded as a declared exemption rather
than quietly carried.

WHERE THE NAMES COME FROM. `--source local` reads the gitignored companions, so
it works on the operator's machine and nowhere else. `--source host` asks the
forge, which is the only source a runner has — a check that reported
`unverified` on every pull request would be a gate that never fires, and a gate
that never fires is worse than none, because a reader believes something is
enforced.
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
    `ci/workspace-private.yaml` as a `repositories` list of entries. Reading
    only the second made this check aware of two names out of thirty-four, and
    a `clean` result meant almost nothing -- it was the roster's two names and
    no others. Both shapes are read here.
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
    # the string and the organisation is public by construction. Matching it
    # produced 187 findings, none of them a disclosure, which is the state in
    # which a check stops being read. Registered as
    # `private-name-equal-to-the-org` in ci/exception-registry.yaml.
    return {n for n in names if n.lower() != ORG.lower()}


def host_names(org: str = ORG) -> set[str] | None:
    """Private repository names, asked of the host. None if it could not be asked.

    The local companions are gitignored, so a runner has neither and this check
    would report `unverified` on every pull request -- a gate that never fires
    is worse than no gate, because a reader believes something is enforced. The
    host knows, and a workflow token can ask it.

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

    Tiering on context alone was wrong in the other direction: a handbook
    sentence listing repositories by name has no slash, no quotes and no field,
    so a genuine disclosure was demoted to `possible` while the noise stayed.
    What actually differs is the *name*. A hyphenated or long name is a
    repository wherever it appears; a short all-letter name is a word that a
    repository also happens to be called.

    A heuristic, and stated as one: it will call a short distinctive name
    ambiguous, and those are reported as `possible` rather than dropped.
    """
    return name.isalpha() and len(name) < 12


def repository_context(name: str) -> re.Pattern[str]:
    """The name used *as a repository*, rather than as a word.

    Knowing all thirty-four private names rather than two turned this check
    from under-reporting into unusable: one private repository is named the
    same as the public organisation, so it matched every `<org>/qm` URL in the
    tree -- 187 hits, none of them a disclosure, because an organisation's name
    is public by construction. Others are three, five and nine letters long and
    are ordinary English words, matching prose that has nothing to do with them.

    A repository name is disclosed when it is used as one: after a slash, as a
    quoted token, or as the value of a field that names a repository. Prose
    that happens to contain the word is reported separately as `possible`, and
    never as a finding, because a check that cries wolf 187 times is a check
    nobody runs.
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

    A plain substring search reported `inventory-public.json` as carrying a
    private name. It carries a *public* repository whose name is three
    characters longer and contains the private one -- so the file's whole
    guarantee appeared broken, by the check rather than by the file. Repository
    names are bounded by characters that cannot appear in one.
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

    A handbook line carrying a checkmark crashed the report on a cp1252
    console, so a tool whose purpose is to surface a leak fell over on the
    leak it was surfacing. The console's encoding is a property of the
    machine, not of the finding.
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
