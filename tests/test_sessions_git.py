import json
import os
import socket
import subprocess
import sys
import time
import pytest
from pmp.core.storage import PMPError,lock,read_json,write_json
from pmp.core.session import start,end,writer,release_stale
from pmp.core.config import Project
from pmp.checkpoints import create
from pmp.git import remote_status,run
from pmp import github

def test_concurrent_session_blocked(project,monkeypatch):
    value=start(project)
    with pytest.raises(PMPError):
        with writer(project): create(project)
    with pytest.raises(PMPError): start(project)
    monkeypatch.setenv('PMP_SESSION_ID',value['session_id'])
    with writer(project): create(project)
    with pytest.raises(PMPError): start(project)
    end(project)
    assert not (project.local/'session.json').exists()

def test_lock_is_exclusive(project):
    with lock(project.local/'writer.lock'):
        with pytest.raises(PMPError):
            with lock(project.local/'writer.lock'): pass

def test_active_and_remote_lease_never_stolen(project):
    value=start(project)
    with pytest.raises(PMPError,match='alive'): release_stale(project,value['session_id'])
    value['host']='another-machine'
    write_json(project.local/'session.json',value)
    with pytest.raises(PMPError,match='Remote'): release_stale(project,value['session_id'])

def test_dead_lease_explicit_release(project):
    child=subprocess.Popen([sys.executable,'-c','pass']); child.wait()
    value=start(project); value['pid']=child.pid
    write_json(project.local/'session.json',value)
    assert release_stale(project,value['session_id'])['released']==value['session_id']
    assert not (project.local/'session.json').exists()

def test_worktrees_distinct(project,commit,tmp_path):
    commit()
    other=tmp_path/'other'
    run(project.root,'worktree','add','-b','independent',str(other))
    p2=Project(other)
    assert p2.project_id==project.project_id
    assert p2.worktree_id!=project.worktree_id
    start(project); start(p2)

def test_remote_divergence(project,commit,tmp_path):
    commit(); remote=tmp_path/'remote.git'
    subprocess.run(['git','init','--bare',str(remote)],check=True,capture_output=True)
    run(project.root,'remote','add','origin',str(remote))
    run(project.root,'push','-u','origin','main')
    (project.root/'one').write_text('one'); commit()
    assert remote_status(project.root)['ahead']==1
    clone=tmp_path/'clone'
    subprocess.run(['git','clone','--branch','main',str(remote),str(clone)],check=True,capture_output=True)
    run(clone,'config','user.name','Other'); run(clone,'config','user.email','other@example.invalid')
    (clone/'two').write_text('two'); run(clone,'add','.'); run(clone,'commit','-m','other'); run(clone,'push')
    run(project.root,'fetch')
    state=remote_status(project.root)
    assert state['ahead']==1 and state['behind']==1 and not state['fresh']

def test_no_sync_from_cached_refs(project):
    create(project)
    result=github.inspect(project)
    assert not result['github_verified']
    assert result['checkpoints'][0]['state']=='LOCAL'

def test_offline_github(project,monkeypatch):
    def offline(*args,**kwargs): raise OSError('offline')
    monkeypatch.setattr(subprocess,'run',offline)
    with pytest.raises(PMPError,match='unavailable'): github.gh('api','user')

def test_repository_url_must_match(project):
    project.config['github']='owner/repo'
    run(project.root,'remote','add','origin','https://example.invalid/other/repo.git')
    with pytest.raises(PMPError,match='URLs'): github.repository(project)

def test_unrelated_staged_files_never_committed(project,commit):
    commit(); (project.root/'owner.txt').write_text('Owner draft')
    run(project.root,'add','owner.txt')
    with pytest.raises(PMPError,match='Index'): github.publish(project,commit=True)
    assert run(project.root,'diff','--cached','--name-only').stdout.strip()==b'owner.txt'

def test_export_commit_relationship(project,commit):
    commit(); c=create(project)
    github.export(project)
    github.publish(project,commit=True)
    assert github.inspect(project)['checkpoints'][0]['state']=='COMMITTED'
    # The immutable checkpoint describes its preceding HEAD; no future SHA cycle.
    assert c['git']['head']!=project.source()['head']

