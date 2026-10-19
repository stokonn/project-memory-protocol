# Git and GitHub milestones

Git is required. Existing repositories are inspected and preserved. Init creates Git only
when no enclosing worktree exists. No automatic commits or pushes from watcher/snapshot.
Configure `.pmp.yml` github as `owner/repository` only after an approved repository exists.
Configure origin normally; PMP does not create GitHub repos, Projects, Issues or tags.

At an approved milestone:

```sh
pmp snapshot --reason approved-milestone
pmp sync --export
git diff -- .pmp docs/ai
# Review new/untracked exports too, not only tracked diffs.
git status --short
pmp sync --commit --message 'Record approved PMP milestone'
pmp sync --push
pmp sync --refresh
```

Flags are direct authorization to perform their named action. Export is reversible local
preparation, commit changes history, push publishes the branch's pending commits. Do not
use push without permission to publish that branch/repository. Branch protection errors
remain errors; PMP never circumvents them. Existing staged changes block PMP commit/push
to avoid including owner work accidentally. Commit scans only share_allowlist paths under
memory roots. Unrelated unstaged/untracked source files are not staged or deleted.

LOCAL checkpoint: immutable private record. COMMITTED: byte-identical shared file appears
in current HEAD. SYNCED: GitHub freshly returns that branch's exact expected HEAD while
checkpoint is COMMITTED. No future commit SHA inside the record. Git status HEAD can differ
from the checkpoint's source HEAD because a subsequent commit contains memory. Evidence
therefore may become conservatively inapplicable after a commit and must be rerun when needed.

`sync` without flags is offline: upstream ahead/behind values reflect **cached refs**.
`sync --refresh` uses installed gh to query exact GitHub branch SHA and workflow runs for
that SHA. CI results remain a separate list of statuses/conclusions/URLs. No runs means
no observed CI, not successful CI. API failure yields exit 4 and no synchronized claim.
No fetch/rebase/merge/reset/branch switch occurs automatically. Resolve divergence through
the project's normal reviewed Git workflow. Separate worktrees isolate concurrent tasks;
PMP leases do not coordinate different branches' eventual merge conflicts.

Run `gh auth status` to diagnose access; authenticate outside PMP using your normal process.
Offline projects retain all local commands. A locally successful push is insufficient to
claim synchronization until GitHub confirms the expected identity. Stable release/tagging
remains a separate owner-authorized workflow and is not implemented as an automatic action.
