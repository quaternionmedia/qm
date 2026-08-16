#!/usr/bin/env python3
"""The repository roster, read once and the same way by everything that uses it.

`ci/workspace.yaml` is the committed roster. A **private** repository appears
there as a bare `ref` and nothing else -- naming it would defeat the redaction
`inventory-public.json` applies to the same repository, which is how the corpus
came to contradict itself for five days.

That redaction broke every consumer at once. Four generators read
`entry["name"]` directly and raised `KeyError` the moment a nameless entry
existed, which is a loud failure and the lucky case; the unlucky one is a
consumer that reads `entry.get("name")` and quietly writes `None` into a
document.

So loading lives here, and **`name` is guaranteed**:

  - with `ci/workspace-private.yaml` present, the private entry's real name and
    paths are merged in, and the tool behaves as it always did;
  - without it -- a fresh clone, another machine, a runner -- `name` is the
    `ref` itself. Consumers keep working and print `private-32`, which is the
    correct thing to publish anyway.

An entry is never dropped. A roster silently two short reads exactly like a
roster of everything that exists.
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml

CI_DIR = Path(__file__).resolve().parent
ROSTER = CI_DIR / "workspace.yaml"
COMPANION = CI_DIR / "workspace-private.yaml"


def label(entry: dict) -> str:
    """What an entry may be called in output.

    Kept even though `load` guarantees `name`, because entries reach output
    from places that never went through the loader -- a test fixture, a hand
    built dict, a document being re-read.
    """
    return entry.get("name") or entry.get("ref") or "<unnamed>"


def merge_private(roster: list[dict], companion: Path = COMPANION) -> list[dict]:
    """Fill in what the committed roster deliberately omits."""
    supplied: dict[str, dict] = {}
    if companion.is_file():
        document = yaml.safe_load(companion.read_text(encoding="utf-8")) or {}
        supplied = {
            e["ref"]: e for e in (document.get("repositories") or []) if e.get("ref")
        }

    merged = []
    for entry in roster:
        ref = entry.get("ref")
        filled = {**entry, **supplied[ref]} if ref and ref in supplied else dict(entry)
        # The guarantee. A consumer reading `entry["name"]` gets the reference
        # when the real name is not available here, never a KeyError and never
        # a None that reaches a document.
        if not filled.get("name"):
            filled["name"] = label(filled)
        merged.append(filled)
    return merged


def load(path: Path = ROSTER, companion: Path = COMPANION) -> list[dict]:
    document = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return merge_private(document.get("repositories") or [], companion)


def redact(node, name: str, ref: str):
    """Replace one repository name with its reference, everywhere in a subtree.

    A project entry does not carry its name once. It carries it as `name`, and
    again inside `branch.ref` as `origin/project/<name>`, and again inside
    `adoption.submodule.branch`. Redacting the field and leaving the branch
    strings publishes the name three times out of five -- so this walks the
    whole entry rather than naming the fields, which would be a list to keep in
    step with a shape that changes.

    Bounded like ci/check_private_names.py, for the same reason: a plain
    substring replace rewrites a longer repository that merely contains this
    one.
    """
    if isinstance(node, dict):
        return {k: redact(v, name, ref) for k, v in node.items()}
    if isinstance(node, list):
        return [redact(v, name, ref) for v in node]
    if isinstance(node, str):
        return re.sub(rf"(?<![A-Za-z0-9_-]){re.escape(name)}(?![A-Za-z0-9_-])", ref, node)
    return node
