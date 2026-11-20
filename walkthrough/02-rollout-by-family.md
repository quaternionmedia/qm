# 02 — A rollout, family by family

A push-through across the estate is not one act; it is the same few steps
taken in every repository, in an order somebody chose. `uv run qm rollout`
keeps that order and reports each repository's position in it — and it keeps
what a person *claimed* apart from what the host *shows*, because a tracker that
merges the two is the tidy, confident, wrong table this corpus keeps finding.

**This page runs.** Every example below is executed by `uv run qm test`, and the
output shown is the output that ran.

---

## 1. A plan is a person's

The plan lives in `ci/rollout.yaml`. A rollout has steps, phases and claims.
Here is a small one, in memory:

    >>> import sys, pathlib
    >>> sys.path.insert(0, str(pathlib.Path("ci").resolve()))
    >>> import rollout
    >>> plan = {
    ...     "name": "demo", "subject": "the entry stage takes pull requests",
    ...     "steps": [
    ...         {"id": "rekeyed",
    ...          "applies_when": {"kind": "path-exists", "path": ".github/workflows/adr-lint.yml"},
    ...          "evidence": {"kind": "file-matches", "path": ".github/workflows/adr-lint.yml",
    ...                       "pattern": r"branches:\s*\[\s*test\s*\]"}},
    ...         {"id": "handoff-noted"},
    ...     ],
    ...     "phases": [
    ...         {"name": "corpus", "repos": ["qm"]},
    ...         {"name": "core", "families": ["core"], "except": ["qm"]},
    ...     ],
    ...     "claims": [{"repo": "qm", "step": "rekeyed", "date": "2026-09-20", "by": "a person"}],
    ... }

Families come from `families.json`, which reads them from the record. A phase
names families, or repositories outright, and may leave named ones out:

    >>> families = {"families": [{"name": "core", "drives": "", "members": ["qm", "dossier"]}], "unstated": []}
    >>> roster = [{"name": "qm"}, {"name": "dossier"}]
    >>> phases, problems = rollout.members_of(plan, families, roster)
    >>> [(p["name"], [m["name"] for m in p["members"]]) for p in phases]
    [('corpus', ['qm']), ('core', ['dossier'])]
    >>> problems
    []

Name a repository twice and the plan is wrong, not deduplicated:

    >>> twice = dict(plan, phases=[{"name": "corpus", "repos": ["qm"]}, {"name": "core", "families": ["core"]}])
    >>> rollout.members_of(twice, families, roster)[1]
    ["qm is named by phase 'core' and by an earlier phase; it belongs to the earlier one"]

## 2. Evidence is measured, and a claim is only a claim

Each step with an `evidence` detector is measured — from the host's default
branch by default, or from the clones on one disk. Here the source is a table,
so the page can show every state:

    >>> class Table:
    ...     def __init__(self, verdicts): self.verdicts = verdicts
    ...     def measure(self, evidence, entry):
    ...         key = (entry["name"], evidence["kind"])
    ...         return self.verdicts.get(key, rollout.Verdict("pass", "gate open"))
    >>> host = Table({("qm", "file-matches"): rollout.Verdict("fail", "still branches: [main]"),
    ...               ("dossier", "file-matches"): rollout.Verdict("pass", "branches: [test]")})
    >>> doc = rollout.report(plan, families, roster, host)

`qm` claimed `rekeyed`, and the host disagrees. That is not resolved; it is
printed in capitals and counted:

    >>> doc["phases"][0]["members"][0]["steps"]["rekeyed"]["state"]
    'CONTRADICTED'
    >>> doc["summary"]["contradicted"]
    1

`dossier` claimed nothing, and the host says its workflow already moved. That
is not "done"; it is work nobody wrote down:

    >>> doc["phases"][1]["members"][0]["steps"]["rekeyed"]["state"]
    'unclaimed'

A step with no detector, when claimed, is a person's word and is labelled so;
unclaimed, it is nothing:

    >>> rollout.state_of(claimed=True, verdict=None)
    'unverified'
    >>> rollout.state_of(claimed=False, verdict=None)
    '-'

## 3. A phase is done when no row is open, and the first that is not is current

    >>> [(p["name"], p["status"]) for p in doc["phases"]]
    [('corpus', 'current'), ('core', 'queued')]

Fix the corpus, claim dossier's step, and both phases close:

    >>> host.verdicts[("qm", "file-matches")] = rollout.Verdict("pass", "branches: [test]")
    >>> plan["claims"].append({"repo": "dossier", "step": "rekeyed", "date": "2026-09-21", "by": "a person"})
    >>> plan["claims"].append({"repo": "qm", "step": "handoff-noted", "date": "2026-09-21", "by": "a person"})
    >>> plan["claims"].append({"repo": "dossier", "step": "handoff-noted", "date": "2026-09-21", "by": "a person"})
    >>> doc = rollout.report(plan, families, roster, host)
    >>> [(p["name"], p["status"]) for p in doc["phases"]]
    [('corpus', 'done'), ('core', 'done')]

`handoff-noted` has no detector, so the two rows that closed it are
`unverified` — the phases are done on a person's word, and each phase counts
how many of its rows are, rather than upgrading the word to evidence:

    >>> {m["repo"]: m["steps"]["handoff-noted"]["state"] for p in doc["phases"] for m in p["members"]}
    {'qm': 'unverified', 'dossier': 'unverified'}
    >>> [(p["name"], p["on_a_persons_word"]) for p in doc["phases"]]
    [('corpus', 1), ('core', 1)]

## 4. What the committed document carries, and what it refuses

`uv run qm rollout --write status/rollout.yaml` writes this report from the
host, with a `reading:` block that says where claims and evidence each came
from and what not to read into a cell. A private repository appears by its
redacted `ref`, never by name:

    >>> secret = rollout.report(dict(plan, phases=[{"name": "p", "repos": ["private-03"]}], claims=[]),
    ...                         families, [{"ref": "private-03", "name": "its-real-name"}], host)
    >>> secret["phases"][0]["members"][0]["repo"]
    'private-03'
    >>> "its-real-name" in str(rollout.document(secret, "host"))
    False

What the tool cannot do is judge the plan: whether a step belongs in it, or
whether a detector's regular expression measures what the step *means*. Read
`means` and `evidence` together before trusting a green cell — and remember
that a placeholder pattern, written before the spelling exists, measures
nothing at all.
