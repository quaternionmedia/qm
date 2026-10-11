"""The voice loop's open set and the durable-text sweep, run together as if every stack had merged.

    uv run python demo/voice_loop.py

Run from qm's demo checkout. Six acts, each run rather than described, against the
pushed heads of the demo branch that checkout has out:

  0. every clone at origin's demo head and clean, which open pull requests each
     head carries, and the integration worktree rebuilt from pushed refs if any
     head moved;
  1. the docstring that started the sweep, before and after, scored by the gate;
  2. a qmcp server from the integration worktree, asked what that docstring says;
  3. one whole spoken session, offline, through qmcp and vox;
  4. one topology drawn by three windows, which must agree;
  5. the gate over each repository: what it reads, and what is left.

It runs nothing that speaks, listens, spends or pushes. The server binds loopback
on a free port over a database made for the run, and stops when the act ends.

Where things are looked for:

- The sibling clones sit beside qm's primary clone or one level up, as `qm demo`
  looks for them; `QM_SIBLINGS` (os.pathsep-separated directories) replaces that.
- Each of qmcp, joe and vox has the demo branch checked out in a worktree of its
  clone, the primary one included; the run names the command when one is missing.
- The integration worktree is `<qmcp clone>.worktrees/integration`, created on the
  first run: qmcp's demo head with `vendor/vox` at vox's demo head and
  `governance/qm` at qm's `project/qmcp` with qm's demo head merged in, the pins a
  bump leaves once the set lands.
"""
import ast
import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

QM_DEMO = Path(__file__).resolve().parents[1]
ENV = {k: v for k, v in os.environ.items() if k != "VIRTUAL_ENV"}

sys.path.insert(0, str(QM_DEMO / "project-seed" / "ci"))
import check_timeless  # noqa: E402

BEFORE_REF = "origin/feat/topology-voice"
BEFORE_PATH = "qmcp/topology_designs.py"


def act(n, title):
    print(f"\n{'=' * 78}\n{n}. {title}\n{'=' * 78}")


def git(cwd, *args):
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, encoding="utf-8",
                          check=True).stdout


def rev(cwd, ref):
    return git(cwd, "rev-parse", ref).strip()


def docstring(source):
    node = ast.parse(source).body[0]
    return node.value.value if isinstance(node, ast.Expr) else ""


def sibling_roots():
    override = os.environ.get("QM_SIBLINGS", "")
    if override.strip():
        return [Path(part) for part in override.split(os.pathsep) if part.strip()]
    primary = Path(git(QM_DEMO, "rev-parse", "--path-format=absolute", "--git-common-dir").strip()).parent
    return [primary.parent, primary.parent.parent]


def clone_of(name):
    for base in ROOTS:
        if (base / name / ".git").exists():
            return base / name
    raise SystemExit(f"{name}: no clone beside qm's ({', '.join(str(r) for r in ROOTS)}); set QM_SIBLINGS")


def demo_checkout(clone):
    for block in git(clone, "worktree", "list", "--porcelain").split("\n\n"):
        fields = dict((line.split(" ", 1) + [""])[:2] for line in block.splitlines() if line)
        if fields.get("branch") == f"refs/heads/{DEMO}":
            return Path(fields["worktree"])
    raise SystemExit(f"{clone.name}: no worktree has {DEMO} checked out. "
                     f"`git -C {clone} worktree add ../{clone.name}.worktrees/demo {DEMO}` makes one.")


DEMO = git(QM_DEMO, "rev-parse", "--abbrev-ref", "HEAD").strip()
if not DEMO.startswith("demo/"):
    raise SystemExit(f"{QM_DEMO} has {DEMO} checked out; run this from qm's demo checkout")
ROOTS = sibling_roots()
QMCP = demo_checkout(clone_of("qmcp"))
CLONES = {"qm": QM_DEMO, "qmcp": QMCP, "joe": demo_checkout(clone_of("joe")),
          "vox": demo_checkout(clone_of("vox"))}
INTEGRATION = clone_of("qmcp").parent / f"{clone_of('qmcp').name}.worktrees" / "integration"

