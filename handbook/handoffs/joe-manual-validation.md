# Handoff — joe validated by hand, the open set

**Under test:** joe `main` at `188a2cb`, the open set landed ([`qm-queue.md`](qm-queue.md) §1,
decision 14). Not in it: #59 (joe's API on 1059). Start joe from a checkout of `main`.

**How to record.** Tick a box when what you see is what the step says. When it
is not, leave it unticked and add a row to the findings log at the end: what you
did, what you saw, what the step says. Each finding is fixed on the pull request
that wrote the text or the code, one commit, before that pull request's merge is
asked ([`qm-queue.md`](qm-queue.md) §1, decision 14).

★ marks a step no spec or test drives: the steps worth a person's time first.

---

## 0. Set up

- [ ] The demo worktree is at the stack's top, clean apart from its own `Data/`.
- [ ] joe started from the demo worktree with every part on, `uv run joe dev`, which with
      no `--allow` turns every capability on (API on 8000 in the sum, page on 3000), or a session asked to serve it on free
      ports through `qm instances run`.
- [ ] qmcp, for the voice loop: `QMCP_VOICE_ENGINE_URL=http://127.0.0.1:<joe's port> uv run qmcp serve --converse --runtime local`.
      Without `QMCP_VOICE_ENGINE_URL` it looks for joe on 8000. For 5.1 and 5.2 of the
      voice loop, qmcp started without `--converse`.
- [ ] A microphone and speakers; `uv run joe voice setup` run once (voice loop 1.1).
- [ ] ffmpeg on `PATH`, or `JOE_FFMPEG`, for the server lane's §2.
- [ ] A browser with joe's storage cleared (`joe.layout.v1`, `joe-hint-dismissed`), so
      the first-run state in music page 1.2 is what shows.

## A. The user paths, step by step

Each line is a step of a lane page in `docs/paths/`, with what checks it automatically.

### The music page — `docs/paths/music-page.md`

**1. Start joe and open the page**

- [ ] **1.1** Start joe with every part on, listening on this machine only. -- 1 spec, 3 tests
- [ ] **1.2** The page opens on the visualiser alone, with the first-run hint and the transport below it, and the canvas names no mode yet; p5 and p5.sound load from the CDN past their integrity check. -- 8 specs
- [ ] **1.3** **Joe, go!** starts the browser's audio; until then **Live** is greyed. -- 3 specs
- [ ] **1.4** A joe started with less shows it (`uv run joe dev --allow media`). -- 9 specs, 1 test

**2. Analyse a recording**

