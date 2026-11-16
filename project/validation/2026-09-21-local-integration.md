# Local integration run-through: the new features, by topic

*A handoff for a person at the bench with `review/2026-09-26` (the design
review, on top of `consolidate/2026-09-19`) checked out. It walks every capability the branch added
since the printer seam landed -- the guard that keeps personal data here, the
geometry brought in from elsewhere, the bench drawn as it is, the rail and
the machine popup, the camera, the printer with and without hardware, the
docs site -- as a checklist you tick as you go. Nothing here needs the
network; everything needs this machine.*

## How to walk it

Two terminals and a browser. Terminal **A** runs a server; terminal **B**
runs the commands in the boxes. Every step is a `- [ ]` line with the action,
then **→** what you should see. Tick what holds; where it does not, write
what you saw under the section in the *Results* table at the end, with the
time, the port and the command -- the convention of
[`2026-09-20-ender-bench.md`](2026-09-20-ender-bench.md), whose latch-side
checklist is the hardware half of section 6 and is not repeated here.

Two servers, on purpose:

- **Your own** (`uv run apothecary serve --reload`, port 8000): your real
  `~/.apothecary` (pins, readings, cameras), your real ports, and your own
  picture folder (the folder you start it in). Sections 2, 3, 4, 7 use it.
- **A demo one** (port 8001): temporary state, the scripted `arduino-cli`
  and the simulated printer, so nothing you do to it touches your pins or
  your board. Sections 5 and 6 use it. Section 6's hardware half uses your
  own server and the bench record's checklist.

Read the page for a topic before its section if you want the why:
[`../geometry-from-elsewhere.md`](../../../../docs/geometry-from-elsewhere.md),
[`../firmware.md`](../../../../docs/firmware.md), the one-screen plan, and the
stays-on-the-device record in `governance/qm/adr/`.

## 0. What the design review changed that you will notice

- [ ] `uv run apothecary render --scene-file examples/scene.json -o /tmp/s.scad`
      → a cube in `/tmp/s.scad` (it raised NotImplementedError before); an
      object without a `type` is refused, not guessed.
- [ ] `uv run pytest` → the unit suite and the walkthrough in well under a
      minute; browser tests skip with a reason unless `--start-server`.
- [ ] `uv run apothecary serve` starts only the server: the docs refresh is
      `--refresh-docs` now.
- [ ] `apothecary system`, `install`, `testrun`, `dev`, `inventory`,
      `submodules` answer with what replaced them and exit 1.
- [ ] Eight parts no longer show sliders OpenSCAD ignored; `apothecary parts
      generate-stl dryerknob -p knob_diameter=60` is refused by name.
- [ ] `apothecary census` is a report; a new button raises one ceiling in
      `tests/test_census.py`, nothing else.
- [ ] **Hardware, before relying on it:** printer ports are opened exclusively
      now. Run the open, identify and poll steps of
      [`2026-09-20-ender-bench.md`](2026-09-20-ender-bench.md) against the Ender.

## 1. Setup

```bash
cd <clone>                          # the folder apothecary is checked out in
git status -sb                      # ## review/2026-09-26
git submodule status                # governance/qm at 20e00bd (the pin), or the adr/ branch if you were drafting
uv sync
uv run apothecary check             # OpenSCAD and each part's, the slicer, the firmware toolchains, the parts
```

- [ ] `apothecary check` → OpenSCAD found, every part with a wrapper or a
      sidecar; it exits 1 if a required package is missing.
- [ ] Terminal A: `uv run apothecary serve --reload` → *Application startup
      complete*; STLs for parts that lack one are
      generated in the background -- expect `ender3.stl` and the five
      boards' STLs to appear under `parts/` within a minute. (A node asked
      for before its parts are built builds them first: a fresh clone
      answers `/sites/garage/nodes/printer_1/stl` on the first request.)
- [ ] Browser: `http://127.0.0.1:8000/viewer/sites/garage` → the garage, its
      walls faded, the workbench, one printer that looks like an Ender 3
      (spool over the top bar, power supply on the right) at the bench's left
      end, boards at its right end.
- [ ] `http://127.0.0.1:8000/docs` → the docs index, with a bar that says when
      the generated walkthroughs were last refreshed (`--refresh-docs` or
      `apothecary docs generate` refreshes them).

## 2. Personal data stays on the device

The guard is the program's shape, not a setting: there is nothing to turn
on. Each check below is a door the record names; each should be shut.

```bash
# the process cannot reach past this machine, whichever way it is asked
# (apothecary.api is an install point; the geometry library alone installs nothing)
uv run python -c "import apothecary.api, socket; socket.create_connection(('example.com', 80))"
uv run python -c "import apothecary.api, socket; socket.getaddrinfo('example.com', 443)"
uv run python -c "import apothecary.api, socket; s=socket.socket(); s.bind(('0.0.0.0', 0))"
uv run python -c "import apothecary.api, socket; s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM); s.sendto(b'x', ('127.0.0.53', 53))"
```

