#!/usr/bin/env python3
"""The phased push-through, family by family, with claims and evidence apart.

    rollout.py                          # the current rollout: phases, members, steps
    rollout.py --next                   # the open phase's members and their next unmet step
    rollout.py --claim REPO STEP        # a person states a step done: dated, attributed, appended
    rollout.py --check                  # refuse a claim the evidence contradicts, or a plan that names nothing
    rollout.py --write status/rollout.yaml --source host

**THE PLAN IS A CLAIM AND THE REPORT IS A MEASUREMENT, AND THIS TOOL NEVER
LETS ONE STAND IN FOR THE OTHER.** `ci/rollout.yaml` is written by a person: an
ordered list of phases, each naming families (read from `families.json`, which
reads them from the record) or repositories outright; the steps every member
must pass; and dated claims that a member passed one. This tool measures each
step that carries a detector and prints the claim beside the evidence:

    ok            claimed, and the evidence agrees
    unverified    claimed, and the step has no detector -- a person's word, labelled as such
    unverifiable  claimed, the step has a detector, and it could not run here (no clone,
                  no host access, a name this machine cannot resolve)
    CONTRADICTED  claimed, and the evidence disagrees -- a delta, never silently resolved
    unclaimed     not claimed, and the evidence says it is done anyway -- drift, or work
                  nobody wrote down
    -             not claimed, and nothing says otherwise
    n/a           the step does not apply to this member, by the plan's own `applies_when`

A phase is `done` when every step of every member is `ok`, `unverified` or
`n/a` -- and it says how many of its rows rest on a person's word, because a
plan with a claim-only step could otherwise never finish. The first phase that
is not done is `current`; the rest are `queued`. A claim on a member of a
queued phase is reported as ahead of its phase and is not refused -- the order is
the plan's intention, and reality is allowed to disagree with it out loud.

WHAT THIS CANNOT DO. Tell whether a step *should* be in the plan, or whether the
detector measures the thing the step means. A detector is a regular expression or
a ref, and a step whose meaning it does not capture reports green on the wrong
fact. Read the step's `means` and its `evidence` together before trusting a row.
It also cannot see a repository the roster does not list.

Records: `records/DRAFT-nothing-is-both-a-claim-and-its-own-evidence.md`,
`records/DRAFT-a-disagreement-is-a-delta.md`,
`records/DRAFT-a-family-is-bordered-by-what-it-drives.md` section 1.
"""

from __future__ import annotations

import argparse
import base64
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

import roster  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
PLAN = ROOT / "ci" / "rollout.yaml"
FAMILIES = ROOT / "families.json"
SEARCH_ROOTS = (ROOT.parent, ROOT.parent.parent)
ORG = "quaternionmedia"

STATES = ("ok", "unverified", "unverifiable", "CONTRADICTED", "unclaimed", "-", "n/a")


# --- the plan ---------------------------------------------------------------

def load_plan(path: Path = PLAN) -> dict:
    if not path.is_file():
        raise SystemExit(f"{path} is missing. The plan is a person's; nothing here invents one.")
    plan = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(plan.get("rollouts"), list) or not plan["rollouts"]:
        raise SystemExit(f"{path} declares no rollouts.")
    return plan


def families_document(path: Path = FAMILIES) -> dict:
    if not path.is_file():
        return {"families": [], "unstated": []}
    return json.loads(path.read_text(encoding="utf-8"))


def select_rollout(plan: dict, name: str | None) -> dict:
    rollouts = plan["rollouts"]
    if name is None:
        return rollouts[0]
    for r in rollouts:
        if r.get("name") == name:
            return r
    known = ", ".join(r.get("name", "<unnamed>") for r in rollouts)
    raise SystemExit(f"no rollout named {name!r}. Declared: {known}")


def publishable(entry: dict) -> str:
    """The name a committed document may carry: the redacted ref, else the name."""
    return entry.get("ref") or entry.get("name") or "<unnamed>"


