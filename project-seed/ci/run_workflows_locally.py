#!/usr/bin/env python3
"""Run this repository's GitHub Actions workflows locally, before opening a PR.

SEED FILE, run in place: a forking project runs it out of the governance
submodule. Nothing copies it, and it is not a gate -- it is the thing you do
before claiming a gate passes.

The point is narrow and worth stating. Reading a workflow and running the
commands you think it contains is not the same as running the workflow: the
expression syntax, the step ordering, the base-ref selection and the guards
are all places where the file does something other than what it looks like it
does. Every claim of "CI is green" made without executing the steps is a claim
about a file that was read, not a pipeline that ran.

What this does NOT reproduce, and where it can therefore be wrong:

  - `uses:` steps. actions/checkout and actions/setup-python are environment,
    not logic; the working tree stands in for them. A workflow whose behaviour
    depends on checkout options (fetch-depth, submodules) is only partly
    exercised here.
  - The runner image. Ubuntu tool versions differ from a developer machine,
    which is the usual reason a locally-green step fails in CI.
  - Secrets, tokens and anything network-gated by them. A step whose `env:` fills
    from `github.token` or `secrets.*` runs with that variable DROPPED, and the
    drop is printed; the step then uses whatever credential this machine has.
  - Event payloads beyond the few fields substituted below.
  - `paths:` and `types:` trigger filters. `applies()` reads only `branches:`, so
    a workflow GitHub would skip for touching no matching path is executed here.
    That errs toward running too much, which is the safe direction, but it means
    a green run here does not prove the workflow would have been triggered.

So a pass here is evidence, not proof.

A failure is not proof either, and saying otherwise was wrong: a step can fail
locally for reasons the runner image does not have -- missing browsers, no
display, a different OS. Apothecary's suite fails here and is green in CI for
exactly that reason. A local failure is a question, and the answer is either a
defect or a difference between the environments. Both are worth knowing; only
one is a defect.

Usage:
    python run_workflows_locally.py                     # simulate a PR into main
    python run_workflows_locally.py --event push --ref main
    python run_workflows_locally.py --base-ref origin/main
"""

from __future__ import annotations

import argparse
import fnmatch
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# Windows ships an `bash.exe` App Execution Alias that launches WSL. It is on
# PATH for every account, and it is not a POSIX shell this can run a workflow
# step in: with no WSL distribution installed it dies with
# `execvpe(/bin/bash) failed`, and with one installed it would run the step in
# a different filesystem. Either way the failure is reported against the step.
WSL_ALIAS_DIR = "windowsapps"


def resolve_bash() -> str:
    """An absolute path to a POSIX bash, never the name `bash`.

    Passing the bare name leaves the choice to PATH ordering, and that ordering
    is not stable: the same repository resolves to Git's bash under a plain
    interpreter and to the WSL alias under `uv run`, which prepends a venv and
    shifts everything after it. The symptom is four workflow steps failing with
    a WSL relay error that names no step and no workflow.

    `QM_BASH` overrides, for a machine whose shell is somewhere unusual.
    """
    override = os.environ.get("QM_BASH")
    if override:
        return override

    candidates = [shutil.which("bash")]
    # Git for Windows, in the two places its installer puts it. Listed after
    # PATH so a deliberate `bash` on PATH still wins.
    for base in (os.environ.get("PROGRAMFILES", r"C:\Program Files"),
                 os.environ.get("LOCALAPPDATA", "")):
        if base:
            candidates.append(str(Path(base) / "Programs" / "Git" / "usr" / "bin" / "bash.exe"))
            candidates.append(str(Path(base) / "Git" / "usr" / "bin" / "bash.exe"))

    for candidate in candidates:
        if not candidate:
            continue
        # The alias is a zero-byte reparse point under WindowsApps. Rejecting it
        # by directory is cruder than probing it and does not need a subprocess
        # per run.
        if WSL_ALIAS_DIR in candidate.replace("/", "\\").lower():
            continue
        if Path(candidate).is_file():
            return candidate

    # Naming the name is the last resort and is reported as such: a runner that
    # silently fell back here would produce exactly the confusing failure this
    # function exists to remove.
    print(
        "  - [env ] no POSIX bash found; falling back to `bash` on PATH. If steps "
        "fail with a WSL relay error, set QM_BASH to your shell.",
        file=sys.stderr,
    )
    return "bash"

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("pyyaml is required: pip install pyyaml")


