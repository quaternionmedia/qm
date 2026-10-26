"""The onboarding pages are generated, and they refuse to flatter.

An onboarding page is read by the person least able to notice it is wrong.
So these assert the two things a newcomer would be misled by: a page that
invents a governed entry point where there is none, and a page whose figures
have drifted from the disk it claims to describe.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

CI_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(CI_DIR))

import cookbook  # noqa: E402


def family(name="a-family", drives="the thing", members=("one", "two")):
    return {"name": name, "drives": drives, "members": list(members)}


def state(name, adopted=False, on_disk=True, dirty=0, branch="main", last="2026-01-01"):
    return {"name": name, "on_disk": on_disk, "branch": branch,
            "dirty": dirty, "last": last, "adopted": adopted}


def test_a_family_with_no_governed_member_gets_no_entry_point():
    """A family with no adopted member gets no governed entry point: one would
    send a newcomer to run a command that does not exist there.

    Mutation: make `page` emit the governed branch unconditionally and this
    fails.
    """
    text = cookbook.page(family(), [state("one"), state("two")], "2026-01-01")
    assert "No member of this family carries governance yet" in text
    assert "uv run qm cowork" not in text


def test_a_family_with_a_governed_member_names_one():
    text = cookbook.page(family(), [state("one", adopted=True), state("two")], "2026-01-01")
    assert "1 of 2 members carry governance" in text
    assert "cd one" in text


def test_the_corpus_is_the_entry_point_for_its_own_family():
    """Reading only `project/*` branches printed the corpus as ungoverned and
    sent a reader to the next repository listed."""
    text = cookbook.page(
        family(members=("dossier", "qm")),
        [state("dossier", adopted=True), state("qm", adopted=True)],
        "2026-01-01")
    assert "cd qm" in text


def test_the_committed_page_carries_no_machine_scoped_state():
    """The committed page carries no machine-scoped state: the branch, the
    uncommitted count and the last commit date differ per machine and change on
    every keystroke, so `qm docs check` would report drift whenever anybody
    edited a file. `status/inventory.yaml` and `inventory-local.json` make the
    same split.

    Mutation: put `state['branch']` or `state['dirty']` back into `page` and
    this fails.
    """
    text = cookbook.page(
        family(), [state("one", branch="feat/x", dirty=7, last="2026-05-05")],
        "2026-01-01")
    assert "feat/x" not in text
    assert "2026-05-05" not in text
    assert "7" not in text.replace("2026-01-01", "")


def test_the_page_says_what_it_deliberately_omits():
    """An omission a reader cannot see is indistinguishable from an oversight."""
    text = cookbook.page(family(), [state("one")], "2026-01-01")
    assert "machine-scoped" in text
    assert "uv run qm cookbook" in text


def test_the_page_carries_only_the_claim_that_does_not_move():
    text = cookbook.page(family(), [state("one", adopted=True), state("two")], "2026-01-01")
    assert "| member | governed |" in text
    assert "| `one` | yes |" in text
    assert "| `two` | no |" in text


def test_the_generated_stamp_is_not_what_the_check_compares():
    """A check that failed daily on a date nobody reads is one people learn to
    rerun rather than read."""
    a = cookbook._without_stamp("body\n*Generated 2026-01-01.*\n")
    b = cookbook._without_stamp("body\n*Generated 2026-12-31.*\n")
    assert a == b


def test_the_picture_is_drawn_from_the_same_states_as_the_prose():
    """Drawn, not pasted -- and from the same facts the prose uses, so the two
    cannot disagree. It carries governance and nothing machine-scoped, for the
    same reason the table does."""
    picture = cookbook.svg("a-family", [state("one", adopted=True), state("two", dirty=3)])
    assert "<svg" in picture and "a-family" in picture
    assert "one" in picture and "two" in picture
    assert "governed" in picture and "not adopted" in picture
    assert "3 dirty" not in picture


# --- the disk view resolves clones the way the roster says -----------------


def _repo(path: Path) -> Path:
    path.mkdir(parents=True)
    (path / ".git").mkdir()
    return path


def test_a_member_is_found_where_the_roster_places_it_not_where_the_probe_looks(
        tmp_path: Path, monkeypatch) -> None:
    """A member is found at the path the roster carries, not only where a
    `<root>/<name>` probe looks, so `qm cookbook` and `qm estate` agree.

    Mutation: make `clone_of` skip the roster entry and fall through to the
    probe, and this fails on the first assertion.
    """
    thing = _repo(tmp_path / "elsewhere" / "thing")
    monkeypatch.setattr(cookbook, "ROSTER_ROOTS", [tmp_path])
    monkeypatch.setattr(cookbook, "SEARCH_ROOTS", (tmp_path / "nowhere",))
    index = {"thing": {"name": "thing", "paths": ["elsewhere/thing"]}}

    assert cookbook.clone_of("thing", index) == thing.resolve()
    assert cookbook.clone_of("thing", {}) is None


def test_a_private_member_is_found_by_its_reference(tmp_path: Path, monkeypatch) -> None:
    """`families.json` names a private member by its reference; the companion
    supplies the paths. A reference is not a directory, so the probe alone
    reported every private member as not on this disk.
    """
    secret = _repo(tmp_path / "secret")
    monkeypatch.setattr(cookbook, "ROSTER_ROOTS", [tmp_path])
    monkeypatch.setattr(cookbook, "SEARCH_ROOTS", (tmp_path / "nowhere",))
    monkeypatch.setattr(cookbook, "git", lambda path, *args: "main")
    index = {"private-98": {"ref": "private-98", "name": "secret", "paths": ["secret"]}}

    assert cookbook.clone_of("private-98", index) == secret.resolve()
    state = cookbook.member_state("private-98", set(), index)
    assert state["on_disk"] is True
    assert state["name"] == "private-98"


def test_a_member_the_roster_does_not_carry_still_gets_the_probe(tmp_path: Path, monkeypatch) -> None:
    orphan = _repo(tmp_path / "orphan")
    monkeypatch.setattr(cookbook, "ROSTER_ROOTS", [tmp_path / "nowhere"])
    monkeypatch.setattr(cookbook, "SEARCH_ROOTS", (tmp_path,))

    assert cookbook.clone_of("orphan", {}) == orphan


def test_build_reads_every_member_through_the_roster(tmp_path: Path, monkeypatch) -> None:
    """`build` itself reads every member through the roster: direct tests of
    the resolver cannot see a lookup overwritten inside `build`.
    """
    _repo(tmp_path / "elsewhere" / "thing")
    families = tmp_path / "families.json"
    families.write_text(
        '{"families": [{"name": "f", "drives": "x", "members": ["thing", "gone"]}],'
        ' "unstated": []}', encoding="utf-8")
    monkeypatch.setattr(cookbook, "FAMILIES", families)
    monkeypatch.setattr(cookbook, "ROSTER_ROOTS", [tmp_path])
    monkeypatch.setattr(cookbook, "SEARCH_ROOTS", (tmp_path / "nowhere",))
    monkeypatch.setattr(cookbook, "adopted_names", lambda: set())
    monkeypatch.setattr(cookbook, "roster_index", lambda: {
        "thing": {"name": "thing", "paths": ["elsewhere/thing"]}})
    monkeypatch.setattr(cookbook, "git", lambda path, *args: "main")
    seen = []
    real = cookbook.member_state
    monkeypatch.setattr(cookbook, "member_state",
                        lambda name, adopted, index=None: seen.append(index) or real(name, adopted, index))

    files = cookbook.build(tmp_path / "out")

    assert set(files) == {"f.md", "f.svg", "README.md", "families.svg"}
    assert "| `thing` | no |" in files["f.md"]
    assert "| `gone` | no |" in files["f.md"]
    # The roster index, not the README's line list, reached every lookup.
    assert seen and all(isinstance(i, dict) and "thing" in i for i in seen)


# --- the desk: every family in one picture -----------------------------------


def _desk_document():
    return {"families": [
        {"name": "performing", "drives": "**a show** — the whole", "within": None,
         "subfamilies": ["instruments"], "members": ["editor"]},
        {"name": "instruments", "drives": "**the sound** — loops", "within": "performing",
         "subfamilies": [], "members": ["synth"]},
        {"name": "irl", "drives": "**matter** — boards", "within": None,
         "subfamilies": [], "members": ["board"]},
    ], "unstated": ["somebody"]}


def test_the_desk_draws_every_family_from_the_counts_it_is_given():
    """Drawn from the same counts as the index table, so the two cannot
    disagree; an inner family is drawn inside its outer one's frame."""
    picture = cookbook.desk(_desk_document(),
                            {"performing": (2, 1), "instruments": (1, 1), "irl": (1, 0)})
    assert "<svg" in picture
    for name in ("performing", "instruments", "irl"):
        assert name in picture
    assert "2 in all · 1 past v0.0.0" in picture
    assert "its own: editor" in picture
    assert "1 rostered repository states no family yet" in picture


