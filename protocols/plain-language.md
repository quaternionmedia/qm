# Protocol — Plain language review

**Question.** Can somebody who has never seen this repository read its first
page and know what it is for?

**Invoked by** a human, or an agent asked to. **Budget** 90 days. **Produces**
`protocols/runs/<date>-plain-language.md`.

This reviews the *openings* of the documents a newcomer meets, and the words
those openings lean on. It is not a copy-edit of the corpus. Most pages here are
written for people who already have the vocabulary, and that is correct; the
entry points are the ones that cannot assume it.

---

## 1. Read the openings together

```sh
uv run qm prose
```

It prints the first sentence of every entry point on one screen, with the
patterns `handbook/style-guide.md` names flagged. **Nothing fails.** A flag is a
place to look, and every pattern flagged is legitimate somewhere: a sentence can
be long and clear, and an opening can name a house word when that word is the
subject.

Read the sentences as a set, aloud. The question is not whether each is accurate
— they usually are — but whether somebody without the vocabulary would still be
reading by the end of the first paragraph.

## 2. Check that the house words are linked

An entry point may use a narrow word. What it may not do is use one *and leave
the reader with nowhere to go*. Every such word should link, on first use, to
the definition that covers it.

```sh
uv run qm docs audit
```

The link dimension refuses a link that leaves the published site — a relative
link to a file outside `docs/` resolves on disk and 404s once deployed — and a
fragment naming no anchor, which lands the reader at the top of a page and reads
as having worked.

Both were live when this protocol was written: `docs/index.md` linked
`../handbook/glossary.md`, which is not published, on the same page as a correct
link to the same glossary.

## 3. Check the glossary covers what the openings use

For each narrow word an entry point uses, confirm the glossary defines it. Add
the entry rather than removing the word when the word is the right one:
`Proposed` and `gate` were both used on the landing page and defined nowhere in
the site's own glossary.

## 4. Record the run

Write `protocols/runs/<date>-plain-language.md`. It carries the commit, the
openings as they read on the day, what was changed, and — the part worth
keeping — what was left alone and why.

---

## What this cannot see

Whether the sentence is true. Whether the reader needed a different fact first.
Whether the words are *the reader's* words, since the tool holds a list of this
corpus's house vocabulary and knows nothing about anybody else's.

It reads openings, which is a small fraction of any page. A document can open
well and be unusable afterwards.

And it says nothing about the repositories this corpus governs. Every command
above reads the repository it is run in. Running it in a project means running
it there.
