# Implementation checklist

- [x] A — Normative draft specification, six versioned JSON Schemas and strict validation.
- [x] B — Packaging, safe initialization, config/state, Git identity, ordered journal,
  immutable checkpoints, evidence, handoff, read-only recovery and explicit reports.
- [x] C — Cooperative sessions, independent optional watcher, generic/vendor process
  wrappers and reversible documented native integration artifacts.
- [x] D — 96 local automated tests; wheel/sdist build, clean offline installation,
  extracted source-distribution tests, failure/restart scenarios and privacy checks.
- [x] E — Executed disposable Goldberg-style workflow and owner readiness proposal.
- [x] F — Live OpenCode v2.0.32 runtime integration in a disposable Git fixture:
  wrapper session lifecycle, checkpoints, shared handoff, fresh-clone recovery,
  independent-agent context recovery and native plugin snapshot capture.

These checkmarks cover implemented alpha work and local validation, not stable certification.
Publication checkpoint is now on public GitHub under owner-approved MIT.
Open gates: native runtime certification beyond OpenCode v2.0.32; cross-platform CI is fully green.
CI for `78c846f261688c91ec0743cdbbbd999fdbea7832`: all six Ubuntu/macOS/Windows
3.11/3.14 jobs succeeded. See VALIDATION.md for CI-fix and live-runtime records.
See READINESS.md for observed platform jobs; no full PMP 1.0 certification is claimed.
See READINESS.md for operational limits and VALIDATION.md for executed evidence.
No stable release/tag or actual Goldberg integration is authorized or performed.
