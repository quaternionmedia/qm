#!/usr/bin/env python3
"""Render the harness status document as one self-contained HTML page.

Org-level tooling, copied nowhere. It reads a document and writes a page. That
is the whole contract, and it is the same contract ci/governance_render.py has.

WHAT THIS MAY NOT DO, and why the list matters more than the features:

  - It may not run git, gh, or anything else. If a fact is not in the document,
    this renderer does not have it, and the fix is a change to
    ci/harness_status.py where the rule is defined once. A convenience
    computation here would be a second definition of a governance rule.
  - It may not write to the document.
  - It may not present a stale document as current. `generated_at` is rendered
    at the top, not in a footer. A dashboard that looks live and is three days
    old is worse than one that admits its age, because the first stops people
    checking.
  - It may not render an unknown as a zero, a blank, or a green tick. A
    repository nobody could measure must not look like a repository with
    nothing wrong. That is the single failure mode a governance dashboard has.

Usage:
    python ci/harness_dashboard.py harness-status.json --out harness.html
"""

from __future__ import annotations

import argparse
import html
import json
import sys
from pathlib import Path

# Run as a script, `ci/` is on the path and the bare import resolves. Imported
# as `ci.harness_dashboard` -- which is what a `qm` route does -- it does not,
# and the module fails at import with a name that says nothing about the cause.
# `gate_dashboard.py` has carried this line since it was routed; this one had no
# route, so nothing ever imported it and the gap sat unnoticed.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from dashboard_style import STYLE  # noqa: E402

OK, WARN, UNKNOWN = "ok", "warn", "unknown"

LINE_BREAK = chr(10)


def esc(value: object) -> str:
    return html.escape("" if value is None else str(value))


def unknown_reason(value: object) -> str | None:
    """The reason, if this value is the document's unknown form."""
    if isinstance(value, dict) and "unknown" in value and len(value) == 1:
        return str(value["unknown"])
    return None


def pill(text: str, state: str) -> str:
    return f'<span class="pill p-{state}">{esc(text)}</span>'


def slot_cell(slots: dict) -> tuple[str, str]:
    """(cell HTML, row class) for one repository's slot state."""
    reason = unknown_reason(slots)
    if reason is not None:
        return (
            f'<td class="s-unknown" title="{esc(reason)}">unknown</td>',
            "unmeasured",
        )
    if slots.get("violations"):
        numbers = []
        for violation in slots["violations"]:
            where = f" against {violation['base']}" if violation.get("base") else ""
            listed = ", ".join(f"#{n}" for n in violation["numbers"])
            numbers.append(f"{esc(violation['author'])} holds {listed}{esc(where)}")
        return (
            "<td>"
            + pill("over limit", WARN)
            + '<div class="sub">'
            + "<br>".join(numbers)
            + "</div></td>",
            "over",
        )
    return f"<td>{pill('one slot each', OK)}</td>", ""


def local_cell(local: object) -> str:
    reason = unknown_reason(local)
    if reason is not None:
        return f'<td class="s-unknown" title="{esc(reason)}">unknown</td>'
    if not isinstance(local, dict):
        return '<td class="s-muted">not collected</td>'

    bits = [f'<span class="mono">{esc(local.get("branch"))}</span>']
    flags = []
    if local.get("dirty"):
        flags.append(pill(f"{local['dirty']} uncommitted", WARN))
    if local.get("upstream") is None:
        flags.append(pill("no upstream", WARN))
    elif local.get("ahead"):
        flags.append(pill(f"{local['ahead']} unpushed", WARN))
    if not flags:
        flags.append(pill("clean", OK))
    bits.append('<div class="sub">' + " ".join(flags) + "</div>")
    return "<td>" + "".join(bits) + "</td>"


def phase_cell(phase: str, source: str) -> str:
    """The claim, with its provenance attached.

    The provenance is not decoration. `scaffolded` means nobody decided this --
    the ladder's floor applied because nothing was stated -- and a table that
    renders it identically to a phase somebody chose has turned a default into
    a finding.
    """
    if phase == UNKNOWN:
        return '<td class="s-unknown">unknown</td>'
    if phase == "n/a":
        return '<td class="s-muted">—</td>'
    label = {
        "stated": '<div class="sub">stated</div>',
        "scaffolded": '<div class="sub s-unknown">scaffolded — nobody decided this</div>',
    }.get(source, f'<div class="sub s-unknown">{esc(source)}</div>')
    return f'<td><span class="mono">{esc(phase)}</span>{label}</td>'


