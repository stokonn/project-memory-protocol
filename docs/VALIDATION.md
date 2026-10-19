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

## Owner-authorized publication preflight

Owner approved public repository creation, MIT, development push and CI verification.
Clean preflight HEAD: e7be1533132307e80091c25a929db360c0162c02. All 88 historical Git
blobs were scanned with PMP's secret patterns; findings were reviewed and classified
as synthetic secret-detector fixtures (also echoed by JUnit parameter names). No real
credential matches were found. Private XDG recovery, .venv and build outputs remain
untracked/ignored. No history rewrite, cleanup, Goldberg operation or stable release.
Pattern scanning is incomplete and is not a guarantee that every secret format is detected.

Publication revision: 90/90 local tests passed in 16.39 seconds; wheel and sdist
rebuilt successfully with MIT metadata via `python -m build --no-isolation`.
`pmp check` passes. Current tracked-file scan has only the previously reviewed synthetic
test/report matches. Repository created PUBLIC at https://github.com/stokonn/project-memory-protocol.

Git transport and GitHub API verified published main SHA
`d11c00422c3f0f44e18f350e8b0899f148d4cdc1`. GitHub recognizes MIT.
Actions workflow is active; observed initial-run jobs are recorded in READINESS.md.
Publication/docs-only follow-up commits have not been relabeled with earlier test evidence.

## macOS watcher CI failure — root cause, fix and verified results

Commit `bd311e34a4bc0c0eb2215ebe5a02ff1505f17d89` fixed the macOS
`tests/test_security_cli.py::test_watcher_lifecycle_and_launch` failure.

Root cause (two parts): in `launch()`, the parent acquires `writer.lock` for the
`session launch` checkpoint immediately after spawning the independent watcher
subprocess; on macOS the watcher's first `heartbeat()` routinely collided with that
still-held lock, raising a transient `Writer lock exists` PMPError. The watcher loop
recorded `last_error` on failure but never cleared it on later successful iterations,
so one recovered startup contention was permanently baked into final `stopped`
metadata, violating the test's no-error assertion. The same mechanism affected
Windows; the earlier Python 3.11 macOS traceback was identical to 3.14.

Fix (smallest correct): the watcher loop's try/except gained an `else` clause setting
`metadata['last_error']=None` after each successful iteration, so metadata reports the
latest iteration outcome. Diff: 46 insertions, 0 deletions. No lock, lease, ownership
or takeover logic was touched; a *persistent* failure re-records every iteration and
remains in final metadata.

Two deterministic regression tests were added: one-shot contention followed by success
must not survive into final metadata (fails on the pre-fix code, verified by temporary
revert), and persistent writer-lock contention must remain reported (safety guard
against suppressing real errors). Existing assertions were not modified.

Local: `python -m pytest -q` — **92 passed** (90 prior + 2 new), zero skips/failures.
Actions run https://github.com/stokonn/project-memory-protocol/actions/runs/39237978499
for exact SHA `bd311e34a4bc0c0eb2215ebe5a02ff1505f17d89`:

| Job | Status | Conclusion |
| --- | --- | --- |
| test (ubuntu-latest, 3.11) | completed | success |
| test (ubuntu-latest, 3.14) | completed | success |
| test (macos-latest, 3.11) | completed | success |
| test (macos-latest, 3.14) | completed | success |
| test (windows-latest, 3.11) | completed | failure |
| test (windows-latest, 3.14) | completed | failure |

Run conclusion: failure, solely due to the Windows jobs. The watcher lifecycle test
now passes on macOS and Ubuntu, and on Windows the only remaining failure is a
different test (see below). No stable tag, release or Goldberg operation was performed.

## Windows fresh-clone CI failure — root cause, fix and verified results

Commit `3eb799939598652a05575d91f88601161b34fe06` fixed the remaining Windows CI failure
`tests/test_sessions_git.py::test_fresh_clone_reads_shared_memory`.

Root cause: Git for Windows ships `core.autocrlf=true`, so `git clone` rewrites the
committed LF-only `.pmp/handoffs/*.json` files to CRLF on checkout. `validate_handoff`
compared `sha256(raw file bytes)` against `handoff_hash`, recorded at checkpoint
creation over the original LF bytes; the CRLF-smudged bytes mismatched, so every
shared checkpoint in a fresh clone was marked damaged and `shared_checkpoints` was
empty. Linux/macOS runners never rewrite line endings. The sibling test
`test_export_commit_relationship` passed on Windows because `git show` reads pristine
blob bytes from the object database, which checkout smudging never touches. All other
raw hashes in the protocol cover private local files (backups, reports) or in-memory
blobs; the seal-based `intact()` checks are already EOL-insensitive because they
re-digest canonical JSON of the parsed content.

Fix (smallest correct): `validate_handoff` accepts the recorded hash over either the
exact raw bytes (checked first, unchanged behavior) or the CRLF->LF-normalized bytes.
Line endings carry no protocol meaning for a JSON document that is parsed and
schema-validated anyway; altered content still fails both hash comparisons, and the
handoff is still schema-validated after hashing. No schema, protocol, stored-record
or repository-configuration change; no migration required.

Two regression tests were added. `test_fresh_clone_shared_memory_survives_crlf_checkout`
clones with `git -c core.autocrlf=true`, deterministically reproducing the Windows
checkout semantics on any platform; it failed with the exact CI symptom (`assert ([])`)
on the pre-fix code and passes after. `test_shared_handoff_content_tamper_still_refused`
forges a completion claim inside a cloned handoff and proves damaged records are still
refused, guarding against weakening the integrity check. Existing assertions unmodified.

