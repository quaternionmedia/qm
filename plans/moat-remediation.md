# moat remediation

**What this is.** Everything outstanding in `quaternionmedia/moat`, written as
slices a session can pick up cold, ordered by dependency and by which slot each
one consumes.

**What it is not.** A schedule, and not a backlog anybody has committed to.
Several items are decisions only a person may take, and those say so.

**Re-derive before acting.** Every item names the command that establishes it. A
finding here was true at some commit and the command is what makes it true
again — or retires the item, which is the cheaper outcome.

---

## The three lanes

Ordering below is dependency and slot contention. Nothing here is calendar.

| Lane | Where the work lands | What constrains order |
|---|---|---|
| **O — operational** | Live systems and credential stores. No branch, no pull request | Nothing. Independent of every other lane, and should not wait on one |
| **C — corpus** | `quaternionmedia/qm` | Its own slot. One item, on which the whole of lane P's governance work blocks |
| **P — project** | `quaternionmedia/moat` | One open pull request per repository per contributor. Strictly sequential — the binding constraint on this page |

Both open pull requests in `moat` belong to the same contributor, so the slot is
doubly occupied and the repository's own `one-pr-check` reports it. Freeing it is
the precondition for every other item in lane P.

`uv run qm slot --repo quaternionmedia/moat` answers the slot question before
any lane P session writes anything.

---

## Lane O — operational

No branch. No pull request. Do not sequence these behind lane P.

### O1 — Rotate every disclosed credential

**Blocks on** nothing.

**The finding.** `moat` is public. Camera RTSP credentials, ONVIF credentials
and MinIO keys in more than one chart are in the tree or in reachable history.

**Establish it.**

```sh
gh repo view quaternionmedia/moat --json isPrivate
grep -rInE 'rtsp://[^@ ]+:[^@ ]+@|access_key|secret_key|password:' \
  --include='*.yaml' charts/ loki/ tempo/
```

**Do.** Rotate at the source — the camera, the ONVIF account, and each MinIO
service account — and inject the replacements from a Kubernetes Secret rather
than a values file. Rotation is what closes this; editing the tree is not.

**Done when.** Each rotated credential is confirmed in use by the workload that
needs it, and the retired ones fail an authentication attempt.

**Why it does not wait.** A redaction commit does not un-disclose anything.
Until rotation, the tree can be spotless and the credentials still work.

### O2 — Decide what happens to the history

**Blocks on** O1. **Only a person may decide this.**

**The finding.** Redacting a credential in a new commit leaves it reachable on
the default branch. The adoption record closes its credential row on the
criterion "credentials removed from the tree" — a criterion the tree satisfies
while the repository still discloses them.

**Establish it.**

```sh
git log -p --all -S 'qwertyui' -- charts/frigate/values.yaml | head
```

**The options, each with its cost.**

| | cost |
|---|---|
| Rewrite history | every clone and any downstream pin breaks; the corpus forbids this in its own repository and has never sanctioned it elsewhere |
| Accept the disclosure, rely on rotation | the credentials stay readable forever; rotation is the only thing standing between them and use |
| Make the repository private | removes the disclosure and forfeits P7 public-by-default, and creates the private-name obligation the corpus already carries an exception for |

**Done when.** The choice is written into a record with its cost stated, or
registered as an exception with a removal condition. Not when it is agreed in a
session.

### O3 — Confirm the load-balancer address pool

**Blocks on** nothing.

**The finding.** `charts/cilium/values.yaml` enables `l2announcements`, the
MetalLB application was removed from the `groot` chart, and nothing in the tree
defines a `CiliumLoadBalancerIPPool` or `CiliumL2AnnouncementPolicy`. A
`LoadBalancer` service — Traefik's among them — has no pool to draw from unless
one was applied out of band.

**Establish it.**

```sh
grep -rn 'CiliumLoadBalancerIPPool\|CiliumL2AnnouncementPolicy' .
grep -rn 'metallb' charts/groot/
kubectl get ciliumloadbalancerippool -A
kubectl get svc -A --field-selector spec.type=LoadBalancer
```

**Name what else produces this.** A pool applied by hand, or synced by ArgoCD
from a repository other than this one, produces an empty grep and a working
cluster. The `kubectl` lines are what tell the two apart. If a pool exists only
in the cluster, this becomes a lane P item — bring it into the tree — rather
than an outage.

---

