#!/usr/bin/env python3
"""What still refers to a branch, asked before the branch is retired.

    uv run qm references <branch>
    uv run qm references <branch> --base origin/project/<name>
    uv run qm references <branch> --offline     # main and the base; no host

`git cherry` says whether a branch's content has landed somewhere else. This
says whether anything still points at the branch itself, which is the other
half of deciding to retire it. It reads four kinds of reference:

  * name      the branch's name as text: as written when it holds a slash,
              in backticks when it does not, since a bare word matches prose;
  * commit    a commit no other branch holds, by its first seven characters;
  * file      a file the branch adds that its base lacks, by its path, or by
              its basename where no file in the base shares it;
  * named     the branch's name in backticks in `docs/ref/namespaces.md`,
              which names the stage refs and every other documented ref.

It searches `main`, the base when that is another branch, and the head of
every open pull request into the corpus except the branch's own. A line a head
carries unchanged from `main` is reported once, as `main`'s. Generated
documents are skipped: each names what was true at its last run, and the next
run drops a retired branch.

Exit 0: nothing refers to the branch. Exit 1: something does; each reference is
listed with its ref, file and line. Exit 2: the branch, the base, the namespace
page or the host could not be read, or an open pull request's head is not
fetched, so part of the search could not run.

What it cannot see: a reference in another repository, a submodule pinned to a
commit only this branch holds among them (`uv run qm estate` surveys the clones
on this disk); text outside the searched refs' files, such as a pull request
body, a comment or an issue; and a citation in a form it does not match, such
as a shortened branch name or a commit abbreviated below seven characters.

It runs five git commands however many refs it searches: one listing of every
ref, one rev-list, one diff, one tree listing and one grep across every
searched ref, which also reads the namespace page. A `--main` or `--base` that
is not a branch costs a rev-parse, and a base other than main a look at main's
namespace page. The reading of their output is pure, so each rule is tested
without git.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

sys.path.insert(0, str(Path(__file__).resolve().parent))

# The host is reached through `merge_review`'s one boundary, `gh`, so a test
# that fakes it there fakes every read this makes.
import generate_docs  # noqa: E402
import merge_review as host  # noqa: E402
from merge_review import DEFAULT_ORG, HostUnavailable  # noqa: E402

NAMESPACES = "docs/ref/namespaces.md"
GENERATED = tuple(step[2] for step in generate_docs.STEPS)
LINE_WIDTH = 160


class Unreadable(RuntimeError):
    """Part of the search could not run, so its silence is no answer."""


@dataclass(frozen=True)
class Reference:
    kind: str
    cited: str
    where: str

    def __str__(self) -> str:
        return f"  {self.kind:<7} {self.cited:<14} {self.where}"[:LINE_WIDTH]


# --------------------------------------------------------------------------
# The rules, pure: each reads text or names and returns what it found.
# --------------------------------------------------------------------------


def short_name(branch: str, remote: str) -> str:
    for prefix in ("refs/remotes/", "refs/heads/"):
        branch = branch.removeprefix(prefix)
    return branch.removeprefix(f"{remote}/") if remote else branch


def spoken(name: str) -> str:
    """How prose cites the branch: as written with a slash, else in backticks."""
    return name if "/" in name else f"`{name}`"


def others(refs: dict[str, str], name: str, remote: str) -> list[str]:
    """Every branch but this one, local or remote, by its full refname."""
    own = {f"refs/heads/{name}", f"refs/remotes/{remote}/{name}"}
    return [ref for ref in refs if ref not in own and not ref.endswith("/HEAD")]


def file_patterns(added: list[str], listing: set[str]) -> dict[str, str]:
    """Pattern -> file, for each file the branch adds that the base lacks.

    The path always; the basename too, where no file in the base shares it.
    """
    taken = {PurePosixPath(path).name for path in listing}
    patterns: dict[str, str] = {}
    for path in added:
        if path in listing:
            continue
        patterns[path] = path
        name = PurePosixPath(path).name
        if name not in taken:
            patterns.setdefault(name, path)
    return patterns


def searched_refs(name: str, remote: str, main: str, base: str,
                  heads: list[str], present: set[str]) -> list[str]:
    """main, the base when it differs, and every fetched open head but this one."""
    refs = [main] + ([base] if base != main else [])
    unfetched = []
    for head in heads:
        if head == name:
            continue
        ref = f"{remote}/{head}"
        if f"refs/remotes/{ref}" not in present:
            unfetched.append(head)
        elif ref not in refs:
            refs.append(ref)
    if unfetched:
        raise Unreadable(
            f"{len(unfetched)} open pull request head(s) not fetched, so not "
            f"searched: {', '.join(unfetched[:5])}; run `git fetch {remote}`")
    return refs


def split_line(line: str, refs: list[str]) -> tuple[str, str, str] | None:
    """A `ref:path:number:text` grep line, as (ref, path, text).

    A ref holds no colon, so the colon after it says which ref a line is from.
    """
    for ref in refs:
        if line.startswith(ref + ":"):
            parts = line[len(ref) + 1:].split(":", 2)
            return (ref, parts[0], parts[2]) if len(parts) == 3 else None
    return None


def distinct(found: list[Reference], refs: list[str]) -> list[Reference]:
    """One reference per kind, citation, path and line text, in `refs`' order.

    Every open pull request carries main's files, so a line a head inherits
    unchanged is main's reference and not the head's.
    """
    order = {ref: index for index, ref in enumerate(refs)}
    keyed = [(split_line(r.where, refs), r) for r in found]
    keyed.sort(key=lambda pair: order[pair[0][0]] if pair[0] else len(order))
    seen: set[tuple] = set()
    kept = []
    for parsed, reference in keyed:
        key = (reference.kind, reference.cited, *(parsed[1:] if parsed else (reference.where,)))
        if key not in seen:
            seen.add(key)
            kept.append(reference)
    return kept


def classify(lines: list[str], refs: list[str], said: str, commits: list[str],
             patterns: dict[str, str]) -> list[Reference]:
    """Every reference in grep output: the name, a commit, a file."""
    found: list[Reference] = []
    words = [re.compile(rf"(?<!\w){re.escape(sha)}(?!\w)") for sha in commits]
    for line in lines:
        parsed = split_line(line, refs)
        if parsed is None:
            continue
        text = parsed[2]
        if said in text:
            found.append(Reference("name", said, line))
        for sha, word in zip(commits, words):
            if word.search(text):
                found.append(Reference("commit", sha, line))
        for pattern, path in patterns.items():
            if pattern in text:
                found.append(Reference("file", path, line))
                break
    return found


def named(lines: list[str], name: str, main: str) -> list[Reference]:
    """Each line of main's namespace page naming the branch in backticks."""
    page = f"{main}:{NAMESPACES}:"
    return [Reference("named", f"`{name}`", line) for line in lines
            if line.startswith(page) and f"`{name}`" in line[len(page):]]


