import json
import os
import pytest
from pmp.core.storage import PMPError,atomic_write,read_json,write_json
from pmp.events import Journal
from pmp.checkpoints import create,history
from pmp.recovery import inspect,check,generate

def test_idempotent_events(project):
    j=Journal(project)
    e=j.append('workspace.changed',{'fingerprint':'abc'},event_id='stable')
    assert j.append('workspace.changed',{'fingerprint':'abc'},event_id='stable')==e
    assert len(j.read()[0])==1
    with pytest.raises(PMPError,match='different content'):
        j.append('workspace.changed',{'fingerprint':'def'},event_id='stable')

def test_truncated_tail_preserved_and_repaired(project):
    j=Journal(project); j.append('workspace.changed',{'fingerprint':'abc'})
    with j.path.open('ab') as stream: stream.write(b'{"event_')
    before=j.path.read_bytes()
    events,tail=j.read(); assert len(events)==1 and tail
    with pytest.raises(PMPError,match='Truncated'): j.append('workspace.changed',{'fingerprint':'x'})
    result=j.repair_tail()
    from pathlib import Path
    assert Path(result['preserved_original']).read_bytes()==before
    assert not j.read()[1]
    assert j.append('workspace.changed',{'fingerprint':'new'})['sequence']==2

def test_middle_journal_corruption_fails_closed(project):
    j=Journal(project); j.append('workspace.changed',{'fingerprint':'a'})
    j.path.write_bytes(b'bad\n'+j.path.read_bytes())
    with pytest.raises(PMPError,match='corruption'): j.read()

def test_event_payload_validation(project):
    with pytest.raises(PMPError): Journal(project).append('checkpoint.created',{'wrong':'id'})
    assert not Journal(project).path.exists()

def test_atomic_replace_failure_keeps_old_file(tmp_path,monkeypatch):
    target=tmp_path/'state'; atomic_write(target,b'old')
    def fail(*args): raise OSError(28,'No space left on device')
    monkeypatch.setattr(os,'replace',fail)
    with pytest.raises(OSError): atomic_write(target,b'new')
    assert target.read_bytes()==b'old'
    assert list(tmp_path.iterdir())==[target]

def test_exclusive_write_never_overwrites(tmp_path):
    target=tmp_path/'cp'; atomic_write(target,b'one',exclusive=True)
    with pytest.raises(FileExistsError): atomic_write(target,b'two',exclusive=True)
    assert target.read_bytes()==b'one'

def test_checkpoint_chain_and_readonly_recovery(project):
    owner=project.root/'RELEASE_NOTES.md'; owner.write_text('Private owner draft')
    c1=create(project); owner.write_text('Edited private draft')
    c2=create(project)
    assert c2['previous']==c1['checkpoint_id']
    before=owner.read_bytes()
    report=inspect(project)
    assert report['checkpoint']['checkpoint_id']==c2['checkpoint_id']
    assert owner.read_bytes()==before
    assert not report['mutated_worktree']
    assert not c2['recovery']['content_backup']
    assert check(project)['valid']

def test_corrupt_latest_uses_previous(project):
    c1=create(project); c2=create(project)
    (project.local/'checkpoints'/(c2['checkpoint_id']+'.json')).write_text('{}')
    result=inspect(project)
    assert result['checkpoint']['checkpoint_id']==c1['checkpoint_id']
    assert len(result['damaged_checkpoints'])==1
    assert not check(project)['valid']

def test_checkpoint_tamper_detected(project):
    c=create(project); c['reason']='tampered'
    write_json(project.local/'checkpoints'/(c['checkpoint_id']+'.json'),c)
    valid,damaged=history(project)
    assert not valid and damaged

def test_allowlisted_backup(project):
    (project.root/'safe.py').write_text('x = 1\n')
    project.config['checkpoint']['backup_allowlist']=['safe.py']
    c=create(project)
    assert c['recovery']['content_backup']
    assert (project.local/'backups'/c['checkpoint_id']/'safe.py').read_text()=='x = 1\n'
    assert (project.local/'backups'/c['checkpoint_id']/'manifest.json').exists()

