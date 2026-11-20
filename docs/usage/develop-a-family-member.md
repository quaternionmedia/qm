# Develop a family member

Change one member of the performing family, see the change in the running
family, and [gate](../ref/glossary.md#gate){ .glossary-term } it before you commit. `uv run qm family-demo` runs the family,
and `ci/family-demo.yaml` says what each member reloads by itself.

## Once

Each core member is a git worktree at `<work>\dev\<member>`, where `<work>` is
the directory you hand `--work`. Keep `<work>` short: joe's native modules stop
loading once their paths grow past what the Windows loader takes.

## The loop

```bash
uv run qm family-demo --dev --work <work> --port-offset 100
```

Every core member runs from its worktree as it stands, installed in place only
when its lock files changed, with the show on the stage and the family held
until Ctrl+C. `--port-offset 100` moves every port past the roster's own range,
so the [loop](../ref/glossary.md#loop){ .glossary-term } runs beside an integration family. The stage's address is printed;
open it.

| Member | Edit | Reloads by itself | Restarted when this changes | Its suite, in its worktree |
|---|---|---|---|---|
| ShowRunner | `src/showrunner/` | nothing | `src/**/*.py` | `uv run pytest` |
| ShowStopper | [`stopwatch.py`](https://github.com/quaternionmedia/ShowStopper), [`stopwatch.tcss`](https://github.com/quaternionmedia/ShowStopper), [`family.py`](https://github.com/quaternionmedia/ShowStopper) | the stopwatch: a new app per view, and the stage reloads its frame | [`family.py`](https://github.com/quaternionmedia/ShowStopper), [`showstopper_cli.py`](https://github.com/quaternionmedia/ShowStopper) | `uv run pytest tests walkthrough --doctest-glob=*.md` |
| carlos | `templates/`, `static/`, `src/` | the rack: read per request, and the stage reloads its frame | `src/**/*.py`, `tools/*.py` | `uv run carlos check` |
| joe | `src/` (the page), `*.py` and `Modules/` (the API) | the page, through Vite's HMR | `*.py`, `Modules/**/*.py`: the API, and Vite with it | `uv run pytest tests walkthrough --doctest-glob=*.md` |
| leo | `src/` | all of it, through Vite's HMR | `leo/*.py` | `uv run pytest tests walkthrough --doctest-glob=*.md` |

A restart stops the member and starts it again with the same command line, the
same ports and the same state directory, so the hub keeps its family links and
every link to the member still reaches it. When it is back, the stage reloads
its frame. The Python servers are restarted by `qm family-demo` rather than
by uvicorn's reloader: the roster's `THE DEV LOOP` comment says why.

**Restart one member alone:** its panel's **Restart** button, or

```bash
curl -X POST http://127.0.0.1:<stage port>/restart/<member>
```

The rest of the family stays up. The answer says how the member came back.

## Before you commit

1. The member's suite, from its worktree: the last column above.
2. Both forms of the family, with your working tree in it:

    ```bash
    uv run qm family-demo --src <member>=<work>\dev\<member> --work <work>\g --port-offset 100
    uv run qm family-demo --stage --src <member>=<work>\dev\<member> --work <work>\g --port-offset 100
    ```

    The first runs every member's own check, alone and then together; the
    second plays the show. The other members are cloned at their branches, so
    the gate gets a work directory of its own: beside a running integration
    family, the two would share `<work>\c`. A dev source's checkout is reported
    as `dev source` rather than compared, because you are editing it.

3. Commit. The integration family, `uv run qm family-demo --stage --work <work>`,
   runs the branches as committed.

## Not automated

- A page opened on a member directly, outside the stage: reload it yourself,
  except leo's and joe's, which Vite updates.
- joe's panel is the stage's own session of joe's page, pictured after each
  take; an edit to the page shows there at the next take.
- A restart drops what the member holds in memory, such as ShowStopper's clock
  and the last cue a member was sent: fire the cue again.
- A changed lock file is installed by the next run, not by a restart.
- ShowStopper's install writes an untracked `uv.lock`, because it carries a pdm
  lock: leave it out of your commits.
- `--dev` runs no member's own check; the gate's first form does.
- Committing, and the integration run on the committed branches.
