#!/usr/bin/env python3
"""`qm` — one entry point for every governance operation in this corpus.

    uv run qm --help

WHAT THIS IS, AND WHAT IT REFUSES TO BE.

This dispatches. Every subcommand calls the `main(argv)` of the module that
owns the rule and implements nothing itself. A subcommand that recomputed a
verdict, prettied up an exit code, or defaulted a flag would be a second
definition of a governance rule, and two definitions drift the first time one
is fixed -- which is the failure the renderers here are already tested against.

So: no verdicts are formed in this file, and `qm <anything>` exits with exactly
the status its module returned. If a command's output reads wrongly, the fix is
in that module.

WHY THE SCRIPTS STILL RUN WITHOUT IT. Forks execute `project-seed/ci/*.py` out
of the governance submodule with a plain interpreter and never install this
package; the workflows invoke scripts directly so a gate cannot fail for want
of a venv. See the header of `pyproject.toml`. One definition, two entry points.

WHERE IT RUNS. Relative paths in the generators are corpus-relative, so this
locates the corpus root -- by marker, walking up from the working directory --
and refuses to run anywhere else rather than writing `gate-status.json` into
whatever directory you happened to be in.
"""

from __future__ import annotations

import argparse
import importlib.util
import inspect
import os
import sys
from pathlib import Path

# Run as a script -- `python ci/cli.py`, which is how CI and anyone without the
# package installed invokes it -- `ci` is not importable, because the directory
# holding it is not on the path. `uv run qm` hides that entirely: it installs
# the package first, so every `import ci.foo` below resolves and the defect is
# invisible until a runner that installs nothing tries it. Remote CI is where
# this was caught, on the first pull request that let a workflow near it.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# A directory is the corpus if it holds the charter and the records. Checking
# one of them would match a fork that copied only the seed.
MARKERS = ("PRINCIPLES.md", "records")


def corpus_root(start: Path | None = None) -> Path | None:
    """The corpus root at or above `start`, or None if there is none."""
    current = (start or Path.cwd()).resolve()
    for candidate in (current, *current.parents):
        if all((candidate / marker).exists() for marker in MARKERS):
            return candidate
    return None


def call_main(module, argv: list[str]) -> int:
    """Call a module's `main`, whichever of the two shapes it has.

    Most entry points here take `main(argv=None)`. Two seed scripts take
    `main()` and read `sys.argv` themselves. Adapting is the wrapper's job:
    changing those signatures would edit files that twelve projects run out of
    the submodule, to fix a problem none of them has.
    """
    if inspect.signature(module.main).parameters:
        return int(module.main(argv))
    saved = sys.argv
    try:
        sys.argv = [getattr(module, "__name__", "qm"), *argv]
        return int(module.main())
    finally:
        sys.argv = saved


def dispatch(module_name: str, argv: list[str]) -> int:
    """Hand off to a module's own entry point, unchanged."""
    return call_main(__import__(f"ci.{module_name}", fromlist=["main"]), argv)


