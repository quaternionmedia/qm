# Family integrations, reviewed 2026-11-05

Each family member apothecary names, read against the member itself. The roster is
the corpus's `ci/workspace.yaml` at `1d8ae63`. What a member has is read from what
GitHub holds, so work on someone's disk and not pushed is not seen here.

## How each stands

| Member | Family | The seam | Holds today? | How it was asked |
|---|---|---|---|---|
| carlos | instruments | `wiring/`, `rig/`, `serve --carlos`: a rig held and drawn | Works; **does not keep `family/1`**; only on unmerged branches | `tests/e2e/test_carlos_bench.py` and `test_carlos_concert.py` with `CARLOS_CHECKOUT`, `hearth check` on it running |
| hearth | not on the roster | The contract and the coordinator, a pinned git dependency | **Works as the hub's library** | `hearth check --hub` on `serve --demo --carlos` |
| qmcp | core | `finders/qmcp.py`, the `qm.vision` contract | **Simulated only**, and says so | qmcp's tree on `main`: no vision path, and no branch named for it |
| datum | irl | Parts `datum_core`, `datum_cap`, `datum_bench`; datum pins apothecary | Works; its pin is far behind | datum's `enclosure.yml`, green on 2026-10-31; `3837828` is on `main` |
| rad | core | `menu.py`, `static/ring.js` follow its nine-cell record | **Follows the record, replays nothing** | rad's `conformance/vectors.json` against `tests/conformance/nine_cells.json` |
| joe, vox, alfred, otto, ira, ShowRunner, uPhonor | irl, some with another | Rows in the hub's plan | Not built | No code here names them |
| stomp, leo, qmetronome, aes, benchmark, codecartographer | various | Mentions in plans and history | No seam | The word in docs only, or another sense of it |

Gridfinity is a submodule and is not on the roster, so it is not reviewed here.

## Findings

**1. Carlos works with apothecary and does not keep the contract.** The three
end-to-end tests pass against a real carlos on `feat/hold-the-rig`, and a hold reached
it through the hub with status 200. `hearth check http://127.0.0.1:4186` says *does
not conform*, with 8 of 11 checks failing:

```
fail  GET /family/identity is 200 with an object -- 404
fail  GET /family/events streams the state at once -- ValueError('404 application/json')
```

The other failures follow from the missing identity. A newer branch does not explain
it: no branch on GitHub has either route, while the same search finds `family/cue` on
both family branches. So the hub's audit keeps carlos's deliveries with no instance.

**2. What apothecary needs of carlos is on unmerged drafts.** Carlos's default branch
`they` has no `/family/cue`. Everything is on `feat/hold-the-rig`, carlos#22, a draft
stacked on carlos#21, itself a draft on an open branch. `CARLOS_CHECKOUT` tests skip
without a checkout of that branch, so a suite that skips them says nothing about it.

**3. No published member is on hearth.** All 56 branches of carlos, ShowRunner,
ShowStopper, joe and leo were read: none depends on `qm-hearth`, and none holds a
`family/coordinator.py`. hearth's adoption record says those four keep the contract
through it and that ShowRunner runs a copy. The ordinary explanation is work in
checkouts that is not pushed: hearth's demo runs each member from a folder a developer
names, and the record says members reach hearth by a path source. This does not show
the record false. It shows apothecary is the first published user of hearth, so nothing
else published would notice a change to `family/1`.

**4. hearth has no release and no place on the roster.** It carries a development
version and no tag, so apothecary pins a revision. `ci/workspace.yaml` has no row for
it, though `status/governance.yaml` tracks its branch, and `qm interop` finds a clone
through the roster. Its vector set keeps cases under `member` and `hub`, while
`qm interop --verify` counts a publisher's `cases`, so a total for `family/1` cannot
be read until one of them moves. Its record names a second exemplar as a trigger for
rereading its scope: this one needed no change in hearth, so that scope held.

**5. `qm.vision` has one side.** apothecary's client and its simulated qmcp are the
only places that contract exists. The client says an address is unreachable until
qmcp serves MCP, so nothing false is claimed. The risk is drift: the first real qmcp
tool is written against a contract only this repository has read.

**6. The ring follows rad's record and replays none of rad's cases.** rad publishes a
vector set, and `ci/interop-registry.yaml` lists codecartographer and dossier against
it. apothecary generates its own vectors from its own functions, at a version of its
own, and is not on the surface, which is accurate: it claims nothing it has not
replayed. Whether it should replay them is a question for a person. Beside this,
carlos's `tests/test_rad.py` does replay rad and is also not on that surface.

**7. Datum's pin is far behind and its gate still passes.** `APOTHECARY_PIN` is
`3837828`, on `main` and well behind it, and datum's handoff still names a branch from
September. The gate proves that commit renders the parts, and nothing newer. Its
release clause waits on a tag, and apothecary has no tag.

**8. The corpus's picture of apothecary is behind it.**

- The roster states phase `v0.0.2`, the project page shows it, `pyproject.toml` says
  `0.1.0`, and the repository has no tags. A phase is a stated claim and a tag is a
  different one, so this is not a contradiction, but a reader will take it for one.
- `project/apothecary` was last moved on 2026-08-12, and the commit this repository
  pins is on the head of the qm#211 draft instead of that branch. Most of the project's
  records are on open pull requests there, so the corpus's status counts two.
- The pictures `ci/showcase.yaml` names all exist on `main`.
- `qm family-demo` is the performing family's alone: one hub by name, and its member
  list is those families. An `irl` phase needs that harness to accept a second hub.

## Registered, as of this review

Before it, apothecary was named the irl hub nowhere: the roster's row said `family: irl`
and the interop registry had no `family/1` surface. The hub now answers at `/family/`
([docs/family.md](../../../../docs/family.md)), and `hearth check --hub` passes it. The roster's row,
the registry's surface and hearth's own table are pull requests in those repositories,
and apothecary's draft record is one on its project branch, each claiming what this
one makes true.
