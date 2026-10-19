# Goldberg pilot proposal — approval required before real integration

The real `~/Projects/Opus` checkout and stokonn/Goldberg were not modified or used for
integration tests. The fixture below is synthetic, derived only from the owner's supplied
workflow description, not a copy of private project files. No phone/device test is run.

Goldberg has canonical AGENTS.md, existing GitHub development workflow/Project/Issues,
English Wiki, roadmaps, a partially completed 0.11 Stage 4 branch, untracked owner
RELEASE_NOTES.md, strict personal-data preservation rules and no physical-phone testing.
Those remain authoritative. PMP must not duplicate tracking resources or resume Stage 4,
start Stage 5, switch/reset/clean the worktree, or publish a Goldberg release.

After PMP safety tests and owner approval:

1. Make a separate, explicit integration plan using existing Goldberg AGENTS.md and docs.
2. Inspect actual worktree/branch/status read-only; keep owner RELEASE_NOTES.md untouched.
3. Prefer a separately approved disposable Git worktree for PMP initialization trial.
4. Point canonical policy at AGENTS.md and create references to existing Wiki/roadmaps;
   do not replace or duplicate canonical planning. Set all sensitive source backups off.
5. Use private checkpoints and private handoffs first. Configure verification only for
   approved emulator/disposable-fixture checks. Physical phone is prohibited.
6. Review all memory paths/privacy policy and proposed diffs before a GitHub milestone.
   Reuse existing workflows/Issues/Project, and approve any real shared-memory publication.
7. Only after separate approval integrate into the actual active repository. No Stage 4/5
   implementation or release is authorized by this proposal.

`python examples/demo.py --goldberg-style` creates a disposable synthetic branch and owner
release-notes file, demonstrates PMP workflow and asserts those files/branch survive recovery.
It exercises PMP only, not Goldberg application correctness or real project integration.