def _force_utf8_output() -> None:
    """Windows consoles default to a legacy codepage, and a workflow name with
    an emoji in it then crashes the runner mid-report -- which looks like the
    workflow failing rather than the tool failing. Names are data; the tool
    reads them, so it has to survive them."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8", errors="replace")


def triggers(workflow: dict) -> dict:
    # `on:` parses as the boolean True under YAML 1.1.
    return workflow.get("on", workflow.get(True)) or {}


def applies(wf: dict, event: str, ref: str, base_ref: str) -> tuple[bool, str]:
    on = triggers(wf)
    if event not in on:
        return False, f"not triggered by {event}"
    spec = on[event] or {}
    branches = spec.get("branches") if isinstance(spec, dict) else None
    if not branches:
        return True, ""
    target = base_ref if event == "pull_request" else ref
    if any(fnmatch.fnmatch(target, pat) for pat in branches):
        return True, ""
    return False, f"{event} branches {branches} do not match {target!r}"


# An `env:` value the runner would fill from something that does not exist off
# the runner: the installation token, and any secret. There is no correct local
# value for these -- and the two wrong ones both cost a real failure.
#
# Setting the literal expression text is what this script did, and `gh` duly
# sent the characters `${{ github.token }}` as a bearer token and got
# `Bad credentials (HTTP 401)`. That reads as "the slot check is broken", which
# is a false red about a check that was fine.
#
# Measured, on this machine, against `gh api repos/quaternionmedia/qm`: with
# GH_TOKEN unset the call succeeds from the keyring credential, with GH_TOKEN
# set to the empty string it also succeeds, and only the literal expression
# gives the 401. So emptying the variable would have been enough for `gh`
# specifically -- but it relies on one tool choosing to treat empty as absent,
# which is a courtesy and not a rule, and it leaves nothing in the output
# saying a workflow-declared variable went unfilled.
#
# So the variable is dropped from the environment entirely, and the drop is
# printed. The step then runs against whatever this machine actually has, which
# is the only honest local answer, and the line in the output says which fact
# came from the machine rather than from the workflow.
UNAVAILABLE_LOCALLY = re.compile(r"^(github\.token|secrets\.\w+)$")


def step_env(
    block: dict, ctx: dict, outputs: dict
) -> tuple[dict[str, str], list[tuple[str, str]]]:
    """Resolve an `env:` block, and say which keys this machine must supply.

    Returns the resolvable variables, and the (key, expression) pairs whose
    value only exists on a GitHub runner and so must not be invented here.
    """
    resolved: dict[str, str] = {}
    dropped: list[tuple[str, str]] = []
    for key, raw in block.items():
        text = str(raw)
        exprs = re.findall(r"\$\{\{(.+?)\}\}", text)
        if any(UNAVAILABLE_LOCALLY.fullmatch(e.strip()) for e in exprs):
            dropped.append((key, exprs[0].strip()))
            continue
        # An expression this script does not model -- a pull-request event
        # payload field, say -- resolves to empty, which is what the runner
        # itself does for a `push` where no pull request exists.
        for expr in exprs:
            key_ = expr.strip()
            value = outputs.get(key_, ctx.get(key_, ""))
            text = text.replace("${{" + expr + "}}", str(value))
        resolved[key] = text
    return resolved, dropped


def substitute(script: str, ctx: dict, outputs: dict) -> str:
    """Resolve the small subset of ${{ }} expressions these workflows use."""

    def resolve(expr: str) -> str:
        expr = expr.strip()
        # steps.<id>.outputs.<name> && format('...{0}', <same>)
        m = re.fullmatch(
            r"(steps\.\w+\.outputs\.\w+)\s*&&\s*format\('([^']*)',\s*\1\s*\)", expr
        )
        if m:
            value = outputs.get(m.group(1), "")
            return m.group(2).replace("{0}", value) if value else ""
        if expr in outputs:
            return outputs[expr]
        if expr in ctx:
            return ctx[expr]
        raise KeyError(expr)

    def repl(m: re.Match) -> str:
        try:
            return resolve(m.group(1))
        except KeyError:
            raise SystemExit(
                f"run_workflows_locally: unsupported expression ${{{{{m.group(1)}}}}}.\n"
                "Add it to substitute() rather than guessing what it evaluates to."
            )

    return re.sub(r"\$\{\{(.+?)\}\}", repl, script, flags=re.S)


def bare_branch(ref: str) -> str:
    """Strip a leading remote name, because GitHub's context never carries one.

    `github.ref_name` and `github.base_ref` hold bare branch names. Passing a
    remote-qualified ref straight through makes this script disagree with the
    runner twice over: the branch filters compare `origin/main` against a
    pattern like `main` and skip the workflow, and any step that prefixes
    `origin/` itself -- adr-lint.yml's base-ref step does -- resolves
    `origin/origin/main` and fails on a ref that cannot exist. This script's
    own usage line offers `--base-ref origin/main`, so that is the documented
    path into both.
    """
    remotes = subprocess.run(
        ["git", "remote"], capture_output=True, text=True
    ).stdout.split()
    for remote in remotes:
        if ref.startswith(f"{remote}/"):
            return ref[len(remote) + 1 :]
    return ref


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--event", default="pull_request")
    ap.add_argument("--ref", default="main", help="branch for a push event")
    ap.add_argument("--base-ref", default="main", help="PR base branch")
    ap.add_argument(
        "--head-ref",
        default="",
        help="PR head branch. Defaults to the branch you are on, which is what a "
        "pull request from this checkout would carry.",
    )
    ap.add_argument("--workflows", default=".github/workflows")
    args = ap.parse_args()
    _force_utf8_output()
    args.ref = bare_branch(args.ref)
    args.base_ref = bare_branch(args.base_ref)

    head = subprocess.run(
        ["git", "rev-parse", "HEAD"], capture_output=True, text=True
    ).stdout.strip()
    ctx = {
        "github.event_name": args.event,
        "github.base_ref": args.base_ref,
        "github.ref_name": args.ref,
        "github.sha": head,
        # A push whose range is unknown locally: the all-zeros sentinel makes
        # the workflow take the same fallback it takes for a new branch.
        "github.event.before": "0" * 40,
    }

    # The same facts the `${{ }}` substitution above already knows, exported the
    # other way a step can read them. A workflow reaching for `$GITHUB_REPOSITORY`
    # rather than `${{ github.repository }}` is doing the same thing, and leaving
    # the variable unset made the step fail on an empty argument -- reported as a
    # step failure, which is a false red. A false red costs as much as a false
    # green here, because it is what teaches a reader to skim past FAIL.
    #
    # `GITHUB_REPOSITORY` is derived from origin rather than guessed: a clone
    # whose remote is a fork legitimately produces a different answer, and the
    # step should see the one it would see in that fork.
    origin = subprocess.run(
        ["git", "remote", "get-url", "origin"], capture_output=True, text=True
    ).stdout.strip()
    slug = re.sub(r"^(?:git@[^:]+:|https?://[^/]+/)", "", origin).removesuffix(".git")
    # GITHUB_HEAD_REF is the branch you are actually on, not `--ref`. The two
    # differ on purpose: `--ref` decides which workflows a *push* event matches
    # and defaults to the default branch so a local run exercises everything,
    # while the head ref answers "what would this pull request be from", which
    # is only ever the current branch. Exporting `--ref` for both made a step
    # reading $GITHUB_HEAD_REF see `main`, and a base check comparing main to
    # main is a check that cannot fail.
    current = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"], capture_output=True, text=True
    ).stdout.strip()
    gh_env = {
        "GITHUB_REPOSITORY": slug,
        "GITHUB_REF_NAME": args.ref,
        "GITHUB_BASE_REF": args.base_ref,
        "GITHUB_HEAD_REF": args.head_ref or current,
        "GITHUB_SHA": head,
        "GITHUB_EVENT_NAME": args.event,
        "CI": "true",
    }
    if not slug:
        print(
            "  note: no `origin` remote, so $GITHUB_REPOSITORY is empty here.\n"
            "        A step that needs it will fail on the empty value, which is\n"
            "        this environment and not the workflow."
        )

    files = sorted(Path(args.workflows).glob("*.y*ml"))
    if not files:
        return exit_with(f"no workflows in {args.workflows}", 1)

    failures: list[str] = []
    ran = 0
    for f in files:
        wf = yaml.safe_load(f.read_text(encoding="utf-8"))
        ok, why = applies(wf, args.event, args.ref, args.base_ref)
        name = wf.get("name", f.stem)
        if not ok:
            print(f"\n--- SKIP {f.name} ({name}): {why}")
            continue
        print(f"\n=== {f.name} ({name})")
        for job_id, job in wf.get("jobs", {}).items():
            outputs: dict[str, str] = {}
            job_failed = False
            for step in job.get("steps", []):
                label = step.get("name") or step.get("uses", "<step>")
                # Actions halts a job at its first failed step. Running on past
                # one produces the result this script's own shell handling calls
                # the one it must never produce: a downstream step reporting
                # PASS against inputs a real job would never have made. Observed
                # here -- a site build failed for want of the generator, and the
                # two steps after it went green against a leftover `site/`, one
                # of them stamping a draft banner across 24 stale pages.
                #
                # `if:` naming always() or failure() runs anyway, as it does on
                # the runner. No other `if:` expression is evaluated, so a step
                # carrying one is reported rather than guessed at.
                condition = str(step.get("if") or "")
                runs_regardless = "always()" in condition or "failure()" in condition
                if job_failed and not runs_regardless:
                    print(f"  - [skip] {label}")
                    print(f"      a previous step in this job failed, so the runner "
                          f"would not reach this one")
                    continue
                if "run" not in step:
                    print(f"  - [env ] {label}")
                    continue
                script = substitute(step["run"], ctx, outputs)
                with tempfile.NamedTemporaryFile(
                    "w", suffix=".sh", delete=False, newline="\n", encoding="utf-8"
                ) as fh:
                    fh.write(script)
                    path = fh.name
                out_file = Path(tempfile.mkdtemp()) / "gh_output"
                out_file.touch()
                env = {**os.environ, "GITHUB_OUTPUT": str(out_file), **gh_env}
                for block in (wf.get("env") or {}, step.get("env") or {}):
                    resolved, dropped = step_env(block, ctx, outputs)
                    env.update(resolved)
                    for key, expr in dropped:
                        env.pop(key, None)
                        print(f"  - [env ] {label}: ${key} left to this machine ({expr})")
                # Match the runner's shell, or a step that fails halfway
                # through passes here and fails in CI. Actions runs `run:`
                # steps as `bash -e {0}`, and as `bash --noprofile --norc
                # -eo pipefail {0}` where the step asks for `shell: bash`.
                # Plain `bash` has neither, so a failing command mid-step is
                # masked by whatever succeeds after it -- a false local pass,
                # which is the one result this script must never produce.
                shell = resolve_bash()
                if (step.get("shell") or "").strip() == "bash":
                    argv = [shell, "--noprofile", "--norc", "-eo", "pipefail", path]
                else:
                    argv = [shell, "-e", path]
                # `working-directory` decides where the step runs, and ignoring
                # it silently runs the command somewhere else. That is not a
                # near miss: `npm ci` in a repository root whose lockfile lives
                # in web/ reports "no package-lock.json" -- a confident failure
                # about a file that exists, in a step that passes in CI. The
                # reverse is worse, since a command that happens to succeed in
                # the wrong directory reports a pass nobody can trust.
                #
                # Defaults follow the runner: a step's own value wins, then the
                # job's `defaults.run`, then the workflow's.
                where = (
                    step.get("working-directory")
                    or ((job.get("defaults") or {}).get("run") or {}).get(
                        "working-directory"
                    )
                    or ((wf.get("defaults") or {}).get("run") or {}).get(
                        "working-directory"
                    )
                )
                cwd = None
                if where:
                    resolved = (Path.cwd() / str(where)).resolve()
                    if not resolved.is_dir():
                        print(f"  - [FAIL] {label}")
                        print(f"      working-directory does not exist: {where}")
                        failures.append(f"{f.name} :: {job_id} :: {label}")
                        ran += 1
                        job_failed = job_failed or not step.get("continue-on-error")
                        os.unlink(path)
                        continue
                    cwd = str(resolved)
                proc = subprocess.run(
                    argv, env=env, capture_output=True, text=True, cwd=cwd
                )
                ran += 1
                for line in out_file.read_text(encoding="utf-8").splitlines():
                    if "=" in line:
                        k, v = line.split("=", 1)
                        outputs[f"steps.{step.get('id', '?')}.outputs.{k}"] = v
                status = "PASS" if proc.returncode == 0 else "FAIL"
                print(f"  - [{status}] {label}")
                body = (proc.stdout + proc.stderr).strip()
                if body:
                    for line in body.splitlines():
                        print(f"      {line}")
                if proc.returncode != 0:
                    failures.append(f"{f.name} :: {job_id} :: {label}")
                    # `continue-on-error` records the failure and lets the job
                    # carry on, which is what the runner does.
                    job_failed = job_failed or not step.get("continue-on-error")
                os.unlink(path)

    print(f"\n{'=' * 60}")
    if failures:
        print(f"{len(failures)} step(s) failed of {ran} run:")
        for x in failures:
            print(f"  {x}")
        return 1
    print(f"All {ran} executed step(s) passed.")
    print("`uses:` steps and the runner image are not reproduced -- see the module")
    print("docstring. A pass here is evidence, not proof.")
    return 0


def exit_with(msg: str, code: int) -> int:
    print(msg)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
