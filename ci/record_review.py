#!/usr/bin/env python3
"""Review every record as one body, and report what only shows up in aggregate.

Org-level tooling, copied nowhere. `ci/adr_lint.py` checks a record's shape;
this checks the *corpus* — the things no single record can be wrong about on its
own.

FOUR QUESTIONS, EACH FROM A DEFECT THIS CORPUS ACTUALLY SHIPPED:

  enforcement   A record's Enforcement clause names a mechanism. Does it exist,
                and does any gate declare it enforces this record?
                `DRAFT-version-tags-are-claims.md` 7 said its 1 was "mechanical
                rather than customary" and nothing read a tag for six days.

  universals    A universal in a Decision clause, surfaced for a human to read.
                A record states a requirement; a generator reports compliance,
                with a timestamp. `DRAFT-outbound-licensing.md` 12 says "Every
                QM repository is REUSE-compliant" and two repositories have no
                REUSE.toml -- but this corpus also writes requirements
                declaratively, so "Every QM repository carries one walkthrough/"
                is a rule in the same grammar. No pattern separates them. These
                are candidates for reading, never defects.

  citations     A record names a path. Does it exist? A ratified record citing
                a file the corpus does not carry is a dangling reference in
                doctrine.

  orphans       A record nothing points at, from any entry point or any gate.
                Not a defect on its own -- most of this corpus is advisory --
                but it is the set a reader will never reach, which is the
                failure `DRAFT-the-read-document-governs.md` is about.

WHAT THIS CANNOT DO, and it is the larger half:

    **It does not read a record for meaning.** It cannot tell that two records
    contradict each other, that a requirement is wrong, or that a universal
    phrased as a requirement is still a universal. Every finding here is
    structural. The semantic review is a human reading all of them in one
    sitting, and this exists to make that sitting shorter, not to replace it.

Usage:
    python ci/record_review.py
    python ci/record_review.py --strict     # exit non-zero on any finding
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent

# `4. **Enforcement.** ...` or `## Enforcement`, and the paragraph after it.
ENFORCEMENT = re.compile(
    r"(?:^\s*\d+\.\s+\*\*Enforcement\.?\*\*|^##+\s+Enforcement\b)(?P<body>.*?)"
    r"(?=^\s*\d+\.\s+\*\*|^##+\s|\Z)",
    re.M | re.S,
)

# A path in a code span. Restricted to extensions this corpus actually carries,
# so a version string or a URL fragment is not read as a file.
CITED_PATH = re.compile(r"`(?:governance/qm/)?([A-Za-z0-9_][A-Za-z0-9_./-]*\.(?:md|py|ya?ml|json|toml))`")

# "Every QM repository is ...", "every project CI ...". The subject matters:
# these are claims about the state of the world, which a record does not make.
UNIVERSAL = re.compile(
    r"\b(every|all|each)\s+(QM\s+)?(repository|repositories|project|projects)\b"
    r"(?P<rest>[^.]{0,120})",
    re.I,
)

# A universal that is plainly a requirement rather than an assertion reads with
# a modal. "Every project must be X" states a rule; "Every project is X" states
# a fact the record never measured.
REQUIREMENT_MODAL = re.compile(r"\b(must|shall|may not|is required|are required|should)\b", re.I)


DECISION_SECTION = re.compile(r"^##+\s+Decision\b(?P<body>.*?)(?=^##+\s|\Z)", re.M | re.S)


def decision_section(text: str) -> str:
    """The clauses that bind, or "" if the record has no Decision heading.

    >>> decision_section("## Context\\nworld\\n## Decision\\nrule\\n## Consequences\\nx")
    '\\nrule\\n'
    >>> decision_section("## Context\\nonly")
    ''
    """
    match = DECISION_SECTION.search(text)
    return match.group("body") if match else ""


def load_gates(registry: Path) -> list[dict]:
    if not registry.is_file():
        return []
    return (yaml.safe_load(registry.read_text(encoding="utf-8")) or {}).get("gates") or []


def entry_point_text(root: Path) -> str:
    """Everything a reader meets before a record, concatenated."""
    parts = []
    for rel in ("AGENTS.md", "README.md", "PRINCIPLES.md", "project-seed/ide/AGENTS.md"):
        path = root / rel
        if path.is_file():
            parts.append(path.read_text(encoding="utf-8", errors="replace"))
    for path in sorted((root / "handbook").rglob("*.md")):
        parts.append(path.read_text(encoding="utf-8", errors="replace"))
    return "\n".join(parts)


def review_record(path: Path, root: Path, gates: list[dict], reachable: str) -> dict:
    rel = path.relative_to(root).as_posix()
    text = path.read_text(encoding="utf-8", errors="replace")
    findings: list[dict] = []

    # --- enforcement -------------------------------------------------------
    match = ENFORCEMENT.search(text)
    enforcing_gates = [g["id"] for g in gates if rel in (g.get("enforces") or [])]
    if match:
        named = {m.group(1) for m in CITED_PATH.finditer(match.group("body"))}
        missing = sorted(p for p in named if not (root / p).exists())
        for gone in missing:
            findings.append({
                "kind": "enforcement-names-a-missing-mechanism",
                "detail": f"the Enforcement clause names `{gone}`, which is not in the corpus",
            })
        if not named and not enforcing_gates:
            findings.append({
                "kind": "enforcement-clause-names-no-mechanism",
                "detail": "an Enforcement clause that names no path and no gate "
                          "claims to enforce this record",
            })
    elif enforcing_gates:
        findings.append({
            "kind": "enforced-but-does-not-say-so",
            "detail": f"gate(s) {', '.join(enforcing_gates)} declare they enforce this "
                      f"record, which has no Enforcement clause naming them",
        })

    # --- universals --------------------------------------------------------
    # Only the Decision section. A Context section describing the problem
    # ("Every QM project acquires a version number, and nothing says what one
    # means") is stating the world in order to argue about it, and Alternatives
    # quote options being rejected. Scanning the whole record produced 27
    # findings of which most were prose doing its job -- a check that fires on
    # everything trains a reader to skip it, which is worse than one that fires
    # on nothing.
    for m in UNIVERSAL.finditer(decision_section(text)):
        sentence = " ".join(m.group(0).split())
        if REQUIREMENT_MODAL.search(m.group("rest") or ""):
            continue
        findings.append({
            "kind": "universal-to-read-by-hand",
            "detail": f"{sentence!r} -- a universal in a Decision clause. This corpus "
                      f"writes requirements declaratively, so no pattern separates a "
                      f"standing requirement from a claim of current compliance. "
                      f"Read it and decide which it is",
        })

    # --- citations ---------------------------------------------------------
    for m in CITED_PATH.finditer(text):
        cited = m.group(1)
        # `adr/...` is a project's own records directory, which exists on every
        # `project/<name>` branch and on none of `main`. A record naming it is
        # correct; flagging it reports the branch this check runs on.
        if cited.startswith("adr/"):
            continue
        # A bare filename is a name, not a path -- `settings.json` means the one
        # at `.vscode/`. Only flag it if the corpus holds no such file anywhere.
        if "/" not in cited:
            if any(root.rglob(cited)):
                continue
        if not (root / cited).exists():
            findings.append({
                "kind": "dangling-citation",
                "detail": f"names `{cited}`, which is not in the corpus",
            })

    # --- reachability ------------------------------------------------------
    if rel not in reachable and not enforcing_gates:
        findings.append({
            "kind": "unreachable",
            "detail": "no entry point and no gate names this record, so a reader "
                      "arrives at it only by listing the directory",
        })

    return {"record": rel, "gates": enforcing_gates, "findings": findings}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", default=str(ROOT))
    parser.add_argument("--records-dir", default=None)
    parser.add_argument("--strict", action="store_true",
                        help="exit non-zero if any finding is reported")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    records_dir = Path(args.records_dir).resolve() if args.records_dir else root / "records"
    records = sorted(records_dir.glob("DRAFT-*.md")) + sorted(records_dir.glob("QM-*.md"))
    if not records:
        print(f"no records under {records_dir} -- nothing was reviewed", file=sys.stderr)
        return 1

    gates = load_gates(root / "ci" / "gate-registry.yaml")
    reachable = entry_point_text(root)
    results = [review_record(p, root, gates, reachable) for p in records]

    by_kind: dict[str, int] = {}
    for result in results:
        for finding in result["findings"]:
            by_kind[finding["kind"]] = by_kind.get(finding["kind"], 0) + 1

    print(f"Reviewed {len(results)} record(s) as one body.\n")
    for result in results:
        if not result["findings"]:
            continue
        gate_note = f"  [gates: {', '.join(result['gates'])}]" if result["gates"] else ""
        print(f"{result['record']}{gate_note}")
        for finding in result["findings"]:
            print(f"    {finding['kind']}")
            print(f"      {finding['detail']}")
        print()

    clean = [r["record"] for r in results if not r["findings"]]
    if clean:
        print(f"No structural finding against {len(clean)} record(s):")
        for rel in clean:
            print(f"  {rel}")
        print()

    total = sum(by_kind.values())
    if total:
        print("Findings by kind:")
        for kind, count in sorted(by_kind.items(), key=lambda kv: -kv[1]):
            print(f"  {count:>3}  {kind}")
    print(
        f"\n{total} structural finding(s). **None of this is a semantic review** -- "
        "nothing here read a record for meaning, or compared two records for "
        "contradiction. That pass is a human reading all of them in one sitting."
    )
    return 1 if (args.strict and total) else 0


if __name__ == "__main__":
    sys.exit(main())
