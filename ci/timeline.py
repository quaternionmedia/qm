#!/usr/bin/env python3
"""A project's timeline, drawn from its git history and its curated round log.

    uv run qm timeline alfred --write             # read alfred's clone, write git.yaml and timeline.md
    uv run qm timeline alfred --write --offline   # timeline.md again, from the committed git.yaml
    uv run qm timeline alfred --check             # the committed files alone: is timeline.md current?
    uv run qm timeline --check                    # every project with a subtree
    uv run qm timeline alfred                     # print the page, write nothing

`records/DRAFT-a-projects-history-lives-in-the-corpus.md` is the decision. A
project's dated account lives in this corpus at `docs/projects/<name>/`, and
three of its files belong to this tool:

    rounds.yaml   written by a person: each development round's branch, pull
                  request, dates and what it carried, the counts measured on
                  it, and counts the project's release notes carried
    git.yaml      written by `--write` from the project's clone: the pull
                  requests merged on its default branch, its tags, and the
                  commit they were read at
    timeline.md   written by `--write` from the two above, and the subtree's
                  retrospectives, which it links

The clone is found the way the cookbook finds a member's: the roster's
candidate paths first, then the sibling probe. `--clone` names one outright.
The runner holds no clones, so `--check` reads the committed files and nothing
else, and refuses a `timeline.md` that differs from what they give, a
`rounds.yaml` of the wrong shape, and a retrospective with no date.

What this cannot do: tell that `git.yaml` is behind its project, which the
page shows by naming the commit it was read at; see a round nobody wrote into
`rounds.yaml`; or check a count against the run that produced it.
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
PROJECTS = ROOT / "docs" / "projects"
INVENTORY = ROOT / "status" / "inventory.yaml"
RECORD = "records/DRAFT-a-projects-history-lives-in-the-corpus.md"
CORPUS_URL = "https://github.com/quaternionmedia/qm/blob/main/"
ROUNDS = "rounds.yaml"
SNAPSHOT = "git.yaml"
PAGE = "timeline.md"
DEFAULT_ORG = "quaternionmedia"

# A merge commit GitHub wrote, and a commit whose subject ends in the pull
# request it merged: a squash, or a merge whose message was edited.
MERGED = re.compile(r"^Merge pull request #(?P<pr>\d+) from (?P<owner>[^/\s]+)/(?P<branch>\S+)")
NUMBERED = re.compile(r"^(?P<title>.*?)\s*\(#(?P<pr>\d+)\)\s*$")
# A retrospective's date, on a line of its own near the top.
DATED = re.compile(r"^\*\*Date:\*\*\s*(?P<date>\d{4}-\d{2}-\d{2})", re.MULTILINE)
TITLE = re.compile(r"^#\s+(?P<title>.+?)\s*$", re.MULTILINE)
DAY = re.compile(r"^\d{4}-\d{2}-\d{2}$")


class Malformed(ValueError):
    """A committed input this tool cannot draw a page from, and where."""


# --- the inputs --------------------------------------------------------------


def subtree(name: str, projects: Path = PROJECTS) -> Path:
    return projects / name


def with_subtree(projects: Path = PROJECTS) -> list[str]:
    """The projects whose subtree holds one of this tool's files."""
    if not projects.is_dir():
        return []
    return sorted((d.name for d in projects.iterdir() if d.is_dir()
                   and any((d / f).is_file() for f in (ROUNDS, SNAPSHOT, PAGE))),
                  key=str.lower)


def _day(value, where: str) -> str:
    """A date as `YYYY-MM-DD`. YAML reads an unquoted one as a date."""
    if isinstance(value, dt.date):
        return value.isoformat()
    if isinstance(value, str) and DAY.match(value.strip()):
        return value.strip()
    raise Malformed(f"{where}: {value!r} is not a date written YYYY-MM-DD")


def _text(value, where: str, optional: bool = False) -> str | None:
    if value is None and optional:
        return None
    if not isinstance(value, (str, int)) or not str(value).strip():
        raise Malformed(f"{where}: needs a value")
    return " ".join(str(value).split())


