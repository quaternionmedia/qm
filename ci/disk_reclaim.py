#!/usr/bin/env python3
"""Free space, but only where ci/disk-policy.yaml says it may, and say so first.

Org-level tooling, copied nowhere. The acting half of the disk tooling:
ci/disk_status.py measures and writes a document, ci/disk_dashboard.py renders
it, and this deletes. Three tools rather than one because the tool that can
delete should be the smallest, the most boring, and the one nobody has a reason
to run casually.

IT DOES NOT READ THE STATUS DOCUMENT, AND THAT IS DELIBERATE

The obvious design is to take the document and remove what it lists. This does
not, because that document has a six-hour staleness budget and deletion has
none: a path that was a 40GB browser cache when the document was written may be
a checkout by the time anybody acts on it. So this reads the same policy the
collector reads, resolves it against the filesystem now, and prints what it
found. The two tools agree because they share a policy, never because one
trusts the other's output.

DRY RUN IS THE DEFAULT AND THERE IS NO CONFIGURATION THAT CHANGES THAT

`--apply` is required per invocation. There is no policy key, no environment
variable and no config file that makes deletion the default, because the
failure this guards against is somebody automating the safe-looking form of the
command and later widening the policy.

THE TIERS ARE A RATCHET, NOT A MENU

`--allow rebuilt` permits refetched and rebuilt. `--allow destructive` permits
all three. You cannot permit an expensive tier while excluding a cheap one, so
there is no invocation that empties the recycle bin but leaves a download cache
alone -- which is the shape every "clean up my disk" script eventually grows
into, one urgent afternoon at a time.

Usage:
    python ci/disk_reclaim.py                          # dry run, refetched only
    python ci/disk_reclaim.py --apply
    python ci/disk_reclaim.py --allow rebuilt --apply
    python ci/disk_reclaim.py --target nvidia-ota-artifacts --apply
    python ci/disk_reclaim.py --until-free 60 --allow rebuilt --apply
"""

from __future__ import annotations

import argparse
import os
import shutil
import stat
import sys
from dataclasses import dataclass
from pathlib import Path

import disk_status as ds

CI_DIR = Path(__file__).resolve().parent
CORPUS = CI_DIR.parent


def refuse(path: Path, roots: list[Path]) -> str | None:
    """The reason this path may not be deleted, or None.

    Checked immediately before every removal rather than once at the start.
    These are not hypotheticals: a policy entry whose environment variable is
    unset expands toward a drive root, and `${USERPROFILE}/.gradle/caches` with
    a typo in the tail is `${USERPROFILE}`.
    """
    resolved = path.resolve()

    if resolved.parent == resolved:
        return "it is a filesystem root"
    if resolved == Path.home().resolve():
        return "it is the home directory"
    if resolved in (CORPUS.resolve(), *CORPUS.resolve().parents):
        return "it contains this corpus"
    if ds.inside_corpus(resolved):
        return "it is inside this corpus, which git is responsible for"
    if not any(
        resolved == root.resolve() or root.resolve() in resolved.parents
        for root in roots
    ):
        return (
            "it is not under any root this policy entry declares, so the policy "
            "does not authorise it"
        )
    if ds.is_reparse_point(resolved):
        return "it is a junction or symlink; deleting it would act on its target"
    return None


def force_writable(action, name, exc_info) -> None:
    """Retry one failed removal after clearing the read-only bit.

    Windows refuses to unlink a read-only file, and package caches are full of
    them -- pip and Maven both mark their contents read-only. Without this the
    first such file aborts the whole target and reports a permission error for
    what is really a normal cache.
    """
    try:
        os.chmod(name, stat.S_IWRITE)
        action(name)
    except OSError:
        pass


def remove(path: Path) -> tuple[bool, str | None]:
    """Delete one path. Returns (removed, the reason it was not)."""
    try:
        if path.is_dir() and not ds.is_reparse_point(path):
            if sys.version_info >= (3, 12):
                shutil.rmtree(path, onexc=lambda a, n, e: force_writable(a, n, e))
            else:
                shutil.rmtree(path, onerror=force_writable)
        else:
            os.chmod(path, stat.S_IWRITE)
            path.unlink()
    except OSError as error:
        return False, str(error)
    return not path.exists(), (None if not path.exists() else "it is still there")


def free_on(path: Path) -> int | None:
    try:
        return shutil.disk_usage(str(ds.anchor_of(path))).free
    except OSError:
        return None


def permitted(allow: str) -> list[str]:
    """Every tier up to and including the one asked for. A ratchet, not a menu."""
    return list(ds.SAFETY_TIERS[: ds.SAFETY_TIERS.index(allow) + 1])