def test_fresh_clone_reads_shared_memory(project,commit,tmp_path):
    from pmp.verification import execute,summary
    commit()
    execute(project,'tests',[sys.executable,'-c','pass'])
    create(project); github.export(project); github.publish(project,commit=True)
    clone=tmp_path/'fresh'
    subprocess.run(['git','clone',str(project.root),str(clone)],check=True,capture_output=True)
    p2=Project(clone)
    from pmp.recovery import inspect,check
    report=inspect(p2)
    assert report['shared_checkpoints'] and report['verification']
    assert report['checkpoint'] is None and report['session'] is None
    assert check(p2)['valid']
    assert p2.local!=project.local

def _crlf_clone(project,tmp_path,name):
    # Reproduce Windows core.autocrlf=true checkout semantics on any platform.
    clone=tmp_path/name
    subprocess.run(['git','-c','core.autocrlf=true','clone',str(project.root),str(clone)],
                   check=True,capture_output=True)
    return clone

def test_fresh_clone_shared_memory_survives_crlf_checkout(project,commit,tmp_path):
    from pmp.verification import execute
    commit()
    execute(project,'tests',[sys.executable,'-c','pass'])
    create(project); github.export(project); github.publish(project,commit=True)
    p2=Project(_crlf_clone(project,tmp_path,'crlf'))
    from pmp.recovery import inspect
    report=inspect(p2)
    assert report['shared_checkpoints'] and report['verification']
    assert not report['damaged_shared_checkpoints']

def test_shared_handoff_content_tamper_still_refused(project,commit,tmp_path):
    from pmp.verification import execute
    commit()
    execute(project,'tests',[sys.executable,'-c','pass'])
    create(project); github.export(project); github.publish(project,commit=True)
    clone=_crlf_clone(project,tmp_path,'tampered')
    checkpoint=json.loads(next((clone/'.pmp'/'checkpoints').glob('*.json')).read_bytes())
    handoff=clone/'.pmp'/checkpoint['handoff']
    data=json.loads(handoff.read_bytes())
    data['completed'].append('Forged completion claim')
    handoff.write_bytes(json.dumps(data,indent=2).encode()+b'\n')
    p2=Project(clone)
    from pmp.recovery import inspect
    report=inspect(p2)
    # Endings may be rewritten by transport; altered content must never be accepted.
    assert not report['shared_checkpoints'] and report['damaged_shared_checkpoints']

def test_github_exact_sha_and_ci_are_separate(project,commit,monkeypatch):
    head=commit(); c=create(project)
    github.export(project); github.publish(project,commit=True)
    current=project.source()['head']
    project.config['github']='owner/repo'
    run(project.root,'remote','add','origin','https://github.com/owner/repo.git')
    def response(*args):
        if args[0]=='api': return {'sha':current}
        return [{'headSha':current,'status':'completed','conclusion':'failure','url':'https://example.invalid/run'}]
    monkeypatch.setattr(github,'gh',response)
    result=github.inspect(project,refresh=True)
    assert result['github_verified'] and result['checkpoints'][0]['state']=='SYNCED'
    assert result['ci'][0]['conclusion']=='failure'
    monkeypatch.setattr(github,'gh',lambda *args:{'sha':head})
    result=github.inspect(project,refresh=True)
    assert not result['github_verified'] and result['checkpoints'][0]['state']=='COMMITTED'
    assert result['ci'] is None

def test_push_failure_never_creates_sync_observation(project,commit,monkeypatch):
    commit(); project.config['github']='owner/repo'
    run(project.root,'remote','add','origin','https://github.com/owner/repo.git')
    original=github.git.run
    def deny(root,*args,**kwargs):
        if args[0]=='push': raise PMPError('Branch protection refused push')
        return original(root,*args,**kwargs)
    monkeypatch.setattr(github.git,'run',deny)
    with pytest.raises(PMPError,match='protection'): github.publish(project,push=True)
    assert not (project.local/'sync-observation.json').exists()

def test_repeated_identical_journal_records_idempotent(project):
    from pmp.events import Journal
    j=Journal(project); j.append('workspace.changed',{'fingerprint':'x'})
    blob=j.path.read_bytes()
    with j.path.open('ab') as stream: stream.write(blob)
    assert len(j.read()[0])==1
    assert j.append('workspace.changed',{'fingerprint':'y'})['sequence']==2

def test_writer_conflict_across_processes(project):
    with lock(project.local/'writer.lock'):
        r=subprocess.run([sys.executable,'-m','pmp','--project',str(project.root),'snapshot'],capture_output=True,text=True)
    assert r.returncode==3 and 'Writer lock' in r.stderr
    assert not list((project.local/'checkpoints').glob('*.json'))
