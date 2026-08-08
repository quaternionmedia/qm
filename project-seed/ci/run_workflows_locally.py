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
  - Secrets, tokens and anything network-gated by them.
  - Event payloads beyond the few fields substituted below.

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
import subprocess
import sys
import tempfile
from pathlib import Path

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


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--event", default="pull_request")
    ap.add_argument("--ref", default="main", help="branch for a push event")
    ap.add_argument("--base-ref", default="main", help="PR base branch")
    ap.add_argument("--workflows", default=".github/workflows")
    args = ap.parse_args()
    _force_utf8_output()

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
            for step in job.get("steps", []):
                label = step.get("name") or step.get("uses", "<step>")
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
                env = {**os.environ, "GITHUB_OUTPUT": str(out_file)}
                env.update(
                    {k: str(v) for k, v in (step.get("env") or {}).items()}
                )
                env.update({k: str(v) for k, v in (wf.get("env") or {}).items()})
                proc = subprocess.run(
                    ["bash", path], env=env, capture_output=True, text=True
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
