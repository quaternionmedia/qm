#!/usr/bin/env python3
"""Write the multi-root VS Code workspace for the QM repositories.

Org-level tooling, copied nowhere. It reads ci/workspace.yaml and writes one
`.code-workspace` file plus a page next to it explaining what the file assumes.

WHY THE OUTPUT IS NOT COMMITTED

A workspace file is a list of folder paths. Committing one into the corpus
would put one contributor's directory layout into a document every project
adopts by reference, and the first person to clone somewhere else would find a
governance repository asserting something false about their machine. So the
roster is committed, the resolution is done here, and the result lands outside
this repository.

WHAT IT REFUSES TO DO

  - It does not drop a repository it could not find. A roster silently missing
    three entries reads exactly like a roster of everything that exists. Absent
    clones are written into the companion page as MISSING, with the candidate
    paths that were tried.
  - It does not guess a phase. `unknown` is rendered as unknown, and collected
    into a question list at the end, because a repository nobody has placed on
    the ladder is not a repository at the bottom of it.
  - It does not write absolute paths. Every folder is relative to the workspace
    file, so the result is shareable with anyone whose clones sit in the same
    shape -- and the companion page states that shape rather than assuming it.
  - It does not accept a family it cannot find declared. `--family` narrows
    the roster to the members of one or more families, and the names are
    checked against `families.json` -- the seam file `uv run qm families
    --write` produces from the record -- so a misspelt family is refused
    rather than quietly resolving to an empty workspace, which would look
    exactly like a family with no clones on this disk.

Usage:
    python ci/make_workspace.py
    python ci/make_workspace.py --out ../quaternion-media.code-workspace
    python ci/make_workspace.py --search-root C:/Users/me/repos --check
    python ci/make_workspace.py --family show-control --family instruments
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import yaml

# This module is imported two ways: as `ci.<name>` by the qm CLI, and as a
# bare script by anyone running it directly. A plain sibling import works
# only in the second. Putting this file's own directory first makes
# `roster` resolvable under both, which is what ci/cli.py does for the seed.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from roster import label as label_of
from roster import merge_private

UNKNOWN = "unknown"
UNSTATED = "unstated"

# The seam file, not the record. `ci/families.py` reads the declaring section
# of the record and writes this; reading it here is the same relation
# `ci/rollout.py` has to it, and keeps this tool from holding a parser of its
# own for a table it does not own.
FAMILIES = Path(__file__).resolve().parent.parent / "families.json"

# Pinned rather than left to whatever a VS Code release defaults to, and the
# same two keys project-seed/ide/.vscode/settings.json pins for a single
# folder: a multi-root window reads workspace settings, not the settings of
# whichever folder happens to be first.
WORKSPACE_SETTINGS = {
    "chat.useAgentsMdFile": True,
    "chat.useClaudeMdFile": True,
    "git.detectSubmodules": True,
    "git.openRepositoryInParentFolders": "never",
    "search.exclude": {
        "**/node_modules": True,
        "**/.venv": True,
        "**/dist": True,
        "**/__pycache__": True,
    },
}

EXTENSIONS = ["anthropic.claude-code", "GitHub.copilot", "GitHub.copilot-chat"]


def load_roster(path: Path) -> list[dict]:
    document = yaml.safe_load(path.read_text(encoding="utf-8"))
    repositories = document.get("repositories") or []
    if not repositories:
        sys.exit(f"make_workspace: {path} lists no repositories")
    return merge_private(repositories, path.parent / "workspace-private.yaml")


def declared_families(path: Path = FAMILIES) -> list[str]:
    """Every family the seam file declares, or none when it is absent."""
    if not path.is_file():
        return []
    document = json.loads(path.read_text(encoding="utf-8"))
    return [f["name"] for f in document.get("families", []) if f.get("name")]


def select_families(
    roster: list[dict], wanted: list[str], declared: list[str], source: Path = FAMILIES
) -> list[dict]:
    """The roster narrowed to `wanted`, refusing a family nobody declared.

    Two refusals, and both are about a workspace that would look right:

      - a name the seam file does not declare. Matching it against the roster
        would find nothing, and an empty folder list is indistinguishable from
        a family none of whose members is cloned here;
      - an empty seam file. With nothing to check against, every name is
        equally unknown, and the fix is to regenerate it rather than to trust
        the roster's `family` values unexamined.

    An entry with no `family` is unstated, and it is never in a family
    selection: nobody has said which system it is part of, and a workspace that
    included it would have answered for them.

    The selection is ordered by the families as they were asked for, roster
    order within each, so the folder list groups one system's members together
    rather than interleaving them in whatever order the roster happens to hold.
    """
    if not wanted:
        return roster
    if not declared:
        sys.exit(
            f"make_workspace: {source} declares no families, so --family cannot be "
            "checked. Regenerate it: uv run qm families --write families.json"
        )
    unknown = [name for name in wanted if name not in declared]
    if unknown:
        sys.exit(
            f"make_workspace: no family named {', '.join(repr(n) for n in unknown)}. "
            f"Declared: {', '.join(declared)}"
        )
    return [e for family in wanted for e in roster if e.get("family") == family]


def resolve(entry: dict, search_roots: list[Path]) -> Path | None:
    """The first candidate path that is a git repository, or None.

    A directory that exists but holds no `.git` is not a clone -- it is an
    empty folder someone made, and adding it to the workspace would present it
    as a checked-out repository.
    """
    for candidate in entry.get("paths", []):
        for root in search_roots:
            probe = (root / candidate).resolve()
            if (probe / ".git").exists():
                return probe
    return None


def relative_to(target: Path, base: Path) -> str:
    """A relative path in POSIX form, going up as far as needed.

    os.path.relpath rather than Path.relative_to: the latter refuses to emit
    `..`, and half of these clones are not below the workspace file.
    """
    return Path(os.path.relpath(target, base)).as_posix()


def build(roster: list[dict], search_roots: list[Path], out: Path) -> tuple[dict, list[dict]]:
    base = out.parent.resolve()
    resolved: list[dict] = []
    for entry in roster:
        found = resolve(entry, search_roots)
        resolved.append({**entry, "resolved": found})

    folders = []
    for entry in resolved:
        if entry["resolved"] is None:
            continue
        label = label_of(entry)
        if entry.get("role") == "corpus":
            label = f"{label} · constitution"
        folders.append({"name": label, "path": relative_to(entry["resolved"], base)})

    workspace = {
        "folders": folders,
        "settings": WORKSPACE_SETTINGS,
        "extensions": {"recommendations": EXTENSIONS},
    }
    return workspace, resolved


def companion_page(
    resolved: list[dict], out: Path, search_roots: list[Path], families: list[str] = ()
) -> str:
    found = [e for e in resolved if e["resolved"] is not None]
    missing = [e for e in resolved if e["resolved"] is None]
    # Scaffolded, not unknown: since the phase-ladder record every project
    # has a phase, and the open question is whether the ladder's floor is
    # the right answer rather than whether there is one at all.
    unplaced = [e for e in found if str(e.get("phase_source", UNKNOWN)) == "scaffolded"]

    lines = [
        f"# {out.stem}",
        "",
        "Generated by `ci/make_workspace.py` in the QM constitution repository,",
        "from the roster at `ci/workspace.yaml`. Regenerate it rather than editing",
        "it: an edit here is lost on the next run and is invisible to everyone else.",
        "",
        "## What it assumes about your machine",
        "",
        "Every folder path in the workspace file is **relative to this file**, so",
        "sharing it works for anyone whose clones sit in the same shape. That shape",
        "is: this file beside the `qm/` directory, with sibling clones under it, and",
        "a few repositories one level up. Searched from:",
        "",
    ]
    lines += [f"- `{root}`" for root in search_roots]
    lines += [
        "",
        "If your layout differs, re-run the generator with `--search-root`; do not",
        "hand-edit the paths.",
        "",
    ]
    if families:
        # Which families were asked for is stated, and so is the count each
        # one resolved to, because a family whose every member is missing is
        # otherwise a heading with nothing under it -- which reads the same as
        # a family nobody asked for.
        lines += [
            "## Which families this is",
            "",
            "Narrowed with `--family` to the members of these families, as",
            "`ci/workspace.yaml` claims them. A family is a claim a person made,",
            "never inferred; a repository with no family is not in this workspace,",
            "because nobody has said which system it is part of.",
            "",
            "| Family | Members rostered | On this machine |",
            "|---|---|---|",
        ]
        for family in families:
            members = [e for e in resolved if e.get("family") == family]
            here = [e for e in members if e["resolved"] is not None]
            lines.append(f"| `{family}` | {len(members)} | {len(here)} |")
        lines.append("")
    lines += [
        "## What is in it",
        "",
        "| Repository | Family | Role | Phase | Resolved to |",
        "|---|---|---|---|---|",
    ]
    for entry in found:
        lines.append(
            f"| {label_of(entry)} | {entry.get('family') or UNSTATED} | "
            f"{entry.get('role', UNKNOWN)} | "
            f"{entry.get('phase', UNKNOWN)} ({entry.get('phase_source', UNKNOWN)}) | "
            f"`{relative_to(entry['resolved'], out.parent.resolve())}` |"
        )

    lines += ["", "## Not on this machine", ""]
    asked = "asked for" if families else "in the roster"
    if missing:
        lines.append(
            "These are in the roster and were not found. They are listed rather than"
        )
        lines.append(
            "dropped, because a workspace quietly missing three repositories looks"
        )
        lines.append("exactly like a complete one.")
        lines.append("")
        lines.append("| Repository | Candidates tried |")
        lines.append("|---|---|")
        for entry in missing:
            candidates = ", ".join(f"`{p}`" for p in entry.get("paths", []))
            lines.append(f"| {label_of(entry)} | {candidates} |")
    else:
        lines.append(f"None — every repository {asked} resolved.")

    lines += ["", "## Phases nobody has stated", ""]
    if unplaced:
        lines.append(
            "The ladder is `records/DRAFT-project-phase-ladder.md`: **v0.0.1 is"
        )
        lines.append(
            "governance**, the same claim in every project, and every rung above it"
        )
        lines.append(
            "is defined by the project in its own records. These carry v0.0.1 because"
        )
        lines.append(
            "nothing was stated — the floor applied, rather than anybody deciding:"
        )
        lines.append("")
        for entry in unplaced:
            note = f" — {entry['note']}" if entry.get("note") else ""
            lines.append(f"- **{label_of(entry)}**{note}")
        lines.append("")
        lines.append(
            "Answer one by setting its `phase` and `phase_source: stated` in"
        )
        lines.append(
            "`ci/workspace.yaml` and re-running. A rung above v0.0.1 also needs its"
        )
        lines.append("definition written in that project's own records.")
    else:
        lines.append("None — every resolved repository has a phase somebody stated.")

    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--roster",
        type=Path,
        default=Path(__file__).resolve().parent / "workspace.yaml",
    )
    parser.add_argument(
        "--out",
        type=Path,
        help="where to write the .code-workspace "
        "(default: quaternion-media.code-workspace beside the corpus clone's parent)",
    )
    parser.add_argument(
        "--search-root",
        action="append",
        type=Path,
        default=[],
        help="a directory the roster's paths are relative to. Repeatable.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="report only; write nothing. Exit 1 if a roster entry is missing.",
    )
    parser.add_argument(
        "--family",
        action="append",
        default=[],
        help="only the members of this family, as families.json declares it. "
        "Repeatable. The default output name carries the families asked for.",
    )
    parser.add_argument(
        "--families",
        type=Path,
        default=FAMILIES,
        help="the seam file --family is checked against (default: families.json "
        "at the corpus root)",
    )
    args = parser.parse_args(argv)

    corpus = Path(__file__).resolve().parent.parent
    default_root = corpus.parent.parent
    # A narrowed workspace gets its own file name, so asking for one family
    # never overwrites the whole-roster workspace beside it.
    stem = "quaternion-media"
    if args.family:
        stem += "-" + "-".join(args.family)
    out = args.out.resolve() if args.out else (default_root / f"{stem}.code-workspace")
    search_roots = [p.resolve() for p in args.search_root] or [default_root]

    roster = select_families(
        load_roster(args.roster), args.family, declared_families(args.families), args.families
    )
    if not roster:
        sys.exit(
            f"make_workspace: no roster entry claims "
            f"{', '.join(repr(f) for f in args.family)}. A family with no members "
            "is a heading, and a workspace of one would look like a family none of "
            "whose members is cloned here."
        )
    workspace, resolved = build(roster, search_roots, out)
    page = companion_page(resolved, out, search_roots, args.family)

    missing = [label_of(e) for e in resolved if e["resolved"] is None]
    unplaced = [
        label_of(e)
        for e in resolved
        if e["resolved"] is not None and str(e.get("phase_source", UNKNOWN)) == "scaffolded"
    ]

    print(f"roster       {args.roster}")
    if args.family:
        print(f"families     {', '.join(args.family)}")
    print(f"search root  {', '.join(str(r) for r in search_roots)}")
    print(f"workspace    {out}")
    print(f"folders      {len(workspace['folders'])} of {len(roster)} resolved")
    if missing:
        print(f"MISSING      {', '.join(missing)}")
    if unplaced:
        print(f"phase scaffolded {', '.join(unplaced)}")

    if args.check:
        print("\n--check: nothing written.")
        return 1 if missing else 0

    out.parent.mkdir(parents=True, exist_ok=True)
    # ensure_ascii=False: this file is meant to be opened and read by whoever
    # it is shared with, and `qm · constitution` is not that.
    out.write_text(
        json.dumps(workspace, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    companion = out.with_suffix(".md")
    companion.write_text(page, encoding="utf-8", newline="\n")
    print(f"\nwrote {out}")
    print(f"wrote {companion}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
