# Roadmap — alfred

What alfred claims is built, in the order to take it. A ticked line is a claim;
what shows it is the journey or the walkthrough pages the line names. `qmcp tour`
reads this page beside the running application's journeys and the feedback kept
on each stage, and says of each line what was found. What a person said is never
written into this page.

A `## ` heading opens a group. A line is a checkbox item, ticked when the project
claims it is built. It names a journey the application serves as `journey:<id>`
in a code span, and a page of the repository's walkthrough by a link to it. A line
that names neither is shown by nothing, and the review says so.

```markdown
## Making a thing

- [x] A part is chosen, shaped, sliced and printed. `journey:make`
- [ ] An assembly is navigated by its pieces. [09](../../../walkthrough/09-an-assembly.md)
```

Where the journeys form a chain, each handing the next what it made, the lines
take them in the chain's order.

alfred's journeys are the editor's user journeys (the application's
`docs/journeys.md`), over its four stages, Source, Edit, Render and Deliver. A
first video goes the whole way; the journeys after it take one part of that way
each, in the order the flow takes them. alfred has no walkthrough, so a
claim no journey shows is shown by nothing.

## Making a video

- [x] A video is made from start to finish from the demo project: chosen, watched, rendered and downloaded. `journey:first-video`
- [x] A project is made from a person's own footage in the server's library. `journey:your-own-footage`
- [x] Clips are arranged, trimmed and cut, and a title is put on, and the timeline saves itself. `journey:arrange-and-title`
- [x] The timeline is rendered at a chosen size, followed to the end, and downloaded or delivered. `journey:render-and-deliver`
- [x] A project with a form makes its video from what is typed into it, previewed a frame at a time. `journey:from-a-form`
- [x] The timeline is transcribed, captioned, and cut by deleting its words. `journey:captions-and-cutting-by-words`

## The editor

- [x] On a phone, the same journeys go a stage at a time.
- [x] A project opens where it was saved, and an edit not saved is offered back.
- [x] An account is made, logged into, and its password reset by mail.
- [x] An assistant lists projects, transcribes, renders and delivers through qmcp.
- [ ] The tour takes the editor to each stage of each journey, and keeps a person's word on it.
