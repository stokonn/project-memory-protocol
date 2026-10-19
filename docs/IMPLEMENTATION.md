# Implementation checklist

- [x] A — Normative draft specification, six versioned JSON Schemas and strict validation.
- [x] B — Packaging, safe initialization, config/state, Git identity, ordered journal,
  immutable checkpoints, evidence, handoff, read-only recovery and explicit reports.
- [x] C — Cooperative sessions, independent optional watcher, generic/vendor process
  wrappers and reversible documented native integration artifacts.
- [x] D — 92 local automated tests; wheel/sdist build, clean offline installation,
  extracted source-distribution tests, failure/restart scenarios and privacy checks.
- [x] E — Executed disposable Goldberg-style workflow and owner readiness proposal.

These checkmarks cover implemented alpha work and local validation, not stable certification.
Publication checkpoint is now on public GitHub under owner-approved MIT.
Open gates: Windows CI (one remaining failure) and native agent runtime verification.
CI for `bd311e34a4bc0c0eb2215ebe5a02ff1505f17d89`: Ubuntu and macOS pass on 3.11/3.14.
See READINESS.md for observed platform jobs; no full PMP 1.0 certification is claimed.
See READINESS.md for operational limits and VALIDATION.md for executed evidence.
No stable release/tag or actual Goldberg integration is authorized or performed.