- [ ] Each of the four → `LeftTheMachine: ... refused to reach ...` naming
      the record. (The last is the resolver's stub on loopback: loopback is
      not this machine when a service there forwards.)
- [ ] `uv run apothecary serve --host 0.0.0.0 --port 8002` → refused before
      binding: *Apothecary listens on this machine only*.
- [ ] `uv run python -m uvicorn apothecary.api:app --host 0.0.0.0 --port 8002`
      → refused at the socket (`_socket.bind: refused`), not by the CLI.

```bash
# the server answers this machine only: client, bound address, Host, sender
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8000/placed                         # 200
curl -s -o /dev/null -w "%{http_code}\n" -H "Host: evil.example" http://127.0.0.1:8000/placed   # 403
curl -s -o /dev/null -w "%{http_code}\n" -H "Host: $(hostname)" http://127.0.0.1:8000/placed    # 403
curl -s -o /dev/null -w "%{http_code}\n" -X POST -H "Origin: https://evil.example" -H "Sec-Fetch-Site: cross-site" -H "Content-Type: application/json" -d '{}' http://127.0.0.1:8000/photos/gather   # 403
curl -s -o /dev/null -w "%{http_code}\n" -H "Sec-Fetch-Site: cross-site" -H "Sec-Fetch-Mode: navigate" http://127.0.0.1:8000/viewer/sites/garage   # 200: a link from elsewhere still opens a page
curl -sI http://127.0.0.1:8000/viewer/sites/garage | grep -i "content-security-policy\|referrer-policy"
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8000/api/docs                      # 404: Swagger is off
```

- [ ] The codes as commented; the CSP header lists `'self'` everywhere and no
      `http:`/`https:` host; `referrer-policy: no-referrer`.
- [ ] From a LAN machine (or `curl --interface <lan-ip>` here):
      `http://<this-machine's-lan-ip>:8000/` → connection refused (nothing
      listens there).
- [ ] `cat ~/.apothecary/tools/arduino-cli.yaml` → `skip_board_detection_calls:
      true`, `enable_notification: false`, the three package indexes. Every
      arduino-cli the seam runs is given this file; your own
      `~/.arduino15/arduino-cli.yaml` is not read under apothecary.
- [ ] `HTTPS_PROXY=http://10.0.0.1:3128 uv run apothecary firmware boards` →
      the same answer as without it: the child's environment carries no proxy
      and no `ARDUINO_*` override.
- [ ] Optional, with `strace`: `strace -f -e trace=network -o /tmp/scan.log
      uv run apothecary firmware boards`, then `grep -v "AF_UNIX\|127.0.0"
      /tmp/scan.log | grep connect` → nothing but the mDNS question to
      `224.0.0.251`/`ff02::fb` (named in the record, carries nothing of yours).
- [ ] `APOTHECARY_PICTURE_ROOT=$HOME uv run apothecary serve --port 8003`, then `curl -s http://127.0.0.1:8003/photos/pictures`
      → a 500 whose text says the folder *holds everything of yours, not a
      folder of pictures*. Stop it. (Same for
      `APOTHECARY_PICTURE_ROOT=~/.apothecary`.)
- [ ] `ls -ld ~/.apothecary` → `drwx------` once anything has been saved
      there on this tip (a pin, a reading: the folder is made the account's
      alone on every write); so is `captures/` under any picture root, once a
      frame is kept.
- [ ] `uv run pytest tests/test_stays_local.py` → every test passes
      (`uv run pytest --co -q tests/test_stays_local.py` says how many). This
      file is the review: loosening any door is an edit here and to the record.

## 3. Geometry from elsewhere, and the bench drawn as it is

On your own server, in the garage.

- [ ] Zoom the camera (scroll) onto the bench: an **Ender 3** at its left
      end -- the 2040 frame, the bed on springs, the X gantry, the **power
      supply on the right side behind the upright**, the LCD off the
      front-right corner, the **spool on the bracket over the top bar**. Its
      cyan build-volume box sits on the bed at 95 mm, not on the bench, and
      inside the frame (not centred on the footprint, which the PSU skews).
- [ ] At the bench's right end: an ESP32 devkit standing on its pins, the
      footpedal, an **Arduino Uno** (teal, USB-B and jack on its left), a
      **Raspberry Pi 4** (green, the USB stacks and Ethernet on its right), a
      **Teensy 4.0** (small, on its pins). Site's tree lists the garage's
      structures, `printer_1` the one printer among them.