## Lane C — corpus (`quaternionmedia/qm`)

### C1 — Create the `project/moat` branch

**Blocks on** nothing. **Blocks** every governance item in lane P.

**The finding.** `moat` has no branch in the corpus. Its submodule cannot be
added, its `submodule-check` cannot pass, and its `adr-lint` has no records
directory to read.

**Establish it.**

```sh
git ls-remote --heads origin 'refs/heads/project/*'
git ls-remote --heads origin refs/heads/project/moat
```

**Do.** Cut `project/moat` the way the existing `project/*` branches were cut,
per `docs/ref/namespaces.md`. Seed it with `project-seed/adr/` copied verbatim.

**Done when.** `git ls-remote --heads origin refs/heads/project/moat` returns a
ref, and `project-seed/ci/check_pr_base.py` refuses a pull request from that
branch into `main`.

**Note.** `moat` is listed under `org.unmanaged_named` in
`governance-status.yaml`, which is correct as long as nothing has merged.
Regenerating that document is what moves it, not editing it.

---

## Lane P — project (`quaternionmedia/moat`)

One slot. Each item assumes the one above it has merged.

### P0 — Free the slot

**Blocks on** nothing. **Blocks** everything below.

**The finding.** Two open pull requests, one contributor, one repository. Both
are drafts, and draft means incomplete — nobody is waiting at the far end of
that queue.

**Establish it.**

```sh
gh pr list --repo quaternionmedia/moat --state open \
  --json number,author,isDraft,baseRefName,headRefName
gh pr checks 3; gh pr checks 4
```

**Do.** Close the network pull request, or retarget its base to `main`. It is
stacked on the adoption branch and inherits every finding below, which is the
only reason it cannot land on its own.

**Watch the ordering.** Pushing a pull request's head onto its base *merges* it,
and a later `gh pr close` is a silent no-op. Close first, then push. Retargeting
is the safer of the two.

**Done when.** One open pull request remains, and `one-pr-check` is green on it.

### P1 — Reduce the adoption pull request to its record

**Blocks on** P0.

**The finding.** The adoption branch carries a record worth having and a large
body of session narration around it: root-level documents that describe the
adoption rather than decide anything, and an executable that performs the
adoption a second way.

**Establish it.**

```sh
git diff --stat origin/main...origin/qm
git diff --name-only origin/main...origin/qm | grep -E '^[A-Z-]+\.(md|sh)$'
```

**Do.** Keep `adr/DRAFT-adoption-scope.md`, the README path corrections and the
credential redactions. Delete the rest of the root-level additions. What is
worth keeping from them belongs in the record's Context, or in a retrospective —
not in a document whose subject is the pull request that added it.

Delete `EXECUTION-SCRIPT.sh` outright rather than fixing it. It runs `git rm`,
`git mv`, `git commit` and `git push` against whatever branch is checked out;
it writes a second and differing `REUSE.toml` and a third and differing
`AGENTS.md` over files the same branch already commits; and it runs
`reuse annotate` across every tracked file, which writes headers into chart
values and into prose whose opening lines are load-bearing. Each thing it does
that is worth doing is an item on this page.

**Done when.** The branch's diff against `main` is the record, the README fix,
the redactions, and nothing whose subject is the branch itself.

### P2 — Decide where moat's records live

**Blocks on** P1. **Only a person may decide this.**

**The finding.** The adoption branch is inconsistent with itself about the
records model. `AGENTS.md` describes the branch-per-project model — records on
`project/moat`, reached through the submodule. The branch instead adds a local
`adr/`, and its `adr-lint` workflow lints that local path.

**Establish it.**

```sh
grep -n 'RECORDS_DIR' project-seed/ci/adr-lint.yml
git ls-tree -r --name-only origin/qm | grep '^adr/'
```

**The two models, both supported.** `project-seed/ci/adr-lint.yml` documents
`RECORDS_DIR` as the switch: empty for branch-per-project, set to `adr` for a
local tree. The governed siblings use branch-per-project; `rad` is the
exception.

**Do.** Pick one and make every artefact agree with it — the workflow's
`RECORDS_DIR`, `AGENTS.md`, and where the record file actually sits.

**Done when.** No document in the repository describes a model the repository
does not use.

### P3 — Wire the governance submodule

**Blocks on** C1 and P2.