def load_rounds(path: Path) -> dict:
    """The round log, checked for the shape the page reads. Absent is empty."""
    if not path.is_file():
        return {"rounds": [], "measured": [], "noted": []}
    where = _shown(path)
    document = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(document, dict):
        raise Malformed(f"{where}: is not a mapping")
    rounds, numbers = [], set()
    for n, item in enumerate(document.get("rounds") or [], start=1):
        at = f"{where}: rounds[{n}]"
        if not isinstance(item, dict):
            raise Malformed(f"{at}: is not a mapping")
        number = item.get("round")
        if not isinstance(number, int) or number in numbers:
            raise Malformed(f"{at}: `round` must be a whole number no other round has")
        numbers.add(number)
        pr = item.get("pr")
        if not isinstance(pr, int):
            raise Malformed(f"{at}: `pr` must be the pull request's number")
        began, ended = _day(item.get("began"), f"{at}.began"), _day(item.get("ended"), f"{at}.ended")
        if began > ended:
            raise Malformed(f"{at}: began {began} is after ended {ended}")
        rounds.append({
            "round": number,
            "branch": _text(item.get("branch"), f"{at}.branch"),
            "pr": pr,
            "title": _text(item.get("title"), f"{at}.title", optional=True),
            "began": began,
            "ended": ended,
            "head": _text(item.get("head"), f"{at}.head", optional=True),
            "carried": _text(item.get("carried"), f"{at}.carried"),
        })
    measured = []
    for n, item in enumerate(document.get("measured") or [], start=1):
        at = f"{where}: measured[{n}]"
        if not isinstance(item, dict):
            raise Malformed(f"{at}: is not a mapping")
        covers = item.get("rounds")
        if not isinstance(covers, list) or not covers or any(r not in numbers for r in covers):
            raise Malformed(f"{at}: `rounds` must list rounds the log holds")
        results = []
        for m, result in enumerate(item.get("results") or [], start=1):
            if not isinstance(result, dict):
                raise Malformed(f"{at}.results[{m}]: is not a mapping")
            results.append({"suite": _text(result.get("suite"), f"{at}.results[{m}].suite"),
                            "result": _text(result.get("result"), f"{at}.results[{m}].result")})
        if not results:
            raise Malformed(f"{at}: `results` is empty")
        # `at`, never `on`: YAML reads a bare `on` key as true.
        measured.append({"rounds": sorted(covers), "at": _text(item.get("at"), f"{at}.at"),
                         "results": results,
                         "also": _text(item.get("also"), f"{at}.also", optional=True)})
    noted = []
    for n, item in enumerate(document.get("noted") or [], start=1):
        at = f"{where}: noted[{n}]"
        if not isinstance(item, dict):
            raise Malformed(f"{at}: is not a mapping")
        noted.append({"version": _text(item.get("version"), f"{at}.version"),
                      "section": _text(item.get("section"), f"{at}.section"),
                      "text": _text(item.get("text"), f"{at}.text")})
    return {"repository": document.get("repository"),
            "default_branch": document.get("default_branch"),
            "source": _text(document.get("source"), f"{where}: source", optional=True),
            "about": _text(document.get("about"), f"{where}: about", optional=True),
            "rounds": rounds, "measured": measured, "noted": noted}


def load_snapshot(path: Path) -> dict | None:
    if not path.is_file():
        return None
    document = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(document, dict) or "read_at" not in document:
        raise Malformed(f"{_shown(path)}: is not a git snapshot this tool wrote")
    return document


def retrospectives(folder: Path) -> list[dict]:
    """Every page in the subtree but the timeline, newest first: its title,
    its file and its date, or None for a page that carries no date."""
    found = []
    for page in sorted(folder.glob("*.md")) if folder.is_dir() else []:
        if page.name == PAGE:
            continue
        text = page.read_text(encoding="utf-8")
        title = TITLE.search(text)
        date = DATED.search(text)
        found.append({"file": page.name,
                      "title": title.group("title") if title else page.stem,
                      "date": date.group("date") if date else None})
    return sorted(found, key=lambda r: (r["date"] or "", r["file"]), reverse=True)


def repository_of(name: str, rounds: dict, inventory: Path = INVENTORY) -> str:
    """`owner/name` on the host: the round log's, else the inventory's org."""
    if rounds.get("repository"):
        return str(rounds["repository"])
    org = DEFAULT_ORG
    if inventory.is_file():
        import json
        org = ((json.loads(inventory.read_text(encoding="utf-8")).get("generator") or {})
               .get("org") or DEFAULT_ORG)
    return f"{org}/{name}"


# --- the clone ---------------------------------------------------------------


