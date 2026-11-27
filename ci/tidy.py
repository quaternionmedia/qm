#!/usr/bin/env python3
"""What there is to tidy in each family, read from each default branch.

    uv run qm tidy --family core
    uv run qm tidy --offline --json
    uv run --extra tidy qm tidy          # with the unused-code count

One row per repository a family claims, and per repository the facts a tidy
starts from that no other command here prints:

  default     the default branch, as the host names it; offline, as the clone
              recorded it in `<remote>/HEAD`. It is never assumed.
  commit      the commit of that branch this clone holds, which is the tree
              every figure beside it describes.
  files       files tracked in that tree.
  remote      branches on the remote, the default included.
  merged      of the others, those whose tip the default branch contains.
  local       local branches in the clone.
  worktrees   linked worktrees, the clone's own tree not counted.
  prs         open pull requests, whoever opened them; `bots` of them opened
              by an automation account and `drafts` of them marked draft.
  unused      unused imports, redefinitions and unused locals in that tree's
              Python files, as `ruff` rules F401, F811 and F841 count them.

**The tree is the default branch's, never the checkout.** The checked-out
branch is an accident of who ran what last, so nothing here reads `HEAD`, the
index or the working tree. The unused-code count is taken from the blobs of the
default branch's tree, written to a temporary directory outside every clone
and removed afterwards, and counted with the tool's own defaults rather than
the repository's configuration, so one rule set measures every row. A
repository whose own configuration excuses a line still has it counted here,
and a directory the tool skips by default, such as `build` or `venv`, is
skipped where it is tracked.

**A fact that could not be established is `unknown`, with the reason.** No
clone on this disk, no `<remote>/HEAD` and nobody to ask, a default branch
this clone has never fetched, `gh` or `ruff` not installed, a host that
refused: each is a cell reading `unknown` and a line beneath the table saying
why. Nothing is assumed in its place and nothing reads as zero.

What it leaves to the commands that own it: which local branches hold work
that exists on this disk alone (`qm estate`), what deleting each branch would
cost (`qm branches --repo <path>`), the current user's own stacks
(`qm stacks`), and who is in a family (`qm families`). The roster, the clone
resolution and the private companion are `ci/roster.py` and
`ci/make_workspace.py`, read the way `ci/estate.py` reads them.

What it refuses to do:

  * **It writes nothing in any repository.** No fetch, prune, checkout,
    delete or push, and no flag to ask for one. The `git` helper refuses any
    verb outside a short list of readers.
  * **It is a reading, not a gate.** A completed reading exits zero whatever
    it found. A roster that cannot be read, or a family the record does not
    declare, exits two: the command did not run.
  * **It names a private repository only by its roster reference**, in the
    table, in the reasons and in `--json`.

`--offline` asks the host nothing: no `ls-remote`, no `gh`. The remote is then
the tracking refs, as of the last fetch, and the pull request cells are
unknown. Online it asks each clone's remote once and the host's pull request
list once, and says how many times it asked.

What it cannot tell: whether a merged branch is still wanted by name, whether
an open pull request is abandoned, or whether an unused import is one a
package re-exports on purpose. It counts and stops; the tidy is a person's
act. It reads Python alone for unused code, and a repository in another
language reads `no .py`, which is not a clean bill.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from dataclasses import asdict, dataclass, field
from pathlib import Path, PurePosixPath

import yaml

# Imported two ways, as `ci.<name>` by the qm CLI and as a bare script; the
# sibling imports below resolve under both, as `ci/estate.py` arranges it.
sys.path.insert(0, str(Path(__file__).resolve().parent))
import families as family_record  # noqa: E402
from estate import label  # noqa: E402
from make_workspace import resolve  # noqa: E402
from roster import ROSTER, families_of, load, redact  # noqa: E402

CORPUS = Path(__file__).resolve().parent.parent

# Every git verb this module may run. `worktree` is a reader only as
# `worktree list`, and the helper holds it to that.
READ_VERBS = frozenset({
    "rev-parse", "symbolic-ref", "for-each-ref", "ls-remote", "ls-tree",
    "cat-file", "merge-base", "worktree",
})

RULES = ("F401", "F811", "F841")

# The facts a row carries, in column order: (field, heading).
COLUMNS = (
    ("files", "files"), ("remote", "remote"), ("merged", "merged"),
    ("local", "local"), ("worktrees", "worktrees"), ("prs", "prs"),
    ("bots", "bots"), ("drafts", "drafts"), ("unused", "unused"),
)

NO_CLONE = "no clone on this disk"
NO_PYTHON = "no .py"


class Refused(RuntimeError):
    """A git verb outside `READ_VERBS`, which this module must never run."""


def unknown(reason: str) -> dict:
    """A fact that was not established, in the shape `ci/inventory.py` uses."""
    return {"unknown": reason}


def is_unknown(value) -> bool:
    return isinstance(value, dict) and "unknown" in value


def run_git(repo: Path, *args: str, stdin: bytes | None = None
            ) -> subprocess.CompletedProcess:
    """`git -C repo <args>` in bytes, refused unless the verb is a reader.

    The one place git is spawned, so the refusal cannot be walked around by a
    later edit that forgot the list existed.
    """
    if (not args or args[0] not in READ_VERBS
            or (args[0] == "worktree" and args[1:2] != ("list",))):
        raise Refused(f"git {' '.join(args) or '<nothing>'} is not a read")
    return subprocess.run(("git", "-C", str(repo), *args), capture_output=True,
                          input=stdin)


def text(raw: bytes | None) -> str:
    return (raw or b"").decode("utf-8", errors="replace")


def git(repo: Path, *args: str) -> str | None:
    """Standard output, or None when git says no.

    None rather than an empty string: no branches and no worktrees are
    answers, and a reader must be able to tell them from a command that failed.
    """
    done = run_git(repo, *args)
    return text(done.stdout) if done.returncode == 0 else None


def first_line(raw: bytes | str | None, otherwise: str) -> str:
    said = (text(raw) if isinstance(raw, bytes) else (raw or "")).strip().splitlines()
    return said[0].strip() if said else otherwise


def run_gh(args: list[str], cwd: Path) -> subprocess.CompletedProcess:
    """One seam for the host CLI, so a test can stand in for it."""
    return subprocess.run(("gh", *args), capture_output=True, text=True,
                          encoding="utf-8", errors="replace", cwd=str(cwd))


def run_ruff(executable: str, directory: Path) -> subprocess.CompletedProcess:
    """One seam for the linter, so a test can stand in for it.

    `--isolated` ignores every configuration file, the user's own included,
    so the count is the same rule set on every machine and every row.
    """
    return subprocess.run(
        (executable, "check", "--isolated", "--no-cache", "--exit-zero",
         "--select", ",".join(RULES), "--output-format", "json", str(directory)),
        capture_output=True, text=True, encoding="utf-8", errors="replace")


@dataclass
class Reading:
    """One roster entry, and what there is to tidy in it.

    Every fact is its value or `{"unknown": reason}`.
    """

    name: str
    found: bool = False
    default: str | dict = field(default_factory=lambda: unknown(NO_CLONE))
    commit: str | dict = field(default_factory=lambda: unknown(NO_CLONE))
    files: int | dict = field(default_factory=lambda: unknown(NO_CLONE))
    remote: int | dict = field(default_factory=lambda: unknown(NO_CLONE))
    merged: int | dict = field(default_factory=lambda: unknown(NO_CLONE))
    local: int | dict = field(default_factory=lambda: unknown(NO_CLONE))
    worktrees: int | dict = field(default_factory=lambda: unknown(NO_CLONE))
    prs: int | dict = field(default_factory=lambda: unknown(NO_CLONE))
    bots: int | dict = field(default_factory=lambda: unknown(NO_CLONE))
    drafts: int | dict = field(default_factory=lambda: unknown(NO_CLONE))
    unused: int | dict = field(default_factory=lambda: unknown(NO_CLONE))
    unused_by_rule: dict = field(default_factory=dict)
    python_files: int | None = None
    notes: list[str] = field(default_factory=list)


def ask_host(repo: Path, remote: str) -> dict:
    """The remote's default branch and every branch tip, in one round trip.

    `{"default": name or None, "heads": {name: sha}}`, or an unknown carrying
    what git said.
    """
    done = run_git(repo, "ls-remote", "--symref", remote, "HEAD", "refs/heads/*")
    if done.returncode != 0:
        return unknown(first_line(done.stderr, "git ls-remote gave no reason"))
    default, heads = None, {}
    for line in text(done.stdout).splitlines():
        left, _, right = line.partition("\t")
        if left.startswith("ref: refs/heads/") and right.strip() == "HEAD":
            default = left.removeprefix("ref: refs/heads/").strip()
        elif right.startswith("refs/heads/"):
            heads[right.removeprefix("refs/heads/").strip()] = left.strip()
    return {"default": default, "heads": heads}


def tracking(repo: Path, remote: str, *extra: str) -> dict[str, str] | None:
    """Branch name -> tip sha from the tracking refs, as of the last fetch."""
    prefix = f"refs/remotes/{remote}/"
    out = git(repo, "for-each-ref", *extra, "--format=%(objectname) %(refname)",
              f"refs/remotes/{remote}")
    if out is None:
        return None
    found = {}
    for line in out.splitlines():
        sha, _, ref = line.partition(" ")
        # `<remote>/HEAD` is a symbolic ref, not a branch.
        if ref.startswith(prefix) and ref != f"{prefix}HEAD":
            found[ref[len(prefix):]] = sha
    return found


def default_branch(repo: Path, remote: str, host: dict | None) -> tuple[str | dict, list[str]]:
    """The default branch, or why it is unknown. Never a guess.

    The host's own answer where it gave one; else the symref the clone
    recorded. With neither there is no default branch to read, and a name
    assumed here would put another branch's figures in every column.
    """
    notes: list[str] = []
    prefix = f"refs/remotes/{remote}/"
    recorded = (git(repo, "symbolic-ref", f"{prefix}HEAD") or "").strip()
    recorded = recorded.removeprefix(prefix) if recorded.startswith(prefix) else ""
    if host is not None and not is_unknown(host) and host["default"]:
        if recorded and recorded != host["default"]:
            notes.append(f"{remote}/HEAD in this clone names {recorded} and the "
                         f"host names {host['default']}; the host's is read")
        return host["default"], notes
    if recorded:
        return recorded, notes
    if host is None:
        why = "--offline asks the host nothing"
    elif is_unknown(host):
        why = f"the host could not be asked: {host['unknown']}"
    else:
        why = "the host names none"
    return unknown(f"no {remote}/HEAD in this clone, and {why}"), notes


def tree_entries(repo: Path, commit: str) -> list[tuple[str, str, str]] | None:
    """`(mode, sha, path)` for every file in the commit's tree; no gitlinks."""
    done = run_git(repo, "ls-tree", "-r", "-z", commit)
    if done.returncode != 0:
        return None
    found = []
    for record in done.stdout.split(b"\0"):
        meta, _, path = record.partition(b"\t")
        parts = meta.split()
        if len(parts) == 3 and parts[1] == b"blob":
            found.append((text(parts[0]), text(parts[2]), text(path)))
    return found


