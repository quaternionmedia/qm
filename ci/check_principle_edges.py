"""Every principle declares how it relates to the others, or that it does not.

Each principle in `PRINCIPLES.md` carries an `↔ Edges:` line: one or more
edges to other principles, each stated from both ends, or `none` with a reason.
An edge is never required; a declaration is. The vocabulary of edge kinds is
closed and every kind has a declared inverse, as `dossier.composition.RELATIONS`
does in `ci/mathematics-registry.yaml`. `ordinal_references` also refuses a
binding document that addresses a principle by position rather than by name.

`docs/ref/ci/gates-and-checks.md` describes the declaration and why `none` is a
first-class answer.

What this cannot do: tell whether two principles actually conflict. It checks
that a stated relationship is stated from both ends and uses a word from the
list. Whether `shrink-the-black-box` really rests on
`credit-tracks-accountability` is a reading, and no script has one.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

CHARTER = Path("PRINCIPLES.md")

# The four kinds, read off relationships already in the charter's prose rather
# than imagined. Each maps to the word its other end must use.
#
#   orders        a tension resolved by precedence. `build-the-seam-buy-the-engines`
#                 orders `commons-first-economics`, in its own text.
#   completes     supplies a half the other lacks. `typing-schedules-interface-work`
#                 -> `interrupted-only-by-a-decision`, in those words.
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
# A principle is addressed by its name, not by an ordinal. A reference to a
# position that has shifted still resolves, to the wrong principle; a name
# moves with the thing it names, so a reference is either correct or visibly
# dangling.
#
# `kind` and `other` are the same shape, so the whitespace between them is
# required: `rests-on show-it-by-running-it` splits on the space and nowhere
# else.
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

    # Both ends: a reader arriving at the other end of a one-sided edge never
    # learns the edge exists.
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

# The escape hatch costs a stated reason, the same shape and price as
# `adr_lint.py`'s, for a document that names the forbidden form in order to
# forbid it. Code spans are scanned rather than stripped, because a backticked
# name is how this corpus writes a principle reference.
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

    Not read: `perspectives/`, which is dated opinion that a later renaming
    must not edit, and `handbook/handoffs/`, which is transient. An ordinal can
    therefore survive in this repository, and a green result here does not mean
    "no ordinal anywhere". Symlinks are skipped, because the target is scanned
    on its own.

    The pattern is a proxy: the letter-and-number form is not reserved to the
    charter, and a plan that numbers its own work packages the same way
    matches it. The annotation is therefore honoured at file scope as well as
    line scope, declared once at the top of a document whose own vocabulary
    collides.

    Mutation: write a bare ordinal principle reference anywhere under
    `records/` and this fails.
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
            # A file-scope annotation covers a document whose own vocabulary
            # uses the same shape. It is read from the first few lines only, so
            # it has to be declared where a reader meets it rather than buried
            # where only the tool would find it.
            head = "\n".join(text.splitlines()[:5])
            file_reason = ORDINAL_ALLOWED.search(head)
            if file_reason is not None and file_reason.group("quoted").strip("\"'"):
                if ORDINAL.search(text):
                    allowed += 1
                continue
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
