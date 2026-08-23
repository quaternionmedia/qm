#!/usr/bin/env python3
"""Every submodule pin is a commit somebody else could actually get.

    python project-seed/ci/check_submodule_pins.py
    python project-seed/ci/check_submodule_pins.py --json

**THE DEFECT THIS EXISTS FOR, WITH A DATE.** On 2026-08-22 `codecartographer`
was found pinning its governance submodule at `fd9d756` -- a commit on no
remote and in no clone but one machine. A fresh checkout could never have
resolved that project's own submodule, and the only copy of a project record
lived in the same unreachable place. It survived by luck: a working tree was
deleted and the git objects happened to outlive it.

Nothing caught it. The workflow that would have was in a repository with GitHub
Actions switched off, and there was no way to ask the question locally at all --
which is the half that matters, because the pin is made locally, minutes before
anybody would want to know.

**UNPUSHED AND UNREADABLE ARE DIFFERENT FACTS.** The check this replaces
reported both as one failure, in an error whose own text admitted it "cannot
tell that apart from a private submodule remote that an unauthenticated runner
cannot read". A check that fails on a question it has not answered teaches
people to ignore it, and a project with one private submodule was permanently
red for a reason nothing was wrong with.

They are tellable apart. `git ls-remote <url>` with **no ref** answers "can this
remote be read at all", which is a different question from "does this commit
exist" and is decidable anywhere:

    remote readable, commit fetchable      ok
    remote readable, commit NOT fetchable  UNPUSHED -- the defect, hard failure
    remote not readable at all             UNKNOWN -- private, or gone; not a
                                           failure, and never silently green

Note which way that cuts. It is a *strengthening*: where the remote is readable
a missing commit is now unambiguous rather than a maybe. Run locally, where
credentials exist, every remote is readable -- so the unpushed pin is caught at
full force in the one place somebody can still fix it in a second.

**WHAT THIS CANNOT DO.** Tell a private remote from a deleted one; both are
unreadable and it says so rather than guessing. Tell you the pin is the commit
you *meant*. And it reads `git submodule status`, so a submodule that is not
initialised is reported as such rather than skipped -- an uninitialised
submodule is how a pin goes unexamined for months.

**DO NOT "FIX" THIS WITH `git ls-remote <url> <sha>`.** `ls-remote` matches ref
*names*. For a commit that is perfectly fine it prints nothing and exits 0,
which reads as confirmation that the commit is missing. That misreading has
already been made here once.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

OK = "ok"
UNPUSHED = "unpushed"
UNREADABLE = "unreadable"
LOCAL_URL = "local-url"
NO_URL = "no-url"

# A verdict that means the tree is wrong, as opposed to one that means this
# machine cannot see far enough to say.
FAILING = (UNPUSHED, LOCAL_URL)

# `git submodule status` emits " <sha> <path> (<describe>)", optionally prefixed
# with `-` (uninitialised), `+` (checked-out sha differs from the index) or `U`
# (merge conflict). Without stripping `U` the sha reads as "U<sha>" and the
# error names a commit that does not exist.
STATUS = re.compile(r"^[-+U ]?(?P<sha>[0-9a-f]{7,40})\s+(?P<path>\S+)")


def run(args: list[str], cwd: str | None = None) -> tuple[int, str]:
    done = subprocess.run(args, cwd=cwd, capture_output=True, text=True,
                          encoding="utf-8", errors="replace")
    return done.returncode, (done.stdout or "") + (done.stderr or "")


def submodules(root: Path) -> list[tuple[str, str]]:
    """(sha, path) for every submodule the index records."""
    code, out = run(["git", "submodule", "status"], cwd=str(root))
    if code != 0:
        return []
    found = []
    for line in out.splitlines():
        match = STATUS.match(line.strip("\n"))
        if match:
            found.append((match.group("sha"), match.group("path")))
    return found


def url_for(root: Path, path: str) -> str:
    code, out = run(["git", "config", "-f", ".gitmodules", "--get",
                     f"submodule.{path}.url"], cwd=str(root))
    return out.strip() if code == 0 else ""


def as_https(url: str) -> str:
    """The https form of an ssh URL, or the url unchanged.

    A runner has no SSH key, so `git@host:owner/repo` cannot be fetched there
    even when the commit is present -- and reading that as "not pushed" is a
    false alarm for every project whose `.gitmodules` names the canonical SSH
    remote, which is what the fork procedure produces.
    """
    swapped = re.sub(r"^ssh://[^@]+@([^/]+)/", r"https://\1/", url)
    swapped = re.sub(r"^[^@/]+@([^:/]+):", r"https://\1/", swapped)
    return swapped


def is_remote_url(url: str) -> bool:
    """A URL another machine could use.

    A filesystem path resolves where it was set up and nowhere else. It is one
    of the ways an unreachable pin is created, and in CI it fails as a missing
    directory rather than as anything naming the cause.
    """
    return bool(re.match(r"^[a-z][a-z0-9+.-]*://", url)
                or re.match(r"^[^@/\\]+@[^:/]+:", url))


def reachable(url: str, sha: str) -> str | None:
    """The URL the commit was fetched over, or None."""
    candidates = [url]
    https = as_https(url)
    if https != url:
        candidates.append(https)
    with tempfile.TemporaryDirectory() as scratch:
        run(["git", "init", "--quiet", "--bare", scratch])
        for candidate in candidates:
            code, _ = run(["git", "-C", scratch, "fetch", "--quiet",
                           "--depth=1", candidate, sha])
            if code == 0:
                return candidate
    return None


def readable(url: str) -> bool:
    """Whether the remote can be read at all. NOT whether a commit is on it."""
    for candidate in {url, as_https(url)}:
        code, _ = run(["git", "ls-remote", "--quiet", candidate])
        if code == 0:
            return True
    return False


def inspect(root: Path, sha: str, path: str) -> dict:
    url = url_for(root, path)
    if not url:
        return {"path": path, "sha": sha, "url": "", "verdict": NO_URL,
                "detail": "no .gitmodules URL records where this came from"}
    if not is_remote_url(url):
        return {"path": path, "sha": sha, "url": url, "verdict": LOCAL_URL,
                "detail": ("a filesystem URL resolves on the machine that set it "
                           "up and nowhere else. Set the canonical remote, then "
                           f"run: git submodule sync {path}")}

    over = reachable(url, sha)
    if over:
        detail = "reachable"
        if over != url:
            detail = f"reachable over {over} (the configured URL is not fetchable here)"
        return {"path": path, "sha": sha, "url": url, "verdict": OK,
                "detail": detail}

    if readable(url):
        return {"path": path, "sha": sha, "url": url, "verdict": UNPUSHED,
                "detail": ("the remote IS readable from here and does not have "
                           "this commit, so it exists only where it was made. "
                           f"Run: (cd {path} && git push origin HEAD), then "
                           "re-push this repository")}

    return {"path": path, "sha": sha, "url": url, "verdict": UNREADABLE,
            "detail": ("the remote could not be read at all. A private "
                       "submodule is unreadable without credentials, and so is "
                       "one that has been deleted; this cannot separate those "
                       "and does not guess")}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", default=".")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    found = submodules(root)
    results = [inspect(root, sha, path) for sha, path in found]

    if args.as_json:
        print(json.dumps({"submodules": results}, indent=2))
    else:
        if not found:
            print("No submodules recorded here. Nothing to check.")
        for row in results:
            print(f"{row['verdict']:>10}  {row['path']} @ {row['sha'][:12]}")
            print(f"            {row['detail']}")
        unknown = [r for r in results if r["verdict"] == UNREADABLE]
        if unknown:
            print(f"\n{len(unknown)} pin(s) could not be checked from here. "
                  f"That is unknown, not a pass -- run this where credentials "
                  f"for those remotes exist.")

    bad = [r for r in results if r["verdict"] in FAILING]
    if bad:
        print(f"\n{len(bad)} pin(s) nobody else could resolve.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
