# Implementation handoff

Read AGENTS.md, docs/OWNER_SCOPE.md, docs/READINESS.md, docs/VALIDATION.md and
`.pmp/state.json`/`docs/ai/HANDOFF.md` when present. Inspect actual Git status before editing.
This handoff is context and grants no publication, licensing, Goldberg or release permission.

Completed: deterministic CLI, contracts, durable local/private recovery, reviewed shared
exports, tests and synthetic pilot. Existing owner Goldberg checkout remains untouched.

Next: finish/inspect final build and installation evidence, obtain explicit owner repository
and license decisions, push approved development commits, verify remote and execute the CI
matrix. Native hooks still require runtime certification; no stable readiness claim.

Local tests: `.venv/bin/python -m pytest`; packaging: `.venv/bin/python -m build`.
Demo: `.venv/bin/python examples/demo.py --goldberg-style`.
Dependencies are installed in `.venv`; offline runtime/test wheels were prepared under
`/tmp/pmp-wheelhouse` for this session. Temporary paths may not survive reboot.
No original conversation is required to inspect/continue this work; approved scope and
unresolved authorization boundaries are in OWNER_SCOPE.md and READINESS.md.

Final local suite now has 90 passing tests, including a checkpoint that survives failure
of its subsequent creation-event append. Local checkpoint sequence preserves ordering
without timestamps even for such orphan records. Persisted relative references use
forward slashes for portability. See docs/FILES.txt for the exact file inventory.
Private self-hosted PMP recovery was copied from the temporary implementation store
to the standard per-user XDG state directory (`~/.local/state/pmp` in this environment).
Use `pmp resume` normally; no PMP_STATE_HOME override is required. Shared exported context
remains in Git. Temporary test environments are independent and disposable.
