# Release evidence record

Copy this template into the release or milestone record only after validation has actually completed. Remove unperformed rows or mark them **not run**; never fill them with assumed results.

## Candidate

- Software version:
- Protocol/schema version:
- Candidate commit SHA:
- Branch:
- Date:
- Maintainer:

## Source integrity

- [ ] Exact candidate SHA recorded
- [ ] Worktree clean, or uncommitted diff attached and identified
- [ ] No private state, credentials, transcripts, or machine-specific hook artifacts included
- [ ] Changelog and migration notes reviewed

## Automated validation

| Check | Exact command or workflow | Source SHA | Result | Notes |
| --- | --- | --- | --- | --- |
| Unit tests | | | Not run | |
| Platform matrix | | | Not run | |
| Package build | | | Not run | |
| Synthetic examples | | | Not run | |
| Recovery fault matrix | | | Not run | |
| Backward compatibility | | | Not run | |

## Integration evidence

For each operator test, record the environment, fixture type, exact steps, observed result, and limitations. Use disposable synthetic repositories unless a separately approved real-project test is essential.

| Integration | Evidence level | Environment | Result | Limitations |
| --- | --- | --- | --- | --- |
| Codex native hooks | Not tested | | | |
| Claude native hooks | Not tested | | | |
| Wrapper lifecycle | Not tested | | | |
| Cross-session recovery | Not tested | | | |

Evidence levels must distinguish unit-tested, synthetic integration-tested, operator-reported, and genuine vendor-event observed. Do not label a manual receiver invocation as a vendor event.

## Security and compatibility review

- [ ] Existing user hook artifacts are preserved
- [ ] No global agent settings or approval policies were changed
- [ ] Unsupported vendor versions fail closed
- [ ] Private state remains in the intended local state root
- [ ] Damaged or interrupted state is reported without silent reset
- [ ] Changed source does not inherit stale verification
- [ ] Windows/macOS/Linux support claims match executed tests

## Decision

- Known blockers:
- Known limitations:
- Deferred work:
- Rollback or recovery plan:
- Release decision and approving owner:

A passing CI workflow is necessary evidence for the tested code, not sufficient evidence for live vendor integration, token savings, or a stable release. Version bumps, tags, and publication require the project's normal explicit release authorization.

created by stokonn with love <3
