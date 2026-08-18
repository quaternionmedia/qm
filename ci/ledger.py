#!/usr/bin/env python3
"""The ledger: every action, what it was predicted to do, and what it cost.

    uv run qm ledger              # the running list
    uv run qm ledger --check      # every closed entry is complete and scored
    uv run qm ledger --open       # what is predicted and not yet settled

WHY. A session states an intention, acts, and reports. Nothing compares the
first to the third, so an overclaim is only caught if a human happens to
remember what was promised. This file makes the prediction durable and the
comparison mechanical.

The scoring field is the point. `outcome_matched_projection` is `true`, `false`,
or `unknown`, and a `false` is not a defect -- an honest wrong prediction is
worth more than a vague right one. What is a defect is a closed entry with no
outcome, which is a prediction quietly dropped.

WHAT IT CANNOT DO. It cannot tell that a projection was vague enough to be
unfalsifiable, or that an outcome was written to match. Both are readings. It
checks that the fields exist, that closed entries are scored, and that nothing
open has been abandoned.
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
LEDGER = ROOT / "ledger.yaml"
TOOL_REGISTRY = ROOT / "ci" / "tool-registry.yaml"

REQUIRED = ("id", "action", "kind", "projected_impact", "status", "tool")
REQUIRED_WHEN_CLOSED = ("outcome", "failure_cost", "outcome_matched_projection")
KINDS = {"build", "fix", "document", "decide", "verify", "revert"}
STATUSES = {"open", "closed"}
SCORES = {True, False, "unknown"}


def load(path: Path) -> list[dict]:
    if not path.is_file():
        raise SystemExit(f"{path}: no ledger. Nothing was recorded.")
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    entries = data.get("entries") or []
    if not entries:
        raise SystemExit(f"{path}: the ledger is empty -- nothing was checked.")
    return entries


def passes(path: Path) -> list[dict]:
    """Every recorded pass over the base, in order.

    Separate from `entries` because they answer different questions. An entry
    says something was found; a pass says the looking happened. Without the
    second, a ledger that grew by nothing is indistinguishable from one nobody
    opened, and the stability criterion in
    records/DRAFT-the-base-is-the-deliverable.md cannot be read at all.
    """
    if not path.is_file():
        return []
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return data.get("passes") or []


def streak(recorded: list[dict]) -> int:
    """Trailing passes that added nothing. The stability measure.

    Counted from the end and stopping at the first pass that added an entry --
    the question is whether the ground is still moving now, not how quiet it
    once was.
    """
    count = 0
    for entry in reversed(recorded):
        if entry.get("added_since_previous"):
            break
        count += 1
    return count


def pass_problems(recorded: list[dict], tools: set[str] | None = None) -> list[str]:
    found: list[str] = []
    for i, entry in enumerate(recorded):
        where = entry.get("at", f"pass {i}")
        for field in ("at", "tool", "ran", "entries_at_pass", "added_since_previous"):
            if entry.get(field) is None:
                found.append(f"{where}: missing `{field}`")
        if not str(entry.get("ran") or "").strip():
            found.append(
                f"{where}: `ran` is empty. A pass that does not say what it ran "
                f"cannot be told from a narrower one, and narrowing the pass is "
                f"the way to lengthen the streak without earning it."
            )
        if tools and entry.get("tool") and entry["tool"] not in tools:
            found.append(f"{where}: tool {entry['tool']} not in ci/tool-registry.yaml")
    # Only the first pass may be unknown, and it must be: a later pass claiming
    # it cannot be compared is a quiet result wearing the baseline's clothes.
    for i, entry in enumerate(recorded):
        is_unknown = isinstance(entry.get("added_since_previous"), dict)
        if i == 0 and not is_unknown:
            found.append(
                f"{entry.get('at')}: the first pass reports a count. It has no "
                f"previous pass to differ from, so the only honest value is unknown."
            )
        if i > 0 and is_unknown:
            found.append(
                f"{entry.get('at')}: added_since_previous is unknown on a pass "
                f"that has a predecessor. The count is computed, not withheld."
            )

    # The count is derived, so a disagreement means it was edited by hand.
    for previous, current in zip(recorded, recorded[1:]):
        expected = (current.get("entries_at_pass") or 0) - (previous.get("entries_at_pass") or 0)
        if isinstance(current.get("added_since_previous"), dict):
            continue
        if current.get("added_since_previous") != expected:
            found.append(
                f"{current.get('at')}: added_since_previous is "
                f"{current.get('added_since_previous')} but the entry counts "
                f"differ by {expected}. This number is computed, never typed."
            )
    return found


def known_tools(path: Path) -> set[str]:
    """Ids in the tool registry. Empty if it is missing, which is itself a problem."""
    if not path.is_file():
        return set()
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return {t["id"] for t in (data.get("tools") or []) if t.get("id")}


def problems(entries: list[dict], tools: set[str] | None = None) -> list[str]:
    found: list[str] = []
    seen: set[str] = set()
    if tools is not None and not tools:
        found.append(
            "ci/tool-registry.yaml names no tools -- every attribution below is "
            "unresolvable, which is the state this field exists to prevent"
        )
    for entry in entries:
        eid = entry.get("id", "<no id>")
        if eid in seen:
            found.append(f"{eid}: duplicate id")
        seen.add(eid)
        for field in REQUIRED:
            if not entry.get(field):
                found.append(f"{eid}: missing `{field}`")
        if entry.get("kind") not in KINDS:
            found.append(f"{eid}: kind {entry.get('kind')!r} is not one of {sorted(KINDS)}")
        if entry.get("status") not in STATUSES:
            found.append(f"{eid}: status {entry.get('status')!r} is not open or closed")
        # Required on every entry, not only failures. Tool authorship is
        # audited on the same terms as tool fault.
        if tools and entry.get("tool") and entry["tool"] not in tools:
            found.append(
                f"{eid}: tool {entry['tool']!r} is not in ci/tool-registry.yaml -- "
                f"an attribution that resolves to nothing cannot be audited"
            )
        if entry.get("status") == "closed":
            for field in REQUIRED_WHEN_CLOSED:
                if field not in entry or entry[field] in (None, ""):
                    found.append(f"{eid}: closed with no `{field}` -- a prediction dropped")
            score = entry.get("outcome_matched_projection")
            if field_present(entry, "outcome_matched_projection") and score not in SCORES:
                found.append(f"{eid}: score {score!r} is not true, false or unknown")
    return found


def field_present(entry: dict, name: str) -> bool:
    return name in entry and entry[name] not in (None, "")


def render(entries: list[dict], only_open: bool) -> str:
    rows = [e for e in entries if not only_open or e.get("status") == "open"]
    closed = [e for e in entries if e.get("status") == "closed"]
    missed = [e for e in closed if e.get("outcome_matched_projection") is False]

    out = [f"{len(entries)} entr(ies): {len(closed)} closed, "
           f"{len(entries) - len(closed)} open.",
           f"{len(missed)} closed entr(ies) did not match their projection.\n"]
    for entry in rows:
        mark = {"open": "[ ]", "closed": "[x]"}.get(entry.get("status"), "[?]")
        score = entry.get("outcome_matched_projection")
        tag = {True: "as predicted", False: "MISSED", "unknown": "unscored"}.get(score, "")
        out.append(f"{mark} {entry.get('id')}  {entry.get('kind')}  {tag}")
        out.append(f"      {entry.get('action')}")
        out.append(f"      projected: {entry.get('projected_impact')}")
        if entry.get("outcome"):
            out.append(f"      outcome:   {entry['outcome']}")
        if entry.get("failure_cost") and entry["failure_cost"] != "none":
            out.append(f"      cost:      {entry['failure_cost']}")
        for lesson in entry.get("lessons") or []:
            out.append(f"      lesson:    {lesson}")
        for test in entry.get("tests_generated") or []:
            out.append(f"      test:      {test}")
        out.append("")
    return "\n".join(out)


def block(text: str, indent: str) -> str:
    """A YAML literal block, so an outcome keeps its paragraphs and its dashes.

    Folded scalars (`>`) rewrap, which silently joins a two-clause score into
    one line. Literal (`|`) does not.

    `indent` is the block's own, and is derived from the key being replaced
    rather than assumed: a hardcoded four spaces produced a parse error here
    against fields that sit at four, and the block must be deeper than its key.
    """
    lines = [f"{indent}{line}".rstrip() for line in text.rstrip().split("\n")]
    return "|-\n" + "\n".join(lines)


def close(raw: str, entry_id: str, outcome: str, cost: str, matched) -> str:
    """Settle one entry by editing its text, leaving the rest of the file alone.

    Not a YAML round-trip. `yaml.safe_dump` reformats every entry and drops
    every comment -- on a first attempt here it turned a four-field change into
    a 989-line diff and deleted the header explaining which entries were
    reconstructed. On an audit record the readable diff is the point.
    """
    lines = raw.split("\n")
    starts = [i for i, line in enumerate(lines)
              if line.strip() == f"- id: {entry_id}"]
    if not starts:
        raise SystemExit(f"{entry_id}: no such entry")
    if len(starts) > 1:
        raise SystemExit(f"{entry_id}: appears {len(starts)} times; refusing to guess")

    start = starts[0]
    field_indent = len(lines[start]) - len(lines[start].lstrip()) + 2
    end = next(
        (i for i in range(start + 1, len(lines))
         if lines[i].strip().startswith("- id:")
         or (lines[i].strip() and not lines[i].startswith(" " * field_indent))),
        len(lines),
    )

    # Refuse an entry that is already settled. Its outcome is a literal block by
    # now, and replacing the `outcome:` line would leave that block's body
    # behind as orphaned lines -- a corruption the YAML would still parse and
    # `--check` would still pass, because a non-empty outcome is all it reads.
    # Rescoring a closed prediction is also not a text edit's decision to make.
    #
    # Scanned across the entry's real extent. A fixed forty-line window passed
    # its unit test against a short synthetic entry and walked straight past a
    # real one, whose projection block alone is longer than the window.
    if any(line.strip() == "status: closed" for line in lines[start:end]):
        raise SystemExit(
            f"{entry_id}: already closed. Re-closing would orphan the "
            f"existing outcome block; edit it deliberately instead."
        )

    scalar = (str(matched).lower() if isinstance(matched, bool)
              else f'"{matched}"')
    written = set()
    for i in range(start, end):
        stripped = lines[i].strip()
        indent = lines[i][:len(lines[i]) - len(lines[i].lstrip())]
        for field in ("outcome", "failure_cost",
                      "outcome_matched_projection", "status"):
            if not stripped.startswith(f"{field}:"):
                continue
            if field == "outcome":
                value = block(outcome, indent + "  ")
            elif field == "failure_cost":
                value = block(cost, indent + "  ")
            elif field == "status":
                value = "closed"
            else:
                value = scalar
            lines[i] = f"{indent}{field}: {value}"
            written.add(field)

    missing = {"outcome", "failure_cost",
               "outcome_matched_projection", "status"} - written
    if missing:
        raise SystemExit(
            f"{entry_id}: fields not found: {', '.join(sorted(missing))}. "
            f"An entry missing them is malformed, not closeable."
        )
    return "\n".join(lines)


def record_pass(raw: str, ran: str, tool: str, when: str, total: int) -> str:
    """Append a pass. Text edit, for the reason `close` is one -- see its note.

    `added_since_previous` is computed from the ledger's own length rather than
    taken as an argument. A contributor counting their own findings is the
    number least worth trusting, and it is the only number the streak reads.
    """
    data = yaml.safe_load(raw) or {}
    previous = data.get("passes") or []

    # The first pass has nothing to be measured against, and saying `0` there
    # would be a fabrication that hands the streak its first point for free --
    # the exact way this measure flatters itself. `unknown` carries its reason,
    # and `streak` stops on it rather than counting it.
    if previous:
        added = f"{total - previous[-1].get('entries_at_pass', total)}"
    else:
        added = ('{unknown: "the first pass has no previous pass to differ '
                 'from; this is a baseline, not a quiet result"}')

    lines = [
        f"  - at: \"{when}\"",
        f"    tool: {tool}",
        f"    ran: {block(ran, '      ')}",
        f"    entries_at_pass: {total}",
        f"    added_since_previous: {added}",
    ]
    body = "\n".join(lines)

    if "\npasses:" in raw or raw.startswith("passes:"):
        return raw.rstrip("\n") + "\n" + body + "\n"
    header = (
        "\n# Every pass over the base, recorded whether or not it found anything.\n"
        "#\n"
        "# `entries:` above grows only when something goes wrong, so on its own it\n"
        "# cannot tell a quiet pass from a pass nobody ran. That distinction is the\n"
        "# whole stability criterion in records/DRAFT-the-base-is-the-deliverable.md,\n"
        "# so the looking is recorded here as well as the findings.\n"
        "#\n"
        "# `added_since_previous` is computed from the ledger's length by\n"
        "# `qm ledger --pass`. A hand-edited value is refused by --check.\n"
        "#\n"
        "# A bad pass is recorded on the same terms as a good one. A log updated\n"
        "# only after the runs that went well is a streak counter, not a test.\n"
        "passes:\n"
    )
    return raw.rstrip("\n") + "\n" + header + body + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--path", default=str(LEDGER))
    parser.add_argument("--pass", dest="record", action="store_true",
                        help="record a pass over the base, found something or not")
    parser.add_argument("--ran", help="what this pass actually ran, in your words")
    parser.add_argument("--tool", default="assistant-2026-08",
                        help="who ran it, resolved against ci/tool-registry.yaml")
    parser.add_argument("--stability", action="store_true",
                        help="the trailing run of passes that added nothing")
    parser.add_argument("--close", metavar="ID",
                        help="settle an open entry against its projection")
    parser.add_argument("--outcome", help="what actually happened")
    parser.add_argument("--cost", help="what the failure cost, or 'none'")
    parser.add_argument("--matched", choices=["true", "false", "unknown"],
                        help="did the outcome match the projection")
    parser.add_argument("--check", action="store_true",
                        help="fail if any entry is incomplete or a closed one is unscored")
    parser.add_argument("--open", dest="only_open", action="store_true",
                        help="only entries still predicted and unsettled")
    args = parser.parse_args(argv)

    path = Path(args.path)

    if args.stability:
        recorded = passes(path)
        if not recorded:
            print("no passes recorded, so stability is unknown -- not zero.")
            print("A ledger that only grows on failure cannot tell a quiet pass "
                  "from a pass nobody ran.")
            print("Record one: uv run qm ledger --pass --ran \"<what you ran>\"")
            return 0
        run = streak(recorded)
        print(f"{len(recorded)} pass(es) recorded; {run} in a row added nothing.")
        last = recorded[-1]
        added = last.get("added_since_previous")
        shown = (f"unknown ({added['unknown']})" if isinstance(added, dict)
                 else f"added {added}")
        print(f"last pass  {last.get('at')}  by {last.get('tool')}  {shown}")
        print()
        print("The base is stable when a full pass adds no entry "
              "(records/DRAFT-the-base-is-the-deliverable.md §3).")
        print("A streak is not correctness: a pass finds only what its checks "
              "look for, and most of this corpus is judgement with no detector.")
        return 0

    if args.record:
        if not args.ran:
            raise SystemExit(
                "--pass needs --ran. A pass that does not say what it ran cannot "
                "be told from a narrower one."
            )
        raw = path.read_text(encoding="utf-8")
        total = len(load(path))
        when = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        updated = record_pass(raw, args.ran, args.tool, when, total)
        try:
            parsed = yaml.safe_load(updated) or {}
        except yaml.YAMLError as exc:
            raise SystemExit(f"the edit produced unparseable YAML: {exc}") from exc
        if len(parsed.get("entries") or []) != total:
            raise SystemExit("the edit changed the entries; nothing written")
        recorded = parsed.get("passes") or []
        path.write_text(updated, encoding="utf-8", newline="\n")
        added = recorded[-1]["added_since_previous"]
        if isinstance(added, dict):
            print("pass recorded as the baseline. There is no previous pass to "
                  "differ from, so it counts toward no streak.")
        else:
            print(f"pass recorded: {added} entr(ies) added since the previous pass.")
        print(f"{streak(recorded)} pass(es) in a row have added nothing.")
        return 0

    if args.close:
        if not (args.outcome and args.cost and args.matched):
            raise SystemExit(
                "--close needs --outcome, --cost and --matched. A closed entry "
                "with a blank outcome is a prediction nobody scored."
            )
        matched = {"true": True, "false": False, "unknown": "unknown"}[args.matched]
        raw = path.read_text(encoding="utf-8")
        updated = close(raw, args.close, args.outcome, args.cost, matched)
        # Assert the intermediate before the file is touched: YAML that no
        # longer parses, or that lost an entry, is what a text edit produces
        # when it goes wrong, and writing first makes it the reader's problem.
        before = load(path)
        try:
            parsed = yaml.safe_load(updated) or {}
        except yaml.YAMLError as exc:
            raise SystemExit(f"the edit produced unparseable YAML: {exc}") from exc
        after = parsed.get("entries") or []
        if len(after) != len(before):
            raise SystemExit(
                f"the edit changed the entry count {len(before)} -> {len(after)}; "
                f"nothing written"
            )
        settled = next((e for e in after if e.get("id") == args.close), None)
        if not settled or settled.get("status") != "closed" or not settled.get("outcome"):
            raise SystemExit(f"{args.close}: did not come back closed and scored; "
                             f"nothing written")
        path.write_text(updated, encoding="utf-8", newline="\n")
        print(f"closed {args.close}")
        return 0

    entries = load(path)

    if args.check:
        tools = known_tools(TOOL_REGISTRY)
        found = problems(entries, tools) + pass_problems(passes(path), tools)
        for problem in found:
            print(f"  - {problem}", file=sys.stderr)
        if found:
            print(f"\n{len(found)} ledger problem(s). A closed entry with no outcome "
                  f"is a prediction nobody scored.", file=sys.stderr)
            return 1
        closed = sum(1 for e in entries if e.get("status") == "closed")
        recorded = passes(path)
        print(f"ledger: {len(entries)} entries, {closed} closed and all scored; "
              f"{len(recorded)} pass(es), {streak(recorded)} in a row adding nothing.")
        print("This does NOT mean the projections were good -- nothing here reads "
              "them for vagueness, and nothing verifies that the tool named is the "
              "tool that ran.")
        return 0

    print(render(entries, args.only_open))
    return 0


if __name__ == "__main__":
    sys.exit(main())
