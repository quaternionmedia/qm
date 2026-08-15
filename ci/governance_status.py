#!/usr/bin/env python3
"""Emit the state of governance across the org as a document, not as a claim.

ORG-LEVEL TOOL, NOT A SEED FILE -- the opposite of everything in
project-seed/ci/, which exists to be copied into projects. This enumerates the
project/* branches of *this* repository and queries the org's own API, so it is
meaningful in exactly one clone. An adopting project vendors project-seed/
through its submodule and must never find this in there: run from a pin sixty
commits stale, it would produce an org-wide report attributed to that project's
checkout. It does import from project-seed/ci/adr_lint.py, and that dependency
points one way -- the org tool may use the seed's definitions, never the
reverse.

Read-only: it never writes to a repository other than the document it emits,
and never calls a mutating `gh` subcommand.

WHY A DOCUMENT AND NOT A DASHBOARD. Governance semantics -- what "behind"
means, when a branch counts as adopted, what makes a record ratified -- belong
to the corpus that defines them. A renderer that re-implements them is a second
definition of one rule, and drift between two definitions is the failure this
corpus exists to prevent. So this emits a document and stops. governance_render
turns it into HTML; dossier can turn it into rows; a threshold job can read it
and fail a build. None of them re-derive a governance fact.

TWO LAYERS, AND THE DIFFERENCE MATTERS.

  git    -- a pure function of the commits named in the document. Given the
            same corpus commit and the same branch commits, it yields the same
            answer forever. This layer is verifiable, and `--check` verifies it.
  github -- observations of a remote at a moment. Someone opens a pull request
            and yesterday's answer is wrong through nobody's fault. This layer
            is stamped and never checked, because "check" would mean asserting
            the world has not moved.

That split is why `--check` is trustworthy offline and in a fork PR with no
token: it re-derives the git layer against the commits the document already
names, and reports how much it could not verify rather than passing over it.

WHAT THIS CANNOT ESTABLISH. Whether a project *should* be adopted. Whether a
record is right. Whether an unpropagated branch is neglected or deliberately
pinned. Whether a repository with no project branch is out of scope or merely
unnoticed. It reports positions, and a position is not a judgement.

UNKNOWN IS A VALUE. Every field is a real answer or an explicit
`{unknown: <reason>}`, and the count of unknowns is in the header. A monitor
that renders "could not reach the API" the same as "nothing wrong" is worse
than no monitor, because it discourages the manual check that would have caught
the problem. Six defects in this seed's own tooling were that exact shape, and
one of them was in the first draft of this file: `gh repo list --json
licenseInfo --jq '.licenseInfo.spdxId'` returns null for every repository in the
org, because that endpoint's licence object has no `spdxId` key. With a
`// "NONE"` fallback it reported ninety-nine unlicensed repositories, confidently
and in a nice table.

Usage:
    governance_status.py                      # emit to stdout
    governance_status.py --write DOC          # emit to a file
    governance_status.py --check DOC          # re-derive the git layer, diff it
    governance_status.py --offline            # git layer only; github -> unknown
"""

from __future__ import annotations

import argparse
import base64
import binascii
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

# The record vocabulary -- what a Status row looks like, which statuses count as
# ratified, which filenames are numbered -- is defined once, in the lint that
# enforces it. Importing it means a change to the rule changes both, and there
# is never a second definition to keep in sync.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "project-seed" / "ci"))
from adr_lint import NUMBERED_FILENAME, is_ratified, status_of  # noqa: E402

SCHEMA = 1

# The branch namespace IS the project registry -- there is no list to keep in
# sync, because a project that has no project/<name> branch is by definition
# not governed. See docs/ref/namespaces.md for the canonical model.
PROJECT_NS = "project/"

# What adoption puts in the PROJECT's repository, per the numbered steps in
# handbook/forking-a-project.md. Presence only: this says a repository has the
# artifact, never that the artifact is correct or current.
#
# `adr/` is deliberately absent from this list. In the branch-per-project model
# a project's records live on a branch of THIS repository and arrive in the
# project through the submodule -- so looking for adr/ in the project repo
# reports every correctly adopted project as incomplete. The first run of this
# generator did exactly that to quaternionmedia/datum, which is adopted.
# The corpus submodule is found by its URL, not by its mount path. The fork
# procedure says governance/qm and codecartographer mounts it at docs/qm, so a
# path check reports a correctly vendored project as not tracking the corpus.
CORPUS_URL_MARK = "/qm"
IDE_ARTIFACTS = ("AGENTS.md", "CLAUDE.md", ".github/copilot-instructions.md")
SEED_WORKFLOWS = (
    ".github/workflows/adr-lint.yml",
    ".github/workflows/submodule-check.yml",
    ".github/workflows/reuse-lint.yml",
)
LICENCE_ARTIFACTS = ("LICENSE", "REUSE.toml")

SEED_COMMENT = re.compile(r"<!--\s*SEED FILE:")