def git(clone: Path, *args: str) -> str:
    done = subprocess.run(["git", "-C", str(clone), *args], capture_output=True,
                          encoding="utf-8", errors="replace", timeout=60)
    if done.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)}: {done.stderr.strip()}")
    return done.stdout


def clone_of(name: str) -> Path | None:
    """Where the cookbook finds the member: the roster's paths, then the probe."""
    sys.path.insert(0, str(ROOT / "ci"))
    import cookbook
    return cookbook.clone_of(name)


def default_ref(clone: Path, branch: str | None = None) -> tuple[str, str]:
    """The default branch, and the ref to read it from: the remote-tracking
    copy where the clone has one, so a local branch ahead of the host is not
    read as merged."""
    if not branch:
        try:
            head = git(clone, "symbolic-ref", "--short", "refs/remotes/origin/HEAD").strip()
            branch = head.split("/", 1)[1] if "/" in head else head
        except RuntimeError:
            branch = "main"
    for ref in (f"origin/{branch}", branch):
        try:
            git(clone, "rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}")
            return branch, ref
        except RuntimeError:
            continue
    raise RuntimeError(f"{clone.name} has no branch {branch!r}, local or remote")


def read_git(clone: Path, name: str, branch: str | None = None) -> dict:
    """The git facts a timeline is drawn from, read from one clone."""
    branch, ref = default_ref(clone, branch)
    tip = git(clone, "rev-parse", ref).strip()
    tip_day = git(clone, "log", "-1", "--format=%cs", ref).strip()
    merged = []
    log = git(clone, "log", "--first-parent", "--format=%H%x1f%P%x1f%cs%x1f%s%x1f%b%x1e", ref)
    for entry in log.split("\x1e"):
        fields = entry.strip("\n").split("\x1f")
        if len(fields) < 5:
            continue
        commit, parents, day, subject, body = fields
        is_merge = len(parents.split()) > 1
        github = MERGED.match(subject) if is_merge else None
        if github:
            lines = [line.strip() for line in body.splitlines() if line.strip()]
            merged.append({"pr": int(github.group("pr")), "date": day,
                           "branch": github.group("branch"),
                           "title": lines[0] if lines else subject, "commit": commit})
            continue
        numbered = NUMBERED.match(subject)
        if numbered:
            merged.append({"pr": int(numbered.group("pr")), "date": day, "branch": None,
                           "title": numbered.group("title"), "commit": commit})
    tags = []
    listing = git(clone, "for-each-ref", "refs/tags", "--format="
                  "%(refname:short)%1f%(objecttype)%1f%(creatordate:short)%1f%(*objectname)%1f%(objectname)")
    for line in listing.splitlines():
        fields = line.split("\x1f")
        if len(fields) != 5:
            continue
        tag, kind, day, peeled, own = fields
        tags.append({"name": tag, "date": day, "commit": peeled or own,
                     "annotated": kind == "tag"})
    merged.sort(key=lambda m: (m["date"], m["pr"]), reverse=True)
    tags.sort(key=lambda t: (t["date"], t["name"]), reverse=True)
    return {"project": name, "default_branch": branch,
            "read_at": {"ref": ref, "commit": tip, "date": tip_day},
            "merged": merged, "tags": tags}


def snapshot_text(document: dict) -> str:
    name = document["project"]
    head = (f"# {name}'s git facts, as `uv run qm timeline {name} --write` read them from\n"
            f"# its clone. Generated: timeline.md is drawn from this file and rounds.yaml,\n"
            f"# and a refresh rewrites both. Do not edit by hand.\n")
    return head + yaml.safe_dump(document, sort_keys=False, allow_unicode=True, width=100)


# --- the page ----------------------------------------------------------------


def _cell(text: str) -> str:
    return text.replace("|", "\\|")


def _rounds_named(numbers: list[int]) -> str:
    if len(numbers) == 1:
        return f"Round {numbers[0]}"
    return "Rounds " + ", ".join(str(n) for n in numbers[:-1]) + f" and {numbers[-1]}"


