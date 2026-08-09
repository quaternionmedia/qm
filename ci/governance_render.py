#!/usr/bin/env python3
"""Render the governance status document as one self-contained HTML page.

SEED FILE, run in place. It reads a document and writes a page. That is the
whole contract.

WHAT THIS MAY NOT DO, and why the list matters more than the features:

  - It may not run git or gh. If a fact is not in the document, this renderer
    does not have it, and the fix is a change to governance_status.py where the
    rule is defined once. A convenience computation here would be a second
    definition of a governance rule, which is the failure the document exists
    to prevent.
  - It may not write to the document. The document is generated; a renderer
    that edits its own input creates a second source of truth for one fact.
  - It may not present a stale document as current. `generated_at` is rendered
    prominently, not in a footer. A dashboard that looks live and is three days
    old is worse than one that admits its age, because the first stops people
    checking.

This is deliberately not the only possible reader. dossier will ingest the same
document into rows; a threshold job can read it and fail a build. Replacing this
file changes nothing about what governance means -- that is the point of it
being a separate file.

Usage:
    governance_render.py governance-status.yaml --out status.html
"""

from __future__ import annotations

import argparse
import html
import sys
from pathlib import Path

# The palette and the three semantic states live in one file, shared with
# ci/harness_dashboard.py. Two governance pages open in one window must not
# be two colour systems, and a state that means `unknown` on one must not
# mean it in a different hue on the other.
from dashboard_style import STYLE

# Semantic state, kept apart from anything decorative. Three states, because
# the third is the one dashboards usually lose: a project nobody could measure
# must not render like a project with nothing wrong.
OK, WARN, UNKNOWN = "ok", "warn", "unknown"


def unknown_reason(value: object) -> str | None:
    """The reason, if this value is the document's unknown form."""
    if isinstance(value, dict) and set(value) == {"unknown"}:
        return str(value["unknown"])
    return None


def esc(value: object) -> str:
    return html.escape("" if value is None else str(value))


def cell(value: object, state: str = OK, title: str = "") -> str:
    reason = unknown_reason(value)
    if reason is not None:
        return f'<td class="s-unknown" title="{esc(reason)}">unknown</td>'
    attrs = f' title="{esc(title)}"' if title else ""
    return f'<td class="s-{state}"{attrs}>{esc(value)}</td>'


def pill(text: str, state: str, title: str = "") -> str:
    attrs = f' title="{esc(title)}"' if title else ""
    return f'<span class="pill p-{state}"{attrs}>{esc(text)}</span>'


def branch_cells(entry: dict) -> tuple[str, int | None]:
    branch = entry.get("branch") or {}
    if unknown_reason(branch) is not None or not isinstance(branch, dict):
        return cell(branch) * 3, None
    behind = branch.get("behind_corpus")
    prop = branch.get("last_propagation")
    behind_state = OK if behind == 0 else WARN
    if unknown_reason(prop) is not None:
        prop_cell = cell(prop)
    elif prop is None:
        prop_cell = f'<td class="s-warn" title="No merge on this branch has a parent contained in the corpus.">never</td>'
    else:
        prop_cell = f'<td class="s-ok">{esc(str(prop.get("committed_at", ""))[:10])}</td>'
    return (
        cell(behind, behind_state, "commits on the corpus branch not on this one")
        + cell(branch.get("ahead_of_corpus"), OK)
        + prop_cell,
        behind if isinstance(behind, int) else None,
    )


def seed_cell(entry: dict) -> str:
    seed = entry.get("seed") or {}
    if not isinstance(seed, dict):
        return cell(seed)
    vs_base = seed.get("adr_template_vs_merge_base")
    reason = unknown_reason(vs_base)
    if reason is not None:
        return cell(vs_base)
    state = OK if vs_base == "match" else WARN
    note = (
        "The copy matches the seed as it stood when this branch last took it."
        if vs_base == "match"
        else "The copy differs from the seed it was taken from -- an edit to a file "
        "that is meant to be verbatim, not merely a seed that has moved since."
    )
    return f'<td class="s-{state}" title="{esc(note)}">{esc(vs_base)}</td>'


