# Tooling reference

How the [corpus](../../ref/glossary.md#corpus){ .glossary-term }'s own tools behave: what each family of scripts in `ci/` and
`project-seed/ci/` reads, decides and cannot see. `uv run qm --help` lists every
command; these pages explain the behaviour the commands share.

- **[Gates and checks](gates-and-checks.md)**: the checks that refuse
  something, and the rules they share.
- **[Status documents](status-documents.md)**: the committed documents under
  `status/`, how they are derived and what their fields mean.
- **[Measuring the suite](measuring-the-suite.md)**: what the tests cost, what
  they catch, and how the mutation score is read.
- **[Documentation tooling](docs-tooling.md)**: the tools that link and audit
  this site.
- **[The trio demo](demos.md)**: one topology through every window, and what
  their agreement does and does not show.
