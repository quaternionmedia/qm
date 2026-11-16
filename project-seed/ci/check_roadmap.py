#!/usr/bin/env python3
"""Whether a roadmap's lines name journeys and pages that exist.

A seed file, run in place: a project runs it out of the governance submodule
with a plain interpreter, and nothing copies it.

A project's roadmap is `project/ROADMAP.md` on its branch of the corpus, which
a clone of the project holds at `governance/qm/project/ROADMAP.md`. Each
checkbox item is a claim, and names what shows it: a journey the application
serves, as `journey:<id>` in a code span, or walkthrough pages, by a link
(`records/DRAFT-the-application-carries-its-tour-and-the-harness-reviews-it.md`
section 2). This reads the roadmap and says, line by line, whether each name
is there: a page in the clone's `walkthrough/`, a journey in the application's
`GET /tour`. It says which lines are shown by nothing, and which journeys the
application serves that no line names.

    python check_roadmap.py                                  # in a clone: its roadmap and pages
    python check_roadmap.py --at http://127.0.0.1:6283       # and the journeys it serves
    python check_roadmap.py --roadmap project/ROADMAP.md --clone ../app --tour tour.json
    python check_roadmap.py --vectors                        # every case of roadmap-vectors.json

It reports, and gates nothing: a line shown by nothing, or one naming what is
not there, is a finding for the project to read, not a fault. What a person
said of a stage, and whether a ticked line's stages work, is the review's
(`qmcp tour`); this reads no feedback.

The line grammar is the one `qmcp tour` reads, and project-seed/roadmap-vectors.json
is the cases that keep the two implementations of it honest.

What it cannot see: whether a page shows what its line claims; a journey's
names without the application's `GET /tour` (`--at` or `--tour`), in which case
each journey is reported as not looked up; and a name written any other way,
which is prose, so its line is shown by nothing.

Exit status: 0 whenever the roadmap was read, whatever it found, and when every
case of the vectors is decided as it declares; 1 when a case is not; 2 when the
roadmap, the tour or the vectors cannot be read.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tour_document  # noqa: E402

VECTORS = Path(__file__).resolve().parent.parent / "roadmap-vectors.json"
ROADMAP = Path("governance") / "qm" / "project" / "ROADMAP.md"

_GROUP = re.compile(r"^##\s+(?P<name>.+?)\s*$")
_ITEM = re.compile(r"^\s*[-*+]\s+\[(?P<tick>[ xX])\]\s+(?P<words>.*)$")
_BULLET = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s")
_JOURNEY = re.compile(r"`journey:([a-z0-9-]+)`")
# A page is named by a link whose target ends in `walkthrough/NN-<slug>.md`,
# after any relative prefix and before an optional fragment.
_PAGE_LINK = re.compile(
    r"\[[^\]]*\]\((?P<target>(?:[^)\s]*/)?walkthrough/(?P<page>\d{2,}-[^/)\s#]+\.md))(?:#[^)\s]*)?\)")

SHOWN_BY_NOTHING = "shown by nothing"
SERVED, NOT_SERVED, NOT_LOOKED_UP = "served", "not served", "not looked up"
FOUND, NOT_FOUND, NOT_REACHED = "found", "not found", "found, but the link does not reach it"


@dataclass(frozen=True)
class Line:
    """One acceptance line: a claim, and what it names as showing it."""

    group: str | None
    text: str
    ticked: bool
    journeys: tuple[str, ...] = ()
    pages: tuple[str, ...] = ()
    targets: tuple[str, ...] = ()

    @property
    def shown_by_nothing(self) -> bool:
        return not self.journeys and not self.pages


def _line(group: str | None, ticked: bool, words: str) -> Line:
    # A name leaves the claim with the commas and spaces that follow it.
    marked = _PAGE_LINK.sub("\0", _JOURNEY.sub("\0", words))
    claim = re.sub(r"\0[\s,]*", " ", marked)
    links = list(_PAGE_LINK.finditer(words))
    return Line(
        group=group,
        text=" ".join(claim.split()),
        ticked=ticked,
        journeys=tuple(dict.fromkeys(_JOURNEY.findall(words))),
        pages=tuple(dict.fromkeys(m["page"] for m in links)),
        targets=tuple(dict.fromkeys(m["target"] for m in links)),
    )


def roadmap_lines(text: str) -> list[Line]:
    """Every acceptance line of a roadmap, in its order.

    A `## ` heading opens a group. A checkbox item is a line, with the indented
    lines that continue it; a nested list item is not part of it. A fenced
    block is an example and holds no lines.
    """
    found: list[Line] = []
    group: str | None = None
    ticked, words = False, []
    fenced = False

    def close() -> None:
        if words:
            found.append(_line(group, ticked, " ".join(words)))
            words.clear()

    for raw in text.splitlines():
        if raw.lstrip().startswith(("```", "~~~")):
            close()
            fenced = not fenced
            continue
        if fenced:
            continue
        item = _ITEM.match(raw)
        if item:
            close()
            ticked = item["tick"] != " "
            words.append(item["words"])
            continue
        if words and raw[:1] in (" ", "\t") and raw.strip() and not _BULLET.match(raw):
            words.append(raw.strip())
            continue
        close()
        heading = _GROUP.match(raw)
        if heading:
            group = heading["name"]
    close()
    return found


def _page_state(page: str, target: str, roadmap: Path, clone: Path) -> str:
    if not (clone / "walkthrough" / page).is_file():
        return NOT_FOUND
    # Only a roadmap inside the clone has a place its links are read from.
    try:
        roadmap.resolve().relative_to(clone.resolve())
    except ValueError:
        return FOUND
    reached = Path(os.path.normpath(roadmap.resolve().parent / target))
    return FOUND if reached == (clone / "walkthrough" / page).resolve() else NOT_REACHED


def check(lines: list[Line], roadmap: Path, clone: Path,
          served: list[str] | None) -> dict[str, Any]:
    """What each line names, and whether it is there. `served` None: not looked up."""
    rows = []
    for line in lines:
        names = [{"journey": j, "state": NOT_LOOKED_UP if served is None
                  else SERVED if j in served else NOT_SERVED} for j in line.journeys]
        names += [{"page": p, "state": _page_state(p, t, roadmap, clone)}
                  for p, t in zip(line.pages, line.targets)]
        rows.append({"group": line.group, "text": line.text, "ticked": line.ticked,
                     "shown_by_nothing": line.shown_by_nothing, "names": names})
    named = {j for line in lines for j in line.journeys}
    return {
        "roadmap": str(roadmap),
        "clone": str(clone),
        "journeys_looked_up": served is not None,
        "lines": rows,
        "shown_by_nothing": [r["text"] for r in rows if r["shown_by_nothing"]],
        "naming_what_is_not_there": [
            r["text"] for r in rows
            if any(n["state"] in (NOT_SERVED, NOT_FOUND, NOT_REACHED) for n in r["names"])],
        "journeys_no_line_names": None if served is None
        else [j for j in served if j not in named],
    }


def render(found: dict[str, Any], tour: str | None) -> str:
    out = [f"check_roadmap: {found['roadmap']}, against {found['clone']}"
           + (f" and {tour}" if tour else "; no tour read, so no journey looked up")]
    group = object()
    for row in found["lines"]:
        if row["group"] != group:
            group = row["group"]
            out.append(f"## {group}" if group else "(above the first group)")
        box = "[x]" if row["ticked"] else "[ ]"
        if row["shown_by_nothing"]:
            out.append(f"  {box} {row['text']} -- {SHOWN_BY_NOTHING}")
            continue
        out.append(f"  {box} {row['text']}")
        for name in row["names"]:
            what = f"journey:{name['journey']}" if "journey" in name else f"walkthrough/{name['page']}"
            out.append(f"        {what} -- {name['state']}")
    out.append("")
    out.append(f"Shown by nothing: {len(found['shown_by_nothing'])} line(s)")
    out.append(f"Naming what is not there: {len(found['naming_what_is_not_there'])} line(s)")
    if found["journeys_no_line_names"] is not None:
        out.append("Journeys served that no line names: "
                   + (", ".join(found["journeys_no_line_names"]) or "none"))
    out.append("check_roadmap reports and gates nothing.")
    return "\n".join(out)


def vectors(path: Path = VECTORS) -> list[str]:
    """Each case whose lines this reads otherwise than the vector declares."""
    wrong = []
    cases = json.loads(path.read_text(encoding="utf-8"))["cases"]
    for case in cases:
        read = [{k: v for k, v in asdict(line).items() if k != "targets"}
                for line in roadmap_lines(case["roadmap"])]
        for line in read:
            line["journeys"], line["pages"] = list(line["journeys"]), list(line["pages"])
        if read != case["lines"]:
            wrong.append(f"{case['name']}: read as {json.dumps(read)}")
    if not cases:
        wrong.append(f"{path}: holds no case")
    return wrong


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--clone", default=".", help="a clone of the project: its walkthrough/ holds the pages (default: here)")
    parser.add_argument("--roadmap", help=f"the roadmap (default: {ROADMAP.as_posix()} in the clone)")
    parser.add_argument("--at", help="where the application runs; URL/tour is read for its journeys")
    parser.add_argument("--tour", help="a GET /tour document, an address or a file, for its journeys")
    parser.add_argument("--json", action="store_true", help="what was found, as data")
    parser.add_argument("--vectors", nargs="?", const=str(VECTORS), metavar="PATH",
                        help="read every case of the vectors instead (default: project-seed/roadmap-vectors.json)")
    args = parser.parse_args(argv)

    if args.vectors:
        try:
            wrong = vectors(Path(args.vectors))
        except (OSError, ValueError, KeyError) as e:
            print(f"check_roadmap: the vectors at {args.vectors} do not read: {e}", file=sys.stderr)
            return 2
        for line in wrong:
            print(f"  {line}")
        print(f"check_roadmap: {args.vectors}: "
              + (f"{len(wrong)} case(s) not read as declared" if wrong else "every case read as declared"))
        return 1 if wrong else 0

    clone = Path(args.clone)
    roadmap = Path(args.roadmap) if args.roadmap else clone / ROADMAP
    try:
        lines = roadmap_lines(roadmap.read_text(encoding="utf-8", errors="replace"))
    except OSError as e:
        print(f"check_roadmap: no roadmap at {roadmap}: {e.strerror}", file=sys.stderr)
        return 2

    source = f"{args.at.rstrip('/')}/tour" if args.at else args.tour
    served = None
    if source:
        try:
            document = tour_document.read(source)
        except (OSError, ValueError, urllib.error.URLError) as e:
            print(f"check_roadmap: {source} does not read as a GET /tour document: {e}", file=sys.stderr)
            return 2
        wrong = tour_document.shape(document, "tour")
        if wrong:
            print(f"check_roadmap: {source} is not the shape of a GET /tour document: {wrong[0]}",
                  file=sys.stderr)
            return 2
        served = [j["id"] for j in document["journeys"]]

    found = check(lines, roadmap, clone, served)
    print(json.dumps(found, indent=2) if args.json else render(found, source))
    return 0


if __name__ == "__main__":
    sys.exit(main())
