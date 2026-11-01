# Operator-reported Claude Code / Ollama PMP wrapper recovery test — 2026-11-01

**Scope:** a genuine user-operated integration exercise in a disposable synthetic Git
fixture. This is **reported, redacted operator evidence**, not a CI automation result,
not an independently instrumented runtime trace, and **not certification of native hooks**.

## Provenance and environment

- Test was performed by the repository owner on Fedora, using the checked-out
  PMP development branch `feat/codex-live-probe-20261101`.
- Python 3.14 and editable PMP alpha `1.0.0a1`; operator reported
  Codex CLI `0.166.0` installed, but **Codex was not the agent used in this test**.
- Agent: **Claude Code launched through Ollama**, as reported by the operator.
  `gemma4:31b-cloud` was discussed as the model; the provider/model identity
  was **not independently verified from runtime metadata**.
- Integration path: `pmp launch generic -- ...` with private
  `PMP_STATE_HOME` outside a brand-new synthetic Git worktree.
  No native Claude or Codex hooks were enabled.
- No credentials, user paths, full AI transcripts, or private-store contents
  were copied into the repository. The disposable Git HEAD reported by the
  read-only inspector was `90680afda1dff1e626da52cbe347c5fd74b38606`.

## Observed first session

1. The agent read the fixture policies and approved task scope.
2. It changed `app.py` from `return 41` to `return 42` and ran:
   `python3 -c "from app import answer; assert answer() == 42; print('Verification successful: answer() returns 42')"`.
   The operator-provided terminal output showed that assertion succeeding.
3. A read-only `examples/codex_live_probe.py inspect` during the first
   session reported:
   - `change_to_42_observed: true`
   - `private_checkpoint_count: 1`, `damaged_checkpoints: 0`
   - uncertainty that a session lease existed and current source differed
     from the checkpoint.
4. After the operator finished that agent session, a fresh read-only
   inspection reported:
   - `change_to_42_observed: true`
   - `private_checkpoint_count: 2`, `damaged_checkpoints: 0`
   - `worktree_complete: true`, `uncertainty: []`
   - `native_hook_named_checkpoints: 0`
   - initial Git HEAD equal to current Git HEAD (the source change was
     uncommitted and preserved).

This supports successful creation of wrapper-managed metadata checkpoints and
normal lease cleanup after session exit. No full dirty-source backup is
claimed. The previously executed Python assertion was **not** recorded as
a source-bound PMP `verify` evidence record.

## Observed second, separate agent session

The operator instructed a new Claude Code session to inspect canonical policy,
run `pmp brief` and `pmp resume`, and independently inspect Git status,
the `app.py` diff and source. The prompt deliberately did not disclose
the target answer value.

The agent's reported response independently identified:
- the original task (change `answer()` from 41 to 42 and verify it),
- that the dirty worktree already contained the intended change,
- that PMP's `verification` evidence array was empty, and
- that checkpoints preserve task/history/source identity context but
  must be cross-checked against actual Git/source.

It did **not** repeat the source edit or claim that PMP had verified the
Python assertion. The operator supplied the tool-call and final response
transcript excerpts; no full transcript was ingested into PMP.

## Results and limits

| Gate | Outcome | Grounding |
| --- | --- | --- |
| Real agent performs scoped edit | PASS (operator evidence) | `app.py` diff and successful Python assertion |
| Generic PMP wrapper persists checkpoints | PASS (operator evidence) | 1 checkpoint during run, 2 after exit |
| Checkpoint integrity and lease cleanup | PASS (operator evidence) | 0 damaged, final uncertainty empty |
| Second agent reads and uses PMP context | PASS (operator evidence) | `pmp brief`, `pmp resume`, Git inspection and independent summary |
| Native Codex/Claude hook executes on model turn | NOT TESTED | No native hooks installed or fired |
| Automated verified-test capture | NOT VERIFIED | PMP verification array empty |
| Causal improvement over no-PMP baseline | NOT MEASURED | Agent also read task scope and Git diff |
| Token/cost savings | NOT MEASURED | No provider accounting or baseline |

**Conclusion:** this is the first reported real-user, two-session recovery
exercise of the PMP **generic wrapper** with Claude Code via Ollama. It
supports real workflow continuity, with limitations stated above, and does
not close Codex native-hook or independent-provider certification gates.

## Follow-up, deliberately not undertaken here

Capture actual source-bound tests via an explicit `pmp verify` invocation;
measure an equivalent no-PMP baseline; optionally verify native hooks for
specific installed agent versions using reviewed, local-only configurations.
Do not merge PRs, publish stable releases, access Gould, or infer automatic
permission to deploy based on this evidence.