def test_the_desk_sets_no_name_in_capitals():
    """A name is set as it is written. Mutation: upper-case `label` and this
    fails."""
    picture = cookbook.desk(_desk_document(),
                            {"performing": (2, 1), "instruments": (1, 1), "irl": (1, 0)})
    assert "text-transform" not in picture
    assert ">the sound<" in picture and ">THE SOUND<" not in picture


def test_a_meter_is_lit_by_the_share_past_v0_0_0():
    lit = cookbook._strip(0, 0, 120, 300, "irl", "**matter**", 4, 2)
    dark = cookbook._strip(0, 0, 120, 300, "irl", "**matter**", 4, 0)
    count = lambda parts: sum(1 for p in parts if 'class="c-irl"' in p and "<rect" in p)
    # The cap is one lit rectangle; the rest are the meter's lit segments.
    assert count(dark) == 1
    assert count(lit) > 1


# --- the docs site's family pages -------------------------------------------


def _project(name, governed=False, pictures=(), families=("instruments",)):
    return {"name": name, "url": f"https://github.com/org/{name}", "description": f"{name} does a thing",
            "families": list(families), "governed": governed, "phase": "v0.0.1",
            "version": "v0.0.1" if governed else "v0.0.0",
            "phase_source": "stated", "language": "Python", "archived": False,
            "pictures": [{"url": f"https://github.com/org/{name}/raw/HEAD/{p}", "caption": p}
                         for p in pictures]}


