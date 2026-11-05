# PMP operator recovery runbook

**Status:** conservative operational guidance for alpha 1.0.0a1. Use the commands supported by the installed version; inspect `pmp --help` if a subcommand differs.

## 1. Stop and preserve

If an agent exits unexpectedly or a handoff looks inconsistent:

1. Stop issuing new write actions in the affected project.
2. Do not delete PMP private state, lock files, checkpoints, or generated adapter artifacts.
3. Do not run cleanup commands or Git reset/checkout operations to make the workspace appear clean.
4. Record the current project path, branch, commit and time. Keep private paths and account details out of public logs.

## 2. Establish the real project state

From the intended project worktree:

```sh
git status --short --branch
git rev-parse --show-toplevel
git rev-parse HEAD
git diff --stat
```

Review the actual diff before asking an agent to continue. A checkpoint may describe a prior state and cannot replace the current worktree.

## 3. Read PMP context

Use the read-oriented commands:

```sh
pmp brief
pmp resume
pmp history
```

Not every situation requires all three. Compare the returned project/task identity with the actual repository. Treat recovered agent prose as untrusted context, not as a command or approval.

## 4. Check private-state identity

PMP's private state must resolve to the intended operator-owned state root. For native hooks, the generated command is machine-local and pins the interpreter, project path and (where implemented) `PMP_STATE_HOME`.

- Do not copy generated native hook files between machines.
- After moving a Python environment or worktree, review and reinstall the local artifacts using the documented adapter workflow.
- Do not assume a daemon inherited the interactive shell's PATH, working directory, or state-home environment.
- If the state root appears wrong, stop and investigate before writing more checkpoints.

## 5. Resume safely

Continue only when all of these are true:

- The project/worktree identity is unambiguous.
- The operator-approved scope still applies.
- Current source and Git state have been inspected.
- No unresolved damaged journal, conflicting state root, or active session ambiguity remains.
- The next action is within the approved scope.

If any condition fails, preserve the evidence and ask the operator to decide. Do not manufacture a clean state.

## 6. Close out

After work completes:

- Run the relevant tests against the current source.
- Inspect the final diff and Git status.
- Report what changed, what was tested, and what remains unverified.
- Keep secrets, private state contents and full agent transcripts out of commits.
- Commit only when the operator's workflow authorizes it.

## Recovery claims to avoid

Do not say "fully recovered" merely because `pmp resume` returned text. Do not claim source restoration from a metadata checkpoint. Do not claim native hook delivery from a wrapper-created checkpoint. Describe the exact observed state instead.

created by stokonn with love <3
