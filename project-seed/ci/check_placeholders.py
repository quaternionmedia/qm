#!/usr/bin/env python3
"""Refuse a template that is being shown to a reader.

A seed file, run in place: a forking project runs it out of the governance
submodule. Nothing copies it.

What this is for. A seed file carries placeholders on purpose -- `<name>` stands
for whatever project copies it. A *copy* carrying the same placeholder is a
different thing: it is a template being used on its reader. Somebody opens
`adr/README.md` on `project/datum`, reads "this project's own dedicated branch
(`project/<name>`)", and learns nothing about which branch that is. The document
is answering a question it was supposed to have answered.

The banners of `project-seed/ide/AGENTS.md` and `project-seed/adr/README.md`
state the rule: replace every <name> placeholder with the project's own name.
This check enforces it on the copies.

How it decides, without an allowlist. A placeholder is a defect in a copy only
if the *seed source of that copy* also has it. So the check pairs each copied
file with its seed original and refuses any placeholder the seed declared and
the copy kept. That means:

  - generic prose is never flagged. `records/` saying "a `project/<name>` branch
    is never merged into `main`" is a statement about the namespace, not about one
    project, and no seed file is its source.
  - a placeholder invented after the copy was made is not flagged either, because
    it is not in the seed.
  - only `<name>` counts. `--base <base>` in a command example is an argument a
    reader fills in, not the project's identity. See the note above the pattern.

There is **no code-span exemption**, unlike the vocabulary and attribution
checks. A placeholder inside backticks is still on the page and still read, and
the seed writes the project's branch as `` `project/<name>` ``.

Exit status is 1 for any finding. Every finding is a refusal: the fix is always
to substitute the placeholder or delete the sentence.

Usage:
    python check_placeholders.py --seed project-seed/adr --copy adr
    python check_placeholders.py --seed project-seed/adr --copy adr --instance datum
    python check_placeholders.py --seed project-seed/ide --copy . --instance dossier
"""

from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path

# `<name>` and nothing else.
#
# A general `<[a-z-]+>` pattern would also match `--base <base> --head <branch>`
# in a command example. Those are arguments a reader supplies when running the
# command: placeholders in a shell sense and not in the identity sense.
#
# `<name>` is the one token the corpus's own rule names -- "Replace every <name>
# placeholder with the project's own name", in `project-seed/ide/AGENTS.md`'s
# banner -- and it is the one that means *this project*. Extending the set is a
# decision about the rule, so it belongs in the rule before it reaches this
# pattern.
PLACEHOLDER = re.compile(r"<name>")

# The seed's own banner is meant to be deleted in the copy, so a placeholder that
# only appears inside it is not a substitution failure -- it is a banner failure,
# which the copy-verbatim checks already cover. Strip it before comparing.
SEED_BANNER = re.compile(r"<!--\s*SEED FILE:.*?-->", re.DOTALL)


def placeholders_in(text: str) -> set[str]:
    return set(PLACEHOLDER.findall(SEED_BANNER.sub("", text)))


def instance_from_branch() -> str | None:
    """Derive the project name from a `project/<x>` branch, if we are on one."""
    result = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"], capture_output=True, text=True
    )
    branch = (result.stdout or "").strip()
    return branch.split("/", 1)[1] if branch.startswith("project/") else None


def check(seed_dir: Path, copy_dir: Path, instance: str | None) -> list[str]:
    if not seed_dir.is_dir():
        return [f"{seed_dir}: not a directory"]
    if not copy_dir.is_dir():
        return [f"{copy_dir}: not a directory"]

    failures: list[str] = []
    paired = 0
    for seed_file in sorted(seed_dir.rglob("*.md")):
        copy_file = copy_dir / seed_file.relative_to(seed_dir)
        if not copy_file.exists():
            continue
        paired += 1
        declared = placeholders_in(seed_file.read_text(encoding="utf-8"))
        if not declared:
            continue
        copy_text = copy_file.read_text(encoding="utf-8")
        body = SEED_BANNER.sub("", copy_text)
        for lineno, line in enumerate(body.splitlines(), start=1):
            for hit in PLACEHOLDER.finditer(line):
                token = hit.group(0)
                if token not in declared:
                    continue
                suggestion = (
                    f" Substitute it: {token} -> {instance!r}."
                    if instance
                    else " Substitute it with this project's own name."
                )
                failures.append(
                    f"{copy_file}:{lineno}: this file is a COPY of {seed_file} and "
                    f"still carries the placeholder {token}. A reader of this page "
                    f"is being shown a template.{suggestion}"
                )

    if paired == 0:
        failures.append(
            f"{copy_dir}: no file here pairs with one in {seed_dir}. Either the "
            f"copy is missing or the wrong directories were passed -- a check that "
            f"examined nothing must not report clean."
        )
    return failures


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--seed", required=True, help="Directory of seed originals")
    ap.add_argument("--copy", required=True, help="Directory of the copies to check")
    ap.add_argument(
        "--instance",
        help="This project's name, for the suggested substitution. Derived from a "
        "project/<x> branch when omitted.",
    )
    args = ap.parse_args()

    instance = args.instance or instance_from_branch()
    failures = check(Path(args.seed), Path(args.copy), instance)

    if failures:
        print("=" * 72)
        print("A TEMPLATE IS BEING SHOWN TO A READER")
        print("=" * 72)
        for line in failures:
            print(line)
        print(
            f"\ncheck_placeholders: {len(failures)} finding(s). A seed carries "
            f"placeholders on purpose; a copy that keeps one is answering a "
            f"question it was supposed to have answered."
        )
        return 1

    where = f" as {instance}" if instance else ""
    print(f"check_placeholders: clean ({args.copy} against {args.seed}{where}).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