def seed_script(name: str, argv: list[str]) -> int:
    """Run a seed script in place, the way a fork runs it.

    Imported rather than spawned, so the exit status is the module's own and not
    a child process's. Loaded out of `project-seed/ci/` rather than a copy,
    because a copy is a fork of the constitution that nothing reports.
    """
    root = corpus_root()
    assert root is not None  # checked in main() before any command runs
    seed = root / "project-seed" / "ci"
    sys.path.insert(0, str(seed))
    return call_main(__import__(name, fromlist=["main"]), argv)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="qm",
        description="Governance operations for the Quaternion Media constitution.",
        epilog=(
            "Every subcommand dispatches to the module that owns the rule and "
            "exits with its status. Run `uv run qm <command> --help` for that "
            "module's own options."
        ),
    )
    sub = parser.add_subparsers(dest="command", metavar="<command>")

    docs = sub.add_parser(
        "docs", help="generate, check and read the generated documents"
    ).add_subparsers(dest="docs_command", metavar="<subcommand>")
    docs.add_parser(
        "generate",
        help="regenerate every generated document (the manual dev pass)",
        add_help=False,
    )
    docs.add_parser(
        "check", help="have any generated documents drifted? CI-safe", add_help=False
    )
    docs.add_parser(
        "audit",
        help="does the published site rebuild, and does it match the corpus",
        add_help=False,
    )
    docs.add_parser(
        "states",
        help="what state every governed document is in; --state to filter",
        add_help=False,
    )

    sub.add_parser(
        "gates",
        help="what governs, what each gate refuses, and what it cannot see",
        add_help=False,
    )
    sub.add_parser(
        "tags", help="audit every v* tag in the org against the tag record", add_help=False
    )
    sub.add_parser(
        "review", help="review every record as one body: enforcement, cites, reach",
        add_help=False,
    )
    sub.add_parser(
        "restatements",
        help="every declared restatement of a record names it back",
        add_help=False,
    )
    sub.add_parser(
        "slot", help="is this contributor's pull request slot free?", add_help=False
    )
    sub.add_parser(
        "branch", help="what a branch actually carries, against its base", add_help=False
    )
    sub.add_parser(
        "rulesets", help="what the rulesets say, and what the host is running",
        add_help=False,
    )
    sub.add_parser(
        "lanes", help="the lanes this work is separated into",
        add_help=False,
    )
    sub.add_parser(
        "protocols", help="the procedures run deliberately, and when each last ran",
        add_help=False,
    )
    sub.add_parser(
        "prose", help="the opening of every entry point, side by side",
        add_help=False,
    )
    sub.add_parser(
        "addresses", help="how one data point is named, in every system that holds it",
        add_help=False,
    )
    sub.add_parser(
        "divergence", help="where two views of one address disagree, as deltas",
        add_help=False,
    )
    sub.add_parser(
        "two-views", help="git against the status document, disagreements as deltas",
        add_help=False,
    )
    sub.add_parser(
        "curriculum", help="the reading order, and how two of them reconcile",
        add_help=False,
    )
    sub.add_parser(
        "private-names", help="no private repository name is in a tracked file",
        add_help=False,
    )
    sub.add_parser(
        "workspace", help="write the multi-root workspace from the roster",
        add_help=False,
    )
    sub.add_parser(
        "devloop", help="the local dev environment, measured against what the loop needs",
        add_help=False,
    )
    sub.add_parser(
        "policies", help="what enforces each policy, and what survives a tool change",
        add_help=False,
    )
    sub.add_parser(
        "exceptions", help="what this corpus deliberately does not enforce, and why",
        add_help=False,
    )
    sub.add_parser(
        "config", help="do data files obey the config standard; --migrate fixes it",
        add_help=False,
    )
    sub.add_parser(
        "inventory", help="every repository the org has, against what the corpus knows",
        add_help=False,
    )
    sub.add_parser(
        "ledger", help="what each action was predicted to do, and what it cost",
        add_help=False,
    )
    sub.add_parser(
        "test", help="run the suites CI runs, with CI's arguments", add_help=False,
    )
    sub.add_parser(
        "mutate", help="break a module on purpose; do its tests notice?",
        add_help=False,
    )
    sub.add_parser(
        "preflight", help="run every workflow's real steps locally", add_help=False
    )
    sub.add_parser(
        "brief", help="build this session's opening brief from the repository", add_help=False
    )
    sub.add_parser(
        "demo", help="run one topology through every window and check they agree",
        add_help=False,
    )
    sub.add_parser(
        "mathematics", help="every mathematical mapping states what it has not earned",
        add_help=False,
    )
    sub.add_parser(
        "patterns", help="every high-frequency pattern has a mechanical check",
        add_help=False,
    )
    sub.add_parser(
        "session", help="write a validated session break observation",
        add_help=False,
    )
    return parser