def write_blobs(repo: Path, blobs: list[tuple[str, str]], out: Path) -> int | None:
    """Write `(sha, path)` blobs under `out`; the number written, or None.

    One `cat-file --batch` for every blob, and the raw bytes: no checkout, no
    attribute and no line-ending conversion stands between the tree and what
    is counted. A path that cannot be written on this disk is left out and
    not counted as written.
    """
    done = run_git(repo, "cat-file", "--batch",
                   stdin="".join(f"{sha}\n" for sha, _ in blobs).encode("ascii"))
    if done.returncode != 0:
        return None
    data, at, written = done.stdout, 0, 0
    for _, path in blobs:
        end = data.find(b"\n", at)
        header = data[at:end].split()
        if end < 0 or len(header) != 3 or header[1] != b"blob":
            return None
        size = int(header[2])
        body = data[end + 1:end + 1 + size]
        at = end + 1 + size + 1
        relative = PurePosixPath(path)
        if relative.is_absolute() or ".." in relative.parts:
            continue
        target = out.joinpath(*relative.parts)
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(body)
        except OSError:
            continue
        written += 1
    return written


def unused_code(repo: Path, entries: list[tuple[str, str, str]],
                ruff: str | None) -> tuple[int | dict | str, dict, int, list[str]]:
    """The unused-code count for one tree: (count, by rule, python files, notes)."""
    python = [(sha, path) for mode, sha, path in entries
              if path.endswith(".py") and mode.startswith("100")]
    if not python:
        return NO_PYTHON, {}, 0, []
    if ruff is None:
        return unknown("ruff not installed"), {}, len(python), []
    notes: list[str] = []
    with tempfile.TemporaryDirectory(prefix="qm-tidy-") as scratch:
        out = Path(scratch) / "tree"
        out.mkdir()
        written = write_blobs(repo, python, out)
        if written is None:
            return unknown("the tree's files could not be read from the clone"), {}, len(python), []
        if written != len(python):
            notes.append(f"{len(python) - written} of {len(python)} Python files "
                         f"could not be written out for the linter and are not counted")
        try:
            done = run_ruff(ruff, out)
        except OSError as exc:
            return unknown(f"ruff could not be run: {exc}"), {}, len(python), notes
    try:
        findings = json.loads(done.stdout or "")
    except json.JSONDecodeError:
        return (unknown("ruff gave no reading: "
                        + first_line(done.stderr, "no output")), {}, len(python), notes)
    by_rule = {rule: 0 for rule in RULES}
    for finding in findings:
        if finding.get("code") in by_rule:
            by_rule[finding["code"]] += 1
    return sum(by_rule.values()), by_rule, len(python), notes