def adoption_cell(entry: dict) -> str:
    """Artifacts present, never a verdict.

    There is no `adopted` column because the corpus does not define adoption --
    see the document's own `undefined` block. Rendering one here would be this
    renderer deciding a governance question, which is exactly what it may not do.
    """
    adoption = entry.get("adoption")
    reason = unknown_reason(adoption)
    if reason is not None or not isinstance(adoption, dict):
        return f'<td class="s-unknown" title="{esc(reason or "no data")}">unknown</td>'

    bits = []
    sub = adoption.get("submodule")
    sub_reason = unknown_reason(sub)
    if sub_reason is not None:
        bits.append(pill("submodule?", UNKNOWN, sub_reason))
    elif isinstance(sub, dict):
        if not sub.get("present"):
            bits.append(pill("no submodule", WARN))
        elif not sub.get("tracks_corpus"):
            bits.append(pill("submodule elsewhere", WARN, "a .gitmodules exists but does not carry the governance path"))
        else:
            bits.append(pill(str(sub.get("branch") or "no branch pin"), OK if sub.get("branch") else WARN))

    missing_wf = adoption.get("workflows_missing") or []
    if unknown_reason(missing_wf) is None:
        n = len(missing_wf) if isinstance(missing_wf, list) else 0
        bits.append(pill(f"{3 - n}/3 workflows", OK if n == 0 else WARN, ", ".join(missing_wf) if n else ""))

    missing_ide = adoption.get("ide_missing") or []
    if isinstance(missing_ide, list) and missing_ide:
        bits.append(pill(f"{len(missing_ide)} IDE file(s) missing", WARN, ", ".join(missing_ide)))

    licensing = adoption.get("licensing")
    if isinstance(licensing, list):
        bits.append(pill("REUSE" if "REUSE.toml" in licensing else "no REUSE.toml",
                         OK if "REUSE.toml" in licensing else WARN))
    return "<td>" + " ".join(bits) + "</td>"


def prs_cell(entry: dict) -> str:
    prs = entry.get("open_prs")
    reason = unknown_reason(prs)
    if reason is not None or not isinstance(prs, list):
        return f'<td class="s-unknown" title="{esc(reason or "")}">unknown</td>'
    if not prs:
        return '<td class="s-muted">none</td>'
    links = " ".join(
        f'<span class="pr" title="{esc(pr.get("title"))}">#{esc(pr.get("number"))}'
        f'{" (draft)" if pr.get("draft") else ""}</span>'
        for pr in prs
    )
    return f"<td>{links}</td>"


def render(doc: dict) -> str:
    projects = doc.get("projects") or []
    corpus = doc.get("corpus") or {}
    org = doc.get("org") or {}
    generator = doc.get("generator") or {}
    repositories = org.get("repositories") or {}

    rows = []
    for entry in sorted(projects, key=lambda p: str(p.get("name"))):
        branch_html, behind = branch_cells(entry)
        records = entry.get("records") or {}
        record_cell = (
            cell(records)
            if unknown_reason(records) is not None
            else f'<td>{esc(records.get("total"))}<span class="sub"> / {esc(records.get("ratified"))} ratified</span></td>'
        )
        rows.append(
            "<tr>"
            f'<th scope="row">{esc(entry.get("name"))}</th>'
            + branch_html
            + seed_cell(entry)
            + record_cell
            + adoption_cell(entry)
            + prs_cell(entry)
            + "</tr>"
        )

    undefined = "".join(
        f"<div class='gap'><h3>{esc(g.get('term'))}</h3><p>{esc(g.get('why_not_computed'))}</p>"
        f"<p class='sub'>Settled by: {esc(g.get('would_be_settled_by'))}</p></div>"
        for g in doc.get("undefined") or []
    )

    behind_counts = [
        (p.get("branch") or {}).get("behind_corpus")
        for p in projects
        if isinstance(p.get("branch"), dict)
    ]
    current = sum(1 for b in behind_counts if b == 0)
    never = sum(
        1
        for p in projects
        if isinstance(p.get("branch"), dict) and p["branch"].get("last_propagation") is None
    )

    return TEMPLATE.format(
        generated_at=esc(doc.get("generated_at")),
        corpus_commit=esc(str(corpus.get("commit", ""))[:8]),
        corpus_ref=esc(corpus.get("ref")),
        corpus_at=esc(str(corpus.get("committed_at", ""))[:10]),
        layers=esc(", ".join(generator.get("layers") or [])),
        unknowns=esc(generator.get("unknowns")),
        n_projects=len(projects),
        n_current=current,
        n_never=never,
        records_total=esc((corpus.get("records") or {}).get("total")),
        records_ratified=esc((corpus.get("records") or {}).get("ratified")),
        repos_total=esc(repositories.get("total")),
        repos_governed=esc(repositories.get("governed")),
        rows="\n".join(rows),
        undefined=undefined,
        org_name=esc(generator.get("org")),
        style=STYLE,
    )


TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Governance status — {org_name}</title>
<style>{style}</style>
</head>
<body>
<main>
<h1>Governance status — {org_name}</h1>
<div class="stamp">
  <span>generated <b>{generated_at}</b></span>
  <span>corpus <b class="mono">{corpus_commit}</b> ({corpus_ref}, {corpus_at})</span>
  <span>layers <b>{layers}</b></span>
  <span>unknown fields <b>{unknowns}</b></span>
</div>

<div class="cards">
  <div class="card"><div class="n">{n_projects}</div><div class="l">project branches</div></div>
  <div class="card"><div class="n">{n_current}</div><div class="l">current with corpus</div></div>
  <div class="card"><div class="n">{n_never}</div><div class="l">never propagated</div></div>
  <div class="card"><div class="n">{records_ratified} / {records_total}</div><div class="l">records ratified</div></div>
  <div class="card"><div class="n">{repos_governed} / {repos_total}</div><div class="l">repositories governed</div></div>
</div>

<div class="scroll">
<table>
<thead><tr>
  <th scope="col">project</th>
  <th scope="col">behind</th>
  <th scope="col">ahead</th>
  <th scope="col">last propagation</th>
  <th scope="col">seed vs merge-base</th>
  <th scope="col">records</th>
  <th scope="col">artifacts in its repository</th>
  <th scope="col">open PRs to its branch</th>
</tr></thead>
<tbody>
{rows}
</tbody>
</table>
</div>

<h2>Not computed, because the corpus does not define it</h2>
<p>Each of these would be a column above if a record settled it. They are gaps in
the corpus, not gaps in the measurement.</p>
{undefined}

<footer>
Rendered from <code>governance-status.yaml</code> by
<code>project-seed/ci/governance_render.py</code>. This page derives no governance
fact of its own; every value above is read from that document. Figures in the
github layer are observations at the moment stamped, not continuously verified.
</footer>
</main>
</body>
</html>
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Render the governance status document.")
    parser.add_argument("document", type=Path)
    parser.add_argument("--out", type=Path, help="write here instead of stdout")
    args = parser.parse_args()

    import yaml

    if not args.document.exists():
        # An absent document is a finding, not an empty page. A renderer that
        # draws a clean table when it has nothing to draw from is the failure
        # this whole arrangement is written against.
        print(f"governance render: no document at {args.document}", file=sys.stderr)
        return 2
    doc = yaml.safe_load(args.document.read_text(encoding="utf-8"))
    if not isinstance(doc, dict) or "projects" not in doc:
        print(f"governance render: {args.document} is not a status document", file=sys.stderr)
        return 2

    page = render(doc)
    if args.out:
        args.out.write_text(page, encoding="utf-8", newline="\n")
        print(f"governance render: wrote {args.out} ({len(doc['projects'])} project(s))")
    else:
        sys.stdout.write(page)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
