# Roadmap — <name>

<!-- SEED FILE: part of project-seed/project/, copied with it; the comment
     in README.md beside this file says how. Delete this comment in the
     copy. -->

What <name> claims is built, in the order to take it. A ticked line is a claim;
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
