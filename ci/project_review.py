#!/usr/bin/env python3
"""One adopted project, read against the corpus it adopted.

    uv run qm project <name>
    python ci/project_review.py <name> --search-root <dir> --offline --json

`handbook/propagation-runbook.md` has two parts, and a project is current when
both hold. This reads each of them for one project and prints one line per
fact, so a refresh starts from what is behind and not from a page describing
it. `protocols/project-refresh.md` is the procedure this is the opening step of.

**The corpus side**, from this clone's remote-tracking refs:

- how far `project/<name>` is behind `main`;
- whether its `adr/TEMPLATE.md` is the seed's file;
- whether its `adr/README.md` still carries a seed placeholder.

**The project's side**, from the remote-tracking refs of its clone:

- whether the governance submodule pins the tip of `project/<name>`;
- each seed workflow in `project-seed/ci/seed-workflows.txt`: the seed's
  file, a different file, or absent;
- whether the governance section of its `AGENTS.md` is the seed's, with the
  project's name substituted;
- whether `CLAUDE.md` is the seed's one-line import.

**The host**, unless `--offline`: every open pull request in the project's
repository, and every one here whose base is `project/<name>`, with its age.

It reads refs and never a working tree, so a branch checked out in either
clone does not change the answer. It writes nothing, fetches nothing and runs
no test.

Each fact is `current`, `behind` or `unknown`. `unknown` is a value: the fact
was not established, and the line says why. The exit status is 0 when every
fact is current, 1 when any is behind or unknown, and 2 when the review did
not run.

What it cannot see: whether the project's tests pass, which is the project's
own command to run; whether a workflow that is the seed's file passes on the
host; whether a record on the branch is right; and anything a fetch has not
brought in. A tracking ref older than the host's is reported when the host
can be asked, and is invisible with `--offline`.
"""

from __future__ import annotations

import argparse
import configparser
import json
import re
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from make_workspace import resolve  # noqa: E402
from roster import ROSTER, load  # noqa: E402

CORPUS = Path(__file__).resolve().parent.parent
ORG = "quaternionmedia"

CURRENT = "current"
BEHIND = "behind"
UNKNOWN = "unknown"

SEED_WORKFLOWS = "project-seed/ci/seed-workflows.txt"
SEED_TEMPLATE = "project-seed/adr/TEMPLATE.md"
SEED_AGENTS = "project-seed/ide/AGENTS.md"
SEED_IMPORT = "project-seed/ide/CLAUDE.md"

# The line a project's own section of AGENTS.md begins at. Everything above it
# is the seed's governance section; everything from it down is the project's.
PROJECT_LINE = "<!-- Project-specific"
SEED_COMMENT = re.compile(r"\A<!-- SEED FILE:.*?-->\n", re.S)
PLACEHOLDER = "<name>"

# Every git verb this module may run. The helper refuses any other, so "it
# writes nothing and fetches nothing" is enforced here and not by a reader.
READ_VERBS = frozenset({
    "rev-parse", "rev-list", "ls-tree", "show", "merge-base", "ls-remote",
    "symbolic-ref",
})


class Refused(RuntimeError):
    """A git verb outside `READ_VERBS`, which this module must never run."""


@dataclass
class Fact:
    """One line of the review: where it was read, what was asked, the answer."""
    side: str
    subject: str
    state: str
    detail: str
    remedy: str = ""


def run_git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    if not args or args[0] not in READ_VERBS:
        raise Refused(f"git {' '.join(args) or '<nothing>'} is not a read")
    return subprocess.run(("git", "-C", str(repo), *args), capture_output=True,
                          text=True, encoding="utf-8", errors="replace")


def git(repo: Path, *args: str) -> str | None:
    """Standard output, or None when git says no. None is not an empty answer."""
    done = run_git(repo, *args)
    return done.stdout if done.returncode == 0 else None