def members_of(rollout: dict, families: dict, entries: list[dict]) -> tuple[list[dict], list[str]]:
    """Phases resolved to roster entries, in plan order, each repository once.

    A repository named by two phases belongs to the first that names it; the
    second is reported, not silently deduplicated -- a phase that means to
    leave one out says so with `except:`. A family the record does not
    declare, or a repository the roster does not list, is a problem and not a
    member -- an empty phase that reads as done is the failure this refuses.
    """
    by_name: dict[str, dict] = {}
    for e in entries:
        for key in (e.get("name"), e.get("ref")):
            if key:
                by_name[key] = e
    declared = {f["name"]: f["members"] for f in families.get("families", [])}
    problems: list[str] = []
    seen: set[str] = set()
    phases: list[dict] = []
    for phase in rollout.get("phases", []):
        wanted: list[str] = []
        for fam in phase.get("families", []) or []:
            if fam not in declared:
                problems.append(f"phase {phase.get('name')!r} names family {fam!r}, which "
                                f"families.json does not declare")
                continue
            wanted.extend(declared[fam])
        wanted.extend(phase.get("repos", []) or [])
        left_out = set(phase.get("except", []) or [])
        members: list[dict] = []
        for name in wanted:
            if name in left_out:
                continue
            entry = by_name.get(name)
            if entry is None:
                problems.append(f"phase {phase.get('name')!r} names {name!r}, which the roster "
                                f"does not list")
                continue
            key = publishable(entry)
            if key in seen:
                problems.append(f"{key} is named by phase {phase.get('name')!r} and by an earlier "
                                f"phase; it belongs to the earlier one")
                continue
            seen.add(key)
            members.append(entry)
        if not members:
            problems.append(f"phase {phase.get('name')!r} resolves to no members")
        phases.append({"name": phase.get("name", "<unnamed>"),
                       "families": list(phase.get("families", []) or []),
                       "members": members})
    return phases, problems


# --- evidence ----------------------------------------------------------------

@dataclass
class Verdict:
    state: str      # pass | fail | unverifiable
    detail: str


def _git(path: Path, *args: str) -> tuple[int, str]:
    try:
        done = subprocess.run(["git", "-C", str(path), *args], capture_output=True,
                              encoding="utf-8", errors="replace", timeout=60)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return 1, str(exc)
    return done.returncode, (done.stdout if done.returncode == 0 else done.stderr).strip()


def run_gh(args: list[str]) -> tuple[int, str]:
    """`gh api ...` as (exit code, stdout). Replaced in tests; never called by the plan."""
    try:
        done = subprocess.run(["gh", *args], capture_output=True, encoding="utf-8",
                              errors="replace", timeout=60)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return 1, str(exc)
    return done.returncode, done.stdout


SHA = re.compile(r"^[0-9a-f]{7,40}$")


def corpus_has_ancestor(commit, descendant: str, corpus: Path = ROOT) -> Verdict:
    # The plan is YAML, and forty zeros parse as the integer 0. A commit is a
    # string of hex or it is not a commit; a placeholder is unverifiable, not a crash.
    commit = str(commit)
    if not SHA.match(commit):
        return Verdict("unverifiable", f"{commit!r} is not a commit; the plan's placeholder is not filled in")
    code, out = _git(corpus, "cat-file", "-e", f"{descendant}^{{commit}}")
    if code != 0:
        return Verdict("unverifiable", f"the corpus clone does not have {descendant[:12]}; fetch first")
    code, out = _git(corpus, "merge-base", "--is-ancestor", commit, descendant)
    if code == 0:
        return Verdict("pass", f"pinned at {descendant[:12]}, at or past {commit[:12]}")
    if code == 1:
        return Verdict("fail", f"pinned at {descendant[:12]}, which is not past {commit[:12]}")
    return Verdict("unverifiable", out)


