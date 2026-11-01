# Handbook — The Gates

**Generated `2026-11-01T23:29:07Z`.** Quotable for 168h. **Do not edit by hand** — the list lives in `ci/gate-registry.yaml`, the document in `status/gates.yaml`, and this page is rendered from the document and nothing else.

| | |
|---|---|
| **Refresh the document** | `uv run qm docs generate` |
| **Re-render this page** | `uv run qm gates --check handbook/gates.md` |
| **Claim** | `ci/gate-registry.yaml` — what a human says each gate does |
| **Evidence** | `.github/workflows/` — what is on disk |
| **Enforcement** | the host — whether any of it blocks a merge |

## The merge boundary

**Nothing blocks a merge on `quaternionmedia/qm`.** The host reports 0 ruleset(s) and no branch protection on `main`.

**Every gate below is therefore advisory.** A green check means *someone was told*, not *this was prevented*. Advisory is a legitimate state — most governance here is advisory on purpose — but it is not the same claim, and a reader who conflates them will trust a merge nobody checked.

**22 gates are built; 0 are declared and not built.** The second number is the honest measure of how much of this governance is still customary. States: 21 ok, 0 warn, 1 unknown.

## Every gate

| | Gate | Stands before | Trigger | Seed | Refuses |
|---|---|---|---|---|---|
| [ok] | `adr-lint` | main, push | pull_request, push | yes | A record whose header table, status or index row is malformed; banned narration vocabulary in a pre-ratification draft; a vendor or model name in a record's prose or a commit subject; a seed copy still showing its template placeholder to a reader; a record whose declared restatement does not name it back; a principle that declares no relationship to the others and gives no reason, or declares one the other end does not declare back. |
| [ok] | `stacked-drafts` | main | pull_request | yes | A pull request marked ready whose base is the branch of another open pull request in the same repository. It fails every such pull request of the author, not only the one whose event ran it. |
| [ok] | `one-pr-voice` | main | pull_request | yes | A pull request body that speaks to its contributor rather than as them: the second person, the handling phrases that have leaked ("assigned, no review requested", "merge when ready"), or the contributor's own login mentioned. Code spans, fenced blocks and quoted lines are left alone. |
| [ok] | `pr-direction` | main | pull_request | no | A pull request whose head is a `project/<name>` branch, which is permanent and never a merge source; a `math/<slug>` exploration aimed at anything but a `workspace/*` branch; and a head carrying a top-level `adr/` at the default branch. The step is in this corpus's copy of the workflow and not in the seed: a project's own repository has no `project/*` branches, so there the same step could never fail. |
| [ok] | `namespace-guard` | project, push | pull_request, push | no | A `project/<name>` branch whose own commits touch anything outside `adr/`, on a pull request into the branch and, after the fact, on a push to it. It compares content with `main` and not commits, so org content arriving by a merge from `main` is not mistaken for the project editing it. |
| [ok] | `ci-tooling-tests` | main, push | pull_request, push | no | A change to the CI tooling that breaks its own test suite. |
| [ok] | `governance-status` | main, push | pull_request, push | no | A committed `status/governance.yaml` that no longer renders the commits it names, and a rendered view that has drifted from it. |
| [ok] | `reuse-lint` | main, push | pull_request, push | yes | A file with no copyright or licence information, a bad or deprecated SPDX expression, or an unused licence file. |
| [ok] | `symlink-integrity` | main, push | pull_request, push | no | A .vscode/ or .claude/ configuration pointer that has stopped being a symlink -- mode other than 120000 -- which is how a Windows checkout without core.symlinks silently forks a shared file into two. |
| [ok] | `docs-audit` | main, push | pull_request, push | no | A documentation site that no longer builds, or builds and emits nothing; a generated family page, project page or front-page snippet that no longer matches its sources; and a project's timeline that no longer matches its committed round log and git snapshot, or a retrospective beside it with no date. A link to nothing, a corpus path a page names that does not exist, and a page that shadows a corpus document are reported and do not fail the run. On a push to `main` it runs with no path filter, so two pull requests each green at their own tip that together leave a generated page stale make `main` red, and not the next contributor's pull request. |
| [ok] | `docs-check` | main, push | pull_request, push | no | A committed generated document that no longer matches what its generator writes from this tree: the governance and gate documents, the gate view, the site palette, the family cookbook and the family site pages, the rollout, and the three index documents, `status/documents.yaml`, `handbook/document-states.md` and `loose-ends.json`. It runs with no path filter, so a page that changes state without its index is red on the pull request that changed it, and `main` is checked after every merge. |
| [ok] | `docs-draft` | main | pull_request, workflow_dispatch | no | Nothing. It builds a preview of the site for the change under review, so a documentation change can be looked at rather than imagined. |
| [ok] | `docs-deploy` | push | push | no | Nothing. It publishes the site from the default branch. A failure here means the published site is older than `main`, which is a fact worth seeing and not a rule anybody violated. |
| [ok] | `tag-claims` | tag | push, workflow_dispatch | yes | A pushed `v*` tag that is lightweight, misnamed, or whose annotation is missing `Reviewed-by`, `Manually-tested`, `Automated-gate` or `Not-covered`. |
| [ok] | `tag-determinism` | tag | push, workflow_dispatch | no | A `v*` tag whose captured test run declares a skip, a rerun or a retry, or whose suite does not pass at all. |
| [??] | `secret-scan` | main | — | no | A commit introducing a credential the scanner recognises. |
| [ok] | `commit-signatures` | main | pull_request | yes | A branch carrying a commit with no verifiable signature. |
| [ok] | `registries` | main, push | pull_request, push | no | An exemption with no stated reason or whose named constant has gone; a policy with neither a detector nor a stated reason it cannot have one; a ledger entry that is unattributed, or closed and unscored; two lanes that are settled by the same gate; a protocol with no page or a step naming a route that does not exist; a curriculum unit citing a document that is not there or claiming a Status its document does not carry; an address vector that does not parse as declared or does not format back to itself; a family claim naming a family the record does not declare; a mathematical mapping that does not state what it has not earned. |
| [ok] | `leak-check` | main, push | pull_request, push | yes | A tracked file that carries a person's home directory, a path through a personal or IDE-made folder, a path into a session's scratch space, a shared-conversation link, a link to a page an assistant's host keeps, or a conversation archive's path. Findings are printed redacted; a deliberate example is declared with `leaks: allow` and a reason, and every allowance is counted on every run. |
| [ok] | `timeless-check` | main, push | pull_request, push | yes | Prose added by a change that sets a phrase in capitals, or that narrates how the text or the code came to be. It reads comments and docstrings in code, markdown outside code blocks and spans, and comments in configuration, on the lines the change adds. A deliberate exception is declared with `timeless: allow` and a reason, and every allowance is counted on every run. |
| [ok] | `rulesets` |  | — | no | Nothing, on a runner. It is a preflight: `uv run qm rulesets --check` exits non-zero when a ruleset drafted in .github/rulesets/ is absent from the host, or is applied at a different enforcement level, or carries a different set of rule types. |
| [ok] | `private-names` |  | — | no | Nothing, on a runner. It is a preflight, run on a machine that holds the gitignored companions, and it refuses a private repository's name used as a repository -- after a slash, quoted, or as the value of a name, slug, repository or branch field -- in any tracked file. |