def governance_cell(governance: object) -> str:
    """What has landed, never what was claimed.

    A complete artifact set renders as `precondition met`, which is the whole
    claim this column is entitled to make: it means a human may now assert
    v0.0.1, not that anybody has.
    """
    reason = unknown_reason(governance)
    if reason is not None:
        return f'<td class="s-unknown" title="{esc(reason)}">unknown</td>'
    if not isinstance(governance, dict):
        return '<td class="s-muted">not collected</td>'
    state = governance.get("precondition")
    if state == "n/a":
        return '<td class="s-muted">—</td>'
    if state == "met":
        return f"<td>{pill('precondition met', OK)}</td>"
    missing = ", ".join(governance.get("missing") or [])
    return (
        "<td>"
        + pill("incomplete", WARN)
        + f'<div class="sub">missing: {esc(missing)}</div></td>'
    )


def pr_counts(slots: dict) -> str:
    if unknown_reason(slots) is not None:
        return '<td class="s-unknown">unknown</td>'
    prs = slots.get("open_prs", [])
    human = sum(1 for p in prs if not p.get("bot"))
    bot = len(prs) - human
    return (
        f"<td>{human}"
        + (f'<span class="s-muted"> + {bot} bot</span>' if bot else "")
        + "</td>"
    )


def render(document: dict, fragment: bool = False) -> str:
    generator = document.get("generator", {})
    totals = document.get("totals", {})
    repositories = document.get("repositories", [])

    rows = []
    for repo in repositories:
        slots = repo.get("slots", {})
        cell, row_class = slot_cell(slots)
        rows.append(
            f'<tr class="{row_class}">'
            f'<th scope="row">{esc(repo.get("name"))}'
            f'<div class="sub">{esc(repo.get("role"))}</div></th>'
            + phase_cell(
                str(repo.get("phase", UNKNOWN)), str(repo.get("phase_source", UNKNOWN))
            )
            + governance_cell(repo.get("governance"))
            + pr_counts(slots)
            + cell
            + local_cell(repo.get("local"))
            + "</tr>"
        )

    over = [
        r
        for r in repositories
        if unknown_reason(r.get("slots", {})) is None and r["slots"].get("violations")
    ]
    unmeasured = [
        r for r in repositories if unknown_reason(r.get("slots", {})) is not None
    ]
    # A claim above governance, where governance itself is not evidenced. This
    # is the gap the ladder exists to keep visible: the rung was named in a
    # session, its definition lives in no record, and the rung below it has not
    # landed. None of those three facts is a failure on its own.
    ahead_of_evidence = []
    for repo in repositories:
        if str(repo.get("phase_source")) != "stated":
            continue
        if str(repo.get("phase", "")) <= "v0.0.1":
            continue
        governance = repo.get("governance")
        reason = unknown_reason(governance)
        if reason is not None:
            ahead_of_evidence.append((repo, reason))
        elif isinstance(governance, dict) and governance.get("precondition") != "met":
            ahead_of_evidence.append(
                (repo, "v0.0.1 missing: " + ", ".join(governance.get("missing") or []))
            )

    unplaced = [
        r
        for r in repositories
        if str(r.get("phase", UNKNOWN)) == UNKNOWN
        and unknown_reason(r.get("local", {})) is None
    ]

    over_html = (
        "".join(
            f'<div class="gap"><h3>{esc(r["name"])}</h3>'
            + "".join(
                f"<p>{esc(v['author'])} holds "
                + ", ".join(f"#{n}" for n in v["numbers"])
                + (f" against <span class=\"mono\">{esc(v['base'])}</span>" if v.get("base") else "")
                + ". One stays open; the rest are closed or folded into it.</p>"
                for v in r["slots"]["violations"]
            )
            + "</div>"
            for r in over
        )
        or "<p class=\"s-ok\">Every contributor holds at most one slot, in every "
        "repository this document could read.</p>"
    )

    unplaced_html = (
        "".join(
            f'<p><b>{esc(r["name"])}</b>'
            + (f' — {esc(r["note"])}' if r.get("note") else "")
            + "</p>"
            for r in unplaced
        )
        or "<p class=\"s-ok\">Every repository present carries a phase.</p>"
    )

    ahead_html = (
        "".join(
            f'<div class="gap"><h3>{esc(repo["name"])} — {esc(repo["phase"])} stated</h3>'
            f"<p>{esc(why)}</p>"
            "<p>What this rung asserts belongs in this project's own records. "
            "Until it is written there, the phase is a statement of intent.</p>"
            "</div>"
            for repo, why in ahead_of_evidence
        )
        or '<p class="s-ok">No project claims a rung above governance without '
        "governance evidence behind it.</p>"
    )

    unmeasured_html = (
        "".join(
            f'<p><b>{esc(r["name"])}</b> — {esc(unknown_reason(r["slots"]))}</p>'
            for r in unmeasured
        )
        or "<p>Every repository in the roster was read.</p>"
    )

    stages = totals.get("threads_by_stage") or {}
    thread_html = []
    for thread in thread_rows(document):
        state, meaning = STAGE_STATE.get(thread.get("stage"), (UNKNOWN, "unknown stage"))
        flag = pill("stalled", WARN) if thread.get("stalled") else ""
        where = f"#{esc(thread['pr'])}" if thread.get("pr") else "&mdash;"
        thread_html.append(
            f'<tr class="{"over" if thread.get("stalled") else ""}">'
            f'<th scope="row">{esc(thread.get("repository"))}</th>'
            f'<td><span class="mono">{esc(thread.get("name"))}</span>'
            f'<div class="sub">onto {esc(thread.get("base") or "unknown")}'
            f' &middot; {esc(thread.get("scope"))}</div></td>'
            f"<td>{pill(esc(thread.get('stage')), state)}"
            f'<div class="sub">{esc(meaning)}</div></td>'
            f"<td>{esc(delta_text(thread.get('delta')))}</td>"
            f"<td>{esc(idle_text(thread.get('idle_hours')))} {flag}</td>"
            f"<td>{where}</td></tr>"
        )
    threads_table = LINE_BREAK.join(thread_html) or (
        '<tr><td colspan="6" class="s-muted">No threads in flight.</td></tr>'
    )

    threads_note = "".join(
        f'<p class="reason">{esc(r["name"])}: threads '
        f'{esc(unknown_reason(r["threads"]))}</p>'
        for r in repositories
        if unknown_reason(r.get("threads")) is not None
    )

    scope = generator.get("local_layer_scope")
    scope_html = (
        f'<p class="reason">The machine column is {esc(scope)}. Nothing in it is '
        "an organisation-level fact, and a second person running this would see "
        "different values for the same repositories.</p>"
        if scope
        else '<p class="reason">The machine layer was not collected.</p>'
    )

    return (FRAGMENT if fragment else TEMPLATE).format(
        style=STYLE,
        org=esc(generator.get("org")),
        generated_at=esc(document.get("generated_at")),
        rule=esc(generator.get("rule")),
        rule_source=esc(generator.get("rule_source")),
        exemption=esc(", ".join(generator.get("corpus_exemption") or []) or "none"),
        n_repos=esc(totals.get("repositories")),
        n_compliant=esc(totals.get("compliant")),
        n_over=esc(totals.get("over_limit")),
        n_unknown=esc(totals.get("slots_unknown")),
        n_unplaced=len(unplaced),
        n_met=esc(totals.get("governance_precondition_met")),
        n_readable=esc(totals.get("governance_readable")),
        n_scaffolded=esc(totals.get("phase_scaffolded")),
        ladder_source=esc(generator.get("phase_ladder_source") or "unstated"),
        rows="\n".join(rows),
        threads=threads_table,
        threads_note=threads_note,
        n_pushed=esc(stages.get("pushed", 0)),
        n_local=esc(stages.get("local", 0)),
        n_draft=esc(stages.get("draft", 0)),
        n_ready=esc(stages.get("ready", 0)),
        n_stalled=esc(totals.get("threads_stalled", 0)),
        stalled_after=esc(generator.get("stalled_after_hours")),
        over=over_html,
        unplaced=unplaced_html,
        ahead=ahead_html,
        unmeasured=unmeasured_html,
        scope=scope_html,
    )