- [ ] Click `printer_1` in Site's tree → the Selected panel shows **Name,
      Position, Status** (editable: it is a structure) and then one row,
      **Part: ender3**. The tree keeps its height and scroll.
- [ ] Double-click `printer_1` → inside it: `frame_system` (the electronics
      box, with the **Creality V4.2.2** board inside) and `gantry_system` (the
      uprights, the top bar, the belt tensioner boss at the Y rail's front).
      The printer's own body is not drawn at this level -- it is the picture
      one level up, which is how the viewer treats every parent. Back out:
      Backspace, or the `garage` crumb of the header's trail.
- [ ] In the parts library (`/viewer/sites/parts_library`): every part
      `apothecary parts list` names, in a grid; double-click `arduino_uno` → the breadcrumb reads
      `parts_library › arduino_uno`, the Selected panel carries the part's
      section (SCAD source, readiness, and the parameters its SCAD declares --
      it is described by its sidecar, not a wrapper, so OpenSCAD's customizer
      lists them: `size`, with a snapshot from `apothecary openscad install`;
      with 2021.01, which cannot list them, none). `ender3` has parameters: `z_axis`,
      `x_axis`, `y_axis`, `with_spool`, `with_lcd`.

Bring a file in:

```bash
cd <clone>
printf 'v 0 0 0\nv 2 0 0\nv 2 1 0\nv 0 1 0\nv 0 0 3\nv 2 0 3\nv 2 1 3\nv 0 1 3\nf 1 2 3 4\nf 5 6 7 8\nf 1 2 6 5\nf 2 3 7 6\nf 3 4 8 7\nf 4 1 5 8\n' > /tmp/brick.obj
uv run apothecary parts import /tmp/brick.obj --name demo_brick --units in --up y \
    --title "A brick" --author "You" --license CC-BY-4.0 --url https://example.org/brick
uv run apothecary parts info demo_brick
ls parts/demo_brick/ ; cat parts/demo_brick/part.json
```

- [ ] `parts import` → `✓ demo_brick: 12 triangles, 50.8 x 76.2 x 25.4 mm`
      (2 x 1 x 3 inches, a quarter turn from Y-up), the folder listing
      (`demo_brick.mesh.stl`, `demo_brick.stl`, `demo_brick.scad`,
      `demo_brick.mesh.stl.license`, `part.json`), and a `Place it:` line
      with the footprint to paste.
- [ ] `parts info` → `category: imported`, bounds `min y -76.2`, the source
      block with your title, author, licence, URL and `obtained` today.
- [ ] Reload `/viewer/sites/parts_library` → one part more; `demo_brick` is
      a grid cell; double-click it → its SCAD is the one `import(...)` line.
- [ ] `uv run apothecary parts import /tmp/brick.obj --name demo_brick` →
      refused: *exists; --force replaces it*. With `--license CC-BY-NC-4.0`
      and `--force` → a yellow line: *a licence with a field-of-use
      restriction cannot be committed to this repository*; the part is still
      made, for your own use.
- [ ] `git status --short parts/demo_brick` → only `part.json`, the `.scad`
      and the `.license` file show; the two STLs are ignored (`*.stl`).
- [ ] Clean up: `rm -rf parts/demo_brick`.
- [ ] Optional, the union limit:
      `printf 'union(){ import("%s/parts/ender3/ender3.stl"); translate([1000,1000,1000]) cube(1); }\n' "$PWD" > /tmp/u.scad && openscad -o /tmp/u.stl /tmp/u.scad`
      → hundreds of facets and no `ERROR:` line. The same with
      `parts/matboard_cutter_mount/matboard_cutter_mount.stl` → a CGAL
      `ERROR:` and 6 facets: that mesh is one OpenSCAD 2021.01 drops from a
      union, which the docs page names.

## 4. One screen: the rail, the anchors, the machine in front of the world

On your own server, in the garage, with the page freshly loaded.

- [ ] One rail, on the right of the world: **Site** and **Selected**
      stacked in it, both open -- Site with the garage's tree, the category
      chips above it and three folded sections below it, **Pinned**,
      **Jobs** and **SCAD** -- and below them a strip of tabs, **Pictures**
      and **Bench**, neither shown. The other side of the world is world, and
      the rail leaves it at least half the page.
- [ ] Press a tab → its panel shows under the strip; press it again → it
      folds away. With a machine open and docked (section 6), its tab joins
      the strip, its log in it: pressing a tab shows that one instead.
- [ ] Press **`** (or `~`) → the rail hides and a tab stands in for it;
      press again → back. Typing in a text box never triggers it.
- [ ] Drag the rail's inner edge → its width follows, never more than half
      the page; reload → the width is kept. Press **⇄** in the rail's head
      (or drag its grip across the page) → the rail and every panel in it
      move to the left of the world; reload → still on the left; **⇄** again
      → back on the right.
- [ ] On **Site**: ▾ collapses it to its title; ⧉ floats it free (drag it
      by its title, resize from its corner); its title's ⇥ docks it back
      above Selected; ✕ closes it to a tab at the bottom right; the tab
      reopens it. A shown tab's ⧉ floats Pictures the same way, and its ⇥
      docks it back into the strip. Reload → the layout is remembered.
- [ ] Unfold Site's **SCAD** → the site's generated OpenSCAD.
- [ ] Select `printer_1`, type 1160 into its X → the header's count says *1
      violation*; Site shows one folded line at its top, *1 problem*, and
      both rows are red, saying so on hover. Click the header's count → the
      fold opens on *printer_1 and footpedal overlap*. Double-click
      `workbench`, then click the problem's row → the view steps back out to
      the root and printer_1 is selected. Close Site, click the header's
      count → Site opens with its problems unfolded. Type 100 back → *Layout
      valid*.
- [ ] Right-click the canvas → the ring; **Panels** → a cell per panel
      (Site, Selected, Pictures, **Machine** (a board's, its log in it),
      Rail, and **Bench**, which opens on the Bench itself, then its verbs);
      a digit toggles one.
- [ ] Select `printer_1`, press **m** → the node ring: Zoom in, Move, Device
      (once its board is pinned; Control is under it, ⌗27), Why this, Into,
      Camera, Picture, Part, seated cardinals first; 5 backs out.
- [ ] A ⚡ **badge** stands at every pinned, connected board and follows it
      as you orbit; with nothing pinned there is none. Its words (state,
      temperatures, the port) show on hover, or while its machine is
      selected. Pin something in section 6 and come back: the badge appears;
      a click selects its machine and opens its **Machine** in the rail's
      strip, a tab beside Pictures and the Bench; the tab's ⧉ floats it over
      the world, its ⇥ docks it back, and floated then closed it opens docked
      again; a printer's Machine has no Flashing card; its jog moves the
      world's nozzle marker ahead of the next poll.
- [ ] `/firmware/monitor?port=<your port>` → the viewer, on the site the
      port is pinned in (pinned nowhere: the default site), with its Machine
      open in the rail's strip, the address keeping `?machine=`; and
      `/firmware` → the viewer with the **Bench** open, its toolchain naming
      the config `~/.apothecary/tools/arduino-cli.yaml`. The header has no
      link to either: Panels › Bench and a board's Machine are the way.

## 5. The camera and the pictures

On the **demo server**, in a folder of pictures, so frames land somewhere you
mean:

```bash
mkdir -p /tmp/apothecary-pictures && cd /tmp/apothecary-pictures
ARDUINO_CLI=$(uv run --project <clone> python -c "import sys; sys.path.insert(0, '<clone>/tests'); from pathlib import Path; from firmware_helpers import write_fake_arduino_cli; print(write_fake_arduino_cli(Path('/tmp/fake-arduino-cli')))") \
APOTHECARY_SERIAL_ENGINE=simulated APOTHECARY_SIMULATED_PRINTER=printing \
APOTHECARY_STATE_DIR=/tmp/apothecary-demo APOTHECARY_TOOLS_DIR=/tmp/apothecary-demo/tools \
uv run --project <clone> apothecary serve --port 8001
```

Open `http://127.0.0.1:8001/viewer/sites/garage`. A camera is a part of the
site: a place's ring adds one, and its own ring (right-click it, or select it
and press `m`) holds its verbs; the pictures are listed in **Pictures** (its
tab in the rail, or ring → Panels → Pictures), and every camera, view and
board pin in Site's **Pinned**.