- [ ] **2.1** A WAV or MP3 in `Data/Audio/`, and the **Library** (`L`) lists it. -- 2 specs
- [ ] **2.2** **Process** runs the pipeline on it, and its notes are drawn. -- 1 spec, 1 test
- [ ] **2.3** A file the pipeline cannot read says why in the Library. -- 1 spec, 1 test
- [ ] **2.4** **Play** loads it on the transport and plays it, its row highlighted, the playhead following the scrubber. -- 6 specs
- [ ] **2.5** `uv run joe run` from a terminal, then **Results** (`A`) → **Fetch Latest** draws the newest result. Also `joe run NAME` and `joe run --all` (#55, in the sum). -- 4 specs
- [ ] **2.6** An earlier result, with no server: **Results** → **Load JSON**. -- 5 specs, 1 test
- [ ] **2.7** `←` and `→` step through the setlist; the era panel shows genre, title, composer and year. -- 4 specs

**3. Record live**

- [ ] **3.1** **Live records from**: **Browser mic** or **joe's mic**, each named in its tooltip. -- 1 spec, 1 test; no test drives joe's mic
- [ ] ★ **3.2** **Joe, go!**, then **Live**: the dot pulses, the canvas reads LIVE, and the recording lands in the Library. -- nothing automated
- [ ] ★ **3.3** **Library → Process** on the new file analyses it as in 2.2, and **Play** replays it with its notes. -- nothing automated

**4. Arrange the windows**

- [ ] **4.1** ♫ ▤ ¶ in the transport, or `L`, `A`, `T`, open a window beside the visualiser, and the piano roll narrows. -- 8 specs
- [ ] **4.2** A tab's ✕, or `Delete` on a focused tab, closes its window; what it held is there when it opens again. -- 5 specs
- [ ] **4.3** The **Panels** menu (▦) lists every window, says which are closed, and opens the one chosen. -- 3 specs
- [ ] **4.4** The arrangement is kept across a reload; **Panels → Reset layout** puts back the visualiser alone; a saved arrangement the page cannot use is dropped, with a note. -- 8 specs
- [ ] At 900 pixels with a take loaded: known to run the playback group under the window buttons (`qm-queue.md` §4). Look, and say whether it matters. -- nothing automated below 1024

### The voice loop — `docs/paths/voice-loop.md`

**1. Set up the microphone, once**

- [ ] **1.1** `uv run joe voice setup`, talking when it says so: it saves the microphone that heard you. -- 4 tests

**2. Start the conversation**

- [ ] ★ **2.1** joe, and qmcp with `--converse`, started in either order; the conversation waits for the other. -- nothing automated
- [ ] **2.2** qmcp says *"Ready. What should be done?"* and the Voice window opens above the transcript. A Voice window opened from the Panels menu stays and comes back after a reload; one the conversation opened closes when the exchange is over and does not come back. -- 8 specs

**3. Take a turn**

- [ ] **3.1** The Voice window shows each turn as it happens, every state in a label and a colour of its own. -- 5 specs, 1 test
- [ ] ★ **3.2** Say an instruction that names a project -- "Which file in qmcp says what qmcp is?" -- and it is read back. -- nothing automated
- [ ] **3.3** The take is written as it is spoken; a struck word crossed out; a segment still being read marked. -- 3 specs
- [ ] **3.4** Answering without speaking: numbered option buttons, `1`–`9`, `R` again, `Shift`+`Esc` stops, `~` held keeps the turn open. -- 8 specs
- [ ] ★ **3.5** The answer said back, then *"Anything else?"*: "yes", "no", "stop listening". -- nothing automated

**4. Read back what was heard**

- [ ] **4.1** `T` opens the whole exchange, oldest first, with strikes, confidence and labels, following the newest line. -- 7 specs, 1 test
- [ ] **4.2** Empty takes fold; a long question shows three lines until opened; each day is named where it changes. -- 4 specs
- [ ] **4.3** **What can be said** lists the conversation's words, its checks' and joe's own. -- 2 specs
- [ ] **4.4** **Show** on a heard take: its recording on the transport, its words on the piano roll, the lit word following playback and scrubbing, a clipped word whole under the pointer, "recording not kept" for one without its file. Tested by hand once for #33. -- 9 specs, 2 tests

**5. Instruct by voice, and answer qmcp's queue**

- [ ] **5.1** With qmcp without `--converse`, **Instruct by voice** takes one instruction into qmcp's inbox and shows what was recorded. -- 8 specs
- [ ] **5.2** qmcp's oldest waiting request is offered with its options, and **Answer by voice** answers it. -- 6 specs
- [ ] **5.3** With qmcp stopped, **Instruct by voice** is dimmed and its tooltip says how to start it. -- 2 specs

### joe as a server — `docs/paths/server.md`

**1. Start joe as a server**

- [ ] **1.1** `uv run joe backend` serves the media API alone on `127.0.0.1`, and says as it starts that it has no authentication and what is on. -- 5 tests
- [ ] **1.2** `GET /api/health` says which capabilities are on; a route whose capability is off answers why. -- 6 tests

**2. Caption and analyse a video for an editor**

- [ ] ★ A real clip end to end, as alfred would: upload, words with times, beats, loudness, silences, waveform, delete. -- each route has tests, the whole run none
- [ ] **2.1** ffmpeg on `PATH` or in `JOE_FFMPEG`; the API started alone. -- 1 test
- [ ] **2.2** Upload, then ask by the answer's `media_id`. -- 3 tests
- [ ] **2.3** Words with their times, and what the sound does. -- 4 tests
- [ ] **2.4** Delete it, or it goes an hour after its last use (`JOE_MEDIA_TTL`). -- 2 tests

**3. Put a recording in the library and run the pipeline**

- [ ] **3** Upload with `curl`, run the pipeline on it, read `GET /api/results/latest`. -- 6 tests; no test reads `/api/results/latest`

**4. Hear and transcribe for a voice tool**

- [ ] **4.1** `POST /api/voice/listen` records a take from joe's microphone and answers what was heard. -- 4 tests
- [ ] ★ **4.2** `POST /api/voice/transcribe?filename=` transcribes a file by name, `Data/Voice/` before `Data/Audio/`. -- 2 tests, neither calling the route
- [ ] **4.3** Another program posts its states to `POST /api/voice/conversation`, and the page reads them. -- 4 tests

## B. The docs, page by page

For each: every command runs as written; every claim matches what A showed;
every address is joe's in the build under test (8000 in the sum, 1059 once #59
lands); every link opens. Known and recorded already, so not new findings:
#38's `docs/api.md` Host list, open routes and POST-not-DELETE, and
`contributing.md`'s "started as `backend`"; #46's 'select "Browser"'; #50's
`audio` relative to `Data/Voice/`.

- [ ] `README.md` -- the onramp: setup with uv, the commands table, the keys, the page.
- [ ] `docs/ui.md` -- the window, each window by its registry id, the transport, what the window does not have.
- [ ] `docs/api.md` -- every route, its capability, its refusals; the datapoints.
- [ ] `docs/media.md` -- the media API: running it, reaching it from Docker, every refusal.
- [ ] `docs/security.md` -- the threat model and every route's exposure.
- [ ] `docs/modules.md` -- Audio, Chroma, MIDI, Voice: what each does.
- [ ] `docs/contributing.md` -- setup, the checks before a PR, the CI that runs, troubleshooting.
- [ ] `docs/paths/README.md` and the three lane pages -- read as a newcomer: could you follow each lane without this checklist?

## C. The tests

- [ ] `npm run check:paths`: every spec is a step of one lane page, once.
- [ ] `npx playwright test`: every spec passes on the specs' own servers.
- [ ] `uv run pytest tests/`: every test passes, the `local` check among them once #60 is in.
- [ ] Spot-check one spec per lane section: does it fail if the step's behaviour breaks? (Every new check in #51 to #60 was seen red; `main`'s were audited on 2026-10-25.)
- [ ] The ★ steps above: does any deserve a spec or test now, rather than a person each time?
- [ ] Untested, recorded in `qm-queue.md` §5: `GET /api/results/latest`; `POST /api/voice/transcribe` over HTTP; `capture.AudioCapture`; a live recording; `LABEL_W` in three files.

## Findings

| # | Where (lane step, doc, test) | Did | Saw | The step says | Owning PR | State |
|---|---|---|---|---|---|---|
| 1 | Music page 2.5, `docs/paths/music-page.md:105` | Read it against `cli.py`, `main.py` and the README in the sum | `uv run joe run` with no names analyses the newest recording; `NAME...` those named; `--all` every one (#55) | "`uv run joe run` analyses every file in `Data/Audio/`" | #52 (3ee6003, only on `docs/user-paths`) | Fixed on #52, 57b86ae |
| 2 | | | | | | |
