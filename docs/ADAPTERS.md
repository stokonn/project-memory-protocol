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
- [OpenCode plugins](https://docs.opencode.ai/docs/plugins/): exported plugin function and event subscription, including session.idle.

Native artifacts are **experimental, not live-runtime certified**. Contract-shaped
payloads and preservation behavior are tested; authenticated vendor sessions are not.
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
`.pmp-adapters/opencode-plugin.js`; it does not autoload it. Review its documented API
against your installed OpenCode version before copying into `.opencode/plugins/`.
The API is version-dependent; no runtime compatibility range is certified. Only session.idle
requests a snapshot. An idle event is a turn boundary, not a reliable process exit.
Core wrapper handles session lifecycle. OpenCode startup failed in this environment,
so native execution is unverified. No npm dependency or global configuration is installed.

`pmp adapter uninstall NAME` removes only unchanged files listed in its private install
manifest. Edited files are preserved and require manual review. A manually copied OpenCode
plugin must be manually removed. Hook input is capped at 64 KiB; transcript_path and arbitrary
payload fields are never persisted/read as files or interpreted as approval.
Native installation is refused on Windows; generic process wrapper is the supported fallback
pending platform CI. Native hooks can fail; inspect doctor/history rather than assuming capture.