- [ ] Right-click `workbench` in Site's tree → **Camera › Add here** →
      `camera_1` stands above the bench looking straight down, selected and
      in Site's tree: its body, its 📷 badge, the move arrows with a turn
      ring and a tilt arc, and its pyramid down to the bench's top.
      Right-click `camera_1` → **Device › Allow** → the browser asks once;
      with one camera it is camera_1's device at once, with several the ring
      reopens at Device to choose one. The status bar names the next step,
      *Take picture (P)*; Selected's camera section names the device.
      `curl -s http://127.0.0.1:8001/sites/garage/cameras/camera_1` → its
      pose, its lens, where it lands (`workbench`) and the browser's id and
      label for its device -- kept in `/tmp/apothecary-demo/camera_parts.json`,
      never in the site. (Chromium's fake camera works too: launch it with
      `--use-fake-ui-for-media-stream --use-fake-device-for-media-stream`.)
- [ ] camera_1's **Live** → *live where it looks*: its video in Selected, its
      pyramid shown even with something else selected; **Still** → it stops.
- [ ] **Take picture** -- camera_1's ring, Selected's button, or **P** with
      it selected → the frame lies on the bench where the camera looks,
      sized from its lens with no width typed, a thumbnail in Selected, and
      the status bar names *Picture › Find shapes*;
      `ls /tmp/apothecary-pictures/captures/` → one PNG, and the folder is
      `drwx------`. The bench's **Picture › Find shapes** → the shapes
      outlined on the picture, and the status bar names Make.