def known(refs: dict[str, str], ref: str) -> bool:
    """Whether `ref` names a branch in the listing, so no rev-parse is needed."""
    return any(candidate in refs for candidate in
               (ref, f"refs/remotes/{ref}", f"refs/heads/{ref}"))


# --------------------------------------------------------------------------
# The reads: git and the host, each once.
# --------------------------------------------------------------------------


class Git:
    def __init__(self, repo: Path) -> None:
        self.repo = repo

    def run(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["git", "-C", str(self.repo), *args],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )

    def out(self, *args: str) -> str:
        done = self.run(*args)
        if done.returncode != 0:
            raise Unreadable(f"git {' '.join(args)}: {done.stderr.strip()}")
        return done.stdout

    def refs(self) -> dict[str, str]:
        listing = self.out("for-each-ref", "--format=%(refname) %(objectname)",
                           "refs/heads", "refs/remotes")
        return dict(line.split(" ", 1) for line in listing.splitlines() if line)

    def grep(self, refs: list[str], patterns: list[str]) -> list[str]:
        """Matching lines in every ref's files, as `ref:path:number:text`."""
        args = ["grep", "-n", "-I", "-F"]
        for pattern in patterns:
            args += ["-e", pattern]
        excluded = [f":(exclude){path}" for path in GENERATED]
        done = self.run(*args, *refs, "--", ".", *excluded)
        # git grep exits 1 for no match, and above 1 for a failure.
        if done.returncode > 1:
            raise Unreadable(f"git grep: {done.stderr.strip()}")
        return done.stdout.splitlines()