class LocalSource:
    """Evidence read from clones on this disk, through git and never the working tree."""

    def __init__(self, roots=SEARCH_ROOTS, corpus: Path = ROOT):
        self.roots = roots
        self.corpus = corpus

    def clone_of(self, entry: dict) -> Path | None:
        candidates = list(entry.get("paths", []) or [])
        if entry.get("name"):
            candidates.append(entry["name"])
        for root in self.roots:
            for rel in candidates:
                candidate = (root / rel).resolve()
                if (candidate / ".git").exists():
                    return candidate
        return None

    def measure(self, evidence: dict, entry: dict) -> Verdict:
        clone = self.clone_of(entry)
        if clone is None:
            return Verdict("unverifiable", "no clone on this disk")
        kind = evidence.get("kind")
        ref = evidence.get("ref", "HEAD")
        if kind in ("file-matches", "path-exists"):
            code, out = _git(clone, "show", f"{ref}:{evidence['path']}")
            if code != 0:
                return Verdict("fail", f"{evidence['path']} is not in {ref}")
            if kind == "path-exists":
                return Verdict("pass", f"{evidence['path']} exists in {ref}")
            if re.search(evidence["pattern"], out, re.MULTILINE):
                return Verdict("pass", f"{evidence['path']} matches /{evidence['pattern']}/")
            return Verdict("fail", f"{evidence['path']} does not match /{evidence['pattern']}/")
        if kind == "ref-exists":
            branch = evidence["branch"]
            for full in (f"refs/remotes/origin/{branch}", f"refs/heads/{branch}"):
                code, _ = _git(clone, "show-ref", "--verify", "--quiet", full)
                if code == 0:
                    return Verdict("pass", f"{full} exists")
            return Verdict("fail", f"no ref named {branch} in the clone")
        if kind == "submodule-at-or-past":
            code, out = _git(clone, "ls-tree", ref, evidence["path"])
            if code != 0 or not out:
                return Verdict("fail", f"{evidence['path']} is not a submodule in {ref}")
            pinned = out.split()[2]
            return corpus_has_ancestor(evidence["commit"], pinned, self.corpus)
        return Verdict("unverifiable", f"unknown evidence kind {kind!r}")


class HostSource:
    """Evidence read from the host's default branch, so the report describes the org
    and not one disk. Private repositories need their real name, which only the
    uncommitted companion holds; without it the step is unverifiable, never failed."""

    def __init__(self, org: str = ORG, runner=run_gh, corpus: Path = ROOT):
        self.org = org
        self.run = runner
        self.corpus = corpus

    def _contents(self, repo: str, path: str, ref: str | None) -> tuple[int, dict | None]:
        endpoint = f"repos/{self.org}/{repo}/contents/{path}"
        if ref:
            endpoint += f"?ref={ref}"
        code, out = self.run(["api", endpoint])
        if code != 0:
            return code, None
        try:
            return 0, json.loads(out)
        except json.JSONDecodeError:
            return 1, None

    def measure(self, evidence: dict, entry: dict) -> Verdict:
        repo = entry.get("name")
        if not repo:
            return Verdict("unverifiable", "a private repository whose name this machine cannot resolve")
        kind = evidence.get("kind")
        ref = evidence.get("ref")
        if kind in ("file-matches", "path-exists"):
            code, doc = self._contents(repo, evidence["path"], ref)
            if code != 0 or doc is None:
                return Verdict("fail", f"{evidence['path']} is not on the host's {ref or 'default branch'}")
            if kind == "path-exists":
                return Verdict("pass", f"{evidence['path']} exists on the host")
            if doc.get("encoding") != "base64" or "content" not in doc:
                return Verdict("unverifiable", f"the host returned no content for {evidence['path']}")
            text = base64.b64decode(doc["content"]).decode("utf-8", errors="replace")
            if re.search(evidence["pattern"], text, re.MULTILINE):
                return Verdict("pass", f"{evidence['path']} matches /{evidence['pattern']}/ on the host")
            return Verdict("fail", f"{evidence['path']} does not match /{evidence['pattern']}/ on the host")
        if kind == "ref-exists":
            code, _ = self.run(["api", f"repos/{self.org}/{repo}/git/ref/heads/{evidence['branch']}"])
            return (Verdict("pass", f"refs/heads/{evidence['branch']} exists on the host") if code == 0
                    else Verdict("fail", f"no refs/heads/{evidence['branch']} on the host"))
        if kind == "submodule-at-or-past":
            code, doc = self._contents(repo, evidence["path"], ref)
            if code != 0 or doc is None or doc.get("type") != "submodule":
                return Verdict("fail", f"{evidence['path']} is not a submodule on the host")
            return corpus_has_ancestor(evidence["commit"], doc["sha"], self.corpus)
        return Verdict("unverifiable", f"unknown evidence kind {kind!r}")


