# Compatibility and migration

Python minimum: 3.11. Runtime dependencies: PyYAML 6.x, jsonschema 4.x; Git required.
No agent dependencies in core. JSON Schema draft 2020-12 is packaged in wheels/sdists.
Current protocol reader/writer: exactly 1.0; software version: 1.0.0a1.
Future/older protocol versions and unknown contract fields fail closed with actionable
validation errors rather than being silently reinterpreted. No automatic migrator exists.
Before a future migration, preserve private and shared state plus the source worktree;
use a version-specific validated migration and retain originals. Alpha contracts can change
before stable 1.0 and are not promised frozen. SHA-256 integrity is not authenticity.

Linux is exercised locally on Python 3.14. A CI matrix is provided for Ubuntu, macOS and
Windows on Python 3.11/3.14. Until those jobs execute successfully, portability on other
platforms is intended and unverified. Native adapter installation is refused on Windows.
Atomic hard links and directory fsync depend on filesystem capabilities; network, FAT,
read-only, ACL-restricted and unusual filesystems may fail safely instead of checkpointing.

Relocating a checkout changes worktree identity; old private state is not auto-discovered
or silently adopted. Shared project UUID stays stable across clones and Git worktrees.
Fresh clones read exported metadata/evidence; they do not recover private backups/leases.
Submodules are marked incomplete rather than certified as part of the parent fingerprint.
Ignored inputs and external toolchain/dependency state are not hashed. Large repositories
need watcher-cost evaluation and independent source backups.