# Terms the corpus uses but does not define, and which this generator therefore
# refuses to compute. Emitted into every document: a reader who wants a green
# "adopted" column should see why there isn't one, in the document rather than
# in a conversation. Each is a gap to close in `records/`, and closing one is
# what would let a field appear here.
UNDEFINED = [
    {
        "term": "adopted",
        "why_not_computed": "The corpus states only what adoption is not -- "
        "'Being pinned is not being adopted, and nothing reports the difference' "
        "-- and warns against filename checks. No record or handbook page gives a "
        "file set, a ref, or a predicate. So the artifacts each repository carries "
        "are listed and no boolean is derived from them.",
        "would_be_settled_by": "a record defining the adoption predicate",
    },
    {
        "term": "current",
        "why_not_computed": "handbook/propagation-runbook.md names 'a dispute "
        "about whether a project is current' as the thing that would force its own "
        "promotion to a record. behind_corpus is a count with no threshold "
        "attached, so no branch is labelled current or stale here.",
        "would_be_settled_by": "a record attaching a state to a commit distance",
    },
    {
        "term": "seed drift reference",
        "why_not_computed": "Nothing states whether a copied seed file is measured "
        "against the corpus tip or against the branch's own merge-base, and the two "
        "disagree on almost every branch. Both are reported; neither is the answer.",
        "would_be_settled_by": "one sentence in the propagation runbook",
    },
    {
        "term": "propagate/* and fix/* namespaces",
        "why_not_computed": "handbook/propagation-runbook.md instructs creating "
        "propagate/<name>-<date> branches and eight are pushed, while README.md's "
        "namespace table has four entries and says a branch outside them 'is a "
        "mistake rather than a variation'. Namespace conformance cannot be computed "
        "against a model that contradicts the procedure.",
        "would_be_settled_by": "adding the namespace to README.md's table, or the "
        "runbook using an existing one",
    },
    {
        "term": "project repository URL",
        "why_not_computed": "There is no index mapping project/<name> to a "
        "repository; handbook/propagation-runbook.md says so outright. This "
        "generator assumes <org>/<name> and reports unknown -- never unadopted -- "
        "when that repository cannot be read.",
        "would_be_settled_by": "a register mapping branches to repositories",
    },
]


class Unknown:
    """A field the generator could not establish, and why.

    Deliberately not None. `None` already means something here -- "never
    propagated" is a fact -- and a monitor that cannot distinguish "no" from
    "I could not look" will eventually report the second as the first.
    """

    __slots__ = ("reason",)

    def __init__(self, reason: str) -> None:
        self.reason = reason

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"Unknown({self.reason!r})"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Unknown) and other.reason == self.reason


# --------------------------------------------------------------------------
# Deterministic YAML, written here rather than by a library
#
# The document is committed, so an unchanged world must produce an unchanged
# file or it churns on every run and becomes noise nobody reads. A library's
# emitter is deterministic for a given version and not across versions, and
# this file is copied into projects that pin nothing. Hand-emitting a value
# space this small -- scalars, maps, lists of maps -- costs thirty lines and
# removes the variable. test_governance_status.py round-trips the output
# through PyYAML, so "valid YAML" stays a tested claim rather than a belief.
# --------------------------------------------------------------------------

PLAIN_SCALAR = re.compile(r"^[A-Za-z_][A-Za-z0-9_./@+-]*$")
OBJECT_ID = re.compile(r"^[0-9a-f]{7,64}$")
YAML_RESERVED = {"true", "false", "yes", "no", "on", "off", "null", "none", "y", "n"}


def yaml_scalar(value: object) -> str:
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, int):
        return str(value)
    text = str(value)
    # Object ids are always quoted, even the ones that would be legal plain.
    # Whether a sha renders bare depends on whether it happens to start with a
    # letter, so two adjacent commits render differently and the diff of a
    # document whose entire purpose is to be read in diffs acquires noise that
    # means nothing.
    if OBJECT_ID.match(text):
        return f'"{text}"'
    if PLAIN_SCALAR.match(text) and text.lower() not in YAML_RESERVED:
        return text
    return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'


def yaml_lines(node: object, indent: int = 0) -> list[str]:
    pad = "  " * indent
    out: list[str] = []
    if isinstance(node, dict):
        for key, value in node.items():
            if isinstance(value, (dict, list)) and value:
                out.append(f"{pad}{key}:")
                out.extend(yaml_lines(value, indent + 1))
            elif isinstance(value, dict):
                out.append(f"{pad}{key}: {{}}")
            elif isinstance(value, list):
                out.append(f"{pad}{key}: []")
            else:
                out.append(f"{pad}{key}: {yaml_scalar(value)}")
    elif isinstance(node, list):
        for item in node:
            if isinstance(item, dict):
                nested = yaml_lines(item, indent + 1)
                out.append(f"{pad}- {nested[0].lstrip()}")
                out.extend(nested[1:])
            elif isinstance(item, list):
                raise TypeError("a list of lists has no stable rendering here")
            else:
                out.append(f"{pad}- {yaml_scalar(item)}")
    else:
        raise TypeError(f"not a document node: {type(node).__name__}")
    return out


def plain(node: object) -> object:
    """Replace every Unknown with its wire form, recursively."""
    if isinstance(node, Unknown):
        return {"unknown": node.reason}
    if isinstance(node, dict):
        return {k: plain(v) for k, v in node.items()}
    if isinstance(node, list):
        return [plain(v) for v in node]
    return node


def count_unknowns(node: object) -> int:
    if isinstance(node, Unknown):
        return 1
    if isinstance(node, dict):
        return sum(count_unknowns(v) for v in node.values())
    if isinstance(node, list):
        return sum(count_unknowns(v) for v in node)
    return 0


