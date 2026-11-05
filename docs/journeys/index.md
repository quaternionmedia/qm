<p class="qm-eyebrow">journeys · a person, a front end, a result</p>

# Journeys

A journey is the path a person takes through this estate's front ends, from where they start to the result they came for. Each page lists every step: the command to run or the place to click, and what you see when it worked.
{ .qm-lede }

<div class="grid" markdown>

<div class="card" markdown>

**from nothing**

Clone the core repositories side by side, sync them, and run the first demo, which checks that two front ends draw the same picture.

[From a clone to the first demo →](clone-to-first-demo.md){ .qm-card-link }

</div>

<div class="card" markdown>

**every day**

Say once which repositories this machine runs, start them, and see each one answer in the browser and in the terminal.

[Bring your set up →](bring-your-set-up.md){ .qm-card-link }

</div>

<div class="card" markdown>

**with a model**

Run a local model, start an application with it, and use it from the browser.

[Use a model with an application →](use-a-model-with-an-application.md){ .qm-card-link }

</div>

</div>

## The front ends

Every journey ends in one of these. The [harness](../ref/glossary.md#harness){ .glossary-term } holds the work; the others read it.

| Surface | Repository | Where you look |
|---|---|---|
| harness | `qmcp` | <http://127.0.0.1:3141/docs>, every route it serves |
| web front end | `codecartographer` | <http://127.0.0.1:2718/app>, then the **Estate** tab |
| terminal front end | `dossier` | `cd dossier && uv run dossier dashboard`, then **Seams**, **Harness** |
| prose reader | `looksatwords` | <http://127.0.0.1:1414/>, then the **Harness** tab at the foot of the page |

`uv run qm dashboard` prints the same table for the surfaces running on your machine, with the command that brings up each one that is not.

## Where the commands run

Every `uv run qm …` command runs in the `qm` clone. The other repositories sit beside it, in one folder: the dashboard and the demo look for them beside the clone and one level up.

The pictures on these pages are taken from running surfaces by `uv run qm journey-pictures`, so they can be taken again when a front end changes. No picture shows a list from the harness's thread archive, which holds the operator's own conversations.

*What these pages cannot do:* stand in for the rules. A journey shows the path; the [handbook](https://github.com/quaternionmedia/qm/tree/main/handbook) and the records decide what is allowed along it, and [Questions a new developer asks](../usage/questions-a-new-developer-asks.md) answers the questions a path raises.
