# Session watcher

Use `pmp launch generic -- COMMAND ...` or `pmp launch codex -- ARGS ...`.
A separate Python process observes the session without calling any model. It owns no
system service and uses no global hooks. Defaults: 30-second heartbeat/poll, 10-second
debounce, 300-second changed-source checkpoint interval, plus wrapper start/exit snapshots
and best-effort observation of owner process exit. Native hooks can request milestone snapshots.
The state is bounded to the most recent fingerprint/change time; there is no unbounded
file-event queue. Each inspection hashes Git-known inputs and can be expensive on large
repositories; the observer does not run on the editor's hot path. Benchmark large projects
before adoption. A source mutation during capture is marked incomplete where detected.

`pmp watcher status` reports persisted state/error. Stop uses a private marker checked
at most every 100 ms during idle waiting; a running Git read/checkpoint can delay stopping.
Default Git subprocess timeout is 30 seconds. Failure does not terminate the agent.
The wrapper requests stop and waits up to five seconds before its final checkpoint;
if checkpoint work still owns the writer lock it fails safely rather than breaking it.
Watcher start refuses existing running/starting metadata. Inspect a crashed watcher and
its lock before deliberately preserving/removing stale private metadata to restart it.

| Interruption | Expected behavior |
| --- | --- |
| SSH disconnect | Terminal/job/session behavior varies; persisted checkpoints survive; no unsaved-buffer guarantee |
| tmux keeps running | Wrapper/agent/watcher generally remain alive; normal polling continues |
| Agent normal exit | Wrapper requests stop and creates a final local checkpoint |
| Agent/wrapper killed | Observer may detect owner PID exit and checkpoint; lease remains for explicit inspection/release |
| Watcher killed | Agent continues; no further watcher persistence; stale lock/metadata require inspection |
| Computer reboot | No process survives; persisted records remain; no automatic restart or lease takeover |

Positive PID absence is useful evidence; PID existence, permissions, PID reuse, and remote
hosts create uncertainty. Cooperative leases do not prevent arbitrary external edits.
No promise that every transient change between polls or every build completion is recorded.