def is_automation(pull: dict) -> bool:
    """Opened by an automation account, as the host itself marks the author."""
    author = pull.get("author") or {}
    return bool(author.get("is_bot")) or str(author.get("login", "")).startswith("app/")


def pull_requests(reading: Reading, repo: Path, online: bool,
                  tally: list[str]) -> None:
    """Every open pull request, split by who opened it and whether it is a draft."""
    if not online:
        why = unknown("--offline asks the host nothing")
    else:
        why = None
        tally.append("gh")
        try:
            done = run_gh(["pr", "list", "--state", "open", "--limit", "1000",
                           "--json", "number,isDraft,author"], repo)
        except FileNotFoundError:
            why = unknown("gh not installed")
        except OSError as exc:
            why = unknown(f"gh could not be run: {exc}")
        else:
            if done.returncode != 0:
                why = unknown(first_line(done.stderr, "gh gave no reason"))
            else:
                try:
                    pulls = json.loads(done.stdout or "[]")
                except json.JSONDecodeError as exc:
                    why = unknown(f"gh output was not JSON ({exc})")
    if why is not None:
        reading.prs = reading.bots = reading.drafts = why
        return
    reading.prs = len(pulls)
    reading.bots = sum(1 for p in pulls if is_automation(p))
    reading.drafts = sum(1 for p in pulls if p.get("isDraft"))


