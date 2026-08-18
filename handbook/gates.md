# Handbook — The Gates

**Generated `2026-08-18T19:39:19Z`.** Quotable for 168h. **Do not edit by hand** — the list lives in `ci/gate-registry.yaml`, the document in `gate-status.json`, and this page is rendered from the document and nothing else.

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

**13 gates are built; 0 are declared and not built.** The second number is the honest measure of how much of this governance is still customary. States: 12 ok, 0 warn, 1 unknown.

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
| [ok] | `registries` | main, push | pull_request, push | no | An exemption with no stated reason or whose named constant has gone; a policy with neither a detector nor a stated reason it cannot have one; a ledger entry that is unattributed, or closed and unscored; two lanes that are settled by the same gate; a protocol with no page or a step naming a route that does not exist; a curriculum unit citing a document that is not there or claiming a Status its document does not carry; an address vector that does not parse as declared or does not format back to itself. |
| [ok] | `rulesets` |  | — | no | Nothing, on a runner. It is a preflight: `uv run qm rulesets --check` exits non-zero when a ruleset drafted in .github/rulesets/ is absent from the host, or is applied at a different enforcement level, or carries a different set of rule types. |
| [ok] | `private-names` |  | — | no | Nothing, on a runner. It is a preflight, run on a machine that holds the gitignored companions, and it refuses a private repository's name used as a repository -- after a slash, quoted, or as the value of a name, slug, repository or branch field -- in any tracked file. |

## What each gate cannot see

Read this before quoting a green check. Every defect this corpus has found in its own tooling was a check that reported success while enforcing nothing.

- **`adr-lint`** — Whether a record is correct, or whether a restatement and its record agree -- it pairs declarations and compares no text. Three of its four sub-checks cannot fire on any ref CI runs against, which is a known finding and not yet fixed. One commit subject is exempt from the vendor-name rule by full SHA -- 35ebca6a, kept as the worked example the rule is taught from -- and check_attribution.py prints that exemption and its reason on every run.
- **`one-pr-slot`** — Whether the two pull requests are actually related. It counts slots, not subject matter, and the `--per-base` exemption is a glob somebody passes.
- **`namespace-guard`** — A branch cut from the wrong parent whose direction is nonetheless legal. `check_pr_base.py` reports the inheritance; nothing fails on it.
- **`ci-tooling-tests`** — Whether a passing test discriminates. A test that passes against the broken tool is inert, and this corpus has shipped two of those -- only a mutation pass finds them, and no gate runs one. For the walkthrough it also cannot see whether a page is worth reading: doctest asserts that an example's printed output is what the page claims, and asserts nothing about whether the example was the one worth showing.
- **`governance-status`** — Whether the document is current. It checks faithfulness to the refs it names, not age -- a document generated from unfetched refs passed this once, which is why the workflow fetches first.
- **`reuse-lint`** — Whether the licence asserted is the licence intended, or whether a dependency's licence is compatible with it.
- **`symlink-integrity`** — A rule missing from one of the two genuinely different AGENTS.md files. They are not symlinked to each other, so this check cannot notice them disagreeing.
- **`tag-claims`** — Whether the review or the manual test happened -- it reads an annotation a human wrote. It does not gate tag creation, which needs a host-side tag-protection ruleset, and it runs after the tag exists.
- **`secret-scan`** — Everything about how it is configured. It is an installed application with no workflow file in this repository and no record describing it, so nothing here states what it scans, who can dismiss a finding, or what happens if it is uninstalled. It appears on pull requests and that is the whole of what this corpus knows about it.
- **`commit-signatures`** — Whether the signer is the person named in the author field, beyond what the key attests. It would establish that an attestation exists, which is currently established for nothing.
- **`registries`** — Whether any registry is complete. Each of these seven checks the entries that exist against their own rules; none can tell that an exemption, a policy, a ledger entry, a lane, a protocol, a curriculum unit or an address case was never written down, and a registry nobody added to is the state all seven report as clean. Nor can it see an address that is well-formed and wrong: the grammar has no idea whether the branch exists. It also cannot see whether a protocol was ever run -- that is reported by `uv run qm protocols` and deliberately never refused -- or whether a curriculum unit's prose is true of the document it cites. Nor is this gate required to merge: it is a candidate for A-main.json's required list and stays off it until it has reported green on a real pull request.
- **`rulesets`** — Whether a rule is the right rule. It compares enforcement levels and rule types, not rule parameters, so a required-status-check list that has been emptied on the host reads as a match. It cannot run in CI at all: reading what is applied needs a host credential, and a check that reads a host reds a pull request for a reason its author cannot fix. It also does not read `rule-suites`, which is the log of what an evaluating rule would have blocked and the thing worth reading before promoting one.
- **`private-names`** — A repository that becomes private after the fact. By records/DRAFT-going-private-is-an-act-with-obligations.md the party who makes a repository private owns removing its name from this corpus, so nothing here watches for the transition: detecting it would need either an organisation-read credential this repository does not hold, or a committed digest list that would be recoverable, since 24 of 33 names are ordinary words of median length 7. It also cannot see history -- two names are published from 2b50bd6 and no forward fix removes them -- and it does not gate a bare-word match in prose, because several private repositories are named after common words and matching those produced 187 findings with no disclosures.

