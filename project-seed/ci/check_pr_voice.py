#!/usr/bin/env python3
"""A pull request speaks as its contributor, to the world -- never to them.

SEED FILE, run in place.

THE RULE. A pull request body is posted under a human's account, so it is that
human's statement of the change. It addresses nobody. A sentence written *to*
the contributor -- "not to be merged without your click", "worth your eye",
"assigned, no review requested", "merge when ready" -- is a tool speaking to its
operator under the operator's own name, published. Read on the host it is the
contributor talking to themself. Everything a session has to say to the person
who asked belongs in the session; the body states decisions and facts
(`handbook/async-contract.md` §3, and clause 5 of
`records/DRAFT-human-only-contributorship.md`).

WHY A CHECK. The rule had been stated to the tool three times and leaked each
time in the same shape: an instruction the contributor gave the session about
how the work was to be handled came back out as a sentence in the body,
addressed to them. Seven pull requests carried it on one day. A rule that has
to be remembered under the operator's name is a rule the tool will forget; this
is the one that does not.

WHAT IT REFUSES

  - the second person anywhere in the body's prose: `you`, `your`, `yours`,
    `yourself`, case-insensitive, as whole words;
  - the handling phrases that have actually leaked, whatever the pronoun:
    "assigned, no review requested", "no review requested", "merge when ready",
    "not to be merged", "please review", "PTAL";
  - the contributor mentioned by their own login (`@login`), when the login is
    given -- a person does not @-mention themself.

WHAT IT LEAVES ALONE

  - fenced code blocks and inline code spans: a command may say `--yours`;
  - quoted lines (`> ...`): a body may quote what somebody said;
  - the third person. "The merge is a human act", "a reviewer's eye is wanted
    on the migration" are statements, and the tool cannot tell a statement about
    a person from one addressed to them without the pronoun. That is the
    documented blind spot.

WHAT THIS CANNOT SEE. Whether the body is honest, complete, or about the diff.
It reads for one voice, and a body that addresses the contributor in the third
person by name walks past it -- which is the shape the rule's own remedy takes
("Peter merges"), so the check does not try to forbid it.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

SECOND_PERSON = re.compile(r"\b(you|your|yours|yourself)\b", re.IGNORECASE)

# Phrases that have leaked, matched as written; the pronoun check catches the
# rest. Kept short and literal so a reader of a refusal can see why.
HANDLING = (
    "assigned, no review requested",
    "no review requested",
    "merge when ready",
    "not to be merged",
    "please review",
    "ptal",
)

FENCE = re.compile(r"^\s*(```|~~~)")
INLINE_CODE = re.compile(r"`[^`]*`")


def offending_lines(body: str, contributor: str | None = None) -> list[tuple[int, str, str]]:
    """Every line that speaks to the contributor: (line number, reason, text)."""
    found: list[tuple[int, str, str]] = []
    in_fence = False
    mention = re.compile(rf"@{re.escape(contributor)}\b", re.IGNORECASE) if contributor else None
    for number, raw in enumerate(body.splitlines(), 1):
        if FENCE.match(raw):
            in_fence = not in_fence
            continue
        if in_fence or raw.lstrip().startswith(">"):
            continue
        line = INLINE_CODE.sub("", raw)
        lowered = line.lower()
        if SECOND_PERSON.search(line):
            found.append((number, "addresses the reader in the second person", raw.strip()))
            continue
        phrase = next((p for p in HANDLING if p in lowered), None)
        if phrase:
            found.append((number, f"a handling instruction ({phrase!r})", raw.strip()))
            continue
        if mention and mention.search(line):
            found.append((number, "mentions the contributor by their own login", raw.strip()))
    return found


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--body-file", help="a file holding the pull request body")
    source.add_argument("--body", help="the body itself")
    parser.add_argument("--contributor", help="the login the pull request is posted under")
    args = parser.parse_args(argv)

    body = Path(args.body_file).read_text(encoding="utf-8") if args.body_file else args.body
    found = offending_lines(body, args.contributor)
    if not found:
        print("voice check: the body speaks as its contributor and addresses nobody.")
        return 0

    print(f"voice check: {len(found)} line(s) speak to the contributor rather than as them.")
    print("A pull request body is posted under a human's account and is their statement of")
    print("the change; what a session has to say to that person belongs in the session.")
    print()
    for number, reason, text in found:
        print(f"  line {number}: {reason}")
        print(f"      {text[:160]}")
    print()
    print("Rewrite in the third person or remove the sentence; `handbook/async-contract.md` §3.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
