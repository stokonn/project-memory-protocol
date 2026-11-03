# PMP next alpha — architecture review and merge plan

**Status:** reviewed merge plan for owner approval, 2026-11-03. This document does not authorize a merge, version bump, tag, or release.  
**Current baseline:** `main` is software `1.0.0a1`, protocol/schema `1.0`; PR #1 is squash-merged at `631c07280782e7e1`.  
**Target proposal:** `1.0.0a2` only after ordered merges, post-merge CI, and separate owner authorization. Not PMP 1.0 Stable.

## Objective

Improve real coding-agent handoffs while preserving PMP's local-first, non-destructive guarantees: bounded context, deterministic worktree identity, correctly installed optional hooks, private checkpoint recovery, and honest evidence.

PMP is not an LLM or transcript-storage service. Handoffs do not grant permission. No automatic secrets, private source, command output or full transcripts may be published. No forced Git operations, automatic release, or silent migration.

## Current GitHub state

| PR | Status | Base / dependency | Scope | Exact head | Exact-head CI |
| --- | --- | --- | --- | --- | --- |
| [#1](https://github.com/stokonn/project-memory-protocol/pull/1) | Merged | `main` | `pmp brief`, adapter discovery, synthetic output-size benchmark | merge `631c07280782e7e1` | Original corrected head passed 6/6 |
| [#5](https://github.com/stokonn/project-memory-protocol/pull/5) | Open, draft | `main` | Codex/Claude native command pins interpreter and worktree | `1a1d8cfdbb9c0f61ebac7a98b52104a2473b5b2d` | run [41508763089](https://github.com/stokonn/project-memory-protocol/actions/runs/41508763089), 6/6 PASS |
| [#6](https://github.com/stokonn/project-memory-protocol/pull/6) | Open, draft | PR #5 branch | Private state-home pinning, isolated Codex probe, recovery evidence | `6115764ba51072b30bcdec69ab8e0fdcb77963d3` | run [41627679097](https://github.com/stokonn/project-memory-protocol/actions/runs/41627679097), 6/6 PASS |
| [#4](https://github.com/stokonn/project-memory-protocol/pull/4) | Open, draft | `main` | This planning document | update in progress | Docs-only |

The validation matrix is Ubuntu/macOS/Windows × Python 3.11/3.14. PR #5 and #6 exact heads have all six jobs completed successfully. Green CI proves the tested repository behavior only; it does **not** prove authenticated live Codex or Claude native hook delivery.

PR #2 and #3 are historical stacked proposals. Their intended changes have clean successors in #5 and #6; do not merge the old stacked branches or close them until successor history is safely accepted.

## Review findings

### PR #5 — native command launcher

Reviewed all four changed files: README, adapter documentation, adapter implementation and security/CLI tests.

- Commands use the active Python interpreter, an explicit worktree path and POSIX shell quoting; they no longer assume the agent daemon can resolve a bare `pmp` on `PATH`.
- Codex remains gated to the inspected `codex-cli 0.163.0`; existing artifacts are not overwritten and user/global agent settings are not edited.
- Native installation is explicitly refused on Windows; wrapper launch remains the fallback. POSIX-only shell command generation is therefore not presented as cross-platform native support.
- Tests cover paths with spaces, invocation from outside the project, artifact generation and uninstall preservation.
- No blocking source-level finding identified in the reviewed diff. Real vendor hook delivery remains unverified.

### PR #6 — state-home pinning and isolated recovery probe

Reviewed all nine changed files, including the inherited #5 changes, probe fixture, operator evidence and tests.

- Native Codex/Claude command generation pins `PMP_STATE_HOME` as well as interpreter and project. The new subprocess test deliberately supplies a conflicting parent environment and checks that the checkpoint lands in the intended private store.
- Probe setup creates a disposable synthetic Git project, refuses an existing output directory, does not launch an LLM, and does not touch Gould.
- Probe inspection is designed as read-only and explicitly returns `live_vendor_hook_provenance_certified=false`; a hook-named checkpoint alone is not treated as proof of a real vendor event.
- Claude Code/Ollama evidence is labeled operator-reported wrapper evidence, not independently captured native-hook evidence.
- No blocking source-level finding identified in the reviewed diff. The native live-turn gate is still open.

### Cross-cutting boundaries

1. PR #1's Markdown escaped-newline issue was corrected before its merge; avoid bringing old stacked branches back.
2. Output-byte reductions are not measured model-token, credit, latency or cost reductions.
3. Protocol/schema remains `1.0`; no migration, private-store transfer, forced Git operation, stable tag or release is included.
4. CI has not exercised authenticated Codex/Claude sessions or the user's local Fedora environment.

## Required merge order

**Do not squash-merge #6 directly after #5 without rebuilding its branch.** PR #6 currently contains #5's changes in its ancestry. If #5 is squash-merged, merely retargeting #6 to `main` can make #5's changes appear again in #6's diff.

1. **Owner reviews and authorizes PR #5.** It is an independent change set against current `main`. Keep it draft until that approval.
2. **Merge #5 using the owner's selected merge strategy.** Then verify the resulting `main` SHA and run all six required CI jobs on the post-merge commit.
3. **Create a clean successor branch for #6 from the new `main`.** Port only #6's incremental changes: probe documentation, probe script/tests, operator evidence, state-home pinning, and its corresponding tests/docs. Do not copy #5's already-merged hunks or preserve the old stacked ancestry.
4. **Open a replacement PR for that clean #6 successor.** Compare its diff against `main`; it must contain only the incremental #6 scope. Run exact-head 6/6 CI. Keep the existing #6 draft as historical until the successor is reviewed; close it only after confirming no unique work was lost.
5. **After both changes are on `main`, run integration and backward-compatibility gates** on that exact combined commit.
6. **Only then present the alpha decision.** A version bump to `1.0.0a2` and any pre-release/tag require separate explicit owner authorization.

PR #4 is a planning artifact and is not a prerequisite for merging code. It should remain draft until the owner accepts the plan.

## Integration gates after code merges

- Run the full 6-job CI matrix on the exact combined `main` commit; verify package build and disposable examples.
- Exercise a fresh project and a copy of an existing alpha project: interrupted writes, damaged journal tail, shared handoff, source-change invalidation and private checkpoint preservation.
- Verify no secrets are published, untrusted text never becomes approval, no forced Git operations occur, and locks/private state are never silently reset.
- On the user's Fedora machine, separately test native hook delivery only with an already-authenticated, user-initiated Codex/Claude session and explicit trust review. No agent account changes, approval bypasses or production-project tests.
- Record exact source SHA, executed checks, counts, environment and limitations. Do not claim live hook certification from CI or a manually invoked receiver.

## Milestone decision

The proposed next milestone remains **alpha 1.0.0a2**, not Stable. Acceptance requires ordered clean merges, post-merge CI, correct documentation, no private-state misrouting, and evidence claims limited to what was actually observed. Native vendor events remain experimental until independently observed in a genuine authenticated model turn.

## Working rules

Review → bounded proposal → owner approval → implementation → exact-source validation → PR review → merge. Preserve original history. Do not touch Gould or any existing user PMP private checkpoint while testing. No automatic release or migration.

created by stokonn with love <3
