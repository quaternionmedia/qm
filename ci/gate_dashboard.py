#!/usr/bin/env python3
"""Render the gate status document. Reads a document; writes a page.

Org-level tooling, copied nowhere. Same contract as ci/harness_dashboard.py
and ci/governance_render.py, and the same refusals:

  - It may not run git, gh, or anything else. If a fact is not in the document,
    this renderer does not have it, and the fix is a change to
    ci/gate_status.py where the rule is defined once. A convenience computation
    here would be a second definition of a governance rule, and two definitions
    drift. `ci/tests/test_gate_tooling.py` asserts that no process-spawning
    import appears anywhere in this file -- including in this sentence, which is
    why it is worded around the module name rather than quoting it.
  - It may not write to the document.
  - It may not present a stale document as current. `generated_at` is rendered
    at the top, never in a footer.
  - It may not render an `unknown` as a zero, a blank, or a green tick. A gate
    nobody could measure must not look like a gate with nothing wrong. That is
    the single failure mode a governance dashboard has.

Usage:
    python ci/gate_dashboard.py gate-status.json --format md
    python ci/gate_dashboard.py gate-status.json --out gates.html
    python ci/gate_dashboard.py gate-status.json --format md --check handbook/gates.md
"""

from __future__ import annotations

import argparse
import html
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from dashboard_style import STYLE  # noqa: E402

OK, WARN, UNKNOWN = "ok", "warn", "unknown"

# State is carried in form as well as colour, so a row needing attention
# survives being printed, read in monochrome, or parsed out of the page.
MARK = {OK: "[ok]", WARN: "[!!]", UNKNOWN: "[??]"}


def reason(value: object) -> str | None:
    """The reason, if this value is the document's unknown form."""
    if isinstance(value, dict) and "unknown" in value and len(value) == 1:
        return str(value["unknown"])
    return None


def text_of(value: object) -> str:
    """A prose field, or its unknown reason marked as one."""
    why = reason(value)
    return f"**unknown** — {why}" if why else str(value)


def esc(value: object) -> str:
    return html.escape("" if value is None else str(value))


def enforcement_lines(doc: dict) -> list[str]:
    """The merge boundary, stated as what it is and never as what is hoped."""
    enforcement = doc.get("enforcement") or {}
    why = reason(enforcement)
    if why:
        return [
            f"**Whether anything blocks a merge is unknown** — {why}.",
            "",
            "Not established is not the same as nothing wrong. Every gate below "
            "may or may not be advisory; this document does not know.",
        ]
    if not enforcement.get("blocks_a_merge"):
        return [
            f"**Nothing blocks a merge on `{enforcement.get('repository')}`.** "
            f"The host reports {enforcement.get('rulesets_applied')} ruleset(s) "
            f"and no branch protection on `main`.",
            "",
            "**Every gate below is therefore advisory.** A green check means "
            "*someone was told*, not *this was prevented*. Advisory is a "
            "legitimate state — most governance here is advisory on purpose — "
            "but it is not the same claim, and a reader who conflates them will "
            "trust a merge nobody checked.",
        ]
    return [
        f"The host reports **{enforcement.get('rulesets_applied')} ruleset(s)** "
        f"({', '.join(enforcement.get('ruleset_names') or []) or 'unnamed'}) and "
        f"branch protection "
        f"**{'present' if enforcement.get('branch_protection_on_main') else 'absent'}**.",
        "",
        "Read the ruleset to learn which of the gates below are *required*. This "
        "page does not restate it, because a restatement is a second copy that "
        "drifts.",
    ]


