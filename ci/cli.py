#!/usr/bin/env python3
"""`qm` — one entry point for every governance operation in this corpus.

    uv run qm --help

It dispatches, and refuses to be anything else.

Every subcommand calls the `main(argv)` of the module that owns the rule and
implements nothing itself. A subcommand that recomputed a verdict, prettied up
an exit code, or defaulted a flag would be a second definition of a governance
rule, and two definitions drift the first time one is fixed.

So: no verdicts are formed in this file, and `qm <anything>` exits with exactly
the status its module returned. If a command's output reads wrongly, the fix is
in that module.

What it does decide is whether a command can run here at all, before the
module is reached, and it says why when it cannot: outside the corpus it
refuses, because every path the generators take is corpus-relative; a command
whose prerequisite is not installed is refused with the command that installs
it, because the module's own failure names the missing import and not the
extra. Neither is a verdict about the corpus, and each exits 2, the status of a
command that did not run.

The scripts still run without it. Forks execute `project-seed/ci/*.py` out
of the governance submodule with a plain interpreter and never install this
package; the workflows invoke scripts directly so a gate cannot fail for want
of a venv. See the header of `pyproject.toml`. One definition, two entry points.

It runs at the corpus root. Relative paths in the generators are
corpus-relative, so this locates the corpus root (by marker, walking up from
the working directory) and refuses to run anywhere else rather than writing
`status/gates.yaml` into whatever directory it was started in.

The help screen is grouped: the commands `AGENTS.md`'s opening tells a reader
to run come first, under their own heading, and everything else follows.
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
# holding it is not on the path. `uv run qm` installs the package first and
# hides that, so the path is set here for the runner that installs nothing.
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
    changing those signatures would edit files that every project runs out of
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


# Every listed command and its one-line help, in the order the help screen
# shows them within each group. `docs` carries subcommands of its own, below.
COMMANDS: tuple[tuple[str, str], ...] = (
    ("docs", "generate, check and read the generated documents"),
    ("gates", "what governs, what each gate refuses, and what it cannot see"),
    ("tags", "audit every v* tag in the org against the tag record"),
    ("review", "review every record as one body: enforcement, cites, reach"),
    ("restatements", "every declared restatement of a record names it back"),
    ("edges", "every principle declares how it relates to the others, or why not"),
    ("glossary-links", "link the first use of each glossary term on every docs page"),
    ("stacks", "your open pull requests, and is any ready while stacked?"),
    ("pins", "is every submodule pin a commit somebody else could get?"),
    ("leaks", "does anything committed name a person, a machine or a conversation?"),
    ("timeless", "does added text shout or narrate its own history? --all for everything"),
    ("harness", "the harness status document, rendered as prose"),
    ("branch", "what a branch actually carries, against its base"),
    ("branches", "every branch, and what deleting it would cost"),
    ("inbound", "what the projects are waiting on this organisation for"),
    ("merge", "your open pull requests, live; merge one when every gate is green"),
    ("queue", "every pull request the queue page names: what changed since its stamp"),
    ("assigned", "what the host says is waiting on you: reviews, assignments, issues"),
    ("references", "what still refers to a branch, before it is retired"),
    ("estate", "every rostered repository, and what of it exists on this disk alone"),
    ("rulesets", "what the rulesets say, and what the host is running"),
    ("lanes", "the lanes this work is separated into"),
    ("families", "which repositories are claimed to be one working system"),
    ("interop", "every repository on one contract surface claims the same version"),
    ("cookbook", "one onboarding page per family, generated from this disk"),
    ("timeline", "a project's dated timeline, from its git history and round log"),
    ("family-suite", "run each family's suites, and say what the batch establishes"),
    ("rollout", "a phased push-through, family by family: claims beside evidence"),
    ("family-demo", "the performing family up on reserved ports, alone and together"),
    ("protocols", "the procedures run deliberately, and when each last ran"),
    ("capabilities", "what each named thing this estate can do has reached"),
    ("prose", "the opening of every entry point, side by side"),
    ("addresses", "how one data point is named, in every system that holds it"),
    ("divergence", "where two views of one address disagree, as deltas"),
    ("two-views", "git against the status document, disagreements as deltas"),
    ("curriculum", "the reading order, and how two of them reconcile"),
    ("private-names", "no private repository name is in a tracked file"),
    ("workspace", "write the multi-root workspace from the roster"),
    ("devloop", "the local dev environment, measured against what the loop needs"),
    ("policies", "what enforces each policy, and what survives a tool change"),
    ("exceptions", "what this corpus deliberately does not enforce, and why"),
    ("config", "do data files obey the config standard; --migrate fixes it"),
    ("inventory", "every repository the org has, against what the corpus knows"),
    ("ledger", "what each action was predicted to do, and what it cost"),
    ("test", "run the suites CI runs, with CI's arguments"),
    ("mutate", "break a module on purpose; do its tests notice?"),
    ("posture", "what the suite costs and what it catches, together"),
    ("preflight", "run every workflow's real steps locally"),
    ("brief", "build this session's opening brief from the repository"),
    ("dashboard", "what of the trio is up, and how to bring up the rest"),
    ("instances", "every server running on this machine, and which one each is"),
    ("demo", "run one topology through every window and check they agree"),
    ("journey-pictures", "take the journeys' pictures from the surfaces that are up"),
    ("mathematics", "every mathematical mapping states what it has not earned"),
    ("patterns", "every high-frequency pattern has a mechanical check"),
    ("session", "write a validated session break observation"),
)
HELP = dict(COMMANDS)

DOCS_COMMANDS: tuple[tuple[str, str], ...] = (
    ("generate", "regenerate every generated document (the manual dev pass)"),
    ("check", "have any generated documents drifted? CI-safe"),
    ("audit", "does the published site rebuild, and does it match the corpus"),
    ("states", "what state every governed document is in; --state to filter"),
)

# The commands `AGENTS.md` tells a reader to run, listed first on the help
# screen so a stranger finds them without reading the rest. The group is
# defined by that page, not by taste: `ci/tests/test_cli.py` reads the page
# and holds the two sets equal.
FIRST_HOUR = ("stacks", "estate", "queue", "gates", "preflight", "test", "branch",
              "leaks", "timeless", "docs", "merge", "brief", "harness", "tags")
FIRST_HOUR_HEADING = "the first hour (the commands AGENTS.md names):"
THE_REST_HEADING = "everything else:"

# Commands that run pytest, which the `dev` extra installs. Refused with the
# command that installs it rather than left to fail inside the module, whose
# own failure names the missing import and nothing else.
NEEDS_PYTEST = frozenset({"test", "posture", "mutate"})


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
    for name, help_line in COMMANDS:
        if name == "docs":
            docs = sub.add_parser(name, help=help_line).add_subparsers(
                dest="docs_command", metavar="<subcommand>")
            for subcommand, sub_help in DOCS_COMMANDS:
                docs.add_parser(subcommand, help=sub_help, add_help=False)
            continue
        sub.add_parser(name, help=help_line, add_help=False)
    # The earlier name for `stacks`, still accepted and left out of the listing.
    sub.add_parser("slot", add_help=False)
    return parser


def help_text(parser: argparse.ArgumentParser) -> str:
    """The help screen: usage, the first hour's commands, then the rest.

    argparse lists every subcommand in one block, in the order added, and has
    no way to group them. This renders the same strings under two headings and
    leaves `qm <command> --help` to the module, so a command's own options
    are still its own.
    """
    width = max(len(name) for name, _ in COMMANDS) + 2

    def block(names) -> str:
        return "\n".join(f"  {name:<{width}}{HELP[name]}" for name in names)

    rest = [name for name, _ in COMMANDS if name not in FIRST_HOUR]
    return "\n".join([
        parser.format_usage().rstrip(),
        "",
        parser.description,
        "",
        FIRST_HOUR_HEADING,
        block(FIRST_HOUR),
        "",
        THE_REST_HEADING,
        block(rest),
        "",
        "options:",
        "  -h, --help  show this help message and exit",
        "",
        parser.epilog,
        "",
    ])


# Commands that read and write only machine-scoped paths, outside every
# repository, and so run from any directory: a session serving another
# repository calls them from that repository's checkout.
ANYWHERE = frozenset({"instances"})

# command -> (module, is_seed_script, argv transform)
ROUTES: dict[str, tuple[str, bool, list[str]]] = {
    "gates": ("gate_dashboard", False, ["status/gates.yaml", "--format", "md"]),
    "tags": ("tag_audit", False, []),
    "restatements": ("check_restatements", False, []),
    "edges": ("check_principle_edges", False, []),
    "glossary-links": ("glossary_links", False, []),
    "review": ("record_review", False, []),
    "stacks": ("check_one_pr", True, []),
    "slot": ("check_one_pr", True, []),
    "pins": ("check_submodule_pins", True, []),
    "leaks": ("check_leaks", True, []),
    "timeless": ("check_timeless", True, []),
    "harness": ("harness_dashboard", False,
                ["status/harness.yaml", "--format", "md"]),
    "branch": ("check_pr_base", True, []),
    "branches": ("branch_census", True, []),
    "inbound": ("inbound", False, []),
    "merge": ("merge_review", False, []),
    "queue": ("queue_page", False, []),
    "assigned": ("assigned", False, []),
    "references": ("branch_references", False, []),
    "estate": ("estate", False, []),
    "rulesets": ("rulesets", False, []),
    "lanes": ("lanes", False, []),
    "families": ("families", False, []),
    "interop": ("interop", False, []),
    "cookbook": ("cookbook", False, []),
    "timeline": ("timeline", False, []),
    "family-suite": ("family_suite", False, []),
    "rollout": ("rollout", False, []),
    "family-demo": ("family_demo", False, []),
    "protocols": ("protocols", False, []),
    "capabilities": ("capabilities", False, []),
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
    "posture": ("test_posture", False, []),
    "preflight": ("run_workflows_locally", True, []),
    "brief": ("cowork_context", True, []),
    # A module with a `main` and no route is reachable only by a path somebody
    # has to have been told; `ci/tests/test_cli.py` refuses one.
    "dashboard": ("dashboard", False, []),
    "instances": ("instances", False, []),
    "demo": ("trio_demo", False, []),
    "journey-pictures": ("journey_pictures", False, []),
    "mathematics": ("check_mathematics", False, []),
    "patterns": ("check_pattern_coverage", False, []),
    "session": ("session_record", False, []),
}

DOCS_ROUTES: dict[str, tuple[str, list[str]]] = {
    "generate": ("generate_docs", []),
    "check": ("generate_docs", ["--check"]),
    "states": ("doc_dashboard", ["status/documents.yaml"]),
    "audit": ("docs_audit", []),
}


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)

    # The registries and pages carry dashes outside ASCII, and Python writes
    # with the console's code page unless told otherwise, so on a Windows
    # console a title reached its reader with a replacement character where
    # the dash was. Set once, here, before any module prints.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    parser = build_parser()

    if not argv or argv[0] in ("-h", "--help"):
        sys.stdout.write(help_text(parser))
        return 0

    command, rest = argv[0], argv[1:]

    if command in ANYWHERE:
        # Read and written outside every repository, and `run` starts its
        # command where it was asked to: neither refused outside the corpus nor
        # moved into it.
        return dispatch(ROUTES[command][0], rest)

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
            # exits 0 on its way out, so an unknown subcommand would report
            # success while doing nothing.
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
        # pip, so the steps that use it fail with "No module named pip" and
        # read as gate failures when the gates are fine. A local failure is a
        # question, not a verdict, and this answers it up front.
        print(
            "qm: this environment has no pip, so every workflow step that installs\n"
            "    its own tools will fail for a reason that is not a gate failure.\n"
            "    Run `uv run --extra preflight qm preflight` instead, or run the\n"
            "    script directly with an interpreter that has pip.\n",
            file=sys.stderr,
        )

    if command in NEEDS_PYTEST and importlib.util.find_spec("pytest") is None:
        # The same shape, and a stop rather than a warning: without pytest
        # these three have nothing to run, and the module's own failure is
        # `No module named pytest`, which names the symptom and not the extra.
        print(
            f"qm: `{command}` runs pytest, which the `dev` extra installs and this\n"
            "    environment does not have. Run it with the extra:\n"
            f"    uv run --extra dev qm {' '.join([command, *rest])}",
            file=sys.stderr,
        )
        return 2

    if command in ROUTES:
        module, is_seed, prefix = ROUTES[command]
        args = prefix + rest
        return seed_script(module, args) if is_seed else dispatch(module, args)

    parser.print_help(sys.stderr)
    print(f"\nqm: unknown command {command!r}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