## What each gate cannot see

Read this before quoting a green check. Every defect this corpus has found in its own tooling was a check that reported success while enforcing nothing.

- **`adr-lint`** — Whether a record is correct, or whether a restatement and its record agree -- it pairs declarations and compares no text. Nor whether two principles actually conflict: the edge check reads a stated relationship from both ends and knows nothing about what either principle says, so a wrong edge declared consistently passes. It also cannot tell a real isolation from a lazy one -- it can only insist the `none` carries a reason somebody had to write. Three of its four sub-checks cannot fire on any ref CI runs against, which is a known finding and not yet fixed. One commit subject is exempt from the vendor-name rule by full SHA -- 35ebca6a, kept as the worked example the rule is taught from -- and check_attribution.py prints that exemption and its reason on every run.
- **`stacked-drafts`** — Whether a pull request is one change. A branch cut from another pull request's branch but opened against the target, carrying its parent's commits. A pull request closed in favour of one that contains it -- closed pull requests are not read.
- **`one-pr-voice`** — The third person. "Peter merges once the gates are green" is a statement about a person and the tool cannot tell it from a sentence addressed to them without a pronoun, so it is allowed; and whether the body is honest, complete, or about the diff at all.
- **`pr-direction`** — A branch under a prefix the namespaces page does not list: it refuses three directions and no unknown prefix, so an `adr/*` or `fix/*` head passes it. A branch cut from the wrong parent whose direction is legal: the merge-base and the commits shared with another branch are reported as an advisory, and nothing fails on them.
- **`namespace-guard`** — Anything on a pull request into `main`: both its triggers are filtered to `project/**`, so the direction of a pull request between namespaces is `pr-direction`'s to refuse. A push cannot be refused, so on a push it reports and prevents nothing. A branch cut from the wrong parent whose own commits touch `adr/` only.
- **`ci-tooling-tests`** — Whether a passing test discriminates. A test that passes against the broken tool is inert, and this corpus has shipped two of those -- only a mutation pass finds them, and no gate runs one. For the walkthrough it also cannot see whether a page is worth reading: doctest asserts that an example's printed output is what the page claims, and asserts nothing about whether the example was the one worth showing.
- **`governance-status`** — Whether the document is current. It checks faithfulness to the refs it names, not age -- a document generated from unfetched refs passed this once, which is why the workflow fetches first.
- **`reuse-lint`** — Whether the licence asserted is the licence intended, or whether a dependency's licence is compatible with it.
- **`symlink-integrity`** — The instruction pointers. CLAUDE.md and project-seed/ide/CLAUDE.md are regular files holding the one line `@AGENTS.md`, an import and not a link, so a wrong line in either is a text change this check does not read. And a rule missing from one of the two genuinely different AGENTS.md files: they are not linked to each other, so this check cannot notice them disagreeing.
- **`docs-audit`** — Whether a page is true. It builds the site and follows the links, so it finds a link to nothing and not a page that is wrong, and it does not read the navigation, so a page nothing links to passes. `uv run qm prose` reads the openings; a person reads the rest. Of the generated pages it sees only whether they match their sources: not whether a showcase caption describes its picture, nor whether a showgraph was drawn from the commits its project is at. Of a timeline it sees the committed files only: not a git snapshot behind its project, nor a round left out of the round log. On a pull request it runs only when the change touches the site or a generator's input, by path filter.
- **`docs-check`** — A document with no check mode, `status/harness.yaml` and `families.json`: their freshness is the staleness budget each carries in its own `reading:` block, and the run reports them skipped. The enforcement layer of `status/gates.yaml`, which is read from the host and changes without a commit here. Whether a generated document is true: it compares each with what its generator writes from the same tree, so a generator that is wrong is wrong on both sides and passes.
- **`docs-draft`** — Anything -- it is a build, not a check, and it is listed here because a workflow nobody declared is a workflow nobody can rely on. Declaring it says plainly that it refuses nothing.
- **`docs-deploy`** — Whether what it published is correct, or whether anybody reads it. It is a deployment, and it is declared for the same reason the draft build is.
- **`tag-claims`** — Whether the review or the manual test happened -- it reads an annotation a human wrote. It does not gate tag creation, which needs a host-side tag-protection ruleset, and it runs after the tag exists.
- **`tag-determinism`** — Whether the suite is deterministic. It refuses a run that announces nondeterminism; one that is nondeterministic and silent about it passes. It also says nothing about coverage: a suite asserting little passes as readily as one asserting much.
- **`secret-scan`** — Everything about how it is configured. It is an installed application with no workflow file in this repository and no record describing it, so nothing here states what it scans, who can dismiss a finding, or what happens if it is uninstalled. It appears on pull requests and that is the whole of what this corpus knows about it.
- **`commit-signatures`** — Whether the signer is the person named in the author field, beyond what the key attests. It would establish that an attestation exists, which is currently established for nothing.
- **`registries`** — Whether any registry is complete. Each of these seven checks the entries that exist against their own rules; none can tell that an exemption, a policy, a ledger entry, a lane, a protocol, a curriculum unit or an address case was never written down, and a registry nobody added to is the state all seven report as clean. Nor can it see an address that is well-formed and wrong: the grammar has no idea whether the branch exists. It also cannot see whether a protocol was ever run -- that is reported by `uv run qm protocols` and deliberately never refused -- or whether a curriculum unit's prose is true of the document it cites. Nor is this gate required to merge: it is a candidate for A-main.json's required list and stays off it until it has reported green on a real pull request.
- **`leak-check`** — Everything on that line that is not a path or a link: an editor named in prose, a process somebody saw running, a tool narrating its own session, a person's words quoted into a constraint. A pattern for those would fire on every page that legitimately discusses editors or quotes a record, so the reader is the check, at the runbook's Step 3. Nor can it read history -- a path already pushed stays pushed -- or tell a placeholder from a real account beyond the ones it lists. Of a hosted page it sees only a link a file carries: a page never linked, a link in a pull request body, and a host its pattern does not list all pass.
- **`timeless-check`** — A story told in neutral words, and a present-tense sentence that is no longer true; those are the reviewer's. Text already on the base, which `--all` reports and a sweep removes. Capitals in title case or spaced out, a phrase broken so that no line holds three of its words, and file types it does not read. In this corpus it does not read a project's subtree under `docs/projects/<name>/`, which is dated history.
- **`rulesets`** — Whether a rule is the right rule. It compares enforcement levels and rule types, not rule parameters, so a required-status-check list that has been emptied on the host reads as a match. It cannot run in CI at all: reading what is applied needs a host credential, and a check that reads a host reds a pull request for a reason its author cannot fix. It also does not read `rule-suites`, which is the log of what an evaluating rule would have blocked and the thing worth reading before promoting one.
- **`private-names`** — A repository that becomes private after the fact. By records/DRAFT-going-private-is-an-act-with-obligations.md the party who makes a repository private owns removing its name from this corpus, so nothing here watches for the transition: detecting it would need either an organisation-read credential this repository does not hold, or a committed digest list that would be recoverable, since 24 of 33 names are ordinary words of median length 7. It also cannot see history -- two names are published from 2b50bd6 and no forward fix removes them -- and it does not gate a bare-word match in prose, because several private repositories are named after common words and matching those produced 187 findings with no disclosures.