# --- the report ---------------------------------------------------------------

def state_of(claimed: bool, verdict: Verdict | None) -> str:
    """The one table this tool exists for. Claim on one axis, evidence on the other."""
    if verdict is None:
        return "unverified" if claimed else "-"
    if verdict.state == "unverifiable":
        return "unverifiable" if claimed else "-"
    if verdict.state == "pass":
        return "ok" if claimed else "unclaimed"
    return "CONTRADICTED" if claimed else "-"


def claims_index(rollout: dict) -> dict[tuple[str, str], dict]:
    index: dict[tuple[str, str], dict] = {}
    for c in rollout.get("claims", []) or []:
        index[(str(c.get("repo")), str(c.get("step")))] = c
    return index


def report(rollout: dict, families: dict, entries: list[dict], source) -> dict:
    phases, problems = members_of(rollout, families, entries)
    steps = rollout.get("steps", []) or []
    step_ids = [s["id"] for s in steps]
    claims = claims_index(rollout)
    known_keys = set()
    out_phases: list[dict] = []
    current_found = False
    for phase in phases:
        members_out: list[dict] = []
        phase_done = True
        on_word = 0
        for entry in phase["members"]:
            key = publishable(entry)
            row_steps: dict[str, dict] = {}
            next_step: str | None = None
            for step in steps:
                applies = step.get("applies_when")
                if applies is not None:
                    gate = source.measure(applies, entry)
                    if gate.state == "fail":
                        row_steps[step["id"]] = {"state": "n/a", "detail": gate.detail}
                        continue
                claim = claims.get((key, step["id"])) or claims.get((entry.get("name", ""), step["id"]))
                claimed = claim is not None
                if claimed:
                    known_keys.add((claim.get("repo"), step["id"]))
                verdict = source.measure(step["evidence"], entry) if step.get("evidence") else None
                state = state_of(claimed, verdict)
                detail = verdict.detail if verdict else ("claimed; no detector" if claimed else "")
                if claim and claim.get("date"):
                    detail = f"{detail} (claimed {claim['date']}"
                    detail += f" by {claim['by']})" if claim.get("by") else ")"
                row_steps[step["id"]] = {"state": state, "detail": detail.strip()}
                if state not in ("ok", "unverified", "n/a") and next_step is None:
                    next_step = step["id"]
                if state not in ("ok", "unverified", "n/a"):
                    phase_done = False
                if state == "unverified":
                    on_word += 1
            members_out.append({"repo": key, "steps": row_steps, "next": next_step})
        status = "done" if phase_done and members_out else ("current" if not current_found else "queued")
        if status == "current":
            current_found = True
        out_phases.append({"name": phase["name"], "families": phase["families"],
                           "status": status, "on_a_persons_word": on_word,
                           "members": members_out})
    # a claim naming nothing the plan resolves
    for (repo, step), c in claims.items():
        if step not in step_ids:
            problems.append(f"claim on {repo!r} names step {step!r}, which the rollout does not declare")
        elif (repo, step) not in known_keys:
            problems.append(f"claim on {repo!r} for {step!r}: no phase names that repository")
    # ahead-of-phase claims: any claimed row in a phase after the current one,
    # whether that phase reads queued or already done -- the order was the intention
    phase_of = {m["repo"]: p["name"] for p in out_phases for m in p["members"]}
    current_at = next((i for i, p in enumerate(out_phases) if p["status"] == "current"), len(out_phases))
    ahead = [f"{m['repo']} ({p['name']})" for p in out_phases[current_at + 1:]
             for m in p["members"] if any(s["state"] in ("ok", "unverified", "CONTRADICTED", "unverifiable")
                                          for s in m["steps"].values())]
    contradicted = sum(1 for p in out_phases for m in p["members"]
                       for s in m["steps"].values() if s["state"] == "CONTRADICTED")
    return {
        "rollout": rollout.get("name"),
        "subject": rollout.get("subject", ""),
        "steps": [{"id": s["id"], "means": s.get("means", ""), "detector": bool(s.get("evidence"))}
                  for s in steps],
        "phases": out_phases,
        "ahead_of_phase": ahead,
        "problems": problems,
        "summary": {
            "phases": len(out_phases),
            "done": sum(1 for p in out_phases if p["status"] == "done"),
            "current": next((p["name"] for p in out_phases if p["status"] == "current"), None),
            "members": sum(len(p["members"]) for p in out_phases),
            "contradicted": contradicted,
        },
        "_phase_of": phase_of,
    }