# 0 -------------------------------------------------------------------------
act(0, "Every head is the pushed one")
for name, root in CLONES.items():
    git(root, "fetch", "-q", "origin")
    local, pushed = rev(root, "HEAD"), rev(root, f"origin/{DEMO}")
    dirty = git(root, "status", "--porcelain").strip()
    if local != pushed or dirty:
        raise SystemExit(f"{name}: {root} is at {local[:7]}, origin's {DEMO} at {pushed[:7]}; "
                         f"{'dirty' if dirty else 'clean'}. Bring it to the pushed head first.")
    carried, missing = [], []
    listing = subprocess.run(["gh", "pr", "list", "--state", "open", "--limit", "200",
                              "--json", "number,headRefOid"], cwd=root, capture_output=True, text=True)
    for pr in json.loads(listing.stdout or "[]") if listing.returncode == 0 else []:
        known = subprocess.run(["git", "cat-file", "-e", pr["headRefOid"]], cwd=root).returncode == 0
        inside = known and subprocess.run(["git", "merge-base", "--is-ancestor", pr["headRefOid"], "HEAD"],
                                          cwd=root).returncode == 0
        (carried if inside else missing).append(pr["number"])
    open_prs = ("open pull requests unread" if listing.returncode
                else f"carries {len(carried)} open pull request(s)"
                + (f"; not #{', #'.join(str(n) for n in sorted(missing))}" if missing else ""))
    print(f"  {name:5} {local[:7]}  == origin/{DEMO}, clean; {open_prs}")

vox_head = rev(CLONES["vox"], f"origin/{DEMO}")
qm_head = rev(QM_DEMO, f"origin/{DEMO}")
qmcp_head = rev(QMCP, f"origin/{DEMO}")
if not INTEGRATION.exists():
    git(QMCP, "worktree", "add", "-q", "--detach", str(INTEGRATION), qmcp_head)
gov = INTEGRATION / "governance" / "qm"


def current():
    try:
        head = rev(INTEGRATION, "HEAD")
        pinned = git(INTEGRATION, "log", "-1", "--format=%s").startswith("Integration pins")
        base = rev(INTEGRATION, "HEAD^") if pinned else head
        parents = git(gov, "log", "-1", "--format=%P").split()
        return (base == qmcp_head and rev(INTEGRATION / "vendor" / "vox", "HEAD") == vox_head
                and len(parents) == 2 and parents[1] == qm_head
                and parents[0] == rev(gov, "origin/project/qmcp"))
    except subprocess.CalledProcessError:
        return False


if gov.exists():
    git(gov, "fetch", "-q", "origin")
if current():
    print(f"  integration worktree current: qmcp {qmcp_head[:7]}, vox {vox_head[:7]}, "
          f"governance {rev(gov, 'HEAD')[:7]} (project/qmcp + qm {qm_head[:7]})")
else:
    print("  integration worktree: rebuilding from the pushed heads")
    git(INTEGRATION, "checkout", "-q", "--detach", qmcp_head)
    git(INTEGRATION, "submodule", "update", "--init", "-q")
    vox_dir = INTEGRATION / "vendor" / "vox"
    git(vox_dir, "fetch", "-q", "origin", DEMO)
    git(vox_dir, "checkout", "-q", vox_head)
    git(gov, "fetch", "-q", "origin")
    git(gov, "fetch", "-q", "origin", DEMO)
    git(gov, "checkout", "-q", "--detach", "origin/project/qmcp")
    git(gov, "merge", "-q", "--no-edit", qm_head)
    git(INTEGRATION, "add", "governance/qm", "vendor/vox")
    git(INTEGRATION, "commit", "-q", "-m", "Integration pins: vox and the corpus at their pushed demos")
    print(f"  rebuilt: qmcp {qmcp_head[:7]}, vox {vox_head[:7]}, governance {rev(gov, 'HEAD')[:7]}")
subprocess.run(["uv", "sync", "--all-extras", "-q"], cwd=INTEGRATION, env=ENV, check=True)

# 1 -------------------------------------------------------------------------
act(1, f"The docstring that started it: {BEFORE_PATH}")
shown = subprocess.run(["git", "show", f"{BEFORE_REF}:{BEFORE_PATH}"], cwd=QMCP, capture_output=True,
                       text=True, encoding="utf-8")
if shown.returncode:
    print(f"  skipped: {BEFORE_REF} is not on origin, so there is no before to show")
else:
    before = shown.stdout
    after = (QMCP / BEFORE_PATH).read_text(encoding="utf-8")
    for label, text in ((f"before ({BEFORE_REF})", before), ("after (the demo)", after)):
        found, _ = check_timeless.scan(BEFORE_PATH, text)
        print(f"  {label}: module docstring {len(docstring(text).splitlines())} lines; "
              f"the gate finds {len(found)} in the file")
    print("\n  before, the lines the gate flags:")
    source_lines = before.splitlines()
    for f in check_timeless.scan(BEFORE_PATH, before)[0]:
        print(f"    {f.line:4} {f.kind:9} | {source_lines[f.line - 1].strip()[:88]}")
    print("\n  after, whole:")
    for line in docstring(after).splitlines():
        print("    | " + line)