# command -> (module, is_seed_script, argv transform)
ROUTES: dict[str, tuple[str, bool, list[str]]] = {
    "gates": ("gate_dashboard", False, ["gate-status.json", "--format", "md"]),
    "tags": ("tag_audit", False, []),
    "restatements": ("check_restatements", False, []),
    "review": ("record_review", False, []),
    "slot": ("check_one_pr", True, []),
    "branch": ("check_pr_base", True, []),
    "rulesets": ("rulesets", False, []),
    "lanes": ("lanes", False, []),
    "protocols": ("protocols", False, []),
    "prose": ("prose", False, []),
    "addresses": ("addresses", False, []),
    "divergence": ("divergence", False, []),
    "two-views": ("two_views", False, []),
    "curriculum": ("curriculum", False, []),
    "private-names": ("check_private_names", False, []),
    "workspace": ("make_workspace", False, []),
    "devloop": ("devloop", False, []),
    "policies": ("policies", False, []),
    "exceptions": ("exceptions", False, []),
    "config": ("config_standard", False, []),
    "inventory": ("inventory", False, []),
    "ledger": ("ledger", False, []),
    "test": ("run_tests", False, []),
    "mutate": ("mutate", False, []),
    "preflight": ("run_workflows_locally", True, []),
    "brief": ("cowork_context", True, []),
    # Four routes added together, because the omission was one shape rather
    # than four mistakes: a module with a `main` and no route is reachable only
    # by a path somebody has to have been told, which is the thing `qm` exists
    # to make unnecessary. `ci/tests/test_cli.py` now refuses a new one.
    "demo": ("trio_demo", False, []),
    "mathematics": ("check_mathematics", False, []),
    "patterns": ("check_pattern_coverage", False, []),
    "session": ("session_record", False, []),
}

DOCS_ROUTES: dict[str, tuple[str, list[str]]] = {
    "generate": ("generate_docs", []),
    "check": ("generate_docs", ["--check"]),
    "states": ("doc_dashboard", ["doc-status.json"]),
    "audit": ("docs_audit", []),
}


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    parser = build_parser()

    if not argv or argv[0] in ("-h", "--help"):
        parser.print_help()
        return 0

    command, rest = argv[0], argv[1:]

    root = corpus_root()
    if root is None:
        print(
            "qm: not inside the QM corpus. Every path these tools read is "
            "corpus-relative, so running here would write documents into the "
            "wrong directory.\nExpected a parent holding "
            + " and ".join(MARKERS) + ".",
            file=sys.stderr,
        )
        return 2
    # The generators take corpus-relative paths. Changing here rather than
    # passing a root to each one keeps the scripts' own interfaces unchanged,
    # which is what lets a fork keep running them in place.
    os.chdir(root)

    if command == "docs":
        if not rest or rest[0] not in DOCS_ROUTES:
            # Printed rather than routed through argparse's own help, which
            # exits 0 on its way out -- so an unknown subcommand reported
            # success while doing nothing, which is the one result a governance
            # tool must never produce.
            known = ", ".join(DOCS_ROUTES)
            stream = sys.stdout if not rest else sys.stderr
            print(f"usage: qm docs <{known}>", file=stream)
            if rest:
                print(f"\nqm: unknown docs subcommand {rest[0]!r}", file=sys.stderr)
                return 2
            return 0
        module, prefix = DOCS_ROUTES[rest[0]]
        return dispatch(module, prefix + rest[1:])

    if command == "preflight" and importlib.util.find_spec("pip") is None:
        # Said before the run, not diagnosed after it. The workflows install
        # their tools with `python -m pip install`, and a uv environment has no
        # pip -- so five steps fail with "No module named pip" and read as gate
        # failures when the gates are fine. A local failure is a question, not a
        # verdict, and this is the answer to that question stated up front.
        print(
            "qm: this environment has no pip, so every workflow step that installs\n"
            "    its own tools will fail for a reason that is not a gate failure.\n"
            "    Run `uv run --extra preflight qm preflight` instead, or run the\n"
            "    script directly with an interpreter that has pip.\n",
            file=sys.stderr,
        )

    if command in ROUTES:
        module, is_seed, prefix = ROUTES[command]
        args = prefix + rest
        return seed_script(module, args) if is_seed else dispatch(module, args)

    parser.print_help(sys.stderr)
    print(f"\nqm: unknown command {command!r}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