- [ ] The camera stays in the garage: double-click `printer_1` → its badge
      and body are gone (not at the top-left corner of the canvas, not
      anywhere); Backspace, or the `garage` crumb → both are back, above the
      bench, and the badge is not dimmed when nothing stands between you and
      the camera; selected again, its pyramid shows.
- [ ] **Pictures** → every picture in the folder as thumbnails, grouped by
      the camera that took them (the capture under *camera_1*), the pictures
      no camera took in a group of their own, last.
      **add** (its file picker) → choose two pictures of your own → the
      status bar says *added 2 picture(s)* and names choosing one and
      Picture › Folder; they are listed *· added*, *pinned nowhere*;
      `ls /tmp/apothecary-pictures/uploads/` → the two, named as you named
      them, the folder `drwx------`. A picture has no button that pins it:
      the ring's Picture › Folder does.
- [ ] Click one of their rows → it is chosen, highlighted, and the status
      bar names Picture › Folder; click it again, or press Escape → let go;
      click another → that one instead. Choose one, right-click `workbench`
      → **Picture › Folder**: among the seven newest pictures its own cell
      is marked; older than those (put more than seven in the folder), the
      last cell is *Pin* and its name. Press it → pinned at the bench as a
      view and drawn; its row names *workbench*. Click a row's *workbench* →
      the bench is selected and that view drawn.
- [ ] **Forget** on the other → gone from the list and from the folder; a
      picture you put in the folder by hand has no Forget.
- [ ] Unfold Pictures' **Gather**, tick **all**, **Gather** → a report with
      *Groups*, the questions the machine thinks are worth your word
      (answered with buttons), and a `details` block.
- [ ] Unfold Site's **Pinned** → every camera, view and board pinned, every
      site's, each row naming its site. A camera's **Remove** → it leaves the
      world and Site's tree, its badge with it, and the pictures it took
      stay; `curl -s http://127.0.0.1:8001/sites/garage/attached` → no
      cameras. Pin a board from a piece's
      Device section (or by typed identity, `aa:bb:cc:dd:ee:ff`) → its row
      appears (fold and unfold Pinned if not); a pin whose site is gone --
      pin a node of an arrangement, then forget the arrangement -- shows
      *site gone*; each row's **Unpin** takes it back, and the piece's
      Device section offers the ports again at once.
- [ ] Pictures' **Purge kept** → asks once → every capture and upload is
      gone, the pictures you put in the folder by hand are still there
      (`ls /tmp/apothecary-pictures/`).
- [ ] Nothing left the machine: the only requests the page made are to
      `127.0.0.1:8001` (the browser's network panel; the CSP would have
      refused anything else).

## 6. The printer, without hardware and with it

**Without** -- on the demo server from section 5 (the simulated printer,
mid-print; two scripted ports, `/dev/ttyFAKE0` an Uno and `/dev/ttyFAKE1` a
bare board):

- [ ] Select `printer_1 › frame_system › mainboard` in the viewer; the
      Device section offers a pick list of free ports → choose
      `/dev/ttyFAKE1`, **Query** → an M115 answer from the simulator, **Pin**
      → the section is one line: the port, `printing` and the temperatures,
      **Open** and **Unpin**; `printer_1`'s row wears the 🖨 badge and its
      status becomes `printing` *via* the board.
- [ ] The badge above `printer_1` in the world; click it (or **Open**, or
      Device › Open on the ring) → the printer's Machine: status cards, a
      temperature chart after a few polls, and the board's log in it, its
      query box below the cards: **M119** → the endstops in the log; **G28**
      → *query refused*, in the log and in the status bar, red. There is no
      serial log over the world and no Comms log tab; the badge, the row's
      badge and Selected's line say what the Machine's polls say, and
      nothing else polls the printer (the browser's network panel: one
      `printers/status` request per interval).