Local: `python -m pytest -q` — **94 passed** (92 prior + 2 new), zero skips/failures.
Actions run https://github.com/stokonn/project-memory-protocol/actions/runs/39241333216
for exact SHA `3eb799939598652a05575d91f88601161b34fe06` — all six jobs green:

| Job | Status | Conclusion |
| --- | --- | --- |
| test (ubuntu-latest, 3.11) | completed | success |
| test (ubuntu-latest, 3.14) | completed | success |
| test (macos-latest, 3.11) | completed | success |
| test (macos-latest, 3.14) | completed | success |
| test (windows-latest, 3.11) | completed | success |
| test (windows-latest, 3.14) | completed | success |

Run conclusion: success. This is the first fully green cross-platform matrix. It
certifies the alpha test suite on these runner images only; native agent runtime
verification remains outstanding and no stable release/tag exists.

## Live OpenCode v2.0.32 runtime integration — verified results

Date: 2026-10-19. Host: Linux (fedora), Git disposable fixture
`/tmp/opencode/pmp-fixture-*` with private state in a separate external
`PMP_STATE_HOME`. Agent binary: **opencode v2.0.32** (inspected via
`opencode --version` and `pmp adapter inspect opencode`). Actual Goldberg and the
PMP source checkout were not used as test targets; the PMP checkout only supplied
the CLI under test.

### Genuine test evidence — all executed, not simulated

1. **Fixture initialization**: fresh `git init` fixture, `pmp init`, `pmp task
   activate` with a local synthetic scope file, `pmp session start --owner`
   acquired a real writer lease (session UUID + live PID recorded).
2. **Manual session lifecycle**: snapshot (sequence 1), private handoff, shared
   handoff (`handoff --shared`), `session end` all succeeded; `pmp check` valid.
3. **Wrapper workflow with a real agent session**: `pmp launch opencode -- run
   --format json "..."` executed a genuine `opencode run` turn (session
   `ses_eab97250affemG24kyhXt6CZpa`, model reply received, exit 0). The wrapper
   recorded `session launch` and `session stopped` checkpoints (sequences 2–5,
   including the first wrapper-arg attempt that failed honestly with exit 1 and
   its own launch/stop pair). Checkpoint chain `previous` links were contiguous.
   Note: wrapper args after `--` are appended to the binary name, so the first
   argument must be an `opencode` subcommand (e.g. `run`); duplicating the
   binary name fails with the agent's own usage error — PMP propagated it.
4. **Resume and cleanup**: `pmp resume` and `pmp check` passed in the fixture;
   `sync --export` exported 10 records; memory-only `sync --commit` created a
   allowlisted commit; `sync --push` correctly **refused** without a configured
   GitHub reference (exit 2). Ordinary `git push` to a local bare remote
   (fixture plumbing, no GitHub) succeeded.
5. **Fresh independent recovery**: a fresh clone with an empty private state
   recovered all 5 shared checkpoints with zero damaged records and zero
   uncertainty; `pmp check` correctly flagged the two untracked-in-clone
   references (canonical policy, approved scope) as errors rather than guessing.
6. **Independent agent session recovery**: a brand-new agent session (fresh
   subagent, no prior conversation) working only from the clone recovered the
   task ID, phase/status, last checkpoint ID and reason, checkpoint count and
   integrity, and all five safety restrictions. Honest gaps it reported:
   private journal event contents, agent/tool identity and the scope/policy
   documents are not recoverable from shared state alone (by design — private
   state stays private; scope files are owner files).
7. **Native plugin — first attempt failed honestly**: the previously shipped
   artifact (named `export const`, `session.idle`, `$` template) was **rejected
   by opencode v2.0.32** at load: `Plugin must export a default definition with
   an id and an effect or setup function`. No snapshot was produced. The public
   plugins docs page still shows the old shape; the installed binary disagrees.
8. **Native plugin — corrected shape validated live**: probe sessions
   established the v2 contract: default export `{ id, setup }`; `setup(ctx)`
   exposes `ctx.event` whose `subscribe(cb)` returns an **async iterable**;
   project directory is `ctx.location.directory` (`ctx.directory` is undefined);
   v2.0.32 `opencode run` mode never emitted `session.idle` in any observed
   session — the turn boundary is `session.execution.succeeded`. With the
   corrected artifact, real OpenCode turns produced PMP checkpoints with reason
   `opencode-session-idle` (sequences 7 and 8, reproduced twice including from
   the exact artifact now shipped by `adapter install opencode --native`).
   Detached spawning is required: an attached child is killed at agent exit.
9. **Cleanup**: manually copied plugin removed manually; `adapter uninstall
   opencode` removed only its unchanged manifested files; fixture `pmp check`
   valid afterwards.

### What this does and does not certify

Certified: the PMP generic process wrapper around the real `opencode` binary on
Linux/opencode v2.0.32, including lease acquisition, launch/stop checkpoints,
watcher lifecycle, shared export, fresh-clone recovery and independent-agent
context recovery; and the experimental native OpenCode plugin's snapshot capture
on that exact version (manual copy into `.opencode/plugins/`, `opencode run
--standalone` mode).

Not certified: other OpenCode versions (the plugin API is version-dependent and
the public docs lag the binary); interactive TUI/serve modes; Codex and Claude
native hooks (no live sessions); Windows/macOS agent hosts; crash-time hook
delivery (a turn boundary is not a process exit); authentication/permission
flows of the agent. No stable release/tag was created; Goldberg untouched.

Local suite after the artifact fix and two new regression tests:
`python -m pytest -q` — **96 passed**, zero skips/failures.
