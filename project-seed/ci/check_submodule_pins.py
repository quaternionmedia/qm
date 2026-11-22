#!/usr/bin/env python3
"""Every submodule pin is a commit somebody else could actually get.

    python project-seed/ci/check_submodule_pins.py
    python project-seed/ci/check_submodule_pins.py --json

A pin on a commit that no remote holds cannot be resolved by a fresh checkout.
The pin is made locally, so this runs locally as well as in CI, where somebody
can still fix it in a second.

Unpushed and unreadable are different facts. `git ls-remote <url>` with no ref
answers whether the remote can be read at all, which is decidable anywhere:

    remote readable, commit fetchable      ok
    remote readable, commit NOT fetchable  UNPUSHED -- the defect, hard failure
    remote not readable at all             UNKNOWN -- private, or gone; not a
                                           failure, and never silently green

Run locally, where credentials exist, every remote is readable, so an unpushed
pin is a hard failure there. `docs/ref/ci/gates-and-checks.md` describes the
verdicts.

The governance submodule's URL is also judged by its form. The seed workflows
that run a corpus script clone it on a runner with `git submodule update`, by
the URL `.gitmodules` records, after an `actions/checkout` with
`submodules: false`, which configures no SSH-to-HTTPS rewrite, and with no SSH
key. Any URL but HTTPS fails each of them at the clone, before this script runs
there. A checkout with `submodules: true` adds that rewrite and clones a GitHub
SSH URL; the seed's checkouts do not. Locally, where a key exists, the clone
succeeds, and this verdict is the one place a local run goes red as the runner
does.

What this cannot do: tell a private remote from a deleted one (both are
unreadable, and it says so rather than guessing), tell that the pin is the
commit somebody meant, or tell that an HTTPS governance URL is one a runner can
read without credentials. It reads `git submodule status`, so a submodule that is
not initialised is reported as such rather than skipped.

Do not "fix" this with `git ls-remote <url> <sha>`: `ls-remote` matches ref
*names*, and for a commit that is perfectly fine it prints nothing and exits 0,
which reads as confirmation that the commit is missing.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

OK = "ok"
UNPUSHED = "unpushed"
UNREADABLE = "unreadable"
LOCAL_URL = "local-url"
NOT_HTTPS = "not-https"
NO_URL = "no-url"

# A verdict that means the tree is wrong, as opposed to one that means this
# machine cannot see far enough to say.
FAILING = (UNPUSHED, LOCAL_URL, NOT_HTTPS)

# The submodule the seed workflows clone, named as they name it.
GOVERNANCE = os.environ.get("QM_SUBMODULE") or "governance/qm"

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
    """The URL `.gitmodules` records for the submodule checked out at `path`.

    Found through the entry's `path`, not by assuming its name: git names a
    submodule once, at `submodule add`, and a later `git mv` changes the path
    and keeps the name. A lookup by path-as-name would report a moved
    submodule `no-url` and pass it unexamined.
    """
    # `-z`: a name may hold spaces, and the plain form separates key from
    # value with one, so splitting it would cut such a name in two.
    code, out = run(["git", "config", "-z", "-f", ".gitmodules", "--get-regexp",
                     r"^submodule\..*\.path$"], cwd=str(root))
    if code != 0:
        return ""
    for entry in filter(None, out.split("\0")):
        key, _, value = entry.partition("\n")
        if value != path:
            continue
        name = key[len("submodule."):-len(".path")]
        code, url = run(["git", "config", "-f", ".gitmodules", "--get",
                         f"submodule.{name}.url"], cwd=str(root))
        return url.strip() if code == 0 else ""
    return ""


def as_https(url: str) -> str:
    """The https form of an ssh URL, or the url unchanged.

    A runner has no SSH key, so `git@host:owner/repo` cannot be fetched there
    even when the commit is present, and reading that as "not pushed" would be
    a false alarm for every submodule whose `.gitmodules` names an SSH remote.
    The governance submodule is the exception: the seed workflows clone it by
    its recorded URL, so its form is a verdict of its own in `inspect`.
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