def read_repository(entry: dict, path: Path, remote: str, online: bool,
                    ruff: str | None, tally: list[str] | None = None) -> Reading:
    """One clone, read. `tally` receives a word for each question put to the host."""
    reading = Reading(name=label(entry), found=True)
    tally = tally if tally is not None else []

    host = None
    if online:
        tally.append("ls-remote")
        host = ask_host(path, remote)
    reading.default, notes = default_branch(path, remote, host)
    reading.notes.extend(notes)

    local = git(path, "for-each-ref", "--format=%(refname)", "refs/heads")
    reading.local = (unknown("the clone's branches could not be read") if local is None
                     else len(local.split()))

    listed = git(path, "worktree", "list", "--porcelain")
    reading.worktrees = (
        unknown("the clone's worktrees could not be read") if listed is None
        # The first entry is the clone's own tree, which is not one to tidy.
        else max(0, sum(1 for l in listed.splitlines() if l.startswith("worktree ")) - 1))

    recorded = tracking(path, remote)
    usable_host = host is not None and not is_unknown(host)
    if usable_host:
        heads = host["heads"]
    elif recorded is None:
        heads = None
    else:
        heads = recorded
        if online:
            reading.notes.append(f"{remote} could not be asked ({host['unknown']}); "
                                 f"its branches are the tracking refs, as of the last fetch")
    reading.remote = (unknown(f"{remote} could not be read") if heads is None
                      else len(heads))

    pull_requests(reading, path, online, tally)

    if is_unknown(reading.default):
        because = reading.default
        reading.commit = reading.files = reading.merged = reading.unused = because
        return reading

    ref = f"refs/remotes/{remote}/{reading.default}"
    commit = (git(path, "rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}") or "").strip()
    if not commit:
        because = unknown(f"no {remote}/{reading.default} in this clone; "
                          f"it has not been fetched")
        reading.commit = reading.files = reading.merged = reading.unused = because
        return reading
    reading.commit = commit
    if usable_host and host["heads"].get(reading.default) not in (None, commit):
        reading.notes.append(
            f"{remote}/{reading.default} in this clone is at {commit[:7]} and the host "
            f"is at {host['heads'][reading.default][:7]}; the tree read is the clone's")

    entries = tree_entries(path, commit)
    if entries is None:
        reading.files = reading.unused = unknown("the tree could not be listed")
    else:
        reading.files = len(entries)
        reading.unused, reading.unused_by_rule, reading.python_files, notes = (
            unused_code(path, entries, ruff))
        reading.notes.extend(notes)

    if heads is not None:
        contained = tracking(path, remote, "--merged", commit) or {}
        merged = unfetched = 0
        for name, sha in heads.items():
            if name == reading.default:
                continue
            if contained.get(name) == sha:
                merged += 1
                continue
            # The host's tip is not the one this clone recorded: ask the
            # objects. Exit 0 is contained, 1 is not, anything else is a
            # commit this clone does not hold.
            status = run_git(path, "merge-base", "--is-ancestor", sha, commit).returncode
            if status == 0:
                merged += 1
            elif status != 1:
                unfetched += 1
        reading.merged = merged
        if unfetched:
            reading.notes.append(
                f"{unfetched} branch(es) on {remote} are at a commit this clone has "
                f"not fetched; they are counted as not merged")
    else:
        reading.merged = unknown(f"{remote} could not be read")
    return reading


