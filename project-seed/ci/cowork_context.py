#!/usr/bin/env python3
"""Build a session's opening brief from the repository, not from memory.

SEED FILE, run in place. It answers the questions a session would otherwise
assume the answer to, and writes them down where the answer can be checked.

WHY A TOOL RATHER THAN A CHECKLIST

Every question below has been answered wrongly, confidently, in a real session
in this org: a review of a branch nobody was running; a working tree reported
as the state of a repository; a submodule pin read off the wrong submodule; a
propagation described from a handbook page whose numbers were four days old. A
checklist asks a session to remember to look. This looks, and prints what it
saw with the commit it saw it at.

WHAT IT REFUSES TO DO

  - It does not report absence as compliance. A fact it could not establish is
    printed as `unknown` with the reason, never omitted and never defaulted to
    the reassuring value. A brief that is quietly missing its pull-request
    section reads exactly like a repository with no open pull requests.
  - It does not write to the repository. `--out` writes one file, and the
    default location is ignored by git.
  - It does not act. Nothing here commits, pushes, opens, closes or fetches.
    The one network call is a read of the open pull request list, and
    `--offline` removes it.

Usage:
    python cowork_context.py
    python cowork_context.py --out .harness/session-brief.md
    python cowork_context.py --offline
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

UNKNOWN = "unknown"

# How many sibling branches to list before saying how many were left off.
SIBLING_LIMIT = 8

# The base-branch glob the corpus repository's own slot check runs with. It is
# DEFAULTED from the repository's role rather than required as a flag, because a
# flag is something a session can add quietly to make a red check go green.
# `--per-base` does exist on this module and overrides this constant when passed
# (see the argument definition and its first use below), so this is a default and
# not an enforcement -- the comment used to say "rather than passed as a flag",
# which reads as though the flag were absent.
# Every `project/<name>` branch here is pinned by a different downstream
# submodule, so two propagation pull requests are two unrelated projects.
CORPUS_PER_BASE = ["project/*"]


def force_utf8_output() -> None:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")


def run(*args: str, cwd: Path | None = None) -> tuple[int, str]:
    """Run a command, returning (status, output). Never raises on failure.

    Failure is a value here rather than an exception because almost every
    question this tool asks has a legitimate "cannot tell" answer, and the
    reason for it is part of the brief.
    """
    result = subprocess.run(
        args,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=str(cwd) if cwd else None,
    )
    return result.returncode, (result.stdout or "").strip() or (result.stderr or "").strip()


def git(root: Path, *args: str) -> tuple[int, str]:
    return run("git", "-C", str(root), *args)


def repo_root() -> Path | None:
    status, out = run("git", "rev-parse", "--show-toplevel")
    return Path(out) if status == 0 and out else None


def slug_from_remote(url: str) -> str | None:
    """owner/name out of either remote form, or None if it is neither."""
    match = re.search(r"[:/]([^/:]+)/([^/]+?)(?:\.git)?/?$", url.strip())
    return f"{match.group(1)}/{match.group(2)}" if match else None


def governance_mount(root: Path) -> dict:
    """Where the corpus is vendored in this repository, and what it points at.

    Named by path rather than taken from the first submodule: reading
    `git submodule status | head -1` once reported an unrelated submodule's
    commit as the governance pin, and the report that followed was confident
    and wrong.
    """
    gitmodules = root / ".gitmodules"
    if not gitmodules.exists():
        if (root / "PRINCIPLES.md").exists() and (root / "records").is_dir():
            return {"role": "corpus", "path": ".", "note": "this repository IS the corpus"}
        return {"role": "none", "unknown": "no .gitmodules, and this is not the corpus"}

    text = gitmodules.read_text(encoding="utf-8", errors="replace")
    blocks = re.findall(r'\[submodule "([^"]+)"\]([^\[]*)', text)
    for _, body in blocks:
        path_match = re.search(r"^\s*path\s*=\s*(.+)$", body, re.M)
        url_match = re.search(r"^\s*url\s*=\s*(.+)$", body, re.M)
        branch_match = re.search(r"^\s*branch\s*=\s*(.+)$", body, re.M)
        if not path_match or not url_match:
            continue
        url = url_match.group(1).strip()
        # A .gitmodules written on Windows records a local path with escaped
        # backslashes -- `C:\\Users\\...\\qm` -- so a separator class of `[:/]`
        # matches the SSH and HTTPS forms and silently misses that one. The
        # symptom is a repository reported as having no governance mount while
        # sitting inside one.
        normalised = url.replace("\\\\", "/").replace("\\", "/")
        if not re.search(r"[:/]qm(?:\.git)?/?$", normalised):
            continue
        path = path_match.group(1).strip()
        found = {
            "role": "submodule",
            "path": path,
            "url": url,
            "branch": branch_match.group(1).strip() if branch_match else UNKNOWN,
        }
        status, out = git(root, "submodule", "status", "--", path)
        found["pin"] = out.split()[0].lstrip("+-U") if status == 0 and out else UNKNOWN
        found["initialised"] = status == 0 and not out.startswith("-")
        if (
            normalised.startswith("/")
            or normalised.startswith(".")
            or re.match(r"^[A-Za-z]:", normalised)
        ):
            found["warning"] = (
                "the URL is a filesystem path; a pin that resolves here will not "
                "resolve in CI"
            )
        return found
    return {"role": "none", "unknown": "no submodule whose URL names the qm corpus"}


def local_state(root: Path) -> dict:
    state: dict = {}
    _, state["branch"] = git(root, "rev-parse", "--abbrev-ref", "HEAD")
    _, state["head"] = git(root, "rev-parse", "HEAD")
    _, state["head_subject"] = git(root, "log", "-1", "--format=%s")
    _, state["head_date"] = git(root, "log", "-1", "--format=%cI")

    status, out = git(root, "status", "--porcelain")
    state["dirty"] = len(out.splitlines()) if status == 0 and out else 0

    status, out = git(root, "rev-parse", "--abbrev-ref", "@{upstream}")
    if status == 0 and out:
        state["upstream"] = out
        _, counts = git(root, "rev-list", "--left-right", "--count", f"{out}...HEAD")
        parts = counts.split()
        state["behind"], state["ahead"] = (parts + ["?", "?"])[:2]
    else:
        state["upstream"] = None
        state["unpushed"] = "this branch has no upstream; nothing here is on a remote"

    status, out = git(root, "remote", "get-url", "origin")
    state["remote"] = out if status == 0 else None
    state["slug"] = slug_from_remote(out) if status == 0 and out else None
    return state


def sibling_branches(root: Path, current: str) -> tuple[list[str], int]:
    """Branches carrying commits the current branch does not, newest first.

    A second session on this repository shows up here first -- as a branch this
    session did not create, holding work it cannot see. Newest first because
    that is the one a session running right now is on.

    **Remote branches count, and this is the half that was missing.** A fresh
    clone has exactly one local branch, so a `refs/heads` scan reports a clean
    repository no matter how much pushed work is waiting. Work that has been
    pushed and has no pull request is invisible to every other signal a session
    has -- the slot check reads pull requests, and the handoff pages live on
    whichever branch they were written on. Two such branches existed in this
    corpus on 2026-08-14 and no opening brief on any other machine would have
    named either.

    A remote-tracking ref whose local branch is already listed is dropped, so
    the usual case prints one line rather than two.

    Returns the listed lines and how many were left off. A corpus clone holds
    two dozen long-lived branches and printing all of them buries the one that
    moved an hour ago, but a list that silently stops reads as a complete one.
    """
    status, out = git(
        root,
        "for-each-ref",
        "--sort=-committerdate",
        "--format=%(refname:short)",
        "refs/heads",
        "refs/remotes",
    )
    if status != 0:
        return [], 0

    # `origin/HEAD` is a symbolic ref, not a branch. Dropping it is defence
    # rather than a load-bearing guard: it resolves to the default branch, so
    # the commit count below is zero and it would be filtered anyway. No
    # mutation reaches this line, which is why there is no test naming it.
    names = [n for n in out.splitlines() if n and not n.endswith("/HEAD")]
    local = {n for n in names if "/" not in n or not n.startswith(("origin/", "upstream/"))}

    others = []
    for name in names:
        if name == current:
            continue
        # `origin/foo` when `foo` is already a local branch is the same work
        # reported twice. The local one wins; it is what a session checks out.
        bare = name.split("/", 1)[1] if name.startswith(("origin/", "upstream/")) else name
        if name != bare and bare in local:
            continue
        code, count = git(root, "rev-list", "--count", f"{current}..{name}")
        if code == 0 and count.isdigit() and int(count) > 0:
            code, when = git(root, "log", "-1", "--format=%cI", name)
            others.append(f"{name}: {count} commit(s) not on {current}, last {when}")
    return others[:SIBLING_LIMIT], max(0, len(others) - SIBLING_LIMIT)


# Generated documents a session can read instead of re-deriving, and the age
# past which each stops being quotable. A document is listed here by filename
# because a session that has to be told the path has already been given the
# facts by whoever told it.
GENERATED_DOCUMENTS = (
    ("governance-status.yaml", "where every project stands", 168),
    ("harness-status.json", "pull request slots, phases, governance evidence", 24),
)


def document_age_hours(path: Path) -> float | None:
    """Hours since the document says it was generated, from its own stamp.

    Read out of the file rather than from its mtime: a checkout sets mtime to
    the moment somebody cloned, so a document generated last month would look
    minutes old to every fresh clone -- which is the reading that matters,
    because a fresh clone is what a new session has.
    """
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    match = re.search(r'"?generated_at"?\s*:\s*"?(\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d)', text)
    if not match:
        return None
    stamped = datetime.strptime(match.group(1), "%Y-%m-%dT%H:%M:%S").replace(
        tzinfo=timezone.utc
    )
    return (datetime.now(timezone.utc) - stamped).total_seconds() / 3600


def generated_documents(root: Path, mount: dict) -> list[str]:
    base = root if mount.get("role") == "corpus" else root / str(mount.get("path", ""))
    lines = []
    for name, what, budget in GENERATED_DOCUMENTS:
        path = base / name
        if not path.exists():
            lines.append(f"- `{name}` — **absent**. Nothing to read; do not assume clean.")
            continue
        age = document_age_hours(path)
        if age is None:
            lines.append(
                f"- `{name}` — {what}. **Age {UNKNOWN}**: no `generated_at` found, "
                "so treat every figure in it as unverified."
            )
        elif age > budget:
            lines.append(
                f"- `{name}` — {what}. **{age:.0f}h old, past its {budget}h "
                "budget.** Read it for shape; re-derive any figure you act on."
            )
        else:
            lines.append(f"- `{name}` — {what}. {age:.0f}h old, within its {budget}h budget.")
    return lines


def workflows(root: Path) -> list[str]:
    directory = root / ".github" / "workflows"
    if not directory.is_dir():
        return []
    return sorted(p.name for p in directory.glob("*.y*ml"))


def handoffs(root: Path, mount: dict) -> tuple[list[str], str | None]:
    base = root if mount.get("role") == "corpus" else root / str(mount.get("path", ""))
    directory = base / "handbook" / "handoffs"
    if not directory.is_dir():
        return [], f"{directory} does not exist or the submodule is not initialised"
    return sorted(p.name for p in directory.glob("*.md") if p.name != "README.md"), None


def viewer_login() -> tuple[str | None, str | None]:
    status, out = run("gh", "api", "user", "--jq", ".login")
    if status != 0 or not out:
        return None, f"gh api user failed: {out.splitlines()[0] if out else 'no output'}"
    return out.splitlines()[0].strip(), None


def pr_slots(slug: str, login: str, per_base: list[str]) -> tuple[str, int | None]:
    """The slot check's own report, verbatim, plus its exit status."""
    script = Path(__file__).with_name("check_one_pr.py")
    args = [sys.executable, str(script), "--repo", slug, "--contributor", login]
    for pattern in per_base:
        args += ["--per-base", pattern]
    status, out = run(*args)
    return out, status