def stranded(root: Path, path: str) -> list[str]:
    """Commits in this submodule's clone that are on no remote of its own.

    The pin being fine does not mean the clone is safe. A submodule is usually
    checked out at a detached HEAD, and work committed onto a branch inside it
    is invisible to every check the parent runs: the parent sees a gitlink,
    `git status` in the parent says nothing, and the branch is on no remote the
    parent knows about. The pin and the branch can be wrong together, and
    fixing the pin alone leaves the branch behind.

    Returns branch names, never the commits: the branch is what somebody pushes.

    This is a local signal, and empty in CI is not a pass: a runner clones each
    submodule fresh and holds no local branches. The question has an answer
    only on the machine where the work was done. Run `uv run qm pins` there.
    """
    code, out = run(["git", "-C", str(root / path), "for-each-ref",
                     "--format=%(refname:short)", "refs/heads"])
    if code != 0:
        return []
    at_risk = []
    for branch in [b.strip() for b in out.splitlines() if b.strip()]:
        code, commits = run(["git", "-C", str(root / path), "rev-list",
                             "--count", branch, "--not", "--remotes"])
        if code == 0 and commits.strip().isdigit() and int(commits.strip()) > 0:
            at_risk.append(f"{branch} ({commits.strip()} commit(s))")
    return at_risk


def inspect(root: Path, sha: str, path: str, governance: str = GOVERNANCE) -> dict:
    url = url_for(root, path)
    if not url:
        return {"path": path, "sha": sha, "url": "", "verdict": NO_URL,
                "detail": "no .gitmodules URL records where this came from"}
    if not is_remote_url(url):
        return {"path": path, "sha": sha, "url": url, "verdict": LOCAL_URL,
                "detail": ("a filesystem URL resolves on the machine that set it "
                           "up and nowhere else. Set the canonical remote, then "
                           f"run: git submodule sync {path}")}
    if path == governance and not url.startswith("https://"):
        https = as_https(url)
        target = https if https.startswith("https://") else "its HTTPS URL"
        return {"path": path, "sha": sha, "url": url, "verdict": NOT_HTTPS,
                "detail": ("the seed workflows clone this submodule on a "
                           "runner by this URL, with no SSH key, and fail at "
                           f"the clone. Set the URL to {target}, then run: "
                           f"git submodule sync {path}")}

    at_risk = stranded(root, path)

    over = reachable(url, sha)
    if over:
        detail = "reachable"
        if over != url:
            detail = f"reachable over {over} (the configured URL is not fetchable here)"
        return {"path": path, "sha": sha, "url": url, "verdict": OK,
                "stranded": at_risk, "detail": detail}

    if readable(url):
        return {"path": path, "sha": sha, "url": url, "verdict": UNPUSHED,
                "stranded": at_risk,
                "detail": ("the remote IS readable from here and does not have "
                           "this commit, so it exists only where it was made. "
                           f"Run: (cd {path} && git push origin HEAD), then "
                           "re-push this repository")}

    return {"path": path, "sha": sha, "url": url, "verdict": UNREADABLE,
            "stranded": at_risk,
            "detail": ("the remote could not be read at all. A private "
                       "submodule is unreadable without credentials, and so is "
                       "one that has been deleted; this cannot separate those "
                       "and does not guess")}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", default=".")
    parser.add_argument("--json", action="store_true", dest="as_json")
    parser.add_argument("--governance", default=GOVERNANCE,
                        help="path of the submodule the seed workflows clone "
                             "(default: $QM_SUBMODULE, else governance/qm)")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    found = submodules(root)
    results = [inspect(root, sha, path, args.governance) for sha, path in found]

    if args.as_json:
        print(json.dumps({"submodules": results}, indent=2))
    else:
        if not found:
            print("No submodules recorded here. Nothing to check.")
        for row in results:
            print(f"{row['verdict']:>10}  {row['path']} @ {row['sha'][:12]}")
            print(f"            {row['detail']}")
            for branch in row.get("stranded") or []:
                print(f"            at risk: {branch} is on no remote of "
                      f"{row['path']}")
        unknown = [r for r in results if r["verdict"] == UNREADABLE]
        if unknown:
            print(f"\n{len(unknown)} pin(s) could not be checked from here. "
                  f"That is unknown, not a pass -- run this where credentials "
                  f"for those remotes exist.")

    at_risk = [(r["path"], b) for r in results for b in (r.get("stranded") or [])]
    if at_risk and not args.as_json:
        print("")
        print(f"{len(at_risk)} branch(es) inside a submodule exist on no "
              f"remote. The pin can be perfectly good and the work still be in "
              f"one place -- push each, or accept losing it with the clone.")

    bad = [r for r in results if r["verdict"] in FAILING]
    if bad:
        print(f"\n{len(bad)} pin(s) nobody else could resolve.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
