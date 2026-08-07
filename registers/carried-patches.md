# Carried-Patch Register (org-level)

Every patch any QM project applies at build time, per the contribution and
sponsorship record. A carried patch is a commitment made by the org. A
build-time patch absent from this table is a lint failure in the carrying
project. Reviewed quarterly; the promote-or-drop trigger fires at two
quarters without upstream movement.

| Upstream | Patch (fork branch) | Upstream PR | Carrying project | Since | Status | Quarterly notes |
|---|---|---|---|---|---|---|
| [awtkns/fastapi-crudrouter](https://github.com/awtkns/fastapi-crudrouter) (MIT) | [quaternionmedia/fastapi-crudrouter](https://github.com/quaternionmedia/fastapi-crudrouter) `motor-reupdate` — Motor/Beanie backend support | *none* | alfred | 2021-11-14 | `unoffered` | Surfaced by alfred's constitution adoption. Installed at build time via a `git+https` dependency in `pyproject.toml`. Carried since 2021-11-14; pinned to `motor-reupdate` since 2023-03-19. No pull request has ever been opened upstream. Upstream is unarchived and MIT-licensed but has had no push since 2023-11-01. Promote-or-drop is long past due: the trigger fires at two quarters, and this is well beyond that. |

**Status values:** `unoffered`, `pr-open`, `pr-merged (archive fork)`,
`upstream-stalled`, `promoted (QM fork)`, `dropped`.

`unoffered` covers a patch carried without ever having been proposed
upstream. The other five values all presuppose that a contribution was
attempted, so the first real entry in this register had no honest status to
take. Recording it as `upstream-stalled` would have credited QM with an
attempt it never made, which is the opposite of what this register is for.
`unoffered` is the state the contribution record's remediation clause exists
to eliminate, so an entry should not rest here quietly: it is a starting
state, not a resting one.
