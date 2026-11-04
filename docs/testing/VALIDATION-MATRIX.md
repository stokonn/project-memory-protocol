# PMP validation and evidence matrix

This matrix separates repeatable repository checks from runtime claims that require an operator session.

## Evidence levels

| Level | What it establishes | What it does not establish |
| --- | --- | --- |
| Unit test | A bounded function or module behavior under test conditions | Correct behavior in every project or agent runtime |
| CLI/integration test | Components work together in the tested local process | Vendor-native event delivery or authenticated account behavior |
| CI matrix | The exact commit passed the configured OS/Python jobs | Untested OS, Python, shell, vendor version, or user configuration |
| Operator-run wrapper test | The reported wrapper workflow behaved as observed | Native hook execution or causal improvement over a baseline |
| Authenticated native-session test | A real vendor session produced correlated native-event evidence, if provenance is adequate | Universal support for other versions or platforms |

## Minimum record for a test claim

Record:

- repository and exact commit SHA;
- command and exit status;
- operating system and Python version;
- relevant dependency and vendor CLI versions;
- test count, pass/fail/skip counts;
- whether the test used a disposable fixture or real project;
- evidence provenance (automated, operator-reported, or inferred);
- known exclusions and limitations.

Do not publish credentials, personal paths, private state, or complete agent transcripts.

## Adapter-specific gates

| Adapter path | Automated checks | Separate runtime gate |
| --- | --- | --- |
| Generic wrapper | Process lifecycle, fixture isolation, checkpoint behavior | Operator-run session on the intended host |
| Codex native | Artifact shape, pinned command, state-home isolation | Authenticated model turn, reviewed hook trust, correlated native event |
| Claude native | Artifact shape and command generation | Authenticated session, explicit settings/trust review, correlated native event |
| OpenCode native | Version-specific artifact checks | Revalidate against the exact installed version |

A native hook is not certified by calling the receiver manually. A generic wrapper can provide useful process-exit checkpoints, but it is a distinct integration path.

## CI review checklist

- [ ] The workflow ran for the exact proposed head SHA.
- [ ] All required jobs completed successfully.
- [ ] Skips are understood and are not counted as executed tests.
- [ ] Build/package checks completed where configured.
- [ ] Tests did not access real user projects, secrets, or hosted services.
- [ ] Any platform-specific exclusions are stated.
- [ ] The final report links the run and records the tested SHA.

## Current alpha caveat

PMP alpha 1.0.0a1 has historical CI evidence for the adapter and recovery-probe work. That evidence must not be carried forward to a changed successor commit without rerunning CI on the new exact head. Authenticated native Codex/Claude hook delivery remains a separate operator gate.

created by stokonn with love <3