- [ ] A devkit's Machine: `curl -s -X POST -H 'Content-Type: application/json'
      -d '{"fqbn":"arduino:avr:uno","port":"/dev/ttyFAKE0"}'
      http://127.0.0.1:8001/firmware/sketches/footpedal/upload` (the scripted
      arduino-cli flashes nothing) → **Rescan** in a piece's Device section →
      `footpedal` wears a ⚡ badge; click it → its Machine: the Uno on
      `/dev/ttyFAKE0`, *should run footpedal*, *not listening -- the port is
      closed* (no `devices/stream` request in the network panel); **Listen**
      → *may reset the board* in the log, then its serial output, and
      *observed fake_blink ✗ differs* once the scripted board says hello. Its
      **Flashing** card has *footpedal* and `arduino:avr:uno` chosen;
      **Compile & upload** → confirm → the task's output in the card, then
      *listening 6 s for the sketch's hello* in the log, and no M115. On the
      ring, Device › Flash (⌗22 from `footpedal`) opens it at that card, and
      Device › Link › Listen is ⌗214.
- [ ] The **Bench** (Panels › Bench, or its tab in the rail's strip): the
      scripted arduino-cli *✓ 9.9.9*, the suggested cores, the sketches with
      their boards; **Compile** `footpedal` → the task log says *succeeded*
      and lists it under Recent tasks.
- [ ] **⚙ Control** → the overlay, a 5:00 latch; **Bed 45 → Set** → `M140
      S45` in the log and the target on the card; **Home XY**; **Y+** by 10 →
      the nozzle marker in the world moves; **Off**.
- [ ] Bed level: **Read mesh** → a record with a heatmap (the simulator's
      tilted, bowed bed) and a relief drawn on the bed in the world at the
      printer's `build_origin`; **▤ Probe bed** → confirm → a job that holds
      the port, then a second record.
- [ ] Print from here: **Choose File** →
      `examples/gcode/dry-run-square.gcode`, **makes** → `footpedal` (the
      garage's parts, `printer_1`'s own left out) → **▶ Print** → confirm →
      lines stream one per `ok`; Site's **Jobs** says *1 running* and lists
      it on top; **⏸ Pause**, **Resume**, **■ Cancel** → the safe-off lines in
      amber; the card's history and Site's row read *cancelled*, and
      `GET /jobs?site=garage` → the job with its file, its printer, the part
      and its outcome. Click its row in Site → `printer_1` is selected and its
      machine opens.
- [ ] `curl -s "http://127.0.0.1:8001/firmware/printers/where?port=/dev/ttyFAKE1"`
      → `build_volume [220,220,250]`, `build_origin [90,100,95]`,
      `base_height 95`, the board inside the printer at (80, 90, 26).
- [ ] Stop the demo server. `ls /tmp/apothecary-demo` → `firmware-state.json`,
      `camera_parts.json`, `jobs/`, `leveling/`, `prints/`: everything the demo
      kept, in the folder you gave it, and nothing under your own
      `~/.apothecary`.

**With hardware** -- your own server, the board plugged in: the latch-side
checklist in [`2026-09-20-ender-bench.md`](2026-09-20-ender-bench.md)
(heaters, motion, the corner checks, a probe, a print from here, E-STOP,
release), unchanged, plus these three that the bench did not have:

- [ ] `apothecary firmware boards` with the board plugged in → the port and
      its `0403:6001` as before; `~/.arduino15/inventory.yaml` does **not**
      gain a new `cache:` entry with today's time: the cloud lookup is off.
- [ ] Pin it to `printer_1.frame_system.mainboard` → the bed reading's relief
      and the nozzle marker sit on the Ender 3 model's bed in the world.
- [ ] The loop from a picture to a print, with the real camera over the bench
      and the board pinned, as
      [walkthrough 03](../../../../walkthrough/03-a-picture-to-a-print.md) goes round
      it with the fakes: the bench's **Camera › Add here**, the camera's
      **Device**, **Take picture**, **Picture › Find shapes**, **Picture › Make**
      on a shape -- the status names *Part › Edit* and *a printer's Machine* --
      **Part › Edit** and Apply, then printer_1's **Device › Open**: *Print from
      here* lists the piece under *makes*. Keep a file sliced from the piece (its
      editor's 💾 Download SCAD, rendered and sliced as any part would be),
      choose the piece, arm, **▶ Print**:
      the confirm names the piece, the status says where it is followed, and the
      history and Site's Jobs keep the job with the piece's name. Turn the
      camera, **P**, make a second piece with the Machine left open: *makes*
      lists it without reopening, and **Print** on the piece's own ring chooses
      it there. When each print ends the status line says so, or that it failed
      and why.

## 7. The docs, and the walkthrough

- [ ] `http://127.0.0.1:8000/docs/geometry-from-elsewhere.md`,
      `/docs/firmware.md`, `/docs/plans/photo-finders-local-models-2026-09-21.md`
      → rendered, links between
      pages work, every image is local (a picture from elsewhere would be
      named, not fetched).
- [ ] `/walkthrough/01-photographs-into-pieces.md` → its last step gives the
      census count (`apothecary census` says the same) and its screenshots
      show the one rail, Site and Selected stacked in it.
- [ ] `/walkthrough/02-the-bench-as-it-is.md` → fourteen steps: a file from
      elsewhere measured, the sidecar part, the Ender 3, the mainboard, the
      DevKitC, a camera added above the bench and *not* following you into a
      printer, what the browser put here taken back (added pictures, one of
      them chosen, a pin, a purge) with Pictures listing only what the page
      put in its own picture folder, the guard's refusal and the server's
      403 -- each with the
      output or the picture of the run that wrote it.
- [ ] `/walkthrough/03-a-picture-to-a-print.md` → the loop from a picture to a
      print twice round, each step's status line naming the next; the pictures'
      times and picture names blanked, the words without them.
- [ ] `uv run apothecary docs generate` → both doc workflows regenerate under
      a temporary server on 8766; the bar on every docs page then says when.
      The walkthrough pages 01, 02 and 03 are rewritten by the browser
      run instead (`uv run pytest tests/e2e --start-server`); CI fails if the
      committed pages differ from what the run writes.

## 8. The suites and the gates

```bash
uv run pytest                                # unit + walkthrough doctests
uv run pytest tests/e2e --start-server -q    # the browser suite, on a scripted machine
uv run apothecary test all                   # both, exiting with pytest's own code
uv run ruff check apothecary tests
uv run --with "reuse[charset-normalizer]" python -m reuse lint
git -C governance/qm log --oneline origin/project/apothecary..adr/firmware-toolchain-seam   # six records
```

- [ ] All green; the browser run never touches `~/.apothecary`, your
      pictures or your serial ports (temp state, temp pictures, the scripted
      arduino-cli and the simulated printer).

## 9. OpenSCAD on every platform

`apothecary openscad install` installs a development snapshot natively where
OpenSCAD publishes one, builds it from source on Linux arm64, and refuses
Windows on ARM as a planned item. CI does not cover the other platforms yet;
this section is how they are proven, on the machines themselves. The tools
folder is `~/.apothecary/tools` (`%USERPROFILE%\.apothecary\tools` on Windows).
`uv run apothecary openscad status` says, per install, how it was installed,
whether it runs natively, and whether it has Manifold.

**Linux x86_64**

- [ ] `uv run apothecary openscad install --latest` → downloads the night's
      AppImage, "SHA-256 verified", `OpenSCAD version <date>`; status reads
      `AppImage, run through FUSE · native · Manifold`.
- [ ] On a machine without FUSE (a container without `/dev/fuse`) → "cannot
      mount itself here (no FUSE); extracting it instead", and status reads
      `AppImage extracted (no FUSE here)`; a render works.

**macOS (Apple Silicon; Intel too if one is to hand)**

- [ ] `uv run apothecary openscad install --latest` → downloads the `.dmg`,
      "SHA-256 verified", "A universal app (x86_64 and arm64)", installed at
      `…/<date>/OpenSCAD.app/Contents/MacOS/OpenSCAD`; no Finder window or
      desktop volume appears, and afterwards `hdiutil info` lists no
      OpenSCAD image and `$TMPDIR` holds no `apothecary-openscad-*` folder.
- [ ] `lipo -archs …/Contents/MacOS/OpenSCAD` → `x86_64 arm64`;
      `xattr -l …/OpenSCAD.app` → no `com.apple.quarantine`;
      `codesign --verify --deep --strict …/OpenSCAD.app` passes, and
      `codesign -dv` names "Developer ID Application: Marius Kintel
      (28U8KJ6T2P)". Write down what `spctl -a -vv` says; the first run shows
      no Gatekeeper prompt.
- [ ] Status → `OpenSCAD.app from the disk image · native (universal) ·
      Manifold`; `uv run pytest --slow` renders with it, and Activity
      Monitor shows OpenSCAD's Kind as Apple.
- [ ] From an x86_64 Python (`uv run --python cpython-3.12-macos-x86_64-none
      apothecary openscad status`) → "emulated: x86_64 under Rosetta 2", and
      a render from it shows Kind Intel.

**Windows x64 (a normal user, PowerShell)**

- [ ] `uv run apothecary openscad install --latest` → downloads the
      `-x86-64.zip`, "SHA-256 verified", "Unpacking", `OpenSCAD version
      <date>`, installed at `…\<date>\openscad.exe`, with `openscad.com`,
      `libraries`, `fonts` and `install.json` beside it. If it fails with
      "reports no version", write it down (the fix is to ask `openscad.com`).
- [ ] Status → `portable zip, unpacked · native · Manifold`, not "unknown
      version" (a first scan by Defender can outlast the 10 s version check);
      `uv run pytest --slow` renders; note any SmartScreen or Defender
      prompt.
- [ ] `install --snapshot <date> --force` replaces it in place, with no
      `.tmp` folders left.

**Windows on ARM (a Snapdragon PC, if one is to hand)**

- [ ] `uv run apothecary openscad install`, from an ARM64 and from an x64
      Python → both refuse with "Windows on ARM is not supported", and
      download nothing.

**Linux arm64 (a Raspberry Pi 4/5 on 64-bit Raspberry Pi OS, or another
arm64 board)**

- [ ] Before installing anything, `uv run apothecary openscad install` →
      refuses, lists what the build needs and prints the `sudo apt install …`
      line; nothing is read or downloaded.
- [ ] Run that line, then the install again, in tmux → "building <date> from
      source", the commit and six submodule lines, seven downloads,
      "Configuring (cmake)", "Building with N jobs", "Built in N min",
      "Manifold X.Y.Z: a cube renders with it", installed at
      `…/<date>/bin/openscad`. Write down N, the wall time, peak memory
      (`free -h`), whether it swapped, and the build folder's peak size. A
      failure keeps its log at `~/.apothecary/tools/openscad/build-<date>.log`.
- [ ] `grep -iE "download|fetchcontent"` over the kept build log → nothing
      fetched during the build.
- [ ] Status → `built from source at <sha> · native · Manifold X.Y.Z`;
      `…/bin/openscad --info` (write down whether its OpenGL part works
      headless); `uv run apothecary parts generate-stl gridfinity --force`
      renders.
- [ ] On a 2 GB board, `--jobs 1` completes; `install --snapshot <same date>`
      again says "already installed" and fetches nothing.

## Results

Fill this in as you go; anything refused or slow gets its time, port and
command. Outcomes that change a number in a doc go to that doc; a defect
goes to `project/todo.md` or an issue; a door found open goes to the record's risk register.

| Section | Ticked | Notes (what, when, port, command) |
|---|---|---|
| 0. After the review | / 7 | |
| 1. Setup | / 4 | |
| 2. Stays on the device | / 12 | |
| 3. Geometry | / 12 | |
| 4. One screen | / 7 | |
| 5. Camera | / 11 | |
| 6. Printer (simulated) | / 7 | |
| 6. Printer (hardware) | / 2 + the bench record | |
| 7. Docs | / 4 | |
| 8. Suites | / 2 | |
| 9. OpenSCAD, Linux x86_64 | / 2 | |
| 9. OpenSCAD, macOS | / 4 | |
| 9. OpenSCAD, Windows x64 | / 3 | |
| 9. OpenSCAD, Windows on ARM | / 1 | |
| 9. OpenSCAD, Linux arm64 | / 5 | |

## For a person, and follow-ups

What this branch leaves to a person, and the hardening that comes after it.
Each item names what done looks like.

**Governance, a person's acts**

- [ ] **Ratify the records on qm#121** (`adr/firmware-toolchain-seam` into
      `project/apothecary`), first *Personal data stays on the device*: its
      §2 names the OpenSCAD installer as the second caller of the tool fetch
      and `files.openscad.org`, `api.github.com` and `codeload.github.com`
      as its sources, and §6 the rules for views. Done: the status flipped
      and a number assigned by a human commit, the PR merged.
- [ ] **Bump apothecary's governance pin** to the ratified
      `project/apothecary` (`git -C governance/qm checkout <commit>`, commit
      the pin alone). Done: `check-submodule-refs` green on the bump's PR.
- [ ] **rad#7** proposes opening a ring entered at an item for rad's host
      standard; apothecary's ring follows whatever rad decides (its host
      record's revision trigger).

**Hardening, after this branch**

- [ ] **GPG signatures** on downloads: check the `.asc` beside each
      OpenSCAD AppImage, zip and installer against OpenSCAD's signing key,
      and the same for arduino-cli's releases where one is published, before
      a download is accepted (needs GnuPG and the key, carried or fetched
      once as a tool).
- [ ] **macOS code signature in code**, not only on the checklist: the
      app's signature verified and its Team ID (28U8KJ6T2P) checked, and its
      notarisation; the `.dmg` has no `.asc`.
- [ ] **Windows Authenticode** on `openscad.exe`, if it is signed.
- [ ] **Source-build integrity**: codeload tarballs have no published
      checksum; check the unpacked files against the git tree the API
      returns, and record each tarball's SHA-256 in `install.json`.
- [ ] **Nested submodules** in a source build (none at today's pins), and
      the `.1` second builds some nights publish (the plain name is used).
- [ ] **One day: Windows on ARM**, natively. No ARM64 snapshot is published;
      today the installer refuses it as a planned item.