## What each gate makes mechanical

| Gate | Record or page |
|---|---|
| `adr-lint` | `records/DRAFT-decision-record-discipline.md`, `records/DRAFT-human-only-contributorship.md`, `records/DRAFT-the-read-document-governs.md`, `records/DRAFT-governance-arrives-as-a-mechanism.md` |
| `one-pr-slot` | `handbook/async-contract.md` |
| `namespace-guard` | `README.md` |
| `ci-tooling-tests` | `records/DRAFT-one-executable-walkthrough.md` |
| `governance-status` | `handbook/generated-documents.md` |
| `reuse-lint` | `records/DRAFT-outbound-licensing.md`, `records/DRAFT-open-license-exclusion-and-upstream-remediation.md` |
| `symlink-integrity` | `records/DRAFT-ide-integrated-governance-discovery.md` |
| `tag-claims` | `records/DRAFT-version-tags-are-claims.md` |
| `secret-scan` | *nothing stated — it guards a habit rather than a decision* |
| `commit-signatures` | `records/DRAFT-human-only-contributorship.md` |
| `registries` | `ci/exception-registry.yaml`, `ci/policy-registry.yaml`, `ci/lane-registry.yaml`, `ci/protocol-registry.yaml`, `curriculum/org.yaml`, `project-seed/address-vectors.json` |
| `rulesets` | `ci/policy-registry.yaml main-is-entered-through-a-pull-request`, `.github/rulesets/README.md` |
| `private-names` | `ci/policy-registry.yaml no-private-name-in-a-public-artifact` |

## Where claim and evidence disagree

- [??] **`secret-scan`** — **unknown** — an installed application with no workflow file in this repository; nothing here can read its configuration
- [!!] **`docs-audit.yml`** is a workflow nobody declared. It is not adopted into the list above — a gate this page cannot describe is a gate nobody can rely on. Add it to `ci/gate-registry.yaml`.
- [!!] **`docs-draft.yml`** is a workflow nobody declared. It is not adopted into the list above — a gate this page cannot describe is a gate nobody can rely on. Add it to `ci/gate-registry.yaml`.
- [!!] **`docs.yml`** is a workflow nobody declared. It is not adopted into the list above — a gate this page cannot describe is a gate nobody can rely on. Add it to `ci/gate-registry.yaml`.

## Reading this document

- **Do not** quote a figure from this document without its generated_at.
- **Do not** read `ok` as `required to merge` -- that is the enforcement layer.
- **Do not** read `ok` as `tested` -- no gate here has a mutation pass.
- **Do not** drop a gate whose declared_built is false to make a view green.
- **Do not** regenerate this in CI with the host layer: it reads the host, so an unrelated pull request would go red for a reason its author cannot fix. --check reads the local layers only, and is safe there.