def run_gh(args: list[str], cwd: Path) -> subprocess.CompletedProcess:
    """One seam for the host CLI, so a test can stand in for it."""
    return subprocess.run(("gh", *args), capture_output=True, text=True,
                          encoding="utf-8", errors="replace", cwd=str(cwd))


def commit_of(repo: Path, ref: str) -> str | None:
    out = git(repo, "rev-parse", "--verify", "-q", f"{ref}^{{commit}}")
    return out.strip() if out else None


def blob_of(repo: Path, ref: str, path: str) -> str | None:
    """The object a path names at a ref, or None when the path is not there."""
    out = git(repo, "rev-parse", "--verify", "-q", f"{ref}:{path}")
    return out.strip() if out else None


def text_of(repo: Path, ref: str, path: str) -> str | None:
    return git(repo, "show", f"{ref}:{path}")


def default_ref(repo: Path, remote: str) -> str | None:
    """The remote's default branch as a tracking ref, as the last fetch left it."""
    out = git(repo, "symbolic-ref", "-q", f"refs/remotes/{remote}/HEAD")
    if out:
        return out.strip().removeprefix("refs/remotes/")
    for guess in ("main", "master"):
        if commit_of(repo, f"{remote}/{guess}"):
            return f"{remote}/{guess}"
    return None


def host_tip(repo: Path, remote: str, branch: str) -> str | None:
    out = git(repo, "ls-remote", remote, f"refs/heads/{branch}")
    if not out or not out.strip():
        return None
    return out.split()[0]


def tracking_is_fresh(side: str, repo: Path, remote: str, ref: str) -> Fact | None:
    """A tracking ref older than the host's tip makes every line below it a
    reading of the last fetch. Returns the fact when that is so, else None."""
    branch = ref.removeprefix(f"{remote}/")
    tip = host_tip(repo, remote, branch)
    if tip is None:
        return Fact(side, f"{ref} against the host", UNKNOWN,
                    f"the host did not answer for {branch}")
    if tip != commit_of(repo, ref):
        return Fact(side, f"{ref} against the host", BEHIND,
                    f"the host is at {tip[:7]} and this clone's ref is not",
                    f"git -C {repo} fetch {remote}")
    return None


# ---------------------------------------------------------------- corpus side

def corpus_side(corpus: Path, name: str, remote: str = "origin") -> list[Fact]:
    side = "corpus"
    branch, main = f"{remote}/project/{name}", f"{remote}/main"
    if commit_of(corpus, branch) is None:
        return [Fact(side, f"project/{name}", UNKNOWN,
                     f"{branch} is not a ref in this clone",
                     f"git fetch {remote}, or the project has no branch here")]
    facts: list[Fact] = []

    behind = git(corpus, "rev-list", "--count", f"{branch}..{main}")
    if behind is None:
        facts.append(Fact(side, f"project/{name} against main", UNKNOWN,
                          f"{main} could not be read"))
    elif int(behind):
        facts.append(Fact(side, f"project/{name} against main", BEHIND,
                          f"{int(behind)} commit(s) on main are not on the branch",
                          f"propagate/{name}-<date>, cut from project/{name}, "
                          "with main merged into it"))
    else:
        facts.append(Fact(side, f"project/{name} against main", CURRENT,
                          "carries every commit on main"))

    seed, copy = blob_of(corpus, main, SEED_TEMPLATE), blob_of(corpus, branch, "adr/TEMPLATE.md")
    if copy is None:
        facts.append(Fact(side, "adr/TEMPLATE.md", UNKNOWN,
                          "the branch has no adr/TEMPLATE.md; its records may "
                          "live in the project's own tree"))
    elif copy == seed:
        facts.append(Fact(side, "adr/TEMPLATE.md", CURRENT, "the seed's file"))
    else:
        facts.append(Fact(side, "adr/TEMPLATE.md", BEHIND,
                          "differs from the seed's template on main",
                          f"copy {SEED_TEMPLATE} over it"))

    readme = text_of(corpus, branch, "adr/README.md")
    if readme is None:
        facts.append(Fact(side, "adr/README.md", UNKNOWN, "the branch has none"))
    elif PLACEHOLDER in readme:
        facts.append(Fact(side, "adr/README.md", BEHIND,
                          f"still carries the seed placeholder {PLACEHOLDER}",
                          f"substitute {name}; "
                          "project-seed/ci/check_placeholders.py names the line"))
    else:
        facts.append(Fact(side, "adr/README.md", CURRENT, "no seed placeholder"))
    return facts