# BODY is the page itself; TEMPLATE is BODY inside a document.
#
# Kept apart so `--fragment` can emit the same page for a host that supplies
# its own document shell -- an artifact publisher, a docs site, a dossier panel
# -- without a second copy of the markup to keep in step. The stylesheet
# travels with the fragment: a host cannot be assumed to carry this palette,
# and a page that inherits an unknown one renders its three semantic states as
# three shades of whatever the host chose.
BODY = """<main>
<h1>Harness status — {org}</h1>
<div class="stamp">
  <span>generated <b>{generated_at}</b></span>
  <span>rule <b>{rule}</b></span>
  <span>defined in <b class="mono">{rule_source}</b></span>
  <span>corpus exemption <b class="mono">{exemption}</b></span>
</div>

<div class="cards">
  <div class="card"><div class="n">{n_repos}</div><div class="l">repositories</div></div>
  <div class="card"><div class="n s-ok">{n_compliant}</div><div class="l">within the rule</div></div>
  <div class="card"><div class="n s-warn">{n_over}</div><div class="l">over the limit</div></div>
  <div class="card"><div class="n s-unknown">{n_unknown}</div><div class="l">could not read</div></div>
  <div class="card"><div class="n">{n_met} <span class="s-muted">/ {n_readable}</span></div><div class="l">v0.0.1 precondition</div></div>
  <div class="card"><div class="n s-unknown">{n_scaffolded}</div><div class="l">phase scaffolded</div></div>
</div>

<div class="scroll">
<table>
<thead><tr>
  <th scope="col">Repository</th>
  <th scope="col">Phase <span class="s-muted">(claimed)</span></th>
  <th scope="col">v0.0.1 governance <span class="s-muted">(evidence)</span></th>
  <th scope="col">Open PRs</th>
  <th scope="col">Slot</th>
  <th scope="col">This machine</th>
</tr></thead>
<tbody>
{rows}
</tbody>
</table>
</div>
<div class="legend">
  <span><span class="pill p-ok">ok</span> measured, within the rule</span>
  <span><span class="pill p-warn">warn</span> measured, needs a human</span>
  <span><span class="pill p-unknown">unknown</span> not measured — not the same as nothing wrong</span>
</div>

<h2>Threads in flight</h2>
<p>One line of work each: a branch, and the pull request it became if it became
one. The stages are <b>observable states, not progress</b> &mdash; nothing here
estimates completion, because the corpus has no definition of done a tool could
read. Sorted worst first: stalled before idle, and <b>pushed</b> before draft,
because a branch on a remote with no pull request is work nobody has been told
about. Stalled means untouched for more than {stalled_after}h.</p>

<div class="cards">
  <div class="card"><div class="n s-warn">{n_pushed}</div><div class="l">pushed, no PR</div></div>
  <div class="card"><div class="n s-warn">{n_local}</div><div class="l">local only</div></div>
  <div class="card"><div class="n">{n_draft}</div><div class="l">draft PR</div></div>
  <div class="card"><div class="n">{n_ready}</div><div class="l">ready for review</div></div>
  <div class="card"><div class="n s-warn">{n_stalled}</div><div class="l">stalled</div></div>
</div>

<div class="scroll">
<table>
<thead><tr>
  <th scope="col">Repository</th>
  <th scope="col">Thread</th>
  <th scope="col">Stage</th>
  <th scope="col">Delta</th>
  <th scope="col">Idle</th>
  <th scope="col">PR</th>
</tr></thead>
<tbody>
{threads}
</tbody>
</table>
</div>
{threads_note}

<h2>Over the limit</h2>
<p>One open pull request per repository, per contributor. Folding has an order:
close the pull request first, then push its commits onto the branch that
survives — pushing first merges it, with no review and no way to undo the
record.</p>
{over}

<h2>Claimed above the evidence</h2>
<p>The ladder is <span class="mono">{ladder_source}</span>.
<b>v0.0.1 is governance</b> and means the same thing in every project; every
rung above it is defined by the project, in the project's own records. The
Phase column is a claim somebody made. The governance column is what has landed
on the default branch — work sitting in an open pull request is work, and it is
not evidence.</p>
{ahead}

<h2>Phases nobody has answered</h2>
<p><span class="s-unknown">unknown</span> is the honest value for a repository
nobody could place, and is not a synonym for the bottom rung. A phase marked
<span class="s-unknown">scaffolded</span> is different again: it is the ladder's
floor applied because nothing was stated, and it is answered by editing
<span class="mono">ci/workspace.yaml</span>.</p>
<div class="q">
{unplaced}
</div>

<h2>What this page could not read</h2>
{unmeasured}
{scope}

<footer>
Generated by <span class="mono">ci/harness_dashboard.py</span> from
<span class="mono">harness-status.json</span>, which is written by
<span class="mono">ci/harness_status.py</span>. This renderer runs no commands
and reads no network: every fact above is in that document, and a fact that is
not in it is not shown. Correct a number by fixing the generator, not this page.
</footer>
</main>
"""