def test_a_site_page_names_its_family_and_where_it_sits():
    page = cookbook.site_page(
        {"name": "instruments", "drives": "the sound — loops", "within": "performing"},
        [state("synth", adopted=True), state("pedal"), state("private-07"), state("planned")],
        also={"pedal": ["irl"]},
        projects={"synth": _project("synth", governed=True, pictures=["a.png"]),
                  "pedal": _project("pedal")})
    assert page.startswith("---\ntitle: instruments\nhide:\n  - toc\n---")
    assert '# the sound<span class="qm-dot">.</span> { .qm-family-title .qm-f-instruments }' in page
    assert "instruments · within [performing](performing.md)\n{ .qm-eyebrow }" in page
    assert "Start in [`synth`](../projects/synth.md)" in page


def test_a_member_with_a_page_is_a_card_that_opens_it():
    """The card's title links the project's page and covers the card; its
    first picture leads it; the other families it is in are links too.

    Mutation: drop `{ .qm-card-link }` from the title link and this fails.
    """
    page = cookbook.site_page(
        {"name": "instruments", "drives": "the sound", "within": None},
        [state("synth", adopted=True), state("pedal")],
        also={"pedal": ["irl"]},
        projects={"synth": _project("synth", governed=True, pictures=["a.png"]),
                  "pedal": _project("pedal")})
    assert "[synth](../projects/synth.md){ .qm-card-link }" in page
    assert "![a.png](https://github.com/org/synth/raw/HEAD/a.png){ .qm-thumb loading=lazy }" in page
    assert "also in [`irl`](irl.md)" in page
    assert '<span class="qm-meta">v0.0.1</span>' in page
    assert "governed" not in page and "not adopted" not in page


def test_a_member_without_a_page_links_its_row_and_a_private_one_is_counted():
    """Every named member is a link: a rostered name the host does not hold
    links its row on the projects page, never a project page that would 404. A
    private repository is counted and never named."""
    page = cookbook.site_page(
        {"name": "games", "drives": "play", "within": None},
        [state("private-38"), state("planned")], projects={})
    assert "projects/planned.md" not in page and "projects/private-38.md" not in page
    assert "[planned](../projects/index.md#planned){ .qm-card-link }" in page
    assert '<span class="qm-meta">not on the host yet</span>' in page
    assert "1 private repository is counted here and not named." in page
    assert "private-38" not in page


def test_a_family_page_names_each_member_once():
    """An outer family shows its own members as cards and each family within
    it as one card naming its members, so nobody's version is said twice.

    Mutation: give every member of the outer family its own card and this
    fails on the count of versions.
    """
    projects = {n: _project(n, governed=n in ("editor", "synth")) for n in ("editor", "synth", "pedal")}
    page = cookbook.site_page(
        {"name": "performing", "drives": "a show", "within": None, "members": ["editor"]},
        [state("editor", adopted=True), state("synth", adopted=True), state("pedal")],
        inner=[{"name": "instruments", "drives": "the sound", "members": 2, "governed": 1,
                "names": ["synth", "pedal", "private-09"]}],
        projects=projects)
    for name in ("editor", "synth", "pedal"):
        assert page.count(f"[{name}](../projects/{name}.md)") == 1, name
    assert page.count('<span class="qm-meta">v0.0.1</span>') == 1
    assert "[the sound](instruments.md){ .qm-card-link }" in page
    assert "[pedal](../projects/pedal.md), and 1 private" in page
    assert "## The families within it" not in page and ".svg" not in page


def test_a_project_page_links_its_repository_and_shows_its_own_pictures():
    page = cookbook.project_page(_project("synth", governed=True, pictures=["a.png", "b.gif"],
                                          families=("instruments", "irl")),
                                 {"instruments": {"within": "performing"}, "irl": {}})
    assert "[synth on GitHub](https://github.com/org/synth){ .md-button .md-button--primary }" in page
    # The first picture opens the page; the rest follow it.
    assert page.count('<figure class="qm-hero-shot" markdown>') == 1
    assert page.count('<figure class="qm-shot" markdown>') == 1
    assert "raw/HEAD/b.gif" in page
    assert ("[instruments](../families/instruments.md) · [irl](../families/irl.md) · within "
            "[performing](../families/performing.md)\n{ .qm-eyebrow }") in page
    assert "[`v0.0.1`](../usage/next-steps.md#the-project-phase-ladder) · Python" in page
    assert "governed" not in page
    assert "## In the estate" not in page


def test_a_project_with_no_pictures_says_so():
    page = cookbook.project_page(_project("plain"), {"instruments": {}})
    assert "No pictures are listed for plain yet." in page
    assert "qm-shot" not in page