def test_sensitive_backup_refused(project):
    (project.root/'.env').write_text('innocent')
    project.config['checkpoint']['backup_allowlist']=['.env']
    with pytest.raises(PMPError,match='sensitive'): create(project)
    assert not list((project.local/'backups').rglob('*'))

def test_existing_handoff_preserved(project):
    target=project.docs/'HANDOFF.md'; target.write_text('Authoritative handoff')
    with pytest.raises(PMPError,match='not PMP-generated'): generate(project,shared=True)
    assert target.read_text()=='Authoritative handoff'

def test_local_handoff_and_index_rebuild(project):
    create(project)
    data=generate(project)
    assert data['safety_restrictions']
    assert (project.local/'HANDOFF.md').is_file()
    (project.local/'checkpoint-index.json').write_text('damaged')
    from pmp.cli import main
    assert main(['--project',str(project.root),'history','--rebuild-index'])==0
    assert len(read_json(project.local/'checkpoint-index.json'))==1

def test_backup_damage_causes_fallback(project):
    (project.root/'safe.py').write_text('x=1')
    first=create(project)
    project.config['checkpoint']['backup_allowlist']=['safe.py']
    second=create(project)
    (project.local/'backups'/second['checkpoint_id']/'safe.py').write_text('tampered')
    result=inspect(project)
    assert result['checkpoint']['checkpoint_id']==first['checkpoint_id']
    assert 'backup file corrupted' in result['damaged_checkpoints'][0]['error']

def test_handoff_damage_causes_fallback(project):
    first=create(project); second=create(project)
    (project.local/second['handoff']).write_text('{}')
    result=inspect(project)
    assert result['checkpoint']['checkpoint_id']==first['checkpoint_id']
    assert 'handoff' in result['damaged_checkpoints'][0]['error']

def test_recovery_report_explicit(project):
    from pmp.cli import main
    assert main(['--project',str(project.root),'resume','--record'])==0
    reports=list((project.local/'recovery').glob('*.json'))
    assert len(reports)==1 and read_json(reports[0])['mutated_worktree'] is False
    types=[e['event_type'] for e in Journal(project).read()[0]]
    assert types==['recovery.started','recovery.completed']

def test_resume_without_record_does_not_create_private_state(project):
    assert not project.local.exists()
    inspect(project)
    assert not project.local.exists()

def test_checkpoint_unsafe_reference_refused(project):
    from pmp.core.storage import seal
    c=create(project); c['handoff']='../../outside.json'
    write_json(project.local/'checkpoints'/(c['checkpoint_id']+'.json'),seal(c))
    valid,damaged=history(project)
    assert not valid and damaged

def test_incomplete_checkpoint_does_not_publish_record(project,monkeypatch):
    from pmp import checkpoints
    original=checkpoints.write_json
    def fail_checkpoint(path,data,**kwargs):
        if path.parent.name=='checkpoints': raise OSError(28,'disk full')
        return original(path,data,**kwargs)
    monkeypatch.setattr(checkpoints,'write_json',fail_checkpoint)
    with pytest.raises(OSError): create(project)
    assert not history(project)[0]
    assert not any(e['event_type']=='checkpoint.created' for e in Journal(project).read()[0])

def test_clock_reversal_does_not_reorder_stream(project,monkeypatch):
    import pmp.events as events
    stamps=iter(['2030-01-01T00:00:00Z','2000-01-01T00:00:00Z'])
    monkeypatch.setattr(events,'now',lambda:next(stamps))
    j=Journal(project)
    j.append('workspace.changed',{'fingerprint':'a'})
    j.append('workspace.changed',{'fingerprint':'b'})
    rows,_=j.read()
    assert [e['sequence'] for e in rows]==[1,2]
    assert rows[0]['timestamp']>rows[1]['timestamp']
