# Recovery fault-injection test matrix

**Purpose:** guide future regression tests for PMP's local-first handoff and recovery behavior.

This is a test plan, not a claim that every scenario is already implemented or passing. Each test should use a fresh temporary Git repository and a private PMP state directory under the test's temporary root.

## Core scenarios

| Scenario | Setup | Expected property | Evidence to capture |
| --- | --- | --- | --- |
| Clean handoff | Initialize a fixture and create a task | Brief/resume output identifies the active project and next action | Test assertion over structured output |
| Changed source | Record a verification result, then edit the verified file | Old verification is not presented as applying to changed source | Source identity and verification status |
| Dirty worktree | Modify a tracked file without committing | Handoff reports the dirty state and does not imply a clean tree | Git status before and after |
| Interrupted write | Interrupt a write at a controlled boundary | Existing valid state remains readable; incomplete tail is reported safely | Journal bytes and read result |
| Damaged journal tail | Append a malformed final record to a disposable journal | Valid earlier records remain distinguishable from the damaged tail | Parsed record count and uncertainty |
| State-home conflict | Set a conflicting inherited `PMP_STATE_HOME` for a child process | Pinned command writes only to the intended private root | Directory listing of both roots |
| Read-only inspect | Snapshot private files, inspect, then snapshot again | Inspection makes no private-state changes | Before/after hashes |
| Existing hook artifact | Place an operator-owned artifact before install | Installer refuses to overwrite it | Original file hash remains identical |
| Path with spaces | Put fixture and private state under paths containing spaces | Commands execute against the intended paths | Resolved paths and subprocess result |
| Wrong working directory | Invoke command from outside the fixture | Explicit project path is honored; no accidental cwd project is created | Both project and cwd state |
| Unsupported vendor version | Stub or install a version outside the allowlist | Native mode refuses unsupported assumptions | Error message and no artifact write |
| Missing interpreter | Substitute an unavailable interpreter path | Installation fails closed | No partial manifest or hook artifact |

## Test design rules

- Prefer deterministic fault injection over timing-sensitive sleeps.
- Assert both the expected result and the absence of writes to unrelated locations.
- Use a separate temporary directory for every test; never share a developer's real PMP state.
- Avoid network access and model calls in the normal test suite.
- Do not make tests depend on a real vendor account, live quota, or interactive trust dialog.
- Mark platform-specific tests explicitly and report skipped counts accurately.
- Preserve failing fixtures as test artifacts only when they contain synthetic data.

## Acceptance

A matrix row is complete only when an automated test exists, it runs in the relevant CI job, and the assertion covers the stated safety property. A test name or documentation checklist alone is not evidence of execution.