def dumps(document: object) -> str:
    return "\n".join(yaml_lines(plain(document))) + "\n"


# --------------------------------------------------------------------------
# git, which either answers or says it could not
# --------------------------------------------------------------------------


class Git:
    """git in one repository. Never turns a failure into an empty string.

    `subprocess.run(...).stdout` on a failing command is `""`, and `""` reads
    as "no branches", "no records", "no merges" at every call site that
    forgets to check. Every defect this seed has found was that shape, so this
    raises and the caller decides whether the answer is Unknown.
    """

    def __init__(self, root: Path) -> None:
        self.root = root

    def run(self, *args: str) -> str:
        proc = subprocess.run(
            ["git", "-C", str(self.root), *args],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        if proc.returncode != 0:
            raise GitError(f"git {' '.join(args)}: {proc.stderr.strip()}")
        return proc.stdout.strip()

    def ok(self, *args: str) -> bool:
        return (
            subprocess.run(
                ["git", "-C", str(self.root), *args], capture_output=True
            ).returncode
            == 0
        )

    def lines(self, *args: str) -> list[str]:
        return [line for line in self.run(*args).splitlines() if line]

    def exists(self, ref: str) -> bool:
        return self.ok("rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}")

    def sha(self, ref: str) -> str:
        return self.run("rev-parse", f"{ref}^{{commit}}")

    def committed_at(self, ref: str) -> str:
        return utc(self.run("log", "-1", "--format=%cI", ref))

    def count(self, rev_range: str) -> int:
        return int(self.run("rev-list", "--count", rev_range))

    def is_ancestor(self, commit: str, ref: str) -> bool:
        return self.ok("merge-base", "--is-ancestor", commit, ref)

    def blob(self, ref: str, path: str) -> str | None:
        try:
            return self.run("show", f"{ref}:{path}")
        except GitError:
            return None

    def tree(self, ref: str, path: str = "") -> list[str]:
        """Every blob under `path` at `ref`, recursively.

        `-r` is load-bearing. Without it `ls-tree <ref> -- records` lists the
        directory entry itself and nothing inside it, so a caller filtering for
        *.md gets an empty list and reads it as "no records". That happened
        here on the first run, against a directory holding ten of them.
        """
        args = ["ls-tree", "-r", "--name-only", ref]
        if path:
            args += ["--", path]
        try:
            return self.lines(*args)
        except GitError:
            return []


class GitError(RuntimeError):
    pass


def utc(iso: str) -> str:
    """Normalise a git ISO timestamp to UTC with a Z suffix.

    git prints the committer's own offset, so the same commit renders
    differently depending on who is asking. In a committed document that is a
    diff every time the reader changes.
    """
    return (
        datetime.fromisoformat(iso).astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    )


def now() -> str:
    stamp = os.environ.get("GOVERNANCE_STATUS_NOW")
    if stamp:
        return stamp
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# --------------------------------------------------------------------------
# The git layer: pure functions of the refs named in the document
# --------------------------------------------------------------------------


def last_propagation(git: Git, corpus: str, branch: str) -> dict | None:
    """The newest merge on `branch` that brought corpus history in, or None.

    Two traps, both of which produced a wrong answer while this was being
    written, and both of which are pinned by tests.

    A merge commit is not a propagation. A project branch merging its own
    feature branch produces one too, and reading that as propagation reports a
    branch as current when nothing has ever reached it. Real case: only merge
    on project/qmetronome is its own pull request #1.

    Walking every reachable merge is worse. Once a branch has taken any corpus
    history, the corpus's own merge commits are reachable from it, and every
    one of them has a parent contained in the corpus -- so the naive test
    counted thirteen of main's merges as thirteen propagations of a branch
    that had had one.

    So: merges in `corpus..branch` -- work that is on the branch and not on the
    corpus -- with at least one parent contained in the corpus.

    A squash-merged propagation leaves no merge commit and is reported here as
    None. That is not a false negative. Squashing a propagation breaks the
    submodule-pin model the merge commit exists to carry, so "no propagation
    recorded" is the correct thing to say about it.
    """
    for commit in git.lines("rev-list", "--merges", f"{corpus}..{branch}"):
        parents = git.run("rev-list", "--parents", "-n", "1", commit).split()[1:]
        if any(git.is_ancestor(parent, corpus) for parent in parents):
            return {
                "commit": commit,
                "committed_at": git.committed_at(commit),
                "subject": git.run("log", "-1", "--format=%s", commit),
            }
    return None


def record_census(git: Git, ref: str, directory: str) -> dict | Unknown:
    """Count records at a ref by the status their own header table declares.

    Reads the ref, never the working tree. The tree on disk is whatever branch
    happens to be checked out, and reporting it as a branch's content is the
    error that put a false adoption finding into this repository's main.
    """
    names = [n for n in git.tree(ref, directory) if n.endswith(".md")]
    if not names:
        return Unknown(f"no {directory} at {ref}")
    statuses: dict[str, int] = {}
    ratified = numbered = 0
    for name in sorted(names):
        base = name.rsplit("/", 1)[-1]
        if base in ("README.md", "TEMPLATE.md"):
            continue
        text = git.blob(ref, name)
        if text is None:
            statuses["unreadable"] = statuses.get("unreadable", 0) + 1
            continue
        status = status_of(text) or "no status row"
        statuses[status] = statuses.get(status, 0) + 1
        if is_ratified(status):
            ratified += 1
        if NUMBERED_FILENAME.match(base):
            numbered += 1
    return {
        "total": sum(statuses.values()),
        "ratified": ratified,
        "numbered_files": numbered,
        "by_status": dict(sorted(statuses.items())),
    }


def seed_drift(git: Git, corpus: str, branch: str) -> dict:
    """Whether a branch's copied seed files still match the seed they came from.

    adr/TEMPLATE.md and project-seed/adr/TEMPLATE.md are different paths, so no
    merge ever reconciles them: propagation moves the seed and leaves the copy
    alone. Compared by content rather than blob id, so a line-ending difference
    between a Windows and a Linux checkout is not reported as an edit.

    TWO COMPARISONS, BECAUSE ONLY ONE OF THEM IS A SIGNAL. Against the corpus
    tip, every project branch here reports drift -- and that is just
    behind_corpus said a second way, since the seed has moved and the copy has
    not. Against the branch's own merge-base with the corpus, the question
    becomes whether the copy still matches the seed *as it stood when the
    branch last took it*, which is the independent fact: the project edited
    something it was supposed to copy verbatim. Of the nine project branches
    here, nine drift from the tip and one drifts from its merge-base. Which
    comparison the corpus intends is not settled anywhere in it -- see the
    `undefined` block of the emitted document -- so both are reported and
    neither is called the answer.

    The README is not compared at all: a project rewrites it. What is checked
    there is the seed comment the fork procedure's step 2 says to delete,
    whose presence means the copy was never finished. Counting the
    `project/<name>` placeholder instead would be wrong -- the seed uses that
    string in ordinary prose about the model, so a correct copy keeps one.
    """
    at_tip = git.blob(corpus, "project-seed/adr/TEMPLATE.md")
    merge_base = git.run("merge-base", corpus, branch)
    at_base = git.blob(merge_base, "project-seed/adr/TEMPLATE.md")
    copied = git.blob(branch, "adr/TEMPLATE.md")

    def compare(seed: str | None, where: str) -> object:
        if copied is None:
            return "absent"
        if seed is None:
            return Unknown(f"no project-seed/adr/TEMPLATE.md at {where}")
        return "match" if norm(copied) == norm(seed) else "drift"

    readme = git.blob(branch, "adr/README.md")
    return {
        "adr_template_vs_corpus": compare(at_tip, corpus),
        "adr_template_vs_merge_base": compare(at_base, merge_base),
        "readme_seed_comment_left_in": (
            Unknown(f"no adr/README.md at {branch}")
            if readme is None
            else bool(SEED_COMMENT.search(readme))
        ),
    }


def norm(text: str) -> str:
    return text.replace("\r\n", "\n").strip()


def git_layer(
    git: Git, corpus_ref: str, remote: str, pins: dict[str, str] | None = None
) -> dict:
    """Everything derivable from the corpus clone alone.

    `pins` re-derives the document against the commits an existing document
    names rather than against whatever the refs point at now. That is what
    makes `--check` a question about the document rather than about the world.
    """
    corpus = pins.get("corpus") if pins else None
    corpus = corpus or git.sha(corpus_ref)

    refs = project_refs(git, remote)
    if not refs:
        # The empty-query pass, in the one place it would otherwise reach the
        # committed artifact. A shallow checkout, or one where the remote
        # namespace was never fetched, has no project refs -- and `projects: []`
        # renders as a clean table for an org with nine project branches.
        # --check catches it afterwards; generation must not produce it.
        return {
            "corpus": corpus_entry(git, corpus_ref, corpus),
            "projects": Unknown(
                f"no {PROJECT_NS}* refs under {remote}/ or refs/heads/ in this clone; "
                "fetch them before generating"
            ),
        }

    projects = []
    for ref in sorted(refs):
        name = ref.split(PROJECT_NS, 1)[1]
        tip = (pins or {}).get(f"project:{name}")
        if tip and not git.exists(tip):
            projects.append(
                {"name": name, "branch": Unknown(f"pinned commit {tip[:8]} not in this clone")}
            )
            continue
        try:
            projects.append(project_entry(git, corpus, ref, tip or git.sha(ref)))
        except GitError as exc:
            # One unreadable ref makes one project unknown. It must not make the
            # document not exist: a generator that dies on the first missing
            # object turns "unknown for one project" into "no report at all",
            # which is the outcome the unknown value exists to avoid.
            projects.append({"name": name, "branch": Unknown(str(exc))})

    return {"corpus": corpus_entry(git, corpus_ref, corpus), "projects": projects}


def corpus_entry(git: Git, corpus_ref: str, corpus: str) -> dict:
    return {
        "ref": corpus_ref,
        "commit": corpus,
        "committed_at": git.committed_at(corpus),
        # Scoped to this repository's own records/ and named accordingly. A
        # project branch's adr/ is counted in that project's entry instead:
        # project/streaming-infrastructure carries an Accepted ADR-0001 while
        # the corpus has no ratified record, so one combined total would state
        # something false about either scope depending on which you quoted.
        "records": record_census(git, corpus, "records"),
    }


def project_entry(git: Git, corpus: str, ref: str, tip: str) -> dict:
    merge_base = git.run("merge-base", corpus, tip)
    return {
        "name": ref.split(PROJECT_NS, 1)[1],
        "branch": {
            "ref": ref,
            "commit": tip,
            "committed_at": git.committed_at(tip),
            "behind_corpus": git.count(f"{tip}..{corpus}"),
            "ahead_of_corpus": git.count(f"{corpus}..{tip}"),
            "merge_base": merge_base,
            "merge_base_at": git.committed_at(merge_base),
            "last_propagation": last_propagation(git, corpus, tip),
        },
        "records": record_census(git, tip, "adr"),
        "seed": seed_drift(git, corpus, tip),
    }


def project_refs(git: Git, remote: str) -> list[str]:
    refs = git.lines(
        "for-each-ref", "--format=%(refname:short)", f"refs/remotes/{remote}/{PROJECT_NS}*"
    )
    if refs:
        return refs
    # A clone with no remote -- a test fixture, or a repository someone
    # exported. Local branches are the registry there.
    return git.lines("for-each-ref", "--format=%(refname:short)", f"refs/heads/{PROJECT_NS}*")


# --------------------------------------------------------------------------
# The github layer: observations, stamped, never checked
# --------------------------------------------------------------------------


class Hub:
    """`gh` reads. Every method answers or returns Unknown with the reason."""

    def __init__(self, org: str, enabled: bool = True) -> None:
        self.org = org
        self.enabled = enabled
        self.reason = "not queried: --offline" if not enabled else ""

    def credential(self) -> str:
        """Which token this run used, named but never printed.

        A 404 means "absent" or "you cannot see it", and the two are the same
        bytes. Three of this org's project repositories are private and an
        Actions GITHUB_TOKEN is scoped to one repository, so a CI run without a
        wider credential sees a third of the fleet as missing everything --
        which reads as the worst-adopted projects in the org and is entirely an
        authentication artifact. Recording the credential is what lets a reader
        tell that story from the document instead of guessing at it.
        """
        if not self.enabled:
            return "none: --offline"
        for name in ("GH_TOKEN", "GITHUB_TOKEN"):
            if os.environ.get(name):
                return f"environment: {name}"
        return "gh cli login"

    def api(
        self,
        path: str,
        jq: str | None = None,
        paginate: bool = False,
        empty_is: object = None,
    ) -> object | Unknown:
        """One GET. `paginate` follows Link headers to the end of the collection.

        Paginate every list endpoint, without exception. GitHub caps a page at
        100 and returns the first one silently -- no error, no marker in the
        body, just a shorter list. This generator's first run against the real
        org reported that quaternionmedia/datum, /qmetronome and
        /factorio-sysops did not exist, because all three sort past the hundredth
        repository. A truncated collection is indistinguishable from a complete
        one at the call site, which is the whole problem.
        """
        if not self.enabled:
            return Unknown(self.reason)
        args = ["gh", "api"]
        if paginate:
            args.append("--paginate")
        args.append(path)
        if jq:
            args += ["--jq", jq]
        proc = subprocess.run(
            args, capture_output=True, text=True, encoding="utf-8", errors="replace"
        )
        if proc.returncode != 0:
            first = proc.stderr.strip().splitlines()
            return Unknown(f"gh api {path}: {first[0] if first else 'failed'}")
        body = proc.stdout.strip()
        if not body:
            # A jq filter over an empty collection prints nothing, and "no open
            # pull requests" is an answer rather than a failure. Only a caller
            # expecting exactly one object treats empty as unknown, which is
            # the default. Passing empty_is=[] says the emptiness is the data.
            return empty_is if empty_is is not None else Unknown(f"gh api {path}: empty response")
        try:
            return json.loads(body)
        except json.JSONDecodeError:
            # --paginate with --jq concatenates each page's jq output, so the
            # result is a stream of documents rather than one array. Parse it as
            # such rather than reporting a JSON error.
            items = []
            for line in body.splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    items.append(json.loads(line))
                except json.JSONDecodeError:
                    return body
            return items

    def repository(self, name: str) -> dict | Unknown:
        got = self.api(f"repos/{self.org}/{name}")
        if isinstance(got, Unknown):
            return got
        if not isinstance(got, dict):
            return Unknown(f"repos/{self.org}/{name}: unexpected response shape")
        licence = got.get("license")
        return {
            "default_branch": got.get("default_branch") or Unknown("no default branch: empty repository"),
            "private": got.get("private"),
            "archived": got.get("archived"),
            "pushed_at": got.get("pushed_at"),
            # `license` is a nested object whose key is `spdx_id`. The list
            # endpoint spells it `key` and has no `spdx_id` at all; asking the
            # wrong one there returns null for every repository in the org and
            # renders as "unlicensed" unless the caller notices. Named here so
            # the next reader does not have to rediscover it.
            "licence": (licence or {}).get("spdx_id") or "NOASSERTION",
        }

    def tree(self, name: str) -> set[str] | Unknown:
        """Every path on the default branch, in one call.

        One request per repository rather than one per artifact: a 404 per
        artifact is slow, is a rate limit waiting to happen, and cannot tell
        "file absent" from "repository unreachable".

        GitHub truncates this response for a large repository and says so in a
        `truncated` flag. An absent path in a truncated tree means nothing at
        all, so a truncated tree becomes Unknown rather than a list of things
        this repository is missing.
        """
        got = self.api(f"repos/{self.org}/{name}/git/trees/HEAD?recursive=1")
        if isinstance(got, Unknown):
            return got
        if not isinstance(got, dict) or "tree" not in got:
            return Unknown(f"trees/{name}: unexpected response shape")
        if got.get("truncated"):
            return Unknown(f"trees/{name}: response truncated; absence proves nothing")
        return {entry["path"] for entry in got["tree"] if "path" in entry}

    def gitmodules(self, name: str) -> str | Unknown:
        """The project's .gitmodules, decoded, or why it could not be read."""
        got = self.api(f"repos/{self.org}/{name}/contents/.gitmodules", ".content")
        if isinstance(got, Unknown):
            return got
        try:
            return base64.b64decode(str(got)).decode("utf-8", "replace")
        except (ValueError, binascii.Error) as exc:
            return Unknown(f"contents/.gitmodules in {name}: undecodable ({exc})")

    def open_prs(self, base: str) -> list[dict] | Unknown:
        got = self.api(
            f"repos/{self.org}/qm/pulls?state=open&base={base}&per_page=100",
            ".[] | {number, title, draft, head: .head.ref}",
            paginate=True,
            empty_is=[],
        )
        if isinstance(got, Unknown):
            return got
        if not isinstance(got, list):
            return Unknown(f"pulls?base={base}: unexpected response shape")
        return sorted(
            (
                {
                    "number": pr.get("number"),
                    "head": pr.get("head"),
                    "draft": pr.get("draft"),
                    "title": pr.get("title"),
                }
                for pr in got
            ),
            key=lambda pr: pr["number"] or 0,
        )


def adoption(hub: Hub, name: str) -> dict | Unknown:
    """What the project's own repository has of the fork procedure's output.

    Reported as four independent facts rather than one boolean, because they
    fail independently and a single "adopted: false" hides which step stopped.
    The submodule is checked by reading .gitmodules and looking for the pin --
    a repository can carry a submodule at governance/qm pointed anywhere, and
    "has a .gitmodules" is not the claim the model rests on.
    """
    tree = hub.tree(name)
    if isinstance(tree, Unknown):
        return tree

    if ".gitmodules" not in tree:
        submodule: object = {"corpus_mounted_at": None, "branch": None}
    else:
        text = hub.gitmodules(name)
        submodule = text if isinstance(text, Unknown) else parse_gitmodules(text)

    return {
        "submodule": submodule,
        "ide": sorted(a for a in IDE_ARTIFACTS if a in tree),
        "ide_missing": sorted(a for a in IDE_ARTIFACTS if a not in tree),
        # A FILENAME PROBE, AND NOTHING MORE. handbook/propagation-runbook.md
        # warns against exactly this: qmetronome runs the ADR lint as an inline
        # step inside ci.yml, so the filename is absent while the check is
        # running. "missing" here means the seed's filename is not present, not
        # that the project lacks the behaviour -- the field is named for the
        # claim it can actually support.
        "seed_workflow_filenames_present": sorted(
            w.rsplit("/", 1)[-1] for w in SEED_WORKFLOWS if w in tree
        ),
        "seed_workflow_filenames_absent": sorted(
            w.rsplit("/", 1)[-1] for w in SEED_WORKFLOWS if w not in tree
        ),
        "licensing": sorted(a for a in LICENCE_ARTIFACTS if a in tree),
    }


def parse_gitmodules(text: str) -> dict:
    """Where the corpus is mounted in this project, and which branch it tracks.

    Identified by URL rather than by mount path, and by section rather than by
    file: a project may vendor several submodules, and the `branch =` of an
    unrelated one is not this one's pin. alfred's .gitmodules carries
    `branch = master` for a submodule that is not the corpus at all, which a
    whole-file regex reports as the corpus pin.
    """
    path = branch = None
    section_path = section_branch = None
    matched = False
    for line in text.splitlines() + ["[submodule "]:
        stripped = line.strip()
        if stripped.startswith("[submodule"):
            if matched:
                path, branch = section_path, section_branch
                break
            section_path = section_branch = None
            matched = False
            continue
        key, _, value = stripped.partition("=")
        key, value = key.strip(), value.strip()
        if key == "path":
            section_path = value
        elif key == "branch":
            section_branch = value
        elif key == "url" and value.rstrip("/").removesuffix(".git").endswith(
            CORPUS_URL_MARK
        ):
            # `endswith`, not `in`. quaternionmedia/qmetronome contains "/qm"
            # as a substring, so a containment test identifies an unrelated
            # submodule as the corpus.
            matched = True
    return {"corpus_mounted_at": path, "branch": branch}


def github_layer(hub: Hub, projects: list[dict], name_private: bool) -> dict:
    """Observations about the remotes, attached to the projects git found."""
    for entry in projects:
        name = entry["name"]
        repo = hub.repository(name)
        entry["repository"] = repo
        entry["adoption"] = Unknown(repo.reason) if isinstance(repo, Unknown) else adoption(hub, name)
        entry["open_prs"] = hub.open_prs(f"{PROJECT_NS}{name}")
        entry["observed_at"] = now()

    return {"org": org_census(hub, [p["name"] for p in projects], name_private)}


def org_census(hub: Hub, governed: list[str], name_private: bool) -> dict:
    listed = hub.api(
        f"orgs/{hub.org}/repos?per_page=100&type=all",
        ".[] | {name, private, archived}",
        paginate=True,
    )
    if isinstance(listed, Unknown):
        return {"repositories": listed, "observed_at": now()}
    if not isinstance(listed, list):
        return {"repositories": Unknown("orgs/repos: unexpected response shape"), "observed_at": now()}

    names = {r["name"] for r in listed}
    private = {r["name"] for r in listed if r.get("private")}
    unmanaged = sorted(names - set(governed) - {"qm"})
    # Private repository names are withheld by default. This document is
    # committed to a public repository, so listing them publishes the shape of
    # unreleased work as a side effect of measuring governance. Whether that is
    # acceptable is a decision for a human, not a default for a generator --
    # see handbook/handoffs/governance-status-generator.md.
    listable = [n for n in unmanaged if name_private or n not in private]
    return {
        "repositories": {
            "total": len(names),
            "private": len(private),
            "governed": len(set(governed) & names),
            "unmanaged": len(unmanaged),
        },
        "governed_without_repository": sorted(set(governed) - names),
        "unmanaged_named": listable,
        "unmanaged_names_withheld": len(unmanaged) - len(listable),
        "observed_at": now(),
    }


# --------------------------------------------------------------------------
# Assembly, and the check that does not lie about what it verified
# --------------------------------------------------------------------------


def build(
    git: Git, corpus_ref: str, remote: str, hub: Hub, name_private: bool, pins=None
) -> dict:
    layer = git_layer(git, corpus_ref, remote, pins)
    projects = layer["projects"]
    org = (
        {"org": Unknown("no projects to attribute repositories to")}
        if isinstance(projects, Unknown)
        else github_layer(hub, projects, name_private)
    )
    document = {
        "schema": SCHEMA,
        "generated_at": now(),
        # Every input that changes the bytes, recorded in the bytes. An
        # environment variable or a flag that silently alters a committed
        # artifact is an invisible input: two people run the same command in
        # the same clone, get different files, and nothing in either says why.
        "generator": {
            "tool": "ci/governance_status.py",
            "layers": ["git"] + ([] if not hub.enabled else ["github"]),
            "org": hub.org,
            "remote": remote,
            "credential": hub.credential(),
            "private_repository_names_listed": name_private,
            # There is no index mapping a project branch to a repository --
            # handbook/propagation-runbook.md says so outright -- so this
            # assumption is stated rather than buried. A repository that cannot
            # be read under it is unknown, never unadopted.
            "repository_name_assumed": f"{hub.org}/<project branch name>",
            "probed": {
                "submodule_url_contains": CORPUS_URL_MARK,
                "ide": list(IDE_ARTIFACTS),
                "seed_workflow_filenames": [w.rsplit("/", 1)[-1] for w in SEED_WORKFLOWS],
                "licensing": list(LICENCE_ARTIFACTS),
            },
        },
        "corpus": layer["corpus"],
        "projects": projects,
        **org,
        "undefined": UNDEFINED,
    }
    document["generator"]["unknowns"] = count_unknowns(document)
    return document


def pins_from(document: dict) -> dict[str, str]:
    """The commits a document names, so it can be re-derived against itself."""
    pins = {"corpus": document.get("corpus", {}).get("commit", "")}
    for entry in document.get("projects", []):
        branch = entry.get("branch")
        if isinstance(branch, dict) and branch.get("commit"):
            pins[f"project:{entry['name']}"] = branch["commit"]
    return {k: v for k, v in pins.items() if v}


class _Absent:
    """Distinct from every document value, so a missing key never compares equal."""

    def __repr__(self) -> str:
        return "<absent from the document>"


_ABSENT = _Absent()


def as_layer(document: dict) -> dict:
    """The git-layer-shaped view of a document, for comparison against a fresh one."""
    return {"corpus": document.get("corpus", {}), "projects": document.get("projects", [])}


def flatten(node: object, prefix: str = "") -> dict[str, object]:
    out: dict[str, object] = {}
    if isinstance(node, dict):
        for key, value in node.items():
            out.update(flatten(value, f"{prefix}.{key}" if prefix else str(key)))
    elif isinstance(node, list):
        for i, value in enumerate(node):
            out.update(flatten(value, f"{prefix}[{i}]"))
    else:
        out[prefix] = node
    return out


def keyed_by_project(layer: dict) -> dict[str, object]:
    """Flatten a git layer, keying projects by name rather than by position.

    Position is not stable: a project branch created or deleted between two
    generations shifts every index after it, and a positional comparison then
    reports every field of every later project as changed.
    """
    flat = dict(flatten({"corpus": layer["corpus"]}))
    projects = layer["projects"]
    if isinstance(projects, Unknown):
        flat["projects"] = plain(projects)
        return flat
    for entry in projects:
        for key, value in entry.items():
            if key == "name":
                continue
            flat.update(flatten(plain(value), f"projects[{entry['name']}].{key}"))
    return flat


def check(document: dict, git: Git, corpus_ref: str, remote: str) -> int:
    """Re-derive the git layer against the commits the document names.

    WHAT IS COMPARED IS DERIVED FROM THE LAYER, NOT FROM THE FIELD NAMES. An
    earlier version filtered the github fields out with a regex over key paths,
    which meant the rule "what is verifiable" lived in two places -- the layer
    split and the regex -- and a field renamed or re-nested by a later schema
    change would stop matching. Nothing would fail; the check would quietly
    begin asserting that the world had not moved, which is the one claim its
    own docstring says it must never make. Here the comparable key set is
    whatever git_layer emits, so a renamed field is compared by construction
    and a field moved into the github layer stops being compared by
    construction.

    Reports the ratio it could verify. A run that verifies nothing exits
    non-zero rather than printing a clean bill: "0 of 0 fields match" is the
    empty-query pass this whole file is written against.
    """
    pins = pins_from(document)
    if not pins.get("corpus"):
        print("governance status: the document names no corpus commit; nothing to check.")
        return 1

    missing = [ref for ref in pins.values() if not git.exists(ref)]
    try:
        fresh = git_layer(git, corpus_ref, remote, pins)
    except GitError as exc:
        # The commit the document names is not in this clone -- a shallow
        # checkout, or one that never fetched the corpus history. Nothing can
        # be re-derived, so nothing may be reported as verified. This is the
        # path that makes the "compared nothing" refusal below reachable
        # rather than decorative.
        print(f"corpus          {pins['corpus'][:8]} (not in this clone)")
        print(f"\nNothing was comparable: {exc}")
        print("A check that verifies nothing is not a pass. Fetch the history first.")
        return 1
    got = keyed_by_project(fresh)
    want = {k: v for k, v in keyed_by_project(as_layer(document)).items() if k in got}

    unverifiable = {k for k, v in got.items() if isinstance(v, str) and "not in this clone" in v}
    comparable = set(got) - unverifiable
    differing = sorted(k for k in comparable if want.get(k, _ABSENT) != got.get(k))

    print(f"corpus          {pins['corpus'][:8]} ({corpus_ref} @ {git.sha(corpus_ref)[:8]})")
    print(f"verified        {len(comparable) - len(differing)} of {len(comparable)} git-layer field(s)")
    if unverifiable:
        print(f"unverifiable    {len(unverifiable)} field(s): commit not in this clone")
    if missing:
        print(f"missing commits {len(missing)}: fetch the branches this document names")

    behind = git.count(f"{pins['corpus']}..{git.sha(corpus_ref)}") if git.exists(pins["corpus"]) else None
    if behind:
        print(f"age             {behind} commit(s) behind {corpus_ref}; regenerate to refresh")

    if not comparable:
        print("\nNothing was comparable. A check that verifies nothing is not a pass.")
        return 1
    if differing:
        print(f"\n{len(differing)} field(s) do not match the commits this document names:")
        for key in differing[:40]:
            print(f"  {key}: document={want.get(key)!r} derived={got.get(key)!r}")
        if len(differing) > 40:
            print(f"  ... and {len(differing) - 40} more")
        print("\nRegenerate with --write. The document is not a faithful rendering of\n"
              "the commits it names, which is the one thing this check can establish.")
        return 1
    print("\nThe document faithfully renders the commits it names.")
    return 0


def force_utf8_output() -> None:
    """Branch names and pull request titles are data this tool did not author.

    One emoji in a PR title crashes a Windows console's cp1252 encoder, and the
    report dies partway through having already printed a confident header.
    """
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")


def main() -> int:
    force_utf8_output()
    parser = argparse.ArgumentParser(description="Emit or verify the governance status document.")
    parser.add_argument("--repo", type=Path, default=Path.cwd(), help="corpus clone")
    parser.add_argument("--corpus-ref", default="origin/main")
    parser.add_argument("--org", default="quaternionmedia")
    parser.add_argument("--remote", default="origin", help="remote whose project/* refs are the registry")
    parser.add_argument("--write", type=Path, help="write the document here")
    parser.add_argument("--check", type=Path, help="verify an existing document's git layer")
    parser.add_argument("--offline", action="store_true", help="skip github; those fields become unknown")
    parser.add_argument(
        "--name-private-repositories",
        action="store_true",
        help="list unmanaged private repositories by name. Off by default: this "
        "document is committed to a public repository.",
    )
    args = parser.parse_args()

    git = Git(args.repo)
    if not git.ok("rev-parse", "--git-dir"):
        print(f"governance status: not a git repository: {args.repo}", file=sys.stderr)
        return 2
    if not git.exists(args.corpus_ref):
        print(f"governance status: no such ref: {args.corpus_ref}", file=sys.stderr)
        return 2

    if args.check:
        import yaml  # deferred: only --check needs to read YAML back

        document = yaml.safe_load(args.check.read_text(encoding="utf-8"))
        if not isinstance(document, dict):
            print(f"governance status: {args.check} is not a document.", file=sys.stderr)
            return 2
        return check(document, git, args.corpus_ref, args.remote)

    document = build(
        git,
        args.corpus_ref,
        args.remote,
        Hub(args.org, enabled=not args.offline),
        args.name_private_repositories,
    )
    text = dumps(document)
    if args.write:
        # newline="\n" explicitly: this file is byte-compared, and Python on
        # Windows writes CRLF by default. A local run reporting the document
        # stale for line endings alone teaches contributors that the check is
        # noise, which is the fastest way to make a gate useless.
        args.write.write_text(text, encoding="utf-8", newline="\n")
        projects = document["projects"]
        count = "unknown" if isinstance(projects, dict) else str(len(projects))
        print(
            f"governance status: wrote {args.write} "
            f"({count} project(s), {document['generator']['unknowns']} unknown(s))"
        )
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