## What each gate makes mechanical

| Gate | Record or page |
|---|---|
| `adr-lint` | `records/DRAFT-decision-record-discipline.md`, `records/DRAFT-human-only-contributorship.md`, `records/DRAFT-the-read-document-governs.md`, `records/DRAFT-governance-arrives-as-a-mechanism.md` |
| `stacked-drafts` | `handbook/async-contract.md` |
| `one-pr-voice` | `records/DRAFT-human-only-contributorship.md`, `handbook/async-contract.md` |
| `pr-direction` | `docs/ref/namespaces.md` |
| `namespace-guard` | `docs/ref/namespaces.md` |
| `ci-tooling-tests` | `records/DRAFT-one-executable-walkthrough.md` |
| `governance-status` | `handbook/generated-documents.md` |
| `reuse-lint` | `records/DRAFT-outbound-licensing.md`, `records/DRAFT-open-license-exclusion-and-upstream-remediation.md` |
| `symlink-integrity` | `records/DRAFT-ide-integrated-governance-discovery.md` |
| `docs-audit` | `records/DRAFT-the-read-document-governs.md`, `records/DRAFT-a-project-page-shows-what-was-picked-and-what-was-drawn.md`, `records/DRAFT-a-projects-history-lives-in-the-corpus.md` |
| `docs-check` | `handbook/generated-documents.md` |
| `docs-draft` | *nothing stated — it guards a habit rather than a decision* |
| `docs-deploy` | *nothing stated — it guards a habit rather than a decision* |
| `tag-claims` | `records/DRAFT-version-tags-are-claims.md` |
| `tag-determinism` | `records/DRAFT-version-tags-are-claims.md` |
| `secret-scan` | *nothing stated — it guards a habit rather than a decision* |
| `commit-signatures` | `records/DRAFT-human-only-contributorship.md` |
| `registries` | `ci/exception-registry.yaml`, `ci/policy-registry.yaml`, `ci/lane-registry.yaml`, `ci/protocol-registry.yaml`, `ci/capability-registry.yaml`, `curriculum/org.yaml`, `project-seed/address-vectors.json` |
| `leak-check` | `records/DRAFT-what-is-not-the-organisation.md`, `records/DRAFT-work-is-delivered-into-a-repository.md`, `ci/policy-registry.yaml nothing-committed-describes-the-workstation-the-agent-or-the-conversation`, `ci/policy-registry.yaml work-is-delivered-into-a-repository` |
| `timeless-check` | `records/DRAFT-durable-text-states-what-is-true.md` |
| `rulesets` | `ci/policy-registry.yaml main-is-entered-through-a-pull-request`, `.github/rulesets/README.md` |
| `private-names` | `ci/policy-registry.yaml no-private-name-in-a-public-artifact` |

## Where claim and evidence disagree

- [??] **`secret-scan`** — **unknown** — an installed application with no workflow file in this repository; nothing here can read its configuration

## Reading this document

- **Do not** quote a figure from this document without its generated_at.
- **Do not** read `ok` as `required to merge` -- that is the enforcement layer.
- **Do not** read `ok` as `tested` -- no gate here has a mutation pass.
- **Do not** drop a gate whose declared_built is false to make a view green.
- **Do not** regenerate this in CI with the host layer: it reads the host, so an unrelated pull request would go red for a reason its author cannot fix. --check reads the local layers only, and is safe there.

