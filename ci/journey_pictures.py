#!/usr/bin/env python3
"""Take the pictures the journeys show, from the surfaces running on this machine.

    uv run qm journey-pictures                # into docs/journeys/pictures/
    uv run qm journey-pictures --generate     # also press the prose reader's Generate
    uv run qm journey-pictures --out DIR

Each page in `docs/journeys/` shows what a person sees at a step, and a picture
taken by hand is one nobody can take again. This takes them from the running
surfaces: the web front end and the prose reader through Chromium at the
family demo's pin (`ci/family-demo.yaml`, `browser:`), and the terminal front
end through Textual's own screenshot, under dossier's environment and over a
scratch database, so the operator's own is never touched.

It starts nothing. Bring the set up first (`docs/journeys/bring-your-set-up.md`);
a surface that does not answer is named and its pictures are skipped.

The harness's thread archive holds the operator's own conversation titles, so
no picture shows a list of them: the prose reader is taken at its archive's
summary card, and the terminal front end above its archive list.

`--generate` presses the prose reader's Generate and then Analyze, with
whichever model its server was started with (`LOOKSATWORDS_OLLAMA_MODEL`). A
missing model is taken as the message the reader shows for it.

What it cannot do: judge a picture. It proves the page drew, not that what it
drew is right; and what a model writes differs on every run.
"""

from __future__ import annotations

import argparse
import asyncio
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT = ROOT / "docs" / "journeys" / "pictures"
FAMILY_DEMO = HERE / "family-demo.yaml"

WEB, PROSE, HARNESS = "http://127.0.0.1:2718", "http://127.0.0.1:1414", 3141
VIEWPORT = {"width": 1280, "height": 800}
HOME = re.compile(r"(?i)([A-Z]:[\\/]{1,2}Users[\\/]{1,2}|/home/|/Users/)[^\\/\s<>\"']+")


# --- under Chromium, at the family demo's pin


def browser(out: Path, surfaces: set[str], generate: bool) -> None:
    from playwright.sync_api import sync_playwright

    with sync_playwright() as playwright:
        chromium = playwright.chromium.launch()
        page = chromium.new_page(viewport=VIEWPORT)
        if "web" in surfaces:
            page.goto(f"{WEB}/app")
            page.keyboard.press("Escape")                # the first visit's tour
            estate = page.locator(".lm_tab", has_text="Estate")
            estate.click()
            page.get_by_text(re.compile(r"seam\(s\) identified")).wait_for()
            # Maximised, so every seam's row is in the picture and not only the first.
            page.locator(".lm_stack", has=estate).locator(".lm_maximise").first.click()
            page.wait_for_timeout(800)
            taken(page.screenshot(path=out / "web-estate.png"), out / "web-estate.png")
            page.reload()
            page.keyboard.press("Escape")
            page.locator(".lm_tab", has_text="Estate").click()
            page.get_by_role("button", name=re.compile("open topology", re.I)).first.click()
            page.locator("button, .chip", has_text=re.compile(r"^\s*pipeline\s*$")).first.click()
            page.get_by_text(re.compile(r"\d+ nodes", re.I)).first.wait_for(timeout=30_000)
            page.wait_for_timeout(1500)                  # the layout settles
            taken(page.screenshot(path=out / "web-topology.png"), out / "web-topology.png")
        if "prose" in surfaces:
            page.goto(f"{PROSE}/")
            page.get_by_role("button", name=re.compile(r"Harness")).first.click()
            # The summary card holds the heading's row; the titles list is below it.
            card = page.get_by_text("Harness thread archive").first.locator("xpath=../..")
            card.wait_for()
            page.wait_for_timeout(500)
            taken(card.screenshot(path=out / "prose-archive.png"), out / "prose-archive.png")
            if generate:
                page.goto(f"{PROSE}/")
                page.get_by_role("button", name="Generate conversation with AI").click()
                written = page.locator("textarea").first
                failed = page.get_by_text(re.compile("Generation failed"))
                for _ in range(360):
                    if written.input_value().strip() or failed.count():
                        break
                    page.wait_for_timeout(500)
                if failed.count():
                    taken(page.screenshot(path=out / "prose-model-missing.png"),
                          out / "prose-model-missing.png")
                else:
                    page.get_by_role("button", name="Analyze conversation").click()
                    page.wait_for_timeout(4000)
                    taken(page.screenshot(path=out / "prose-analyzed.png"),
                          out / "prose-analyzed.png")
        chromium.close()