**The finding.** `AGENTS.md` states the corpus is pinned at `governance/qm` on
branch `project/moat`. There is no `.gitmodules` and no `governance/` path.

**Establish it.**

```sh
git ls-tree -r --name-only origin/qm | grep -iE 'gitmodules|governance'
```

**Do.** Add the submodule at `governance/qm`, tracking `project/moat`, per
`handbook/forking-a-project.md`. Do not improvise a lighter version.

**Done when.** `git submodule status` resolves, and the pinned commit exists on
the submodule's own remote — which is what `check_submodule_pins.py` verifies
and what P4 wires up.

### P4 — Replace the governance workflows with the seed files

**Blocks on** P3.

**The finding.** Each governance workflow on the adoption branch is a
reimplementation rather than the seed file, and each drops something the seed
carries. The seed files say `SEED FILE: copy verbatim` in their first lines.

**Establish it.** For each of `adr-lint`, `one-pr-check`, `reuse-lint`,
`submodule-check`:

```sh
git show 'origin/qm:.github/workflows/NAME.yml' > /tmp/moat-NAME.yml
diff -u project-seed/ci/NAME.yml /tmp/moat-NAME.yml
```

On Windows set `MSYS_NO_PATHCONV=1` first, or `git show` reads the argument as a
path and reports a missing revision — an empty extract diffs as a wholly deleted
file, which reads exactly like a workflow that does not exist.

**What each reimplementation drops.**

| Workflow | What is lost |
|---|---|
| `adr-lint` | Invokes a script at a path that does not exist in the corpus. Checks out without the submodule and without full history, so the append-only check has nothing to diff against even once the path is right. Gated on a records path, where the seed runs on the default branch too |
| `submodule-check` | Asserts the pin's *branch name*. The seed verifies the pinned **commit exists on the submodule's remote** — the failure the seed file's own comment names. Checks out submodules first, which the seed's comment says masks this check's clearer error. Gated on paths that do not exist, so it cannot run |
| `one-pr-check` | Passes `creator` to the pull-request listing endpoint, where it is a parameter of the *issues* endpoint. An unrecognised query parameter is ignored, so the filter is inert and the check enforces one open pull request per **repository**. Triggers only on open and reopen, so a pull request opened into a free slot never re-checks |
| `reuse-lint` | Invokes the console script; the seed uses `python -m reuse lint` with a comment explaining the entry point is not on PATH everywhere |

**Do.** Copy the seed files verbatim. Set `QM_SUBMODULE` and `RECORDS_DIR`
to match P2's decision, and change nothing else.

**Done when — and this is the item, not the copy.** Each gate has been seen to
fail for the reason it exists, and the mutation is written down beside it:

| Gate | The mutation that must turn it red |
|---|---|
| `adr-lint` | Put a banned narrating word in a draft. Then rename a draft to a numbered filename with a non-Accepted status. Then edit an Accepted record's body outside its Amendments section |
| `submodule-check` | Commit a submodule pointer bump without pushing the submodule commit |
| `one-pr-check` | Open a second pull request as the same contributor, and — separately — as a different one. The first must fail and the second must pass. This is the hole in the reimplementation; a green here that does not distinguish them has not been tested |
| `reuse-lint` | Add a tracked file no annotation covers |

A check nobody has watched fail tells you what its author meant, not what it
checks.

### P5 — Licensing

**Blocks on** P4.

**The finding.** `reuse lint` fails with `MISSING LICENSES` — the branch adds
`LICENSE` but no `LICENSES/` directory holding the licence text. Separately, the
`REUSE.toml` it adds uses a `skip` key that is not in the REUSE specification,
and licenses records and prose under the same terms as code, where the corpus
licenses its prose differently and carries a no-grant reference.

**Establish it.**

```sh
gh run view --log <reuse-lint run> | sed -n '/Run reuse lint/,$p' | head -20
git ls-tree -r --name-only origin/qm | grep '^LICENSES/'
head -40 REUSE.toml   # in the corpus, for the shape to follow
```

**Do.** Add `LICENSES/` with the text of every identifier the configuration
declares. Reconcile the annotation blocks against
`records/DRAFT-outbound-licensing.md` and the open-licence record, and drop the
unsupported key. Decide deliberately whether moat's prose takes the corpus's
prose terms or the project's code terms — it is a choice, and the current
configuration makes it by accident.

**Done when.** `python -m reuse lint` exits zero, and one tracked file added
without an annotation turns it red.