def publish(reading: Reading, entry: dict) -> Reading:
    """A private repository's name replaced by its reference, in every string.

    A reason carries what git or the host said, and either may say the name.
    """
    name, ref = entry.get("name"), entry.get("ref")
    if not ref or not name or name == ref:
        return reading
    return Reading(**redact(asdict(reading), name, ref))


def members(roster: list[dict], family: str, parents: dict) -> list[dict]:
    """The entries claiming `family` or a family that sits within it."""
    return [e for e in roster
            if any(f == family or family in family_record.ancestors(f, parents)
                   for f in families_of(e))]


def read(roster: list[dict], search_roots: list[Path], wanted: list[str] | None,
         parents: dict, remote: str = "origin", online: bool = True,
         ruff: str | None = None,
         tally: list[str] | None = None) -> list[tuple[str, list[Reading]]]:
    """Each family and a row for every entry it claims. Never fewer rows.

    `wanted` of None is every family with a clone on this disk. A repository
    in two families is read once and is a row under each.
    """
    paths = {id(e): resolve(e, search_roots) for e in roster}
    if wanted is None:
        claimed = sorted({f for e in roster for f in families_of(e)}
                         | {p for p in parents.values() if p})
        wanted = [f for f in claimed
                  if any(paths[id(e)] is not None for e in members(roster, f, parents))]
    done: dict[int, Reading] = {}
    found = []
    for family in wanted:
        rows = []
        for entry in members(roster, family, parents):
            if id(entry) not in done:
                path = paths[id(entry)]
                done[id(entry)] = (
                    Reading(name=label(entry)) if path is None
                    else publish(read_repository(entry, path, remote, online, ruff, tally), entry))
            rows.append(done[id(entry)])
        found.append((family, rows))
    return found


def cell(value) -> str:
    return "unknown" if is_unknown(value) else str(value)


def reasons(reading: Reading) -> list[tuple[str, str]]:
    """`(facts, reason)` for each reason, naming every fact it left unknown."""
    grouped: dict[str, list[str]] = {}
    facts = (("default", "default"), ("commit", "commit")) + COLUMNS
    for name, heading in facts:
        value = getattr(reading, name)
        if is_unknown(value):
            grouped.setdefault(value["unknown"], []).append(heading)
    return [(", ".join(headings), reason) for reason, headings in grouped.items()]


