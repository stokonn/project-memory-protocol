# CLI reference

Install locally with `pipx install .` (or `python -m pip install .` inside a venv).
Until an approved public package/repository exists, install from the reviewed checkout.
PMP requires Git. gh is optional for local operations and required for GitHub confirmation.
No default network traffic, global hooks, account login, or model API calls.

Global flags go **before** the subcommand: `pmp --project /path --json status`.
All command results are JSON, including without --json. Explicit verification/launch
children inherit the terminal and may write their own output; automate their results by
reading persisted evidence rather than assuming mixed stdout is a single JSON document.
`pmp --help` and `pmp COMMAND --help` describe arguments.

| Command | Behavior |
| --- | --- |
| init | Initialize Git if needed; create missing PMP memory; preserve existing config/docs |
| status | Read real Git state, task, checkpoint, source, verification and cached sync facts |
| check | Validate schemas, identities, integrity, references and local consistency |
| snapshot --reason TEXT | Durable LOCAL record, no stage/commit/push |
| handoff | Write private JSON and Markdown handoff |
| handoff --shared | Explicitly update PMP-generated shared handoff; refuse unrelated existing Markdown |
| resume --record | Explicit private recovery report and journal events; no source restoration |
| resume | Read-only reconciliation of local/shared records, Git, session and uncertainty |
| verify | List evidence and current source applicability |
| verify --run NAME -- COMMAND ... | Execute explicitly requested argv; no shell; no captured logs |
| sync | Inspect local commit relationships and cached remote tracking counts |
| sync --refresh | Query GitHub branch and CI at exact HEAD; exit 4 if unavailable |
| sync --export | Scan/copy private checkpoint/evidence/handoff context to shared memory for review |
| sync --commit | Authorize allowlisted memory-only commit; refuse pre-staged changes |
| sync --push | Authorize ordinary branch push; validate origin, then confirm GitHub identity |
| doctor | Diagnose configuration, dependencies, locks, references and free disk space |
| doctor --repair-journal | Preserve original and atomically remove truncated tail only |
| history | Inspect local and shared checkpoint records separately |
| history --rebuild-index | Rebuild disposable private checkpoint index from validated records |
| release-check | Evaluate evidence, explicit approval, phase/status and clean source; never publish |
| task activate ID --approved-scope scope.md | Caller explicitly asserts existing owner-approved scope |
| task set --phase PHASE --status STATUS | Explicit state update, no automated release promotion |
| task set --completed TEXT --in-progress TEXT --blocker TEXT --next-action TEXT | Replace supplied claim lists; repeat flags for multiple items |
| task set --phase ready_for_release --authorization approval.md | Require applicable configured checks and explicit caller-supplied approval reference |
| task archive | Clear active task, pause and return to planning; prior events/checkpoints remain |
| session start --owner NAME | Acquire lease; export returned ID as PMP_SESSION_ID for subsequent commands |
| session end | End the session owned by PMP_SESSION_ID |
| session release-stale --session-id UUID | Explicit release only after matching local process is positively absent |
| watcher start/stop/status | Start observer for owned session, request cooperative stop, or inspect metadata |
| launch generic -- COMMAND ... | Acquire session, start independent observer, run command, checkpoint on exit |
| launch codex/claude/opencode -- ARGS ... | Same wrapper around optional installed agent binary |
| adapter inspect/install/uninstall NAME | Capabilities; bootstrap install; remove only unchanged installed files |
| adapter install NAME --native | Explicit experimental native artifacts; see adapter setup |
| hook --event NAME | Bounded stdin JSON lifecycle receiver; never ingests transcript |

Verification with pytest and measured execution count:

```sh
pmp verify --run tests -- python -m pytest '--junitxml={report}'
```

The placeholder becomes a fresh private path; raw XML is parsed then removed to avoid
retaining test logs. The evidence keeps command, result, testcase count and report digest.
No report => unknown count. Compiling or collecting tests never implies execution.

Exits: 0 success/inspection, 1 failed check or unmet release prerequisites,
2 invalid contracts/usage/IO, 3 writer/lease/scope conflict, 4 unavailable GitHub verification.
Wrapped command exits are propagated (130 for interrupt). argparse uses 2 for invalid syntax.
No command creates a stable tag or GitHub Release.
