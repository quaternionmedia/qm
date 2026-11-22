# Project refresh — 2026-11-21, qmetronome

**Protocol** `protocols/project-refresh.md`, read with one question added:
what a version tag pushed at this commit would meet. `qm` at `e31fb04`;
`project/qmetronome` at `348e31f`; `qmetronome` at `39c1beb`.

| | |
|---|---|
| **Operator** | Peter Kagstrom |
| **Machine** | Windows 11, the JDK Android Studio bundles, Android SDK platform 35 |
| **Tools** | Claude Fable 5.2 |

Everything below was true at the commits named.

---

## 1. What was behind

`uv run qm project qmetronome`, before any change, at `qm` `d59fbff` and
`qmetronome` `c5e480b`: 2 behind, 0 unknown. `project/qmetronome` lacked
`main`, and `governance/qm` pinned a commit behind the branch tip. Every seed
workflow, `AGENTS.md` and `CLAUDE.md` read current, and no pull request was
open on either side.

## 2. The corpus side

quaternionmedia/qm#339, merged as `348e31f` with a merge commit. The merge of
`main` was clean, and the two seed copies in `adr/` already matched the seed.

## 3. The project's side

quaternionmedia/qmetronome#22, merged as `3aaaa28`: one gitlink,
`governance/qm` to `348e31f`. Nothing the project copies from the seed moved
with that step, so there was no second pull request.

## 4. The tests

`./gradlew assembleDebug testDebugUnitTest --console=plain`.

- At `c5e480b`: one run red, on `MidiClockSenderTest`'s organic-mode tick
  case, with a `ConcurrentModificationException` where the test counts the
  bytes its fake destination received. The class run alone passed.
- The cause is in the test. It collected the bytes in a plain list, the sender
  delivers on its own thread, and the count runs on the test's thread while
  ticks still arrive. A probe case that counts in a loop for three seconds at
  300 BPM was red with the plain list and green with a copy-on-write list. The
  probe is not committed.
- quaternionmedia/qmetronome#23, merged as `39c1beb`, makes the list
  copy-on-write. At its head `7483872`: `BUILD SUCCESSFUL`, 322 passed. `git
  diff 7483872 39c1beb` is empty, so that run is a run of `39c1beb`'s tree.

Each run rewrote the three GIFs under `docs/images/generated/videos/`; they
were restored and are in no pull request above.

## 5. The policies

`run_workflows_locally.py --event pull_request --base-ref main` in qmetronome
at `7483872`, with `JAVA_HOME` and `ANDROID_HOME` set. Without them the build
step fails for want of a JDK, which is the environment and not the project.

17 steps ran and 17 passed. Three workflows were skipped as not triggered by a
pull request: `alpha-release.yml`, `release.yml` and `tag-claims.yml`.

On the host, every check on #23 concluded `SUCCESS`, `build-and-test` and
`reuse-lint` among them.

Read by hand for the commits and pull requests of this run: no `-c` passed to
git, nothing pushed to a shared branch outside a pull request, and no commit
carrying a co-author trailer.

## 6. The second reading

`uv run qm project qmetronome`, at `qm` `e31fb04` and `qmetronome` `39c1beb`:
1 behind, 0 unknown. Every line on the project's side and on the host is
current. `project/qmetronome` lacks the commits `main` gained after #339, a
queue page and a perspective, none of them under `project-seed/`.

## 7. What a version tag would meet

Read from the repository, its workflows and the host. Nothing was tagged.

**In place.**

- The repository is public and the host reads its licence as GPL-3.0.
  `REUSE.toml` and the texts under `LICENSES/` satisfy the REUSE lint.
- No keystore, key or credentials file is tracked at `39c1beb`, and `git log
  --all --diff-filter=A --name-only` names none in any commit.
- `PRIVACY.md` names every permission `AndroidManifest.xml` declares.

**The two tracks.** A `v0.*` tag runs `alpha-release.yml`, which builds a debug
APK and reads no secret. Any later major runs `release.yml`, which signs with
four repository secrets.

**What stands in the way of either.**

- `uv run qm tags --repo quaternionmedia/qmetronome` fails every existing `v*`
  tag: no annotation carries `Reviewed-by:`, `Manually-tested:`,
  `Automated-gate:` or `Not-covered:`. `tag-claims.yml` runs on every `v*` tag
  push, so a tag without those lines goes red there.
- `MetronomeEngineTest` drives the engine on real threads against the wall
  clock. The body of the pull request merged as `a591c00` measures it red on
  the host intermittently, each failed run passing when run again, so a red
  `build-and-test` on a tag push is not by itself a finding about the tag.
- `CHANGELOG.md` has no entry above `v0.1.3`. `v0.2.0` is tagged and released,
  and `main` is 34 commits past it.
- Issue 12, hardware volume buttons not changing the volume, is open. Its fix
  is reverted at `a591c00`.

**What stands in the way of the signed track only.**

- `gh secret list --repo quaternionmedia/qmetronome` prints nothing. The
  organisation's secrets were not readable with the token used, so whether the
  four exist there is not established.
- `docs/publication_checklist.md`, *Final Manual Verification*: no item is
  checked, and each names a device in the hand.
- `docs/app-store-checklist.md`: the listing's privacy policy URL, icon export,
  feature graphic, screenshots, descriptions, data-safety form, the
  foreground-service declaration and the Glyph Matrix SDK's redistribution
  terms are all open.

**Pages that disagree with the tree.**

- `docs/publication_checklist.md`'s *Permissions* item says every permission
  but the Glyph Matrix SDK's is merged in by a dependency. The manifest
  declares `FOREGROUND_SERVICE`, `FOREGROUND_SERVICE_SPECIAL_USE`,
  `POST_NOTIFICATIONS` and `REQUEST_IGNORE_BATTERY_OPTIMIZATIONS` itself.
- `PRIVACY.md` is dated 2026-07-06 and was last changed on 2026-11-20.

## Left open

- **`project/qmetronome` is one propagation behind `main`.** Nothing in the
  difference reaches the project, and this record lands on `main` after it, so
  the next refresh takes both.
- **`main` in qmetronome has no branch protection and no ruleset.** The
  checklist's *Repository Governance* section holds the item, and applying one
  is a person's act on the host.
- **Two remote branches besides `main`.** `timing/first-beat-precision` has
  nothing `main` lacks. `copilot/research-hardware-button-bug-and-animation-enhance`
  is two commits ahead and was not read.
- **`MidiActionSenderTest`** collects into a plain list from a sender on a
  background dispatcher, as `MidiClockSenderTest` did. It was not seen to fail
  and is not changed.
- **`uv run qm docs generate`** was not run.
- **Tag claims, the alpha build and the signed build** were not exercised: each
  runs on a tag push.