def render_md(doc: dict) -> str:
    out: list[str] = []
    add = out.append
    totals = doc.get("totals") or {}
    reading = doc.get("reading") or {}

    add("# Handbook — The Gates\n")
    add(f"**Generated `{doc.get('generated_at')}`.** Quotable for "
        f"{reading.get('staleness_budget_hours')}h. **Do not edit by hand** — the "
        f"list lives in `ci/gate-registry.yaml`, the document in `gate-status.json`, "
        f"and this page is rendered from the document and nothing else.\n")
    add(f"| | |\n|---|---|")
    add(f"| **Refresh the document** | `{reading.get('refresh')}` |")
    add(f"| **Re-render this page** | `{reading.get('agent_view')} --check handbook/gates.md` |")
    add(f"| **Claim** | `ci/gate-registry.yaml` — what a human says each gate does |")
    add(f"| **Evidence** | `.github/workflows/` — what is on disk |")
    add(f"| **Enforcement** | the host — whether any of it blocks a merge |\n")

    add("## The merge boundary\n")
    out.extend(enforcement_lines(doc))
    add("")

    built, unbuilt = totals.get("built"), totals.get("declared_not_built")
    add(f"**{built} gate{'' if built == 1 else 's'} "
        f"{'is' if built == 1 else 'are'} built; {unbuilt} "
        f"{'is' if unbuilt == 1 else 'are'} declared and not built.** The "
        f"second number is the honest measure of how much of this governance is "
        f"still customary. States: "
        + ", ".join(f"{n} {s}" for s, n in (totals.get("by_state") or {}).items())
        + ".\n")

    add("## Every gate\n")
    add("| | Gate | Stands before | Trigger | Seed | Refuses |")
    add("|---|---|---|---|---|---|")
    for gate in doc.get("gates") or []:
        evidence = gate.get("evidence") or {}
        why = reason(evidence)
        trigger = "—" if why else ", ".join(evidence.get("triggers") or []) or "—"
        add(f"| {MARK.get(gate.get('state'), '[??]')} | `{gate.get('id')}` | "
            f"{', '.join(gate.get('gates') or [])} | {trigger} | "
            f"{'yes' if gate.get('seed') else 'no'} | {text_of(gate.get('refuses'))} |")
    add("")

    not_built = [g for g in (doc.get("gates") or []) if not g.get("declared_built")]
    if not_built:
        add("## Declared, not built\n")
        add("A rule this org has decided on and not yet made mechanical. These "
            "are kept rather than dropped: deleting one to make this page green "
            "is the single edit the registry forbids.\n")
        for gate in not_built:
            add(f"### `{gate.get('id')}` — stands before "
                f"{', '.join(gate.get('gates') or [])}\n")
            add(f"**Would refuse.** {text_of(gate.get('refuses'))}\n")
            if gate.get("note"):
                add(f"**What it would find today.** {gate['note']}\n")

    add("## What each gate cannot see\n")
    add("Read this before quoting a green check. Every defect this corpus has "
        "found in its own tooling was a check that reported success while "
        "enforcing nothing.\n")
    for gate in doc.get("gates") or []:
        add(f"- **`{gate.get('id')}`** — {text_of(gate.get('cannot_see'))}")
    add("")

    add("## What each gate makes mechanical\n")
    add("| Gate | Record or page |\n|---|---|")
    for gate in doc.get("gates") or []:
        enforces = gate.get("enforces") or []
        add(f"| `{gate.get('id')}` | "
            + (", ".join(f"`{e}`" for e in enforces) if enforces
               else "*nothing stated — it guards a habit rather than a decision*")
            + " |")
    add("")

    problems = [g for g in (doc.get("gates") or []) if g.get("state") != OK]
    undeclared = doc.get("undeclared_workflows") or []
    add("## Where claim and evidence disagree\n")
    if not problems and not undeclared:
        add("Nowhere. Every declared workflow is on disk with the job it names, "
            "and every workflow on disk is declared.\n")
    else:
        for gate in problems:
            add(f"- {MARK.get(gate.get('state'))} **`{gate.get('id')}`** — "
                f"{text_of(gate.get('evidence'))}")
        for name in undeclared:
            add(f"- {MARK[WARN]} **`{name}`** is a workflow nobody declared. It is "
                f"not adopted into the list above — a gate this page cannot "
                f"describe is a gate nobody can rely on. Add it to "
                f"`ci/gate-registry.yaml`.")
        add("")

    add("## Reading this document\n")
    for line in reading.get("do_not") or []:
        add(f"- **Do not** {line}.")
    add("")
    return "\n".join(out) + "\n"


