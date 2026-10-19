# Implementation handoff

Read AGENTS.md, docs/OWNER_SCOPE.md, docs/READINESS.md, docs/VALIDATION.md and
`.pmp/state.json`/`docs/ai/HANDOFF.md` when present. Inspect actual Git status before editing.
This handoff is context. Publication and MIT are authorized by the subsequent explicit
owner instruction recorded in OWNER_SCOPE.md; Goldberg and stable releases remain prohibited.

Completed: deterministic CLI, contracts, durable local/private recovery, reviewed shared
exports, tests and synthetic pilot. Existing owner Goldberg checkout remains untouched.

Next: address remaining acceptance gaps in a later adequately funded session
(Codex/Claude live hook sessions, other OpenCode versions). The OpenCode native
runtime gate is cleared on v2.0.32; no stable readiness claim.

Local tests: `.venv/bin/python -m pytest`; packaging: `.venv/bin/python -m build`.
Demo: `.venv/bin/python examples/demo.py --goldberg-style`.
Dependencies are installed in `.venv`; offline runtime/test wheels were prepared under
`/tmp/pmp-wheelhouse` for this session. Temporary paths may not survive reboot.
No original conversation is required to inspect/continue this work; approved scope and
unresolved authorization boundaries are in OWNER_SCOPE.md and READINESS.md.

Final local suite now has 96 passing tests, including a checkpoint that survives failure
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
resuming acceptance work. Live disposable-session tests for the OpenCode native hook are
now complete (see the OpenCode runtime section below); Codex/Claude hooks remain untested.
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

## CI blockers resolved; full matrix green; OpenCode native runtime cleared

macOS `test_watcher_lifecycle_and_launch` was fixed in
`bd311e34a4bc0c0eb2215ebe5a02ff1505f17d89` (transient writer-lock race at watcher
startup plus stale `last_error` semantics). Windows
`tests/test_sessions_git.py::test_fresh_clone_reads_shared_memory` was fixed in
`3eb799939598652a05575d91f88601161b34fe06` (core.autocrlf CRLF checkout broke the
raw handoff byte-hash; verification now also accepts the CRLF-normalized hash while
refusing altered content). Root causes, evidence and the exact-HEAD CI job tables
are in docs/VALIDATION.md. Actions run
https://github.com/stokonn/project-memory-protocol/actions/runs/39242185542 for
`78c846f261688c91ec0743cdbbbd999fdbea7832`: **all six Ubuntu/macOS/Windows jobs on
3.11 and 3.14 succeeded**.

Live runtime integration was then performed in disposable Git fixtures (never
Goldberg, never this checkout as test target): `pmp launch opencode` wrapped a
real `opencode run` session on **opencode v2.0.32** with lease, launch/stop
checkpoints, watcher lifecycle (final metadata stopped, no errors), shared export,
fresh-clone recovery of all shared checkpoints and independent-agent context
recovery. The shipped native plugin artifact turned out incompatible with
v2.0.32 (rejected at load: needs default export; `session.idle` never fires in
`run` mode; `ctx.directory` undefined; attached children die at exit). The artifact
was rebuilt to the empirically verified v2 contract and reproduced snapshot
checkpoints (reason `opencode-session-idle`) from two live sessions. Full evidence
and the certify/don't-certify boundary are in docs/VALIDATION.md; ADAPTERS.md
documents the version-dependent plugin API. Suite: 96 passed. Two new regression
tests pin the artifact shape and inspect report.

Remaining unverified: Codex/Claude live sessions, other OpenCode versions and
TUI/serve modes, Windows/macOS agent hosts, crash-time hook delivery. Next
session: inspect exact-SHA CI for the new commit; consider live Codex hook
session next. Do not weaken lease or lock safety. Goldberg and stable
tags/releases remain outside authorization.