# A target that is not on this machine, and one that could not be handled, are
# both "nothing was removed" and they are not the same event. The policy is
# written against an organisation, not a laptop: nobody here has every tool it
# names, so an absent pip cache is the normal state of a machine without pip.
#
# Reporting it as a failure made a dry run exit non-zero on a healthy machine,
# which is the surest way to teach somebody that this tool's exit code means
# nothing. So absence is printed and carried, and only a real failure -- a
# path that would not delete, a prune that errored, a directory that would not
# list -- reaches the exit status.
@dataclass
class Gap:
    """Why an entry produced no paths, and whether that is a problem."""

    reason: str
    absent: bool = False


def units_for(
    entry: dict, search_roots: list[Path], blocked: set[str]
) -> tuple[list[Path], list[Path], Gap | None]:
    """(paths to remove, the roots authorising them, the reason there are none).

    Resolved from the filesystem now, never from a status document. The roots
    travel with the paths so that refuse() can check containment against the
    entry that actually named them.
    """
    kind = entry.get("kind")
    if kind == "glob":
        roots = (
            search_roots
            if entry.get("within") == "search_roots"
            else ds.resolve_roots(entry)[0]
        )
        if not roots:
            return [], [], Gap("no search roots to sweep", absent=True)
        units = ds.units_of_glob(roots, entry.get("patterns") or [], blocked)
        return [Path(u["path"]) for u in units], roots, None

    if kind == "directory_contents":
        roots, gaps = ds.resolve_roots(entry)
        if not roots:
            # resolve_roots only reports two things, and both are absence: a
            # path that is not here, and an environment variable that is not
            # set on this machine.
            return [], [], Gap("; ".join(gaps) or "no roots resolved", absent=True)
        paths = []
        for root in roots:
            try:
                paths.extend(
                    Path(u["path"])
                    for u in ds.units_of_directory(root, entry.get("retain_days"))
                )
            except (OSError, PermissionError) as error:
                return [], roots, Gap(f"could not be listed: {error}")
        return paths, roots, None

    return [], [], Gap(f"kind {kind!r} is not removed by path")


