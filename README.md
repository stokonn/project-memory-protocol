# Project Memory Protocol (PMP)

PMP is a local-first, agent-agnostic development memory CLI for Git projects.
Python 3.11+. No model API, vendor account, or running service is required.
**Development alpha (1.0.0a1), not an approved PMP 1.0 stable release.**
Licensed under MIT. Public development repository: https://github.com/stokonn/project-memory-protocol.

```sh
pipx install .
pmp --help
pmp init
pmp status
pmp resume
```

Read [the protocol](spec/1.0.md), [CLI reference](docs/CLI.md),
[security limitations](docs/SECURITY.md), [adapter setup](docs/ADAPTERS.md),
and [implementation status](docs/IMPLEMENTATION.md). Existing AGENTS.md and owner
instructions stay authoritative. A handoff grants no new permission.

```sh
# scope.md must describe work already approved by the owner.
pmp task activate example --approved-scope scope.md
pmp task set --phase implementing
pmp snapshot --reason milestone
pmp verify --run tests -- python -m pytest '--junitxml={report}'
pmp verify
pmp handoff
pmp history
pmp check
```

Output is structured JSON; errors use stderr and nonzero exit codes. Commands
inspect by default where applicable. Snapshots never commit or push. Private state
uses XDG state directories on Linux, Application Support on macOS, and LocalAppData
on Windows. `PMP_STATE_HOME` overrides the base for isolated experiments.

A snapshot is a durable metadata record, **not a full dirty-worktree backup**.
Explicit `checkpoint.backup_allowlist` entries enable bounded private file copies.
Ignored files, editor buffers, and secrets are never promised recoverable.

Developers: `python -m venv .venv`, activate it, then
`python -m pip install -e . pytest build`;
`python -m pytest`; `python -m build`. See [validation](docs/VALIDATION.md) for
executed evidence and [the demonstration](examples/demo.py) for a disposable workflow.