TEMPLATE = (
    """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Harness status — {org}</title>
<style>{style}</style>
</head>
<body>
"""
    + BODY
    + """</body>
</html>
"""
)

FRAGMENT = "<style>{style}</style>\n" + BODY


# Stage → (label, severity). `pushed` is warned on deliberately: it is work
# that exists on a remote and that no reviewer has been told about, which is
# the state this org has already lost a branch in.
STAGE_STATE = {
    "local": (WARN, "not on any remote"),
    "pushed": (WARN, "no pull request — nobody has been told"),
    "draft": (OK, "draft pull request"),
    "ready": (OK, "left draft — the human's signal"),
}


def delta_text(delta: object) -> str:
    """The size of a thread's change, however it was measured.

    Two shapes, because two sources: a pull request's counts come from the
    host, and a local branch's come from `git diff --shortstat`. Rendering one
    as the other would report a number the reader cannot check.
    """
    reason = unknown_reason(delta)
    if reason is not None:
        return f"unknown ({reason})"
    if not isinstance(delta, dict):
        return "unknown"
    if "additions" in delta:
        return (
            f"{delta.get('commits')} commits, {delta.get('changed_files')} files, "
            f"+{delta.get('additions')}/-{delta.get('deletions')}"
        )
    return f"{delta.get('commits')} commits, {delta.get('shortstat', 'no diff')}"


