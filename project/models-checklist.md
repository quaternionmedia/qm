# The models checklist: image models through qmcp, by hand

`tests/test_vision_through_qmcp.py` holds every path below against the
simulated qmcp, and `tests/e2e/test_models_window.py` the window's own: opened,
a shape asked about, a person's word, a model switched off and kept so, written
as walkthrough pages [35](../../../walkthrough/35-the-models-window.md) and
[36](../../../walkthrough/36-the-models-window-narrow-and-wide.md). This is how a person
confirms the same paths in the viewer and at the command line, and that each one
reads well. The plan is
[image models through qmcp](plans/image-models-through-qmcp-2026-10-30.md).

Every model here is the **simulated qmcp** (`apothecary/finders/simulated.py`):
it answers in process, works its answers plainly from the pixels, and is named
*simulated* wherever it is shown. A real qmcp is reached over MCP once qmcp's
own server speaks it (the plan's qmcp slice 2); until then an address on this
machine says so, and apothecary reads without it.

Tick each box as it passes. When one fails, note what the Models window and the
status bar said, word for word.

## Setting up

- [ ] `uv run apothecary serve --simulated` (`--port` for a port of its own), and
      open the viewer. It runs with the simulated qmcp unless
      `APOTHECARY_QMCP` names another.
- [ ] A picture with a few things of plain colours on a light ground, a black
      disc among them (a lens cap, a puck): a photograph of the bench, or a
      drawn one. **Pictures › Add** keeps it, and the ring's **Picture ›
      Folder** pins it at the workbench.
- [ ] The ring's **Picture › Find shapes** finds its shapes, and each sits on
      the picture's mat at the workbench.

## qmcp, and its models

- [ ] **⊞ Windows › Models**, or the ring's **Panels › Pictures › Models ›
      Models**, opens a window of its own beside the world, the height of the
      page, with the world still in view. Its first line has a green dot and
      says *the simulated qmcp is answering: simulated-vlm 0*, with a sentence
      under it saying checking a model is not built, so none is trusted.
- [ ] **Origins** lists `plain/colour`, the plain reader, and
      `qmcp/simulated-vlm@0`, which says what it answers and *not checked*.
      Each has its switch, ticked.
- [ ] Opening Models asked qmcp what it has, and nothing about any picture:
      the server's log shows `GET /vision` and no `ask`.

## Asking about a shape

- [ ] With no shape chosen, Ask about a shape says *Choose a shape on a
      picture's mat to ask about it*, and offers no button. The ring's
      **Panels › Pictures › Models › Ask** says *choose a shape on a picture's
      mat first* in the status bar.
- [ ] Click a shape on the mat. Selected names it, and under it says
      *⊞ Windows › Models asks a model about it*. Models names the same shape,
      its word, the picture and where it lies, with one button, **Ask**, whose
      tooltip says what it reads and asks, and among which words.
- [ ] **Ask** on a shape of one plain colour: the line under it says *the
      simulated qmcp answered 2 of 3*. The table has a row for colour, material
      and label.
  - [ ] **colour:** *Read* (off its pixels) has a swatch, the colour's word
        and its sRGB; *Guessed* has the model's word, how sure it says it is,
        *not checked*, and *agrees* in green; hovering it names the model.
  - [ ] **material:** a guess among plastic, metal, wood, rubber, fabric,
        glass, paper and ceramic, *not checked*.
  - [ ] **label:** *unread: the model answered 'block'* (or *'bar'*)
        *, which is outside the words asked among*. A word outside the list
        is shown, and used for nothing.
- [ ] Narrow the window, or open it on a page 1024 px wide: the table reads
      down, each property and then *Read*, *Guessed* and *A person* each on
      a line of its own, named, with nothing reached by a scroll across.
      Widened, it is a table again.
- [ ] **Ask** on the black disc: the reading says *black*, and the guess
      names another colour and says *disagrees* in red; the reading stays as
      read. The plain reader takes the median of the disc's box, which is the
      disc's; the simulated model takes the mean, which the light ground in
      the box's corners draws lighter.
- [ ] Choose another shape: Models follows it, with that shape's own rows.
      Choose the first again: what was asked about it is still there.
- [ ] The ring's **Panels › Pictures › Models › Ask** does the same as the
      button, on the shape chosen.

## A person's word

- [ ] In material's *A person* box, pick a word from its list (or type one)
      and press Enter: *A person* shows the word, and the guess is struck
      through, *overruled by a person*. The status bar says *a person says its
      material is …*.
- [ ] The ring's **Panels › Pictures › Models › Colour ›** a word does the
      same for colour, without the keyboard: black, white, grey, red, yellow,
      green and blue a cell each, orange, purple, pink and brown under
      **More**.
- [ ] In label's box, type a word and press Enter: the same, with no list;
      the model's unread label is struck through too, *overruled by a person*.
- [ ] A colour outside the basic colour words (*teal*) is refused, and says
      *a colour is one of black, white, grey, …*.
- [ ] With no model asked at all, a person's word on material is still taken.

## Switching an origin off

- [ ] Untick `qmcp/simulated-vlm@0`. Each row's guess goes, and the row says
      *1 guess not shown: switched off*; the reading and the person's word stay.
- [ ] **Ask** again: the line says *every model is switched off: qmcp was not
      asked*.
- [ ] Untick `plain/colour` and **Ask**: the line says *plain/colour is
      switched off*, and the colour row reads nothing.
- [ ] Tick both again, reload the page: both stay ticked (the switches are kept
      in the state folder), and Models is open again where it was, the world as
      wide as it was.
- [ ] With that server's state folder (`APOTHECARY_STATE_DIR=.cache/simulated/state`),
      `uv run apothecary vision off plain/colour` and `vision on plain/colour`
      switch the same origin, and Models shows it the next time it is shown.

## Each way qmcp can be missing

Stop the server and serve `--simulated` again with `APOTHECARY_QMCP` set as each
row says (it starts afresh: pin the picture and find its shapes again).
Each time, Models' first line says which, a colour is still read off the
pixels, and nothing else in the viewer changes.

- [ ] `APOTHECARY_QMCP=off`: a grey dot, *qmcp is not configured
      (APOTHECARY_QMCP)*, and a note that apothecary reads without it. Only
      `plain/colour` is listed, and the button reads **Read its colour**, its
      tooltip saying there is no model to ask.
- [ ] `APOTHECARY_QMCP=simulated:down`: an amber dot, *the simulated qmcp
      (down) is not answering (connection refused)*, and the same button.
      **Read its colour** says *… is not answering (connection refused): no
      model answered*, and the colour is read.
- [ ] `APOTHECARY_QMCP=simulated:empty`: *the simulated qmcp (empty) is
      answering, with no model*. **Read its colour** reads the colour; the
      guesses are *unread: no model that answers … is loaded*.
- [ ] `APOTHECARY_QMCP=simulated:slow`: **Ask** greys and the line says *asking
      about shape …* for a few seconds, then *did not answer within 4 s: the
      call was given up*; each guess is *unread: the deadline passed*, and the
      colour is read off the pixels all the same. The rest of the viewer
      answers while it waits.
- [ ] `APOTHECARY_QMCP=simulated:broken`: **Ask** says *the simulated qmcp
      (broken) answered, and the answer was refused, so nothing from it is
      kept: the answer's observations are not a list*; no guess is shown.
- [ ] `APOTHECARY_QMCP=http://localhost/mcp`: *the qmcp extra is not
      installed*: nothing is asked.
- [ ] `APOTHECARY_QMCP=http://192.0.2.7/mcp`: *it is not on this machine:
      personal data stays on the device*: nothing is sent.

## At the command line

- [ ] `uv run apothecary vision status --qmcp simulated` says what qmcp has,
      each model *not checked*, and what is switched off.
- [ ] `uv run apothecary vision ask <picture> --box 0.1,0.2,0.4,0.8 --qmcp
      simulated` prints the plain reader's `rgb` and colour, then each guess
      with its origin, how sure, and *not checked*; a label outside
      `--label`'s words is unread, with the word.
- [ ] The same with `--qmcp simulated:slow` returns after the deadline, saying
      so, and does not hang.
- [ ] `--json` prints one observation a line, each with
      `"contract": "qm.observation"`.

## What this does not cover yet

- A real qmcp, over MCP: it waits on qmcp's own server speaking MCP.
- Trust: checking a model is not built
  ([the plan](plans/image-models-through-qmcp-2026-10-30.md#how-each-is-measured-before-anything-trusts-it)),
  so every guess is *not checked* and used for nothing.
- The `qmcp` finder in **Picture › Find shapes**, and asking about a rig's face.
- A site's own words mapped onto the colour and material lists.
- Keeping what was asked: it lasts as long as the server, and a restart forgets
  it. The switches are kept.
