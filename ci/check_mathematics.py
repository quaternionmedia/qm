"""Every mathematical mapping states what it decides and what it has not earned.

    python ci/check_mathematics.py

`PRINCIPLES.md` P15 and `records/DRAFT-a-knot-is-a-cycle-of-obligation.md` say
the mathematics a layer has is looked for on purpose. This is what stops that
becoming a habit of naming things after theorems.

**IT CHECKS THE SHAPE OF A CLAIM, NEVER THE MATHEMATICS.** Nothing here knows
what a knot is. It asks whether an entry claiming to be `earned` names the
measurement that earned it, whether an entry that decides nothing is honest
enough to say `decorative`, and whether every entry names what it has *not* got.
A registry where every mapping is earned and nothing is unearned is a registry
nobody is being honest in, and that is the failure this is pointed at.

**THE `unearned` FIELD IS THE ONE THAT MATTERS.** An entry with nothing unearned
is either a finished mapping -- which is rare enough to be worth arguing about --
or somebody who stopped looking. Requiring it keeps the practice evolving rather
than congratulating itself, which is why it is mandatory even for `decorative`
entries.
"""

from __future__ import annotations

import sys
from pathlib import Path

EARNED, DECORATIVE, ASPIRATIONAL = "earned", "decorative", "aspirational"
STATES = (EARNED, DECORATIVE, ASPIRATIONAL)

REQUIRED = ("layer", "structure", "state", "decides", "measured", "unearned",
            "next")

# Short enough to be a placeholder rather than an answer. A field somebody
# filled in with a word to get past the check is worse than an empty one,
# because an empty one is visible.
TOO_SHORT = 12


def _duplicate_keys(raw: str) -> list[str]:
    """Fields stated twice in one entry.

    **YAML TAKES THE LAST AND SAYS NOTHING**, so a second `measured:` silently
    replaces the first and the checker reads a value nobody meant to be the
    answer. Found while mutating this registry to test the guards: an inserted
    duplicate looked like it had changed the entry and had not, which read as a
    guard failing to fire.

    Text rather than the parsed document, because by the time it is parsed the
    duplicate is gone -- which is exactly the problem.
    """
    found: list[str] = []
    seen: set[str] = set()
    for number, line in enumerate(raw.splitlines(), start=1):
        stripped = line.strip()
        if stripped.startswith("- "):
            seen = set()
            stripped = stripped[2:]
        if not stripped or stripped.startswith("#") or ":" not in stripped:
            continue
        if not line.startswith(("    ", "  - ")):
            continue
        key = stripped.split(":", 1)[0].strip()
        if key in REQUIRED:
            if key in seen:
                found.append(f"line {number}: {key} is stated twice in one "
                             f"entry; YAML keeps the last and drops the first")
            seen.add(key)
    return found


def check(path: Path) -> list[str]:
    """Every problem with the registry, or an empty list."""
    import yaml

    if not path.is_file():
        return [f"{path} is not there"]

    raw = path.read_text(encoding="utf-8")
    document = yaml.safe_load(raw) or {}
    mappings = document.get("mappings") or []
    if not mappings:
        return [f"{path} lists no mappings, so this check asserts nothing"]

    problems: list[str] = _duplicate_keys(raw)
    seen: set[str] = set()

    for index, entry in enumerate(mappings):
        where = entry.get("layer") or f"entry {index}"

        for field in REQUIRED:
            value = entry.get(field)
            if value is None or not str(value).strip():
                problems.append(f"{where}: no {field}")
                continue
            if field in ("decides", "measured", "unearned", "next"):
                if len(str(value).strip()) < TOO_SHORT and str(value).strip() not in (
                        "none", "nothing"):
                    problems.append(
                        f"{where}: {field} is too short to be an answer -- "
                        f"{value!r}")

        if where in seen:
            problems.append(f"{where}: two entries claim this layer")
        seen.add(where)

        state = str(entry.get("state") or "").strip()
        if state and state not in STATES:
            problems.append(f"{where}: state {state!r} is not one of {STATES}")

        decides = str(entry.get("decides") or "").strip().lower()
        measured = str(entry.get("measured") or "").strip().lower()
        unearned = str(entry.get("unearned") or "").strip().lower()

        # An earned mapping decided something, and named what did the deciding.
        if state == EARNED:
            if measured in ("none", "nothing", ""):
                problems.append(
                    f"{where}: claims to be earned and names no measurement. "
                    f"Earned means a measurement decided something")
            if decides in ("nothing", "none", ""):
                problems.append(
                    f"{where}: claims to be earned and decides nothing. A "
                    f"mapping that settles nothing is decorative, and saying "
                    f"so is not a demotion")

        # A decorative one is honest about deciding nothing.
        if state == DECORATIVE and decides not in ("nothing", "none"):
            problems.append(
                f"{where}: is decorative and claims to decide {decides!r}. If "
                f"it decides something it is not decorative; if it does not, "
                f"say `nothing`")

        # An aspirational one has not been measured yet, by definition.
        if state == ASPIRATIONAL and measured not in ("none", "nothing", ""):
            problems.append(
                f"{where}: is aspirational and names a measurement. A measured "
                f"mapping is earned or it failed; either way it is not still "
                f"aspirational")

        # THE ONE THAT KEEPS THIS HONEST.
        if unearned in ("nothing", "none", "n/a"):
            problems.append(
                f"{where}: nothing unearned. Either this mapping is complete, "
                f"which is worth arguing about in a record, or somebody "
                f"stopped looking")

    return problems


def main() -> int:
    path = Path(__file__).resolve().parent / "mathematics-registry.yaml"
    problems = check(path)

    import yaml

    document = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    mappings = document.get("mappings") or []
    counts = {state: sum(1 for m in mappings
                         if str(m.get("state", "")).strip() == state)
              for state in STATES}

    if problems:
        print(f"mathematics registry: {len(problems)} problem(s)\n")
        for problem in problems:
            print(f"  {problem}")
        return 1

    print(f"mathematics registry: {len(mappings)} mapping(s) -- "
          + ", ".join(f"{n} {state}" for state, n in counts.items()))
    print("Every one names what it decides, what measured it, and what it has "
          "not earned.")
    print("This does NOT mean a mapping is correct -- nothing here knows what "
          "a knot is. It means the claim is shaped so somebody can check it.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