def idle_text(hours: object) -> str:
    if hours is None:
        return "unknown"
    hours = float(hours)
    if hours < 48:
        return f"{hours:.0f}h"
    return f"{hours / 24:.0f}d"


def threads_of(repo: dict) -> list[dict]:
    """Both scopes, tagged, so a reader never has to guess which they have."""
    found = []
    for holder, scope in (
        (repo.get("threads"), "org"),
        ((repo.get("local") or {}).get("threads"), "machine"),
    ):
        if isinstance(holder, list):
            found.extend({**t, "scope": scope} for t in holder)
    return found


def thread_rows(document: dict) -> list[dict]:
    """Every thread across every repository, worst first.

    Stalled before idle, and `pushed` before `draft`: a stalled branch nobody
    can see is the row that needs a person, and a dashboard that sorts by
    repository name buries it under whatever comes first alphabetically.
    """
    rows = []
    for repo in document.get("repositories", []):
        for thread in threads_of(repo):
            rows.append({**thread, "repository": repo.get("name")})
    order = {"pushed": 0, "local": 1, "draft": 2, "ready": 3}
    return sorted(
        rows,
        key=lambda t: (
            not t.get("stalled"),
            order.get(t.get("stage"), 9),
            -(t.get("idle_hours") or 0),
        ),
    )