def entries(rounds: dict, snapshot: dict | None, repository: str) -> list[dict]:
    """Every dated thing the page lists, newest first."""
    url = f"https://github.com/{repository}"
    short = repository.split("/")[-1]
    found = []
    for r in rounds["rounds"]:
        when = r["ended"] if r["began"] == r["ended"] else f"{r['began']} to {r['ended']}"
        found.append({"key": (r["ended"], 2, r["round"]), "date": when,
                      "what": f"**Round {r['round']}**, on `{r['branch']}`: {r['carried']}",
                      "link": f"[{short}#{r['pr']}]({url}/pull/{r['pr']})"})
    for m in (snapshot or {}).get("merged") or []:
        branch = f" `{m['branch']}`" if m.get("branch") else ""
        found.append({"key": (m["date"], 1, m["pr"]), "date": m["date"],
                      "what": f"Merged{branch}: {m['title']}",
                      "link": f"[{short}#{m['pr']}]({url}/pull/{m['pr']})"})
    for t in (snapshot or {}).get("tags") or []:
        kind = "" if t.get("annotated") else ", a lightweight tag"
        found.append({"key": (t["date"], 0, 0), "date": t["date"],
                      "what": f"Tagged `{t['name']}` at `{t['commit'][:7]}`{kind}",
                      "link": f"[{t['name']}]({url}/releases/tag/{t['name']})"})
    return sorted(found, key=lambda e: e["key"], reverse=True)


def render(name: str, rounds: dict, snapshot: dict | None, retros: list[dict],
           repository: str, has_page: bool = True) -> str:
    here = f"[{name}](../{name}.md)" if has_page else name
    source = f"{CORPUS_URL}docs/projects/{name}/"
    lines = ["---", f"title: {name}'s timeline", "---", "",
             f"# {name}'s timeline", "",
             f"What happened in {here}, newest first: its development rounds, the pull "
             f"requests merged on its default branch and its tags, each with its date and "
             f"a link to it on GitHub. This page is dated history, and each entry is true "
             f"of the day it names; {name}'s own pages say what is true of it now.", ""]
    if snapshot:
        read = snapshot["read_at"]
        facts = (f"the git facts in [`{SNAPSHOT}`]({source}{SNAPSHOT}), read from {name}'s "
                 f"`{snapshot['default_branch']}` at `{read['commit'][:7]}`, a commit of "
                 f"{read['date']}")
    else:
        facts = (f"no git facts: none have been read for {name}, and `uv run qm timeline "
                 f"{name} --write` reads them from its clone")
    log = (f"the round log [`{ROUNDS}`]({source}{ROUNDS}), which a person keeps"
           if rounds["rounds"] else "no round log")
    lines += [f"Generated by `uv run qm timeline {name} --write` from {log}, and {facts}. "
              f"`--check` refuses this page when it differs from them, so a change is made "
              f"to the round log and the page regenerated. The decision is "
              f"[the record on a project's dated history]({CORPUS_URL}{RECORD}).", ""]
    if rounds.get("source"):
        lines += [f"The round log is taken from {rounds['source'].rstrip('.')}.", ""]

    lines += ["## Retrospectives", ""]
    if retros:
        for r in retros:
            lines.append(f"- {r['date'] or 'undated'} · [{r['title']}]({r['file']})")
        lines.append("")
    else:
        lines += [f"No retrospective of {name} is kept here yet.", ""]

    lines += ["## Timeline", ""]
    if rounds.get("about"):
        lines += [f"The rounds: {rounds['about']}", ""]
    listed = entries(rounds, snapshot, repository)
    if listed:
        lines += ["| Date | What happened | On GitHub |", "|---|---|---|"]
        lines += [f"| {e['date']} | {_cell(e['what'])} | {e['link']} |" for e in listed]
        lines.append("")
    else:
        lines += ["Nothing is dated yet.", ""]

    if rounds["measured"]:
        lines += ["## Measured", "",
                  "Each count is what one run reported, at the commit or branch named, "
                  f"and none is a count of {name} now.", ""]
        for m in sorted(rounds["measured"], key=lambda m: m["rounds"], reverse=True):
            lines += [f"### {_rounds_named(m['rounds'])}, at `{m['at']}`", ""]
            lines += [f"- `{r['suite']}`: {r['result']}" for r in m["results"]]
            lines.append("")
            if m["also"]:
                lines += [f"Also: {m['also']}", ""]

    if rounds["noted"]:
        lines += ["## Counts in the release notes", "",
                  f"Measured counts {name}'s changelog carried, by the version and section "
                  "that carried them.", "",
                  "| Version | Section | Count |", "|---|---|---|"]
        lines += [f"| {_cell(n['version'])} | {_cell(n['section'])} | {_cell(n['text'])} |"
                  for n in rounds["noted"]]
        lines.append("")
    return "\n".join(lines)