# --------------------------------------------------------------- project side

def governance_mount(clone: Path, ref: str) -> tuple[str, str] | None:
    """(path, branch) of the submodule whose url is this corpus, at `ref`.

    The url is compared by its last segment: `.../qmetronome` contains `/qm`
    and is not the corpus.
    """
    text = text_of(clone, ref, ".gitmodules")
    if text is None:
        return None
    parser = configparser.ConfigParser()
    try:
        parser.read_string(re.sub(r"^[ \t]+", "", text, flags=re.M))
    except configparser.Error:
        return None
    for section in parser.sections():
        url = parser.get(section, "url", fallback="").rstrip("/").removesuffix(".git")
        if re.split(r"[/:]", url)[-1] == "qm" and parser.has_option(section, "path"):
            return parser.get(section, "path"), parser.get(section, "branch", fallback="")
    return None


def seed_workflows(corpus: Path, ref: str) -> list[tuple[str, str]]:
    """(file name, required|copied) for every workflow the seed list names."""
    text = text_of(corpus, ref, SEED_WORKFLOWS) or ""
    rows = []
    for line in text.splitlines():
        parts = line.split()
        if len(parts) == 2 and not line.startswith("#"):
            rows.append((parts[0], parts[1]))
    return rows


def governance_section(text: str) -> str:
    """An AGENTS.md down to the project's own line, without the seed comment."""
    text = SEED_COMMENT.sub("", text.replace("\r\n", "\n"))
    return text.split(PROJECT_LINE, 1)[0].strip()