def md_release(release: object) -> str:
    """The release column: what a tag asserts, and what main carries past it.

    `unreleased` and `current` are kept apart on purpose. Both have nothing
    outstanding, and they mean opposite things: one has never been asserted at
    all, the other has been asserted and nothing has changed since.

    A lightweight tag is called out rather than counted as a release. The
    version-tags record requires annotated tags precisely because a lightweight
    one carries no annotation, so it can name neither the reviewer nor the
    manual test -- a claim with nothing behind it.
    """
    reason = unknown_reason(release)
    if reason:
        return f"unknown ({reason})"
    if not isinstance(release, dict):
        return "unknown (no release layer in this document)"
    state = release.get("state")
    latest = release.get("latest")
    if state == "unreleased":
        return "never tagged"
    flag = "" if release.get("annotated") else " **lightweight**"
    if state == "current":
        return f"{latest}{flag}"
    n = release.get("unreleased_commits")
    if n is None:
        return f"{latest}{flag}, unknown commits since"
    return f"{latest}{flag} + {n} unreleased"


def md_state(governance: object) -> str:
    reason = unknown_reason(governance)
    if reason is not None:
        return f"unknown ({reason})"
    if not isinstance(governance, dict):
        return "not collected"
    if governance.get("precondition") == "n/a":
        return "n/a"
    if governance.get("precondition") == "met":
        return "precondition met"
    return "incomplete — missing " + ", ".join(governance.get("missing") or [])


def md_slot(slots: dict) -> str:
    reason = unknown_reason(slots)
    if reason is not None:
        return f"unknown ({reason})"
    if not slots.get("violations"):
        return "ok"
    return "OVER — " + "; ".join(
        f"{v['author']} holds "
        + ", ".join(f"#{n}" for n in v["numbers"])
        + (f" against {v['base']}" if v.get("base") else "")
        for v in slots["violations"]
    )