def page_for(name: str, projects: Path = PROJECTS, snapshot: dict | None = None,
             inventory: Path = INVENTORY) -> str:
    """The page the committed inputs give, or `snapshot` in place of git.yaml."""
    folder = subtree(name, projects)
    rounds = load_rounds(folder / ROUNDS)
    if snapshot is None:
        snapshot = load_snapshot(folder / SNAPSHOT)
    return render(name, rounds, snapshot, retrospectives(folder),
                  repository_of(name, rounds, inventory), (projects / f"{name}.md").is_file())


def _shown(path: Path) -> str:
    """A path as the corpus names it, not as this disk does."""
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def problems(name: str, projects: Path = PROJECTS, inventory: Path = INVENTORY) -> list[str]:
    """What `--check` refuses for one project."""
    folder = subtree(name, projects)
    try:
        expected = page_for(name, projects, inventory=inventory)
    except Malformed as exc:
        return [str(exc)]
    found = [f"{_shown(folder / r['file'])}: no `**Date:** YYYY-MM-DD` line; a "
             f"retrospective here is dated" for r in retrospectives(folder) if not r["date"]]
    page = folder / PAGE
    if not page.is_file():
        found.append(f"{_shown(page)}: missing")
    elif page.read_text(encoding="utf-8") != expected:
        found.append(f"{_shown(page)}: differs from what {ROUNDS} and {SNAPSHOT} give")
    return found


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("project", nargs="?", help="the project; every one with a subtree when omitted")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--write", action="store_true",
                      help="read the clone into git.yaml, then write timeline.md")
    mode.add_argument("--check", action="store_true",
                      help="refuse a timeline.md its committed inputs do not give")
    parser.add_argument("--offline", action="store_true",
                        help="with --write: keep the committed git.yaml and redraw the page from it")
    parser.add_argument("--clone", metavar="PATH", help="with --write: the project's clone")
    args = parser.parse_args(argv)

    names = [args.project] if args.project else with_subtree()
    if args.clone and len(names) != 1:
        print("timeline: --clone names one project's clone; name the project too.", file=sys.stderr)
        return 2
    if not names:
        print("timeline: no project has a subtree under docs/projects/ yet.")
        return 0

    if args.check:
        found = [p for name in names for p in problems(name)]
        for problem in found:
            print(f"  {problem}", file=sys.stderr)
        if found:
            again = " ".join(["uv run qm timeline", *([args.project] if args.project else []), "--write"])
            print(f"\ntimeline: {len(found)} problem(s). Fix the round log or the page's date "
                  f"line, then `{again}`.", file=sys.stderr)
            return 1
        print(f"timeline: {len(names)} timeline(s) match their committed inputs. Whether "
              "git.yaml is behind its project is read off each page's commit.")
        return 0

    failed = 0
    for name in names:
        folder = subtree(name)
        snapshot = None
        if args.write and not args.offline:
            clone = Path(args.clone) if args.clone else clone_of(name)
            if clone is None or not (clone / ".git").exists():
                print(f"timeline: {name}'s clone is not on this disk. Name it with --clone, "
                      f"or redraw from the committed {SNAPSHOT} with --offline.", file=sys.stderr)
                failed += 1
                continue
            try:
                rounds = load_rounds(folder / ROUNDS)
                snapshot = read_git(clone, name, rounds.get("default_branch"))
            except (RuntimeError, Malformed) as exc:
                print(f"timeline: {name}: {exc}", file=sys.stderr)
                failed += 1
                continue
        try:
            text = page_for(name, snapshot=snapshot)
        except Malformed as exc:
            print(f"timeline: {exc}", file=sys.stderr)
            failed += 1
            continue
        if not args.write:
            print(text)
            continue
        folder.mkdir(parents=True, exist_ok=True)
        if snapshot is not None:
            # newline="\n": a Windows text write is CRLF, and the committed file LF.
            (folder / SNAPSHOT).write_text(snapshot_text(snapshot), encoding="utf-8", newline="\n")
            read = snapshot["read_at"]
            print(f"wrote {(folder / SNAPSHOT).relative_to(ROOT).as_posix()} from {read['ref']} "
                  f"at {read['commit'][:7]} ({read['date']})")
        (folder / PAGE).write_text(text, encoding="utf-8", newline="\n")
        print(f"wrote {(folder / PAGE).relative_to(ROOT).as_posix()}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
