# Codex live hook + handoff certification plan (opt-in)

**Status: prepared fixture / CI validation, NOT a completed Codex live model-turn test.**

PMP's October 19, 2026 native Codex 0.163.0 trust-flow inspection observed that
the background app-server daemon could not resolve a virtualenv-local bare `pmp`
command. PR #2 pins the Python executable and Git worktree. This milestone also
pins the private PMP state directory so the daemon cannot silently use a
different recovery store. These are necessary correctness fixes, **not proof
that Codex executes hooks on a real turn**.

## Operator environment

The ChatGPT/GitHub development environment used for this PR does **not**
have authenticated Codex CLI. Do not label a CI test, manual hook invocation,
or generic wrapper exit as a live vendor hook pass.

The fixture script is designed for a separate Linux/macOS terminal where the
operator already has Codex installed and authenticated. It never calls an LLM;
the operator must start and approve the session explicitly.

### 1. Prepare an isolated fixture

From a reviewed PMP checkout at this PR's commit:

```sh
python -m venv .venv
source .venv/bin/activate
python -m pip install -e . pytest
python -m pytest
python examples/codex_live_probe.py setup
```

The setup prints the fixture root, **private store** and exact
`next_manual_command`. It creates a brand-new temporary Git project
with fictional `AGENTS.md`, `SCOPE.md` and `app.py`, then activates
**only its explicit fixture scope**. It refuses to reuse an existing
`--output` directory and never accesses Gould.

### 2. Choose a mode

**Native mode (experimental):** only if your installed Codex reports the
strictly supported version `codex-cli 0.163.0` on a POSIX host.
For this mode **create a separate new fixture**:

```sh
codex --version
python examples/codex_live_probe.py setup --native
```

The generated native artifacts are local to this new fixture. Carefully
review `.codex/hooks.json` and the Codex `/hooks` trust dialog and accept
only commands you recognize. Native hooks must use a pinned Python interpreter,
an explicit `--project` path, and `PMP_STATE_HOME` for that fixture.
Do not copy machine-specific hook artifacts into Git or another computer.

**Portable wrapper fallback:** use plain `setup` if Codex is newer,
unavailable to native hooks, or native event shapes have not been verified.
The wrapper independently starts a watcher and checkpoints at process exit,
but wrapper-created checkpoints **do not** certify native hook delivery.

### 3. Execute a real, operator-initiated model turn

Copy the printed `next_manual_command` into the local terminal. Use
normal Codex authentication and permission prompts. **No trust, quota,
sandbox, safety or approval bypass flags** are permitted.

In the genuine Codex chat send the printed `manual_prompt`: in the
disposable Git fixture only, edit `app.py` to make `answer()` return
`42`, execute a local Python assertion and stop. The baseline returns 41.
A screenshot of `/hooks` state (with personal/account details redacted)
or a safely redacted audit note can corroborate hook activation; do not
collect chat transcripts or credentials.

Close the agent normally and, from the original PMP checkout, run:

```sh
python examples/codex_live_probe.py inspect --fixture /path/printed/by/setup
```

The read-only inspector reports whether the fixture edit exists, number
of valid private checkpoints, whether any reason begins with
`adapter lifecycle:`, and uncertainty. It **deliberately always
sets** `live_vendor_hook_provenance_certified=false`: a hand-invoked
hook can create the same named checkpoint. An operator must correlate
the real Codex trust/event evidence separately.

### 4. Verify recovery and context continuity

Review `pmp brief`, `pmp resume` and `pmp history` on the fixture with
the **same** `PMP_STATE_HOME`. A private checkpoint should be available
after a genuine native Stop/SessionEnd hook; a generic wrapper creates
a different type of checkpoint. Never confuse either with a complete
source backup, a Git commit, or approved production deployment.

For the second-session continuation test, **optionally** start a new
Codex session in the same disposable fixture and ask it to read the
canonical policy and `pmp brief`, confirm `answer()==42`, and explain
the remaining work without editing. This is another genuine model turn
and can consume credits. No second turn is required for the CLI fixture
or automated CI.

### 5. Evidence and exit criteria

Classify each finding as one of:

| Gate | Evidence |
| --- | --- |
| Fixture isolation | Absolute paths point to new disposable root and private store |
| Hook wiring | Reviewed native hook commands resolve their exact Python and worktree |
| Real hook delivery | Actual Codex model turn, trusted `/hooks`, correlated generated checkpoint |
| Source recovery | Subsequent read-only inspect resolves the exact worktree and existing edit |
| New agent continuation | A second real agent session demonstrates correct independent recovery |
| Usage cost | Provider-reported tokens/credits, where available, not JSON bytes |

Only claim **native live certification** if all relevant runtime provenance
has been independently observed. Do not publish user paths, auth state,
provider transcripts or full runtime logs. Never auto-merge or tag a
stable release from this fixture. Manual removal of the disposable
folder is optional after evidence review; the script does not delete it.

## Automated CI scope

`tests/test_codex_live_probe.py` verifies fixture creation, refusal to
overwrite an existing directory and read-only inspection. Additional
hook tests verify state-home propagation even when the launching daemon
has a different `PMP_STATE_HOME`. The existing Linux/macOS/Windows CI
matrix tests project logic, but **does not run or authenticate Codex**.
