"""CLI-only fixture tests. No vendor authentication or model turns involved."""
import json
from pathlib import Path
import subprocess
import sys


SCRIPT=Path(__file__).resolve().parents[1]/'examples'/'codex_live_probe.py'


def probe(*args):
    result=subprocess.run([sys.executable,str(SCRIPT),*map(str,args)],
                          capture_output=True,text=True,timeout=45)
    assert result.returncode==0,result.stderr
    return json.loads(result.stdout)


def test_disposable_probe_is_explicit_and_read_only(tmp_path):
    base=tmp_path/'fixture with spaces'
    result=probe('setup','--output',base)
    root=base/'project'
    assert result['fixture']==str(root)
    assert result['native_hooks_installed'] is False
    assert 'codex' in result['next_manual_command']
    assert (root/'app.py').read_text()=='def answer():\n    return 41\n'
    assert (root/'AGENTS.md').exists() and (root/'SCOPE.md').exists()
    assert (base/'private').exists()  # Explicit fixture-only task activation writes a journal.
    assert not (root/'.codex/hooks.json').exists()
    assert (base/'probe.json').exists()

    before={str(p.relative_to(base)):p.read_bytes() for p in (base/'private').rglob('*') if p.is_file()}
    first=probe('inspect','--fixture',base)
    assert first['read_only'] is True
    assert not first['change_to_42_observed']
    assert first['private_checkpoint_count']==0
    assert first['native_hook_named_checkpoints']==0
    assert not first['live_vendor_hook_provenance_certified']
    after={str(p.relative_to(base)):p.read_bytes() for p in (base/'private').rglob('*') if p.is_file()}
    assert after==before  # Inspection must not append events or snapshots.
    # Human-approved fixture-only change; not a simulated agent turn.
    (root/'app.py').write_text('def answer():\n    return 42\n')
    second=probe('inspect','--fixture',base)
    assert second['change_to_42_observed']
    assert second['native_hook_named_checkpoints']==0
    assert not second['live_vendor_hook_provenance_certified']


def test_probe_cannot_replace_an_existing_directory(tmp_path):
    base=tmp_path/'existing'
    base.mkdir()
    (base/'owner-notes.txt').write_text('must survive')
    result=subprocess.run([sys.executable,str(SCRIPT),'setup','--output',str(base)],
                          capture_output=True,text=True,timeout=20)
    assert result.returncode != 0
    assert (base/'owner-notes.txt').read_text()=='must survive'
    assert not (base/'project').exists()