def render_html(doc: dict) -> str:
    totals = doc.get("totals") or {}
    rows = []
    for gate in doc.get("gates") or []:
        evidence = gate.get("evidence") or {}
        why = reason(evidence)
        trigger = "&mdash;" if why else esc(", ".join(evidence.get("triggers") or []))
        rows.append(
            f'<tr class="{esc(gate.get("state"))}">'
            f'<td class="mark">{esc(MARK.get(gate.get("state"), "[??]"))}</td>'
            f"<td><code>{esc(gate.get('id'))}</code></td>"
            f"<td>{esc(', '.join(gate.get('gates') or []))}</td>"
            f"<td>{trigger}</td>"
            f"<td>{esc(reason(gate.get('refuses')) or gate.get('refuses'))}</td>"
            f"<td>{esc(reason(gate.get('cannot_see')) or gate.get('cannot_see'))}</td>"
            f"</tr>"
        )
    boundary = "<p>" + "</p><p>".join(
        esc(line) for line in enforcement_lines(doc) if line
    ) + "</p>"
    return (
        "<!doctype html><html lang='en'><head><meta charset='utf-8'>"
        "<meta name='viewport' content='width=device-width,initial-scale=1'>"
        "<title>QM — The Gates</title>"
        f"<style>{STYLE}</style></head><body>"
        "<h1>The Gates</h1>"
        f"<p class='stamp'>Generated {esc(doc.get('generated_at'))} &middot; "
        f"quotable for {esc((doc.get('reading') or {}).get('staleness_budget_hours'))}h</p>"
        f"<h2>The merge boundary</h2>{boundary}"
        f"<p><strong>{esc(totals.get('built'))}</strong> built, "
        f"<strong>{esc(totals.get('declared_not_built'))}</strong> declared and not built.</p>"
        "<table><thead><tr><th></th><th>Gate</th><th>Stands before</th>"
        "<th>Trigger</th><th>Refuses</th><th>Cannot see</th></tr></thead>"
        f"<tbody>{''.join(rows)}</tbody></table>"
        "</body></html>\n"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("document")
    parser.add_argument("--format", choices=("md", "html"), default=None)
    parser.add_argument("--out", help="write here instead of stdout")
    parser.add_argument("--check", help="fail if this path differs from a fresh render")
    args = parser.parse_args(argv)

    path = Path(args.document)
    if not path.is_file():
        print(f"{args.document}: not present.", file=sys.stderr)
        return 1
    doc = json.loads(path.read_text(encoding="utf-8"))

    fmt = args.format or ("html" if (args.out or "").endswith(".html") else "md")
    page = render_html(doc) if fmt == "html" else render_md(doc)

    if args.check:
        target = Path(args.check)
        if not target.is_file():
            print(f"{args.check}: not present.", file=sys.stderr)
            return 1
        # Newlines normalised: a checkout that translated line endings would
        # otherwise report drift that is entirely encoding, which has produced
        # a false finding in this repository before.
        if target.read_text(encoding="utf-8").replace("\r\n", "\n") != page.replace("\r\n", "\n"):
            print(f"{args.check} has drifted from {args.document}.", file=sys.stderr)
            return 1
        print(f"{args.check} matches {args.document}.")
        return 0

    if args.out:
        Path(args.out).write_text(page, encoding="utf-8", newline="\n")
        print(f"wrote {args.out}")
        return 0

    sys.stdout.write(page)
    return 0


if __name__ == "__main__":
    sys.exit(main())
