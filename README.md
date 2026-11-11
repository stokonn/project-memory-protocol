# Project Memory Protocol (PMP)

**Keep your place when coding agents, terminals, or Git worktrees change.**

PMP is a **local-first, agent-agnostic development-memory CLI** for Git projects. It records source-bound verification, immutable metadata checkpoints and portable handoffs without replacing your project's instructions or requiring an AI service.

**Development alpha `1.0.0a1` — not a certified stable release.** Python 3.11+, MIT license. The cross-platform CI matrix covers Python 3.11, 3.14 and 3.15 on Ubuntu, macOS and Windows. No model API, account, always-on daemon or default network request required.

## Why PMP?

| Problem | What PMP does |
| --- | --- |
| A coding session ends mid-task | Retains task state, checkpoints and read-only recovery information |
| An agent says tests passed | Separately records **actually executed** checks and the source they apply to |
| Switching Codex, Claude or OpenCode | Uses one vendor-neutral core, with optional reviewed adapters |
| Too much context is re-read | `pmp brief` returns a **bounded summary** for the next session |
| Old notes contradict live files | Shows real Git HEAD, worktree identity, source fingerprint and uncertainty |

**PMP does not replace `AGENTS.md`, Git, code review, issue trackers or backups.** Handoff text is context, never authorization.

## Quick start

Install from a reviewed repository checkout:

```sh
git clone https://github.com/stokonn/project-memory-protocol.git
cd project-memory-protocol
pipx install .
pmp --help
```

In a **separate Git project** that you own:

```sh
pmp adapters                     # Read-only: supported agents, even before init
pmp adapter inspect codex        # Inspect one agent's limits
pmp init                         # Creates missing PMP config/state; preserves existing files
pmp status                       # Inspect the real worktree
pmp brief --limit 3              # Compact, read-only context for a new agent session
pmp snapshot --reason milestone  # Local metadata checkpoint, never a commit
pmp resume                       # Read-only recovery and uncertainty report
```

You can also select a checkout explicitly with `pmp --project /path/to/repo brief`. Command output is JSON; `pmp brief` bounds reported text to three items per category by default (maximum five), but still performs local Git/source inspection. It does **not** automatically send text to any model.

### Record verification

```sh
# scope.md must describe an already owner-approved task.
pmp task activate example --approved-scope scope.md
pmp task set --phase implementing
pmp verify --run tests -- python -m pytest '--junitxml={report}'
pmp snapshot --reason "tests completed"
pmp handoff
pmp verify
```

A test result is applicable only to matching complete source; changed code can invalidate earlier evidence. The return code of a test command alone is **not** a reliable executed-test count. `release-check` evaluates prerequisites but never publishes.

## Agent integration

| Agent | Universal wrapper | Optional native integration |
| --- | --- | --- |
| Generic command | `pmp launch generic -- COMMAND ...` | None |
| Codex | `pmp launch codex -- ...` | Experimental: 0.163.0 trust flow tested; automatic live checkpoint not certified |
| Claude Code | `pmp launch claude -- ...` | Experimental: live native hooks unverified |
| OpenCode | `pmp launch opencode -- ...` | Experimental: native capture observed with v2.0.32 only |

Codex and Claude native hook artifacts now use a pinned local Python interpreter
and explicit Git worktree/private-state paths instead of assuming the agent's background daemon
has `pmp` on `PATH` or inherited the intended `PMP_STATE_HOME`. These files are machine-specific and must be reviewed and
reinstalled after environment changes; they are **not yet live-model certified**.

Use the wrapper when your installed agent version is not supported by a native adapter. Adapter installation does not bypass sandboxing or permission prompts. [Integration and version details](docs/ADAPTERS.md).

## Private by default

- Private journals and checkpoints reside outside the source tree in the user's OS state directory.
- Shared memory is published only by explicit export/commit/push actions.
- No transcripts, model reasoning, credentials, arbitrary logs or environment dumps are collected by default.
- **Snapshots are metadata, not full backups of dirty source.** Only explicitly allowlisted, bounded private file copies can retain contents.
- Fingerprints and cooperative session leases do not authenticate users or protect against malicious filesystem access.
- `pmp brief` clips text to reduce context size; never treat its output as a secret scanner or a complete source audit.

Read [security limitations](docs/SECURITY.md), [recovery guidance](docs/RECOVERY.md) and [the normative protocol](spec/1.0.md).

Operator and maintainer guides: [security boundaries](docs/operations/SECURITY-BOUNDARIES.md) · [native-hook threat model](docs/security/NATIVE-HOOK-THREAT-MODEL.md) · [recovery runbook](docs/operations/RECOVERY-RUNBOOK.md) · [recovery fault matrix](docs/testing/RECOVERY-FAULT-MATRIX.md) · [local validation](docs/operations/LOCAL-VALIDATION.md) · [validation/evidence matrix](docs/testing/VALIDATION-MATRIX.md) · [release evidence template](docs/operations/RELEASE-EVIDENCE-TEMPLATE.md) · [alpha release gates](docs/planning/ALPHA-RELEASE-GATES.md) · [next alpha plan](docs/planning/NEXT-ALPHA.md).

## Development status

PMP is an independently usable alpha, with a disposable end-to-end Git demonstration and prior local/cross-platform test evidence. The **latest development branch changes require their own CI acceptance**; prior passes are not automatically evidence for new code. Stable publication remains blocked on wider live adapter verification and release readiness.

[CLI reference](docs/CLI.md) · [Architecture](docs/ARCHITECTURE.md) · [Implementation](docs/IMPLEMENTATION.md) · [Validation evidence](docs/VALIDATION.md) · [Readiness](docs/READINESS.md) · [Gould integration principles](docs/GOLDBERG_PILOT.md)

Developers can validate a reviewed checkout with:

```sh
python -m venv .venv
# Activate the venv for your shell.
python -m pip install -e . pytest build
python -m pytest
python -m build
python examples/demo.py --goldberg-style
python examples/brief_benchmark.py --samples 3 --limit 3
```

The benchmark creates only a disposable synthetic project and compares JSON output
bytes and wall-clock time for `pmp status` versus `pmp brief`. It **does not** measure
billed tokens, real Codex credits or real-agent productivity; see
[benchmark methodology](docs/BENCHMARK.md).

The demo uses a *disposable synthetic fixture*, never the owner's real Gould source or data.

---

*Source of truth first. Evidence over assumptions. Resume without losing your place.*