def render(found: list[tuple[str, list[Reading]]], online: bool,
           ruff_version: str | None, asked: int) -> str:
    out: list[str] = []
    every = [r for _, rows in found for r in rows]
    width = max([len("repository")] + [len(r.name) for r in every])
    branch = max([len("default")] + [len(cell(r.default)) for r in every])
    for family, rows in found:
        present = sum(1 for r in rows if r.found)
        out.append(f"## {family}  {len(rows)} named, {present} on this disk")
        out.append(f"  {'repository':<{width}}  {'default':<{branch}}  {'commit':<7}  "
                   + "  ".join(f"{heading:>9}" for _, heading in COLUMNS))
        for r in rows:
            commit = cell(r.commit) if is_unknown(r.commit) else r.commit[:7]
            out.append(f"  {r.name:<{width}}  {cell(r.default):<{branch}}  {commit:<7}  "
                       + "  ".join(f"{cell(getattr(r, name)):>9}" for name, _ in COLUMNS))
        out.append("")

    distinct = list({r.name: r for r in every}.values())
    # A reason every clone shares is said once: under --offline it is the same
    # line for every row, and repeated it buries the ones that differ.
    clones = [r for r in distinct if r.found]
    shared = ([pair for pair in reasons(clones[0])
               if all(pair in reasons(r) for r in clones)] if len(clones) > 1 else [])
    said = [f"every clone: {facts} unknown: {reason}" for facts, reason in shared]
    for r in distinct:
        said.extend(f"{r.name}: {facts} unknown: {reason}"
                    for facts, reason in reasons(r) if (facts, reason) not in shared)
        said.extend(f"{r.name}: {note}" for note in r.notes)
    if said:
        out.extend(f"  {line}" for line in said)
        out.append("")

    out.append("  Every figure but local and worktrees describes the default branch "
               "at the commit shown, never the checkout.")
    out.append("  remote counts the default branch; merged is of the others. "
               "prs is every open pull request, bots and drafts among them.")
    out.append("  unused is ruff " + ", ".join(RULES) + " over that tree's Python files, "
               + (f"with the tool's defaults ({ruff_version})." if ruff_version
                  else "and ruff is not installed here: uv run --extra tidy qm tidy."))
    if online:
        out.append(f"  The host was asked {asked} time(s): one ls-remote and one "
                   f"pull request listing for each clone found.")
    else:
        out.append("  --offline: the remote is as of the last fetch, and no pull "
                   "request was asked about.")
    out.append("  What each local branch holds is `qm estate`; what deleting a branch "
               "costs is `qm branches --repo <path>`.")
    out.append("  This reading writes nothing in any repository. Tidying is a "
               "person's act.")
    return "\n".join(out) + "\n"


def as_document(found: list[tuple[str, list[Reading]]], online: bool,
                ruff_version: str | None, asked: int) -> dict:
    return {
        "schema": 1,
        "offline": not online,
        "rules": list(RULES),
        "ruff": ruff_version,
        "host_calls": asked,
        "families": [{"name": family, "repositories": [asdict(r) for r in rows]}
                     for family, rows in found],
    }


def version_of(ruff: str | None) -> str | None:
    if ruff is None:
        return None
    try:
        done = subprocess.run((ruff, "--version"), capture_output=True, text=True,
                              encoding="utf-8", errors="replace")
    except OSError:
        return None
    return done.stdout.strip() or None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="What there is to tidy in each family, read from each "
                    "default branch and never from a checkout.")
    parser.add_argument("--family", action="append", default=[],
                        help="a family to read. Repeatable. Default: every family "
                             "with a clone on this disk.")
    parser.add_argument("--roster", type=Path, default=ROSTER)
    parser.add_argument(
        "--search-root", action="append", type=Path, default=[],
        help="a directory the roster's paths are relative to. Repeatable. "
             "Default: two directories above the corpus clone.")
    parser.add_argument("--remote", default="origin")
    parser.add_argument("--offline", action="store_true",
                        help="ask nothing of the host: no ls-remote, no gh")
    parser.add_argument("--json", action="store_true",
                        help="emit the reading as one JSON document")
    parser.add_argument("--ruff", default=None,
                        help="the ruff executable. Default: the one on PATH, "
                             "which `uv run --extra tidy` provides.")
    args = parser.parse_args(argv)

    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    try:
        roster = load(args.roster)
    except (OSError, ValueError, yaml.YAMLError) as exc:
        print(f"tidy: cannot read the roster at {args.roster}: {exc}", file=sys.stderr)
        return 2
    if not roster:
        print(f"tidy: {args.roster} lists no repositories", file=sys.stderr)
        return 2

    declared = family_record.declared(CORPUS / family_record.RECORD)
    parents = family_record.within(CORPUS / family_record.RECORD)
    strangers = [f for f in args.family if f not in declared]
    if strangers:
        print(f"tidy: {', '.join(strangers)}: not a family "
              f"{family_record.RECORD.as_posix()} declares. Declared: "
              + ", ".join(sorted(declared)), file=sys.stderr)
        return 2

    search_roots = [p.resolve() for p in args.search_root] or [CORPUS.parent.parent]
    online = not args.offline
    ruff = args.ruff or shutil.which("ruff")
    tally: list[str] = []
    found = read(roster, search_roots, args.family or None, parents,
                 args.remote, online, ruff, tally)
    asked = len(tally)

    if args.json:
        json.dump(as_document(found, online, version_of(ruff), asked),
                  sys.stdout, indent=2)
        sys.stdout.write("\n")
    else:
        sys.stdout.write(render(found, online, version_of(ruff), asked))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
