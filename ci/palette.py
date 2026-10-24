#!/usr/bin/env python3
"""The one palette QM draws with: the docs site, the family pictures and the
generated dashboards.

Every colour is a pair, light and dark, and every reader takes it from here:

  - the docs site reads `docs/stylesheets/palette.css`, written from this
    module and mapped onto the theme's own variables, so a page, a picture
    and a dashboard open side by side show one colour system;
  - `ci/cookbook.py` draws each family in its hue, and the desk in all of them;
  - `ci/dashboard_style.py` builds the dashboards' stylesheet from the
    neutrals and the states.

A family keeps one hue wherever it appears. A family the record declares and
this module does not colour draws in the neutral, which is a reason to add it
rather than a fault. Names are set as written: nothing styled from here is
transformed to capitals.

The fonts are the site's own copies under `docs/assets/fonts/`, never a font
service, and every stack ends in what any machine has, so a picture or a
dashboard opened without them still reads.

`ci/tests/test_palette.py` holds the contrast floors and the agreement between
this module and the stylesheet written from it.

Usage:
    palette.py --write docs/stylesheets/palette.css
    palette.py --check docs/stylesheets/palette.css
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

LIGHT, DARK = 0, 1

# The page and what sits on it.
NEUTRAL = {
    "ground": ("#f3f4f7", "#0d1118"),
    "surface": ("#ffffff", "#151b25"),
    "sunken": ("#e8eaf0", "#1c2331"),
    "ink": ("#141922", "#e7eaf1"),
    "muted": ("#536075", "#9ba5b7"),
    "line": ("#d5d9e2", "#283143"),
    "accent": ("#9a520b", "#f2aa4c"),
}

# One hue per family: what it drives, in colour.
FAMILY = {
    "performing": ("#9a520b", "#f2aa4c"),
    "show-control": ("#b3305a", "#f0708f"),
    "instruments": ("#0a6f6b", "#43c6bf"),
    "performer-display": ("#5a43b5", "#a693f3"),
    "irl": ("#94551f", "#dd9b63"),
    "infra": ("#55647a", "#98a7bc"),
    "core": ("#2a61bd", "#74a8f6"),
    "games": ("#2d7241", "#73c886"),
    "civic": ("#8a3f9e", "#cf8ce0"),
}
NEUTRAL_HUE = NEUTRAL["muted"]

# What a dashboard says about a measurement. `unknown` is its own colour and
# never green: a thing nobody could measure does not read as fine.
STATE = {
    "ok": ("#2f6b4f", "#7fbaa6"),
    "ok-bg": ("#e6f0e9", "#1a2622"),
    "warn": ("#8a5a12", "#d6a45a"),
    "warn-bg": ("#f6ecd9", "#2a2217"),
    "unknown": ("#4a4a8a", "#9d9ad6"),
    "unknown-bg": ("#eae9f5", "#21223a"),
}

FONTS = {
    "display": "'Big Shoulders Display', 'Arial Narrow', Impact, sans-serif",
    "body": "'IBM Plex Sans', system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif",
    "mono": "'IBM Plex Mono', ui-monospace, 'Cascadia Mono', Consolas, monospace",
}


def hue(family: str, scheme: int = LIGHT) -> str:
    """A family's colour in one scheme, or the neutral for one not coloured."""
    return FAMILY.get(family, NEUTRAL_HUE)[scheme]


def variables(scheme: int) -> dict[str, str]:
    """Every token as a CSS custom property, for one scheme."""
    out = {f"--qm-{name}": pair[scheme] for name, pair in NEUTRAL.items()}
    out.update({f"--qm-{name}": pair[scheme] for name, pair in STATE.items()})
    out.update({f"--qm-family-{name}": pair[scheme] for name, pair in FAMILY.items()})
    out.update({f"--qm-font-{name}": stack for name, stack in FONTS.items()})
    return out


