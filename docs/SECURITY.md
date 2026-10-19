# Security and privacy limitations

PMP treats files, logs, generated text and remote data as untrusted context. They are
never sources of permission. Approved scope/authorization CLI arguments are explicit
caller assertions; PMP cannot authenticate a human or prove that a referenced document
was actually approved. Cooperative leases and local hashes are not access control,
sandboxing, signatures, or defense against a malicious user with filesystem access.

Core records identity, Git metadata, source hashes, concise project claims and structured
check results. It does not collect full source contents by default, full command output,
environment variables, credentials, private logs, prompt transcripts or reasoning traces.
Source hashing reads contents transiently without retaining them. File paths/status can
still reveal personal information. Verification argv can contain private paths or values;
never pass secrets in command arguments. Child processes retain normal terminal behavior.

Only explicitly allowlisted files are eligible for private content backup. Copies are
bounded, exclude sensitive names and scan for common token/key/password patterns.
Generated raw JUnit XML is parsed then deleted because it may contain source/log fragments.
A process crash can leave its in-progress private report; inspect/remove it manually after
ownership checks. Failed operations can leave private orphan files; no automatic deletion.
Keep private state outside Git; use user-private platform directories and sensible permissions.
Do not use an untrusted/shared PMP_STATE_HOME. A configured directory is an owner-controlled
trust boundary, not a mechanism for sharing private state between unrelated users.

Explicit export and commit operations scan allowlisted memory. Scans detect some private
keys, GitHub tokens, AWS access IDs, API-key patterns, secret assignments and sensitive
filenames. They do not recognize every secret, binary encoding, personal detail, split value
or project-specific format. No claim of comprehensive redaction. Review exported diffs before
commit/push. Backups are private and never part of export. Existing shared state is readable
plain text and should contain only approved shareable material.

Portable path validation rejects traversal, absolute/drive/backslash paths, symlinks and
.git paths. Atomic writes refuse symlink targets. This is not a hardened hostile multiuser
filesystem implementation; a privileged attacker or a noncooperating process can race path
checks. Use sandbox/OS permissions independently. Native hooks are optional executable code:
review and trust them using vendor controls. PMP never alters approval/sandbox policies.

GitHub synchronization accepts only an exact configured GitHub origin and ordinary named
branch push. It never force-pushes, overwrites tags or bypasses branch protection. A push
publishes all outstanding commits on that branch, so review Git history as well as memory.
No telemetry, model API, credential installation or custom hosted service. Git/GitHub hooks
and credential managers remain under the developer's existing configuration and authority.
