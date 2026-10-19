# Owner readiness report

PMP is a functioning development alpha, **not ready for PMP 1.0.0 stable publication**.
The owner explicitly authorized the public repository stokonn/project-memory-protocol,
MIT licensing, development pushes, and CI verification. MIT is applied locally.
Publication observations are recorded below after verifying GitHub. No stable tag,
release or real Goldberg integration is authorized or performed.

Implemented: strict protocol/config/state/event/checkpoint/evidence/handoff contracts;
Python packaging and CLI; source identity; local durable journal and checkpoint chains;
truncated-tail repair; corruption fallback; opt-in private backups with integrity manifests;
source-bound check evidence and real test counts; JSON/Markdown handoffs; explicit recovery
reports; session leases; independent optional watcher; generic/vendor process wrappers;
optional native artifacts; allowlisted publication and exact GitHub SHA/CI separation.
All requested top-level CLI commands exist. See CLI.md, IMPLEMENTATION.md and VALIDATION.md.

Tests execute in disposable repositories. Demonstration preserves synthetic Goldberg
policy, Stage 4-style branch and untracked owner release notes; it never accesses actual
Goldberg source or a physical device. Real Goldberg rollout still requires separate approval.

Remaining release blockers and limits:

- Native vendor lifecycle artifacts are based on inspected official docs, not authenticated
  live agent sessions. Codex native install gates to inspected CLI 0.163.0; Claude/OpenCode
  artifacts are experimental/manual opt-in, with no certified runtime version range.
- Cross-platform CI has started on GitHub. Exact initial-checkpoint job observations
  appear below; pending jobs and newer commits are not certified by earlier passes.
- Owner authorization covers public development publication under MIT. Remote SHA and
  CI observations are recorded below. There is no stable release/tag; version is 1.0.0a1.
- Snapshots are metadata by default. Only explicit bounded private backup allowlists retain
  file bytes. No automatic restore or recovery of unpersisted/unsaved state.
- Source identity excludes ignored/external inputs and PMP memory/config; submodules are
  incomplete. Reproducible environment/dependency pinning remains the project operator's job.
- Secret detection is conservative and incomplete. Review shared memory and all pending
  branch commits before publication. Leases/hashes do not authenticate humans or stop
  noncooperating writers. Hostile filesystem races are outside the cooperative model.
- Crash-left locks and uncertain/remote leases require deliberate inspection. No automatic
  lock break or takeover. Watcher polling can miss transient edits and costs file hashing.
- Alpha schema evolution is not frozen; no automated compatibility migrator is provided.

Safe next actions: verify remote development checkpoint and full CI matrix, then validate
native adapters in disposable trusted agent sessions. Any failed or unavailable CI jobs
remain acceptance blockers. Evaluate readiness again before seeking stable publication.

## Public development checkpoint

Explicit owner authorization was exercised: public repository
https://github.com/stokonn/project-memory-protocol is created and MIT is recognized by GitHub.
Checkpoint `d11c00422c3f0f44e18f350e8b0899f148d4cdc1` was pushed on main; local Git,
`git ls-remote origin refs/heads/main`, and the GitHub commit API returned the same SHA.
Pre-push local validation: 90 tests passed; wheel/sdist build succeeded; pmp check passed.
No existing work was discarded, and all earlier commits remain in the published history.

Initial Actions run: https://github.com/stokonn/project-memory-protocol/actions/runs/39233284582
Workflow is active; CI was in progress when first checked. This is not a passing result
and does not certify Python 3.11/macOS/Windows. Recheck the exact head SHA and every job.
Final documentation commits trigger additional runs; use `gh run list` to select by SHA.
No stable tag, GitHub Release, or Goldberg integration has been created.

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

## Concrete macOS blocker for the next session

Initial checkpoint job `test (macos-latest, 3.14)` completed with **89 passed, 1 failed**
in 38.61 seconds. Failure: `tests/test_security_cli.py::test_watcher_lifecycle_and_launch`.
Watcher metadata reached `stopped`, but retained a `Writer lock exists` last_error,
violating the test's no-error assertion. The Python 3.11 macOS job also failed; its
precise traceback has not been separately inspected. Investigate watcher contention
and diagnostic semantics in disposable fixtures; do not weaken ownership/lock safety
or relabel the failing result as a pass. Windows jobs were still running at last check.

Documentation checkpoint `5b7cc8c7cfe3b224f68a10d242287c8c44e948df` also triggered run
https://github.com/stokonn/project-memory-protocol/actions/runs/39233446500
which was in progress when inspected. Subsequent docs-only commits may trigger more runs.
