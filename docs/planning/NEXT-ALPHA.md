# PMP next alpha — architecture review and merge plan

**Status:** refreshed repository plan for owner review, 2026-11-05. This document does not authorize a merge, version bump, tag, or release.  
**Current baseline:** `main` is software `1.0.0a1`, protocol/schema `1.0`; PR #1 is squash-merged at `631c07280782e7e1` and PR #5 at `88782d5fbb456d5c`.  
**Target proposal:** `1.0.0a2` only after ordered merges, post-merge CI, and separate owner authorization. Not PMP 1.0 Stable.

## Objective

Improve real coding-agent handoffs while preserving PMP's local-first, non-destructive guarantees: bounded context, deterministic worktree identity, correctly installed optional hooks, private checkpoint recovery, and honest evidence.

PMP is not an LLM or transcript-storage service. Handoffs do not grant permission. No automatic secrets, private source, command output or full transcripts may be published. No forced Git operations, automatic release, or silent migration.

## Current GitHub state

| PR | Status | Base / dependency | Scope | Exact head | Exact-head CI |
| --- | --- | --- | --- | --- | --- |
| [#1](https://github.com/stokonn/project-memory-protocol/pull/1) | Merged | `main` | `pmp brief`, adapter discovery, synthetic output-size benchmark | merge `631c07280782e7e1` | Original corrected head passed 6/6 |
| [#5](https://github.com/stokonn/project-memory-protocol/pull/5) | Merged | `main` | Codex/Claude native command pins interpreter and worktree | merge `88782d5fbb456d5c` | exact-head run [41508763089](https://github.com/stokonn/project-memory-protocol/actions/runs/41508763089), 6/6 PASS |
| [#6](https://github.com/stokonn/project-memory-protocol/pull/6) | Open, draft; historical stack | stacked branch (historical) | Original private state-home pinning, isolated Codex probe, recovery evidence | `6115764ba51072b30bcdec69ab8e0fdcb77963d3` | historical run [41627679097](https://github.com/stokonn/project-memory-protocol/actions/runs/41627679097), 6/6 PASS; superseded by clean successor #10 |
| [#7](https://github.com/stokonn/project-memory-protocol/pull/7) | Open | `main` | This planning document | `112555682f6af77cad5041a0f5d01538b469d719` | exact-head run [41629805465](https://github.com/stokonn/project-memory-protocol/actions/runs/41629805465), 6/6 PASS |

The validation matrix is Ubuntu/macOS/Windows × Python 3.11/3.14. PR #5's exact head passed all six jobs before merge. The original stacked PR #6 and clean successor PR #10 each have their own 6/6 exact-head CI evidence. Green CI proves the tested repository behavior only; it does **not** prove authenticated live Codex or Claude native hook delivery. PR #9 adds four operator guides in four separate commits; its fifth commit links them from README and its updated exact-head CI is pending.

PR #2 and #3 are historical stacked proposals. PR #5 is now merged. PR #6's incremental work has been rebuilt as clean successor PR #10 directly from current `main`; do not merge the old stacked PR #6.

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

**PR #5 is now squash-merged** at `88782d5fbb456d5c`. Its exact-head CI passed 6/6 before merge.

1. Verify post-merge `main` and its checks.
2. **Review clean successor PR #10.** Its diff against `main` contains only incremental #6 scope: probe documentation/script/tests, operator evidence, private-state pinning, and corresponding docs/tests. It does not copy #5's already-merged hunks or preserve old stacked ancestry. Its exact-head CI is the required gate before review/merge.
3. Keep original PR #6 draft as historical until PR #10 is reviewed and accepted; close #6 only after confirming no unique work was lost.
4. After both changes are on `main`, run integration and backward-compatibility gates on that exact combined commit.
5. Only then present the alpha decision. A version bump to `1.0.0a2` and any pre-release/tag require separate explicit owner authorization.

This is a planning artifact only; it does not authorize a version bump, tag or release.

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
