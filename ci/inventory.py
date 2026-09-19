#!/usr/bin/env python3
"""Every repository the org has, against what the corpus knows about.

    uv run qm inventory
    uv run qm inventory --write
    uv run qm inventory --resolve private-03

WHY. The org has many times as many repositories as `ci/workspace.yaml` lists.
Every plan this corpus has written -- adoption, propagation, the phase ladder,
the harness status -- was scoped to the roster, and nothing said the rest
existed. A roster that omits a repository does not merely miss it: it makes the
org invisible to its own planning, and the omission looks exactly like a
decision. The current figures are in the document this writes; do not restate
them here, where nothing would update them.

THREE FILES, SPLIT BY WHAT MAY LEAVE THE MACHINE

    inventory-public.json    public repositories by name, plus counts and
                             references standing in for the rest. Committable.
    inventory-private.json   reference -> private repository name. Never.
    inventory-local.json     what is cloned on this disk, and where. Never.

**The split is the control, not the redaction.** An earlier version of this file
produced one document and filtered the sensitive fields out of it. That works
until a filter has a bug, and then a single logic error publishes the names of a
private organisation irreversibly. A public file that never receives private
names cannot leak them however broken this code is, so the boundary is a file
boundary and the two gitignored files are the second layer rather than the first.

That earlier version wrote 34 private repository names and 28 absolute paths
carrying the operator's username into the working tree of a public repository,
and was one command from being pushed when the reviewer stopped it. It had
reintroduced a problem `ci/governance_status.py` already solved -- that file
records `private_repository_names_listed: false` -- because assistant-2026-08
was run at the problem without reading that file first.

PRIVATE REPOSITORIES ARE COUNTED AND REFERENCED, NEVER DROPPED. Omitting them
would be the easy fix and the wrong one: a census that silently loses a third of
its subject is a census nobody can act on. So the public file carries

    private-01   ->  "quaternionmedia private repo 1"

with the name only in the private file. References are assigned by creation
order, which is append-only, so `private-03` means the same repository next
month and in every document that cites it. `--resolve` reads the mapping back on
a machine that has it.

WHAT IT CANNOT DO. It cannot see a repository the credential cannot read, a
clone outside the search roots, or anything on a machine that is not this one --
which is most of what `plans/data-collection-pathways.md` cares about. Those are
unknown, never absent.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from roster import load as load_roster  # noqa: E402

SCHEMA = 1
ROOT = Path(__file__).resolve().parent.parent
DEFAULT_ORG = "quaternionmedia"

PUBLIC = "inventory-public.json"
PRIVATE = "inventory-private.json"
LOCAL = "inventory-local.json"

NEVER_COMMIT = (
    "Machine-scoped. Gitignored on purpose. Do not commit this file, paste from "
    "it, or quote it in anything that leaves this machine."
)


def unknown(reason: str) -> dict:
    return {"unknown": reason}


def now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def host_repositories(org: str) -> list[dict] | dict:
    proc = subprocess.run(
        ["gh", "repo", "list", org, "--limit", "500", "--json",
         "name,isPrivate,isArchived,isFork,updatedAt,createdAt,primaryLanguage,diskUsage"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    if proc.returncode != 0:
        detail = (proc.stderr or "").strip().splitlines()[:1]
        return unknown(f"could not list {org}: {detail[0] if detail else 'no detail'}")
    try:
        return json.loads(proc.stdout or "[]")
    except json.JSONDecodeError as exc:
        return unknown(f"repo list was not JSON: {exc}")


DEFAULT_BRANCH_COMMITS = """
query($org: String!, $endCursor: String) {
  organization(login: $org) {
    repositories(first: 100, after: $endCursor) {
      pageInfo { hasNextPage endCursor }
      nodes {
        name
        defaultBranchRef { target { ... on Commit { committedDate } } }
      }
    }
  }
}
"""

# The two thresholds the recency axis turns on, named so a test can pin them
# and so changing one is a diff rather than a search.
LIVE_DAYS = 30
QUIET_DAYS = 365


def decode_stream(text: str) -> list:
    """Every JSON document in a concatenated stream.

    `gh api graphql --paginate` emits one document per page rather than one
    array, and `--slurp` is not on every installed version. Reading only the
    first document returns one page of an organisation that has more than one,
    and reports every repository after it as absent -- the defect this corpus
    already recorded against a `gh api` call made without `--paginate` at all.
    """
    decoder = json.JSONDecoder()
    docs, index = [], 0
    while index < len(text):
        while index < len(text) and text[index].isspace():
            index += 1
        if index >= len(text):
            break
        doc, index = decoder.raw_decode(text, index)
        docs.append(doc)
    return docs


def default_branch_commits(org: str) -> dict:
    """name -> the default branch's last commit date, or an unknown.

    THIS IS THE ACTIVITY FIELD, AND THE OTHER TWO CANDIDATES ARE NOT.

    `updatedAt` moves when anybody edits a description or a topic, and lags a
    real push -- repositories in this org carry one weeks or years behind their
    own last commit.

    `pushedAt` moves on a push to ANY ref: a tag, a bot branch, a Pages deploy,
    a sweep. Repositories here have reported it on a day their default branch
    had not moved in years, so a classification built on it calls a dormant
    repository active, confidently and every time.

    A commit date on the branch that matters is the closest cheap answer to
    "did anyone do work here". It is still not the whole answer: it cannot see
    work on another branch, and it cannot see work that never left a disk.
    Those are the local half, below.

    The measurements behind all three sentences, with the query and the date,
    are in perspectives/2026-08-19-three-fields-and-none-of-them-is-activity.md.
    """
    proc = subprocess.run(
        ["gh", "api", "graphql", "--paginate",
         "-F", f"org={org}", "-f", f"query={DEFAULT_BRANCH_COMMITS}"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    if proc.returncode != 0:
        detail = (proc.stderr or "").strip().splitlines()[:1]
        return unknown("could not read default branches: "
                       f"{detail[0] if detail else 'no detail'}")
    try:
        pages = decode_stream(proc.stdout or "")
    except ValueError as exc:
        return unknown(f"default branch response was not JSON: {exc}")

    dates = {}
    for page in pages:
        nodes = (((page.get("data") or {}).get("organization") or {})
                 .get("repositories") or {}).get("nodes") or []
        for node in nodes:
            target = ((node.get("defaultBranchRef") or {}).get("target") or {})
            dates[node["name"]] = target.get("committedDate")
    return dates


def git(clone: Path, *args: str) -> str | None:
    proc = subprocess.run(["git", "-C", str(clone), *args],
                          capture_output=True, text=True,
                          encoding="utf-8", errors="replace")
    return proc.stdout if proc.returncode == 0 else None


def local_signals(clone: str | None) -> dict:
    """What only a clone can answer, and an unreadable wherever it cannot.

    `local_only_commits` is the signal nothing else in this corpus has: work
    that exists on one disk and on no remote. What it found on its first run --
    a governance standard another repository defers to, a release tag nobody
    can fetch, and a repository every host field calls dead -- is in
    perspectives/2026-08-19-three-fields-and-none-of-them-is-activity.md.

    It is `--all --not --remotes`, which is meaningless in a clone that has
    never fetched -- there every commit is "on no remote". So the
    remote-tracking refs are asserted first and their absence is reported as
    unreadable rather than as a repository full of unpushed work. That
    assertion is the difference between measuring the repository and measuring
    the checkout.
    """
    if clone is None:
        return {"readable": False, "reason": "not cloned here"}
    path = Path(clone)
    if not (path / ".git").exists():
        return {"readable": False, "reason": "clone path holds no .git"}

    remotes = git(path, "for-each-ref", "--format=%(refname)", "refs/remotes")
    if remotes is None:
        return {"readable": False, "reason": "git could not read this clone"}
    if not remotes.strip():
        return {"readable": False,
                "reason": "no remote-tracking refs -- nothing to compare against"}

    last = git(path, "for-each-ref", "--sort=-committerdate",
               "--format=%(committerdate:iso-strict)", "refs/heads")
    only = git(path, "log", "--all", "--not", "--remotes", "--format=%H")
    status = git(path, "status", "--porcelain")

    entries = [line for line in (status or "").splitlines() if line.strip()]
    return {
        "readable": True,
        "last_commit_any_branch": (last or "").splitlines()[0] if last else None,
        "local_only_commits": (total := len([c for c in (only or "").splitlines() if c])),
        "local_only_by_ref": local_only_by_ref(path, total),
        "dirty_entries": len(entries),
        "submodule_pin_dirty": any(
            line[2:].strip().strip('"').startswith("governance/qm")
            for line in entries
        ),
    }


def local_only_by_ref(path: Path, total: int) -> list[dict]:
    """Which refs hold the local-only commits, and what each ref's state says.

    A bare total cannot be acted on, because several quite different things
    produce one:

      upstream `gone`     the branch was merged and deleted on the host. Its
                          commits are almost certainly in the base under other
                          hashes, and the count is noise.
      no upstream         never pushed. Could be a scratch branch or a month
                          of work; only a person can tell.
      `ahead <n>`         the branch exists on the host and the local copy is
                          in front of it. This is the one with no benign
                          reading.
      a tag               a release claim that exists on one disk. In this
                          corpus the version tag is a human gate, so a tag
                          nobody else can fetch is a claim nobody can check.

    TAGS ARE WALKED BECAUSE LEAVING THEM OUT MADE THIS FUNCTION DISAGREE WITH
    ITS OWN TOTAL. The total is `--all --not --remotes`, and `--all` includes
    tags; the breakdown read `refs/heads` alone. A repository reported unpushed
    commits and listed no branch holding any of them -- they hung off a version
    tag that was on no branch and no remote. The `unaccounted` row closes the
    gap rather than leaving the two figures to differ quietly.

    Patch-id was tried as a way to tell merged work from unmerged and rejected:
    the seed-refresh commits in this corpus are byte-identical to each other by
    construction, so matching on patch-id reported one branch's work as already
    landed on another's. A check that answers confidently and wrongly is worse
    than the ambiguity it replaced.
    """
    rows, accounted = [], set()

    def commits_only_here(ref: str) -> list[str]:
        out = git(path, "rev-list", ref, "--not", "--remotes")
        return [line for line in (out or "").splitlines() if line]

    listing = git(path, "for-each-ref", "refs/heads",
                  "--format=%(refname:short)%09%(upstream:short)%09%(upstream:track)")
    for line in (listing or "").splitlines():
        parts = line.split("\t")
        if not parts or not parts[0]:
            continue
        branch = parts[0]
        upstream = parts[1] if len(parts) > 1 else ""
        track = parts[2] if len(parts) > 2 else ""
        found = commits_only_here(branch)
        if not found:
            continue
        accounted.update(found)
        if not upstream:
            state = "no upstream"
        elif "gone" in track:
            state = "upstream gone -- merged and deleted, most likely"
        else:
            state = f"upstream {upstream} {track}".strip()
        rows.append({"ref": branch, "kind": "branch",
                     "commits": len(found), "state": state})

    tags = git(path, "for-each-ref", "refs/tags", "--format=%(refname:short)")
    for tag in (tags or "").splitlines():
        if not tag:
            continue
        found = commits_only_here(tag)
        if not found:
            continue
        fresh = [c for c in found if c not in accounted]
        accounted.update(found)
        rows.append({"ref": tag, "kind": "tag", "commits": len(found),
                     "state": "tag on no remote -- a release claim nobody can fetch"
                              + ("" if fresh else ", also on a branch above")})

    if total > len(accounted):
        rows.append({"ref": "(unaccounted)", "kind": "unknown",
                     "commits": total - len(accounted),
                     "state": "reachable from --all but from no branch or tag: "
                              "a stash, a note, or another tool's refs. Every "
                              "instance found so far was a stash, and a stash is "
                              "work at stake like any other"})
    return sorted(rows, key=lambda r: -r["commits"])


def age_days(stamp: str | None, at: datetime) -> float | None:
    if not stamp:
        return None
    try:
        when = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
    except ValueError:
        return None
    return (at - when).total_seconds() / 86400.0


def recency_of(row: dict, at: datetime) -> str:
    """archived | live | quiet | cold | unknown -- from the default branch only.

    `archived` wins over every date: the host has stated the repository is
    closed, and a commit from last week does not reopen it.
    """
    if row.get("archived"):
        return "archived"
    days = age_days(row.get("default_branch_commit_at"), at)
    if days is None:
        return "unknown"
    if days < LIVE_DAYS:
        return "live"
    if days < QUIET_DAYS:
        return "quiet"
    return "cold"


def risk_of(local: dict) -> list[str]:
    """What is at stake here, as a list -- because these hold at once.

    `unreadable` is not `clean`. A repository nobody can inspect has an unknown
    amount of work at stake, and reporting that as nothing at stake is the
    substitution this corpus refuses everywhere else. `uncloned` arrives here
    rather than on the recency axis for the same reason: the host still answers
    when this repository last moved, so what the absent clone costs is the
    ability to see risk, not the ability to see recency.
    """
    if not local.get("readable"):
        return [f"unreadable:{local.get('reason', 'no reason given')}"]
    flags = []
    if local.get("local_only_commits"):
        flags.append(f"unpushed:{local['local_only_commits']}")
    if local.get("dirty_entries"):
        flags.append(f"dirty:{local['dirty_entries']}")
    if local.get("submodule_pin_dirty"):
        flags.append("pin-drift")
    return flags or ["clean"]


ATTENTION_VALUES = ("active", "queued", "dormant", "retired", "external")


def attention_of(entry: dict | None) -> str:
    """What a human said about this repository, and `unstated` when nobody did.

    Silence is not `dormant`. `dormant` says nobody is working on it;
    `unstated` says nobody has answered the question. Collapsing the second
    into the first would let the roster grow claims nobody made -- which is the
    same substitution `ci/workspace.yaml` already refuses for `phase`.
    """
    if entry is None:
        return "unrostered"
    stated = entry.get("attention")
    if stated in ATTENTION_VALUES:
        return stated
    return "unstated"


def roster_names(path: Path) -> tuple[dict[str, dict], dict[str, dict], dict | None]:
    """(by name, by private reference, problem) -- loaded through ci/roster.py.

    THIS MODULE USED TO PARSE THE ROSTER ITSELF, and `ci/roster.py` exists
    because of what that costs. A private repository is rostered as
    `ref: private-NN` with no `name`, so that a public file never carries the
    name; the loader here keyed on `name` alone and therefore dropped every one
    of them. The corpus listed repositories in its roster and then reported the
    same repositories under "the corpus cannot see these", while propagating
    into them.

    `roster.py`'s docstring records the same breakage happening to four other
    generators at once, which is why loading was moved there and why `name` is
    guaranteed: the real name when the gitignored companion is present, and the
    reference itself when it is not. A second parser in this file was the
    defect, so it is gone rather than repaired.

    Both indexes are returned because the two machines differ. Where the
    companion is present a private entry carries its real name and matches the
    host by name; where it is absent the entry's name is its reference, and the
    reference assigned by creation order is what matches.
    """
    if not path.is_file():
        return {}, {}, unknown(f"{path} is not present")
    entries = load_roster(path, path.parent / "workspace-private.yaml")
    return (
        {e["name"]: e for e in entries},
        {e["ref"]: e for e in entries if e.get("ref")},
        None,
    )


def assign_references(private: list[dict], org: str) -> dict[str, dict]:
    """name -> {ref, label}, ordered by creation date.

    Creation order is append-only: a repository made tomorrow takes the next
    number and never renumbers the ones before it. Ordering by name or by hash
    would shift every reference each time the org gained a repository, which
    would make a reference in a six-month-old document point somewhere else.
    """
    ordered = sorted(private, key=lambda r: (r.get("createdAt") or "", r["name"]))
    return {
        repo["name"]: {"ref": f"private-{i:02d}", "label": f"{org} private repo {i}"}
        for i, repo in enumerate(ordered, start=1)
    }


def local_clone(name: str, entry: dict | None, search_roots: list[Path]) -> str | None:
    """Where this repository is cloned, or None. The path is local-file-only."""
    candidates = list((entry or {}).get("paths") or []) + [name, f"qm/{name}"]
    for candidate in candidates:
        for root in search_roots:
            path = root / candidate
            if (path / ".git").exists():
                return str(path.resolve())
    return None


def build(org: str, roster_path: Path,
          search_roots: list[Path]) -> tuple[dict, dict, dict]:
    """Returns (public, private, local). Only the first may ever be committed."""
    host = host_repositories(org)
    roster, roster_by_ref, roster_problem = roster_names(roster_path)
    commits = default_branch_commits(org)
    at = datetime.now(timezone.utc)

    if isinstance(host, dict):
        return ({"schema": SCHEMA, "generated_at": now(), "host": host,
                 "repositories": [], "totals": {}}, {}, {})

    references = assign_references([r for r in host if r.get("isPrivate")], org)
    host_names = {r["name"] for r in host}

    dates = {} if isinstance(commits, dict) and "unknown" in commits else commits
    commits_problem = commits if dates is not commits else None

    public_rows, private_names, local_rows, matched = [], {}, {}, set()
    for r in sorted(host, key=lambda x: x["name"]):
        name = r["name"]
        private = bool(r.get("isPrivate"))
        entry, matched_key = roster.get(name), name
        if entry is None and private:
            matched_key = references[name]["ref"]
            entry = roster_by_ref.get(matched_key)
        if entry is not None:
            matched.add(matched_key)
        clone = local_clone(name, entry, search_roots)

        row = {
            "private": private,
            "fork": bool(r.get("isFork")),
            "archived": bool(r.get("isArchived")),
            "updated_at": r.get("updatedAt"),
            "created_at": r.get("createdAt"),
            "default_branch_commit_at": dates.get(name),
            "language": (r.get("primaryLanguage") or {}).get("name"),
            "disk_usage_kb": r.get("diskUsage"),
            "in_roster": entry is not None,
            "roster_phase": (entry or {}).get("phase"),
            "cloned_here": clone is not None,
        }
        row["attention"] = attention_of(entry)
        row["recency"] = recency_of(row, at)
        if private:
            row.update(references[name])
            private_names[references[name]["ref"]] = name
            key = references[name]["ref"]
        else:
            row["name"] = name
            key = name
        public_rows.append(row)
        if clone:
            signals = local_signals(clone)
            local_rows[key] = {"path": clone, "signals": signals,
                               "risk": risk_of(signals)}

    public_rows.sort(key=lambda r: (r["private"], r.get("name") or r.get("ref")))
    # A roster entry is one row however it was matched. `roster.load` guarantees
    # `name`, so a private entry appears in both indexes -- under its reference
    # and under that same reference standing in as a name on a machine without
    # the companion. Counting the two indexes would report it twice, and
    # subtracting host names would report it as missing from a host it is on.
    # So the loop above records what it matched, and this reads that.
    entries = {e["name"]: e for e in roster.values()}
    entries.update({e["ref"]: e for e in roster_by_ref.values()})
    in_roster_only = sorted(
        key for key, entry in entries.items()
        if key not in matched and entry.get("ref") not in matched
        and entry.get("name") not in matched
    )

    public = {
        "schema": SCHEMA,
        "generated_at": now(),
        "generator": {
            "tool": "ci/inventory.py",
            "produced_by": "assistant-2026-08",
            "org": org,
            "private_repository_names_listed": False,
            "absolute_paths_written": False,
            "private_repositories_referenced_as": "private-NN, by creation order",
            "companion_files": {
                PRIVATE: "reference -> name. Gitignored, never committed.",
                LOCAL: "clone paths on one machine. Gitignored, never committed.",
            },
            "roster_is_a_claim": (
                "ci/workspace.yaml is a human's list. Presence in this inventory "
                "is not adoption, not a backlog, and not a phase claim."
            ),
            "activity_axes": {
                "attention": (
                    "A CLAIM, from ci/workspace.yaml: active, queued, dormant, "
                    "retired, external. `unstated` means nobody answered; "
                    "`unrostered` means the corpus does not list the repository."
                ),
                "recency": (
                    "MEASURED, from the default branch's last commit date: "
                    "archived, live, quiet, cold, unknown. Not from updatedAt "
                    "and not from pushedAt -- see default_branch_commits."
                ),
                "risk": (
                    "MEASURED, and machine-scoped, so it is in "
                    f"{LOCAL} and never here: unpushed, dirty, pin-drift, "
                    "clean, unreadable."
                ),
            },
            "default_branch_commits": (
                commits_problem["unknown"] if commits_problem else "read"
            ),
        },
        "reading": {
            "refresh": "uv run qm inventory --write",
            "resolve": "uv run qm inventory --resolve private-03",
            "staleness_budget_hours": 168,
            "do_not": [
                "read this as a list of repositories that should adopt governance",
                "read `cloned_here: false` as a repository that does not exist",
                "commit either companion file, or quote a resolved name anywhere",
                "quote a count without generated_at -- the org gains repositories",
                "read updated_at or a host pushed_at as work happening -- neither is",
                "read `attention` as evidence: it is what a human claimed",
                "read `recency` as intent: a live repository nobody meant to touch "
                "is still live, and a cold one may be finished rather than neglected",
            ],
        },
        "roster_problem": roster_problem,
        "totals": {
            "on_host": len(host_names),
            "in_roster": len(roster),
            "on_host_not_in_roster": sum(1 for r in public_rows if not r["in_roster"]),
            "in_roster_not_on_host": len(in_roster_only),
            "cloned_here": sum(1 for r in public_rows if r["cloned_here"]),
            "private": sum(1 for r in public_rows if r["private"]),
            "forks": sum(1 for r in public_rows if r["fork"]),
            "archived": sum(1 for r in public_rows if r["archived"]),
            "by_recency": {
                value: sum(1 for r in public_rows if r["recency"] == value)
                for value in ("live", "quiet", "cold", "archived", "unknown")
            },
            "by_attention": {
                value: sum(1 for r in public_rows if r["attention"] == value)
                for value in ATTENTION_VALUES + ("unstated", "unrostered")
            },
        },
        "in_roster_not_on_host": in_roster_only,
        "repositories": public_rows,
    }

    private_doc = {"generated_at": now(), "warning": NEVER_COMMIT,
                   "references": private_names}
    local_doc = {"generated_at": now(), "warning": NEVER_COMMIT,
                 "reading": {
                     "risk_is_here_on_purpose": (
                         "Unpushed counts, dirty counts and pin drift describe one "
                         "operator's disk, not the repository. They stay out of "
                         f"{PUBLIC} for the same reason clone paths do."
                     ),
                 },
                 "search_roots": [str(r) for r in search_roots],
                 "clones": local_rows}
    return public, private_doc, local_doc


def key_of(row: dict) -> str:
    return row.get("name") or row["ref"]


def disagrees(row: dict) -> str | None:
    """Where the claim and the measurement do not describe the same repository.

    Neither side is corrected here. `records/DRAFT-a-disagreement-is-a-delta.md`
    is why: a claim and an observation that differ are a unit of work for
    somebody to close, not a field for a generator to overwrite. This function
    only names the pair.
    """
    attention, recency = row["attention"], row["recency"]
    if attention == "active" and recency in ("cold", "archived"):
        return f"claimed {attention}, default branch is {recency}"
    if attention in ("retired", "dormant") and recency == "live":
        return f"claimed {attention}, default branch is {recency}"
    if attention == "unrostered" and recency == "live":
        return "moving, and the roster does not list it"
    return None


def render(doc: dict, local: dict | None = None) -> str:
    host = doc.get("host")
    if isinstance(host, dict) and "unknown" in host:
        return f"inventory: {host['unknown']}"
    t = doc["totals"]
    clones = (local or {}).get("clones") or {}
    out = [
        f"inventory of {doc['generator']['org']} at {doc['generated_at']}",
        "",
        f"  on the host          {t['on_host']}",
        f"  in the roster        {t['in_roster']}",
        f"  host, not roster     {t['on_host_not_in_roster']}   <- the corpus cannot see these",
        f"  cloned here          {t['cloned_here']}",
        f"  private {t['private']}   forks {t['forks']}   archived {t['archived']}",
        "",
        "  Private repositories are referenced, not named. Names and clone paths",
        f"  live in {PRIVATE} and {LOCAL}, both gitignored.",
        "",
    ]

    by_recency, by_attention = t.get("by_recency") or {}, t.get("by_attention") or {}
    if by_recency:
        out += [
            "activity, on three axes that are not interchangeable:",
            "",
            "  recency   measured, from the default branch's last commit  "
            + "  ".join(f"{k} {v}" for k, v in by_recency.items() if v),
            "  attention a claim, from ci/workspace.yaml                  "
            + "  ".join(f"{k} {v}" for k, v in by_attention.items() if v),
            f"  risk      measured and machine-scoped -- {LOCAL}, never committed",
            "",
        ]

    rostered = [r for r in doc["repositories"] if r["in_roster"]]
    if rostered:
        out.append(f"in the roster ({len(rostered)}):")
        out.append(f"  {'':<26}{'attention':<12}{'recency':<10}risk")
        for r in sorted(rostered, key=lambda r: (r["recency"], key_of(r))):
            risk = (clones.get(key_of(r)) or {}).get("risk") or ["unreadable:not cloned here"]
            out.append(f"  {key_of(r):<26}{r['attention']:<12}{r['recency']:<10}"
                       + " ".join(risk))
        out.append("")

    gaps = [(key_of(r), reason) for r in doc["repositories"]
            if (reason := disagrees(r))]
    if gaps:
        out.append(f"claim and measurement disagree ({len(gaps)}):")
        for name, reason in gaps:
            out.append(f"  {name:<26}{reason}")
        out += ["",
                "  Neither side is corrected here. A disagreement between two views",
                "  of one repository is a delta -- see qm divergence.", ""]

    at_risk = [
        (key, entry) for key, entry in clones.items()
        if any(f.startswith("unpushed:") for f in (entry.get("risk") or []))
    ]

    def unpushed_count(entry: dict) -> int:
        flag = next(f for f in entry["risk"] if f.startswith("unpushed:"))
        return int(flag.split(":")[1])

    if at_risk:
        out.append(f"work that exists on this disk and on no remote ({len(at_risk)}):")
        for key, entry in sorted(at_risk, key=lambda kv: -unpushed_count(kv[1])):
            out.append(f"  {key:<26}{' '.join(entry['risk'])}")
            for ref in (entry.get("signals") or {}).get("local_only_by_ref") or []:
                mark = "#" if ref["kind"] == "tag" else " "
                out.append(f"    {mark} {ref['commits']:>3}  {ref['ref']:<38}"
                           f"{ref['state']}")
        out += ["",
                "  Read the upstream column before acting on a count. `upstream gone`",
                "  is a branch that was merged and deleted, and its commits are",
                "  almost certainly in the base under other hashes; `no upstream` may",
                "  be a scratch branch or a month of work, and only a person can tell.",
                "  A local copy ahead of a branch that still exists on the host is the",
                "  one case with no benign reading, and so is a # tag.", ""]

    missing = [r for r in doc["repositories"] if not r["in_roster"]]
    if missing:
        out.append(f"not in the roster ({len(missing)}):")
        for r in missing:
            flags = "".join(["F" if r["fork"] else " ",
                             "A" if r["archived"] else " ",
                             "L" if r["cloned_here"] else " "])
            out.append(f"  [{flags}] {(r.get('name') or r['label']):<40}{r['recency']}")
        out += ["", "  F fork  A archived  L cloned here", ""]
    out.append("Presence here is not adoption. This lists what exists, nothing more.")
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--org", default=DEFAULT_ORG)
    parser.add_argument("--roster", default=str(ROOT / "ci" / "workspace.yaml"))
    parser.add_argument("--search-root", action="append", default=None)
    parser.add_argument("--out-dir", default=str(ROOT),
                        help="where the three files are written")
    parser.add_argument("--write", action="store_true",
                        help=f"write {PUBLIC}, {PRIVATE} and {LOCAL}")
    parser.add_argument("--resolve", metavar="REF",
                        help="print the name behind a reference, from the local file")
    args = parser.parse_args(argv)

    out_dir = Path(args.out_dir)

    if args.resolve:
        path = out_dir / PRIVATE
        if not path.is_file():
            print(f"no {PRIVATE} here. Run `uv run qm inventory --write` on the "
                  f"machine with the credential.", file=sys.stderr)
            return 1
        name = (json.loads(path.read_text(encoding="utf-8")).get("references") or {}
                ).get(args.resolve)
        if not name:
            print(f"{args.resolve} is not in {PRIVATE}.", file=sys.stderr)
            return 1
        print(name)
        return 0

    roots = [Path(r).resolve() for r in (args.search_root or [ROOT.parent, ROOT.parent.parent])]
    public, private_doc, local_doc = build(args.org, Path(args.roster), roots)

    if args.write:
        for name, doc in ((PUBLIC, public), (PRIVATE, private_doc), (LOCAL, local_doc)):
            if not doc:
                continue
            (out_dir / name).write_text(json.dumps(doc, indent=2) + "\n",
                                        encoding="utf-8", newline="\n")
        print(f"wrote {PUBLIC}  (committable)")
        print(f"wrote {PRIVATE}, {LOCAL}  (gitignored -- do not commit)")
        return 0

    print(render(public, local_doc))
    return 0


if __name__ == "__main__":
    sys.exit(main())
