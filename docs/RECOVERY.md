# Recovery procedure

1. Read AGENTS.md and canonical owner-approved scope. Stop editing if another agent may own the worktree.
2. Run `pmp resume`, `pmp status`, `git status --short`, and inspect diffs. Resume changes no worktree files.
3. Run `pmp doctor`. Inspect any lease/lock PID, host, worktree identity and heartbeat. A stale heartbeat alone is insufficient.
4. If only the journal's final record is truncated, use `pmp doctor --repair-journal`. It retains the exact damaged original privately before publishing the valid prefix.
5. For damaged checkpoints, use `pmp history`. Recovery selects earlier validated records and reports damage; never deletes the bad records.
6. If an owner process is positively dead on this host, explicitly run `pmp session release-stale --session-id UUID`. Remote/uncertain or potentially reused live PIDs are refused.
7. A crash-left lock requires independent process inspection. Preserve a copy and manually remove **only** that confirmed stale private lock; there is deliberately no automatic lock-break command. Never remove a lock just to bypass a refusal.
8. Rebuild disposable indices with `pmp history --rebuild-index` after resolving ownership. Corrupt indices do not prevent record scans.
9. Compare files against source fingerprints and optional private backup manifests. Backup hashes are checked during checkpoint inspection. Restore individual files manually only after reviewing current owner changes; PMP has no automatic restore command.
10. Run applicable checks again, create a fresh snapshot, and generate a handoff.

Low disk space or interrupted atomic replacement should leave the prior target intact.
A failed directory fsync may mean publication occurred but durability is uncertain: inspect
before retrying. An interrupted append can leave a tail; readers retain its valid prefix.
Corruption in a complete interior journal record requires manual investigation and fails closed.
Interrupted initialization may leave partial new files; preserve them and use doctor to
identify missing configuration/state rather than assuming initialization completed.

Recovery cannot recover unsaved buffers, ignored files, never-persisted observations,
unallowlisted dirty contents, lost disks, or remote commits never pushed. Shared records
never include private content backups. Keep independent filesystem backups for source recovery.
