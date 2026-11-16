#!/usr/bin/env python3
"""The tour's two documents, checked against project-seed/tour-schema.json.

A seed file, run in place: a project runs it out of the governance submodule
with a plain interpreter, and nothing copies it.

An application that carries a tour serves two documents: `GET /tour`, its
journeys in order with each stage's line, what to try on it and its latest
word, and `GET /tour/feedback`, every word kept, oldest first
(`records/DRAFT-the-application-carries-its-tour-and-the-harness-reviews-it.md`
sections 3 and 7). The harness reads both. This says whether a document has the
shape both sides hold to.

    python tour_document.py --at http://127.0.0.1:6283     # what an application serves
    python tour_document.py --tour tour.json --feedback feedback.json
    python tour_document.py --vectors                       # every case of tour-vectors.json

It reads the schema itself, with the part of JSON Schema that file uses, and
refuses a schema that uses any other keyword, so the file is the one
definition. Beside it, it holds the three rules a schema cannot state: a
stage's id is its journey's id, a slash and its own stage; a stage's journey is
the journey it is listed under; no two stages share an id.

What it cannot see: whether a stage's line is the one the application shows,
whether what a stage names to try goes through it, and whether a word was kept
as the record says. Those are the application's tests.

Exit status: 0 when every document read has its shape and every case of the
vectors is decided as it declares; 1 when one does not; 2 when a document or
the vectors cannot be read.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

SEED = Path(__file__).resolve().parent.parent
SCHEMA = SEED / "tour-schema.json"
VECTORS = SEED / "tour-vectors.json"
KINDS = ("tour", "feedback")

# Keywords that say what a value is, and so are checked; and keywords that only
# describe, and so are passed over. Any other keyword in the schema is refused.
_CHECKED = {"$ref", "oneOf", "anyOf", "allOf", "if", "then", "type", "enum",
            "const", "pattern", "minLength", "minItems", "required",
            "properties", "items"}
_DESCRIBING = {"$schema", "$id", "$defs", "title", "description", "note"}


class SchemaError(ValueError):
    """The schema uses what this reader does not check."""


def load_schema(path: Path = SCHEMA) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _is(value: Any, kind: str) -> bool:
    if kind == "null":
        return value is None
    if kind == "boolean":
        return isinstance(value, bool)
    if kind == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if kind == "string":
        return isinstance(value, str)
    if kind == "array":
        return isinstance(value, list)
    if kind == "object":
        return isinstance(value, dict)
    raise SchemaError(f"type {kind!r} is not one this reader checks")


def _pattern(pattern: str) -> re.Pattern[str]:
    # A schema's `$` is the end of the string; Python's also matches before a
    # final newline.
    if pattern.endswith("$") and not pattern.endswith("\\$"):
        pattern = pattern[:-1] + r"\Z"
    return re.compile(pattern)


def _check(value: Any, schema: dict[str, Any], root: dict[str, Any], at: str,
           found: list[str]) -> None:
    unknown = set(schema) - _CHECKED - _DESCRIBING
    if unknown:
        raise SchemaError(f"{at}: the schema uses {', '.join(sorted(unknown))}, "
                          "which this reader does not check")
    if "$ref" in schema:
        name = schema["$ref"].removeprefix("#/$defs/")
        if name not in root.get("$defs", {}):
            raise SchemaError(f"{at}: {schema['$ref']} names nothing in $defs")
        _check(value, root["$defs"][name], root, at, found)
    for part in schema.get("allOf", []):
        _check(value, part, root, at, found)
    for key, needed in (("anyOf", "at least one"), ("oneOf", "exactly one")):
        if key not in schema:
            continue
        held = []
        for part in schema[key]:
            alone: list[str] = []
            _check(value, part, root, at, alone)
            held.append(not alone)
        if (key == "anyOf" and not any(held)) or (key == "oneOf" and held.count(True) != 1):
            found.append(f"{at}: is not {needed} of the shapes it may take")
    if "if" in schema:
        test: list[str] = []
        _check(value, schema["if"], root, at, test)
        if not test and "then" in schema:
            _check(value, schema["then"], root, at, found)
    if "type" in schema:
        kinds = schema["type"] if isinstance(schema["type"], list) else [schema["type"]]
        if not any(_is(value, kind) for kind in kinds):
            found.append(f"{at}: is {type(value).__name__}, not {' or '.join(kinds)}")
            return
    if "enum" in schema and value not in schema["enum"]:
        found.append(f"{at}: is {value!r}, not one of {', '.join(map(repr, schema['enum']))}")
    if "const" in schema and value != schema["const"]:
        found.append(f"{at}: is {value!r}, not {schema['const']!r}")
    if isinstance(value, str):
        if len(value) < schema.get("minLength", 0):
            found.append(f"{at}: is empty" if not value else f"{at}: is too short")
        if "pattern" in schema and not _pattern(schema["pattern"]).search(value):
            found.append(f"{at}: {value!r} does not match {schema['pattern']}")
    if isinstance(value, list):
        if len(value) < schema.get("minItems", 0):
            found.append(f"{at}: has fewer than {schema['minItems']} items")
        if "items" in schema:
            for i, item in enumerate(value):
                _check(item, schema["items"], root, f"{at}[{i}]", found)
    if isinstance(value, dict):
        for key in schema.get("required", []):
            if key not in value:
                found.append(f"{at}.{key}: missing")
        for key, part in schema.get("properties", {}).items():
            if key in value:
                _check(value[key], part, root, f"{at}.{key}", found)


def _rules(document: dict[str, Any]) -> list[str]:
    """The three rules of a tour document that the schema cannot state."""
    found, seen = [], {}
    for j, journey in enumerate(document.get("journeys") or []):
        if not isinstance(journey, dict):
            continue
        for s, stage in enumerate(journey.get("stages") or []):
            if not isinstance(stage, dict):
                continue
            at = f"$.journeys[{j}].stages[{s}]"
            if stage.get("journey") != journey.get("id"):
                found.append(f"{at}.journey: is {stage.get('journey')!r}, under the "
                             f"journey {journey.get('id')!r}")
            if stage.get("id") != f"{stage.get('journey')}/{stage.get('stage')}":
                found.append(f"{at}.id: is {stage.get('id')!r}, not its journey, a slash "
                             "and its stage")
            if stage.get("id") in seen:
                found.append(f"{at}.id: {stage.get('id')!r} is also {seen[stage.get('id')]}")
            else:
                seen[stage.get("id")] = at
    return found


def shape(document: Any, kind: str, schema: dict[str, Any] | None = None) -> list[str]:
    """What is wrong with a document of `kind`, `tour` or `feedback`; empty when nothing."""
    schema = schema or load_schema()
    found: list[str] = []
    _check(document, {"$ref": f"#/$defs/{kind}"}, schema, "$", found)
    if kind == "tour" and isinstance(document, dict) and not found:
        found += _rules(document)
    return found


def read(source: str) -> Any:
    """A document from an address, or from a file."""
    if source.startswith(("http://", "https://")):
        with urllib.request.urlopen(source, timeout=10) as answer:
            return json.load(answer)
    return json.loads(Path(source).read_text(encoding="utf-8"))


def vectors(path: Path = VECTORS, schema: dict[str, Any] | None = None) -> list[str]:
    """Each case the reader decides other than its vector declares."""
    schema = schema or load_schema()
    wrong = []
    cases = json.loads(path.read_text(encoding="utf-8"))["cases"]
    for case in cases:
        found = shape(case["payload"], case["document"], schema)
        if case["valid"] and found:
            wrong.append(f"{case['name']}: declared valid, refused: {found[0]}")
        elif not case["valid"] and not found:
            wrong.append(f"{case['name']}: declared invalid, accepted ({case['why']})")
    if not cases:
        wrong.append(f"{path}: holds no case")
    return wrong


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--at", help="where the application runs; URL/tour and URL/tour/feedback are read")
    parser.add_argument("--tour", help="a GET /tour document: an address or a file")
    parser.add_argument("--feedback", help="a GET /tour/feedback document: an address or a file")
    parser.add_argument("--vectors", nargs="?", const=str(VECTORS), metavar="PATH",
                        help="check every case of the vectors (default: project-seed/tour-vectors.json)")
    parser.add_argument("--schema", default=str(SCHEMA), metavar="PATH",
                        help="the schema to check against (default: project-seed/tour-schema.json)")
    args = parser.parse_args(argv)

    sources = {}
    if args.at:
        base = args.at.rstrip("/")
        sources = {"tour": f"{base}/tour", "feedback": f"{base}/tour/feedback"}
    for kind in KINDS:
        if getattr(args, kind):
            sources[kind] = getattr(args, kind)
    if not sources and not args.vectors:
        parser.error("say what to check: --at, --tour, --feedback or --vectors")

    try:
        schema = load_schema(Path(args.schema))
    except (OSError, ValueError) as e:
        print(f"tour_document: the schema at {args.schema} does not read: {e}", file=sys.stderr)
        return 2
    failed = False
    if args.vectors:
        try:
            wrong = vectors(Path(args.vectors), schema)
        except SchemaError as e:
            print(f"tour_document: {args.schema}: {e}", file=sys.stderr)
            return 2
        except (OSError, ValueError, KeyError) as e:
            print(f"tour_document: the vectors at {args.vectors} do not read: {e}", file=sys.stderr)
            return 2
        for line in wrong:
            print(f"  {line}")
        print(f"tour_document: {args.vectors}: "
              + (f"{len(wrong)} case(s) not decided as declared" if wrong else "every case decided as declared"))
        failed |= bool(wrong)
    for kind, source in sources.items():
        try:
            document = read(source)
        except (OSError, ValueError, urllib.error.URLError) as e:
            print(f"tour_document: {source} does not read as a {kind} document: {e}", file=sys.stderr)
            return 2
        try:
            found = shape(document, kind, schema)
        except SchemaError as e:
            print(f"tour_document: {args.schema}: {e}", file=sys.stderr)
            return 2
        for line in found:
            print(f"  {line}")
        print(f"tour_document: {source}: " + ("not the shape of a " if found else "the shape of a ")
              + ("GET /tour" if kind == "tour" else "GET /tour/feedback") + " document")
        failed |= bool(found)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
