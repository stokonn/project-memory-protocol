# Architecture

The protocol is in spec/1.0.md and six JSON Schemas. The core is Python, with PyYAML
safe loading and jsonschema validation. CLI dispatch contains no LLM dependency.
Adapters delegate to canonical core operations rather than maintaining separate memory.

| Package | Ownership |
| --- | --- |
| core | Configuration/schema validation, durable IO, identity and cooperative sessions |
| git | Read-only Git facts and source fingerprints |
| events | Local ordered append-only JSONL and explicit tail repair |
| checkpoints | Immutable records, handoff seals, optional private allowlisted backups |
| verification | Explicit command execution, JUnit counts, evidence applicability and release gates |
| recovery | Non-destructive reconciliation, checks, JSON/Markdown handoff |
| github | Guarded export/commit/push and fresh GitHub/CI identity checks |
| watcher | Independent session-scoped local observer and subprocess wrapper |
| security | Portable paths, secret-pattern and filename guards |
| adapters | Optional documented lifecycle artifacts and universal bootstrap |
| cli | argparse interface, stable structured results and error exits |

Private: `$XDG_STATE_HOME/pmp/PROJECT_UUID/WORKTREE_ID/` (default
`~/.local/state/pmp/...`) on Linux. macOS uses `~/Library/Application Support/pmp`;
Windows `%LOCALAPPDATA%/pmp`. `PMP_STATE_HOME` isolates tests and portable deployments.
Never place it in tracked source or share it automatically.

Shared: `.pmp.yml`, `.pmp/state.json`, explicitly exported `.pmp/checkpoints/`,
`.pmp/evidence/`, `.pmp/handoffs/`, `.pmp/handoff.json`, and docs/ai context. A fresh
clone can validate/read shared evidence and checkpoints but cannot inherit another
worktree's local session or claim access to its private backups.

Writes are temporary-file fsync + atomic rename, or exclusive hard-link publication
for immutable records. Parent directory fsync is used on POSIX. Event appends fsync
under an exclusive lock. Session lease and writer lock combine cooperative ownership
with short critical sections. Explicit verification holds the writer lock for its
execution; watcher failures during long checks are isolated and exposed in metadata.
Locks left by process death are never automatically removed.

Checkpoint hashes detect accidental corruption, not malicious forgery. The local index
is optional and never a recovery authority. A valid checkpoint can outlive its missing
creation event after a crash; history scans immutable records rather than trusting an index.
Protocol excludes memory directories and .pmp.yml from source fingerprints to avoid
self-invalidation; changes to actual tests/source/approved scope still invalidate evidence.