def test_a_listed_picture_the_default_branch_does_not_hold_waits(tmp_path):
    """A picture still on a pull request is not a broken image on the site.

    Mutation: ignore `pictures_on_default_branch` in site_projects and this fails.
    """
    import json
    inventory = tmp_path / "inventory.yaml"
    inventory.write_text(json.dumps({"generator": {"org": "org"}, "repositories": [
        {"name": "synth", "private": False, "pictures_on_default_branch": ["a.png"]},
        {"name": "editor", "private": False, "pictures_on_default_branch": []},
    ]}), encoding="utf-8")
    shown = tmp_path / "showcase.yaml"
    shown.write_text("projects:\n"
                     "  synth:\n    - path: a.png\n      caption: A.\n    - path: b.png\n      caption: B.\n"
                     "  editor:\n    - path: c.png\n      caption: C.\n", encoding="utf-8")
    document = {"families": [{"name": "instruments", "members": ["synth", "editor"]}]}
    projects = cookbook.site_projects(document, set(), {}, inventory, shown)
    assert [p["caption"] for p in projects["synth"]["pictures"]] == ["A."]
    assert projects["synth"]["waiting"] == 1
    assert projects["editor"]["pictures"] == [] and projects["editor"]["waiting"] == 1
    page = cookbook.project_page(projects["editor"], {"instruments": {}})
    assert "not yet on its default branch" in page and "c.png" not in page


def test_the_projects_page_is_one_row_per_named_repository(tmp_path):
    """Each row links the project's page and its repository; a name the host
    does not hold carries the anchor family pages link to; a private one is
    counted; a table cell cannot be split by a description.

    Mutation: drop the anchor on a row with no repository and this fails.
    """
    import json
    inventory = tmp_path / "inventory.yaml"
    inventory.write_text(json.dumps({"generator": {"org": "org"}, "repositories": [
        {"name": "synth", "private": False, "description": "loops | layers"},
        {"name": "stray", "private": False},
    ]}), encoding="utf-8")
    document = {"families": [{"name": "instruments", "members": ["synth", "planned", "private-07"]},
                             {"name": "irl", "members": ["synth"]}]}
    projects = cookbook.site_projects(document, set(), {}, inventory, tmp_path / "none.yaml")
    page = cookbook.projects_index(document, projects, {"planned": {"note": "coming soon; later"}}, inventory)
    assert ("| [synth](synth.md) | `v0.0.0` | loops \\| layers | "
            "[instruments](../families/instruments.md), [irl](../families/irl.md) | "
            "[GitHub](https://github.com/org/synth) |") in page
    assert '| <span id="planned"></span>planned | `v0.0.0` | Coming soon. |' in page
    assert "1 private repository is in the families too" in page
    assert "private-07" not in page
    assert "The host holds 1 more public repositories no family claims" in page


def test_only_a_public_repository_on_the_host_gets_a_page(tmp_path):
    """The inventory decides: a private row is a reference, and a name it does
    not list has no repository to link to.

    Mutation: build a page for every claimed member and this fails on `planned`.
    """
    import json
    inventory = tmp_path / "inventory.yaml"
    inventory.write_text(json.dumps({"generator": {"org": "org"}, "repositories": [
        {"name": "synth", "private": False, "description": "a synth"},
        {"ref": "private-07", "private": True},
        {"name": "quiet", "private": False, "description": None},
    ]}), encoding="utf-8")
    shown = tmp_path / "showcase.yaml"
    shown.write_text("projects:\n  synth:\n    - path: a.png\n      caption: A synth.\n",
                     encoding="utf-8")
    document = {"families": [{"name": "instruments", "members": ["synth", "private-07", "planned", "quiet"]}]}
    entries = {"quiet": {"note": "a quiet thing; more notes"}}
    projects = cookbook.site_projects(document, {"synth"}, entries, inventory, shown)
    assert set(projects) == {"synth", "quiet"}
    assert projects["synth"]["url"] == "https://github.com/org/synth"
    assert projects["synth"]["pictures"][0]["url"] == "https://github.com/org/synth/raw/HEAD/a.png"
    assert projects["quiet"]["description"] == "A quiet thing."
    assert projects["synth"]["governed"] and not projects["quiet"]["governed"]


def test_the_showcase_names_only_pages_that_exist_and_says_what_each_picture_shows():
    """Every project the showcase lists has a page, and every picture has a
    path and a caption."""
    import yaml
    root = CI_DIR.parent
    shown = yaml.safe_load((root / "ci" / "showcase.yaml").read_text(encoding="utf-8"))["projects"]
    pages = {p.stem for p in (root / "docs" / "projects").glob("*.md")}
    assert set(shown) <= pages, f"showcase names projects with no page: {set(shown) - pages}"
    for name, pictures in shown.items():
        assert pictures, name
        for picture in pictures:
            assert picture.get("path") and picture.get("caption"), name


def test_a_site_page_invents_no_entry_point():
    page = cookbook.site_page({"name": "f", "drives": "x", "within": None}, [state("one")])
    assert "Every member here is at `v0.0.0`" in page