### P6 — Rewrite `AGENTS.md` against what exists

**Blocks on** P2 through P5, since it describes their outcome.

**The finding.** The file describes a governance system that is not the one in
the corpus.

**Establish it — each of these is one command.**

```sh
ls ci/ratify.py ci/adr-lint.py ci/check_pr_base.py   # none exist at those paths
grep -cE '^## P[0-9]+' PRINCIPLES.md                 # the file states a different number
grep -nE '^\| \*\*(Draft|Proposed|Accepted)' project-seed/adr/README.md
```

**What is wrong.** A ratification script that does not exist. A bot command that
does not exist. Seed scripts named at `ci/` when they live in `project-seed/ci/`.
A count of principles that does not match `PRINCIPLES.md`. A record-status
vocabulary — `Ratified`, `Amended` — that is not the seed's `Draft | Proposed |
Accepted | Deprecated | Superseded`, which matters because `adr_lint.py` keys on
**Accepted**. And the record referred to by an assigned number while its own
header is numberless, which is the ratifier's act being performed in prose.

**Do.** Rewrite it to say only what a command can establish. Prefer naming the
corpus document over restating it; where it does restate, name the path, and add
the `Restated in` row on the other side so `check_restatements.py` can see the
pair. State no count of principles at all — the relation is "the principles in
`PRINCIPLES.md`", and that sentence never goes stale.

**Done when.** Every path the file names resolves, and every mechanism it
describes can be run.

### P7 — Close the adoption record's remaining rows

**Blocks on** P6. Each row is its own pull request and its own slot.

**The finding.** The record's conflict table is the deliverable, and most rows
are open by design — enumerating a gap is the adoption, not closing it. Two
rows need attention before the rest.

**The credential row** is marked closed on a criterion the tree can satisfy
while the repository still discloses. Reopen it, or restate its closing
criterion as rotation — which O1 does and the tree cannot show. Its reproduction
column also omits one of the two MinIO credential pairs.

**Establish it.**

```sh
git diff --name-only origin/main...origin/qm | grep -i tempo   # empty
grep -n 'access_key\|secret_key' tempo/values.yaml
```

**The chart-layout row** is open and freezes its own subject, while the deleted
execution script performed the move. Whether that row closes here or later is a
decision; performing it while the row is open is not.

**A row this table does not carry.** The network branch pins a community-tier
OpenTofu provider. The command below returns that major version's publication
date and its download count — compare both against the branch that pins it. The
record's own rows already require a component-selection record naming the
protocol and answering the replaceability test, and a risk-register entry per
selected component. Add the row, or bring this selection under the rows that
exist.

```sh
curl -s https://registry.terraform.io/v1/providers/openwrt-iac/uapi
```

### P8 — Normalise the chart layout

**Blocks on** P7's decision on that row.

**The finding.** Chart directories sit outside `charts/`. The publishing
workflow triggers on `charts/**/Chart.yaml`, so those charts never publish, and
none of them is referenced by the `groot` application set.

**Establish it.**

```sh
ls -d */Chart.yaml | grep -v '^charts/'
grep -n 'paths:' -A3 .github/workflows/publish-chart.yaml
for d in $(ls -d */ | grep -v charts); do
  echo "$d $(git log -1 --format=%ad --date=short -- $d)"
