# Codex live integration evidence — 2026-10-19 (partial; quota-blocked)

All items below were executed, not simulated. Fixture:
`/tmp/opencode/pmp-codex-fixture-1792437534` (disposable Git repo), private state
`/tmp/opencode/pmp-codex-state-1792437534` (`PMP_STATE_HOME`, external to the
worktree). Neither Goldberg nor the PMP source checkout was a test target.
/tmp may not survive reboot; the fixture and its trust records were retained for
resumption after the weekly quota reset.

## Environment

- Host: Linux (fedora), Codex CLI `codex-cli 0.163.0` (`~/.local/bin/codex`),
  standalone install; `codex doctor`: 21 ok / 0 warn / 0 fail.
- Auth: ChatGPT (Plus plan). Account identifier redacted here.
- PMP: editable checkout `.venv` at the repository under test, CLI 1.0.0a1.
- Codex `/status` at test time: 5h limit 100% left; **weekly limit 1% left**
  (resets 11:21 PM local, 24 Oct 2026). This is the primary blocker.

## Executed steps and results

1. **PMP initialization**: `pmp init` (project id `14f8120a-…`), `pmp task
   activate codex-live-verify --approved-scope SCOPE.md`, `pmp session start
   --owner` acquired a real writer lease (session `d5479838-de62-412e-8d57-5476877cf1df`,
   live PID recorded).
2. **Lease/ownership safety (live)**: second `pmp session start --owner interloper`
   refused (exit 3, "never take over automatically"). `pmp session end` from a
   shell without `PMP_SESSION_ID` correctly refused (exit 3); succeeded only with
   the session's own identity.
3. **Hook receiver safety (live negative tests)**: `pmp hook --event Stop` with
   `cwd` != project root refused (exit 2). Oversized payload (>64 KiB) refused
   (exit 2). Both without any state mutation.
4. **Native adapter install**: `pmp adapter install codex --native` created only
   `.codex/hooks.json` and `.pmp-adapters/codex-BOOTSTRAP.md` in the fixture;
   re-install refused (exit 2); no global configuration changed. Artifact shape:
   `SessionStart`, `Stop`, `SessionEnd`, `Interrupt` command hooks running
   `pmp hook --event <EVENT>` (no matcher, sync mode).
5. **Real TUI trust flow (tmux-driven, no bypass flags)**: interactive `codex`
   in the fixture displayed the genuine folder-trust prompt (accepted), then
   "Hooks need review — 4 hooks are new or changed". Each hook was individually
   reviewed in `/hooks`: source "Project config - …/.codex/hooks.json", exact
   commands as installed by PMP, timeouts SessionStart 600 s, Stop 600 s,
   SessionEnd 1 s, Interrupt 1 s. After `t` (trust), all four showed
   Installed 1 / Active 1.
6. **Trust persistence mechanism (new finding)**: Codex 0.163.0 records hook
   trust in `~/.codex/config.toml` under `[hooks.state."<path>:<event>:<i>:<j>"]`
   with `trusted_hash = "sha256:…"`, i.e. hash-pinned per hook definition. The
   four fixture entries (and the fixture folder-trust entry, later removed)
   were written there. Trust survives across Codex processes.
7. **Zero-token TUI cycles**: two fresh TUI sessions (one startup, one with
   explicitly created new threads via the Agent Command Center `n`) ran with a
   transparent pass-through `pmp` logging shim first on `PATH`. **Zero hook
   invocations were logged**; system-wide process sampling during thread creation
   caught no hook command execution; the shared background app-server daemon
   (`codex app-server`, ephemeral mode) logged no hook errors.
8. **Daemon environment finding**: the background app-server daemon's `PATH`
   (read from `/proc/<pid>/environ`) contains no directory holding a resolvable
   `pmp` (the CLI exists only inside the project venv). If/when Codex executes
   project hooks in that environment, `pmp hook …` cannot resolve. No global
   binary was installed to work around this (prohibited).
9. **Session-lifecycle inference**: no hook process is spawned on thread
   creation alone; Codex session lifecycle hooks (SessionStart/Stop/SessionEnd)
   are turn/session-bound. Observing their execution therefore requires at least
   one real model turn — blocked by the weekly quota.
10. **Manual hook execution (contract check)**: `pmp hook --event SessionStart`
    emitted the documented `hookSpecificOutput.additionalContext` JSON in
    0.149 s; `pmp hook --event SessionEnd` emitted `{}` and created checkpoint
    sequence 1 (`adapter lifecycle: SessionEnd`, session "manual" — a synthetic
    invocation used only for timing, not evidence of Codex execution) in
    0.215 s. Both well within Codex's 1 s SessionEnd timeout in this
    environment, though under load that margin is not guaranteed.
11. **Fixture integrity**: `pmp check` valid, zero errors/warnings, after all
    steps.

## Not executed (blocked)

- Live model turn in the fixture: `pmp launch codex -- exec …` (blocked: weekly
  quota 1%).
- Automatic checkpoint creation from real Codex `Stop`/`SessionEnd` hook events.
- Wrapper session lifecycle around a real Codex turn, fresh-clone recovery and
  independent-agent recovery in this Codex fixture (all previously verified on
  the OpenCode path; not re-claimed for Codex here).

## Safety posture

No `--dangerously-bypass-*` flag was used. No global hook, binary, or config was
installed. Goldberg untouched. The owner's `~/.codex/config.toml` gained only the
fixture hook-trust records (hash-pinned, inert without the fixture); the fixture
folder-trust entry was removed after the test. Cleanup command for the owner if
desired: delete the `[hooks.state]` entries referencing the fixture path and
remove the fixture directories under `/tmp/opencode/`.