def render(doc: dict, only_next: bool = False) -> str:
    lines = [f"rollout      {doc['rollout']}", f"subject      {doc['subject']}", ""]
    ids = [s["id"] for s in doc["steps"]]
    for p in doc["phases"]:
        if only_next and p["status"] != "current":
            continue
        fam = ", ".join(p["families"]) if p["families"] else "named repositories"
        word = f", {p['on_a_persons_word']} row(s) on a person's word" if p["on_a_persons_word"] else ""
        lines.append(f"## {p['name']}  [{p['status']}{word}]  {fam}")
        width = max([len(m["repo"]) for m in p["members"]] + [4])
        lines.append("   " + "repo".ljust(width) + "  " + "  ".join(i.ljust(14) for i in ids))
        for m in p["members"]:
            cells = "  ".join(m["steps"].get(i, {"state": "?"})["state"].ljust(14) for i in ids)
            tail = f"   next: {m['next']}" if only_next and m["next"] else ""
            lines.append("   " + m["repo"].ljust(width) + "  " + cells + tail)
        lines.append("")
    if doc["ahead_of_phase"]:
        lines.append("ahead of their phase: " + ", ".join(doc["ahead_of_phase"]))
    for problem in doc["problems"]:
        lines.append(f"problem: {problem}")
    s = doc["summary"]
    lines.append(f"{s['done']} of {s['phases']} phase(s) done; current: {s['current'] or 'none'}; "
                 f"{s['members']} member(s); {s['contradicted']} contradicted claim(s).")
    lines.append("")
    lines.append("A claim is a person's; the evidence is the host's or this disk's; a row shows both "
                 "and decides nothing.")
    return "\n".join(lines)


def document(doc: dict, source_name: str) -> dict:
    """The generated form, for status/. Redacted by construction: every repo is its publishable name."""
    out = {k: v for k, v in doc.items() if not k.startswith("_")}
    return {
        "schema": 1,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "generator": {"tool": "ci/rollout.py", "source": source_name,
                      "plan": str(PLAN.relative_to(ROOT)).replace("\\", "/")},
        "reading": {
            "refresh": "uv run qm rollout --write status/rollout.yaml --source host",
            "staleness_budget_hours": 168,
            "claims_come_from": "ci/rollout.yaml, written by a person; never inferred here",
            "evidence_comes_from": "the host's default branch (--source host) or clones on one disk "
                                   "(--source local); the generator block says which",
            "do_not": [
                "read `unverified` as done -- it is a claim with no detector",
                "read `-` as not started -- it is the absence of a claim and of evidence",
                "resolve a CONTRADICTED row by editing the claim; it is a delta for a person",
                "read a phase's order as a schedule; it is the plan's intention",
            ],
        },
        **out,
    }


# --- claims --------------------------------------------------------------------