done
```

**Do.** Move each one under `charts/`, or delete it. Several have not been
touched in a long while and are stubs carrying only a `Chart.yaml`; deleting a
chart nothing deploys is cheaper than publishing it.

**Done when.** No `Chart.yaml` sits outside `charts/`, the README's paths
resolve, and the publish workflow's trigger covers every chart in the tree.

### P9 — Retire the dead and the expired

**Blocks on** nothing in this lane beyond the slot.

| | The finding | Establish it |
|---|---|---|
| Root `moat` script | References compose files that do not exist, and contains a bracket test with a missing space that is always true | `ls docker-compose.yml dev.yml production.yml` |
| `tower/` base image | Python and Alpine versions both past end of life. The record names it | `head -1 tower/Dockerfile` |
| Traefik logging | `general.level: DEBUG` with access-log header mode `keep`, which writes every request header including authorisation and cookies | `grep -n 'level:\|defaultmode' charts/traefik/values.yaml` |
| CSI install document | Instructs the reader to put a Proxmox API token into `values.yaml`, which is how the next credential arrives in a public tree | `grep -n token_secret charts/csi/README.md charts/csi/values.yaml` |
| Jellyfin | Runs with `SYS_ADMIN` and a `/dev/dri` host path | `grep -n -A6 securityContext charts/jellyfin/values.yaml` |

Each is a small pull request. The CSI document is the one worth doing early —
it is the instruction that reproduces O1.

### P10 — Rework the network branch

**Blocks on** P0, and on whatever base P0 leaves it on. Independent of the
governance items otherwise.

**The finding.** The configuration is structurally sound — a single VLAN map
driven by `for_each`, tokens through `TF_VAR_`, state and secrets ignored. The
policy it encodes contradicts the cluster the same repository deploys.

**Establish it.** Nothing here needs the router. Each is a read of two files
that disagree.

| | The finding | Establish it |
|---|---|---|
| The cluster loses Proxmox | The Kubernetes zones forward only to WAN; the CSI driver reaches Proxmox on the management VLAN | `grep -n 'url:' charts/csi/values.yaml` against `bailey_vlans` and the forwardings in `net/firewall.tf` |
| The cluster loses its cameras | Frigate and go2rtc pull RTSP from a perimeter-video address, which is an isolated zone with no forwarding from Kubernetes | `grep -n 'rtsp://\|host:' charts/frigate/values.yaml` against `isolated_vlans` |
| Most VLANs lose DNS | Semi-trusted and isolated zones set `input` to drop. The only input rule opened is DHCP. The resolver serves DNS on its own port and nothing allows it | `grep -n 'input\|dest_port' net/firewall.tf` |
| A rule that is not the rule it describes | The lateral-movement rule matches a source zone with no destination, which reads as an input rule rather than a forward rule. Lateral movement is already blocked by the zone's forward policy, so it adds an ordering hazard against the DHCP accept without adding protection. Its comment says it logs; nothing logs | `grep -n -A8 drop_lateral net/firewall.tf` |
| VLAN 8 has two addressings | The VLAN map assigns one subnet to VLAN 8; the Talos virtual machines are tagged onto VLAN 8 and addressed from another | `grep -n 'vlan_id\|ip_config' -A4 tofu/moat/vm.tf` against `net/variables.tf` |

**Also.** The audio, lighting, video and infrastructure VLANs carry `/16`
netmasks, which makes each a very large layer-two broadcast domain for exactly
the protocols — mDNS, Dante, xLights — that flood it. The management VLAN is
fully trusted, forwarded to WAN, and is the untagged default on most switches.
The VLAN table exists in three places: the source spreadsheet, the plan
document, and the configuration. The plan document is committed working notes,
with unchecked boxes for work the same branch completes and absolute paths from
one machine — it belongs in a retrospective or nowhere.

**Do.** Add the forwardings and the resolver rule the deployed workloads need,
or state in a record that those workloads move. Reconcile the VLAN 8 addressing
against the infrastructure definitions. Delete the duplicate tables and let the
configuration be the one place. Run `tofu validate` and `tofu plan` and put the
output in the pull request body — the plan document names those commands and
records no result.

**Done when.** A `tofu plan` is in the pull request, and every service the
cluster already runs has a named path to what it depends on.

---

## Blocked on a person, and only a person

These are not risky to automate. Automating them would change what they assert.

| | |
|---|---|
| **Rotate the disclosed credentials** | O1. An agent must not hold or set them |
| **Decide what happens to the history** | O2. Rewrite, accept, or go private — each forfeits something permanent |
| **Choose the records model** | P2. Both are supported; the corpus does not pick |
| **Ratify the adoption record** | It stays Proposed and binds nothing until a second active code owner ratifies it. That is the human gate, and merging to `main` is not it |

## What this page does not cover

- **Whether the cluster matches the tree.** Every finding here is a read of two
  committed files disagreeing, or of a file and a corpus document disagreeing.
  None of it is a read of the running cluster. O3 is the one item that needs
  `kubectl` to resolve, and it is written that way on purpose.
- **The upstream charts.** Every chart here wraps a third-party chart at a
  pinned version. Nothing on this page examines what those pins contain, and the
  adoption record's open rows are where that obligation lives.
- **Anything the gates cannot see.** `uv run qm gates` lists them with what each
  one misses. A green run of all four workflows in P4 leaves the whole of lane O
  and the whole of P10 unmeasured.
