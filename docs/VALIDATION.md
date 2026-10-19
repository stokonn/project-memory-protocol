# Executed validation

Initial inspection: Python 3.14.8, Git 2.56.0, Codex CLI 0.163.0.
Claude CLI absent. OpenCode present but version command failed opening its read-only
user log path. gh auth status reported an invalid active token; initial network calls
could not reach GitHub. Workspace was empty with a read-only .git placeholder;
authorized git init created the local main branch.

No automated test result is claimed here until the test suite has actually executed.

2026-10-19 intermediate run: `python -m pytest -q --junitxml=/tmp/pmp-tests.xml`
executed 70 tests, 70 passed in 5.81 seconds. Included killed-session observer/restart,
fresh-clone shared memory, truncated journal repair and atomic failure fixtures.
Earlier first run: 67 passed/1 failed due to a mock rejecting keyword arguments; fixed
mock and reran successfully. No production data or Goldberg checkout used.

`python examples/demo.py --goldberg-style` completed in `/tmp/pmp-demo-0tg0i42m`:
one real unittest passed, dirty source checkpoint persisted, simulated interrupted lease
was detected and explicitly released, shared handoff was read without an agent, and
fixture policy/branch/untracked owner release notes were preserved.

Read-only GitHub recheck outside network sandbox: account stokonn authenticated through
keyring; planned repository could not be resolved. No public repository was created.

Expanded hardening run: `python -m pytest -q --junitxml=/tmp/pmp-tests.xml`:
88 passed in 16.40 seconds on Linux/Python 3.14.8. Covers cross-process writer exclusion,
clock reversal, backup/handoff tampering, report/approval/count release gates, branch
protection refusal, separate failed CI on confirmed synced SHA, watcher crash isolation,
and an actual subprocess-based Goldberg-style demo. A new private-store safety check
initially rejected one fixture that put its private store inside its worktree; corrected
fixture to use external private state, then reran successfully.

Windows process liveness uses a read-only query API; that platform-specific branch is
not yet runtime tested. Native adapter and multi-platform CI results are not claimed.

Final implementation suite (after checkpoint orphan ordering and wire-path hardening):
`python -m pytest -q --junitxml=/tmp/pmp-tests.xml` — **90 passed**, zero failures,
errors or skips. Preserved JUnit: docs/evidence/pytest.xml. All tests are actually executed.

Packaging verification already executed on the preceding 89-test code revision:
- `python -m build --no-isolation`: wheel and source distribution built successfully.
- Fresh `/tmp/pmp-installed-check` venv installed wheel and dependencies using
  `--no-index --find-links=/tmp/pmp-wheelhouse`; CLI 1.0.0a1 loaded from its installed
  site-packages, independent of editable source checkout.
- Full extracted source-distribution tests against installed wheel: **89 passed in
  16.58 seconds**; JUnit preserved as docs/evidence/installed-pytest.xml.
- Separate fresh `/tmp/pmp-source-installed-check` installed the tar.gz with normal
  isolated packaging from the offline wheelhouse; CLI version worked and its actual
  Goldberg-style demo executed one passing unittest plus interruption/handoff preservation.

Final artifact rebuild/reinstallation is performed after this documentation checkpoint.
Build outputs are intentionally ignored by Git under dist/; inspect dist/SHA256SUMS for
actual local artifact digests. Packaging validation does not imply a published package.
Only Python 3.14 is installed locally. CI matrix is present but unexecuted remotely.
Native vendor sessions remain untested; no claim of production/stable readiness.

Final rebuilt wheel installation was rerun against the final extracted source-distribution
tests: **90 passed in 16.73 seconds** (zero skips/failures/errors). The current preserved
installed-pytest.xml is this final run, superseding the intermediate 89-test artifact.
PMP self-verification also executed 90 tests in 16.58 seconds against clean source commit
`dec3b56155e4e44f16a80edcfea30865902efd18`, fingerprint
`a89cefd8988b467314db16becf9952703cf8931cc8a06b967874cf8617e03c89`.
Its canonical evidence is exported under .pmp/evidence, with outcome passed, credibility
verified and tests_executed=90. Later documentation/memory commits invalidate applicability
to their newer Git HEAD; final exact-HEAD evidence is rerun and retained privately.
Injected low-disk/write failures are fixtures, not physical disk-exhaustion experiments.
Process deaths are real disposable subprocess kills; no reboot/power-loss claim is made.
