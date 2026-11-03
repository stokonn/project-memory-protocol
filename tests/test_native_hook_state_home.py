"""Prove native hook commands pin writes to the configured private state home."""
import json
import os
import subprocess
import sys

import pytest

from pmp.core.config import initialize
from pmp.adapters import native_hook_command


@pytest.mark.skipif(os.name == "nt", reason="Native hooks are intentionally disabled on Windows")
def test_native_hook_write_uses_pinned_state_home(tmp_path, monkeypatch):
    root = tmp_path / "project with spaces"
    root.mkdir()
    intended_state = tmp_path / "private state"
    wrong_state = tmp_path / "wrong private state"
    monkeypatch.setenv("PMP_STATE_HOME", str(intended_state))
    project, _ = initialize(root)

    # Stop creates a real private checkpoint. The parent process deliberately
    # supplies a conflicting state home to simulate an agent daemon environment.
    env = os.environ.copy()
    env.pop("PMP_SESSION_ID", None)
    env["PMP_STATE_HOME"] = str(wrong_state)
    command = native_hook_command(project, "Stop")
    result = subprocess.run(
        command,
        shell=True,
        cwd=tmp_path,
        env=env,
        input=json.dumps({"hook_event_name": "Stop"}),
        text=True,
        capture_output=True,
        timeout=20,
    )

    assert result.returncode == 0, result.stderr
    assert project.local.is_dir()
    assert list((project.local / "checkpoints").glob("*.json"))
    assert not wrong_state.exists()
