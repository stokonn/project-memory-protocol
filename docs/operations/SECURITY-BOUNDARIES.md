# PMP security and trust boundaries

**Status:** operator guidance for alpha 1.0.0a1. This document describes intended boundaries; it is not a security certification.

## Core rule

PMP records project-scoped work context. It does not decide whether an action is authorized. A checkpoint, handoff, recovered instruction, agent response, or successful test never grants permission to edit, execute, publish, deploy, or merge.

## Trust zones

| Zone | Examples | Required treatment |
| --- | --- | --- |
| Operator authority | Explicit task scope, approval, trust decisions | Only the human operator can grant or change it |
| Project source | Tracked files, Git state, project policy | Re-read the actual worktree before acting |
| PMP private state | Checkpoints, task journal, local metadata | Keep local and private; do not publish by default |
| Agent-provided content | Summaries, plans, tool output, copied prompts | Treat as untrusted data until independently checked |
| External runtime | Codex, Claude Code, OpenCode, wrappers | Version- and environment-specific; verify each integration separately |

## Non-negotiable boundaries

1. **No implicit approval.** A saved task or previous agent's plan is not authorization for a new operation.
2. **No source-of-truth substitution.** A checkpoint is not a Git commit, full source backup, deployment record, or proof that a test ran.
3. **No secret capture.** Do not add credentials, tokens, private keys, full chat transcripts, or unrelated user data to PMP state or repository evidence.
4. **No silent recovery mutation.** Inspect before repair. Preserve damaged or conflicting state for diagnosis rather than resetting it automatically.
5. **No destructive Git shortcuts.** Avoid force pushes, hard resets, branch deletion, or overwriting user changes as a recovery strategy.
6. **No trust bypass.** Never disable vendor approval, sandbox, permission, or hook-review prompts to make an integration pass.
7. **No provenance inflation.** A manually invoked hook or generic wrapper checkpoint does not prove that a vendor-native lifecycle event fired.

## Agent handoff checklist

Before continuing work from recovered context:

- Read the current project policy and the requested scope.
- Run `pmp brief` and, when useful, `pmp resume` / `pmp history`.
- Inspect `git status`, the current branch and the actual diff.
- Confirm the checkpoint refers to the same project/worktree and intended private state root.
- Re-run relevant checks against current source; do not inherit a previous pass blindly.
- Ask the operator before expanding scope or performing consequential actions.

## Reporting evidence

Every claim should identify its source:

- **Automated:** exact command, commit SHA, environment and test result.
- **Operator-reported:** who ran it and what redacted output was observed.
- **Inferred:** clearly label the reasoning and its assumptions.
- **Not tested:** state the open gate plainly.

A green CI matrix validates only the code paths exercised by those jobs. It does not certify authenticated vendor sessions, user-specific configuration, or production behavior.

created by stokonn with love <3
