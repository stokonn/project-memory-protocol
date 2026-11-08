# PMP alpha release gates

**Current baseline:** software alpha 1.0.0a1; protocol/schema 1.0.  
**Proposal only:** the next alpha may be considered after the gates below. This document does not authorize a version bump, tag, publication, or stable release.

## Gate 1 — source integrity

- [ ] All intended work is on clean branches based on current `main`.
- [ ] No stale stacked branch is merged directly.
- [ ] The proposed release commit and its full diff have been reviewed.
- [ ] No unrelated project files, private state, credentials, or generated machine-local hook artifacts are included.

## Gate 2 — correctness

- [ ] Exact-head CI passes on every required OS/Python combination.
- [ ] Package build and installation checks pass.
- [ ] Fresh-project initialization and read-only inspection pass.
- [ ] Existing alpha state remains readable; no silent migration or reset occurs.
- [ ] Interrupted writes, damaged journal tails, conflicting state roots and source-change invalidation have explicit tests.
- [ ] Skipped tests and platform exclusions are reported honestly.

## Gate 3 — integration evidence

- [ ] Generic wrapper behavior is distinguished from native hooks.
- [ ] Any native-hook claim is backed by a genuine authenticated operator session and correlated event evidence.
- [ ] User-specific host testing is recorded separately from CI.
- [ ] No approval, trust, sandbox, or permission bypass was used.
- [ ] Token/cost claims use provider accounting and a meaningful baseline; output bytes alone are not token savings.

## Gate 4 — documentation and compatibility

- [ ] README and adapter docs match the actual supported versions and platform gates.
- [ ] Recovery instructions preserve private state and user changes.
- [ ] Evidence records distinguish automated results, operator reports and inference.
- [ ] Protocol/schema compatibility and any migration are documented.
- [ ] Known limitations are visible before installation.

## Gate 5 — owner decision

Only after gates 1–4 are reviewed should the maintainer explicitly decide whether to:

1. keep the current alpha unchanged;
2. authorize a new alpha version and tag; or
3. defer release while additional runtime evidence is collected.

A green CI run is necessary for code changes but is not sufficient for a release decision. No workflow should silently create a release or tag.

created by stokonn with love <3
