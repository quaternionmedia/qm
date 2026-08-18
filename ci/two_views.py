#!/usr/bin/env python3
"""Two independent views of the same branches, and where they disagree.

    uv run qm two-views              # git against the committed status document
    uv run qm two-views --deltas     # the disagreements, as delta payloads

WHAT THE TWO VIEWS ARE. Both are already in this repository and neither was
built for this:

  git         `git rev-parse` over the `project/**` refs. What is true now.
  document    `governance-status.yaml`, which records each project branch's
              commit at the moment it was generated.

They agree while the document is fresh and disagree the moment a project branch
moves, which is the honest end-to-end case: two systems observing one moving
thing at different times. It is the same shape dossier and qmcp will have, with
the advantage that both halves are local, offline and already committed.

WHY THIS IS NOT A STALENESS CHECK. `uv run qm docs check` already asks whether
the document is faithful to the refs it names, and answers pass or fail. This
answers a different question -- *which* addresses disagree and about what -- and
by `records/DRAFT-a-disagreement-is-a-delta.md` the answer is a set of deltas
somebody schedules, not a red build. A repository can be perfectly well-run and
carry open reconcile deltas.

WHAT THIS CANNOT SEE. A branch neither view knows about. Both are keyed on the
document's project list, so a `project/**` ref created since generation is
invisible to the comparison rather than reported as a divergence -- one view
having never heard of a row is not the same fact as two views disagreeing about
one, and inventing a row from a single side would be the second view asserting
something it never observed.

It also cannot see anything a `git fetch` has not brought down. The git view
reads local remote-tracking refs, so an unfetched clone reports the branch it
last saw, and the divergence is then between a stale document and a stale ref.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "ci"))

from addresses import format_address  # noqa: E402
from divergence import compare, to_delta  # noqa: E402

DOCUMENT = ROOT / "governance-status.yaml"
DEFAULT_OWNER = "quaternionmedia"
DEFAULT_REPO = "qm"

# Compared deliberately, and it is one field. `records/DRAFT-a-disagreement-is-a-delta.md`
# names an over-broad field list as this rule's failure mode: both sides carry
# their own observation timestamp, and comparing those opens a delta on every
# run for no reason anybody can act on.
FIELDS = ["commit"]

GIT_VIEW = "git"
DOCUMENT_VIEW = "governance-status"


def rev_parse(ref: str, root: Path = ROOT) -> str | None:
    """The commit a ref points at, or None when this clone has no such ref.

    None rather than an empty string: a ref that is absent is a fact, and an
    empty commit would compare unequal to every real one and open a delta
    saying two systems disagree when one of them was never asked.
    """
    proc = subprocess.run(
        ["git", "rev-parse", "--verify", "--quiet", ref],
        cwd=str(root), capture_output=True, text=True,
    )
    if proc.returncode != 0:
        return None
    return proc.stdout.strip() or None


def document_view(path: Path = DOCUMENT) -> dict[str, dict]:
    """What the committed document says each project branch was.

    Keyed by address, so the two views are joined on the grammar rather than on
    a name each side spells its own way.
    """
    if not path.is_file():
        raise SystemExit(f"{path}: no status document to compare against.")
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    view: dict[str, dict] = {}
    for project in data.get("projects") or []:
        branch = project.get("branch") or {}
        ref = branch.get("ref")
        commit = branch.get("commit")
        if not ref or not commit:
            continue
        view[address_of(ref)] = {"commit": commit, "ref": ref}
    return view


def address_of(ref: str, owner: str = DEFAULT_OWNER, repo: str = DEFAULT_REPO) -> str:
    """`origin/project/datum` as an address.

    The remote prefix is stripped and nothing else is. The rest of the ref keeps
    its slashes, which is the property the grammar exists for -- 30 of the 32
    branches here are namespaced, and a slug would make the address unable to
    name the ref it came from.
    """
    name = ref.split("/", 1)[1] if ref.startswith("origin/") else ref
    return format_address(owner, repo, "branch", name)


def git_view(known: dict[str, dict], root: Path = ROOT,
             lookup=None) -> dict[str, dict]:
    """What git says the same branches are, now.

    Keyed on the document's addresses on purpose: this reports disagreements
    about rows both views hold, and a ref git knows that the document has never
    heard of is not a disagreement. See the module docstring.
    """
    lookup = lookup or (lambda ref: rev_parse(ref, root))
    view: dict[str, dict] = {}
    for address, recorded in known.items():
        commit = lookup(recorded["ref"])
        view[address] = {} if commit is None else {"commit": commit}
    return view


def unobservable(document: dict[str, dict], git: dict[str, dict]) -> list[str]:
    """Addresses whose ref this clone cannot resolve at all.

    NOT DIVERGENCES, AND THE DISTINCTION COST A REAL BUG. Three of this
    corpus's project branches are recorded under redacted names --
    `origin/project/private-32` and two more -- which are placeholders rather
    than refs, so `git rev-parse` fails on them permanently. Read as
    disagreements they became three deltas that no work could ever close, which
    is exactly the queue-fills-with-noise failure
    `records/DRAFT-a-disagreement-is-a-delta.md` names as this rule's own.

    A ref one view cannot observe is not two views disagreeing about a value.
    Reported, counted, and never turned into work. An unfetched clone lands here
    too, which is why it is reported rather than filtered away in silence.
    """
    return [address for address in sorted(document) if not git.get(address)]


def reconcile(document: dict[str, dict], git: dict[str, dict],
              fields: list[str] | None = None) -> list:
    """Every divergence between the two views, in address order.

    Addresses the git view could not observe are skipped -- see `unobservable`.
    """
    blind = set(unobservable(document, git))
    found = []
    for address in sorted(document):
        if address in blind:
            continue
        found += compare(
            address, document[address], git.get(address, {}),
            fields or FIELDS, DOCUMENT_VIEW, GIT_VIEW,
        )
    return found


def render(document: dict[str, dict], divergences: list,
           blind: list[str] | None = None) -> str:
    blind = blind or []
    out = [
        f"{len(document)} branch(es) recorded, {len(blind)} of them not "
        f"resolvable in this clone.",
        f"{len(document) - len(blind)} compared on {', '.join(FIELDS)}; "
        f"{len(divergences)} disagree.",
        "",
    ]
    for divergence in divergences:
        out.append(f"  [!] {divergence.address}")
        left = divergence.left if divergence.left is not None else "-"
        right = divergence.right
        out.append(f"      {DOCUMENT_VIEW}: {str(left)[:12]}   "
                   f"{GIT_VIEW}: {'(absent)' if divergence.missing else str(right)[:12]}")
    if not divergences:
        out.append("  Every branch both views could observe is at the same "
                   "commit in both.")
    if blind:
        out += ["", f"{len(blind)} not observable here, and therefore not deltas:"]
        out += [f"  [?] {address}" for address in blind]
        out.append("      A ref this clone cannot resolve -- a redacted name, or "
                   "an unfetched remote.")
        out.append("      One view unable to look is not two views disagreeing.")
    out += [
        "",
        "Each disagreement is a delta, opened at `brainstorm`. Neither view is "
        "treated as correct:",
        "the document is not stale-and-wrong, and git is not right-by-default.",
        "A branch only one view holds is not reported -- that is a different "
        "fact from a disagreement.",
    ]
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--document", default=str(DOCUMENT))
    parser.add_argument("--deltas", action="store_true",
                        help="emit the delta payloads instead of the report")
    args = parser.parse_args(argv)

    document = document_view(Path(args.document))
    git = git_view(document)
    divergences = reconcile(document, git)
    blind = unobservable(document, git)

    if args.deltas:
        print(json.dumps([to_delta(d) for d in divergences], indent=2))
        return 0

    print(render(document, divergences, blind))
    return 0


if __name__ == "__main__":
    sys.exit(main())
