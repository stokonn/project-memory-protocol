# PMP next alpha — architecture review and staged upgrade plan

**Status:** planning proposal for owner review, 2026-11-02. No implementation or release authorization is implied.  
**Current baseline:** `main` advertises software version `1.0.0a1`, protocol/schema `1.0`.  
**Suggested next software milestone:** `1.0.0a2` **only after explicit acceptance**; not PMP 1.0 Stable.

## Objective

Make PMP more useful for real coding-agent handoffs without losing its local-first,
non-destructive guarantees. Priority: accurate short context, deterministic worktree
identity, correctly installed optional hooks, source-bound evidence, and honest
recovery after interruption or agent switch.

PMP is **not** an LLM or transcript storage service. Hand-offs do not grant
permission. No automatic secrets, private source, command output or full transcripts
may be published. No forced Git operations, automatic release, or silent migration.

## Evidence baseline

This review used the GitHub repository's `main` documentation/source and the
three *open stacked PRs*, plus their actual GitHub Actions run statuses.
No source checkout, local Python tests, native agent turns, production repository
data, or real user PMP state were executed or modified for this review.

| Candidate | Dependency | Main scope | Head checked | GitHub Actions |
| --- | --- | --- | --- | --- |
| [PR #1](https://github.com/stokonn/project-memory-protocol/pull/1) | `main` | `pmp brief`, adapter discovery, synthetic output-size benchmark | `017972ea88fc` | [run 41255058393](https://github.com/stokonn/project-memory-protocol/actions/runs/41255058393), 6/6 PASS |
| [PR #2](https://github.com/stokonn/project-memory-protocol/pull/2) | PR #1 | Native Codex/Claude commands pin Python and worktree | `aa2735cd3225` | [run 41256035868](https://github.com/stokonn/project-memory-protocol/actions/runs/41256035868), 6/6 PASS |
| [PR #3](https://github.com/stokonn/project-memory-protocol/pull/3) | PR #2 | Explicit private state root, isolated Codex live probe and recovery evidence | `bcc6273cf53c` | [run 41258161780](https://github.com/stokonn/project-memory-protocol/actions/runs/41258161780), 6/6 PASS |

The matrix is Ubuntu/macOS/Windows × Python 3.11/3.14.
**CI passes do not prove vendor-native hook delivery in live authenticated sessions**.
PR #3 also contains operator-reported Claude Code/Ollama *wrapper* recovery evidence;
the report explicitly does not certify native hooks or token savings.

Current core structure: `src/pmp/core/`, `events/`, `checkpoints/`,
`recovery/`, `verification/`, `github/`, `watcher/`, `adapters/`,
`security/`, `cli/`. The normative contract remains `spec/1.0.md`.

## Findings requiring action

1. **Observed documentation defect in PR #1:** `docs/ADAPTERS.md` and
   `docs/IMPLEMENTATION.md` contain literal `\\n` characters embedded in
   paragraphs where Markdown line breaks were intended. Correct in the originating
   PR and verify that rendered Markdown is readable; avoid propagating the typo
   through later stacked branches.
2. **Current runtime-certification gap:** the exact Codex/Claude native hook
   integration remains unproven by a real authenticated hook-fired model turn.
   A generated artifact, manual receiver call, test fixture, or wrapper result
   must not be represented as a vendor hook firing.
3. **Machine-local artifact portability:** PRs #2–#3 deliberately pin the Python
   executable, worktree and `PMP_STATE_HOME`. Verify behavior after moving a
   checkout, recreating a virtual environment or starting an agent daemon with
   a different environment. Fail visibly instead of silently writing to the wrong store.
4. **Benchmark interpretation:** PR #1's demonstrated reduction is in CLI output
   bytes, **not measured model tokens, credits, latency of agent responses or costs**.
   Keep that distinction throughout README, releases and marketing text.
5. **Protocol/recovery boundary:** `1.0` schema and local/private record identity
   should stay unchanged for this milestone. No automatic migration, history rewrite
   or transfer of private recovery stores.

## Execution checklist (owner approval required for implementation and merge)

### Stage 0 — bounded review and acceptance criteria

- [x] Inspect `main` architecture/specification, alpha status and open PR stack.
- [x] Check exact PR head runs and all six jobs per PR.
- [x] Identify PR #1 literal-newline documentation issue.
- [ ] Review each PR's entire diff, regressions and test evidence together for
      stacked dependencies; record any additional blocking finding with file/line.
- [ ] Confirm that intended next milestone is alpha rather than Stable.

### Stage 1 — compact context and adapter discovery (PR #1)

- [ ] Fix literal `\\n` in Markdown and align descriptions with CI evidence.
- [ ] Review `pmp brief` for no unexpected source disclosure, correct current HEAD,
      source-bound applicable evidence, explicit uncertainty and bounded output.
- [ ] Check pre-init `pmp adapters` and `adapter inspect` are truly read-only,
      including paths with spaces and disabled/missing vendor executables.
- [ ] Review synthetic benchmark and keep byte-size numbers separate from token claims.
- [ ] Owner review → merge PR #1 **only if** all mandatory checks pass.

### Stage 2 — native hook path correctness (PR #2)

- [ ] Rebase/retarget the stacked PR onto the newly accepted `main`.
- [ ] Test interpreter/worktree quoting, project selection, missing binary,
      moved interpreter and daemon `PATH` divergence in disposable fixtures.
- [ ] Keep existing vendor approval, trust and sandbox settings untouched.
- [ ] Owner review → merge PR #2 only after fresh exact-head CI success.

### Stage 3 — recovery-store pinning and live probe (PR #3)

- [ ] Rebase/retarget after PR #2; verify `PMP_STATE_HOME` selection independently
      from current process directory and agent daemon environment.
- [ ] Ensure `setup` refuses overwrites and `inspect` is read-only.
- [ ] If the operator elects to run a genuine authenticated Codex turn, record
      real vendor-event provenance, private checkpoint integrity, second-agent
      recovery and clear failure cases. Do **not** fabricate success.
- [ ] Preserve operator-reported Claude/Ollama wrapper evidence with its
      reported/not-independently-captured label.
- [ ] Owner review → merge PR #3 only after checks appropriate to its scope.

### Stage 4 — integration and backwards-compatibility gate

- [ ] On the resulting `main` commit, run the full 6-job CI matrix; ensure
      package builds and disposable demos pass.
- [ ] Exercise a fresh project and an **existing alpha project copy**, including
      interrupted writes, damaged journal tail, shared handoff, source-change
      invalidation and private checkpoint preservation.
- [ ] Check security: no secret publication, untrusted text never becomes approval,
      no forced Git operations and no auto-reset of locks or private state.
- [ ] Record exact source SHA, executed checks, counts, environment, limitations.
- [ ] Update README, CLI, adapter and readiness docs with accurate supported
      versions; avoid claims not backed by live evidence.

### Stage 5 — milestone decision

- [ ] Present evidence and remaining gaps to owner.
- [ ] Only with separate authorization, bump software version to the agreed
      next **alpha** and consider a pre-release.
- [ ] No stable release/tag, migration, real Gould integration, agent-account
      changes or public checkpoint upload by default.

## Acceptance definition

The upgrade is acceptable when the feature stack is merged in order with passing
post-merge CI, the documentation renders properly, read-only operations do not
mutate projects, private state is never mislocated or published silently, and every
integration claim is scoped to actually observed evidence. Unverified native
vendor events stay clearly labeled experimental.

## Working rules

Review → bounded proposal → owner approval → implementation → test with exact
source identity → PR review → merge. Preserve original history and avoid touching
Gould or any user's existing PMP private checkpoints while testing. Never declare
a stage complete from an older unrelated CI run.

created by stokonn with love <3
