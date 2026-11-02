"""Measure compact PMP context output against full status in a disposable Git fixture.

Not an LLM/token benchmark. No agent is invoked, and no real project is inspected.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import statistics
import subprocess
import sys
import tempfile
import time

from demo import demonstrate


def benchmark(samples=3, limit=3):
    if samples not in range(1, 11) or limit not in range(1, 6):
        raise ValueError("samples must be 1..10 and limit must be 1..5")
    with tempfile.TemporaryDirectory(prefix="pmp-brief-benchmark-") as temp:
        base = Path(temp)
        fixture = demonstrate(output=base / "fixture", goldberg_style=True)
        root = Path(fixture["project"])
        cmd = [sys.executable, "-m", "pmp", "--project", str(root)]

        # A deliberately verbose synthetic task, never the operator's notes.
        labels = ["Completed synthetic milestone %02d with verified design decisions and safe handoff" % i
                  for i in range(20)]
        blockers = ["Synthetic blocker %02d: human approval and review pending" % i for i in range(8)]
        actions = ["Synthetic follow-up %02d: review proposed next action" % i for i in range(8)]
        task_args = ["task", "set"] + [arg for x in labels for arg in ("--completed", x)]
        task_args += [arg for x in blockers for arg in ("--blocker", x)]
        task_args += [arg for x in actions for arg in ("--next-action", x)]
        subprocess.run(cmd + task_args, check=True, capture_output=True, text=True)

        def measure(subcommand):
            timings = []
            payload = None
            for _ in range(samples):
                start = time.perf_counter()
                result = subprocess.run(cmd + subcommand, check=True, capture_output=True, text=True)
                timings.append((time.perf_counter() - start) * 1000)
                item = json.loads(result.stdout)
                if payload is None:
                    payload = item
            return len(result.stdout.encode("utf-8")), round(statistics.median(timings), 2), payload

        status_bytes, status_ms, status = measure(["status"])
        brief_bytes, brief_ms, brief = measure(["brief", "--limit", str(limit)])
        if not brief["read_only"] or brief["worktree_id"] != status["worktree_id"]:
            raise AssertionError("Brief source identity or read-only invariant failed")
        if brief["git"]["head"] != status["git"]["head"]:
            raise AssertionError("Brief and status describe different source revisions")
        if not brief["truncated"]:
            raise AssertionError("Fixture must exercise the bounded-output path")
        return {
            "fixture": "synthetic-disposable-git-project",
            "real_agent_invoked": False,
            "token_or_credit_savings_measured": False,
            "samples_per_command": samples,
            "brief_limit": limit,
            "status_output_bytes": status_bytes,
            "brief_output_bytes": brief_bytes,
            "output_reduction_percent": round((1 - brief_bytes / status_bytes) * 100, 1),
            "status_median_wall_ms": status_ms,
            "brief_median_wall_ms": brief_ms,
            "source_head_equal": True,
            "reported_items_truncated": True,
            "notes": "Wall time includes Python startup, Git inspection and JSON serialization; "
                     "bytes are not model tokens or billed credits."
        }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--samples", type=int, default=3)
    parser.add_argument("--limit", type=int, default=3)
    args = parser.parse_args()
    print(json.dumps(benchmark(samples=args.samples, limit=args.limit), indent=2))
