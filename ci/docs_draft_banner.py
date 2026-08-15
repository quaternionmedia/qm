#!/usr/bin/env python3
"""Mark a built docs site as a draft, loudly, in every page.

A draft site that looks like the published one is worse than no draft site: a
reader who lands on it has no way to know what they are reading, and a screenshot
of it circulates as though it were the documentation.

So the banner is deliberately hard to miss and hard to remove by accident: fixed
to the top of the viewport, full width, high contrast, and injected into every
HTML file the generator produced rather than into one template the theme might
override.

WHAT IT CANNOT DO. It cannot stop someone deploying an unbannered build -- it is
a post-processing step, and a build that skips it publishes clean. The workflow
runs it between build and upload for that reason, and the check below fails if
any page came out unbannered.

Usage:
    python ci/docs_draft_banner.py site --label "PR #55" --url https://github.com/...
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

MARKER = "qm-draft-banner"

BANNER = """<div id="{marker}" style="
  position:fixed;top:0;left:0;right:0;z-index:2147483647;
  background:repeating-linear-gradient(45deg,#b30000,#b30000 12px,#8a0000 12px,#8a0000 24px);
  color:#fff;font:700 14px/1.5 system-ui,sans-serif;text-align:center;
  padding:10px 16px;box-shadow:0 2px 8px rgba(0,0,0,.4);letter-spacing:.02em;">
  DRAFT DOCUMENTATION &mdash; {label} &mdash; NOT PUBLISHED, ASSERTS NOTHING.
  <a href="{url}" style="color:#fff;text-decoration:underline;">source</a>
  <div style="font-weight:400;font-size:12px;opacity:.9;">
    Built from an unmerged branch. The published site is elsewhere; a version tag
    is the only thing that asserts a release.
  </div>
</div>
<div style="height:74px;"></div>
"""


def inject(html: str, label: str, url: str) -> str:
    """Put the banner directly after <body>, or at the top if there is none."""
    if MARKER in html:
        return html
    banner = BANNER.format(marker=MARKER, label=label, url=url)
    lowered = html.lower()
    index = lowered.find("<body")
    if index == -1:
        return banner + html
    end = lowered.find(">", index)
    if end == -1:
        return banner + html
    return html[: end + 1] + "\n" + banner + html[end + 1 :]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("site", help="the built site directory")
    parser.add_argument("--label", required=True, help="what this draft is, e.g. 'PR #55'")
    parser.add_argument("--url", default="", help="where the draft came from")
    args = parser.parse_args(argv)

    site = Path(args.site)
    if not site.is_dir():
        print(f"{site} is not a directory; there is no build to mark", file=sys.stderr)
        return 1

    pages = sorted(site.rglob("*.html"))
    if not pages:
        # An unbannered empty site would upload clean and say nothing.
        print(f"{site} holds no HTML; nothing was built to mark", file=sys.stderr)
        return 1

    for page in pages:
        text = page.read_text(encoding="utf-8", errors="replace")
        page.write_text(inject(text, args.label, args.url), encoding="utf-8", newline="\n")

    missed = [p for p in pages if MARKER not in p.read_text(encoding="utf-8", errors="replace")]
    if missed:
        print(f"{len(missed)} page(s) came out unbannered, e.g. {missed[0]}", file=sys.stderr)
        return 1

    print(f"marked {len(pages)} page(s) as draft: {args.label}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
