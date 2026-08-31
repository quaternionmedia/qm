"""Every principle declares how it relates to the others, or that it does not.

**A PRINCIPLE THAT NOTHING POINTS AT IS A PRINCIPLE NOTHING WILL BE CHECKED
AGAINST.** Measured on 2026-08-25, before this check existed: six of seventeen
principles were named by nobody and named nobody -- `seams-on-standard-protocols`, `one-house-stack`, `minimal-legible-deliverables`, `credit-tracks-accountability`, `governance-finds-the-reader`, `a-loop-is-not-a-knot`.
`credit-tracks-accountability` was among them, and `credit-tracks-accountability` is the one that says a tool is an instrument a human
directs rather than a party who can answer for the result.

A draft of `shrink-the-black-box` then said the model "is what writes the check", which contradicts
`credit-tracks-accountability` in its central sentence. Nothing surfaced it. `check_restatements.py` pairs a
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
`a-loop-is-not-a-knot` refuses. A free string would let a typo become a category.

WHAT THIS CANNOT DO. Tell whether two principles actually conflict. It checks
that a relationship somebody stated is stated from both ends and uses a word from
the list. Whether `shrink-the-black-box` really rests on `credit-tracks-accountability` is a reading, and no script has one.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

CHARTER = Path("PRINCIPLES.md")

# The four kinds, read off relationships already in the charter's prose rather
# than imagined. Each maps to the word its other end must use.
#
#   orders        a tension resolved by precedence.   `build-the-seam-buy-the-engines` orders `commons-first-economics`, and `build-the-seam-buy-the-engines`'s own
#                 text has said so since it was written.
#   completes     supplies a half the other was missing. `typing-schedules-interface-work` -> `interrupted-only-by-a-decision`, in those
#                 words.
#   shares-teeth  enforced through the other's mechanism. `systems-over-heroics` -> `ownership-is-the-deliverable`. Symmetric:
#                 sharing is mutual and there is no direction to name.
#   rests-on      the claim is false unless the other holds. `shrink-the-black-box` -> `credit-tracks-accountability`.
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

# `↔ Edges: rests-on credit-tracks-accountability, completes show-it-by-running-it`
# `↔ Edges: none -- <reason>`
#
# A PRINCIPLE IS ADDRESSED BY ITS NAME, NOT BY AN ORDINAL. A heading carried a
# position where it now carries a name, and every reference in the corpus
# addressed the position. An ordinal is a claim about where a thing sits, so
# inserting a principle anywhere but the end reaims every reference below it --
# and nothing here could have noticed, because a reference to a position that
# has shifted is still well-formed and resolves to the wrong principle rather
# than to none. A name moves with the thing it names, so the same edit leaves
# every reference either correct or visibly dangling.
#
# `kind` and `other` are now the same shape, which is why the whitespace
# between them is required rather than optional: `rests-on show-it-by-running-it`
# splits on the space and nowhere else.
LINE = re.compile(r"^↔ Edges:\s*(?P<value>.+?)\s*$", re.MULTILINE)
HEADING = re.compile(r"^## (?P<name>[a-z][a-z0-9-]*) — (?P<title>.*)$", re.MULTILINE)
EDGE = re.compile(r"^(?P<kind>[a-z-]+)\s+(?P<other>[a-z][a-z0-9-]*)$")

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
            return [], None, f"cannot read {piece!r} as `<kind> <principle-name>`"
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

    # **BOTH ENDS, WHICH IS THE WHOLE MECHANISM.** A one-sided edge is how `build-the-seam-buy-the-engines`
    # has said it orders `commons-first-economics` since it was written while `commons-first-economics` says nothing -- a
    # reader arriving at `commons-first-economics` never learns it is ordered.
    for name, edges in stated.items():
        for kind, other in edges:
            want = INVERSES[kind]
            back = stated.get(other, [])
            if (want, name) not in back:
                problems.append(
                    f"{name} declares `{kind} {other}` and {other} does not "
                    f"declare `{want} {name}` back")
    return problems


# An ordinal reference to a principle, in any document that still binds.
ORDINAL = re.compile(r"\bP(?:1[0-7]|[1-9])\b")

# The escape hatch, and it costs a stated reason -- the same shape and the same
# price as `adr_lint.py`'s. It exists because a document that *names* the
# forbidden form in order to forbid it is describing the rule rather than
# breaking it, and this file is the first such document. Stripping code spans
# instead was the other option and it was rejected: a backticked name is how
# this corpus writes a principle reference, so a guard blind to backticks would
# be blind to the most likely way a stale one gets written.
ORDINAL_ALLOWED = re.compile(
    r"principle-name:\s*allow\s+(?P<quoted>\S.*?)\s*(?:-->|$)", re.IGNORECASE
)

# Where a principle reference has to be a name. Everything else in the
# repository is outside this scan, and two directories are outside it on
# purpose rather than by omission -- see `ordinal_references`.
BINDING = ("AGENTS.md", "README.md", "records", "handbook", "docs", "ci",
           "project-seed", "plans", "protocols", "curriculum", "walkthrough")
NOT_BINDING = ("perspectives/", "handbook/handoffs/", "__pycache__", ".venv/")
READABLE = (".md", ".py", ".yaml", ".yml", ".json")


def ordinal_references(root: Path) -> list[str]:
    """Every place a binding document still addresses a principle by position.

    WHAT THIS DELIBERATELY DOES NOT READ. `perspectives/` is dated, attributed,
    non-binding opinion: a retrospective records what somebody wrote on a day,
    and editing one to match a later renaming would falsify the thing its value
    depends on. `handbook/handoffs/` is transient by its own definition --
    deleted when the work lands -- so a handoff is left as its author left it.
    Both exclusions mean an ordinal survives in this repository, and reading a
    green result here as "no ordinal anywhere" is wrong.

    Symlinks are skipped because writing through one writes the target, and the
    target is scanned on its own.

    Mutation: write a bare ordinal principle reference anywhere under
    `records/` -- the old charter-position form -- and this fails. Verified by
    doing it, on the record behind the evidence principle, which is the one
    whose own subject this is.
    """
    problems = []
    allowed = 0
    for entry in BINDING:
        base = root / entry
        paths = [base] if base.is_file() else sorted(
            p for p in base.rglob("*") if p.is_file() and p.suffix in READABLE
        ) if base.is_dir() else []
        for path in paths:
            rel = path.relative_to(root).as_posix()
            if any(part in rel for part in NOT_BINDING) or path.is_symlink():
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            for number, line in enumerate(text.splitlines(), start=1):
                for hit in ORDINAL.finditer(line):
                    reason = ORDINAL_ALLOWED.search(line)
                    if reason is None:
                        problems.append(
                            f"{rel}:{number}: addresses a principle as "
                            f"{hit.group(0)!r}. A principle is addressed by its "
                            f"name -- an ordinal reaims itself when one is "
                            f"inserted above it, and stays well-formed while it "
                            f"does. If this names the form in order to forbid "
                            f"it, annotate the line: "
                            f"principle-name: allow \"why this is not a reference\""
                        )
                    elif not reason.group("quoted").strip("\"'"):
                        problems.append(
                            f"{rel}:{number}: an exemption states a reason. An "
                            f"empty one is the check turned off."
                        )
                    else:
                        allowed += 1
    if allowed:
        print(f"principle names: {allowed} ordinal(s) allowed by a stated "
              f"reason. Each is a place the form is named in order to refuse it.")
    return problems


def main() -> int:
    if not CHARTER.is_file():
        print(f"check_principle_edges: {CHARTER} is not here.", file=sys.stderr)
        return 1

    text = CHARTER.read_text(encoding="utf-8")
    found = principles(text)
    problems = check(text) + ordinal_references(Path("."))

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