def test_a_site_page_links_nothing_outside_the_site():
    """Only `docs/` is published, so a relative link to the corpus would 404.
    The record is linked by its address on the host."""
    page = cookbook.site_page({"name": "f", "drives": "x", "within": None}, [state("one")])
    assert "](records/" not in page and "](../../" not in page
    assert cookbook.RECORD_URL in page


def test_the_site_navigation_lists_every_family_page():
    """A generated page the navigation does not list is a page nobody reaches.

    Mutation: drop `families/commons.md` from zensical.toml's nav and this fails.
    """
    import json
    root = CI_DIR.parent
    names = [f["name"] for f in json.loads((root / "families.json").read_text(encoding="utf-8"))["families"]]
    nav = (root / "zensical.toml").read_text(encoding="utf-8")
    missing = [n for n in ["index", *names] if f'"families/{n}.md"' not in nav]
    assert not missing, f"zensical.toml's nav lists no page for {missing}"
    assert '"projects/index.md"' in nav, "zensical.toml's nav lists no projects page"


def test_no_generated_site_page_hides_a_link_inside_raw_html():
    """A link written inside a raw `<p>` is not parsed: the reader sees the
    brackets. Every committed site page keeps its links in markdown.

    Mutation: put the families page's lede back inside `<p class="qm-lede">`
    and regenerate; this fails.
    """
    import re
    docs = CI_DIR.parent / "docs"
    pages = sorted((docs / "families").rglob("*.md")) + sorted((docs / "projects").rglob("*.md"))
    assert pages
    hidden = [f"{p.name}: {line[:60]}" for p in pages
              for line in p.read_text(encoding="utf-8").splitlines()
              if re.match(r"\s*<p[ >]", line) and re.search(r"\]\([^)]+\)", line)]
    assert not hidden, hidden


def test_the_version_says_whether_a_project_has_adopted():
    """`v0.0.0` until a project has its branch, then its stated phase, and
    `v0.0.1` when it states none. The rule is `roster.version_of`, which the
    harness status reads too.

    Mutation: return the stated phase for a project with no branch and this
    fails on the second case.
    """
    assert cookbook.version_of(False, None, None) == "v0.0.0"
    assert cookbook.version_of(False, "v0.0.2", "stated") == "v0.0.0"
    assert cookbook.version_of(True, None, None) == "v0.0.1"
    assert cookbook.version_of(True, "n/a", "n/a") == "v0.0.1"
    assert cookbook.version_of(True, "v0.0.3", "stated") == "v0.0.3"


def test_a_scaffolded_phase_never_moves_the_version():
    """The default is read from the branch, never from the roster's copy of it.

    Mutation: drop the `source == "stated"` test from `roster.version_of` and
    this fails on the first case.
    """
    assert cookbook.version_of(True, "v0.0.0", "scaffolded") == "v0.0.1"
    assert cookbook.version_of(False, "v0.0.1", "scaffolded") == "v0.0.0"
    assert cookbook.version_of(True, "v0.0.2", "scaffolded") == "v0.0.1"


def test_a_phase_stated_without_a_branch_stands_beside_the_version():
    project = {**_project("bench"), "phase": "v0.0.2"}
    page = cookbook.project_page(project, {"instruments": {}})
    assert "[`v0.0.0`](../usage/next-steps.md#the-project-phase-ladder) · `v0.0.2` stated" in page


def test_a_scaffolded_phase_is_not_shown_as_stated():
    """Nobody said it, so a page that printed it as stated would invent a claim.

    Mutation: show any phase that differs from the version, whatever its source,
    and this fails.
    """
    project = {**_project("vox"), "phase": "v0.0.1", "phase_source": "scaffolded"}
    page = cookbook.project_page(project, {"instruments": {}})
    assert "stated" not in page


def test_no_generated_page_says_governed_where_a_version_says_it():
    """The version is the one word a page uses for how far governance reaches:
    no state label, no count of the governed. A repository's own description
    is its own words, and may say what it likes.

    Mutation: put the card's `governed` back and regenerate; this fails.
    """
    import re
    docs = CI_DIR.parent / "docs"
    pages = sorted((docs / "families").rglob("*.md")) + sorted((docs / "projects").rglob("*.md"))
    said = [p.name for p in pages
            if re.search(r">(governed|not adopted)<|\b\d+ governed\b|qm-state",
                         p.read_text(encoding="utf-8"))]
    assert not said, said


def test_a_family_page_opens_with_the_first_picture_its_members_have():
    """The roster's order decides: the family's own members, then those of the
    families within it. A family none of whose members has a picture opens
    with its words alone.

    Mutation: return the copy without the figure in `hero` and this fails.
    """
    projects = {"editor": _project("editor"), "synth": _project("synth", pictures=["a.png"])}
    page = cookbook.site_page(
        {"name": "performing", "drives": "a show", "within": None, "members": ["editor"]},
        [state("editor"), state("synth")], projects=projects)
    assert '<div class="qm-hero" markdown>' in page
    assert "[![a.png](https://github.com/org/synth/raw/HEAD/a.png)](../projects/synth.md)" in page
    assert "<figcaption><strong>synth.</strong> a.png</figcaption>" in page
    plain = cookbook.site_page({"name": "f", "drives": "x", "within": None},
                               [state("one")], projects={"one": _project("one")})
    assert "qm-hero" not in plain


