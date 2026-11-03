"""Prepare and inspect a disposable, opt-in Codex/PMP live-session fixture.

This script NEVER launches an AI model, trusts a hook, edits a real project,
or pretends to certify vendor event delivery. The operator starts Codex manually.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import tempfile


def run_command(args, *, cwd=None, env=None):
    result = subprocess.run(args, cwd=cwd, env=env, text=True,
                            capture_output=True, timeout=45, check=False)
    if result.returncode:
        raise RuntimeError(f"Command failed ({result.returncode}): {args[0]}: {result.stderr[:500]}")
    return result.stdout.strip()


def cli(root, state_home, *args):
    env = dict(os.environ, PMP_STATE_HOME=str(state_home))
    env.pop("PMP_SESSION_ID", None)
    result = run_command([sys.executable, "-m", "pmp", "--project", str(root), *args], env=env)
    return json.loads(result)


def setup(output=None, native=False):
    if output is None:
        base = Path(tempfile.mkdtemp(prefix="pmp-codex-live-")).resolve()
    else:
        base = Path(output).expanduser().resolve()
        base.mkdir(parents=True, exist_ok=False)  # Never reuse or overwrite a project.
    root = base / "project"
    state_home = base / "private"
    root.mkdir()
    (root / "AGENTS.md").write_text(
        "# Disposable test rules\n\n"
        "Only edit files in this temporary project. Read SCOPE.md before editing.\n"
        "Do not open other repositories, credentials or user data.\n"
        "No Git push, releases, installs, network calls or approval bypasses.\n",
        encoding="utf-8")
    (root / "SCOPE.md").write_text(
        "Approved fixture-only task: change app.py answer() from 41 to 42; "
        "run a small local Python assertion. Do not touch other projects.\n",
        encoding="utf-8")
    (root / "app.py").write_text("def answer():\n    return 41\n", encoding="utf-8")
    (root / ".gitignore").write_text("__pycache__/\n", encoding="utf-8")
    cli(root, state_home, "init")
    def git(*args):
        return run_command(["git", "-C", str(root), *args])
    git("config", "user.name", "PMP Fixture")
    git("config", "user.email", "pmp-fixture@example.invalid")
    git("add", ".")
    git("commit", "-m", "Create disposable live Codex probe")
    cli(root, state_home, "task", "activate", "codex-live-probe", "--approved-scope", "SCOPE.md")
    cli(root, state_home, "task", "set", "--phase", "implementing",
        "--next-action", "Change answer() to 42 inside this disposable fixture only")
    native_files = []
    if native:
        result = cli(root, state_home, "adapter", "install", "codex", "--native")
        native_files = result["files"]
    metadata = {
        "schema_version": 1,
        "fixture": "codex-disposable-only",
        "root": str(root),
        "private_state": str(state_home),
        "native": native,
        "native_files": native_files,
        "initial_head": git("rev-parse", "HEAD"),
        "installed_version": None,
    }
    if shutil.which("codex"):
        try:
            metadata["installed_version"] = run_command(["codex", "--version"])[:100]
        except (OSError, RuntimeError, subprocess.TimeoutExpired):
            pass
    (base / "probe.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    def quote(value):
        return shlex.quote(str(value))
    if native:
        command = f"cd {quote(root)} && PMP_STATE_HOME={quote(state_home)} codex"
    else:
        command = (
            f"cd {quote(root)} && PMP_STATE_HOME={quote(state_home)} "
            f"{quote(sys.executable)} -m pmp --project {quote(root)} launch codex --"
        )
    return {
        "fixture": str(root),
        "private_state": str(state_home),
        "native_hooks_installed": native,
        "installed_codex_version": metadata["installed_version"],
        "next_manual_command": command,
        "manual_prompt": (
            "Read AGENTS.md and SCOPE.md. Only in this disposable test project, "
            "edit app.py so answer() returns 42. Run a local Python assertion, "
            "report what changed, and stop. Do not touch any other project."
        ),
        "afterwards": f"{quote(sys.executable)} examples/codex_live_probe.py inspect --fixture {quote(base)}",
        "note": "No Codex session was started; no native hook activation or checkpoint is claimed.",
    }


def inspect(fixture):
    base = Path(fixture).expanduser().resolve()
    data = json.loads((base / "probe.json").read_text(encoding="utf-8"))
    root = Path(data["root"]).resolve()
    state_home = Path(data["private_state"]).resolve()
    if not root.is_relative_to(base) or not state_home.is_relative_to(base):
        raise ValueError("Fixture paths escaped the designated disposable directory")
    if data.get("fixture") != "codex-disposable-only":
        raise ValueError("Not a Codex probe fixture")
    brief = cli(root, state_home, "brief")
    history = cli(root, state_home, "history")
    checkpoints = history["checkpoints"]
    hooks = [c for c in checkpoints if c["reason"].startswith("adapter lifecycle: ")]
    observed_return = (root / "app.py").read_text(encoding="utf-8")
    return {
        "fixture": str(root),
        "read_only": True,
        "initial_head": data["initial_head"],
        "current_head": brief["git"]["head"],
        "change_to_42_observed": observed_return == "def answer():\n    return 42\n",
        "private_checkpoint_count": len(checkpoints),
        "native_hook_named_checkpoints": len(hooks),
        "native_hook_reasons": [c["reason"] for c in hooks[-5:]],
        "damaged_checkpoints": len(history.get("damaged", [])),
        "worktree_complete": brief["git"]["complete"],
        "uncertainty": brief["uncertainty"],
        "live_vendor_hook_provenance_certified": False,
        "note": ("Presence of a hook-named checkpoint only shows a receiver recorded it. "
                 "Review the genuine Codex /hooks trust UI, executed model turn, "
                 "and event timing separately to establish live vendor provenance. "
                 "No model transcripts were read."),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest="command", required=True)
    s = subs.add_parser("setup")
    s.add_argument("--output", help="New, non-existing directory; omit for system temp")
    s.add_argument("--native", action="store_true",
                   help="Only for a locally supported Codex version, explicit native artifacts")
    s = subs.add_parser("inspect")
    s.add_argument("--fixture", required=True, help="Parent directory containing probe.json")
    args = parser.parse_args()
    result = setup(args.output, args.native) if args.command == "setup" else inspect(args.fixture)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