def project_side(corpus: Path, clone: Path, name: str, remote: str = "origin") -> list[Fact]:
    side = "project"
    main = f"{remote}/main"
    ref = default_ref(clone, remote)
    if ref is None:
        return [Fact(side, "default branch", UNKNOWN,
                     f"{clone} has no {remote} tracking ref to read",
                     f"git -C {clone} fetch {remote}")]
    facts: list[Fact] = []

    mount = governance_mount(clone, ref)
    tip = commit_of(corpus, f"{remote}/project/{name}")
    if mount is None:
        facts.append(Fact(side, "governance pin", BEHIND,
                          f"{ref} mounts no submodule whose url is this corpus",
                          "handbook/forking-a-project.md"))
    else:
        path, branch = mount
        entry = git(clone, "ls-tree", ref, path)
        pin = entry.split()[2] if entry and entry.split()[1:2] == ["commit"] else None
        if pin is None or tip is None:
            facts.append(Fact(side, "governance pin", UNKNOWN,
                              f"no gitlink at {path}" if pin is None
                              else f"project/{name} is not a ref in the corpus clone"))
        elif pin == tip:
            facts.append(Fact(side, "governance pin", CURRENT,
                              f"{path} pins {pin[:7]}, the tip of project/{name}"))
        else:
            behind = git(corpus, "rev-list", "--count", f"{pin}..{tip}")
            ancestor = run_git(corpus, "merge-base", "--is-ancestor", pin, tip).returncode == 0
            if behind is None:
                detail = f"{path} pins {pin[:7]}, which the corpus clone does not hold"
            elif ancestor:
                detail = (f"{path} pins {pin[:7]}, {int(behind)} commit(s) behind "
                          f"project/{name} at {tip[:7]}")
            else:
                detail = (f"{path} pins {pin[:7]}, which is not an ancestor of "
                          f"project/{name} at {tip[:7]}")
            facts.append(Fact(side, "governance pin", BEHIND, detail,
                              "handbook/propagation-runbook.md, Part B"))
        if branch != f"project/{name}":
            facts.append(Fact(side, ".gitmodules branch", BEHIND,
                              f"names {branch or 'no branch'}, not project/{name}",
                              f"branch = project/{name}"))

    for workflow, kind in seed_workflows(corpus, main):
        seed = blob_of(corpus, main, f"project-seed/ci/{workflow}")
        copy = blob_of(clone, ref, f".github/workflows/{workflow}")
        subject = f".github/workflows/{workflow} ({kind})"
        if copy is None:
            facts.append(Fact(side, subject, BEHIND, "absent",
                              f"copy project-seed/ci/{workflow}"))
        elif copy == seed:
            facts.append(Fact(side, subject, CURRENT, "the seed's file"))
        else:
            facts.append(Fact(side, subject, BEHIND, "differs from the seed's file",
                              f"copy project-seed/ci/{workflow}, keeping its env: knobs"))

    seed_page, page = text_of(corpus, main, SEED_AGENTS), text_of(clone, ref, "AGENTS.md")
    if page is None:
        facts.append(Fact(side, "AGENTS.md", BEHIND, "absent", f"copy {SEED_AGENTS}"))
    elif seed_page is None:
        facts.append(Fact(side, "AGENTS.md", UNKNOWN, f"{main} has no {SEED_AGENTS}"))
    elif governance_section(page) == governance_section(seed_page).replace(PLACEHOLDER, name):
        facts.append(Fact(side, "AGENTS.md governance section", CURRENT,
                          "the seed's, with the project's name"))
    else:
        facts.append(Fact(side, "AGENTS.md governance section", BEHIND,
                          "differs from the seed's above the project's own line",
                          f"copy {SEED_AGENTS} above that line, substituting {name}"))

    seed_import, pointer = blob_of(corpus, main, SEED_IMPORT), blob_of(clone, ref, "CLAUDE.md")
    if pointer is not None and pointer == seed_import:
        facts.append(Fact(side, "CLAUDE.md", CURRENT, "the seed's one-line import"))
    else:
        facts.append(Fact(side, "CLAUDE.md", BEHIND,
                          "absent" if pointer is None else "not the seed's one-line import",
                          f"copy {SEED_IMPORT}"))
    return facts


# ----------------------------------------------------------------------- host

def age_days(stamp: str, now: datetime) -> int:
    then = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
    return (now - then).days


def open_pull_requests(side: str, repo: str, cwd: Path, now: datetime,
                       base: str | None = None) -> list[Fact]:
    """Every open pull request is work that has not reached its base."""
    args = ["pr", "list", "--repo", repo, "--state", "open", "--limit", "100",
            "--json", "number,title,isDraft,baseRefName,updatedAt"]
    if base:
        args += ["--base", base]
    where = f"{repo}, base {base}" if base else repo
    done = run_gh(args, cwd)
    if done.returncode != 0:
        why = (done.stderr.strip().splitlines() or ["gh failed"])[-1]
        return [Fact(side, f"open pull requests in {where}", UNKNOWN, why,
                     "gh auth login")]
    try:
        rows = json.loads(done.stdout)
    except json.JSONDecodeError:
        return [Fact(side, f"open pull requests in {where}", UNKNOWN,
                     "the host's answer was not JSON")]
    if not rows:
        return [Fact(side, f"open pull requests in {where}", CURRENT, "none")]
    return [Fact(side, f"{repo}#{row['number']}", BEHIND,
                 f"{'draft' if row['isDraft'] else 'ready'} against "
                 f"{row['baseRefName']}, untouched for "
                 f"{age_days(row['updatedAt'], now)} day(s): {row['title']}",
                 "merge it, finish it or close it")
            for row in sorted(rows, key=lambda r: r["number"])]


# --------------------------------------------------------------------- output