def _rgba(hex_colour: str, alpha: float) -> str:
    r, g, b = (int(hex_colour[i:i + 2], 16) for i in (1, 3, 5))
    return f"rgba({r}, {g}, {b}, {alpha})"


def theme(scheme: int) -> dict[str, str]:
    """The site theme's own variables, set from the tokens.

    The theme draws its header, navigation, links, code and tables from these;
    setting them here is what makes every page take the palette without a rule
    of its own.
    """
    n = {name: pair[scheme] for name, pair in NEUTRAL.items()}
    return {
        "--md-default-bg-color": n["ground"],
        "--md-default-bg-color--light": _rgba(n["ground"], 0.85),
        "--md-default-bg-color--lighter": _rgba(n["ground"], 0.6),
        "--md-default-bg-color--lightest": _rgba(n["ground"], 0.3),
        "--md-default-fg-color": n["ink"],
        "--md-default-fg-color--light": n["muted"],
        "--md-default-fg-color--lighter": _rgba(n["muted"], 0.55),
        "--md-default-fg-color--lightest": _rgba(n["muted"], 0.14),
        "--md-typeset-color": n["ink"],
        "--md-typeset-a-color": n["accent"],
        "--md-primary-fg-color": n["ink"],
        "--md-primary-fg-color--light": n["muted"],
        "--md-primary-fg-color--dark": n["ink"],
        "--md-primary-bg-color": n["surface"],
        "--md-primary-bg-color--light": _rgba(n["surface"], 0.7),
        "--md-accent-fg-color": n["accent"],
        "--md-accent-fg-color--transparent": _rgba(n["accent"], 0.1),
        "--md-accent-bg-color": n["surface"],
        "--md-accent-bg-color--light": _rgba(n["surface"], 0.7),
        "--md-code-bg-color": n["sunken"],
        "--md-code-fg-color": n["ink"],
        "--md-typeset-table-color": n["line"],
        "--md-text-font": "'IBM Plex Sans'",
        "--md-code-font": "'IBM Plex Mono'",
    }


def stylesheet() -> str:
    """`docs/stylesheets/palette.css`: the tokens and the theme, both schemes."""
    def block(selector: str, scheme: int, extra: str = "") -> str:
        lines = [f"{selector} {{"]
        lines += [f"  {k}: {v};" for k, v in variables(scheme).items()]
        lines += [f"  {k}: {v};" for k, v in theme(scheme).items()]
        if extra:
            lines.append(f"  {extra}")
        lines.append("}")
        return "\n".join(lines)

    return "\n".join([
        "/* Generated from ci/palette.py -- do not edit. Regenerate with",
        " * `python ci/palette.py --write docs/stylesheets/palette.css`.",
        " * Light is the theme's `default` scheme and dark is `slate`. */",
        "",
        block(':root, [data-md-color-scheme="default"]', LIGHT),
        "",
        block('[data-md-color-scheme="slate"]', DARK, "color-scheme: dark;"),
        "",
        "/* A family's hue on anything that carries its class. */",
        *[f".qm-f-{name} {{ --c: var(--qm-family-{name}); }}" for name in FAMILY],
        "",
    ])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--write", metavar="PATH")
    parser.add_argument("--check", metavar="PATH")
    args = parser.parse_args(argv)
    body = stylesheet()
    if args.check:
        path = Path(args.check)
        if not path.is_file() or path.read_text(encoding="utf-8") != body:
            print(f"{path} no longer matches ci/palette.py. Regenerate: "
                  f"python ci/palette.py --write {path}", file=sys.stderr)
            return 1
        print(f"{path} matches ci/palette.py.")
        return 0
    if args.write:
        path = Path(args.write)
        path.parent.mkdir(parents=True, exist_ok=True)
        # newline="\n": a Windows text write is CRLF otherwise.
        path.write_text(body, encoding="utf-8", newline="\n")
        print(f"wrote {path}")
        return 0
    sys.stdout.write(body)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