def open_heads(repository: str) -> list[str]:
    reply = host.gh_json("pr", "list", "--repo", repository, "--state", "open",
                         "--limit", "500", "--json", "headRefName")
    if not isinstance(reply, list):
        raise Unreadable(f"the host did not list {repository}'s open pull requests")
    return sorted({pr["headRefName"] for pr in reply if pr.get("headRefName")})


def report(git: Git, branch: str, remote: str, main: str, base: str,
           repository: str | None, out) -> int:
    name = short_name(branch, remote)
    refs = git.refs()
    ref = next((r for r in (f"refs/remotes/{remote}/{name}", f"refs/heads/{name}")
                if r in refs), None)
    if ref is None:
        raise Unreadable(f"no branch {name!r}, locally or on {remote}")
    tip = refs[ref]
    unknown = [r for r in dict.fromkeys((main, base)) if not known(refs, r)]
    if unknown:
        git.out("rev-parse", "-q", *(f"{r}^{{commit}}" for r in unknown))
    heads = open_heads(repository) if repository else []
    searched = searched_refs(name, remote, main, base, heads, set(refs))

    rest = others(refs, name, remote)
    commits = [sha[:7] for sha in git.out("rev-list", tip, "--not", *rest).split()]
    listing = set(git.out("ls-tree", "-r", "-z", "--name-only", base).split("\0"))
    listing.discard("")
    if base != main and git.run("cat-file", "-e", f"{main}:{NAMESPACES}").returncode:
        raise Unreadable(f"{NAMESPACES} is not on {main}")
    if base == main and NAMESPACES not in listing:
        raise Unreadable(f"{NAMESPACES} is not on {main}")
    added = git.out("diff", "--name-only", "-z", "--diff-filter=A",
                    f"{base}...{tip}").split("\0")
    patterns = file_patterns([p for p in added if p], listing)
    said = spoken(name)
    # The name as said matches every line naming it in backticks too, so the
    # one grep serves the namespace page.
    lines = git.grep(searched, list(dict.fromkeys([said, *commits, *patterns])))
    found = distinct(classify(lines, searched, said, commits, patterns)
                     + named(lines, name, main), searched)

    out.write(f"references to {name} ({short_name(ref, '')} @ {tip[:7]})\n")
    heads_searched = len(searched) - (2 if base != main else 1)
    scope = main + (f", {base}" if base != main else "")
    scope += (f" and {heads_searched} open pull request head(s)" if repository
              else "; open pull requests not searched (--offline)")
    out.write(f"searched {scope}; generated documents skipped\n")
    if found:
        out.write(f"\n{len(found)} reference(s); retiring the branch leaves each "
                  "pointing at nothing:\n")
        for reference in found:
            out.write(f"{reference}\n")
    else:
        out.write("\nNothing searched refers to it.\n")
    out.write("\nCannot see: another repository, a submodule pin among them; "
              "pull request bodies, comments and issues.\n")
    return 1 if found else 0


def run(argv: list[str] | None, out, err) -> int:
    """The command, writing to the streams it is given, so runs can share a process."""
    parser = argparse.ArgumentParser(
        description="What still refers to a branch: its name, the commits and "
                    "files only it holds, and the namespace page.")
    parser.add_argument("branch", help="the branch, as `name` or `<remote>/name`")
    parser.add_argument("--remote", default="origin")
    parser.add_argument("--main", default=None,
                        help="the corpus's main branch (default <remote>/main)")
    parser.add_argument("--base", default=None,
                        help="what the branch was cut from, for the files only it "
                             "holds (default the main branch)")
    parser.add_argument("--repository", default=f"{DEFAULT_ORG}/qm",
                        help="whose open pull requests are searched")
    parser.add_argument("--offline", action="store_true",
                        help="ask the host nothing; search main and the base only")
    parser.add_argument("--repo", type=Path, default=Path.cwd(),
                        help="the clone to read (default the current directory)")
    args = parser.parse_args(argv)
    main_ref = args.main or f"{args.remote}/main"
    try:
        return report(Git(args.repo), args.branch, args.remote, main_ref,
                      args.base or main_ref, None if args.offline else args.repository,
                      out)
    except (HostUnavailable, Unreadable) as exc:
        err.write(f"references: {exc}\n")
        return 2


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    return run(argv, sys.stdout, sys.stderr)


if __name__ == "__main__":
    raise SystemExit(main())