def append_claim(path: Path, rollout_name: str, repo: str, step: str, by: str,
                 note: str | None, on: str | None = None) -> str:
    """Append one dated claim under the named rollout's `claims:` key, by text, so the
    hand-written file keeps its comments and order. Returns the line written."""
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    # find the rollout block, then its claims key
    start = next((i for i, l in enumerate(lines) if re.match(rf"\s*-\s*name:\s*{re.escape(rollout_name)}\s*$", l)), None)
    if start is None:
        raise SystemExit(f"no rollout named {rollout_name!r} in {path}")
    indent = len(lines[start]) - len(lines[start].lstrip())
    end = len(lines)
    for i in range(start + 1, len(lines)):
        if re.match(rf"\s{{{indent}}}-\s*name:", lines[i]):
            end = i
            break
    claims_at = next((i for i in range(start, end) if re.match(r"\s*claims:", lines[i])), None)
    if claims_at is None:
        raise SystemExit(f"rollout {rollout_name!r} has no `claims:` key; add `claims: []` under it")
    key_indent = len(lines[claims_at]) - len(lines[claims_at].lstrip())
    item_indent = " " * (key_indent + 2)
    # `date`, not `on`: YAML 1.1 reads a bare `on` as a boolean and every dumper quotes it.
    entry = {"repo": repo, "step": step, "date": on or date.today().isoformat(), "by": by}
    if note:
        entry["note"] = note
    flow = yaml.safe_dump(entry, default_flow_style=True, sort_keys=False, width=10_000).strip()
    line = f"{item_indent}- {flow}\n"
    # `claims: []` -> `claims:` with a block
    if re.match(r"\s*claims:\s*\[\s*\]\s*$", lines[claims_at]):
        lines[claims_at] = " " * key_indent + "claims:\n"
        insert_at = claims_at + 1
    else:
        insert_at = claims_at + 1
        while insert_at < end and (lines[insert_at].strip() == "" or
                                   lines[insert_at].startswith(item_indent + "-") or
                                   lines[insert_at].startswith(item_indent + " ")):
            insert_at += 1
        while insert_at > claims_at + 1 and lines[insert_at - 1].strip() == "":
            insert_at -= 1
    lines.insert(insert_at, line)
    path.write_text("".join(lines), encoding="utf-8", newline="\n")
    yaml.safe_load(path.read_text(encoding="utf-8"))  # it must still parse
    return line.rstrip("\n")


def git_user_name(corpus: Path = ROOT) -> str:
    code, out = _git(corpus, "config", "--get", "user.name")
    return out if code == 0 and out else "unknown"


# --- main ---------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--rollout", help="which rollout; default the first in the plan")
    parser.add_argument("--source", choices=["host", "local"], default=None,
                        help="where evidence comes from: local for a terminal, host for a written document")
    parser.add_argument("--next", action="store_true", help="only the current phase, with each member's next step")
    parser.add_argument("--check", action="store_true", help="exit non-zero on a contradicted claim or a plan problem")
    parser.add_argument("--write", metavar="PATH", help="write the generated document")
    parser.add_argument("--claim", nargs=2, metavar=("REPO", "STEP"), help="append a dated claim to the plan")
    parser.add_argument("--by", help="who claims (default: git user.name)")
    parser.add_argument("--note", help="a pull request, a commit, a sentence")
    args = parser.parse_args(argv)

    plan = load_plan()
    rollout = select_rollout(plan, args.rollout)

    if args.claim:
        repo, step = args.claim
        if step not in {s["id"] for s in rollout.get("steps", [])}:
            print(f"rollout {rollout['name']!r} has no step {step!r}", file=sys.stderr)
            return 2
        line = append_claim(PLAN, rollout["name"], repo, step, args.by or git_user_name(), args.note)
        print(f"appended to {PLAN.relative_to(ROOT)}: {line.strip()}")
        print("A claim is a person's statement. Run `uv run qm rollout --check` to see whether the evidence agrees.")
        return 0

    # A written document describes the org, so it reads the host unless told
    # otherwise; a terminal read describes this disk, which is faster and offline.
    source_name = args.source or ("host" if args.write else "local")
    source = HostSource() if source_name == "host" else LocalSource()
    families = families_document()
    entries = roster.load()
    doc = report(rollout, families, entries, source)

    if args.write:
        rendered = yaml.safe_dump(document(doc, source_name), sort_keys=False, allow_unicode=True, width=100)
        out = Path(args.write)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(rendered, encoding="utf-8", newline="\n")
        print(f"wrote {args.write} (source: {source_name})")
    else:
        print(render(doc, only_next=args.next))

    if args.check:
        failures = list(doc["problems"])
        if doc["summary"]["contradicted"]:
            failures.append(f"{doc['summary']['contradicted']} claim(s) contradicted by the evidence")
        for f in failures:
            print(f"  {f}", file=sys.stderr)
        if failures:
            print(f"\nrollout: {len(failures)} problem(s).", file=sys.stderr)
            return 1
        print("rollout: no claim is contradicted and the plan resolves. Unverified and unverifiable "
              "rows are printed above and are not passes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