def test_the_front_page_showcase_follows_the_performing_family(tmp_path):
    """The front page opens with the first picture in `performing`, shows the
    parts of a show, then the pictures in the show and those outside it. Every
    link is relative to docs/, where the front page sits.

    Mutation: build the performing grid from every pictured project and this
    fails on `rad`.
    """
    document = {"families": [
        {"name": "performing", "drives": "a show", "within": None, "members": ["editor"],
         "subfamilies": ["instruments"], "all_members": ["editor", "synth", "pedal"]},
        {"name": "instruments", "drives": "the sound — loops", "within": "performing",
         "members": ["synth", "pedal"]},
        {"name": "core", "drives": "the corpus", "within": None, "members": ["rad"]},
    ]}
    by_name = {f["name"]: f for f in document["families"]}
    projects = {
        "editor": _project("editor", families=("performing",)),
        "synth": _project("synth", pictures=["s.png"]),
        "pedal": _project("pedal", pictures=["p.png"]),
        "rad": _project("rad", pictures=["r.png"], families=("core",)),
    }
    snippets = cookbook.showcase_snippets(document, projects, by_name)
    assert set(snippets) == {"showcase-hero.md", "showcase-parts.md",
                             "showcase-performing.md", "showcase-estate.md"}
    assert "](projects/synth.md)" in snippets["showcase-hero.md"]
    assert "[The instruments family →](families/instruments.md){ .qm-card-link }" in snippets["showcase-parts.md"]
    assert "**a show**" in snippets["showcase-parts.md"]
    performing = snippets["showcase-performing.md"]
    assert "[synth](projects/synth.md)" in performing and "[pedal](projects/pedal.md)" in performing
    assert "rad" not in performing and "editor" not in performing
    assert "[rad](projects/rad.md)" in snippets["showcase-estate.md"]
    assert all("](../" not in body for body in snippets.values())
    assert cookbook.showcase_snippets({"families": []}, projects, {}) == {}


def test_the_front_page_includes_every_showcase_snippet_and_each_is_committed():
    """A snippet the front page names but nobody wrote fails the build; one
    written and never included is a section nobody sees."""
    import re
    root = CI_DIR.parent
    front = (root / "docs" / "index.md").read_text(encoding="utf-8")
    included = set(re.findall(r'--8<-- "includes/([^"]+)"', front))
    written = {p.name for p in (root / "includes").glob("showcase-*.md")}
    assert included and included == written, (included, written)


# --- a project's detail page ------------------------------------------------

DETAIL = """\
details:
  editor:
    lede: An editor, in a `browser`.
    try:
      run: ./run dev
      then: Then open `127.0.0.1:8000`.
    picture: {path: hero.png, caption: The editor.}
    steps:
      title: How it goes
      items:
        - {name: Source, text: Bring media.}
        - {name: Render, text: Queue it., picture: {path: render.png, caption: A render queued.}}
    features:
      - eyebrow: on a phone
        title: The same editor on a phone
        text: One stage at a time.
        pictures:
          - {path: phone-a.png, caption: Edit on a phone.}
          - {path: phone-b.png, caption: Render on a phone.}
    built:
      title: A seam and an engine
      text: The seam calls the engine.
      parts:
        - {name: the browser, via: over HTTP, text: Shows frames.}
        - {name: editor, via: the control plane, text: Holds the state.}
        - {name: engine, via: vendored, text: Draws the picture.}
      beside:
        - {name: tooling, text: Calls the API.}
"""
DETAIL_FAMILIES = {"families": [{"name": "performing", "members": ["editor"]},
                                {"name": "core", "members": ["engine"]}]}
ALL = ["hero.png", "render.png", "phone-a.png", "phone-b.png"]
BY_NAME = {"performing": {}, "core": {}}


def _detail_site(tmp_path, held, refs=None, showcase=DETAIL):
    """The projects a site with one detail block builds, `held` being what
    the inventory found on the editor's default branch."""
    import json
    inventory = tmp_path / "inventory.yaml"
    inventory.write_text(json.dumps({"generator": {"org": "org"}, "repositories": [
        {"name": "editor", "private": False, "description": "the host's words",
         "pictures_on_default_branch": held},
        {"name": "engine", "private": False, "description": "an engine"},
    ]}), encoding="utf-8")
    shown = tmp_path / "showcase.yaml"
    shown.write_text(showcase, encoding="utf-8")
    return cookbook.site_projects(DETAIL_FAMILIES, set(), {}, inventory, shown, refs=refs)


