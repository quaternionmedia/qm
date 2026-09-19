"""Every principle declares how it relates to the others, or that it does not.

**A PRINCIPLE THAT NOTHING POINTS AT IS A PRINCIPLE NOTHING WILL BE CHECKED
AGAINST.** Measured on 2026-08-25, before this check existed: six of seventeen
principles were named by nobody and named nobody -- P3, P5, P9, P10, P11, P15.
P10 was among them, and P10 is the one that says a tool is an instrument a human
directs rather than a party who can answer for the result.

A draft of P17 then said the model "is what writes the check", which contradicts
P10 in its central sentence. Nothing surfaced it. `check_restatements.py` pairs a
*record* with the documents that summarise it -- one layer down -- and at charter
level there was no check at all. It was caught by a person reading the sentence.

**THE HARD PART IS NOT REQUIRING EDGES. IT IS NOT MANUFACTURING THEM.** A graph
made connected by effort is worse than an honest sparse one, because it looks
checked. So this never requires an edge: it requires a *declaration*, and `none`
is a first-class answer that must carry a reason.

That inverts the pressure. Writing "none -- a house-stack rule constrains no
epistemic one" is cheaper than inventing a relationship, so the lazy path is the
honest one. It is the shape this corpus already uses five times over:
`cannot_see` on a gate, `unearned` on a mapping, `only` on an action,
`why_no_gate` on a workflow, and `FIELDS_WITH_THEIR_OWN_MEANING`'s "Enter does
nothing here, and that is correct" -- a different fact from "nobody wired Enter".

**THE VOCABULARY IS CLOSED, WITH DECLARED INVERSES.** Not a new structure: this
is a second instance of the one `dossier.composition.RELATIONS` already earned in
`ci/mathematics-registry.yaml`, and naming it again there would be the ornament
P15 refuses. A free string would let a typo become a category.

WHAT THIS CANNOT DO. Tell whether two principles actually conflict. It checks
that a relationship somebody stated is stated from both ends and uses a word from
the list. Whether P17 really rests on P10 is a reading, and no script has one.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

CHARTER = Path("PRINCIPLES.md")

# The four kinds, read off relationships already in the charter's prose rather
# than imagined. Each maps to the word its other end must use.
#
#   orders        a tension resolved by precedence.   P4 orders P2, and P4's own
#                 text has said so since it was written.
#   completes     supplies a half the other was missing. P14 -> P13, in those
#                 words.
#   shares-teeth  enforced through the other's mechanism. P8 -> P1. Symmetric:
#                 sharing is mutual and there is no direction to name.
#   rests-on      the claim is false unless the other holds. P17 -> P10.
INVERSES: dict[str, str] = {
    "orders": "ordered-by",
    "ordered-by": "orders",
    "completes": "completed-by",
    "completed-by": "completes",
    "shares-teeth": "shares-teeth",
    "rests-on": "bears",
    "bears": "rests-on",
}

SYMMETRIC = frozenset({"shares-teeth"})

# `↔ Edges: rests-on P10, completes P16`
# `↔ Edges: none -- <reason>`
LINE = re.compile(r"^↔ Edges:\s*(?P<value>.+?)\s*$", re.MULTILINE)
HEADING = re.compile(r"^## (?P<name>P\d+) — (?P<title>.*)$", re.MULTILINE)
EDGE = re.compile(r"^(?P<kind>[a-z-]+)\s+(?P<other>P\d+)$")

# A reason shorter than this is a label. The number matches the bar
# `actions.REGISTRY` sets for `only`, for the same reason: "not applicable" is
# not a reason, it is a way of not writing one.
REASON_ENOUGH = 40


def principles(text: str) -> list[tuple[str, str, str]]:
    """`(name, title, body)` for each principle, in charter order."""
    found = [(m.group("name"), m.group("title"), m.start()) for m in
             HEADING.finditer(text)]
    out = []
    for index, (name, title, start) in enumerate(found):
        end = found[index + 1][2] if index + 1 < len(found) else len(text)
        out.append((name, title, text[start:end]))
    return out


def declared(body: str) -> tuple[list[tuple[str, str]], str | None, str | None]:
    """`(edges, reason, complaint)` from one principle's body.

    `reason` is set only when the declaration is `none`. `complaint` is the
    first thing wrong with the declaration, or None.
    """
    lines = LINE.findall(body)
    if not lines:
        return [], None, "declares no edges line at all"
    if len(lines) > 1:
        return [], None, f"declares {len(lines)} edges lines; one is the shape"

    value = lines[0]
    if value.lower().startswith("none"):
        rest = value[4:].lstrip(" —-–").strip()
        if len(rest) < REASON_ENOUGH:
            return [], rest, ("declares no edges and gives no reason worth the "
                              "name -- `none` is an answer and an unexplained "
                              "`none` is a shrug")
        return [], rest, None

    edges = []
    for piece in value.split(","):
        piece = piece.strip()
        match = EDGE.match(piece)
        if match is None:
            return [], None, f"cannot read {piece!r} as `<kind> P<n>`"
        kind, other = match.group("kind"), match.group("other")
        if kind not in INVERSES:
            known = ", ".join(sorted(set(INVERSES)))
            return [], None, (f"{kind!r} is not one of the declared kinds. "
                              f"The vocabulary is closed: {known}")
        edges.append((kind, other))
    return edges, None, None


def check(text: str) -> list[str]:
    """Every complaint, in charter order. Empty means the charter is consistent
    with what it declared -- not that the declarations are true."""
    found = principles(text)
    names = {name for name, _, _ in found}
    stated: dict[str, list[tuple[str, str]]] = {}
    problems: list[str] = []

    for name, _, body in found:
        edges, _reason, complaint = declared(body)
        if complaint:
            problems.append(f"{name} {complaint}")
            continue
        stated[name] = edges
        for kind, other in edges:
            if other not in names:
                problems.append(f"{name} names {other}, which is not a principle")
            if other == name:
                problems.append(f"{name} declares an edge to itself")

    # **BOTH ENDS, WHICH IS THE WHOLE MECHANISM.** A one-sided edge is how P4
    # has said it orders P2 since it was written while P2 says nothing -- a
    # reader arriving at P2 never learns it is ordered.
    for name, edges in stated.items():
        for kind, other in edges:
            want = INVERSES[kind]
            back = stated.get(other, [])
            if (want, name) not in back:
                problems.append(
                    f"{name} declares `{kind} {other}` and {other} does not "
                    f"declare `{want} {name}` back")
    return problems


def main() -> int:
    if not CHARTER.is_file():
        print(f"check_principle_edges: {CHARTER} is not here.", file=sys.stderr)
        return 1

    text = CHARTER.read_text(encoding="utf-8")
    found = principles(text)
    problems = check(text)

    for problem in problems:
        print(f"  {problem}")

    if problems:
        print()
        print(f"principle edges: {len(problems)} problem(s) in {len(found)} "
              f"principles.")
        return 1

    isolated = []
    for name, _, body in found:
        edges, reason, _ = declared(body)
        if not edges and reason:
            isolated.append(name)

    print(f"principle edges: {len(found)} principles, every one declares.")
    if isolated:
        print(f"  {len(isolated)} declare no edges, each with a reason: "
              f"{', '.join(isolated)}")
    print("This does NOT mean the relationships are real -- nothing here reads "
          "a principle. It means a stated one is stated from both ends, and an "
          "absent one was a decision somebody wrote down.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