def render_markdown(document: dict) -> str:
    """The same document, for a reader that parses rather than looks.

    An agent opening an HTML page is parsing a rendering, and the first thing
    it loses is the distinction the page spends its colours on: `unknown` is a
    span class in HTML and a word here. So this view states every state in
    words, and never leaves one implied by an empty cell.
    """
    generator = document.get("generator", {})
    reading = document.get("reading", {})
    totals = document.get("totals", {})
    lines: list[str] = []
    add = lines.append

    add(f"# Harness status — {generator.get('org', 'unknown')}")
    add("")
    add(f"- generated: **{document.get('generated_at')}**")
    add(f"- rule: {generator.get('rule')} (`{generator.get('rule_source')}`)")
    add(f"- corpus exemption: `{', '.join(generator.get('corpus_exemption') or []) or 'none'}`")
    add(f"- layers: {', '.join(generator.get('layers') or [])}")
    if reading.get("staleness_budget_hours"):
        add(
            f"- **quote nothing here that is older than "
            f"{reading['staleness_budget_hours']}h.** Refresh: "
            f"`{reading.get('refresh')}`"
        )
    add("")
    add(
        "`unknown` is a value: the fact could not be established, and the "
        "reason is given. It is not zero, not empty, and not compliant."
    )
    add("")
    add(
        f"**Totals** — {totals.get('repositories')} repositories, "
        f"{totals.get('compliant')} within the slot rule, "
        f"{totals.get('over_limit')} over it, "
        f"{totals.get('slots_unknown')} unreadable; "
        f"{totals.get('governance_precondition_met')} of "
        f"{totals.get('governance_readable')} readable meet the v0.0.1 "
        f"precondition; {totals.get('phase_scaffolded')} phases scaffolded."
    )
    add("")
    add("| Repository | Phase (claimed) | Source | v0.0.1 governance (evidence) | Slot | Release |")
    add("|---|---|---|---|---|---|")
    for repo in document.get("repositories", []):
        add(
            f"| {repo.get('name')} | {repo.get('phase')} | "
            f"{repo.get('phase_source')} | {md_state(repo.get('governance'))} | "
            f"{md_slot(repo.get('slots', {}))} | {md_release(repo.get('release'))} |"
        )
    add("")
    add(
        "**`main` is readiness; a `v` tag is governance.** Merging asserts the "
        "work is ready to build on and nothing more. A tag asserts that a human "
        "reviewed it, manually tested it against its real runtime, and that its "
        "automated gate passed and is deterministic. The Release column is the "
        "gap between the two: commits carried on the default branch that no tag "
        "has asserted."
    )
    add("")

    add("## Threads in flight")
    add("")
    add(
        "One line of work each. The stages are observable states, not progress: "
        f"{generator.get('thread_stages_are_states_not_progress', '')}"
    )
    add("")
    add(
        f"Stalled means untouched for more than "
        f"{generator.get('stalled_after_hours')}h."
    )
    add("")
    add("| Repository | Thread | Stage | Delta | Idle | PR | Scope |")
    add("|---|---|---|---|---|---|---|")
    for thread in thread_rows(document):
        flag = " STALLED" if thread.get("stalled") else ""
        add(
            f"| {thread.get('repository')} | {thread.get('name')} "
            f"| {thread.get('stage')}{flag} | {delta_text(thread.get('delta'))} "
            f"| {idle_text(thread.get('idle_hours'))} "
            f"| {('#' + str(thread['pr'])) if thread.get('pr') else '-'} "
            f"| {thread.get('scope')} |"
        )
    add("")

    add("## What needs a human")
    add("")
    actions = []
    for repo in document.get("repositories", []):
        slots = repo.get("slots", {})
        if unknown_reason(slots) is None and slots.get("violations"):
            actions.append(
                f"- **{repo['name']}**: {md_slot(slots)}. One stays open; the "
                "rest are closed or folded into it. Close the pull request "
                "FIRST, then push — pushing first merges it."
            )
        for thread in threads_of(repo):
            if thread.get("stage") == "pushed":
                actions.append(
                    f"- **{repo['name']}** `{thread.get('name')}`: pushed with no "
                    f"pull request ({delta_text(thread.get('delta'))}, idle "
                    f"{idle_text(thread.get('idle_hours'))}). It exists on a "
                    "remote and no reviewer has been told. Open a draft pull "
                    "request, or record why not."
                )
        if str(repo.get("phase_source")) == "scaffolded":
            actions.append(
                f"- **{repo['name']}**: phase `{repo.get('phase')}` is the "
                "ladder's floor applied because nothing was stated. Confirm or "
                "replace it in `ci/workspace.yaml`."
            )
    if actions:
        lines.extend(actions)
    else:
        add("- nothing")
    add("")

    add("## What this document could not establish")
    add("")
    gaps = [
        f"- **{r['name']}** {layer}: {unknown_reason(r.get(layer))}"
        for r in document.get("repositories", [])
        for layer in ("slots", "governance", "local")
        if unknown_reason(r.get(layer)) is not None
    ]
    lines.extend(gaps or ["- nothing; every layer was read for every repository"])
    add("")

    for warning in reading.get("do_not") or []:
        add(f"> Do not {warning}.")
    add("")
    add(
        f"Generated by `{generator.get('tool')}`. This view runs no commands "
        "and reads no network — correct a fact by fixing the generator."
    )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    # The agent view is read from stdout as often as from a file, and it
    # carries text this tool did not author -- branch names, pull request
    # titles, a command's stderr. On a cp1252 console the em dashes in its own
    # prose arrive as replacement characters and anything worse raises.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("document", type=Path, help="harness-status.json")
    parser.add_argument("--out", type=Path, help="write here instead of stdout")
    parser.add_argument(
        "--fragment",
        action="store_true",
        help="emit the page without a document shell, for a host that supplies one",
    )
    parser.add_argument(
        "--format",
        choices=("html", "md"),
        default="html",
        help="html for a person, md for an agent. Same document either way.",
    )
    args = parser.parse_args(argv)

    if not args.document.exists():
        sys.exit(
            f"harness_dashboard: no document at {args.document}. "
            "Refusing to render an empty page, which would read as a clean org."
        )
    document = json.loads(args.document.read_text(encoding="utf-8"))
    if document.get("schema") != 1 or "repositories" not in document:
        sys.exit(
            f"harness_dashboard: {args.document} is not a harness status document "
            "(schema 1 with a repositories list)."
        )

    page = (
        render_markdown(document)
        if args.format == "md"
        else render(document, fragment=args.fragment)
    )
    if args.out:
        args.out.write_text(page, encoding="utf-8", newline="\n")
        print(f"wrote {args.out}")
    else:
        sys.stdout.write(page)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