def test_a_detail_block_is_a_page_of_its_own_sections(tmp_path):
    """What it is and how to try it beside its picture, the steps, a section per
    feature, and how it is built, each part with a page opening it.

    Mutation: drop the dispatch to `detail_page` in `project_page` and this fails.
    """
    projects = _detail_site(tmp_path, ALL)
    page = cookbook.project_page(projects["editor"], BY_NAME, projects)
    assert "An editor, in a `browser`.\n{ .qm-lede }" in page
    assert "the host's words" not in page
    assert "```sh\n./run dev\n```\n\nThen open `127.0.0.1:8000`." in page
    assert "[![The editor.](https://github.com/org/editor/raw/HEAD/hero.png)]" in page
    assert '<div class="grid qm-parts" markdown>' in page
    assert "**Source**" in page and '<span class="qm-meta">step 2</span>' in page
    assert "<figcaption><strong>Render.</strong> A render queued.</figcaption>" in page
    assert "on a phone\n{ .qm-eyebrow }\n\n## The same editor on a phone" in page
    assert page.count('<figure class="qm-shot" markdown>') == 3
    assert '<div class="card qm-f-core" markdown>\n\n[engine](engine.md){ .qm-card-link }' in page
    assert "**editor**" in page and "[editor](editor.md)" not in page
    assert '<div class="card" markdown>\n\n**the browser**' in page
    assert "beside it\n{ .qm-eyebrow }" in page and "**tooling**" in page
    assert "default branch yet" not in page and "A local preview" not in page
    assert page.count('<section class="qm-section" markdown>') == 3


def test_a_detail_picture_the_default_branch_does_not_hold_waits(tmp_path):
    """A picture still on a pull request is named and not shown: no broken
    image, and no section dropped for the want of one.

    Mutation: mark every picture held in `_resolved` and this fails.
    """
    projects = _detail_site(tmp_path, ["render.png"])
    page = cookbook.project_page(projects["editor"], BY_NAME, projects)
    for missing in ("hero.png", "phone-a.png", "phone-b.png"):
        assert missing not in page, missing
    assert "raw/HEAD/render.png" in page
    assert "*Not on editor's default branch yet:* The editor.\n{ .qm-caption }" in page
    assert "<em>Not on editor's default branch yet.</em> Edit on a phone." in page
    assert "qm-hero" not in page
    assert "## The same editor on a phone" in page


def test_a_branch_that_could_not_be_read_shows_what_the_block_lists(tmp_path):
    """As on a plain page: an unread branch is unknown, not empty."""
    projects = _detail_site(tmp_path, None)
    page = cookbook.project_page(projects["editor"], BY_NAME, projects)
    assert "default branch yet" not in page
    assert all(f"raw/HEAD/{p}" in page for p in ALL)


def test_a_project_without_a_detail_block_keeps_its_page(tmp_path):
    """Only a project a person wrote a block for changes; every other page is
    the one `project_page` makes from its pictures alone.

    Mutation: give every project the first block in `site_projects` and this fails.
    """
    projects = _detail_site(tmp_path, ALL)
    engine = projects["engine"]
    assert "details" not in engine and "details" in projects["editor"]
    assert cookbook.project_page(engine, BY_NAME, projects) == cookbook.project_page(engine, BY_NAME)
    assert "qm-section" not in cookbook.project_page(engine, BY_NAME, projects)


@pytest.mark.parametrize("block, where", [
    ({"lede": "x", "pictrue": {"path": "a.png", "caption": "A."}}, "details.p: block has no key pictrue"),
    ({"features": [{"text": "x"}]}, "details.p.features[0]: feature needs title"),
    ({"picture": {"path": "a.png"}}, "details.p.picture: picture needs caption"),
    ({"steps": {"title": "t", "items": []}}, "details.p.steps: steps needs items"),
    ({"steps": {"title": "t", "items": "Source"}}, "details.p.steps.items: a non-empty list"),
    ({"built": {"title": "t", "parts": [{"name": "n"}]}}, "details.p.built.parts[0]: part needs text"),
    ({"try": {"then": "open it"}}, "details.p.try: try needs run"),
])
def test_a_malformed_detail_block_is_refused_where_it_is_wrong(block, where):
    """A misspelt or incomplete section would vanish from the page without a
    word, so the generator stops and says where.

    Mutation: let `_shaped` ignore unknown keys and the first case fails.
    """
    with pytest.raises(ValueError) as refused:
        cookbook.detail_block(block, "details.p")
    assert str(refused.value).startswith(where), str(refused.value)


def _texts(node) -> list[str]:
    if isinstance(node, str):
        return [node]
    if isinstance(node, dict):
        return [t for key, value in node.items() if key not in ("path", "url") for t in _texts(value)]
    if isinstance(node, list):
        return [t for item in node for t in _texts(item)]
    return []


def test_the_committed_details_load_name_pages_that_exist_and_carry_no_date():
    """Every committed block has the shape, its project has a page, and its
    text is timeless: a date, a pull request number or a measured count
    belongs in the project's changelog, where it is true of one commit.

    Mutation: add "on 23 October 2026" to a block's text and this fails.
    """
    import re
    root = CI_DIR.parent
    blocks = cookbook.details(root / "ci" / "showcase.yaml")
    assert blocks, "the committed showcase has no detail block"
    pages = {p.stem for p in (root / "docs" / "projects").glob("*.md")}
    assert set(blocks) <= pages, set(blocks) - pages
    dated = re.compile(r"\b20\d\d\b|#\d+\b|\b\d+ (?:passed|tests?|commits?|files?)\b")
    for name, block in blocks.items():
        said = [t for t in _texts(block) if dated.search(t)]
        assert not said, (name, said)