def exit_status(facts: list[Fact]) -> int:
    return 0 if all(f.state == CURRENT for f in facts) else 1


def render(name: str, facts: list[Fact]) -> str:
    out = [f"{name}, read against the corpus it adopted.", ""]
    for side, heading in (("corpus", f"In the corpus, on project/{name}"),
                          ("project", "In the project's repository, on its default branch"),
                          ("host", "On the host")):
        rows = [f for f in facts if f.side == side]
        if not rows:
            continue
        out.append(heading)
        for fact in rows:
            out.append(f"  {fact.state:<8} {fact.subject}: {fact.detail}")
            if fact.state != CURRENT and fact.remedy:
                out.append(f"  {'':<8} -> {fact.remedy}")
        out.append("")
    behind = sum(f.state == BEHIND for f in facts)
    unknown = sum(f.state == UNKNOWN for f in facts)
    if behind or unknown:
        out.append(f"{behind} behind, {unknown} unknown. An unknown was not "
                   "established and is not a pass.")
    else:
        out.append("Every fact read is current.")
    out.append("Not read: whether the project's tests pass. "
               "protocols/project-refresh.md is the procedure.")
    return "\n".join(out) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="One adopted project, read against the corpus it adopted.")
    parser.add_argument("name", help="the project's name, as the roster and "
                                     "its project/<name> branch spell it")
    parser.add_argument("--roster", type=Path, default=ROSTER)
    parser.add_argument(
        "--search-root", action="append", type=Path, default=[],
        help="a directory the roster's paths are relative to. Repeatable. "
             "Default: two directories above the corpus clone.")
    parser.add_argument("--remote", default="origin")
    parser.add_argument("--offline", action="store_true",
                        help="ask nothing of the host: no ls-remote, no gh")
    parser.add_argument("--json", action="store_true",
                        help="emit the review as one JSON document")
    args = parser.parse_args(argv)

    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    try:
        roster = load(args.roster)
    except (OSError, ValueError) as exc:
        print(f"project: cannot read the roster at {args.roster}: {exc}", file=sys.stderr)
        return 2
    entry = next((e for e in roster if e.get("name") == args.name), None)
    if entry is None:
        print(f"project: {args.roster} names no repository called {args.name}.",
              file=sys.stderr)
        return 2
    roots = [p.resolve() for p in args.search_root] or [CORPUS.parent.parent]
    clone = resolve(entry, roots)
    if clone is None:
        looked = " or ".join(entry.get("paths", [])) or "(no paths in the roster)"
        print(f"project: no clone of {args.name} under "
              f"{', '.join(str(r) for r in roots)}; looked for {looked}.\n"
              f"  gh repo clone {ORG}/{args.name} <one of those paths>\n"
              "  A review with no clone has read nothing about the project.",
              file=sys.stderr)
        return 2

    facts: list[Fact] = []
    if not args.offline:
        for side, repo, ref in (("corpus", CORPUS, f"{args.remote}/main"),
                                ("corpus", CORPUS, f"{args.remote}/project/{args.name}"),
                                ("project", clone, default_ref(clone, args.remote))):
            if ref and (stale := tracking_is_fresh(side, repo, args.remote, ref)):
                facts.append(stale)
    facts += corpus_side(CORPUS, args.name, args.remote)
    facts += project_side(CORPUS, clone, args.name, args.remote)
    if not args.offline:
        now = datetime.now(timezone.utc)
        facts += open_pull_requests("host", f"{ORG}/{args.name}", clone, now)
        facts += open_pull_requests("host", f"{ORG}/qm", CORPUS, now,
                                    base=f"project/{args.name}")

    if args.json:
        json.dump({"project": args.name, "clone": str(clone),
                   "facts": [asdict(f) for f in facts]}, sys.stdout, indent=2)
        sys.stdout.write("\n")
    else:
        sys.stdout.write(render(args.name, facts))
    return exit_status(facts)


if __name__ == "__main__":
    raise SystemExit(main())
