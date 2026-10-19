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
- Cross-platform CI is configured but has not run. Linux/Python 3.14 is locally verified;
  macOS/Windows and Python 3.11 execution require real CI evidence.
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
