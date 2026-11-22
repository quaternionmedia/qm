<p class="qm-eyebrow">journeys · from nothing</p>

# From a clone to the first demo

Five repositories cloned side by side, each synced, and one command that runs the same topology through two front ends and checks that they agree. On a machine with uv's cache already warm it takes about two minutes.
{ .qm-lede }

## What you need

- **git** and **[uv](https://docs.astral.sh/uv/)**. uv brings the Python each repository asks for.
- **Node.js 20 or later, with npm**, to build the web front end once.
- About 1.5 GB of disk for five environments and the web build.

## 1. Clone the core, side by side

Make one folder and clone into it. `qmcp` carries a submodule, so it is cloned with it.

```sh
mkdir estate && cd estate
git clone https://github.com/quaternionmedia/qm.git
git clone --recurse-submodules https://github.com/quaternionmedia/qmcp.git
git clone https://github.com/quaternionmedia/codecartographer.git
git clone https://github.com/quaternionmedia/dossier.git
git clone https://github.com/quaternionmedia/looksatwords.git
```

`qm` is the [corpus](../ref/glossary.md#corpus){ .glossary-term } and its commands; `qmcp` is the [harness](../ref/glossary.md#harness){ .glossary-term }; `codecartographer` and `dossier` are the web and terminal front ends; `looksatwords` reads the harness's conversations.

## 2. Sync each one

Each repository has its own environment, and the commands below run each one in its own. Sync each once, from the lock:

```sh
cd qm && uv sync --locked && cd ..
cd qmcp && uv sync --locked && cd ..
cd codecartographer && uv sync --locked && cd ..
cd dossier && uv sync --locked && cd ..
cd looksatwords && uv sync --locked && cd ..
```

The web front end serves a built page, so build it once:

```sh
cd codecartographer/web && npm install && npm run build && cd ../..
```

## 3. Ask what this machine has

```sh
cd qm
uv run qm devloop
```

It measures this machine against what the [loop](../ref/glossary.md#loop){ .glossary-term } needs and ends with what to do next. A line saying that most roster repositories are not on this disk is expected: the core is five of them.

## 4. Run the first demo

```sh
uv run qm demo
```

It runs one topology through the terminal front end and the web front end, each under its own repository's environment, and compares what they drew. Then it serves one thread to three readers, and has two front ends read the estate. Each act runs only once the one before it agrees. It ends:

```text
ESTATE AGREEMENT
  codecartographer and dossier agree about every family, every member, and every placement -- 52 of them.

  What this did not establish: that any placement is right.
```

The count follows the estate. Without a thread archive on the machine the demo uses a stated fixture and says so.

## 5. Next

Agreement between two front ends run as subprocesses is a claim about the documents they draw. [Bring your set up](bring-your-set-up.md) starts the same front ends as servers and makes the claim about the running processes:

```sh
uv run qm demo --over-http --side-by-side
```

## When a step does not work

| What you see | What it means | What to do |
|---|---|---|
| `program not found` for `qm` | the command ran outside the `qm` clone | `cd qm` first |
| `<repo> is not beside this clone` | that repository is not in the same folder as `qm` | clone it beside `qm` |
| `qmcp` fails to sync, naming `vendor/vox` | the submodule was not cloned | `git submodule update --init` in `qmcp` |
| `http://127.0.0.1:2718/` shows a page asking for a build | the web front end has no built page | step 2's `npm run build` |
| a front end reports `has no environment yet` | that repository was not synced | step 2, in that repository |

*What this cannot do:* show that a topology is right. The demo checks that the windows agree about what the harness gave them; if the harness gave both a wrong picture, both draw it faithfully. [The demo's reference](../ref/ci/demos.md) says what each act establishes and what it does not.