def emit(root: Path, args: argparse.Namespace) -> str:
    lines: list[str] = []
    add = lines.append

    state = local_state(root)
    mount = governance_mount(root)

    add("# Session brief")
    add("")
    add(
        "Generated by `cowork_context.py`. Every number below is true at the "
        "commit named in it and nowhere else; re-derive before acting on any of "
        "it. Facts this tool could not establish say `unknown` and why — none of "
        "them defaults to the reassuring value."
    )
    add("")

    add("## Where you are")
    add("")
    add(f"- repository: `{root}`")
    add(f"- remote: `{state['remote'] or UNKNOWN}`  ({state['slug'] or UNKNOWN})")
    add(f"- branch: `{state['branch']}`")
    add(f"- HEAD: `{state['head'][:12]}` {state['head_date']} — {state['head_subject']}")
    if state["upstream"]:
        add(
            f"- upstream: `{state['upstream']}` — "
            f"{state['ahead']} ahead, {state['behind']} behind"
        )
    else:
        add(f"- upstream: **none** — {state['unpushed']}")
    add(
        f"- uncommitted changes: {state['dirty']}"
        + ("  ← someone left work here, and it may not be yours" if state["dirty"] else "")
    )
    add("")

    add("## Governance")
    add("")
    if mount.get("role") == "corpus":
        add("- this repository **is** the corpus; there is no submodule to read")
        add("- read `AGENTS.md`, then `handbook/async-contract.md`")
    elif mount.get("role") == "submodule":
        add(f"- corpus mounted at `{mount['path']}`, branch `{mount['branch']}`")
        add(f"- pinned commit: `{str(mount.get('pin', UNKNOWN))[:12]}`")
        if not mount.get("initialised"):
            add(
                "- **the submodule is not initialised** — every governance file is "
                "absent, and a check that looks for one will report it missing "
                "rather than unreadable. `git submodule update --init --recursive`"
            )
        if mount.get("warning"):
            add(f"- **warning**: {mount['warning']}")
        add(f"- read `{mount['path']}/AGENTS.md`, then `{mount['path']}/handbook/async-contract.md`")
    else:
        add(f"- corpus mount: **{UNKNOWN}** — {mount.get('unknown')}")
        add("- this repository has not adopted the constitution, or has adopted it by hand")
    add("")

    add("## Your pull request slot")
    add("")
    if args.offline:
        add(f"- {UNKNOWN} — `--offline` was passed, so no pull request was read")
    elif not state["slug"]:
        add(f"- {UNKNOWN} — no `origin` remote to name a repository")
    else:
        login, why = viewer_login()
        if not login:
            add(f"- {UNKNOWN} — {why}")
            add("- this is not the same as holding no slot; nothing was read")
        else:
            per_base = args.per_base
            if not per_base and mount.get("role") == "corpus":
                per_base = CORPUS_PER_BASE
                add(
                    "Each `project/<name>` branch here is pinned by a different "
                    "downstream submodule, so each holds its own slot. That is the "
                    "only exemption, and it is applied because this repository is "
                    "the corpus — not because a flag was passed."
                )
                add("")
                add(
                    "**The slot belongs to the *base*, not to the branch.** A pull "
                    "request whose base is `project/<name>` gets the exemption; one "
                    "whose *head* is a project branch does not, and never should — a "
                    "`project/<name>` branch is permanent and is never merged into "
                    "`main`. Reading this as \"my project branch has its own slot, so "
                    "I may open a pull request from it\" is how the `main` slot gets "
                    "spent twice; `project-seed/ci/check_pr_base.py` refuses that "
                    "direction, and the README's \"Branch namespaces\" says why."
                )
                add("")
            report, status = pr_slots(state["slug"], login, per_base)
            add("```")
            lines.extend(report.splitlines())
            add("```")
            if status == 0:
                add("")
                add("Your slot is free, or holds the one pull request you will add to.")
            else:
                add("")
                add(
                    "**You are over the limit.** Fold or close before opening "
                    "anything: close the pull request FIRST, then push onto the "
                    "branch that survives — pushing first merges it."
                )
    add("")

    add("## Other work in this clone")
    add("")
    others, omitted = sibling_branches(root, state["branch"])
    if others:
        add("Branches carrying commits this one does not, newest first. A second")
        add("session on this clone shows up here:")
        add("")
        for line in others:
            add(f"- `{line}`")
        if omitted:
            add("")
            add(
                f"- …and {omitted} more, not listed. Full list: "
                "`git for-each-ref --sort=-committerdate refs/heads`"
            )
    else:
        add("- no local branch carries commits this one does not")
    add("")

    add("## Gates you must run before calling anything ready")
    add("")
    found = workflows(root)
    if found:
        for name in found:
            add(f"- `.github/workflows/{name}`")
        add("")
        prefix = "" if mount.get("role") == "corpus" else f"{mount.get('path')}/"
        add(f"Run them: `python {prefix}project-seed/ci/run_workflows_locally.py`")
        add(
            f"Check the branch: `python {prefix}project-seed/ci/check_pr_base.py "
            f"--base <base> --head {state['branch']}`"
        )
        add("")
        add(
            "The runner does not reproduce `uses:` steps, the runner image, or "
            "secrets. Say so when reporting, and treat a local failure as a "
            "question rather than a verdict."
        )
    else:
        add(f"- {UNKNOWN} — no `.github/workflows/` in this repository")
        add("- a repository with no gates is not a repository that passed them")
    add("")

    add("## Generated documents, and whether you may quote them")
    add("")
    add(
        "Read these instead of re-deriving what they hold — and check the age. "
        "A figure quoted from a stale document is a claim about an organisation "
        "that has moved on, delivered with a date that makes it look checked."
    )
    add("")
    lines.extend(generated_documents(root, mount))
    add("")
    add(
        "`ci/harness_dashboard.py harness-status.json --format md` renders the "
        "second one for reading; each document also carries its own refresh "
        "command and its own `do_not` list."
    )
    add("")

    add("## Open handoffs")
    add("")
    pages, why = handoffs(root, mount)
    if why:
        add(f"- {UNKNOWN} — {why}")
    elif pages:
        for name in pages:
            add(f"- `handbook/handoffs/{name}`")
        add("")
        add("Read `handbook/handoffs/README.md` first, then exactly one of these.")
    else:
        add("- none")
    add("")

    add("## Before you write anything")
    add("")
    add("- [ ] State the commit you are working against, here and in the pull request.")
    add("- [ ] Ask every question you are unsure of **now**. A pull request states decisions.")
    add("- [ ] Confirm whether *keep everything local* is in force. It survives compaction.")
    add("- [ ] Bind no default port, and ask any server you measure what it is.")
    add("- [ ] Suppress co-author trailers. Commits carry the contributor's name only.")

    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    force_utf8_output()
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", metavar="PATH", help="also write the brief here")
    parser.add_argument(
        "--offline", action="store_true", help="skip the pull request read"
    )
    parser.add_argument(
        "--per-base",
        action="append",
        default=[],
        metavar="GLOB",
        help="passed through to check_one_pr.py",
    )
    args = parser.parse_args(argv)

    root = repo_root()
    if root is None:
        sys.exit("cowork_context: not inside a git repository")

    brief = emit(root, args)
    sys.stdout.write(brief)

    if args.out:
        target = Path(args.out)
        if not target.is_absolute():
            target = root / target
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(brief, encoding="utf-8", newline="\n")
        print(f"\nwritten to {target}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