def taken(_, path: Path) -> None:
    print(f"took {path.name}")


# --- under dossier's own environment


def terminal(out: Path) -> None:
    from dossier.health import prepare
    from dossier.tui import DossierApp

    async def run() -> None:
        prepare()
        app = DossierApp(initial_tab="tab-harness")
        async with app.run_test(size=(120, 34)) as pilot:
            await pilot.pause(6)                         # the harness tab polls
            app.save_screenshot(filename="terminal-harness.svg", path=str(out))

    asyncio.run(run())
    path = out / "terminal-harness.svg"
    svg = HOME.sub(lambda m: m.group(1) + "you", path.read_text(encoding="utf-8"))
    cropped = above(svg, "Thread archive")
    if cropped is None:
        path.unlink()
        print("terminal-harness.svg not kept: its archive list could not be cut off")
        return
    path.write_text(cropped, encoding="utf-8")
    print(f"took {path.name}")


def above(svg: str, marker: str) -> str | None:
    """The screenshot cut off at the row that holds `marker`, or None.

    Cut, not hidden: every row from the marker down is removed from the file,
    so what the picture does not show is not in its source either."""
    import html
    text_row = re.compile(r'<text[^>]*?y="([\d.]+)"[^>]*>(.*?)</text>')
    rows: dict[float, str] = {}                          # one terminal row per y
    for m in text_row.finditer(svg):
        text = html.unescape(re.sub(r"<[^>]+>", "", m.group(2))).replace("\xa0", " ")
        rows[float(m.group(1))] = rows.get(float(m.group(1)), "") + text
    hits = [y for y, text in rows.items() if marker in text]
    box = re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', svg)
    if not hits or not box:
        return None
    cut = min(hits)
    svg = text_row.sub(lambda m: "" if float(m.group(1)) >= cut else m.group(0), svg)
    height = cut - 8
    return (svg.replace(box.group(0), f'viewBox="0 0 {box.group(1)} {height:g}"', 1)
               .replace(f'height="{box.group(2)}"', f'height="{height:g}"', 1))


# --- here: what is up, and each part in its own environment


def pin() -> tuple[str, str]:
    import yaml
    block = yaml.safe_load(FAMILY_DEMO.read_text(encoding="utf-8")).get("browser") or {}
    return str(block.get("python", "3.12")), str(block["playwright"])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path, default=OUT)
    parser.add_argument("--generate", action="store_true",
                        help="also press the prose reader's Generate, then Analyze")
    parser.add_argument("--browser", help=argparse.SUPPRESS)
    parser.add_argument("--terminal", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    out = args.out.resolve()
    if args.browser is not None:
        browser(out, set(args.browser.split(",")) - {""}, args.generate)
        return 0
    if args.terminal:
        terminal(out)
        return 0

    sys.path.insert(0, str(HERE))
    import dashboard
    out.mkdir(parents=True, exist_ok=True)
    up = {name for name in ("web", "prose")
          if dashboard.listening(dashboard.BY_NAME[name].port)}
    for name in sorted({"web", "prose"} - up):
        print(f"{name}: nothing answers on {dashboard.BY_NAME[name].port}; its "
              f"pictures are skipped. `uv run qm dashboard --start {name}`")
    status = 0
    if up:
        python, playwright = pin()
        argv = ["uv", "run", "--no-project", "--python", python,
                "--with", f"playwright=={playwright}", "python", str(Path(__file__)),
                "--out", str(out), "--browser", ",".join(sorted(up))]
        status = subprocess.run(argv + (["--generate"] if args.generate else []),
                                cwd=ROOT).returncode
    repo = dashboard.repo_of(dashboard.BY_NAME["terminal"])
    if repo is None or not dashboard.listening(HARNESS):
        print("terminal: dossier is not beside this clone, or the harness does not "
              "answer; its picture is skipped")
        return status
    with tempfile.TemporaryDirectory() as scratch:
        # This corpus's environment is not dossier's; uv warns of one it ignores.
        env = {key: value for key, value in os.environ.items() if key != "VIRTUAL_ENV"}
        env["DOSSIER_DATABASE_URL"] = f"sqlite:///{Path(scratch, 'dossier.db').as_posix()}"
        done = subprocess.run(["uv", "run", "--no-sync", "--project", str(repo), "python",
                               str(Path(__file__)), "--out", str(out), "--terminal"],
                              cwd=scratch, env=env)
    return status or done.returncode


if __name__ == "__main__":
    sys.exit(main())
