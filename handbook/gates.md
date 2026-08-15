# Handbook — The Gates

**Generated `2026-08-15T04:28:54Z`.** Quotable for 168h. **Do not edit by hand** — the list lives in `ci/gate-registry.yaml`, the document in `gate-status.json`, and this page is rendered from the document and nothing else.

| | |
|---|---|
| **Refresh the document** | `uv run qm docs generate` |
| **Re-render this page** | `uv run qm gates --check handbook/gates.md` |
| **Claim** | `ci/gate-registry.yaml` — what a human says each gate does |
| **Evidence** | `.github/workflows/` — what is on disk |
| **Enforcement** | the host — whether any of it blocks a merge |

## The merge boundary

**Whether anything blocks a merge is unknown** — --no-host was passed, so the host was not asked what it requires.

Not established is not the same as nothing wrong. Every gate below may or may not be advisory; this document does not know.

**10 gates are built; 0 are declared and not built.** The second number is the honest measure of how much of this governance is still customary. States: 9 ok, 0 warn, 1 unknown.

## Every gate

| | Gate | Stands before | Trigger | Seed | Refuses |
|---|---|---|---|---|---|
| [ok] | `adr-lint` | main, push | pull_request, push | yes | A record whose header table, status or index row is malformed; banned narration vocabulary in a pre-ratification draft; a vendor or model name in a record's prose or a commit subject; a seed copy still showing its template placeholder to a reader; a record whose declared restatement does not name it back. |
| [ok] | `one-pr-slot` | main | pull_request | yes | A pull request whose author already holds an open slot in this repository. It fails every one of them rather than picking a survivor. |
| [ok] | `namespace-guard` | main, push | pull_request, push | no | A pull request opened in the wrong direction between namespaces, and a project branch whose own commits touch anything outside `adr/`. |
| [ok] | `ci-tooling-tests` | main, push | pull_request, push | no | A change to the CI tooling that breaks its own test suite. |
| [ok] | `governance-status` | main, push | pull_request, push | no | A committed `governance-status.yaml` that no longer renders the commits it names, and a rendered view that has drifted from it. |
| [ok] | `reuse-lint` | main, push | pull_request, push | yes | A file with no copyright or licence information, a bad or deprecated SPDX expression, or an unused licence file. |
| [ok] | `symlink-integrity` | main, push | pull_request, push | no | A pointer file that has stopped being a symlink -- mode other than 120000 -- which is how a Windows checkout silently forks a shared document into two. |
| [ok] | `tag-claims` | tag | push, workflow_dispatch | yes | A pushed `v*` tag that is lightweight, misnamed, or whose annotation is missing `Reviewed-by`, `Manually-tested`, `Automated-gate` or `Not-covered`. |
| [??] | `secret-scan` | main | — | no | A commit introducing a credential the scanner recognises. |
| [ok] | `commit-signatures` | main | pull_request | yes | A branch carrying a commit with no verifiable signature. |

## What each gate cannot see

Read this before quoting a green check. Every defect this corpus has found in its own tooling was a check that reported success while enforcing nothing.

- **`adr-lint`** — Whether a record is correct, or whether a restatement and its record agree -- it pairs declarations and compares no text. Three of its four sub-checks cannot fire on any ref CI runs against, which is a known finding and not yet fixed.
- **`one-pr-slot`** — Whether the two pull requests are actually related. It counts slots, not subject matter, and the `--per-base` exemption is a glob somebody passes.
- **`namespace-guard`** — A branch cut from the wrong parent whose direction is nonetheless legal. `check_pr_base.py` reports the inheritance; nothing fails on it.
- **`ci-tooling-tests`** — Whether a passing test discriminates. A test that passes against the broken tool is inert, and this corpus has shipped two of those -- only a mutation pass finds them, and no gate runs one.
- **`governance-status`** — Whether the document is current. It checks faithfulness to the refs it names, not age -- a document generated from unfetched refs passed this once, which is why the workflow fetches first.
- **`reuse-lint`** — Whether the licence asserted is the licence intended, or whether a dependency's licence is compatible with it.
- **`symlink-integrity`** — A rule missing from one of the two genuinely different AGENTS.md files. They are not symlinked to each other, so this check cannot notice them disagreeing.
- **`tag-claims`** — Whether the review or the manual test happened -- it reads an annotation a human wrote. It does not gate tag creation, which needs a host-side tag-protection ruleset, and it runs after the tag exists.
- **`secret-scan`** — Everything about how it is configured. It is an installed application with no workflow file in this repository and no record describing it, so nothing here states what it scans, who can dismiss a finding, or what happens if it is uninstalled. It appears on pull requests and that is the whole of what this corpus knows about it.
- **`commit-signatures`** — Whether the signer is the person named in the author field, beyond what the key attests. It would establish that an attestation exists, which is currently established for nothing.

## What each gate makes mechanical

| Gate | Record or page |
|---|---|
| `adr-lint` | `records/DRAFT-decision-record-discipline.md`, `records/DRAFT-human-only-contributorship.md`, `records/DRAFT-the-read-document-governs.md`, `records/DRAFT-governance-arrives-as-a-mechanism.md` |
| `one-pr-slot` | `handbook/async-contract.md` |
| `namespace-guard` | `README.md` |
| `ci-tooling-tests` | *nothing stated — it guards a habit rather than a decision* |
| `governance-status` | `handbook/generated-documents.md` |
| `reuse-lint` | `records/DRAFT-outbound-licensing.md`, `records/DRAFT-open-license-exclusion-and-upstream-remediation.md` |
| `symlink-integrity` | `records/DRAFT-ide-integrated-governance-discovery.md` |
| `tag-claims` | `records/DRAFT-version-tags-are-claims.md` |
| `secret-scan` | *nothing stated — it guards a habit rather than a decision* |
| `commit-signatures` | `records/DRAFT-human-only-contributorship.md` |

## Where claim and evidence disagree

- [??] **`secret-scan`** — **unknown** — an installed application with no workflow file in this repository; nothing here can read its configuration

## Reading this document

- **Do not** quote a figure from this document without its generated_at.
- **Do not** read `ok` as `required to merge` -- that is the enforcement layer.
- **Do not** read `ok` as `tested` -- no gate here has a mutation pass.
- **Do not** drop a gate whose declared_built is false to make a view green.
- **Do not** regenerate this in CI with the host layer: it reads the host, so an unrelated pull request would go red for a reason its author cannot fix. --check reads the local layers only, and is safe there.

