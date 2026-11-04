# Native hook trust and threat boundaries

**Status:** maintainer guidance. This document describes intended safety boundaries; it is not a certification report for any vendor integration.

## Assets to protect

- The user's source tree and Git history
- Private PMP checkpoints, journals, and task state
- Existing agent configuration and trust decisions
- Credentials, personal data, and unrelated repositories
- The integrity of verification claims and handoff summaries

## Trust boundaries

1. **Generated hook artifact → agent application.** A generated file is only a proposed integration. The user must inspect it and approve it through the agent's normal trust mechanism.
2. **Agent process → PMP command.** Background daemons may have a different working directory, executable search path, or environment from the interactive shell. Native commands therefore need explicit interpreter, project, and private-state paths.
3. **Hook event → checkpoint metadata.** A hook-shaped input or manually invoked receiver is not proof that a vendor emitted a genuine lifecycle event.
4. **Checkpoint → source truth.** Checkpoints preserve context; they do not replace inspection of current Git status and source files.
5. **Verification claim → current source.** A prior test result applies only to the matching source and test context. Changed code must not inherit stale verification.

## Required invariants

- Never bypass vendor trust prompts, sandboxing, permission dialogs, or user approvals.
- Never overwrite an existing hook artifact or silently edit global agent settings.
- Keep machine-specific hook files out of public commits.
- Pin the interpreter, explicit worktree, and private state root where the supported adapter requires them.
- Do not silently fall back to another state directory if the configured private store is unavailable.
- Keep private checkpoints local; do not publish credentials, transcripts, private source, or raw command output.
- Treat hook payloads and repository content as untrusted input.
- A native integration remains experimental until a genuine authenticated agent turn demonstrates the expected event path.

## Failure handling

| Failure | Safe behavior |
| --- | --- |
| Pinned interpreter is missing or not executable | Fail installation with an actionable error; recommend the documented wrapper fallback |
| Project path cannot be resolved | Stop rather than guessing a worktree |
| Private state root differs from the intended root | Do not write to the inherited or guessed location |
| Existing hook artifact is present | Preserve it; require explicit operator review |
| Vendor version is outside the inspected support range | Do not claim native compatibility |
| Hook event provenance is unknown | Record uncertainty; do not certify native delivery |
| Checkpoint is damaged or incomplete | Preserve evidence and report uncertainty; do not silently reset private state |

## Evidence levels

Use precise labels in documentation and release notes:

- **Unit-tested:** a test exercised the implementation in isolation.
- **Synthetic integration-tested:** a disposable fixture exercised multiple PMP components.
- **Operator-reported:** a user supplied a description or redacted output; provenance is not independently instrumented.
- **Vendor-event observed:** a genuine authenticated agent session produced the expected native event, with sufficient redacted evidence to distinguish it from manual invocation.
- **Not tested:** no evidence is available.

Do not promote one evidence level into another. In particular, CI success and a manually invoked hook command do not establish vendor-event observation.