def reclaim_command(entry: dict, apply: bool) -> Gap | None:
    """Hand a target back to the tool that owns it.

    Docker's layers live inside a virtual disk and uv hardlinks its cache into
    live environments; deleting either by path corrupts something that was
    working. The owning tool's own prune is the only correct removal, so the
    policy names it and this runs exactly that.
    """
    requires = entry.get("requires")
    if requires and not shutil.which(requires):
        return Gap(f"{requires} is not on PATH", absent=True)
    argv = [str(a) for a in ((entry.get("reclaim") or {}).get("argv") or [])]
    if not argv:
        return Gap("policy entry has no reclaim.argv")
    if not apply:
        return None
    status, out, err = ds.run(argv)
    if status != 0:
        # The fallback is not decoration. A prune that fails silently -- no
        # stdout, no stderr, just a status -- indexed into an empty list and
        # brought the whole run down with an IndexError, which reads as a bug
        # in the reclaimer rather than a failure in the tool it called.
        first = (err or out or "no output").splitlines()[0]
        return Gap(f"{argv[0]} exited {status}: {first[:160]}")
    return None


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--policy", type=Path, default=CI_DIR / "disk-policy.yaml")
    parser.add_argument(
        "--apply",
        action="store_true",
        help="actually delete. Without it nothing is removed and the plan is printed.",
    )
    parser.add_argument(
        "--allow",
        choices=ds.SAFETY_TIERS,
        default="refetched",
        help="the most expensive tier permitted. Permits every cheaper tier too.",
    )
    parser.add_argument(
        "--target",
        action="append",
        default=[],
        help="run only this policy entry, by name; repeatable",
    )
    parser.add_argument("--search-root", action="append", type=Path, default=[])
    parser.add_argument(
        "--until-free",
        type=float,
        metavar="GB",
        help="stop once the volume holding the corpus has this many GB free",
    )
    args = parser.parse_args(argv)

    policy = ds.load_policy(args.policy)
    search_roots = [p.resolve() for p in args.search_root] or [CORPUS.parent]
    blocked = ds.glob_names(policy)
    tiers = permitted(args.allow)

    entries = [
        e for e in policy.get("reclaimers") or []
        if e.get("safety") in tiers and (not args.target or e["name"] in args.target)
    ]
    named = {e["name"] for e in policy.get("reclaimers") or []}
    for wanted in args.target:
        if wanted not in named:
            sys.exit(
                f"disk_reclaim: no policy entry named {wanted}. "
                f"The policy names: {', '.join(sorted(named))}"
            )

    if args.apply:
        print(f"APPLYING — tiers permitted: {', '.join(tiers)}")
    else:
        print(f"DRY RUN — nothing will be deleted. Tiers permitted: {', '.join(tiers)}")
        print("Pass --apply to act.")
    print()

    before = free_on(CORPUS)
    removed_bytes = 0
    removed_paths = 0
    refused: list[str] = []
    failed: list[str] = []
    absent: list[str] = []

    def record(name: str, gap: Gap) -> None:
        """Print a gap, and file it under absence or failure."""
        print(f"{name}: {'absent' if gap.absent else 'FAILED'} — {gap.reason}")
        (absent if gap.absent else failed).append(f"{name}: {gap.reason}")

    for entry in entries:
        name = entry["name"]
        if entry.get("kind") == "command":
            gap = reclaim_command(entry, args.apply)
            verb = "ran" if args.apply else "would run"
            argv_text = " ".join(str(a) for a in ((entry.get("reclaim") or {}).get("argv") or []))
            if gap:
                record(name, gap)
            else:
                print(f"{name}: {verb} `{argv_text}` [{entry['safety']}]")
            continue

        paths, roots, gap = units_for(entry, search_roots, blocked)
        if gap:
            record(name, gap)
            continue
        if not paths:
            print(f"{name}: nothing to remove")
            continue

        entry_bytes = 0
        entry_paths = 0
        for path in paths:
            reason = refuse(path, roots)
            if reason:
                # Loud, and never silently skipped. A guard that fires without
                # saying so is a policy nobody knows is wrong.
                print(f"  REFUSED {path} — {reason}")
                refused.append(f"{path}: {reason}")
                continue
            size = ds.tree_size(path)[0]
            if not args.apply:
                entry_bytes += size
                entry_paths += 1
                continue
            ok, why = remove(path)
            if ok:
                entry_bytes += size
                entry_paths += 1
            else:
                print(f"  FAILED {path} — {why}")
                failed.append(f"{path}: {why}")

        verb = "removed" if args.apply else "would remove"
        print(
            f"{name}: {verb} {entry_paths} paths, {ds.gb(entry_bytes)} "
            f"[{entry['safety']}]"
        )
        removed_bytes += entry_bytes
        removed_paths += entry_paths

        if args.until_free and args.apply:
            now = free_on(CORPUS)
            if now is not None and now / 10**9 >= args.until_free:
                print(
                    f"\nstopping: {ds.gb(now)} free, at or above the "
                    f"{args.until_free:g}GB asked for"
                )
                break

    print()
    verb = "Removed" if args.apply else "Would remove"
    # The exact count travels beside the rounded one. `0.0GB` is what a 5KB
    # sweep rounds to, and a caller parsing this line -- dossier records it as
    # the run's `claimed` figure -- would store a zero for a run that removed
    # something. The rounded form stays because it is the one a person reads.
    print(
        f"{verb} {removed_paths} paths, {ds.gb(removed_bytes)} "
        f"({removed_bytes} bytes)"
    )

    after = free_on(CORPUS)
    if args.apply and before is not None and after is not None:
        # Measured against the volume rather than summed from the deletions.
        # They disagree whenever something else was writing during the run, and
        # the volume is the number the next build actually meets.
        print(
            f"Free on {ds.anchor_of(CORPUS)}: {ds.gb(before)} -> {ds.gb(after)} "
            f"({ds.gb(after - before)} recovered)"
        )
    elif after is not None:
        print(f"Free on {ds.anchor_of(CORPUS)} now: {ds.gb(after)}")

    if refused:
        print(f"\n{len(refused)} paths refused by the containment guard:")
        for line in refused[:10]:
            print(f"  {line}")
    if absent:
        print(
            f"\n{len(absent)} targets are not on this machine, which is not a "
            "problem — the policy is written for an organisation, not a laptop:"
        )
        for line in absent[:10]:
            print(f"  {line}")
    if failed:
        print(f"\n{len(failed)} targets or paths could not be handled:")
        for line in failed[:10]:
            print(f"  {line}")

    if not args.apply:
        print(
            "\nNothing was deleted. Re-run with --apply."
            + (
                ""
                if args.allow == ds.SAFETY_TIERS[-1]
                else f" Widen with --allow {ds.SAFETY_TIERS[ds.SAFETY_TIERS.index(args.allow) + 1]}."
            )
        )
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
