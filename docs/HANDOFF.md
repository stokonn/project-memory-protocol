# Implementation handoff

Read AGENTS.md, docs/OWNER_SCOPE.md, docs/READINESS.md, docs/VALIDATION.md and
`.pmp/state.json`/`docs/ai/HANDOFF.md` when present. Inspect actual Git status before editing.
This handoff is context. Publication and MIT are authorized by the subsequent explicit
owner instruction recorded in OWNER_SCOPE.md; Goldberg and stable releases remain prohibited.

Completed: deterministic CLI, contracts, durable local/private recovery, reviewed shared
exports, tests and synthetic pilot. Existing owner Goldberg checkout remains untouched.

Next: preserve the authorized public development checkpoint, verify exact remote SHA and
CI, then address acceptance gaps in a later adequately funded session. Native hooks still
require runtime certification; no stable readiness claim.

Local tests: `.venv/bin/python -m pytest`; packaging: `.venv/bin/python -m build`.
Demo: `.venv/bin/python examples/demo.py --goldberg-style`.
Dependencies are installed in `.venv`; offline runtime/test wheels were prepared under
`/tmp/pmp-wheelhouse` for this session. Temporary paths may not survive reboot.
No original conversation is required to inspect/continue this work; approved scope and
unresolved authorization boundaries are in OWNER_SCOPE.md and READINESS.md.

Final local suite now has 90 passing tests, including a checkpoint that survives failure
of its subsequent creation-event append. Local checkpoint sequence preserves ordering
without timestamps even for such orphan records. Persisted relative references use
forward slashes for portability. See docs/FILES.txt for the exact file inventory.
Private self-hosted PMP recovery was copied from the temporary implementation store
to the standard per-user XDG state directory (`~/.local/state/pmp` in this environment).
Use `pmp resume` normally; no PMP_STATE_HOME override is required. Shared exported context
remains in Git. Temporary test environments are independent and disposable.

## Published checkpoint and exact resumption

Repository: https://github.com/stokonn/project-memory-protocol (PUBLIC, MIT).
Published development checkpoint: `d11c00422c3f0f44e18f350e8b0899f148d4cdc1` on main,
confirmed by both Git transport and GitHub API. Subsequent documentation commits may
advance main; inspect the real remote/current HEAD rather than assuming this is latest.
Actions run for that checkpoint: https://github.com/stokonn/project-memory-protocol/actions/runs/39233284582
Initially in progress; do not infer a pass from successful publication.

In the existing checkout, preserve local work before any update:

```sh
cd ~/Projects/project-memory-protocol
git status --short --branch
git rev-parse HEAD
git ls-remote origin refs/heads/main
gh run list --repo stokonn/project-memory-protocol --limit 5
.venv/bin/pmp resume
.venv/bin/pmp check
```

For a fresh checkout:

```sh
git clone https://github.com/stokonn/project-memory-protocol.git
cd project-memory-protocol
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e . pytest build
pmp resume
pmp check
python -m pytest
python -m build
```

On Windows activate with `.venv\Scripts\Activate.ps1` in PowerShell and use an installed
Python 3.11+ interpreter. Fresh clones have shared context but no private local backups.

Next agent: inspect exact-SHA CI jobs and downloadable reports; record any failures before
resuming acceptance work. Native agent hooks still need live disposable-session tests.
Do not treat currently unknown matrix results as certified support. No new features were
started during publication because the owner's Codex quota was nearly exhausted.
Goldberg and stable tags/releases remain outside authorization.

### Observed initial-checkpoint CI jobs


| Job | Status | Conclusion |
| --- | --- | --- |
| test (ubuntu-latest, 3.11) | completed | success |
| test (macos-latest, 3.14) | completed | failure |
| test (windows-latest, 3.14) | in_progress | pending |
| test (windows-latest, 3.11) | in_progress | pending |
| test (ubuntu-latest, 3.14) | completed | success |
| test (macos-latest, 3.11) | completed | failure |

Run status: in_progress; conclusion: pending.
These observations apply to `d11c00422c3f0f44e18f350e8b0899f148d4cdc1`, not automatically to subsequent commits.
