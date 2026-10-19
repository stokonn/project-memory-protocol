# Agent adapters and compatibility

All adapters use identical .pmp configuration, state, events, checkpoints and evidence.
Core works with no agent installed. Install bootstrap only:
`pmp adapter install generic`. Read `.pmp-adapters/generic-BOOTSTRAP.md`.
A human or a GitHub-reading chat agent can read the shared handoff without executing PMP;
it must ask a local operator to verify worktree state before continuing.

Reliable fallback: `pmp launch generic -- COMMAND ...`, or
`pmp launch codex -- ARGS ...`, `pmp launch claude -- ARGS ...`,
`pmp launch opencode -- ARGS ...`. These preserve the executable's sandbox/approval flags.
PMP does not add trust-bypass or permission-bypass arguments. Use `adapter inspect NAME`
for binary availability, inspected version and honest capability limitations.

Official references inspected 2026-10-19:

- [Codex hooks](https://developers.openai.com/codex/hooks): project-local hooks.json, explicit hook trust and JSON stdin lifecycle contract.
- [Claude Code hooks](https://code.claude.com/docs/en/hooks): SessionStart, Stop and SessionEnd command hooks and JSON input.
- [OpenCode plugins](https://docs.opencode.ai/docs/plugins/): plugin lifecycle and event subscription, including session.idle. The public docs page (inspected 2026-10-19) still shows a named-export shape that installed v2.0.32 rejects; the binary requires a default export. The v2.0.32-verified shape is what PMP ships.

Native artifacts are **experimental**. Contract-shaped payloads and preservation
behavior are tested for all adapters; the OpenCode artifact additionally has a live
runtime verification on v2.0.32 (wrapper + native snapshot capture, see VALIDATION.md).
Codex and Claude native hooks remain untested against authenticated live sessions.
Future API/schema/version changes require reinspection; wrappers remain the fallback.

`pmp adapter install codex --native` creates `.codex/hooks.json` only if absent and gates
to inspected `codex-cli 0.163.0`. Review/trust through Codex `/hooks`; PMP never bypasses
trust. SessionStart supplies bootstrap context; Stop/SessionEnd/Interrupt request local
snapshots. Under the PMP wrapper they inherit the session identity. Without a wrapper
there is no independent session watcher or automatic lease ownership; a conflicting lease
blocks writes. Hook-only mode must not be mistaken for automatic concurrency protection.
Existing hooks.json is preserved; use the wrapper rather than silently merging.

`pmp adapter install claude --native` creates `.pmp-adapters/claude-settings.json` with
SessionStart/Stop/SessionEnd entries. It never edits `.claude/settings.json`. Review against
your installed version, then explicitly run
`pmp launch claude -- --settings .pmp-adapters/claude-settings.json`.
Claude was not installed in the implementation environment, so no tested version range
or runtime compatibility guarantee is claimed. Use wrapper-only if uncertain.

`pmp adapter install opencode --native` creates a **review artifact**
`.pmp-adapters/opencode-plugin.js`; it does not autoload it. Copy it into
`.opencode/plugins/` only after reviewing it against your installed OpenCode version.
The API is version-dependent; the certified runtime range is **exactly opencode
v2.0.32** (Linux, 2026-10-19 live verification; see VALIDATION.md). The v2 plugin
contract differs from older docs: a default export `{ id, setup }`, event
subscription via `ctx.event.subscribe(cb)` returning an async iterable, project
directory at `ctx.location.directory`, and detached child spawning so the snapshot
survives process exit. In v2.0.32 `opencode run` mode, `session.idle` was never
emitted; the observed turn boundary is `session.execution.succeeded`, which the
artifact also accepts. Only turn-boundary events request a snapshot. A turn
boundary is not a reliable process exit. Core wrapper handles session lifecycle.
An inert `session.idle`-only plugin (the previous artifact shape) loads with a
warning on v2.0.32 and silently does nothing; do not mistake a loadable plugin
for a working one. No npm dependency or global configuration is installed.

`pmp adapter uninstall NAME` removes only unchanged files listed in its private install
manifest. Edited files are preserved and require manual review. A manually copied OpenCode
plugin must be manually removed. Hook input is capped at 64 KiB; transcript_path and arbitrary
payload fields are never persisted/read as files or interpreted as approval.
Native installation is refused on Windows; generic process wrapper is the supported fallback
pending platform CI. Native hooks can fail; inspect doctor/history rather than assuming capture.
