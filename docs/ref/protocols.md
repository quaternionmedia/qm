# Protocols index

The [protocols](https://github.com/quaternionmedia/qm/tree/main/protocols) are
the procedures somebody runs on purpose. A protocol takes judgement, produces a
dated artifact, and is invoked — nothing triggers one automatically.

That is the whole distinction from a [gate](glossary.md#gate). A gate runs
itself, refuses, and answers pass or fail. The two are kept in separate
registries deliberately: merging them makes a protocol read as always-on and a
gate read as optional, and both readings are wrong in the direction that hurts.

`uv run qm protocols` lists them with each one's last run, its budget, and
whether it is overdue. Read that rather than this page for the current state —
the table below says what each protocol is for, not when it was last done.

| Protocol | The question it answers |
|---|---|
| [plain-language.md](https://github.com/quaternionmedia/qm/blob/main/protocols/plain-language.md) | Can somebody who has never seen this repository read its first page and know what it is for? |
| [security-review.md](https://github.com/quaternionmedia/qm/blob/main/protocols/security-review.md) | What could leak from this repository, and what actually protects it right now? |
| [local-demo.md](https://github.com/quaternionmedia/qm/blob/main/protocols/local-demo.md) | Does this project actually do the thing, on this machine, today? *(optional)* |
| [curriculum.md](https://github.com/quaternionmedia/qm/blob/main/protocols/curriculum.md) | In what order should someone with no context read this corpus, and what can they do afterwards? *(optional)* |

Each protocol states its own budget in its page, and `uv run qm protocols`
prints them alongside the last run. They are not copied here, because a budget
restated in a second place is a number nothing updates.

Each run writes a dated page under
[protocols/runs/](https://github.com/quaternionmedia/qm/tree/main/protocols/runs).
A run is a record of what was true on one day, so runs are added rather than
edited.

## Plain language review

This is the one most likely to matter to you, because it governs the pages a
newcomer meets before they have the vocabulary.

It reviews the *openings* of the entry-point documents and the house words those
openings lean on. It is not a copy-edit of the corpus: most pages here are
written for people who already have the vocabulary and that is correct, but the
entry points cannot assume it.

It asks two things of an entry point. The first is a judgement rather than a
rule: read the openings **as a set, aloud**, and ask not whether each sentence is
accurate — they usually are — but whether somebody without the vocabulary would
still be reading by the end of the first paragraph. An opening may name a house
word when that word is its subject; what it may not do is assume one.

The second is closer to a rule: **a house word should link, on first use, to the
definition that covers it**, and the [glossary](glossary.md) holds them. An
unlinked house word leaves the reader with nowhere to go.

`uv run qm prose` prints the opening of every entry point side by side, which is
the mechanical half. **Nothing fails** — a flag is a place to look, and every
pattern it flags is legitimate somewhere. The reading is the protocol; the
command is the shortcut into it.

## Related

- [Glossary](glossary.md) — the house words the protocol asks you to link
- [Handbook index](handbook.md) — policy and procedure, as distinct from these
  invoked procedures
- [Record precedence](precedence.md) — what binds, and in what order
