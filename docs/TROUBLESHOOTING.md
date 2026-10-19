# Troubleshooting

- Invalid/missing .pmp.yml or state: `pmp doctor`; preserve files and restore the known
  configuration/identity. Do not generate a competing project UUID over existing memory.
- Interrupted initialization: inspect newly created files. Repeated init preserves existing
  config and does not overwrite/guess missing authoritative task state; repair deliberately.
- Writer lock or lease refusal: inspect host/PID and `pmp resume`; follow RECOVERY.md.
  Never clear metadata simply because heartbeat is old.
- Tail corruption: explicit `doctor --repair-journal` preserves original bytes. Interior
  corruption requires investigation; do not truncate valid history blindly.
- Damaged checkpoint/handoff/backup: use history; previous valid checkpoints remain readable.
  Keep corrupted records for diagnosis. No automatic content restoration.
- Verification passed but not applicable: HEAD/fingerprint changed, capture was incomplete,
  or the check modified inputs. Rerun against actual current sources. Compilation alone
  yields no measured test count. JUnit empty/only-skipped cases cannot satisfy required execution.
- Command report malformed: verification is blocked; fix the check's fresh JUnit output.
- Sync unavailable: inspect gh auth, origin URLs and network. Local checkpoints still work.
  Cached refs/CI badges are not fresh evidence of a remote SHA.
- Existing handoff/hooks: init/adapter install preserve owner files. Review and move/merge
  manually or use private handoff and generic wrapper. PMP never silently merges policy/config.
- Watcher failed: inspect watcher.json last_error and private locks. Editing/builds continue;
  observation gaps are unrecoverable unless another mechanism persisted the information.
- Low disk/permission failure: retain worktree and prior state; free space or fix permissions,
  inspect whether publication happened, then retry. Do not assume a failed fsync wrote nothing.
- Unsupported agent/version: `pmp launch generic -- YOUR_COMMAND`; native artifacts remain
  disabled until reviewed against current official interfaces.