# 2 -------------------------------------------------------------------------
act(2, "What that docstring says, asked of a running server")
with socket.socket() as s:
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
scratch = Path(tempfile.mkdtemp(prefix="qmcp-demo-"))
env = dict(ENV, QMCP_DATABASE_URL=f"sqlite+aiosqlite:///{(scratch / 'demo.db').as_posix()}")
server = subprocess.Popen(["uv", "run", "qmcp", "serve", "--host", "127.0.0.1", "--port", str(port)],
                          cwd=INTEGRATION, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
base = f"http://127.0.0.1:{port}"


def call(method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(base + path, data=data, method=method,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b"{}")


try:
    for _ in range(120):
        try:
            if call("GET", "/health")[0] == 200:
                break
        except OSError:
            time.sleep(0.5)
    else:
        raise SystemExit("the server did not answer /health")
    code, health = call("GET", "/health")
    print(f"  qmcp on {base}, its own database; /health {code}")

    code, council = call("POST", "/v1/topologies", {
        "name": "the-council", "description": "nine perspectives and an arbiter", "topology_type": "council"})
    cap = council["capability"]
    print(f"\n  POST /v1/topologies  the-council (council)          -> {code}")
    print(f"    capability.status   {cap['status']}")
    print(f"    saved_anyway        {cap['saved_anyway']}")
    print(f"    address             {council.get('address')!r}")
    print(f"    address_unknown     {council.get('address_unknown')!r}")

    code, advisors = call("POST", "/v1/topologies", {
        "name": "the-advisors", "description": "nine perspectives, no verdict", "topology_type": "council",
        "config": {"arbiter_can_override": False}})
    print(f"\n  POST /v1/topologies  the-advisors (arbiter cannot override) -> {code}")
    print(f"    capability.option   {advisors['capability']['option']}")
    print(f"    capability.status   {advisors['capability']['status']}, "
          f"refusal {advisors['capability']['refusal']!r}")

    code, judged = call("GET", "/v1/topologies/the-advisors?act=ratify%20a%20record")
    print(f"\n  GET  /v1/topologies/the-advisors?act=ratify a record  -> {code}")
    print(f"    refusal             {judged['capability']['refusal']}")

    code, listing = call("GET", "/v1/topologies")
    print(f"\n  GET  /v1/topologies  -> {code}: {[row['name'] for row in listing['topologies']]}")
    code, refused = call("POST", "/v1/topologies", {
        "name": "ghost", "description": "names a missing component", "topology_type": "crosscheck",
        "config": {"components": [{"name": "no-such-checker"}]}})
    print(f"  POST a design naming a missing component -> {code}: {refused.get('detail')}")
finally:
    server.terminate()
    server.wait(timeout=30)
    shutil.rmtree(scratch, ignore_errors=True)
    print("  server stopped")

# 3 -------------------------------------------------------------------------
act(3, "One whole spoken session, offline: qmcp and vox at their demo heads")
done = subprocess.run(["uv", "run", "qmcp", "cookbook", "converse"], cwd=INTEGRATION, env=ENV,
                      capture_output=True, text=True, encoding="utf-8")
for line in [line for line in done.stdout.splitlines() if line.strip()][:60]:
    print("  " + line)
print(f"  (exit {done.returncode}; vox from {git(INTEGRATION, 'submodule', 'status', 'vendor/vox').split()[0][:7]})")

# 4 -------------------------------------------------------------------------
act(4, "One topology, three windows")
done = subprocess.run(["uv", "run", "qm", "demo", "--fixture"], cwd=QM_DEMO,
                      env=dict(ENV, QM_SIBLINGS=os.pathsep.join(str(r) for r in ROOTS)),
                      capture_output=True, text=True, encoding="utf-8")
for line in done.stdout.splitlines():
    if "agree" in line or line.startswith("[") or "What this did not establish" in line:
        print("  " + line.strip())
print(f"  (exit {done.returncode})")

# 5 -------------------------------------------------------------------------
act(5, "The gate, over each repository at its demo head")
for name, root in CLONES.items():
    found, allowed = check_timeless.findings(root)
    files = sorted({f.path for f in found})
    print(f"  {name:5} {git(root, 'rev-parse', '--short', 'HEAD').strip()}  {len(found):3} finding(s) in every tracked line"
          + (f"  -- {', '.join(files[:4])}{' ...' if len(files) > 4 else ''}" if files else ""))
found, _ = check_timeless.findings(QM_DEMO, "origin/main")
print(f"\n  qm demo, lines added since main: {len(found)} finding(s)")