def test_the_inventory_asks_about_every_picture_a_detail_block_names():
    """A picture the inventory never asks about is never found held, and its
    page waits for ever.

    Mutation: read only `projects:` in `inventory.showcase_paths` and this fails.
    """
    import inventory
    root = CI_DIR.parent
    asked = inventory.showcase_paths(root / "ci" / "showcase.yaml")
    for name, block in cookbook.details(root / "ci" / "showcase.yaml").items():
        named = [p["path"] for p in cookbook.detail_pictures(block)]
        assert named and set(named) <= set(asked.get(name, [])), name


# --- the preview -------------------------------------------------------------


def test_a_preview_shows_a_ref_s_pictures_and_says_it_is_one(tmp_path):
    """A ref's commit stands in for the default branch, for what it holds and
    no more, and the page says it is a preview.

    Mutation: ignore the ref's `held` in `site_projects` and this fails.
    """
    sha = "a" * 40
    projects = _detail_site(tmp_path, [], refs={
        "editor": {"ref": sha, "label": "feat/x", "held": ["hero.png", "render.png"]}})
    page = cookbook.project_page(projects["editor"], BY_NAME, projects)
    assert f"raw/{sha}/hero.png" in page and f"raw/{sha}/render.png" in page
    assert "phone-a.png" not in page and "raw/HEAD/" not in page
    assert "A local preview: editor's pictures are shown from `feat/x` at `aaaaaaa`." in page
    assert "A local preview" not in cookbook.project_page(projects["engine"], BY_NAME, projects)


def test_a_ref_writes_only_into_a_preview(monkeypatch, capsys):
    """The site's pages are committed, so a ref never reaches them.

    Mutation: drop the refusal in `main` and this fails on the build it reaches.
    """
    monkeypatch.setattr(cookbook, "build", lambda *a, **k: pytest.fail("built a committed page"))
    assert cookbook.main(["docs/families", "--site", "--write", "--ref", "alfred=feat/x"]) == 2
    assert "--preview" in capsys.readouterr().err


def test_a_preview_is_written_beside_the_site_and_reads_its_own_includes(tmp_path):
    """The copy builds alone: its config reads snippets from the copy, so its
    front page shows its own showcase. It replaces an earlier preview, and
    refuses a directory that holds anything else or is the site itself.

    Mutation: drop the check for the preview's mark and the refusal fails.
    """
    where = cookbook.prepare_preview(tmp_path / "preview")
    assert (where / "docs" / "index.md").is_file() and (where / "includes").is_dir()
    config = (where / "zensical.toml").read_text(encoding="utf-8")
    assert f'base_path = ["{where.as_posix()}"]' in config
    assert cookbook.prepare_preview(tmp_path / "preview") == where
    (tmp_path / "other").mkdir()
    (tmp_path / "other" / "notes.md").write_text("mine", encoding="utf-8")
    with pytest.raises(ValueError):
        cookbook.prepare_preview(tmp_path / "other")
    assert (tmp_path / "other" / "notes.md").is_file()
    for own in (cookbook.ROOT, cookbook.ROOT / "docs", cookbook.ROOT / "docs" / "preview"):
        with pytest.raises(ValueError):
            cookbook.prepare_preview(own)


def test_a_ref_the_host_cannot_resolve_is_refused(monkeypatch):
    """A preview of nothing would read as a preview of the branch."""
    import subprocess
    import inventory
    monkeypatch.setattr(cookbook.subprocess, "run", lambda cmd, **kw:
                        subprocess.CompletedProcess(cmd, 1, "", "HTTP 404"))
    monkeypatch.setattr(inventory, "pictures_on_host", lambda *a, **k: pytest.fail("asked"))
    with pytest.raises(ValueError):
        cookbook.preview_refs("org", {"editor": "no/such"}, {"editor": ["a.png"]})


def test_a_resolved_ref_is_read_at_its_commit(monkeypatch):
    """The branch is resolved to one commit, and the pictures are looked for
    in that commit's tree."""
    import subprocess
    import inventory
    sha = "b" * 40
    asked = {}
    monkeypatch.setattr(cookbook.subprocess, "run", lambda cmd, **kw:
                        subprocess.CompletedProcess(cmd, 0, sha + "\n", ""))
    monkeypatch.setattr(inventory, "pictures_on_host",
                        lambda org, wanted, ref="HEAD": asked.update(ref=ref, wanted=wanted)
                        or {n: ["a.png"] for n in wanted})
    found = cookbook.preview_refs("org", {"editor": "feat/x"}, {"editor": ["a.png", "b.png"]})
    assert found == {"editor": {"ref": sha, "label": "feat/x", "held": ["a.png"]}}
    assert asked == {"ref": sha, "wanted": {"editor": ["a.png", "b.png"]}}
