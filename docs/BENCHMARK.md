# Measuring bounded agent context

This is a **synthetic CLI-output benchmark**, not an AI model benchmark. No model API calls, prompts, real transcripts, credits, personal files, active Gould worktrees or production services are used.

## Run

From an editable or installed PMP checkout:

```sh
python examples/brief_benchmark.py --samples 3 --limit 3
```

The script creates a temporary Git fixture with synthetic owner instructions, an explicit scope, verified fixture checks, checkpoint, and handoff. It populates a verbose synthetic task and measures the JSON stdout from:

- `pmp status` — full read-only recovery and sync view
- `pmp brief --limit 3` — capped, read-only agent starting context

Both commands run against the same fixture and are validated to report the same `HEAD` and worktree identity. The script checks that `brief` truncates its synthetic content.

Reported values:

| Field | Meaning |
| --- | --- |
| `status_output_bytes` | UTF-8 bytes written by full status |
| `brief_output_bytes` | UTF-8 bytes written by brief |
| `output_reduction_percent` | `100 * (1 - brief_bytes/status_bytes)` on the fixture |
| `status_median_wall_ms` | Median subprocess runtime, including Python startup |
| `brief_median_wall_ms` | Same measurement for brief |
| `source_head_equal` | Both responses identify the same Git revision |
| `real_agent_invoked` | Always false; no vendor AI runtime |

## Interpretation limits

**JSON byte reduction is not a measured reduction in model tokens or money.** Tokenization, repeated policy loads, prompts, context compaction and agent behavior vary. The benchmark measures neither actual Codex usage nor the quality of recovered decisions. Each invocation still computes a source fingerprint, which can involve substantial disk I/O on a large worktree such as Gould.

A useful later **opt-in** real-agent experiment should compare the same scoped, isolated tasks with and without PMP, include interruption and cold restart, record actual provider-reported consumption if exposed, and have human reviewers evaluate recovery correctness. Keep user data, credentials and live application artifacts out of both fixtures.

The cross-platform CI runs the synthetic benchmark with two samples per command. Results remain job logs; they are not claimed as reproducible performance figures for the owner’s computer or charged model sessions. No stable-release acceptance is inferred from this benchmark alone.
